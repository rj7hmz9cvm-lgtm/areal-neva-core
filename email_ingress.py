from __future__ import annotations

import asyncio
import logging

from core.db import init_db

logger = logging.getLogger("email_ingress")

async def run_email_ingress_loop(interval: int = 30) -> None:
    await init_db()
    logger.info("email ingress started interval=%s", interval)
    while True:
        try:
            await asyncio.sleep(interval)
        except Exception:
            logger.exception("email ingress loop error")
            await asyncio.sleep(interval)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    asyncio.run(run_email_ingress_loop())
