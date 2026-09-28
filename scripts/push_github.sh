#!/bin/bash
# Publish a curated snapshot (code + dataset exports + judgments) to
# github.com/ai-pipestream/lanthorn-ai-data. Raw run archives stay off GitHub;
# full history lives on the cm5v3 backup remote.
set -euo pipefail
src=/work/experiments/lanthorn-recall-training
stage=/work/experiments/lanthorn-ai-data-public
mkdir -p "$stage"
rsync -a --delete \
  --exclude '__pycache__' --exclude 'node_modules' --exclude '*.pyc' --exclude '*.lock' \
  --include '*/' \
  --include 'scripts/***' --include 'prompts/***' --include 'docs/***' \
  --include 'exports/***' --include 'reviewed/***' --include 'batches/***' \
  --include 'transcripts/***' \
  --include 'README.md' --include 'BRIEF.md' --include 'LICENSE' --include 'run-*.sh' \
  --exclude '*' \
  "$src/" "$stage/"
cd "$stage"
if [ ! -d .git ]; then
  git init -b main >/dev/null
  git remote add origin https://github.com/ai-pipestream/lanthorn-ai-data.git
fi
git add -A
git -c user.name='lanthorn-fleet' -c user.email='fleet@lanthorn.local' \
  commit -m "snapshot $(date -u +%Y-%m-%dT%H:%MZ)" --quiet
git push origin main "$@"
