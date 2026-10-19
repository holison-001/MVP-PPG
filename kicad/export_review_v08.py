"""Export PCB review PDF/SVG/PNG only, without Gerber, drill, positions or BOM.

Run the separate run_v08.sh --check-only validation before publishing a final
review. This exporter reads the PCB and never changes its geometry or routing.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def main():
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', type=Path, default=root / 'kicad/ppg_pcb_v08.kicad_pcb')
    parser.add_argument('--output-dir', type=Path, default=root / 'docs')
    args = parser.parse_args()
    board = args.board.resolve()
    output = args.output_dir.resolve()
    layers = output / 'layers_png'
    layers.mkdir(parents=True, exist_ok=True)
    cli = os.environ.get('KICAD_CLI', 'kicad-cli')
    inkscape = os.environ.get('INKSCAPE', 'inkscape')
    before = hashlib.sha256(board.read_bytes()).hexdigest()
    entries = [
        ('01_F_Cu_TOP', 'F.Cu,F.Mask,F.Fab,Edge.Cuts', False, 'TOP: GND, D6/D7 ESD, exposed pogo pads and fabrication labels, viewed from top'),
        ('02_In1_Cu_GND', 'In1.Cu,Edge.Cuts', False, 'Layer 2: dedicated GND plane, viewed from top'),
        ('03_In2_Cu_SIGNAL', 'In2.Cu,Edge.Cuts', False, 'Layer 3: signals and full-board GND pour, viewed from top'),
        ('04_In3_Cu_POWER', 'In3.Cu,Edge.Cuts', False, 'Layer 4: broad 3V3, selected signals and full-board GND pour, viewed from top'),
        ('05_In4_Cu_GND', 'In4.Cu,Edge.Cuts', False, 'Layer 5: GND plane and selected short detours, viewed from top'),
        ('06_B_Cu_BOTTOM', 'B.Cu,Edge.Cuts', True, 'BOTTOM copper and GND pour, viewed from bottom, mirrored'),
    ]
    records = []
    for name, selection, mirror, view in entries:
        svg = layers / (name + '.svg')
        png = layers / (name + '.png')
        command = [cli, 'pcb', 'export', 'svg', '--layers', selection,
                   '--fit-page-to-board', '--exclude-drawing-sheet', '--mode-single',
                   '--drill-shape-opt', '2', '-o', str(svg)]
        if mirror:
            command.append('--mirror')
        subprocess.run(command + [str(board)], check=True)
        subprocess.run([inkscape, str(svg), '--export-type=png', '--export-width=1800',
                        '--export-background=white', '--export-background-opacity=1',
                        '--export-filename=' + str(png)], check=True, capture_output=True)
        records.append({'file': png.name, 'layers': selection, 'view': view,
                        'sha256': hashlib.sha256(png.read_bytes()).hexdigest(),
                        'svg_file': svg.name,
                        'svg_sha256': hashlib.sha256(svg.read_bytes()).hexdigest()})
    subprocess.run([cli, 'pcb', 'export', 'pdf', '--layers',
                    'F.Cu,In1.Cu,In2.Cu,In3.Cu,In4.Cu,B.Cu', '--common-layers', 'Edge.Cuts',
                    '--mode-multipage', '--scale', '1', '-o',
                    str(output / 'ppg_pcb_v08_layers.pdf'), str(board)], check=True)
    # Preserve the actual custom drawing-sheet position in a separate 1:1 view.
    sheet_svg = output / 'pcb_sheet.svg'
    sheet_png = output / 'pcb_sheet.png'
    subprocess.run([cli, 'pcb', 'export', 'svg', '--layers', 'F.Cu,F.Fab,Edge.Cuts',
                    '--mode-single', '--scale', '1', '-o', str(sheet_svg), str(board)], check=True)
    subprocess.run([inkscape, str(sheet_svg), '--export-type=png', '--export-width=2400',
                    '--export-background=white', '--export-background-opacity=1',
                    '--export-filename=' + str(sheet_png)], check=True, capture_output=True)
    assert hashlib.sha256(board.read_bytes()).hexdigest() == before, 'Source PCB changed during export'
    (layers / 'source_manifest.json').write_text(json.dumps({
        'source_board': str(board), 'board_sha256': before,
        'companion_files_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in [board.with_suffix('.kicad_pro'), board.with_suffix('.kicad_dru'),
                                             board.parent / 'ppg_compact.kicad_wks']
                                   if p.is_file()},
        'exporter_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'purpose': 'PCB review only; manufacturing and BOM exports require user approval',
        'images': records,
        'sheet_view': {'file': sheet_png.name, 'svg_file': sheet_svg.name,
                       'view': 'Actual 40 x 40 mm sheet, 1:1 PCB scale, viewed from top',
                       'sha256': hashlib.sha256(sheet_png.read_bytes()).hexdigest(),
                       'svg_sha256': hashlib.sha256(sheet_svg.read_bytes()).hexdigest()},
        'pdf': {'file': 'ppg_pcb_v08_layers.pdf',
                'layers': ['F.Cu', 'In1.Cu', 'In2.Cu', 'In3.Cu', 'In4.Cu', 'B.Cu'],
                'view': 'All PDF layers viewed from top at 1:1 on the custom sheet; bottom PNG is mirrored',
                'sha256': hashlib.sha256((output / 'ppg_pcb_v08_layers.pdf').read_bytes()).hexdigest()},
    }, indent=2) + '\n')
    (layers / 'README.md').write_text(
        '# RS-422 PCB 레이어 검토 PNG\n\n'
        '현재 PCB에서 직접 출력한 검토 이미지입니다. 탑면과 내층은 위에서 본 방향, '
        '바텀면은 부품 쪽에서 본 방향으로 좌우 반전했습니다. '
        '배선 확인을 위해 구리와 보드 외곽을 표시합니다. 탑면은 GND 포고 패드를 '
        '식별할 수 있도록 마스크 개구와 F.Fab 검토 표기를 함께 표시합니다. '
        '정확한 부품 위치는 원본 PCB에서 확인합니다.\n\n'
        + ''.join(f'- [{item["file"]}]({item["file"]}): {item["view"]}\n' for item in records)
        + '\n[도면 시트 내 PCB 위치](../pcb_sheet.png)도 별도로 출력했습니다.\n'
        + '\n거버·BOM을 생성하지 않는 검토 출력입니다. 원본 PCB와 이미지 해시는 '
        '`source_manifest.json`에 기록했습니다.\n')


if __name__ == '__main__':
    main()
