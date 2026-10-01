#!/usr/bin/env python3
"""Read-only electrical audit; writes only this directory's JSON report.

KiCad ERC and netlist exports run in a temporary directory. PCB placement is
intentionally excluded from the comparison against the archived 39-part design.
Run with Python 3; optionally set KICAD_CLI to the KiCad CLI executable.
"""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "docs/legacy_rs422_with_sm712"
REMOVED = {"D2", "D4"}
CHECKS = {}


def check(name, condition):
    CHECKS[name] = bool(condition)
    if not condition:
        raise AssertionError(name)


def model(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.COMPONENTS


def canonical_xml(element):
    return (element.tag, sorted(element.attrib.items()),
            (element.text or "").strip(),
            [canonical_xml(c) for c in element])


def netlist(path):
    tree = ET.parse(path).getroot()
    components = {c.attrib["ref"]: canonical_xml(c)
                  for c in tree.findall("./components/comp")}
    nets = {n.attrib["name"]: {
        (p.attrib["ref"], p.attrib["pin"]): dict(p.attrib)
        for p in n.findall("node")} for n in tree.findall("./nets/net")}
    return components, nets


def sexpr(path):
    stack, root = [], None
    for token in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', path.read_text()):
        if token == "(":
            node = []
            if stack:
                stack[-1].append(node)
            else:
                root = node
            stack.append(node)
        elif token == ")":
            stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    assert not stack
    return root


def children(node, key):
    return [n for n in node[1:] if isinstance(n, list) and n[0] == key]


def child(node, key):
    return children(node, key)[0]


def symbols(path):
    root = sexpr(path)
    result = {}
    for symbol in children(root, "symbol"):
        fields = {p[1]: p[2] for p in children(symbol, "property")}
        ref = fields["Reference"]
        if ref.startswith("#"):
            continue
        result[ref] = {
            "fields": fields,
            "lib_id": child(symbol, "lib_id")[1],
            "uuid": child(symbol, "uuid")[1],
            "pin_uuids": {p[1]: child(p, "uuid")[1]
                          for p in children(symbol, "pin")},
        }
    return child(root, "uuid")[1], result


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source_paths = [
        ROOT / "kicad" / name for name in (
            "design_v08.py", "build_sch_v08.py", "layout_schematic_v08.py",
            "SleepBud.kicad_sym", "ppg_pcb_v08.kicad_sch",
            "ppg_pcb_v08.kicad_pro", "sym-lib-table", "fp-lib-table")
        if (ROOT / "kicad" / name).is_file()
    ] + [
        BASE / "kicad/design_v08.py",
        BASE / "kicad/ppg_pcb_v08.kicad_sch",
        BASE / "docs/verification_rs422_schematic/netlist.xml",
        OUT / "netlist.xml", OUT / "erc.json", Path(__file__).resolve(),
    ]
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in source_paths}
    report = {
        "status": "running", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Schematic electrical data only; not PCB routing/manufacturing approval",
        "excluded_model_fields": ["pos", "rot"],
        "source_sha256": hashes, "checks": CHECKS,
    }
    try:
        before = model(BASE / "kicad/design_v08.py", "audit_before")
        after = model(ROOT / "kicad/design_v08.py", "audit_after")
        check("only_D2_D4_removed_from_model", set(before) - set(after) == REMOVED
              and set(after) <= set(before))
        electrical = lambda c: {k: v for k, v in c.items() if k not in {"pos", "rot"}}
        check("surviving_model_fields_and_pins_preserved",
              all(electrical(c) == electrical(before[r]) for r, c in after.items()))
        old_uuid, old_symbols = symbols(BASE / "kicad/ppg_pcb_v08.kicad_sch")
        new_uuid, new_symbols = symbols(ROOT / "kicad/ppg_pcb_v08.kicad_sch")
        check("schematic_refs_match_model", set(new_symbols) == set(after))
        check("root_schematic_uuid_preserved", old_uuid == new_uuid)
        check("surviving_symbol_fields_and_pin_UUIDs_preserved",
              all(old_symbols[r] == s for r, s in new_symbols.items()))

        executable = os.environ.get("KICAD_CLI") or shutil.which("kicad-cli")
        if not executable:
            executable = "/workspace/.amp-env/bin/kicad-cli"
        schematic = ROOT / "kicad/ppg_pcb_v08.kicad_sch"
        with tempfile.TemporaryDirectory(prefix="ppg-electrical-audit-") as tmp:
            fresh_netlist, fresh_erc = Path(tmp) / "netlist.xml", Path(tmp) / "erc.json"
            commands = [
                [executable, "sch", "export", "netlist", "--format", "kicadxml",
                 "-o", str(fresh_netlist), str(schematic)],
                [executable, "sch", "erc", "--format", "json",
                 "-o", str(fresh_erc), str(schematic)],
            ]
            for command in commands:
                subprocess.run(command, check=True, capture_output=True, text=True)
            old_components, old_nets = netlist(BASE / "docs/verification_rs422_schematic/netlist.xml")
            new_components, new_nets = netlist(fresh_netlist)
            check("fresh_export_matches_stored_netlist", (new_components, new_nets) == netlist(OUT / "netlist.xml"))
            check("only_D2_D4_removed_from_netlist", set(old_components) - set(new_components) == REMOVED
                  and set(new_components) <= set(old_components))
            check("all_surviving_component_XML_fields_preserved",
                  all(old_components[r] == c for r, c in new_components.items()))
            expected_nets = {name: {pin: attrs for pin, attrs in pins.items() if pin[0] not in REMOVED}
                             for name, pins in old_nets.items()}
            expected_nets = {name: pins for name, pins in expected_nets.items() if pins}
            check("only_D2_D4_six_nodes_removed", new_nets == expected_nets)
            removed_nodes = sorted([list(pin) for pins in old_nets.values() for pin in pins if pin[0] in REMOVED])
            check("removed_node_count_is_six", len(removed_nodes) == 6)
            check("exported_refs_match_model", set(new_components) == set(after))
            actual_pins = {pin: name.lstrip("/") for name, pins in new_nets.items() for pin in pins}
            model_pins = {(ref, pin): net for ref, c in after.items() for pin, net in c["pins"].items()}
            check("exported_pins_match_model", set(actual_pins) == set(model_pins))
            check("every_pin_has_expected_net", all(
                actual_pins[p].startswith("unconnected-") if n is None else actual_pins[p] == n
                for p, n in model_pins.items()))
            check("counts_37_refs_117_pins_48_nets",
                  (len(new_components), len(actual_pins), len(new_nets)) == (37, 117, 48))
            erc = json.loads(fresh_erc.read_text())
            violations = [v for sheet in erc["sheets"] for v in sheet.get("violations", [])]
            check("fresh_ERC_zero_errors_and_warnings", not violations)
            report.update({
                "components_before": len(old_components), "components_after": len(new_components),
                "pins_after": len(actual_pins), "nets_after": len(new_nets),
                "removed_references": sorted(REMOVED), "removed_net_nodes": removed_nodes,
                "erc_violations": len(violations), "erc_kicad_version": erc.get("kicad_version"),
                "erc_included_severities": erc.get("included_severities"),
                "erc_ignored_checks": erc.get("ignored_checks"),
                "fresh_exports_sha256": {"netlist.xml": sha(fresh_netlist), "erc.json": sha(fresh_erc)},
            })
        check("source_hashes_unchanged_during_audit",
              all(sha(p) == hashes[str(p.relative_to(ROOT))] for p in source_paths))
        report["status"] = "pass"
    except Exception as exc:
        report["status"] = "fail"
        report["failure"] = str(exc)
        raise
    finally:
        target = OUT / "electrical_final_audit.json"
        target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        print(f"{report['status']}: {target}")


if __name__ == "__main__":
    main()
