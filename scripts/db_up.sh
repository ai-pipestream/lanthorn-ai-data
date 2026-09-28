#!/bin/bash
# Bring up the lanthorn Postgres container (PostgreSQL 18) from scratch.
# Idempotent: existing healthy container is left alone. Password lives in
# ~/.config/lanthorn/pg.env (NOT in the repo).
set -euo pipefail
cd "$(dirname "$0")/.."
envfile="$HOME/.config/lanthorn/pg.env"
if [ ! -f "$envfile" ]; then
  mkdir -p "$HOME/.config/lanthorn"
  printf 'POSTGRES_PASSWORD=%s\n' "$(head -c 24 /dev/urandom | base64)" > "$envfile"
  chmod 600 "$envfile"
  echo "generated $envfile"
fi
source "$envfile"
if ! docker ps --format '{{.Names}}' | grep -qx lanthorn-db; then
  docker rm -f lanthorn-db >/dev/null 2>&1 || true
  docker run -d --name lanthorn-db --restart unless-stopped \
    -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" -e POSTGRES_USER=lanthorn \
    -e POSTGRES_DB=lanthorn -v lanthorn-pg18:/var/lib/postgresql \
    -p 127.0.0.1:5433:5432 postgres:18-alpine >/dev/null
  for i in $(seq 1 30); do
    docker exec lanthorn-db pg_isready -U lanthorn >/dev/null 2>&1 && break
    sleep 1
  done
fi
python3 scripts/pg_import.py
