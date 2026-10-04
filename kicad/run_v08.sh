#!/usr/bin/env bash
# Validate the routed board first; publish outputs only after every gate succeeds.
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo_dir=$(cd -- "$script_dir/.." && pwd)
board="$script_dir/ppg_pcb_v08.kicad_pcb"
schematic="$script_dir/ppg_pcb_v08.kicad_sch"
output_dir="$repo_dir"
check_only=1
explicit_check_only=0
publish_approved=0
rebuild=0
usage() {
    cat <<'HELP'
Usage: run_v08.sh [--check-only | --publish-approved-outputs]
                  [--board FILE] [--schematic FILE]
                  [--output-dir DIR] [--rebuild]

Default: validate the existing routed PCB only. No Gerber or BOM is generated.
The source PCB and schematic are never rewritten.
--check-only  Validate only; do not publish manufacturing or documentation outputs.
--publish-approved-outputs
              Use only after explicit user approval for Gerber and BOM creation.
              Publish Gerber/drill ZIP, positions, PDF/SVG, grouped BOM and reports.
              Exports are staged until every check/export passes.
--rebuild     Explicitly rebuild and route a NEW candidate from design_v08.py.
              Requires FREEROUTING. With --check-only, the candidate is temporary.
              With --publish-approved-outputs, save it under DIR/rebuilt/ after
              validation. This never replaces the reviewed source PCB.
--output-dir  Output root (default: repository root; docs/, gerber/, bom/).

Environment (each value is an executable path, not a shell command):
  KICAD_CLI     kicad-cli executable; default: kicad-cli on PATH
  KICAD_PYTHON  Python with pcbnew; default: kicad-python, then python3 on PATH
  BOM_PYTHON    Python with BOM dependencies; default: python3 on PATH
  FREEROUTING  Headless executable/wrapper, or .jar (used with JAVA, default java)
  ROUTE_PASSES Maximum passes for explicit rebuild (default 80)
  ROUTE_THREADS Optimization workers for explicit rebuild (default 4)

Examples:
  source /workspace/.amp-env/activate.sh
  ./run_v08.sh --check-only
  # Only after explicit user approval:
  ./run_v08.sh --publish-approved-outputs --output-dir /workspace/ppg-exports
HELP
}
while (($#)); do
    case "$1" in
        --help|-h) usage; exit 0 ;;
        --check-only) explicit_check_only=1; shift ;;
        --publish-approved-outputs) publish_approved=1; shift ;;
        --rebuild) rebuild=1; shift ;;
        --board|--schematic|--output-dir)
            (($# >= 2)) || { printf 'Missing argument for %s\n' "$1" >&2; exit 2; }
            case "$1" in
                --board) board="$2" ;;
                --schematic) schematic="$2" ;;
                --output-dir) output_dir="$2" ;;
            esac
            shift 2 ;;
        *) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
done
if ((explicit_check_only && publish_approved)); then
    printf 'Choose either --check-only or --publish-approved-outputs.\n' >&2
    exit 2
fi
if ((publish_approved)); then check_only=0; fi
KICAD_CLI=${KICAD_CLI:-$(command -v kicad-cli || true)}
KICAD_PYTHON=${KICAD_PYTHON:-$(command -v kicad-python || command -v python3 || true)}
BOM_PYTHON=${BOM_PYTHON:-$(command -v python3 || true)}
export KICAD_CLI
for executable in "$KICAD_CLI" "$KICAD_PYTHON" "$BOM_PYTHON"; do
    [[ -n "$executable" ]] && command -v "$executable" >/dev/null || {
        printf 'Missing tool. Set KICAD_CLI, KICAD_PYTHON and BOM_PYTHON.\n' >&2; exit 2;
    }
done
[[ -f "$board" && -f "$schematic" ]] || { printf 'PCB or schematic is missing.\n' >&2; exit 2; }
"$KICAD_PYTHON" -c 'import pcbnew' >/dev/null
if ((rebuild)); then
    [[ -n ${FREEROUTING:-} ]] || { printf '--rebuild requires FREEROUTING.\n' >&2; exit 2; }
    if [[ "$FREEROUTING" == *.jar ]]; then
        [[ -f "$FREEROUTING" ]] || { printf 'FREEROUTING jar is missing.\n' >&2; exit 2; }
        router=("${JAVA:-java}" -Djava.awt.headless=true -jar "$FREEROUTING")
    else
        command -v "$FREEROUTING" >/dev/null || { printf 'FREEROUTING is not executable.\n' >&2; exit 2; }
        router=("$FREEROUTING")
    fi
fi
stage=$(mktemp -d "${TMPDIR:-/tmp}/ppg-v08.XXXXXX")
finish() {
    status=$?
    if ((status)); then
        printf 'Stopped (exit %s); no exports published. Diagnostics: %s\n' "$status" "$stage" >&2
    else
        rm -rf -- "$stage"
    fi
}
trap finish EXIT
mkdir -p "$stage/input" "$stage/output/docs/verification_v08" "$stage/output/gerber" "$stage/output/bom"
# Use one immutable snapshot for all checks and outputs, with a matching sibling
# schematic so KiCad's --schematic-parity cannot silently check an unrelated file.
"$BOM_PYTHON" - "$board" "$schematic" "$stage/input" <<'PY'
import json, hashlib, shutil, sys
from pathlib import Path
board, schematic, target = map(lambda x: Path(x).resolve(), sys.argv[1:])
for source, name in [(board, 'ppg_pcb_v08.kicad_pcb'), (schematic, 'ppg_pcb_v08.kicad_sch')]:
    shutil.copy2(source, target / name)
project = board.with_suffix('.kicad_pro')
if not project.is_file():
    project = schematic.with_suffix('.kicad_pro')
if project.is_file():
    shutil.copy2(project, target / 'ppg_pcb_v08.kicad_pro')
custom_rules = board.with_suffix('.kicad_dru')
if custom_rules.is_file():
    shutil.copy2(custom_rules, target / 'ppg_pcb_v08.kicad_dru')
for directory in {board.parent, schematic.parent}:
    for source in directory.iterdir():
        if source.name in {'fp-lib-table', 'sym-lib-table'} or source.suffix in {'.pretty', '.kicad_sym', '.kicad_wks'}:
            dest = target / source.name
            if not dest.exists():
                if source.is_dir():
                    shutil.copytree(source, dest)
                else:
                    shutil.copy2(source, dest)
manifest = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (board, schematic)}
if project.is_file():
    manifest[str(project)] = hashlib.sha256(project.read_bytes()).hexdigest()
if custom_rules.is_file():
    manifest[str(custom_rules)] = hashlib.sha256(custom_rules.read_bytes()).hexdigest()
(target / 'source_sha256.json').write_text(json.dumps(manifest, indent=2) + '\n')
PY
work_board="$stage/input/ppg_pcb_v08.kicad_pcb"
work_schematic="$stage/input/ppg_pcb_v08.kicad_sch"
reports="$stage/output/docs/verification_v08"
if ((rebuild)); then
    "$KICAD_PYTHON" "$script_dir/build_pcb_v08.py" "$work_board"
    # Both inner layers allow routing. In1 retains its GND zone after refill.
    "${router[@]}" --gui.enabled=false -da --user_data_path="$stage/router-data" \
        --router.layers.routable=true,true,true,true --router.fanout.enabled=false \
        -de "$stage/input/ppg_pcb_v08.dsn" -do "$stage/input/ppg_pcb_v08.ses" \
        -mp "${ROUTE_PASSES:-80}" -mt "${ROUTE_THREADS:-4}" -l en
    [[ -s "$stage/input/ppg_pcb_v08.ses" ]] || { printf 'Router produced no session.\n' >&2; exit 1; }
    "$KICAD_PYTHON" "$script_dir/build_pcb_v08.py" "$work_board" --ses "$stage/input/ppg_pcb_v08.ses"
    # Rebuild candidates must follow the reviewed broad In2 power topology.
    # This touches only the temporary candidate, then all normal checks run.
    "$KICAD_PYTHON" "$script_dir/route_in2_power_v08.py" "$work_board" "$work_board"
fi
# Refill the staged board once; checks and exports use this same final input.
"$KICAD_PYTHON" - "$work_board" <<'PY'
import pcbnew, sys
board = pcbnew.LoadBoard(sys.argv[1])
if any(zone.GetLayer() == pcbnew.In2_Cu for zone in board.Zones()):
    raise SystemExit('In2.Cu must use broad 3V3 traces, without a pour')
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(sys.argv[1], board)
PY
"$KICAD_PYTHON" "$script_dir/netcheck_v08.py" "$work_board" \
    --schematic "$work_schematic" --json "$reports/netcheck.json"
# Report warnings, but fail on errors, any missing connection, or any parity
# issue. KiCad exit 5 can reflect warnings only, so inspect the complete JSON.
drc_status=0
"$KICAD_CLI" pcb drc --schematic-parity --severity-all \
    --exit-code-violations --format json -o "$reports/drc.json" "$work_board" || drc_status=$?
[[ "$drc_status" == 0 || "$drc_status" == 5 ]] || exit "$drc_status"
"$BOM_PYTHON" - "$reports/drc.json" <<'PY'
import json, sys
from pathlib import Path
report = json.loads(Path(sys.argv[1]).read_text())
required = {'violations', 'unconnected_items', 'schematic_parity'}
if not required <= report.keys():
    raise SystemExit('DRC report is incomplete: ' + ', '.join(sorted(required - report.keys())))
errors = [v for v in report['violations'] if v.get('severity') == 'error']
warnings = [v for v in report['violations'] if v.get('severity') == 'warning']
unconnected, parity = report['unconnected_items'], report['schematic_parity']
print(f'DRC: {len(errors)} errors, {len(warnings)} warnings, {len(unconnected)} unconnected, {len(parity)} parity issues')
for item in errors + unconnected + parity:
    print(item.get('type', 'issue') + ': ' + item.get('description', ''))
if errors or unconnected or parity:
    raise SystemExit(1)
PY
if ((check_only)); then
    printf 'Checks passed; source PCB and exported files unchanged.\n'
    exit 0
fi
docs="$stage/output/docs"
gerber="$stage/output/gerber"
"$KICAD_CLI" pcb export gerbers \
    --layers 'F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts,F.Fab,B.Fab' \
    --subtract-soldermask --use-drill-file-origin -o "$gerber/" "$work_board"
"$KICAD_CLI" pcb export drill --format excellon --excellon-units mm --drill-origin plot \
    --excellon-separate-th --generate-map --map-format pdf -o "$gerber/" "$work_board"
"$KICAD_CLI" pcb export pos --format csv --units mm --side both --exclude-dnp \
    --use-drill-file-origin -o "$docs/ppg_pcb_v08_positions.csv" "$work_board"
"$KICAD_CLI" pcb export pdf --layers 'F.Cu,B.Cu,In1.Cu,In2.Cu,Edge.Cuts,F.Fab,B.Fab' \
    --mode-multipage -o "$docs/ppg_pcb_v08_layers.pdf" "$work_board"
"$KICAD_CLI" pcb export svg --layers 'F.Cu,F.Fab,Edge.Cuts' --page-size-mode 2 --mode-single \
    -o "$docs/layout_front.svg" "$work_board"
"$KICAD_CLI" pcb export svg --layers 'B.Cu,B.Fab,Edge.Cuts' --page-size-mode 2 --mode-single --mirror \
    -o "$docs/layout_back.svg" "$work_board"
"$KICAD_CLI" sch export pdf -o "$docs/ppg_pcb_v08_schematic.pdf" "$work_schematic"
# BOM is generated by the current-schema exporter (DNP excluded, grouped values,
# package names and datasheet basenames); no old design-data BOM is reused.
"$BOM_PYTHON" "$script_dir/bom_v08.py" --schematic "$work_schematic" --output-dir "$stage/output/bom"
"$BOM_PYTHON" - "$stage" "$output_dir" "$rebuild" <<'PY'
import hashlib, json, shutil, sys, zipfile
from pathlib import Path
stage, output = Path(sys.argv[1]), Path(sys.argv[2]).resolve()
artifacts = stage / 'output'
# Only this run's generated Gerbers/drills enter the manufacturing archive.
with zipfile.ZipFile(artifacts / 'ppg_pcb_v08_gerber.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted((artifacts / 'gerber').iterdir()):
        if path.is_file():
            archive.write(path, path.name)
csvs = sorted((artifacts / 'bom').glob('*.csv'))
if len(csvs) != 1:
    raise SystemExit(f'Expected one grouped BOM CSV, found {len(csvs)}')
shutil.copy2(csvs[0], artifacts / 'docs' / 'ppg_pcb_v08_BOM.csv')
shutil.copy2(stage / 'input' / 'source_sha256.json', artifacts / 'docs' / 'verification_v08' / 'source_sha256.json')
if sys.argv[3] == '1':
    candidate = artifacts / 'rebuilt'
    candidate.mkdir()
    for path in (stage / 'input').iterdir():
        if path.suffix in {'.kicad_pcb', '.kicad_sch', '.kicad_pro', '.kicad_dru', '.kicad_wks', '.dsn', '.ses'}:
            shutil.copy2(path, candidate / path.name)
manifest = {str(path.relative_to(artifacts)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(artifacts.rglob('*')) if path.is_file()}
(artifacts / 'docs' / 'verification_v08' / 'output_sha256.json').write_text(json.dumps(manifest, indent=2) + '\n')
# Publish after every producer succeeded. Existing unrelated files are preserved.
for source in sorted(artifacts.rglob('*')):
    if source.is_file():
        dest = output / source.relative_to(artifacts)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
print(f'Validated exports published: {output}')
PY
