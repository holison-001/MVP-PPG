"""Separate the board's sheet position from coordinates relative to its center."""
import pcbnew as k
from pathlib import Path
import re

SHEET_SIZE_MM = (40.0, 40.0)
BOARD_CENTER_MM = (20.0, 17.0)
SHEET_MARGIN_MM = 2.0


def set_saved_sheet_size(path):
    """Set User paper size; KiCad 10's Python bindings do not expose PAGE_INFO."""
    path = Path(path)
    text, count = re.subn(r'\(paper\s+"[^"]+"[^)]*\)',
                         f'(paper "User" {SHEET_SIZE_MM[0]:g} {SHEET_SIZE_MM[1]:g})',
                         path.read_text(), count=1)
    if count != 1:
        raise ValueError('Expected one saved paper declaration')
    path.write_text(text)


def saved_sheet_size(path):
    match = re.search(r'\(paper\s+"User"\s+([\d.]+)\s+([\d.]+)\)', Path(path).read_text())
    return tuple(map(float, match.groups())) if match else None


def center_mm(board):
    edges = [item for item in board.GetDrawings()
             if isinstance(item, k.PCB_SHAPE) and item.GetLayer() == k.Edge_Cuts]
    if len(edges) != 1 or edges[0].GetShape() != k.SHAPE_T_CIRCLE:
        raise ValueError('Expected one circular board outline')
    p = edges[0].GetCenter()
    return (k.ToMM(p.x), k.ToMM(p.y))


def move_center(board, target):
    """Move all geometry, including filled polygons, by one rigid translation."""
    old = center_mm(board)
    delta = k.VECTOR2I(k.FromMM(target[0] - old[0]), k.FromMM(target[1] - old[1]))
    board.Move(delta)
    return old


def place_in_sheet(board):
    move_center(board, BOARD_CENTER_MM)
    origin = k.VECTOR2I(k.FromMM(BOARD_CENTER_MM[0]), k.FromMM(BOARD_CENTER_MM[1]))
    board.GetDesignSettings().SetAuxOrigin(origin)
    board.GetDesignSettings().SetGridOrigin(origin)


def normalize_for_analysis(board):
    """Normalize an in-memory board only; callers must not save this copy."""
    return move_center(board, (0.0, 0.0))
