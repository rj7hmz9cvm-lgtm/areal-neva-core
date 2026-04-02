import asyncio
import logging
import sys

sys.path.insert(0, "/root/.areal-neva-core")

from core.automation_daemon import run_automation_daemon

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    asyncio.run(run_automation_daemon())
