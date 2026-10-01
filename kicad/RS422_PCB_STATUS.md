# Current RS-422 PCB

Updated 2026-10-02. U4/U5 now use the Microchip MCP1703A /MC land pattern; U2 uses the matching project NoSilk variant. The 37-reference board was rearranged and rerouted. ERC errors/warnings, DRC errors, unrouted connections and schematic parity differences are zero. Full DRC restores ignored checks in a temporary copy and reports 25 advisory warnings.

See [current review](../docs/footprint_correction_20261001/README.md) for exact hashes, warnings, placement, layer totals and independent physical checks. The previous 59-via/18.799-mm front-routing figures are historical, not this board's metrics. Current via count: 62.

The board remains diameter13.5 mm, 4 layers, thickness0.8 mm, U1 alone on F.Cu. F.Cu and In1.Cu contain GND pours; In2 retains minimum0.40-mm 3V3 distribution without a pour. Keep the .kicad_dru file. F.Cu ground uses0.20-mm edge setback and0.15-mm signal clearance; other copper uses0.30-mm edge setback.

PCB center is (20,17) mm in the40×40-mm sheet. All design-model placements match the PCB and are relative to this center. Cable pads and labels have moved; old coordinate CSVs are stale.

Existing Gerber/BOM/position/board-STEP/schematic-PDF/old render outputs do not include this correction. No new Gerber or BOM was produced. Current review PNGs are in the linked review folder. Hardware and assembly validation remain required.
