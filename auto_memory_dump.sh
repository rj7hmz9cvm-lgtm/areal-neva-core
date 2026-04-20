#!/bin/bash
cd /root/.areal-neva-core
/root/.areal-neva-core/.venv/bin/python3 /root/.areal-neva-core/orchestra_full_dump.py >> /root/.areal-neva-core/logs/auto_dump.log 2>&1
