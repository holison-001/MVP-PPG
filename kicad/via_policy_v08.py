"""Reviewed trace/via dimensions; electrical connectivity is checked by PCB DRC."""
from collections import Counter

import pcbnew as k
import design_v08 as D

MIN_TRACK_WIDTH_MM = D.RULES['track_min']
VIA_DIAMETER_MM = D.RULES['via_dia']
SIGNAL_GROUND_DRILL_MM = D.RULES['via_drill']
POWER_REFERENCE_DRILL_MM = D.RULES['power_via_drill']
POWER_REFERENCE_NETS = D.POWER_REFERENCE_NETS


def via_group(net_name):
    name = net_name.rsplit('/', 1)[-1]
    if name == 'GND':
        return 'ground'
    return 'power_reference' if name in POWER_REFERENCE_NETS else 'signal'


def via_drill_mm(net_name):
    return (POWER_REFERENCE_DRILL_MM if via_group(net_name) == 'power_reference'
            else SIGNAL_GROUND_DRILL_MM)


def check_vias_and_widths(board):
    errors = []
    groups = Counter()
    widths = Counter()
    sizes = Counter()
    for item in board.GetTracks():
        uid = item.m_Uuid.AsString()
        if item.GetClass() != 'PCB_VIA':
            width = k.ToMM(item.GetWidth())
            widths[round(width, 6)] += 1
            if width < MIN_TRACK_WIDTH_MM - 1e-6:
                errors.append(f'{uid}: {item.GetNetname()} trace width {width:g} mm is below 0.15 mm')
            continue
        net = item.GetNetname()
        group = via_group(net)
        groups[group] += 1
        diameter = k.ToMM(item.GetWidth(k.F_Cu))
        drill = k.ToMM(item.GetDrillValue())
        sizes[(group, round(diameter, 6), round(drill, 6))] += 1
        expected_drill = via_drill_mm(net)
        if abs(diameter - VIA_DIAMETER_MM) > 1e-6 or abs(drill - expected_drill) > 1e-6:
            errors.append(f'{uid}: {net} via is {diameter:g}/{drill:g} mm, '
                          f'expected {VIA_DIAMETER_MM:g}/{expected_drill:g} mm')
        if item.GetViaType() != k.VIATYPE_THROUGH:
            errors.append(f'{uid}: only through vias are permitted')
    return {
        'ok': not errors,
        'minimum_track_width_mm': min(widths) if widths else None,
        'track_width_counts': dict(sorted(widths.items())),
        'via_groups': dict(groups),
        'via_sizes': [{'group': group, 'diameter_mm': diameter, 'drill_mm': drill, 'count': count}
                      for (group, diameter, drill), count in sorted(sizes.items())],
        'power_reference_nets': sorted(POWER_REFERENCE_NETS),
        'errors': errors,
    }
