"""Independent read-only post-serialization 1+1 Gerber and Excellon audit."""
from pathlib import Path
import collections, dataclasses, gc, hashlib, json, math, re, sys, warnings
gc.disable()
OUT=Path(__file__).resolve().parents[1]
ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'.git/all_ground_gerber_20261005/pydeps'))
from gerbonara import GerberFile, ExcellonFile
from gerbonara.utils import MM
import pcbnew as k

MAN=json.loads((OUT/'array_manifest.json').read_text(encoding='utf8'))
MAN_HASHES={x['file']:x['sha256'] for x in MAN['files']}
LAYERS={
 'F.Cu':('Copper','L1','Top'),'In1.Cu':('Copper','L2','Inr'),
 'In2.Cu':('Copper','L3','Inr'),'In3.Cu':('Copper','L4','Inr'),
 'In4.Cu':('Copper','L5','Inr'),'B.Cu':('Copper','L6','Bot'),
 'F.Mask':('Soldermask','Top'),'B.Mask':('Soldermask','Bot'),
 'F.Silkscreen':('Legend','Top'),'B.Silkscreen':('Legend','Bot'),
 'F.Paste':('Paste','Top'),'B.Paste':('Paste','Bot'),'Edge.Cuts':('Profile','NP')}
errors=[]; parser_warnings=[]; keepers=[]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(ok,message):
 if not ok:errors.append(message)
def parse(path,kind=None):
 with warnings.catch_warnings(record=True) as ww:
  warnings.simplefilter('always')
  value=GerberFile.open(path,enable_includes=False) if kind is None else ExcellonFile.open(path,plated=kind=='PTH')
 for w in ww:parser_warnings.append({'file':str(path.relative_to(OUT)),'category':w.category.__name__,'message':str(w.message)})
 return value
def primitives(obj,offset=(0,0)):
 result=[];dx,dy=offset
 for p in obj.to_primitives(MM):
  d=dataclasses.asdict(p)
  # Equivalent rotated rectangular macros may swap width/height and rotate 90
  # degrees on serialization. Compare actual corners, not parameter labels.
  # Use the elementary rotation formula independently of Gerbonara rendering.
  if type(p).__name__=='Rectangle':
   c=math.cos(d['rotation']);s=math.sin(d['rotation'])
   corners=[(d['x']+dx+u*c-v*s,d['y']+dy+u*s+v*c) for u,v in [(-d['w']/2,-d['h']/2),(-d['w']/2,d['h']/2),(d['w']/2,d['h']/2),(d['w']/2,-d['h']/2)]]
   corners.sort(key=lambda pt:(round(pt[0],5),round(pt[1],5)))
   result.append({'primitive_type':'RectangleCorners','corners':corners,'polarity_dark':p.polarity_dark})
   continue
  for q in ['x','x1','x2','cx']:
   if q in d:d[q]+=dx
  for q in ['y','y1','y2','cy']:
   if q in d:d[q]+=dy
  if 'outline' in d:d['outline']=[(x+dx,y+dy) for x,y in d['outline']]
  if 'arc_centers' in d:
   d['arc_centers']=[None if v is None else (v[0],(v[1][0]+dx,v[1][1]+dy)) for v in d['arc_centers']]
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
 remaining=list(expected);matched=[];extra=[];ambiguous=[]
 for a in actual:
  matches=[(i,e) for i,e in enumerate(remaining) if abs(a[2]-e[2])<1e-8 and abs(a[0]-e[0])<=tol and abs(a[1]-e[1])<=tol]
  if len(matches)!=1:
   (extra if not matches else ambiguous).append(a);continue
  i,e=matches[0];remaining.pop(i);matched.append({'native_mm':e,'output_mm':a,'delta_xy_mm':[a[0]-e[0],a[1]-e[1]]})
 return {'pass':not remaining and not extra and not ambiguous,'native_count':len(expected),'output_count':len(actual),'matched_count':len(matched),'max_abs_per_axis_delta_mm':max((max(abs(x) for x in m['delta_xy_mm']) for m in matched),default=0),'missing':remaining,'extra':extra,'ambiguous':ambiguous,'matches':matched}
def hits(d):
 check(all(type(o).__name__=='Flash' for o in d.objects),'Non-circular drill object')
 return [(o.x,o.y,o.aperture.diameter) for o in d.objects]

report={'scope':'Read-only independent post-serialization array audit. Each combined object and expanded aperture primitive is compared to separately parsed unit artwork with manually translated coordinates; merge/offset exporter methods are not called.',
 'primitive_tolerance_mm':1.0001e-6,'drill_native_per_axis_tolerance_mm':.0005001,'sources':{},'file_inventory':{},'layers':[],'drills':{},'parser_warnings':parser_warnings}
native_combined={'PTH':[],'NPTH':[]};native_units={}
for name,s in MAN['unit_sources'].items():
 p=Path(s['path']);check(sha(p)==s['sha'],name+' source hash changed')
 b=k.LoadBoard(str(p));keepers.append(b)
 stage=OUT/'verification/staged_sources'/name/(name+'.kicad_pcb')
 def tokens_no_origin(text):
  return re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',re.sub(r'\(aux_axis_origin [^)]+\)','',text))
 only_origin=tokens_no_origin(stage.read_text(encoding='utf8'))==tokens_no_origin(p.read_text(encoding='utf8'))
 check(only_origin,name+' staged PCB has changes beyond auxiliary origin')
 expected={'PTH':[],'NPTH':[]};origin=s['origin'];off=s['offset']
 for v in b.GetTracks():
  if not isinstance(v,k.PCB_VIA):continue
  check(v.IsOnLayer(k.F_Cu) and v.IsOnLayer(k.B_Cu),name+' has a non-through via')
  pos=v.GetPosition();expected['PTH'].append((k.ToMM(pos.x)-origin[0],origin[1]-k.ToMM(pos.y),k.ToMM(v.GetDrillValue())))
 for f in b.GetFootprints():
  for p2 in f.Pads():
   drill=p2.GetDrillSize()
   if not drill.x and not drill.y:continue
   check(drill.x==drill.y,name+' has slotted hole')
   pos=p2.GetPosition();kind='NPTH' if p2.GetAttribute()==k.PAD_ATTRIB_NPTH else 'PTH'
   expected[kind].append((k.ToMM(pos.x)-origin[0],origin[1]-k.ToMM(pos.y),k.ToMM(drill.x)))
 native_units[name]=expected
 for kind,hh in expected.items():native_combined[kind]+=[(x+off[0],y+off[1],d) for x,y,d in hh]
 report['sources'][name]={'path':str(p),'sha256':sha(p),'hash_matches_manifest':sha(p)==s['sha'],'staged_only_auxiliary_origin_changed':only_origin,'export_origin_mm':origin,'array_translation_mm':off,'native_hole_counts':{kind:len(hh) for kind,hh in expected.items()}}
for label,folder in [('PPG',OUT/'units/PPG'),('UART',OUT/'units/UART'),('array',OUT/'array_1plus1')]:
 counts={'.gbr':len(list(folder.glob('*.gbr'))),'.drl':len(list(folder.glob('*.drl')))}
 check(counts=={'.gbr':13,'.drl':2},label+' file count incorrect')
 report['file_inventory'][label]=counts

parsed_array={}
for layer,function in LAYERS.items():
 suffix=layer.replace('.','_');expected=[];raw_counts={};macros=0;units_functions={};expanded_count=0
 for name,s in MAN['unit_sources'].items():
  g=parse(OUT/'units'/name/(name+'-'+suffix+'.gbr'))
  check(g.unit==MM,name+' '+layer+' is not mm')
  check(tuple(g.file_attrs.get('.FileFunction',()))==function,name+' '+layer+' file function mismatch')
  raw_counts[name]=len(g.objects);units_functions[name]=g.file_attrs.get('.FilePolarity')
  for obj in g.objects:
   pp=primitives(obj,s['offset']);expanded_count+=len(pp)
   expected.append({'object_type':type(obj).__name__,'polarity_dark':obj.polarity_dark,'primitives':pp})
   if 'Macro' in type(getattr(obj,'aperture',None)).__name__:macros+=1
 path=OUT/'array_1plus1'/('PPG_UART_1plus1-'+suffix+'.gbr');g=parse(path);parsed_array[layer]=g
 check(sha(path)==MAN_HASHES[path.name],layer+' differs from manifest hash')
 check(g.unit==MM,layer+' combined is not mm')
 check(tuple(g.file_attrs.get('.FileFunction',()))==function,layer+' combined file function mismatch')
 check(all(v==g.file_attrs.get('.FilePolarity') for v in units_functions.values()),layer+' file polarity changed')
 actual=[{'object_type':type(o).__name__,'polarity_dark':o.polarity_dark,'primitives':primitives(o)} for o in g.objects]
 diffs,maxdiff,numbers=compare(expected,actual)
 check(not diffs,layer+f' has {len(diffs)} primitive differences')
 report['layers'].append({'layer':layer,'file':path.name,'sha256':sha(path),'file_function':function,'units':'mm','file_polarity':g.file_attrs.get('.FilePolarity'),'unit_object_counts':raw_counts,'combined_objects':len(actual),'expanded_primitive_count':expanded_count,'source_macro_flash_count':macros,'compared_numeric_values':numbers,'max_numeric_difference_mm':maxdiff,'sequential_geometry_polarity_and_macro_expansion_preserved':not diffs,'differences':diffs[:30],'no_mirror_or_rotation':not diffs})

for kind in ['PTH','NPTH']:
 unit_expected=[];unit_report={}
 for name,s in MAN['unit_sources'].items():
  path=OUT/'units'/name/(name+'-'+kind+'.drl');d=parse(path,kind)
  check(d.import_settings.unit==MM,name+' '+kind+' is not mm')
  h=hits(d);cmp=match_hits(native_units[name][kind],h)
  check(cmp['pass'],name+' '+kind+' differs from native holes')
  unit_report[name]={'file':str(path.relative_to(OUT)),'sha256':sha(path),'native_comparison':cmp}
  off=s['offset'];unit_expected += [(x+off[0],y+off[1],dr) for x,y,dr in h]
 path=OUT/'array_1plus1'/('PPG_UART_1plus1-'+kind+'.drl');d=parse(path,kind);h=hits(d)
 check(sha(path)==MAN_HASHES[path.name],kind+' differs from manifest hash')
 check(d.import_settings.unit==MM,kind+' combined is not mm')
 unit_cmp=match_hits(unit_expected,h,tol=1e-8);native_cmp=match_hits(native_combined[kind],h)
 check(unit_cmp['pass'],kind+' translated unit drill mismatch');check(native_cmp['pass'],kind+' native drill mismatch')
 diameter_counts=collections.Counter(round(z[2],6) for z in h)
 check(dict(diameter_counts)==({.25:164} if kind=='PTH' else {3.:4}),kind+' unexpected diameter/count')
 content=path.read_text(encoding='utf8')
 check('TYPE=PLATED' in content if kind=='PTH' else 'TYPE=NON_PLATED' in content,kind+' explicit plating comment missing')
 check('\nG90\n' in content,kind+' explicit absolute-mode command missing')
 report['drills'][kind]={'file':path.name,'sha256':sha(path),'unit_files':unit_report,'diameter_counts_mm':dict(diameter_counts),'translated_unit_comparison':unit_cmp,'native_source_comparison':native_cmp,'plating_identification':'Separate PTH/NPTH filename plus explicit TYPE=PLATED or TYPE=NON_PLATED comment; explicit G90 absolute coordinates.'}

g=parsed_array['Edge.Cuts'];arcs=[o for o in g.objects if type(o).__name__=='Arc'];lines=[o for o in g.objects if type(o).__name__=='Line']
check(len(arcs)==2 and len(lines)==4,'Outline must have two PPG semicircular arcs and four UART edges')
closed_circle=len(arcs)==2 and all(math.dist((a.x2,a.y2),(z.x1,z.y1))<1e-6 for a,z in zip(arcs,arcs[1:]+arcs[:1]))
circle_checks=[{'center':[a.x1+a.cx,a.y1+a.cy],'radius':math.hypot(a.cx,a.cy),'end_radius':math.hypot(a.x2-a.x1-a.cx,a.y2-a.y1-a.cy),'start':[a.x1,a.y1],'end':[a.x2,a.y2],'clockwise':a.clockwise} for a in arcs]
circle_ok=closed_circle and all(math.dist(a['center'],(66.75,17.5))<1e-6 and abs(a['radius']-6.75)<1e-6 and abs(a['end_radius']-6.75)<1e-6 for a in circle_checks)
circle_sweep=0.
for a in circle_checks:
 c=a['center'];st=math.atan2(a['start'][1]-c[1],a['start'][0]-c[0]);en=math.atan2(a['end'][1]-c[1],a['end'][0]-c[0])
 circle_sweep+=((st-en) if a['clockwise'] else (en-st))%(2*math.pi)
circle_ok=circle_ok and abs(circle_sweep-2*math.pi)<1e-8 and len({a['clockwise'] for a in circle_checks})==1
vertices=collections.Counter((round(x,6),round(y,6)) for o in lines for x,y in [(o.x1,o.y1),(o.x2,o.y2)])
rect_ok=dict(vertices)=={(5.,5.):2,(5.,30.):2,(57.,5.):2,(57.,30.):2} and sorted(round(math.hypot(o.x2-o.x1,o.y2-o.y1),6) for o in lines)==[25.,25.,52.,52.]
check(circle_ok,'PPG circle profile invalid');check(rect_ok,'UART rectangle profile invalid')
check(abs((66.75-6.75)-57-3)<1e-8,'Gap not 3 mm')
report['profile']={'closed_profile_count':2 if circle_ok and rect_ok else None,'ppg':{'closed':closed_circle,'center_mm':[66.75,17.5],'diameter_mm':13.5,'sweep_degrees':math.degrees(circle_sweep),'arcs':circle_checks,'pass':circle_ok},'uart':{'closed':rect_ok,'bounds_mm':[[5,5],[57,30]],'size_mm':[52,25],'pass':rect_ok},'minimum_outline_centerline_gap_mm':3,'finished_board_envelope_mm':[68.5,25],'rail_or_tabs_in_gerber':False,'scope_note':'Two finished board profiles only. Manufacturer CAM must design/confirm panel supports, rails, tabs, tooling and separation; this artwork alone is not a mechanically connected assembly panel.'}
for name,s in MAN['unit_sources'].items():check(sha(s['path'])==s['sha'],name+' source changed during audit')
report['source_hashes_unchanged']=all(sha(s['path'])==s['sha'] for s in MAN['unit_sources'].values())
report['parser_warning_summary']=dict(collections.Counter(w['message'].split(':')[-1].strip() for w in parser_warnings))
report['limitations']=['Uses the same Gerbonara parser library as the export workflow, but does not call the exporter, merge or offset helpers; comparisons use freshly parsed serialized output and manually translated expanded primitives.', 'Geometry/polarity equivalence is between native KiCad unit Gerbers and combined Gerbers. It is not a separate full copper-polygon comparison against KiCad PCB internals.', 'Drill coordinates and dimensions are independently compared directly against native PCB data; 0.0005001 mm per axis accommodates KiCad decimal Excellon rounding.', 'Both canonical PCBs omit a detailed physical stackup. This audit does not establish fabricator acceptance or detailed copper/dielectric construction.', 'No electrical or component-placement changes, source PCB edits, fabrication order or assembly order were made by this audit.']
report['errors']=errors;report['pass']=not errors
(OUT/'verification/gerber_independent.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'pass':not errors,'layers':len(report['layers']),'expanded_primitives':sum(x['expanded_primitive_count'] for x in report['layers']),'parser_warning_count':len(parser_warnings),'errors':errors},ensure_ascii=False))
raise SystemExit(0 if not errors else 1)
