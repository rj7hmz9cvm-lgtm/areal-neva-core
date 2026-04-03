#!/bin/bash
set -e
cd /root/.areal-neva-core || exit 1
git add -A
git diff --cached --quiet && exit 0
git commit -m "auto-sync $(date +%F_%T)" || exit 0
git push origin main --force
