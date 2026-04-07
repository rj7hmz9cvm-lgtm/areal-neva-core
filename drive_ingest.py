from __future__ import annotations

import asyncio
import logging

from core.db import init_db

logger = logging.getLogger("drive_ingest")

async def run_drive_ingest_loop(interval: int = 60) -> None:
    await init_db()
    logger.info("drive ingest started interval=%s", interval)
    while True:
        try:
            await asyncio.sleep(interval)
        except Exception:
            logger.exception("drive ingest loop error")
            await asyncio.sleep(interval)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    asyncio.run(run_drive_ingest_loop())
