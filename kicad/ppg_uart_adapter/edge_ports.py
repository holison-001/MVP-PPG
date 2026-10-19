"""Route the adapter with cable pads on the actual board perimeter."""
from pathlib import Path
import math
from collections import defaultdict
import pcbnew as k
from pcb_geometry import item_geometry
from shapely.geometry import Point
from shapely.ops import unary_union
from mounting_holes import HOLES, HEAD_CLEARANCE_DIAMETER

M, V = k.FromMM, k.VECTOR2I_MM
PORT_POSITIONS = {'J1': (102.5, 99.75, 0), 'J2': (101.5, 122.25, 0), 'J3': (121.1, 122.25, 0)}
POSITIONS = {
    **PORT_POSITIONS,
    'U3': (106, 111, 270), 'U2': (109.6, 111, 270),
    'D1': (106, 119.35, 270), 'D2': (109.6, 119.35, 270),
    'R2': (105.05, 114.4, 90), 'R3': (106.95, 114.4, 90), 'R1': (106, 116.65, 0),
    'R4': (108.65, 114.4, 270), 'R5': (110.55, 114.4, 270),
    'C5': (102.7, 109.8, 180), 'C4': (112.2, 110.2, 270),
    'D3': (122.55, 120.4, 180), 'D4': (125.05, 120.4, 0),
    'R7': (122.9, 118.3, 270), 'R8': (124.7, 118.3, 90), 'R6': (124.7, 114.3, 270),
}


def apply_edge_ports(board):
    retained = []
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    nets = {n.GetNetname().lstrip('/'): n for n in board.GetNetInfo().NetsByNetcode().values()}
    xy = lambda v: (k.ToMM(v.x), k.ToMM(v.y))
    old_stitches = [xy(t.GetPosition()) for t in board.GetTracks()
                    if isinstance(t, k.PCB_VIA) and t.GetNetname() == '/GND']
    for ref, (x, y, angle) in POSITIONS.items():
        f = fps[ref]; f.SetPosition(V(x, y)); f.SetOrientationDegrees(angle)
        f.Reference().SetPosition(V(x, y)); f.Reference().SetTextAngle(k.EDA_ANGLE(0, k.DEGREES_T))
        if ref in PORT_POSITIONS: f.Reference().SetPosition(V(x + (1.8 if ref == 'J1' else 3.6), y + (1.3 if ref == 'J1' else -1.3)))
    pads = {(f.GetReference(), p.GetNumber()): p for f in board.GetFootprints() for p in f.Pads()}
    pp = lambda ref, num: xy(pads[ref, str(num)].GetPosition())
    # Keep the reviewed LDO input/output copper. Replace changed port/communication routes.
    preserved = []
    for item in list(board.GetTracks()):
        name = item.GetNetname().lstrip('/')
        keep = name in ('9V_LDO', 'COUT_BULK') or (name == '3V3' and max(xy(item.GetStart())[1], xy(item.GetEnd())[1]) <= 106.800001)
        if keep: preserved.append(item.m_Uuid.AsString())
        else: retained.append(item); board.Remove(item)

    def route(net, points, width=.2, layer=k.B_Cu):
        for a, c in zip(points, points[1:]):
            if math.dist(a, c) < .00001: continue
            track = k.PCB_TRACK(board); track.SetStart(V(*a)); track.SetEnd(V(*c))
            track.SetLayer(layer); track.SetWidth(M(width)); track.SetNet(nets[net]); board.Add(track)

    def via(net, p):
        for item in board.GetTracks():
            if isinstance(item, k.PCB_VIA) and math.dist(xy(item.GetPosition()), p) < .001:
                assert item.GetNetname().lstrip('/') == net; return
        item = k.PCB_VIA(board); item.SetPosition(V(*p)); item.SetViaType(k.VIATYPE_THROUGH)
        item.SetLayerPair(k.F_Cu, k.B_Cu); item.SetWidth(M(.5))
        item.SetDrill(M(.25))
        item.SetNet(nets[net]); board.Add(item)

    for jpin, d, dp, r, rp, ic, ip in [('3','D1','1','R2','1','U3','6'), ('4','D1','2','R3','1','U3','4'), ('5','D2','1','R4','2','U2','6'), ('6','D2','2','R5','2','U2','4')]:
        start, land, dest = pp('J2',jpin), pp(d,dp), pp(r,rp)
        net = pads['J2',jpin].GetNetname().lstrip('/')
        route(net,[start,(land[0],start[1]-abs(land[0]-start[0])),land,dest])
        other = '2' if rp == '1' else '1'
        route(pads[r,other].GetNetname().lstrip('/'),[pp(r,other),pp(ic,ip)])
    # R1's two pads intersect the receive pair after D1; no bypass around the TVS.
    for jpin, d, r, rp, net in [('2','D3','R7','2','TX_OUT'),('3','D4','R8','1','RX_IN')]:
        route(net,[pp('J3',jpin),pp(d,'1'),pp(r,rp)])
    for net, p in [('UART_TX_IC',(107,108.6)),('UART_TX_IC',(122.9,116.5)),('UART_RX_IC',(108.05,110.4)),('UART_RX_IC',(124.7,116.5))]: via(net,p)
    route('UART_TX_IC',[pp('U3','3'),(106.95,108.65),(107,108.6)])
    route('UART_TX_IC',[(107,108.6),(114.9,116.5),(122.9,116.5)],.2,k.In2_Cu)
    route('UART_TX_IC',[(122.9,116.5),pp('R7','1')])
    route('UART_RX_IC',[pp('U2','1'),(108.05,110.4)])
    route('UART_RX_IC',[(108.05,110.4),(114.95,117.3),(123.9,117.3),(124.7,116.5)],.2,k.In2_Cu)
    route('UART_RX_IC',[pp('R8','2'),(124.7,116.5),pp('R6','2')])
    # The 9V feed branches before FB1 and reaches the lower PPG port on L4.
    route('9V_SHARED',[pp('J1','1'),(102.5,102.7),pp('FB1','1')],.7)
    via('9V_SHARED',(102.5,100.9)); via('9V_SHARED',(101.5,121.0))
    route('9V_SHARED',[(102.5,100.9),(101.5,101.9),(101.5,121.0)],.7,k.In3_Cu)
    route('9V_SHARED',[(101.5,121.0),pp('J2','1')],.7)
    # Short local bypass connections, distribution below on L4.
    for p in [(103.475,108.7),(112.2,108.2),(120.2,121.3),(124.7,112.5)]: via('3V3',p)
    route('3V3',[pp('U3','1'),pp('C5','1'),(103.475,108.7)],.4)
    route('3V3',[pp('U2','2'),pp('U2','3'),(111.925,109.8),pp('C4','1'),(112.2,108.2)],.4)
    route('3V3',[(120.2,121.3),(121.1,122.2),pp('J3','1')],.5)
    route('3V3',[(124.7,112.5),pp('R6','1')],.3)
    route('3V3',[(116.5,106.8),(115.5,107.8),(104.375,107.8),(103.475,108.7)],.65,k.In3_Cu)
    route('3V3',[(112.2,107.8),(112.2,108.2)],.5,k.In3_Cu)
    route('3V3',[(116.5,106.8),(118.4,108.7),(118.4,119.5),(120.2,121.3)],.65,k.In3_Cu)
    route('3V3',[(118.4,112.5),(124.7,112.5)],.5,k.In3_Cu)

    ground = {('J1','2'):(105.4,99.75),('J2','2'):(103.3,121.05),('J3','4'):(127.5,122.25),
              ('U1','1'):(108.85,108.7),('C1','2'):(103.9,105),('C3','2'):(103.9,107),
              ('D1','3'):(106,121.35),('D2','3'):(109.6,121.35),
              ('U3','2'):(106,108.65),('U3','5'):(106,113.35),('U2','5'):(109.6,113.35),
              ('C4','2'):(113.25,110.975),('D3','2'):(121.4,120.4),('D4','2'):(126.2,120.4)}
    for ref in ['C2','C6','C7','C8']: ground[ref,'2'] = (125.7,xy(fps[ref].GetPosition())[1])
    for (ref,pin),p in ground.items():
        route('GND',[pp(ref,pin),p],.3 if ref.startswith('D') or ref in ('U2','U3') else .4); via('GND',p)
    route('GND',[pp('C5','2'),(101.925,110.425),(102.5,111)],.4);via('GND',(102.5,111))
    # Reuse unobstructed GND stitching; do not leave vias in moved SMT pads.
    diag=defaultdict(int)
    foreign=[item_geometry(p,k.B_Cu,diag,.00001) for f in board.GetFootprints() for p in f.Pads()]
    foreign += [item_geometry(t,t.GetLayer(),diag,.00001) for t in board.GetTracks() if t.GetNetname()!='/GND']
    obstacles=unary_union(foreign); stitched=[]
    for p in old_stitches:
        if Point(p).distance(obstacles)<.405:continue
        if any(math.dist(p,h)<HEAD_CLEARANCE_DIAMETER/2+.255 for h in HOLES.values()):continue
        if any(isinstance(t,k.PCB_VIA) and math.dist(p,xy(t.GetPosition()))<.71 for t in board.GetTracks()):continue
        via('GND',p);stitched.append(p)

    # Labels on both assembly view and the empty top face identify every cable pad.
    port_words={'PPG','UART','9V  GND','9V','GND','TXP','TXN','RXP','RXN','3V3','TX','RX'}
    for t in list(board.GetDrawings()):
        if t.GetClass()=='PCB_TEXT' and t.GetText() in port_words:
            retained.append(t);board.Remove(t)
    def text(value,p,size=.8,layer=k.F_SilkS,angle=0):
        t=k.PCB_TEXT(board);t.SetText(value);t.SetPosition(V(*p));t.SetLayer(layer)
        t.SetTextSize(V(size,size));t.SetTextThickness(M(.12));t.SetTextAngle(k.EDA_ANGLE(angle,k.DEGREES_T));board.Add(t)
    text('9V  GND',(103.4,101.4));text('PPG',(101.7,116.9));text('UART',(122.9,114.8))
    for ref,labels in [('J2',['9V','GND','TXP','TXN','RXP','RXN']),('J3',['3V3','TX','RX','GND'])]:
        for i,label in enumerate(labels,1):
            p=pp(ref,str(i));text(label,(p[0],p[1]-1.9),.8,angle=90)
    board.BuildConnectivity();k.ZONE_FILLER(board).Fill(board.Zones());board.BuildConnectivity()
    return {'placements_absolute_mm':POSITIONS,'preserved_ldo_copper_uuids':preserved,
            'reused_ground_stitch_positions_mm':stitched,
            'ports':{ref:{'position_mm':list(pp(ref,'1')),'outward_direction':'-Y' if ref=='J1' else '+Y','pad_to_board_edge_mm':.65} for ref in PORT_POSITIONS},
            'routing':'External pads on B.Cu -> TVS land -> series resistors; UART internal routing on L3, power distribution on L4.'}
