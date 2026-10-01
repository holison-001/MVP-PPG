# Independent PCB audit — PASS

Audited `/workspace/ppg-pcb-work/stage/ppg_pcb_v08.kicad_pcb` read-only against the current repository schematic, design data, footprint libraries and original PCB. All audit inputs remained unchanged throughout validation.

| Check | Result |
|---|---|
| Schematic components / numbered pads / nets | 35 / 111 / 44; exact match |
| Component sides | U1 only on top; all other 34 on bottom |
| Power and TVS polarity | J1/D1/FB1.1 on 12V_IN; FB1.2/C13/U4 VIN on 12V; every TVS pin 1 signal, pin 2 GND |
| Sensor and footprints | U1 placement unchanged; all pad geometries preserved |
| Board | Diameter 13.5 mm; 4 copper layers; thickness 0.8 mm |
| Routing | 30 front and 153 back track segments; zero inner-layer track segments |
| Track and via dimensions | Minimum trace width 0.1 mm; 34 vias, all 0.5 mm / 0.25 mm drill |
| Via interference | No via drill over SMD copper; no same-net via-to-via overlap |
| TVS ground returns | All 8 dedicated vias and 0.2 mm direct traces preserved; length 0.525–0.570 mm |

Two ground vias have annular copper joining same-net pads, with their drills remaining outside the pads; this is not a drill interference. The independent audit reports no remaining issues. DRC is recorded separately.

The reusable net checker rejects incorrect board thickness, copper-layer count, circular board outline and any routed track segment on an inner layer. Incorrect thickness, layer count and an inner-layer track were detected in memory without saving a PCB.

Audited board SHA-256: `03709b49341c3901012be2a3edece03c8007b1238ee3284406bd707d44844c5a`

Schematic SHA-256: `cacd4a8d676d97b61cb60be985126533673ead4233c0b91e2fb304bb89bcadf3`

Design SHA-256: `39a60a1d9a6ea4ed8aa5c0c6b9a769795a27177670610c5391cc5554986667e8`

Full checks and hashes for every source input are in `final_audit.json`.
