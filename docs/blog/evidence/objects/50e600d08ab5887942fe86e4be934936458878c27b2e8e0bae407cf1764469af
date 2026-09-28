#!/usr/bin/env python3
"""Check schema and successful fetch evidence; relevance still needs review."""
import argparse
import datetime
import json
from pathlib import Path
from urllib.parse import urlsplit


def validate(run):
    assignment = json.loads((run / 'assignment.json').read_text())
    fetched = set()
    completed = False
    for line in (run / 'events.jsonl').read_text().splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue  # a running writer may have a partial final line
        p = event.get('payload', {})
        if event.get('payload_type') == 'run.terminal.completed':
            completed = True
        if event.get('payload_type') != 'tool.result' or p.get('correlation_facts', {}).get('tool_name') != 'web_fetch':
            continue
        body = p.get('text', '')
        if 'Status: 200' in body:
            for item in body.splitlines():
                if item.startswith('Source: '):
                    fetched.add(item.removeprefix('Source: ').strip())
    results = []
    for game in assignment['games']:
        gid = game['game_id']
        errors = []
        record = run / 'records' / f'{gid}.json'
        try:
            row = json.loads(record.read_text())
            if row.get('schema_version') != 1 or row.get('game_id') != gid:
                errors.append('wrong schema_version or game_id')
            if row.get('status') != 'source_verified':
                errors.append('not source_verified: ' + str(row.get('blocker', row.get('status'))))
            datetime.date.fromisoformat(row['access_date'])
            for field in ('title', 'author'):
                if not isinstance(row.get(field), str) or not row[field].strip():
                    errors.append(f'missing {field}')
            rel, walk = row['release'], row['walkthrough']
            for label, url in [('download', rel['download_url']), ('release evidence', rel['evidence_url']), ('walkthrough', walk['url'])]:
                if not isinstance(url, str) or urlsplit(url).scheme not in ('http', 'https') or not urlsplit(url).netloc:
                    errors.append(f'invalid {label} URL')
            if not rel.get('number') or not rel.get('serial'):
                errors.append('exact Z-machine release/serial missing')
            sources = {s['url']: s for s in row['fetched_sources']}
            for url in (rel['evidence_url'], walk['url']):
                if url not in sources:
                    errors.append(f'missing source entry: {url}')
                elif not sources[url].get('evidence_summary') or not sources[url].get('access_date'):
                    errors.append(f'missing evidence/date: {url}')
                if url not in fetched:
                    errors.append(f'no successful web_fetch event for {url}')
            if len(walk.get('evidence_summary', '')) < 40:
                errors.append('walkthrough body evidence missing')
            if row['compatibility']['status'] not in ('needs_smoke_check', 'documented_match'):
                errors.append('invalid compatibility claim (execution is checked separately)')
            if not row['compatibility'].get('evidence'):
                errors.append('missing compatibility evidence')
            if not all(row['reuse'].get(k) for k in ('game', 'walkthrough')):
                errors.append('missing reuse status')
            commands = row['opening_commands']
            if not isinstance(commands, list) or not 12 <= len(commands) <= 30 or any(not isinstance(c, str) or not c.strip() or '\n' in c for c in commands):
                errors.append('expected 12-30 single-line commands')
            if row.get('commands_origin') not in ('walkthrough', 'suggested'):
                errors.append('invalid commands_origin')
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
            errors.append(str(error))
        results.append({'game_id': gid, 'passed': not errors, 'errors': errors})
    report = {'run': str(run), 'model_completed': completed, 'successful_fetches': len(fetched), 'results': results,
              'passed': completed and all(r['passed'] for r in results),
              'scope': 'Schema and observed HTTP200 fetches only; Terra review and real interpreter smoke still required.'}
    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    report = validate(args.run.resolve())
    (args.run / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['passed'] else 1)
