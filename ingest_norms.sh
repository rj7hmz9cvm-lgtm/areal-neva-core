#!/bin/bash
set -euo pipefail

FOLDER="${1:-}"
PY="/root/.areal-neva-core/.venv/bin/python3"
BASE="/root/.areal-neva-core"

if [ -z "$FOLDER" ]; then
  echo "УКАЖИ ПАПКУ С PDF"
  exit 1
fi

for f in "$FOLDER"/*.pdf; do
  [ -e "$f" ] || continue
  echo "ЗАГРУЗКА $f"
  "$PY" "$BASE/normative_engine.py" "$f"
done

echo "БАЗА НОРМ ОБНОВЛЕНА"
