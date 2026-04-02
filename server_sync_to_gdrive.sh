#!/usr/bin/env bash
set -euo pipefail

SRC=/root/AI_ORCHESTRA/telegram
DST='gdrive:AI_ORCHESTRA/telegram'
LOG=/root/.areal-neva-core/logs/rclone_sync.log
LOCK=/tmp/ai_orchestra_gdrive_sync.lock

mkdir -p /root/.areal-neva-core/logs

exec 9>"$LOCK"
flock -n 9 || exit 0

{
  echo "===== $(date '+%F %T') START ====="

  rclone copy "$SRC" "$DST" \
    --create-empty-src-dirs \
    --fast-list \
    --transfers 8 \
    --checkers 16 \
    --checksum \
    --update \
    --exclude ".DS_Store" \
    --exclude "Thumbs.db" \
    --exclude ".git/**" \
    --exclude "__pycache__/**" \
    --exclude "*.pyc" \
    --exclude "*.tmp" \
    --exclude "*.swp" \
    --exclude "tmp/**" \
    --log-level INFO

  echo "===== $(date '+%F %T') DONE ====="
  echo
} >> "$LOG" 2>&1
