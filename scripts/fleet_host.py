#!/usr/bin/env python3
"""Pi-side Muse supervisor and narrowly scoped mailbox. No interpreter lives here."""
import base64
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path.home() / 'lanthorn-muse'


def valid_id(gid):
    if not re.fullmatch(r'[a-z0-9-]+', gid):
        raise ValueError('invalid game ID')
    return gid


def write(path, value):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2) + '\n')
    tmp.replace(path)


def live(pid, gid):
    try:
        args = Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
        return b'worker' in args and gid.encode() in args and any(b'fleet_host.py' in x for x in args)
    except OSError:
        return False


def state(gid):
    p = ROOT / 'state' / (gid + '.json')
    s = json.loads(p.read_text()) if p.exists() else {'state': 'absent'}
    s['alive'] = live(s.get('pid', 0), gid)
    try:
        args = Path(f"/proc/{s.get('muse_pid', 0)}/cmdline").read_bytes().split(b'\0')
        s['muse_alive'] = str(ROOT / 'play' / gid).encode() in args and any(b'muse' in a for a in args[:1])
    except OSError:
        s['muse_alive'] = False
    return s


def worker(gid):
    with (ROOT / 'state/start.lock').open('a') as start_lock:
        fcntl.flock(start_lock, fcntl.LOCK_EX)
    base = ROOT / 'play' / gid
    lock = (base / 'worker.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    state_path = ROOT / 'state' / (gid + '.json')
    for segment in range(12):
        if (base / 'ending-claim.json').exists():
            write(state_path, {'pid': os.getpid(), 'state': 'finished', 'exit': 0})
            return
        pending = [p for p in (base / 'inbox').glob('*.json') if not (base / 'responses' / p.name).exists()]
        deadline = time.monotonic() + 240
        while pending and time.monotonic() < deadline:
            time.sleep(2)
            pending = [p for p in (base / 'inbox').glob('*.json') if not (base / 'responses' / p.name).exists()]
        if pending:
            write(state_path, {'pid': os.getpid(), 'state': 'pending_requests', 'exit': 75})
            return
        if (base / 'ending-claim.json').exists():
            write(state_path, {'pid': os.getpid(), 'state': 'finished', 'exit': 0})
            return
        run = ROOT / 'runs' / f'{gid}-{time.time_ns()}'
        run.mkdir()
        prompt = (ROOT / 'fullplay.md').read_text() + f'\nGame: {gid}. Read latest.json, manifest.json, collection-notes.md and progress.md if present. Continue actual state.\nMailbox synchronization can take several seconds. Never resubmit pending requests.\n'
        (run / 'prompt.md').write_text(prompt)
        argv = [str(Path.home() / '.local/bin/muse'), 'exec', '--provider', 'meta',
                '--workspace', str(base), '--prompt-file', str(run / 'prompt.md'), '--json',
                '--max-model-steps', '400', '--max-tool-output-bytes', '262144',
                '--approval-mode', 'never', '--disable-shell', '--disable-web-tools',
                '--no-foreign-personal-context']
        with (run / 'events.jsonl').open('wb') as out, (run / 'stderr.log').open('wb') as err:
            child = subprocess.Popen(argv, stdout=out, stderr=err, stdin=subprocess.DEVNULL)
            write(state_path, {'pid': os.getpid(), 'muse_pid': child.pid, 'state': 'running',
                               'run': str(run), 'segment': segment, 'started_at': time.time()})
            try:
                code = child.wait(timeout=2700)
            except subprocess.TimeoutExpired:
                child.terminate()
                try: child.wait(timeout=10)
                except subprocess.TimeoutExpired: child.kill(); child.wait()
                code = 124
        (run / 'exit.status').write_text(str(code) + '\n')
        if code:
            write(state_path, {'pid': os.getpid(), 'state': 'failed', 'exit': code, 'run': str(run)})
            return
    write(state_path, {'pid': os.getpid(), 'state': 'segments_exhausted', 'exit': 0})


def mailbox_locked(req):
    gid = valid_id(req['game_id'])
    base = ROOT / 'play' / gid
    (base / 'inbox').mkdir(parents=True, exist_ok=True)
    (base / 'responses').mkdir(exist_ok=True)
    (ROOT / 'state').mkdir(exist_ok=True)
    (ROOT / 'runs').mkdir(exist_ok=True)
    session = req['session_id']; revision = req['revision']
    if not isinstance(session, str) or not session or not isinstance(revision, int) or revision < 1:
        raise ValueError('missing session/revision fence')
    fence_path = base / '.bridge-state.json'
    fence = json.loads(fence_path.read_text()) if fence_path.exists() else {}
    old_manifest = base / 'manifest.json'
    previous_session = fence.get('session_id')
    if previous_session is None and old_manifest.exists():
        previous_session = json.loads(old_manifest.read_text())['session_id']
    if previous_session is not None and previous_session != session:
        raise ValueError('session mismatch; explicit recovery handoff required')
    if revision <= fence.get('revision', 0):
        raise ValueError('stale or repeated mirror revision')
    for name in ('manifest.json', 'latest.json'):
        if name in req.get('files', {}):
            value = json.loads(base64.b64decode(req['files'][name], validate=True))
            if value['session_id'] != session: raise ValueError('mixed-session mirror')
    # Persist the fence before applying files. After an interrupted transaction,
    # only a higher revision may repair the mirror; a late old RPC cannot regress it.
    write(fence_path, {'session_id': session, 'revision': revision})
    for name, encoded in req.get('files', {}).items():
        allowed = name in ('latest.json', 'manifest.json', 'events.jsonl', 'collection-notes.md', 'ending-claim.json')
        allowed |= bool(re.fullmatch(r'responses/[A-Za-z0-9_-]+\.json', name))
        if not allowed: raise ValueError('invalid mirror filename')
        p = base / name
        if p.is_symlink(): raise ValueError('symlink in mailbox')
        data = base64.b64decode(encoded, validate=True)
        tmp = p.with_suffix(p.suffix + '.bridge-tmp')
        tmp.write_bytes(data); tmp.replace(p)
    if req.get('start'):
        start_lock = (ROOT / 'state/start.lock').open('a')
        fcntl.flock(start_lock, fcntl.LOCK_EX)
        old = state(gid)
        occupied = sum(s['alive'] or s['muse_alive'] for s in
                       (state(p.stem) for p in (ROOT / 'state').glob('*.json')))
        if old['state'] != 'absent' or occupied >= 4:
            # Start is idempotent; uncertain transport must never create another worker.
            pass
        else:
            with (ROOT / 'runs' / (gid + '-supervisor.log')).open('ab') as out:
                child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'worker', gid],
                                         stdin=subprocess.DEVNULL, stdout=out, stderr=out, start_new_session=True)
            write(ROOT / 'state' / (gid + '.json'), {'pid': child.pid, 'state': 'starting'})
        start_lock.close()
    requests = {}
    for p in (base / 'inbox').glob('*.json'):
        if p.is_symlink() or not re.fullmatch(r'[A-Za-z0-9_-]+\.json', p.name): continue
        if (base / 'responses' / p.name).exists(): continue
        data = p.read_bytes()
        if len(data) > 1048576: raise ValueError('oversized request')
        try: json.loads(data)
        except (ValueError, UnicodeError): continue  # An incomplete write is not a submitted request.
        requests[p.name] = base64.b64encode(data).decode()
    progress = base / 'progress.md'
    result = {'worker': state(gid), 'requests': requests, 'session_id': session, 'revision': revision}
    if progress.exists() and not progress.is_symlink():
        result['progress'] = progress.read_text()[:200000]
    s = result['worker']
    if s.get('run'):
        p = Path(s['run']) / 'events.jsonl'
        if p.exists(): result['worker']['log_mtime'] = p.stat().st_mtime
    return result


def mailbox(req):
    gid = valid_id(req['game_id'])
    base = ROOT / 'play' / gid
    base.mkdir(parents=True, exist_ok=True)
    with (base / '.bridge.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return mailbox_locked(req)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'worker':
        worker(valid_id(sys.argv[2]))
    else:
        print(json.dumps(mailbox(json.load(sys.stdin))))
