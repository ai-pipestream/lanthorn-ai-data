# Experiment journal

Dates are UTC. Initial entries reconstruct earlier work from retained artifacts;
they are not notes written contemporaneously. Append subsequent findings with
their evidence instead of silently rewriting the history.

## 2026-09-24: scope and discovery

The user wanted to ease text-adventure frustrations while retaining the original
interpreter. Recall came first; command assistance became a related collection
target. Hybrid retrieval and MiniLM were discussed. Neither discussion selected
a final model or established that training would help.

We created a separate experiment workspace. Muse uses the Meta provider; Terra
independently reviews evidence. The first source pilot failed to adequately verify
walkthrough bodies. Revised prompts and validation required actual fetch receipts.

Evidence: `sources/pilot-*`, `runs/pilot-review.md`, `scripts/validate_sources.py`,
`run-sources.sh`, and retained per-run prompts and outputs in `runs/`.

## 2026-09-24: actual play and synthetic mistakes

The user clarified that the target is useful test data, not Muse's playing skill.
Workers inject labeled synthetic human-like mistakes while advancing real games.
They request small walkthrough excerpts through a logged broker action. Actual
game output supplies evidence; guide prose and model recollection cannot replace it.

The initial games were the Zork/Dungeon Inform 7 port, Hitchhiker's Guide,
Adventureland, Pirate Adventure and Lost Pig. If an alternative command works,
it stays an accepted alternative rather than becoming an invented parser failure.

Evidence: `prompts/fullplay.md`, `run-fullplay.sh`, `scripts/play_broker.py`, and
each game's `manifest.json`, `events.jsonl` and `stdout.raw` under `play/`.

## 2026-09-24: capture and review failures

A slow Zork response demonstrated that a quiet output interval did not mean the
interpreter was ready for input. Delayed text could be attributed to the following
command. The broker now checks whether the owned interpreter is waiting to read
stdin and blocks further input after an uncertain timeout. Earlier affected
examples remain quarantined. Tests of the corrected transport do not retroactively
validate old captures.

Review also caught changed-intent repairs, cross-branch state assumptions and
unsupported explanations of why a command failed. Parser acceptance differs from
achieving the intended world effect. Separate those labels instead of treating
any later success as a correction.

CSV tooling inferred dates and formulas from strings. The exporter now protects
literal text and verifies readback before emitting quoted CSV. JSON retains
original timestamp precision; CSV timestamps use milliseconds.

Evidence: `scripts/test_broker_transport.py`, `scripts/export_dataset.mjs`,
`reviewed/fullplay-cases.json` and `runs/fullplay-supervision.md`.

## 2026-09-24 23:20: host restart recovery

After the user reported a restart, we preserved history and recovered from
engine-confirmed saves with story/save hash checks. Recovery creates explicit
new sessions and branches. Uncertain pending inputs were not blindly replayed.

Evidence: `control/fullplay-host-restart-20260924T2318.json`,
`scripts/recover_broker.py`, recovery receipts in `runs/fullplay-status.json`.

## 2026-09-24: four independently verified endings

The reviewer record retains the raw spans and hashes for these receipts:

- Adventureland: `adventureland-19f4e4861c:e00939`, 13 treasures and explicit
  completion.
- Pirate Adventure: `pirate-adventure-3b0fad2d95:e00853`, both treasures and
  explicit completion.
- Lost Pig: `lost-pig-7c88b2b933:e00357`, farm-return ending, score 6/7.
- Hitchhiker's Guide: `hhgttg-7b4da6d228:e00397` and `e00398`, Magrathea arrival,
  final score 385/400 and natural engine exit.

A maximum score is not always necessary for an ending. Conversely, a high rank,
death, quit or scene transition does not establish an intended ending.

## 2026-09-25: Zork remains incomplete

The story is Zork/Dungeon 3.2B, an Inform 7 port, not commercial Zork I. The first
guide did not cover the same content. A matching source archive contained a story
binary with the same hash, providing a stronger identity check than the title.

Exploratory commands repeatedly exhausted lamp power needed later. Sending a
shorter route does not prove it ran: after advice to restore an early checkpoint,
the worker restored a later depleted one. Report observed execution separately
from instructions and resource estimates.

A parent hypothesis that an exhausted lamp could be reactivated was also wrong:
it missed a source guard and actual output contradicted it. Preserve that mistake
in the account. Source inspection and supervisor advice also need verification.
The intermediate 586-point/wraith stage is not a verified ending.

Evidence: `control/ZorkI7-source.zip`, `control/zork-port-story.ni`,
`control/zork-port-walkthrough.txt`, and the supervision record. Guidance at
`zork-i7-c569ad8028:e01394` differs from the actual restore at `e01424`/`e01425`.

## 2026-09-25 01:54: five more games

The user authorized Photopia, Shade, Suveh Nux, Secret Mission and Voodoo Castle.
Separate brokers use existing local story files and privately retained guide
sources. A new-game broker refuses an existing game directory to prevent silent
resets. Game-family split assignments were preserved before collection.

Startup checks exposed distinctions worth recording:

- Photopia is stripped-down Z-code 1.30, not Glulx 2.01.
- Shade is release 3 / 001127, matching the guide's stated release.
- Suveh Nux's selected 2007 binary reports version 1.1; its guide describes 1.0.
  The initial collection note implied a match and was subsequently corrected.
- Secret Mission's actual banner says MISSION IMPOSSIBLE by Scott Adams.
- Voodoo Castle's banner credits Alexis Adams.
- Initial SAVE commands failed in both new Scott-format games. An attempted
  checkpoint is not a recoverable save without engine confirmation.

Evidence: `control/fullplay-expansion-20260925.json`,
`sources/expansion-20260925/`, `control/expansion-launch-20260925.json`,
`batches/splits.json`, and startup receipts in `runs/fullplay-status.json`.

## 2026-09-25 02:18: blog evidence record

The user requested a durable account of acquisition, capture, testing and future
model creation. Added this journal, methodology, proposed model plan and a dated
evidence snapshot script.

The initial snapshot captured 12,475 events and a CSV with 709 cases: 433 accepted,
165 revise, 15 quarantine and 96 unreviewed. All recorded response byte spans
matched their hashes and decoded text. This verifies byte integrity, not intent
preservation or causal attribution. Collection, review and export run separately;
their timestamps may differ.

Evidence: `docs/blog/evidence/snapshots/20260925T021805.922507Z.json`.
The three current transport tests also passed in this documentation pass, in
3.925 seconds. Training and model evaluation have not started.

## 2026-09-25 02:30: three more endings; Zork continuation corrected

Parent review verified the actual raw spans and response hashes for Photopia's
nursery lights-out and final title (e00219/e00220), Shade's final desert narrative
and restart/restore/quit menu (e00347), and Suveh Nux's vault escape and master
rescue with explicit escape banner (e00269/e00270/e00271, 99%). The Photopia and
Shade guide endings were compared locally to distinguish final narrative from
earlier scene transitions or deaths. Terra's separate review was requested;
consult its dated status for the independent verdict and candidate-case review.

Evidence: `control/ending-parent-verification-20260925T0230.json`, containing exact
session event IDs, byte spans, hashes and responses. Seven games now have endings
verified by the parent against interpreter evidence. No completed game was resumed.

Zork's launcher had exhausted its twelve continuation segments and stopped cleanly
without an ending. The interpreter broker remained alive with no pending requests.
A new worker reused that broker. A dated collection note explicitly superseded
stale b88 guidance, preserving the previous notes and all checkpoints. This time
actual events e01592/e01593 acknowledge restoration of shaft-coal-in-basket-b43,
starting a new branch. The short route's eventual lamp reserve and completion
remain unverified; successful restore alone proves neither.

Evidence: `control/zork-collection-notes-before-20260925T0230.md`,
`play/zork-i7/collection-notes.md`, `runs/fullplay-zork-i7-20260925T022837Z-cS2k3t/`,
`zork-i7-c569ad8028:e01592` and `e01593`. Secret Mission and Voodoo Castle continue.

## 2026-09-25 02:35: second authorized five-game expansion

The user requested more Muse agents. Started separate real interpreters and Muse
workers for The Dreamhold, Bronze, 9:05, Violet and Slouching Towards Bedlam.
This brings the scope to fifteen games. Existing sessions were not reset.
Startup story hashes and raw-response hashes were verified before workers began.

Story files already existed in the private library. Retrieved and retained guides
with source URL, access timestamp, hashes and normalization notes. The 9:05 HTML
was limited to the AustinH walkthrough section; unrelated review/comments are not
part of its hint text. Violet uses the original competition file and author guide
from the same directory; Slouch uses the competition2003 file and archive-linked
Michael Martin solution. Dreamhold's R4 guide versus R5 story, Bronze's unspecified
guide on the R13 site versus local R11 story, and 9:05's older guide versus actual
v1.11/2012.0724 remain explicit compatibility gaps, not claims of full matching.

Bronze initially asks a yes/no question; Violet pauses for a key. Per-game notes
prevent an early SAVE from becoming a reply to the wrong kind of prompt. Slouch's
five deliberately ambiguous endings require identifying a substantive intended
route, rather than imposing a happy-win criterion. 9:05 is short: use diverse
cases rather than repeating probes for a quota, and seek a non-arrest escape
rather than forcing its timeout ending.

Preserved prior split assignments for Dreamhold/development, Bronze/train and
905/train. Assigned Violet/test and Slouching Bedlam/development before generation;
all versions and branches within each game family remain together. No training
or model evaluation occurred. Terra was asked to review new startup identities
and exact failed/recovery pairs. The monitor now covers fifteen games.

Evidence: `control/fullplay-expansion-20260925-batch3.json`,
`control/expansion-launch-20260925-batch3.json`,
`sources/expansion-20260925-batch3/`, `batches/splits.json`,
`play/*/collection-notes.md`, and timestamped `runs/fullplay-*` launch directories.

## 2026-09-25 02:45: manual-menu stall and explicit recovery

Slouching Towards Bedlam's EXAMINE MANUAL opened a menu at original-session
`slouching-bedlam-bb653b6ab4:e00017`. Muse then sent TAKE MANUAL as if it were an
ordinary parser prompt. The command and later await-output both produced empty
timeouts (e00018/e00019). The broker correctly blocked further input, but waiting
could not exit this menu. These records remain uncertain/quarantined, not clean
wording-repair evidence.

Stopped only this game's worker and broker, preserving history and its confirmed
start-office save. The first recovery attempt refused the save because our helper
required literal Ok., although the CLI had printed Saved to the exact save path.
Read-only CLI source inspection confirmed that successful writes print this line;
an isolated restore check retained the game's distinctive restore response.
Updated the experiment recovery helper to accept the exact saved-path receipt and
a configured exact restore-response line. No interpreter/application code changed.

Recovery used a new explicit session `slouching-bedlam-18faea2151`, branch b2,
with a verified save hash and successful restore response; old pending input was
not replayed. A post-restore LOOK confirmed the Office. Timer-driven checkpoints
are disabled for this session so SAVE cannot be injected into another manual
menu. The new worker's notes require Q to leave a displayed manual menu before
ordinary commands. Historical unsaved actions are not assumed to carry over.

Evidence: `control/fullplay-slouch-menu-recovery-20260925T0244.json`,
`control/slouch-restore-check-20260925T0245/`,
`control/fullplay-slouch-recovery-receipt-20260925T0245.json`,
`play/slouching-bedlam/recovery.json` and `session-history/`.
The three transport regression tests passed (3.950 seconds); new recovery raw
spans/hashes were checked against stdout.raw. This is a harness recovery, not a
completed game or a retroactive validation of the timed-out command.

## 2026-09-25 02:58: 9:05 escape verified

9:05 completed the non-arrest escape branch. Actual event
`905-0674f2e54c:e00098` (b1) describes merging onto the freeway and shows the
You have left Las Mesas ending, credits and restart/restore/quit menu. Parent
checked exact stdout bytes/hash; Terra independently verified completion in its
02:47 status. The earlier b0 arrest ending remains separate failure evidence.
This is eight completed games of fifteen, not eight maximum-score runs.

Evidence: `control/ending-parent-verification-20260925T0300-905.json`,
`play/905/ending-claim.json`, `play/905/stdout.raw`, `runs/fullplay-status.json`.
The completed worker and broker remain stopped. Seven other workers continue;
review of new cases is ongoing. The two Scott-format games still show repeated
puzzle/timing failures; their proposed explanations are hypotheses until checked
against exact game data or observed responses.

A further capture-protocol mistake surfaced during this check: Slouch's
`inbox/m0115.json` contained a Markdown progress note rather than a JSON request.
The broker correctly skipped it without executing anything, but an unanswered
file could block the next worker continuation. Parent preserved its bytes and
SHA in `control/slouch-m0115-rejection-20260925T0301.*` and supplied an explicit
supervisor error response. The request was not rewritten as a command and did
not become a game turn. This illustrates why process exit and file presence are
insufficient proof of a successfully serviced request.

## 2026-09-25 03:10: ten concurrent Muse workers

The user authorized increasing concurrent games to ten and offered Raspberry Pis
as later worker hosts. At the live check, Violet had reached its author winning
narrative (`violet-bfdc33ea8f:e00293`); parent checked the actual response/hash and
requested Terra's independent verdict. It remains stopped. Six games were still
incomplete, but Voodoo's launcher had stopped because another Markdown progress
note was written into inbox/m0417.json. Parent preserved/rejected that invalid
request without game input and resumed the existing Voodoo interpreter.

Added Anchorhead (original Z-code R5/990206), Curses (R16/951024), Theatre
(R2/951203) and Savoir-Faire (R8/040205), bringing scope to nineteen games and
verified live launchers to ten. Story files came from the existing private
library; fetched guides and raw hashes are retained. Curses guide matches R16;
Anchorhead/Theatre guide editions are unspecified; Savoir-Faire guide is based on
R6 and deliberately includes false/nonessential steps. These distinctions are
recorded rather than hidden by title matching. Three new games start with key
pauses; the fourth starts at an ordinary prompt. Per-game notes handle both.

Host check showed about91GiB available RAM and a4.38 one-minute load average;
this observation justified the modest local increase, not an inference-throughput
benchmark. The installed Muse executable is x86-64. Pi deployment remains a
proposed pilot requiring ARM-compatible installation and user authentication;
no Pi workers are claimed as running. No model training or publication occurred.

Evidence: `control/fullplay-expansion-20260925-batch4.json`,
`control/expansion-launch-20260925-batch4.json`,
`sources/expansion-20260925-batch4/`,
`control/ending-parent-verification-20260925T0311-violet.json`, and
`control/voodoo-m0417-rejection-20260925T0310.*`. The monitor covers nineteen games
with a cap of ten concurrent workers. New games beyond this batch are not
implicitly added whenever a slot opens.


## 2026-09-25T03:17:32.479165+00:00: source-supported Scott hints and independent expansion review

Terra independently confirmed Violet's ending (violet-bfdc33ea8f:e00293) and the four batch4 startups, bringing verified completed games to nine of nineteen. See runs/fullplay-supervision.md and runs/fullplay-status.json, with source review archived in control/scott-hints-review-20260925T031627.md.

Narrow static-data hints were delivered through the help broker as voodoo-castle-5bd0b59cae:e00673 and secret-mission-08dcee7c13:e01257. Voodoo's second-part ON MAN command requires the rabbit foot and open coffin; Secret Mission's broken window reactivates the camera, so picture display must follow the break. These are source-supported hypotheses, not successful play evidence, and are explicitly separated from player-observed recall. Original bytes and SHA256 are in the archived review and request metadata.

Muse live session-message attempts returned external_agent_ingress_closed; receipts are control/scott-hints-message-voodoo-castle-20260925T0316.json and control/scott-hints-message-secret-mission-20260925T0316.json. Healthy workers were left running. supervisor-hint.json points to each broker response for the next continuation; no claim that the current workers have consumed those hints. No reset, replay or game command was issued by the supervisor.

The automation now records nine independently verified conclusions and keeps the ten-worker ceiling. No Pi worker has been installed, no further games added, no training/evaluation or publication started.


## 2026-09-25T03:29:49.493791+00:00: two menu stalls recovered, and Scott hints checked in live play

Slouch's File F6A142 menu selection followed by literal RETURN produced empty timeouts (slouching-bedlam-18faea2151:e00290-e00292). Savoir-Faire HELP/Special Instructions requested SPACE; the space command and later waits likewise timed out (savoir-faire-3e83fd4831:e00102 onward). These are transport failures, not parser-rejection examples or game endings. Old histories are intact; affected evidence stays quarantined.

Stopped only the two affected broker/worker process trees (control/menu-stop-20260925T0329.json). Restored engine-confirmed office-journal and basin-full saves into explicit new sessions slouching-bedlam-b08abfcb18 b4 and savoir-faire-5a89e6c8ff b3. Confirmed restore acknowledgments, observed rooms and raw-span hashes: control/menu-recovery-receipt-20260925T0329.json. New configurations: control/fullplay-slouching-bedlam-menu-recovery-20260925T0329.json and control/fullplay-savoir-faire-menu-recovery-20260925T0329.json. Both use12-hour brokers, automatic checkpoints disabled; pending old inputs were cancelled without replay. Restarted workers only after verified restore. Notes direct workers to broker excerpts instead of the problematic interactive help/file menus. No application or harness implementation changed.

Secret Mission's m0529.json had a stray final closing bracket and stopped its launcher. Original bytes/hash preserved at control/secret-m0529-rejection-20260925T0329.*; request explicitly rejected without execution, then worker resumed on the same live broker.

Independent Scott review now confirms local outcomes: Voodoo e755 ON MAN placed the foot with thunder; e758 LOOK COFFIN confirmed it worn. The static prediction that LOOK MAN would confirm it was wrong (e756), and is corrected here. Secret Mission e1292 broke the window/reactivated camera, e1293 SHOW PICTURE deactivated it, e1294 entered the ledge without the earlier alarm. These are local puzzle steps, not completed games. Nine endings remain verified. Further review requested from Terra.

Training/evaluation and publication remain unstarted; only collection, review and private experiment records changed.


## 2026-09-25T03:30:48.831934+00:00: Voodoo Castle completed

Parent independently checked raw bytes/hash/text of voodoo-castle-5bd0b59cae:e00763 (raw67015:67243, SHA256 469d368636df3267da2837559e645623bb26c55ba7521b94151d4a7d81a81b25). YELL CHANT concludes the ritual with pins falling out, Smiling Count Cristo, explicit game over and interpreter exit. This is a verified curse-lifting ending, bringing the total to ten of nineteen. Receipt: control/ending-parent-verification-20260925T0331-voodoo.json. Worker is stopped; do not resume completed game. Nine other game launchers remain. The earlier entry saying nine endings was the review snapshot before this ending was inspected. Terra notified for its independent audit.


## 2026-09-25T03:43:50.914853+00:00: menu input encoding clarified

Anchorhead m0246 requests literal space while declaring an Enter intent, after e301 selected book chapter2. At inspection the request was still within its wait, not yet a concluded timeout. Local CLI source inspection finds read_char_from_line uses first byte of nonempty input and ZSCII13 for an empty line: literal RETURN is R, literal space is space. This explains an input mismatch without establishing all menu stalls have the same cause (Savoir requested an actual space). Source hashes and scope limitation: control/menu-input-source-20260925T0344.json. Added encoding clarification to future Muse prompts and incomplete-game notes. No game input, replay, binary or application change was made.


## 2026-09-25T03:46:30.261236+00:00: Anchorhead menu timeout and checkpoint recovery

anchorhead-4f68bc5f05:e00302 returned empty no_output_timeout after m0246 sent literal space while declaring Enter intent. Preserved and quarantined as transport evidence, never interpreted as successful reading or parser rejection. Only its broker/worker tree stopped (control/anchor-menu-stop-20260925T0346.json). Restored library-day2-circulation (old e281) into anchorhead-51ee2d15c2 b2; engine Ok acknowledgement, LOOK and raw hashes checked in control/anchor-menu-recovery-receipt-20260925T0346.json. Earlier pending inputs cancelled without replay. New12-hour broker config control/fullplay-anchorhead-menu-recovery-20260925T0346.json disables automatic checkpoints. Notes explain correct Return encoding and broker excerpts for optional book content; this is not an application fix. Ten endings remain independently verified; nine games incomplete.


## 2026-09-25T03:52:07.876272+00:00: continuous ten-worker authorization

User requested ten always running, superseding the fixed nineteen-game limit. Added systemd user manager scripts/maintain_workers.py with15-second slot checks, duplicate guards, exact story/guide hash validation, safe same-broker worker continuation, and explicit holds for uncertain unfinished sessions. Enabled lanthorn-muse-pool.service and user lingering. A manager restart preserved all ten worker PIDs and all brokers (control/pool-before-restart-20260925T0351.json). Three focused pool-policy tests passed. No application, training or publication changes.

Prepared five source-pinned games in control/fullplay-refill-queue-20260925.json; receipts sources/refill-20260925/*.json and raw guide files retain version gaps. Balances R5/961216 started as balances-01a7783d25:e00001, restoring actual concurrency to ten. Spider and Web R4/980226 has matching guide; So Far R6/961218 differs from guideR5/960619; Hunter in Darkness R4/991119 has unspecified-guide release; Jigsaw R3/951129 guide1995 release unspecified. Jigsaw is conservatively grouped with Curses in train due shared protagonist reference. No reuse-permission claim; sources remain private. Future launched games and queue exhaustion are monitored through control/worker-pool-events.jsonl and status.


## 2026-09-25T03:54:30.791635+00:00: first automatic slot refill observed

Slouching Bedlam stopped after a concluding gallows/Logos-spread epilogue. Parent verified e233 raw102314:105261 and SHA256 d4439fd038e6cd45c1b69e3545a81f23b32eb377546400016da67b92c6bbeaa4; explicit end marker and Appendix B unlocked. This is an intended bleak ending, not a happy win or successful containment; model route wording is not accepted as authoritative. Receipt control/ending-parent-verification-20260925T0354-slouch.json. Terra independent review requested.

When the launcher exited, the pool automatically started Spider and Web (spider-and-web-e5197766e3) at03:53:17, keeping ten actual worker launchers. Start/process receipts in control/worker-pool-events.jsonl; exact startupR4/980226 and guideR4/980226 are pinned. This is an observed automatic refill, in addition to pure policy tests and manager-restart verification. Remaining queue: So Far, Hunter in Darkness, Jigsaw.


## 2026-09-25T03:59:40.565429+00:00: broker-cap recovery and queue replenishment

Zork reached the2500-event service cap. Paused only its worker and the pool manager, then captured a fresh save at zork-i7-c569ad8028:e02500/e02501 (pool-cap-2499). Stopped the old broker and restored that exact save into zork-i7-05114e1aff b99, with Ok acknowledgement, Round Room LOOK and raw hashes verified. Receipt control/zork-pool-cap-recovery-receipt-20260925T0359.json. No pending input replay or rollback to an older checkpoint. New config control/fullplay-zork-pool-cap-recovery-20260925T0358.json uses12hours, max_events100000, automatic checkpoints disabled. Recovery cap is now configurable, preserving2500 default for older configs; pool readiness uses the same manifest limit. Three pool-policy and three real-process transport tests passed. Restarted pool manager after restore, which resumes the same game.

Prepared A Bears Night Out and The Acorn Court as additional successors in control/fullplay-refill-queue2-20260925.json, with exact story headers/hashes and IF Archive guide receipts under sources/refill-20260925. Guide releases unspecified, no compatibility assumption. Added family splits without modifying existing assignments. Only queued: no extra simultaneous workers started.


## 2026-09-25T04:02:06.137145+00:00: worker manager review follow-up

Terra independently verified Slouchs intended bleak finale, Balances/Spider startup identities, and Zorks new save/restore hashes. Its audit flagged automatic-resume and capacity races. Manager now checks the last actual input state (help/annotation cannot hide a timeout), exact engine/story/save-directory child identity, a supervisor hold marker and a clean launcher exit before auto-resume. Nonzero or missing exit status requires diagnosis instead of provider/auth retry loops. It rereads live capacity before resume and after broker startup; manual operations must still pause the manager because external launches do not share its lock. Active event caps and timeouts surface as attention. Unreviewed ending claims are explicitly listed for review; freeing their compute does not certify an ending. This provisional replacement policy retains evidence and permits recovery into a later slot if a claim is false. Four pool tests pass, including timeout hidden by metadata. User service restarted with existing live workers preserved.


## 2026-09-25T04:13:31.138617+00:00: Secret Mission completed and So Far started

Parent verified secret-mission-08dcee7c13:e01789, raw270134:270260 SHA2562d8cfbf195b2422399cd934ddb49d8467c7eab4f54e285145ccbba48008d2ea3. POUR WATER defuses the bomb, prints mission complete and game over; distinct from earlier bomb-death branches. Receipt control/ending-parent-verification-20260925T0413-secret.json; independent Terra audit requested. Twelve parent-verified conclusions. Pool filled its slot with So Far, so-far-8d580943cf. Startup verified at control/so-far-startup-verification-20260925T0413.json; guideR5 differs from storyR6. No invented compatibility claim.

Savoir m0376 was missing its final JSON brace. Preserved original bytes/hash and rejected without executing route commands: control/savoir-m0376-rejection-20260925T0413.*. Existing worker/broker left running to handle rejection; no silent request rewrite or replay.

Fixed reviewer-reproduced active-health monitoring gap: help/annotation metadata after a timeout no longer hides the attention signal. active_health now uses last real engine state; added regression for active timeout and configured cap. Five pool tests passed. User manager restarted with live workers preserved. No app changes or model training/evaluation/publication.


## 2026-09-25T04:43:24.236040+00:00: Bronze ending and replacement queue

Parent verified bronze-edcd114f65:e00854 HUG BEAST, raw481384:482401 SHA2565b33a6c7277f1bff3d2575446883c26f8a582c00bddcb08fb6f2d092d876fa84. Explicit King-restored/servants-freed ending; model notes describe kiss but actual command was hug. Receipt control/ending-parent-verification-20260925T0443-bronze.json. Thirteen parent-verified conclusions; Terra independent review requested.

Pool replaced stopped Bronze with Hunter in Darkness; startup receipt control/hunter-startup-verification-20260925T0443.json checks raw hash and exact banner, while guide release remains unspecified. Refilled queue with A Change in the Weather, actual headerR6/960613 vs explicit guideR6/960613; source body/hashes at sources/refill-20260925/change-in-weather.json and config control/fullplay-refill-queue3-20260925.json. Family split test; previous assignments unchanged. Remains queued rather than increasing concurrency. Ten workers/four successors targeted, no app/model/publication changes.

## 2026-09-25T05:02:48.346917+00:00 - Balances and Hunter conclusions; ten workers maintained

Parent verified raw bytes, response text and SHA256 for Balances balances-01a7783d25:e00653 (final cube, Borphee Labs epilogue, explicit victory, 50/51), and Hunter hunter-in-darkness-d1b183a1fc:e00187 (UP, daylight escape after bat swarm, final It's over banner). Receipts: control/ending-parent-verification-20260925T0502-balances.json and control/ending-parent-verification-20260925T0502-hunter-in-darkness.json. Fifteen parent-verified conclusions; newest two independent Terra audits pending. Claims themselves do not establish completion.

Pool replaced them with Jigsaw jigsaw-673cabd620 and A Bear's Night Out bears-night-out-a79e3c9a58. Startup splash, actual banners and early successful saves have verified raw hashes in control/jigsaw-startup-verification-20260925T0502.json and control/bears-night-out-startup-verification-20260925T0502.json. Jigsaw R3/951129 and Bear R5/990224 match local headers. Ten distinct live launchers each have one broker and recent actual input output; one export watcher remains.

Queue replenished with The Jewel of Knowledge R2/990710 versus guide R1/990629, and Tryst of Fate R205/970629 versus guide R104/970330. Both IF Archive community solutions, not official author solutions; version gaps preserved, private reuse permission unknown. Jewel guide includes an intentional failure/restore branch, expressly excluded as a completion. Source URL/access time/raw and normalized hashes under sources/refill-20260925/{jewel-of-knowledge,tryst-of-fate}.json; config control/fullplay-refill-queue4-20260925.json; prior splits retained at control/splits-before-refill4-20260925T0503.json. Four prepared successors now include Acorn Court and Change in Weather. No model training, evaluation or publication performed.

## 2026-09-25T05:12:30.488862+00:00 - Independent ending and startup follow-up

Terra independently rechecked Balances e00653 and Hunter in Darkness e00187 raw evidence at 05:04:56 UTC; fifteen independently verified conclusions in runs/fullplay-status.json verified_historical_endings. Hunter escape is observed; the Wumpus being killed is an inference from the cut-off scream, not an explicit outcome. Jigsaw and Bears startup banners, story hashes, save acknowledgments and save hashes independently verified in ending_startup_followup_0502 / runs/fullplay-supervision.md. Ten live workers with one broker apiece still producing actual interpreter responses; four queued, no pool attention. Training and model evaluation have not started.

## 2026-09-25T05:29:52.064358+00:00 - Spider escape and Acorn victory; queue and exporter refreshed

Parent checked exact raw spans/text/SHA for Spider and Web spider-and-web-e5197766e3:e00781 (b19 G repeating WAIT, teleport narrative with papers and explicit made-a-difference ending); Acorn Court acorn-court-7685b36b67:e00082 (OPEN GATE, explicit victory30/30). Receipts control/ending-parent-verification-20260925T0528-{spider-and-web,acorn-court}.json. Seventeen parent-verified conclusions; newest two independent review requested. Spider claim is on b20 after additional post-ending probes restored papers; victory evidence remains b19, not live b20. Do not silently merge those branches or resume these completed games. Acorn GO WEST to OPEN GATE candidate needs intent review, independent of true ending.

Acorn startup R3/970904/save checked in control/acorn-court-startup-verification-20260925T0529.json. Pool then filled its slot with change-in-weather-3ff9a98393; actual R6/960613 and early save checked in control/change-in-weather-startup-verification-20260925T0529.json. Ten distinct workers and one broker per game continue. Export watcher expired as designed near05:23; verified absent before restarting PID2883706 at05:27 for another3hours. Process receipt control/pool-health-20260925T0530.json. No game resets or duplicated managers.

Queue5 control/fullplay-refill-queue5-20260925.json registers Delusions local R4/971121 versus community guideR2/961021, and Child's Play embedded Z8 R4/080129 with author Stephen Granade's February2008 hints, release unspecified. The latter warns some questions are jokes/not in game. Original HTML preserved and normalized using HTMLParser excluding script/style but retaining hidden hint text. Container and embedded Z-code hashes both recorded; exact Blorb still passed to supported CLI. Sources and version gaps: sources/refill-20260925/{delusions,childs-play}.json. Existing splits preserved; Delusions train and Child's Play test; backup control/splits-before-refill5-20260925T0530.json. Four prepared successors. No training/evaluation/application edits/publication.

## 2026-09-25T05:43:49.566328+00:00 - Bear picnic finale and Jewel opening; Moon-Shaped queued

Bears Night Out bears-night-out-a79e3c9a58:e00366 SLEEP verified against raw117349:118132 SHA04b1d282554606b772197dbeaccb7264d498b8f2cc76d9014754d19bc3cc126e: morning picnic, explicit won33/33, lifelong companion and final menu. Receipt control/ending-parent-verification-20260925T0543-bears.json. Eighteen parent-verified conclusions; newest independent audit requested. Full score does not prove all cases covered. Terra has independently verified previous Spider/Acorn endings (17total).

Pool replacement Jewel of Knowledge jewel-of-knowledge-61db1c70d2 startup and successful early save verified in control/jewel-startup-verification-20260925T0543.json. R2/990710 is pinned header, not an initial on-screen release banner; guideR1 gap retained. Ten healthy workers, one manager, one exporter.

Queue6 adds Moon-Shaped exact Blorb embedded Z8R2/080710 with author Jason Ermer's Release2 annotated walkthrough, guide serial unspecified. Both container and ZCOD hashes recorded sources/refill-20260925/moon-shaped.json. Eight authored endings; aim for guide ending1 (family survives, curse lifted), distinguish alternate finales and ordinary early failure. Configuration control/fullplay-refill-queue6-20260925.json; family moon-shaped/development, prior split backup control/splits-before-refill6-20260925T0544.json. Acquisition stays private, reuse permission unknown. No training or evaluation.

## 2026-09-25T05:50:10.855495+00:00 - Pi fleet readiness audit

User proposed3-4workers per device. Read-only SSH resource/version checks and tiny no-tools Meta connectivity probes recorded in docs/blog/fleet-readiness.md and control/fleet/auth-probe-20260925.json. Four successful authentications, three explicit login requirements, one timeout under diagnosis, one missing install and one unreachable host. Local collection unchanged; no credential replication or remote game rollout.

Pi5v2 bounded retry returned READY at05:50UTC, bringing authenticated hosts to5. Initial timeout retained in receipt; no game workers deployed.

## 2026-09-25T05:59:25.181248+00:00 - Three conclusions, queue replenishment, CM5 authentication

Dreamhold dreamhold-362786f871:e02043 WEST Doorstep portal, explicit end and thanks; Theatre theatre-8533784a56:e01699 GET IN CAR explicit win47/50; Weather change-in-weather-3ff9a98393:e00297 WEST reunion and good-time ending verified against raw text/spans/hashes. Receipts control/ending-parent-verification-20260925T0559-{dreamhold,theatre,change-in-weather}.json. Twenty-one parent-verified conclusions, newest3independent audit pending. Bear now independently verified (18prior). No claim of exhaustive coverage or maximal ending content.

Replacement startups Tryst R205/970629, Delusions R4/971121, ChildsPlay BlorbZ8R4/080129 recorded with initial raw spans and saves in control/{tryst-of-fate,delusions,childs-play}-startup-verification-20260925T0559.json. Initial ChildsPlay opening has no release banner; use pinned header and later output.

Queue7 prepared Frozen R1/960620 and Reverberations R1/990110, community guides with unspecified releases; SpiritWrak R3/960606 vs guideR2 (includesR1 notes). SpiritWrak conservatively grouped zork-i/development due shared FROTZ/GNUSTO vocabulary, not asserted full-game equivalence. Source URLs, raw/normalized hashes, headers in sources/refill-20260925/{frozen,reverberations,spiritwrak}.json, configs control/fullplay-refill-queue7-20260925.json, prior split backup control/splits-before-refill7-20260925T0600.json. Four prepared successors incl MoonShaped.

User reported cm5v1/v2/v3 login completed; actual no-tools Meta READY responses confirmed all three. Eight authenticated Pis total; docs/blog/fleet-readiness.md and control/fleet/auth-probe-20260925.json updated. No remote game workers deployed. No training/evaluation/publication.

## 2026-09-25T06:14:05.234546+00:00 - Remote Muse pilot verified and eight-host ramp enabled

Frozen pilot frozen-a2e5d2eea9 on cm5ai1: e1 actualR1/960620 startup; e2/e3 SAVE acknowledged; e20/e21 both rejected conversation commands. Raw/text/SHA checks preserved in control/fleet/pilot-and-ending-raw-verification-20260925T0612.json. These are collection events, not accepted model cases. Target expands from10 local to10local+24remote,3 each on8authenticatedARM hosts. Actual rollout verification pending, never infer count from config. No credentials transferred, no remote interpreter binaries needed: game state and authoritative raw/events remain central, Muse file tools onPis use a scoped SSH mailbox. Full guides remain broker-side.

Registered24 pinned source configs in control/fleet-batch-{a,b}-20260925.json, verified actual story and normalized guide SHA values plus family-split consistency: control/fleet/batch-ab-parent-validation.json. Guide gaps and uncertain family links retained. Seven fleet tests and five pool tests passed before ramp. Idempotent request/start, three-per-host cap, central reservation/local exclusion and disconnect retention covered. Deployment digests in control/fleet/deployment-20260925T0613.json. Independent audit requested. Snapshot now archives fleet configs/sourceJSON/remote ownership along with scripts and exact raw prefixes.

Separately parent raw-checked Savoir-Faire e1522/e1523 rescue/Paris explicit win and Jewel e424 TOUCH MIRROR homecoming explicit win against the same receipt. Genuine conclusions; earlier Jewel poisoned GET JEWEL is a separate losing branch. Terra independent verdict pending. Training and model evaluation have not started; all work private.

## 2026-09-25T06:16:43.465166+00:00 - 34 concurrent clients observed

control/fleet/rollout-verification-20260925T0614.json records three actual Muse processes per each of eight Pi hosts (24), with expected game workspaces and at least three real command events for every remote game. All checked central raw spans match their event text and SHA256. Local live process inventory separately confirmed10 workers, no attention conditions. Total34 is an observed concurrency snapshot, not a permanent guarantee or completed-game count. Existing19/10-game limits are superseded by the explicit Pi authorization. The heartbeat now manages both schedulers, reservations, remote failures and queue preparation. Two source-checked successors remain queued and batchC8 is in preparation.

## 2026-09-25T06:22:01.676077+00:00 - Independent fleet review and session fencing fix

Dirac found two P1 risks in the first runner: overlapping old RPC mirrors could regress state, and stale Pi requests could reach a new recovered interpreter session. No corrupted pilot spans were found. Fixes: per-game remote bridge lock plus persisted monotonic revision/session fence; central assignment/manifest checks before and after RPC; response session/revision checks; imported requests tagged with their session; future/recovered brokers reject mismatched tags before handling. Existing interpreters were preserved, protected by central checks; they were not restarted merely to load the extra broker check. Explicit recovery handoff is now required, not silently accepted.

Also counted orphan Muse children in per-host capacity and validated settings caps. Twelve fleet tests, three broker transport tests and five local pool tests passed, including late old snapshot rejection, stale requests/engine restart denial, accepted remote start with lost response, duplicate starts and orphan-child capacity. Exact code hashes: control/fleet/fencing-test-receipt.json. Eight host RPC script digests: control/fleet/deployment-fencing-20260925T0622.json. Only the fleet manager stopped briefly/restarted for deployment; games and Muse processes were retained. Follow-up independent review requested, not yet asserted clear.

Registered8 batchC spare games after local story/guide hashes and family-split checks, receipt control/fleet/batch-c-parent-validation.json. Bedlam is a distinct available preview, not Slouch or evidence of full-game completion. PUTPBAA SAVE/RESTORE can end its narrative, so ordinary checkpoint advice must not be applied. Mansion R3 torch issue/older guide remains documented. Private collection only; no training/evaluation/publication.

## 2026-09-25T06:24:07.619142+00:00 - Restart guard and post-update health

Singer confirmed the first session/revision fixes but found that the older broker restart action bypassed unresolved-input protection. Added a guard before engine close/start; a matching session cannot override it. Fleet ingress also refuses such a restart, protecting existing live broker instances without resets. The new direct broker guard loads on future launches/recovery. Two regressions assert no engine close/start and no stale restart entering the inbox, including metadata after timeout. All14fleet+3transport+5pool checks pass; final source hashes in control/fleet/fencing-test-receipt.json. Independent follow-up requested. At06:23:12UTC managers report10local+24remote with no attention/error; nine source-checked spares remain.

## 2026-09-25T06:29:16.618078+00:00 - Reverberations conclusion and Anchorhead recovery

Parent verified Reverberations e151 HIT FLOOR WITH AXE: mafia exposure/rescue and explicit You Rule game-over/final menu, raw26865:28844 SHA6bb1136e3a5930d5f292c613e8299a8ff9f9345fe91ba238f18580791ca90f16. Receipt control/ending-parent-verification-20260925T0629-reverberations.json; Terra independent review requested, not yet claimed. Pool replaced it with The Edifice.

Anchorhead read-clippings returned only auto-take text e1576, then e1577 command and e1578+ await_output stalled with empty output. Parent preserved those ambiguous spans and stopped only its worker/broker. Restored confirmed cellar-fuse-day3 save olde1571 into explicit session anchorhead-2c1c588159; verified restore acknowledgment/LOOK and raw hashes. Pending await_output cancelled without replay. Receipt control/anchorhead-clippings-recovery-receipt-20260925T0628.json; new config same timestamp max100000 events,12hours,auto-checkpoints false. Added warning to avoid the clippings menu path and reconcile old progress after restore. No engine/app modification.

Dirac closed both original fleet P1s for process restart/reconnect; power-loss fsync durability remains unproven and recovery handoffs must stay paused. Added broker capability declarations and importer hold on every remote restart against old brokers, preventing an already queued restart from slipping past a later timeout. New/recovered brokers enforce session and restart guards directly. Fifteen fleet+three transport checks passed in this heartbeat. Current sessions otherwise preserved. Independent next80case/threeending/recovery audit requested. No training, model evaluation or publication.

## 2026-09-25T06:31:00.064907+00:00 - So Far malformed help released safely

Pool correctly held So Far after its launcher stopped waiting on malformed m0938 (stray final bracket). Worker had already superseded that help with valid m0951, but unacknowledged old file retained the slot. Parent archived original exact bytes/SHA and rejected it without executing any command, receipt control/so-far-m0938-rejection-20260925T0631.json. Same interpreter session so-far-8d580943cf preserved. Pool resumes safely from real state; no restore or request replay. Singer was assigned a bounded read-only guide/version diagnosis of the repeated dark-area blockage; source hints remain provisional until actual game evidence.

## 2026-09-25T06:35:51.812490+00:00 - First remote conclusion and explicit Pi recovery

Asylum on cm5ai1 reached e46 NORTH explicit win/final menu; parent raw verified, receipt control/ending-parent-verification-20260925T0635-asylum.json. Compact cpuguy edition,0/0 score is not content-coverage proof. Independent audit pending. First observed remote refill started Mother Loose on same host, keeping its three-slot target.

Kook U target terminal menu SPACE e54 stalled. Stopped only its Pi supervisor/Muse and central broker; restored acknowledged computer-room-network-up olde40 in explicit new session kook-u-ef2767bf50 b2. Old Pi workspace and worker state archived, new-session fence installed before RPC resumed, central reservation updated and cache cleared. Pending old actions cancelled, not replayed. Recovery/progress context staged without replacing newly written worker progress; new worker used m0101, a new request ID. Receipt control/fleet/kook-u-recovery-20260925T0634.json pins old/new state and raw restore evidence. New broker has session/restart guards,100000eventcap,24h lifetime. Avoid optional target menu and use small source help. No old fence removed merely to accept an old request. New independent handoff review requested.


## 2026-09-25 06:52 UTC — new conclusions, startup recovery, and source help

Parent verified exact raw spans/text/SHA for Moon-Shaped e406 (family survives/curse removed), Nine Points e61 (explicit SAMPLE completion), Childs Play e438 (toy/playdate finale), Zuni Doll e112 (disposal finale), All Quiet on the Library Front e123 (book/graduation), Only After Dark e85 (Davids survival), PUTPBAA e7 (authored absurdist title-command win), Pentari e129 (Galin freed), and Slacker X e119 (installment finale with sequel teaser). Receipts are control/ending-parent-verification-20260925T0645-*.json, *T0648-*.json, *T0651-*.json and *T0652-*.json. This brings parent-checked authored conclusions to 34, including Nine Points explicitly as a sample; independent review still stood at 24 at this inspection. Scores do not establish coverage. All Quiet has trailing stale status/quotation text retained for interleaving review; no candidate is accepted based on ending verification alone. Replacements continue automatically.

Delusions HINT menu SPACE timed out at delusions-07b4a7fbbe:e00448; await e449 was empty. The first checkpoint recovery failed because RESTORE was consumed at a startup keypause (delusions-20a1b41aa0:e4); the helper closed its engine and no worker was launched. Failure preserved in control/delusions-first-recovery-failure-20260925T0648.json. Added explicit before/after screen guards and Enter-only startup steps to recover_broker.py, tested by four regression tests (docs/blog/test-receipts/recovery-startup-20260925T0652.json). Successfully restored confirmed before-pizza old e389 into delusions-8997f25a87 b12; new e6 confirms restore, e7 LOOK confirms live location. Receipt control/delusions-menu-recovery-receipt-20260925T0648.json. Pending input cancelled without replay; old timeout/failed restore evidence quarantined. Both schedulers coordinated through scheduling.lock. No application code changed.

So Far author R6 source archive retrieved privately from eblong.com/zarf/ftp/sofar-src.tar.gz; README explicitly identifies R6. Source bytes/hashes in sources/so-far-r6-source-20260925/source.json. Singer's narrow low-PLOOPING versus PLIPPING diagnosis was logged by the live broker as so-far-8d580943cf:e01409 with source hash and lines 729–836, then supervisor-hint.json points to the response. No game action or reset was sent. Do not assume the currently running worker read it yet; advice remains provisional until live output verifies it.

Startup raw/header receipts for Mother Loose R2/981128, Paper Chase R1/950503, Hunt for Relief R1/000820, Mansion R3/260803, and PUTPBAA R2/010618 are control/*-startup-verification-20260925T0648.json. PUTPBAA deliberately received no automatic SAVE because SAVE can be an ending command. Parent hash/header/family verified and registered batch D: Gumshoe R1/960331 (guide R1, serial unspecified), Fine-Tuned R8/020520 (author guide R6), Magic Toyshop R1/951018 (exact guide match), Christminster R4/961117 (older guide unspecified release). All train; Christminster conservatively joins curses family. Receipt control/fleet/batch-d-parent-validation.json. Full guides/stories remain central, never staged on Pis. Pasteur is preparing four batch E successors in its own source/config paths; not yet registered or runtime-verified.

Collection, independent review and exports continue. No training, model evaluation or publication has begun. Snapshots remain local archives and prefix hashes, not off-host backups.


## 2026-09-25 07:02 UTC — queue replenishment and explicit transport quarantine

Tube Trouble tube-trouble-1b2d95be53:e00139 EAT CHOCOLATE reached the authored hunger-satisfied win/final menu; exact raw/text/hash verified in control/ending-parent-verification-20260925T0658-tube-trouble.json. Parent total 35 authored conclusions, including Nine Points explicitly as a sample. Dirac independently reached 27 (Asylum, Moon-Shaped family-survives ending, and Nine Points added), and reviewed another 80 cases: 67 accepted, 11 revise, 2 quarantine. Newer endings and cases remain pending, not automatically accepted.

Dirac independently verified Kook U and Delusions recoveries. Added exact manual transport exclusions for kook-u-489e2b24ed:e00054, delusions-07b4a7fbbe:e00448/e00449, and failed startup restore delusions-20a1b41aa0:e00004 in reviewed/transport-events.json. Also excluded Library Front e00123 from isolated command-response cases because its verified ending narrative has stale status/quotation text appended. The five exclusions were confirmed in exports/events.csv; no currently linked case used these five events. Export snapshot 07:00:27 has 42,125 events and 2,905 candidate cases, which is not an accepted-case count.

Parent validated and registered batch E4 and F4 under the shared scheduling lock. Receipts control/fleet/batch-e-parent-validation.json and batch-f-parent-validation.json pin bytes/header/guide hashes and family consistency. E: The Wedding R5/970825 vs author-amended R3 guide; Ghost Train R7/290912 vs R4/070503 guide; Schooldays R3/092800 guide unspecified; Not Just A Game R3/210603 guide unspecified. Serial values are literal pins, not normalized dates. F: Attack of the Yeti Robot Zombies R0/060825 (release zero alone does not mean demo); HLA Inform R1/050715, explicitly the Inform conversion with source port-version axis distinct from Z-machine release; Muse: An Autumn Romance R2/990922 with older guide; Invisible Man R2/100130 with author guide explicitly R2, serial unspecified. F normalization preserves token sequence. All eight are train families, full guides/stories remain central, runtime completion unproven.

Six replacement startup/save receipts at control/*-startup-verification-20260925T0700.json: BSE, Bedlam (Michael Zey preview), Critical Breach, Danger! Adventurer at Work!, Gumshoe and Fine-Tuned. Fresh read-only remote /proc inspection confirmed three Muse binaries per authenticated Pi, 24 total, correct game workspaces and shell/web disabled; receipt control/fleet/live-proc-check-20260925T0659.json. Initial diagnostic matched basename muse rather than the actual muse-bin-1.4.0-R4161.1 and falsely found zero; corrected against actual executable paths, no outage. At the final health check 10 local plus 24 remote were active, no attention/error, nine source-checked successors queued; control/fleet/heartbeat-health-20260925T0702.json. One export watcher remains. No training/evaluation/publication.


## 2026-09-25 07:16 UTC — So Far conclusion and recovery provenance correction

Parent raw/text/SHA verified So Far e1571 final moons/theater epilogue, Tryst of Fate e908 GET UP homecoming and Deadeye resolution, Paper Chase e335 YES graduation, and Space Station e237 WAIT safe scooter departure with Fussbudget and distant reactor destruction. Receipts control/ending-parent-verification-20260925T0714-{so-far,tryst-of-fate,paper-chase}.json and T0716-space-station.json. Parent now 39 authored current-version conclusions including Nine Points sample. Dirac independently verified previous 35 and completed 80 more cases (61 accepted, 18 revise, 1 quarantine). Only After Dark win is historical b2, not subsequent b4. New claims remain pending. No maximum-score coverage inference.

So Far now has observed FOLLOW LOW PLOOPING success e1423 and ENTER SILENCE transition e1476 following logged source-help e1409. This supports the narrow source diagnosis; it does not show exactly when Muse read the supervisor pointer or prove causal attribution. Hints remain separately labeled from player-observed recall.

Anchorhead historical overview READ BOOK menu SPACE e295 and awaits e296/e297 stalled in session 2c1c588159. Stopped only its worker/broker under scheduling.lock, preserved raw/history and cancelled pending await without replay. Restored library-safe-day3 into anchorhead-9852cd5b9d b36; broker3672312/worker3672439, 24h from07:12, max100000 auto=false. Receipt control/anchorhead-book-recovery-receipt-20260925T0713.json and config control/fullplay-anchorhead-book-recovery-20260925T0713.json. Current progress explicitly avoids optional book/clippings menus; old contradictory route text remains archived, not appended as current instructions. Timeout events manually quarantined.

This recovery exposed a metadata defect: recover_broker.py accepted a RESTORE filename Ok response as the checkpoint SAVE receipt because both share checkpoint_filename type. Actual restored bytes and engine success were valid, but its source event pointed to Anchorhead e198 instead of true SAVE e174. Auditing all current recovery records found the same reference error for completed Savoir-Faire (e92 restore instead of e86 save). Added confirmed_checkpoints requiring preceding SAVE, matching session/branch/name. Five startup/provenance regression tests pass. Corrected current recovery.json/manifest references with explicit before/after receipt control/checkpoint-provenance-recovery-receipt-20260925T0715.json; immutable raw journals and original receipts remain intact. No game state altered for this metadata repair. Independent reviewer notified.

Magic Toyshop, Christminster and The Wedding startup/early save receipts at control/*-startup-verification-20260925T0714.json retain exact versions. Pasteur is preparing bounded batchG4 successors without shared registry changes; not yet registered. Singer assigned read-only diagnosis of repeated plain CLI menu SPACE handling; no application modification or uncertain-input flush permitted. Collection/export watcher remains active; no model training/evaluation/publication.

## 2026-09-25T07:32:54.307054+00:00 — shared provider quota pause, preserved live sessions

All 34 Muse clients (10 local, 24 Pi) stopped with Meta HTTP 429 subscription-quota exhaustion around 07:18 UTC. The provider reported reset at 2026-09-25T07:40:45Z. Parent checked all failed logs, empty pending mailboxes, normal last input states and all 34 still-live central brokers. Exact log paths/hashes, process evidence and original scheduler settings are in `control/provider-quota-hold-20260925T0728.json`. Both scheduler launch settings are now disabled under the shared scheduling lock; services remain active to preserve mailbox sync and ownership. No game reset, command replay, credential change or provider retry was performed. After reset, use one supervised local canary and confirm real provider/interpreter progress before resuming remaining clients in their existing sessions. Preserve failed run evidence and remote session fences/workspaces.

Mother Loose reached its substantive authored happy ending at `mother-loose-608208fd92:e00182` (Z/WAIT, branch b1), with homecoming and THE END. Parent verified raw bytes 51528:54055, SHA256 `d056ff98046982b026f494a1e78a6eb93e7e53c0eff112aadea49fa778aa4517`; receipt `control/ending-parent-verification-20260925T0732-mother-loose.json`. This brings parent-verified authored conclusions to 40, including the explicitly labeled Nine Points sample; independent review remains separate.

Batch G is source-checked and registered while launches remain held: Traffic R2/241027 author guide R2 without serial; BiCon Blorb embedded Z8 R4/101006 with matching author guide and separate container/embedded hashes; Mortlake Manor R1/120304 matching author transcript; Windhall Volume One R5/960828 versus community R3 guide. All four preserve canonical train families and private reuse status; parent receipt `control/fleet/batch-g-parent-validation.json`. Prepared configurations do not prove runtime compatibility or completion.

Dirac found checkpoint selection could accept a timeout-tagged Ok reply. Future recovery now requires clean states on both SAVE and filename reply and excludes manual transport quarantine, delayed-linked events and first inputs after unresolved output. Six startup/checkpoint tests pass; receipt `docs/blog/test-receipts/checkpoint-transport-20260925T0732.json`. No running interpreter or historical journal was changed. Snapshot coverage now includes quota hold receipts and menu-diagnosis reports.

Singer's read-only menu diagnosis is at `control/menu-input-diagnosis-20260925T0716.md`: silent redraw/output-drain behavior is a supported hypothesis, not a verified live-state classification. The proposed host-only menu query is not implemented or deployed. Optional menus remain avoided; no speculative flush keys or application changes. Training, model evaluation and publication remain unstarted.

## 2026-09-25T07:46:47.367237+00:00 — quota reset and supervised same-session resumption

After the provider's 07:40:45 UTC reset, parent verified all 34 brokers/interpreters still alive, their actual latest input states normal and pending mailboxes empty. No orphan Muse clients were present. Delusions was the single local canary at 07:41:26; it produced actual same-session commands and raw replies e239–e241 before broader resumption. Evidence: `control/provider-quota-canary-20260925T0741.json`.

Parent resumed the other nine local clients and three on each of eight Pis. On each Pi, failed state JSON was archived under `~/lanthorn-muse/history/quota-20260925T0743/` while holding the workspace bridge and host start locks, after confirming the old client absent, no pending requests and matching session/fence. Game workspaces, fences, revisions, request/response files, central brokers and all session IDs remained intact. Old failed logs and exit statuses were preserved. No interpreter reset or replay. Launch and archive hashes: `control/fleet/quota-resume-launch-20260925T0743.json`; read-only readiness: `control/fleet/quota-resume-readiness-20260925T0742.json`; one-off supervision code retained beside these receipts.

Actual process inspection verified 10 local Muse binaries and 24 remote binaries, three per Pi, with shell/web disabled. Same-session interpreter progress is checked against fresh raw spans/hashes in `control/fleet/quota-resume-live-verification-20260925T0744.json` (receipt timestamp records the latest check). Both scheduler launch flags were re-enabled after process/transport checks. Neither service was duplicated or stopped; fleet synchronization remained active. No fresh quota errors were found. Exactly one export watcher remains; all 50 manual transport exclusions were verified as quarantined in the refreshed CSV.

Dirac independently confirmed Space Station and Mother Loose: 40 historical authored conclusions, including Nine Points explicitly as a sample. Its completed 120-case pass accepted 99, requested revision for 19 and quarantined 2, checking 735 raw spans without mismatch; 947 cases remained unreviewed at that pass. A further bounded review is underway.

The checkpoint guard still skipped an empty Enter timeout because it tested command truthiness. It now distinguishes missing command from the empty string. The same edge was fixed in export transport classification, so a timed-out Enter and the next actual input are excluded while intervening metadata does not clear the unresolved marker. Six Python recovery tests and three persistent Node exporter assertions pass; `docs/blog/test-receipts/empty-enter-transport-20260925T0744.json`. This is collection-harness evidence handling, not application code or model evaluation. No training, evaluation or publication started.

Final resumption check at 2026-09-25T07:47:15.974269+00:00: all 34 games now have fresh interpreter input/output with verified raw hashes in their unchanged sessions, including I-0 after its help requests. Ten local plus 24 remote actual Muse processes, no quota errors, no active transport attention. Receipt `control/fleet/quota-resume-live-verification-20260925T0744.json`.

## 2026-09-25T07:58:06.858864+00:00 — three more authored endings after quota recovery

Parent verified exact raw bytes, response text and SHA256 for Night at the Computer Center `night-at-the-computer-center-d16c3b6cd5:e00263` (PUT STOLEN PRINTER ON TABLE, saved-your-job finale); Kook U `kook-u-ef2767bf50:e00187` (TURN ON NAME, network restored and Dean appointment epilogue); and Hunt for Relief `hunt-for-relief-b4de5c739d:e00167` (SIT ON TOILET, authored relief/win). Receipts `control/ending-parent-verification-20260925T0757-{night-at-the-computer-center,kook-u,hunt-for-relief}.json`. Parent total is 43 authored conclusions including Nine Points SAMPLE; independent count was 40 when this audit started. Repeated Night status/quotation tail and Hunt's USE TOLIET→SIT ON TOILET intent are specifically sent for separate command-pair review. Valid endings do not certify all candidate cases or full content coverage.

Automatic replacements are Not Just a Game (`not-just-a-game-8201b5a6d4`, Z5 R3/210603), Attack of the Yeti Robot Zombies (`attack-of-the-yeti-robot-zombies-504df4e144`, Z5 R0/060825), and HLA Inform (`hla-inform-09ea9c8220`, Z5 R1/050715). Parent verified actual header bytes and startup/early checkpoint raw spans; receipts `control/{not-just-a-game,attack-of-the-yeti-robot-zombies,hla-inform}-startup-verification-20260925T0757.json`. HLA's initial e1 reports Library error 10/player-object outside object tree before PLOT. Preserve that fault: later e2 version3.20 banner, e3 Guild and e4/e5 actual SAVE succeed. It is not an error-free startup, and banner3.20 and Inform-port R1 are distinct version axes. No application patch or reset performed.

Fresh remote /proc inspection confirms 24 actual Muse binaries, three per authenticated host with correct distinct workspaces and shell/web disabled, plus 10 local Muse binaries; receipt `control/fleet/live-proc-check-20260925T0758.json`. All active brokers have recent normal input states, no scheduler attention/errors, and one export watcher remains. The queue had six prepared successors; Pasteur is preparing four Batch H candidates for parent validation, not yet registered.

Dirac closed the empty-Enter checkpoint/export P2 after independent review. Its completed bounded120-case pass accepted101, requested14 revisions and quarantined5, verifying617 raw spans;904 were unreviewed at that pass. Another bounded120-case pass plus these endings/startups is requested. Review counts will change while collection continues. No training, model evaluation or publication.

## 2026-09-25T08:14:10.643522+00:00 — three game finales, a preview conclusion, and Batch H

Parent independently checked raw byte spans, SHA256 and exact text for The Edifice `the-edifice-79519f86df:e00829` (WEST, return-to-roots/HISTORY ending after three levels solved), Magic Toyshop `magic-toyshop-9a53f3ebb2:e00291` (ENTER CHEST, Victorian arcade/birthday parcel win), and I-0 `i-0-d1ac7729bb:e00250/e00257/e00263` (homecoming and birthday epilogue, READ MESSAGE finale). I-0 completed the alternate gray-pickup route, not the manifest's preferred Larry/Willowbutton/bus route; e257 ended branch b8 before restored bedroom branch b9 ended at e263. Bedlam `bedlam-59f5a6e860:e00143` (TURN ON CAR) explicitly completes Michael Zey's PREVIEW, described in-game as about one-fourth of the planned project. Do not call that full-game completion. Exact evidence is in `control/ending-parent-verification-20260925T0813-{the-edifice,magic-toyshop,i-0,bedlam}.json`. Parent now has 47 authored conclusions, explicitly including Nine Points sample and Bedlam preview; independent review of these four is requested.

Replacements Muse: An Autumn Romance R2/990922, The Believable Adventures of an Invisible Man R2/100130, Traffic R2/241027 and BiCon (Blorb embedded Z8 R4/101006) have parent-checked story/header and actual startup/early-save raw spans. Receipts `control/{muse-autumn-romance,believable-adventures-invisible-man,traffic,bicon}-startup-verification-20260925T0814.json`. Guide version caveats remain unchanged. Fresh process inspection at `control/fleet/live-proc-check-20260925T0814.json` verifies ten local and 24 remote actual clients, correct workspaces and disabled shell/web, with no scheduler attention. One export watcher continues through about08:27 UTC.

Batch H was validated and registered under the shared scheduling lock: Varicella Z8 R1/990831 (catalog version1.14/serial9339 remains separate; guide release unspecified), Cacophony Z8 R4/091209 (author ZIP guides older, primary member Walkthrough3; all ZIP/member/raw/normalized hashes checked), Risorgimento Represso Blorb Z8 R6/171114 (author guide Glulx R5/171024, both edition and release gaps retained), WadeWars III: Askin Z5 R106/020512 (author Z-code guide older, release unspecified). Actual bytes/header/hash/normalization/family receipt `control/fleet/batch-h-parent-validation.json`. All train. Reserve Illuminismo Iniziato with risorgimento-represso and Got Toast?/WadeWars ports in wade-wars; generic influences or shared authorship are not evidence of shared puzzles. These are prepared configurations, not runtime compatibility/completion proofs. Six successors queued after registration. Singer is preparing four Batch I candidates; they remain unregistered until parent validation.

Dirac independently verified the preceding Night/Kook/Hunt endings, bringing its count to43. Its latest completed120-case review accepted91, requested19 revisions and quarantined10, with729 raw spans verified. Night's recurring status/Relax quotation tail remains excluded from unsplit correction examples while its finale body is independently valid. HLA startup version labels additionally differ: e2 banner3.20/Informport0.2, e3 status3.20a, source note port0.3; preserve all with the initial Library error10. Another bounded120 review plus new endings/startups is active. No training, model evaluation, app changes or publication.

## 2026-09-25T08:32:46.674419+00:00 — Dungeon finale, three further conclusions, and Glulx queue preparation

Parent raw/text/SHA verification confirms Zork/Dungeon Inform7 port R4/190920 `zork-i7-05114e1aff:e02122` S on b129: Treasury, Dungeon Master succession and explicit win716/716. This is the full Dungeon port, not commercial ZorkI. Zork is now concluded and must not be resumed from historical recovery instructions. Also verified The Wedding e441 DEBORAH, GO NORTH (elopement and year-later Christening/win); Beyond the Tesseract e353 SAY TESSERACT (stack protects protagonist, Earth saved, explicit win145/155); and Attack of the Yeti Robot Zombies e103 DOWN (country-saved finale). Receipts `control/ending-parent-verification-20260925T0829-{zork-i7,the-wedding,beyond-the-tesseract,attack-of-the-yeti-robot-zombies}.json`. Parent total51 authored conclusions includes Nine Points SAMPLE and Bedlam PREVIEW. Wedding repeated Pope/status tail is flagged for command-response attribution review separately from its valid finale body. Scores alone do not establish content coverage.

Mortlake Manor R1/120304, Windhall R5/960828, Varicella R1/990831 and Cacophony R4/091209 startup/header/early-event bytes were checked in `control/{mortlake-manor,windhall,varicella,cacophony}-startup-verification-20260925T0829.json`. Retain Windhall guideR3 gap, Varicella catalog/version axes and older Cacophony guide. Fresh /proc receipt `control/fleet/live-proc-check-20260925T0832.json` confirms10 local plus24 remote Muse clients, correct host/game workspaces,34 live brokers with normal latest input states and no pool attention. The expired export watcher was verified absent and replaced once at08:28:40 by PID460667, expiring about11:28UTC; receipt `control/fleet/export-watcher-restart-20260925T0829.json`. Both CSVs refreshed08:31:14.

BatchI4 parent validated and registered under scheduling lock, `control/fleet/batch-i-parent-validation.json`: Augmented Fourth Z8R4/200401 with author release4 guide; Pytho's Mask Glulx InformR4/020223 VM2.0.0 with unversioned author guide; Alias the Magpie Glulx InformR5/220210 VM3.1.2 and A Remote Problem Glulx InformR3/250920 VM3.1.2 with co-packaged solution guides. Glulx editions are explicit, container/GLUL/header/local-archive/member/source hashes checked, normalized guide content checked, all four canonical families train. Co-packaging does not add missing guide version pins. Assets remain central and these are prepared configurations, not runtime proofs. Six successors remain queued; Pasteur is preparing four BatchJ candidates, not registered yet.

Dirac independently confirmed the previous four endings (Edifice, Toyshop, I-0, Bedlam), now47 historical authored conclusions. Its last bounded120 pass accepted101, requested9 revisions and quarantined10 with737 clean raw spans. The four new endings/startups and next bounded120 review are pending. Collected events and candidate counts remain distinct from accepted cases. No training, model evaluation, application changes or publication.

## 2026-09-25T08:49:35.676473+00:00 — five conclusions, one held Glulx startup, and a supervised client continuation

Parent verified exact raw/text/SHA finales for Jigsaw e2396 GIVE TEDDY BEAR TO BLACK (b9, together through the century, explicit win100/100); Save Princeton e443 PLAY TRUMPET (university restored, explicit win200/200); Muse: An Autumn Romance e334–336 (beach farewell, StFrancis pause, Barchester/John-and-Konstanza marriage letter, narrator accepts station in life and terminal menu); BiCon e304 KISS wins, native UNDO e305 then e306 KISS PHOENIX wins again. Both BiCon phrasings work; keep the undo chronology even though broker branch remains b0, not a failure/repair pair. Receipts `control/ending-parent-verification-20260925T0845-{jigsaw,save-princeton,muse-autumn-romance,bicon}.json`. Vindaloo e433 TURN ON STOVE cooks and enjoys the meal with explicitwin18/18, receipt `control/ending-parent-verification-20260925T0849-vindaloo.json`. Parent now56 authored conclusions including Nine Points SAMPLE and Bedlam PREVIEW; Dirac independently51 before these5. Its last120 pass accepted94, requested18 revisions, quarantined8 with733 clean context raw spans. Current bounded120 audit includes these new endings. Full score is not full content coverage.

Risorgimento Represso, WadeWars III, Augmented Fourth and Lecture Feature have raw-checked startup/early-save evidence in `control/*-startup-verification-20260925T0846.json` and `control/lecture-feature-startup-verification-20260925T0849.json`. Preserve their pinned headers and guide gaps. Pytho's Mask Glulx `pythos-mask-a39eb2af1a` stalled during startup: title e1, empty Enter e2 produces briefing/MORE, empty Enter e3 gives no_output_timeout and passive await m0003/e4 again produces zero bytes. No save or ordinary gameplay prompt exists. Held only its client under scheduling lock, preserving broker473922/interpreter473923 and owned slot. No extra key, replay, restart or format substitution. `control/pythos-startup-hold-20260925T0844.json`, `control/pythos-startup-failure-20260925T0848.json`, `play/pythos-mask/supervisor-hold.json`. Both timeout events are manually excluded in transport-events and exported as quarantined.

Singer's read-only diagnosis `control/pythos-startup-diagnosis-20260925T0842.md` found an idle pipe read and broker nonempty-output prerequisite, but cannot prove exact story input state or a safe replacement key. Host paging is already disabled. Corrected BatchI Glulx notes: empty request sends GlkReturn0xfffffffa, not Z-machine13; actual sending was already correct, so this is not a demonstrated fix. Original source records remain immutable, correction receipt records affected configs/current held manifest. Singer is now checking exact source provenance statically; no live probes/app modifications authorized. Target34 remains, actual33 clients plus one held slot, not34 healthy games.

Enemies cm5v1 supervisor reached its2700s run limit (exit124, SIGTERM; no provider/auth error). Central/remote inboxes empty, old client/wrapper absent, sameSID and fence matched, live broker normal. Under shared scheduling and remote bridge/start locks, archived failed state and log hash then started a fresh client on the same workspace/session. `control/fleet/enemies-timeout-resume-20260925T0848.json`; remote archive `~/lanthorn-muse/history/timeout-20260925T0848/enemies.json`. Fresh e364 GRAB SPRING, e365 SPACE and e367 LOOK AT DESK demonstrate actual resumed output. No broker restart or uncertain replay. Actual process/workspace/shell-web-disabled proof `control/fleet/live-proc-check-20260925T0849.json`:9local+24remote,34brokers, Pytho only unresolved. One export watcher460667 remains, through~11:28UTC.

BatchJ4 parent local/archive-byte/header/raw-guide/normalization/hash/family validation and registration receipt `control/fleet/batch-j-parent-validation.json`: Lecture Feature BlorbZ8R1/200414 vs older unversioned guide, conservatively teacher-feature family; UnderoosZ5R1/970329 guide predates author TADS-to-Inform port; TimeZ8R7/970521 vs guideR5/961014; DetectiveZ5R1/000715 Informport vs AGT guide. Alltrain; parser/edition gaps explicit. Registered before remaining Glulx successors during diagnosis. Five successors remain after Lecture refill. Pasteur preparing bounded4 BatchK, not registered. Snapshot archive coverage now includes generic startup-verification and Pytho failure/diagnosis records. No training, model evaluation, application changes or publication.

## 2026-09-25T08:58:06.543137+00:00 — Batch K source validation and bounded review follow-up

Parent independently reproduced BatchK story/container/member/header/checksum checks and fetched archive bytes for comparison. Raw guide and normalized hashes match, including Baltimore:24 period-space segmentation and exact assembly of Mulldoon's published release6 marble-maze correction into the older release2 guide. Receipt `control/fleet/batch-k-parent-validation.json`; reproducible validator `control/fleet/validate-batch-k-20260925T0858.py`. Registered all four under the shared scheduling lock before the remaining Glulx queue: Busted! Z5R4/941223 with exact-release guide, Earth and Sky Episode1 Z5R2/011204 with author guide archived beforeR2 and unspecified release, Baltimore:24 Z5R2/970706 unversioned guide, The Mulldoon Legacy Z8R6/000724 vs baseguideR2 plus author-attributed R6 maze correction. Alltrain; reserve Earth-and-Sky episodes as earth-and-sky and Mulldoon Legacy/Murders as mulldoon. These are source preparation receipts, not runtime/completion proof. Nine successors queued at this check; source agents idle.

Fresh /proc/workspace/disabled-shell-web evidence in `control/fleet/live-proc-check-20260925T0858.json` confirms9local+24remote actual clients,34live brokers, unchanged Pytho hold and no new transport failure. The held Pytho session remains e4 with no pending request or checkpoint; no key, reset or format substitution. Exactly one export watcher460667 remains; both Pytho timeout rows retain CSV transport quarantine. Routine continued collection does not warrant another failure notification.

Dirac completed120 exact-pair cases:89accepted24revise7quarantine,791raw spans verified. Jigsaw, Save Princeton, Muse Autumn and BiCon independently verified, raising historical conclusions to55 including qualified sample/preview; Vindaloo and Lecture startup remain pending in the next requested bounded120 pass. Review receipt ownership remains with Dirac. No training/evaluation, app changes or publication.

## 2026-09-25T09:14:07.040223+00:00 — three authored finales and Fine-Tuned response exclusions

Parent checked exact raw bytes, SHA256 and response text for BSE `bse-ec63f1779d:e00378` WEST (barn collapse escaped, humanity saved, explicit win60/60); Danger! Adventurer at Work e437 RIDE PONY (cloud/computers/adventures, congratulations) and e438 empty Enter (END OF D.A.A.W.,100%,play-again); WadeWars III: Askin e377 WEST (rescued Uncle and kitchen epilogue) and e378 SPACE (explicitwin100/100), branchb2 after earlier b1death/recovery. Wade's promise to return to Askin is a future installment obligation, not an uncompleted current-game finale. BSE's repeated status/PurpleCow quotation tail is flagged for separate isolated-response attribution review; the finale body is explicit. Receipts `control/ending-parent-verification-20260925T0913-{bse,danger-adventurer-at-work,wadewars-iii-askin}.json`. Parent59 historical authored conclusions includes NinePointsSAMPLE andBedlamPREVIEW; no full content/case coverage claim.

Replacement Underoos Z5R1/970329, Time Z8R7/970521 and Detective Z5R1/000715 headers and startup/early SAVE raw spans verified in `control/{underoos-that-ate-new-york,time-all-things-come-to-an-end,detective}-startup-verification-20260925T0913.json`. Preserve respectively probable TADS-to-Inform guide gap, Time guideR5/961014, and AGT-to-Inform guide gap. Runtime starts do not erase version caveats. Six prepared successors remain; Pasteur is preparing bounded4 BatchL under control/fleet-batch-l-20260925.json and sources/fleet-batch-l-20260925, not yet registered.

Dirac independently confirmed Vindaloo and Lecture startup, reaching56 historical conclusions. Its latest120 cases:87accepted25revise8quarantine,645raw spans verified. Next bounded120 requested with the three new endings/startups. Parent confirmed Dirac's Fine-Tuned e40/e41 attribution finding: GRAB HORSE produces an implicit exit/rolling fragment, and subsequent LOOK receives brake continuation plus GRAB HORSE rejection. Both exact raw spans match hashes but cannot form isolated command-response pairs; added both manual transport exclusions, receipt `control/fleet/fine-tuned-transport-exclusion-20260925T0914.json`. Mechanism unproven; raw evidence unchanged.

Fresh actual process/workspace/shell-weboff verification `control/fleet/live-proc-check-20260925T0913.json` confirms9local+24remote clients and34live brokers. Pytho is the sole unchanged held slot, e4/pendingempty/no checkpoint; no input/reset/substitution. One watcher460667 continues normal refreshes through~11:28UTC. No new runtime failure, application changes, training, evaluation or publication.

## 2026-09-25 09:30 UTC — user-authorized Kimi coordination pilot

Two real Kimi k3 provider passes on Time/Enemies/Traffic/Pytho completed with zero tools. First-pass refill/certification confusion corrected in briefing; second-pass continue/continue/verify/hold decisions matched parent evidence. Raw outputs and parent reviews retained under control/kimi-pilot/{20260925T092417.148209Z,20260925T092601.202521Z}. Five negative harness fixtures passed; fenced-JSON normalization explicit. No automatic actions delegated. Parent independently verified Traffic e233 b3 raw/text/SHA, receipt control/ending-parent-verification-20260925T0927-traffic.json; historical authored conclusions now60 including NinePoints SAMPLE and Bedlam PREVIEW, independent review pending. No extra slot released. Pilot details docs/blog/kimi-coordinator-pilot.md. No training, application changes or publication. BatchL preparation finished but still unregistered pending parent source/family validation.

## 2026-09-25 09:38 UTC — queue, endings and export continuity

Ghost Train e409 and Risorgimento Represso e508 parent raw/text/SHA verified, receipts control/ending-parent-verification-20260925T0934-{ghost-train,risorgimento-represso}.json. Preserve spectral signalman finale and unresolved Blumph/home/paradox future respectively. Parent62 authored conclusions inclsample/preview; newest Christminster/Underoos/Baltimore claims delegated directly to independent Dirac audit. Startup/header/save receipts0935 coverBusted/EarthSkyEpisode1/Baltimore24. Actual9local+24remote,34brokers withonlyPythoheld, receipt control/fleet/live-proc-check-20260925T0935.json.

BatchL actuallocal/archive/member/container/header/checksum/raw-normalization/family validated and registeredunderlock; receipt control/fleet/batch-l-parent-validation.json. TeacherFeature train sharesLecture; InsideWoman train separatefamily pendingadditionalworldevidence (sharedauthoraloneinsufficient); ZorkianStories1 development sharesZork; MysteryFunHouse ScottAdventure7v1.45 train. BatchM4 preparation assignedPasteur, notregistered.

Exportwatcher460667 died after exporter exceeded60seconds, traceback retained runs/pool-export-refresh-1790324920406374866.log. Verified no watcher/exporter, raisedboundedtimeout180s, started sole640478 at~09:34 through~12:34; receipt control/fleet/export-watcher-restart-20260925T0935.json. NormalCSVrefresh succeeded09:35:11 andsubsequently; Pytho3/4 andFineTuned40/41 exclusionsverified. Noexportsemanticchange.

User explicitly requested expandingKimi delegation toconserveparentusage. Singer implementing failclosed pilotfixes and boundedreadonly5minfleetcoordinationloop, not yetdeployed atthisentry. No gameinput/recoveryexecutor; existingdeterministicschedulers/Muse retainownership, independentendingreviewretained. No appchanges/training/publication.


## 2026-09-25 09:50 UTC: second Meta quota hold

All 33 active Muse clients exited with API429 and a provider reset at12:41:27UTC (08:41:27EDT). Parent checked all9local and24remote failedlogs, exact hashes, remote processabsence, and central session/input/pending state. Actual Muse clients are zero; all34brokers remain alive. Both launch enabledflags are false under scheduling.lock, while both managers and mailboxsync remain active. No retries, interpreterreset, uncertaininputreplay, or quota purchase. Receipt: `control/provider-quota-hold-20260925T0950.json`; concise recovery handoff: `control/collection-supervision.md`. Pytho remains separately held. Kimi routine-supervision deployment is still being validated and must not be mistaken for Muse playback or autonomous recovery.


## 2026-09-25 10:05 UTC: expanded Kimi coordination deployed

Kimi now handles routine fleet supervision and ending triage through a singleton loop: one check every five minutes after the previous call finishes, for up to three hours. The corrected fleet call inspected 38 games while Muse was paused for quota. Its saved reply passed policy, session, reference and capacity validation after an explicit, lossless conversion of the exact held-game list to a count. Original outputs and failing receipts remain unchanged. Evidence: `control/kimi-pilot/revalidation-20260925T1004.json` and `control/kimi-pilot/deployment-20260925T1005.json`.

Watcher 763144 was running a fresh cycle at deployment. A failed call stops the loop without automatic retry. Kimi writes proposals; it has no game-command executor, autonomous recovery, ending-certification or publication authority. The first fleet reply omitted supplementary ending references and proposed verification for an unclaimed ending; the profile now explains the required formats. The CLI's resume hint is treated only as informational metadata. All 33 pure harness tests passed.

Kimi found useful evidence: Gerbil Riot had reached its finale at e664 without filing a claim. Dirac independently verified the raw escape narrative and hash. Parent then recorded an administrative finish without sending interpreter input and reconciled the fleet assignment while preventing a sync-write race. Remote provider-failure logs and state were preserved. Receipt: `control/fleet/gerbil-completion-reconciliation-20260925T1005.json`. Gerbil Riot will not resume.

There are 103 started titles and 70 independently verified historical conclusions, including the explicitly labeled Nine Points sample and Bedlam preview. This is not a claim of full content coverage. Muse has zero active clients during the quota hold; 33 unfinished interpreter slots remain, including held Pytho. After the 12:41:27 UTC reset, fresh checks and one successful canary must precede the remaining eight local and 23 remote resumptions. One vacant remote slot can then refill. Both launch flags remain disabled and both managers remain active.

The Codex heartbeat now uses a shorter operational handoff instead of repeating the full history. No total token savings have been measured. Batch N is prepared but unregistered. Export watcher 640478 remains the sole exporter, expiring around 12:34 UTC. No training, application changes or publication occurred.


At 10:09 UTC the fresh scheduled Kimi cycle completed successfully: 37 supplied games, zero active clients, 33 retained slots including Pytho, no launch recommendation. Provider and validation exits were zero, with no output normalization required. Runtime logs confirm `kimi-code/k3` and zero tools. Watcher763144 remains running, with one completed cycle. Evidence: `control/kimi-pilot/20260925T100510.324038Z/{run,validation,decision,parent-review,native-runtime-verification}.json`. Parent noted a prose count ambiguity (Pytho is included in33, not additional) and four already-reviewed historical branch flags; those do not authorize extra work or launches. Structured decisions remain proposals.


## 2026-09-25 10:28 UTC: queue prepared during quota hold

Batch N is parent-validated and registered: Metamorphoses R4/020222 versus the guide's R1/000930 companion; Gourmet R1/030927 with an unversioned author-package guide; BOFH R2/020927 versus an explicit R1/020927 author transcript; and Splashdown R1/040926 with an unversioned author-package guide. Actual local story bytes, headers, checksums, freshly fetched source bytes, normalized guides, companion edition and readme hashes were checked. All four remain in train families. BOFH's explicit series adaptation and remaining relationship uncertainty are documented; shared authorship and a generic XYZZY reference alone do not establish a different game family. Splashdown's trailing QUIT cannot serve as completion evidence. Receipt: `control/fleet/batch-n-parent-validation.json`. Original source records remain unchanged, and runtime compatibility is unproven.

The queue now has eight successors. Both launch flags remain false, preserving the Meta quota hold until the reset and successful canary. No games launched or received input. Kimi has completed three validated scheduled cycles; its latest triage repeats the known quota hold and historical branch-review flags. Both managers, all 33 unfinished brokers and the sole export watcher remain alive with no pending game requests. No new completion, failure, training, application change or publication.


## 2026-09-25 10:34 UTC: central Kimi coordination, hourly parent checks

The user requested leaving coordination with Kimi here and checking back in about an hour. Kimi is already authenticated on the central host, demonstrated by successful local provider calls; this architecture does not require Kimi logins on the Pis. The Pis continue running Muse. Existing Kimi watcher763144 continues its bounded five-minute proposal loop; no duplicate coordinator was started.

The parent heartbeat was changed from15 to60 minutes. Routine coordination stays with Kimi and worker scheduling stays with the existing managers. Exceptional recovery and independent verification remain supervised. The next parent visit should arrange a check just after the12:41:27 UTC Meta quota reset, accounting for the export watcher expiry around12:34 and Kimi watcher expiry around13:05. No Muse retry or provider switch was made. The user's delegation request does not remove Meta's quota limit.


## 11:41 UTC: Kimi timeout diagnosed and redundant quota checks suppressed

The fifth Kimi call, control/kimi-pilot/20260925T104128.748159Z, reached the 300-second provider bound without a reply after four validated cycles. Native logs show a k3 request with zero tools but no visible provider rejection; the nonresponse cause remains unknown. No Kimi orphan processes remained. Original failure bytes and statuses were preserved.

The watcher now performs a fresh deterministic capture before each call. Only an unchanged pre-reset quota hold can reuse the last validated decision as an explicitly historical reference. Full progress, manifests, scheduler settings and raw/journal prefix hashes participate in comparison. State changes or reset arrival require a provider call; bad capture still stops. The bounded provider timeout is now600seconds, not a claim that the provider issue is fixed. Singer ran42 pure tests normally and with Python optimization; actual read-only preflight matched the last successful103142 snapshot. Receipt: control/kimi-pilot/timeout-fix-receipt.json.

Parent verified deployed script hashes and absence of an existing coordinator, then started singleton watcher1165243 at11:41:21 UTC for three hours. Its first actual capture passed and skipped one redundant call: zero new provider calls, zero fresh decisions, no game actions. Prior failed statuses are archived under control/kimi-pilot/watcher-history/20260925T114121.713244Z. Deployment receipt: control/kimi-pilot/deployment-20260925T1141.json.

Fresh health receipt control/fleet/quota-health-20260925T1135.json confirms33 retained live brokers, empty pending queues and unchanged launch flagsfalse. Pytho remains held. Both sync managers and export watcher640478 remain active. No Muse retry or interpreter input occurred. The next parent visit is scheduled just after the12:41:27 UTC reset, approximately12:42 UTC, using a temporary63-minute interval; restore60-minute cadence at that visit. Export watcher640478 expires~12:34; restart exactly one only after confirming absence during the reset visit. The canary-first recovery protocol remains mandatory.


## 2026-09-26 10:53 UTC: new quota hold and expired brokers

The previous handoff was stale. Fresh remote logs show that workers did run after the original hold, then failed with Meta429 reporting a new reset at2026-09-28T00:00:00Z (SundaySeptember27,8p.m.EDT). Six reachablePis have no actual Muse clients; cm5v1 andcm5v2 time out overSSH, so a global zero-client claim is unverified. There are no local Muse clients. New launches are now disabled in both settings, while the singleton managers and mailbox sync remain active. No provider retry or canary was attempted.

The fleet configuration had been changed externally toper_host4 andenabledtrue. Parent preserved the original bytes/settings in control/fleet/recovery-hold-20260926T1045.json and changed onlyenabledfalse under the scheduling lock. Fresh ownership shows35retained unfinishedslots includingPytho; seven centralbrokers are alive and28expired/missing. Do not silently discard ownership or add slots. Reconcile against the authorized34target before future launches. Receipts: control/provider-quota-hold-20260926T1048.json, control/fleet/remote-readiness-20260926T1047.json. The source/authority of the intervening configuration changes is not established here.

After checking ordinary command prompts, no clients on the relevant reachablehosts, empty pendingqueues and exactlivebrokers, parent submitted five unique SAVE requests. AllRoads,Gourmet,BOFH,Splashdown andAliasMagpie confirmedquota-preserve-20260926T1051. Exact rawspans, responsehashes and nonempty savefilehashes are pinned in control/fleet/idle-checkpoint-verification-20260926T1051.json. This is save proof, not restore proof. BlueChairs andMetamorphoses were untouched because their hosts could not be checked. Existing broker lifetimes may end around18:09UTC today.

Singer completed control/recovery-audit-20260926T1045.json: all nine oldlocalbrokers are absent; eight localgames have verified checkpoint candidates, MysteryFunHouse has none. Delusions' latest clean SAVE is olde1538 with no subsequent input, but restoration is untested. No recovery or new session was attempted while quota is held. At reset, expired games need explicit new-session recovery and, forremoteclients, a fenced workspacehandoff with context. Same-broker canary instructions from yesterday no longer apply to expired sessions. Pytho also has no verified save and remains held; never reset or substitute silently.

Kimi watcher1165243 cleanly completed13validatedcalls and12unchangedhold skips, finalcall20260925T142601.070683Z finished14:28UTC yesterday. No currentKimiwatcher exists. It was not blindly renewed: currentcapacity andstaleremotesync fail its capture assumptions, and no provider calls can safely resolve these facts. Last validated proposals are historical only. Exportwatcher3463020 is the sole actualwatcher, started10:29:36UTC today andexpiresabout13:29; exports refreshed10:50.

The parent heartbeat is back to60minutes with this new reset and current blockers, replacing stale63-minute instructions. Dirac is checking only six newendingclaims (Deephome,Schooldays,HLAInform,EarthSkyEpisode1,DashSlapney,ARemoteProblem), no extra casebatch. Claims remain unverified until his report. Prior70historicalconclusions includeNinePointsSAMPLE andBedlamPREVIEW. No application changes, model training, publication or provider switch.


10:53 UTC ending-review completion: Dirac independently verified all six new claims, with83 exact raw event spans checked; historical authored conclusions now76, no duplicate or false finale found. Deephome Part1, Schooldays firstpart and EarthSkyEpisode1 remain installment endings. A Remote Problem succeeds with54minutes remaining, not before the show starts. Receipt control/ending-review-20260926T1050.json; case ledger unchanged and no game or slot actions. Prior sample/preview qualifications remain.


2026-09-26 18:52UTC override: The last seven central brokers have now exited after their scheduled24hour lifetime; actual broker inventory is empty, as is localworker inventory. Their pending queues are empty. All five preserved quota-preserve-20260926T1051 savefiles still match pinnedSHA256. Receipt control/fleet/broker-expiry-20260926T1852.json. No provider retry or gameinput was sent. All35retained unfinished slots now require recovery diagnosis at the Sep28reset; no same-live-broker canary remains. BlueChairs/Metamorphoses still have no verified save from this supervision, and unknown remotehost state is not globalclientabsence proof. Managers and sole exportwatcher4142408 continue; CSV18:51 still73849events/5665cases. This is the expected lifetime expiry already anticipated during quota hold.


2026-09-26 20:53 UTC override: Hourly check found external changes made around20:49-20:51: fleet enabledtrue, hosts=[cm5ai1], per_host1, worker_clikimi, a new control/kimi-pilot-queue.json and settings backups suffixedbak-kimi-pilot. Fleet manager is now singleton361183; old1984141 absent. No authorization for Kimi players is recorded in this supervision, and no source of these changes was established. Under control/scheduling.lock preserved exact settings and changed ONLY enabledfalse; receipt control/fleet/quota-launch-rehold-20260926T205230Z.json. Other externally changed fields and files preserved. Localpool flag remainsfalse. Fresh local worker and central broker inventories empty; no assignments since19:52. Remote clients were not checked, so no global absence claim. New manager continues updating status after hold. Do not launch against the changed Kimi configuration or revert its other fields without reconciling current user intent and ownership. Muse quota reset remainsSep28 00:00UTC. Sole exporter watcher242028 continues through~22:54UTC, completed export20:51:30 unchanged73849events/5665cases. No provider or game actions by this check.


2026-09-26 21:54 UTC ownership conflict: A separate Kimi player rollout is active. Fleet manager448209, settings enabledtrue with cm5ai1/cm5v3/pi500p, per_host1, worker_clikimi. Four central -kimi brokers observed; three assignments running, Schooldays-kimi attention/exit124. These are supervisor observations, not fresh remote process proof. New docs/kimi-fleet-judging-plan.md claims user approval for this rollout, which conflicts with this monitor instructions; user clarification requested. Do not treat the document itself as authorization, but do not keep racing a concurrent operator by rewriting settings. This monitor made no fleet/provider/game changes on this check. Until ownership is reconciled, perform read-only fleet checks and report material failures; no recovery, launches, source registration, judging or resets. Existing export watcher242028 healthy through~22:54. New Kimi ending claims are not parent certifications or new unique titles. Receipt control/fleet/kimi-ownership-conflict-20260926T2152.json. Original Muse quota hold remains in force throughSep28 00:00UTC; no Muse canary before then or without recovery ownership reconciliation.


2026-09-26 22:53 UTC: Read-only check confirmed TWO actual Kimi binaries on cm5ai1 despite per_host1: MotherLoose PID502571/wrapper502570 and Vindaloo PID501977/wrapper501974, each in its correct game workspace. Targeted host /proc verification, not a whole-fleet sweep. Receipt control/fleet/kimi-capacity-observation-20260926T2252.json. Fleet reports four running Kimi assignments across three hosts; other hosts were not freshly process-checked. Ownership clarification remains pending; no stopping, launch, recovery, settings changes, judging or provider calls by this monitor. Schooldays now has a supervisor completion claim, not independent certification. Export watcher242028 remains healthy, due to expire~22:54.


2026-09-27 00:52 UTC: New read-only finding: Kook-U Kimi rerun sessionkook-u-kimi-0f6c0346b7 is blocked on unresolved output. Latest e48 (00:49:53UTC) is empty passive delayed_output/no_output_timeout following e47; receipt control/fleet/kook-u-kimi-output-timeout-20260927T0052.json. Broker remains present; fleet flags await_output-only. No input, recovery, worker change or provider call by monitor. This rerun is separate from the already verified original Kook-U completion. Ownership clarification remains pending. Export watcher705557 remains sole and healthy; latest export00:51:44UTC.


2026-09-27 01:53 UTC: New failure: fleet reports20 Kimi assignments attention/failed. Targeted read-only stderr check on cm5ai1 i-0-kimi confirms provider.auth_error403 explicitly stating the five-hour usage limit was reached; no exact reset time supplied. Do not misclassify this sample as bad credentials or infer a new Muse reset. Receipt control/fleet/kimi-quota-failure-20260927T0152.json. Fleet manager changed externally to842001; launch setting remainstrue, no fleet mutations/retries by this monitor under pending ownership clarification. Preserve evidence and do not purchase, upgrade, switch providers or blindly retry. Export watcher705557 remains healthy, latest01:52:09 export77823events/5903candidatecases; these are not accepted counts.


2026-09-27 03:52 UTC: Separate operator resumed Kimi collection. Fleet manager now1157955; status18complete claims/3running/13ready, no current errors. Fresh central SpaceStation e46 AFT and Traffic e7 X BUS responses at03:52/03:51 prove renewed interpreter activity; Pentari latest is fresh help. Receipt control/fleet/kimi-progress-observation-20260927T0352.json. This is progress evidence, not proof of global provider quota availability, remote process inventory or independent endings. Monitor remains read-only pending ownership clarification and made no recovery/provider/game actions. Sole exportwatcher1052172 remains healthy until~05:53UTC.


2026-09-27 08:53 UTC: Detected overlapping export watchers1430155 (owned by this monitor) and1757381 (external), each with an active exporter. Verified exact /proc argv/cwd and original launch receipt, then SIGTERM only own watcher1430155; in-flight exporters allowed to finish. Subsequent check confirms sole watcher1757381 and one current exporter1773670; prior exporter processes absent. Last completed export08:52:34 with81844events/6152candidatecases. Receipt control/fleet/export-watcher-overlap-20260927T0852.json. No fleet/provider/game actions; ownership clarification still pending. Do not renew against the now-stale own watcherPID; check all watcher/exporter processes and current external watcher lifetime first. Overlap resolved; no claim of full dataset integrity audit.


2026-09-28 14:10 UTC read-only override: Separate operator fleet nowworker_climuse oncm5ai1/pi500p, per_host1, manager656242. Frozen-kimi reports missing/duplicatebroker and stale sync10:48 despite running label; BOFH-kimi mailbox explicitly rejects session mismatch; Gumshoe-kimi sync current. No resets/worker mutations attempted. Export watcher/exporter absent, last completed CSV12:28:49UTC. Shared watch_exports.py now also executes pg_import.py, which truncates/reloads local Postgres tables; this monitor did not renew the expanded workflow under unresolved ownership. Receipt control/fleet/monitor-observation-20260928T1408.json. Further checks must not repeat these notifications unless state changes. Muse reset date having passed is not recovery authorization/readiness.
