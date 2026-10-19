from pathlib import Path
import subprocess, sys
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'.git/all_ground_gerber_20261005/pydeps'))
from gerbonara import GerberFile,ExcellonFile
from gerbonara.layers import LayerStack
from PIL import Image,ImageDraw,ImageFont
NODE=r'C:/Users/LAPTOP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
RENDER=ROOT/'.git/all_ground_gerber_20261005/render_svg.cjs'
REV=OUT/'review'; REV.mkdir(exist_ok=True)
def render(svg,png): subprocess.run([NODE,str(RENDER),str(svg),str(png)],check=True,capture_output=True,creationflags=0x08000000)
def g(layer): return GerberFile.open(OUT/'array_1plus1'/('PPG_UART_1plus1-'+layer+'.gbr'))
pth=ExcellonFile.open(OUT/'array_1plus1/PPG_UART_1plus1-PTH.drl',plated=True)
npth=ExcellonFile.open(OUT/'array_1plus1/PPG_UART_1plus1-NPTH.drl',plated=False)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',23)
canvas=Image.new('RGB',(1800,1400),'white');draw=ImageDraw.Draw(canvas)
draw.text((28,14),'PPG 1 + UART 1 | 실제 거버 6층 동박 · 공통 TOP VIEW',font=font,fill='#152e40')
for i,layer in enumerate(['F_Cu','In1_Cu','In2_Cu','In3_Cu','In4_Cu','B_Cu']):
    stack=LayerStack(graphic_layers={('mechanical','outline'):g('Edge_Cuts'),('top','copper'):g(layer)},drill_pth=pth,drill_npth=npth)
    svg=REV/(layer+'.svg');png=REV/(layer+'.png')
    svg.write_text(str(stack.to_svg(force_bounds=((0,0),(78.5,35)),colors={'top copper':'#277766','mechanical outline':'#23334a','drill pth':'#ffffff','drill npth':'#ffffff'})),encoding='utf-8')
    render(svg,png)
    im=Image.open(png).convert('RGB');im.thumbnail((875,395))
    x=15+(i%2)*900;y=75+(i//2)*430
    draw.text((x+15,y),f'L{i+1}  {layer.replace("_",".")}',font=font,fill='#23334a')
    canvas.paste(im,(x,y+34))
canvas.save(REV/'copper_6layers.png')
# Dimensioned manufacturing-coordinate diagram. Dashed frame is an advisory envelope only.
scale=14; ox=72; oy=630
X=lambda x:ox+x*scale
Y=lambda y:oy-y*scale
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="825" viewBox="0 0 1240 825">','<rect width="1240" height="825" fill="#f7fafc"/>','<g font-family="Malgun Gothic, sans-serif" fill="#153047">','<text x="44" y="44" font-size="26" font-weight="bold">PPG 1개 + UART 1개 · 제조사 CAM 연배열용</text>','<text x="44" y="76" font-size="16">공통 좌표: mm / 위에서 본 방향 / X →, Y ↑ / 두 보드 회전 0°</text>']
parts += [f'<rect x="{X(0)}" y="{Y(35)}" width="{78.5*scale}" height="{35*scale}" rx="4" fill="none" stroke="#98a5b4" stroke-width="2" stroke-dasharray="10 7"/>',f'<rect x="{X(5)}" y="{Y(30)}" width="{52*scale}" height="{25*scale}" fill="#dcefe8" stroke="#1f6e57" stroke-width="2"/>',f'<circle cx="{X(66.75)}" cy="{Y(17.5)}" r="{6.75*scale}" fill="#e4edf9" stroke="#356b9b" stroke-width="2"/>']
for x,y in [(11.5,23.5),(50.5,23.5),(11.5,11.5),(50.5,11.5)]:
    parts += [f'<circle cx="{X(x)}" cy="{Y(y)}" r="{5.5*scale}" fill="none" stroke="#a7beb3" stroke-dasharray="5 5"/>',f'<circle cx="{X(x)}" cy="{Y(y)}" r="{1.5*scale}" fill="#f7fafc" stroke="#1f6e57"/>']
parts += [f'<text x="{X(31)}" y="{Y(19)}" font-size="23" text-anchor="middle" font-weight="bold">UART 52 × 25 mm</text>',f'<text x="{X(31)}" y="{Y(16)}" font-size="16" text-anchor="middle">좌하단 (5, 5)</text>',f'<text x="{X(66.75)}" y="{Y(18)}" font-size="20" text-anchor="middle" font-weight="bold">PPG Ø13.5</text>',f'<text x="{X(66.75)}" y="{Y(15.5)}" font-size="13" text-anchor="middle">중심 (66.75, 17.5)</text>']
parts += [f'<path d="M {X(57)} {Y(17.5)} H {X(60)}" stroke="#c27221" stroke-width="2"/>',f'<text x="{X(58.5)}" y="{Y(20)}" font-size="13" text-anchor="middle">3 mm</text>',f'<circle cx="{X(0)}" cy="{Y(0)}" r="4" fill="#c27221"/>',f'<text x="{X(0)-15}" y="{Y(0)+26}" font-size="14">(0, 0)</text>',f'<text x="{X(39.25)}" y="{Y(32.5)}" text-anchor="middle" font-size="15" fill="#647589">점선 78.5 × 35 mm = 5 mm 가이드 여유 제안 · 실제 거버에 없음</text>']
parts += ['<text x="44" y="699" font-size="18" font-weight="bold">실제 거버: 완성 외곽 2개 / 보드 영역 합계 경계 68.5 × 25 mm</text>','<text x="44" y="733" font-size="16">제조사 CAM에서 지지 탭·가이드바·툴링·분리 가공 확정 필요. 완성 SMT 패널이 아닙니다.</text>','<text x="44" y="762" font-size="16">PPG 외곽 GND 보존: 완성 외곽선 위 분리 타공 금지. 좌표 이동·회전 시 실장 좌표 재생성.</text>','<text x="44" y="791" font-size="14" fill="#647589">6층 / 공칭 0.8 mm / PTH Ø0.25 × 164 / NPTH Ø3.0 × 4 / 2026-10-09</text>','</g></svg>']
svg=OUT/'ARRAY_LAYOUT.svg';svg.write_text('\n'.join(parts),encoding='utf-8');render(svg,OUT/'ARRAY_LAYOUT.png')
print('Rendered ARRAY_LAYOUT.png and review/copper_6layers.png')
