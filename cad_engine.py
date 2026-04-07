from pathlib import Path
from typing import Dict

import ezdxf


class CADEngine:
    @staticmethod
    def process(path: str) -> Dict[str, object]:
        p = Path(path)
        ext = p.suffix.lower()

        if ext == ".dwg":
            return {
                "status": "error",
                "message": "DWG not supported by ezdxf directly. Convert DWG to DXF first",
                "file": str(p),
            }

        if ext != ".dxf":
            return {
                "status": "error",
                "message": f"Unsupported CAD extension: {ext}",
                "file": str(p),
            }

        try:
            doc = ezdxf.readfile(path)
            msp = doc.modelspace()
            layers = [layer.dxf.name for layer in doc.layers]
            entities = []
            count = 0

            for entity in msp:
                count += 1
                if len(entities) < 200:
                    entities.append(entity.dxftype())

            return {
                "status": "ok",
                "file": str(p),
                "layers": layers,
                "entities_total": count,
                "entities_sample": entities,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "file": str(p),
            }
