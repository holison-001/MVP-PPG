"""Export BOM and placement lists from the final board, without guessed parts.

Run with KiCad Python from any directory. Copper cable/debug pads are listed
separately from assembled components. Positions and rotations are actual PCB
coordinates: origin at board centre, x right, y down, KiCad angle convention.
"""
import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import zipfile

import pcbnew
import design_v08 as D
from verify_v08 import HERE, actual_fpid, expected_fpid, is_copper_feature, point, ref_key, sha256


def write_csv(path, headers, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)


def export(board_path, output_dir, gerber_dir, zip_path):
    board = pcbnew.LoadBoard(str(board_path))
    all_footprints = list(board.GetFootprints())
    ref_counts = Counter(fp.GetReference() for fp in all_footprints)
    if set(ref_counts) != set(D.COMPONENTS) or any(count != 1 for count in ref_counts.values()):
        raise ValueError("PCB references do not match design exactly; run netcheck_v08.py")
    footprints = {fp.GetReference(): fp for fp in all_footprints}
    groups = defaultdict(list)
    placements, copper_features = [], []
    for ref in sorted(D.COMPONENTS, key=ref_key):
        component, fp = D.COMPONENTS[ref], footprints[ref]
        if fp.GetValue() != component["value"] or actual_fpid(fp) != expected_fpid(component):
            raise ValueError("PCB value/footprint differs from design for " + ref)
        side = "Bottom(B)" if fp.IsFlipped() else "Top(F)"
        x, y = point(fp.GetPosition())
        row = [ref, fp.GetValue(), actual_fpid(fp), side, f"{x:.6f}", f"{y:.6f}", f"{fp.GetOrientationDegrees():.6f}"]
        if is_copper_feature(component):
            copper_features.append(row + [component["pins"]["1"], "Copper feature; no component to purchase/place", component.get("desc", "")])
            continue
        placements.append(row)
        key = (component["value"], actual_fpid(fp), side, component.get("mpn", ""), component.get("datasheet", ""))
        groups[key].append(ref)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for (value, fpid, side, mpn, datasheet), refs in groups.items():
        notes = "; ".join(ref + ": " + D.COMPONENTS[ref].get("desc", "") for ref in refs)
        if not mpn:
            notes += "; MPN not specified in design; select a part meeting the stated value/package/rating"
        rows.append([", ".join(refs), len(refs), value, fpid, side, mpn, datasheet, notes])
    write_csv(output_dir / "ppg_pcb_v08_BOM.csv",
              ["Refs", "Qty", "Value / required specification", "Footprint", "Side", "MPN (explicit design field)", "Datasheet", "Notes"], rows)
    position_headers = ["Ref", "Value", "Footprint", "Side", "X_mm (right)", "Y_mm (down)", "Rotation_deg (KiCad)"]
    write_csv(output_dir / "ppg_pcb_v08_assembly_positions.csv", position_headers, placements)
    write_csv(output_dir / "ppg_pcb_v08_copper_pads.csv", position_headers + ["Net", "Assembly classification", "Description"], copper_features)
    result = dict(status="PASS", PCB_references=len(footprints), design_references=len(D.COMPONENTS),
                  board_sha256=sha256(board_path), design_sha256=sha256(HERE / "design_v08.py"),
                  assembled_components=len(placements), nonplaced_copper_features=len(copper_features),
                  BOM_line_items=len(rows), copper_feature_refs=[row[0] for row in copper_features],
                  coordinate_system="PCB origin at centre; x right; y down; native KiCad rotation, actual PCB side",
                  unspecified_MPN_refs=[ref for ref, c in D.COMPONENTS.items() if not is_copper_feature(c) and not c.get("mpn")])
    if zip_path is not None:
        files = sorted(path for path in gerber_dir.iterdir() if path.is_file())
        if not files:
            raise ValueError("No Gerber/drill files found; refusing to create an empty fabrication archive")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, path.name)
        result["archive_file_count"] = len(files)
    (output_dir / "ppg_pcb_v08_BOM_summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", type=Path, default=HERE / "ppg_pcb_v08.kicad_pcb")
    parser.add_argument("--output-dir", type=Path, default=HERE.parent / "docs")
    parser.add_argument("--gerber-dir", type=Path, default=HERE.parent / "gerber")
    parser.add_argument("--zip", type=Path, default=HERE.parent / "ppg_pcb_v08_gerber.zip")
    parser.add_argument("--no-zip", action="store_true", help="Only generate BOM and placement reports")
    args = parser.parse_args(argv)
    try:
        result = export(args.board.resolve(), args.output_dir.resolve(), args.gerber_dir.resolve(), None if args.no_zip else args.zip.resolve())
    except Exception as exc:
        result = dict(status="FAIL", error=str(exc))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
