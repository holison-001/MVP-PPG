"""Four 3.0 mm NPTH holes with 11 mm clearance, preserving the reviewed circuit."""
from pathlib import Path
import math
import pcbnew as k

HERE = Path(__file__).resolve().parent
BOUNDS = (88.0, 98.5, 140.0, 123.5)
HOLES = {'H1': (94.5, 105.0), 'H2': (133.5, 105.0),
         'H3': (94.5, 117.0), 'H4': (133.5, 117.0)}
HEAD_CLEARANCE_DIAMETER = 11.0
LAYERS = [k.F_Cu, k.In1_Cu, k.In2_Cu, k.In3_Cu, k.In4_Cu, k.B_Cu]
M, V = k.FromMM, k.VECTOR2I_MM


def apply_mounting_layout(board, metadata, prior_ground_vias=None):
    """Operate on a saved board or freshly built candidate; preserve all routing."""
    retained = []  # retain removed SWIG items until this operation completes
    ground = board.FindNet('/GND')
    assert ground is not None
    # Relocate only the previous mounting-extension stitching, identified exactly.
    for position in prior_ground_vias or []:
        matches = [item for item in board.GetTracks()
                   if isinstance(item, k.PCB_VIA) and item.GetPosition() == V(*position)]
        assert len(matches) == 1, ('Expected one previous mounting via', position)
        item = matches[0]
        assert item.GetNetname() == '/GND' and item.GetDrillValue() == M(.25) and item.GetWidth(k.F_Cu) == M(.5)
        retained.append(item); board.Remove(item)
    for item in list(board.GetDrawings()):
        if item.GetLayer() == k.Edge_Cuts:
            retained.append(item); board.Remove(item)
        elif item.GetClass() == 'PCB_TEXT' and item.GetText() in ('28 x 22 mm | 6L / 0.8 mm', '42 x 22 mm | 6L / 0.8 mm'):
            item.SetText('52 x 25 mm | 6L / 0.8 mm')
    x0, y0, x1, y1 = BOUNDS
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for a, b in zip(corners, corners[1:] + corners[:1]):
        edge = k.PCB_SHAPE(board); edge.SetShape(k.SHAPE_T_SEGMENT)
        edge.SetStart(V(*a)); edge.SetEnd(V(*b))
        edge.SetLayer(k.Edge_Cuts); edge.SetWidth(M(.05)); board.Add(edge)
    for zone in list(board.Zones()):
        if (not zone.GetIsRuleArea() and zone.GetNetname() == '/GND') or zone.GetZoneName().startswith(tuple(ref + ' screw head clearance' for ref in HOLES)):
            retained.append(zone); board.Remove(zone)
    for layer in LAYERS:
        zone = k.ZONE(board); zone.SetLayer(layer); zone.SetNet(ground)
        zone.SetLocalClearance(M(.15)); zone.SetMinThickness(M(.15))
        zone.SetPadConnection(k.ZONE_CONNECTION_FULL)
        zone.SetIslandRemovalMode(k.ISLAND_REMOVAL_MODE_ALWAYS)
        for point in corners: zone.AppendCorner(V(*point), -1)
        board.Add(zone)
    existing = {fp.GetReference(): fp for fp in board.GetFootprints()}
    for ref, position in HOLES.items():
        component = metadata['components'][ref]
        library_fp = k.FootprintLoad(str(HERE / 'Adapter.pretty'), 'MountingHole_3mm_Clearance11mm')
        assert library_fp is not None
        if ref in existing:
            fp = existing[ref]
            # Preserve this footprint and NPTH pad UUID while resizing its circles.
            for graphic in fp.GraphicalItems():
                if graphic.GetClass() == 'PCB_SHAPE' and graphic.GetShape() == k.SHAPE_T_CIRCLE:
                    delta = graphic.GetEnd() - graphic.GetCenter()
                    dx, dy = k.ToMM(delta.x), k.ToMM(delta.y)
                    scale = HEAD_CLEARANCE_DIAMETER / 2 / math.hypot(dx, dy)
                    graphic.SetEnd(graphic.GetCenter() + V(dx * scale, dy * scale))
            fp.SetLibDescription(library_fp.GetLibDescription())
            fp.SetKeywords(library_fp.GetKeywords())
        else:
            fp = library_fp; board.Add(fp)
        fp.SetFPID(k.LIB_ID('Adapter', 'MountingHole_3mm_Clearance11mm'))
        fp.SetReference(ref); fp.SetValue(component['value'])
        fp.SetPosition(V(*position))
        if fp.GetLayer() != k.B_Cu: fp.SetLayerAndFlip(k.B_Cu)
        fp.SetPath(k.KIID_PATH(component['path']))
        for name, value in component['fields'].items():
            fp.SetField(name, value); fp.GetField(name).SetVisible(False)
        fp.Reference().SetLayer(k.B_Fab); fp.Reference().SetTextSize(V(.7, .7))
        fp.Reference().SetTextThickness(M(.1))
        fp.Value().SetVisible(False)
        # Reference text sits within the clear circle, away from drill and wire pads.
        ref_position = (position[0], position[1] + (-3.5 if ref in ('H1', 'H2') else 3.5))
        fp.Reference().SetPosition(V(*ref_position))
        labels = [item for item in board.GetDrawings() if item.GetClass() == 'PCB_TEXT' and item.GetText() == ref and item.GetLayer() == k.F_SilkS]
        assert len(labels) <= 1
        label = labels[0] if labels else k.PCB_TEXT(board)
        label.SetText(ref); label.SetLayer(k.F_SilkS)
        label.SetPosition(V(*ref_position)); label.SetTextSize(V(.8, .8))
        label.SetTextThickness(M(.12))
        if not labels: board.Add(label)
        # Circumscribed polygon ensures at least the stated circular clearance.
        area = k.ZONE(board); area.SetIsRuleArea(True)
        area.SetZoneName(f'{ref} screw head clearance D11')
        layer_set = k.LSET()
        for layer in LAYERS: layer_set.AddLayer(layer)
        area.SetLayerSet(layer_set)
        area.SetDoNotAllowTracks(True); area.SetDoNotAllowVias(True)
        area.SetDoNotAllowZoneFills(True); area.SetDoNotAllowPads(False)
        area.SetDoNotAllowFootprints(False)  # hole itself is within this area
        segments = 96
        radius = HEAD_CLEARANCE_DIAMETER / 2 / math.cos(math.pi / segments)
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            area.AppendCorner(V(position[0] + radius * math.cos(angle),
                                position[1] + radius * math.sin(angle)), -1)
        board.Add(area)
    # Extra ground stitching follows the enlarged perimeter; original vias remain.
    seeds = [(x, y) for x in (88.75, 139.25) for y in (102, 106, 110, 114, 118, 122)]
    seeds += [(x, y) for x in (90, 94.5, 99, 103.5, 108, 112.5, 117, 121.5, 126, 130.5, 135, 138) for y in (99.15, 122.85)]
    for x, y in seeds:
        assert all(math.dist((x, y), hole) >= HEAD_CLEARANCE_DIAMETER / 2 + .25 for hole in HOLES.values())
        via = k.PCB_VIA(board); via.SetPosition(V(x, y)); via.SetViaType(k.VIATYPE_THROUGH)
        via.SetLayerPair(k.F_Cu, k.B_Cu); via.SetWidth(M(.5)); via.SetDrill(M(.25))
        via.SetNet(ground); board.Add(via)
    board.BuildConnectivity()
    k.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    return {'outline_mm': list(BOUNDS), 'size_mm': [52, 25],
            'holes': {ref: {'center_mm': list(p), 'drill_mm': 3.0, 'plated': False}
                      for ref, p in HOLES.items()},
            'center_pitch_mm': [39, 12], 'center_to_edge_mm': 6.5,
            'head_clearance_diameter_mm': HEAD_CLEARANCE_DIAMETER,
            'added_ground_vias_mm': [list(p) for p in seeds]}
