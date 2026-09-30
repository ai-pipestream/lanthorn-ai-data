#!/usr/bin/env python3
"""Central interpreters and remote Muse mailboxes; no uncertain input replay."""
import base64
from concurrent.futures import ThreadPoolExecutor
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
from play_broker import ROOT, now, write_json
from maintain_workers import inventory, processes, input_state
CONTROL = ROOT / 'control/fleet'
CIRCUIT = CONTROL / 'circuit.json'
LAUNCH_LOG = CONTROL / 'launch-log.jsonl'

def digest(data): return hashlib.sha256(data).hexdigest()

RECOVERY_BUDGET = 3        # auto-recoveries per game per 24h
RECOVERY_WINDOW = 86400
RECOVERABLE = ('Remote worker exited or failed to start',
               'broker missing at grant', 'missing/duplicate broker')
STALL_RUN_BUDGET = 6       # worker runs without checkpoint advance -> park for judgment

def newest_checkpoint(gid, exclude=()):
    # Checkpoint names embed the event index (auto-<session>-<index>) or a branch
    # label, so the newest NAME only changes when the game actually advanced;
    # the broker's periodic re-save of an unchanged index rewrites the same file.
    sdir = ROOT / 'play' / gid / 'saves'
    best, best_m = None, -1
    skip = {n + '.sav.qzl' for n in exclude}
    for q in sdir.glob('*/*.qzl'):
        if q.name in skip: continue
        try: m = q.stat().st_mtime
        except OSError: continue
        if m > best_m: best, best_m = q.name, m
    return best[:-len('.sav.qzl')] if best else None

def stall_check(gid, a):
    w = a.get('worker') or {}
    run = w.get('run')
    marker = newest_checkpoint(gid)
    st = dict(a.get('stall') or {})
    if marker and st.get('marker') != marker:
        st = {'marker': marker, 'runs': 0, 'last_run': run}
    elif run and run != st.get('last_run') and a['state'] == 'running':
        st['runs'] = st.get('runs', 0) + 1
        st['last_run'] = run
    a['stall'] = st
    if st.get('runs', 0) >= STALL_RUN_BUDGET and a['state'] == 'running':
        a.update(state='attention',
                 error=f"stalled: {st['runs']} worker runs without checkpoint advance; needs judgment")

def remote_handoff(gid, host):
    # Clear the remote session fence so the next sync re-mirrors fresh, and reset
    # a dead remote worker state (pending_requests/finished never auto-start) —
    # post-recovery progress.md documents the cancelled requests, so absent is safe.
    script = (f'cd "$HOME/lanthorn-muse/play/{gid}" 2>/dev/null && rm -f .bridge-state.json'
              f' && mv -f manifest.json manifest.json.pre-recovery; '
              f'python3 -c "\n'
              f'import json, os\n'
              f'from pathlib import Path\n'
              f'p = Path.home()/\\"lanthorn-muse/state/{gid}.json\\"\n'
              f's = json.loads(p.read_text()) if p.exists() else None\n'
              f'dead = s is not None and not any(os.path.exists(f\\"/proc/{{s.get(k) or 0}}\\") for k in (\\"pid\\", \\"muse_pid\\"))\n'
              f'p.rename(p.with_name(p.name + \\".pre-recovery\\")) if dead else None\n'
              f'"')
    try:
        subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ForwardAgent=no', '-o', 'ConnectTimeout=8',
            host, script], capture_output=True, timeout=30)
    except subprocess.TimeoutExpired: pass

def auto_recover(gid, a):
    # Checkpoint recovery for infra deaths (worker exit / broker expiry) on muse
    # queue games. Never for cli=None originals, never over unresolved output,
    # never past the per-day budget — those stay parked for supervised review.
    base = ROOT / 'play' / gid
    err = a.get('error') or ''
    if a['state'] != 'attention' or a.get('cli') != 'muse': return
    if not any(err.startswith(p) for p in RECOVERABLE): return
    if (base / 'ending-claim.json').exists() or not (base / 'manifest.json').exists(): return
    checkpoint = newest_checkpoint(gid, exclude=a.get('bad_checkpoints', ()))
    if not checkpoint: return
    now_ts = time.time()
    if a.get('recovery_in_progress') and now_ts - a['recovery_in_progress'] < 900: return
    _, live_brokers = inventory(processes())
    if live_brokers.get(gid):
        # A broker is already alive for this game (e.g. a just-finished recovery):
        # never spawn a second one (recovery.lock would collide and burn budget).
        # Adopt the manifest session if it moved, then return to ready.
        m = json.loads((base / 'manifest.json').read_text())
        if m.get('session_id') and m['session_id'] != a.get('session_id'):
            remote_handoff(gid, a['host'])
            a.update(session_id=m['session_id'], sent={})
            a.pop('sent_host', None)
        a.update(state='ready', error=None)
        a.pop('worker', None)
        return
    tries = [t for t in a.get('auto_recoveries', []) if now_ts - t < RECOVERY_WINDOW]
    if len(tries) >= RECOVERY_BUDGET:
        a.update(error='auto-recovery budget exhausted (3/24h); supervised review required',
                 auto_recoveries=tries)
        return
    manifest = json.loads((base / 'manifest.json').read_text())
    entry = {k: v for k, v in manifest.items() if k not in
             ('session_id', 'started_at', 'recovery', 'broker_guards', 'story_sha256', 'dataset_purpose')}
    entry['recovery_checkpoint'] = checkpoint
    entry['recovery_reason'] = f'auto-recovery by fleet manager: {err[:120]}'
    cfg_path = CONTROL / f'recovery-{gid}.json'
    write_json(cfg_path, {'games': [entry]})
    a['auto_recoveries'] = tries + [now_ts]
    a['recovery_in_progress'] = now_ts
    with (ROOT / 'runs' / f'fleet-broker-{gid}.log').open('ab') as out:
        subprocess.Popen(['python3', 'scripts/recover_broker.py', str(cfg_path), '--hours', '24'],
             cwd=ROOT, stdin=subprocess.DEVNULL, stdout=out, stderr=out, start_new_session=True)
    prev = manifest.get('session_id')
    deadline = time.monotonic() + 90
    new_session = None
    while time.monotonic() < deadline:
        try:
            r = json.loads((base / 'recovery.json').read_text())
            m = json.loads((base / 'manifest.json').read_text())
            if r.get('session_id') != prev and m.get('session_id') == r.get('session_id'):
                new_session = r['session_id']; break
        except (OSError, ValueError): pass
        time.sleep(1)
    a.pop('recovery_in_progress', None)
    if not new_session:
        # A failed recovery can leave latest.json stamped with the aborted session
        # while manifest.json keeps the old one (mixed-session mirror wedge). Patch
        # latest.json back to the manifest session so mirroring stays consistent.
        try:
            lp = base / 'latest.json'
            latest = json.loads(lp.read_text())
            if latest.get('session_id') != a.get('session_id'):
                latest['session_id'] = a['session_id']
                write_json(lp, latest)
        except (OSError, ValueError): pass
        a['bad_checkpoints'] = list(a.get('bad_checkpoints', ())) + [checkpoint]
        a['error'] = 'auto-recovery spawned but restore did not confirm; supervised review required'
        return
    remote_handoff(gid, a['host'])
    a.update(session_id=new_session, state='ready', error=None, sent={})
    for k in ('worker', 'sent_host'): a.pop(k, None)
def assignments():
    p = CONTROL / 'assignments.json'
    return json.loads(p.read_text()) if p.exists() else {}

def circuit_state():
    try: return json.loads(CIRCUIT.read_text())
    except (OSError, ValueError): return {}

def circuit_open():
    return circuit_state().get('open_until', 0) > time.time()

def circuit_update(records):
    # Systemic-failure breaker: several recent launches failing fast means launching
    # more games just burns brokers — hold new launches for 30 min, then re-probe.
    # Quota pauses are excluded: those park and resume via their own backoff.
    if not LAUNCH_LOG.exists(): return
    cutoff = time.time() - 900
    recent = []
    for line in LAUNCH_LOG.read_text().splitlines()[-60:]:
        try: e = json.loads(line)
        except ValueError: continue
        if isinstance(e.get('at'), (int, float)) and e['at'] >= cutoff: recent.append(e)
    failed = [e for e in recent
              if (r := records.get(e.get('gid'), {})).get('state') == 'attention'
              and (r.get('worker') or {}).get('state') != 'quota_pause']
    if len(failed) >= 3:
        write_json(CIRCUIT, {'open_until': time.time() + 1800,
                             'reason': f"{len(failed)} launches failed within 15 min"})

def rpc(host, payload, cli='muse'):
    script = 'fleet_host_kimi.py' if cli == 'kimi' else 'fleet_host.py'
    result = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ForwardAgent=no',
        '-o', 'ConnectTimeout=8', host, f'python3 "$HOME/lanthorn-muse/{script}"'],
        input=json.dumps(payload), capture_output=True, text=True, timeout=25)
    if result.returncode: raise RuntimeError(f'SSH RPC exit {result.returncode}: {result.stderr[-500:]}')
    return json.loads(result.stdout)

def accept_request(base, name, data, session_id=None):
    if not re.fullmatch(r'[A-Za-z0-9_-]+\.json', name): raise ValueError('invalid request name')
    if len(data) > 1048576: raise ValueError('oversized request')
    value = json.loads(data)
    if not isinstance(value, dict) or not isinstance(value.get('action'), str): raise ValueError('invalid request')
    if value['action'] == 'restart':
        manifest = json.loads((base / 'manifest.json').read_text())
        if manifest.get('broker_guards', {}).get('restart_timeout') != 1:
            raise ValueError('Remote restart held for older broker; supervised recovery required')
        history = [json.loads(line) for line in (base / 'events.jsonl').read_text().splitlines()]
        if input_state(history) == 'no_output_timeout':
            raise ValueError('Unresolved input; await_output only, restart held')
    original = data
    if session_id is not None:
        manifest = json.loads((base / 'manifest.json').read_text())
        if manifest['session_id'] != session_id:
            raise ValueError('stale request session; no input sent')
        if value.get('_fleet_session_id', session_id) != session_id:
            raise ValueError('request claims another session')
        value['_fleet_session_id'] = session_id
        data = (json.dumps(value, sort_keys=True) + '\n').encode()
    dest = base / 'inbox' / name
    if dest.exists():
        if dest.read_bytes() not in (data, original): raise ValueError(f'Changed existing request {name}; held')
        return False
    tmp = dest.with_suffix('.incoming')
    with tmp.open('wb') as f:
        f.write(data); f.flush()
        import os
        os.fsync(f.fileno())
    tmp.replace(dest)
    return True

def sync_one(gid, assignment, start_ok=None):
    a = dict(assignment)
    if a['state'] == 'complete': return gid, a
    base = ROOT / 'play' / gid
    try:
        if a.get('sent_host') != a.get('host'):
            # Host (re)assignment invalidates the mirror ledger: the new host has
            # none of the files, so force a full re-mirror on this sync.
            a['sent'] = {}
        files, hashes = {}, {}
        paths = [base / n for n in ['manifest.json', 'latest.json', 'events.jsonl', 'collection-notes.md', 'ending-claim.json']]
        paths += list((base / 'responses').glob('*.json'))
        for p in paths:
            if not p.exists(): continue
            data = p.read_bytes()
            if p.name == 'events.jsonl': data = data[:data.rfind(b'\n') + 1]
            name = str(p.relative_to(base)); hashes[name] = digest(data)
            if a.get('sent', {}).get(name) != hashes[name]: files[name] = base64.b64encode(data).decode()
        if not (base / 'manifest.json').exists(): raise ValueError('central broker not initialized')
        session = json.loads((base / 'manifest.json').read_text())['session_id']
        if session != a['session_id']:
            raise ValueError('assignment/central session mismatch; explicit recovery handoff required')
        counter = CONTROL / (gid + '-revision.json')
        previous = json.loads(counter.read_text())['revision'] if counter.exists() else 0
        revision = max(time.time_ns(), previous + 1)
        write_json(counter, {'revision': revision, 'session_id': session})
        start = a['state'] == 'ready' and (start_ok is None or gid in start_ok)
        _, brokers = inventory(processes())
        completed = (base / 'ending-claim.json').exists()
        live = len(brokers.get(gid, []))
        if not completed and live != 1:
            if start:
                # Granted a slot with no single live broker: never blind-spawn over
                # an existing session dir; supervised recovery decides.
                a.update(state='attention', error='broker missing at grant; supervised recovery required')
                return gid, a
            # Otherwise let the rpc resolve worker state first; the broker error
            # is recorded below so a dead broker can no longer mask a dead worker.
        if a.get('cli') == 'kimi' and a['state'] == 'attention' and (a.get('worker') or {}).get('state') == 'quota_pause':
            # Quota pause is a known-safe resume point: back off 30 min, then ask the
            # remote for a fresh worker. Not a blind restart of a sick game.
            since = a.setdefault('quota_pause_since', time.time())
            if time.time() - float(since) >= 1800 and (start_ok is None or gid in start_ok):
                start = True
        out = rpc(a['host'], {'game_id': gid, 'session_id': session, 'revision': revision,
                            'files': files, 'start': start}, a.get('cli', 'muse'))
        if out.get('session_id') != session or out.get('revision') != revision:
            raise ValueError('stale RPC response')
        if json.loads((base / 'manifest.json').read_text())['session_id'] != session:
            raise ValueError('session changed during RPC; no requests/progress imported')
        a['sent'] = hashes
        a['sent_host'] = a.get('host')
        a.pop('broker_spawn_attempts', None)
        for name, encoded in out.get('requests', {}).items(): accept_request(base, name, base64.b64decode(encoded, validate=True), session)
        if 'progress' in out:
            p = base / 'progress.md'; tmp = p.with_suffix('.bridge-tmp'); tmp.write_text(out['progress']); tmp.replace(p)
        a['worker'] = out['worker']; a['last_sync'] = now(); a.pop('error', None)
        if (a.get('worker') or {}).get('state') != 'quota_pause': a.pop('quota_pause_since', None)
        if completed and out['worker']['state'] == 'finished' and not out['worker']['alive']:
            a.update(state='complete', completed_at=now())
        elif out['worker']['alive']: a['state'] = 'running'
        elif a['state'] == 'ready' and not start:
            pass  # Queued behind a full host; stay ready until a slot grants a start.
        elif not completed and a.get('cli') is not None and (out['worker'] or {}).get('state') == 'segments_exhausted':
            # Healthy segment churn: the worker finished its 12 segments mid-game.
            # Stay/return to ready so the next slot grant starts a fresh worker.
            # (cli=None originals never auto-requeue: they await supervised recovery.)
            a.update(state='ready', error=None)
        else: a.update(state='attention', error='Remote worker exited or failed to start; no blind restart')
        stall_check(gid, a)
        history = [json.loads(l) for l in (base / 'events.jsonl').read_text().splitlines()]
        if input_state(history) == 'no_output_timeout': a['error'] = 'Unresolved output; await_output only'
        if not completed and live != 1 and a.get('error') is None:
            a['error'] = 'missing/duplicate broker; slot retained'
    except Exception as exc: a.update(error=str(exc), last_error_at=now())
    return gid, a

def launch_new(host, config, game, records, cli='muse'):
    gid = game['game_id']; base = ROOT / 'play' / gid
    if base.exists() or gid in records: raise ValueError('game already reserved')
    if digest(Path(game['story']).read_bytes()) != game['story_sha256_expected']: raise ValueError('story hash mismatch')
    source = json.loads(Path(game['source_record']).read_text())
    if digest(Path(game['walkthrough']).read_bytes()) != source['normalized_sha256']: raise ValueError('guide hash mismatch')
    records[gid] = {'host': host, 'state': 'starting', 'config': config, 'cli': cli, 'assigned_at': now()}
    write_json(CONTROL / 'assignments.json', records)
    with LAUNCH_LOG.open('a') as f: f.write(json.dumps({'gid': gid, 'host': host, 'at': time.time()}) + '\n')
    with (ROOT / 'runs' / f'fleet-broker-{gid}.log').open('ab') as out:
        child = subprocess.Popen(['python3', 'scripts/run_new_game.py', config, gid, '--hours', '24'],
             cwd=ROOT, stdin=subprocess.DEVNULL, stdout=out, stderr=out, start_new_session=True)
    records[gid]['broker_pid'] = child.pid
    deadline = time.monotonic() + 210
    while not (base / 'manifest.json').exists() and child.poll() is None and time.monotonic() < deadline: time.sleep(.5)
    if (base / 'manifest.json').exists():
        latest = json.loads((base / 'latest.json').read_text())
        (base / 'collection-notes.md').write_text(game['collection_notes'])
        write_json(base / 'remote-worker.json', {'host': host, 'mode': f'central-interpreter-remote-{cli}'})
        records[gid].update(session_id=latest['session_id'], state='ready' if latest['engine_state'] == 'awaiting_input_or_idle' else 'attention')
    else: records[gid].update(state='attention', error='broker startup failed; do not reset')
    write_json(CONTROL / 'assignments.json', records)

def tick():
    cfg = json.loads((CONTROL / 'settings.json').read_text()); records = assignments()
    if not 1 <= cfg['per_host'] <= 4 or len(set(cfg['hosts'])) != len(cfg['hosts']):
        raise ValueError('invalid fleet capacity or duplicate host')
    # Per-host start allowance: only live-worker states occupy a slot ('ready' and
    # 'attention' hold none), and each tick grants starts only up to free capacity,
    # so a bulk batch of ready games cannot overrun per_host on any host.
    live = {h: sum(a.get('host') == h and a['state'] in ('running', 'starting') for a in records.values()) for h in cfg['hosts']}
    free = {h: max(0, cfg['per_host'] - live[h]) for h in cfg['hosts']}
    start_ok, now_ts = set(), time.time()
    for gid, a in records.items():
        h = a.get('host')
        if h not in free or free[h] <= 0: continue
        if a['state'] == 'ready':
            start_ok.add(gid); free[h] -= 1
        elif (a.get('cli') == 'kimi' and a['state'] == 'attention'
              and (a.get('worker') or {}).get('state') == 'quota_pause'
              and a.get('quota_pause_since') is not None
              and now_ts - float(a['quota_pause_since']) >= 1800):
            start_ok.add(gid); free[h] -= 1
    with ThreadPoolExecutor(max_workers=8) as ex: records = dict(ex.map(lambda pair: sync_one(*pair, start_ok), list(records.items())))
    _, live_brokers = inventory(processes())
    for bgid, ba in records.items():
        if ba['state'] == 'complete':
            for bpid in live_brokers.get(bgid, []):
                try: os.kill(bpid, 15)
                except OSError: pass
    if cfg['enabled'] and not circuit_open():
        for rgid, ra in records.items(): auto_recover(rgid, ra)
    write_json(CONTROL / 'assignments.json', records)
    circuit_update(records)
    if cfg['enabled'] and not circuit_open():
        with (ROOT / 'control/scheduling.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            local = json.loads((ROOT / 'control/worker-pool.json').read_text()); queue = []
            for config in local['queue_configs']:
                for game in json.loads((ROOT / config).read_text())['games']:
                    if not (ROOT / 'play' / game['game_id']).exists() and game['game_id'] not in records: queue.append((config, game))
            for host in cfg['hosts']:
                # 'attention' assignments hold no live worker (broker aged out / worker
                # exited); they stay recoverable via supervised recovery but must not
                # block new launches. Only live states occupy a slot.
                occupied = sum(a['host'] == host and a['state'] not in ('complete', 'attention') for a in records.values())
                for _ in range(max(0, cfg['per_host'] - occupied)):
                    if not queue: break
                    config, game = queue.pop(0); launch_new(host, config, game, records, cfg.get('worker_cli', 'muse'))
    write_json(CONTROL / 'status.json', {'timestamp': now(), 'per_host': cfg['per_host'], 'hosts': cfg['hosts'],
        'circuit': circuit_state(),
        'assigned': {g: {k: v for k, v in a.items() if k != 'sent'} for g, a in records.items()}})
    # Heartbeat: durable per-tick evidence for the sustain audit (who was running,
    # who was quota-parked, whether the launch breaker was open).
    with (CONTROL / 'sustain-log.jsonl').open('a') as hb:
        hb.write(json.dumps({'ts': now(),
            'running': sorted(g for g, a in records.items() if a['state'] == 'running'),
            'quota_paused': sorted(g for g, a in records.items() if (a.get('worker') or {}).get('state') == 'quota_pause'),
            'circuit_open': circuit_open()}) + '\n')

def main():
    import os
    lock = (CONTROL / 'manager.lock').open('a'); fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    while True:
        try:
            while os.waitpid(-1, os.WNOHANG)[0]: pass
        except ChildProcessError: pass
        try: tick()
        except Exception as exc:
            with (CONTROL / 'errors.jsonl').open('a') as out: out.write(json.dumps({'timestamp': now(), 'error': repr(exc)})+'\n')
        time.sleep(5)
if __name__ == '__main__': main()
