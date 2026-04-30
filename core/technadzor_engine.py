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

def generate_act_docx_full(
    defects: list,
    object_name: str = "Объект",
    task_id: str = "",
    photo_links: list = None,
    norm_results: list = None,
) -> str:
    """TECHNADZOR_DOCX_FULL_V1 — полный акт: заголовок/объект/дата/таблица/нормы/вывод"""
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor
        from datetime import datetime
        import os

        doc = Document()

        # Заголовок
        h = doc.add_heading("АКТ ТЕХНИЧЕСКОГО ОСМОТРА", level=1)
        h.alignment = 1  # CENTER

        # Метаданные
        from datetime import date
        doc.add_paragraph(f"Объект: {object_name}")
        doc.add_paragraph(f"Дата: {date.today().strftime('%d.%m.%Y')}")
        doc.add_paragraph(f"Задача: {task_id}")
        doc.add_paragraph("")

        # Таблица замечаний
        headers = ["№", "Описание", "Место", "Тяжесть", "Норма", "Риск"]
        table = doc.add_table(rows=1, cols=len(headers))
        table.style = "Table Grid"
        hdr_cells = table.rows[0].cells
        for i, h in enumerate(headers):
            hdr_cells[i].text = h
            hdr_cells[i].paragraphs[0].runs[0].bold = True

        for i, d in enumerate(defects, 1):
            row_cells = table.add_row().cells
            severity = classify_severity(d)
            norm = find_norm(d)
            row_cells[0].text = str(i)
            row_cells[1].text = str(d)[:200]
            # === PHOTO_LINKAGE_V1 ===
            if photo_links and i <= len(photo_links):
                link = photo_links[i-1] if i <= len(photo_links) else ""
                if link and "drive.google" in str(link):
                    from docx.oxml.ns import qn
                    from docx.oxml import OxmlElement
                    p_elem = row_cells[2].paragraphs[0]
                    run = p_elem.add_run("Фото " + str(i))
                    run.font.color.rgb = None
                    try:
                        from docx.opc.constants import RELATIONSHIP_TYPE as RT
                        rPr = run._r.get_or_add_rPr()
                        rStyle = OxmlElement("w:rStyle")
                        rStyle.set(qn("w:val"), "Hyperlink")
                        rPr.insert(0, rStyle)
                        rel = row_cells[2].paragraphs[0].part.relate_to(link, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
                        r_elem = run._r
                        hlinkClick = OxmlElement("w:hlinkClick")
                        hlinkClick.set(qn("r:id"), rel)
                        rPr.append(hlinkClick)
                    except Exception:
                        run.text = link[:80]
                else:
                    row_cells[2].text = str(link)[:80] if link else "см. фото"
            else:
                row_cells[2].text = ""
            # === END PHOTO_LINKAGE_V1 ===
            row_cells[3].text = severity
            row_cells[4].text = norm or "уточняется"
            row_cells[5].text = "ВЫСОКИЙ" if severity == "CRITICAL" else "СРЕДНИЙ" if severity == "MAJOR" else "НИЗКИЙ"

        doc.add_paragraph("")

        # Нормативные требования
        if norm_results:
            doc.add_heading("Нормативные требования", level=2)
            for n in norm_results[:5]:
                doc.add_paragraph(f"• {n.get('norm_id','')}: {n.get('requirement','')[:200]}")

        # Фото ссылки
        if photo_links:
            doc.add_heading("Фотофиксация", level=2)
            for i, link in enumerate(photo_links, 1):
                doc.add_paragraph(f"Фото {i}: {link}")

        # Вывод
        doc.add_heading("Заключение", level=2)
        critical = sum(1 for d in defects if classify_severity(d) == "CRITICAL")
        major = sum(1 for d in defects if classify_severity(d) == "MAJOR")
        if critical:
            doc.add_paragraph(f"Выявлено критических нарушений: {critical}. Требуется немедленное устранение.")
        if major:
            doc.add_paragraph(f"Выявлено значительных нарушений: {major}. Требуется устранение в установленные сроки.")
        if not defects:
            doc.add_paragraph("Видимых дефектов не выявлено.")

        # Сохранение
        out_path = f"/tmp/act_{task_id or 'unknown'}.docx"
        doc.save(out_path)
        logger.info("TECHNADZOR_DOCX_FULL_V1 saved=%s", out_path)
        return out_path

    except Exception as e:
        logger.error("TECHNADZOR_DOCX_FULL_ERR %s", e)
        return ""

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

    # DOCX — DOCX_FULL_CALL_V1
    try:
        docx_path = generate_act_docx_full(
            defects=defects,
            object_name=str(raw_input or "Объект")[:80],
            task_id=task_id,
            photo_links=[local_path] if local_path else None,
            norm_results=norm_results if "norm_results" in dir() else None,
        )

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
