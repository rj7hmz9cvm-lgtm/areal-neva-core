import os, logging, tempfile
from typing import Dict, Any
from datetime import datetime, timezone
from core.engine_base import update_drive_file_stage, upload_artifact_to_drive, quality_gate, calculate_file_hash

logger = logging.getLogger(__name__)

try:
    import ezdxf
    DWG_AVAILABLE = True
except: DWG_AVAILABLE = False
try:
    from openpyxl import Workbook
    EXCEL_AVAILABLE = True
except: EXCEL_AVAILABLE = False

async def process_dwg_to_excel(file_path: str, task_id: str, topic_id: int) -> Dict[str, Any]:
    res = {"success": False, "excel_path": None, "drive_link": None, "error": None}
    if not DWG_AVAILABLE or not EXCEL_AVAILABLE:
        res["error"] = "Missing deps"; return res
    try:
        h = calculate_file_hash(file_path)
        update_drive_file_stage(task_id, f"dwg_{h[:16]}", "DOWNLOADED")
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()
        lines = sum(1 for e in msp if e.dxftype() == 'LINE')
        circles = sum(1 for e in msp if e.dxftype() == 'CIRCLE')
        arcs = sum(1 for e in msp if e.dxftype() == 'ARC')
        texts = sum(1 for e in msp if e.dxftype() in ('TEXT','MTEXT'))
        update_drive_file_stage(task_id, f"dwg_{h[:16]}", "PARSED")
        
        wb = Workbook()
        ws = wb.active; ws.title = "DWG Summary"
        ws.cell(1, 1, "Entity"); ws.cell(1, 2, "Count")
        ws.cell(2, 1, "LINES"); ws.cell(2, 2, lines)
        ws.cell(3, 1, "CIRCLES"); ws.cell(3, 2, circles)
        ws.cell(4, 1, "ARCS"); ws.cell(4, 2, arcs)
        ws.cell(5, 1, "TEXTS"); ws.cell(5, 2, texts)
        tmp = tempfile.gettempdir()
        xl = os.path.join(tmp, f"dwg_{task_id}_{int(datetime.now(timezone.utc).timestamp())}.xlsx")
        wb.save(xl); wb.close()
        res["excel_path"] = xl
        update_drive_file_stage(task_id, f"dwg_{h[:16]}", "ARTIFACT_CREATED")
        qg = quality_gate(xl, task_id, "excel")
        if not qg["passed"]:
            res["error"] = f"Quality gate: {qg['errors']}"; return res
        link = upload_artifact_to_drive(xl, task_id, topic_id)
        if link:
            res["drive_link"] = link; res["success"] = True
    except Exception as e:
        logger.error(f"DWG: {e}"); res["error"] = str(e)
    return res
