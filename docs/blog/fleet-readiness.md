# Raspberry Pi fleet readiness

Inspected 2026-09-25 around05:49UTC. User proposed3-4Muse workers per box. Start with3 per ready host, then measure a real game pilot before4. Local active Muse RSS observed214-474MiB; no remote sustained game capacity measured yet. Meta inference is remote; Pis host the agent client and file tools; the implemented rollout keeps interpreters on the central host.

- cm5ai1, pi500p, pi5ai1, pi5ai2p.local: ARM64,16GB, Muse1.4.0; successful actual Meta READY response.
- cm5v1, cm5v2: ARM64,16GB, Muse1.4.0; explicit missing Meta credentials. Run muse login on each.
- cm5v3.local: ARM64,8GB,Muse1.4.0; missing credentials. LAN resolves; not a Tailscale peer here.
- pi5v2: ARM64,8GB,Muse1.4.0; first request timed out; a second bounded request returned READY successfully.
- pi5v4: ARM64,4GB; Muse absent from PATH and ~/.local/bin and no match in usual install roots. Start at2 if later provisioned.
- pi5v3: Tailscale reports offline; SSH timed out and mDNS did not resolve despite supplied Connect listing showing online.

First-seen cm5v3.local and pi5ai2p.local SSH keys were accepted with accept-new; no changed host keys bypassed. No credentials copied between machines. Readiness requests disabled shell, web and filesystem writes. Probe receipt control/fleet/auth-probe-20260925.json.

Existing10-game local pool stays authoritative. No remote game workers or distributed collection service have been deployed yet. Distributed runner needs host leases, unique game assignment, ARM interpreter binaries, centralized raw/event ingestion and review, and per-host concurrency caps. Source/version/hash and interrupted-session recovery rules remain in force. Authentication smoke checks are not training or model evaluation.

## 2026-09-25T05:59:25.181248+00:00 - User completed CM5 logins

cm5v1, cm5v2 and cm5v3.local each passed an actual Meta READY request after user login. Historical missing-credentials diagnoses above are superseded. Eight authenticated hosts total. Proposed3perhost means24remote workers, but no distributed game runners have been deployed and local pool remains10.

## 2026-09-25T06:14:05.234546+00:00 - Pi collection rollout

User explicitly authorized Pi collection. Pilot Frozen on cm5ai1 executed actual checkpoint and game requests through the SSH mailbox: control/fleet/pilot-and-ending-raw-verification-20260925T0612.json pins startup/save/rejection raw spans. Both failed conversation phrasings remain unreviewed, not accepted repairs. The eight authenticated hosts are now configured for three Muse workers each, in addition to ten local workers: target34. Live counts must be read from control/fleet/status.json and verified against host processes and recent interpreter events; configuration alone is not evidence of34 healthy sessions.

The Pis run Muse1.4.0 with Meta, shell/web disabled, using scripts/fleet_host.py. Interpreters, walkthroughs, raw bytes, checkpoints and event journals remain central. scripts/maintain_fleet.py mirrors allowed input/output files via SSH without forwarding credentials. Full walkthroughs are not copied to Pi workspaces; small excerpts remain broker help events. No ARM interpreter build was needed. Remote Muse traces remain under each host ~/lanthorn-muse/runs; central raw/events are authoritative.

A durable reservation precedes each broker launch, and control/scheduling.lock coordinates local and remote queue claims. Hosts enforce three supervisors; duplicate start requests are idempotent. Missing connections retain reservations, and failed/uncertain workers require supervised diagnosis. Seven fleet tests and five existing pool tests passed before expansion. Independent fleet audit was requested and remains pending at this journal time. Script deployment digests: control/fleet/deployment-20260925T0613.json.

pi5v4 remains unprovisioned for Muse; pi5v3 remains unreachable. They contribute no slots. Batches A/B add24 source-checked candidates; conservative family groupings and guide-version gaps are preserved in control/fleet/batch-ab-parent-validation.json and sources/fleet-batch-*/. No training, model evaluation, blog or dataset publication.

## 2026-09-25T06:16:43.465166+00:00 - 34 concurrent clients observed

control/fleet/rollout-verification-20260925T0614.json records three actual Muse processes per each of eight Pi hosts (24), with expected game workspaces and at least three real command events for every remote game. All checked central raw spans match their event text and SHA256. Local live process inventory separately confirmed10 workers, no attention conditions. Total34 is an observed concurrency snapshot, not a permanent guarantee or completed-game count. Existing19/10-game limits are superseded by the explicit Pi authorization. The heartbeat now manages both schedulers, reservations, remote failures and queue preparation. Two source-checked successors remain queued and batchC8 is in preparation.


08:49UTC Sep25: target34, actual33 clients plus held PythosMask startup slot. Central Glulx is not yet qualified by this run: opening MORE e3/e4 silent timeouts, no checkpoint, preserved for read-only source diagnosis. No replacement key or reset authorized by evidence. Glulx empty request maps to GlkReturn0xfffffffa;13 applies to Z-machine. Enemies same-session client continuation after2700s timeout verified by fresh output; receipts in experiment journal. No Pi asset transfer.


## 2026-09-25 09:50 UTC: second Meta quota hold

All 33 active Muse clients exited with API429 and a provider reset at12:41:27UTC (08:41:27EDT). Parent checked all9local and24remote failedlogs, exact hashes, remote processabsence, and central session/input/pending state. Actual Muse clients are zero; all34brokers remain alive. Both launch enabledflags are false under scheduling.lock, while both managers and mailboxsync remain active. No retries, interpreterreset, uncertaininputreplay, or quota purchase. Receipt: `control/provider-quota-hold-20260925T0950.json`; concise recovery handoff: `control/collection-supervision.md`. Pytho remains separately held. Kimi routine-supervision deployment is still being validated and must not be mistaken for Muse playback or autonomous recovery.


## 2026-09-25 10:05 UTC: expanded Kimi coordination deployed

Kimi now handles routine fleet supervision and ending triage through a singleton loop: one check every five minutes after the previous call finishes, for up to three hours. The corrected fleet call inspected 38 games while Muse was paused for quota. Its saved reply passed policy, session, reference and capacity validation after an explicit, lossless conversion of the exact held-game list to a count. Original outputs and failing receipts remain unchanged. Evidence: `control/kimi-pilot/revalidation-20260925T1004.json` and `control/kimi-pilot/deployment-20260925T1005.json`.

Watcher 763144 was running a fresh cycle at deployment. A failed call stops the loop without automatic retry. Kimi writes proposals; it has no game-command executor, autonomous recovery, ending-certification or publication authority. The first fleet reply omitted supplementary ending references and proposed verification for an unclaimed ending; the profile now explains the required formats. The CLI's resume hint is treated only as informational metadata. All 33 pure harness tests passed.

Kimi found useful evidence: Gerbil Riot had reached its finale at e664 without filing a claim. Dirac independently verified the raw escape narrative and hash. Parent then recorded an administrative finish without sending interpreter input and reconciled the fleet assignment while preventing a sync-write race. Remote provider-failure logs and state were preserved. Receipt: `control/fleet/gerbil-completion-reconciliation-20260925T1005.json`. Gerbil Riot will not resume.

There are 103 started titles and 70 independently verified historical conclusions, including the explicitly labeled Nine Points sample and Bedlam preview. This is not a claim of full content coverage. Muse has zero active clients during the quota hold; 33 unfinished interpreter slots remain, including held Pytho. After the 12:41:27 UTC reset, fresh checks and one successful canary must precede the remaining eight local and 23 remote resumptions. One vacant remote slot can then refill. Both launch flags remain disabled and both managers remain active.

The Codex heartbeat now uses a shorter operational handoff instead of repeating the full history. No total token savings have been measured. Batch N is prepared but unregistered. Export watcher 640478 remains the sole exporter, expiring around 12:34 UTC. No training, application changes or publication occurred.
