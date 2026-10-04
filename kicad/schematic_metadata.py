"""Synchronize a pcbnew board with a freshly exported schematic netlist.

This updates footprint metadata and pad net assignments, not routing.  Callers
must reroute changed connections and run schematic parity plus DRC afterwards.
"""

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

import pcbnew


def _kicad_cli():
    configured = os.environ.get("KICAD_CLI")
    if configured:
        return configured
    executable = shutil.which("kicad-cli") or shutil.which("kicad-cli.exe")
    if executable:
        return executable
    for name in ("kicad-cli.exe", "kicad-cli"):
        sibling = Path(sys.executable).with_name(name)
        if sibling.is_file():
            return str(sibling)
    raise RuntimeError("kicad-cli is required; add it to PATH or set KICAD_CLI")


def load_schematic_metadata(schematic_path=None):
    """Read the current schematic through KiCad, never an old cached netlist."""
    schematic = Path(schematic_path or Path(__file__).with_name("ppg_pcb_v08.kicad_sch")).resolve()
    source = schematic.read_text(encoding="utf-8")
    root_match = re.search(r'\(uuid\s+"([0-9a-fA-F-]{36})"\)', source.split("(lib_symbols", 1)[0])
    if root_match is None:
        raise ValueError(f"No root schematic UUID found: {schematic}")
    root_uuid = root_match.group(1)
    with tempfile.TemporaryDirectory(prefix="ppg-netlist-") as work:
        netlist = Path(work) / "current.xml"
        result = subprocess.run(
            [_kicad_cli(), "sch", "export", "netlist", "--format", "kicadxml",
             "--output", str(netlist), str(schematic)],
            check=False, capture_output=True, text=True,
        )
        if result.returncode:
            raise RuntimeError(f"KiCad netlist export failed ({result.returncode}):\n"
                               f"{result.stdout}{result.stderr}")
        xml = ET.parse(netlist).getroot()

    components = {}
    for comp in xml.findall("components/comp"):
        ref = comp.attrib["ref"]
        footprint = comp.findtext("footprint", "")
        if not footprint or ref.startswith("#"):
            continue
        if ":" not in footprint:
            raise ValueError(f"{ref}: schematic footprint needs a library nickname: {footprint}")
        fields = {f.attrib["name"]: f.text or "" for f in comp.findall("fields/field")}
        sheet = comp.find("sheetpath")
        sheet_path = sheet.get("tstamps", "/") if sheet is not None else "/"
        path_parts = [p for p in sheet_path.split("/") if p]
        if not path_parts or path_parts[0] != root_uuid:
            path_parts.insert(0, root_uuid)
        component_uuid = comp.findtext("tstamps", "").split()
        if len(component_uuid) != 1:
            raise ValueError(f"{ref}: expected one component UUID, got {component_uuid}")
        path_parts.append(component_uuid[0])
        components[ref] = {
            "footprint": footprint,
            "value": comp.findtext("value", ""),
            "path": "/" + "/".join(path_parts),
            "fields": {
                "MPN": fields.get("MPN", ""),
                "Manufacturer": fields.get("Manufacturer", ""),
                "Datasheet": fields.get("Datasheet", comp.findtext("datasheet", "")),
                "Description": fields.get("Description", comp.findtext("description", "")),
            },
        }

    pad_nets = {}
    names = set()
    for net in xml.findall("nets/net"):
        name = net.attrib["name"]
        names.add(name)
        for node in net.findall("node"):
            key = (node.attrib["ref"], node.attrib["pin"])
            if key in pad_nets and pad_nets[key] != name:
                raise ValueError(f"Schematic pin belongs to two nets: {key}")
            pad_nets[key] = name
    return {"components": components, "pad_nets": pad_nets, "net_names": names}


def validate_placement(board, expected_refs):
    """Enforce complete placement and the optical-side-only PPG constraint."""
    footprints = list(board.GetFootprints())
    refs = [fp.GetReference() for fp in footprints]
    expected = set(expected_refs)
    if len(refs) != len(set(refs)) or set(refs) != expected:
        raise ValueError(f"PCB reference mismatch: missing={sorted(expected - set(refs))}, "
                         f"extra={sorted(set(refs) - expected)}, duplicates={len(refs) - len(set(refs))}")
    top_refs = {fp.GetReference() for fp in footprints if fp.GetLayer() == pcbnew.F_Cu}
    if top_refs != {"U1"}:
        raise ValueError(f"Only U1 may be on the top side; found {sorted(top_refs)}")
    invalid = [fp.GetReference() for fp in footprints
               if fp.GetLayer() not in (pcbnew.F_Cu, pcbnew.B_Cu)]
    if invalid:
        raise ValueError(f"Footprints must be on an outer copper layer: {invalid}")


def sync_schematic_metadata(board, schematic_path=None, expected_refs=None, *, require_complete=True):
    """Update metadata and nets in memory; leave saving and validation to caller.

    ``require_complete=False`` is for reviewing a partial migration only.  Normal
    board generation/import requires all schematic footprints to be present.
    """
    metadata = load_schematic_metadata(schematic_path)
    components = metadata["components"]
    footprints = list(board.GetFootprints())
    refs = [fp.GetReference() for fp in footprints]
    if len(refs) != len(set(refs)):
        raise ValueError("PCB contains duplicate references")
    extra = set(refs) - set(components)
    missing = set(components) - set(refs)
    if extra or (require_complete and missing):
        raise ValueError(f"PCB/schematic component mismatch: missing={sorted(missing)}, extra={sorted(extra)}")
    if expected_refs is not None:
        if set(expected_refs) != set(components):
            raise ValueError("Design data component references do not match the current schematic")
        validate_placement(board, expected_refs)

    names = metadata["net_names"]
    existing = {net.GetNetname(): net for net in board.GetNetInfo().NetsByNetcode().values()}
    # Legacy generated boards omit the slash on local nets. Rename the existing
    # NETINFO_ITEM so tracks, vias and zones keep their connection to that net.
    for name, net in list(existing.items()):
        canonical = "/" + name
        if name and name not in names and canonical in names:
            if canonical in existing:
                for item in list(board.GetTracks()) + list(board.Zones()):
                    if item.GetNetCode() == net.GetNetCode():
                        item.SetNet(existing[canonical])
            else:
                net.SetNetname(canonical)
                existing[canonical] = net
    nets = {net.GetNetname(): net for net in board.GetNetInfo().NetsByNetcode().values()}
    for name in sorted(names):
        if name not in nets:
            net = pcbnew.NETINFO_ITEM(board, name)
            board.Add(net)
            nets[name] = net

    for fp in footprints:
        ref = fp.GetReference()
        comp = components[ref]
        library, item = comp["footprint"].split(":", 1)
        fp.SetFPID(pcbnew.LIB_ID(library, item))
        fp.SetValue(comp["value"])
        fp.SetPath(pcbnew.KIID_PATH(comp["path"]))
        for key, value in comp["fields"].items():
            fp.SetField(key, value)
            field = fp.GetField(key)
            if field is not None:
                field.SetVisible(False)
        for pad in fp.Pads():
            name = metadata["pad_nets"].get((ref, pad.GetNumber()))
            if name is not None:
                pad.SetNet(nets[name])
            elif pad.GetNumber():
                raise ValueError(f"No schematic net for {ref} pad {pad.GetNumber()}")
    return {"components": len(footprints), "nets": len(names), "missing_refs": sorted(missing)}
