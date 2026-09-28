#!/usr/bin/env bash
set -euo pipefail
experiment_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
game_id="${1:?Usage: ./run-fullplay.sh game-id}"
[[ "$game_id" =~ ^[a-z0-9-]+$ ]] || exit 2
workspace="$experiment_dir/play/$game_id"
[[ -f "$workspace/latest.json" ]] || { echo 'Interpreter is not ready'; exit 1; }
# One launcher per game; a continuation never starts a second interpreter.
exec 9> "$workspace/muse-worker.lock"
flock -n 9 || { echo 'A Muse launcher already owns this game'; exit 2; }
for segment in {1..12}; do
 [[ ! -f "$workspace/ending-claim.json" ]] || break
 # A clean model stop can precede a slow interpreter's response. Wait for the
 # existing request, without sending or replaying any game command.
 python3 - "$workspace" <<'PYWAIT'
import json, sys, time
from pathlib import Path
base = Path(sys.argv[1]); deadline = time.monotonic() + 200
while True:
    pending = [p for p in (base/'inbox').glob('*.json')
               if not (base/'responses'/p.name).exists()]
    if not pending:
        break
    if time.monotonic() >= deadline:
        print('Pending requests still unresolved; supervisor needed: ' + ', '.join(p.name for p in pending), flush=True)
        raise SystemExit(75)
    time.sleep(2)
PYWAIT
 run_dir="$(mktemp -d "$experiment_dir/runs/fullplay-$game_id-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")"
 cp "$experiment_dir/prompts/fullplay.md" "$run_dir/prompt.md"
 printf '\nGame: %s. Continuation segment %s. Start by reading this workspace latest.json, manifest.json and progress.md if present.\n' "$game_id" "$segment" >> "$run_dir/prompt.md"
 printf 'GAME=%s RUN_DIR=%s\n' "$game_id" "$run_dir"
 set +e
 timeout --signal=TERM --kill-after=10s 2700s \
  muse exec --provider meta --workspace "$workspace" --prompt-file "$run_dir/prompt.md" \
  --json --max-model-steps 400 --max-tool-output-bytes 262144 --approval-mode never \
  --disable-shell --disable-web-tools --no-foreign-personal-context \
  > "$run_dir/events.jsonl" 2> "$run_dir/stderr.log"
 run_status=$?
 printf '%s\n' "$run_status" > "$run_dir/exit.status"
 set -e
 [[ "$run_status" == 0 ]] || { printf 'Run stopped with exit %s\n' "$run_status"; exit "$run_status"; }
 # A clean early finish with an incomplete game can continue from the real state.
 [[ ! -f "$workspace/ending-claim.json" ]] || break
done
