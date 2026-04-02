from __future__ import annotations

import asyncio
import logging
import os
import sys

sys.path.insert(0, "/root/.areal-neva-core")

from core.db import init_db

logger = logging.getLogger("core.automation_daemon")
DAEMON_TICK = int(os.getenv("AUTOMATION_DAEMON_TICK", "10"))

async def run_automation_daemon() -> None:
    await init_db()
    logger.info("automation daemon started tick=%s", DAEMON_TICK)
    while True:
        try:
            await asyncio.sleep(DAEMON_TICK)
        except Exception:
            logger.exception("automation daemon tick error")
            await asyncio.sleep(DAEMON_TICK)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    asyncio.run(run_automation_daemon())
