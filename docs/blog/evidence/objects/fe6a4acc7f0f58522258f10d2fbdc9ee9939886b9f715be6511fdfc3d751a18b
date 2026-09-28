# Collection and testing method

## Acquisition and identity

Retain story hashes, release banners, interpreter identity and acquisition URLs
where known. A title alone does not identify a release. Preserve fetched guide
bytes, access times, hashes and compatibility/reuse notes. Mark unknowns as
unknown. An opening smoke test cannot establish full-guide compatibility.

Expansion source manifests live under `sources/expansion-20260925/`; runtime
manifests under `play/`. Earlier source receipts remain in `sources/` and `runs/`.
Do not reconstruct an original download URL merely from a file's present path.

## Muse and the broker

Muse uses each game workspace with shell and web tools disabled. It submits
unique requests to a parent-controlled broker that drives the real interpreter.
A per-game worker lock prevents duplicate launchers. Requests, responses, raw
stdout and append-only events preserve what actually ran. These tool restrictions
are not a claim of adversarial isolation from every file.

Walkthrough excerpts arrive through logged help requests. Supervisor hints are
also recorded. Neither is player-observed recall evidence. Workers label synthetic
mistakes and link their declared intent to actual failed/recovery responses.

The launcher currently permits twelve 45-minute, 400-step segments. Those are
execution bounds, not token or cost budgets. Preserve per-run prompts, available
provider/model identifiers, stderr and exit status. A clean process exit proves
neither story completion nor correct labels.

## State and response attribution

Events carry stable IDs, session/branch identity and raw byte spans with SHA-256.
Restore/restart creates explicit branches; recovery from a dead broker uses a
new session and confirmed checkpoint provenance. An unanswered request may have
executed; never blindly replay it.

The transport checks stdin readiness rather than a quiet interval alone. After
timeout it blocks new input until output is collected. Ordinary command prompts,
question prompts and key pauses still differ. Save only at a suitable prompt and
require successful engine evidence before describing a checkpoint as recoverable.

## Review policy

Terra reviews exact event pairs against raw responses. Dispositions are accepted,
revise, quarantine or unreviewed. Review checks that failure actually occurred,
the recovery preserves intent, session/branch context supports the pairing and
the claimed world effect is visible. A valid action blocked by a locked door is
not necessarily a vocabulary error. Changing the action is planning assistance,
not wording repair.

Accepted cases can document successful alternatives or state constraints as well
as repairs. Later model preparation must select task-specific examples. A second
model's review has limits too; human spot-checking remains necessary before
publishing quality claims.

## Mechanical checks and CSV

`test_broker_transport.py` tests real subprocess pipes: quiet fragments are not
input readiness, timeout blocks commands/checkpoints until output is collected,
and exited engines are not command prompts.

```sh
PYTHONPATH=scripts python3 -m unittest discover -s scripts -p test_broker_transport.py -v
```

`validate_sources.py` checks source/fetch receipts. `validate_candidates.py`
checks references and split constraints in the earlier recall pipeline. Neither
proves semantic relevance. `export_dataset.mjs` joins reviews to matching
evidence and writes quoted multiline CSV with literal-text and readback checks.

`snapshot_experiment.py` checks every recorded response against its raw span,
records exact journal/raw prefix lengths and hashes, and archives small harness,
prompt and review artifacts. Hash integrity cannot repair uncertain causal
attribution from an earlier transport bug; quarantine still applies. Live CSV
and reviewer snapshots can lag the event journals.

## Limits for the public account

These probes are model-generated, not observed human errors. Hints, prior model
knowledge, game selection and retries shape coverage. This is neither a blind
trial nor a measure of unaided Muse skill. Large event counts establish neither
model improvement nor cheap generation. Report measured costs only if accounting
records exist; a model-step limit does not reveal token allowance or spend.
