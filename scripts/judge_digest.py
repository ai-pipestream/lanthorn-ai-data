#!/usr/bin/env python3
"""Build a bounded judgment digest for one or more play/<gid> runs.

Prints (and saves to control/judge/digests/<gid>.txt): completion criterion,
ending claim + evidence events, final events, prefilter summary. The K3 judge
reads this and renders the verdict; digests stay under ~4k chars per game.

Usage: judge_digest.py <gid> [gid ...]
"""
import json
from pathlib import Path
import sys

ROOT = Path('/work/experiments/lanthorn-recall-training')
OUT = ROOT / 'control/judge/digests'


def digest(gid):
    base = ROOT / 'play' / gid
    lines = [f"=== {gid} ==="]
    m = json.loads((base / 'manifest.json').read_text())
    lines.append("CRITERION: " + m.get('completion', '')[:350])
    events = [json.loads(l) for l in (base / 'events.jsonl').read_text().splitlines()]
    by_id = {e['event_id']: e for e in events}
    claim_path = base / 'ending-claim.json'
    if claim_path.exists():
        claim = json.loads(claim_path.read_text())
        md = claim.get('metadata', {})
        lines.append(f"CLAIM: {str(claim.get('notes') or md.get('notes'))[:250]}")
        lines.append(f"QUOTE: {str(claim.get('ending_quote') or md.get('ending_quote'))[:200]}")
        for eid in md.get('evidence_event_ids', [])[:3]:
            e = by_id.get(eid)
            if e:
                lines.append(f"EV {eid.split(':')[-1]} cmd={e.get('command')!r}: {(e.get('response') or '')[:400]}")
            else:
                lines.append(f"EV {eid}: NOT FOUND")
    else:
        lines.append("CLAIM: none")
    resp_events = [e for e in events if e.get('event_type') == 'command' and e.get('response')]
    for e in resp_events[-2:]:
        lines.append(f"FINAL cmd={e.get('command')!r}: {(e.get('response') or '')[:300]}")
    pf_path = ROOT / 'control/judge/prefilter' / (gid + '.json')
    if pf_path.exists():
        pf = json.loads(pf_path.read_text())
        lines.append(f"PF: hf={pf['hard_fail']} warn={pf.get('warnings', [])} "
                     f"ev={pf['metrics']['events']} cmd={pf['metrics']['commands']} "
                     f"cases={pf['metrics']['case_ids']} ckpt={pf['metrics']['checkpoints']}")
    text = '\n'.join(lines) + '\n'
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / (gid + '.txt')).write_text(text)
    return text


if __name__ == '__main__':
    for gid in sys.argv[1:]:
        print(digest(gid))
