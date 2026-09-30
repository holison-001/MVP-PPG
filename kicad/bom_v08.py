import pymupdf, sys, csv, zipfile, glob, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_v08 as D
pg = pymupdf.open("../docs/ppg_pcb_v08_schematic.pdf")[0]; pg.get_pixmap(dpi=110).save("../docs/schematic_preview.png")
note = {"MAXM86161EFD+": "ADI MAXM86161EFD+ (consigned)", "STM32C011F6U6": "ST STM32C011F6U6 UFQFPN-20",
        "SN65LVDS1DBVR": "TI SN65LVDS1DBVR LVDS driver SOT-23-5", "SN65LVDT2DBVR": "TI SN65LVDT2DBVR LVDS receiver, 110 R termination, SOT-23-5",
        "MCP1703A-5002E/MC": "Microchip MCP1703A-5002E/MC (2x3 DFN)", "MCP1703A-3302E/MC": "Microchip MCP1703A-3302E/MC (2x3 DFN)",
        "10uF 6.3V X5R": "0402 X5R 6.3V 10uF e.g. GRM155R60J106ME47", "1uF 6.3V": "0201 X5R 6.3V 1uF e.g. GRM033R60J105MEA2",
        "100nF": "0201 X7R 16V 100nF e.g. GRM033R71C104KE14", "4.7k": "0201 1% 4.7k", 
        "1uF 25V X7R": "0402 X7R 25V 1uF e.g. GRM155R61E105KA12"}
groups = {}
for ref, c in D.COMPONENTS.items():
    if ref.startswith("J"): continue
    groups.setdefault((c["value"], c["fp"]), []).append(ref)
with open("../docs/ppg_pcb_v08_BOM.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["Refs", "Qty", "Value", "Footprint", "Side", "Part / note"])
    for (val, fp), refs in groups.items():
        w.writerow([", ".join(refs), len(refs), val, fp, "Top(F)" if D.COMPONENTS[refs[0]]["side"] == "F" else "Bottom(B)", note.get(val, "")])
    w.writerow(["J1-J6", 6, "cable solder pads (12V, GND, TXP, TXN, RXP, RXN)", "CablePad_D1.2", "Bottom(B)", "hand-soldered cable (LVDS pairs twisted); piezo coax not on PCB"])
    w.writerow(["J7-J9", 3, "SWD test pads (SWDIO, SWCLK, NRST)", "CablePad_D0.8", "Bottom(B)", "debug; GND/3V3 from cable pads"])
z = zipfile.ZipFile("../ppg_pcb_v08_gerber.zip", "w", zipfile.ZIP_DEFLATED)
for fn in sorted(glob.glob("../gerber/*")): z.write(fn, os.path.basename(fn))
z.close(); print("gerber zip:", len(z.namelist()), "files")
