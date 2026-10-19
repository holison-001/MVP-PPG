"""Full-board GND pours on all six layers; continuous rims on L1-L5."""
import pcbnew as k
from ground_rim_v08 import check_ground_rim

GROUND_LAYERS = (k.In1_Cu, k.In4_Cu)
GND_POUR_LAYERS = (k.F_Cu, k.In1_Cu, k.In2_Cu, k.In3_Cu, k.In4_Cu, k.B_Cu)
SIGNAL_LAYERS = (k.In2_Cu, k.In3_Cu, k.In4_Cu)
POWER_LAYER = k.In3_Cu
POWER_MIN_WIDTH_MM = 0.30


def check_layers(board):
    errors = []
    zones = [(z.GetLayer(), z.GetNetname()) for z in board.Zones()]
    expected_zones = {(layer, 'GND') for layer in GND_POUR_LAYERS}
    if len(zones) != 6 or set(zones) != expected_zones:
        errors.append('Expected one full-board GND zone on each of the six copper layers')
    pour_details = []
    for zone in board.Zones():
        outline = zone.Outline()
        holes = sum(outline.HoleCount(i) for i in range(outline.OutlineCount()))
        filled = zone.GetFilledPolysList(zone.GetLayer())
        area_mm2 = filled.Area() / 1e12
        if outline.OutlineCount() != 1 or holes:
            errors.append(f'{board.GetLayerName(zone.GetLayer())}: GND outline must have no intentional cutout')
        if area_mm2 <= 0:
            errors.append(f'{board.GetLayerName(zone.GetLayer())}: missing saved GND fill')
        pour_details.append({'layer': board.GetLayerName(zone.GetLayer()),
                             'net': zone.GetNetname(), 'outline_holes': holes,
                             'filled_area_mm2': area_mm2})
    inner = [t for t in board.GetTracks() if t.GetClass() != 'PCB_VIA'
             and t.GetLayer() not in (k.F_Cu, k.B_Cu)]
    if any(t.GetLayer() not in SIGNAL_LAYERS for t in inner):
        errors.append('L2/In1.Cu must have no tracks/arcs; L5 permits reviewed short detours')
    power = [t for t in inner if t.GetLayer() == POWER_LAYER and t.GetNetname() == '3V3']
    if not power:
        errors.append('Missing broad 3V3 distribution traces on In3.Cu (L4)')
    elif min(k.ToMM(t.GetWidth()) for t in power) < POWER_MIN_WIDTH_MM - 1e-6:
        errors.append('In3.Cu (L4) 3V3 distribution must be at least 0.30 mm wide')
    rim = check_ground_rim(board)
    errors.extend(rim['errors'])
    return {
        'ok': not errors,
        'inner_layer_track_count': len(inner),
        'ground_plane_layers': [board.GetLayerName(layer) for layer in GROUND_LAYERS],
        'gnd_pour_layers': [board.GetLayerName(layer) for layer in GND_POUR_LAYERS],
        'gnd_pours': pour_details,
        'ground_plane_track_count': sum(t.GetLayer() in GROUND_LAYERS for t in inner),
        'l2_track_count': sum(t.GetLayer() == k.In1_Cu for t in inner),
        'l5_track_count': sum(t.GetLayer() == k.In4_Cu for t in inner),
        'l5_trace_length_mm': sum(k.ToMM(t.GetLength()) for t in inner if t.GetLayer() == k.In4_Cu),
        'signal_layer_tracks': {board.GetLayerName(layer): sum(t.GetLayer() == layer for t in inner)
                                for layer in SIGNAL_LAYERS},
        'power_layer': board.GetLayerName(POWER_LAYER),
        'power_3V3_track_count': len(power),
        'power_3V3_widths_mm': sorted({k.ToMM(t.GetWidth()) for t in power}),
        'ground_rim': rim,
        'errors': errors,
    }
