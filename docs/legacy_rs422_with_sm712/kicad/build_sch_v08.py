# -*- coding: utf-8 -*-
"""Generate ppg_pcb_v08.kicad_sch (KiCad 9/10 s-expression) from design_v08.py.
Plain CPython:  python build_sch_v08.py <out.kicad_sch>
Every symbol pin gets a short wire ending in a net label (or a power symbol for GND/3V3/5V_LED).
"""
import os, sys, uuid
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_v08 as D
from layout_schematic_v08 import parse, get, children, prop as get_property, tidy

out = sys.argv[1]
PROJECT = os.path.splitext(os.path.basename(out))[0]
# Retain PCB cross-probe links when rebuilding an existing schematic.
PREVIOUS = parse(Path(out).read_text(encoding="utf-8")) if Path(out).exists() else None
PREVIOUS_SYMBOLS = {str(get_property(s, "Reference")[2]): s for s in children(PREVIOUS, "symbol")} if PREVIOUS else {}
ROOT_UUID = str(get(PREVIOUS, "uuid")[1]) if PREVIOUS else str(uuid.uuid4())
POWER = {"GND": "SleepBud:GND", "3V3": "SleepBud:3V3", "5V_LED": "SleepBud:5V_LED", "12V": "SleepBud:12V"}
FONT = "(effects (font (size 1.27 1.27)))"

def U(): return str(uuid.uuid4())

# ----------------------------------------------------------------- symbol library definitions
def prop(name, val, x, y, hide=False, rot=0, justify=None):
    h = "(hide yes)" if hide else ""
    j = f"(justify {justify})" if justify else ""
    return f'(property "{name}" "{val}" (at {x} {y} {rot}) (effects (font (size 1.27 1.27)) {j} {h}))'

def pin(etype, x, y, ang, length, name, num, hide_name=False):
    fx = "(effects (font (size 1.27 1.27)) (hide yes))" if hide_name else FONT
    return (f'(pin {etype} line (at {x} {y} {ang}) (length {length}) '
            f'(name "{name}" {fx}) (number "{num}" {fx}))')

def rect(x1, y1, x2, y2):
    return f'(rectangle (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.254) (type default)) (fill (type background)))'

def sym_ic(libid, name, ref_prefix, left, right, bottom, w, h, desc):
    """left/right/bottom: list of (num, name, etype, offset).  Body rect +/-w, +/-h.  Pin length 5.08."""
    L = 5.08
    pins = []
    for num, nm, et, y in left:
        pins.append(pin(et, -w - L, y, 0, L, nm, num))
    for num, nm, et, y in right:
        pins.append(pin(et, w + L, y, 180, L, nm, num))
    for num, nm, et, x in bottom:
        pins.append(pin(et, x, -h - L, 90, L, nm, num))
    return f'''(symbol "{libid}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
      {prop("Reference", ref_prefix, -w, h + 2.54)} {prop("Value", name, w, h + 2.54)}
      {prop("Footprint", "", 0, 0, True)} {prop("Datasheet", "", 0, 0, True)} {prop("Description", desc, 0, 0, True)}
      (symbol "{name}_0_1" {rect(-w, -h, w, h)})
      (symbol "{name}_1_1" {' '.join(pins)}))'''

def sym_passive(libid, name, desc, fp_filter):
    if name == "R":
        body = rect(-1.016, -2.54, 1.016, 2.54)
        p1 = pin("passive", 0, 3.81, 270, 1.27, "", "1"); p2 = pin("passive", 0, -3.81, 90, 1.27, "", "2")
    else:
        body = ('(polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508) (type default)) (fill (type none)))'
                '(polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none)))')
        p1 = pin("passive", 0, 3.81, 270, 2.794, "", "1"); p2 = pin("passive", 0, -3.81, 90, 2.794, "", "2")
    return f'''(symbol "{libid}" (pin_numbers (hide yes)) (pin_names (offset 0)) (exclude_from_sim no) (in_bom yes) (on_board yes)
      {prop("Reference", name, 2.032, 0, rot=90)} {prop("Value", name, 0, 0, rot=90)}
      {prop("Footprint", "", -1.778, 0, True, 90)} {prop("Datasheet", "", 0, 0, True)} {prop("Description", desc, 0, 0, True)}
      {prop("ki_fp_filters", fp_filter, 0, 0, True)}
      (symbol "{name}_0_1" {body})
      (symbol "{name}_1_1" {p1} {p2}))'''

def sym_pad():
    return f'''(symbol "SleepBud:PAD" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
      {prop("Reference", "J", 0, 3.81)} {prop("Value", "PAD", 0, -3.81)}
      {prop("Footprint", "", 0, 0, True)} {prop("Datasheet", "", 0, 0, True)} {prop("Description", "Cable solder pad", 0, 0, True)}
      (symbol "PAD_0_1" (circle (center 0 0) (radius 1.27) (stroke (width 0.254) (type default)) (fill (type none))))
      (symbol "PAD_1_1" {pin("passive", -3.81, 0, 0, 2.54, "", "1", True)}))'''

def sym_tvs(name, bidirectional=False):
    """Vertical TVS, pin 1 at top (cathode for a unidirectional part).

    Geometry follows KiCad Device:D_Zener / D_TVS, rotated into a shunt
    orientation; this is deliberately distinct from an ordinary diode.
    """
    if bidirectional:
        paths = [[(-2.54, 1.27), (-2.54, -1.27), (2.54, 1.27), (2.54, -1.27), (-2.54, 1.27)],
                 [(0.508, 1.27), (0, 1.27), (0, -1.27), (-0.508, -1.27)],
                 [(1.27, 0), (-1.27, 0)]]
    else:
        paths = [[(-1.27, -1.27), (-1.27, 1.27), (-0.762, 1.27)],
                 [(1.27, 0), (-1.27, 0)],
                 [(1.27, -1.27), (1.27, 1.27), (-1.27, 0), (1.27, -1.27)]]
    body = ' '.join('(polyline (pts ' + ' '.join(f'(xy {y} {-x})' for x, y in path)
                    + ') (stroke (width 0.254) (type default)) (fill (type none)))' for path in paths)
    desc = ('Bidirectional' if bidirectional else 'Unidirectional, pin 1 cathode and pin 2 anode') + ' transient-voltage-suppression diode'
    return f'''(symbol "SleepBud:{name}" (pin_numbers (hide yes)) (pin_names (offset 0) (hide yes)) (exclude_from_sim no) (in_bom yes) (on_board yes)
      {prop("Reference", "D", 3.81, 1.905)} {prop("Value", name, 3.81, -1.905)}
      {prop("Footprint", "", 0, 0, True)} {prop("Datasheet", "", 0, 0, True)} {prop("Description", desc, 0, 0, True)}
      (symbol "{name}_0_1" {body})
      (symbol "{name}_1_1" {pin("passive", 0, 3.81, 270, 2.54, "A1" if bidirectional else "K", "1", True)}
        {pin("passive", 0, -3.81, 90, 2.54, "A2" if bidirectional else "A", "2", True)}))'''

def sym_sm712():
    # Same 3-pin IO1/IO2/GND symbol convention as MVP-AMP CDSOT23-SM712.
    return f'''(symbol "SleepBud:CDSOT23-SM712" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
      {prop("Reference", "D", 6.35, 5.08)} {prop("Value", "SM712", 6.35, 2.54)}
      {prop("Footprint", "Package_TO_SOT_SMD:SOT-23", 0, 0, True)}
      {prop("Datasheet", "${KIPRJMOD}/../datasheet/pdf/Bourns_CDSOT23-SM712.pdf", 0, 0, True)}
      {prop("Description", "SM712 asymmetric two-line TVS array, -7/+12 V working; pins 1/2 lines, pin 3 GND", 0, 0, True)}
      (symbol "CDSOT23-SM712_0_1" {rect(-5.08, -5.08, 5.08, 5.08)})
      (symbol "CDSOT23-SM712_1_1" {pin("passive", -7.62, 2.54, 0, 2.54, "IO1", "1")}
        {pin("passive", -7.62, -2.54, 0, 2.54, "IO2", "2")}
        {pin("passive", 0, -7.62, 90, 2.54, "GND", "3")}))'''


def sym_bead():
    # Horizontal version of KiCad Device:FerriteBead_Small: slanted core block,
    # not a resistor body. Pin 1 is the unfiltered input on the left.
    body = ('(polyline (pts (xy -0.2794 -1.8288) (xy -1.4986 -1.1176) (xy 0.2032 1.8288) (xy 1.4224 1.1176) (xy -0.2794 -1.8288)) '
            '(stroke (width 0.254) (type default)) (fill (type none)))'
            '(polyline (pts (xy -1.2954 0) (xy -0.889 0)) (stroke (width 0) (type default)) (fill (type none)))'
            '(polyline (pts (xy 0.7874 0) (xy 1.27 0)) (stroke (width 0) (type default)) (fill (type none)))')
    return f'''(symbol "SleepBud:FerriteBead" (pin_numbers (hide yes)) (pin_names (offset 0) (hide yes)) (exclude_from_sim no) (in_bom yes) (on_board yes)
      {prop("Reference", "FB", 0, 5.08)} {prop("Value", "FerriteBead", 0, 2.54)}
      {prop("Footprint", "", 0, 0, True)} {prop("Datasheet", "", 0, 0, True)} {prop("Description", "Series ferrite bead", 0, 0, True)}
      (symbol "FerriteBead_0_1" {body})
      (symbol "FerriteBead_1_1" {pin("passive", -3.81, 0, 0, 2.54, "", "1", True)} {pin("passive", 3.81, 0, 180, 2.54, "", "2", True)}))'''

def sym_power(libid, name, up=True):
    if up:
        g = ('(polyline (pts (xy -0.762 1.27) (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none)))'
             '(polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none)))')
        vy = 3.81
    else:
        g = ('(polyline (pts (xy 0 0) (xy 0 -1.27)) (stroke (width 0) (type default)) (fill (type none)))'
             '(polyline (pts (xy -1.27 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27)) (stroke (width 0) (type default)) (fill (type none)))')
        vy = -3.81
    return f'''(symbol "{libid}" (power) (pin_names (offset 0)) (exclude_from_sim no) (in_bom no) (on_board yes)
      {prop("Reference", "#PWR", 0, -2.54 if up else 2.54, True)} {prop("Value", name, 0, vy)}
      {prop("Footprint", "", 0, 0, True)} {prop("Datasheet", "", 0, 0, True)} {prop("Description", "Power symbol", 0, 0, True)}
      (symbol "{name}_0_1" {g})
      (symbol "{name}_1_1" (pin power_in line (at 0 0 {90 if up else 270}) (length 0) (name "{name}" (effects (font (size 1.27 1.27)) (hide yes))) (number "1" (effects (font (size 1.27 1.27)) (hide yes))))))'''

def sym_pwr_flag():
    return f'''(symbol "SleepBud:PWR_FLAG" (power) (pin_names (offset 0)) (exclude_from_sim no) (in_bom no) (on_board yes)
      {prop("Reference", "#FLG", 0, 1.905, True)} {prop("Value", "PWR_FLAG", 0, 3.81)}
      {prop("Footprint", "", 0, 0, True)} {prop("Datasheet", "", 0, 0, True)} {prop("Description", "Power flag", 0, 0, True)}
      (symbol "PWR_FLAG_0_1" (polyline (pts (xy 0 0) (xy 0 1.27) (xy -1.016 1.905) (xy 0 2.54) (xy 1.016 1.905) (xy 0 1.27)) (stroke (width 0) (type default)) (fill (type none))))
      (symbol "PWR_FLAG_1_1" (pin power_out line (at 0 0 90) (length 0) (name "pwr" (effects (font (size 1.27 1.27)) (hide yes))) (number "1" (effects (font (size 1.27 1.27)) (hide yes))))))'''

U1_LEFT = [("1", "SDA", "bidirectional", 10.16), ("2", "SCL", "input", 7.62), ("3", "LDO_EN", "input", 5.08),
           ("4", "VLDO", "passive", 0), ("5", "VLED", "power_in", -5.08)]
U1_RIGHT = [("14", "INTB", "open_collector", 10.16), ("13", "GPIO", "bidirectional", 7.62), ("12", "VREF", "passive", 2.54),
            ("11", "GND_ANA", "power_in", -2.54), ("10", "GND_DIG", "power_in", -5.08), ("9", "PGND", "power_in", -7.62)]
U1_BOTTOM = [("6", "NC", "no_connect", -5.08), ("7", "NC", "no_connect", 0), ("8", "NC", "no_connect", 5.08)]
# STM32C011F6U6 UFQFPN-20
U2_LEFT = [("2", "VDD", "power_in", 15.24), ("3", "VSS", "power_in", 12.7), ("4", "PF2-NRST", "bidirectional", 7.62),
           ("14", "PA9/USART1_TX", "output", 2.54), ("15", "PA10/USART1_RX", "input", 0),
           ("18", "PB6/I2C1_SCL", "bidirectional", -5.08), ("19", "PB7/I2C1_SDA", "bidirectional", -7.62)]
U2_RIGHT = [("1", "PC15", "bidirectional", 15.24), ("20", "PC14", "bidirectional", 12.7), ("5", "PA0", "bidirectional", 10.16),
            ("6", "PA1", "bidirectional", 7.62), ("7", "PA2", "bidirectional", 5.08), ("8", "PA3", "bidirectional", 2.54),
            ("9", "PA4", "bidirectional", 0), ("10", "PA5", "bidirectional", -2.54), ("11", "PA6", "bidirectional", -5.08),
            ("12", "PA7", "bidirectional", -7.62), ("13", "PA8", "bidirectional", -10.16), ("16", "PA13/SWDIO", "bidirectional", -12.7),
            ("17", "PA14/SWCLK/BOOT0", "bidirectional", -15.24)]
# XR33194 TSOT-23-6: DI=1, VCC=2, DE=3, Z=4, GND=5, Y=6.
# DE is high for always-enabled full-duplex operation.
U3_LEFT = [("2", "VCC", "power_in", 7.62), ("3", "DE", "input", 2.54),
           ("1", "DI", "input", -2.54), ("5", "GND", "power_in", -7.62)]
U3_RIGHT = [("6", "Y", "output", 5.08), ("4", "Z", "output", -5.08)]
# XR33183 TSOT-23-6: VCC=1, GND=2, RO=3, B=4, active-low EN=5, A=6.
# Active-low EN is grounded; R3 provides the external receive termination.
U6_LEFT = [("1", "VCC", "power_in", 7.62), ("5", "~{EN}", "input", 2.54),
           ("3", "RO", "output", -2.54), ("2", "GND", "power_in", -7.62)]
U6_RIGHT = [("6", "A", "input", 5.08), ("4", "B", "input", -5.08)]
# MCP1703A 2x3 DFN-8
LDO_LEFT = [("8", "VIN", "power_in", 2.54), ("4", "GND", "power_in", -2.54)]
LDO_RIGHT = [("1", "VOUT", "power_out", 2.54), ("9", "EP", "passive", -2.54)]
LDO_BOTTOM = [("2", "NC", "no_connect", -5.08), ("3", "NC", "no_connect", -2.54), ("5", "NC", "no_connect", 0),
              ("6", "NC", "no_connect", 2.54), ("7", "NC", "no_connect", 5.08)]

LIB = "\n".join([
    sym_ic("SleepBud:MAXM86161", "MAXM86161", "U", U1_LEFT, U1_RIGHT, U1_BOTTOM, 12.7, 12.7, "PPG optical module, single supply 3.0-5.5 V, I2C 0x62"),
    sym_ic("SleepBud:STM32C011F6U6", "STM32C011F6U6", "U", U2_LEFT, U2_RIGHT, [], 15.24, 17.78, "STM32C0 MCU, UFQFPN-20 3x3"),
    sym_ic("SleepBud:XR33194", "XR33194", "U", U3_LEFT, U3_RIGHT, [], 10.16, 10.16, "RS-422 driver, 2.5 Mbps, 3.3 V +/-5%, TSOT-23-6; DE high"),
    sym_ic("SleepBud:XR33183", "XR33183", "U", U6_LEFT, U6_RIGHT, [], 10.16, 10.16, "RS-422 receiver, 52 Mbps, enhanced fail-safe high, TSOT-23-6; active-low EN low; external R3 termination"),
    sym_ic("SleepBud:MCP1703A_DFN", "MCP1703A_DFN", "U", LDO_LEFT, LDO_RIGHT, LDO_BOTTOM, 10.16, 7.62, "LDO 16 V in, 250 mA, 2x3 DFN"),
    sym_passive("SleepBud:R", "R", "Resistor", "R_*"),
    sym_passive("SleepBud:C", "C", "Unpolarized capacitor", "C_*"),
    sym_tvs("TVS_Uni"), sym_tvs("TVS_Bi", bidirectional=True), sym_sm712(), sym_bead(),
    sym_pad(),
    sym_power("SleepBud:GND", "GND", up=False), sym_power("SleepBud:3V3", "3V3"), sym_power("SleepBud:5V_LED", "5V_LED"), sym_power("SleepBud:12V", "12V"),
    sym_pwr_flag(),
])

# ----------------------------------------------------------------- schematic items
items = []
def wire(x1, y1, x2, y2):
    items.append(f'(wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))')

def label(net, x, y, rot):
    j = "right bottom" if rot == 180 else "left bottom"
    items.append(f'(label "{net}" (at {x:.2f} {y:.2f} {rot}) (effects (font (size 1.27 1.27)) (justify {j})) (uuid "{U()}"))')

def no_connect(x, y):
    items.append(f'(no_connect (at {x:.2f} {y:.2f}) (uuid "{U()}"))')

PWR_N = [0]
def power_symbol(net, x, y):
    PWR_N[0] += 1
    ref = "#PWR%02d" % PWR_N[0]
    up = net != "GND"
    vy = y - 3.81 if up else y + 3.81
    items.append(f'''(symbol (lib_id "{POWER[net]}") (at {x:.2f} {y:.2f} 0) (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no) (uuid "{U()}")
    {prop("Reference", ref, x, y, True)} {prop("Value", net, x, vy)}
    {prop("Footprint", "", x, y, True)} {prop("Datasheet", "", x, y, True)} {prop("Description", "", x, y, True)}
    (pin "1" (uuid "{U()}"))
    (instances (project "{PROJECT}" (path "/{ROOT_UUID}" (reference "{ref}") (unit 1)))))''')

FLG_N = [0]
def pwr_flag(x, y):
    FLG_N[0] += 1
    ref = "#FLG%02d" % FLG_N[0]
    items.append(f'''(symbol (lib_id "SleepBud:PWR_FLAG") (at {x:.2f} {y:.2f} 0) (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no) (uuid "{U()}")
    {prop("Reference", ref, x, y, True)} {prop("Value", "PWR_FLAG", x, y - 3.81)}
    {prop("Footprint", "", x, y, True)} {prop("Datasheet", "", x, y, True)} {prop("Description", "", x, y, True)}
    (pin "1" (uuid "{U()}"))
    (instances (project "{PROJECT}" (path "/{ROOT_UUID}" (reference "{ref}") (unit 1)))))''')

def place_symbol(ref, libid, x, y, value, footprint, pins, ref_at, val_at):
    old = PREVIOUS_SYMBOLS.get(ref)
    old_pins = {str(p[1]): str(get(p, "uuid")[1]) for p in children(old, "pin")} if old else {}
    symbol_uuid = str(get(old, "uuid")[1]) if old else U()
    pin_uuids = " ".join(f'(pin "{n}" (uuid "{old_pins[n] if n in old_pins else U()}"))' for n in pins)
    items.append(f'''(symbol (lib_id "{libid}") (at {x:.2f} {y:.2f} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{symbol_uuid}")
    {prop("Reference", ref, *ref_at, justify="left")} {prop("Value", value, *val_at, justify="left")}
    {prop("Footprint", footprint, x, y, True)} {prop("Datasheet", D.COMPONENTS[ref].get("datasheet", ""), x, y, True)} {prop("Description", D.COMPONENTS[ref]["desc"], x, y, True)}
    {prop("MPN", D.COMPONENTS[ref].get("mpn", ""), x, y, True)}
    {prop("Manufacturer", D.COMPONENTS[ref].get("manufacturer", ""), x, y, True)}
    {pin_uuids}
    (instances (project "{PROJECT}" (path "/{ROOT_UUID}" (reference "{ref}") (unit 1)))))''')

def connect(net, x, y, dirn):
    """Attach net to pin end (x,y). dirn: 'L','R','D' = direction the stub leaves the pin."""
    L = 5.08
    if net is None:
        no_connect(x, y); return
    if dirn == "L":
        wire(x, y, x - L, y); ex, ey, rot = x - L, y, 180
    elif dirn == "R":
        wire(x, y, x + L, y); ex, ey, rot = x + L, y, 0
    else:
        wire(x, y, x, y + L); ex, ey, rot = x, y + L, 0
    if net in POWER:
        power_symbol(net, ex, ey)
    else:
        label(net, ex, ey, rot)

def fp_of(ref):
    c = D.COMPONENTS[ref]
    return f'SleepBud:{c["fp"]}' if c["lib"] == "custom" else f'{c["lib"]}:{c["fp"]}'

# ---- ICs
def place_ic(ref, libid, x, y, w, h, left, right, bottom):
    c = D.COMPONENTS[ref]
    L = 5.08
    place_symbol(ref, libid, x, y, c["value"], fp_of(ref), c["pins"].keys(), (x - w, y - h - 2.54), (x - w, y - h - 5.08))
    for num, nm, et, py in left:
        connect(c["pins"][num], x - w - L, y - py, "L")
    for num, nm, et, py in right:
        connect(c["pins"][num], x + w + L, y - py, "R")
    for num, nm, et, px in bottom:
        connect(c["pins"][num], x + px, y + h + L, "D")

place_ic("U1", "SleepBud:MAXM86161", 60.96, 63.5, 12.7, 12.7, U1_LEFT, U1_RIGHT, U1_BOTTOM)
place_ic("U2", "SleepBud:STM32C011F6U6", 152.4, 66.04, 15.24, 17.78, U2_LEFT, U2_RIGHT, [])
place_ic("U3", "SleepBud:XR33194", 233.68, 50.8, 10.16, 10.16, U3_LEFT, U3_RIGHT, [])
place_ic("U6", "SleepBud:XR33183", 233.68, 83.82, 10.16, 10.16, U6_LEFT, U6_RIGHT, [])
place_ic("U4", "SleepBud:MCP1703A_DFN", 45.72, 121.92, 10.16, 7.62, LDO_LEFT, LDO_RIGHT, LDO_BOTTOM)
place_ic("U5", "SleepBud:MCP1703A_DFN", 45.72, 152.4, 10.16, 7.62, LDO_LEFT, LDO_RIGHT, LDO_BOTTOM)

def place_passive(ref, x, y):
    c = D.COMPONENTS[ref]
    libid = "SleepBud:R" if ref.startswith("R") else "SleepBud:C"
    place_symbol(ref, libid, x, y, c["value"], fp_of(ref), ["1", "2"], (x + 2.54, y - 1.27), (x + 2.54, y + 1.27))
    top, bot = c["pins"]["1"], c["pins"]["2"]
    if top in POWER:
        power_symbol(top, x, y - 3.81)
    else:
        wire(x, y - 3.81, x, y - 8.89); label(top, x, y - 8.89, 0)
    if bot in POWER:
        power_symbol(bot, x, y + 3.81)
    else:
        wire(x, y + 3.81, x, y + 8.89); label(bot, x, y + 8.89, 0)

for i, ref in enumerate(["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "C1", "C4", "C5"]):
    place_passive(ref, 88.9 + i * 15.24, 121.92)
for i, ref in enumerate(["C6", "C7", "C11", "C12", "C13", "C14"]):
    place_passive(ref, 88.9 + i * 15.24, 152.4)

# Protection components are first instantiated here, then the reviewed A3
# layout groups them with their external pads. Values and footprints come only
# from the electrical design, including a future change in TVS polarity.
for i in range(1, 9):
    ref = f"D{i}"
    if ref not in D.COMPONENTS:
        continue
    c = D.COMPONENTS[ref]
    x, y = 25.4 + (i-1)*25.4, 175.26
    if len(c["pins"]) == 3:
        place_symbol(ref, "SleepBud:CDSOT23-SM712", x, y, c["value"], fp_of(ref), ["1", "2", "3"], (x+6.35, y-5.08), (x+6.35, y-2.54))
        connect(c["pins"]["1"], x-7.62, y-2.54, "L")
        connect(c["pins"]["2"], x-7.62, y+2.54, "L")
        connect(c["pins"]["3"], x, y+7.62, "D")
        continue
    libid = "SleepBud:TVS_Bi" if c.get("bidirectional", False) else "SleepBud:TVS_Uni"
    place_symbol(ref, libid, x, y, c["value"], fp_of(ref), ["1", "2"], (x+3.81, y-1.905), (x+3.81, y+1.905))
    wire(x, y-3.81, x, y-7.62)
    label(c["pins"]["1"], x, y-7.62, 0)
    wire(x, y+3.81, x, y+7.62)
    power_symbol(c["pins"]["2"], x, y+7.62)
if "FB1" in D.COMPONENTS:
    c = D.COMPONENTS["FB1"]
    place_symbol("FB1", "SleepBud:FerriteBead", 45.72, 190.5, c["value"], fp_of("FB1"), ["1", "2"], (40.64, 185.42), (40.64, 187.96))
    connect(c["pins"]["1"], 41.91, 190.5, "L")
    connect(c["pins"]["2"], 49.53, 190.5, "R")

for i, ref in enumerate(["J1", "J2", "J3", "J4", "J5", "J6", "J7", "J8", "J9"]):
    x, y = 165.1 + i * 15.24, 121.92
    c = D.COMPONENTS[ref]
    place_symbol(ref, "SleepBud:PAD", x, y, c["value"], fp_of(ref), ["1"], (x - 1.27, y - 3.81), (x - 1.27, y + 5.08))
    connect(c["pins"]["1"], x - 3.81, y, "L")

# ---- power flags (one per power net) + a note
for i, net in enumerate(["GND", "12V"]):
    x, y = 203.2 + i * 20.32, 160.02
    pwr_flag(x, y)
    if net == "GND":
        power_symbol(net, x, y)
    else:
        wire(x, y, x, y - 5.08); power_symbol(net, x, y - 5.08)

items.append(f'''(text "SleepBud PPG PCB v0.8 - MAXM86161 + STM32C011 + UART over RS-422, 4-layer 13.5 mm disc.\\nU3 XR33194: UART_TX -> TXP/TXN (to AMP RS-422 receiver). U6 XR33183: RXP/RXN (from AMP RS-422 driver) -> UART_RX; R3 120 ohm at the receiving end. DE high, active-low EN low; R4 holds UART_TX high during reset.\\nCable: 12V, GND, TXP, TXN, RXP, RXN + piezo coax (not on PCB). J7-J9 SWD test pads. 3V3/5V_LED planes from U5/U4 LDOs."
    (exclude_from_sim no) (at 25.4 190.5 0) (effects (font (size 1.6 1.6)) (justify left bottom)) (uuid "{U()}"))''')

sch = f'''(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0") (uuid "{ROOT_UUID}") (paper "A4")
  (title_block (title "{D.TITLE}") (rev "0.8") (company "SleepBud") (comment 1 "PPG sensor board for in-ear sleep device"))
  (lib_symbols
{LIB}
  )
{chr(10).join(items)}
  (sheet_instances (path "/" (page "1")))
)
'''
open(out, "w", encoding="utf-8").write(sch)
# Apply the reviewed A3 presentation to every future generation as well.
tidy(Path(out), Path(out))
print("written", out, "items:", len(items))
