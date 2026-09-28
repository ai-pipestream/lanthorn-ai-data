#!/usr/bin/env bash
set -euo pipefail
experiment_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$experiment_dir"
transcript="$(realpath "${1:?Usage: ./run-candidates.sh transcripts/game-opening}")"
run_dir="$(mktemp -d "$experiment_dir/runs/questions-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")"
cat prompts/questions.md > "$run_dir/prompt.md"
printf '\nTranscript: %s/passages.jsonl\nManifest: %s/manifest.json\nRUN_ID: %s\nOutput JSONL: %s/candidates.jsonl\n' "$transcript" "$transcript" "$(basename "$run_dir")" "$run_dir" >> "$run_dir/prompt.md"
printf 'RUN_DIR=%s\n' "$run_dir"
set +e
timeout --signal=TERM --kill-after=10s 1200s \
 muse exec --provider meta --workspace "$experiment_dir" \
 --prompt-file "$run_dir/prompt.md" --json --max-model-steps 40 \
 --max-tool-output-bytes 262144 --approval-mode never \
 --disable-shell --disable-web-tools --no-foreign-personal-context \
 > "$run_dir/events.jsonl" 2> "$run_dir/stderr.log"
run_status=$?
printf '%s\n' "$run_status" > "$run_dir/exit.status"
printf 'Muse exit=%s; candidates: %s/candidates.jsonl\n' "$run_status" "$run_dir"
exit "$run_status"
