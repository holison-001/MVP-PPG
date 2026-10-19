"""Check saved L1-L5 GND fill against an inset circular rim, without rewriting it.

This uses KiCad polygon subtraction rather than angular samples. The 5 um inner
guard and 20 um outer guard avoid treating polygon tessellation as a copper gap.
It verifies a 0.225 mm interior band (0.325 mm on F.Cu), not a claimed fabrication
width. Ground connectivity and clearance still require the separate PCB DRC.
"""
import math
import pcbnew as k
import design_v08 as D
from board_coordinates_v08 import BOARD_CENTER_MM


def _band(inner, outer):
    shape = k.SHAPE_POLY_SET()
    shape.NewOutline()
    cx, cy = BOARD_CENTER_MM
    for index in range(1440):
        angle = 2 * math.pi * index / 1440
        shape.Append(k.FromMM(cx + outer * math.cos(angle)),
                     k.FromMM(cy + outer * math.sin(angle)), 0, -1)
    hole = shape.NewHole(0)
    for index in range(1440):
        angle = -2 * math.pi * index / 1440
        shape.Append(k.FromMM(cx + inner * math.cos(angle)),
                     k.FromMM(cy + inner * math.sin(angle)), 0, hole)
    return shape


def check_ground_rim(board):
    reports = {}
    errors = []
    inner = D.GND_RIM_INNER_RADIUS_MM + 0.005
    for layer in (k.F_Cu, k.In1_Cu, k.In2_Cu, k.In3_Cu, k.In4_Cu):
        name = board.GetLayerName(layer)
        outer = D.BOARD_R - (0.22 if layer == k.F_Cu else 0.32)
        expected = _band(inner, outer)
        fill = k.SHAPE_POLY_SET()
        for zone in board.Zones():
            if zone.GetNetname() == 'GND' and zone.IsOnLayer(layer):
                fill.BooleanAdd(zone.GetFilledPolysList(layer))
        expected.BooleanSubtract(fill)
        missing = max(0.0, expected.Area() / 1e12)
        reports[name] = {'inner_radius_mm': inner, 'outer_radius_mm': outer,
                         'checked_width_mm': outer - inner,
                         'missing_saved_fill_mm2': missing}
        if not board.GetEnabledLayers().Contains(layer) or missing > 1e-6:
            errors.append(f'{name}: incomplete peripheral GND fill ({missing:.6f} mm^2 missing)')
    return {'ok': not errors, 'method': 'KiCad polygon subtraction, 1440-sided inset annulus',
            'layers': reports, 'errors': errors}
