"""Connect existing 3V3 vias with broad In2 traces; preserve In1 routing and GND."""
import argparse,gc,hashlib,heapq,itertools,json,math,sys,shutil
from pathlib import Path
import numpy as np
import pcbnew as k
from shapely.geometry import Point,LineString
from shapely.ops import unary_union
from shapely import contains_xy
from board_coordinates_v08 import normalize_for_analysis, move_center
gc.disable();held=[]
xy=lambda p:(k.ToMM(p.x),k.ToMM(p.y))
vec=lambda p:k.VECTOR2I(round(p[0]*1e6),round(p[1]*1e6))
def copper(t):
 if isinstance(t,k.PCB_VIA):return Point(xy(t.GetPosition())).buffer(k.ToMM(t.GetWidth(k.In2_Cu))/2,quad_segs=64)
 return LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(k.ToMM(t.GetWidth())/2,quad_segs=64)
def add(b,a,c,w):
 t=k.PCB_TRACK(b);t.SetStart(vec(a));t.SetEnd(vec(c));t.SetWidth(k.FromMM(w));t.SetLayer(k.In2_Cu);t.SetNet(b.FindNet('3V3'));b.Add(t);held.append(t)
 return t

def main(src,out):
 project=src.with_suffix('.kicad_pro')
 if not project.is_file():raise ValueError('A matching .kicad_pro is required to preserve clearance rules')
 project_bytes=project.read_bytes()
 custom_rules=src.with_suffix('.kicad_dru')
 if custom_rules.is_file() and custom_rules.resolve()!=out.with_suffix('.kicad_dru').resolve():
  shutil.copy2(custom_rules,out.with_suffix('.kicad_dru'))
 source_sha256=hashlib.sha256(src.read_bytes()).hexdigest()
 b=k.LoadBoard(str(src));held.append(b)
 sheet_center=normalize_for_analysis(b)
 for z in list(b.Zones()):
  if z.GetLayer()==k.In2_Cu:held.append(z);b.Remove(z)
 if not any(z.GetLayer()==k.F_Cu for z in b.Zones()):
  z=k.ZONE(b);z.SetLayer(k.F_Cu);z.SetNet(b.FindNet('GND'))
  z.SetLocalClearance(k.FromMM(.2));z.SetMinThickness(k.FromMM(.15))
  for i in range(128):
   a=2*math.pi*i/128;z.AppendCorner(vec((6.75*math.cos(a),6.75*math.sin(a))),-1)
  b.Add(z);held.append(z)
 for z in b.Zones():
  if z.GetNetname()=='GND':
   z.SetIslandRemovalMode(k.ISLAND_REMOVAL_MODE_ALWAYS)
   if z.GetLayer()==k.F_Cu:
    z.SetPadConnection(k.ZONE_CONNECTION_FULL)
    z.SetLocalClearance(k.FromMM(.15))
 for t in list(b.GetTracks()):
  if not isinstance(t,k.PCB_VIA)and t.GetLayer()==k.In2_Cu and t.GetNetname()=='3V3':held.append(t);b.Remove(t)
 vias=[t for t in b.GetTracks()if isinstance(t,k.PCB_VIA)and t.GetNetname()=='3V3']
 assert len(vias)>1
 polys=[copper(v)for v in vias]
 foreign=unary_union([copper(t)for t in b.GetTracks()if t.GetNetname()!='3V3'and(t.IsOnLayer(k.In2_Cu)if isinstance(t,k.PCB_VIA)else t.GetLayer()==k.In2_Cu)])
 grid=.025;axis=-6.4+np.arange(513)*grid;xx,yy=np.meshgrid(axis,axis)
 coord=lambda n:(float(axis[n[1]]),float(axis[n[0]]))
 mask=lambda g:contains_xy(g,xx,yy)
 # Start at U5's regulator-output via.
 root=min(range(len(vias)),key=lambda i:math.dist(xy(vias[i].GetPosition()),(3,5.4)))
 connected={root};tree=polys[root];records=[]
 dirs=[(-1,0,1),(1,0,1),(0,-1,1),(0,1,1),(-1,-1,2**.5),(-1,1,2**.5),(1,-1,2**.5),(1,1,2**.5)]
 while len(connected)<len(vias):
  result=None
  for width in [.4,.3]:
   offset=.15+width/2+.001
   bad=mask(foreign.buffer(offset));bad|=xx**2+yy**2>(6.75-.3-width/2-.001)**2
   sm=mask(tree.buffer(-.001))&~bad
   target_map=np.full(xx.shape,-1,dtype=int)
   for j in range(len(vias)):
    if j not in connected:target_map[mask(polys[j].buffer(-.001))&~bad]=j
   dist=np.full(xx.shape,np.inf);prev={};heap=[];serial=itertools.count()
   for n in zip(*np.where(sm)):dist[n]=0.;heapq.heappush(heap,(0.,next(serial),n))
   found=None
   while heap:
    cost,_,n=heapq.heappop(heap)
    if cost!=dist[n]:continue
    if target_map[n]>=0:found=n;break
    i,j=n
    for di,dj,dc in dirs:
     ni,nj=i+di,j+dj
     if not(0<=ni<513 and 0<=nj<513)or bad[ni,nj]:continue
     nn=(ni,nj)
     if di and dj and(bad[i,nj]or bad[ni,j])and LineString([coord(n),coord(nn)]).distance(foreign)<offset:continue
     nc=cost+dc
     if nc<dist[nn]:dist[nn]=nc;prev[nn]=n;heapq.heappush(heap,(nc,next(serial),nn))
   if found is None:continue
   points=[found]
   while points[-1]in prev:points.append(prev[points[-1]])
   points=[coord(n)for n in reversed(points)];segments=[];j=0
   while j<len(points)-1:
    end=len(points)-1
    while end>j+1 and LineString([points[j],points[end]]).distance(foreign)<offset:end-=1
    segments.append((points[j],points[end]));j=end
   result=(int(target_map[found]),width,segments);break
  if result is None:raise RuntimeError('No broad In2 path to remaining 3V3 vias: '+str([xy(vias[i].GetPosition())for i in range(len(vias))if i not in connected]))
  j,width,segments=result
  added=[]
  for a,c in segments:
   assert LineString([a,c]).distance(foreign)>=.15+width/2-1e-6
   t=add(b,a,c,width);added.append(copper(t))
  connected.add(j);tree=unary_union([tree,polys[j],*added])
  for i in range(len(vias)):
   if tree.distance(polys[i])<1e-6:connected.add(i);tree=unary_union([tree,polys[i]])
  record={'target_via':xy(vias[j].GetPosition()),'width_mm':width,'segments':segments};records.append(record)
  print(json.dumps({'connected_vias':len(connected),'total_vias':len(vias),'target':record['target_via'],'width':width}),flush=True)
 move_center(b,sheet_center)
 k.ZONE_FILLER(b).Fill(b.Zones());k.SaveBoard(str(out),b)
 out.with_suffix('.kicad_pro').write_bytes(project_bytes)
 report={'source_sha256':source_sha256,'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source':str(src),'output':str(out),'source_3V3_vias':len(vias),'layer':'In2.Cu','net':'3V3','widths_mm':sorted({r['width_mm']for r in records}),'length_mm':sum(math.dist(*s)for r in records for s in r['segments']),'routes':records}
 out.with_suffix('.power.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('source',type=Path)
 parser.add_argument('output',type=Path)
 args=parser.parse_args()
 main(args.source,args.output)
