"""Approved stack: F/In1 ground pours and routing; In2 broad 3V3 and signals."""
import pcbnew as k

IN2_POWER_MIN_WIDTH_MM = 0.30


def check_layers(board):
    errors = []
    zones = [(z.GetLayer(), z.GetNetname()) for z in board.Zones()]
    if len(zones) != 2 or set(zones) != {(k.F_Cu, 'GND'), (k.In1_Cu, 'GND')}:
        errors.append('Expected F.Cu and In1.Cu GND zones only; In2.Cu must not have a pour')
    inner = [t for t in board.GetTracks() if t.GetClass() != 'PCB_VIA'
             and t.GetLayer() not in (k.F_Cu, k.B_Cu)]
    if any(t.GetLayer() not in (k.In1_Cu, k.In2_Cu) for t in inner):
        errors.append('Inner routing is allowed on In1.Cu and In2.Cu only')
    power = [t for t in inner if t.GetLayer() == k.In2_Cu and t.GetNetname() == '3V3']
    if not power:
        errors.append('Missing broad 3V3 distribution traces on In2.Cu')
    elif min(k.ToMM(t.GetWidth()) for t in power) < IN2_POWER_MIN_WIDTH_MM - 1e-6:
        errors.append('In2.Cu 3V3 distribution must be at least 0.30 mm wide')
    return {
        'ok': not errors,
        'inner_layer_track_count': len(inner),
        'in1_track_count': sum(t.GetLayer() == k.In1_Cu for t in inner),
        'in1_routed_nets': sorted({t.GetNetname() for t in inner if t.GetLayer() == k.In1_Cu}),
        'in2_3V3_track_count': len(power),
        'in2_3V3_widths_mm': sorted({k.ToMM(t.GetWidth()) for t in power}),
        'errors': errors,
    }
