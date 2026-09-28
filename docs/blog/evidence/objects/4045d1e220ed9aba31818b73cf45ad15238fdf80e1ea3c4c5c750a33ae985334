#!/usr/bin/env bash
set -euo pipefail
experiment_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$experiment_dir"
batch="${1:?Usage: ./run-sources.sh batches/single.json}"
run_dir="$(mktemp -d "$experiment_dir/runs/sources-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")"
mkdir "$run_dir/records"
cp "$batch" "$run_dir/assignment.json"
cat prompts/source-verification.md > "$run_dir/prompt.md"
printf '\nASSIGNMENT (only these games):\n' >> "$run_dir/prompt.md"
cat "$batch" >> "$run_dir/prompt.md"
printf '\nOUTPUT_DIR: %s/records\n' "$run_dir" >> "$run_dir/prompt.md"
printf 'RUN_DIR=%s\n' "$run_dir"
step_limit="$(python3 -c 'import json,sys; print(60*len(json.load(open(sys.argv[1]))["games"]))' "$batch")"
set +e
timeout --signal=TERM --kill-after=10s 1800s \
 muse exec --provider meta --workspace "$experiment_dir" \
 --prompt-file "$run_dir/prompt.md" --json --max-model-steps "$step_limit" \
 --max-tool-output-bytes 262144 --approval-mode never \
 --disable-shell --no-foreign-personal-context \
 > "$run_dir/events.jsonl" 2> "$run_dir/stderr.log"
run_status=$?
printf '%s\n' "$run_status" > "$run_dir/exit.status"
set -e
printf 'Muse exit=%s; records: %s\n' "$run_status" "$run_dir/records"
exit "$run_status"
