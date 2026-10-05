#!/usr/bin/env python3
"""Per-game JSON interchange for the lanthorn DB.

  dump:  Postgres -> exports/games/<game_id>.json   (one file per catalog game)
  load:  exports/games/*.json -> Postgres           (rebuilds events/cases/judgments)

The JSON files are the stable interchange contract: future run exporters can
write them directly, and the DB can always be rebuilt from them."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pg_import import ROOT, password, psql, tsv, EVENTS_COLS, CASES_COLS

OUT = ROOT / 'exports' / 'games'


def query_json(pw, sql):
    r = subprocess.run(['docker', 'exec', '-i', '-e', f'PGPASSWORD={pw}',
                        'lanthorn-db', 'psql', '-U', 'lanthorn', '-d', 'lanthorn',
                        '-v', 'ON_ERROR_STOP=1', '-tA', '-c', sql],
                       capture_output=True, text=True, check=True)
    text = r.stdout.strip()
    try:
        return json.loads(text) if text else []
    except json.JSONDecodeError:
        raise SystemExit(f'bad JSON from query (rc ok, {len(text)} chars): '
                         f'{text[:200]!r}')


def query_pairs(pw, sql):
    """Two-column (key, json) query -> dict. One row per line; the JSON half
    never contains literal newlines, and the key never contains '|'."""
    r = subprocess.run(['docker', 'exec', '-i', '-e', f'PGPASSWORD={pw}',
                        'lanthorn-db', 'psql', '-U', 'lanthorn', '-d', 'lanthorn',
                        '-v', 'ON_ERROR_STOP=1', '-tA', '-c', sql],
                       capture_output=True, text=True, check=True)
    out = {}
    for line in r.stdout.splitlines():
        if not line:
            continue
        key, _, payload = line.partition('|')
        out[key] = json.loads(payload) if payload else []
    return out


def dump():
    pw = password()
    OUT.mkdir(parents=True, exist_ok=True)
    events = query_pairs(pw,
        "SELECT replace(game_id,'-kimi','') AS g, json_agg(row_to_json(events) ORDER BY event_index) AS rows "
        "FROM events GROUP BY 1")
    cases = query_pairs(pw,
        "SELECT replace(game_id,'-kimi','') AS g, json_agg(row_to_json(cases)) AS rows "
        "FROM cases GROUP BY 1")
    judgments = query_pairs(pw,
        "SELECT replace(game_id,'-kimi','') AS g, json_agg(record ORDER BY judgment_id) AS rows "
        "FROM judgments GROUP BY 1")
    catalog = {}
    for row in query_json(pw, "SELECT json_agg(row_to_json(catalog)) FROM catalog"):
        catalog[row['game_id']] = row
    fleet = {}
    for row in query_json(pw, "SELECT json_agg(row_to_json(fleet_state)) FROM fleet_state"):
        fleet.setdefault(row['game_id'].removesuffix('-kimi'), []).append(row)
    files = query_pairs(pw,
        "SELECT replace(game_id,'-kimi',''), json_agg(json_build_object('game_id', game_id, 'name', name, 'content', content, 'text', text_content)) "
        "FROM game_files GROUP BY 1")
    n = 0
    for gid in sorted(catalog):
        doc = dict(catalog[gid])
        doc['fleet_states'] = fleet.get(gid, [])
        doc['files'] = files.get(gid, [])
        doc['events'] = events.get(gid, [])
        doc['cases'] = cases.get(gid, [])
        doc['judgments'] = judgments.get(gid, [])
        (OUT / f'{gid}.json').write_text(json.dumps(doc, indent=1) + '\n')
        n += 1
    print(json.dumps({'games_dumped': n, 'dir': str(OUT)}))


def load():
    pw = password()
    docs = [json.loads(p.read_text()) for p in sorted(OUT.glob('*.json'))]
    if not docs:
        raise SystemExit(f'no game JSON in {OUT}')
    erows, crows, jrows = [], [], []
    seen_j = set()
    for d in docs:
        for e in d.get('events', []):
            erows.append(tsv([e.get(c) or '' for c in EVENTS_COLS]))
        for c in d.get('cases', []):
            crows.append(tsv([c.get(k) or '' for k in CASES_COLS]))
        for j in d.get('judgments', []):
            if j['judgment_id'] in seen_j:
                continue
            seen_j.add(j['judgment_id'])
            jrows.append(tsv([j['judgment_id'], j['game_id'], j['verdict'],
                              j.get('reason', ''), j.get('created_at', ''), json.dumps(j)]))
    for table, rows in (('events', erows), ('cases', crows), ('judgments', jrows)):
        psql(f'TRUNCATE {table}', pw)
        if rows:
            psql(f'\\copy {table} FROM stdin', pw, stdin='\n'.join(rows))
    print(json.dumps({'games_loaded': len(docs), 'events': len(erows),
                      'cases': len(crows), 'judgments': len(jrows)}))


if __name__ == '__main__':
    {'dump': dump, 'load': load}[sys.argv[1]]()
