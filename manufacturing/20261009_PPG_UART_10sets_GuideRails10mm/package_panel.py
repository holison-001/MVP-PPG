import hashlib,json,shutil,zipfile
from pathlib import Path
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((OUT/'panel_manifest.json').read_text(encoding='utf-8'))
for f in manifest['files']:assert sha(OUT/f['file'])==f['sha256'],f['file']
for name in ['panel_gerber_independent.json','panel_mechanical_independent.json']:
    r=json.loads((OUT/'verification'/name).read_text(encoding='utf-8'))
    assert r.get('pass',r.get('result')=='PASS'),(name,r.keys())
    if name=='panel_gerber_independent.json':assert r['manifest_sha256']==sha(OUT/'panel_manifest.json'),'Gerber report is stale'
    else:assert r['source_geojson_sha256']==sha(OUT/'engineering/panel_geometry.geojson'),'Mechanical report is stale'
coords=json.loads((OUT/'verification/coordinates_verification.json').read_text(encoding='utf-8'))
assert coords['result']=='PASS';assert sha(OUT/coords['workbook'])==coords['sha256']
features=json.loads((OUT/'engineering/panel_geometry.geojson').read_text(encoding='utf-8'))['features']
lines=['0','SECTION','2','HEADER','9','$ACADVER','1','AC1009','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES']
paths=[f['geometry']['coordinates'] for f in features if f['properties']['kind']=='final_cut_centerline']
for path in paths:
    lines+=['0','POLYLINE','8','TAB_CUT_CENTER_R1_REF','66','1','70','0','10','0','20','0','30','0']
    for x,y in path:lines+=['0','VERTEX','8','TAB_CUT_CENTER_R1_REF','10',f'{x:.6f}','20',f'{y:.6f}','30','0']
    lines+=['0','SEQEND']
lines+=['0','ENDSEC','0','EOF']
dxf=OUT/'reference/FINAL_TAB_CUT_TOOLCENTER_REFERENCE.dxf';dxf.write_text('\n'.join(lines)+'\n',encoding='ascii')
assert len(paths)==100
assert sum(1 for l in lines if l=='POLYLINE')==100
shutil.copy2(OUT/'engineering/panel_geometry.geojson',OUT/'reference/panel_geometry.geojson')
contents={}
for file in sorted((OUT/'gerber').iterdir()):
    if file.suffix=='.drl':folder='drill'
    elif file.suffix=='.gbr':folder='stencil' if '_Paste' in file.stem else 'gerber'
    else:continue
    contents[folder+'/'+file.name]=file
for name in ['README_FABRICATION.md','PANEL_LAYOUT.png','PANEL_LAYOUT.svg','panel_manifest.json']:contents[name]=OUT/name
contents['assembly/'+coords['workbook']]=OUT/coords['workbook']
for name in ['PANEL_TOP.png','PANEL_BOTTOM_TOPVIEW.png']:contents['review/'+name]=OUT/'review'/name
for name in ['panel_gerber_independent.json','panel_mechanical_independent.json','coordinates_verification.json']:contents['verification/'+name]=OUT/'verification'/name
for file in (OUT/'reference').iterdir():contents['reference/'+file.name]=file
payload={name:p.read_bytes() for name,p in contents.items()}
payload['SHA256SUMS.txt']=''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name,data in sorted(payload.items())).encode('utf-8')
zip_path=OUT/'PPG_UART_10sets_GuideRails10mm_Gerber_20261009.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,data in payload.items():z.writestr(name,data)
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None
    assert set(z.namelist())==set(payload)
    assert all(z.read(name)==data for name,data in payload.items())
report=dict(file=zip_path.name,size_bytes=zip_path.stat().st_size,sha256=sha(zip_path),entries=len(payload),crc_check='PASS',contents_hash_check='PASS',dxf_reference_path_count=len(paths),source_boards_unchanged=all(sha(Path(s['path']))==s['sha'] for s in manifest['unit_sources'].values()))
(OUT/'verification/package_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
