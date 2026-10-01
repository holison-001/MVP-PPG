"""Check PCB references, pad nets, metadata and side constraints against the schematic.

Run with KiCad's Python: netcheck_v08.py [board.kicad_pcb] [--json report.json]
This is read-only. Connectivity/routing clearance is checked separately by DRC.
"""

import argparse
from collections import Counter
import json
import math
from pathlib import Path

import pcbnew

import design_v08 as D
from schematic_metadata import load_schematic_metadata


def check_board(board, metadata):
    errors = []
    components = metadata["components"]
    footprints = list(board.GetFootprints())
    ref_counts = Counter(fp.GetReference() for fp in footprints)
    expected_refs = set(components)
    actual_refs = set(ref_counts)
    for ref, count in ref_counts.items():
        if count != 1:
            errors.append(f"Duplicate reference {ref}: {count} footprints")
    for ref in sorted(expected_refs - actual_refs):
        errors.append(f"Missing footprint: {ref}")
    for ref in sorted(actual_refs - expected_refs):
        errors.append(f"Unexpected footprint: {ref}")
    if set(D.COMPONENTS) != expected_refs:
        errors.append("design_v08.COMPONENTS references differ from the current schematic: "
                      f"missing={sorted(expected_refs - set(D.COMPONENTS))}, "
                      f"extra={sorted(set(D.COMPONENTS) - expected_refs)}")

    top_refs = sorted(fp.GetReference() for fp in footprints if fp.GetLayer() == pcbnew.F_Cu)
    if top_refs != ["U1"]:
        errors.append(f"Only U1 may be on the top side; found {top_refs}")

    thickness_mm = pcbnew.ToMM(board.GetDesignSettings().GetBoardThickness())
    copper_layers = board.GetCopperLayerCount()
    if not math.isclose(thickness_mm, D.THICKNESS, abs_tol=1e-6):
        errors.append(f"Board thickness: expected {D.THICKNESS} mm, got {thickness_mm} mm")
    if copper_layers != D.LAYERS:
        errors.append(f"Copper layers: expected {D.LAYERS}, got {copper_layers}")
    edges = [item for item in board.GetDrawings()
             if isinstance(item, pcbnew.PCB_SHAPE) and item.GetLayer() == pcbnew.Edge_Cuts]
    radius_mm = None
    if len(edges) != 1 or edges[0].GetShape() != pcbnew.SHAPE_T_CIRCLE:
        errors.append("Board outline: expected one circular Edge.Cuts shape")
    else:
        edge = edges[0]
        center = edge.GetCenter()
        end = edge.GetEnd()
        radius_mm = math.hypot(pcbnew.ToMM(end.x - center.x), pcbnew.ToMM(end.y - center.y))
        if not math.isclose(radius_mm, D.BOARD_R, abs_tol=1e-6):
            errors.append(f"Board radius: expected {D.BOARD_R} mm, got {radius_mm} mm")
        if center.x != 0 or center.y != 0:
            errors.append("Board outline center must remain at the origin")

    numbered_pads = 0
    for fp in footprints:
        ref = fp.GetReference()
        if fp.GetLayer() not in (pcbnew.F_Cu, pcbnew.B_Cu):
            errors.append(f"{ref}: footprint is not on an outer copper layer")
        if ref not in components:
            continue
        comp = components[ref]
        footprint_id = f"{fp.GetFPID().GetLibNickname()}:{fp.GetFPID().GetLibItemName()}"
        checks = {"footprint": footprint_id, "value": fp.GetValue(), "path": fp.GetPath().AsString()}
        for key, actual in checks.items():
            if actual != comp[key]:
                errors.append(f"{ref} {key}: expected {comp[key]!r}, got {actual!r}")
        for key, expected in comp["fields"].items():
            field = fp.GetField(key)
            actual = field.GetText() if field is not None else ""
            if actual != expected:
                errors.append(f"{ref} {key}: expected {expected!r}, got {actual!r}")

        expected_pins = {pin for (net_ref, pin) in metadata["pad_nets"] if net_ref == ref}
        actual_pins = set()
        for pad in fp.Pads():
            number = pad.GetNumber()
            if not number:
                if pad.GetNetname():
                    errors.append(f"{ref}: unnumbered pad unexpectedly assigned to {pad.GetNetname()!r}")
                continue
            numbered_pads += 1
            actual_pins.add(number)
            expected = metadata["pad_nets"].get((ref, number))
            actual = pad.GetNetname()
            if expected is None:
                errors.append(f"{ref}.{number}: pad has no matching schematic pin")
            elif actual != expected:
                errors.append(f"{ref}.{number} net: expected {expected!r}, got {actual!r}")
        for number in sorted(expected_pins - actual_pins):
            errors.append(f"{ref}.{number}: schematic pin has no matching PCB pad")

    routing = Counter("via" if item.GetClass() == "PCB_VIA" else board.GetLayerName(item.GetLayer())
                      for item in board.GetTracks())
    inner_tracks = [item for item in board.GetTracks()
                    if item.GetClass() != "PCB_VIA" and item.GetLayer() not in (pcbnew.F_Cu, pcbnew.B_Cu)]
    if inner_tracks:
        inner_layers = Counter(board.GetLayerName(item.GetLayer()) for item in inner_tracks)
        errors.append(f"Inner copper layers must remain planes without routed track segments: {dict(inner_layers)}")
    return {
        "ok": not errors,
        "footprints": len(footprints),
        "schematic_components": len(components),
        "numbered_pads": numbered_pads,
        "schematic_nets": len(metadata["net_names"]),
        "top_references": top_refs,
        "board_thickness_mm": thickness_mm,
        "copper_layers": copper_layers,
        "outline_radius_mm": radius_mm,
        "routing": dict(routing),
        "inner_layer_track_count": len(inner_tracks),
        "errors": errors,
    }


def main():
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board", nargs="?", type=Path, default=directory / "ppg_pcb_v08.kicad_pcb")
    parser.add_argument("--schematic", type=Path, default=directory / "ppg_pcb_v08.kicad_sch")
    parser.add_argument("--json", dest="report", type=Path, help="Optional machine-readable report")
    args = parser.parse_args()
    if not args.board.is_file():
        parser.error(f"Board does not exist: {args.board}")
    if not args.schematic.is_file():
        parser.error(f"Schematic does not exist: {args.schematic}")
    board = pcbnew.LoadBoard(str(args.board.resolve()))
    result = check_board(board, load_schematic_metadata(args.schematic))
    result["board"] = str(args.board.resolve())
    result["schematic"] = str(args.schematic.resolve())
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"PCB/schematic: {'PASS' if result['ok'] else 'FAIL'}; "
          f"{result['footprints']} footprints, {result['numbered_pads']} numbered pads, "
          f"{result['schematic_nets']} schematic nets; top={result['top_references']}")
    print("routing:", result["routing"])
    for error in result["errors"]:
        print("ERROR:", error)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
