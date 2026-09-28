# Lanthorn recall training experiment

This workspace is for collecting and reviewing training candidates for an
interactive-fiction recall retriever. The application checkout is
`/work/reference-code/lanthorn`; this experiment does not modify it.

The first milestone is a small, traceable pilot, not a trained model.

## Workflow

1. Find a walkthrough and identify the exact game release it describes.
2. Use it to guide a real playthrough. Capture commands and game responses,
   including failed actions and save/restore branches.
3. Generate questions whose supporting passages exist in that captured text.
4. Validate source references mechanically and review relevance labels.
5. Compare baseline retrieval before deciding whether to train.

Walkthrough prose can guide collection. It is not evidence that a player saw a
particular game response. Generated examples remain candidates until reviewed.

## Layout

- `sources/`: source inventory, URLs, provenance, release/version and reuse notes.
- `transcripts/`: captured game output, stable passage IDs and turn/branch IDs.
- `candidates/`: unreviewed question/passage/negative records.
- `reviewed/`: accepted labels and review decisions.
- `evaluation/`: games and query sets held out from training and threshold tuning.
- `prompts/`: bounded Muse task briefs.
- `runs/`: timestamped Muse JSON event streams.

## Muse

Installed interface verified with Muse Code 1.3.0 help. `muse exec` accepts
`--workspace`, `--prompt-file`, `--json` and `--max-model-steps`.

The initial discovery pilot completed but did not verify walkthrough bodies. Its
records and Terra review remain in `sources/pilot-*` and `runs/pilot-review.md`.
The revised prompt tells Muse to read its saved full fetch outputs, supplies
explicit acceptance criteria, and records commands for a real interpreter smoke.

```sh
./run-sources.sh batches/single.json
./run-sources.sh batches/five-01.json
python3 scripts/validate_sources.py runs/<source-run>
python3 scripts/capture_opening.py runs/<source-run>/records/<game>.json /absolute/story/path --out transcripts/<unique-capture>
./run-candidates.sh transcripts/<unique-capture>
python3 scripts/validate_candidates.py runs/<question-run> transcripts/<unique-capture>
```

Source batches contain at most five games after the single-game pilot. The
runner retains per-run prompts, assignments, individual records, event traces,
stderr and exit status. Each batch has a 30-minute limit and 60 model steps per
game. A successful process exit alone does not pass the batch. The validator
checks schema and successful fetch events; Terra checks actual evidence. Opening
captures record exact bytes, input order and binary/story hashes. An opening
smoke does not establish compatibility for a complete walkthrough.

Question runs are separate, with web and shell disabled, and use only captured
transcripts. A 20-minute / 40-step cap limits each question run. The split registry
is assigned before generation. Candidates are never automatically accepted or
used for training. Neither launcher publishes data or modifies the application.
Shell remains disabled for Muse; the parent owns the capture/validation scripts.
A step limit is not a token or cost budget.

A live Meta-provider connection check returned `MUSE_CONNECTION_OK` using
`muse-spark-1.3-contributor`. Live discovery has also exercised web fetch and file
writes. No claim is made about the account's remaining token allowance.

For interactive work:

```sh
muse --workspace /work/experiments/lanthorn-recall-training
```

`muse resume <session-id>` resumes an existing conversation. Active sessions can
be found with `muse session-message list --json`; follow-ups can be sent with
`muse session-message send --target <session-id> --json` using stdin for the body.
Do not message unrelated existing sessions.

If authentication or a workspace permission blocks a run, record the error.
Do not disable the sandbox to make the run succeed.

## Full-play test-data collection

The current objective is synthetic test data for recall and command assistance,
not a benchmark of Muse's playing ability. The nineteen-game scope is the Zork/Dungeon
Inform 7 port, Hitchhiker's Guide, Adventureland, Pirate Adventure, Lost Pig,
Photopia, Shade, Suveh Nux, Secret Mission, Voodoo Castle, The Dreamhold, Bronze,
9:05, Violet, Slouching Towards Bedlam, Anchorhead, Curses, Theatre and Savoir-Faire.
A genuine ending needs
independent review; deaths, quitting, scores in mid-game, and model claims do
not count as completion.

`run-fullplay.sh GAME_ID` gives Muse a persistent real interpreter controlled by
`scripts/play_broker.py`. The model has web and shell disabled. It writes unique
requests in `play/GAME_ID/inbox/` and reads matching broker-owned responses.
The broker records exact output bytes and append-only JSON events. Do not launch
a second worker for a game that already has one. Each launcher allows up to twelve
45-minute / 400-step segments. New-game brokers run for up to twelve hours;
recovery brokers and CSV watchers have separate shorter bounds. The app follow-up checks every 15 minutes and can recover an incomplete
run while preserving its actual state and provenance.

Walkthroughs stay in `control/`. Muse requests small excerpts through a logged
help action. Help text never becomes player-observed recall evidence. Deliberate
mistakes use `origin=synthetic_probe`; accepted alternative wording is recorded
as accepted, not invented failure. A correction must preserve intent, and a
successful parse alone does not establish the intended world effect. This is
model-generated test input, not a sample of real human mistakes.

Live outputs:

- `exports/events.csv`: actual commands/responses, help requests and provenance.
- `exports/test-cases.csv`: linked failed/recovery candidates and review status.
- `play/*/events.jsonl` and `stdout.raw`: original records and exact bytes.
- `reviewed/fullplay-cases.json`: independent review decisions.

CSV snapshots refresh about every 45 seconds through
`scripts/watch_exports.py`. Their UTC timestamps are normalized to milliseconds;
JSON preserves the original timestamp precision. CSV fields are quoted, including
multiline game responses. Only an independently accepted row is an accepted test
case. Delayed output and its following command are quarantined as potentially
interleaved, never exported as a clean isolated repair.

The export can be refreshed manually with the bundled Node runtime and
`scripts/export_dataset.mjs`. No model is trained and nothing is published.

## Blog working record

The [experiment journal and evidence](docs/blog/README.md) track acquisition,
capture, testing, review and setbacks. The model plan is explicitly future work.
