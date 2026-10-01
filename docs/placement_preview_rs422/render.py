"""Render audited placement geometry without modifying the PCB.

Stored polygons already include footprint-side flips and selected rotations.
BOTTOM is viewed directly from the component side (board-wide X reflection).
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/ppg-placement-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager, patheffects
from matplotlib.patches import Circle, Patch, Polygon as PatchPolygon
from shapely.affinity import translate
from shapely.geometry import Point, Polygon, shape
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE.parent / 'verification_rs422_no_bus_tvs/placement'
HISTORY = HERE / 'history_sm71239'
COL = {'board': '#123e3b', 'pad': '#efd28a', 'court': '#70d9d3',
       'body': '#37545f', 'overlap': '#ff4356', 'edge': '#ff9e42', 'swd': '#bdf4ff'}
SWD = {'J7': 'SWDIO', 'J8': 'SWCLK', 'J9': 'NRST'}


def read_json(path):
    return json.loads(Path(path).read_text())


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Scene:
    def __init__(self, placement_path, geometry_path, audit_path):
        self.paths = [Path(placement_path), Path(geometry_path), Path(audit_path)]
        self.placement = read_json(placement_path)['placement']
        self.geometry = read_json(geometry_path)
        self.report = read_json(audit_path)
        self.top_refs = sorted(r for r, p in self.placement.items() if p['side'] == 'F')
        self.bottom_refs = sorted(r for r, p in self.placement.items() if p['side'] == 'B')
        self.radius = self.geometry['board_radius_mm']
        self.copper_radius = self.geometry['copper_radius_mm']
        self.required_edge = self.radius - self.copper_radius
        self.passed = self.report.get('feasible') is True
        assert self.top_refs == ['U1'], 'This renderer expects the fixed PPG top side'
        assert self.placement['U1']['pos'] == [0, 0] and self.placement['U1']['rot'] == 0
        assert set(self.geometry['footprints']) == set(self.bottom_refs)
        for key, path in [('candidate_sha256', placement_path), ('geometry_sha256', geometry_path)]:
            expected = self.report.get(key)
            if expected:
                assert expected == sha256(path), f'Audit does not match {path}'
        for key, value in [('total_components', len(self.placement)), ('bottom_count', len(self.bottom_refs))]:
            if key in self.report:
                assert self.report[key] == value, f'Audit count mismatch: {key}'
        self.parts = {}
        for ref in self.bottom_refs:
            p = self.placement[ref]
            ori = next(o for o in self.geometry['footprints'][ref]['orientations'] if o['rot'] == p['rot'] % 360)
            self.parts[ref] = {key: translate(shape(ori[key]), *p['pos']) for key in ['courtyard', 'copper', 'body']}

    @property
    def status(self):
        return '배치 형상 검증 통과 · 배선 미표시' if self.passed else '배치 형상 검증 미통과 · 배선 미표시'

    @property
    def metrics(self):
        return (f"조립 여유 겹침 {len(self.report['courtyard_overlap_pairs'])}쌍 · "
                f"최소 외곽 간격 {self.report['minimum_copper_edge_clearance_mm']:.3f} mm "
                f"/ 요구 {self.required_edge:.2f} mm")


def draw_poly(ax, geometry, **kwargs):
    if geometry.is_empty:
        return
    if geometry.geom_type == 'Polygon':
        ax.add_patch(PatchPolygon(list(geometry.exterior.coords), **kwargs))
    elif hasattr(geometry, 'geoms'):
        for part in geometry.geoms:
            draw_poly(ax, part, **kwargs)


def frame(ax, title, subtitle, radius, back=True):
    ax.set_facecolor('#f3f6f7')
    ax.add_patch(Circle((0, 0), radius, facecolor=COL['board'], edgecolor='#253f49', lw=1.6, zorder=0))
    ax.set_xlim(-radius - 2.6, radius + 2.6)
    ax.set_ylim(radius + .4, -radius - .4)
    ax.set_aspect('equal')
    if back:
        ax.invert_xaxis()
    ax.set_xticks(range(-6, 7, 2))
    ax.set_yticks(range(-6, 7, 2))
    ax.tick_params(colors='#52636b', labelsize=9)
    ax.set_xlabel('x (mm)')
    ax.set_ylabel('y (mm)')
    ax.set_title(title + '\n' + subtitle, fontsize=13, pad=14, linespacing=1.6, color='#193440')
    ax.grid(color='#becdd1', alpha=.12, lw=.6)
    for spine in ax.spines.values():
        spine.set_visible(False)


def label(ax, xy, ref):
    ax.text(*xy, ref, ha='center', va='center', color='white', fontsize=9 if ref.startswith('U') else 8,
            fontweight='bold', zorder=10,
            path_effects=[patheffects.withStroke(linewidth=2.4, foreground=COL['board'])])


def swd_callouts(ax, positions, radius):
    for side in [-1, 1]:
        refs = sorted((r for r in SWD if r in positions and (1 if positions[r][0] >= 0 else -1) == side),
                      key=lambda r: positions[r][1])
        ys = []
        for ref in refs:
            y = max(-radius + .7, min(radius - .7, positions[ref][1]))
            ys.append(max(y, ys[-1] + 1.1) if ys else y)
        if ys and ys[-1] > radius - .7:
            ys = [y - (ys[-1] - radius + .7) for y in ys]
        for ref, y in zip(refs, ys):
            ax.add_patch(Circle(positions[ref], .52, fill=False, edgecolor=COL['swd'], lw=1.5, zorder=11))
            ax.annotate(f'{ref}\n{SWD[ref]}', xy=positions[ref], xytext=(side * (radius + 2.2), y),
                        color='#143f50', fontsize=9, fontweight='bold', ha='left' if side > 0 else 'right',
                        va='center', zorder=12, bbox=dict(boxstyle='round,pad=.25', fc='#e6f4f8', ec='#8cafbc', lw=.6),
                        arrowprops=dict(arrowstyle='-', color='#54bddb', lw=1.2, shrinkB=6))


def legacy_view(ax, legacy, radius, front=False):
    positions = {}
    for fp in legacy['footprints']:
        if fp['side'] != ('front' if front else 'back'):
            continue
        if front:
            draw_poly(ax, Polygon([(-1.45, -2.15), (1.45, -2.15), (1.45, 2.15), (-1.45, 2.15)]),
                      facecolor=COL['body'], edgecolor='#bed9dc', lw=.65, zorder=1)
        for p in fp['pads']:
            draw_poly(ax, Polygon(p['points']), facecolor=COL['pad'], edgecolor='#d6b76e', lw=.35, zorder=3)
        for p in fp['court']:
            draw_poly(ax, Polygon(p), fill=False, edgecolor=COL['court'], lw=.65, ls='--', zorder=4)
        label(ax, fp['xy'], fp['ref'])
        positions[fp['ref']] = fp['xy']
    if front:
        ax.text(0, 3.35, 'MAXM86161EFD+\nPPG U1만 탑면 · 중심 위치 유지', ha='center', va='center',
                fontsize=11, color='white', linespacing=1.8)
    else:
        swd_callouts(ax, positions, radius)


def candidate_view(ax, scene, highlight_removed=False):
    courts, copper = [], []
    for ref, part in scene.parts.items():
        courts.append(part['courtyard'])
        copper.append(part['copper'])
        draw_poly(ax, part['body'], facecolor=COL['body'], edgecolor='#b6ccd0', lw=.5, zorder=1)
        draw_poly(ax, part['copper'], facecolor=COL['pad'], edgecolor='#d6b76e', lw=.35, zorder=3)
        draw_poly(ax, part['courtyard'], fill=False, edgecolor=COL['court'], lw=.7, ls='--', zorder=4)
        label(ax, scene.placement[ref]['pos'], ref)
        if highlight_removed and ref in ['D2', 'D4']:
            draw_poly(ax, part['courtyard'], fill=False, edgecolor='#ffd78a', lw=2, zorder=5)
    overlaps = unary_union([a.intersection(b) for i, a in enumerate(courts) for b in courts[:i]])
    draw_poly(ax, overlaps, facecolor=COL['overlap'], edgecolor=COL['overlap'], lw=1.4, zorder=6)
    allowed = Point(0, 0).buffer(scene.copper_radius, resolution=1024)
    draw_poly(ax, unary_union(copper).difference(allowed), facecolor=COL['edge'], edgecolor=COL['edge'], lw=1.3, zorder=7)
    ax.add_patch(Circle((0, 0), scene.copper_radius, fill=False, edgecolor=COL['edge'], lw=.9,
                        ls=(0, (4, 4)), alpha=.75, zorder=5))
    swd_callouts(ax, {r: p['pos'] for r, p in scene.placement.items()}, scene.radius)


def footer(fig, scene, extra=None):
    fig.legend(handles=[Patch(facecolor=COL['pad'], label='동박 패드'),
                        Patch(facecolor='none', edgecolor=COL['court'], linestyle='--', label='조립 여유 영역'),
                        Patch(facecolor=COL['overlap'], label='조립 여유 겹침'),
                        Patch(facecolor=COL['edge'], label='외곽 간격 부족')],
               loc='lower center', bbox_to_anchor=(.5, .082), ncol=4, frameon=False, fontsize=10)
    fig.text(.5, .062, '최신 배치: ' + scene.metrics, ha='center', fontsize=11,
             color='#246550' if scene.passed else '#a43239')
    body_count = len(scene.report.get('body_overlaps', []))
    fig.text(.5, .037, f'본체 겹침 {body_count}건 · 부품 배치만 표시 · 배선/비아 미표시 · PCB 배선 및 제조 검증 별도',
             ha='center', fontsize=10, color='#52636b')
    if extra:
        fig.text(.5, .015, extra, ha='center', fontsize=10, color='#52636b')


def figure(title):
    fig, axes = plt.subplots(1, 2, figsize=(18, 10))
    fig.subplots_adjust(top=.86, bottom=.20, left=.035, right=.98, wspace=.12)
    fig.suptitle(title, fontsize=19, y=.97, color='#193440')
    return fig, axes


def save(fig, path):
    fig.savefig(path, dpi=190, facecolor='white')
    plt.close(fig)
    print(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--placement', type=Path, default=DEFAULT_DATA / 'placement_candidate.json')
    parser.add_argument('--geometry', type=Path, default=DEFAULT_DATA / 'geometry.json')
    parser.add_argument('--audit', type=Path, default=DEFAULT_DATA / 'placement_audit.json')
    parser.add_argument('--output-dir', type=Path, default=HERE)
    args = parser.parse_args()
    font_path = Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
    if font_path.exists():
        font_manager.fontManager.addfont(str(font_path))
    plt.rcParams.update({'font.family': 'Noto Sans CJK JP', 'font.size': 10, 'axes.unicode_minus': False})
    scene = Scene(args.placement, args.geometry, args.audit)
    old = Scene(HISTORY / 'packing_strict_best.json', HISTORY / 'packing_geometry_physical.json',
                HISTORY / 'mechanical_candidate_assessment.json')
    legacy_path = HERE / 'legacy_lvds_geometry.json'
    legacy = read_json(legacy_path)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    count = len(scene.placement)
    bottom_count = len(scene.bottom_refs)
    current_change = 'D2·D4 제거' if not {'D2', 'D4'} & set(scene.placement) else 'SM712 포함'
    fig, axes = figure(f'MVP-PPG  |  RS-422 {count}부품 배치  |  Ø{scene.radius * 2:g} mm')
    frame(axes[0], 'TOP · 탑 부품면', f'{len(scene.top_refs)}레퍼런스 · U1 위치/방향 유지', scene.radius, False)
    legacy_view(axes[0], legacy, scene.radius, True)
    frame(axes[1], 'BOTTOM · 바텀 부품면', f'{bottom_count}레퍼런스 · {scene.status}', scene.radius)
    candidate_view(axes[1], scene)
    footer(fig, scene, current_change + ' · J7 SWDIO / J8 SWCLK / J9 NRST')
    outputs = [args.output_dir / 'rs422_top_bottom.png']
    save(fig, outputs[-1])
    fig, axes = figure(f'MVP-PPG  |  {current_change} 전후 바텀 배치  |  Ø{scene.radius * 2:g} mm')
    frame(axes[0], f'이전 RS-422 · {len(old.placement)}부품 · SM712 포함',
          f'{len(old.bottom_refs)}레퍼런스 · {old.status}', old.radius)
    candidate_view(axes[0], old, True)
    frame(axes[1], f'현재 RS-422 · {count}부품 · {current_change}',
          f'{bottom_count}레퍼런스 · {scene.status}', scene.radius)
    candidate_view(axes[1], scene)
    footer(fig, scene, '왼쪽 노란 테두리: 제거된 D2·D4 위치 · 양쪽 모두 부품면에서 본 바텀')
    outputs.append(args.output_dir / 'd2_d4_removed_comparison.png')
    save(fig, outputs[-1])
    fig, axes = figure(f'MVP-PPG  |  과거 LVDS와 현재 RS-422 배치 비교  |  Ø{scene.radius * 2:g} mm')
    legacy_count = sum(p['side'] == 'back' for p in legacy['footprints'])
    frame(axes[0], '과거 LVDS · 이력 참고', f'이전 배치 · {legacy_count}레퍼런스', scene.radius)
    legacy_view(axes[0], legacy, scene.radius)
    frame(axes[1], f'현재 RS-422 · {count}부품', f'{bottom_count}레퍼런스 · {scene.status}', scene.radius)
    candidate_view(axes[1], scene)
    footer(fig, scene, 'LVDS 그림은 이전 설계 이력이며 현재 RS-422 PCB 상태를 나타내지 않습니다.')
    outputs.append(args.output_dir / 'bottom_before_after.png')
    save(fig, outputs[-1])
    inputs = scene.paths + old.paths + [legacy_path, HERE / 'render.py']
    def manifest_path(path):
        return os.path.relpath(path.resolve(), args.output_dir.resolve())
    manifest = {
        'view': 'Each side viewed directly; BOTTOM horizontally mirrored from KiCad board coordinates',
        'status': 'Placement geometry only; routing/vias not rendered; not manufacturing validation',
        'total_components': count, 'top_refs': scene.top_refs, 'bottom_count': bottom_count,
        'placement_geometry_passed': scene.passed, 'swd_pad_functions': SWD,
        'source_board': scene.report.get('source_board'),
        'source_files': {manifest_path(p): sha256(p) for p in inputs},
        'output_files': {p.name: sha256(p) for p in outputs},
    }
    (args.output_dir / 'source_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    readme = f'''# RS-422 부품 배치 화면

현재 {count}부품({len(scene.top_refs)}개 탑 / {bottom_count}개 바텀)의 저장된 배치 도형을 표시합니다. {current_change} 상태이며 탑면 U1 위치·방향은 유지합니다.

- `rs422_top_bottom.png`: 현재 탑/바텀 배치. **{scene.status}**.
- `d2_d4_removed_comparison.png`: 이전 {len(old.placement)}부품 SM712 구성과 현재 {count}부품 비교.
- `bottom_before_after.png`: 과거 LVDS 배치와 현재 RS-422 비교. LVDS 그림은 이력 참고입니다.
- `history_sm71239/`: 이전 {len(old.placement)}부품 후보의 원본 좌표·도형·검증 결과.

각 면을 부품 쪽에서 직접 본 방향입니다. 바텀은 KiCad 보드 좌표에서 좌우 반전했으며, J7 SWDIO / J8 SWCLK / J9 NRST를 외부 인출선으로 표시했습니다.

현재 형상 판정: {scene.metrics}. 실제 본체 겹침은 {len(scene.report.get('body_overlaps', []))}건입니다. 조립 여유 겹침은 빨강, 구리–외곽 간격 부족은 주황으로 표시합니다.

이 그림은 부품 배치 화면이며 배선·비아를 표시하지 않습니다. 형상 통과 표시는 배치 검사만 뜻하며 PCB 배선, 전기적 연결, 제조 검증의 완료를 뜻하지 않습니다.

Matplotlib·Shapely가 설치된 Python에서 `python3 render.py`로 다시 그릴 수 있습니다. 현재 클라우드 환경에서는 `PYTHONPATH=/workspace/.amp-env/python-extra python3 render.py`를 사용합니다. 임시 후보는 `--placement`, `--geometry`, `--audit`, `--output-dir` 옵션으로 별도 출력할 수 있습니다. 입력·출력 SHA-256은 `source_manifest.json`에 기록됩니다.
'''
    (args.output_dir / 'README.md').write_text(readme)


if __name__ == '__main__':
    main()
