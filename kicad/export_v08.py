"""Validate and export the existing authoritative PPG board and schematic.

Run with KiCad Python. Nothing is rebuilt or rerouted. A temporary source copy
is refilled and checked before any deliverables are generated. Failed checks or
exports retain their staging folder and leave existing deliverables untouched.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STEM = "ppg_pcb_v08"


def discover_cli(override=None):
    candidates = [override, os.environ.get("KICAD_CLI")]
    for directory in [os.environ.get("KICAD_BIN"), str(Path(sys.executable).parent)]:
        if directory:
            candidates.extend(str(Path(directory) / name) for name in ["kicad-cli.exe", "kicad-cli"])
    candidates.append(shutil.which("kicad-cli"))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Path(candidate).resolve()
    raise FileNotFoundError("kicad-cli unavailable; use KiCad Python, --cli, KICAD_CLI or KICAD_BIN")


def runtime_environment(cli):
    environment = os.environ.copy()
    shares = [cli.parent.parent / "share" / "kicad", Path("/usr/share/kicad"),
              cli.parent.parent / "SharedSupport"]
    resolved = {}
    for variable, folder in [("KICAD10_FOOTPRINT_DIR", "footprints"),
                             ("KICAD10_3DMODEL_DIR", "3dmodels"),
                             ("KICAD10_SYMBOL_DIR", "symbols")]:
        candidates = ([Path(environment[variable])] if environment.get(variable) else [])
        candidates += [share / folder for share in shares]
        directory = next((path.resolve() for path in candidates if path.is_dir()), None)
        if directory is None:
            raise FileNotFoundError(f"Cannot locate {folder}; set {variable}")
        environment[variable] = str(directory)
        resolved[variable] = str(directory)
    return environment, resolved


def stage_sources(destination):
    destination.mkdir()
    required = [STEM + extension for extension in [".kicad_pcb", ".kicad_sch", ".kicad_pro"]]
    for name in required:
        if not (HERE / name).is_file():
            raise FileNotFoundError(HERE / name)
    for path in HERE.iterdir():
        if path.is_dir() and path.suffix in {".pretty", ".3dshapes"}:
            shutil.copytree(path, destination / path.name)
        elif path.is_file() and (path.suffix in {".kicad_pcb", ".kicad_sch", ".kicad_pro", ".kicad_dru", ".kicad_sym", ".kicad_wks"}
                                or path.name in {"fp-lib-table", "sym-lib-table"}):
            shutil.copy2(path, destination / path.name)
    # Legacy project defaults must not silently suppress checks. Only the staged
    # checking project is changed; the user's project settings remain intact.
    project_path = destination / (STEM + ".kicad_pro")
    project = json.loads(project_path.read_text(encoding="utf-8"))
    changes = []
    sections = [("DRC", project.setdefault("board", {}).setdefault("design_settings", {}), "drc_exclusions"),
                ("ERC", project.setdefault("erc", {}), "erc_exclusions")]
    for kind, section, exclusion_key in sections:
        for name, severity in section.setdefault("rule_severities", {}).items():
            if severity == "ignore":
                section["rule_severities"][name] = "warning"
                changes.append(dict(check=kind, rule=name, previous="ignore", checked_as="warning"))
        if section.get(exclusion_key):
            changes.append(dict(check=kind, restored_exclusion_count=len(section[exclusion_key])))
        section[exclusion_key] = []
    project_path.write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")
    return changes


def collect_issues(value):
    if isinstance(value, dict):
        if "severity" in value:
            yield value
        else:
            for child in value.values():
                yield from collect_issues(child)
    elif isinstance(value, list):
        for child in value:
            yield from collect_issues(child)


def check_summary(path, kind):
    report = json.loads(path.read_text(encoding="utf-8"))
    if kind == "DRC":
        for key in ["violations", "unconnected_items", "schematic_parity"]:
            if not isinstance(report.get(key), list):
                raise ValueError("Incomplete DRC report: missing " + key)
    elif not isinstance(report.get("sheets"), list):
        raise ValueError("Incomplete ERC report: missing sheets")
    issues = list(collect_issues(report))
    counts = Counter(issue["severity"] for issue in issues)
    unknown = set(counts) - {"error", "warning", "exclusion"}
    result = dict(errors=counts["error"], warnings=counts["warning"], exclusions=counts["exclusion"],
                  unconnected=len(report.get("unconnected_items", [])),
                  schematic_parity=len(report.get("schematic_parity", [])),
                  ignored_checks=report.get("ignored_checks", []),
                  issue_types=dict(Counter(issue.get("type", "unknown") for issue in issues)))
    result["passed"] = not (unknown or result["errors"] or result["exclusions"]
                            or result["unconnected"] or result["schematic_parity"] or result["ignored_checks"])
    return result


def replace_directory(source, destination):
    """Publish a fresh generated directory, with rollback if its rename fails."""
    parent = destination.parent.resolve()
    token = uuid.uuid4().hex
    incoming = parent / ("." + destination.name + "-new-" + token)
    previous = parent / ("." + destination.name + "-old-" + token)
    shutil.copytree(source, incoming)
    try:
        if destination.exists():
            destination.rename(previous)
        incoming.rename(destination)
    except Exception:
        if previous.exists() and not destination.exists():
            previous.rename(destination)
        raise
    finally:
        for path in [incoming, previous]:
            if path.exists() and path.resolve().parent == parent:
                shutil.rmtree(path)


def run_export(args):
    import verify_v08 as verify
    import bom_v08 as bom
    import pcbnew

    cli = discover_cli(args.cli)
    environment, library_paths = runtime_environment(cli)
    temp_parent = Path(args.work_dir).resolve() if args.work_dir else Path(tempfile.gettempdir()).resolve()
    temp_parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="ppg-export-", dir=temp_parent)).resolve()
    print("Staging: " + str(stage), flush=True)
    source, docs, gerber = stage / "kicad", stage / "docs", stage / "gerber"
    docs.mkdir()
    gerber.mkdir()
    log_path = stage / "export.log"

    def command(label, arguments):
        print(label, flush=True)
        result = subprocess.run([str(cli)] + [str(argument) for argument in arguments],
                                cwd=source, env=environment, capture_output=True,
                                text=True, encoding="utf-8", errors="replace")
        with log_path.open("a", encoding="utf-8") as stream:
            stream.write("\n" + label + "\n" + result.stdout + result.stderr + f"\nExit: {result.returncode}\n")
        if result.returncode:
            raise RuntimeError(f"{label} failed (exit {result.returncode}); see {log_path}")
        return result.stdout.strip()

    try:
        input_hashes = {name: verify.sha256(HERE / name) for name in
                        [STEM + ".kicad_pcb", STEM + ".kicad_sch", STEM + ".kicad_pro", "design_v08.py"]}
        restored_checks = stage_sources(source)
        board, schematic = source / (STEM + ".kicad_pcb"), source / (STEM + ".kicad_sch")
        version = command("KiCad version", ["--version"])
        xml = source / "netlist.xml"
        command("Export schematic connectivity", ["sch", "export", "netlist", "--format", "kicadxml", "-o", xml, schematic])
        erc = docs / (STEM + "_ERC.json")
        drc = docs / (STEM + "_DRC.json")
        command("Check schematic (all severities)", ["sch", "erc", "--severity-all", "--format", "json", "-o", erc, schematic])
        command("Refill and check PCB, including schematic parity", ["pcb", "drc", "--severity-all", "--all-track-errors",
                "--schematic-parity", "--refill-zones", "--save-board", "--format", "json", "-o", drc, board])
        verification = verify.verify(board, xml, schematic)
        verification["netlist_source"] = "fresh kicad-cli export in isolated staging folder"
        verification["authoritative_input_hashes"] = input_hashes
        (docs / (STEM + "_verification.json")).write_text(json.dumps(verification, indent=2) + "\n", encoding="utf-8")
        checks = dict(ERC=check_summary(erc, "ERC"), DRC=check_summary(drc, "DRC"),
                      identity_and_connectivity=verification["status"])
        (stage / "check_summary.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
        if verification["status"] != "PASS" or not all(checks[kind]["passed"] for kind in ["ERC", "DRC"]):
            raise RuntimeError("Validation gate failed; no deliverables published. See " + str(stage / "check_summary.json"))
        print(f"Checks passed; ERC warnings {checks['ERC']['warnings']}, DRC warnings {checks['DRC']['warnings']}", flush=True)
        if args.check_only:
            return dict(status="PASS", mode="checks only", staging_directory=str(stage), checks=checks)

        layers = "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts,F.Fab,B.Fab"
        command("Export Gerbers", ["pcb", "export", "gerbers", "--layers", layers, "--subtract-soldermask", "--no-x2", "--use-drill-file-origin", "-o", str(gerber) + os.sep, board])
        command("Export drill files and maps", ["pcb", "export", "drill", "--format", "excellon", "--drill-origin", "plot",
                "--excellon-units", "mm", "--excellon-separate-th", "--generate-map", "--map-format", "pdf", "-o", str(gerber) + os.sep, board])
        command("Export placement coordinates", ["pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "--use-drill-file-origin", "-o", docs / (STEM + "_positions.csv"), board])
        # The board is centered at (0, 0), not inside an A4 drawing sheet.
        # Autoscale centers the entire board; 1:1 plotting clips negative XY.
        command("Export PCB layers PDF", ["pcb", "export", "pdf", "--layers", "F.Cu,B.Cu,In1.Cu,In2.Cu,Edge.Cuts,F.Fab,B.Fab", "--common-layers", "Edge.Cuts", "--scale", "0", "--mode-multipage", "--no-property-popups", "-o", docs / (STEM + "_layers.pdf"), board])
        command("Export schematic PDF", ["sch", "export", "pdf", "-o", docs / (STEM + "_schematic.pdf"), schematic])
        command("Export STEP", ["pcb", "export", "step", "--subst-models", "-o", docs / (STEM + ".step"), board])
        for label, side, copper, mirror in [("front", "top", "F", []), ("back", "bottom", "B", ["--mirror"])]:
            command("Export " + label + " assembly PDF", ["pcb", "export", "pdf", "--layers", f"{copper}.Fab,Edge.Cuts", "--mode-single", "--scale", "0", "--no-property-popups", *mirror, "-o", docs / (STEM + "_assembly_" + label + ".pdf"), board])
            command("Render " + label, ["pcb", "render", "--side", side, "--background", "opaque", "--quality", "high", "-w", "1400", "--height", "1400", "-o", docs / ("render_" + label + ".png"), board])
            command("Export " + label + " SVG", ["pcb", "export", "svg", "--layers", f"{copper}.Cu,{copper}.Fab,Edge.Cuts", "--mode-single", "--page-size-mode", "2", *mirror, "-o", docs / ("layout_" + label + ".svg"), board])
        archive = stage / (STEM + "_gerber.zip")
        bom_summary = bom.export(board, docs, gerber, archive)
        required_docs = [STEM + suffix for suffix in ["_BOM.csv", "_assembly_positions.csv", "_copper_pads.csv", "_BOM_summary.json", "_positions.csv", "_layers.pdf", "_schematic.pdf", ".step"]]
        required_docs += ["render_front.png", "render_back.png", "layout_front.svg", "layout_back.svg",
                          STEM + "_assembly_front.pdf", STEM + "_assembly_back.pdf"]
        required_gerbers = [STEM + suffix for suffix in ["-F_Cu.gtl", "-In1_Cu.g1", "-In2_Cu.g2", "-B_Cu.gbl",
                            "-F_Paste.gtp", "-B_Paste.gbp", "-F_Mask.gts", "-B_Mask.gbs",
                            "-F_Silkscreen.gto", "-B_Silkscreen.gbo", "-Edge_Cuts.gm1", "-F_Fab.gbr", "-B_Fab.gbr",
                            "-PTH.drl", "-NPTH.drl", "-PTH-drl_map.pdf", "-NPTH-drl_map.pdf", "-job.gbrjob"]]
        for path in [docs / name for name in required_docs] + [gerber / name for name in required_gerbers] + [archive]:
            if not path.is_file() or not path.stat().st_size:
                raise RuntimeError("Export did not produce a nonempty expected file: " + str(path))
        if input_hashes != {name: verify.sha256(HERE / name) for name in input_hashes}:
            raise RuntimeError("Source files changed during export; no deliverables published")
        checked_board = pcbnew.LoadBoard(str(board))
        no_models = sorted(fp.GetReference() for fp in checked_board.GetFootprints()
                           if not verify.is_copper_feature(verify.D.COMPONENTS[fp.GetReference()]) and not list(fp.Models()))
        manifest = dict(status="PASS", created_at=datetime.now(timezone.utc).isoformat(), kicad_version=version,
                        authoritative_input_hashes=input_hashes, checked_board_sha256=verify.sha256(board),
                        libraries=library_paths, checks=checks, checks_restored_in_staging=restored_checks,
                        component_counts=bom_summary, components_without_3D_models=no_models,
                        board_thickness_mm=verification["geometry"]["thickness_mm"],
                        stackup_status="Nominal 0.8 mm board thickness; fabricator layer/material stackup remains unconfirmed.",
                        files={str(path.relative_to(stage)): dict(bytes=path.stat().st_size, sha256=verify.sha256(path))
                               for path in sorted(list(docs.iterdir()) + list(gerber.iterdir()) + [archive]) if path.is_file()})
        (docs / (STEM + "_export_manifest.json")).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        shutil.copy2(log_path, docs / (STEM + "_export.log"))
        # All generation succeeded. Publish only generated documents; replace the
        # entire generated Gerber directory so obsolete plots cannot survive.
        (ROOT / "docs").mkdir(exist_ok=True)
        replace_directory(gerber, ROOT / "gerber")
        for path in docs.iterdir():
            shutil.copy2(path, ROOT / "docs" / path.name)
        shutil.copy2(archive, ROOT / archive.name)
        if args.save_refill:
            shutil.copy2(board, HERE / board.name)
        result = dict(status="PASS", checks=checks, manifest=str(ROOT / "docs" / (STEM + "_export_manifest.json")),
                      source_refill_saved=args.save_refill)
        if not args.keep_stage and stage.parent == temp_parent and stage.name.startswith("ppg-export-"):
            shutil.rmtree(stage)
        else:
            result["staging_directory"] = str(stage)
        return result
    except Exception as exc:
        return dict(status="FAIL", error=str(exc), staging_directory=str(stage), log=str(log_path))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", help="kicad-cli executable; otherwise discover beside Python or from KICAD_CLI/KICAD_BIN")
    parser.add_argument("--check-only", action="store_true", help="Run all checks, retain reports in staging, publish no exports")
    parser.add_argument("--work-dir", type=Path, help="Parent directory for fresh staging folders (default: system temporary directory)")
    parser.add_argument("--keep-stage", action="store_true", help="Retain successful staging files")
    parser.add_argument("--save-refill", action="store_true", help="After successful exports, save the checked refilled board back to kicad/")
    args = parser.parse_args(argv)
    try:
        result = run_export(args)
    except Exception as exc:
        result = dict(status="FAIL", error=str(exc))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
