"""Render stored engineering geometry only; does not change the PCB or placement."""
import os,json,hashlib
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/ppg-placement-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager,patheffects
from matplotlib.patches import Polygon as PatchPolygon,Circle,Patch
from shapely.geometry import shape,Polygon,Point
from shapely.affinity import translate
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parent
DATA=HERE.parent/'verification_rs422_schematic/placement_feasibility'
font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams.update({'font.family':'Noto Sans CJK JP','font.size':10,'axes.unicode_minus':False})
placement=json.loads((DATA/'packing_strict_best.json').read_text())['placement']
geometry=json.loads((DATA/'packing_geometry_physical.json').read_text())['footprints']
report=json.loads((DATA/'mechanical_candidate_assessment.json').read_text())
legacy=json.loads((HERE/'legacy_lvds_geometry.json').read_text())
COL={'board':'#123e3b','pad':'#efd28a','court':'#70d9d3','body':'#37545f','overlap':'#ff4356','edge':'#ff9e42'}
def draw_poly(ax,g,**kwargs):
 if g.is_empty:return
 if g.geom_type=='Polygon':ax.add_patch(PatchPolygon(list(g.exterior.coords),**kwargs))
 elif hasattr(g,'geoms'):
  for p in g.geoms:draw_poly(ax,p,**kwargs)
def frame(ax,title,subtitle,back=True):
 ax.set_facecolor('#f3f6f7');ax.add_patch(Circle((0,0),6.75,facecolor=COL['board'],edgecolor='#253f49',lw=1.6,zorder=0))
 ax.set_xlim(-7.15,7.15);ax.set_ylim(7.15,-7.15);ax.set_aspect('equal')
 if back:ax.invert_xaxis()
 ax.set_xticks(range(-6,7,2));ax.set_yticks(range(-6,7,2));ax.tick_params(colors='#52636b',labelsize=9)
 ax.set_xlabel('x (mm)');ax.set_ylabel('y (mm)')
 ax.set_title(title+'\n'+subtitle,fontsize=14,pad=15,linespacing=1.6,color='#193440')
 ax.grid(color='#becdd1',alpha=.12,lw=.6)
 for spine in ax.spines.values():spine.set_visible(False)
def label(ax,xy,ref):
 ax.text(*xy,ref,ha='center',va='center',color='white',fontsize=9 if ref.startswith('U')else 8,fontweight='bold',zorder=10,path_effects=[patheffects.withStroke(linewidth=2.4,foreground=COL['board'])])
def legacy_view(ax,front=False):
 for fp in legacy['footprints']:
  if fp['side']!=('front'if front else'back'):continue
  if front:draw_poly(ax,Polygon([(-1.45,-2.15),(1.45,-2.15),(1.45,2.15),(-1.45,2.15)]),facecolor=COL['body'],edgecolor='#bed9dc',lw=.65,zorder=1)
  for p in fp['pads']:draw_poly(ax,Polygon(p['points']),facecolor=COL['pad'],edgecolor='#d6b76e',lw=.35,zorder=3)
  for p in fp['court']:draw_poly(ax,Polygon(p),fill=False,edgecolor=COL['court'],lw=.65,ls='--',zorder=4)
  label(ax,fp['xy'],fp['ref'])
 if front:
  ax.text(0,3.35,'MAXM86161EFD+\nPPG U1만 탑면 · 중심 위치 유지',ha='center',va='center',fontsize=11,color='white',linespacing=1.8)
def candidate_view(ax):
 courts=[];pad_geometries=[]
 for ref,fp in geometry.items():
  c=placement[ref];ori=next(o for o in fp['orientations']if o['rot']==c['rot']%360)
  court=translate(shape(ori['courtyard']),*c['pos']);cu=translate(shape(ori['copper']),*c['pos']);body=translate(shape(ori['body']),*c['pos'])
  courts.append(court);pad_geometries.append(cu)
  draw_poly(ax,body,facecolor=COL['body'],edgecolor='#b6ccd0',lw=.5,zorder=1)
  draw_poly(ax,cu,facecolor=COL['pad'],edgecolor='#d6b76e',lw=.35,zorder=3)
  draw_poly(ax,court,fill=False,edgecolor=COL['court'],lw=.7,ls='--',zorder=4)
  label(ax,c['pos'],ref)
 overlaps=unary_union([a.intersection(b)for i,a in enumerate(courts)for b in courts[:i]])
 draw_poly(ax,overlaps,facecolor=COL['overlap'],edgecolor=COL['overlap'],lw=1.4,zorder=6)
 allowed=Point(0,0).buffer(6.45,resolution=1024)
 draw_poly(ax,unary_union(pad_geometries).difference(allowed),facecolor=COL['edge'],edgecolor=COL['edge'],lw=1.3,zorder=7)
 ax.add_patch(Circle((0,0),6.45,fill=False,edgecolor=COL['edge'],lw=.9,ls=(0,(4,4)),alpha=.75,zorder=5))
def footer(fig):
 fig.legend(handles=[Patch(facecolor=COL['pad'],label='동박 패드'),Patch(facecolor='none',edgecolor=COL['court'],linestyle='--',label='조립 여유 영역'),Patch(facecolor=COL['overlap'],label='조립 여유 겹침'),Patch(facecolor=COL['edge'],label='외곽 간격 부족')],loc='lower center',bbox_to_anchor=(.5,.075),ncol=4,frameon=False,fontsize=10)
 fig.text(.5,.042,'RS-422 검토안: 조립 여유 겹침 44쌍 · 최소 외곽 간격 0.263 mm / 요구 0.30 mm',ha='center',fontsize=11,color='#a43239')
 fig.text(.5,.018,'실제 본체 겹침 0건 · 부품 배치만 표시 · 배선/비아 미표시 · 제조용 확정 배치 아님',ha='center',fontsize=10,color='#52636b')
def save(figure,path):
 figure.savefig(path,dpi=190,facecolor='white');plt.close(figure)
fig,axs=plt.subplots(1,2,figsize=(16,9.5));fig.subplots_adjust(top=.86,bottom=.19,left=.055,right=.975,wspace=.15)
fig.suptitle('MVP-PPG  |  RS-422 배치 검토안  |  Ø13.5 mm',fontsize=19,y=.97,color='#193440')
frame(axs[0],'TOP · 탑 부품면','U1 1개 · 위치/방향 유지',False);legacy_view(axs[0],True)
frame(axs[1],'BOTTOM · 바텀 부품면','38레퍼런스 · RS-422 변경안 · 검증 미통과');candidate_view(axs[1]);footer(fig)
save(fig,HERE/'rs422_top_bottom.png')
fig,axs=plt.subplots(1,2,figsize=(16,9.5));fig.subplots_adjust(top=.86,bottom=.19,left=.055,right=.975,wspace=.15)
fig.suptitle('MVP-PPG  |  바텀 배치 비교  |  Ø13.5 mm',fontsize=19,y=.97,color='#193440')
frame(axs[0],'변경 전 · LVDS','현재 PCB에 저장된 배치 · 34레퍼런스');legacy_view(axs[0])
frame(axs[1],'변경 후 · RS-422 검토안','배선 전 후보 · 38레퍼런스 · 검증 미통과');candidate_view(axs[1]);footer(fig)
save(fig,HERE/'bottom_before_after.png')
files=[DATA/'packing_strict_best.json',DATA/'packing_geometry_physical.json',DATA/'mechanical_candidate_assessment.json',HERE/'legacy_lvds_geometry.json',HERE/'render.py',HERE/'rs422_top_bottom.png',HERE/'bottom_before_after.png']
(HERE/'source_manifest.json').write_text(json.dumps({'view':'Each side viewed directly; bottom horizontally mirrored from board coordinates','status':'Placement preview only; not routed or approved','files':{str(p.relative_to(HERE.parent)):hashlib.sha256(p.read_bytes()).hexdigest()for p in files}},indent=2)+'\n')
print(HERE/'rs422_top_bottom.png');print(HERE/'bottom_before_after.png')
