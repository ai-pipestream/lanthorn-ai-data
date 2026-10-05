#!/usr/bin/env python3
"""Full-refresh load of the canonical export files into the lanthorn Postgres
container (lanthorn-db, localhost:5433). Files stay the source of truth; the
DB is a rebuildable query layer. Safe to run any time."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = Path.home() / '.config' / 'lanthorn' / 'pg.env'
CONTAINER = 'lanthorn-db'

EVENTS_COLS = ['event_id', 'game_id', 'session_id', 'branch_id', 'event_index',
               'timestamp_utc_ms', 'event_type', 'origin', 'case_id', 'intent',
               'command', 'response', 'expected_outcome', 'help_reason',
               'hint_text', 'hint_source', 'related_event_ids', 'review_status',
               'transport_quality', 'story_sha256']
CASES_COLS = ['annotation_event_id', 'case_id', 'game_id', 'session_id',
              'failed_event_id', 'corrected_event_id', 'failed_branch_id',
              'corrected_branch_id', 'intent', 'failed_command',
              'failure_response', 'corrected_command', 'correction_response',
              'failure_type', 'suggestion', 'intent_preserved', 'outcome_label',
              'synthetic_probe', 'evidence_available', 'review_status',
              'review_notes', 'notes', 'story_sha256']

DDL = """
CREATE TABLE IF NOT EXISTS events (
  event_id text PRIMARY KEY,
  game_id text, session_id text, branch_id text,
  event_index integer, timestamp_utc_ms timestamptz,
  event_type text, origin text, case_id text, intent text,
  command text, response text, expected_outcome text, help_reason text,
  hint_text text, hint_source text, related_event_ids text,
  review_status text, transport_quality text, story_sha256 text);
CREATE INDEX IF NOT EXISTS events_game ON events(game_id);
CREATE TABLE IF NOT EXISTS cases (
  annotation_event_id text, case_id text, game_id text, session_id text,
  failed_event_id text, corrected_event_id text, failed_branch_id text,
  corrected_branch_id text, intent text, failed_command text,
  failure_response text, corrected_command text, correction_response text,
  failure_type text, suggestion text, intent_preserved text,
  outcome_label text, synthetic_probe text, evidence_available text,
  review_status text, review_notes text, notes text, story_sha256 text);
CREATE INDEX IF NOT EXISTS cases_game ON cases(game_id);
CREATE TABLE IF NOT EXISTS judgments (
  judgment_id text PRIMARY KEY, game_id text, verdict text, reason text,
  created_at text, record jsonb);
CREATE TABLE IF NOT EXISTS case_tags (
  game_id text PRIMARY KEY, record jsonb);
CREATE TABLE IF NOT EXISTS game_files (
  game_id text, name text, content jsonb, text_content text,
  PRIMARY KEY (game_id, name));
CREATE TABLE IF NOT EXISTS import_log (
  at timestamptz DEFAULT now(), source text, rows integer);
"""


def password():
    for line in ENV.read_text().splitlines():
        if line.startswith('POSTGRES_PASSWORD='):
            return line.split('=', 1)[1].strip()
    raise SystemExit(f'no POSTGRES_PASSWORD in {ENV}')


def psql(sql, pw, stdin=None, check=True):
    return subprocess.run(['docker', 'exec', '-i', '-e', f'PGPASSWORD={pw}',
                           CONTAINER, 'psql', '-U', 'lanthorn', '-d', 'lanthorn',
                           '-v', 'ON_ERROR_STOP=1', '-c', sql],
                          input=stdin, capture_output=True, text=True, check=check)


def copy_csv(pw, table, cols, path):
    psql(f'TRUNCATE {table}', pw)
    sql = (f"\\copy {table} ({', '.join(cols)}) FROM stdin "
           f"WITH (FORMAT csv, HEADER true, NULL '')")
    psql(sql, pw, stdin=path.read_bytes().decode('utf-8'))
    n = int(psql(f'SELECT count(*) FROM {table}', pw).stdout.splitlines()[2].strip())
    psql(f"INSERT INTO import_log(source, rows) VALUES ('{path.name}', {n})", pw)
    return n


def tsv(fields):
    def esc(v):
        if v is None:
            return '\\N'
        return str(v).replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
    return '\t'.join(esc(f) for f in fields)


def build_catalog():
    """Canonical lanthorn catalog: union of every queue config's games,
    keyed by base id (kimi re-runs folded onto their muse title)."""
    import glob
    cat = {}
    for p in glob.glob(str(ROOT / 'control/*.json')) + glob.glob(str(ROOT / 'batches/*.json')):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        games = d.get('games') if isinstance(d, dict) else None
        if not isinstance(games, list):
            continue
        for g in games:
            g = {'game_id': g} if isinstance(g, str) else g
            if not isinstance(g, dict) or not g.get('game_id'):
                continue
            gid = g['game_id']
            base = gid[:-5] if gid.endswith('-kimi') else gid
            row = cat.setdefault(base, {'game_id': base, 'title': None, 'engine': None,
                                        'story_path': None, 'source_batch': None,
                                        'walkthrough_url': None, 'variants': set()})
            row['variants'].add(gid)
            for src_key, dst_key in (('title', 'title'), ('engine', 'engine'),
                                     ('story', 'story_path'), ('walkthrough_url', 'walkthrough_url')):
                if not row[dst_key] and g.get(src_key):
                    row[dst_key] = g[src_key]
            if not row['source_batch'] and g.get('story') and '/sources/' in str(g['story']):
                row['source_batch'] = str(g['story']).split('/sources/')[1].split('/')[0]
    return cat


CATALOG_DDL = """
CREATE TABLE IF NOT EXISTS catalog (
  game_id text PRIMARY KEY, title text, engine text, story_path text,
  source_batch text, walkthrough_url text, variants jsonb);
CREATE TABLE IF NOT EXISTS fleet_state (
  game_id text PRIMARY KEY, cli text, state text, host text);
DROP VIEW IF EXISTS game_progress;
CREATE VIEW game_progress AS
SELECT c.game_id, c.title, c.engine, c.source_batch, c.variants,
       COALESCE(e.sessions, 0) AS sessions, COALESCE(e.events, 0) AS events,
       COALESCE(ca.cases, 0) AS cases, e.last_event_at, e.story_sha256,
       f.fleet_states, j.verdicts, j.judgments
FROM catalog c
LEFT JOIN (SELECT replace(game_id, '-kimi', '') AS g,
                  count(DISTINCT session_id) AS sessions, count(*) AS events,
                  max(timestamp_utc_ms) AS last_event_at,
                  string_agg(DISTINCT story_sha256, ',') AS story_sha256
           FROM events GROUP BY 1) e ON e.g = c.game_id
LEFT JOIN (SELECT replace(game_id, '-kimi', '') AS g, count(*) AS cases
           FROM cases GROUP BY 1) ca ON ca.g = c.game_id
LEFT JOIN (SELECT replace(game_id, '-kimi', '') AS g,
                  string_agg(game_id || ':' || COALESCE(cli, 'muse') || ':' || state, '; ') AS fleet_states
           FROM fleet_state GROUP BY 1) f ON f.g = c.game_id
LEFT JOIN (SELECT replace(game_id, '-kimi', '') AS g,
                  string_agg(DISTINCT verdict, ',') AS verdicts, count(*) AS judgments
           FROM judgments GROUP BY 1) j ON j.g = c.game_id;
DROP VIEW IF EXISTS run_summary;
CREATE VIEW run_summary AS
SELECT game_id, session_id,
       count(*) AS events,
       count(*) FILTER (WHERE event_type = 'command') AS commands,
       count(DISTINCT branch_id) AS branches,
       min(timestamp_utc_ms) AS first_event_at,
       max(timestamp_utc_ms) AS last_event_at,
       bool_or(event_type = 'ending_claim') AS ending_claimed
FROM events GROUP BY 1, 2;
"""


def main():
    pw = password()
    psql(DDL, pw)
    psql(CATALOG_DDL, pw)
    counts = {}
    counts['events'] = copy_csv(pw, 'events', EVENTS_COLS, ROOT / 'exports/events.csv')
    counts['cases'] = copy_csv(pw, 'cases', CASES_COLS, ROOT / 'exports/test-cases.csv')
    jlines = [json.loads(l) for l in (ROOT / 'reviewed/k3-judgments.jsonl').read_text().splitlines() if l.strip()]
    rows = '\n'.join(tsv([r['judgment_id'], r['game_id'], r['verdict'],
                          r.get('reason', ''), r.get('created_at', ''),
                          json.dumps(r)]) for r in jlines)
    psql('TRUNCATE judgments', pw)
    psql('\\copy judgments FROM stdin', pw, stdin=rows)
    counts['judgments'] = len(jlines)
    tags = json.loads((ROOT / 'reviewed/k3-case-tags.json').read_text())
    rows = '\n'.join(tsv([gid, json.dumps(rec)]) for gid, rec in sorted(tags.items()))
    psql('TRUNCATE case_tags', pw)
    psql('\\copy case_tags FROM stdin', pw, stdin=rows)
    counts['case_tags'] = len(tags)
    psql(f"INSERT INTO import_log(source, rows) VALUES ('k3-judgments.jsonl', {counts['judgments']})", pw)
    cat = build_catalog()
    rows = '\n'.join(tsv([c['game_id'], c['title'] or '', c['engine'] or '',
                          c['story_path'] or '', c['source_batch'] or '',
                          c['walkthrough_url'] or '',
                          json.dumps(sorted(c['variants']))]) for c in cat.values())
    psql('TRUNCATE catalog', pw)
    psql('\\copy catalog FROM stdin', pw, stdin=rows)
    counts['catalog'] = len(cat)
    fa = json.loads((ROOT / 'control/fleet/assignments.json').read_text())
    rows = '\n'.join(tsv([gid, str(v.get('cli') or ''), v['state'], str(v.get('host') or '')])
                     for gid, v in sorted(fa.items()))
    psql('TRUNCATE fleet_state', pw)
    psql('\\copy fleet_state FROM stdin', pw, stdin=rows)
    counts['fleet_state'] = len(fa)
    gf_rows = []
    for d in sorted((ROOT / 'play').iterdir()):
        if not d.is_dir():
            continue
        for name in ('manifest.json', 'latest.json', 'ending-claim.json'):
            p = d / name
            if p.exists():
                try:
                    gf_rows.append(tsv([d.name, name, p.read_text(), None]))
                except Exception:
                    pass
        for name in ('progress.md', 'collection-notes.md'):
            p = d / name
            if p.exists():
                gf_rows.append(tsv([d.name, name, None, p.read_text()]))
    psql('TRUNCATE game_files', pw)
    if gf_rows:
        psql('\\copy game_files FROM stdin', pw, stdin='\n'.join(gf_rows))
    counts['game_files'] = len(gf_rows)
    print(json.dumps(counts))


if __name__ == '__main__':
    sys.exit(main())
