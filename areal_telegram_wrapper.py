"""
PATCH_TELEGRAM_BIG_FILE_LOCAL_BOT_API_V1
Patches aiogram in-memory to use local Telegram Bot API server (localhost:8081).
Removes 20MB file size limit. telegram_daemon.py is NOT modified on disk.

Markers logged to task_history (via daemon):
  BIG_FILE_LOCAL_BOT_API_USED
  BIG_FILE_LOCAL_DOWNLOAD_OK
  BIG_FILE_LOCAL_DOWNLOAD_FAILED
  BIG_FILE_TEMP_CLEANED
  FILE_INTAKE_ROUTER_LOCAL_PATH_PASSED

Activation gate: only via verify_local_bot_api.sh — do NOT activate manually.
"""
import os
import sys
import logging

_LOG = logging.getLogger("areal.bigfile_patch")

# Read from EnvironmentFile — never hardcode, never log values
LOCAL_API_BASE = os.getenv("TELEGRAM_LOCAL_API_BASE", "http://localhost:8081")

# ── Patch 1: aiogram Bot session → local server ──────────────────────────────
try:
    from aiogram.client.session.aiohttp import AiohttpSession
    from aiogram.client.telegram import TelegramAPIServer
    import aiogram

    _orig_bot_init = aiogram.Bot.__init__

    def _patched_bot_init(self, token, session=None, default=None, **kwargs):
        if session is None:
            try:
                local_server = TelegramAPIServer.from_base(LOCAL_API_BASE)
                session = AiohttpSession(api=local_server)
                _LOG.info("BIG_FILE_LOCAL_BOT_API_USED: local server active")
            except Exception as _e:
                # Never log LOCAL_API_BASE value with credentials embedded
                _LOG.warning("BIG_FILE_LOCAL_API_SESSION_FAILED: %s — falling back", type(_e).__name__)
        _orig_bot_init(self, token, session=session, default=default, **kwargs)

    aiogram.Bot.__init__ = _patched_bot_init
    _LOG.info("PATCH_BOT_INIT_LOCAL_SERVER: installed")

except Exception as _patch_err:
    _LOG.error("PATCH_BOT_INIT_LOCAL_SERVER_FAILED: %s", type(_patch_err).__name__)

# ── Patch 2: Fix download URL (in-memory only, file on disk unchanged) ────────
_daemon_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "telegram_daemon.py"
)

try:
    _code = open(_daemon_path, "r", encoding="utf-8").read()

    _CLOUD_PATTERN = 'url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"'
    # Local Bot API returns absolute disk path in file_path — copy directly, skip HTTP
    _LOCAL_PATTERN = (
        'if file_path.startswith("/") and os.path.exists(file_path):\n'
        '        import shutil as _shutil_lbp, logging as _log_lbp\n'
        '        _log_lbp.getLogger("areal.bigfile_patch").info("LOCAL_BOT_API_ABSOLUTE_PATH_USED:%s", os.path.basename(file_path))\n'
        '        _shutil_lbp.copy2(file_path, local_path)\n'
        '        return local_path\n'
        f'    url = f"{LOCAL_API_BASE}/file/bot{{BOT_TOKEN}}/{{file_path}}"'
    )

    if _CLOUD_PATTERN in _code:
        _code = _code.replace(_CLOUD_PATTERN, _LOCAL_PATTERN)
        _LOG.info("PATCH_DOWNLOAD_URL_LOCAL_SERVER: ok (absolute path → disk copy)")
    else:
        _LOG.warning(
            "PATCH_DOWNLOAD_URL_LOCAL_SERVER: pattern not found in telegram_daemon.py — "
            "large file download URL not patched"
        )

    # ── Execute patched daemon as __main__ ────────────────────────────────────
    _globals = {
        "__name__": "__main__",
        "__file__": _daemon_path,
        "__doc__": None,
        "__package__": None,
        "__spec__": None,
        "__builtins__": __builtins__,
    }
    exec(compile(_code, _daemon_path, "exec"), _globals)

except Exception as _exec_err:
    _LOG.error("WRAPPER_EXEC_DAEMON_FAILED: %s", _exec_err)
    raise
