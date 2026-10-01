# -*- coding: utf-8 -*-
"""
PPG PCB v0.8 - UART over RS-422, full duplex, Ø13.5; driver/receiver match MVP-AMP.
U3 XR33194ESBTR (TSOT-23-6): DI = UART_TX -> Y/Z = cable TXP/TXN (earbud -> controller).
U6 XR33183ESBTR (TSOT-23-6): A/B = cable RXP/RXN (controller -> earbud) -> RO = UART_RX.
Receiver enhanced fail-safe -> RO high (UART idle) for open/short/idle inputs.
U3 DE tied high and U6 active-low EN tied low: always enabled. R3 is the local 120 ohm receive termination.
R4 pulls UART_TX high during MCU reset. Matches the STM32 USART bootloader idle state.
Cable: +12V, GND, TXP, TXN, RXP, RXN (6 wires) + piezo coax direct to PZT. Use the shared GND conductor and keep the receiver common-mode input within -7 V to +12 V.
MCU STM32C011F6U6, LDO1 12->5 V (VLED), LDO2 5->3.3 V. 4-layer 0.8 mm. Front: U1 only.
Coordinates: centre (0,0), x right, y DOWN, mm.
"""

NETS = ["TXP_DRV", "TXN_DRV", "RXP_RCV", "RXN_RCV", "GND", "3V3", "5V_LED", "12V", "12V_IN", "SDA", "SCL", "VLDO", "VREF", "UART_TX", "UART_RX", "TXP", "TXN", "RXP", "RXN", "SWDIO", "SWCLK", "NRST"]

C0201 = dict(lib="Capacitor_SMD", fp="C_0201_0603Metric")
C0402 = dict(lib="Capacitor_SMD", fp="C_0402_1005Metric")
R0201 = dict(lib="Resistor_SMD", fp="R_0201_0603Metric")
TSOT236 = dict(lib="custom", fp="TSOT23-6_MaxLinear")
R0402 = dict(lib="Resistor_SMD", fp="R_0402_1005Metric")

COMPONENTS = {
    "U1": dict(value="MAXM86161EFD+", lib="custom", fp="MAXM86161_OLGA-14", side="F", pos=(0.0, 0.0), rot=0,
               desc="PPG optical module (G/R/IR LED + PD + AFE), single supply, internal 1.8 V LDO, I2C 0x62",
               pins={"1": "SDA", "2": "SCL", "3": "3V3", "4": "VLDO", "5": "5V_LED", "6": None, "7": None,
                     "8": None, "9": "GND", "10": "GND", "11": "GND", "12": "VREF", "13": None, "14": None}),
    "U2": dict(value="STM32C011F6U6", lib="custom", fp="ST_UFQFPN-20_3x3mm_P0.5mm_NoSilk", side="B", pos=(0.27, -4.0), rot=0,
               desc="MCU, USART1 (PA9/PA10) <-> RS-422 driver/receiver, I2C1 (PB6/PB7) -> PPG; USART bootloader over the link",
               pins={"1": None, "2": "3V3", "3": "GND", "4": "NRST", "5": None, "6": None, "7": None, "8": None, "9": None, "10": None,
                     "11": None, "12": None, "13": None, "14": "UART_TX", "15": "UART_RX", "16": "SWDIO", "17": "SWCLK",
                     "18": "SCL", "19": "SDA", "20": None}),
    "U3": dict(value="XR33194", mpn="XR33194ESBTR", manufacturer="MaxLinear", side="B", pos=(3.0, 0.1), rot=-90,
               desc="RS-422 driver, 2.5 Mbps slew-rate limited, VCC 3.3 V +/-5%; pin 2 VCC and pin 3 DE tied to 3V3; TSOT-23-6",
               datasheet="${KIPRJMOD}/../datasheet/pdf/XR33193_XR33194_XR33195_MaxLinear.pdf",
               pins={"1": "UART_TX", "2": "3V3", "3": "3V3", "4": "TXN_DRV", "5": "GND", "6": "TXP_DRV"}, **TSOT236),
    "U6": dict(value="XR33183", mpn="XR33183ESBTR", manufacturer="MaxLinear", side="B", pos=(-3.05, -0.82), rot=90,
               desc="RS-422 receiver, 52 Mbps, enhanced open/short/idle fail-safe RO high; VCC 3.0-5.5 V; pin 2 GND and active-low EN pin 5 tied to GND; external R3 120 ohm receive termination; TSOT-23-6",
               datasheet="${KIPRJMOD}/../datasheet/pdf/XR33180_XR33181_XR33183_XR33184_MaxLinear.pdf",
               pins={"1": "3V3", "2": "GND", "3": "UART_RX", "4": "RXN_RCV", "5": "GND", "6": "RXP_RCV"}, **TSOT236),
    "U4": dict(value="MCP1703A-5002E/MC", lib="custom", fp="MCP1703A_MC_DFN8_3x2mm_P0.5mm", side="B", pos=(-1.85, 4.37), rot=90,
               datasheet="${KIPRJMOD}/../datasheet/pdf/MCP1703A.pdf",
               desc="LDO 12 V -> 5 V (VLED)", pins={"1": "5V_LED", "2": None, "3": None, "4": "GND", "5": None, "6": None, "7": None, "8": "12V", "9": "GND"}),
    "U5": dict(value="MCP1703A-3302E/MC", lib="custom", fp="MCP1703A_MC_DFN8_3x2mm_P0.5mm", side="B", pos=(1.85, 4.37), rot=90,
               datasheet="${KIPRJMOD}/../datasheet/pdf/MCP1703A.pdf",
               desc="LDO 5 V -> 3.3 V", pins={"1": "3V3", "2": None, "3": None, "4": "GND", "5": None, "6": None, "7": None, "8": "5V_LED", "9": "GND"}),
    # ---- passives
    "C1": dict(value="10uF 6.3V X5R", side="B", pos=(0.0, 2.17), rot=180, pins={"1": "5V_LED", "2": "GND"}, desc="VLED bulk / LDO1 output", **C0402),
    "C4": dict(value="1uF 6.3V", side="B", pos=(-0.85, 0.85), rot=90, pins={"1": "VLDO", "2": "GND"}, desc="U1 VLDO bypass", **C0201),
    "C5": dict(value="1uF 6.3V", side="B", pos=(0.85, 0.85), rot=90, pins={"1": "VREF", "2": "GND"}, desc="U1 VREF bypass", **C0201),
    "R1": dict(value="4.7k", side="B", pos=(-0.85, -0.65), rot=90, pins={"1": "SDA", "2": "3V3"}, desc="I2C SDA pull-up", **R0201),
    "R2": dict(value="4.7k", side="B", pos=(0.85, -0.65), rot=90, pins={"1": "SCL", "2": "3V3"}, desc="I2C SCL pull-up", **R0201),
    "C6": dict(value="100nF", side="B", pos=(4.87, -3.4), rot=90, pins={"1": "3V3", "2": "GND"}, desc="U3 VCC bypass", **C0201),
    "C7": dict(value="100nF", side="B", pos=(-3.0, -3.4), rot=180, pins={"1": "3V3", "2": "GND"}, desc="U6 VCC bypass", **C0201),
    "C11": dict(value="100nF", side="B", pos=(-2.7, -4.35), rot=180, pins={"1": "3V3", "2": "GND"}, desc="U2 VDD bypass", **C0201),
    "C12": dict(value="1uF 6.3V", side="B", pos=(2.45, -5.1), rot=90, pins={"1": "3V3", "2": "GND"}, desc="U2 VDD bulk", **C0201),
    "C13": dict(value="1uF 25V X7R", side="B", pos=(-4.7, 2.75), rot=180, pins={"1": "12V", "2": "GND"}, desc="LDO1 input", **C0402),
    "C14": dict(value="1uF 6.3V", side="B", pos=(4.6, 3.5), rot=90, pins={"1": "3V3", "2": "GND"}, desc="LDO2 output", **C0201),
    # RS-422 additions; reviewed physical positions are applied in PLACEMENT below.
    "R3": dict(value="120/1%", mpn="CRCW0402120RFKEDHP", manufacturer="Vishay",
               datasheet="${KIPRJMOD}/../datasheet/pdf/Vishay_CRCW-HP_e3.pdf", side="B", pos=(-3.0, 2.3), rot=90,
               pins={"1": "RXP", "2": "RXN"},
               desc="RS-422 receive termination across cable RXP/RXN at U6; 120 ohm +/-1%, 0402, 0.2 W high-pulse series; cable-side of R7/R8; prototype pulse performance requires validation", **R0402),
    "R4": dict(value="10k", side="B", pos=(2.75, -2.1), rot=90,
               pins={"1": "UART_TX", "2": "3V3"},
               desc="UART_TX idle-state pull-up to 3V3, 10 kohm +/-5%, 0201; max static loss 1.21 mW at 3.465 V; keeps U3 DI high during MCU reset; MPN pending", **R0201),
    # ---- cable solder pads Ø1.2 (r <= 5.85)
    "J1": dict(value="12V", lib="custom", fp="CablePad_D1.2", side="B", pos=(-4.39, 3.85), rot=180, pins={"1": "12V_IN"}, desc="cable +12 V input, before ESD suppressor and FB1"),
    "J2": dict(value="GND", lib="custom", fp="CablePad_D1.2", side="B", pos=(0.0, 5.85), rot=180, pins={"1": "GND"}, desc="cable GND"),
    "J3": dict(value="TXP", lib="custom", fp="CablePad_D1.2", side="B", pos=(5.6, 1.3), rot=180, pins={"1": "TXP"}, desc="cable RS-422 TX+ (earbud -> controller)"),
    "J4": dict(value="TXN", lib="custom", fp="CablePad_D1.2", side="B", pos=(5.7, -1.0), rot=180, pins={"1": "TXN"}, desc="cable RS-422 TX-"),
    "J5": dict(value="RXP", lib="custom", fp="CablePad_D1.2", side="B", pos=(-5.8, 0.5), rot=180, pins={"1": "RXP"}, desc="cable RS-422 RX+ (controller -> earbud)"),
    "J6": dict(value="RXN", lib="custom", fp="CablePad_D1.2", side="B", pos=(-5.49, -2.0), rot=180, pins={"1": "RXN"}, desc="cable RS-422 RX-"),
    # ---- SWD debug test pads Ø0.8 (r <= 6.05; GND/3V3 via cable pads)
    "J7": dict(value="SWDIO", lib="custom", fp="CablePad_D0.8", side="B", pos=(2.6, -2.6), rot=180, pins={"1": "SWDIO"}, desc="SWD test pad PA13"),
    "J8": dict(value="SWCLK", lib="custom", fp="CablePad_D0.8", side="B", pos=(3.7, -2.6), rot=180, pins={"1": "SWCLK"}, desc="SWD test pad PA14"),
    "J9": dict(value="NRST", lib="custom", fp="CablePad_D0.8", side="B", pos=(-4.85, -3.1), rot=180, pins={"1": "NRST"}, desc="reset test pad"),
}

# 2026-10-01 ESD / input EMI filtering PCB placement update.
# Compact candidate sizes: FB1/series/termination = metric 1005; UART pull-up = 0201.
# RS-422 bus TVS arrays are omitted; D1 and SWD ESD retain the original 1.0 x 0.6 mm bodies.
# U1 is the only front-side component; all ESD suppressors and FB1 are on the back.
COMPONENTS.update({
    "D1": dict(value="SPHV15-01ETG", mpn="SPHV15-01ETG", lib="custom",
               fp="TVS_SOD882_1x0.6", side="B", pos=(-3.9, 1.76), rot=0,
               pins={"1": "12V_IN", "2": "GND"},
               desc="Littelfuse 15 V unidirectional input ESD TVS; K=1, A=2; 1.0x0.6 mm; transient residual at U4 VIN requires validation",
               datasheet="https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_array_sphv_datasheet.pdf?assetguid=4bdc7e09-5dd4-4010-a86a-0008bb6e228c"),
    "FB1": dict(value="BLM15PX601SN1D", mpn="BLM15PX601SN1D", lib="Inductor_SMD",
                fp="L_0402_1005Metric", side="B", pos=(-2.1, 2.15), rot=0,
                pins={"1": "12V_IN", "2": "12V"},
                desc="Murata ferrite bead 600 ohm at 100 MHz, 0.9 A at 85C, DCR 0.23 ohm max; metric 1005; C13 remains on filtered side",
                datasheet="https://www.murata.com/en-us/products/productdetail?partno=BLM15PX601SN1%23"),
})
# Compact RS-422 prototype: no bus TVS arrays; retain 22 ohm IC-side series resistors.
# The 0402 HP parts are not assumed equivalent to AMP's larger resistors in pulse capability.
for ref, net, pos, rot in [
    ("D6", "SWDIO", (2.6, -3.65), 90),
    ("D7", "SWCLK", (3.7, -4.0), 90),
    ("D8", "NRST", (-4.2, -4.15), 90),
]:
    COMPONENTS[ref] = dict(value="ESD351DPYR", mpn="ESD351DPYR", lib="custom",
        fp="TI_DPY0002A_1x0.6", side="B", pos=pos, rot=rot,
        pins={"1": net, "2": "GND"},
        desc=f"TI unidirectional low-capacitance ESD TVS for {net}; K/IO=1, A/GND=2; VRWM 3.6 V, Ctyp 1.8 pF; DFN1006",
        datasheet="https://www.ti.com/lit/ds/symlink/esd351.pdf")
for ref, inner, cable, pos in [
    ("R5", "TXP_DRV", "TXP", (3.5, 1.7)),
    ("R6", "TXN_DRV", "TXN", (3.5, -1.7)),
    ("R7", "RXP_RCV", "RXP", (-3.5, 1.7)),
    ("R8", "RXN_RCV", "RXN", (-3.5, -1.7)),
]:
    COMPONENTS[ref] = dict(value="22", mpn="CRCW040222R0JNEDHP", manufacturer="Vishay",
        side="B", pos=pos, rot=0, pins={"1": inner, "2": cable},
        desc="RS-422 IC-side series resistor, 22 ohm +/-5%, 0402, 0.2 W high-pulse series; prototype surge/ESD performance requires validation",
        datasheet="${KIPRJMOD}/../datasheet/pdf/Vishay_CRCW-HP_e3.pdf", **R0402)

# 2026-10-02: 37-part placement after correcting the MCP1703A /MC land pattern.
# This table is authoritative for PCB generation; schematic drawing coordinates
# are maintained independently by layout_schematic_v08.py.
PLACEMENT = {
    "C1": (-2.10000000, 0.90000000, 270),
    "C11": (2.55000000, 1.10000000, 90),
    "C12": (-4.74000000, -1.93370000, 180),
    "C13": (-5.10000000, 2.80000000, 90),
    "C14": (3.60000000, 2.10000000, 180),
    "C4": (0.40000000, -2.10000000, 0),
    "C5": (2.55000000, -0.30000000, 270),
    "C6": (5.32960000, -2.79780000, 315),
    "C7": (0.50880000, -4.67000000, 45),
    "D1": (-2.23020000, -5.49890000, 180),
    "D6": (-2.50000000, 5.45000000, 0),
    "D7": (3.52840000, -1.13820000, 315),
    "D8": (-3.50230000, 0.40770000, 180),
    "FB1": (0.91970000, -5.93190000, 0),
    "J1": (-0.78280000, -5.79100000, 180),
    "J2": (0.60000000, 5.75000000, 225),
    "J3": (4.48130000, -2.01010000, 270),
    "J4": (5.10310000, 1.68080000, 180),
    "J5": (-4.93450000, -3.05030000, 270),
    "J6": (-0.90000000, 5.75000000, 90),
    "J7": (1.90000000, 5.51000000, 0),
    "J8": (5.10000000, 3.00000000, 135),
    "J9": (-3.29550000, 1.40620000, 315),
    "R1": (-2.43310000, -0.40760000, 180),
    "R2": (-3.14660000, -1.11730000, 180),
    "R3": (-5.89710000, 0.86760000, 90),
    "R4": (5.82670000, -0.99760000, 45),
    "R5": (3.40000000, 0.80000000, 90),
    "R6": (5.50000000, 0.30000000, 0),
    "R7": (-4.71970000, 0.65260000, 270),
    "R8": (-4.88500000, -0.82780000, 180),
    "U1": (0.00000000, 0.00000000, 0),
    "U2": (0.14190000, 0.27490000, 90),
    "U3": (2.55630000, -3.63250000, 45),
    "U4": (-2.15000000, 3.70000000, 180),
    "U5": (2.30000000, 3.70000000, 180),
    "U6": (-2.19000000, -3.23370000, 180),
}
assert set(PLACEMENT) == set(COMPONENTS)
for _ref, (_x, _y, _rot) in PLACEMENT.items():
    COMPONENTS[_ref].update(pos=(_x, _y), rot=_rot)

VIAS = []
TRACKS = []

BOARD_R = 6.75         # Ø13.5 (fixed approved board diameter)
LAYERS = 4
THICKNESS = 0.8
RULES = dict(clearance=0.15, track=0.15, via_dia=0.5, via_drill=0.25, edge_clearance=0.3)
TITLE = "SleepBud PPG PCB v0.8"
