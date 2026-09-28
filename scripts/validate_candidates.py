#!/usr/bin/env python3
"""Reject mechanically invalid candidates without deciding semantic relevance."""
import argparse
import hashlib
import json
from pathlib import Path


def check(rows, passages, manifest, raw, splits, run_id):
    errors = []
    by_id = {p['id']: p for p in passages}
    if len(by_id) != len(passages):
        errors.append('duplicate passage IDs')
    if hashlib.sha256(raw).hexdigest() != manifest['stdout_sha256']:
        errors.append('raw transcript digest differs from manifest')
    for passage in passages:
        if raw[passage['raw_start']:passage['raw_end']].decode('utf-8') != passage['text']:
            errors.append(f"altered transcript text: {passage['id']}")
    seen, queries = set(), set()
    for row in rows:
        rid = row.get('id', '<missing>')
        def fail(reason):
            errors.append(f'{rid}: {reason}')
        if rid in seen:
            fail('duplicate ID')
        seen.add(rid)
        query = row.get('query', '').strip().casefold()
        if not query or query in queries:
            fail('missing or duplicate query')
        queries.add(query)
        for key in ('game_id', 'session_id'):
            if row.get(key) != manifest[key]:
                fail(f'wrong {key}')
        if row.get('split') != splits['assignments'][manifest['game_id']]:
            fail('wrong game-family split')
        if row.get('review_status') != 'unreviewed':
            fail('generator cannot approve candidates')
        if row.get('generation_run_id') != run_id:
            fail('wrong generation run')
        if row.get('source_ids') != [manifest['session_id']]:
            fail('wrong source IDs')
        if not row.get('release') or not row.get('review_notes'):
            fail('missing release or rationale')
        positives = row.get('positive_passage_ids', [])
        negatives = row.get('hard_negative_passage_ids', [])
        if not isinstance(positives, list) or not positives or not isinstance(negatives, list):
            fail('missing positives or invalid reference list')
            continue
        if set(positives) & set(negatives):
            fail('positive/negative overlap')
        # The native embedding input is observed response text, without commands.
        normalize = lambda text: ' '.join(text.replace('>', ' ').split()).casefold()
        positive_texts = {normalize(by_id[pid]['text']) for pid in positives if pid in by_id}
        for pid in negatives:
            if pid in by_id and normalize(by_id[pid]['text']) in positive_texts:
                fail(f'identical response text has opposite labels: {pid}')
        cutoff = row.get('query_after_input_index')
        if not isinstance(cutoff, int) or cutoff < 0 or cutoff > manifest['captured_commands']:
            fail('invalid query cutoff')
            continue
        for pid in positives + negatives:
            passage = by_id.get(pid)
            if passage is None:
                fail(f'unknown passage {pid}')
            elif passage['branch_id'] != row.get('branch_id') or passage['session_id'] != row.get('session_id'):
                fail(f'cross-branch/session reference {pid}')
            elif passage['input_index'] > cutoff:
                fail(f'future passage {pid}')
    return {'passed': not errors, 'candidate_count': len(rows), 'errors': errors,
            'scope': 'Mechanical provenance and leakage checks only. Relevance and negative labels need independent review.'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    parser.add_argument('transcript', type=Path)
    args = parser.parse_args()
    rows = [json.loads(s) for s in (args.run/'candidates.jsonl').read_text().splitlines() if s.strip()]
    passages = [json.loads(s) for s in (args.transcript/'passages.jsonl').read_text().splitlines()]
    manifest = json.loads((args.transcript/'manifest.json').read_text())
    splits = json.loads((Path(__file__).resolve().parent.parent/'batches/splits.json').read_text())
    result = check(rows, passages, manifest, (args.transcript/'stdout.raw').read_bytes(), splits, args.run.name)
    (args.run/'validation.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
