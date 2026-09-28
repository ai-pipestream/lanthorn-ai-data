#!/usr/bin/env bash
set -euo pipefail
experiment_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$experiment_dir/runs"
run_log="$(mktemp "$experiment_dir/runs/pilot-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX.jsonl")"
printf 'Muse event log: %s\n' "$run_log"
cd "$experiment_dir"
timeout --signal=TERM --kill-after=10s "${MUSE_RUN_TIMEOUT:-600s}" \
  muse exec --provider meta --workspace "$experiment_dir" \
  --prompt-file "$experiment_dir/prompts/pilot.md" \
  --json --max-model-steps 12 --approval-mode never \
  --disable-shell --no-foreign-personal-context \
  2> "${run_log%.jsonl}.stderr" | tee "$run_log"
