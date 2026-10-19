"""Export frozen units and translate their Gerbers into the requested 1+1 CAM array.
No source PCB edits. Closed unit outlines intentionally leave support tooling to CAM.
Run with KiCad Python. Dependencies are the previously verified local Gerbonara cache.
"""
import gc, hashlib, json, shutil, subprocess, sys, re, warnings
from pathlib import Path
gc.disable()
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'.git/all_ground_gerber_20261005/pydeps'))
from gerbonara import GerberFile, ExcellonFile
from gerbonara.cam import FileSettings
from gerbonara.utils import MM
CLI=r'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
LAYERS='F.Cu,In1.Cu,In2.Cu,In3.Cu,In4.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,B.Paste,Edge.Cuts'
SOURCES={
 'PPG':dict(path=ROOT/'kicad/ppg_pcb_v08.kicad_pcb',sha='d8ab57b499b6bec9f0e7d4ffc6dcf7341c4ac6b95dc3e1944c301da4cf5201eb',origin=[20,17],offset=[66.75,17.5]),
 'UART':dict(path=ROOT/'kicad/ppg_uart_adapter/ppg_uart_adapter_v01.kicad_pcb',sha='dc9846308f960d4a7d07a931229f7b5ec0d9006f6d22199e07f73a14362606c7',origin=[88,123.5],offset=[5,5])}
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
logs=[]
def run(args):
    proc=subprocess.run([CLI,*map(str,args)],capture_output=True,text=True,encoding='utf-8',errors='replace',creationflags=0x08000000)
    logs.append(dict(command=[CLI,*map(str,args)],returncode=proc.returncode,output=proc.stdout+proc.stderr))
    if proc.returncode: raise RuntimeError(logs[-1])
    print(proc.stdout.strip())
for name,s in SOURCES.items():
    assert sha(s['path'])==s['sha'], f'{name} source changed'
    stage=OUT/'verification/staged_sources'/name
    unit=OUT/'units'/name
    stage.mkdir(parents=True,exist_ok=True);unit.mkdir(parents=True,exist_ok=True)
    pcb=stage/(name+'.kicad_pcb')
    data=s['path'].read_bytes()
    origin=('(aux_axis_origin %s %s)'%tuple(s['origin'])).encode()
    if b'(aux_axis_origin ' in data:
        data,n=re.subn(rb'\(aux_axis_origin [^)]+\)',origin,data); assert n==1
    else:
        data,n=re.subn(rb'\(setup\r?\n',b'(setup\n\t\t'+origin+b'\n',data,count=1);assert n==1
    pcb.write_bytes(data)
    for ext in ['.kicad_pro','.kicad_dru']:
        shutil.copy2(s['path'].with_suffix(ext),pcb.with_suffix(ext))
    run(['pcb','export','gerbers','--layers',LAYERS,'--subtract-soldermask','--use-drill-file-origin','--no-protel-ext','--no-netlist','--precision','6','-o',str(unit)+'/',pcb])
    run(['pcb','export','drill','--format','excellon','--excellon-units','mm','--excellon-zeros-format','decimal','--drill-origin','plot','--excellon-separate-th','--generate-report','--report-path',OUT/'verification'/(name+'_drill_report.txt'),'-o',str(unit)+'/',pcb])
    for job in unit.glob('*.gbrjob'):
        shutil.move(str(job),str(OUT/'verification'/(name+'_automatic_gbrjob_UNCONFIRMED.json')))
    assert sha(s['path'])==s['sha']
(OUT/'verification/export_log.json').write_text(json.dumps(logs,indent=2,ensure_ascii=False),encoding='utf-8')
combined=OUT/'array_1plus1';combined.mkdir(exist_ok=True)
settings=FileSettings(unit=MM,number_format=(4,6),zeros='leading')
files=[]
for layer in LAYERS.split(','):
    suffix=layer.replace('.','_')
    objects=[];gs=[]
    for name,s in SOURCES.items():
        path=OUT/'units'/name/(name+'-'+suffix+'.gbr')
        g=GerberFile.open(path)
        g.offset(*s['offset'],unit=MM)
        gs.append(g);objects.append(len(g.objects))
    assert gs[0].file_attrs['.FileFunction']==gs[1].file_attrs['.FileFunction']
    gs[0].merge(gs[1])
    # Unit-specific hashes and project IDs no longer describe this combined file.
    for key in ['.MD5','.ProjectId','.SameCoordinates','.CreationDate']:
        gs[0].file_attrs.pop(key,None)
    gs[0].file_attrs['.GenerationSoftware']=('Gerbonara','PPG_UART_1plus1','20261009')
    path=combined/('PPG_UART_1plus1-'+suffix+'.gbr')
    gs[0].save(path,settings=settings)
    # This cached writer omits the terminator on its standalone G75 statement.
    # Emit a complete RS-274X command so CAM parsers reliably select multi-quadrant arcs.
    emitted=path.read_text(encoding='utf-8')
    emitted=re.sub(r'^G75$', 'G75*', emitted, flags=re.M)
    path.write_text(emitted,encoding='utf-8')
    files.append(dict(file=path.name,layer=layer,source_object_counts=objects,combined_object_count=len(gs[0].objects),sha256=sha(path)))
for kind in ['PTH','NPTH']:
    ds=[]
    for name,s in SOURCES.items():
        d=ExcellonFile.open(OUT/'units'/name/(name+'-'+kind+'.drl'),plated=kind=='PTH')
        d.offset(*s['offset'],unit=MM);ds.append(d)
    ds[0].merge(ds[1]);path=combined/('PPG_UART_1plus1-'+kind+'.drl')
    ds[0].save(path,settings=settings)
    emitted=path.read_text(encoding='utf-8').replace('M48\n','M48\n;TYPE='+('PLATED' if kind=='PTH' else 'NON_PLATED')+'\nG90\n',1)
    path.write_text(emitted,encoding='utf-8')
    files.append(dict(file=path.name,drill_type=kind,hit_count=len(ds[0].objects),sha256=sha(path)))
manifest=dict(date='2026-10-09',purpose='1 PPG + 1 UART array artwork for manufacturer CAM; not a self-supporting assembly panel',coordinate_system='mm, top view, +X right, +Y up; no mirroring',board_rotation_deg=0,unit_sources={n:{**s,'path':str(s['path'])} for n,s in SOURCES.items()},array=dict(uart_bounds_mm=[[5,5],[57,30]],ppg_center_mm=[66.75,17.5],ppg_diameter_mm=13.5,minimum_board_gap_mm=3,finished_board_envelope_mm=[68.5,25],suggested_rail_envelope_mm=[78.5,35],rail_in_gerber=False,breakaway_tabs_in_gerber=False,mouse_bites_in_drill=False),files=files)
(OUT/'array_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'complete':True,'array_files':len(files),'sources_unchanged':all(sha(s['path'])==s['sha'] for s in SOURCES.values())}))
