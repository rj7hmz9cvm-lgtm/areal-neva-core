#!/bin/bash
# verify_local_bot_api.sh
# PATCH_TELEGRAM_BIG_FILE_LOCAL_BOT_API_V1 — activation gate
#
# Run all 4 checks before activating wrapper.
# Exit 0 = all OK, ready to activate.
# Exit 1 = not ready, do NOT activate.

set -e
PASS=0
FAIL=0
CRED_FILE="/etc/areal/telegram-local-api.env"
BINARY="/usr/local/bin/telegram-bot-api"
SERVICE="telegram-bot-api-local.service"
WRAPPER="/root/.areal-neva-core/areal_telegram_wrapper.py"
PENDING="/root/.areal-neva-core/tmp/bigfile_ingress_override.conf.pending"
OVERRIDE_DIR="/etc/systemd/system/telegram-ingress.service.d"

echo "=== PATCH_TELEGRAM_BIG_FILE_LOCAL_BOT_API_V1 — Activation Gate ==="
echo ""

# ── Check 1: binary ───────────────────────────────────────────────────────────
echo "1. Binary..."
if [ -x "$BINARY" ]; then
    VER=$("$BINARY" --version 2>/dev/null || echo "built")
    echo "   OK: $BINARY ($VER)"
    PASS=$((PASS+1))
else
    echo "   FAIL: $BINARY not found or not executable"
    FAIL=$((FAIL+1))
fi

# ── Check 2: service active ───────────────────────────────────────────────────
echo "2. Service telegram-bot-api-local..."
if systemctl is-active "$SERVICE" >/dev/null 2>&1; then
    echo "   OK: $SERVICE is active"
    PASS=$((PASS+1))
else
    STATUS=$(systemctl is-active "$SERVICE" 2>/dev/null || echo "unknown")
    echo "   FAIL: $SERVICE status=$STATUS"
    FAIL=$((FAIL+1))
fi

# ── Check 3: local getMe ──────────────────────────────────────────────────────
echo "3. Local getMe..."
source "$CRED_FILE" 2>/dev/null || true
BOT_TOKEN=$(systemctl show telegram-ingress -p Environment --value 2>/dev/null | \
    tr ' ' '\n' | grep "^TELEGRAM_BOT_TOKEN=" | cut -d= -f2- | head -1)
if [ -z "$BOT_TOKEN" ]; then
    # Try from running process
    PID=$(systemctl show telegram-ingress -p MainPID --value 2>/dev/null)
    BOT_TOKEN=$([ -n "$PID" ] && grep -z "TELEGRAM_BOT_TOKEN" /proc/$PID/environ 2>/dev/null \
        | tr '\0' '\n' | grep "^TELEGRAM_BOT_TOKEN=" | cut -d= -f2- | head -1 || echo "")
fi
if [ -n "$BOT_TOKEN" ]; then
    RESULT=$(curl -s --max-time 5 "http://localhost:8081/bot${BOT_TOKEN}/getMe" 2>/dev/null)
    if echo "$RESULT" | /root/.areal-neva-core/.venv/bin/python3 -c \
        "import sys,json; d=json.load(sys.stdin); assert d.get('ok'), 'not ok'" 2>/dev/null; then
        USERNAME=$(echo "$RESULT" | /root/.areal-neva-core/.venv/bin/python3 -c \
            "import sys,json; d=json.load(sys.stdin); print(d['result'].get('username','?'))" 2>/dev/null)
        echo "   OK: getMe → @${USERNAME}"
        PASS=$((PASS+1))
    else
        echo "   FAIL: getMe returned error or timeout"
        FAIL=$((FAIL+1))
    fi
else
    echo "   SKIP: BOT_TOKEN not found — cannot test getMe (manual check required)"
    FAIL=$((FAIL+1))
fi

# ── Check 4: wrapper dry-run ──────────────────────────────────────────────────
echo "4. Wrapper imports dry-run..."
/root/.areal-neva-core/.venv/bin/python3 -c "
import sys, os
os.environ.setdefault('TELEGRAM_LOCAL_API_BASE', 'http://localhost:8081')
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession
srv = TelegramAPIServer.from_base('http://localhost:8081')
sess = AiohttpSession(api=srv)
# Verify pattern exists in daemon
daemon = open('/root/.areal-neva-core/telegram_daemon.py').read()
pattern = 'url = f\"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}\"'
assert pattern in daemon, 'download URL pattern not found in telegram_daemon.py'
print('   OK: aiogram local server imports ok, daemon pattern ok')
" && PASS=$((PASS+1)) || { echo "   FAIL: wrapper dry-run failed"; FAIL=$((FAIL+1)); }

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "=== Results: $PASS/4 passed, $FAIL failed ==="
echo ""

if [ "$FAIL" -eq 0 ]; then
    echo "ALL CHECKS PASSED — ready to activate"
    echo ""
    echo "Activation (requires explicit confirmation):"
    echo "  mkdir -p $OVERRIDE_DIR"
    echo "  cp $PENDING $OVERRIDE_DIR/bigfile.conf"
    echo "  systemctl daemon-reload"
    echo "  systemctl restart telegram-ingress"
    echo ""
    exit 0
else
    echo "NOT READY — do NOT activate wrapper"
    echo ""
    exit 1
fi
