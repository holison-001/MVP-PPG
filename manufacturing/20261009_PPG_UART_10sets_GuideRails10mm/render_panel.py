import json, subprocess, sys
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'.git/all_ground_gerber_20261005/pydeps'))
sys.path.insert(0,str(ROOT/'.git/6layer_impl_20261005/pydeps'))
from gerbonara import GerberFile,ExcellonFile
from gerbonara.utils import MM
from shapely.geometry import shape
NODE=r'C:/Users/LAPTOP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
RENDER=ROOT/'.git/all_ground_gerber_20261005/render_svg.cjs'
manifest=json.loads((OUT/'panel_manifest.json').read_text(encoding='utf-8'))
features=json.loads((OUT/'engineering/panel_geometry.geojson').read_text())['features']
substrate=shape(next(f['geometry'] for f in features if f['properties']['kind']=='substrate'))
def ring(coords):return 'M '+' L '.join(f'{x:.6f},{y:.6f}' for x,y in coords)+' Z'
def path(poly):return ring(poly.exterior.coords)+' '+' '.join(ring(r.coords) for r in poly.interiors)
subpath=path(substrate)
def render(file):subprocess.run([NODE,str(RENDER),str(file),str(file.with_suffix('.png'))],check=True,capture_output=True,creationflags=0x08000000)
def svgitems(layer,fg,bg):
    p=OUT/'gerber'/('PPG_UART_10sets-'+layer+'.gbr')
    return ''.join(str(t) for t in GerberFile.open(p).svg_objects(svg_unit=MM,fg=fg,bg=bg))
for side,layer in [('TOP','F'),('BOTTOM_TOPVIEW','B')]:
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1570" height="1850" viewBox="-3 -5 163 185">','<rect x="-3" y="-5" width="163" height="185" fill="#f4f6f7"/>',f'<text x="0" y="-1" font-family="Arial" font-size="2.1" fill="#1d3241">PPG 10 + UART 10 | 157 x 177 mm | {side} | 10 mm rails</text>','<g transform="translate(0 177) scale(1 -1)">',f'<path d="{subpath}" fill="#355b35" fill-rule="evenodd"/>']
    parts.append(svgitems(layer+'_Cu','#a6aa47','#355b35'))
    parts.append(svgitems(layer+'_Silkscreen','#eef6df','#355b35'))
    # Make carrier fiducials visible after the silk SVG's clear-polarity background.
    # Centers and diameters come from the actual serialized carrier copper/mask files.
    for suffix,fg in [('_Mask','#698151'),('_Cu','#e0c455')]:
        cg=GerberFile.open(OUT/'engineering/carrier_gerber'/('Panel_Carrier_Only-'+layer+suffix+'.gbr'))
        parts.extend(str(t) for t in cg.svg_objects(svg_unit=MM,fg=fg,bg='#355b35'))
    for kind in ['PTH','NPTH']:
        d=ExcellonFile.open(OUT/'gerber'/f'PPG_UART_10sets-{kind}.drl',plated=kind=='PTH')
        parts.extend(str(t) for t in d.svg_objects(svg_unit=MM,fg='#f4f6f7',bg='#f4f6f7'))
    parts.extend([f'<path d="{subpath}" fill="none" stroke="#263b2d" stroke-width="0.035"/>','</g></svg>'])
    file=OUT/'review'/f'PANEL_{side}.svg';file.write_text('\n'.join(parts),encoding='utf-8');render(file)
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1650" height="2050" viewBox="-6 -8 200 235">','<rect x="-6" y="-8" width="200" height="235" fill="#f7fafc"/>','<g font-family="Malgun Gothic,Arial,sans-serif" fill="#19374c">','<text x="0" y="-1" font-size="4.3" font-weight="bold">10세트 패널 · PPG 10개 + UART 10개</text>','<text x="0" y="4" font-size="2.6">2열 × 5행 / 위·아래 10 mm 가이드바 / 단위 mm · 공통 TOP VIEW</text>','<g transform="translate(0 187) scale(1 -1)">',f'<path d="{subpath}" fill="#e1eddf" stroke="#48654b" stroke-width="0.12" fill-rule="evenodd"/>']
for f in features:
    if f['properties']['kind']=='finished_board':
        parts.append(f'<path d="{path(shape(f["geometry"]))}" fill="none" stroke="#709c8b" stroke-width="0.12" stroke-dasharray="0.8 0.7"/>')
for p in manifest['tooling_holes']:parts.append(f'<circle cx="{p["x_mm"]}" cy="{p["y_mm"]}" r="1.5" fill="#f7fafc" stroke="#28607b" stroke-width="0.18"/>')
for p in manifest['fiducials'][:3]:
    parts.append(f'<circle cx="{p["x_mm"]}" cy="{p["y_mm"]}" r="1.5" fill="#f8f1d4" stroke="#cb9c21" stroke-width="0.1"/><circle cx="{p["x_mm"]}" cy="{p["y_mm"]}" r="0.5" fill="#bc9227"/>')
parts.append('</g>')
for inst in manifest['instances']:
    x,y=inst['offset_mm'];cx=x+26 if inst['board']=='UART' else x;cy=y+12.5 if inst['board']=='UART' else y
    parts.append(f'<text x="{cx}" y="{187-cy}" font-size="2.5" text-anchor="middle">{inst["set_id"]} {inst["board"]}</text>')
parts += ['<path d="M 0,195 H 157 M 0,193 V 197 M 157,193 V 197" stroke="#315064" fill="none" stroke-width="0.2"/>','<text x="78.5" y="201" text-anchor="middle" font-size="3.3">157 mm</text>','<path d="M 163,10 V 187 M 161,10 H 165 M 161,187 H 165" stroke="#315064" fill="none" stroke-width="0.2"/>','<text x="169" y="95" font-size="3.3">177 mm</text>','<path d="M 159,10 H 161 M 159,20 H 161 M 160,10 V 20" stroke="#b47824" stroke-width="0.2"/>','<text x="166" y="17" font-size="3">10 mm</text>','<path d="M 159,177 H 161 M 159,187 H 161 M 160,177 V 187" stroke="#b47824" stroke-width="0.2"/>','<text x="166" y="184" font-size="3">10 mm</text>','<text x="0" y="209" font-size="3" font-weight="bold">가이드 홀 Ø3 × 4 / 피듀셜 양면 각 3개 (동박 Ø1 · 마스크 Ø3)</text>','<text x="0" y="215" font-size="2.8">실제 연결 탭 90개 · 폭 3 mm · Ø2 라우팅 슬롯 · 6층 / 공칭 0.8 mm</text>','<text x="0" y="221" font-size="2.8">조립 후 고정 지그 + CNC로 탭 절단. 손으로 꺾거나 V-cut으로 분리하지 않습니다.</text>','<text x="0" y="227" font-size="2.6" fill="#526674">점선은 분리 후 보드 외곽 참조입니다. 생산용 Edge.Cuts에는 연결 탭이 유지됩니다.</text>','</g></svg>']
file=OUT/'PANEL_LAYOUT.svg';file.write_text('\n'.join(parts),encoding='utf-8');render(file)
print('Rendered actual copper previews and dimensioned panel layout.')
