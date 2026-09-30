# -*- coding: utf-8 -*-
"""Build an UNROUTED placement study, not the authoritative release PCB.
Use export_v08.py to validate/export the committed routed board.
  "...\\KiCad\\10.0\\bin\\python.exe" build_pcb_v08.py <out.kicad_pcb>            -> placement, planes, DSN
  "...\\KiCad\\10.0\\bin\\python.exe" build_pcb_v08.py <out.kicad_pcb> --ses x.ses -> import routed SES, fill, save
"""
import os, sys, math
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
from pcbnew import VECTOR2I_MM as MM, FromMM
import design_v08 as D

_fp_candidates = [os.environ.get("KICAD10_FOOTPRINT_DIR", ""),
                  r"C:\Program Files\KiCad\10.0\share\kicad\footprints",
                  r"C:\Users\LAPTOP\AppData\Local\Programs\KiCad\10.0\share\kicad\footprints"]
KICAD_FP = next(p for p in _fp_candidates if p and Path(p).is_dir())
out_path = sys.argv[1]
ses_path = sys.argv[sys.argv.index("--ses") + 1] if "--ses" in sys.argv else None

# ------------------------------------------------------------------ SES import mode
if ses_path:
    board = pcbnew.LoadBoard(out_path)
    ok = pcbnew.ImportSpecctraSES(board, ses_path)
    print("SES import:", ok)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(out_path, board)
    print("routed board saved; tracks:", len(board.GetTracks()))
    sys.exit(0)

board = pcbnew.BOARD()
ds = board.GetDesignSettings()
ds.SetCopperLayerCount(D.LAYERS)
ds.SetBoardThickness(FromMM(D.THICKNESS))
ds.m_MinClearance = FromMM(D.RULES["clearance"]); ds.m_TrackMinWidth = FromMM(0.1)
ds.m_ViasMinSize = FromMM(D.RULES["via_dia"]); ds.m_MinThroughDrill = FromMM(D.RULES["via_drill"])
ds.m_CopperEdgeClearance = FromMM(D.RULES["edge_clearance"]); ds.m_HoleClearance = FromMM(0.2)
ds.m_SolderMaskMinWidth = FromMM(0.1)
try:
    nc = ds.m_NetSettings.GetDefaultNetclass()
except Exception:
    nc = ds.m_NetSettings.m_DefaultNetClass
nc.SetClearance(FromMM(D.RULES["clearance"])); nc.SetTrackWidth(FromMM(D.RULES["track"]))
nc.SetViaDiameter(FromMM(D.RULES["via_dia"])); nc.SetViaDrill(FromMM(D.RULES["via_drill"]))

nets = {}
for n in D.NETS:
    ni = pcbnew.NETINFO_ITEM(board, n); board.Add(ni); nets[n] = ni

# ------------------------------------------------------------------ custom footprints
def new_fp(name):
    fp = pcbnew.FOOTPRINT(board); fp.SetFPID(pcbnew.LIB_ID("SleepBud", name)); fp.SetAttributes(pcbnew.FP_SMD); return fp

def smd_pad(fp, num, x, y, w, h, shape="roundrect"):
    pad = pcbnew.PAD(fp); pad.SetNumber(str(num)); pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    if shape == "circle":
        pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    else:
        pad.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT); pad.SetRoundRectRadiusRatio(0.25)
    pad.SetSize(MM(w, h)); pad.SetPosition(MM(x, y)); pad.SetLayerSet(pad.SMDMask()); fp.Add(pad); return pad

def fp_shape(fp, layer, pts, width=0.1):
    for a, b in zip(pts, pts[1:]):
        s = pcbnew.PCB_SHAPE(fp); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(MM(*a)); s.SetEnd(MM(*b))
        s.SetLayer(layer); s.SetWidth(FromMM(width)); fp.Add(s)

def fp_maxm86161():
    fp = new_fp("MAXM86161_OLGA-14"); fp.SetLibDescription("MAXM86161 14-pin OLGA 2.9x4.3 mm, land pattern 90-100106")
    for i in range(7):
        y = -1.8 + 0.6 * i
        smd_pad(fp, i + 1, -0.95, y, 0.66, 0.40); smd_pad(fp, 14 - i, 0.95, y, 0.66, 0.40)
    w, h = 1.45, 2.15
    fp_shape(fp, pcbnew.F_Fab, [(-w, -h), (w, -h), (w, h), (-w, h), (-w, -h)]); fp_shape(fp, pcbnew.F_Fab, [(-w, -h + 0.6), (-w + 0.6, -h)])
    cw, ch = 1.75, 2.45
    fp_shape(fp, pcbnew.F_CrtYd, [(-cw, -ch), (cw, -ch), (cw, ch), (-cw, ch), (-cw, -ch)], 0.05)
    d = pcbnew.PCB_SHAPE(fp); d.SetShape(pcbnew.SHAPE_T_CIRCLE); d.SetCenter(MM(-1.95, -2.1)); d.SetEnd(MM(-1.85, -2.1))
    d.SetLayer(pcbnew.F_SilkS); d.SetWidth(FromMM(0.15)); d.SetFilled(True); fp.Add(d)
    return fp

def fp_thvd_drl8():
    """TI DRL0008A (SOT-5X3): pads 0.67 x 0.30, pitch 0.5, columns 1.48 apart; pins 1-4 left top->bottom, 5-8 right bottom->top"""
    fp = new_fp("THVD1400_DRL8"); fp.SetLibDescription("TI DRL0008A SOT-5X3 8-pin, land pattern from THVD1400 datasheet")
    for i in range(4):
        y = -0.75 + 0.5 * i
        smd_pad(fp, i + 1, -0.74, y, 0.67, 0.30); smd_pad(fp, 8 - i, 0.74, y, 0.67, 0.30)
    w, h = 0.8, 1.05
    fp_shape(fp, pcbnew.B_Fab if False else pcbnew.F_Fab, [(-w, -h), (w, -h), (w, h), (-w, h), (-w, -h)])
    fp_shape(fp, pcbnew.F_Fab, [(-w, -h + 0.4), (-w + 0.4, -h)])
    cw, ch = 1.3, 1.1
    fp_shape(fp, pcbnew.F_CrtYd, [(-cw, -ch), (cw, -ch), (cw, ch), (-cw, ch), (-cw, -ch)], 0.05)
    return fp

def fp_cablepad(dia):
    fp = new_fp("CablePad_D%.1f" % dia); fp.SetLibDescription("Cable solder pad, round %.1f mm" % dia)
    smd_pad(fp, 1, 0, 0, dia, dia, "circle"); return fp

# ------------------------------------------------------------------ place
fps = {}
for ref, c in D.COMPONENTS.items():
    if c["lib"] == "custom":
        local_fp = Path(__file__).with_name("SleepBud.pretty") / (c["fp"] + ".kicad_mod")
        if local_fp.is_file():
            fp = pcbnew.FootprintLoad(str(local_fp.parent), c["fp"])
        elif c["fp"].startswith("MAXM"):
            fp = fp_maxm86161()
        elif c["fp"].startswith("THVD"):
            fp = fp_thvd_drl8()
        elif c["fp"].startswith("CablePad_D"):
            fp = fp_cablepad(float(c["fp"].split("_D")[1]))
        else:
            fp = pcbnew.FootprintLoad(str(Path(__file__).with_name("SleepBud.pretty")), c["fp"])
            assert fp is not None, (ref, c["fp"])
    else:
        fp = pcbnew.FootprintLoad(os.path.join(KICAD_FP, c["lib"] + ".pretty"), c["fp"]); assert fp is not None, (ref, c["fp"])
    fp.SetFPID(pcbnew.LIB_ID("SleepBud" if c["lib"] == "custom" else c["lib"], c["fp"]))
    fp.SetReference(ref); fp.SetValue(c["value"]); board.Add(fp); fp.SetPosition(MM(*c["pos"]))
    if c["side"] == "B":
        fp.SetLayerAndFlip(pcbnew.B_Cu)
    if c.get("rot"):
        fp.SetOrientationDegrees(c["rot"])
    fps[ref] = fp
    for num, net in c["pins"].items():
        pad = fp.FindPadByNumber(num); assert pad is not None, (ref, num)
        if net: pad.SetNet(nets[net])

def pp(ref, num):
    p = fps[ref].FindPadByNumber(num).GetPosition(); return pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)

def orient(ref, rule):
    fp = fps[ref]
    for rot in (0, 90, 180, 270):
        fp.SetOrientationDegrees(rot)
        if rule(): return rot
    raise SystemExit("no rotation satisfies rule for " + ref)

mx, my = D.COMPONENTS["U2"]["pos"]
r = orient("U2", lambda: pp("U2", "18")[1] > my + 1 and pp("U2", "19")[1] > my + 1 and pp("U2", "14")[0] > mx + 1)  # SWD/I2C row towards the centre, TX right
print("U2 rot", r, "SCL", pp("U2", "18"), "SDA", pp("U2", "19"), "TX", pp("U2", "14"), "RX", pp("U2", "15"), "VDD", pp("U2", "2"))
for ref in ("U4", "U5"):
    print(ref, "VOUT", pp(ref, "1"), "GND", pp(ref, "4"), "VIN", pp(ref, "8"))
# LVDS chips: differential pins 3/4 face the rim (outward), pins 1/5 face the centre
for ref, sgn in (("U3", 1), ("U6", -1)):
    cx, cy = D.COMPONENTS[ref]["pos"]
    r = orient(ref, lambda: sgn * (pp(ref, "3")[0] - cx) > 0.5 and sgn * (pp(ref, "4")[0] - cx) > 0.5 and sgn * (pp(ref, "1")[0] - cx) < -0.5 and (ref == "U3" or pp(ref, "5")[1] < cy))  # U6: R pin at the top end (towards the MCU); U3 is the mirror case (D at the bottom, VCC top)
    print(ref, "rot", r, "p1", pp(ref, "1"), "p2", pp(ref, "2"), "p3", pp(ref, "3"), "p4", pp(ref, "4"), "p5", pp(ref, "5"))

for ref, fp in fps.items():
    bb = fp.GetCourtyard(pcbnew.B_CrtYd if D.COMPONENTS[ref]["side"] == "B" else pcbnew.F_CrtYd).BBox()
    if bb.GetWidth(): print("crtyd %-3s x[%.2f,%.2f] y[%.2f,%.2f]" % (ref, pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetBottom())))
# text: refs on Fab layers only
for ref, fp in fps.items():
    rr = fp.Reference(); rr.SetTextSize(MM(0.5, 0.5)); rr.SetTextThickness(FromMM(0.08)); fp.Value().SetVisible(False)
    rr.SetLayer(pcbnew.F_Fab if D.COMPONENTS[ref]["side"] == "F" else pcbnew.B_Fab)
    if ref.startswith("J"):
        rr.SetVisible(False); pos = fp.GetPosition()
        lt = pcbnew.PCB_TEXT(board); lt.SetText(D.COMPONENTS[ref]["value"]); lt.SetLayer(pcbnew.B_Fab); lt.SetMirrored(True)
        lt.SetTextSize(MM(0.5, 0.5)); lt.SetTextThickness(FromMM(0.08)); lt.SetPosition(pcbnew.VECTOR2I(pos.x, pos.y - FromMM(1.0))); board.Add(lt)
for it in list(fps["U2"].GraphicalItems()):
    if it.GetLayer() in (pcbnew.B_SilkS, pcbnew.F_SilkS):
        it.GetParent().Remove(it)

# ------------------------------------------------------------------ outline + planes
edge = pcbnew.PCB_SHAPE(board); edge.SetShape(pcbnew.SHAPE_T_CIRCLE); edge.SetCenter(MM(0, 0)); edge.SetEnd(MM(D.BOARD_R, 0))
edge.SetLayer(pcbnew.Edge_Cuts); edge.SetWidth(FromMM(0.1)); board.Add(edge)

def zone(layer, net, prio, clearance=0.2):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(nets[net]); z.SetAssignedPriority(prio)
    z.SetLocalClearance(FromMM(clearance)); z.SetMinThickness(FromMM(0.15))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetThermalReliefGap(FromMM(0.2)); z.SetThermalReliefSpokeWidth(FromMM(0.25))
    for i in range(64):
        a = 2 * math.pi * i / 64; z.AppendCorner(MM(D.BOARD_R * math.cos(a), D.BOARD_R * math.sin(a)), -1)
    board.Add(z); return z

zone(pcbnew.In1_Cu, "GND", 0)
zone(pcbnew.In2_Cu, "3V3", 0)

t = pcbnew.PCB_TEXT(board); t.SetText("SleepBud PPG v0.8"); t.SetPosition(MM(0, 6.6)); t.SetLayer(pcbnew.B_Fab); t.SetMirrored(True)
t.SetTextSize(MM(0.5, 0.5)); t.SetTextThickness(FromMM(0.08)); board.Add(t)

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(out_path, board)
# Read local footprint definitions; never overwrite reviewed library sources.
dsn = os.path.splitext(out_path)[0] + ".dsn"
print("DSN export:", pcbnew.ExportSpecctraDSN(board, dsn), dsn)
print("saved", out_path, "pads:", sum(len(fp.Pads()) for fp in board.GetFootprints()))
