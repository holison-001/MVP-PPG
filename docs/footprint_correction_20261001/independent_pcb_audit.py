"""Read-only independent geometry and return-path review of a saved PCB snapshot."""
import argparse
from collections import Counter, defaultdict
import gc
import hashlib
import heapq
import json
import math
from pathlib import Path
import sys

import pcbnew as k
from shapely.geometry import Polygon, Point, LineString, shape as as_shape
from shapely.affinity import translate, rotate
from shapely.ops import unary_union, nearest_points

gc.disable()
ROOT = Path(__file__).resolve().parents[2] / 'kicad'
sys.path.insert(0, str(ROOT))
from schematic_metadata import load_schematic_metadata
from netcheck_v08 import check_board
from board_coordinates_v08 import normalize_for_analysis


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def xy(v):
    return (k.ToMM(v.x), k.ToMM(v.y))


def shape(ps):
    polys = []
    for i in range(ps.OutlineCount()):
        o = ps.COutline(i)
        pts = [xy(o.CPoint(j)) for j in range(o.PointCount())]
        holes = []
        for j in range(ps.HoleCount(i)):
            h = ps.CHole(i, j)
            holes.append([xy(h.CPoint(n)) for n in range(h.PointCount())])
        if len(pts) >= 3:
            polys.append(Polygon(pts, holes))
    return unary_union(polys)


def pad_distance(point, pad):
    """Nominal distance to circles/rectangles/roundrects without arc tessellation."""
    distances=[]
    for g in pad['analytic_geometry']:
        if g['shape'] not in (k.PAD_SHAPE_CIRCLE,k.PAD_SHAPE_RECT,k.PAD_SHAPE_OVAL,k.PAD_SHAPE_ROUNDRECT):
            distances.append(Point(point).distance(pad['poly']))
            continue
        dx,dy=point[0]-g['pos'][0],point[1]-g['pos'][1]
        angle=math.radians(g['angle']);ca,sa=math.cos(angle),math.sin(angle)
        x,y=abs(ca*dx-sa*dy),abs(sa*dx+ca*dy)
        hx,hy=g['size'][0]/2,g['size'][1]/2
        radius=0.
        if g['shape'] in (k.PAD_SHAPE_CIRCLE,k.PAD_SHAPE_OVAL):radius=min(hx,hy)
        elif g['shape']==k.PAD_SHAPE_ROUNDRECT:radius=g['radius']
        qx,qy=x-(hx-radius),y-(hy-radius)
        signed=math.hypot(max(qx,0),max(qy,0))+min(max(qx,qy),0)-radius
        distances.append(max(signed,0.))
    return min(distances)


def clearance_core(g, fallback):
    """Express a rounded pad exactly as a convex core plus a circular radius."""
    if g['shape'] not in (k.PAD_SHAPE_CIRCLE,k.PAD_SHAPE_RECT,k.PAD_SHAPE_OVAL,k.PAD_SHAPE_ROUNDRECT):
        return fallback,0.
    hx,hy=g['size'][0]/2,g['size'][1]/2
    radius=min(hx,hy)if g['shape']in(k.PAD_SHAPE_CIRCLE,k.PAD_SHAPE_OVAL)else(g['radius']if g['shape']==k.PAD_SHAPE_ROUNDRECT else 0.)
    hx-=radius;hy-=radius
    angle=math.radians(g['angle']);ca,sa=math.cos(angle),math.sin(angle)
    transform=lambda x,y:(g['pos'][0]+ca*x+sa*y,g['pos'][1]-sa*x+ca*y)
    if hx<1e-12 and hy<1e-12:return Point(g['pos']),radius
    if hx<1e-12:return LineString([transform(0,-hy),transform(0,hy)]),radius
    if hy<1e-12:return LineString([transform(-hx,0),transform(hx,0)]),radius
    return Polygon([transform(-hx,-hy),transform(hx,-hy),transform(hx,hy),transform(-hx,hy)]),radius


def max_radius(geometry):
    if geometry.is_empty:return 0.
    if hasattr(geometry,'geoms'):return max(max_radius(g)for g in geometry.geoms)
    coords=geometry.exterior.coords if geometry.geom_type=='Polygon'else geometry.coords
    return max(math.hypot(x,y)for x,y in coords)


class Graph:
    """Centerline path lengths including center-to-contact distance within pads/vias.

    Planes are intentionally excluded: the target is a via connected to a filled plane.
    Same-net touching pad/track copper is included even without identical endpoints.
    """
    def __init__(self, tracks, vias, pads, net):
        self.adj = defaultdict(list)
        self.tracks = [t for t in tracks if t['net'] == net]
        self.vias = [v for v in vias if v['net'] == net]
        self.pads = [p for p in pads if p['net'] == net]
        cuts = [[0., t['line'].length] for t in self.tracks]
        links = []
        for i, a in enumerate(self.tracks):
            for j, b in enumerate(self.tracks[:i]):
                if a['layer'] != b['layer']:
                    continue
                if a['line'].distance(b['line']) <= (a['width']+b['width'])/2 + 1e-7:
                    pa, pb = nearest_points(a['line'], b['line'])
                    da, db = a['line'].project(pa), b['line'].project(pb)
                    cuts[i].append(da); cuts[j].append(db)
                    links.append((self.node(pa.coords[0], a['layer']), self.node(pb.coords[0], b['layer']), pa.distance(pb), min(a['width'], b['width']), 'copper_contact'))
            for p in self.pads:
                if a['layer'] not in p['layers'] or p['poly'].distance(a['line']) > a['width']/2+1e-7:
                    continue
                d = a['line'].project(Point(p['pos']))
                q = a['line'].interpolate(d)
                cuts[i].append(d)
                links.append((self.padnode(p), self.node(q.coords[0], a['layer']), Point(p['pos']).distance(q), None, 'within_pad'))
            for v in self.vias:
                if a['layer'] not in v['layers'] or a['line'].distance(Point(v['pos'])) > a['width']/2+v['diameter']/2+1e-7:
                    continue
                d = a['line'].project(Point(v['pos'])); q = a['line'].interpolate(d)
                cuts[i].append(d)
                links.append((self.vianode(v), self.node(q.coords[0], a['layer']), Point(v['pos']).distance(q), a['width'], 'within_via'))
        for i, t in enumerate(self.tracks):
            distances = sorted(set(round(v, 9) for v in cuts[i]))
            for lo, hi in zip(distances, distances[1:]):
                a = self.node(t['line'].interpolate(lo).coords[0], t['layer'])
                b = self.node(t['line'].interpolate(hi).coords[0], t['layer'])
                links.append((a, b, hi-lo, t['width'], 'track'))
        for p in self.pads:
            for v in self.vias:
                if set(p['layers']) & set(v['layers']) and p['poly'].distance(Point(v['pos'])) <= v['diameter']/2+1e-7:
                    links.append((self.padnode(p), self.vianode(v), math.dist(p['pos'], v['pos']), None, 'pad_via_copper_contact'))
        for a, b, length, width, kind in links:
            self.adj[a].append((b, length, width, kind)); self.adj[b].append((a, length, width, kind))

    @staticmethod
    def node(p, layer):
        return ('xy', layer, round(p[0], 6), round(p[1], 6))

    @staticmethod
    def padnode(p):
        return ('pad', p['ref'], p['number'], p['index'])

    @staticmethod
    def vianode(v):
        return ('via', v['index'])

    def shortest(self, source, targets, ignore_pad_via_contact=False):
        queue = [(0., source)]; dist = {source: 0.}; prev = {}
        while queue:
            distance, node = heapq.heappop(queue)
            if distance != dist[node]:
                continue
            if node in targets:
                path = []; cursor = node
                while cursor != source:
                    parent, length, width, kind = prev[cursor]
                    path.append({'from': parent, 'to': cursor, 'length_mm': length, 'width_mm': width, 'kind': kind})
                    cursor = parent
                path.reverse()
                widths = [s['width_mm'] for s in path if s['width_mm'] is not None]
                return {'target': node, 'length_mm': distance, 'minimum_track_width_mm': min(widths) if widths else None, 'path': path}
            for other, length, width, kind in self.adj[node]:
                if ignore_pad_via_contact and kind=='pad_via_copper_contact':
                    continue
                nd = distance + length
                if nd < dist.get(other, float('inf'))-1e-12:
                    dist[other] = nd; prev[other] = (node, length, width, kind)
                    heapq.heappush(queue, (nd, other))
        return None


def audit(board_path, drc_path, output, project_path=None):
    sch = ROOT/'ppg_pcb_v08.kicad_sch'
    initial_hash = sha(board_path)
    initial_schematic_hash = sha(sch)
    b = k.LoadBoard(str(board_path))
    errors = []; observations = []
    project_path=project_path or Path(board_path).with_suffix('.kicad_pro')
    project_rules=None
    if Path(project_path).is_file():
        project=json.loads(Path(project_path).read_text())
        rules=project['board']['design_settings']['rules']
        required={'min_clearance':.15,'min_copper_edge_clearance':.3,'min_track_width':.1,'min_via_diameter':.5,'min_through_hole_diameter':.25,'min_hole_to_hole':.25}
        project_rules={'path':str(project_path),'sha256':sha(project_path),'rules':{key:rules.get(key)for key in required}}
        custom_rules=Path(board_path).with_suffix('.kicad_dru')
        if custom_rules.is_file():
            project_rules['custom_rules']={'path':str(custom_rules),'sha256':sha(custom_rules)}
        for key,minimum in required.items():
            if rules.get(key,0)<minimum-1e-6:errors.append(f'Project rule {key} is below required {minimum} mm')
    metadata = load_schematic_metadata(sch)
    netcheck = check_board(b, metadata)
    errors.extend(netcheck['errors'])
    sheet_center = normalize_for_analysis(b)
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    if len(fps) != 37 or any(r in fps for r in ['D2', 'D3', 'D4', 'D5']):
        errors.append('Expected 37 components without D2/D3/D4/D5')
    if netcheck['numbered_pads'] != 117:
        errors.append('Expected exactly 117 numbered pads')
    u1 = fps['U1']
    if xy(u1.GetPosition()) != (0., 0.) or u1.GetOrientationDegrees() != 0.:
        errors.append('U1 must remain at the PCB center, rotation 0')
    expected_polarity={
        ('J1','1'):'/12V_IN',('D1','1'):'/12V_IN',('D1','2'):'GND',
        ('FB1','1'):'/12V_IN',('FB1','2'):'12V',('C13','1'):'12V',('U4','8'):'12V',
        ('D6','1'):'/SWDIO',('D7','1'):'/SWCLK',('D8','1'):'/NRST',
        ('D6','2'):'GND',('D7','2'):'GND',('D8','2'):'GND',
        ('U3','1'):'/UART_TX',('U3','2'):'3V3',('U3','3'):'3V3',
        ('U3','4'):'/TXN_DRV',('U3','5'):'GND',('U3','6'):'/TXP_DRV',
        ('U6','1'):'3V3',('U6','2'):'GND',('U6','3'):'/UART_RX',
        ('U6','4'):'/RXN_RCV',('U6','5'):'GND',('U6','6'):'/RXP_RCV',
    }
    pinmap_errors=[]
    for (ref,pin),expected in expected_polarity.items():
        pad=fps[ref].FindPadByNumber(pin)
        actual=pad.GetNetname()if pad is not None else None
        if actual!=expected:pinmap_errors.append({'pad':ref+'.'+pin,'expected':expected,'actual':actual})
    if pinmap_errors:errors.append('Power split, TVS polarity, or RS422 IC package pin mapping differs from the approved topology')

    pads = []; tracks = []; vias = []; zones = []
    for f in fps.values():
        for p in f.Pads():
            layers = [l for l in [k.F_Cu, k.B_Cu] if p.IsOnLayer(l)]
            if not layers:
                continue
            poly = unary_union([shape(p.GetEffectivePolygon(l)) for l in layers])
            analytic=[{'shape':int(p.GetShape(l)),'pos':xy(p.ShapePos(l)),'size':xy(p.GetSize(l)),'angle':p.GetOrientationDegrees(),'radius':k.ToMM(p.GetRoundRectCornerRadius())}for l in layers]
            pads.append({'ref':f.GetReference(), 'number':p.GetNumber(), 'net':p.GetNetname(), 'pos':xy(p.GetPosition()), 'layers':layers, 'poly':poly, 'index':len(pads), 'smd':p.GetAttribute()==k.PAD_ATTRIB_SMD,'analytic_geometry':analytic})
            pads[-1]['clearance_cores']=[clearance_core(g,poly)for g in analytic]
    for t in b.GetTracks():
        if isinstance(t,k.PCB_VIA):
            vias.append({'pos':xy(t.GetPosition()), 'net':t.GetNetname(), 'diameter':k.ToMM(t.GetWidth(k.F_Cu)), 'drill':k.ToMM(t.GetDrillValue()), 'layers':[l for l in [k.F_Cu,k.In1_Cu,k.In2_Cu,k.B_Cu] if t.IsOnLayer(l)], 'index':len(vias),'tented_front':bool(t.IsTented(k.F_Mask)),'tented_back':bool(t.IsTented(k.B_Mask))})
        else:
            if isinstance(t,k.PCB_ARC):
                errors.append('Arc centerline is unsupported in this independent path analysis')
            line=LineString([xy(t.GetStart()),xy(t.GetEnd())])
            tracks.append({'line':line,'width':k.ToMM(t.GetWidth()),'net':t.GetNetname(),'layer':t.GetLayer(),'index':len(tracks)})
    for z in b.Zones():
        layer=z.GetLayer()
        poly=shape(z.GetFilledPolysList(layer)) if z.IsFilled() else Polygon()
        edge_gap=6.75-max_radius(poly) if not poly.is_empty else None
        required_edge=.20 if layer==k.F_Cu else .30
        if edge_gap is not None and edge_gap<required_edge-1e-5:
            errors.append(f'{b.GetLayerName(layer)} filled-zone edge clearance is below {required_edge:.2f} mm')
        if layer==k.F_Cu and edge_gap is not None and edge_gap>.205:
            errors.append('F.Cu GND fill does not reach the requested 0.20 mm edge setback; check custom rules and refill')
        zones.append({'layer':layer,'layer_name':b.GetLayerName(layer),'net':z.GetNetname(),'filled':z.IsFilled(),'poly':poly,'filled_area_mm2':poly.area,'minimum_edge_clearance_mm':edge_gap,'required_edge_clearance_mm':required_edge,'local_clearance_mm':k.ToMM(z.GetLocalClearance())})
    expected={(k.F_Cu,'GND'),(k.In1_Cu,'GND')}
    if {(z['layer'],z['net'])for z in zones} != expected or not all(z['filled'] and z['filled_area_mm2']>0 for z in zones):
        errors.append('Expected filled F.Cu/In1.Cu GND zones only; In2 uses routed 3V3')
    for v in vias:
        v['plane_connections']=[z['layer_name'] for z in zones if z['layer']==k.In1_Cu and v['net']==z['net'] and z['layer']in v['layers'] and z['poly'].distance(Point(v['pos'])) < v['diameter']/2-1e-6]
        v['in2_power_connections']=[t['index'] for t in tracks if t['net']==v['net']=='3V3' and t['layer']==k.In2_Cu and t['line'].distance(Point(v['pos'])) <= (t['width']+v['diameter'])/2+1e-7]

    geometry_path=Path(__file__).with_name('placement') / 'geometry.json'
    geometry=json.loads(geometry_path.read_text())
    courts={};bodies={};geometry_changes=[];body_edge=[]
    for ref,f in fps.items():
        if ref=='U1':continue
        base=next(o for o in geometry['footprints'][ref]['orientations']if o['rot']==0)
        pos=xy(f.GetPosition());angle=f.GetOrientationDegrees()
        transform=lambda s:translate(rotate(as_shape(s),-angle,origin=(0,0)),*pos)
        courts[ref]=transform(base['courtyard']);bodies[ref]=transform(base['body'])
        expected_copper=transform(base['copper'])
        actual_copper=unary_union([p['poly']for p in pads if p['ref']==ref])
        area=expected_copper.symmetric_difference(actual_copper).area
        if area>1e-5:geometry_changes.append({'ref':ref,'copper_difference_area_mm2':area})
        shapes=list(bodies[ref].geoms)if hasattr(bodies[ref],'geoms')else[bodies[ref]]
        radius=max((math.hypot(x,y)for g in shapes if not g.is_empty for x,y in g.exterior.coords),default=0.)
        if radius>6.75+1e-6:body_edge.append({'ref':ref,'max_radius_mm':radius})
    court_overlap=[];body_overlap=[]
    for i,ref in enumerate(courts):
        for other in list(courts)[:i]:
            area=courts[ref].intersection(courts[other]).area
            if area>1e-8:court_overlap.append({'refs':[ref,other],'area_mm2':area})
            area=bodies[ref].intersection(bodies[other]).area
            if area>1e-8:body_overlap.append({'refs':[ref,other],'area_mm2':area})
    if geometry_changes:errors.append('Footprint copper geometry differs from frozen manufacturer/standard-library placement geometry')
    if body_edge or body_overlap or court_overlap:errors.append('Physical body/courtyard placement constraints failed')

    drill_overlap=[]; same_net_overlap=[]; drill_gaps=[]; drill_pair_gaps=[]
    for v in vias:
        for p in pads:
            if p['smd']:
                row={'via_index':v['index'],'via_pos':v['pos'],'via_net':v['net'],'pad':p['ref']+'.'+p['number'],'pad_net':p['net'],'drill_clearance_mm':pad_distance(v['pos'],p)-v['drill']/2}
                drill_gaps.append(row)
                if row['drill_clearance_mm'] < -1e-6:drill_overlap.append(row)
        for u in vias[:v['index']]:
            distance=math.dist(v['pos'],u['pos'])
            gap=distance-(v['diameter']+u['diameter'])/2
            drill_pair_gaps.append({'via_indices':[u['index'],v['index']],'positions':[u['pos'],v['pos']],'nets':[u['net'],v['net']],'drill_gap_mm':distance-(v['drill']+u['drill'])/2})
            if v['net']==u['net'] and gap < -1e-6:
                same_net_overlap.append({'via_indices':[u['index'],v['index']],'positions':[u['pos'],v['pos']],'net':v['net'],'gap_mm':gap})
    if drill_overlap:errors.append('Via drills intersect SMD pads, including same-net pads')
    drill_pair_gaps.sort(key=lambda row:row['drill_gap_mm'])
    drill_pair_violations=[row for row in drill_pair_gaps if row['drill_gap_mm']<.25-1e-6]
    if drill_pair_violations:errors.append('Via drill-to-drill spacing below nominal 0.25 mm')
    drill_gaps.sort(key=lambda row:row['drill_clearance_mm'])
    narrow_drill_gaps=[row for row in drill_gaps if row['drill_clearance_mm']<.025-1e-6]
    if narrow_drill_gaps:errors.append('Through-via drill to SMD copper gap below required nominal 0.025 mm')
    untented=[v for v in vias if not(v['tented_front']and v['tented_back'])]
    if untented:errors.append('All vias must be tented on both faces')
    pad_gaps=[];interfootprint_gaps=[]
    for i,a in enumerate(pads):
        for bb in pads[:i]:
            if not(set(a['layers'])&set(bb['layers'])):continue
            exact_gap=max(0.,min(ca.distance(cb)-ra-rb for ca,ra in a['clearance_cores']for cb,rb in bb['clearance_cores']))
            row={'pads':[a['ref']+'.'+a['number'],bb['ref']+'.'+bb['number']],'nets':[a['net'],bb['net']],'clearance_mm':exact_gap}
            pad_gaps.append(row)
            if a['ref']!=bb['ref']:interfootprint_gaps.append(row)

    copper=[]
    for p in pads:copper.append({'id':p['ref']+'.'+p['number'],'net':p['net'],'layers':p['layers'],'poly':p['poly'],'cores':p['clearance_cores'],'max_radius':max(max_radius(core)+radius for core,radius in p['clearance_cores'])})
    for t in tracks:copper.append({'id':'track'+str(t['index']),'net':t['net'],'layers':[t['layer']],'poly':t['line'].buffer(t['width']/2,resolution=64),'cores':[(t['line'],t['width']/2)],'max_radius':max_radius(t['line'])+t['width']/2})
    for v in vias:copper.append({'id':'via'+str(v['index']),'net':v['net'],'layers':v['layers'],'poly':Point(v['pos']).buffer(v['diameter']/2,resolution=64),'cores':[(Point(v['pos']),v['diameter']/2)],'max_radius':math.hypot(*v['pos'])+v['diameter']/2})
    edge_rows=[]
    for c in copper:
        edge_rows.append({'item':c['id'],'clearance_mm':6.75-c['max_radius']})
    min_edge=min(edge_rows,key=lambda r:r['clearance_mm'])
    if min_edge['clearance_mm']<.3-1e-5:errors.append('Copper edge clearance is below 0.30 mm')
    min_clearance={'gap_mm':float('inf')}
    for i,a in enumerate(copper):
        for bb in copper[:i]:
            if a['net']==bb['net']or not(set(a['layers'])&set(bb['layers'])):continue
            gap=max(0.,min(ca.distance(cb)-ra-rb for ca,ra in a['cores']for cb,rb in bb['cores']))
            if gap<min_clearance['gap_mm']:min_clearance={'items':[a['id'],bb['id']],'nets':[a['net'],bb['net']],'gap_mm':gap}
    if min_clearance['gap_mm']<.15-1e-6:errors.append('Nominal inter-net copper clearance is below 0.15 mm')
    if min(t['width']for t in tracks)<.1-1e-6:errors.append('Trace width below 0.10 mm')
    in2_power=[t for t in tracks if t['net']=='3V3' and t['layer']==k.In2_Cu]
    if not in2_power or any(t['width']<.4-1e-6 for t in in2_power):errors.append('In2 3V3 distribution must retain 0.40 mm minimum width')
    if any(v['diameter']<.5-1e-6 or v['drill']<.25-1e-6 for v in vias):errors.append('Via diameter/drill below 0.50/0.25 mm')

    graphs={net:Graph(tracks,vias,pads,net)for net in ['GND','3V3']}
    def pad(ref,num):return next(p for p in pads if p['ref']==ref and p['number']==num)
    def return_path(ref,num):
        p=pad(ref,num); graph=graphs[p['net']]
        eligible=[v for v in vias if v['net']==p['net']and (v['plane_connections'] or v['in2_power_connections'])]
        result=graph.shortest(graph.padnode(p),{graph.vianode(v)for v in eligible})
        out={'pad':ref+'.'+num,'net':p['net'],'pad_pos':p['pos'],'destination':'In1 ground plane' if p['net']=='GND' else 'In2 broad 3V3 distribution','nearest_distribution_via_geometric_mm':min((math.dist(p['pos'],v['pos'])for v in eligible),default=None)}
        if result:
            v=next(v for v in eligible if graph.vianode(v)==result['target'])
            out.update(result);out['via_pos']=v['pos'];out['via_index']=v['index'];out['via_plane_connections']=v['plane_connections'];out['via_in2_power_tracks']=v['in2_power_connections'];out['straight_distance_mm']=math.dist(p['pos'],v['pos'])
            track_path=graph.shortest(graph.padnode(p),{graph.vianode(v)},ignore_pad_via_contact=True)
            out['explicit_track_path']=track_path
        else:out['connected_outer_copper_path_found']=False
        return out
    esd={ref:return_path(ref,'2')for ref in ['D1','D6','D7','D8']}
    for ref,result in esd.items():
        if 'length_mm'not in result:errors.append(ref+' has no outer-copper path to a directly connected GND plane via')
        elif result['length_mm']>1. or (result['minimum_track_width_mm']is not None and result['minimum_track_width_mm']<.2-1e-6):
            observations.append(ref+' GND path is longer than 1 mm or narrower than the prior dedicated 0.2 mm connection; review ESD return inductance')
    decoupling={}
    for ic,pin,ground_pin,cap in [('U3','2','5','C6'),('U6','1','2','C7'),('U2','2','3','C11')]:
        a=pad(ic,pin);c=pad(cap,'1');graph=graphs['3V3']
        direct=graph.shortest(graph.padnode(a),{graph.padnode(c)})
        decoupling[ic]={'capacitor':cap,'supply_pad_center_distance_mm':math.dist(a['pos'],c['pos']),'routed_supply_path_including_In2':direct,'ic_supply_to_distribution':return_path(ic,pin),'capacitor_supply_to_distribution':return_path(cap,'1'),'capacitor_ground_to_plane':return_path(cap,'2'),'ic_ground_to_plane':return_path(ic,ground_pin)}
        if math.dist(a['pos'],c['pos'])>2.:
            observations.append(f'{ic}/{cap} supply-pad separation exceeds 2 mm; assess loop using routed supply and ground-via locations')

    supply_graph=graphs['3V3']; supply_source=pad('U5','1')
    supply_paths={p['ref']+'.'+p['number']:supply_graph.shortest(supply_graph.padnode(p),{supply_graph.padnode(supply_source)}) for p in pads if p['net']=='3V3'}
    if any(path is None for path in supply_paths.values()):
        errors.append('A 3V3 pad has no routed copper path to regulator U5.1')

    drc=None
    if drc_path:
        raw=json.loads(Path(drc_path).read_text())
        counts=Counter(v.get('severity','unknown')for v in raw['violations'])
        drc={'path':str(drc_path),'sha256':sha(drc_path),'source':raw.get('source'),'date':raw.get('date'),'violations':dict(counts),'unconnected_count':len(raw['unconnected_items']),'schematic_parity_count':len(raw['schematic_parity']),'violation_types':dict(Counter(v['type']for v in raw['violations']))}
        if counts.get('error',0)or drc['unconnected_count']or drc['schematic_parity_count']:errors.append('Supplied DRC contains errors, unrouted connections, or schematic parity differences')
    if sha(board_path)!=initial_hash:raise RuntimeError('Board changed during read-only audit; use a stable snapshot')
    if sha(sch)!=initial_schematic_hash:raise RuntimeError('Schematic changed during audit; rerun against stable sources')
    result={'ok':not errors,'board':str(board_path),'board_sha256':initial_hash,'schematic':str(sch),'schematic_sha256':initial_schematic_hash,'netcheck':netcheck,'u1':{'position':xy(u1.GetPosition()),'rotation':u1.GetOrientationDegrees(),'layer':b.GetLayerName(u1.GetLayer())},'track_count':len(tracks),'via_count':len(vias),'track_width_min_mm':min(t['width']for t in tracks),'via_diameter_drill_mm':sorted({(v['diameter'],v['drill'])for v in vias}),'zones':[{key:value for key,value in z.items()if key!='poly'}for z in zones],'minimum_copper_edge':min_edge,'minimum_different_net_clearance_nominal':min_clearance,'via_drill_overlaps':drill_overlap,'same_net_via_overlaps':same_net_overlap,'mechanical':{'geometry_path':str(geometry_path),'geometry_sha256':sha(geometry_path),'copper_shape_changes':geometry_changes,'courtyard_overlap_pairs':court_overlap,'body_overlap_pairs':body_overlap,'body_edge_violations':body_edge},'esd_ground_returns':esd,'decoupling':decoupling,'drc':drc,'errors':errors,'observations':observations,'method_notes':['Read-only pcbnew analysis; current actual schematic netlist freshly exported by KiCad.', 'Path lengths follow copper track centerlines, with pad/via center-to-contact distances; inner planes excluded until reaching a plane-connected via.', 'Plane connection requires via annulus overlap with same-net filled inner-layer polygon.', 'Nominal copper clearances use analytic rounded primitives and polygonal custom pads. Zones are checked by the supplied KiCad DRC.', 'Observations on ESD/decoupling are engineering review prompts, not standalone proof of EMC or transient performance.']}
    result['project_rules']=project_rules
    result['coordinates']={'board_center_on_sheet_mm':sheet_center,
                           'analysis_origin':'PCB center',
                           'note':'Geometry was translated in memory for analysis; the saved PCB was not modified.'}
    result['routed_3V3_distribution']={'source':'U5.1','layer':'In2.Cu','widths_mm':sorted({t['width']for t in tracks if t['net']=='3V3'and t['layer']==k.In2_Cu}),'pad_paths_to_regulator':supply_paths}
    result['power_tvs_rs422_pinmap']={'ok':not pinmap_errors,'errors':pinmap_errors,'checked_pins':len(expected_polarity)}
    result['via_drill_pad_gap']={'required_nominal_mm':.025,'minimum':drill_gaps[0]if drill_gaps else None,'violations':narrow_drill_gaps,'smd_pad_count':sum(p['smd']for p in pads),'via_pad_comparisons':len(drill_gaps)}
    result['via_tenting']={'all_tented_front_and_back':not untented,'untented_vias':untented,'count':len(vias)}
    result['via_drill_pair_clearance']={'required_nominal_mm':.25,'minimum':drill_pair_gaps[0]if drill_pair_gaps else None,'violations':drill_pair_violations}
    result['pad_clearances']={'minimum_including_within_footprints':min(pad_gaps,key=lambda row:row['clearance_mm']),'minimum_between_different_footprints':min(interfootprint_gaps,key=lambda row:row['clearance_mm'])}
    result['method_notes'].append('Drill-to-pad distances use analytic circle/rectangle/roundrect boundaries and polygon geometry for custom MCU pads; nominal 0.025 mm minimum is enforced with 0.000001 mm numerical tolerance.')
    result['method_notes'].append('Same-net via annulus overlaps are informational. Nominal drill-to-drill spacing of at least 0.25 mm is required for every via pair.')
    Path(output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({key:result[key]for key in ['ok','board_sha256','netcheck','minimum_copper_edge','minimum_different_net_clearance_nominal','errors','observations']},indent=2))
    print('ESD',[(r,{key:v for key,v in row.items()if key!='path'})for r,row in esd.items()])
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('board',type=Path)
    parser.add_argument('--drc',type=Path)
    parser.add_argument('--project',type=Path)
    parser.add_argument('--output',type=Path,default=Path(__file__).with_name('independent_final_audit.json'))
    args=parser.parse_args()
    result = audit(args.board,args.drc,args.output,args.project)
    raise SystemExit(0 if result['ok'] else 1)
