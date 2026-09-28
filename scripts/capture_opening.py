#!/usr/bin/env python3
"""Capture a short Z-machine opening via the existing plain CLI, one input at a time.
Only the supplied bytes are source evidence. No model-generated game text.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
from pathlib import Path
import selectors
import subprocess
import time
import uuid


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_prompt(proc, selector, extra_prompts=(), timeout=10):
    output = bytearray()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        ready = selector.select(0.15)
        if ready:
            data = os.read(proc.stdout.fileno(), 65536)
            if not data:
                return bytes(output), 'exited'
            output.extend(data)
        elif output.rstrip().endswith((b'>', *(p.encode() for p in extra_prompts))):
            return bytes(output), 'prompt'
        elif proc.poll() is not None:
            return bytes(output), 'exited'
    return bytes(output), 'timeout_or_nonstandard_prompt'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('record', type=Path)
    p.add_argument('story', type=Path)
    p.add_argument('--binary', type=Path, default=Path('/work/reference-code/lanthorn/target.noindex/debug/zvm-cli'))
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    record = json.loads(args.record.read_text())
    for text in record['opening_commands']:
        parts = text.casefold().replace('.', ' ').split()
        if (not text.strip() and not (text == ' ' and record.get('allow_space_input'))) or '\n' in text or '\r' in text or '/' in text or '\\' in text or any(word in ('save', 'restore', 'restart', 'quit', 'script', 'unscript') for word in parts):
            raise SystemExit(f'Needs manual capture plan for host/file/session command: {text!r}')
    args.out.mkdir(parents=True, exist_ok=False)
    session = f"{record['game_id']}-{uuid.uuid4().hex[:12]}"
    command = [str(args.binary.resolve()), '--plain', '--sound', 'off', str(args.story.resolve())]
    env = dict(os.environ, TERM='dumb')
    with (args.out / 'stderr.txt').open('wb') as stderr:
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr, cwd=args.out, env=env)
        selector = selectors.DefaultSelector()
        selector.register(proc.stdout, selectors.EVENT_READ)
        pieces = []
        rows = []
        status = 'not_started'
        try:
            for turn, input_text in enumerate([None] + record['opening_commands']):
                if input_text is not None:
                    proc.stdin.write((input_text + '\n').encode())
                    proc.stdin.flush()
                data, status = read_prompt(proc, selector, record.get("prompt_suffixes", []))
                offset = sum(len(b) for b in pieces)
                pieces.append(data)
                rows.append({'id': f'{session}:p{turn:03}', 'game_id': record['game_id'],
                             'session_id': session, 'branch_id': 'main', 'input_index': turn,
                             'command': input_text, 'text': data.decode('utf-8', errors='strict'),
                             'raw_start': offset, 'raw_end': offset + len(data), 'read_status': status})
                if status != 'prompt':
                    break
        finally:
            proc.stdin.close()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
            tail = proc.stdout.read()
            selector.close()
        raw = b''.join(pieces) + tail
        (args.out / 'stdout.raw').write_bytes(raw)
        (args.out / 'passages.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
        observed = re.search(r'Release\s+(\d+)\s*/\s*Serial(?: number)?\s+(\d+)', raw.decode('utf-8'), re.IGNORECASE)
        observed_release = {'number': observed[1], 'serial': observed[2]} if observed else None
        release_matches = bool(observed_release and all(str(record['release'][k]) == observed_release[k] for k in ('number', 'serial')))
        manifest = {'observed_release': observed_release, 'release_matches_source': release_matches, 'game_id': record['game_id'], 'session_id': session,
                    'access_time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    'source_record': str(args.record.resolve()), 'source_record_sha256': sha(args.record),
                    'story_path': str(args.story.resolve()), 'story_sha256': sha(args.story),
                    'interpreter': str(args.binary.resolve()), 'interpreter_sha256': sha(args.binary),
                    'argv': command, 'stdout_sha256': hashlib.sha256(raw).hexdigest(),
                    'requested_commands': len(record['opening_commands']), 'captured_commands': len(rows) - 1,
                    'last_read_status': status, 'exit_code': proc.returncode,
                    'release_banner': rows[0]['text'],
                    'review_status': 'unreviewed', 'compatibility_scope': 'Input/output capture of opening only. A returned prompt proves input delivery, not successful puzzle traversal or full walkthrough compatibility.',
                    'input_index_note': 'Input order, not the game engine turn counter.'}
        (args.out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        print(json.dumps({k: manifest[k] for k in ('game_id', 'captured_commands', 'requested_commands', 'last_read_status', 'exit_code')}, indent=2))
        if not release_matches or status != 'prompt' or len(rows)-1 != len(record['opening_commands']):
            raise SystemExit(1)

if __name__ == '__main__':
    main()
