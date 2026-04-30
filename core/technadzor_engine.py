# === TECHNADZOR_ENGINE_V1 ===
import logging, os
from typing import Dict, Any, Optional
logger = logging.getLogger(__name__)

_SEVERITY = {"CRITICAL": 3, "MAJOR": 2, "MINOR": 1}

_NORMS_HINTS = {
    "трещин": "СП 70.13330.2012 §7.3",
    "арматур": "ГОСТ 10884-94",
    "бетон": "СП 63.13330.2018",
    "кровл": "СП 17.13330.2017",
    "фасад": "СП 293.1325800.2017",
    "фундамент": "СП 22.13330.2016",
    "пожар": "СП 2.13130.2020",
    "электр": "ПУЭ-7",
    "вентиляц": "СП 60.13330.2020",
    "водопровод": "СП 30.13330.2016",
    "отделк": "СП 71.13330.2017",
}

def classify_severity(text: str) -> str:
    low = text.lower()
    if any(w in low for w in ["обрушен", "критическ", "авари", "опасн", "немедленн"]):
        return "CRITICAL"
    if any(w in low for w in ["значительн", "существенн", "серьёзн", "серьезн", "нарушен"]):
        return "MAJOR"
    return "MINOR"

def find_norm(text: str) -> str:
    low = text.lower()
    for kw, norm in _NORMS_HINTS.items():
        if kw in low:
            return norm
    return ""

def extract_defects(text: str) -> list:
    defects = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    current = []
    for line in lines:
        low = line.lower()
        if any(w in low for w in ["дефект", "нарушен", "трещин", "отслоен", "разруш",
                                   "поврежден", "скол", "протечк", "ржавч"]):
            if current:
                defects.append(" ".join(current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        defects.append(" ".join(current))
    return defects[:20]

def generate_act_text(defects: list, object_name: str = "Объект") -> str:
    lines = [f"АКТ ТЕХНИЧЕСКОГО ОСМОТРА\nОбъект: {object_name}\n"]
    for i, d in enumerate(defects, 1):
        severity = classify_severity(d)
        norm = find_norm(d)
        norm_str = f" — {norm}" if norm else " — норма уточняется"
        lines.append(f"{i}. [{severity}] {d}{norm_str}")
    if not defects:
        lines.append("Видимых дефектов не обнаружено.")
    return "\n".join(lines)

def process_technadzor(
    conn, task_id: str, chat_id: str, topic_id: int,
    raw_input: str, file_name: str = "", local_path: str = ""
) -> Dict[str, Any]:
    """Основная точка входа для технадзора"""
    result = {"ok": False, "result_text": "", "artifact": None, "error_code": None}

    # Gemini vision если фото
    vision_text = ""
    if local_path and any(local_path.lower().endswith(ext)
                          for ext in (".jpg", ".jpeg", ".png", ".webp", ".heic")):
        try:
            import asyncio
            from core.gemini_vision import analyze_image_file
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                vision_text = asyncio.run(
                    analyze_image_file(local_path,
                                       prompt="Опиши все видимые дефекты строительных конструкций",
                                       timeout=60)
                ) or ""
        except Exception as e:
            logger.warning("TECHNADZOR_VISION_ERR %s", e)

    # Собираем текст для анализа
    analysis_text = " ".join(filter(None, [raw_input, vision_text]))

    # Нормы через normative_db
    norm_text = ""
    try:
        from core.normative_db import search_norms
        import asyncio
        try:
            asyncio.get_running_loop()
            norm_results = []
        except RuntimeError:
            norm_results = asyncio.run(search_norms(analysis_text))
        if norm_results:
            norm_lines = [f"  {n['norm_id']}: {n['requirement'][:150]}" for n in norm_results[:3]]
            norm_text = "\nНормативные требования:\n" + "\n".join(norm_lines)
    except Exception as e:
        logger.warning("TECHNADZOR_NORM_ERR %s", e)

    # Дефекты
    defects = extract_defects(analysis_text)

    # Генерируем акт
    act_text = generate_act_text(defects) + norm_text

    # DOCX
    try:
        from core.defect_act_engine import generate_act_docx
        docx_path = generate_act_docx(task_id, analysis_text, file_name)
        if docx_path and os.path.exists(docx_path):
            # Upload
            try:
                from core.artifact_upload_guard import upload_many_or_fail
                up = upload_many_or_fail([docx_path], task_id, int(topic_id or 0))
                link = up.get("links", {}).get(docx_path) or up.get("drive_link", "")
                if link:
                    act_text += f"\n\nДокумент: {link}"
                    result["artifact"] = {"path": docx_path, "drive_link": link}
            except Exception as ue:
                logger.warning("TECHNADZOR_UPLOAD_ERR %s", ue)
                result["artifact"] = {"path": docx_path}
    except Exception as de:
        logger.warning("TECHNADZOR_DOCX_ERR %s", de)

    result["ok"] = True
    result["result_text"] = act_text
    return result

def is_technadzor_intent(text: str, mime_type: str = "") -> bool:
    low = text.lower()
    return any(w in low for w in [
        "технадзор", "дефект", "акт осмотр", "нарушени", "предписани",
        "осмотр", "проверк", "инспекц", "обследован"
    ])
# === END TECHNADZOR_ENGINE_V1 ===
