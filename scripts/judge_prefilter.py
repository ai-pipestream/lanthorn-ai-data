#!/usr/bin/env python3
"""Deterministic prefilter for the K3 judging pipeline (layer 0).

Per play/<gid>/ dir: schema validation, mechanical grounding of every response
against stdout.raw (sha256 + byte presence), loop/thrash detection, and progress
metrics. Writes control/judge/prefilter/<gid>.json. Hard-fail = auto-reject
candidate; the K3 judge never needs to spend context on those.

Usage: judge_prefilter.py [gid ...]   (default: every play/ dir with events.jsonl)
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path('/work/experiments/lanthorn-recall-training')
OUT = ROOT / 'control/judge/prefilter'
REQUIRED = ['event_id', 'timestamp', 'game_id', 'session_id', 'branch_id',
            'event_index', 'event_type']


def check_game(base):
    gid = base.name
    r = {'game_id': gid, 'hard_fail': [], 'metrics': {}, 'loops': {}}
    ev_path = base / 'events.jsonl'
    raw_path = base / 'stdout.raw'
    raw = raw_path.read_bytes().decode('utf-8', 'replace').replace('\r', '') if raw_path.exists() else ''
    if not raw_path.exists():
        r['hard_fail'].append('missing stdout.raw')
    events, bad_lines = [], 0
    for line in ev_path.read_text().splitlines():
        try:
            events.append(json.loads(line))
        except (ValueError, UnicodeError):
            bad_lines += 1
    if bad_lines:
        r['hard_fail'].append(f'{bad_lines} unparseable event lines')
    if not events:
        r['hard_fail'].append('no events')
        return r
    missing_keys = sum(1 for e in events if any(k not in e for k in REQUIRED))
    if missing_keys:
        r['hard_fail'].append(f'{missing_keys} events missing required keys')

    checked = grounded = 0
    ungrounded = []
    for e in events:
        resp = e.get('response')
        if not resp:
            continue
        checked += 1
        ok = hashlib.sha256(resp.encode()).hexdigest() == e.get('response_sha256')
        ok = ok and resp.strip()[:80] in raw
        if ok:
            grounded += 1
        elif len(ungrounded) < 5:
            ungrounded.append(e.get('event_id'))
    if checked and grounded < checked:
        r['hard_fail'].append(f'{checked - grounded}/{checked} responses failed grounding')
    r['metrics']['responses_grounded'] = f'{grounded}/{checked}'
    if ungrounded:
        r['loops']['ungrounded_samples'] = ungrounded

    cmds = [e.get('command') for e in events if e.get('event_type') == 'command' and e.get('command') is not None]
    r['metrics']['events'] = len(events)
    r['metrics']['commands'] = len(cmds)
    if not cmds:
        r['hard_fail'].append('no commands issued')
    # A repeated command is only degenerate when the response also repeats:
    # 'north' x5 with changing rooms is travel; x5 with the same rejection is thrash.
    pairs = [(e.get('command'), e.get('response_sha256')) for e in events
             if e.get('event_type') == 'command' and e.get('command') is not None]
    max_run, cur, prev = 1, 0, None
    for p in pairs:
        cur = cur + 1 if p == prev else 1
        prev = p
        max_run = max(max_run, cur)
    r['loops']['max_consecutive_identical_cmd_resp'] = max_run
    r.setdefault('warnings', [])
    if max_run >= 5:
        r['warnings'].append(f'identical command+response x{max_run} consecutively')
    if cmds:
        from collections import Counter
        top_pair, top_n = Counter(pairs).most_common(1)[0]
        r['loops']['top_cmd_resp_share'] = f'{top_n}/{len(cmds)} {top_pair[0][:40]!r}'
        if len(cmds) >= 30 and top_n / len(cmds) > 0.5:
            r['warnings'].append(f'thrash: {top_n}/{len(cmds)} identical command+response {top_pair[0][:40]!r}')

    r['metrics']['sessions'] = len({e['session_id'] for e in events if 'session_id' in e})
    r['metrics']['branches'] = len({e['branch_id'] for e in events if 'branch_id' in e})
    case_ids = sorted({e['metadata']['case_id'] for e in events
                       if isinstance(e.get('metadata'), dict) and e['metadata'].get('case_id')})
    r['metrics']['case_ids'] = len(case_ids)
    r['metrics']['case_id_list'] = case_ids[:50]
    origins = {}
    for e in events:
        o = isinstance(e.get('metadata'), dict) and e['metadata'].get('origin')
        if o:
            origins[o] = origins.get(o, 0) + 1
    r['metrics']['origins'] = origins
    ts = [e['timestamp'] for e in events if 'timestamp' in e]
    if ts:
        r['metrics']['first_event'] = min(ts)
        r['metrics']['last_event'] = max(ts)
    r['metrics']['ending_claim'] = (base / 'ending-claim.json').exists()
    saves = list((base / 'saves').rglob('*.sav.qzl')) if (base / 'saves').exists() else []
    r['metrics']['checkpoints'] = len(saves)
    return r


def main():
    gids = sys.argv[1:]
    if not gids:
        gids = sorted(p.name for p in (ROOT / 'play').iterdir()
                      if p.is_dir() and (p / 'events.jsonl').exists())
    OUT.mkdir(parents=True, exist_ok=True)
    n_fail = 0
    for gid in gids:
        r = check_game(ROOT / 'play' / gid)
        (OUT / (gid + '.json')).write_text(json.dumps(r, indent=1) + '\n')
        status = 'HARD-FAIL: ' + '; '.join(r['hard_fail']) if r['hard_fail'] else \
                 ('warn: ' + '; '.join(r.get('warnings', [])) if r.get('warnings') else 'ok')
        n_fail += bool(r['hard_fail'])
        m = r['metrics']
        print(f"{gid:45s} ev={m.get('events', 0):5d} cmd={m.get('commands', 0):5d} "
              f"cases={m.get('case_ids', 0):3d} grounded={m.get('responses_grounded', '-'):>9s} {status}")
    print(f"\n{len(gids)} games checked, {n_fail} hard-fail -> {OUT}")


if __name__ == '__main__':
    main()
