import os
import json
from modules.document_module import run as doc_run
from modules.image_ocr_module import run as img_run
from modules.estimate_module import run as est_run
from modules.template_engine import run as tpl_run
from modules.artifact_manager import save_artifact

def run(ctx):
    task_id = ctx.get("task_id") or ctx.get("id") or "unknown"
    file_path = (ctx.get("file_path") or "").strip()
    input_text = ctx.get("text", "") or ""
    template_path = ctx.get("template_path") or ""
    mode = (ctx.get("mode") or ctx.get("task_mode") or "estimate").strip().lower()

    extracted_text = input_text
    lp = file_path.lower()

    if file_path:
        if lp.endswith((".pdf", ".docx", ".xlsx", ".xls", ".csv")):
            extracted_text = doc_run({"file_path": file_path}).get("text", "")
        elif lp.endswith((".jpg", ".jpeg", ".png", ".webp")):
            extracted_text = img_run({"file_path": file_path}).get("text", "")

    est = est_run({"text": extracted_text})
    totals = est.get("totals", {})

    if template_path:
        rendered = tpl_run({"template_path": template_path, "data": totals})
        result_text = rendered.get("result", str(totals))
    else:
        if mode in ("tehnadzor", "tech", "inspection"):
            lines = ["Технический результат", ""]
            if totals:
                lines.append("Что найдено")
                for unit, value in sorted(totals.items()):
                    lines.append(f"- {unit}: {value}")
            else:
                lines.append("Явные объёмы не выделены")
            lines.extend(["", "Исходный фрагмент", extracted_text[:3000]])
            result_text = "\n".join(lines).strip()
        elif mode in ("calc", "calculation", "raschet"):
            lines = ["Расчётный результат", ""]
            if totals:
                for unit, value in sorted(totals.items()):
                    lines.append(f"{unit}: {value}")
            else:
                lines.append("Данные для расчёта не найдены")
            result_text = "\n".join(lines).strip()
        else:
            lines = ["Сметный результат", ""]
            if totals:
                lines.append("Итоги по единицам")
                for unit, value in sorted(totals.items()):
                    lines.append(f"- {unit}: {value}")
            else:
                lines.append("Объёмы не найдены")
            lines.extend(["", "Извлечённый текст", extracted_text[:4000]])
            result_text = "\n".join(lines).strip()

    artifact_path = save_artifact(task_id, result_text, "txt", "result")

    return {
        "type": "final_result",
        "mode": mode,
        "text": extracted_text,
        "totals": totals,
        "result_text": result_text,
        "artifact_path": artifact_path,
    }
