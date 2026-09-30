import pcbnew, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_v08 as D
from collections import Counter
b = pcbnew.LoadBoard("ppg_pcb_v08.kicad_pcb"); mism = []
for fp in b.GetFootprints():
    for pad in fp.Pads():
        want = D.COMPONENTS[fp.GetReference()]["pins"].get(pad.GetNumber()); got = pad.GetNetname() or None
        if want != got: mism.append((fp.GetReference(), pad.GetNumber(), want, got))
print("PCB vs design mismatches:", mism or "NONE (%d pads)" % sum(len(fp.Pads()) for fp in b.GetFootprints()))
c = Counter()
for t in b.GetTracks(): c["via" if t.GetClass() == "PCB_VIA" else b.GetLayerName(t.GetLayer())] += 1
print("routing:", dict(c))
