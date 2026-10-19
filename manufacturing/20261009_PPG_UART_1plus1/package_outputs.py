import hashlib,json,zipfile
from pathlib import Path
OUT=Path(__file__).resolve().parent
sha=lambda data:hashlib.sha256(data).hexdigest()
assert json.loads((OUT/'verification/gerber_independent.json').read_text(encoding='utf-8'))['pass']
coordinates=json.loads((OUT/'verification/coordinates_verification.json').read_text(encoding='utf-8'))
assert coordinates['result']=='PASS'
assert sha((OUT/coordinates['workbook']).read_bytes())==coordinates['sha256']
def package(path,files):
    contents={name:file.read_bytes() for name,file in files}
    checks=''.join(sha(data)+'  '+name+'\n' for name,data in sorted(contents.items()))
    contents['SHA256SUMS.txt']=checks.encode('utf-8')
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in contents.items():z.writestr(name,data)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        assert set(z.namelist())==set(contents)
        assert all(z.read(n)==v for n,v in contents.items())
    return dict(file=path.name,bytes=path.stat().st_size,sha256=sha(path.read_bytes()),entries=len(contents),crc_check='PASS',contents_hash_check='PASS')
main=[]
for file in sorted((OUT/'array_1plus1').iterdir()):
    if file.suffix=='.gbr': folder='stencil' if '_Paste' in file.stem else 'gerber'
    elif file.suffix=='.drl':folder='drill'
    else:continue
    main.append((folder+'/'+file.name,file))
for name in ['README_FABRICATION.md','ARRAY_LAYOUT.png','ARRAY_LAYOUT.svg','array_manifest.json']:
    main.append((name,OUT/name))
xlsx=OUT/'PPG_UART_부품좌표_20261009.xlsx'
assert xlsx.is_file()
main.append(('assembly/'+xlsx.name,xlsx))
main.append(('review/copper_6layers.png',OUT/'review/copper_6layers.png'))
for name in ['gerber_independent.json','coordinates_verification.json']:
    main.append(('verification/'+name,OUT/'verification'/name))
results=[package(OUT/'PPG_UART_1plus1_Gerber_Drill_20261009.zip',main)]
for unit in ['PPG','UART']:
    results.append(package(OUT/(unit+'_Unit_Gerber_Drill_20261009.zip'),[(p.name,p) for p in sorted((OUT/'units'/unit).iterdir()) if p.suffix in ['.gbr','.drl']]))
(OUT/'verification/package_verification.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
