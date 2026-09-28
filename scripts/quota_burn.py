#!/usr/bin/env python3
"""Sum kimi usage.record tokens per hour across all fleet sessions on this host."""
import datetime
import glob
import json
import os
import time
from collections import defaultdict

tot = defaultdict(lambda: [0, 0, 0, 0, 0])
cutoff = (time.time() - 10 * 3600) * 1000
pattern = os.path.expanduser('~/lanthorn-muse/kimi-home/sessions/*/*/agents/main/wire.jsonl')
for f in glob.glob(pattern):
    for line in open(f, errors='replace'):
        if '"usage.record"' not in line[:60]:
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get('time', 0) < cutoff:
            continue
        u = r.get('usage', {})
        v = tot[int(r['time'] // 3600000)]
        v[0] += u.get('inputOther', 0) + u.get('inputCacheCreation', 0)
        v[1] += u.get('output', 0)
        v[2] += u.get('inputCacheRead', 0)
        v[3] += 1
for h in sorted(tot):
    ts = datetime.datetime.utcfromtimestamp(h * 3600).strftime('%m-%d %H:00')
    v = tot[h]
    print(f"{ts}Z  fresh_in={v[0]:>10,}  out={v[1]:>9,}  cache_read={v[2]:>12,}  turns={v[3]}")
