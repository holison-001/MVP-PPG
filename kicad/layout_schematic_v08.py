"""Readable A3 schematic layout; preserve existing component/pin UUIDs.

Run: python layout_schematic_v08.py [input.kicad_sch] [output.kicad_sch]
Only presentation is changed. Net membership is checked separately with KiCad.
"""
from pathlib import Path
from copy import deepcopy
from collections import defaultdict
import json
import re
import sys
import uuid
import design_v08 as D


class Quoted(str):
    pass


def parse(source):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', source)
    stack, root = [], None
    for token in tokens:
        if token == '(':
            node = []
            if stack:
                stack[-1].append(node)
            else:
                root = node
            stack.append(node)
        elif token == ')':
            stack.pop()
        else:
            if token.startswith('"'):
                token = Quoted(json.loads(token))
            stack[-1].append(token)
    assert not stack
    return root


def dump(node):
    if isinstance(node, list):
        return '(' + ' '.join(dump(v) for v in node) + ')'
    if isinstance(node, Quoted):
        return json.dumps(node, ensure_ascii=False)
    if isinstance(node, float):
        return f'{node:.4f}'.rstrip('0').rstrip('.')
    return str(node)


def children(node, key):
    return [v for v in node[1:] if isinstance(v, list) and v[0] == key]


def get(node, key):
    return next(v for v in node[1:] if isinstance(v, list) and v[0] == key)


def prop(node, name):
    return next(v for v in children(node, 'property') if v[1] == name)


def uid():
    return ['uuid', Quoted(str(uuid.uuid4()))]


def effects(size=1.27, justify=None, bold=False):
    font = ['font', ['size', size, size]]
    if bold:
        font.append(['bold', 'yes'])
    result = ['effects', font]
    if justify:
        result.append(['justify', *justify.split()])
    return result


def tidy(source, target):
    sch = parse(source.read_text(encoding='utf-8'))
    get(sch, 'paper')[1] = Quoted('A3')
    original = {str(prop(s, 'Reference')[2]): deepcopy(s) for s in children(sch, 'symbol')}
    library = get(sch, 'lib_symbols')
    libs = {str(s[1]): s for s in children(library, 'symbol')}
    power_pool = defaultdict(list)
    for ref, symbol in original.items():
        if ref.startswith('#'):
            power_pool[str(get(symbol, 'lib_id')[1])].append(symbol)
    power_templates = {name: deepcopy(pool[0]) for name, pool in power_pool.items()}
    used_refs = set(original)

    def auxiliary_symbol(libid):
        """Reuse identities where possible; grow the power-symbol pool safely."""
        if power_pool[libid]:
            return power_pool[libid].pop(0)
        symbol = deepcopy(power_templates[libid])
        prefix = '#FLG' if libid.endswith(':PWR_FLAG') else '#PWR'
        index = 1
        while f'{prefix}{index:03d}' in used_refs:
            index += 1
        ref = f'{prefix}{index:03d}'
        used_refs.add(ref)

        def renew(node):
            if node[0] == 'uuid':
                node[1] = Quoted(str(uuid.uuid4()))
            elif node[0] == 'reference':
                node[1] = Quoted(ref)
            for child in node[1:]:
                if isinstance(child, list):
                    renew(child)
        renew(symbol)
        prop(symbol, 'Reference')[2] = Quoted(ref)
        return symbol

    # Power symbols have zero-length pins: the pin names/numbers must be hidden
    # at symbol level, otherwise KiCad renders a duplicate vertical net name.
    for name in ['GND', '3V3', '5V_LED', '12V', 'PWR_FLAG']:
        lib = libs['SleepBud:' + name]
        lib[:] = [v for v in lib if not (isinstance(v, list) and v[0] in ('pin_names', 'pin_numbers'))]
        lib.extend([['pin_names', ['offset', 0], ['hide', 'yes']], ['pin_numbers', ['hide', 'yes']]])

    def reshape(name, w, h, pin_positions):
        lib = libs['SleepBud:' + name]
        for unit in children(lib, 'symbol'):
            for rect in children(unit, 'rectangle'):
                get(rect, 'start')[1:] = [-w, -h]
                get(rect, 'end')[1:] = [w, h]
            for pin in children(unit, 'pin'):
                num = str(get(pin, 'number')[1])
                get(pin, 'at')[1:] = pin_positions[num]

    u1_positions = {}
    for n, y in [('1', 20.32), ('2', 10.16), ('3', 0), ('4', -10.16), ('5', -20.32)]:
        u1_positions[n] = [-22.86, y, 0]
    for n, y in [('14', 20.32), ('13', 10.16), ('12', 0), ('11', -10.16), ('10', -17.78), ('9', -25.4)]:
        u1_positions[n] = [22.86, y, 180]
    for n, x in [('6', -7.62), ('7', 0), ('8', 7.62)]:
        u1_positions[n] = [x, -33.02, 90]
    reshape('MAXM86161', 17.78, 27.94, u1_positions)

    u2_positions = {}
    for n, y in [('2', 30.48), ('3', 22.86), ('4', 12.7), ('14', 2.54), ('15', -5.08), ('18', -17.78), ('19', -25.4)]:
        u2_positions[n] = [-35.56, y, 0]
    for i, n in enumerate(['1', '20', '5', '6', '7', '8', '9', '10', '11', '12', '13', '16', '17']):
        u2_positions[n] = [35.56, 30.48 - i * 5.08, 180]
    reshape('STM32C011F6U6', 30.48, 35.56, u2_positions)

    # Regenerate only graphical placement and wires; keep all main identities.
    sch[:] = [v for v in sch if not (isinstance(v, list) and v[0] in
             ('symbol', 'wire', 'label', 'global_label', 'junction', 'no_connect', 'text', 'polyline', 'rectangle'))]
    items = []

    def wire(x1, y1, x2, y2):
        items.append(['wire', ['pts', ['xy', x1, y1], ['xy', x2, y2]], ['stroke', ['width', 0], ['type', 'default']], uid()])

    def junction(x, y):
        items.append(['junction', ['at', x, y], ['diameter', 0], ['color', 0, 0, 0, 0], uid()])

    def label(net, x, y, left=False):
        items.append(['label', Quoted(net), ['at', x, y, 180 if left else 0],
                      effects(1.27, 'right bottom' if left else 'left bottom'), uid()])

    def text(value, x, y, size=1.27, bold=False):
        items.append(['text', Quoted(value), ['exclude_from_sim', 'no'], ['at', x, y, 0], effects(size, 'left top', bold), uid()])

    def rule(x1, y, x2):
        items.append(['polyline', ['pts', ['xy', x1, y], ['xy', x2, y]],
                      ['stroke', ['width', 0.254], ['type', 'default']], ['fill', ['type', 'none']], uid()])

    def heading(title, x, y, width):
        text(title, x, y, 1.8, True)
        rule(x, y + 4.6, x + width)

    def move(symbol, x, y, rotation=0, ref_at=None, val_at=None):
        symbol = deepcopy(symbol)
        get(symbol, 'at')[1:] = [x, y, rotation]
        for field in children(symbol, 'property'):
            get(field, 'at')[1:] = [x, y, 0]
        for name, pos in [('Reference', ref_at), ('Value', val_at)]:
            if pos is not None:
                field = prop(symbol, name)
                get(field, 'at')[1:] = [*pos, 0]
                field[:] = [v for v in field if not (isinstance(v, list) and v[0] == 'effects')]
                field.append(effects(1.27, 'left'))
        items.append(symbol)
        return symbol

    def power(net, x, y):
        symbol = auxiliary_symbol('SleepBud:' + net)
        result = move(symbol, x, y)
        field = prop(result, 'Value')
        get(field, 'at')[1:] = [x, y + (4.445 if net == 'GND' else -4.445), 0]
        field[:] = [v for v in field if not (isinstance(v, list) and v[0] == 'effects')]
        field.append(effects())

    def ic(ref, x, y):
        src = original[ref]
        lib = libs[str(get(src, 'lib_id')[1])]
        rect = next(r for u in children(lib, 'symbol') for r in children(u, 'rectangle'))
        w, h = map(float, get(rect, 'end')[1:])
        move(src, x, y, ref_at=(x-w, y-h-6.35), val_at=(x-w, y-h-3.175))
        for unit in children(lib, 'symbol'):
            for p in children(unit, 'pin'):
                num = str(get(p, 'number')[1])
                px, py, angle = map(float, get(p, 'at')[1:])
                ax, ay = x+px, y-py
                net = D.COMPONENTS[ref]['pins'][num]
                if net is None:
                    items.append(['no_connect', ['at', ax, ay], uid()])
                elif angle == 0:
                    wire(ax, ay, ax-7.62, ay)
                    label(net, ax-7.62, ay, True)
                elif angle == 180:
                    if ref in ('U3', 'U6') and num in ('4', '6') and 'R5' in original:
                        series = {('U3', '6'): 'R5', ('U3', '4'): 'R6', ('U6', '6'): 'R7', ('U6', '4'): 'R8'}[ref, num]
                        sx = 368.3
                        placed = move(original[series], sx, ay, 90,
                                      ref_at=(sx-3.81, ay-4.445), val_at=(sx+1.27, ay-4.445))
                        for field_name in ('Reference', 'Value'):
                            get(prop(placed, field_name), 'at')[3] = 90
                        wire(ax, ay, sx-3.81, ay)
                        label(net, ax+1.27, ay)
                        wire(sx+3.81, ay, sx+11.43, ay)
                        label(D.COMPONENTS[series]['pins']['2'], sx+11.43, ay)
                    else:
                        wire(ax, ay, ax+7.62, ay)
                        label(net, ax+7.62, ay)
                else:
                    raise ValueError('Unexpected connected bottom pin')

    def passive(ref, x, y):
        resistor = ref.startswith('R')
        # Rotate pull-ups 180 deg so pin 2 (3V3) faces upward, keeping pin/net IDs.
        placed = move(original[ref], x, y, 180 if resistor else 0,
                      ref_at=(x+3.81, y-1.905), val_at=(x+3.81, y+1.905))
        if resistor:
            # KiCad reverses field justification on a 180-degree symbol.
            for name in ['Reference', 'Value']:
                get(get(prop(placed, name), 'effects'), 'justify')[1:] = ['right']
        for num, dy in ([('2', -1), ('1', 1)] if resistor else [('1', -1), ('2', 1)]):
            net = D.COMPONENTS[ref]['pins'][num]
            py, ey = y + dy*3.81, y + dy*7.62
            wire(x, py, x, ey)
            if net in ['3V3', '5V_LED', '12V', 'GND']:
                power(net, x, ey)
            elif dy > 0:
                wire(x, ey, x+3.81, ey)
                label(net, x+3.81, ey)
            else:
                label(net, x, ey)

    def tvs(ref, x, y, rail_y=None):
        move(original[ref], x, y, ref_at=(x+3.81, y-1.905), val_at=(x+3.81, y+1.905))
        upper = y-7.62 if rail_y is None else rail_y
        wire(x, y-3.81, x, upper)
        if rail_y is None:
            label(D.COMPONENTS[ref]['pins']['1'], x, upper)
        else:
            junction(x, upper)
        wire(x, y+3.81, x, y+7.62)
        power(D.COMPONENTS[ref]['pins']['2'], x, y+7.62)

    def pad(ref, x, y, protection=None, drop=10.16):
        move(original[ref], x, y, ref_at=(x+3.81, y-1.905), val_at=(x+3.81, y+1.905))
        endpoint = x-(30.48 if protection else 11.43)
        wire(x-3.81, y, endpoint, y)
        label(D.COMPONENTS[ref]['pins']['1'], endpoint, y, True)
        if protection:
            assert D.COMPONENTS[ref]['pins']['1'] == D.COMPONENTS[protection]['pins']['1']
            tvs(protection, x-19.05, y+drop, rail_y=y)

    text('SleepBud | PPG sensor board', 15.24, 15.24, 3.0, True)
    text('v0.8  /  MAXM86161 + STM32C011  /  full-duplex UART over RS-422', 15.24, 22.86, 1.5)
    text('A3  |  FUNCTIONAL SCHEMATIC', 327.66, 19.05, 1.5)

    heading('01  PPG SENSOR', 15.24, 31.75, 116.84)
    heading('02  MCU + I2C PULL-UPS', 144.78, 31.75, 125.73)
    heading('03  UART / RS-422 LINK', 283.21, 31.75, 120.65)

    ic('U1', 68.58, 76.2)
    passive('C1', 30.48, 134.62)
    passive('C4', 68.58, 134.62)
    passive('C5', 101.6, 134.62)
    text('VLED bulk', 22.86, 150.495)
    text('VLDO bypass', 60.96, 150.495)
    text('VREF bypass', 93.98, 150.495)

    ic('U2', 208.28, 83.82)
    passive('C11', 158.75, 139.7)
    passive('C12', 186.69, 139.7)
    passive('R1', 222.25, 139.7)
    passive('R2', 250.19, 139.7)

    text('TX  /  earbud to controller', 285.75, 42.545)
    ic('U3', 335.28, 66.04)
    passive('C6', 289.56, 66.04)
    passive('R4', 387.35, 90.17)
    text('RX  /  controller to earbud', 285.75, 93.98)
    ic('U6', 335.28, 116.84)
    passive('C7', 289.56, 116.84)
    passive('R3', 387.35, 144.78)
    text('U3: DE = 3V3. U6: /EN = GND.', 285.75, 139.065)
    text('R3: 120/1% at the local RX cable pair.', 285.75, 144.145)
    text('Enhanced fail-safe: UART_RX high.', 285.75, 149.225)

    protected = 'FB1' in original
    if protected:
        required = {'D1', 'D6', 'D7', 'D8'}
        assert required.issubset(original), 'Protection layout requires supply and SWD TVS'
        heading('04  INPUT PROTECTION + POWER', 15.24, 165.1, 125.73)

        # The raw pad rail is visibly clamped before the series ferrite bead.
        # Existing 12V remains the filtered rail feeding C13 and U4.
        bead_x, rail_y = 66.04, 184.15
        move(original['FB1'], bead_x, rail_y,
             ref_at=(bead_x-7.62, rail_y-8.89), val_at=(bead_x-7.62, rail_y-5.08))
        wire(25.4, rail_y, bead_x-3.81, rail_y)
        label(D.COMPONENTS['FB1']['pins']['1'], 25.4, rail_y, True)
        wire(bead_x+3.81, rail_y, 88.9, rail_y)
        label(D.COMPONENTS['FB1']['pins']['2'], 88.9, rail_y)
        assert D.COMPONENTS['D1']['pins']['1'] == D.COMPONENTS['FB1']['pins']['1']
        tvs('D1', 30.48, 193.04, rail_y=rail_y)
        passive('C13', 119.38, 195.58)
        ic('U4', 81.28, 218.44)
        ic('U5', 81.28, 248.92)
        passive('C14', 123.19, 248.92)

        # A filtered-rail flag is needed because ERC does not propagate power
        # drive through a passive ferrite bead. Keep ground driven as before.
        for net, y in [('12V', 222.25), ('GND', 246.38)]:
            x = 20.32
            flag = auxiliary_symbol('SleepBud:PWR_FLAG')
            move(flag, x, y, val_at=(x-5.08, y-5.08))
            wire(x, y, x+15.24, y)
            power(net, x+15.24, y)

        heading('05  RS-422 CABLE PADS', 153.67, 165.1, 142.24)
        pad('J1', 187.96, 184.15)
        pad('J2', 264.16, 184.15)
        text('J1 raw supply -> D1 / FB1 (section 04)', 157.48, 193.04)
        for ref, x, y in [('J3', 187.96, 205.74), ('J4', 264.16, 205.74),
                          ('J5', 187.96, 226.06), ('J6', 264.16, 226.06)]:
            pad(ref, x, y)

        # Local 3V3 bypass additions use the open space below the cable pads.
        if {'C15', 'C16'}.issubset(original):
            text('Additional 3V3 bypass  /  0603 MLCC', 157.48, 234.95)
            passive('C15', 180.34, 251.46)
            passive('C16', 243.84, 251.46)

        heading('06  SWD TEST PADS + ESD', 309.88, 165.1, 93.98)
        # The reference pads occupy the open left column of this section.
        # Existing SWD protection remains on the three signal pads.
        for ref, y in [('J10', 191.77), ('J11', 217.17)]:
            if ref in original:
                pad(ref, 328.93, y)
        for ref, diode, y in [('J7', 'D6', 179.07), ('J8', 'D7', 204.47), ('J9', 'D8', 229.87)]:
            pad(ref, 377.19, y, protection=diode, drop=7.62)

        rule(15.24, 269.24, 289.56)
        text('C1: 5V_LED / U4 output bulk capacitor (section 01). D1 clamps raw 12V_IN; FB1 feeds filtered 12V.', 15.24, 273.05)
        text('Cable: 12V, GND, TXP, TXN, RXP, RXN. Piezo coax bypasses this PCB. Matching net labels are connected.', 15.24, 278.13)
        text('RS-422 bus TVS omitted; 22 ohm series retained. D1 protects supply, D6-D8 protect SWD. IEC immunity requires physical validation.', 15.24, 283.21)
    else:
        # Continue to support the original 26-part design for archived builds.
        heading('04  POWER SUPPLIES', 15.24, 165.1, 229.87)
        ic('U4', 76.2, 195.58)
        ic('U5', 187.96, 195.58)
        passive('C13', 27.94, 195.58)
        passive('C14', 232.41, 195.58)
        text('12V -> U4 -> 5V_LED -> U5 -> 3V3', 20.32, 221.615, 1.5)
        text('C1: 5V_LED bulk / U4 output capacitor (section 01).', 20.32, 228.6)
        for net, x in [('12V', 86.36), ('GND', 139.7)]:
            flag = auxiliary_symbol('SleepBud:PWR_FLAG')
            y = 246.38
            move(flag, x, y, val_at=(x-5.08, y-5.08))
            wire(x, y, x+20.32, y)
            power(net, x+20.32, y)
        text('External supply flags', 20.32, 241.3)
        heading('05  CABLE PADS', 260.35, 165.1, 68.58)
        for ref, y in [('J1', 184.15), ('J2', 194.31), ('J3', 207.01), ('J4', 217.17), ('J5', 229.87), ('J6', 240.03)]:
            pad(ref, 297.18, y)
        heading('06  SWD TEST PADS', 341.63, 165.1, 62.23)
        for ref, y in [('J7', 181.61), ('J8', 191.77), ('J9', 201.93), ('J10', 212.09), ('J11', 222.25)]:
            if ref in original:
                pad(ref, 377.19, y)
        text('J7: PA13 / SWDIO', 344.17, 235.585)
        text('J8: PA14 / SWCLK', 344.17, 240.665)
        text('J9: reset / NRST', 344.17, 245.745)
        rule(15.24, 260.35, 240.03)
        text('BOARD / INTERCONNECT NOTES', 15.24, 264.16, 1.5, True)
        text('4-layer PCB, 13.5 mm disc. U1 is the optical PPG module.', 15.24, 270.51)
        text('Cable: 12V, GND, TXP, TXN, RXP, RXN. Piezo coax bypasses this PCB.', 15.24, 275.59)
        text('Matching net labels are connected. Crosses mark intentionally unused pins.', 15.24, 280.67)

    sch.extend(items)
    target.write_bytes(('(kicad_sch\n' + '\n'.join('  '+dump(n) for n in sch[1:]) + '\n)\n').encode('utf-8'))
    # Restore the missing project-local symbol library from the embedded symbols.
    local_lib = ['kicad_symbol_lib', ['version', '20250114'], ['generator', Quoted('kicad_symbol_editor')], ['generator_version', Quoted('9.0')]]
    for s in children(library, 'symbol'):
        s = deepcopy(s)
        s[1] = Quoted(str(s[1]).split(':', 1)[-1])
        local_lib.append(s)
    target.with_name('SleepBud.kicad_sym').write_bytes((dump(local_lib)+'\n').encode('utf-8'))
    print(f'Wrote {target}; preserved {sum(not r.startswith("#") for r in original)} component identities.')


if __name__ == '__main__':
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('ppg_pcb_v08.kicad_sch')
    target = Path(sys.argv[2]) if len(sys.argv) > 2 else source
    tidy(source, target)
