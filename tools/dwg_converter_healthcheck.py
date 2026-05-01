#!/usr/bin/env python3
# === DWG_CONVERTER_HEALTHCHECK_V1 ===
from __future__ import annotations
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
OUT = BASE / "docs/SHARED_CONTEXT/DWG_CONVERTER_STATUS.json"

def main():
    status = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "dwg2dxf": shutil.which("dwg2dxf"),
        "ODAFileConverter": shutil.which("ODAFileConverter") or shutil.which("ODAFileConverter.exe"),
        "geometry_status": "FULL_DWG_GEOMETRY_READY" if (shutil.which("dwg2dxf") or shutil.which("ODAFileConverter") or shutil.which("ODAFileConverter.exe")) else "DWG_METADATA_ONLY_DXF_FULL_PARSE_READY",
        "note": "DXF parses directly. DWG full geometry requires dwg2dxf or ODAFileConverter; without converter DWG metadata path remains active",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(status, ensure_ascii=False))

if __name__ == "__main__":
    main()
# === END_DWG_CONVERTER_HEALTHCHECK_V1 ===
