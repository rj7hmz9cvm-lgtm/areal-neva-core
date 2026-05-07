#!/usr/bin/env bash
set -Eeuo pipefail
cd /root/.areal-neva-core

set -a
set +u
[ -f .env ] && . ./.env
set -u
set +a

exec /root/.areal-neva-core/.venv/bin/python3 /root/.areal-neva-core/tools/full_context_aggregator_guard.py "$@"
