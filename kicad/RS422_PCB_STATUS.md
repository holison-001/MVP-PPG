# Current RS-422 PCB

`ppg_pcb_v08.kicad_pcb` is the routed 37-reference design without D2/D4. DRC errors, unrouted connections and schematic-parity differences are zero. Five existing advisory warnings remain documented in `../docs/verification_rs422_no_bus_tvs/`.

F.Cu contains U1, 18.799 mm of local routing and 102.636 mm² GND fill. In1.Cu contains 43.971 mm of selected routing and 88.032 mm² GND fill. Its two filled regions connect through the existing ground network. In2.Cu retains the 0.40 mm 3V3 tracks and selected routing, without a pour. All other components remain on B.Cu. There are 59 existing vias; no new vias were added.

The board center is at (20,17) mm inside the custom 40×40 mm sheet, with the auxiliary and grid origins at that point. Design-model placement and preview geometry remain relative to the PCB center. `board_coordinates_v08.py` handles translation for generation and read-only inspection.

F.Cu ground-to-signal clearance is 0.15 mm and ground-to-edge setback is 0.20 mm. Keep `ppg_pcb_v08.kicad_dru` beside the PCB/project. Other copper retains the 0.30 mm edge rule.

`ppg_rs422_review.*` is an earlier incomplete snapshot. Gerber/BOM payloads remain frozen until explicit user approval. See `../docs/PCB_layers_20261001.md` and `../docs/verification_rs422_no_bus_tvs/in1_routing_changes.json`.
