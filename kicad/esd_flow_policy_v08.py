"""Check that debug-pad copper paths pass through their TVS signal landings.

Uses native KiCad connectivity, without additional geometry libraries. Each
check loads a scratch board and removes only the TVS signal-pad object from
memory, leaving every trace, via and zone intact. A remaining path to the MCU
is a bypass. This is a routing topology check, not a diode/transient simulation.
The saved board is never modified.
"""

import argparse
import hashlib
import json
from pathlib import Path

import pcbnew as k


# D8 remains on B.Cu, so its J9-to-D8 entry path may contain signal vias.
FLOW_RULES = (
    ('/SWDIO', 'J7.1', 'D6.1', 'U2.16', True),
    ('/SWCLK', 'J8.1', 'D7.1', 'U2.17', True),
    ('/NRST', 'J9.1', 'D8.1', 'U2.4', False),
)


def _uid(item):
    return item.m_Uuid.AsString()


def _cluster(board, source, target):
    if not board.BuildConnectivity():
        raise RuntimeError('KiCad could not build the copper connectivity index')
    # GetConnectedItems is the whole connected cluster; GetConnectedPads and
    # GetConnectedTracks return only immediate contacts and are insufficient.
    items = list(board.GetConnectivity().GetConnectedItems(source))
    ids = {_uid(item) for item in items}
    vias = sorted(_uid(item) for item in items
                  if item.GetClass() == 'PCB_VIA' and item.GetNetname() == source.GetNetname())
    return {
        'source_found': _uid(source) in ids,
        'source_reaches_IC': _uid(target) in ids,
        'source_reaches_vias': vias,
        'source_via_count': len(vias),
        'connected_item_count': len(ids),
    }


def check_esd_flow(board_path):
    """Return a read-only report with typed errors for the saved PCB file."""
    path = Path(board_path).resolve()
    errors = []
    checks = {}
    scratch_boards = []
    detached_pads = []

    def error(code, message, tvs=None):
        errors.append({'code': code, 'message': message, 'TVS_signal_pad': tvs})

    if not path.is_file():
        error('ESD_BOARD_MISSING', f'ESD flow check requires a saved PCB: {path}')
        return {'ok': False, 'checked_paths': 0, 'required_paths': len(FLOW_RULES),
                'error_count': len(errors), 'checks': checks, 'errors': errors}

    board_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    try:
        for net, source_name, tvs_name, target_name, forbid_entry_vias in FLOW_RULES:
            board = k.LoadBoard(str(path))
            if board is None or not hasattr(board, 'GetFootprints'):
                raise RuntimeError('KiCad could not load the scratch board')
            scratch_boards.append(board)
            pads = {}
            for footprint in board.GetFootprints():
                for pad in footprint.Pads():
                    name = f'{footprint.GetReference()}.{pad.GetNumber()}'
                    pads.setdefault(name, []).append((footprint, pad))

            invalid = False
            for name in (source_name, tvs_name, target_name):
                matches = pads.get(name, [])
                if len(matches) != 1:
                    error('ESD_PAD_COUNT', f'{name}: expected one pad, found {len(matches)}', tvs_name)
                    invalid = True
                elif matches[0][1].GetNetname() != net:
                    error('ESD_PAD_NET', f'{name}: expected {net}, got {matches[0][1].GetNetname()}', tvs_name)
                    invalid = True
            if invalid:
                continue

            source = pads[source_name][0][1]
            target = pads[target_name][0][1]
            footprint, signal_pad = pads[tvs_name][0]
            normal = _cluster(board, source, target)
            # Keep native boards AND removed pads alive through all checks.
            # Early destruction of a removed PAD can invalidate KiCad SWIG
            # wrappers on subsequent board loads. Restore ownership in finally.
            footprint.Remove(signal_pad)
            signal_pad.thisown = False
            detached_pads.append((footprint, signal_pad))
            omitted = _cluster(board, source, target)

            landing_required = normal['source_reaches_IC'] and not omitted['source_reaches_IC']
            no_entry_vias = not omitted['source_reaches_vias']
            checks[tvs_name] = {
                'net': net, 'source': source_name, 'target': target_name,
                'normal': normal,
                'without_TVS_signal_pad_copper': omitted,
                'TVS_landing_is_required_for_IC_path': landing_required,
                'no_via_before_TVS': no_entry_vias,
                'no_via_before_TVS_required': forbid_entry_vias,
                'entry_via_policy': 'none' if forbid_entry_vias else 'allowed: D8 is on B.Cu',
            }
            if not normal['source_reaches_IC']:
                error('ESD_PATH_DISCONNECTED', f'{source_name} does not reach {target_name}', tvs_name)
            if omitted['source_reaches_IC']:
                error('ESD_TVS_PAD_BYPASS', f'{source_name} reaches {target_name} without {tvs_name} copper', tvs_name)
            if forbid_entry_vias and not no_entry_vias:
                error('ESD_VIA_BEFORE_TVS', f'{source_name} reaches {omitted["source_via_count"]} signal via(s) before {tvs_name}', tvs_name)
    except (RuntimeError, AttributeError, TypeError) as exc:
        error('ESD_CONNECTIVITY_CHECK_FAILED', str(exc))
    finally:
        # This changes only scratch boards and returns ownership to their
        # footprints before local native wrappers can be destroyed.
        for footprint, pad in detached_pads:
            footprint.Add(pad)

    if hashlib.sha256(path.read_bytes()).hexdigest() != board_hash:
        error('ESD_BOARD_CHANGED', 'PCB changed while the ESD flow check was running')
    return {
        'ok': not errors,
        'board_sha256': board_hash,
        'checked_paths': len(checks),
        'required_paths': len(FLOW_RULES),
        'error_count': len(errors),
        'checks': checks,
        'errors': errors,
        'method': 'Native copper connectivity with only the TVS signal-pad object omitted on scratch boards; no transient ESD simulation.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('board', type=Path)
    parser.add_argument('--json', dest='report', type=Path)
    args = parser.parse_args()
    result = check_esd_flow(args.board)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'ESD flow: {"PASS" if result["ok"] else "FAIL"}; {result["checked_paths"]} paths')
    for item in result['errors']:
        print(f'ERROR [{item["code"]}]: {item["message"]}')
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
