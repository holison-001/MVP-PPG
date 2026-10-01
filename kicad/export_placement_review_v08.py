"""Read a fixed KiCad PCB and bind its actual placement to preview source JSON.

Writes documentation JSON only. The board must match its independent audit.
Run with the rootless kicad-python wrapper; rendering is a separate command.
"""
import argparse
import gc
import hashlib
import json
import math
from pathlib import Path

import pcbnew as k
from shapely.affinity import rotate, translate
from shapely.geometry import Polygon, mapping, shape
from shapely.ops import unary_union
from board_coordinates_v08 import normalize_for_analysis

gc.disable()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def xy(vector):
    return [k.ToMM(vector.x), k.ToMM(vector.y)]


def pcb_polygon(polyset):
    polygons = []
    for i in range(polyset.OutlineCount()):
        outline = polyset.COutline(i)
        points = [xy(outline.CPoint(n)) for n in range(outline.PointCount())]
        holes = []
        for h in range(polyset.HoleCount(i)):
            hole = polyset.CHole(i, h)
            holes.append([xy(hole.CPoint(n)) for n in range(hole.PointCount())])
        if len(points) >= 3:
            polygons.append(Polygon(points, holes))
    return unary_union(polygons)


def radius(geometry):
    if geometry.is_empty:
        return 0.0
    if hasattr(geometry, 'geoms'):
        return max(radius(g) for g in geometry.geoms)
    points = geometry.exterior.coords if geometry.geom_type == 'Polygon' else geometry.coords
    return max(math.hypot(x, y) for x, y in points)


def serialize(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', required=True, type=Path)
    parser.add_argument('--geometry', required=True, type=Path)
    parser.add_argument('--independent-audit', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    board_hash = digest(args.board)
    audit_hash = digest(args.independent_audit)
    independent = json.loads(args.independent_audit.read_text())
    if independent['board_sha256'] != board_hash:
        raise ValueError('Board does not match the independently audited snapshot')
    if not independent.get('ok'):
        raise ValueError('Independent final PCB audit has not passed; do not publish as final placement')
    geometry_bytes = args.geometry.read_bytes()
    geometry_hash = hashlib.sha256(geometry_bytes).hexdigest()
    geometry = json.loads(geometry_bytes)
    mechanical = independent['mechanical']
    if mechanical['geometry_sha256'] != geometry_hash:
        raise ValueError('Independent audit used a different frozen geometry')
    if mechanical['copper_shape_changes']:
        raise ValueError('Frozen geometry no longer represents the actual footprint copper')
    board = k.LoadBoard(str(args.board))
    sheet_center = normalize_for_analysis(board)
    footprints = list(board.GetFootprints())
    if len({f.GetReference() for f in footprints}) != len(footprints):
        raise ValueError('Duplicate footprint reference')
    placement = {}
    for fp in footprints:
        side = 'F' if fp.GetLayer() == k.F_Cu else 'B' if fp.GetLayer() == k.B_Cu else None
        if side is None:
            raise ValueError(f'Unsupported footprint side: {fp.GetReference()}')
        angle = fp.GetOrientationDegrees() % 360
        if abs(angle - round(angle)) < 1e-8:
            angle = int(round(angle)) % 360
        placement[fp.GetReference()] = {
            'pos': xy(fp.GetPosition()), 'rot': angle, 'side': side,
            'footprint': str(fp.GetFPID().GetLibItemName()),
        }
    placement = dict(sorted(placement.items()))
    top_refs = [r for r, p in placement.items() if p['side'] == 'F']
    bottom_refs = [r for r, p in placement.items() if p['side'] == 'B']
    if top_refs != ['U1'] or placement['U1']['pos'] != [0.0, 0.0] or placement['U1']['rot'] != 0:
        raise ValueError('The top must contain only fixed U1 at the PCB center')
    if set(bottom_refs) != set(geometry['footprints']):
        raise ValueError('Actual bottom references do not match the frozen geometry')
    if {'D2', 'D3', 'D4', 'D5'} & set(placement):
        raise ValueError('Unexpected removed RS-422 TVS reference found')

    parts, radii, copper_changes = {}, {}, []
    geometry_modified = False
    for fp in footprints:
        ref = fp.GetReference()
        if ref == 'U1':
            continue
        p = placement[ref]
        frozen = geometry['footprints'][ref]
        if frozen['footprint'] != p['footprint']:
            raise ValueError(f'Footprint identity changed for {ref}')
        orientation = next((o for o in frozen['orientations'] if o['rot'] == p['rot']), None)
        if orientation is None:
            zero = next(o for o in frozen['orientations'] if o['rot'] == 0)
            orientation = {'rot': p['rot'], **{
                key: mapping(rotate(shape(zero[key]), -p['rot'], origin=(0, 0)))
                for key in ['courtyard', 'copper', 'body']}}
            frozen['orientations'].append(orientation)
            geometry_modified = True
        part = {key: translate(shape(orientation[key]), *p['pos'])
                for key in ['courtyard', 'copper', 'body']}
        actual_copper = unary_union([pcb_polygon(pad.GetEffectivePolygon(k.B_Cu))
                                     for pad in fp.Pads() if pad.IsOnLayer(k.B_Cu)])
        difference = part['copper'].symmetric_difference(actual_copper).area
        if difference > 1e-5:
            copper_changes.append({'ref': ref, 'area_mm2': difference})
        parts[ref] = part
        radii[ref] = {key: radius(g) for key, g in part.items()}
    if copper_changes:
        raise ValueError(f'Actual PCB copper differs from preview geometry: {copper_changes}')
    if geometry_modified:
        geometry_bytes = serialize(geometry)
        geometry_hash = hashlib.sha256(geometry_bytes).hexdigest()

    court_overlaps, body_overlaps, gaps, edge_violations = [], [], [], []
    minimum_pad_gap, minimum_court_gap = float('inf'), float('inf')
    board_radius = geometry['board_radius_mm']
    copper_radius = geometry['copper_radius_mm']
    court_radius = geometry['max_courtyard_radius_mm']
    for i, ref in enumerate(bottom_refs):
        for other in bottom_refs[:i]:
            for key, records in [('courtyard', court_overlaps), ('body', body_overlaps)]:
                area = parts[ref][key].intersection(parts[other][key]).area
                if area > 1e-8:
                    records.append({'refs': [ref, other], 'area_mm2': area})
            gap = parts[ref]['copper'].distance(parts[other]['copper'])
            minimum_pad_gap = min(minimum_pad_gap, gap)
            minimum_court_gap = min(minimum_court_gap, parts[ref]['courtyard'].distance(parts[other]['courtyard']))
            if gap < .15 - 1e-6:
                gaps.append({'refs': [ref, other], 'clearance_mm': gap})
        rr = radii[ref]
        if rr['body'] > board_radius + 1e-6 or rr['copper'] > copper_radius + 1e-6 or rr['courtyard'] > court_radius + 1e-6:
            edge_violations.append({'ref': ref, **rr})
    feasible = not (court_overlaps or body_overlaps or gaps or edge_violations)
    if not feasible:
        raise ValueError('Final board placement violates the preview geometry constraints; no sources written')
    source_board = {'path': str(args.board.resolve()), 'sha256': board_hash}
    candidate = {'source_board': source_board,
                 'board_center_on_sheet_mm': sheet_center,
                 'status': 'Placement extracted read-only from an independently audited PCB; traces omitted',
                 'placement': placement}
    candidate_bytes = serialize(candidate)
    report = {
        'feasible': feasible,
        'status': 'Actual PCB placement geometry only; rendered preview omits tracks and vias',
        'source_board': source_board,
        'source_independent_audit': {'path': str(args.independent_audit.resolve()), 'sha256': audit_hash},
        'independent_pcb_audit_passed': independent['ok'],
        'candidate_sha256': hashlib.sha256(candidate_bytes).hexdigest(),
        'geometry_sha256': geometry_hash,
        'total_components': len(placement), 'total_count': len(placement),
        'top_refs': top_refs, 'bottom_count': len(bottom_refs),
        'removed_refs': ['D2', 'D4'],
        'courtyard_overlap_pairs': court_overlaps, 'courtyard_overlaps': court_overlaps,
        'body_overlaps': body_overlaps, 'copper_clearance_violations': gaps,
        'edge_violations': edge_violations,
        'minimum_copper_edge_clearance_mm': board_radius - max(rr['copper'] for rr in radii.values()),
        'minimum_pad_copper_gap_mm': minimum_pad_gap,
        'minimum_courtyard_gap_mm': minimum_court_gap,
        'maximum_body_radius_mm': max(rr['body'] for rr in radii.values()),
        'maximum_courtyard_radius_mm': max(rr['courtyard'] for rr in radii.values()),
        'bottom_courtyard_sum_mm2': sum(part['courtyard'].area for part in parts.values()),
        'per_ref_radii_mm': radii,
        'constraints': {'body_radius_mm': board_radius, 'copper_radius_mm': copper_radius,
                        'courtyard_radius_mm': court_radius, 'pad_to_pad_clearance_mm': .15,
                        'courtyard_overlap_mm2': 0},
        'coordinates': {'origin': 'PCB center', 'board_center_on_sheet_mm': sheet_center,
                        'units': 'mm', 'y_positive': 'down',
                        'rotation': 'Actual KiCad orientation; board-side flip already represented in geometry'},
        'notes': ['The original PCB is not modified.',
                  'Placement uses saved PCB coordinates relative to its center on the drawing sheet.',
                  'The PCB hash and independent audit hash bind this placement to a fixed verified source.',
                  'These placement-only metrics omit copper tracks, vias and zones; see the complete PCB audit.'],
    }
    if digest(args.board) != board_hash or digest(args.independent_audit) != audit_hash:
        raise ValueError('The source changed during extraction; no sources written')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = {'placement_candidate.json': candidate_bytes, 'geometry.json': geometry_bytes,
              'placement_audit.json': serialize(report)}
    for filename, content in output.items():
        (args.output_dir / filename).write_bytes(content)
    summary = {key: report[key] for key in ['feasible', 'source_board', 'total_components', 'top_refs',
                                            'bottom_count', 'minimum_copper_edge_clearance_mm']}
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
