"""Ten mixed sets, physical 10 mm top/bottom handling rails and routed solid tabs.
Canonical unit PCBs remain unchanged. All output coordinates are top-view, +Y up.
"""
import gc, hashlib, json, math, re, shutil, subprocess, sys
from pathlib import Path
gc.disable()
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'.git/all_ground_gerber_20261005/pydeps'))
sys.path.insert(0,str(ROOT/'.git/6layer_impl_20261005/pydeps'))
import pcbnew as k
from shapely.geometry import Point, LineString, Polygon, box, mapping
from shapely.ops import unary_union, substring
from gerbonara import GerberFile, ExcellonFile
from gerbonara.cam import FileSettings
from gerbonara.utils import MM
OLD=ROOT/'manufacturing/20261009_PPG_UART_1plus1'
CLI=r'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
W,H=157.0,177.0;TOOL_R=1.0;PATH_OFFSET=1.0001;NECK=3.0
layers=['F_Cu','In1_Cu','In2_Cu','In3_Cu','In4_Cu','B_Cu','F_Mask','B_Mask','F_Silkscreen','B_Silkscreen','F_Paste','B_Paste','Edge_Cuts']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=json.loads((OLD/'array_manifest.json').read_text(encoding='utf-8'))
for s in base['unit_sources'].values():s.pop('offset',None)
for name,s in base['unit_sources'].items(): assert sha(Path(s['path']))==s['sha'],name+' source changed'
for folder in ['engineering','gerber','verification','review','reference']:(OUT/folder).mkdir(parents=True,exist_ok=True)
instances=[]
for row_from_top in range(5):
    r=4-row_from_top
    for c in range(2):
        sid=f'S{row_from_top*2+c+1:02d}'
        for unit,off in [('UART',[5+78.5*c,12+32*r]),('PPG',[66.75+78.5*c,24.5+32*r])]:
            instances.append(dict(set_id=sid,board=unit,column=c+1,row_from_top=row_from_top+1,offset_mm=off,rotation_deg=0))
tooling=[dict(ref=f'GH{i+1}',kind='NPTH',diameter_mm=3.0,x_mm=x,y_mm=y) for i,(x,y) in enumerate([(3.5,5),(153.5,5),(3.5,172),(153.5,172)])]
fids=[dict(ref=f'FID_{side[0]}{i+1}',kind='FIDUCIAL',side=side,copper_diameter_mm=1.0,mask_diameter_mm=3.0,paste=False,x_mm=x,y_mm=y) for side in ['TOP','BOTTOM'] for i,(x,y) in enumerate([(10,5),(147,5),(10,172)])]
def periodic_paths(path,gaps):
    length=path.length;excluded=[]
    for d,half in gaps:
        a,b=d-half,d+half
        if a<0:excluded.extend([(0,b),(a+length,length)])
        elif b>length:excluded.extend([(a,length),(0,b-length)])
        else:excluded.append((a,b))
    excluded.sort();merged=[]
    for a,b in excluded:
        if merged and a<=merged[-1][1]:merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
        else:merged.append((a,b))
    keep=[];cursor=0
    for a,b in merged:
        if a>cursor+1e-9:keep.append(substring(path,cursor,a))
        cursor=b
    if cursor<length-1e-9:keep.append(substring(path,cursor,length))
    return keep,[substring(path,a,b) for a,b in merged]
routepaths=[];cutpaths=[];finished=[];tabs=[]
for inst in instances:
    unit=inst['board'];x,y=inst['offset_mm'];gaps=[]
    if unit=='UART':
        shape=box(x,y,x+52,y+25)
        path=LineString(shape.buffer(PATH_OFFSET,quad_segs=128).exterior.coords)
        for label,centers,edge_y,tool_y in [('bottom',[6.5,28,45.5],y,y-PATH_OFFSET),('top',[6.5,26,45.5],y+25,y+25+PATH_OFFSET)]:
            for j,tx in enumerate(centers):
                center=Point(x+tx,tool_y);gaps.append((path.project(center),(NECK+2*TOOL_R)/2))
                tabs.append(dict(id=f'{inst["set_id"]}_UART_{label}_{j+1}',set_id=inst['set_id'],board=unit,edge_center_mm=[x+tx,edge_y],tool_center_mm=[x+tx,tool_y],neck_mm=NECK,toolpath_gap_mm=5.0))
    else:
        shape=Point(x,y).buffer(6.75,quad_segs=2048)
        radius=6.75+PATH_OFFSET
        path=LineString([(x+radius*math.cos(i*2*math.pi/8192),y+radius*math.sin(i*2*math.pi/8192)) for i in range(8193)])
        half=radius*math.asin((NECK+2*TOOL_R)/(2*radius))
        for angle in [0,135,220]:
            a=math.radians(angle);center=Point(x+radius*math.cos(a),y+radius*math.sin(a))
            gaps.append((path.project(center),half))
            tabs.append(dict(id=f'{inst["set_id"]}_PPG_{angle}',set_id=inst['set_id'],board=unit,edge_center_mm=[x+6.75*math.cos(a),y+6.75*math.sin(a)],tool_center_mm=[center.x,center.y],angle_deg_y_up=angle,neck_mm=NECK,toolpath_gap_mm=2*half))
    paths,cuts=periodic_paths(path,gaps);routepaths.extend(paths);cutpaths.extend(cuts);finished.append(shape)
voids=unary_union([p.buffer(TOOL_R,quad_segs=128) for p in routepaths])
outer=box(0,0,W,H);material=outer.difference(voids)
assert material.is_valid and material.geom_type=='Polygon','Carrier is disconnected'
intrusion=max(voids.intersection(p).area for p in finished)
assert intrusion<1e-9,('Route enters a finished board',intrusion)
for p in tooling:assert material.contains(Point(p['x_mm'],p['y_mm']).buffer(1.5)),p
for p in fids:assert material.contains(Point(p['x_mm'],p['y_mm']).buffer(1.5)),p
geometry={'type':'FeatureCollection','features':[
 dict(type='Feature',properties={'kind':'substrate'},geometry=mapping(material)),
 dict(type='Feature',properties={'kind':'route_void'},geometry=mapping(voids)),
 *[dict(type='Feature',properties={'kind':'route_centerline','index':i},geometry=mapping(p)) for i,p in enumerate(routepaths)],
 *[dict(type='Feature',properties={'kind':'final_cut_centerline','index':i},geometry=mapping(p)) for i,p in enumerate(cutpaths)],
 *[dict(type='Feature',properties={'kind':'finished_board',**inst},geometry=mapping(shape)) for inst,shape in zip(instances,finished)]]}
(OUT/'engineering/panel_geometry.geojson').write_text(json.dumps(geometry,separators=(',',':')),encoding='utf-8')
manifest=dict(date='2026-10-09',units_per_set={'PPG':1,'UART':1},set_count=10,board_count=20,grid={'columns':2,'rows':5},panel_size_mm=[W,H],rail_width_mm={'top':10,'bottom':10},minimum_side_carrier_mm=3,coordinate_system='mm; origin physical panel bottom-left; top view +X right +Y up; no mirroring',unit_sources=base['unit_sources'],instances=instances,tooling_holes=tooling,fiducials=fids,tabs=tabs,solid_tab_count=len(tabs),nominal_tab_neck_mm=NECK,router_diameter_mm=2.0,separation='Fixture-supported CNC removal of solid tabs after assembly; no manual snapping, V-score or mouse-bites',copper_layer_count=6,nominal_thickness_mm=.8,source_pth_count=1640,unit_npth_count=40,guide_npth_count=4,substrate_connected=True,route_intrusion_into_finished_boards_mm2=intrusion)
(OUT/'panel_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
# Native mechanical carrier: manufacturing coordinates map to native (x, H-y).
b=k.BOARD();b.SetCopperLayerCount(6);b.GetDesignSettings().SetBoardThickness(k.FromMM(.8));b.GetDesignSettings().SetAuxOrigin(k.VECTOR2I_MM(0,H))
V=lambda p:k.VECTOR2I_MM(p[0],H-p[1])
refs=[]
def edge_ring(coords,layer=k.Edge_Cuts):
    for a,z in zip(coords,list(coords)[1:]):
        if math.dist(a,z)<1e-6:continue
        s=k.PCB_SHAPE(b);s.SetShape(k.SHAPE_T_SEGMENT);s.SetStart(V(a));s.SetEnd(V(z));s.SetWidth(k.FromMM(.05));s.SetLayer(layer);b.Add(s)
edge_ring(list(material.exterior.coords))
for ring in material.interiors:edge_ring(list(ring.coords))
def text(text,x,y,layer=k.F_SilkS,size=1.0,mirror=False):
    t=k.PCB_TEXT(b);t.SetText(text);t.SetPosition(V((x,y)));t.SetLayer(layer);t.SetTextSize(k.VECTOR2I_MM(size,size));t.SetTextThickness(k.FromMM(.15));t.SetMirrored(mirror);b.Add(t)
for p in tooling:
    fp=k.FOOTPRINT(b);b.Add(fp);fp.SetReference(p['ref']);fp.SetValue('Guide_NPTH_3mm');fp.SetPosition(V((p['x_mm'],p['y_mm'])));fp.SetAttributes(k.FP_EXCLUDE_FROM_POS_FILES|k.FP_EXCLUDE_FROM_BOM);fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
    pad=k.PAD(fp);pad.SetNumber('');pad.SetAttribute(k.PAD_ATTRIB_NPTH);pad.SetShape(k.PAD_SHAPE_CIRCLE);pad.SetSize(k.VECTOR2I_MM(3,3));pad.SetDrillSize(k.VECTOR2I_MM(3,3));pad.SetLayerSet(k.LSET.AllCuMask());pad.SetPosition(fp.GetPosition());fp.Add(pad)
for p in fids:
    fp=k.FOOTPRINT(b);b.Add(fp);fp.SetReference(p['ref']);fp.SetValue('Fiducial_1mm_Mask3mm');fp.SetPosition(V((p['x_mm'],p['y_mm'])));fp.SetAttributes(k.FP_EXCLUDE_FROM_POS_FILES|k.FP_EXCLUDE_FROM_BOM);fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
    ly=k.F_Cu if p['side']=='TOP' else k.B_Cu
    if ly==k.B_Cu:fp.SetLayerAndFlip(k.B_Cu)
    pad=k.PAD(fp);pad.SetNumber('1');pad.SetAttribute(k.PAD_ATTRIB_SMD);pad.SetShape(k.PAD_SHAPE_CIRCLE);pad.SetSize(k.VECTOR2I_MM(1,1));ls=k.LSET();ls.AddLayer(ly);ls.AddLayer(k.F_Mask if ly==k.F_Cu else k.B_Mask);pad.SetLayerSet(ls);pad.SetLocalSolderMaskMargin(k.FromMM(1));pad.SetPosition(fp.GetPosition());fp.Add(pad)
for ly,mirror in [(k.F_SilkS,False),(k.B_SilkS,True)]:
    text('PPG + UART | 10 SETS | 6L / 0.8 mm',78.5,172,ly,1.2,mirror)
    text('157 x 177 mm | CNC TAB CUT | 2026-10-09',78.5,5,ly,1.0,mirror)
    text('-->',135,5,ly,1.5,mirror)
for inst in instances:
    if inst['board']=='UART':text(inst['set_id'],inst['offset_mm'][0]-3.5,inst['offset_mm'][1]+12.5,k.F_SilkS,.8)
carrier=OUT/'engineering/Panel_Carrier_Only.kicad_pcb';k.SaveBoard(str(carrier),b)
carrierout=OUT/'engineering/carrier_gerber';carrierout.mkdir(exist_ok=True)
logs=[]
def run(args):
    proc=subprocess.run([CLI,*map(str,args)],capture_output=True,text=True,encoding='utf-8',errors='replace',creationflags=0x08000000)
    logs.append(dict(command=[CLI,*map(str,args)],returncode=proc.returncode,output=proc.stdout+proc.stderr));assert proc.returncode==0,logs[-1]
run(['pcb','export','gerbers','--layers','F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts','--subtract-soldermask','--use-drill-file-origin','--no-protel-ext','--no-netlist','--precision','6','-o',str(carrierout)+'/',carrier])
run(['pcb','export','drill','--format','excellon','--excellon-units','mm','--excellon-zeros-format','decimal','--drill-origin','plot','--excellon-separate-th','-o',str(carrierout)+'/',carrier])
settings=FileSettings(unit=MM,number_format=(4,6),zeros='leading');records=[]
for suffix in layers:
    if suffix=='Edge_Cuts':g=GerberFile.open(carrierout/'Panel_Carrier_Only-Edge_Cuts.gbr')
    else:
        g=None
        for inst in instances:
            unit=inst['board'];q=GerberFile.open(OLD/'units'/unit/f'{unit}-{suffix}.gbr');q.offset(*inst['offset_mm'],unit=MM)
            if g is None:g=q
            else:g.merge(q)
        extra=carrierout/f'Panel_Carrier_Only-{suffix}.gbr'
        if extra.is_file():g.merge(GerberFile.open(extra))
    for key in ['.MD5','.ProjectId','.SameCoordinates','.CreationDate']:g.file_attrs.pop(key,None)
    g.file_attrs['.GenerationSoftware']=('Gerbonara','PPG_UART_10sets_GuideRails','20261009')
    path=OUT/'gerber'/f'PPG_UART_10sets-{suffix}.gbr';g.save(path,settings=settings)
    path.write_text(re.sub(r'^G75$','G75*',path.read_text(encoding='utf-8'),flags=re.M),encoding='utf-8')
    records.append(dict(file='gerber/'+path.name,layer=suffix,sha256=sha(path),object_count=len(g.objects)))
for kind in ['PTH','NPTH']:
    d=None
    for inst in instances:
        unit=inst['board'];q=ExcellonFile.open(OLD/'units'/unit/f'{unit}-{kind}.drl',plated=kind=='PTH');q.offset(*inst['offset_mm'],unit=MM)
        if d is None:d=q
        else:d.merge(q)
    if kind=='NPTH':d.merge(ExcellonFile.open(carrierout/'Panel_Carrier_Only-NPTH.drl',plated=False))
    path=OUT/'gerber'/f'PPG_UART_10sets-{kind}.drl';d.save(path,settings=settings)
    path.write_text(path.read_text(encoding='utf-8').replace('M48\n','M48\n;TYPE='+('PLATED' if kind=='PTH' else 'NON_PLATED')+'\nG90\n',1),encoding='utf-8')
    records.append(dict(file='gerber/'+path.name,kind=kind,sha256=sha(path),hit_count=len(d.objects)))
# Finished profiles are reference only; never overlay them onto production Edge.Cuts.
g=None
for inst in instances:
    unit=inst['board'];q=GerberFile.open(OLD/'units'/unit/f'{unit}-Edge_Cuts.gbr');q.offset(*inst['offset_mm'],unit=MM)
    if g is None:g=q
    else:g.merge(q)
path=OUT/'reference/FINISHED_UNITS_REFERENCE_ONLY.gbr';g.save(path,settings=settings);path.write_text(re.sub(r'^G75$','G75*',path.read_text(),flags=re.M),encoding='utf-8')
manifest['files']=records;manifest['source_hashes_unchanged']=all(sha(Path(s['path']))==s['sha'] for s in base['unit_sources'].values())
(OUT/'panel_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
(OUT/'verification/export_log.json').write_text(json.dumps(logs,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'panel_mm':[W,H],'sets':10,'solid_tabs':len(tabs),'routing_cutouts':len(material.interiors),'connected':material.geom_type=='Polygon','PTH':1640,'NPTH':44,'source_unchanged':manifest['source_hashes_unchanged']}))
