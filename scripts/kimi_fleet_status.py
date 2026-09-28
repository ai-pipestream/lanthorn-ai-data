#!/usr/bin/env python3
"""One-shot kimi fleet status: workers, event counts, claims, queue depth."""
import json
from pathlib import Path

ROOT = Path('/work/experiments/lanthorn-recall-training')

def main():
    recs = json.loads((ROOT / 'control/fleet/assignments.json').read_text())
    judged = set()
    jpath = ROOT / 'reviewed/k3-judgments.jsonl'
    if jpath.exists():
        judged = {json.loads(l)['game_id'] for l in jpath.read_text().splitlines()}
    for gid, a in sorted(recs.items()):
        if not gid.endswith('-kimi'):
            continue
        w = a.get('worker', {})
        n = sum(1 for _ in (ROOT / 'play' / gid / 'events.jsonl').open())
        claim = (ROOT / 'play' / gid / 'ending-claim.json').exists()
        flags = []
        if claim and gid not in judged:
            flags.append('NEEDS-JUDGMENT')
        if a.get('error'):
            flags.append(a['error'][:40])
        print(f"{gid:38s} {a.get('state'):9s} w={w.get('state','-'):18s} ev={n:4d} "
              f"claim={claim} {' '.join(flags)}")
    q = json.loads((ROOT / 'control/kimi-pilot-queue.json').read_text())
    pending = [g['game_id'] for g in q['games'] if g['game_id'] not in recs]
    print('queue pending:', len(pending), pending[:8])
    cfg = json.loads((ROOT / 'control/fleet/settings.json').read_text())
    print('settings:', cfg)

if __name__ == '__main__':
    main()
