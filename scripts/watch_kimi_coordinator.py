#!/usr/bin/env python3
"""Bounded singleton proposal loop. Parent review only; never executes decisions."""
import argparse
import base64
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from kimi_coordinator_pilot import (ROOT, MAX_RUN_SECONDS, collect, encode, loads,
                                    require, sha, utcnow, validate_decision, write_json)

CALL_BUDGET = MAX_RUN_SECONDS + 30


# Ignore only observation mechanics. Unknown/new fields remain significant.
VOLATILE = {'snapshot_id', 'captured_at', 'capture_finished_at', 'pool_observed_at',
            'fleet_observed_at', 'timestamp', 'last_sync', 'log_mtime', 'revision',
            '_fleet_revision', 'created_at', 'started_at', 'finished_at', 'assigned_at',
            'completed_at', 'at'}
SET_FIELDS = {'queued', 'pending_requests', 'held_slots', 'active_game_ids_local',
              'active_game_ids_remote', 'owned_remote_game_ids', 'owned_local_game_ids',
              'retained_slot_game_ids', 'local_pool_attention'}


def canonical(value, field=''):
    if isinstance(value, dict):
        return {key: canonical(item, key) for key, item in sorted(value.items())
                if key not in VOLATILE and not (field == 'provider_quota_hold' and key == 'receipt_sha256')}
    if isinstance(value, list):
        items = [canonical(item) for item in value]
        if field == 'games':
            return sorted(items, key=lambda item: item['game_id'])
        if field in SET_FIELDS:
            return sorted({json.dumps(item, sort_keys=True): item for item in items}.values(),
                          key=lambda item: json.dumps(item, sort_keys=True))
        return items
    return value


def semantic_digest(snapshot, inputs, root):
    # Snapshot covers all selected raw evidence and state. Retain full progress and
    # manifests, not just the model's progress tail, plus exact journal prefix pins.
    names = ['control/worker-pool.json', 'control/fleet/settings.json']
    for game in snapshot['games']:
        names += ['play/' + game['game_id'] + '/' + filename for filename in
                  ('manifest.json', 'progress.md', 'events.jsonl', 'stdout.raw')]
    context = {}
    for name in names:
        record = inputs.get(str(root / name))
        require(record is not None, 'missing captured comparison input: ' + name)
        if 'bytes_base64' in record:
            content = record['bytes_base64']
            raw = base64.b64decode(content, validate=True) if content is not None else None
            require((sha(raw) if raw is not None else None) == record['sha256'], 'captured comparison digest mismatch')
            context[name] = loads(raw) if raw is not None and name.endswith('.json') else (raw.decode() if raw is not None else None)
        else:
            # Prefix digests are conservative: any new event/raw bytes cause a call.
            context[name] = {key: record[key] for key in ('sha256', 'captured_byte_count')}
    return sha(encode(canonical({'snapshot': snapshot, 'complete_inputs': context})))


def last_validated(root):
    for run in sorted((root / 'control/kimi-pilot').glob('[0-9]*Z'), reverse=True):
        if not (run / 'run.json').is_file():
            continue
        receipt = loads((run / 'run.json').read_bytes())
        if receipt.get('exit_code') != 0 or receipt.get('provider_exit_code') != 0:
            continue
        validation = loads((run / 'validation.json').read_bytes())
        require(validation.get('valid') is True and validation.get('status') == 'validated_proposal_only'
                and validation.get('actions_executed') == [], 'invalid last successful validation receipt')
        raw = (run / 'snapshot.json').read_bytes()
        require(sha(raw) == receipt['snapshot_sha256'], 'last successful snapshot digest mismatch')
        snapshot = loads(raw)
        decision_bytes = (run / 'decision.json').read_bytes()
        # Revalidate as historical evidence at its original finish time, never now.
        validate_decision(decision_bytes.decode(), snapshot,
                          dt.datetime.fromisoformat(receipt['finished_at']))
        inputs = (run / 'captured-inputs.json').read_bytes()
        require(sha(inputs) == receipt['inputs_sha256'], 'last successful input digest mismatch')
        return dict(run=str(run), snapshot=snapshot, inputs=loads(inputs),
                    decision_sha256=sha(decision_bytes), snapshot_sha256=sha(raw))
    return None


def quota_preflight(root=ROOT, collector=collect, now=utcnow, baseline_loader=last_validated):
    snapshot, captured = collector(fleet_mode=True, root=root)  # Always run fresh fail-closed checks.
    checked_at = now()
    quota = snapshot.get('provider_quota_hold', {})
    result = dict(skip_provider=False, checked_at=checked_at.isoformat(),
                  fresh_capture_snapshot_id=snapshot['snapshot_id'], decision_is_fresh=False,
                  provider_calls=0, reason='outside active pre-reset quota hold')
    if not (quota.get('active') is True and quota.get('local_enabled') is False
            and quota.get('remote_enabled') is False):
        return result
    reset = dt.datetime.fromisoformat(quota['reset_at'].replace('Z', '+00:00'))
    require(reset.tzinfo is not None, 'quota reset needs timezone')
    if checked_at >= reset:
        return result
    prior = baseline_loader(root)
    if prior is None:
        result['reason'] = 'no last validated success'
        return result
    current_digest = semantic_digest(snapshot, captured.copies(), root)
    previous_digest = semantic_digest(prior['snapshot'], prior['inputs'], root)
    result.update(semantic_sha256=current_digest, baseline_semantic_sha256=previous_digest,
                  baseline_run=prior['run'], baseline_snapshot_id=prior['snapshot']['snapshot_id'],
                  baseline_snapshot_sha256=prior['snapshot_sha256'],
                  baseline_decision_sha256=prior['decision_sha256'], quota_reset_at=quota['reset_at'])
    result['skip_provider'] = current_digest == previous_digest
    result['reason'] = 'unchanged pre-reset quota hold; historical decision reference only' if result['skip_provider'] else 'semantic fleet state changed'
    return result


def preserve_previous_status(root):
    directory = root / 'control/kimi-pilot'
    preserved = {}
    archive = directory / 'watcher-history' / utcnow().strftime('%Y%m%dT%H%M%S.%fZ')
    for name in ('watcher-status.json', 'latest-status.json'):
        path = directory / name
        if path.exists():
            data = path.read_bytes()
            archive.mkdir(parents=True, exist_ok=True)
            (archive / name).write_bytes(data)
            preserved[name] = dict(path=str(archive / name), sha256=sha(data))
    return preserved


def invoke_pilot(root):
    # Only our own process group may be terminated on timeout. No worker/game signals.
    command = [sys.executable, '-B', str(root / 'scripts/kimi_coordinator_pilot.py'), '--fleet']
    with subprocess.Popen(command, cwd=root, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, start_new_session=True) as child:
        try:
            stdout, stderr = child.communicate(timeout=CALL_BUDGET)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.communicate()
            return 124, None, 'pilot invocation exceeded bounded timeout'
    if child.returncode:
        return child.returncode, None, (stderr or stdout)[-2000:]
    try:
        result = loads(stdout)
        run = Path(result['run'])
        if run.parent != root / 'control/kimi-pilot' or result['exit_code'] != 0:
            raise ValueError('invalid child run receipt')
        status = loads((run / 'run.json').read_bytes())
        validation = loads((run / 'validation.json').read_bytes())
        if (status['exit_code'] != 0 or status['provider_exit_code'] != 0 or
                validation['valid'] is not True or validation['status'] != 'validated_proposal_only' or
                validation['actions_executed'] != [] or not (run / 'decision.json').is_file()):
            raise ValueError('child run did not produce a validated proposal')
        return 0, str(run), None
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return 3, None, str(exc)


def run_loop(root=ROOT, duration=10800, interval=300, invoke=invoke_pilot,
             clock=time.monotonic, sleep=time.sleep, emit=write_json,
             preflight=quota_preflight, preserve=preserve_previous_status):
    if not (CALL_BUDGET + 3 <= duration <= 10800 and interval >= 300):
        raise ValueError(f'duration must be {CALL_BUDGET + 3}..10800 seconds; interval at least 300 seconds')
    started = clock()
    status = dict(started_at=utcnow().isoformat(), duration_seconds=duration,
                  interval_seconds=interval, calls_completed=0, provider_calls=0, cycles_checked=0, skipped_calls=0, status='running',
                  prior_status_archive=preserve(root),
                  parent_review_required=True, actions_executed=[])
    path = root / 'control/kimi-pilot/watcher-status.json'
    emit(path, status)
    try:
        while clock() + CALL_BUDGET + 3 <= started + duration:
            status.update(last_started_at=utcnow().isoformat())
            emit(path, status)
            check = preflight(root)
            status.update(preflight=check, cycles_checked=status['cycles_checked'] + 1)
            # Preflight consumes budget too. Never start a call without its full bound.
            if clock() + CALL_BUDGET + 3 > started + duration:
                break
            if check['skip_provider']:
                status.update(status='unchanged_quota_hold_historical_reference',
                              skipped_calls=status['skipped_calls'] + 1, decision_is_fresh=False,
                              last_finished_at=utcnow().isoformat())
                emit(path, status)
                emit(root / 'control/kimi-pilot/latest-status.json', status)
            else:
                status['status'] = 'calling_provider'
                status['provider_calls'] += 1
                emit(path, status)
                code, run, error = invoke(root)
                status.update(last_exit_code=code, last_run=run, error=error,
                              last_finished_at=utcnow().isoformat())
                if code:
                    status['status'] = 'stopped_failure_no_retry'
                    emit(path, status)
                    emit(root / 'control/kimi-pilot/latest-status.json', status)
                    return code
                status['calls_completed'] += 1
                status['status'] = 'validated_proposal_only'
                emit(path, status)
            remaining = started + duration - clock() - CALL_BUDGET - 3
            if remaining < interval:
                break
            sleep(interval)  # completion-to-next-start; no overlapping calls, no catch-up bursts
        status['status'] = 'completed_duration'
        emit(path, status)
        return 0
    except (OSError, ValueError, KeyError, TypeError, KeyboardInterrupt) as exc:
        status.update(status='stopped_failure_no_retry', error=str(exc), last_exit_code=3)
        emit(path, status)
        emit(root / 'control/kimi-pilot/latest-status.json', status)
        return 3


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--duration-seconds', type=int, default=10800)
    parser.add_argument('--interval-seconds', type=int, default=300)
    args = parser.parse_args()
    directory = ROOT / 'control/kimi-pilot'
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'watcher.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('Kimi watcher already owns singleton lock', file=sys.stderr)
            return 73
        return run_loop(duration=args.duration_seconds, interval=args.interval_seconds)


if __name__ == '__main__':
    sys.exit(main())
