#!/bin/bash
set -e

LOG=~/.areal-neva-core/data/memory/LOGS/kordon_orchestra_agent.log
AGENT=~/.areal-neva-core/data/memory/DEVOPS_AUTOMATION/kordon_orchestra_agent.py

mkdir -p ~/.areal-neva-core/data/memory/LOGS
mkdir -p ~/AI_ORCHESTRA/telegram/"кордон СНТ"/{фото,документы,tmp}

echo "===== START AGENT =====" >> $LOG
date >> $LOG

pkill -9 -f kordon_orchestra_agent.py 2>/dev/null || true

nohup python3 $AGENT >> $LOG 2>&1 &
echo $! > ~/.areal-neva-core/kordon_agent.pid

echo "AGENT_STARTED PID=$(cat ~/.areal-neva-core/kordon_agent.pid)"
