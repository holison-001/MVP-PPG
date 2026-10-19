"""Read-only independent serialized 10-set panel Gerber/Excellon verification."""
from pathlib import Path
import collections, dataclasses, gc, hashlib, json, math, re, sys, warnings
gc.disable()
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
OLD=ROOT/'manufacturing/20261009_PPG_UART_1plus1'
sys.path.insert(0,str(ROOT/'.git/all_ground_gerber_20261005/pydeps'))
from gerbonara import GerberFile, ExcellonFile
from gerbonara.utils import MM
import pcbnew as k
MAN=json.loads((OUT/'panel_manifest.json').read_text(encoding='utf8'))
manifest_hash=hashlib.sha256((OUT/'panel_manifest.json').read_bytes()).hexdigest()
MH={Path(x['file']).name:x['sha256'] for x in MAN['files']}
LAYERS={'F_Cu':('Copper','L1','Top'),'In1_Cu':('Copper','L2','Inr'),'In2_Cu':('Copper','L3','Inr'),'In3_Cu':('Copper','L4','Inr'),'In4_Cu':('Copper','L5','Inr'),'B_Cu':('Copper','L6','Bot'),'F_Mask':('Soldermask','Top'),'B_Mask':('Soldermask','Bot'),'F_Silkscreen':('Legend','Top'),'B_Silkscreen':('Legend','Bot'),'F_Paste':('Paste','Top'),'B_Paste':('Paste','Bot'),'Edge_Cuts':('Profile','NP')}
errors=[];parse_warnings=[];keepers=[]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(ok,message):
 if not ok:errors.append(message)
def parse(path,kind=None):
 with warnings.catch_warnings(record=True) as ww:
  warnings.simplefilter('always')
  value=GerberFile.open(path,enable_includes=False) if kind is None else ExcellonFile.open(path,plated=kind=='PTH')
 for w in ww:parse_warnings.append({'file':str(path),'category':w.category.__name__,'message':str(w.message)})
 return value
def primitives(obj,off=(0,0)):
 result=[];dx,dy=off
 for p in obj.to_primitives(MM):
  d=dataclasses.asdict(p)
  if type(p).__name__=='Rectangle':
   c=math.cos(d['rotation']);s=math.sin(d['rotation'])
   corners=[(d['x']+dx+u*c-v*s,d['y']+dy+u*s+v*c) for u,v in [(-d['w']/2,-d['h']/2),(-d['w']/2,d['h']/2),(d['w']/2,d['h']/2),(d['w']/2,-d['h']/2)]]
   corners.sort(key=lambda pt:(round(pt[0],5),round(pt[1],5)))
   result.append({'primitive_type':'RectangleCorners','corners':corners,'polarity_dark':p.polarity_dark});continue
  for q in ['x','x1','x2','cx']:
   if q in d:d[q]+=dx
  for q in ['y','y1','y2','cy']:
   if q in d:d[q]+=dy
  if 'outline' in d:d['outline']=[(x+dx,y+dy) for x,y in d['outline']]
  if 'arc_centers' in d:d['arc_centers']=[None if v is None else (v[0],(v[1][0]+dx,v[1][1]+dy)) for v in d['arc_centers']]
  result.append({'primitive_type':type(p).__name__,**d})
 return result
def compare(a,b,path='',tol=1.0001e-6):
 diffs=[];maximum=0.;count=0
 if isinstance(a,bool) or a is None or isinstance(a,str):
  if a!=b:diffs.append([path,a,b])
 elif isinstance(a,(int,float)) and isinstance(b,(int,float)):
  count=1;maximum=abs(a-b)
  if maximum>tol:diffs.append([path,a,b])
 elif isinstance(a,dict) and isinstance(b,dict):
  if set(a)!=set(b):diffs.append([path,sorted(a),sorted(b)])
  for key in set(a)&set(b):
   d,m,c=compare(a[key],b[key],path+'.'+key,tol);diffs+=d;maximum=max(maximum,m);count+=c
 elif isinstance(a,(list,tuple)) and isinstance(b,(list,tuple)):
  if len(a)!=len(b):diffs.append([path+'.length',len(a),len(b)])
  for i,(x,y) in enumerate(zip(a,b)):
   d,m,c=compare(x,y,path+f'[{i}]',tol);diffs+=d;maximum=max(maximum,m);count+=c
 elif a!=b:diffs.append([path,str(a),str(b)])
 return diffs,maximum,count
def match_hits(expected,actual,tol=.0005001):
 remaining=list(expected);matched=0;extra=[];ambiguous=[];maxaxis=0
 for a in actual:
  matches=[(i,e) for i,e in enumerate(remaining) if abs(a[2]-e[2])<1e-8 and abs(a[0]-e[0])<=tol and abs(a[1]-e[1])<=tol]
  if len(matches)!=1:
   (extra if not matches else ambiguous).append(a);continue
  i,e=matches[0];remaining.pop(i);matched+=1;maxaxis=max(maxaxis,abs(a[0]-e[0]),abs(a[1]-e[1]))
 return {'pass':not remaining and not extra and not ambiguous,'native_count':len(expected),'output_count':len(actual),'matched_count':matched,'max_abs_per_axis_delta_mm':maxaxis,'missing':remaining,'extra':extra,'ambiguous':ambiguous}
def hits(d):
 check(all(type(o).__name__=='Flash' for o in d.objects),'Non-circular drill object')
 return [(o.x,o.y,o.aperture.diameter) for o in d.objects]
def native_holes(board,origin):
 h={'PTH':[],'NPTH':[]}
 for v in board.GetTracks():
  if not isinstance(v,k.PCB_VIA):continue
  check(v.IsOnLayer(k.F_Cu) and v.IsOnLayer(k.B_Cu),'Non-through via')
  pos=v.GetPosition();h['PTH'].append((k.ToMM(pos.x)-origin[0],origin[1]-k.ToMM(pos.y),k.ToMM(v.GetDrillValue())))
 for f in board.GetFootprints():
  for pad in f.Pads():
   drill=pad.GetDrillSize()
   if not drill.x and not drill.y:continue
   check(drill.x==drill.y,'Slotted source hole')
   pos=pad.GetPosition();kind='NPTH' if pad.GetAttribute()==k.PAD_ATTRIB_NPTH else 'PTH'
   h[kind].append((k.ToMM(pos.x)-origin[0],origin[1]-k.ToMM(pos.y),k.ToMM(drill.x)))
 return h

report={'scope':'Independent post-serialization 20-board panel audit. Freshly parsed output objects are compared in sequence with manually translated unit objects plus native carrier Gerber extras; production Edge.Cuts is compared only to the carrier physical profile.', 'manifest_sha256':manifest_hash,'primitive_tolerance_mm':1.0001e-6,'native_drill_tolerance_per_axis_mm':.0005001,'sources':{},'layers':[],'drills':{},'fiducials':{},'errors':errors}
check(len(MAN['instances'])==20,'Expected 20 instances')
check(collections.Counter(x['board'] for x in MAN['instances'])=={'PPG':10,'UART':10},'Expected 10 PPG and 10 UART')
check(all(i['rotation_deg']==0 for i in MAN['instances']),'Nonzero instance rotation')
check(len({(i['set_id'],i['board']) for i in MAN['instances']})==20,'Duplicate instance id')
counts={'.gbr':len(list((OUT/'gerber').glob('*.gbr'))),'.drl':len(list((OUT/'gerber').glob('*.drl')))}
check(counts=={'.gbr':13,'.drl':2},'Expected 13 Gerbers and 2 drills');report['production_file_counts']=counts
native_units={};serialized_units={};native_expected={'PTH':[],'NPTH':[]};serialized_expected={'PTH':[],'NPTH':[]}
for name,s in MAN['unit_sources'].items():
 p=Path(s['path']);check(sha(p)==s['sha'],name+' source hash changed')
 board=k.LoadBoard(str(p));keepers.append(board);native_units[name]=native_holes(board,s['origin'])
 report['sources'][name]={'path':str(p),'sha256':sha(p),'matches_manifest':sha(p)==s['sha'],'unit_gerber_origin_mm':s['origin']}
 for kind in ['PTH','NPTH']:serialized_units[(name,kind)]=hits(parse(OLD/'units'/name/(name+'-'+kind+'.drl'),kind))
for i in MAN['instances']:
 off=i['offset_mm']
 for kind in ['PTH','NPTH']:
  native_expected[kind]+=[(x+off[0],y+off[1],d) for x,y,d in native_units[i['board']][kind]]
  serialized_expected[kind]+=[(x+off[0],y+off[1],d) for x,y,d in serialized_units[i['board'],kind]]
carrier_path=OUT/'engineering/Panel_Carrier_Only.kicad_pcb';carrier_hash=sha(carrier_path)
carrier=k.LoadBoard(str(carrier_path));keepers.append(carrier);carrier_holes=native_holes(carrier,[0,177])
native_expected['NPTH']+=carrier_holes['NPTH'];check(not carrier_holes['PTH'],'Carrier must have no plated holes')
carrier_dir=OUT/'engineering/carrier_gerber'
serialized_expected['NPTH']+=hits(parse(carrier_dir/'Panel_Carrier_Only-NPTH.drl','NPTH'))
check(sorted(carrier_holes['NPTH'])==sorted((p['x_mm'],p['y_mm'],p['diameter_mm']) for p in MAN['tooling_holes']),'Guide holes differ from carrier native PCB')
report['carrier']={'path':str(carrier_path),'sha256':carrier_hash,'native_tooling_holes_mm':carrier_holes['NPTH']}

cached_carrier={}
for suffix,function in LAYERS.items():
 chunks=[];source_file_hashes={};native_extra_count=0
 if suffix!='Edge_Cuts':
  units={name:parse(OLD/'units'/name/f'{name}-{suffix}.gbr') for name in MAN['unit_sources']}
  for name,g in units.items():
   check(g.unit==MM,name+' '+suffix+' not mm');check(tuple(g.file_attrs.get('.FileFunction',()))==function,name+' '+suffix+' bad FileFunction')
   source_file_hashes[name]=sha(OLD/'units'/name/f'{name}-{suffix}.gbr')
  chunks=[(f'{i["set_id"]}_{i["board"]}',units[i['board']],i['offset_mm']) for i in MAN['instances']]
 extra=carrier_dir/f'Panel_Carrier_Only-{suffix}.gbr'
 if extra.is_file():
  cg=parse(extra);cached_carrier[suffix]=cg;chunks.append(('CARRIER',cg,(0,0)));native_extra_count=len(cg.objects);source_file_hashes['CARRIER']=sha(extra)
 check(chunks,'No expected objects for '+suffix)
 path=OUT/'gerber'/f'PPG_UART_10sets-{suffix}.gbr';g=parse(path)
 check(sha(path)==MH[path.name],suffix+' final hash differs from manifest')
 check(g.unit==MM,suffix+' final not mm');check(tuple(g.file_attrs.get('.FileFunction',()))==function,suffix+' final bad FileFunction')
 check(all(src.file_attrs.get('.FilePolarity')==g.file_attrs.get('.FilePolarity') for _,src,_ in chunks),suffix+' FilePolarity changed')
 expected_count=sum(len(src.objects) for _,src,_ in chunks);check(expected_count==len(g.objects),suffix+' object count changed')
 j=0;differences=[];numeric_count=0;maxdiff=0;primitive_count=0;macro_count=0
 for label,src,off in chunks:
  for o in src.objects:
   if j>=len(g.objects):break
   dst=g.objects[j];pp=primitives(o,off);primitive_count+=len(pp)
   ex={'object_type':type(o).__name__,'polarity_dark':o.polarity_dark,'primitives':pp}
   ac={'object_type':type(dst).__name__,'polarity_dark':dst.polarity_dark,'primitives':primitives(dst)}
   ds,md,n=compare(ex,ac,label+f'[{j}]');differences+=ds;maxdiff=max(maxdiff,md);numeric_count+=n;j+=1
   macro_count+='Macro' in type(getattr(o,'aperture',None)).__name__
 check(not differences,suffix+f' {len(differences)} primitive differences')
 report['layers'].append({'layer':suffix,'file':path.name,'sha256':sha(path),'FileFunction':function,'FilePolarity':g.file_attrs.get('.FilePolarity'),'units':'mm','source_hashes':source_file_hashes,'expected_object_count':expected_count,'actual_object_count':len(g.objects),'carrier_extra_object_count':native_extra_count,'expanded_primitive_count':primitive_count,'source_macro_flash_count':macro_count,'numeric_values_compared':numeric_count,'max_numeric_difference_mm':maxdiff,'geometry_polarity_and_macro_expansion_preserved':not differences,'no_mirror_or_rotation':not differences,'differences':differences[:30]})
 print(suffix+': '+str(len(g.objects))+' objects checked',flush=True)

for side,cu,mask in [('TOP','F_Cu','F_Mask'),('BOTTOM','B_Cu','B_Mask')]:
 f=[x for x in MAN['fiducials'] if x['side']==side];footprints={x.GetReference():x for x in carrier.GetFootprints()};records=[]
 for fid in f:
  fp=footprints[fid['ref']];pads=list(fp.Pads());check(len(pads)==1,fid['ref']+' unexpected pads');p=pads[0]
  actual=[k.ToMM(p.GetPosition().x),177-k.ToMM(p.GetPosition().y)];position_ok=math.dist(actual,[fid['x_mm'],fid['y_mm']])<1e-6
  no_paste=not p.IsOnLayer(k.F_Paste) and not p.IsOnLayer(k.B_Paste)
  check(position_ok and no_paste and p.GetDrillSize().x==0 and p.GetDrillSize().y==0,fid['ref']+' position/paste/drill mismatch')
  check(p.GetSize().x==k.FromMM(1) and p.GetSize().y==k.FromMM(1),fid['ref']+' Cu diameter mismatch')
  records.append({'reference':fid['ref'],'xy_mm':actual,'copper_diameter_mm':k.ToMM(p.GetSize().x),'no_paste':no_paste,'undrilled':p.GetDrillSize().x==0})
 for suffix,diameter in [(cu,1),(mask,3)]:
  gg=cached_carrier[suffix];expected=[(x['x_mm'],x['y_mm'],diameter) for x in f]
  check(all(type(o).__name__=='Flash' and hasattr(o.aperture,'diameter') for o in gg.objects),suffix+' carrier should contain fiducial circular flashes only')
  check(match_hits(expected,hits(gg),tol=1e-8)['pass'],suffix+' fiducial output mismatch')
 report['fiducials'][side]={'count':len(f),'records':records,'native_carrier_Cu1mm_Mask3mm_verified':True}
check(len(MAN['fiducials'])==6,'Expected six fiducials')
for suffix in ['F_Paste','B_Paste']:
 check(not (carrier_dir/f'Panel_Carrier_Only-{suffix}.gbr').exists(),'Unexpected carrier paste export')

for kind in ['PTH','NPTH']:
 path=OUT/'gerber'/f'PPG_UART_10sets-{kind}.drl';d=parse(path,kind);h=hits(d)
 check(sha(path)==MH[path.name],kind+' final hash differs from manifest');check(d.import_settings.unit==MM,kind+' drill not mm')
 expected_diam={.25:1640} if kind=='PTH' else {3.:44};diam=dict(collections.Counter(round(z[2],6) for z in h));check(diam==expected_diam,kind+' count or diameter mismatch')
 nc=match_hits(native_expected[kind],h);uc=match_hits(serialized_expected[kind],h,tol=1e-8);check(nc['pass'],kind+' differs from native PCB coordinates');check(uc['pass'],kind+' differs from translated unit/carrier drill coordinates')
 text=path.read_text(encoding='utf8');check(('TYPE=PLATED' if kind=='PTH' else 'TYPE=NON_PLATED') in text,kind+' plating header missing');check('\nG90\n' in text,kind+' absolute coordinate command missing')
 report['drills'][kind]={'file':path.name,'sha256':sha(path),'diameter_counts_mm':diam,'native_source_comparison':nc,'unit_plus_carrier_serialized_comparison':uc,'units':'mm','absolute_G90':True,'plating_header_verified':True}

check(sha(OUT/'panel_manifest.json')==manifest_hash,'Manifest changed during audit');check(sha(carrier_path)==carrier_hash,'Carrier PCB changed during audit')
check(all(sha(s['path'])==s['sha'] for s in MAN['unit_sources'].values()),'Canonical source changed during audit')
report['source_hashes_unchanged']=all(sha(s['path'])==s['sha'] for s in MAN['unit_sources'].values())
report['parser_warnings']=parse_warnings
report['summary']={'primitive_count':sum(x['expanded_primitive_count'] for x in report['layers']),'numeric_values_compared':sum(x['numeric_values_compared'] for x in report['layers']),'max_numeric_difference_mm':max(x['max_numeric_difference_mm'] for x in report['layers']),'production_parser_warning_count':sum(str(OUT/'gerber') in x['file'] for x in parse_warnings)}
report['limitations']=['Same Gerbonara parser library as exporter is used, but no exporter merge/offset functions are called. Expected coordinates are computed separately and all serialized output is reparsed.', 'Unit PCB geometry is represented by previous native KiCad Gerbers whose source hashes were independently verified. This audit compares post-parsed Gerber primitives, not full native PCB copper polygons.', 'Carrier topology, routing manufacturability, tab strength and mechanical clearance are separate geometry-audit scope.', 'No fabrication acceptance, thermal/reflow stability or physical stackup approval is implied.']
report['pass']=not errors
(OUT/'verification/panel_gerber_independent.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'pass':not errors,**report['summary'],'errors':errors},ensure_ascii=False),flush=True)
raise SystemExit(0 if not errors else 1)
