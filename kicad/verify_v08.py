"""Fail-closed verification of design, board and freshly exported schematic XML.

Run with KiCad Python from any directory. --netlist accepts an existing XML
export; by default adjacent kicad-cli exports a fresh one. DRC/ERC and physical
hardware validation are separate checks, not implied by this report's PASS.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

import pcbnew
import design_v08 as D

HERE = Path(__file__).resolve().parent


def ref_key(ref):
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", ref)]


def expected_fpid(component):
    library = "SleepBud" if component["lib"] == "custom" else component["lib"]
    return library + ":" + component["fp"]


def actual_fpid(footprint):
    fid = footprint.GetFPID()
    return str(fid.GetLibNickname()) + ":" + str(fid.GetLibItemName())


def copper_pad(pad):
    return any(pad.IsOnLayer(layer) for layer in pcbnew.LSET.AllCuMask().Seq())


def is_copper_feature(component):
    return component["lib"] == "custom" and component["fp"].startswith("CablePad_D")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def point(v):
    return (pcbnew.ToMM(v.x), pcbnew.ToMM(v.y))


def courtyard_polygons(footprint):
    layer = pcbnew.B_CrtYd if footprint.IsFlipped() else pcbnew.F_CrtYd
    courtyard = footprint.GetCourtyard(layer)
    return [[point(courtyard.Outline(i).CPoint(j))
             for j in range(courtyard.Outline(i).PointCount())]
            for i in range(courtyard.OutlineCount())]


def segments(poly):
    return zip(poly, poly[1:] + poly[:1])


def point_segment_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    denominator = dx * dx + dy * dy
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / denominator)) if denominator else 0
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def intersects(a, b, c, d):
    if any(point_segment_distance(p, x, y) < 1e-9 for p, x, y in
           [(a, c, d), (b, c, d), (c, a, b), (d, a, b)]):
        return True
    return cross(a, b, c) * cross(a, b, d) < 0 and cross(c, d, a) * cross(c, d, b) < 0


def inside(p, poly):
    result = False
    for a, b in segments(poly):
        if (a[1] > p[1]) != (b[1] > p[1]):
            if p[0] < a[0] + (p[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
                result = not result
    return result


def polygon_distance(first, second):
    if inside(first[0], second) or inside(second[0], first):
        return 0.0
    if any(intersects(a, b, c, d) for a, b in segments(first) for c, d in segments(second)):
        return 0.0
    return min([point_segment_distance(p, a, b) for p in first for a, b in segments(second)] +
               [point_segment_distance(p, a, b) for p in second for a, b in segments(first)])


def read_netlist(path):
    tree = ET.parse(path).getroot()
    components = defaultdict(list)
    for component in tree.findall("components/comp"):
        components[component.get("ref")].append(component)
    pins = defaultdict(list)
    for net in tree.findall("nets/net"):
        nodes = net.findall("node")
        for node in nodes:
            pins[(node.get("ref"), node.get("pin"))].append({
                "net": net.get("name", ""), "pintype": node.get("pintype", ""),
                "node_count": len(nodes)})
    return tree, components, pins


def verify(board_path, netlist_path, schematic_path):
    errors = []

    def check(condition, code, **detail):
        if not condition:
            errors.append(dict(code=code, **detail))

    board = pcbnew.LoadBoard(str(board_path))
    tree, xml_components, xml_pins = read_netlist(netlist_path)
    footprints = defaultdict(list)
    for fp in board.GetFootprints():
        footprints[fp.GetReference()].append(fp)
    wanted_refs = set(D.COMPONENTS)
    for source, actual in [("PCB", footprints), ("schematic_XML", xml_components)]:
        check(set(actual) == wanted_refs, "reference_set", source=source,
              missing=sorted(wanted_refs - set(actual), key=ref_key),
              extra=sorted(set(actual) - wanted_refs, key=ref_key))
        for ref, records in actual.items():
            check(len(records) == 1, "duplicate_reference", source=source, ref=ref, count=len(records))
    for ref, pin in xml_pins:
        check(ref in D.COMPONENTS and pin in D.COMPONENTS[ref]["pins"],
              "unexpected_schematic_net_node", ref=ref, pin=pin)

    logical_pads = noncopper_apertures = no_connects = 0
    no_connect_nets = set()
    positions = {}
    for ref in sorted(wanted_refs, key=ref_key):
        component = D.COMPONENTS[ref]
        want_pins = set(component["pins"])
        fp = footprints[ref][0] if len(footprints.get(ref, [])) == 1 else None
        xml = xml_components[ref][0] if len(xml_components.get(ref, [])) == 1 else None
        if xml is not None:
            check(xml.findtext("value") == component["value"], "schematic_value", ref=ref,
                  expected=component["value"], actual=xml.findtext("value"))
            check(xml.findtext("footprint") == expected_fpid(component), "schematic_footprint", ref=ref,
                  expected=expected_fpid(component), actual=xml.findtext("footprint"))
            xml_declared_pins = [p.get("num") for p in xml.findall("units/unit/pins/pin")]
            if not xml_declared_pins:
                libsource = xml.find("libsource")
                if libsource is not None:
                    part = next((p for p in tree.findall("libparts/libpart")
                                 if p.get("lib") == libsource.get("lib") and p.get("part") == libsource.get("part")), None)
                    if part is not None:
                        xml_declared_pins = [p.get("num") for p in part.findall("pins/pin")]
            check(set(xml_declared_pins) == want_pins, "schematic_pin_set", ref=ref,
                  expected=sorted(want_pins), actual=sorted(set(xml_declared_pins)))
            check(len(xml_declared_pins) == len(set(xml_declared_pins)), "duplicate_schematic_pin", ref=ref)
            for field in ("mpn", "datasheet"):
                if component.get(field):
                    actual = xml.findtext("datasheet") if field == "datasheet" else None
                    if not actual:
                        tag = "MPN" if field == "mpn" else "Datasheet"
                        actual = next((f.text or "" for f in xml.findall("fields/field") if f.get("name") == tag), "")
                    check(actual == component[field], "schematic_metadata", ref=ref,
                          field=field, expected=component[field], actual=actual)
        pads = defaultdict(list)
        if fp is not None:
            check(fp.GetValue() == component["value"], "PCB_value", ref=ref,
                  expected=component["value"], actual=fp.GetValue())
            check(actual_fpid(fp) == expected_fpid(component), "PCB_footprint", ref=ref,
                  expected=expected_fpid(component), actual=actual_fpid(fp))
            side = "B" if fp.IsFlipped() else "F"
            check(side == component["side"], "PCB_side", ref=ref, expected=component["side"], actual=side)
            positions[ref] = dict(x_mm=point(fp.GetPosition())[0], y_mm=point(fp.GetPosition())[1],
                                  rotation_deg=fp.GetOrientationDegrees(), side=side)
            for pad in fp.Pads():
                if pad.GetNumber():
                    pads[pad.GetNumber()].append(pad)
                    check(copper_pad(pad), "numbered_pad_without_copper", ref=ref, pin=pad.GetNumber())
                else:
                    noncopper_apertures += 1
                    check(not copper_pad(pad) and not pad.GetNetname(), "unnumbered_electrical_pad", ref=ref)
            logical_pads += len(pads)
            check(set(pads) == want_pins, "PCB_pin_set", ref=ref,
                  missing=sorted(want_pins - set(pads)), extra=sorted(set(pads) - want_pins))
            for pin, records in pads.items():
                check(len(records) == 1, "duplicate_numbered_pad", ref=ref, pin=pin, count=len(records))
            if xml is not None:
                uuids = (xml.findtext("tstamps") or "").split()
                actual_path = fp.GetPath().AsString()
                check(len(uuids) == 1 and actual_path.endswith("/" + uuids[0]),
                      "PCB_schematic_path", ref=ref, schematic_uuids=uuids, actual=actual_path)
        for pin, want_net in component["pins"].items():
            nodes = xml_pins.get((ref, pin), [])
            check(len(nodes) == 1, "schematic_pin_net_count", ref=ref, pin=pin, count=len(nodes))
            if len(nodes) != 1:
                continue
            node = nodes[0]
            xml_net = node["net"]
            if want_net is None:
                no_connects += 1
                no_connect_nets.add(xml_net)
                check(xml_net.startswith("unconnected-(") and node["node_count"] == 1
                      and "no_connect" in node["pintype"].split("+"),
                      "schematic_no_connect", ref=ref, pin=pin, actual=node)
            else:
                check(xml_net.removeprefix("/") == want_net and "no_connect" not in node["pintype"],
                      "schematic_net", ref=ref, pin=pin, expected=want_net, actual=xml_net)
            for pad in pads.get(pin, []):
                pcb_net = pad.GetNetname()
                check(pcb_net == xml_net, "PCB_schematic_net", ref=ref, pin=pin,
                      expected=xml_net, actual=pcb_net)
                if want_net is not None:
                    check(pcb_net.removeprefix("/") == want_net, "PCB_design_net", ref=ref, pin=pin,
                          expected=want_net, actual=pcb_net)

    for item in list(board.GetTracks()) + list(board.Zones()):
        check(item.GetNetname() not in no_connect_nets, "routed_no_connect",
              item_class=item.GetClass(), net=item.GetNetname())

    # Check the outline itself, not text or fab drawings that affect the bounding box.
    edges = [d for d in board.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
    check(len(edges) == 1 and edges[0].GetShape() == pcbnew.SHAPE_T_CIRCLE,
          "board_outline_shape", expected="one circle", edge_shape_count=len(edges))
    geometry = dict(copper_layers=board.GetCopperLayerCount(),
                    thickness_mm=pcbnew.ToMM(board.GetDesignSettings().GetBoardThickness()))
    check(geometry["copper_layers"] == D.LAYERS, "copper_layers", expected=D.LAYERS, actual=geometry["copper_layers"])
    check(abs(geometry["thickness_mm"] - D.THICKNESS) < 1e-6, "board_thickness",
          expected=D.THICKNESS, actual=geometry["thickness_mm"])
    if len(edges) == 1 and edges[0].GetShape() == pcbnew.SHAPE_T_CIRCLE:
        center, end = point(edges[0].GetCenter()), point(edges[0].GetEnd())
        radius = math.dist(center, end)
        geometry.update(center_mm=center, diameter_mm=2 * radius)
        check(math.hypot(*center) < 1e-6 and abs(radius - D.BOARD_R) < 1e-6,
              "board_outline_dimensions", expected_center=[0, 0], expected_diameter=2 * D.BOARD_R,
              actual_center=center, actual_diameter=2 * radius)
    sensor = footprints.get("U1", [])
    if len(sensor) == 1:
        fp = sensor[0]
        check(math.dist(point(fp.GetPosition()), D.COMPONENTS["U1"]["pos"]) < 1e-6,
              "sensor_position", expected=D.COMPONENTS["U1"]["pos"], actual=point(fp.GetPosition()))
        rotation_difference = (fp.GetOrientationDegrees() - (D.COMPONENTS["U1"].get("rot") or 0) + 180) % 360 - 180
        check(abs(rotation_difference) < 1e-6, "sensor_orientation",
              expected=D.COMPONENTS["U1"].get("rot"), actual=fp.GetOrientationDegrees())
        sensor_polygons = courtyard_polygons(fp)
        check(bool(sensor_polygons), "missing_sensor_courtyard", ref="U1")
        separation = {}
        for ref, group in footprints.items():
            if ref == "U1" or len(group) != 1 or group[0].IsFlipped():
                continue
            polygons = courtyard_polygons(group[0])
            check(bool(polygons), "missing_front_courtyard", ref=ref)
            if sensor_polygons and polygons:
                distance = min(polygon_distance(a, b) for a in sensor_polygons for b in polygons)
                separation[ref] = round(distance, 6)
                check(distance > 1e-6, "sensor_courtyard_intersection", ref=ref, separation_mm=distance)
        geometry["sensor_courtyard_separation_mm"] = separation
    routing = Counter("via" if t.GetClass() == "PCB_VIA" else board.GetLayerName(t.GetLayer()) for t in board.GetTracks())
    return dict(status="PASS" if not errors else "FAIL", checked_at=datetime.now(timezone.utc).isoformat(),
                files={"board": {"path": str(board_path), "sha256": sha256(board_path)},
                       "schematic": {"path": str(schematic_path), "sha256": sha256(schematic_path)},
                       "design": {"path": str(HERE / "design_v08.py"), "sha256": sha256(HERE / "design_v08.py")},
                       "schematic_XML_sha256": sha256(netlist_path)},
                counts=dict(design_references=len(D.COMPONENTS), PCB_references=len(footprints),
                            schematic_references=len(xml_components),
                            assembled_components=sum(not is_copper_feature(c) for c in D.COMPONENTS.values()),
                            copper_features=sum(is_copper_feature(c) for c in D.COMPONENTS.values()),
                            expected_numbered_pins=sum(len(c["pins"]) for c in D.COMPONENTS.values()),
                            PCB_numbered_pins=logical_pads, noncopper_apertures=noncopper_apertures,
                            explicit_no_connect_pins=no_connects),
                geometry=geometry, placements=positions, routing=dict(routing),
                scope="Identity, connectivity and stated geometry only; DRC/ERC, stackup and hardware validation are separate.",
                errors=errors)


def find_cli(override=None):
    if override:
        return str(Path(override).resolve())
    candidates = [Path(sys.executable).with_name("kicad-cli.exe"), Path(sys.executable).with_name("kicad-cli")]
    candidates += [Path(p) for p in [shutil.which("kicad-cli")] if p]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    raise FileNotFoundError("kicad-cli not found; run KiCad Python or supply --cli")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", type=Path, default=HERE / "ppg_pcb_v08.kicad_pcb")
    parser.add_argument("--schematic", type=Path, default=HERE / "ppg_pcb_v08.kicad_sch")
    parser.add_argument("--netlist", type=Path, help="Existing XML netlist; omitted = fresh export")
    parser.add_argument("--cli", help="kicad-cli executable override")
    parser.add_argument("--report", type=Path, default=HERE.parent / "docs" / "ppg_pcb_v08_verification.json")
    args = parser.parse_args(argv)
    try:
        if args.netlist:
            report = verify(args.board.resolve(), args.netlist.resolve(), args.schematic.resolve())
            report["netlist_source"] = "supplied XML (caller is responsible for freshness)"
        else:
            with tempfile.TemporaryDirectory(prefix="ppg-netcheck-") as directory:
                netlist = Path(directory) / "schematic.xml"
                command = [find_cli(args.cli), "sch", "export", "netlist", "--format", "kicadxml", "-o", str(netlist), str(args.schematic.resolve())]
                result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
                if result.returncode or not netlist.is_file():
                    raise RuntimeError("Schematic XML export failed: " + result.stdout + result.stderr)
                report = verify(args.board.resolve(), netlist, args.schematic.resolve())
                report["netlist_source"] = "fresh kicad-cli export"
    except Exception as exc:
        report = dict(status="FAIL", errors=[dict(code="verification_exception", detail=str(exc))])
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
