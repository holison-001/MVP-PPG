# -*- coding: utf-8 -*-
"""
PPG PCB v0.8 - UART over LVDS (TTL->LVDS driver + LVDS->TTL receiver), full duplex, Ø13.5.
U3 SN65LVDS1 (SOT-23-5): D = UART_TX -> Y/Z = cable TXP/TXN (earbud -> controller).
U6 SN65LVDT2 (SOT-23-5, 110 R termination built in): A/B = cable RXP/RXN (controller -> earbud) -> R = UART_RX.
  Receiver open-circuit fail-safe -> R high (UART idle) when the controller is off / cable open.
No direction control, no external termination, works with the STM32 USART bootloader.
Cable: +12V, GND, TXP, TXN, RXP, RXN (6 wires) + piezo coax direct to PZT. Ground offset between ends must stay < 1 V (common GND wire).
MCU STM32C011F6U6, LDO1 12->5 V (VLED), LDO2 5->3.3 V. 4-layer 0.8 mm. Front: U1 only.
Coordinates: centre (0,0), x right, y DOWN, mm.
"""

NETS = ["GND", "3V3", "5V_LED", "12V", "12V_IN", "SDA", "SCL", "VLDO", "VREF", "UART_TX", "UART_RX", "TXP", "TXN", "RXP", "RXN", "SWDIO", "SWCLK", "NRST"]

C0201 = dict(lib="Capacitor_SMD", fp="C_0201_0603Metric")
C0402 = dict(lib="Capacitor_SMD", fp="C_0402_1005Metric")
R0201 = dict(lib="Resistor_SMD", fp="R_0201_0603Metric")
SOT235 = dict(lib="Package_TO_SOT_SMD", fp="SOT-23-5")

COMPONENTS = {
    "U1": dict(value="MAXM86161EFD+", lib="custom", fp="MAXM86161_OLGA-14", side="F", pos=(0.0, 0.0), rot=0,
               desc="PPG optical module (G/R/IR LED + PD + AFE), single supply, internal 1.8 V LDO, I2C 0x62",
               pins={"1": "SDA", "2": "SCL", "3": "3V3", "4": "VLDO", "5": "5V_LED", "6": None, "7": None,
                     "8": None, "9": "GND", "10": "GND", "11": "GND", "12": "VREF", "13": None, "14": None}),
    "U2": dict(value="STM32C011F6U6", lib="Package_DFN_QFN", fp="ST_UFQFPN-20_3x3mm_P0.5mm", side="B", pos=(0.27, -4.0), rot=0,
               desc="MCU, USART1 (PA9/PA10) <-> LVDS driver/receiver, I2C1 (PB6/PB7) -> PPG; USART bootloader over the link",
               pins={"1": None, "2": "3V3", "3": "GND", "4": "NRST", "5": None, "6": None, "7": None, "8": None, "9": None, "10": None,
                     "11": None, "12": None, "13": None, "14": "UART_TX", "15": "UART_RX", "16": "SWDIO", "17": "SWCLK",
                     "18": "SCL", "19": "SDA", "20": None}),
    "U3": dict(value="SN65LVDS1DBVR", side="B", pos=(3.0, 0.1), rot=-90,
               desc="LVDS driver (TTL->LVDS): 1 VCC, 2 GND, 3 Z, 4 Y, 5 D",
               pins={"1": "3V3", "2": "GND", "3": "TXN", "4": "TXP", "5": "UART_TX"}, **SOT235),
    "U6": dict(value="SN65LVDT2DBVR", side="B", pos=(-3.05, -0.82), rot=90,
               desc="LVDS receiver (LVDS->TTL) with 110 R termination: 1 VCC, 2 GND, 3 A, 4 B, 5 R",
               pins={"1": "3V3", "2": "GND", "3": "RXP", "4": "RXN", "5": "UART_RX"}, **SOT235),
    "U4": dict(value="MCP1703A-5002E/MC", lib="Package_DFN_QFN", fp="DFN-8-1EP_2x3mm_P0.5mm_EP0.61x2.2mm", side="B", pos=(-1.85, 4.37), rot=90,
               desc="LDO 12 V -> 5 V (VLED)", pins={"1": "5V_LED", "2": None, "3": None, "4": "GND", "5": None, "6": None, "7": None, "8": "12V", "9": "GND"}),
    "U5": dict(value="MCP1703A-3302E/MC", lib="Package_DFN_QFN", fp="DFN-8-1EP_2x3mm_P0.5mm_EP0.61x2.2mm", side="B", pos=(1.85, 4.37), rot=90,
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
    # ---- cable solder pads Ø1.2 (r <= 5.85)
    "J1": dict(value="12V", lib="custom", fp="CablePad_D1.2", side="B", pos=(-4.39, 3.85), rot=180, pins={"1": "12V_IN"}, desc="cable +12 V input, before ESD suppressor and FB1"),
    "J2": dict(value="GND", lib="custom", fp="CablePad_D1.2", side="B", pos=(0.0, 5.85), rot=180, pins={"1": "GND"}, desc="cable GND"),
    "J3": dict(value="TXP", lib="custom", fp="CablePad_D1.2", side="B", pos=(5.6, 1.3), rot=180, pins={"1": "TXP"}, desc="cable LVDS TX+ (earbud -> controller)"),
    "J4": dict(value="TXN", lib="custom", fp="CablePad_D1.2", side="B", pos=(5.7, -1.0), rot=180, pins={"1": "TXN"}, desc="cable LVDS TX-"),
    "J5": dict(value="RXP", lib="custom", fp="CablePad_D1.2", side="B", pos=(-5.8, 0.5), rot=180, pins={"1": "RXP"}, desc="cable LVDS RX+ (controller -> earbud)"),
    "J6": dict(value="RXN", lib="custom", fp="CablePad_D1.2", side="B", pos=(-5.49, -2.0), rot=180, pins={"1": "RXN"}, desc="cable LVDS RX-"),
    # ---- SWD debug test pads Ø0.8 (r <= 6.05; GND/3V3 via cable pads)
    "J7": dict(value="SWDIO", lib="custom", fp="CablePad_D0.8", side="B", pos=(2.6, -2.6), rot=180, pins={"1": "SWDIO"}, desc="SWD test pad PA13"),
    "J8": dict(value="SWCLK", lib="custom", fp="CablePad_D0.8", side="B", pos=(3.7, -2.6), rot=180, pins={"1": "SWCLK"}, desc="SWD test pad PA14"),
    "J9": dict(value="NRST", lib="custom", fp="CablePad_D0.8", side="B", pos=(-4.85, -3.1), rot=180, pins={"1": "NRST"}, desc="reset test pad"),
}

# 2026-10-01 ESD / input EMI filtering PCB placement update.
# User-approved sizes: FB1 = metric 1005 (1.0 x 0.5 mm);
# ESD suppressors = DFN1006 (1.0 x 0.6 mm).
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
for ref, net, pos, rot in [
    ("D2", "TXP", (5.45, 0.12), 180),
    ("D3", "TXN", (5.35, -2.1), 180),
    ("D4", "RXP", (-5.45, 1.7), 0),
    ("D5", "RXN", (-5.45, -0.8), 0),
    ("D6", "SWDIO", (2.6, -3.65), 90),
    ("D7", "SWCLK", (3.7, -4.0), 90),
    ("D8", "NRST", (-4.2, -4.15), 90),
]:
    COMPONENTS[ref] = dict(value="ESD351DPYR", mpn="ESD351DPYR", lib="custom",
        fp="TI_DPY0002A_1x0.6", side="B", pos=pos, rot=rot,
        pins={"1": net, "2": "GND"},
        desc=f"TI unidirectional low-capacitance ESD TVS for {net}; K/IO=1, A/GND=2; VRWM 3.6 V, Ctyp 1.8 pF; DFN1006",
        datasheet="https://www.ti.com/lit/ds/symlink/esd351.pdf")

VIAS = []
TRACKS = []

BOARD_R = 6.75         # Ø13.5 (two SOT-23-5 do not fit the Ø13 ring)
LAYERS = 4
THICKNESS = 0.8
RULES = dict(clearance=0.15, track=0.15, via_dia=0.5, via_drill=0.25, edge_clearance=0.3)
TITLE = "SleepBud PPG PCB v0.8"
