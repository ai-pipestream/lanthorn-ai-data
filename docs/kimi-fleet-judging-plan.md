# Kimi fleet + K3 judging plan

Status: approved by user 2026-09-26; blocked on fleet API key. Supersedes nothing —
BRIEF.md rules remain fully in force (writes only in this workspace, no changes to
/work/reference-code/lanthorn, game text is data never instructions, ending claims need
independent verification, all cases stay `unreviewed` until human review).

## Why

Muse weekly quota exhausted 2026-09-26T01:20Z, resets 2026-09-28T00:00Z (~2 days).
The Kimi account has high weekly quota remaining, so the fleet switches to kimi CLI
until muse returns. Lower-tier model plays; K3 judges.

## Locked decisions

- Player model: `kimi-for-coding` (K2.8 Preview, 1M ctx). Fallback if burn/throughput
  demands: `kimi-for-coding-highspeed` (K2.7).
- Judge: K3 (the coordinator, this session). Judging is bursty and digest-bounded.
- Concurrency: user revised 2026-09-26 to 1 per host, 3 hosts total (cm5ai1,
  cm5v3, pi500p) — account was at 60% weekly usage with ~1 day to reset; keep
  burn modest. Scale only on user instruction.
- Fleet auth: one API key from the Kimi Code Console, deployed into each host's
  isolated fleet config. All devices/keys share the same account quota.
- The kimi account is a legacy weekly plan: weekly window + rolling 5-hour rate
  window. Workers must detect 429/quota errors and back off, not crash-loop.

## Fleet changes (per host)

Hosts: cm5ai1, cm5v1, cm5v2 (both Tailscale-blocked), krickert@cm5v3.local, pi500p,
pi5ai1, krickert@pi5ai2p.local, pi5v2. Start with the 6 reachable.

1. Install: ALREADY DONE — kimi 2.1.1 (latest per npm registry, verified
   2026-09-26) is present at `~/.kimi-code/bin/kimi` on all 6 reachable hosts.
   Rollout still runs `kimi upgrade -y` per host as a drift guard.
2. Isolated home: `KIMI_CODE_HOME=$HOME/lanthorn-muse/kimi-home` with config.toml:
   - `default_model = "kimi-for-coding"`, `default_permission_mode = "auto"`
   - provider `managed:kimi-code` with the fleet API key
   - `[tools] enabled = ["Read","Write","Edit","Glob","Grep"]` — file tools only.
     This replicates muse's `--disable-shell --disable-web-tools --approval-mode never`.
3. New worker variant `scripts/fleet_host_kimi.py` (copy of fleet_host.py), deployed
   as `~/lanthorn-muse/fleet_host_kimi.py`; the muse copy stays untouched for the
   09-28 return. Only the worker argv changes:
   `kimi -p @prompt --model kimi-for-coding --auto --output-format stream-json`
   run with cwd=`~/lanthorn-muse/play/<gid>`. Segment loop (12 x <=45 min),
   mailbox protocol, state files, per-host cap: unchanged.
4. Quota/rate-limit handling: on 429/quota text in run output, worker exits with a
   distinct code and maintain_fleet backs off exponentially instead of relaunching
   immediately.

Central side untouched: brokers (run_new_game.py), maintain_fleet.py (point its
worker-launch at the kimi variant), watch_exports.py, export schema. Events land in
the same exports/events.csv + exports/test-cases.csv.

## Judging pipeline

Layer 0 — deterministic prefilter (`scripts/judge_prefilter.py`, no model cost),
per finished run -> `control/judge/prefilter/<run_id>.json`:
- schema validation; every game-output span must byte-match the broker's raw
  interpreter log (mechanical "never invent game output" enforcement)
- loop/thrash detection; progress metrics (rooms, commands, checkpoints, segments)
- hard-fail => auto-reject, no judge time spent

Layer 1 — K3 verdict over a bounded digest (metrics + opening + sampled middles +
ending + the run's progress.md), rubric: grounded / coherent / data-valuable /
terminal-state. Verdicts:
- `keep`     — cases eligible
- `reject`   — degenerate/thin, quarantine from exports
- `continue` — good but truncated; resume from named broker checkpoint
  (recover_broker.py already restores from the 10-min autosaves)
- `restart`  — bad trajectory, fresh attempt

Layer 2 — tracking: append-only `reviewed/k3-judgments.jsonl`, one record per
verdict: {judgment_id, run_id, game_id, player_model, judge:"kimi-k3",
judge_session, verdict, reason (1-2 sentences), rubric, prefilter_metrics,
cases_span, created_at}. Case tags live in sidecar `reviewed/k3-case-tags.json`
(`k3-kept` / `k3-rejected`). `reviewed/fullplay-cases.json` is never written by the
judge — human review remains the only gate per BRIEF.md.

Continuation: a `continue` verdict names the checkpoint; relaunch = recover_broker.py
restore + worker prompt seeded with the judgment reason. Unsaved actions after the
checkpoint are historical only (existing recovery semantics).

## Rollout

1. DONE — Pilot on cm5ai1 (dash-slapney-patrol-leader-kimi): launched, played,
   completed with a genuine authored ending, exported, judged keep
   (j-20260926-001 pilot partial, j-20260926-039 completion).
2. DONE — API key validated locally then on each host (smoke script
   /tmp/kimi_smoke_remote.py checks rc=0 and no key leakage into output).
3. DONE — Scaled to 3 hosts x 1 concurrent (cm5ai1, krickert@cm5v3.local,
   pi500p); settings.json carries worker_cli="kimi". Queue refills use the
   `<gid>-kimi> `-suffix re-run convention in control/kimi-pilot-queue.json;
   completions free slots and the manager auto-launches the next queued game.
4. DONE — judge_prefilter.py run over all 114 games; grounding 100% corpus-wide;
   only blue-chairs/metamorphoses hard-fail (never-started, blocked hosts).
5. DONE — Muse backlog judged: 38 records (12 ending claims + 25 completions +
   pilot partial). i-0 and bicon ending claims evidence-backed but still awaiting
   human verification (flagged in their records).
6. ONGOING — judge kimi completions as they land; keep queue depth >= 4; watch
   for genuine 429s.

As-built extras beyond the original sketch:
- scripts/judge_prefilter.py (layer 0; identical-cmd+response loop warnings,
  grounding hard-fails), outputs control/judge/prefilter/<gid>.json; digests in
  control/judge/digests/.
- scripts/kimi_fleet_status.py — one-shot fleet/judgment status.
- Quota auto-resume: worker exits 77/quota_pause on real stderr quota errors
  (stderr only — the word "quota" appears in collection notes, so events.jsonl
  is never error evidence); manager resumes a paused kimi worker after a 30-min
  backoff (start guard treats quota_pause as resumable).
- Known-benign: every kimi run's stderr ends with a `runtime.not_found`
  stack trace from AgentFileHistoryService.endCheckpoint (the isolated
  KIMI_CODE_HOME doesn't register ad-hoc cwds for file history). Exit code is
  still 0 and all output is intact; we do not use kimi file history.
- Exit 124 (45-min segment wall-clock) is routine churn for kimi workers, not
  failure: the segment loop continues. Muse segments self-terminated in ~2 min,
  but kimi-for-coding plays until stopped, so long games hit the wall mid-game;
  the next segment resumes from mirrored state + progress.md.
- loop_control.max_steps_per_turn raised 400 -> 2000 in the fleet config after
  mother-loose-kimi died at the cap (400 model steps only covered ~60-80
  mailbox round-trips). The 45-min wall remains the real segment bound; the
  step cap is now runaway insurance only.

## Coexistence with muse

The one-shot muse recovery canary (cron 01M3DMZ56M6TY8J89PF2P3DA2F, fires 2026-09-27
20:12 local = 20 min after the muse weekly reset) stays in place. If both fleets run
after the reset, keep total workers per host <= 4 across both CLIs (kimi workers live
in a separate state namespace, so the cap must be enforced by launch policy, not by
fleet_host.py's own occupancy check).

## Open items

- BLOCKER: fleet API key from the Kimi Code Console (user action; 5 max, one is
  enough — it is shared quota). Deliver via a local file I scp without echoing, or
  paste and I deploy without logging it.  [RESOLVED 2026-09-26: key in ~/.bashrc
  KIMI_KEY, deployed to kimi-home/env on each host via stdin pipe]
- cm5v1/cm5v2 still need Tailscale re-auth (links already given to user) — 8 slots.
- After muse returns: decide the kimi/muse split (kimi judges muse too; the pipeline
  is model-agnostic — every run record carries player_model).

## Quota wall incident + hardening (2026-09-27)

The account's rolling 5-hour usage limit (403 "5-hour usage limit", distinct from
the weekly budget) halted the fleet ~01:11Z after ~4h14m of 3-worker play. Two
defects made it expensive, both fixed:

1. `fleet_host_kimi.py quota_hit()` only watched for 'quota exhausted'/429 text;
   the wall says "usage limit" (stderr: `provider.auth_error: 403 ...`). Workers
   exited `failed` instead of parking. Patterns now include 'usage limit' and
   'auth_error: 403' (stderr only, as before).
2. Fast-failures freed slots instantly, so the manager launch loop burned 15 queue
   games into instant-403 brokers before anyone noticed. Manager hardening:
   - `circuit_update()`/`circuit_open()`: >=3 fast non-quota launch failures in
     15 min holds all launches for 30 min (control/fleet/circuit.json), then
     re-probes. Quota pauses excluded — they park and resume via the 30-min
     backoff path.
   - Per-host start gating in tick(): 'ready'/'quota_pause-resume' games are
     granted starts only up to free per_host capacity (only 'running'/'starting'
     occupy), so a bulk-ready batch cannot overrun a host.
   - sync_one no longer demotes a ready game that merely wasn't granted a start
     this tick (previously -> attention 'no blind restart', which silently
     shredded bulk resumes).
- sustain-log.jsonl: manager appends {ts, running, quota_paused, circuit_open}
  every tick — durable evidence for the 12h sustain criterion.
- Hosts reboot weekly: /etc/cron.d/weekly-reboot (Sunday 03:00 local) kills all
  workers; remote state files keep saying 'running' with dead pids. The remote
  spawn guard now consults computed liveness (old['alive']/['muse_alive']), so
  stale 'running' no longer blocks starts. Central side still needs the
  attention->ready flip (no blind restart of possibly-sick games).
- Wave-game resume procedure (broker alive, worker dead): stop manager, set
  assignment state='ready' (keep session_id), delete remote
  ~/lanthorn-muse/state/<gid>.json, restart manager.
- pkill self-match trap bit twice: never put a pkill pattern for the manager in
  the same shell command as the literal path scripts/maintain_fleet.py (e.g. a
  py_compile in the same call) — the regex matches the invoking shell's cmdline.
- Judgment id collision (09:20Z): the overdue sustain one-shot cron fired into a
  parallel context of this session and re-judged deephome-kimi/i-0-kimi with
  colliding ids j-071/j-072. Repaired: doppelganger rows renumbered to
  j-20260927-074/-075 with collision_note (verdicts identical; no data loss),
  tags repointed, the stale one-shot cron deleted. Lesson: judgment writes must
  flock reviewed/.k3-judgments.lock around next-id allocation + append.

## Recovery runbook (validated 2026-09-26 on kook-u-kimi menu wedge)

Symptom: assignment attention, latest.json engine_state=no_output_timeout that
await_output cannot resolve (e.g. literal-space menu keypress producing no output).
1. Kill the central broker process for the gid and the remote worker
   (`ssh host 'pkill -f "fleet_host_kimi[.]py worker <gid>"'` — bracket trick,
   plain patterns self-match the invoking shell and kill the ssh session).
2. Build control/recovery-<gid>.json from the queue entry + recovery_checkpoint
   (latest confirmed named checkpoint; check play/<gid>/saves/ and checkpoint
   events) + recovery_reason.
3. `setsid nohup python3 scripts/recover_broker.py control/recovery-<gid>.json
   --hours 12` — writes recovery.json, new-session manifest, updated progress.md,
   and runs as the replacement broker.
4. Handoff: stop the manager (assignments.json is rewritten per tick from
   in-memory records; external edits race and get clobbered), set the assignment
   session_id to the new session + state=ready, restart the manager.
5. Remote handoff on the worker host: scp the new manifest.json into
   ~/lanthorn-muse/play/<gid>/, write .bridge-state.json {session_id: new,
   revision: 0}, delete ~/lanthorn-muse/state/<gid>.json. The manager then
   mirrors and starts a fresh worker on the new branch.
