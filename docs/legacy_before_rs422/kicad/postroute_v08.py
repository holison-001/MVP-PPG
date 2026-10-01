"""post-route: widen necked tracks, connect dangling 3V3/GND ends to planes with vias, straight C2 stubs"""
import pcbnew, json, sys, math
from pcbnew import FromMM, ToMM, VECTOR2I_MM as MM
b = pcbnew.LoadBoard(sys.argv[1]); drc = json.load(open(sys.argv[2], encoding="utf-8")) if len(sys.argv) > 2 else None
def P(v): return (round(ToMM(v.x), 4), round(ToMM(v.y), 4))
n = 0
for t in b.GetTracks():
    if t.GetClass() == "PCB_TRACK" and t.GetWidth() < FromMM(0.10): t.SetWidth(FromMM(0.10)); n += 1
print("widened (<0.10):", n)
PADS = [(P(pd.GetPosition()), max(ToMM(pd.GetSize().x), ToMM(pd.GetSize().y)) / 2, pd.GetNetCode()) for fp in b.GetFootprints() for pd in fp.Pads()]
def close(a, c): return abs(a[0]-c[0]) < 0.01 and abs(a[1]-c[1]) < 0.01
def ok(p, vpos, code):
    x, y = p
    if 0.45 < abs(x) < 1.45 and abs(y) < 2.4: return False
    if 1.95 < abs(x) < 3.75 and abs(y - 0.2) < 2.9: return False
    if math.hypot(x, y) > 6.9: return False
    if not all(math.hypot(x - vx, y - vy) >= 0.8 for vx, vy in vpos): return False
    return all(math.hypot(x - px, y - py) >= r + 0.25 + 0.2 for (px, py), r, nc in PADS if nc != code)
if drc:
    for u in drc.get("unconnected_items", []):
        for it in u["items"]:
            p = it.get("pos"); 
            if not p: continue
            # which net? find track at that point
            segs = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK" and (close(P(t.GetStart()), (p["x"], p["y"])) or close(P(t.GetEnd()), (p["x"], p["y"])))]
            if not segs: continue
            code = segs[0].GetNetCode(); name = segs[0].GetNetname()
            if name not in ("3V3", "GND"): print("unconnected on", name, "at", p, "- skipped (not a plane net)"); continue
            layer = segs[0].GetLayer()
            chain = {(p["x"], p["y"])}; changed = True
            allsegs = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK" and t.GetNetCode() == code and t.GetLayer() == layer]
            while changed:
                changed = False
                for s in allsegs:
                    a, c = P(s.GetStart()), P(s.GetEnd())
                    ina, inc = any(close(a, q) for q in chain), any(close(c, q) for q in chain)
                    if ina and not inc: chain.add(c); changed = True
                    if inc and not ina: chain.add(a); changed = True
            vpos = [P(v.GetPosition()) for v in b.GetTracks() if v.GetClass() == "PCB_VIA"]
            # candidates: chain points, segment midpoints, and points offset +/-0.5 mm perpendicular to segments (with a stub)
            cands = [(q, None) for q in chain if ok(q, vpos, code)]
            for sgm in allsegs:
                a, c = P(sgm.GetStart()), P(sgm.GetEnd())
                if not (any(close(a, q) for q in chain) and any(close(c, q) for q in chain)): continue
                m = ((a[0]+c[0])/2, (a[1]+c[1])/2); L = math.hypot(c[0]-a[0], c[1]-a[1])
                if L < 0.3: continue
                nx, ny = -(c[1]-a[1])/L, (c[0]-a[0])/L
                for q in (m, (m[0]+0.5*nx, m[1]+0.5*ny), (m[0]-0.5*nx, m[1]-0.5*ny)):
                    if ok(q, vpos, code): cands.append((q, m if q != m else None))
            if not cands: print("no via spot for", name, chain); continue
            q, stub = max(cands, key=lambda r: min(math.hypot(r[0][0]-vx, r[0][1]-vy) for vx, vy in vpos))
            v = pcbnew.PCB_VIA(b); v.SetPosition(MM(*q)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            v.SetDrill(FromMM(0.25)); v.SetWidth(FromMM(0.5)); v.SetNetCode(code); b.Add(v)
            if stub:
                t = pcbnew.PCB_TRACK(b); t.SetStart(MM(*stub)); t.SetEnd(MM(*q)); t.SetWidth(FromMM(0.15)); t.SetLayer(layer); t.SetNetCode(code); b.Add(t)
            print("via", name, "at", q, "stub" if stub else "")
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b); print("saved")
