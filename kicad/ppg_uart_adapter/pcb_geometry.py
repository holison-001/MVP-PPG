"""Exact copper geometry used to keep stitching vias clear of signal copper.

Requires KiCad's pcbnew and Shapely. The local development dependency fallback
is optional; an ordinary Shapely installation is sufficient on other machines.
"""
from pathlib import Path
import sys
import pcbnew as k

try:
    import shapely
except ModuleNotFoundError:
    local = Path(__file__).resolve().parents[2] / '.git/6layer_impl_20261005/pydeps'
    if not local.is_dir():
        raise RuntimeError('Install Shapely for the Python interpreter bundled with KiCad.')
    sys.path.insert(0, str(local))
    import shapely

from shapely import make_valid
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union


def polygons(geometry):
    if geometry.is_empty:
        return []
    if geometry.geom_type == 'Polygon':
        return [geometry]
    return [p for g in getattr(geometry, 'geoms', []) for p in polygons(g)]


def polyset_geometry(polyset, diagnostics):
    result = []
    xy = lambda v: (k.ToMM(v.x), k.ToMM(v.y))
    for i in range(polyset.OutlineCount()):
        outline = polyset.COutline(i)
        exterior = [xy(outline.CPoint(j)) for j in range(outline.PointCount())]
        holes = []
        for h in range(polyset.HoleCount(i)):
            hole = polyset.CHole(i, h)
            holes.append([xy(hole.CPoint(j)) for j in range(hole.PointCount())])
        if len(exterior) < 3:
            continue
        g = Polygon(exterior, holes)
        if not g.is_valid:
            diagnostics['invalid_input_contours_repaired'] += 1
            g = make_valid(g)
        result.extend(polygons(g))
    return unary_union(result)


def item_geometry(item, layer, diagnostics, error_mm):
    if item.GetClass() == 'PAD':
        return polyset_geometry(item.GetEffectivePolygon(layer), diagnostics)
    polyset = k.SHAPE_POLY_SET()
    item.TransformShapeToPolygon(polyset, layer, 0, k.FromMM(error_mm), k.ERROR_INSIDE)
    g = polyset_geometry(polyset, diagnostics)
    if item.GetClass() == 'PCB_VIA':
        p = item.GetPosition()
        hole = Point(k.ToMM(p.x), k.ToMM(p.y)).buffer(
            k.ToMM(item.GetDrillValue()) / 2, quad_segs=128)
        g = g.difference(hole)
    return g
