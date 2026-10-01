"""Verify the Microchip MC land pattern and its electrical integration read-only.

Run with KiCad Python. --library-only checks the source footprint before routing.
Default mode also exports the current schematic netlist and checks every PCB pin.
Dimensional source: Microchip DS20005122C pp.29-31, C04-123/C04-2123 Rev E.
Manufacturer drawing is rotated 90 degrees clockwise: body X=3, Y=2 mm.
"""
import argparse
from collections import Counter
import gc
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import pcbnew as k

gc.disable()
NAME = 'MCP1703A_MC_DFN8_3x2mm_P0.5mm'
FPID = 'SleepBud:' + NAME
PIN_POSITIONS = {
    '1': (-1.5, -.75), '2': (-1.5, -.25), '3': (-1.5, .25), '4': (-1.5, .75),
    '5': (1.5, .75), '6': (1.5, .25), '7': (1.5, -.25), '8': (1.5, -.75), '9': (0., 0.),
}
PIN_NETS = {
    'U4': {'1': '5V_LED', '2': None, '3': None, '4': 'GND', '5': None,
           '6': None, '7': None, '8': '12V', '9': 'GND'},
    'U5': {'1': '3V3', '2': None, '3': None, '4': 'GND', '5': None,
           '6': None, '7': None, '8': '5V_LED', '9': 'GND'},
}


def xy(v):
    return [k.ToMM(v.x), k.ToMM(v.y)]


def close(actual, expected):
    return len(actual) == len(expected) and all(math.isclose(a, e, abs_tol=2e-6) for a, e in zip(actual, expected))


def footprint_id(fp):
    return f'{fp.GetFPID().GetLibNickname()}:{fp.GetFPID().GetLibItemName()}'


def geometry(fp, board, errors, label):
    # Clone and normalize only in memory. The saved board is never modified.
    local = k.FOOTPRINT(fp)
    local.SetParent(board)
    local.SetLayerAndFlip(k.F_Cu)
    local.SetOrientationDegrees(0)
    local.SetPosition(k.VECTOR2I(0, 0))
    pads = list(local.Pads())
    numbered = [p for p in pads if p.GetNumber()]
    counts = Counter(p.GetNumber() for p in numbered)
    if counts != Counter({n: 1 for n in PIN_POSITIONS}):
        errors.append(f'{label}: expected exactly pads 1..9 once each, got {dict(counts)}')
    rows = []
    for pad in numbered:
        number = pad.GetNumber()
        if number not in PIN_POSITIONS:
            continue
        size = [1.75, 1.55] if number == '9' else [.85, .30]
        shape = k.PAD_SHAPE_RECT if number == '9' else k.PAD_SHAPE_OVAL
        expected_layers = {k.F_Cu, k.F_Mask} | (set() if number == '9' else {k.F_Paste})
        actual_layers = set(pad.GetLayerSet().Seq())
        row = dict(pin=number, position_mm=xy(pad.GetPosition()), size_mm=xy(pad.GetSize()),
                   orientation_deg=pad.GetOrientationDegrees(), shape=int(pad.GetShape()))
        rows.append(row)
        if not close(row['position_mm'], PIN_POSITIONS[number]):
            errors.append(f'{label}.{number}: center differs from manufacturer land pattern')
        if not close(row['size_mm'], size) or pad.GetShape() != shape:
            errors.append(f'{label}.{number}: land dimensions/shape differ from manufacturer pattern')
        if abs(pad.GetOrientationDegrees() % 180) > 1e-6:
            errors.append(f'{label}.{number}: pad major axis is rotated relative to package')
        if pad.GetAttribute() != k.PAD_ATTRIB_SMD or actual_layers != expected_layers:
            errors.append(f'{label}.{number}: unexpected pad attribute/copper/mask/paste layers')
    paste = [p for p in pads if not p.GetNumber()]
    aperture_positions = sorted(tuple(round(v, 6) for v in xy(p.GetPosition())) for p in paste)
    expected_apertures = sorted((x, y) for x in [-.45, .45] for y in [-.40, .40])
    if aperture_positions != expected_apertures or any(
        not close(xy(p.GetSize()), [.70, .60]) or set(p.GetLayerSet().Seq()) != {k.F_Paste}
        or p.GetShape() != k.PAD_SHAPE_RECT or p.GetNetname() for p in paste
    ):
        errors.append(f'{label}: EP paste must be four unnumbered, non-copper 0.70x0.60 apertures')
    mask_margin = local.GetLocalSolderMaskMargin()
    if mask_margin is None or not math.isclose(k.ToMM(mask_margin), .025, abs_tol=1e-6):
        errors.append(f'{label}: expected explicit 0.025 mm mask expansion')
    fab_points = []
    for item in local.GraphicalItems():
        if isinstance(item, k.PCB_SHAPE) and item.GetLayer() == k.F_Fab:
            fab_points.extend([xy(item.GetStart()), xy(item.GetEnd())])
    fab_bounds = ([min(v[0] for v in fab_points), min(v[1] for v in fab_points),
                   max(v[0] for v in fab_points), max(v[1] for v in fab_points)] if fab_points else [])
    if not close(fab_bounds, [-1.5, -1., 1.5, 1.]):
        errors.append(f'{label}: body Fab envelope must be 3.00x2.00 mm')
    return {'pads': rows, 'body_bounds_mm': fab_bounds, 'paste_aperture_count': len(paste),
            'row_center_spacing_mm': 3.0, 'pitch_mm': .50, 'ep_copper_mm': [1.75, 1.55]}


def main():
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', type=Path, default=directory/'ppg_pcb_v08.kicad_pcb')
    parser.add_argument('--schematic', type=Path, default=directory/'ppg_pcb_v08.kicad_sch')
    parser.add_argument('--design', type=Path, default=directory/'design_v08.py')
    parser.add_argument('--library', type=Path, default=directory/'SleepBud.pretty')
    parser.add_argument('--library-only', action='store_true')
    parser.add_argument('--json', type=Path)
    args = parser.parse_args()
    errors = []
    report = {'ok': False, 'source': 'DS20005122C pp.29-31, C04-123/C04-2123 Rev E',
              'expected_fpid': FPID, 'mode': 'library_only' if args.library_only else 'board_and_schematic', 'errors': errors}
    library_file = args.library/(NAME+'.kicad_mod')
    report['library_sha256'] = hashlib.sha256(library_file.read_bytes()).hexdigest()
    scratch = k.BOARD()
    reference = k.FootprintLoad(str(args.library.resolve()), NAME)
    if reference is None:
        raise RuntimeError(f'Cannot load {library_file}')
    report['source_footprint'] = geometry(reference, scratch, errors, 'library')
    if not args.library_only:
        from schematic_metadata import load_schematic_metadata
        board_hash = hashlib.sha256(args.board.read_bytes()).hexdigest()
        schematic_hash = hashlib.sha256(args.schematic.read_bytes()).hexdigest()
        board = k.LoadBoard(str(args.board.resolve()))
        metadata = load_schematic_metadata(args.schematic)
        spec = importlib.util.spec_from_file_location('mc_validation_design', args.design)
        design = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(design)
        fps = list(board.GetFootprints())
        ref_counts = Counter(f.GetReference() for f in fps)
        expected_refs = set(metadata['components'])
        if ref_counts != Counter({r: 1 for r in expected_refs}) or len(expected_refs) != 37:
            errors.append('Expected exactly 37 distinct PCB/schematic references')
        if set(design.COMPONENTS) != expected_refs:
            errors.append('Source model references differ from schematic')
        actual_pins = Counter((fp.GetReference(), p.GetNumber()) for fp in fps for p in fp.Pads() if p.GetNumber())
        if actual_pins != Counter({p: 1 for p in metadata['pad_nets']}) or sum(actual_pins.values()) != 117:
            errors.append('Expected exactly 117 distinct PCB/schematic pins with no duplicates')
        for fp in fps:
            ref = fp.GetReference()
            component = metadata['components'].get(ref)
            if component and (footprint_id(fp) != component['footprint'] or fp.GetValue() != component['value']):
                errors.append(f'{ref}: PCB/schematic footprint or value mismatch')
            for pad in fp.Pads():
                if pad.GetNumber() and pad.GetNetname() != metadata['pad_nets'].get((ref, pad.GetNumber())):
                    errors.append(f'{ref}.{pad.GetNumber()}: PCB net differs from fresh schematic netlist')
        if len(metadata['net_names']) != 48:
            errors.append('Expected 48 schematic nets')
        report['components'] = {}
        for ref, nets in PIN_NETS.items():
            fp = next((f for f in fps if f.GetReference() == ref), None)
            model = design.COMPONENTS.get(ref, {})
            if fp is None:
                continue
            if footprint_id(fp) != FPID or metadata['components'][ref]['footprint'] != FPID:
                errors.append(f'{ref}: PCB and schematic must use corrected project MC footprint')
            if model.get('fp') != NAME or model.get('lib') not in {'custom', 'SleepBud'}:
                errors.append(f'{ref}: source model still names another footprint')
            if model.get('pins') != nets:
                errors.append(f'{ref}: source-model pin map differs from Microchip pinout')
            if fp.GetLayer() != k.B_Cu:
                errors.append(f'{ref}: expected bottom placement')
            for number, net in nets.items():
                actual = metadata['pad_nets'].get((ref, number), '')
                correct = actual.startswith('unconnected-') if net is None else actual.lstrip('/') == net
                if not correct:
                    errors.append(f'{ref}.{number}: expected logical net {net!r}, got {actual!r}')
            report['components'][ref] = geometry(fp, board, errors, ref)
        report.update(board_sha256=board_hash, schematic_sha256=schematic_hash,
                      references=len(ref_counts), numbered_pads=sum(actual_pins.values()),
                      schematic_nets=len(metadata['net_names']))
        if hashlib.sha256(args.board.read_bytes()).hexdigest() != board_hash or hashlib.sha256(args.schematic.read_bytes()).hexdigest() != schematic_hash:
            errors.append('Inputs changed during validation')
    report['ok'] = not errors
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
