#!/bin/bash
# Nightly pg_dump of the lanthorn container DB onto the NAS (/work/shared-docs).
set -euo pipefail
source "$HOME/.config/lanthorn/pg.env"
out=/work/shared-docs/lanthorn-db-dumps
mkdir -p "$out"
f="$out/lanthorn-$(date -u +%Y%m%dT%H%M%SZ).sql.gz"
docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" lanthorn-db \
  pg_dump -U lanthorn -d lanthorn | gzip > "$f.tmp"
mv "$f.tmp" "$f"
ls -t "$out"/lanthorn-*.sql.gz | tail -n +15 | xargs -r rm -f
echo "$f"
