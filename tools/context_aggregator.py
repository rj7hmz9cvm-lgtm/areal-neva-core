#!/usr/bin/env python3
# === CONTEXT_AGGREGATOR_WRAPPER_V1 ===
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

BASE = Path("/root/.areal-neva-core")

def main() -> None:
    print("CONTEXT_AGGREGATOR_WRAPPER_V1 -> full_context_aggregator.py")
    p = subprocess.run([sys.executable, str(BASE / "tools/full_context_aggregator.py")], cwd=str(BASE))
    sys.exit(p.returncode)

if __name__ == "__main__":
    main()
# === END_CONTEXT_AGGREGATOR_WRAPPER_V1 ===
