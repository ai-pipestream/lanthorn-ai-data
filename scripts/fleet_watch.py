#!/usr/bin/env python3
"""Exit when the fleet needs coordinator attention; else time out quietly.

Exit reasons printed on stdout (one line):
  JUDGE <gid>...   - completed+claimed runs lacking a judgment record
  PAUSE <gid>...   - any worker entered quota_pause
  DROP             - fewer than 3 running while ready games remain
  TIMEOUT          - nothing needed attention within the window
"""
import json
import subprocess
import sys
import time

WINDOW = int(sys.argv[1]) if len(sys.argv) > 1 else 600
ASSIGN = 'control/fleet/assignments.json'


def judged():
    return {json.loads(l)['game_id'] for l in open('reviewed/k3-judgments.jsonl')}


def check():
    records = json.load(open(ASSIGN))
    j = judged()
    kimi = {g: a for g, a in records.items() if a.get('cli') == 'kimi'}
    need_judge = sorted(g for g, a in kimi.items()
                        if a['state'] == 'complete' and g not in j)
    if need_judge:
        return 'JUDGE ' + ' '.join(need_judge)
    paused = sorted(g for g, a in kimi.items()
                    if (a.get('worker') or {}).get('state') == 'quota_pause'
                    and a['state'] != 'complete')
    if paused:
        return 'PAUSE ' + ' '.join(paused)
    running = sum(a['state'] == 'running' for a in kimi.values())
    waiting = sum(a['state'] == 'ready' for a in kimi.values())
    # Per-host view: a host with zero running workers while a ready game is
    # assigned TO THAT HOST is a stall. (An idle host whose games all finished
    # while other hosts hold the ready queue is normal.)
    per_host = {}
    for g, a in kimi.items():
        h = a.get('host')
        d = per_host.setdefault(h, [0, 0])
        if a['state'] == 'running': d[0] += 1
        if a['state'] == 'ready': d[1] += 1
    stalled = [h for h, (rn, rd) in per_host.items() if rn == 0 and rd > 0]
    if stalled:
        return f'DROP stalled-hosts={stalled} running={running} ready={waiting}'
    return None


deadline = time.monotonic() + WINDOW
while True:
    reason = check()
    if reason:
        print(reason)
        sys.exit(0)
    if time.monotonic() >= deadline:
        print('TIMEOUT')
        sys.exit(0)
    time.sleep(30)
