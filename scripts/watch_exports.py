#!/usr/bin/env python3
"""Refresh CSV snapshots while the authorized game collection is active."""
from pathlib import Path
import subprocess
import time
root=Path(__file__).resolve().parent.parent
node='/home/krickert/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
end=time.monotonic()+3*3600
while time.monotonic()<end and not (root/'control'/'stop-exports').exists():
    # The growing corpus exceeded 60 seconds at ~65,000 events. Keep a bounded
    # export timeout while allowing the normal table serialization to finish.
    result=subprocess.run([node,str(root/'scripts/export_dataset.mjs')],cwd=root,capture_output=True,text=True,timeout=180)
    (root/'exports'/'refresh.log').write_text(result.stdout+result.stderr)
    if result.returncode:raise SystemExit(result.returncode)
    # Best-effort Postgres refresh; a DB hiccup must never kill the export loop.
    subprocess.run(['python3',str(root/'scripts/pg_import.py')],cwd=root,capture_output=True,text=True,timeout=300)
    time.sleep(45)
