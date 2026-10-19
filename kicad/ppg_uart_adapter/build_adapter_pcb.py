"""Build the reviewed adapter layout/routing; output to an explicit candidate path."""
from pathlib import Path
import sys, json, math, gc, shutil, xml.etree.ElementTree as ET
import pcbnew as k
HERE=Path(__file__).resolve().parent; REPO=HERE.parent.parent
sys.path.insert(0,str(HERE.parent))
from schematic_metadata import load_schematic_metadata
from layout_schematic_v08 import parse, children, prop
from pcb_geometry import item_geometry, polyset_geometry
from mounting_holes import HOLES, apply_mounting_layout
from edge_ports import apply_edge_ports
from shapely.geometry import Point, LineString, box
from shapely.ops import unary_union
from collections import defaultdict
M=k.FromMM; V=k.VECTOR2I_MM
gc.disable()
OUT=Path(sys.argv[1]).resolve();OUT.parent.mkdir(parents=True,exist_ok=True)
meta=load_schematic_metadata(HERE/'ppg_uart_adapter_v01.kicad_sch')
symbol_fields={str(prop(s,'Reference')[2]):{str(p[1]):str(p[2]) for p in children(s,'property')} for s in children(parse((HERE/'ppg_uart_adapter_v01.kicad_sch').read_text(encoding='utf-8')),'symbol')}
b=k.BOARD();ds=b.GetDesignSettings();ds.SetCopperLayerCount(6);ds.SetBoardThickness(M(.8))
for name,value in [('m_MinClearance',.15),('m_TrackMinWidth',.15),('m_ViasMinSize',.5),('m_MinThroughDrill',.25),('m_MicroViasMinDrill',.25),('m_MicroViasMinSize',.5),('m_CopperEdgeClearance',.3),('m_HoleClearance',.2),('m_SolderMaskMinWidth',.1)]:setattr(ds,name,M(value))
try:nc=ds.m_NetSettings.GetDefaultNetclass()
except:nc=ds.m_NetSettings.m_DefaultNetClass
nc.SetClearance(M(.15));nc.SetTrackWidth(M(.2));nc.SetViaDiameter(M(.5));nc.SetViaDrill(M(.25));nc.SetuViaDiameter(M(.5));nc.SetuViaDrill(M(.25));ds.SetCustomViaSize(M(.5));ds.SetCustomViaDrill(M(.25))
LAYERS=[k.F_Cu,k.In1_Cu,k.In2_Cu,k.In3_Cu,k.In4_Cu,k.B_Cu]
b.SetLayerType(k.In1_Cu,k.LT_POWER);b.SetLayerType(k.In4_Cu,k.LT_POWER)
nets={}
for name in sorted(meta['net_names']):
    n=k.NETINFO_ITEM(b,name);b.Add(n);nets[name.lstrip('/')]=n
# Coordinates in the KiCad top-view editor. All footprints lie on B.Cu.
POS={
 'J1':(2.5,1.5,0),'J2':(1.5,10,270),'J3':(26.5,13,270),
 'FB1':(6.375,2.7,0),'U1':(12,5,0),'C1':(5.6,5,180),'C3':(5.6,7,180),
 'R9':(19,5,0),'C2':(23.8,2.8,0),'C6':(23.8,4.6,0),'C7':(23.8,6.4,0),'C8':(23.8,8.2,0),
 'D1':(5,14.5,180),'D2':(5,18.1,180),'R1':(8,14.5,270),
 'R2':(10.3,13.55,0),'R3':(10.3,15.45,0),'U3':(14,14.5,180),
 'R4':(10.3,17.15,180),'R5':(10.3,19.05,180),'U2':(14,18.1,180),
 'C5':(17.3,12.3,90),'C4':(16.8,19.825,270),'R6':(21.8,19,90),
 'R7':(20.3,14.8,0),'R8':(20.3,16.6,180),
 'D3':(23.5,14.45,90),'D4':(23.5,16.95,270),
}
assert set(POS) | set(HOLES) == set(meta['components'])
fps={};padmap={};kept=[]
def absolute(p):return (100+p[0],100+p[1])
def xy(p):return (k.ToMM(p.x)-100,k.ToMM(p.y)-100)
for ref,c in meta['components'].items():
    if ref in HOLES: continue  # mechanical footprints are added after routing
    lib,part=c['footprint'].split(':',1)
    path=HERE/'Adapter.pretty' if lib=='Adapter' else Path(r'C:\Program Files\KiCad\10.0\share\kicad\footprints')/(lib+'.pretty')
    f=k.FootprintLoad(str(path),part);assert f,ref
    f.SetFPID(k.LIB_ID(lib,part));f.SetReference(ref);f.SetValue(c['value']);b.Add(f)
    x,y,rot=POS[ref];f.SetPosition(V(*absolute((x,y))));f.SetLayerAndFlip(k.B_Cu);f.SetOrientationDegrees(rot)
    f.SetPath(k.KIID_PATH(c['path']))
    f.SetAttributes(f.GetAttributes() & ~k.FP_EXCLUDE_FROM_BOM)
    for field,value in c['fields'].items():f.SetField(field,value);f.GetField(field).SetVisible(False)
    for field in ['Voltage','Tolerance','Dielectric']:
        if field in symbol_fields[ref]:f.SetField(field,symbol_fields[ref][field]);f.GetField(field).SetVisible(False)
    for pad in f.Pads():
        name=meta['pad_nets'][ref,pad.GetNumber()];pad.SetNet(nets[name.lstrip('/')]);padmap.setdefault((ref,pad.GetNumber()),[]).append(pad)
    f.Reference().SetLayer(k.B_Fab);f.Reference().SetTextSize(V(.6,.6));f.Reference().SetTextThickness(M(.1));f.Value().SetVisible(False)
    for graphic in list(f.GraphicalItems()):
        if graphic.GetClass()=='PCB_TEXT' and graphic.GetText()=='${REFERENCE}':
            kept.append(graphic);f.Remove(graphic)
    f.Reference().SetTextAngle(k.EDA_ANGLE(0,k.DEGREES_T));f.Reference().SetKeepUpright(True)
    refpos={'J1':(3.4,2.5),'J2':(1.5,8.8),'J3':(26.5,11.8)}.get(ref,(x,y))
    f.Reference().SetPosition(V(*absolute(refpos)))
    refsize=.4 if ref=='FB1' else .45 if ref in {'D3','D4'} else .5 if ref.startswith(('R','C')) else .6
    f.Reference().SetTextSize(V(refsize,refsize));f.Reference().SetTextThickness(M(.08))
    fps[ref]=f

def pp(ref,num,index=0):return xy(padmap[ref,str(num)][index].GetPosition())
def route(net,points,width=.2,layer=k.B_Cu):
    for a,c in zip(points,points[1:]):
        if math.dist(a,c)<.00001:continue
        t=k.PCB_TRACK(b);t.SetStart(V(*absolute(a)));t.SetEnd(V(*absolute(c)));t.SetLayer(layer);t.SetWidth(M(width));t.SetNet(nets[net]);b.Add(t)

def via(net,p):
    for t in b.GetTracks():
        if t.GetClass()=='PCB_VIA' and math.dist(xy(t.GetPosition()),p)<.001:
            assert t.GetNetname().lstrip('/')==net;return
    v=k.PCB_VIA(b);v.SetPosition(V(*absolute(p)));v.SetViaType(k.VIATYPE_THROUGH);v.SetLayerPair(k.F_Cu,k.B_Cu);v.SetWidth(M(.5));v.SetDrill(M(.25));v.SetNet(nets[net]);b.Add(v)
# Cable/TVS/series/IC paths are continuous through the TVS signal land centre.
for jpin,d,dp,r,rp,ic,ip in [('3','D1','1','R2','1','U3','6'),('4','D1','2','R3','1','U3','4'),('5','D2','1','R4','2','U2','6'),('6','D2','2','R5','2','U2','4')]:
    start=pp('J2',jpin);land=pp(d,dp);dest=pp(r,rp);net=padmap['J2',jpin][0].GetNetname().lstrip('/')
    # Small pitch transition is made at the cable side, with a single diagonal.
    route(net,[start,(start[0]+abs(land[1]-start[1]),land[1]),land,dest],.2)
    other='2' if rp=='1' else '1';net2=padmap[r,other][0].GetNetname().lstrip('/')
    route(net2,[pp(r,other),pp(ic,ip)],.2)
# R1 lands intersect the existing pair after D1; no overlapping branch tracks.
for jpin,d,r,rp,net in [('2','D3','R7','2','TX_OUT'),('3','D4','R8','1','RX_IN')]:route(net,[pp('J3',jpin),pp(d,'1'),pp(r,rp)],.2)
route('UART_TX_IC',[pp('U3','3'),(18.825,15.45),pp('R7','1')],.2)
route('UART_RX_IC',[pp('U2','1'),(18.925,17.15),pp('R8','2')],.2)
route('UART_RX_IC',[pp('R8','2'),(21.05,18.175),pp('R6','2')],.2)
# Shared 9V passes directly to PPG; only the local LDO branch uses FB1.
route('9V_SHARED',[pp('J1','1'),(2.5,2.7),pp('FB1','1')],.7)
route('9V_SHARED',[(2.5,2.7),(2.5,9),pp('J2','1')],.7)
route('9V_LDO',[pp('FB1','2'),pp('U1','3')],.5)
route('9V_LDO',[(7.4,2.7),(7.4,7),pp('C3','1')],.5)
route('9V_LDO',[pp('C1','1'),(7.4,5)],.5)
# Both U1 pad2 lands are connected; its large tab is VOUT, never GND.
route('3V3',[pp('U1','2',0),pp('U1','2',1),pp('R9','1')],.75)
route('COUT_BULK',[pp('R9','2'),(22.2,5)],.65)
route('COUT_BULK',[(22.2,2.8),(22.2,8.2)],.65)
for ref in ['C2','C6','C7','C8']:route('COUT_BULK',[(22.2,POS[ref][1]),pp(ref,'1')],.5)
# 3V3 long distribution on L4, local decoupling connections on B.Cu.
route('3V3',[(16.5,5),(16.5,6.8)],.75);via('3V3',(16.5,6.8))
route('3V3',[(16.5,6.8),(17.3,7.6),(17.3,13.8)],.65,k.In3_Cu)
route('3V3',[(17.3,13.8),(18.2,14.7),(18.2,18.75),(17.9,19.05)],.65,k.In3_Cu)
route('3V3',[(17.3,10.2),(23.6,10.2),(25.3,11.9),(25.3,13)],.65,k.In3_Cu)
via('3V3',(17.3,13.8));via('3V3',(17.9,19.05));via('3V3',(25.3,13))
route('3V3',[(25.3,13),pp('J3','1')],.5)
route('3V3',[pp('C5','1'),(17.3,13.8)],.4)
route('3V3',[pp('U3','1'),(16.825,13.55),pp('C5','1')],.4)
route('3V3',[pp('U2','2'),(16.1,18.1),(16.1,19.05),pp('U2','3')],.4)
route('3V3',[(16.1,19.05),pp('C4','1'),(17.9,19.05)],.4)
route('3V3',[pp('R6','1'),(21.8,20.7)],.3);via('3V3',(21.8,20.7))
route('3V3',[(17.9,19.05),(20.15,19.05),(21.8,20.7)],.5,k.In3_Cu)
# Pad escapes to adjacent ground vias. Do not put unfilled through vias in SMD lands.
GROUND={('J1','2'):(5.4,1.5),('J2','2'):(2.7,11.8),('J3','4'):(25.3,18.4),
('U1','1'):(8.85,8.7),('C1','2'):(3.9,5),('C3','2'):(3.9,7),
('D1','3'):(3.0,14.5),('D2','3'):(3.0,18.1),('U3','2'):(16.05,14.5),('U3','5'):(11.95,14.5),('U2','5'):(11.95,18.1),
('C5','2'):(18.3,11.525),('C4','2'):(17.9,20.6),('D3','2'):(23.5,13.3),('D4','2'):(23.5,18.1)}
for ref in ['C2','C6','C7','C8']:GROUND[ref,'2']=(25.7,POS[ref][1])
for (ref,pin),v in GROUND.items():route('GND',[pp(ref,pin),v],.3 if ref.startswith('D') else .4);via('GND',v)
# Outline and full-board ground on all six layers.
for a,c in [((0,0),(28,0)),((28,0),(28,22)),((28,22),(0,22)),((0,22),(0,0))]:
    e=k.PCB_SHAPE(b);e.SetShape(k.SHAPE_T_SEGMENT);e.SetStart(V(*absolute(a)));e.SetEnd(V(*absolute(c)));e.SetLayer(k.Edge_Cuts);e.SetWidth(M(.05));b.Add(e)
for layer in LAYERS:
    z=k.ZONE(b);z.SetLayer(layer);z.SetNet(nets['GND']);z.SetAssignedPriority(0);z.SetLocalClearance(M(.15));z.SetMinThickness(M(.15));z.SetPadConnection(k.ZONE_CONNECTION_FULL);z.SetIslandRemovalMode(k.ISLAND_REMOVAL_MODE_ALWAYS)
    for p in [(0,0),(28,0),(28,22),(0,22)]:z.AppendCorner(V(*absolute(p)),-1)
    b.Add(z)
# Ground stitching, filtered against all foreign pads/tracks, preserves outer ground rim.
diag=defaultdict(int);foreign=[]
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetNetname().lstrip('/')!='GND':foreign.append(item_geometry(p,k.B_Cu,diag,.00001))
for t in b.GetTracks():
    if t.GetNetname().lstrip('/')!='GND':foreign.append(item_geometry(t,t.GetLayer(),diag,.00001))
obstacles=unary_union(foreign)
seeds=[(x,.7) for x in [1,6.5,9,12,15,18,21,24,27]]+[(x,21.3) for x in [1,4,7,10,13,16,19,22,25,27]]
seeds += [(.7,y) for y in [2,5,8,10.9,12.7,14.5,16.3,18.1,19.9]]+[(27.3,y) for y in [2,5,8,10.5,13.9,15.7,17.5,20]]
seeds += [(10,10.5),(14,10.5),(20,10.5),(7.5,10.5),(20,20.7)]
stitched=[]
for p in seeds:
    if Point(*absolute(p)).distance(obstacles)<.405:continue
    if any(t.GetClass()=='PCB_VIA' and math.dist(p,xy(t.GetPosition()))<.71 for t in b.GetTracks()):continue
    via('GND',p);stitched.append(p)
# Silk is limited to the empty top face; assembly references remain on B.Fab.
def text(txt,p,layer=k.F_SilkS,size=.7):
    size=max(.8,size)
    t=k.PCB_TEXT(b);t.SetText(txt);t.SetPosition(V(*absolute(p)));t.SetLayer(layer);t.SetTextSize(V(size,size));t.SetTextThickness(M(.12));b.Add(t)
text('PPG UART ADAPTER',(14,2.5),size=1.0);text('9V / 3V3 UART',(14,4),size=.8)
text('PPG',(3.0,8.5));text('UART',(25,11));text('9V  GND',(3.4,3.6),size=.6)
for i,name in enumerate(['9V','GND','TXP','TXN','RXP','RXN']):text(name,(4.1,10+i*1.8),size=.65)
for i,name in enumerate(['3V3','TX','RX','GND']):text(name,(22.4,13+i*1.8),size=.65)
text('28 x 22 mm | 6L / 0.8 mm',(14,8.8),size=.7)
mounting=apply_mounting_layout(b,meta)
edge_ports=apply_edge_ports(b)
ground_via_points={xy(t.GetPosition()) for t in b.GetTracks() if isinstance(t,k.PCB_VIA) and t.GetNetname()=='/GND'}
mounting['added_ground_vias_mm']=[p for p in mounting['added_ground_vias_mm'] if (p[0]-100,p[1]-100) in ground_via_points]
k.SaveBoard(str(OUT),b)
(OUT.parent/'mounting_layout.json').write_text(json.dumps(mounting,indent=2)+'\n')
(OUT.parent/'edge_port_layout.json').write_text(json.dumps(edge_ports,indent=2)+'\n')
# Candidate project uses normal active checks, without exclusions from the PPG board.
project=json.loads((REPO/'kicad/ppg_pcb_v08.kicad_pro').read_text(encoding='utf-8'))
project['meta']['filename']=OUT.with_suffix('.kicad_pro').name
project['board']['design_settings']['drc_exclusions']=[]
project['board']['design_settings']['rule_severities']['missing_courtyard']='warning'
project['board']['design_settings']['rule_severities']['lib_footprint_mismatch']='warning'
project['pcbnew']={};project['text_variables']={}
project['board']['design_settings']['rules']['min_clearance']=.15
project['board']['design_settings']['rules']['min_track_width']=.15
project['board']['design_settings']['rules']['min_via_diameter']=.5
project['board']['design_settings']['rules']['min_through_hole_diameter']=.25
project['board']['design_settings']['rules']['min_microvia_drill']=.25
project['board']['design_settings']['rules']['min_microvia_diameter']=.5
project['board']['design_settings']['via_dimensions']=[{'diameter':.5,'drill':.25}]
for netclass in project['net_settings']['classes']:
    netclass.update({'via_diameter':.5,'via_drill':.25,'microvia_diameter':.5,'microvia_drill':.25})
OUT.with_suffix('.kicad_pro').write_text(json.dumps(project,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['fp-lib-table','sym-lib-table','Adapter.kicad_sym']:
    if (HERE/name).resolve() != (OUT.parent/name).resolve():
        shutil.copy2(HERE/name,OUT.parent/name)
if HERE.resolve() != OUT.parent.resolve():
    shutil.copytree(HERE/'Adapter.pretty',OUT.parent/'Adapter.pretty',dirs_exist_ok=True)
OUT.with_suffix('.kicad_dru').write_text('''(version 1)
(rule "L2 dedicated GND" (layer "In1.Cu") (constraint disallow track))
(rule "All traces at least 0.15 mm" (constraint track_width (min 0.15mm)))
(rule "Signal/GND via" (condition "A.Type == 'Via' && !(A.NetName == '/3V3' || A.NetName == '/9V_SHARED' || A.NetName == '/9V_LDO' || A.NetName == '/COUT_BULK')") (constraint via_diameter (min 0.50mm) (max 0.50mm)) (constraint hole_size (min 0.25mm) (max 0.25mm)))
(rule "Power via" (condition "A.Type == 'Via' && (A.NetName == '/3V3' || A.NetName == '/9V_SHARED' || A.NetName == '/9V_LDO' || A.NetName == '/COUT_BULK')") (constraint via_diameter (min 0.50mm) (max 0.50mm)) (constraint hole_size (min 0.25mm) (max 0.25mm)))
''',encoding='utf-8')
positions={f.GetReference():(*xy(f.GetPosition()),f.GetOrientationDegrees()) for f in b.GetFootprints()}
(OUT.parent/'placement_and_routing.json').write_text(json.dumps({'positions':positions,'pads':{ref:{pin:[xy(p.GetPosition()) for p in pads] for (r,pin),pads in padmap.items() if r==ref} for ref in positions},'ground_stitches':[(x-100,y-100) for x,y in edge_ports['reused_ground_stitch_positions_mm']],'mounting':mounting,'edge_ports':edge_ports},indent=2)+'\n')
print('saved',OUT,'tracks/vias',len(b.GetTracks()),'ground stitch vias',len(stitched))
