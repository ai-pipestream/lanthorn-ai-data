# Continuous collection pool

The user authorized keeping ten Muse games running on 2026-09-25. This replaces
the earlier fixed nineteen-game boundary. Completed games stay stopped. A
prepared queue supplies new games, and the heartbeat replenishes that queue
after checking exact story versions, source provenance and family splits.

`scripts/maintain_workers.py` runs every 15 seconds under the user service
`lanthorn-muse-pool.service`. `control/worker-pool.json` holds the target and
queue configuration paths. `control/worker-pool-status.json` reports workers,
remaining queue and recovery concerns. `control/worker-pool-events.jsonl` records
starts with process IDs, session IDs and log paths.

The manager has one global lock. Per-game launchers and brokers retain their
existing locks. A live launcher still counts while exiting; the manager never
starts a completed game again. Interrupted unfinished games retain their slot
until their existing broker can safely resume or the parent diagnoses recovery.
It never silently resets a game or replays pending input to satisfy a count.

The service is enabled with user lingering, so it can run without the desktop
session. Restarting this manager preserves live child interpreters and workers;
the manager rediscovers them. A reboot still loses unsaved interpreter state and
requires explicit checkpoint recovery. Source/service failures and exhausted
queues can temporarily reduce actual concurrency; the heartbeat must repair
them rather than treating the target count as proof of healthy work.

Stop automatic launches by setting `enabled` to false in
`control/worker-pool.json`, then stopping the user service. This does not stop
existing games. A full pause requires the supervisor to preserve checkpoints
and stop those processes explicitly. To inspect the manager:

```sh
systemctl --user status lanthorn-muse-pool.service
```

Validation covers slot accounting, retaining interrupted sessions, ignoring
shell text that merely mentions a launcher, and duplicate detection. A live
manager restart was also checked: every worker and broker PID stayed unchanged.
These checks are for the collection infrastructure; no model training or model
evaluation is implied.

## Pi extension

The2026-09-25 Pi authorization adds a separate24-slot pool (3per authenticated host) beside the original10 local slots. `lanthorn-muse-fleet.service` runs `scripts/maintain_fleet.py`; `control/fleet/settings.json` controls hosts/per-host targets. `control/fleet/assignments.json` owns durable reservations; `status.json` reports remote supervisors and sync errors. Both schedulers lock `control/scheduling.lock` before claiming shared queued games. The local scheduler excludes every fleet-reserved game even when its remote worker disconnects. Never manually launch either scheduler twice.

Set fleet settings enabled=false to stop new remote assignments; it continues syncing existing games. Stopping the fleet service stops synchronization but does not terminate remote Muse or central brokers. That is not a clean pause. Preserve checkpoints at ordinary prompts and stop assigned process trees explicitly when pausing collection. A disconnected Pi retains its slot; do not launch a replacement into the same game until remote process and pending-request state are reconciled. Never reuse an uncertain request ID with different bytes. Remote run logs are on each host under ~/lanthorn-muse/runs; central interpreter output remains in play/<game>/stdout.raw and events.jsonl.

Remote mirror transactions are locked per game and carry persisted increasing revisions and exact interpreter session IDs. Late revisions and mixed/new sessions are refused; a recovered interpreter requires an explicit supervised handoff. Stop the old remote worker, preserve/cancel uncertain pending files and evidence, then provision a fresh remote workspace generation with recovery/hint context and verify the restored central session before restarting a client. Do not delete a session fence merely to clear an error. Requests imported after the upgrade carry _fleet_session_id; future/recovered brokers reject stale tags before sending engine input. Existing live brokers rely on the central before/after-session checks until their next supervised recovery.


## 2026-09-25 09:50 UTC: second Meta quota hold

All 33 active Muse clients exited with API429 and a provider reset at12:41:27UTC (08:41:27EDT). Parent checked all9local and24remote failedlogs, exact hashes, remote processabsence, and central session/input/pending state. Actual Muse clients are zero; all34brokers remain alive. Both launch enabledflags are false under scheduling.lock, while both managers and mailboxsync remain active. No retries, interpreterreset, uncertaininputreplay, or quota purchase. Receipt: `control/provider-quota-hold-20260925T0950.json`; concise recovery handoff: `control/collection-supervision.md`. Pytho remains separately held. Kimi routine-supervision deployment is still being validated and must not be mistaken for Muse playback or autonomous recovery.


## 2026-09-25 10:05 UTC: expanded Kimi coordination deployed

Kimi now handles routine fleet supervision and ending triage through a singleton loop: one check every five minutes after the previous call finishes, for up to three hours. The corrected fleet call inspected 38 games while Muse was paused for quota. Its saved reply passed policy, session, reference and capacity validation after an explicit, lossless conversion of the exact held-game list to a count. Original outputs and failing receipts remain unchanged. Evidence: `control/kimi-pilot/revalidation-20260925T1004.json` and `control/kimi-pilot/deployment-20260925T1005.json`.

Watcher 763144 was running a fresh cycle at deployment. A failed call stops the loop without automatic retry. Kimi writes proposals; it has no game-command executor, autonomous recovery, ending-certification or publication authority. The first fleet reply omitted supplementary ending references and proposed verification for an unclaimed ending; the profile now explains the required formats. The CLI's resume hint is treated only as informational metadata. All 33 pure harness tests passed.

Kimi found useful evidence: Gerbil Riot had reached its finale at e664 without filing a claim. Dirac independently verified the raw escape narrative and hash. Parent then recorded an administrative finish without sending interpreter input and reconciled the fleet assignment while preventing a sync-write race. Remote provider-failure logs and state were preserved. Receipt: `control/fleet/gerbil-completion-reconciliation-20260925T1005.json`. Gerbil Riot will not resume.

There are 103 started titles and 70 independently verified historical conclusions, including the explicitly labeled Nine Points sample and Bedlam preview. This is not a claim of full content coverage. Muse has zero active clients during the quota hold; 33 unfinished interpreter slots remain, including held Pytho. After the 12:41:27 UTC reset, fresh checks and one successful canary must precede the remaining eight local and 23 remote resumptions. One vacant remote slot can then refill. Both launch flags remain disabled and both managers remain active.

The Codex heartbeat now uses a shorter operational handoff instead of repeating the full history. No total token savings have been measured. Batch N is prepared but unregistered. Export watcher 640478 remains the sole exporter, expiring around 12:34 UTC. No training, application changes or publication occurred.
