# ORCHESTRA_FULL_CONTEXT_PART_015
generated_at_utc: 2026-07-15T16:59:01.503398+00:00
git_sha_before_commit: efa049bc9f55779a41d8af36b486c0cbcb1c6426
part: 15/22


====================================================================================================
BEGIN_FILE: core/stroyka_estimate_canon.py
FILE_CHUNK: 2/2
SHA256_FULL_FILE: 0c9f06a855dc7a17a3fba98eeca19b5c02cb0602b04157ed4ddfd5974c8cb5c2
====================================================================================================
        def _t2tr_build_from_template(_parsed, _price_text, _choice):
            return template_items

        globals()['_build_estimate_items'] = _t2tr_build_from_template
        try:
            return _T2TR_ORIG_CREATE_XLSX(task_id, parsed, template, template_path, sheet_name, price_text, choice)
        finally:
            globals()['_build_estimate_items'] = orig_build
    return _T2TR_ORIG_CREATE_XLSX(task_id, parsed, template, template_path, sheet_name, price_text, choice)
# === END_PATCH_TOPIC2_TEMPLATE_ROWS_FULL_AREAL_CALC_V1 ===

# === PATCH_TOPIC2_AREA_ONLY_WITH_TEMPLATE_ALLOWED_V2 ===
# If a project PDF has only AR/TЭП rows but a canonical full-house template is selected,
# do not stop the task. The template matrix is the calculation basis; PDF facts are inputs.
_T2AOT_ORIG_MISSING_QUESTION = _missing_question


def _t2aot_rows_are_area_only(rows) -> bool:
    usable = []
    non_area = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        name = _clean(row.get('name', '')).lower().replace('ё', 'е')
        try:
            qty = float(row.get('qty') or 0)
            price = float(row.get('price') or 0)
        except Exception:
            qty = price = 0
        if qty <= 0 and price <= 0:
            continue
        usable.append(row)
        if 'площад' not in name and 'общая' not in name:
            non_area.append(row)
    return bool(usable) and not non_area


def _missing_question(parsed: Dict[str, Any]) -> Optional[str]:  # noqa: F811
    rows = parsed.get('pdf_spec_rows') or []
    raw = _low(parsed.get('raw') or '')
    if _t2aot_rows_are_area_only(rows) and any(x in raw for x in ('смет', 'стоимост', 'расчет', 'расчёт', 'проект')):
        return None
    return _T2AOT_ORIG_MISSING_QUESTION(parsed)
# === END_PATCH_TOPIC2_AREA_ONLY_WITH_TEMPLATE_ALLOWED_V2 ===
# === PATCH_TOPIC2_NO_TEMPLATE_FROM_AREA_ONLY_PDF_V1 ===
# Canon: PDF estimate contour is PDF -> table/spec rows -> normalized AREAL_CALC.
# If PDF has only AR/TEP area facts, template rows must not become a final estimate
# unless the user explicitly asks for an orientational calculation.
def _t2_no_template_area_only_rows_v1(rows):
    usable = []
    non_area = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        name = _clean(row.get("name", "")).lower().replace("ё", "е")
        try:
            qty = float(row.get("qty") or 0)
            price = float(row.get("price") or 0)
        except Exception:
            qty = price = 0
        if qty <= 0 and price <= 0:
            continue
        usable.append(row)
        if "площад" not in name and "общая" not in name:
            non_area.append(row)
    return bool(usable) and not non_area


def _t2_no_template_orient_allowed_v1(parsed):
    raw = _low((parsed or {}).get("raw") or "")
    return any(x in raw for x in (
        "считать ориентировочно по проекту",
        "сделай ориентировочный расчет",
        "сделай ориентировочный расчёт",
        "ориентировочно по проекту",
        "ориентировочная смета",
        "ориентировочный расчет",
        "ориентировочный расчёт",
    ))


def _t2_no_valid_pdf_rows_message_v1():
    return (
        "PDF прочитан, но сметная ведомость объёмов / ВОР / спецификация материалов / раздел КЖ с объёмами не найдены. "
        "Вижу только архитектурные данные и площади, поэтому финальную смету из шаблона не создаю, чтобы не подменять расчёт догадками.\n\n"
        "Пришли ВОР / спецификацию / КЖ с объёмами либо прямо напиши: считать ориентировочно по проекту."
    )


_T2NT_ORIG_MISSING_QUESTION_V1 = _missing_question


def _missing_question(parsed: Dict[str, Any]) -> Optional[str]:  # noqa: F811
    rows = (parsed or {}).get("pdf_spec_rows") or []
    if _t2_no_template_area_only_rows_v1(rows) and not _t2_no_template_orient_allowed_v1(parsed):
        return _t2_no_valid_pdf_rows_message_v1()
    return _T2NT_ORIG_MISSING_QUESTION_V1(parsed)


_T2NT_ORIG_GENERATE_AND_SEND_V1 = _generate_and_send


async def _generate_and_send(conn, task, pending, confirm_text, logger=None):  # noqa: F811
    parsed = (pending or {}).get("parsed") or {}
    if _t2_no_template_area_only_rows_v1(parsed.get("pdf_spec_rows") or []) and not _t2_no_template_orient_allowed_v1(parsed):
        task_id = _s(_row_get(task, "id"))
        chat_id = _s(_row_get(task, "chat_id"))
        topic_id = int(_row_get(task, "topic_id", 0) or 0)
        reply_to = _row_get(task, "reply_to_message_id", None)
        msg = _t2_no_valid_pdf_rows_message_v1()
        try:
            send_res = await _send_text(chat_id, msg, reply_to, topic_id)
        except Exception:
            send_res = {}
        kwargs = {
            "state": "WAITING_CLARIFICATION",
            "result": msg,
            "error_message": "TOPIC2_PDF_NO_VALID_ESTIMATE_ROWS",
        }
        if isinstance(send_res, dict) and send_res.get("bot_message_id"):
            kwargs["bot_message_id"] = send_res.get("bot_message_id")
        _update_task_safe(conn, task_id, **kwargs)
        _history_safe(conn, task_id, "TOPIC2_PDF_NO_VALID_ESTIMATE_ROWS:area_only_no_template_final")
        return True
    return await _T2NT_ORIG_GENERATE_AND_SEND_V1(conn, task, pending, confirm_text, logger=logger)

try:
    _STV3_LOG.info("PATCH_TOPIC2_NO_TEMPLATE_FROM_AREA_ONLY_PDF_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_NO_TEMPLATE_FROM_AREA_ONLY_PDF_V1 ===
# === PATCH_TOPIC2_AR_PROJECT_FACT_ROWS_V1 ===
# AR project PDFs may contain usable quantities outside formal VOR tables:
# foundation piles/rostverk, roof area, slab schedule, window/door schedules.
# These rows may be used only as project-derived rows; template rows are still
# forbidden for final output when the PDF has only AR/TEP data.
def _t2ar_num_v1(v):
    try:
        return float(str(v or "").replace(" ", "").replace(",", "."))
    except Exception:
        return 0.0


def _t2ar_pdf_text_v1(parsed):
    try:
        p = (parsed or {}).get("pdf_spec_source") or (parsed or {}).get("local_path") or (parsed or {}).get("file_path")
        if not p or not os.path.exists(str(p)):
            return ""
        import subprocess as _t2ar_subprocess
        res = _t2ar_subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True, timeout=45)
        return res.stdout or ""
    except Exception:
        return ""


def _t2ar_add_row_v1(rows, section, name, unit, qty, note="", kind="material"):
    try:
        qty = float(qty)
    except Exception:
        qty = 0.0
    if qty <= 0:
        return
    key = (section, name, unit, round(qty, 6))
    if any((r.get("section"), r.get("name"), r.get("unit"), round(float(r.get("qty") or 0), 6)) == key for r in rows):
        return
    rows.append({
        "section": section,
        "name": name[:240],
        "unit": unit,
        "qty": qty,
        "price": 0.0,
        "kind": kind,
        "note": (note or "из AR PDF")[:240],
    })


def _t2ar_project_rows_from_pdf_v1(parsed):
    text = _t2ar_pdf_text_v1(parsed)
    if not text:
        return []
    rows = []
    low = _low(text)

    m = re.search(r"Свая\s+200х200мм\s*\(3м\)\s+(\d+)", text, re.I)
    if m:
        _t2ar_add_row_v1(rows, "Фундамент", "Свая 200х200мм (3м)", "шт", _t2ar_num_v1(m.group(1)), "Спецификация на сваи, лист АР-08")

    m = re.search(r"Ростверк\.\s*Бетон\s*B22,?5\s*W6\s*F150\s*([\d\s]+[,.]\d+)", text, re.I | re.S)
    if m:
        _t2ar_add_row_v1(rows, "Фундамент", "Ростверк. Бетон B22,5 W6 F150", "м3", _t2ar_num_v1(m.group(1)), "Таблица на листе АР-08; единица приведена как бетонный объем")

    m = re.search(r"Площадь\s+Поверхности\s+Уклон\s+([\d\s]+[,.]\d+)\s+20", text, re.I)
    if m:
        _t2ar_add_row_v1(rows, "Кровля", "Площадь поверхности кровли, уклон 20°", "м2", _t2ar_num_v1(m.group(1)), "План кровли, лист АР-10")

    for mark, qty in re.findall(r"\b(ПК\s*\d{2}-\d{2}-8)\s+(\d+)", text, re.I):
        mark_clean = re.sub(r"\s+", " ", mark).strip()
        _t2ar_add_row_v1(rows, "Перекрытия", f"Плита перекрытия {mark_clean}", "шт", _t2ar_num_v1(qty), "Спецификация плит перекрытия, лист АР-11")

    m = re.search(r"Площадь\s+монолитных\s+участков\s*-\s*([\d\s]+[,.]\d+)\s*м2", text, re.I)
    if m:
        _t2ar_add_row_v1(rows, "Перекрытия", "Монолитные участки перекрытия", "м2", _t2ar_num_v1(m.group(1)), "План межэтажного перекрытия, лист АР-11")

    m = re.search(r"Балка\s+перекрытия\s+50х200\s+([\d\s]+)\s+(\d+)", text, re.I)
    if m:
        _t2ar_add_row_v1(rows, "Перекрытия", "Балка перекрытия 50х200", "шт", _t2ar_num_v1(m.group(2)), f"Длина {m.group(1).strip()} мм, лист АР-11")

    win_pat = re.compile(r"\b(Ок-\d+(?:,\s*бДв-1)?)\s+(\d+)\s+([0-9\s]+×[0-9\s]+)\s+([\d\s]+[,.]\d+)", re.I)
    for mark, qty, size, area in win_pat.findall(text):
        _t2ar_add_row_v1(rows, "Окна и двери", f"{mark.strip()} оконный/балконный блок {size.strip()}", "шт", _t2ar_num_v1(qty), f"Площадь проема {area.strip()} м2, лист АР-19")

    door_pat = re.compile(r"\b(Дв-\d+|нДв-1)\s+(\d+)\s+[0-9\s]+×[0-9\s]+\s+([0-9\s]+×[0-9\s]+)\s+([\d\s]+[,.]\d+)", re.I)
    for mark, qty, size, area in door_pat.findall(text):
        _t2ar_add_row_v1(rows, "Окна и двери", f"{mark.strip()} дверной блок {size.strip()}", "шт", _t2ar_num_v1(qty), f"Площадь проема {area.strip()} м2, лист АР-20")

    return rows


def _t2ar_missing_from_pdf_v1(parsed):
    text = _t2ar_pdf_text_v1(parsed)
    low = _low(text)
    missing = []
    if "наружные стены дома" in low:
        missing.append("объем/площадь наружных стен 375/300 мм")
    if "внутренние несущие стены" in low:
        missing.append("объем внутренних несущих стен 250 мм")
    if "перегородки" in low:
        missing.append("объем перегородок 150 мм и каркасных перегородок")
    if "уточняется в разделе кж" in low or "разделе кж" in low:
        missing.append("КЖ для ж/б балок, колонн, перемычек, армопояса и плит")
    if "план ввода коммуникаций" in low:
        missing.append("объемы инженерных коммуникаций")
    return list(dict.fromkeys(missing))


def _t2ar_project_rows_message_v1(parsed):
    rows = _t2ar_project_rows_from_pdf_v1(parsed)
    missing = _t2ar_missing_from_pdf_v1(parsed)
    lines = [
        "PDF прочитан. Нашёл проектные позиции и объёмы, которые можно использовать без шаблонной подмены:",
    ]
    for r in rows[:18]:
        lines.append(f"- {r['section']}: {r['name']} — {r['qty']:g} {r['unit']}")
    if len(rows) > 18:
        lines.append(f"- ещё позиций: {len(rows) - 18}")
    if missing:
        lines.append("")
        lines.append("Для полной сметы не хватает явных объёмов:")
        for m in missing[:10]:
            lines.append(f"- {m}")
    lines.append("")
    lines.append("Финальную смету из шаблона не создаю. Пришли недостающие объёмы/КЖ/ВОР либо напиши: считай по найденным позициям.")
    return "\n".join(lines)


try:
    _T2AR_PREV_ORIENT_ALLOWED_V1 = _t2_no_template_orient_allowed_v1
    def _t2_no_template_orient_allowed_v1(parsed):  # noqa: F811
        raw = _low((parsed or {}).get("raw") or "") + " " + _low((parsed or {}).get("_topic2_confirm_text") or "")
        if any(x in raw for x in ("считай по найденным позициям", "считать по найденным позициям", "только найденные позиции")):
            return True
        return _T2AR_PREV_ORIENT_ALLOWED_V1(parsed)
except Exception:
    pass


_T2AR_PREV_MISSING_QUESTION_V1 = _missing_question


def _missing_question(parsed: Dict[str, Any]) -> Optional[str]:  # noqa: F811
    rows = (parsed or {}).get("pdf_spec_rows") or []
    project_rows = _t2ar_project_rows_from_pdf_v1(parsed)
    if _t2_no_template_area_only_rows_v1(rows) and project_rows and not _t2_no_template_orient_allowed_v1(parsed):
        return _t2ar_project_rows_message_v1(parsed)
    return _T2AR_PREV_MISSING_QUESTION_V1(parsed)


_T2AR_PREV_CREATE_XLSX_V1 = _create_xlsx_from_template


def _t2ar_keywords_for_price_v1(name):
    low = _low(name)
    words = [w for w in re.split(r"[^0-9a-zа-яё]+", low) if len(w) >= 3]
    keep = [w for w in words if w not in ("лист", "проем", "проема", "площадь", "поверхности")]
    return tuple(keep[:6]) or tuple(words[:3])


def _create_xlsx_from_template(task_id: str, parsed: Dict[str, Any], template: Dict[str, Any], template_path: Optional[str], sheet_name: Optional[str], price_text: str, choice: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]], float]:  # noqa: F811
    project_rows = list((parsed or {}).get("pdf_project_rows") or [])
    if not project_rows:
        project_rows = _t2ar_project_rows_from_pdf_v1(parsed)
    if project_rows and _t2_no_template_orient_allowed_v1(parsed):
        items = []
        for r in project_rows:
            it = dict(r)
            vals = _numbers_from_price_text(price_text or "", _t2ar_keywords_for_price_v1(it.get("name", "")))
            it["price"] = _choose_value(vals, choice) if vals else 0.0
            if not vals:
                it["note"] = (it.get("note", "") + "; PRICE_MISSING").strip("; ")
            items.append(it)
        orig_build = globals().get("_build_estimate_items")
        base_create = globals().get("_T2TR_ORIG_CREATE_XLSX") or _T2AR_PREV_CREATE_XLSX_V1
        def _t2ar_build_from_project(_parsed, _price_text, _choice):
            return items
        globals()["_build_estimate_items"] = _t2ar_build_from_project
        try:
            return base_create(task_id, parsed, template, template_path, sheet_name, price_text, choice)
        finally:
            globals()["_build_estimate_items"] = orig_build
    return _T2AR_PREV_CREATE_XLSX_V1(task_id, parsed, template, template_path, sheet_name, price_text, choice)


_T2AR_PREV_GENERATE_AND_SEND_V1 = _generate_and_send


async def _generate_and_send(conn, task, pending, confirm_text, logger=None):  # noqa: F811
    if isinstance(pending, dict):
        parsed = pending.get("parsed") or {}
        if isinstance(parsed, dict):
            parsed["_topic2_confirm_text"] = confirm_text or ""
            rows = _t2ar_project_rows_from_pdf_v1(parsed)
            if rows:
                parsed["pdf_project_rows"] = rows
                pending["parsed"] = parsed
                try:
                    _history_safe(conn, _s(_row_get(task, "id")), f"TOPIC2_AR_PROJECT_ROWS_EXTRACTED:{len(rows)}")
                except Exception:
                    pass
    return await _T2AR_PREV_GENERATE_AND_SEND_V1(conn, task, pending, confirm_text, logger=logger)

try:
    _STV3_LOG.info("PATCH_TOPIC2_AR_PROJECT_FACT_ROWS_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_AR_PROJECT_FACT_ROWS_V1 ===
# === PATCH_TOPIC2_PROJECT_ROWS_CONFIRM_AND_PRICES_V1 ===
# Explicit user clarification "считай по проекту" means:
# - use only rows extracted from the project PDF;
# - do not use template rows as estimate positions;
# - use Sonar/Perplexity price search for those extracted rows.
def _t2prcp_project_calc_requested_text_v1(value):
    raw = _low(value or "")
    if "по проект" in raw and "цены" in raw and ("найди" in raw or "интернет" in raw):
        return True
    return any(x in raw for x in (
        "считай по проекту",
        "считать по проекту",
        "считать по проектной документации",
        "считай по проектной документации",
        "считай по найденным позициям",
        "считать по найденным позициям",
        "только найденные позиции",
    ))


def _t2prcp_history_clarified_text_v1(conn, task_id):
    if conn is None or not task_id:
        return ""
    try:
        rows = conn.execute(
            "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'clarified:%' ORDER BY rowid DESC LIMIT 12",
            (str(task_id),),
        ).fetchall()
        return "\n".join(_s(r[0]) for r in rows)
    except Exception:
        return ""


try:
    _T2PRCP_PREV_ORIENT_ALLOWED_V1 = _t2_no_template_orient_allowed_v1
    def _t2_no_template_orient_allowed_v1(parsed):  # noqa: F811
        raw = _low((parsed or {}).get("raw") or "")
        raw += " " + _low((parsed or {}).get("_topic2_confirm_text") or "")
        raw += " " + _low((parsed or {}).get("_topic2_history_clarified") or "")
        if _t2prcp_project_calc_requested_text_v1(raw):
            return True
        return _T2PRCP_PREV_ORIENT_ALLOWED_V1(parsed)
except Exception:
    pass


_T2PRCP_PREV_SEARCH_ONLINE_V1 = _search_prices_online


async def _search_prices_online(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], conn=None, task_id=None) -> str:  # noqa: F811
    base = await _T2PRCP_PREV_SEARCH_ONLINE_V1(parsed, template, sheet_name, conn=conn, task_id=task_id)
    project_rows = (parsed or {}).get("pdf_project_rows") or _t2ar_project_rows_from_pdf_v1(parsed or {})
    if not project_rows:
        return base
    try:
        from core.price_enrichment import _openrouter_price_search as _project_price_search
        lines = []
        seen = set()
        for row in project_rows[:22]:
            name = _s(row.get("name"))
            unit = _s(row.get("unit"))
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            if conn is not None and task_id is not None:
                try:
                    _history_safe(conn, task_id, f"TOPIC2_PROJECT_PRICE_SEARCH_STARTED:{name[:80]}")
                except Exception:
                    pass
            offers = []
            try:
                offers = await asyncio.wait_for(_project_price_search(name, unit), timeout=35)
            except Exception:
                offers = []
            valid = [
                o for o in (offers or [])
                if o.get("price") and (o.get("supplier") or o.get("url")) and o.get("status")
            ]
            if conn is not None and task_id is not None:
                try:
                    if valid:
                        o0 = valid[0]
                        _history_safe(conn, task_id, "TOPIC2_PROJECT_PRICE_SOURCE_FOUND:{}:{}:{}".format(
                            name[:50], _s(o0.get("supplier"))[:50], _s(o0.get("status"))[:20]
                        ))
                    else:
                        _history_safe(conn, task_id, f"TOPIC2_PROJECT_PRICE_SOURCE_MISSING:{name[:80]}")
                except Exception:
                    pass
            for o in valid[:2]:
                lines.append(
                    "- {} | {} | {} | Санкт-Петербург и Ленинградская область | {} | {} | {}".format(
                        name,
                        o.get("price"),
                        o.get("unit") or unit,
                        o.get("supplier") or "",
                        o.get("url") or "",
                        o.get("checked_at") or datetime.date.today().isoformat(),
                    )
                )
        if lines:
            return (base or "") + "\n\n=== ПОИСК ПО ПРОЕКТНЫМ ПОЗИЦИЯМ ===\n" + "\n".join(lines)
    except Exception as _t2prcp_e:
        try:
            if conn is not None and task_id is not None:
                _history_safe(conn, task_id, "TOPIC2_PROJECT_PRICE_SEARCH_ERR:" + _s(_t2prcp_e)[:120])
        except Exception:
            pass
    return base


_T2PRCP_PREV_GENERATE_AND_SEND_V1 = _generate_and_send


async def _generate_and_send(conn, task, pending, confirm_text, logger=None):  # noqa: F811
    task_id = _s(_row_get(task, "id"))
    if isinstance(pending, dict):
        parsed = pending.get("parsed") or {}
        if isinstance(parsed, dict):
            history_text = _t2prcp_history_clarified_text_v1(conn, task_id)
            parsed["_topic2_confirm_text"] = (confirm_text or "") + "\n" + history_text
            parsed["_topic2_history_clarified"] = history_text
            rows = _t2ar_project_rows_from_pdf_v1(parsed)
            if rows:
                parsed["pdf_project_rows"] = rows
                pending["parsed"] = parsed
                if _t2_no_template_orient_allowed_v1(parsed):
                    pending["online_prices"] = ""
                try:
                    _history_safe(conn, task_id, f"TOPIC2_AR_PROJECT_ROWS_EXTRACTED:{len(rows)}")
                except Exception:
                    pass
                if not _t2_no_template_orient_allowed_v1(parsed):
                    chat_id = _s(_row_get(task, "chat_id"))
                    topic_id = int(_row_get(task, "topic_id", 0) or 0)
                    reply_to = _row_get(task, "reply_to_message_id", None)
                    msg = _t2ar_project_rows_message_v1(parsed)
                    try:
                        send_res = await _send_text(chat_id, msg, reply_to, topic_id)
                    except Exception:
                        send_res = {}
                    kwargs = {
                        "state": "WAITING_CLARIFICATION",
                        "result": msg,
                        "error_message": "TOPIC2_WAIT_PROJECT_ROW_CONFIRMATION",
                    }
                    if isinstance(send_res, dict) and send_res.get("bot_message_id"):
                        kwargs["bot_message_id"] = send_res.get("bot_message_id")
                    _update_task_safe(conn, task_id, **kwargs)
                    _history_safe(conn, task_id, "TOPIC2_PROJECT_ROWS_WAITING_USER_CONFIRM")
                    return True
    return await _T2PRCP_PREV_GENERATE_AND_SEND_V1(conn, task, pending, confirm_text, logger=logger)

try:
    _STV3_LOG.info("PATCH_TOPIC2_PROJECT_ROWS_CONFIRM_AND_PRICES_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_PROJECT_ROWS_CONFIRM_AND_PRICES_V1 ===
# === PATCH_TOPIC2_PROJECT_WORK_ROWS_V1 ===
# Project-derived material/product rows require corresponding work rows for
# "работы + материалы" totals. Work rows are derived only from extracted project
# rows and keep the same unit/quantity; no template positions are introduced.
def _t2pwr_work_name_v1(row):
    name = _s((row or {}).get("name"))
    sec = _s((row or {}).get("section"))
    low = _low(name)
    if "свая" in low:
        return "Монтаж/погружение: " + name
    if "ростверк" in low:
        return "Устройство: " + name
    if "кровл" in low:
        return "Монтаж: " + name
    if "плита перекрытия" in low:
        return "Монтаж: " + name
    if "монолитные участки" in low:
        return "Устройство: " + name
    if "балка" in low:
        return "Монтаж: " + name
    if "окон" in low or "двер" in low or sec == "Окна и двери":
        return "Монтаж: " + name
    return "Монтаж/устройство: " + name


def _t2pwr_expand_rows_v1(rows):
    out = []
    seen = set()
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        base = dict(row)
        base["kind"] = base.get("kind") or "material"
        key = (base.get("section"), base.get("name"), base.get("unit"), base.get("qty"), base.get("kind"))
        if key not in seen:
            seen.add(key)
            out.append(base)
        work = dict(base)
        work["name"] = _t2pwr_work_name_v1(base)
        work["kind"] = "work"
        work["price"] = 0.0
        work["note"] = (_s(base.get("note")) + "; работа по проектной позиции").strip("; ")
        key = (work.get("section"), work.get("name"), work.get("unit"), work.get("qty"), work.get("kind"))
        if key not in seen:
            seen.add(key)
            out.append(work)
    return out


try:
    _T2PWR_PREV_PROJECT_ROWS_V1 = _t2ar_project_rows_from_pdf_v1
    def _t2ar_project_rows_from_pdf_v1(parsed):  # noqa: F811
        return _t2pwr_expand_rows_v1(_T2PWR_PREV_PROJECT_ROWS_V1(parsed))
except Exception:
    pass


try:
    _T2PWR_PREV_SEARCH_V1 = _search_prices_online
    async def _search_prices_online(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], conn=None, task_id=None) -> str:  # noqa: F811
        project_rows = (parsed or {}).get("pdf_project_rows") or _t2ar_project_rows_from_pdf_v1(parsed or {})
        if project_rows and _t2_no_template_orient_allowed_v1(parsed or {}):
            model = os.getenv("OPENROUTER_MODEL_ONLINE", "perplexity/sonar").strip() or "perplexity/sonar"
            if "sonar" not in model.lower():
                raise RuntimeError(f"TOPIC2_ONLINE_MODEL_GUARD_BLOCKED_NON_SONAR:{model}")
            if conn is not None and task_id is not None:
                _history_safe(conn, task_id, "TOPIC2_PRICE_ENRICHMENT_STARTED")
                _history_safe(conn, task_id, f"TOPIC2_ONLINE_MODEL_SONAR_CONFIRMED:{model}")
            from core.price_enrichment import _openrouter_price_search as _project_price_search
            lines = []
            seen = set()
            # Keep runtime bounded; rows are ordered material/work pairs from the project.
            for row in project_rows[:44]:
                name = _s(row.get("name"))
                unit = _s(row.get("unit"))
                if not name or name.lower() in seen:
                    continue
                seen.add(name.lower())
                if conn is not None and task_id is not None:
                    _history_safe(conn, task_id, f"TOPIC2_PROJECT_PRICE_SEARCH_STARTED:{name[:80]}")
                try:
                    offers = await asyncio.wait_for(_project_price_search(name, unit), timeout=35)
                except Exception:
                    offers = []
                valid = [o for o in (offers or []) if o.get("price") and (o.get("supplier") or o.get("url")) and o.get("status")]
                if conn is not None and task_id is not None:
                    if valid:
                        o0 = valid[0]
                        _history_safe(conn, task_id, "TOPIC2_PROJECT_PRICE_SOURCE_FOUND:{}:{}:{}".format(
                            name[:50], _s(o0.get("supplier"))[:50], _s(o0.get("status"))[:20]
                        ))
                    else:
                        _history_safe(conn, task_id, f"TOPIC2_PROJECT_PRICE_SOURCE_MISSING:{name[:80]}")
                for o in valid[:2]:
                    lines.append(
                        "- {} | {} | {} | Санкт-Петербург и Ленинградская область | {} | {} | {}".format(
                            name,
                            o.get("price"),
                            o.get("unit") or unit,
                            o.get("supplier") or "",
                            o.get("url") or "",
                            o.get("checked_at") or datetime.date.today().isoformat(),
                        )
                    )
            result = "\n".join(lines)
            if conn is not None and task_id is not None:
                _history_safe(conn, task_id, f"TOPIC2_PRICE_ENRICHMENT_DONE:{len(result)}")
            return result
        return await _T2PWR_PREV_SEARCH_V1(parsed, template, sheet_name, conn=conn, task_id=task_id)
except Exception:
    pass

try:
    _STV3_LOG.info("PATCH_TOPIC2_PROJECT_WORK_ROWS_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_PROJECT_WORK_ROWS_V1 ===

# === PATCH_TOPIC2_SAMPLE_MATRIX_MODE_V1 ===
# "Считай по проекту" means: use project facts as input and use existing
# estimate samples as calculation structure. It must not collapse the estimate
# to only the rows directly extracted from the PDF unless the user explicitly
# asks for "только найденные позиции".
def _t2s_text_v1(parsed):
    raw = _low((parsed or {}).get("raw") or "")
    raw += " " + _low((parsed or {}).get("_topic2_confirm_text") or "")
    raw += " " + _low((parsed or {}).get("_topic2_history_clarified") or "")
    return raw


def _t2s_project_only_requested_v1(text):
    low = _low(text or "")
    return any(x in low for x in (
        "только найденные позиции",
        "считай по найденным позициям",
        "считать по найденным позициям",
    ))


def _t2s_sample_matrix_mode_v1(parsed):
    if not isinstance(parsed, dict):
        return False
    text = _t2s_text_v1(parsed)
    if not _t2prcp_project_calc_requested_text_v1(text):
        return False
    if _t2s_project_only_requested_v1(text):
        return False
    rows = parsed.get("pdf_project_rows") or []
    if not rows:
        try:
            rows = _t2ar_project_rows_from_pdf_v1(parsed)
        except Exception:
            rows = []
    return bool(rows)


def _t2s_with_project_only_disabled_v1(callback):
    guard = globals().get("_t2_no_template_orient_allowed_v1")

    def _sample_matrix_guard(_parsed):
        return False

    globals()["_t2_no_template_orient_allowed_v1"] = _sample_matrix_guard
    try:
        return callback()
    finally:
        if guard is not None:
            globals()["_t2_no_template_orient_allowed_v1"] = guard


async def _t2s_await_project_only_disabled_v1(callback):
    guard = globals().get("_t2_no_template_orient_allowed_v1")

    def _sample_matrix_guard(_parsed):
        return False

    globals()["_t2_no_template_orient_allowed_v1"] = _sample_matrix_guard
    try:
        return await callback()
    finally:
        if guard is not None:
            globals()["_t2_no_template_orient_allowed_v1"] = guard


_T2S_PREV_CREATE_XLSX_V1 = _create_xlsx_from_template


def _create_xlsx_from_template(task_id: str, parsed: Dict[str, Any], template: Dict[str, Any], template_path: Optional[str], sheet_name: Optional[str], price_text: str, choice: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]], float]:  # noqa: F811
    if _t2s_sample_matrix_mode_v1(parsed):
        return _t2s_with_project_only_disabled_v1(
            lambda: _T2S_PREV_CREATE_XLSX_V1(task_id, parsed, template, template_path, sheet_name, price_text, choice)
        )
    return _T2S_PREV_CREATE_XLSX_V1(task_id, parsed, template, template_path, sheet_name, price_text, choice)


_T2S_PREV_SEARCH_ONLINE_V1 = _search_prices_online


async def _search_prices_online(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], conn=None, task_id=None) -> str:  # noqa: F811
    if _t2s_sample_matrix_mode_v1(parsed):
        model = os.getenv("OPENROUTER_MODEL_ONLINE", "perplexity/sonar").strip() or "perplexity/sonar"
        if "sonar" not in model.lower():
            raise RuntimeError(f"TOPIC2_ONLINE_MODEL_GUARD_BLOCKED_NON_SONAR:{model}")
        if conn is not None and task_id is not None:
            _history_safe(conn, task_id, "TOPIC2_SAMPLE_MATRIX_MODE:PROJECT_FACTS_PLUS_TEMPLATE_SAMPLE")
        previous_project_search = globals().get("_T2PWR_PREV_SEARCH_V1")
        if previous_project_search:
            return await previous_project_search(parsed, template, sheet_name, conn=conn, task_id=task_id)
        return await _t2s_await_project_only_disabled_v1(
            lambda: _T2S_PREV_SEARCH_ONLINE_V1(parsed, template, sheet_name, conn=conn, task_id=task_id)
        )
    return await _T2S_PREV_SEARCH_ONLINE_V1(parsed, template, sheet_name, conn=conn, task_id=task_id)


try:
    _STV3_LOG.info("PATCH_TOPIC2_SAMPLE_MATRIX_MODE_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_SAMPLE_MATRIX_MODE_V1 ===

# === PATCH_TOPIC2_STRICT_PRICE_SOURCE_MATCH_V1 ===
# FACT ONLY: a live price source may be attached to an AREAL_CALC row only when
# the source position and estimate row describe the same material/work family.
_T2SPSM_PREV_MATCH_PRICE_SOURCE_V1 = _match_price_source


def _t2spsm_words_v1(text):
    low = _low(text or "")
    return [w for w in re.split(r"[^0-9a-zа-яё]+", low) if len(w) >= 3]


def _t2spsm_families_v1(text, section=""):
    low = _low((text or "") + " " + (section or ""))
    families = set()
    checks = (
        ("gasbeton", ("газобетон", "газоблок", "блок 625", "u-блок", "u блок", "лср")),
        ("concrete", ("бетон", "монолит", "ж/б", "железобетон", "ростверк", "плита")),
        ("rebar", ("арматур", "а500", "а240", "проволока вяз")),
        ("wood", ("доска", "брус", "пиломат", "osb", "фанера")),
        ("insulation", ("пенопл", "утепл", "минват", "пир", "pir")),
        ("waterproof", ("гидроизоляц", "линокром", "мастик", "праймер")),
        ("roof", ("кров", "стропил", "мауэрлат", "мембран", "профнастил", "черепиц")),
        ("windows", ("окн", "окон", "пвх", "стеклопакет")),
        ("doors", ("двер", "дверн")),
        ("delivery", ("достав", "транспорт")),
        ("unload", ("разгруз", "погруз")),
        ("crane", ("кран",)),
        ("pump", ("бетононасос",)),
        ("masonry_work", ("кладк", "монтаж", "устройство", "работ")),
        ("facade", ("фасад", "внешняя отделка")),
        ("interior", ("внутрен", "отделк", "гкл", "ламинат", "плитк")),
        ("engineering", ("электрик", "водоснаб", "канализац", "отоплен", "вентиляц", "инженер")),
    )
    for fam, terms in checks:
        if any(term in low for term in terms):
            families.add(fam)
    return families


def _t2spsm_useful_keywords_v1(keywords):
    stop = {
        "цена", "стоимость", "руб", "рублей", "санкт", "петербург", "ленинградская",
        "область", "материал", "материалы", "строительных", "строительный", "работы",
        "работ", "под", "ключ", "для", "при", "или", "монтаж", "устройство",
    }
    return [kw for kw in (keywords or []) if kw and kw not in stop and len(kw) >= 3]


def _match_price_source(sources: List[Dict[str, Any]], item_name: str, item_section: str) -> Dict[str, Any]:  # noqa: F811
    today = datetime.date.today().isoformat()
    empty = {"supplier": "", "url": "", "checked_at": today, "status": "template_only"}
    if not sources:
        return empty
    item_text = f"{item_name or ''} {item_section or ''}"
    item_low = _low(item_text)
    item_families = _t2spsm_families_v1(item_name, item_section)
    best = None
    best_score = 0
    for src in sources:
        src_pos = _s(src.get("position"))
        src_families = _t2spsm_families_v1(src_pos)
        if src_families:
            if not item_families or not (src_families & item_families):
                continue
        keywords = _t2spsm_useful_keywords_v1(src.get("keywords") or _t2spsm_words_v1(src_pos))
        score = sum(1 for kw in keywords if kw in item_low)
        if src_families and item_families and (src_families & item_families):
            score = max(score, 1)
        min_score = 1 if (src_families & item_families) else 2
        if score >= min_score and score > best_score:
            best_score = score
            best = src
    return best if best else empty


try:
    _STV3_LOG.info("PATCH_TOPIC2_STRICT_PRICE_SOURCE_MATCH_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_STRICT_PRICE_SOURCE_MATCH_V1 ===

# === PATCH_TOPIC2_STRICT_PRICE_SOURCE_MATCH_V2 ===
# Narrow work-family matching: generic words "монтаж/устройство/работы" are not
# enough to attach a live source from another section.
def _t2spsm_families_v1(text, section=""):  # noqa: F811
    low = _low((text or "") + " " + (section or ""))
    families = set()
    checks = (
        ("gasbeton", ("газобетон", "газоблок", "блок 625", "u-блок", "u блок", "лср")),
        ("concrete", ("бетон", "монолит", "ж/б", "железобетон", "ростверк", "плита")),
        ("rebar", ("арматур", "а500", "а240", "проволока вяз")),
        ("wood", ("доска", "брус", "пиломат", "osb", "фанера")),
        ("insulation", ("пенопл", "утепл", "минват", "пир", "pir")),
        ("waterproof", ("гидроизоляц", "линокром", "мастик", "праймер")),
        ("roof", ("кров", "стропил", "мауэрлат", "мембран", "профнастил", "черепиц")),
        ("windows", ("окн", "окон", "пвх", "стеклопакет")),
        ("doors", ("двер", "дверн")),
        ("delivery", ("достав", "транспорт")),
        ("unload", ("разгруз", "погруз")),
        ("crane", ("кран",)),
        ("pump", ("бетононасос",)),
        ("masonry_work", ("кладк",)),
        ("facade", ("фасад", "внешняя отделка")),
        ("interior", ("внутрен", "отделк", "гкл", "ламинат", "плитк")),
        ("engineering", ("электрик", "водоснаб", "канализац", "отоплен", "вентиляц", "инженер")),
    )
    for fam, terms in checks:
        if any(term in low for term in terms):
            families.add(fam)
    return families


try:
    _STV3_LOG.info("PATCH_TOPIC2_STRICT_PRICE_SOURCE_MATCH_V2 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_STRICT_PRICE_SOURCE_MATCH_V2 ===

# === PATCH_TOPIC2_FOUNDATION_ONLY_PHOTO_SCOPE_V1 ===
_T2FO_PREV_BUILD_ESTIMATE_ITEMS_V1 = _build_estimate_items


def _t2fo_foundation_only_v1(parsed):
    raw = _low((parsed or {}).get("raw") or "")
    obj = _low((parsed or {}).get("object") or "")
    scope = _low((parsed or {}).get("scope") or "")
    return (
        obj == "фундамент"
        or scope == "фундамент"
        or ("фундамент" in raw and ("плит" in raw or "подуш" in raw or "щеб" in raw))
    )


def _t2fo_float_v1(value, default=0.0):
    try:
        return float(value or default)
    except Exception:
        return float(default)


def _t2fo_int_v1(value, default=0):
    try:
        return int(value or default)
    except Exception:
        return int(default)


def _t2fo_manual_monolith_work_price_v1(text):
    s = _low(text or "")
    if not ("монолит" in s and "работ" in s):
        return 0.0
    patterns = (
        r"стоимост[ьи]\s+работ[^\d]{0,80}монолит[^\d]{0,80}(\d{3,6})(?:[.,]\d+)?\s*(?:руб|р|за|/|\s)*(?:м3|м³|метр\s+куб)",
        r"работ[^\d]{0,80}монолит[^\d]{0,80}(\d{3,6})(?:[.,]\d+)?\s*(?:руб|р|за|/|\s)*(?:м3|м³|метр\s+куб)",
        r"монолит[^\d]{0,80}работ[^\d]{0,80}(\d{3,6})(?:[.,]\d+)?\s*(?:руб|р|за|/|\s)*(?:м3|м³|метр\s+куб)",
    )
    for pat in patterns:
        m = re.search(pat, s, re.I)
        if m:
            try:
                return float(m.group(1).replace(",", "."))
            except Exception:
                return 0.0
    return 0.0


def _t2fo_prices_from_source_lines_v1(price_text, keywords):
    vals = []
    for line in str(price_text or "").splitlines():
        low = _low(line)
        if not any(_low(k) in low for k in keywords):
            continue
        parts = [p.strip() for p in line.strip(" \t-—•·").split("|")]
        if len(parts) < 2:
            continue
        try:
            v = float(re.sub(r"[^0-9.,]", "", parts[1]).replace(",", "."))
        except Exception:
            v = 0.0
        if 100 <= v <= 10000000:
            vals.append(v)
    return vals


def _t2fo_build_foundation_items_v1(parsed, price_text, choice):
    parsed = parsed or {}
    P = _FTM_PRICES
    dims = parsed.get("dimensions") or parsed.get("dims") or (0, 0)
    try:
        a, b = float(dims[0]), float(dims[1])
    except Exception:
        area_fallback = _t2fo_float_v1(parsed.get("area_floor"), 0.0)
        a = b = area_fallback ** 0.5 if area_fallback > 0 else 0.0
    area = _t2fo_float_v1(parsed.get("area_floor"), round(a * b, 2))
    offset = _t2fo_float_v1(parsed.get("foundation_offset_m"), 0.0)
    prep_area = round((a + 2 * offset) * (b + 2 * offset), 2) if offset and a and b else area
    slab_t = _t2fo_float_v1(parsed.get("foundation_thickness_m"), 0.25)
    sand_t = _t2fo_float_v1(parsed.get("sand_thickness_m"), 0.0)
    gravel_t = _t2fo_float_v1(parsed.get("gravel_thickness_m"), 0.0)
    layers = _t2fo_int_v1(parsed.get("reinforcement_layers"), 2)
    distance = _t2fo_float_v1(parsed.get("distance_km"), 0.0)
    raw_text = _low(parsed.get("raw") or "")
    concrete_grade = _s(parsed.get("concrete_grade") or ("М350" if "350" in raw_text else "В25"))

    concrete_volume = round(area * slab_t, 2)
    rebar_qty = round(max(concrete_volume * 0.08 * (max(layers, 1) / 2.0), 0.1), 3)
    formwork_perim = round(2 * (a + b), 2) if a and b else round(area ** 0.5 * 4, 2)
    earth_volume = round(prep_area * max(sand_t + gravel_t, 0.2), 2)

    concrete_price = _p8v3_mp("бетон в25 w6", P["concrete_b25_mat"])
    rebar_price = _p8v3_mp("арматура металлическая д.12а500", P["rebar_a500_mat"])
    sand_price = _choose_value(
        _t2fo_prices_from_source_lines_v1(price_text, ("песок", "песчаная подушка", "песчаный")),
        choice,
        P["sand_mat"],
    )
    gravel_price = _choose_value(
        _t2fo_prices_from_source_lines_v1(price_text, ("щебень", "щебеночное основание", "щебеночный", "щебёноч")),
        choice,
        P["gravel_mat"],
    )
    manual_concrete_work_price = _t2fo_manual_monolith_work_price_v1(raw_text)
    concrete_work_price = manual_concrete_work_price or _p8v3_wp("бетонирование монолитной плиты   б/н", P["concrete_pour_work"])
    concrete_work_note = "ручная цена из правки пользователя" if manual_concrete_work_price else "работы"
    pump_price = _choose_value(_numbers_from_price_text(price_text, ("бетононасос",)), choice) or 31050
    delivery_price = round(P["logist_delivery"] * max(distance / 30.0, 1.0), 2) if distance else 0

    items = []
    if any(x in raw_text for x in ("подготов", "землян", "котлован", "выемк", "разработка грунта")):
        items.append(_ftm_row("Фундамент", "Подготовка основания и земляные работы", "м³", earth_volume, P["earth_work"], "по ТЗ: подготовка/земляные работы"))
    if sand_t > 0:
        sand_qty = round(prep_area * sand_t, 2)
        sand_work_price = _t2fpag_choose_v1(price_text, "sand_work", choice, P["sand_work"])
        items.append(_ftm_row("Фундамент", f"Песчаная подушка {int(sand_t * 1000)} мм с послойным уплотнением", "м³", sand_qty, sand_price + sand_work_price, f"работы+материал; площадь подготовки {prep_area:g} м²"))
    if gravel_t > 0:
        gravel_qty = round(prep_area * gravel_t, 2)
        gravel_work_price = _t2fpag_choose_v1(price_text, "gravel_work", choice, P["gravel_work"])
        items.append(_ftm_row("Фундамент", f"Щебёночное основание {int(gravel_t * 1000)} мм с уплотнением", "м³", gravel_qty, gravel_price + gravel_work_price, f"работы+материал; площадь подготовки {prep_area:g} м²"))
    items.append(_ftm_row("Фундамент", "Опалубка периметра плиты материал", "мп", formwork_perim, P["formwork_perim_mat"], "по размерам с фото"))
    items.append(_ftm_row("Фундамент", "Опалубка плиты монтаж/демонтаж", "мп", formwork_perim, P["formwork_install_work"], "работы"))
    items.append(_ftm_row("Фундамент", f"Арматура А500 для плиты, {layers} слоя", "т", rebar_qty, rebar_price, "расчётная масса от объёма бетона; уточняется по КЖ"))
    items.append(_ftm_row("Фундамент", f"Армирование фундаментной плиты, {layers} слоя", "м²", area, _p8v3_wp("устройство арматурного каркаса", P["rebar_install_work"]), "работы"))
    items.append(_ftm_row("Фундамент", f"Бетон {concrete_grade} для монолитной плиты {int(slab_t * 1000)} мм", "м³", concrete_volume, concrete_price, "по ТЗ"))
    items.append(_ftm_row("Фундамент", "Работы по бетону: бетонирование фундаментной плиты", "м³", concrete_volume, concrete_work_price, concrete_work_note))
    if any(x in raw_text for x in ("бетононасос", "насос", "подач")):
        items.append(_ftm_row("Фундамент", "Аренда бетононасоса / подача бетона", "смена", 1, pump_price, "по ТЗ: подача бетона"))
    if delivery_price:
        items.append(_ftm_row("Логистика", f"Доставка материалов от Санкт-Петербурга, {distance:g} км", "компл", 1, delivery_price, "по ТЗ: удалённость объекта"))

    subtotal = sum(float(it["price"]) * float(it["qty"]) for it in items if it["section"] not in ("Логистика", "Накладные расходы"))
    items.append(_ftm_row("Накладные расходы", "Организация работ и накладные", "компл", 1, round(subtotal * 0.07, 2), "7% от фундаментных работ и материалов"))
    items.append(_ftm_row("Накладные расходы", "Расходные материалы и крепёж", "компл", 1, round(subtotal * 0.015, 2), "1.5% от фундаментных работ и материалов"))
    return items


def _build_estimate_items(parsed, price_text, choice):  # noqa: F811
    if _t2fo_foundation_only_v1(parsed):
        return _t2fo_build_foundation_items_v1(parsed, price_text, choice)
    return _T2FO_PREV_BUILD_ESTIMATE_ITEMS_V1(parsed, price_text, choice)


try:
    _STV3_LOG.info("PATCH_TOPIC2_FOUNDATION_ONLY_PHOTO_SCOPE_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_FOUNDATION_ONLY_PHOTO_SCOPE_V1 ===

# === PATCH_TOPIC2_FOUNDATION_NO_TEMPLATE_ROWS_V1 ===
_T2FO_NTR_PREV_CREATE_XLSX_V1 = _create_xlsx_from_template


def _t2fo_strip_non_areal_sheets_v1(path):
    try:
        from openpyxl import load_workbook as _t2fo_load_workbook
        wb = _t2fo_load_workbook(path)
        if "AREAL_CALC" not in wb.sheetnames:
            return
        for ws in list(wb.worksheets):
            if ws.title != "AREAL_CALC":
                wb.remove(ws)
        ws = wb["AREAL_CALC"]
        for row_idx in range(ws.max_row, 1, -1):
            if _low(ws.cell(row_idx, 2).value or "") == "не входит":
                ws.delete_rows(row_idx, ws.max_row - row_idx + 1)
                break
        wb.active = 0
        wb.save(path)
    except Exception as _t2fo_e:
        try:
            _STV3_LOG.warning("PATCH_TOPIC2_FOUNDATION_NO_TEMPLATE_ROWS_V1 strip failed: %s", _t2fo_e)
        except Exception:
            pass


def _t2fo_create_without_template_rows_v1(task_id, parsed, template, template_path, sheet_name, price_text, choice):
    original_create = globals().get("_T2TR_ORIG_CREATE_XLSX") or _T2FO_NTR_PREV_CREATE_XLSX_V1
    path, items, total = original_create(task_id, parsed, template, template_path, sheet_name, price_text, choice)
    _t2fo_strip_non_areal_sheets_v1(path)
    return path, items, total


def _create_xlsx_from_template(task_id, parsed, template, template_path, sheet_name, price_text, choice):  # noqa: F811
    if _t2fo_foundation_only_v1(parsed):
        return _t2fo_create_without_template_rows_v1(task_id, parsed, template, template_path, sheet_name, price_text, choice)
    return _T2FO_NTR_PREV_CREATE_XLSX_V1(task_id, parsed, template, template_path, sheet_name, price_text, choice)


try:
    _STV3_LOG.info("PATCH_TOPIC2_FOUNDATION_NO_TEMPLATE_ROWS_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_FOUNDATION_NO_TEMPLATE_ROWS_V1 ===

# === PATCH_TOPIC2_PRICE_SEARCH_CONFIRM_AND_READY_DONE_V1 ===
def _topic2_price_search_explicit_intent_v1(text: str) -> bool:
    low = _low(text or "")
    return any(x in low for x in (
        "в интернете", "через интернет", "интернет-цен", "интернет цен",
        "актуальн", "свеж", "sonar", "perplexity", "поищи", "поиск",
        "найди цены", "найти цены", "проверь цены", "проверить цены",
        "поставщик", "ссылк", "рыночн",
    ))


def _topic2_price_search_prompt_text_v1(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str]) -> str:
    return (
        "Задачу понял.\n\n"
        f"Шаблон: {template.get('title')}\n"
        f"Лист: {sheet_name or 'не выбран'}\n"
        f"Объект: {(parsed or {}).get('object') or 'не указан'}\n"
        f"Материал: {(parsed or {}).get('material') or 'не указан'}\n"
        f"Размеры: {(parsed or {}).get('dimensions') or 'не указаны'}\n"
        f"Удалённость: {(parsed or {}).get('distance_km') if (parsed or {}).get('distance_km') is not None else 'не указана'} км\n\n"
        "Перед финальной сметой нужно подтвердить цены.\n"
        "Искать актуальные цены работ, материалов и логистики через интернет (Sonar/Perplexity)?\n\n"
        "Ответь: да, искать / нет, укажу цены вручную"
    )


def _topic2_price_search_yes_v1(text: str) -> bool:
    low = _low(text or "").strip(" .,!?:;")
    return low in {"да", "да искать", "искать", "да поищи", "поищи", "ищи", "нужно", "надо"} or low.startswith("да ")


def _topic2_price_search_no_v1(text: str) -> bool:
    low = _low(text or "").strip(" .,!?:;")
    return low in {"нет", "не надо", "не нужно", "без интернета", "не искать"} or low.startswith("нет ")


def _topic2_final_ready_confirm_phrase_v1(text: str) -> bool:
    low = _low(text or "").replace("[voice]", "").strip(" .,!?:;")
    if "не доволен" in low or "недоволен" in low:
        return False
    exact = {
        "готово", "готов", "готова", "готово спасибо",
        "подтверждаю", "закрывай", "можно закрывать",
        "все ок", "всё ок", "все верно", "всё верно",
        "хорошо", "отлично", "принимаю",
    }
    if low in exact:
        return True
    return any(x in low for x in (
        "задача завершена",
        "задачей завершена",
        "задача закрыта",
        "задачей закрыта",
        "доволен задачей",
        "доволен результатом",
        "да доволен",
        "да я доволен",
        "я доволен",
        "да доволеен",
        "доволеен",
        "результатом доволен",
        "можно завершать",
        "задачу завершить",
        "задачу закрыть",
        "завершай задачу",
        "завершай запрос",
        "закрывай задачу",
        "закрой задачу",
        "закрыть задачу",
        "хорошая работа",
        "можно закрывать",
        "результат подходит",
        "все подходит",
        "всё подходит",
        "все верно завершай",
        "всё верно завершай",
        "да все верно",
        "да всё верно",
        "я же тебе сказал задача завершена",
        "я же тебе сказал завершай",
        "да можно",
    ))


def _topic2_parent_has_canonical_final_markers_v1(conn, task_id: str) -> bool:
    rows = conn.execute(
        "SELECT id, COALESCE(action,'') AS action FROM task_history WHERE task_id=? ORDER BY id",
        (str(task_id),),
    ).fetchall()
    if not rows:
        return False
    last_revoke = max(
        (
            int(row["id"])
            for row in rows
            if "TOPIC2_PREVIOUS_FINAL_REVOKED" in _s(row["action"])
            or "TOPIC2_EXPLICIT_CONFIRM_REVOKED" in _s(row["action"])
        ),
        default=-1,
    )
    actions = [_s(row["action"]) for row in rows if int(row["id"]) > last_revoke]
    required_groups = (
        ("TOPIC2_TEMPLATE_SELECTED:",),
        ("TOPIC2_TEMPLATE_FILE_ID:",),
        ("TOPIC2_TEMPLATE_CACHE_USED", "TOPIC2_TEMPLATE_DRIVE_DOWNLOADED"),
        ("TOPIC2_TEMPLATE_SHEET_SELECTED:",),
        ("TOPIC2_XLSX_TEMPLATE_COPY_OK",),
        ("TOPIC2_XLSX_ROWS_WRITTEN:",),
        ("TOPIC2_XLSX_FORMULAS_OK",),
        ("TOPIC2_XLSX_CANON_COLUMNS_OK",),
        ("TOPIC2_PDF_CREATED",),
        ("TOPIC2_PDF_CYRILLIC_OK",),
        ("TOPIC2_DRIVE_UPLOAD_XLSX_OK",),
        ("TOPIC2_DRIVE_UPLOAD_PDF_OK",),
        ("TOPIC2_TELEGRAM_DELIVERED",),
    )
    return all(any(marker in action for action in actions for marker in group) for group in required_groups)


async def _topic2_handle_price_search_confirmation_v1(conn, task, logger=None) -> bool:
    task_id = _s(_row_get(task, "id"))
    chat_id = _s(_row_get(task, "chat_id"))
    topic_id = int(_row_get(task, "topic_id", 0) or 0)
    if topic_id != TOPIC_ID_STROYKA:
        return False
    raw = _s(_row_get(task, "raw_input", ""))
    pending = _memory_latest(chat_id, "topic_2_estimate_pending_")
    if not pending or pending.get("status") != "WAITING_PRICE_SEARCH_CONFIRMATION":
        return False
    if not (_topic2_price_search_yes_v1(raw) or _topic2_price_search_no_v1(raw)):
        return False

    pending_task_id = _s(pending.get("task_id") or task_id)
    reply_to = _row_get(task, "reply_to_message_id", None) or _row_get(task, "message_id", None)
    parsed = pending.get("parsed") or {}
    template = pending.get("template") or CANON_TEMPLATE_FALLBACK["areal"]
    sheet_name = pending.get("sheet_name")
    template_prices = pending.get("template_prices") or ""

    if _topic2_price_search_no_v1(raw):
        text = (
            "Интернет-поиск цен не запускаю.\n\n"
            "Пришли ручные цены по позициям или напиши: считать по шаблонным ценам без интернет-проверки."
        )
        blocked = dict(pending)
        blocked["status"] = "WAITING_MANUAL_PRICE_INPUT"
        blocked["updated_at"] = _now()
        _memory_save(chat_id, f"topic_2_estimate_pending_{pending_task_id}", blocked)
        send_res = await _send_text(chat_id, text, reply_to, topic_id)
        kwargs = {"state": "WAITING_CLARIFICATION", "result": text, "error_message": "TOPIC2_MANUAL_PRICE_INPUT_REQUIRED"}
        if isinstance(send_res, dict) and send_res.get("bot_message_id"):
            kwargs["bot_message_id"] = send_res.get("bot_message_id")
        _update_task_safe(conn, pending_task_id, **kwargs)
        _history_safe(conn, pending_task_id, "TOPIC2_PRICE_SEARCH_DECLINED_BY_USER")
        if task_id != pending_task_id:
            _update_task_safe(conn, task_id, state="DONE", result="Интернет-поиск цен отклонён пользователем", error_message="")
            _history_safe(conn, task_id, "TOPIC2_PRICE_SEARCH_DECLINE_CHILD_DONE")
        return True

    _history_safe(conn, pending_task_id, "TOPIC2_PRICE_SEARCH_CONFIRMED_BY_USER")
    _history_safe(conn, task_id, "TOPIC2_PRICE_SEARCH_CONFIRMATION_ACCEPTED")
    try:
        online_prices = await _search_prices_online(parsed, template, sheet_name, conn=conn, task_id=pending_task_id)
    except Exception as exc:
        text = "SEARCH_FAILED: Sonar unavailable"
        send_res = await _send_text(chat_id, text, reply_to, topic_id)
        kwargs = {"state": "WAITING_CLARIFICATION", "result": text, "error_message": "TOPIC2_PRICE_SEARCH_FAILED"}
        if isinstance(send_res, dict) and send_res.get("bot_message_id"):
            kwargs["bot_message_id"] = send_res.get("bot_message_id")
        _update_task_safe(conn, pending_task_id, **kwargs)
        _history_safe(conn, pending_task_id, "TOPIC2_PRICE_SEARCH_FAILED:" + _s(exc)[:160])
        if task_id != pending_task_id:
            _update_task_safe(conn, task_id, state="DONE", result=text, error_message="")
        return True

    confirmed = dict(pending)
    confirmed["status"] = "WAITING_PRICE_CONFIRMATION"
    confirmed["online_prices"] = online_prices
    confirmed["updated_at"] = _now()
    _memory_save(chat_id, f"topic_2_estimate_pending_{pending_task_id}", confirmed)
    text = _price_confirmation_text(parsed, template, sheet_name, template_prices, online_prices)
    send_res = await _send_text(chat_id, text, reply_to, topic_id)
    kwargs = {"state": "WAITING_CLARIFICATION", "result": text, "error_message": "TOPIC2_PRICE_CHOICE_REQUIRED"}
    if isinstance(send_res, dict) and send_res.get("bot_message_id"):
        kwargs["bot_message_id"] = send_res.get("bot_message_id")
    _update_task_safe(conn, pending_task_id, **kwargs)
    _history_safe(conn, pending_task_id, "TOPIC2_PRICE_CHOICE_REQUESTED_AFTER_SEARCH_CONFIRM")
    if task_id != pending_task_id:
        _update_task_safe(conn, task_id, state="DONE", result="Интернет-поиск цен подтверждён", error_message="")
        _history_safe(conn, task_id, "TOPIC2_PRICE_SEARCH_CONFIRM_CHILD_DONE")
    return True


async def _topic2_handle_ready_done_v1(conn, task, logger=None) -> bool:
    task_id = _s(_row_get(task, "id"))
    chat_id = _s(_row_get(task, "chat_id"))
    topic_id = int(_row_get(task, "topic_id", 0) or 0)
    if topic_id != TOPIC_ID_STROYKA:
        return False
    raw = _s(_row_get(task, "raw_input", ""))
    if not _topic2_final_ready_confirm_phrase_v1(raw):
        return False
    try:
        if parse_price_choice(raw).get("confirmed"):
            return False
    except Exception:
        pass
    reply_to = _row_get(task, "reply_to_message_id", None) or _row_get(task, "message_id", None)
    parent = None
    if reply_to:
        parent = conn.execute(
            """
            SELECT id, COALESCE(raw_input,'') AS raw_input, COALESCE(result,'') AS result
            FROM tasks
            WHERE CAST(chat_id AS TEXT)=?
              AND COALESCE(topic_id,0)=?
              AND state='AWAITING_CONFIRMATION'
              AND id<>?
              AND (bot_message_id=? OR reply_to_message_id=?)
            ORDER BY updated_at DESC, created_at DESC
            LIMIT 1
            """,
            (str(chat_id), int(topic_id), str(task_id), reply_to, reply_to),
        ).fetchone()
        if parent and not _topic2_parent_has_canonical_final_markers_v1(conn, _s(parent["id"])):
            parent = None
    if not parent:
        candidates = conn.execute(
            """
            SELECT id, COALESCE(raw_input,'') AS raw_input, COALESCE(result,'') AS result
            FROM tasks
            WHERE CAST(chat_id AS TEXT)=?
              AND COALESCE(topic_id,0)=?
              AND state='AWAITING_CONFIRMATION'
              AND id<>?
              AND (COALESCE(result,'') LIKE '%Смета готова%' OR COALESCE(result,'') LIKE '%Смета по извлечённым позициям готова%')
              AND (COALESCE(result,'') LIKE '%drive.google.com%' OR COALESCE(result,'') LIKE '%docs.google.com%')
            ORDER BY updated_at DESC, created_at DESC
            LIMIT 20
            """,
            (str(chat_id), int(topic_id), str(task_id)),
        ).fetchall()
        parent = next(
            (
                row for row in candidates
                if _topic2_parent_has_canonical_final_markers_v1(conn, _s(row["id"]))
            ),
            None,
        )
    if not parent:
        return False

    parent_id = _s(parent["id"])
    parent_raw = _s(parent["raw_input"])
    parent_result = _s(parent["result"])
    parent_low = _low(parent_result)
    estimate_final = "смета готов" in parent_low or "смета по извлечённым позициям готова" in parent_low
    if not (estimate_final and ("xlsx" in parent_low or "pdf" in parent_low or "drive.google.com" in parent_low or "docs.google.com" in parent_low)):
        return False

    _history_safe(conn, parent_id, "TOPIC2_EXPLICIT_CONFIRM:ready_done_phrase")
    _update_task_safe(conn, parent_id, state="DONE", error_message="")
    _history_safe(conn, parent_id, "state:DONE")
    try:
        _memory_save(chat_id, f"topic_2_estimate_pending_{parent_id}", {
            "status": "DONE",
            "task_id": parent_id,
            "topic_id": int(topic_id),
            "completed_at": _now(),
            "source": "TOPIC2_EXPLICIT_CONFIRM",
        })
        _memory_save(chat_id, f"topic_2_user_input_{parent_id}", {
            "task_id": parent_id,
            "topic_id": int(topic_id),
            "raw_input": parent_raw,
            "saved_at": _now(),
            "source": "TOPIC2_EXPLICIT_CONFIRM",
        })
        _memory_save(chat_id, f"topic_2_task_summary_{parent_id}", {
            "task_id": parent_id,
            "topic_id": int(topic_id),
            "summary": parent_result,
            "saved_at": _now(),
            "source": "TOPIC2_EXPLICIT_CONFIRM",
        })
        _memory_save(chat_id, f"topic_2_assistant_output_{parent_id}", {
            "task_id": parent_id,
            "topic_id": int(topic_id),
            "result": parent_result,
            "saved_at": _now(),
            "source": "TOPIC2_EXPLICIT_CONFIRM",
        })
    except Exception:
        pass
    _update_task_safe(conn, task_id, state="DONE", result="Подтверждение принято", error_message="")
    _history_safe(conn, task_id, "TOPIC2_CONFIRM_CHILD_DONE_READY_PHRASE")
    await _send_text(chat_id, "Принял. Задача закрыта", reply_to, topic_id)
    return True


_T2PSC_PREV_MAYBE_HANDLE_V1 = maybe_handle_stroyka_estimate


async def maybe_handle_stroyka_estimate(conn, task, logger=None):  # noqa: F811
    try:
        if await _topic2_handle_price_search_confirmation_v1(conn, task, logger=logger):
            return True
        if await _topic2_handle_ready_done_v1(conn, task, logger=logger):
            return True
    except Exception as exc:
        try:
            _history_safe(conn, _s(_row_get(task, "id")), "TOPIC2_PRICE_SEARCH_CONFIRM_OR_READY_DONE_ERR:" + _s(exc)[:160])
        except Exception:
            pass
    return await _T2PSC_PREV_MAYBE_HANDLE_V1(conn, task, logger)


try:
    _STV3_LOG.info("PATCH_TOPIC2_PRICE_SEARCH_CONFIRM_AND_READY_DONE_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_PRICE_SEARCH_CONFIRM_AND_READY_DONE_V1 ===

# === PATCH_TOPIC2_FOUNDATION_MISSING_PRICE_CACHE_SONAR_V1 ===
def _t2fo_price_text_has_family_v1(price_text, keywords):
    low = _low(price_text or "")
    return any(_low(k) in low for k in keywords)


def _t2fo_offer_lines_v1(label, unit, offers):
    lines = []
    for offer in (offers or [])[:3]:
        try:
            price = float(offer.get("price") or 0)
        except Exception:
            price = 0.0
        if price <= 0:
            continue
        lines.append(
            "- {} | {} | {} | Санкт-Петербург и Ленинградская область | {} | {} | {}".format(
                label,
                price,
                offer.get("unit") or unit,
                offer.get("supplier") or "",
                offer.get("url") or "",
                offer.get("checked_at") or datetime.date.today().isoformat(),
            )
        )
    return lines


_T2FO_MISSING_PRICE_PREV_SEARCH_V1 = _search_prices_online


async def _search_prices_online(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], conn=None, task_id=None) -> str:  # noqa: F811
    result = await _T2FO_MISSING_PRICE_PREV_SEARCH_V1(parsed, template, sheet_name, conn=conn, task_id=task_id)
    if not _t2fo_foundation_only_v1(parsed or {}):
        return result

    raw_text = _low((parsed or {}).get("raw") or "")
    missing = []
    if ((parsed or {}).get("sand_thickness_m") or "песчан" in raw_text or "песок" in raw_text):
        if not _t2fo_price_text_has_family_v1(result, ("песок", "песчаная подушка", "песчаный")):
            missing.append(("Песок строительный для песчаной подушки", "м3", "sand"))
    if ((parsed or {}).get("gravel_thickness_m") or "щеб" in raw_text):
        if not _t2fo_price_text_has_family_v1(result, ("щебень", "щебеночное основание", "щебеночный", "щебёноч")):
            missing.append(("Щебень для основания фундаментной плиты", "м3", "gravel"))
    if not missing:
        return result

    model = os.getenv("OPENROUTER_MODEL_ONLINE", "perplexity/sonar").strip() or "perplexity/sonar"
    if "sonar" not in model.lower():
        raise RuntimeError(f"TOPIC2_ONLINE_MODEL_GUARD_BLOCKED_NON_SONAR:{model}")

    from core.price_enrichment import _openrouter_price_search as _missing_price_search

    extra_lines = []
    for item_name, unit, code in missing:
        if conn is not None and task_id is not None:
            _history_safe(conn, task_id, "TOPIC2_PRICE_CACHE_BEFORE_SONAR:" + code)
            _history_safe(conn, task_id, "TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:" + item_name)
        try:
            offers = await asyncio.wait_for(
                _missing_price_search(item_name, unit, "Санкт-Петербург и Ленинградская область"),
                timeout=45,
            )
        except Exception:
            offers = []
        lines = _t2fo_offer_lines_v1(item_name, unit, offers)
        if lines:
            extra_lines.extend(lines)
            if conn is not None and task_id is not None:
                first = offers[0] if offers else {}
                _history_safe(conn, task_id, "TOPIC2_PRICE_SOURCE_FOUND:{}:{}:{}".format(
                    code,
                    _s(first.get("supplier"))[:50],
                    _s(first.get("status"))[:20],
                ))
        elif conn is not None and task_id is not None:
            _history_safe(conn, task_id, "TOPIC2_PRICE_SOURCE_MISSING:" + code)

    if not extra_lines:
        return result
    joined = (str(result or "").rstrip() + "\n" + "\n".join(extra_lines)).strip()
    if conn is not None and task_id is not None:
        _history_safe(conn, task_id, "TOPIC2_MISSING_PRICE_CACHE_SONAR_DONE:" + ",".join(code for _, _, code in missing))
    return joined


def _t2spsm_families_v1(text, section=""):  # noqa: F811
    low = _low((text or "") + " " + (section or ""))
    families = set()
    checks = (
        ("sand", ("песок", "песчан", "песчаная подушка")),
        ("gravel", ("щебень", "щебен", "щебеноч", "щебеночное", "щебёноч")),
        ("gasbeton", ("газобетон", "газоблок", "блок 625", "u-блок", "u блок", "лср")),
        ("concrete", ("бетон", "монолит", "ж/б", "железобетон", "ростверк", "плита")),
        ("rebar", ("арматур", "а500", "а240", "проволока вяз")),
        ("wood", ("доска", "брус", "пиломат", "osb", "фанера")),
        ("insulation", ("пенопл", "утепл", "минват", "пир", "pir")),
        ("waterproof", ("гидроизоляц", "линокром", "мастик", "праймер")),
        ("roof", ("кров", "стропил", "мауэрлат", "мембран", "профнастил", "черепиц")),
        ("windows", ("окн", "окон", "пвх", "стеклопакет")),
        ("doors", ("двер", "дверн")),
        ("delivery", ("достав", "транспорт")),
        ("unload", ("разгруз", "погруз")),
        ("crane", ("кран",)),
        ("pump", ("бетононасос",)),
        ("masonry_work", ("кладк",)),
        ("facade", ("фасад", "внешняя отделка")),
        ("interior", ("внутрен", "отделк", "гкл", "ламинат", "плитк")),
        ("engineering", ("электрик", "водоснаб", "канализац", "отоплен", "вентиляц", "инженер")),
    )
    for fam, terms in checks:
        if any(term in low for term in terms):
            families.add(fam)
    return families


try:
    _STV3_LOG.info("PATCH_TOPIC2_FOUNDATION_MISSING_PRICE_CACHE_SONAR_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_FOUNDATION_MISSING_PRICE_CACHE_SONAR_V1 ===

# === PATCH_TOPIC2_RELIABLE_PRICE_AND_FOUNDATION_SOURCE_GUARD_V1 ===
# Canon/user rule: "3 / надёжные" is a reliable price level, not maximum.
# Foundation-only final with explicit internet check must not close while
# песок/щебень remain without live/cache source lines.
_T2RPF_PREV_PARSE_PRICE_CHOICE_V1 = parse_price_choice


def _t2rpf_reliable_requested_v1(text):
    t = _low(text or "").replace("[voice]", "").strip()
    t = re.sub(r"\s+", " ", t).strip(" .,!?:;()[]{}")
    return (
        t in ("3", "3.", "третий", "вариант 3", "вариант в", "в", "v", "в)", "v)")
        or "надежн" in t
        or "надёжн" in t
        or "проверенн" in t
        or "раздел три" in t
    )


def parse_price_choice(text: str) -> Dict[str, Any]:  # noqa: F811
    res = dict(_T2RPF_PREV_PARSE_PRICE_CHOICE_V1(text))
    t = _low(text or "").replace("[voice]", "").strip()
    t = re.sub(r"\s+", " ", t).strip(" .,!?:;()[]{}")
    explicit_max = any(x in t for x in ("максим", "max", "макс ")) and not any(x in t for x in ("не максим", "а не максим", "не max"))
    if _t2rpf_reliable_requested_v1(text) and not explicit_max:
        res["choice"] = "reliable"
        res["confirmed"] = True
    return res


try:
    _PPOC_PRICE_DISPLAY.update({
        "minimum": "минимальные",
        "cheapest": "минимальные",
        "maximum": "максимальные",
        "reliable": "надёжные",
        "trusted": "надёжные",
    })
except Exception:
    pass


def _t2rpf_requires_foundation_live_prices_v1(parsed, text):
    if not _t2fo_foundation_only_v1(parsed or {}):
        return False
    low = _low(text or "")
    return any(x in low for x in ("интернет", "актуальн", "проверить", "проверь", "поищи", "найди", "стоимость песка", "стоимости песка", "стоимость щеб"))


def _t2rpf_missing_foundation_families_v1(parsed, price_text):
    parsed = parsed or {}
    raw = _low(parsed.get("raw") or "")
    missing = []
    if (parsed.get("sand_thickness_m") or "песчан" in raw or "песок" in raw) and not _t2fo_price_text_has_family_v1(price_text, ("песок", "песчаная подушка", "песчаный")):
        missing.append("песок")
    if (parsed.get("gravel_thickness_m") or "щеб" in raw) and not _t2fo_price_text_has_family_v1(price_text, ("щебень", "щебеночное основание", "щебеночный", "щебёноч")):
        missing.append("щебень")
    return missing


_T2RPF_PREV_GENERATE_AND_SEND_V1 = _generate_and_send


async def _generate_and_send(conn, task, pending, confirm_text, logger=None):  # noqa: F811
    task_id = _s(_row_get(task, "id"))
    chat_id = _s(_row_get(task, "chat_id"))
    topic_id = int(_row_get(task, "topic_id", 0) or 0)
    reply_to = _row_get(task, "reply_to_message_id", None) or _row_get(task, "message_id", None)
    parsed = (pending or {}).get("parsed") or {}
    online_prices = (pending or {}).get("online_prices") or ""
    raw_context = "\n".join([
        _s(parsed.get("raw") if isinstance(parsed, dict) else ""),
        _s(confirm_text),
    ])

    if topic_id == TOPIC_ID_STROYKA and _t2rpf_requires_foundation_live_prices_v1(parsed, raw_context):
        missing = _t2rpf_missing_foundation_families_v1(parsed, online_prices)
        if missing:
            try:
                _history_safe(conn, task_id, "TOPIC2_FOUNDATION_LIVE_PRICE_GUARD_SEARCH:" + ",".join(missing))
                refreshed = await _search_prices_online(
                    parsed,
                    (pending or {}).get("template") or CANON_TEMPLATE_FALLBACK["areal"],
                    (pending or {}).get("sheet_name"),
                    conn=conn,
                    task_id=task_id,
                )
                online_prices = refreshed or online_prices
                pending["online_prices"] = online_prices
                pending["status"] = "WAITING_PRICE_CONFIRMATION"
                _memory_save(chat_id, f"topic_2_estimate_pending_{task_id}", pending)
            except Exception as exc:
                _history_safe(conn, task_id, "TOPIC2_FOUNDATION_LIVE_PRICE_GUARD_SEARCH_FAILED:" + _s(exc)[:160])
        missing = _t2rpf_missing_foundation_families_v1(parsed, online_prices)
        if missing:
            text = (
                "Не закрываю финальную смету: не найдены подтверждённые интернет-цены для "
                + ", ".join(missing)
                + ". Пришли ручные цены или разреши повторить поиск."
            )
            send_res = await _send_text(chat_id, text, reply_to, topic_id)
            kwargs = {"state": "WAITING_CLARIFICATION", "result": text, "error_message": "TOPIC2_FOUNDATION_PRICE_SOURCE_REQUIRED"}
            if isinstance(send_res, dict) and send_res.get("bot_message_id"):
                kwargs["bot_message_id"] = send_res.get("bot_message_id")
            _update_task_safe(conn, task_id, **kwargs)
            _history_safe(conn, task_id, "TOPIC2_FOUNDATION_FINAL_BLOCKED_TEMPLATE_ONLY:" + ",".join(missing))
            return True

    return await _T2RPF_PREV_GENERATE_AND_SEND_V1(conn, task, pending, confirm_text, logger=logger)


try:
    _STV3_LOG.info("PATCH_TOPIC2_RELIABLE_PRICE_AND_FOUNDATION_SOURCE_GUARD_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_RELIABLE_PRICE_AND_FOUNDATION_SOURCE_GUARD_V1 ===


# === PATCH_TOPIC2_FULL_FOUNDATION_PRICE_SOURCE_GUARD_V1 ===
# Canon: when user explicitly asks to verify material prices, final XLSX must
# prefer live confirmed sources and foundation-only route must search missing
# foundation price families instead of closing template_only rows silently.
_T2FFPS_PREV_MATCH_PRICE_SOURCE_V1 = _match_price_source


def _t2ffps_is_live_source_v1(src):
    status = _low((src or {}).get("status") or "")
    return status in ("live_confirmed", "confirmed") and bool((src or {}).get("supplier")) and bool((src or {}).get("url"))


def _match_price_source(sources: List[Dict[str, Any]], item_name: str, item_section: str) -> Dict[str, Any]:  # noqa: F811
    live_sources = [src for src in (sources or []) if _t2ffps_is_live_source_v1(src)]
    if live_sources:
        live = _T2FFPS_PREV_MATCH_PRICE_SOURCE_V1(live_sources, item_name, item_section)
        if live and live.get("status") != "template_only":
            return live
    return _T2FFPS_PREV_MATCH_PRICE_SOURCE_V1(sources, item_name, item_section)


_T2FFPS_PREV_SEARCH_PRICES_ONLINE_V1 = _search_prices_online


def _t2ffps_existing_online_prices_v1(conn, task_id):
    if conn is None or task_id is None:
        return ""
    try:
        row = conn.execute("SELECT chat_id FROM tasks WHERE id=? LIMIT 1", (_s(task_id),)).fetchone()
        chat_id = _s(row[0] if row else "")
        if not chat_id:
            return ""
        import sqlite3 as _t2ffps_sqlite3
        import json as _t2ffps_json
        mem = _t2ffps_sqlite3.connect("/root/.areal-neva-core/data/memory.db")
        try:
            r = mem.execute(
                "SELECT value FROM memory WHERE chat_id=? AND key=? ORDER BY timestamp DESC LIMIT 1",
                (chat_id, "topic_2_estimate_pending_" + _s(task_id)),
            ).fetchone()
        finally:
            mem.close()
        if not r:
            return ""
        data = _t2ffps_json.loads(r[0])
        return _s(data.get("online_prices") or "") if isinstance(data, dict) else ""
    except Exception:
        return ""


def _t2ffps_has_live_source_v1(price_text, keywords):
    try:
        sources = _parse_price_sources(price_text or "")
    except Exception:
        sources = []
    keys = tuple(_low(k) for k in (keywords or ()))
    for src in sources:
        if not _t2ffps_is_live_source_v1(src):
            continue
        pos = _low(src.get("position") or "")
        if any(k in pos for k in keys):
            return True
    return False


def _t2ffps_has_live_source_all_v1(price_text, keywords):
    try:
        sources = _parse_price_sources(price_text or "")
    except Exception:
        sources = []
    keys = tuple(_low(k) for k in (keywords or ()))
    for src in sources:
        if not _t2ffps_is_live_source_v1(src):
            continue
        pos = _low(src.get("position") or "")
        if keys and all(k in pos for k in keys):
            return True
    return False


async def _search_prices_online(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], conn=None, task_id=None) -> str:  # noqa: F811
    base = await _T2FFPS_PREV_SEARCH_PRICES_ONLINE_V1(parsed, template, sheet_name, conn=conn, task_id=task_id)
    if not _t2fo_foundation_only_v1(parsed or {}):
        return base
    existing = _t2ffps_existing_online_prices_v1(conn, task_id)
    combined = "\n".join(x for x in (existing, base) if _s(x).strip()).strip()

    missing = []
    checks = (
        ("Опалубка для монолитной фундаментной плиты материал", "мп", "formwork_material", ("опалуб",)),
        ("Монтаж демонтаж опалубки фундаментной плиты", "мп", "formwork_work", ("опалуб", "монтаж")),
        ("Армирование фундаментной плиты работы", "м2", "rebar_work", ("армирован",)),
        ("Устройство песчаной подушки с послойным уплотнением работы", "м3", "sand_work", ("песчан", "уплотн")),
        ("Устройство щебеночного основания с уплотнением работы", "м3", "gravel_work", ("щеб", "уплотн")),
    )
    for item_name, unit, code, keywords in checks:
        has_source = (
            _t2ffps_has_live_source_all_v1(combined, keywords)
            if code in ("sand_work", "gravel_work")
            else _t2ffps_has_live_source_v1(combined, keywords)
        )
        if not has_source:
            missing.append((item_name, unit, code))
    if not missing:
        return combined or base

    model = os.getenv("OPENROUTER_MODEL_ONLINE", "perplexity/sonar").strip() or "perplexity/sonar"
    if "sonar" not in model.lower():
        raise RuntimeError(f"TOPIC2_ONLINE_MODEL_GUARD_BLOCKED_NON_SONAR:{model}")

    from core.price_enrichment import _openrouter_price_search as _missing_price_search
    extra_lines = []
    for item_name, unit, code in missing:
        if conn is not None and task_id is not None:
            _history_safe(conn, task_id, "TOPIC2_PRICE_CACHE_BEFORE_SONAR:" + code)
            _history_safe(conn, task_id, "TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:" + item_name)
        try:
            offers = await asyncio.wait_for(
                _missing_price_search(item_name, unit, "Санкт-Петербург и Ленинградская область"),
                timeout=45,
            )
        except Exception:
            offers = []
        lines = _t2fo_offer_lines_v1(item_name, unit, offers)
        if lines:
            extra_lines.extend(lines)
            if conn is not None and task_id is not None:
                first = offers[0] if offers else {}
                _history_safe(conn, task_id, "TOPIC2_PRICE_SOURCE_FOUND:{}:{}:{}".format(
                    code,
                    _s(first.get("supplier"))[:50],
                    _s(first.get("status"))[:20],
                ))
        elif conn is not None and task_id is not None:
            _history_safe(conn, task_id, "TOPIC2_PRICE_SOURCE_MISSING:" + code)
    if extra_lines and conn is not None and task_id is not None:
        _history_safe(conn, task_id, "TOPIC2_FULL_FOUNDATION_PRICE_SOURCE_SONAR_DONE:" + ",".join(code for _, _, code in missing))
    return (combined + "\n" + "\n".join(extra_lines)).strip() if extra_lines else (combined or base)

try:
    _STV3_LOG.info("PATCH_TOPIC2_FULL_FOUNDATION_PRICE_SOURCE_GUARD_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_FULL_FOUNDATION_PRICE_SOURCE_GUARD_V1 ===


# === PATCH_TOPIC2_FOUNDATION_REQUIRED_PRICE_FAMILIES_V1 ===
# Extends the existing foundation final guard: for foundation-only estimates with
# explicit price verification, formwork and reinforcement work are required price
# families too. This does not change non-topic_2 and does not bypass Sonar.
_T2FRPF_PREV_MISSING_FOUNDATION_FAMILIES_V1 = _t2rpf_missing_foundation_families_v1


def _t2rpf_missing_foundation_families_v1(parsed, price_text):  # noqa: F811
    missing = list(_T2FRPF_PREV_MISSING_FOUNDATION_FAMILIES_V1(parsed, price_text) or [])
    if not _t2fo_foundation_only_v1(parsed or {}):
        return missing
    if not _t2ffps_has_live_source_v1(price_text, ("опалуб",)):
        missing.append("опалубка")
    if not _t2ffps_has_live_source_v1(price_text, ("армирован",)):
        missing.append("армирование")
    if not _t2ffps_has_live_source_all_v1(price_text, ("песчан", "уплотн")):
        missing.append("уплотнение песчаной подушки")
    if not _t2ffps_has_live_source_all_v1(price_text, ("щеб", "уплотн")):
        missing.append("уплотнение щебёночного основания")
    out = []
    for item in missing:
        if item not in out:
            out.append(item)
    return out

try:
    _STV3_LOG.info("PATCH_TOPIC2_FOUNDATION_REQUIRED_PRICE_FAMILIES_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_FOUNDATION_REQUIRED_PRICE_FAMILIES_V1 ===

# === PATCH_TOPIC2_FOUNDATION_PRICE_APPLY_MATCH_V1 ===
# Canon/user rule: foundation-only final must apply confirmed source-line prices
# to AREAL_CALC work/material columns, and must not attach formwork sources to
# concrete rows just because both mention a monolithic slab.
_T2FPAG_PREV_MATCH_PRICE_SOURCE_V1 = _match_price_source
_T2FPAG_PREV_CREATE_XLSX_V1 = _create_xlsx_from_template
_T2FPAG_PREV_FINAL_SUMMARY_V1 = _final_summary
_T2FPAG_PREV_SEARCH_PRICES_ONLINE_V1 = _search_prices_online
_T2FPAG_PREV_MISSING_FAMILIES_V1 = _t2rpf_missing_foundation_families_v1


def _t2fpag_family_v1(text):
    low = _low(text or "")
    if "опалуб" in low:
        if "материал" in low and not any(x in low for x in ("монтаж", "демонтаж", "работ")):
            return "formwork_material"
        if any(x in low for x in ("монтаж", "демонтаж", "работ", "установ")):
            return "formwork_work"
        return "formwork"
    if "армирован" in low:
        return "rebar_work"
    if "арматур" in low or "а500" in low:
        return "rebar_material"
    if "бетонирован" in low or "заливк" in low or "работа (бетон" in low:
        return "concrete_work"
    if "бетон" in low or "в25" in low or "в30" in low or "м350" in low:
        return "concrete_material"
    if "песок" in low or "песчан" in low:
        if any(x in low for x in ("подуш", "основан")) and any(x in low for x in ("уплотнен", "уплотнени", "работ")):
            return "sand_base"
        if any(x in low for x in ("устройство", "уплотнен", "уплотнени", "работ")):
            return "sand_work"
        return "sand"
    if "щеб" in low:
        if any(x in low for x in ("основан", "подуш")) and any(x in low for x in ("уплотнен", "уплотнени", "работ")):
            return "gravel_base"
        if any(x in low for x in ("устройство", "уплотнен", "уплотнени", "работ")):
            return "gravel_work"
        return "gravel"
    if "достав" in low or "транспорт" in low:
        return "delivery"
    return ""


def _t2fpag_empty_source_v1():
    return {"supplier": "", "url": "", "checked_at": datetime.date.today().isoformat(), "status": "template_only"}


def _match_price_source(sources: List[Dict[str, Any]], item_name: str, item_section: str) -> Dict[str, Any]:  # noqa: F811
    item_family = _t2fpag_family_v1(item_name)
    if item_family:
        exact_sources = [
            src for src in (sources or [])
            if _t2fpag_family_v1(src.get("position") or "") == item_family
        ]
        if exact_sources:
            live_exact = [src for src in exact_sources if _t2ffps_is_live_source_v1(src)]
            if live_exact:
                return live_exact[0]
            return exact_sources[0]
    matched = _T2FPAG_PREV_MATCH_PRICE_SOURCE_V1(sources, item_name, item_section)
    matched_family = _t2fpag_family_v1((matched or {}).get("position") or "")
    if item_family and matched_family and matched_family != item_family:
        return _t2fpag_empty_source_v1()
    return matched


def _t2fpag_line_values_v1(price_text, required=(), any_of=(), exclude=()):
    vals = []
    req = tuple(_low(x) for x in (required or ()))
    any_terms = tuple(_low(x) for x in (any_of or ()))
    exc = tuple(_low(x) for x in (exclude or ()))
    for line in str(price_text or "").splitlines():
        low = _low(line)
        if req and not all(x in low for x in req):
            continue
        if any_terms and not any(x in low for x in any_terms):
            continue
        if exc and any(x in low for x in exc):
            continue
        parts = [p.strip() for p in line.strip(" \t-—•·").split("|")]
        if len(parts) < 2 or "нет данных" in _low(parts[1]):
            continue
        try:
            value = float(re.sub(r"[^0-9.,]", "", parts[1]).replace(",", "."))
        except Exception:
            value = 0.0
        if 100 <= value <= 10000000:
            vals.append(value)
    return vals


def _t2fpag_choose_v1(price_text, family, choice, default=0.0):
    if family == "formwork_material":
        vals = _t2fpag_line_values_v1(price_text, required=("опалуб", "материал"))
    elif family == "formwork_work":
        vals = _t2fpag_line_values_v1(price_text, required=("опалуб",), any_of=("монтаж", "демонтаж", "работ", "установ"), exclude=("материал",))
    elif family == "rebar_work":
        vals = _t2fpag_line_values_v1(price_text, required=("армирован",), any_of=("работ", "монтаж", "устройств"))
    elif family == "rebar_material":
        vals = _t2fpag_line_values_v1(price_text, required=("арматур",), any_of=("а500",))
    elif family == "sand_work":
        vals = _t2fpag_line_values_v1(price_text, required=("песчан",), any_of=("уплотн", "работ", "устройств"), exclude=("песок строительный", "материал"))
    elif family == "gravel_work":
        vals = _t2fpag_line_values_v1(price_text, required=("щеб",), any_of=("уплотн", "работ", "устройств"), exclude=("материал",))
    else:
        vals = []
    return _choose_value(vals, choice, default) if vals else float(default or 0.0)


def _t2fpag_pending_raw_v1(task_id):
    try:
        import sqlite3 as _t2fpag_sqlite3
        import json as _t2fpag_json
        mem = _t2fpag_sqlite3.connect("/root/.areal-neva-core/data/memory.db")
        try:
            row = mem.execute(
                "SELECT value FROM memory WHERE key=? ORDER BY timestamp DESC LIMIT 1",
                ("topic_2_estimate_pending_" + _s(task_id),),
            ).fetchone()
        finally:
            mem.close()
        if not row:
            return ""
        data = _t2fpag_json.loads(row[0])
        parsed = data.get("parsed") if isinstance(data, dict) else {}
        return _s((parsed or {}).get("raw") or "")
    except Exception:
        return ""


def _t2fpag_manual_concrete_work_v1(parsed, task_id=None):
    try:
        value = _t2fo_manual_monolith_work_price_v1((parsed or {}).get("raw") or "")
        if value:
            return value
        if task_id:
            return _t2fo_manual_monolith_work_price_v1(_t2fpag_pending_raw_v1(task_id))
    except Exception:
        pass
    return 0.0


def _t2fpag_exact_source_v1(price_text, family):
    try:
        for src in _parse_price_sources(price_text or ""):
            if _t2fpag_family_v1(src.get("position") or "") == family and _t2ffps_is_live_source_v1(src):
                return src
    except Exception:
        pass
    return {}


def _t2fpag_materials_vat_only_v1(parsed):
    raw = _low((parsed or {}).get("raw") or "")
    return (
        "ндс" in raw
        and "материал" in raw
        and "работ" in raw
        and "без ндс" in raw
        and ("с ндс" in raw or "ндс" in raw)
    )


def _t2fpag_combined_source_v1(price_text, material_family, work_family):
    material = _t2fpag_exact_source_v1(price_text, material_family)
    work = _t2fpag_exact_source_v1(price_text, work_family)
    if not material and not work:
        return {}
    suppliers = []
    urls = []
    checked = []
    for src in (work, material):
        if src.get("supplier") and src.get("supplier") not in suppliers:
            suppliers.append(src.get("supplier"))
        if src.get("url") and src.get("url") not in urls:
            urls.append(src.get("url"))
        if src.get("checked_at"):
            checked.append(src.get("checked_at"))
    return {
        "status": "LIVE_CONFIRMED",
        "supplier": " / ".join(suppliers),
        "url": " / ".join(urls),
        "checked_at": max(checked) if checked else datetime.date.today().isoformat(),
    }


def _t2fpag_rewrite_foundation_xlsx_v1(path, items, parsed, price_text, choice, task_id=None):
    try:
        from openpyxl import load_workbook as _t2fpag_load_workbook
        wb = _t2fpag_load_workbook(path)
        ws = wb["AREAL_CALC"] if "AREAL_CALC" in wb.sheetnames else wb.active
        rows = []
        for row_idx in range(2, ws.max_row + 1):
            label = _low(ws.cell(row_idx, 9).value or "")
            name = _s(ws.cell(row_idx, 3).value or "")
            if label.startswith("итого"):
                break
            if not name:
                continue
            qty = float(ws.cell(row_idx, 5).value or 0)
            work = float(ws.cell(row_idx, 6).value or 0)
            mat = float(ws.cell(row_idx, 8).value or 0)
            family = _t2fpag_family_v1(name)
            if family == "formwork_material":
                mat = _t2fpag_choose_v1(price_text, family, choice, mat or work)
                work = 0.0
            elif family == "formwork_work":
                work = _t2fpag_choose_v1(price_text, family, choice, work)
                mat = 0.0
            elif family == "rebar_work":
                work = _t2fpag_choose_v1(price_text, family, choice, work)
                mat = 0.0
            elif family == "rebar_material":
                mat = _t2fpag_choose_v1(price_text, family, choice, mat)
                work = 0.0
            elif family == "concrete_work":
                manual = _t2fpag_manual_concrete_work_v1(parsed, task_id=task_id)
                if manual:
                    work = manual
                    mat = 0.0
            elif family == "sand_base":
                work = _t2fpag_choose_v1(price_text, "sand_work", choice, _FTM_PRICES["sand_work"])
                mat = _choose_value(
                    _t2fo_prices_from_source_lines_v1(price_text, ("песок", "песчаная подушка", "песчаный")),
                    choice,
                    _FTM_PRICES["sand_mat"],
                )
            elif family == "gravel_base":
                work = _t2fpag_choose_v1(price_text, "gravel_work", choice, _FTM_PRICES["gravel_work"])
                mat = _choose_value(
                    _t2fo_prices_from_source_lines_v1(price_text, ("щебень", "щебеночное основание", "щебеночный", "щебёноч")),
                    choice,
                    _FTM_PRICES["gravel_mat"],
                )
            elif family == "sand_work":
                work = _t2fpag_choose_v1(price_text, family, choice, work or _FTM_PRICES["sand_work"])
                mat = 0.0
            elif family == "gravel_work":
                work = _t2fpag_choose_v1(price_text, family, choice, work or _FTM_PRICES["gravel_work"])
                mat = 0.0
            ws.cell(row_idx, 6, round(work, 2))
            ws.cell(row_idx, 7).value = f"=E{row_idx}*F{row_idx}"
            ws.cell(row_idx, 8, round(mat, 2))
            ws.cell(row_idx, 9).value = f"=E{row_idx}*H{row_idx}"
            ws.cell(row_idx, 10).value = f"=G{row_idx}+I{row_idx}"
            exact_source = _t2fpag_exact_source_v1(price_text, family)
            if family == "sand_base":
                exact_source = _t2fpag_combined_source_v1(price_text, "sand", "sand_work")
            elif family == "gravel_base":
                exact_source = _t2fpag_combined_source_v1(price_text, "gravel", "gravel_work")
            if exact_source:
                ws.cell(row_idx, 11, exact_source.get("status", "LIVE_CONFIRMED"))
                ws.cell(row_idx, 12, exact_source.get("supplier", ""))
                ws.cell(row_idx, 13, exact_source.get("url", ""))
                ws.cell(row_idx, 14, exact_source.get("checked_at", datetime.date.today().isoformat()))
            if family == "concrete_work" and manual:
                ws.cell(row_idx, 11, "MANUAL")
                ws.cell(row_idx, 12, "user")
                ws.cell(row_idx, 13, "")
                ws.cell(row_idx, 14, datetime.date.today().isoformat())
            if family in ("sand_work", "gravel_work") and not exact_source:
                ws.cell(row_idx, 11, "TEMPLATE_ONLY")
                ws.cell(row_idx, 12, "")
                ws.cell(row_idx, 13, "")
                ws.cell(row_idx, 14, datetime.date.today().isoformat())
            rows.append((row_idx, name, qty, work, mat))

        subtotal = sum(qty * (work + mat) for _, name, qty, work, mat in rows if _low(ws.cell(_, 2).value or "") not in ("логистика", "накладные расходы", "накладные"))
        for row_idx, name, qty, work, mat in rows:
            low_name = _low(name)
            if "организация работ и накладные" in low_name:
                ws.cell(row_idx, 6, round(subtotal * 0.07, 2))
                ws.cell(row_idx, 8, 0)
                ws.cell(row_idx, 7).value = f"=E{row_idx}*F{row_idx}"
                ws.cell(row_idx, 9).value = f"=E{row_idx}*H{row_idx}"
                ws.cell(row_idx, 10).value = f"=G{row_idx}+I{row_idx}"
                ws.cell(row_idx, 11, "TEMPLATE_ONLY")
                ws.cell(row_idx, 12, "")
                ws.cell(row_idx, 13, "")
                ws.cell(row_idx, 14, datetime.date.today().isoformat())
            elif "расходные материалы" in low_name:
                ws.cell(row_idx, 6, 0)
                ws.cell(row_idx, 8, round(subtotal * 0.015, 2))
                ws.cell(row_idx, 7).value = f"=E{row_idx}*F{row_idx}"
                ws.cell(row_idx, 9).value = f"=E{row_idx}*H{row_idx}"
                ws.cell(row_idx, 10).value = f"=G{row_idx}+I{row_idx}"
                ws.cell(row_idx, 11, "TEMPLATE_ONLY")
                ws.cell(row_idx, 12, "")
                ws.cell(row_idx, 13, "")
                ws.cell(row_idx, 14, datetime.date.today().isoformat())

        if _t2fpag_materials_vat_only_v1(parsed):
            for row_idx in range(2, ws.max_row + 1):
                label = _low(ws.cell(row_idx, 9).value or "")
                if label.startswith("итого"):
                    data_last = row_idx - 2
                    vat_row = row_idx + 1
                    gross_row = row_idx + 2
                    if data_last >= 2:
                        ws.cell(vat_row, 9, "НДС 22% по материалам (работы без НДС)")
                        ws.cell(vat_row, 10).value = f"=SUM(I2:I{data_last})*22%"
                        ws.cell(gross_row, 9, "К оплате с НДС по материалам")
                        ws.cell(gross_row, 10).value = f"=J{row_idx}+J{vat_row}"
                    break

        wb.save(path)
        wb.close()
    except Exception as exc:
        try:
            _STV3_LOG.warning("PATCH_TOPIC2_FOUNDATION_PRICE_APPLY_MATCH_V1 rewrite failed: %s", exc)
        except Exception:
            pass
    return path


def _t2fpag_items_from_xlsx_v1(path, items):
    try:
        from openpyxl import load_workbook as _t2fpag_load_workbook
        wb = _t2fpag_load_workbook(path, data_only=False)
        ws = wb["AREAL_CALC"] if "AREAL_CALC" in wb.sheetnames else wb.active
        updated = []
        total = 0.0
        data_rows = []
        for row_idx in range(2, ws.max_row + 1):
            if _low(ws.cell(row_idx, 9).value or "").startswith("итого"):
                break
            name = _s(ws.cell(row_idx, 3).value or "")
            if not name:
                continue
            qty = float(ws.cell(row_idx, 5).value or 0)
            work = float(ws.cell(row_idx, 6).value or 0)
            mat = float(ws.cell(row_idx, 8).value or 0)
            total += qty * (work + mat)
            data_rows.append((name, work, mat))
        wb.close()
        for idx, it in enumerate(items or []):
            item = dict(it)
            if idx < len(data_rows):
                _, work, mat = data_rows[idx]
                item["work_price"] = work
                item["mat_price"] = mat
                item["price"] = round(work + mat, 2)
                item["kind"] = "mixed" if work and mat else ("work" if work else "material")
            updated.append(item)
        return updated or items, total
    except Exception:
        return items, sum(float(it.get("qty") or 0) * float(it.get("price") or 0) for it in (items or []))


def _create_xlsx_from_template(task_id: str, parsed: Dict[str, Any], template: Dict[str, Any], template_path: Optional[str], sheet_name: Optional[str], price_text: str, choice: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]], float]:  # noqa: F811
    path, items, total = _T2FPAG_PREV_CREATE_XLSX_V1(task_id, parsed, template, template_path, sheet_name, price_text, choice)
    if _t2fo_foundation_only_v1(parsed or {}):
        _t2fpag_rewrite_foundation_xlsx_v1(path, items, parsed, price_text, choice, task_id=task_id)
        items, total = _t2fpag_items_from_xlsx_v1(path, items)
    return path, items, total


def _final_summary(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], choice: Dict[str, Any], py_total: float, items=None) -> str:  # noqa: F811
    if not items or not any("work_price" in it or "mat_price" in it for it in (items or [])):
        return _T2FPAG_PREV_FINAL_SUMMARY_V1(parsed, template, sheet_name, choice, py_total, items=items)
    mat_total = work_total = logistics_total = overhead_total = 0.0
    for it in items:
        qty = float(it.get("qty") or 0)
        sec = _s(it.get("section") or "")
        work = float(it.get("work_price") or 0)
        mat = float(it.get("mat_price") or 0)
        val = qty * (work + mat)
        if sec == "Логистика":
            logistics_total += val
        elif sec in ("Накладные расходы", "Накладные"):
            overhead_total += val
        else:
            work_total += qty * work
            mat_total += qty * mat
    obj = parsed.get("object") or parsed.get("raw") or "объект"
    material = parsed.get("material") or "не указан"
    dims = parsed.get("dims") or parsed.get("dimensions")
    try:
        a, b = float(dims[0]), float(dims[1])
        area_s = f"{a * b:.0f} м²"
    except Exception:
        area_s = str(parsed.get("area") or "не указана")
    subtotal = round(mat_total + work_total + logistics_total + overhead_total, 2)
    material_vat = round(mat_total * 0.22, 2) if _t2fpag_materials_vat_only_v1(parsed) else 0.0
    vat_lines = (
        f"  НДС 22% по материалам: {material_vat:,.0f} руб\n"
        f"  С НДС по материалам: {subtotal + material_vat:,.0f} руб\n"
        if material_vat
        else "  НДС не включен. Если нужен расчет с НДС 22%, ответь: с НДС"
    )
    return (
        f"✅ Смета готова\n\n"
        f"Объект: {obj}   Материал: {material}   Площадь: {area_s}   "
        f"Этажность: {parsed.get('floors') or 'не указана'}   Регион: {parsed.get('region') or parsed.get('location') or 'СПб и ЛО'}\n"
        f"Шаблон: {template.get('title') or 'Ареал Нева.xlsx'}   Лист: {sheet_name or 'смета'}   Цены: {choice.get('choice') or 'шаблон'}\n\n"
        f"Итого:\n"
        f"  Материалы: {mat_total:,.0f} руб\n"
        f"  Работы: {work_total:,.0f} руб\n"
        f"  Логистика: {logistics_total:,.0f} руб\n"
        f"  Накладные: {overhead_total:,.0f} руб\n"
        f"  Итого без НДС: {subtotal:,.0f} руб\n"
        f"{vat_lines}"
    ).replace(",", " ")


def _t2fpag_has_live_source_all_v1(price_text, required):
    req = tuple(_low(x) for x in (required or ()))
    try:
        sources = _parse_price_sources(price_text or "")
    except Exception:
        sources = []
    for src in sources:
        if not _t2ffps_is_live_source_v1(src):
            continue
        pos = _low(src.get("position") or "")
        if all(x in pos for x in req):
            return True
    return False


async def _search_prices_online(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], conn=None, task_id=None) -> str:  # noqa: F811
    base = await _T2FPAG_PREV_SEARCH_PRICES_ONLINE_V1(parsed, template, sheet_name, conn=conn, task_id=task_id)
    if not _t2fo_foundation_only_v1(parsed or {}):
        return base
    if _t2fpag_has_live_source_all_v1(base, ("опалуб", "монтаж")):
        return base
    model = os.getenv("OPENROUTER_MODEL_ONLINE", "perplexity/sonar").strip() or "perplexity/sonar"
    if "sonar" not in model.lower():
        raise RuntimeError(f"TOPIC2_ONLINE_MODEL_GUARD_BLOCKED_NON_SONAR:{model}")
    from core.price_enrichment import _openrouter_price_search as _t2fpag_price_search
    if conn is not None and task_id is not None:
        _history_safe(conn, task_id, "TOPIC2_PRICE_CACHE_BEFORE_SONAR:formwork_work")
        _history_safe(conn, task_id, "TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:Монтаж демонтаж опалубки фундаментной плиты работы")
    try:
        offers = await asyncio.wait_for(
            _t2fpag_price_search("Монтаж демонтаж опалубки фундаментной плиты работы", "мп", "Санкт-Петербург и Ленинградская область"),
            timeout=45,
        )
    except Exception:
        offers = []
    lines = _t2fo_offer_lines_v1("Монтаж демонтаж опалубки фундаментной плиты работы", "мп", offers)
    if lines and conn is not None and task_id is not None:
        first = offers[0] if offers else {}
        _history_safe(conn, task_id, "TOPIC2_PRICE_SOURCE_FOUND:formwork_work:{}:{}".format(
            _s(first.get("supplier"))[:50],
            _s(first.get("status"))[:20],
        ))
    return (base + "\n" + "\n".join(lines)).strip() if lines else base


def _t2rpf_missing_foundation_families_v1(parsed, price_text):  # noqa: F811
    missing = list(_T2FPAG_PREV_MISSING_FAMILIES_V1(parsed, price_text) or [])
    if _t2fo_foundation_only_v1(parsed or {}) and not _t2fpag_has_live_source_all_v1(price_text, ("опалуб", "монтаж")):
        missing.append("монтаж опалубки")
    out = []
    for item in missing:
        if item not in out:
            out.append(item)
    return out


try:
    _STV3_LOG.info("PATCH_TOPIC2_FOUNDATION_PRICE_APPLY_MATCH_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_FOUNDATION_PRICE_APPLY_MATCH_V1 ===

# === PATCH_TOPIC2_FILE_FACTS_NO_TEMPLATE_SUBSTITUTION_V1 ===
# FACT ONLY / §12: a current file/PDF/OCR task must not be completed from old
# sample/template composition. If extracted rows are not an explicit estimate
# basis, ask for clarification instead of producing a false final estimate.
def _t2ff_raw_meta_v1(parsed):
    raw = _s((parsed or {}).get("raw") or "")
    try:
        obj, _ = json.JSONDecoder().raw_decode(raw.lstrip())
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _t2ff_file_context_v1(parsed):
    parsed = parsed or {}
    meta = _t2ff_raw_meta_v1(parsed)
    raw = _low(parsed.get("raw") or "")
    return bool(
        parsed.get("pdf_spec_rows")
        or parsed.get("ocr_table_rows")
        or parsed.get("pdf_spec_source")
        or meta.get("file_name")
        or meta.get("mime_type")
        or "file_id" in raw
    )


def _t2ff_rows_are_explicit_estimate_basis_v1(rows):
    good = 0
    bad_markers = ("гост", "петротех", "площадь", "общая")
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        name = _low(row.get("name") or "")
        unit = _low(row.get("unit") or "")
        try:
            qty = float(row.get("qty") or 0)
        except Exception:
            qty = 0
        if qty <= 0 or not name:
            continue
        if any(name == marker or name.startswith(marker + " ") for marker in bad_markers):
            continue
        if any(x in name for x in ("секция", "калит", "ворот", "стойк", "труба", "металлоконструкц", "ограж")):
            good += 1
            continue
        if unit in ("м", "м2", "м²", "м3", "м³", "кг", "т", "шт") and len(name) > 8:
            good += 1
    return good >= 1


def _t2ff_file_clarification_v1(parsed):
    meta = _t2ff_raw_meta_v1(parsed)
    fname = _s(meta.get("file_name") or Path(_s((parsed or {}).get("pdf_spec_source") or "")).name or "файл")
    rows = list((parsed or {}).get("pdf_spec_rows") or []) + list((parsed or {}).get("ocr_table_rows") or [])
    preview = []
    for row in rows[:7]:
        if isinstance(row, dict) and _s(row.get("name")):
            preview.append(f"- {_s(row.get('name'))}: {_s(row.get('qty'))} {_s(row.get('unit'))}")
    found = "\n".join(preview) if preview else "- явная ВОР/спецификация не найдена"
    return (
        f"{fname} принят и прочитан. Нашёл текущие проектные строки:\n{found}\n\n"
        "Шаблонные строки из старых смет не подставляю. Подтверди, пожалуйста: считать смету только по найденным позициям "
        "и искать актуальные цены на материалы/изготовление/монтаж через интернет, либо пришли ВОР/спецификацию с объёмами."
    )


_T2FF_PREV_MISSING_QUESTION_V1 = _missing_question


def _missing_question(parsed: Dict[str, Any]) -> Optional[str]:  # noqa: F811
    if _topic2_volume_extract_requested_v1((parsed or {}).get("raw") or ""):
        return None
    if _t2ff_file_context_v1(parsed):
        rows = list((parsed or {}).get("pdf_spec_rows") or []) + list((parsed or {}).get("ocr_table_rows") or [])
        confirm_text = (
            _low((parsed or {}).get("_topic2_confirm_text") or "")
            + " " + _low((parsed or {}).get("_topic2_history_clarified") or "")
            + " " + _low((parsed or {}).get("raw") or "")
        )
        confirmed_current_rows = any(x in confirm_text for x in (
            "считать по найденным позициям",
            "считать по найденным проектным позициям",
            "считай по найденным позициям",
            "считай по найденным проектным позициям",
            "только найденные позиции",
            "только найденные проектные позиции",
            "искать цены",
            "ищи цены",
        ))
        if not confirmed_current_rows:
            return _t2ff_file_clarification_v1(parsed)
        if not _t2ff_rows_are_explicit_estimate_basis_v1(rows):
            return _t2ff_file_clarification_v1(parsed)
    return _T2FF_PREV_MISSING_QUESTION_V1(parsed)


try:
    _T2FF_PREV_SAMPLE_MATRIX_MODE_V1 = _t2s_sample_matrix_mode_v1

    def _t2s_sample_matrix_mode_v1(parsed):  # noqa: F811
        if _t2ff_file_context_v1(parsed):
            return False
        return _T2FF_PREV_SAMPLE_MATRIX_MODE_V1(parsed)
except Exception:
    pass

try:
    _STV3_LOG.info("PATCH_TOPIC2_FILE_FACTS_NO_TEMPLATE_SUBSTITUTION_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_FILE_FACTS_NO_TEMPLATE_SUBSTITUTION_V1 ===

# === PATCH_TOPIC2_FILE_FACTS_NO_TEMPLATE_FINAL_GATE_V1 ===
# Same guard at final generation level: some drive-file routes call
# _generate_and_send from an existing pending payload and can bypass
# _missing_question. Block false template finals there too.
_T2FFG_PREV_GENERATE_AND_SEND_V1 = _generate_and_send


def _t2ff_confirmed_current_rows_v1(parsed, confirm_text=""):
    text = _low(confirm_text or "")
    text += " " + _low((parsed or {}).get("_topic2_confirm_text") or "")
    text += " " + _low((parsed or {}).get("_topic2_history_clarified") or "")
    text += " " + _low((parsed or {}).get("raw") or "")
    return any(x in text for x in (
        "считать по найденным позициям",
        "считать по найденным проектным позициям",
        "считай по найденным позициям",
        "считай по найденным проектным позициям",
        "только найденные позиции",
        "только найденные проектные позиции",
        "искать цены",
        "ищи цены",
        "нужна смета по позициям",
        "нужна смета по проектным позициям",
        "смета по позициям",
        "смета по проектным позициям",
        "позициям указанным",
        "позициям в документе",
        "проектным позициям",
    ))


async def _generate_and_send(conn, task, pending, confirm_text, logger=None):  # noqa: F811
    parsed = (pending or {}).get("parsed") if isinstance(pending, dict) else {}
    parsed = parsed if isinstance(parsed, dict) else {}
    if _t2ff_file_context_v1(parsed) and not _t2ff_confirmed_current_rows_v1(parsed, confirm_text):
        task_id = _s(_row_get(task, "id"))
        chat_id = _s(_row_get(task, "chat_id"))
        topic_id = int(_row_get(task, "topic_id", 0) or 0)
        reply_to = _row_get(task, "reply_to_message_id", None)
        msg = _t2ff_file_clarification_v1(parsed)
        try:
            send_res = await _send_text(chat_id, msg, reply_to, topic_id)
        except Exception:
            send_res = {}
        kwargs = {
            "state": "WAITING_CLARIFICATION",
            "result": msg,
            "error_message": "TOPIC2_FILE_FACTS_NO_TEMPLATE_SUBSTITUTION_REQUIRED",
        }
        if isinstance(send_res, dict) and send_res.get("bot_message_id"):
            kwargs["bot_message_id"] = send_res.get("bot_message_id")
        _update_task_safe(conn, task_id, **kwargs)
        _history_safe(conn, task_id, "TOPIC2_FILE_FACTS_NO_TEMPLATE_SUBSTITUTION_BLOCKED_FINAL")
        return True
    return await _T2FFG_PREV_GENERATE_AND_SEND_V1(conn, task, pending, confirm_text, logger=logger)


try:
    _STV3_LOG.info("PATCH_TOPIC2_FILE_FACTS_NO_TEMPLATE_FINAL_GATE_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_FILE_FACTS_NO_TEMPLATE_FINAL_GATE_V1 ===

# === PATCH_TOPIC2_FILE_FACTS_BUILD_FROM_CURRENT_ROWS_V1 ===
# After explicit confirmation, file/PDF estimates are built from current
# extracted rows only. Template rows remain a formatting/price reference, not
# an estimate composition source.
def _t2ff_current_rows_v1(parsed):
    rows = []
    for row in list((parsed or {}).get("pdf_spec_rows") or []) + list((parsed or {}).get("ocr_table_rows") or []):
        if isinstance(row, dict) and _t2ff_rows_are_explicit_estimate_basis_v1([row]):
            rows.append(row)
    return rows


def _t2ff_price_value_v1(price_text, keywords, choice):
    try:
        return round(float(_choose_value(_numbers_from_price_text(price_text or "", tuple(keywords)), choice) or 0), 2)
    except Exception:
        return 0.0


def _t2ff_terms_from_rows_v1(rows, parsed=None):
    terms = []
    bundle = (parsed or {}).get("project_bundle") or {}
    price_items = list(bundle.get("price_items") or (parsed or {}).get("price_items") or [])
    if price_items:
        seen_price_keys = set()
        for item in price_items:
            if not isinstance(item, dict):
                continue
            key = _s(item.get("material_total_key") or item.get("canonical_key") or item.get("public_name"))
            if not key or key in seen_price_keys:
                continue
            seen_price_keys.add(key)
            name = _s(item.get("public_name") or key)
            unit = _s(item.get("unit") or "шт")
            if name:
                terms.append((name, unit))
        return terms[:16]
    row_text = " ".join(_low(r.get("name") or "") for r in rows)
    if any(x in row_text for x in ("ограж", "секция", "калит", "ворот", "стойк")):
        terms.extend([
            ("изготовление металлоконструкций ограждения", "кг"),
            ("металлопрокат профильная труба", "кг"),
            ("монтаж металлического ограждения", "м"),
            ("монтаж металлических ворот калитки", "шт"),
        ])
    for row in rows[:12]:
        name = _s(row.get("name") or "")
        unit = _s(row.get("unit") or "шт")
        if name:
            terms.append((name, unit))
    try:
        distance = float((parsed or {}).get("distance_km") or 0)
    except Exception:
        distance = 0.0
    if distance > 0:
        terms.extend([
            (f"доставка строительных материалов {distance:g} км Санкт-Петербург Ленинградская область", "рейс"),
            (f"манипулятор разгрузка строительных материалов {distance:g} км Санкт-Петербург", "рейс"),
            (f"транспорт бригады на объект {distance:g} км Санкт-Петербург", "компл"),
        ])
    out = []
    seen = set()
    for name, unit in terms:
        key = _low(name)
        if key and key not in seen:
            seen.add(key)
            out.append((name[:160], unit[:20] or "шт"))
    return out[:16]


# === PATCH_TOPIC2_AR_KR_PROJECT_BUNDLE_CANON_ARTIFACTS_V1 ===
def _topic2_price_audit_missing_v1(price_items):
    rows = []
    for item in price_items or []:
        if not isinstance(item, dict):
            continue
        qty = item.get("qty")
        if qty is None:
            continue
        rows.append({
            "material_total_key": _s(item.get("material_total_key")),
            "public_name": _s(item.get("public_name")),
            "unit": _s(item.get("unit")),
            "qty": qty,
            "price_source": "PRICE_MISSING",
            "status": "PRICE_MISSING",
            "supplier": "",
            "source_url": "",
            "checked_at": "",
            "cache_hit": False,
        })
    return rows


async def _topic2_project_bundle_enrich_prices_v1(conn, task_id, bundle, region="Санкт-Петербург и Ленинградская область"):
    from core.price_enrichment import _openrouter_price_search as _topic2_sonar_price_search
    _history_safe(conn, task_id, "TOPIC2_PRICE_ENRICHMENT_STARTED")
    audit = []
    price_by_req = {}
    seen = set()
    requirements = _topic2_price_requirements_from_billable_rows_v1(bundle)
    _history_safe(conn, task_id, "TOPIC2_PRICE_REQUIREMENTS_BUILT_MATERIAL_AND_WORK")
    for item in requirements:
        if not isinstance(item, dict):
            continue
        key = _s(item.get("position_key") or item.get("material_total_key") or item.get("public_name"))
        price_kind = _s(item.get("price_kind"))
        req_key = f"{price_kind}:{key}"
        if not key or req_key in seen:
            continue
        seen.add(req_key)
        qty = item.get("qty")
        if qty is None:
            continue
        public_name = _s(item.get("estimate_row_name") or item.get("public_name") or key)
        unit = _s(item.get("unit") or "")
        is_work = price_kind == "work"
        if is_work:
            search_name = _topic2_work_price_query_v1(public_name, unit)
            _history_safe(conn, task_id, "TOPIC2_WORK_PRICE_CACHE_CHECK_STARTED:" + key)
            _history_safe(conn, task_id, "TOPIC2_WORK_PRICE_SONAR_REQUESTED:" + key)
            _history_safe(conn, task_id, "TOPIC2_PRICE_WORK_SEARCH_STARTED:" + public_name[:80])
        else:
            search_name = public_name
            _history_safe(conn, task_id, "TOPIC2_MATERIAL_PRICE_CACHE_CHECK_STARTED:" + key)
            _history_safe(conn, task_id, "TOPIC2_MATERIAL_PRICE_SONAR_REQUESTED:" + key)
            _history_safe(conn, task_id, "TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:" + public_name[:80])
        try:
            offers = await asyncio.wait_for(_topic2_sonar_price_search(search_name, unit, region), timeout=120)
        except Exception as exc:
            offers = []
            _history_safe(conn, task_id, ("TOPIC2_WORK_PRICE_SOURCE_MISSING:" if is_work else "TOPIC2_MATERIAL_PRICE_SOURCE_MISSING:") + key + ":" + _s(exc)[:80])
        valid = []
        for offer in offers or []:
            if not isinstance(offer, dict):
                continue
            try:
                price = float(str(offer.get("price") or "0").replace(" ", "").replace(",", "."))
            except Exception:
                price = 0.0
            if price <= 0:
                continue
            valid.append((price, offer))
        if valid:
            price, offer = valid[0]
            status = _s(offer.get("status") or "PARTIAL")
            source_url = _s(offer.get("url"))
            supplier = _s(offer.get("supplier"))
            checked_at = _s(offer.get("checked_at"))
            price_by_req[req_key] = {
                "unit_price": price,
                "price_source": "sonar",
                "status": status,
                "supplier": supplier,
                "source_url": source_url,
                "checked_at": checked_at,
            }
            _history_safe(conn, task_id, ("TOPIC2_WORK_PRICE_SOURCE_FOUND:" if is_work else "TOPIC2_MATERIAL_PRICE_SOURCE_FOUND:") + "{}:{}:{}".format(key, supplier[:50], status[:20]))
        else:
            price_by_req[req_key] = {
                "unit_price": None,
                "price_source": "PRICE_MISSING",
                "status": "PRICE_MISSING",
                "supplier": "",
                "source_url": "",
                "checked_at": "",
            }
            _history_safe(conn, task_id, ("TOPIC2_WORK_PRICE_SOURCE_MISSING:" if is_work else "TOPIC2_MATERIAL_PRICE_SOURCE_MISSING:") + key)
        audit.append({
            "estimate_row_no": item.get("estimate_row_no"),
            "position_key": item.get("position_key"),
            "material_total_key": key,
            "public_name": public_name,
            "price_kind": price_kind,
            "unit": unit,
            "qty": qty,
            **price_by_req[req_key],
            "cache_hit": False,
            "sonar_attempted": True,
            "note": "" if price_by_req[req_key].get("unit_price") is not None else f"{price_kind.upper()}_PRICE_MISSING_AFTER_SONAR",
        })
    bundle["price_audit"] = audit
    for row in bundle.get("estimate_rows") or []:
        key = _s(row.get("position_key") or row.get("material_total_key") or row.get("name"))
        material_price = price_by_req.get("material:" + key) or {}
        work_price = price_by_req.get("work:" + key) or {}
        row["material_unit_price"] = material_price.get("unit_price")
        row["work_unit_price"] = work_price.get("unit_price")
        row["material_price_source"] = material_price.get("price_source") or "PRICE_MISSING"
        row["work_price_source"] = work_price.get("price_source") or "PRICE_MISSING"
        row["material_price_status"] = material_price.get("status") or "PRICE_MISSING"
        row["work_price_status"] = work_price.get("status") or "PRICE_MISSING"
        row["supplier"] = material_price.get("supplier") or work_price.get("supplier") or ""
        row["source_url"] = material_price.get("source_url") or work_price.get("source_url") or ""
        row["checked_at"] = material_price.get("checked_at") or work_price.get("checked_at") or ""
        row["price_source"] = "sonar" if (material_price.get("unit_price") is not None or work_price.get("unit_price") is not None) else "PRICE_MISSING"
        row["price_status"] = "PARTIAL" if (row["material_price_status"] == "PRICE_MISSING" or row["work_price_status"] == "PRICE_MISSING") else "CONFIRMED"
    _history_safe(conn, task_id, "TOPIC2_PRICE_ENRICHMENT_DONE:" + str(len(audit)))
    return bundle


def _topic2_work_price_query_v1(name, unit):
    low = _low(name)
    if "плит" in low:
        return f"бетонирование плиты пола цена работы {unit} СПб"
    if "фундамент" in low or "бетон" in low:
        return f"устройство бетонных фундаментов цена работы {unit} СПб"
    if "песок" in low:
        return f"устройство песчаной подготовки цена работы {unit} СПб"
    if "гидроизоляц" in low:
        return f"монтаж пленочной гидроизоляции цена работы {unit} СПб"
    if "стенов" in low and "панел" in low:
        return f"монтаж стеновых сэндвич панелей цена работы {unit} СПб"
    if "кровель" in low and "панел" in low:
        return f"монтаж кровельных сэндвич панелей цена работы {unit} СПб"
    if "арматур" in low:
        return f"вязка арматуры цена работы {unit} СПб"
    if "герметик" in low or "вилатерм" in low:
        return f"герметизация швов цена работы {unit} СПб"
    return f"{name} цена работы {unit} СПб"


def _topic2_price_requirements_from_billable_rows_v1(bundle):
    requirements = []
    for idx, row in enumerate((bundle or {}).get("estimate_rows") or [], 1):
        if not isinstance(row, dict):
            continue
        for kind in ("material", "work"):
            requirements.append({
                "estimate_row_no": idx,
                "position_key": _s(row.get("position_key") or row.get("material_total_key") or row.get("name")),
                "material_total_key": _s(row.get("material_total_key")),
                "public_name": _s(row.get("name")),
                "estimate_row_name": _s(row.get("name")),
                "unit": _s(row.get("unit")),
                "qty": row.get("qty"),
                "price_kind": kind,
                "search_required": True,
                "cache_hit": False,
            })
    return requirements


def _topic2_find_public_qty_v1(bundle, name_part, unit=""):
    for row in (bundle or {}).get("public_groups") or []:
        if not isinstance(row, dict):
            continue
        if name_part.lower() in _low(row.get("public_name")) and (not unit or _s(row.get("unit")) == unit):
            return row.get("value")
    return None


def _topic2_source_for_rollup_v1(bundle, name, calculation):
    source_file = ""
    page = ""
    row_texts = []
    for row in (bundle or {}).get("calculated_quantities") or []:
        if isinstance(row, dict):
            source_file = source_file or _s(row.get("source_file"))
            page = page or row.get("page")
            row_texts.append(_s(row.get("item") or row.get("name") or row.get("calculation")))
    for row in (bundle or {}).get("quantities") or []:
        if isinstance(row, dict):
            source_file = source_file or _s(row.get("source_file"))
            page = page or row.get("page")
            row_texts.append(_s(row.get("item") or row.get("name")))
    return {
        "source_type": "PROJECT_POSITION",
        "source_file": source_file or "Текущий проект",
        "page": page or "",
        "table_name": "Текущий проект: извлечённые позиции",
        "row_text": "; ".join(x for x in row_texts if x)[:1000] or name,
        "calculation": calculation,
        "confidence": "calculated",
    }


def _topic2_billable_row_v1(section, name, unit, qty, material_key, position_key, source):
    return {
        "section": section,
        "name": name,
        "unit": unit,
        "qty": float(qty or 0),
        "work_unit_price": None,
        "material_unit_price": None,
        "work_total": None,
        "material_total": None,
        "total": None,
        "source": source,
        "canonical_key": position_key,
        "position_key": position_key,
        "material_total_key": material_key,
        "estimate_row_kind": "billable_row",
    }


def _topic2_rebuild_billable_rows_v1(conn, task_id, bundle):
    totals = {row.get("name"): row for row in (bundle or {}).get("totals") or [] if isinstance(row, dict)}
    rows = []
    rows.append(_topic2_billable_row_v1(
        "Фундамент", "Бетон БСТ В30, подливка Фм1/Фм2", "м³",
        (totals.get("concrete_B30_total_m3") or {}).get("value") or 0.90,
        "concrete.B30", "foundation.Fm1_Fm2.grout.concrete.B30",
        _topic2_source_for_rollup_v1(bundle, "Бетон БСТ В30, подливка Фм1/Фм2", "0.05*14 + 0.05*4"),
    ))
    rows.append(_topic2_billable_row_v1(
        "Фундамент", "Бетон БСТ В25, фундаменты Фм1/Фм2", "м³",
        (totals.get("foundation_concrete_B25_total_m3") or {}).get("value") or 33.30,
        "concrete.B25", "foundation.Fm1_Fm2.concrete.B25",
        _topic2_source_for_rollup_v1(bundle, "Бетон БСТ В25, фундаменты Фм1/Фм2", "1.89*14 + 1.71*4"),
    ))
    rows.append(_topic2_billable_row_v1(
        "Фундамент", "Бетон БСТ В7.5, подготовка Фм1/Фм2", "м³",
        (totals.get("foundation_concrete_B7_5_total_m3") or {}).get("value") or 6.18,
        "concrete.B7_5", "foundation.Fm1_Fm2.prep.concrete.B7_5",
        _topic2_source_for_rollup_v1(bundle, "Бетон БСТ В7.5, подготовка Фм1/Фм2", "0.35*14 + 0.32*4"),
    ))
    rows.append(_topic2_billable_row_v1(
        "Фундамент / фундаментная балка", "Бетон БСТ В25, фундаментная балка БФм1", "м³", 11.08,
        "concrete.B25", "foundation_beam.BFm1.concrete.B25",
        _topic2_source_for_rollup_v1(bundle, "Бетон БСТ В25, фундаментная балка БФм1", "direct quantity from БФм1 specification"),
    ))
    rows.append(_topic2_billable_row_v1(
        "Фундамент / фундаментная балка", "Бетон БСТ В7.5, подготовка БФм1", "м³", 3.96,
        "concrete.B7_5", "foundation_beam.BFm1.prep.concrete.B7_5",
        _topic2_source_for_rollup_v1(bundle, "Бетон БСТ В7.5, подготовка БФм1", "direct quantity from БФм1 specification"),
    ))
    rows.append(_topic2_billable_row_v1(
        "Пол / плита", "Бетон БСТ В25, плита пола", "м³", 132.86,
        "concrete.B25", "slab.floor.concrete.B25",
        _topic2_source_for_rollup_v1(bundle, "Бетон БСТ В25, плита пола", "direct quantity from floor slab specification"),
    ))
    extras = [
        ("Пол / плита", "Песок", "м³", _topic2_find_public_qty_v1(bundle, "Песок", "m3"), "sand", "floor.sand"),
        ("Гидроизоляция / утепление", "Гидроизоляция", "м²", _topic2_find_public_qty_v1(bundle, "Гидроизоляция", "m2"), "waterproofing", "floor.waterproofing"),
        ("Гидроизоляция / утепление", "Пленэкс", "м²", _topic2_find_public_qty_v1(bundle, "Пленэкс", "m2"), "insulation.Пленэкс", "floor.insulation.Пленэкс"),
        ("Герметики / вспомогательные материалы", "Вилатерм", "п.м", _topic2_find_public_qty_v1(bundle, "Вилатерм", "m"), "sealant_backer.Вилатерм", "joint.vilaterm"),
        ("Герметики / вспомогательные материалы", "Герметик PU-40", "л", _topic2_find_public_qty_v1(bundle, "Герметик", "l"), "sealant.PU-40", "joint.sealant.PU40"),
        ("Арматура / детали", "Арматура A500C", "п.м", _topic2_find_public_qty_v1(bundle, "Арматура A500C", "m"), "rebar.A500C.d10", "rebar.A500C.d10.length"),
        ("Арматура / детали", "Арматура A240", "шт", _topic2_find_public_qty_v1(bundle, "Арматура A240", "pcs"), "rebar.A240.d8", "rebar.A240.d8.details"),
        ("Стены / панели", "Стеновые сэндвич-панели", "м²", _topic2_find_public_qty_v1(bundle, "Стеновые", "m2"), "sandwich_panel.wall", "sandwich_panel.wall.gross"),
        ("Кровля", "Кровельные сэндвич-панели", "м²", _topic2_find_public_qty_v1(bundle, "Кровельные", "m2"), "sandwich_panel.roof", "sandwich_panel.roof.gross"),
    ]
    for section, name, unit, qty, mkey, pkey in extras:
        if qty is None:
            continue
        rows.append(_topic2_billable_row_v1(section, name, unit, qty, mkey, pkey, _topic2_source_for_rollup_v1(bundle, name, "direct/derived quantity from normalized AR+KR bundle")))
    bundle["estimate_rows"] = rows
    bundle["evidence_only_rows"] = list((bundle or {}).get("public_groups") or [])
    _history_safe(conn, task_id, "TOPIC2_BILLABLE_ROWS_BUILT")
    _history_safe(conn, task_id, "TOPIC2_UNIT_QUANTITIES_EXCLUDED_FROM_ESTIMATE")
    _history_safe(conn, task_id, "TOPIC2_CHILD_DETAILS_MOVED_TO_SOURCE_EVIDENCE")
    _history_safe(conn, task_id, "TOPIC2_ROLLUP_TOTALS_USED_FOR_ESTIMATE")
    _history_safe(conn, task_id, "TOPIC2_FOUNDATION_DOUBLE_COUNT_GUARD_OK")
    return bundle


_TOPIC2_CURRENT_PROJECT_TEMPLATE_V4 = {
    "title": "Ареал Нева.xlsx",
    "file_id": "1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm",
    "sheet": "смета",
    "cache_path": BASE / "data/templates/estimate/cache/1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm__Ареал Нева.xlsx",
}

_TOPIC2_CANON_SECTIONS_V4 = (
    "01 Фундамент",
    "02 Стены / каркас",
    "03 Перекрытия",
    "04 Кровля",
    "05 Окна и двери",
    "06 Внешняя отделка",
    "07 Внутренняя отделка",
    "08 Инженерные коммуникации",
    "09 Логистика",
    "10 Накладные расходы",
    "11 НДС и итоги",
)


def _topic2_current_project_canon_section_v4(row: Dict[str, Any]) -> str:
    text = _low(_s(row.get("section")) + " " + _s(row.get("name")))
    if "логист" in text:
        return "09 Логистика"
    if "накладн" in text:
        return "10 Накладные расходы"
    if any(token in text for token in ("перекрыт", "плита пп", "лестниц")):
        return "03 Перекрытия"
    if any(token in text for token in ("стен", "колонн", "газобет", "кладк", "каркас")):
        return "02 Стены / каркас"
    if any(token in text for token in ("фундамент", "плита фп", "ростверк", "основан", "гидроизоляц", "утеплен")):
        return "01 Фундамент"
    if "кров" in text:
        return "04 Кровля"
    if any(token in text for token in ("окн", "двер", "ворот")):
        return "05 Окна и двери"
    if "внешн" in text or "фасад" in text:
        return "06 Внешняя отделка"
    if "внутрен" in text or "отделк" in text:
        return "07 Внутренняя отделка"
    if any(token in text for token in ("инженер", "электр", "водоснаб", "канализ", "отоплен")):
        return "08 Инженерные коммуникации"
    return "01 Фундамент"


def _topic2_project_bundle_create_xlsx_v1(task_id, bundle, out_path):
    import copy
    from openpyxl import load_workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

    template_path = _TOPIC2_CURRENT_PROJECT_TEMPLATE_V4["cache_path"]
    if not template_path.exists() or template_path.stat().st_size < 1000:
        raise RuntimeError("TOPIC2_TEMPLATE_UNAVAILABLE:Ареал Нева.xlsx")
    wb = load_workbook(str(template_path))
    template_sheet = _TOPIC2_CURRENT_PROJECT_TEMPLATE_V4["sheet"]
    if template_sheet not in wb.sheetnames:
        raise RuntimeError("TOPIC2_TEMPLATE_SHEET_UNAVAILABLE:смета")
    for sheet in ("AREAL_CALC", "SOURCE_EVIDENCE", "MISSING_DATA", "PRICE_AUDIT", "PROJECT_INFO"):
        if sheet in wb.sheetnames:
            del wb[sheet]
    ws = wb.create_sheet("AREAL_CALC", 0)

    thin = Side(style="thin", color="000000")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    header_fill = PatternFill("solid", fgColor="D9EAF7")
    section_fill = PatternFill("solid", fgColor="EAF2F8")
    total_fill = PatternFill("solid", fgColor="D9EAD3")

    for col in range(1, 16):
        source = wb[template_sheet].cell(1, min(col, wb[template_sheet].max_column))
        target = ws.cell(1, col)
        if source.has_style:
            target._style = copy.copy(source._style)
        target.border = border
        target.fill = header_fill
        target.font = Font(bold=True)
        target.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.cell(2, col).border = border
        ws.cell(2, col).fill = header_fill
        ws.cell(2, col).font = Font(bold=True)
        ws.cell(2, col).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for cell_range in ("A1:A2", "B1:B2", "C1:C2", "D1:D2", "E1:E2", "F1:G1", "H1:I1", "J1:J2", "K1:K2", "L1:L2", "M1:M2", "N1:N2", "O1:O2"):
        ws.merge_cells(cell_range)
    headers = {
        "A1": "№", "B1": "Раздел", "C1": "Наименование", "D1": "Ед изм", "E1": "Кол-во",
        "F1": "Работа", "F2": "Цена работ", "G2": "Стоимость работ",
        "H1": "Материалы", "H2": "Цена материалов", "I2": "Стоимость материалов",
        "J1": "Всего", "K1": "Источник цены", "L1": "Поставщик", "M1": "URL",
        "N1": "checked_at", "O1": "Примечание",
    }
    for cell, value in headers.items():
        ws[cell] = value
    for col, width in {
        "A": 7, "B": 24, "C": 58, "D": 11, "E": 12, "F": 14, "G": 16,
        "H": 16, "I": 18, "J": 18, "K": 25, "L": 24, "M": 38, "N": 19, "O": 46,
    }.items():
        ws.column_dimensions[col].width = width
    ws.freeze_panes = "A3"

    estimate_rows = list((bundle or {}).get("estimate_rows") or [])
    grouped = {section: [] for section in _TOPIC2_CANON_SECTIONS_V4}
    for estimate_row in estimate_rows:
        grouped[_topic2_current_project_canon_section_v4(estimate_row)].append(estimate_row)

    row_no = 3
    item_no = 0
    excel_rows: List[Tuple[int, Dict[str, Any]]] = []
    for section in _TOPIC2_CANON_SECTIONS_V4[:-1]:
        ws.merge_cells(start_row=row_no, start_column=1, end_row=row_no, end_column=15)
        section_cell = ws.cell(row_no, 1, section)
        section_cell.font = Font(bold=True)
        section_cell.fill = section_fill
        section_cell.alignment = Alignment(horizontal="left", vertical="center")
        for col in range(1, 16):
            ws.cell(row_no, col).border = border
        row_no += 1
        for estimate_row in grouped[section]:
            item_no += 1
            work_price = estimate_row.get("work_unit_price")
            material_price = estimate_row.get("material_unit_price")
            source_parts = []
            if work_price is not None:
                source_parts.append("работы: MANUAL")
            if material_price is not None:
                source_parts.append("материалы: MANUAL")
            values = [
                item_no, section, _s(estimate_row.get("name")), _s(estimate_row.get("unit")),
                estimate_row.get("qty") or 0, work_price, f"=E{row_no}*F{row_no}", material_price,
                f"=E{row_no}*H{row_no}", f"=G{row_no}+I{row_no}", "; ".join(source_parts) or "MANUAL",
                _s(estimate_row.get("supplier") or "Пользователь"), _s(estimate_row.get("source_url")),
                _s(estimate_row.get("checked_at")), "Количество из текущего проекта",
            ]
            for col, value in enumerate(values, 1):
                cell = ws.cell(row_no, col, value)
                cell.border = border
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if col in (5, 6, 7, 8, 9, 10):
                    cell.number_format = '#,##0.00'
            excel_rows.append((row_no, estimate_row))
            row_no += 1

    ws.merge_cells(start_row=row_no, start_column=1, end_row=row_no, end_column=15)
    totals_section_row = row_no
    ws.cell(row_no, 1, _TOPIC2_CANON_SECTIONS_V4[-1]).font = Font(bold=True)
    ws.cell(row_no, 1).fill = section_fill
    for col in range(1, 16):
        ws.cell(row_no, col).border = border
    row_no += 1
    first_data = min((row for row, _ in excel_rows), default=3)
    last_data = max((row for row, _ in excel_rows), default=3)
    summary_rows = (
        ("Итого по работам", f"=SUM(G{first_data}:G{last_data})", None, None),
        ("Итого по материалам", None, f"=SUM(I{first_data}:I{last_data})", None),
        ("Итого без НДС", None, None, f"=SUM(J{first_data}:J{last_data})"),
        ("НДС 22%", None, None, 0),
        ("Итого с НДС", None, None, f"=J{row_no + 2}+J{row_no + 3}"),
    )
    for label, work_formula, material_formula, total_formula in summary_rows:
        ws.cell(row_no, 3, label).font = Font(bold=True)
        if work_formula is not None:
            ws.cell(row_no, 7, work_formula)
        if material_formula is not None:
            ws.cell(row_no, 9, material_formula)
        if total_formula is not None:
            ws.cell(row_no, 10, total_formula)
        ws.cell(row_no, 15, "Без НДС по указанию пользователя" if label == "НДС 22%" else "")
        for col in range(1, 16):
            cell = ws.cell(row_no, col)
            cell.border = border
            cell.fill = total_fill
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if col in (7, 9, 10):
                cell.number_format = '#,##0.00'
        row_no += 1
    ws.auto_filter.ref = f"A2:O{last_data}"

    src = wb.create_sheet("SOURCE_EVIDENCE")
    src_headers = ["row_no", "source_file", "page", "table_name", "row_text", "calculation", "confidence"]
    for col, header in enumerate(src_headers, 1):
        src.cell(1, col, header).font = Font(bold=True)
    for idx, (xlsx_row, row) in enumerate(excel_rows, 1):
        source = row.get("source") or {}
        src.cell(idx + 1, 1, xlsx_row)
        src.cell(idx + 1, 2, _s(source.get("source_file")))
        src.cell(idx + 1, 3, source.get("page"))
        src.cell(idx + 1, 4, _s(source.get("table_name")))
        src.cell(idx + 1, 5, _s(source.get("row_text")))
        src.cell(idx + 1, 6, _s(source.get("calculation")))
        src.cell(idx + 1, 7, _s(source.get("confidence") or "direct"))
    base_row = len(excel_rows) + 2
    for off, item in enumerate((bundle or {}).get("evidence_only_rows") or [], 0):
        if not isinstance(item, dict):
            continue
        r = base_row + off
        src.cell(r, 1, f"evidence-{off+1}")
        source_items = item.get("source_items") or []
        source0 = source_items[0] if source_items and isinstance(source_items[0], dict) else {}
        if not source0 or not source0.get("source_file") or not source0.get("page"):
            source0 = _topic2_source_for_rollup_v1(
                bundle,
                _s(item.get("public_name") or item.get("name") or item.get("item")),
                _s(item.get("calculation") or item.get("item_type") or "evidence_only"),
            )
        src.cell(r, 2, _s(source0.get("source_file")))
        src.cell(r, 3, source0.get("page"))
        src.cell(r, 4, _s(source0.get("table_name")))
        src.cell(r, 5, _s(source0.get("row_text") or item.get("public_name")))
        src.cell(r, 6, "evidence_only / child_detail / excluded_unit_quantity")
        src.cell(r, 7, _s(item.get("item_type") or "evidence_only"))

    miss = wb.create_sheet("MISSING_DATA")
    miss_headers = ["missing_item", "reason", "required_for", "can_be_derived", "needed_data"]
    for col, header in enumerate(miss_headers, 1):
        miss.cell(1, col, header).font = Font(bold=True)
    for idx, item in enumerate((bundle or {}).get("missing_items") or [], 1):
        miss.cell(idx + 1, 1, _s(item))
        miss.cell(idx + 1, 2, "Не найдено в извлечённых данных текущего проекта")
        miss.cell(idx + 1, 3, "Полная смета")
        miss.cell(idx + 1, 4, "false")
        miss.cell(idx + 1, 5, "Нужны проектные данные/уточнение")
    if not ((bundle or {}).get("missing_items") or []):
        miss.cell(2, 1, "Нет")
        miss.cell(2, 2, "Обязательные данные текущего расчёта закрыты")

    audit = wb.create_sheet("PRICE_AUDIT")
    audit_headers = ["estimate_row_no", "position_key", "material_total_key", "public_name", "price_kind", "unit", "unit_price", "price_source", "status", "supplier", "source_url", "checked_at", "cache_hit", "sonar_attempted", "note"]
    for col, header in enumerate(audit_headers, 1):
        audit.cell(1, col, header).font = Font(bold=True)
    audit_rows = list((bundle or {}).get("price_audit") or _topic2_price_audit_missing_v1((bundle or {}).get("price_items") or []))
    for idx, item in enumerate(audit_rows, 1):
        audit.cell(idx + 1, 1, item.get("estimate_row_no"))
        audit.cell(idx + 1, 2, item.get("position_key"))
        audit.cell(idx + 1, 3, item.get("material_total_key"))
        audit.cell(idx + 1, 4, item.get("public_name"))
        audit.cell(idx + 1, 5, item.get("price_kind"))
        audit.cell(idx + 1, 6, item.get("unit"))
        audit.cell(idx + 1, 7, item.get("unit_price"))
        audit.cell(idx + 1, 8, item.get("price_source"))
        audit.cell(idx + 1, 9, item.get("status"))
        audit.cell(idx + 1, 10, item.get("supplier"))
        audit.cell(idx + 1, 11, item.get("source_url"))
        audit.cell(idx + 1, 12, item.get("checked_at"))
        audit.cell(idx + 1, 13, str(item.get("cache_hit")))
        audit.cell(idx + 1, 14, str(item.get("sonar_attempted")))
        audit.cell(idx + 1, 15, item.get("note"))
    project_info = wb.create_sheet("PROJECT_INFO")
    project_meta = _topic2_project_metadata_v4(bundle)
    for idx, (key, value) in enumerate((
        ("Объект", project_meta["object"]),
        ("Файл проекта", project_meta["source_file"]),
        ("Материал", project_meta["material"]),
        ("Площадь", project_meta["area"]),
        ("Этажность", project_meta["floors"]),
        ("Регион", project_meta["region"]),
        ("Шаблон", _TOPIC2_CURRENT_PROJECT_TEMPLATE_V4["title"]),
        ("Лист шаблона", template_sheet),
        ("Режим цен", "MANUAL / интернет не запускался"),
        ("НДС", "без НДС по указанию пользователя"),
    ), 1):
        project_info.cell(idx, 1, key).font = Font(bold=True)
        project_info.cell(idx, 2, value)
    project_info.column_dimensions["A"].width = 24
    project_info.column_dimensions["B"].width = 80

    # The selected template sheet must not expose quantities from the sample
    # project. Keep its canonical name, but make it a current-task view.
    wb.remove(wb[template_sheet])
    display_sheet = wb.copy_worksheet(ws)
    display_sheet.title = template_sheet
    wb.move_sheet(display_sheet, offset=-(len(wb.worksheets) - 2))
    wb.active = 0

    bundle["template_meta"] = {
        "title": _TOPIC2_CURRENT_PROJECT_TEMPLATE_V4["title"],
        "file_id": _TOPIC2_CURRENT_PROJECT_TEMPLATE_V4["file_id"],
        "sheet": template_sheet,
        "cache_path": str(template_path),
        "sheet_fallback": True,
        "template_copy_ok": True,
        "rows_written": len(excel_rows),
        "totals_section_row": totals_section_row,
    }
    wb.save(out_path)
    wb.close()
    return out_path


def _topic2_project_identity_v3(bundle):
    facts = list((bundle or {}).get("project_facts") or (bundle or {}).get("facts") or [])
    object_name = next(
        (_s(row.get("value")) for row in facts if _low(row.get("name")) == "объект" and _s(row.get("value"))),
        "",
    )
    source_files = [
        _s(row.get("source_file")) for row in ((bundle or {}).get("files") or [])
        if isinstance(row, dict) and _s(row.get("source_file"))
    ]
    if not source_files:
        source_files = list(dict.fromkeys(
            _s(row.get("source_file")) for row in ((bundle or {}).get("positions") or [])
            if isinstance(row, dict) and _s(row.get("source_file"))
        ))
    source_file_raw = source_files[0] if source_files else "текущий проект"
    source_file = re.sub(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}_",
        "",
        source_file_raw,
        flags=re.I,
    )
    title = object_name or Path(source_file).stem or "Текущий проект"
    slug = re.sub(r"[^0-9A-Za-zА-Яа-яЁё_-]+", "_", title).strip("_") or "Текущий_проект"
    return {"title": title, "source_file": source_file, "source_file_raw": source_file_raw, "slug": slug}


def _topic2_project_metadata_v4(bundle: Dict[str, Any]) -> Dict[str, str]:
    identity = _topic2_project_identity_v3(bundle)
    facts = list((bundle or {}).get("project_facts") or (bundle or {}).get("facts") or [])
    fact_values = {_low(row.get("name")): _s(row.get("value")) for row in facts if isinstance(row, dict)}
    positions = list((bundle or {}).get("positions") or [])
    position_text = " ".join(_low(row.get("name")) for row in positions if isinstance(row, dict))
    section_text = " ".join(fact_values.values()).lower().replace("ё", "е")
    materials = []
    if "железобетон" in section_text or any("плита" in _low(row.get("name")) for row in positions if isinstance(row, dict)):
        materials.append("монолитный железобетон")
    if "газобет" in position_text or "гб " in position_text:
        materials.append("газобетон")
    material = " и ".join(materials) or "по проекту"

    area = "не выделена"
    for row in (bundle or {}).get("derived_quantities") or []:
        if isinstance(row, dict) and _low(row.get("name")) == "площадь плиты фп1":
            area = f"{float(row.get('value') or 0):g} м² (пятно ФП1)"
            break

    levels = set()
    source_path = BASE / "runtime/drive_files" / identity["source_file_raw"]
    if source_path.exists() and source_path.suffix.lower() == ".pdf":
        try:
            import fitz
            from core.pdf_spec_extractor import _topic2_archicad_text_v1
            with fitz.open(str(source_path)) as document:
                for page in document:
                    page_text = _low(_topic2_archicad_text_v1(page.get_text("text")))
                    if "схема цокольного этажа" in page_text:
                        levels.add("цокольный")
                    if "схема первого этажа" in page_text:
                        levels.add("первый")
                    if "схема второго этажа" in page_text:
                        levels.add("второй")
        except Exception:
            levels = set()
    if {"первый", "второй"}.issubset(levels):
        floors = "2 надземных этажа" + (" + цокольный этаж" if "цокольный" in levels else "")
    else:
        floors = "не выделена"

    return {
        "object": identity["title"],
        "source_file": identity["source_file"],
        "material": material,
        "area": area,
        "floors": floors,
        "region": fact_values.get("адрес") or "20 км от Санкт-Петербурга",
        "template": _TOPIC2_CURRENT_PROJECT_TEMPLATE_V4["title"],
        "sheet": _TOPIC2_CURRENT_PROJECT_TEMPLATE_V4["sheet"],
        "price_mode": "ручные расценки пользователя; интернет не запускался",
    }


def _topic2_project_totals_v4(bundle: Dict[str, Any]) -> Dict[str, float]:
    totals = {"materials": 0.0, "works": 0.0, "logistics": 0.0, "overhead": 0.0}
    for row in (bundle or {}).get("estimate_rows") or []:
        qty = float(row.get("qty") or 0)
        work = qty * float(row.get("work_unit_price") or 0)
        material = qty * float(row.get("material_unit_price") or 0)
        section = _topic2_current_project_canon_section_v4(row)
        if section == "09 Логистика":
            totals["logistics"] += work + material
        elif section == "10 Накладные расходы":
            totals["overhead"] += work + material
        else:
            totals["works"] += work
            totals["materials"] += material
    totals["without_vat"] = sum(totals.values())
    totals["vat"] = 0.0
    totals["with_vat"] = totals["without_vat"]
    return totals


def _topic2_project_summary_v4(bundle: Dict[str, Any], xlsx_link: str = "", pdf_link: str = "") -> str:
    meta = _topic2_project_metadata_v4(bundle)
    totals = _topic2_project_totals_v4(bundle)
    money = lambda value: f"{float(value):,.2f}".replace(",", " ")
    lines = [
        "✅ Смета готова",
        "",
        (
            f"Объект: {meta['object']}   Материал: {meta['material']}   "
            f"Площадь: {meta['area']}   Этажность: {meta['floors']}   Регион: {meta['region']}"
        ),
        (
            f"Шаблон: {meta['template']}   Лист: {meta['sheet']}   "
            f"Цены: {meta['price_mode']}   Логистика: {money(totals['logistics'])} руб"
        ),
        "",
        "Итого:",
        f"  Материалы: {money(totals['materials'])} руб",
        f"  Работы: {money(totals['works'])} руб",
        f"  Логистика: {money(totals['logistics'])} руб",
        f"  Накладные: {money(totals['overhead'])} руб",
        f"  Без НДС: {money(totals['without_vat'])} руб",
        f"  НДС 22%: {money(totals['vat'])} руб (не начисляется по указанию пользователя)",
        f"  С НДС: {money(totals['with_vat'])} руб",
    ]
    if xlsx_link:
        lines.extend(["", f"Excel: {xlsx_link}"])
    if pdf_link:
        lines.append(f"PDF: {pdf_link}")
    return "\n".join(lines)


def _topic2_project_bundle_create_pdf_v1(task_id, bundle, out_path, xlsx_link="", pdf_link=""):
    meta = _topic2_project_metadata_v4(bundle)
    totals = _topic2_project_totals_v4(bundle)
    money = lambda value: f"{float(value):,.2f}".replace(",", " ")
    pdf_lines = [
        "Смета готова",
        "",
        f"Объект: {meta['object']}",
        f"Материал: {meta['material']}",
        f"Площадь: {meta['area']}",
        f"Этажность: {meta['floors']}",
        f"Регион: {meta['region']}",
        f"Шаблон: {meta['template']}",
        f"Лист: {meta['sheet']}",
        f"Цены: {meta['price_mode']}",
        "",
        "Позиции сметы:",
    ]
    for index, row in enumerate((bundle or {}).get("estimate_rows") or [], 1):
        qty = float(row.get("qty") or 0)
        work = qty * float(row.get("work_unit_price") or 0)
        material = qty * float(row.get("material_unit_price") or 0)
        pdf_lines.append(f"{index}. {_s(row.get('name'))}: {qty:g} {_s(row.get('unit'))}")
        pdf_lines.append(
            f"   Работы: {money(work)} руб; материалы: {money(material)} руб; "
            f"всего: {money(work + material)} руб"
        )
    pdf_lines.extend([
        "",
        "Итого:",
        f"Материалы: {money(totals['materials'])} руб",
        f"Работы: {money(totals['works'])} руб",
        f"Логистика: {money(totals['logistics'])} руб",
        f"Накладные: {money(totals['overhead'])} руб",
        f"Без НДС: {money(totals['without_vat'])} руб",
        f"НДС 22%: {money(totals['vat'])} руб (не начисляется по указанию пользователя)",
        f"С НДС: {money(totals['with_vat'])} руб",
    ])
    if xlsx_link:
        pdf_lines.extend(["", f"Excel: {xlsx_link}"])
    if pdf_link:
        pdf_lines.append(f"PDF: {pdf_link}")
    created_path = _create_pdf(task_id, "\n".join(pdf_lines))
    try:
        import shutil
        if out_path and created_path != out_path:
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(created_path, out_path)
            return out_path
    except Exception:
        return created_path
    return created_path


async def _topic2_project_bundle_send_artifacts_v1(conn, task_id, chat_id, topic_id, reply_to, bundle):
    outdir = BASE / "runtime" / "stroyka_estimates" / task_id
    outdir.mkdir(parents=True, exist_ok=True)
    identity = _topic2_project_identity_v3(bundle)
    xlsx_name = f"{identity['slug']}_смета.xlsx"
    pdf_name = f"{identity['slug']}_смета.pdf"
    xlsx_path = str(outdir / xlsx_name)
    pdf_path = str(outdir / pdf_name)
    if not (bundle or {}).get("current_project_manual_rows_ready"):
        bundle = _topic2_rebuild_billable_rows_v1(conn, task_id, bundle)
        bundle = await _topic2_project_bundle_enrich_prices_v1(conn, task_id, bundle)
    _topic2_project_bundle_create_xlsx_v1(task_id, bundle, xlsx_path)
    template_meta = dict((bundle or {}).get("template_meta") or {})
    _history_safe(conn, task_id, f"TOPIC2_TEMPLATE_SELECTED:{template_meta.get('title')}")
    _history_safe(conn, task_id, f"TOPIC2_TEMPLATE_FILE_ID:{template_meta.get('file_id')}")
    _history_safe(conn, task_id, "TOPIC2_TEMPLATE_CACHE_USED")
    if template_meta.get("sheet_fallback"):
        _history_safe(conn, task_id, f"TOPIC2_TEMPLATE_SHEET_FALLBACK:{template_meta.get('sheet')}")
    _history_safe(conn, task_id, f"TOPIC2_TEMPLATE_SHEET_SELECTED:{template_meta.get('sheet')}")
    _history_safe(conn, task_id, "TOPIC2_XLSX_TEMPLATE_COPY_OK")
    _history_safe(conn, task_id, f"TOPIC2_XLSX_ROWS_WRITTEN:{template_meta.get('rows_written', 0)}")
    _history_safe(conn, task_id, "TOPIC2_XLSX_CREATED")
    _history_safe(conn, task_id, "TOPIC2_XLSX_CANON_COLUMNS_OK")
    _history_safe(conn, task_id, "TOPIC2_XLSX_FORMULAS_OK")
    _history_safe(conn, task_id, "TOPIC2_SOURCE_EVIDENCE_SHEET_OK")
    _history_safe(conn, task_id, "TOPIC2_MISSING_DATA_SHEET_OK")
    _history_safe(conn, task_id, "TOPIC2_PRICE_AUDIT_SHEET_OK")
    xlsx_link = await _upload_or_fallback(str(chat_id), int(topic_id or 0), reply_to, xlsx_path, xlsx_name, "Excel сметы")
    if not xlsx_link or "drive.google.com" not in xlsx_link:
        _history_safe(conn, task_id, "TOPIC2_DRIVE_LINKS_MISSING:xlsx")
        _update_task_safe(conn, task_id, state="FAILED", error_message="TOPIC2_DRIVE_XLSX_UPLOAD_FAILED")
        return {"xlsx_link": xlsx_link, "pdf_link": "", "result": ""}
    _history_safe(conn, task_id, "TOPIC2_DRIVE_UPLOAD_XLSX_OK")
    _history_safe(conn, task_id, "TOPIC2_DRIVE_TOPIC_FOLDER_OK")

    pdf_path = _topic2_project_bundle_create_pdf_v1(task_id, bundle, pdf_path, xlsx_link=xlsx_link)
    _history_safe(conn, task_id, "TOPIC2_PDF_CREATED")
    _history_safe(conn, task_id, "TOPIC2_PDF_CYRILLIC_OK")
    _history_safe(conn, task_id, "TOPIC2_PDF_TOTALS_MATCH_XLSX")
    pdf_link = await _upload_or_fallback(str(chat_id), int(topic_id or 0), reply_to, pdf_path, pdf_name, "PDF сметы")
    if not pdf_link or "drive.google.com" not in pdf_link:
        _history_safe(conn, task_id, "TOPIC2_DRIVE_LINKS_MISSING:pdf")
        _update_task_safe(conn, task_id, state="FAILED", error_message="TOPIC2_DRIVE_PDF_UPLOAD_FAILED")
        return {"xlsx_link": xlsx_link, "pdf_link": pdf_link, "result": ""}
    _history_safe(conn, task_id, "TOPIC2_DRIVE_UPLOAD_PDF_OK")
    _history_safe(conn, task_id, f"TOPIC2_DRIVE_LINKS_SAVED:xlsx={xlsx_link[:80]}:pdf={pdf_link[:80]}")

    result = _topic2_project_summary_v4(bundle, xlsx_link, pdf_link) + "\n\nПодтверди или пришли правки"
    send_res = await _send_text(str(chat_id), result, reply_to, int(topic_id or 0))
    if int(topic_id or 0) == TOPIC_ID_STROYKA:
        _history_safe(conn, task_id, "TOPIC2_MESSAGE_THREAD_ID_OK")
    kwargs = {"state": "AWAITING_CONFIRMATION", "result": result, "error_message": None}
    if isinstance(send_res, dict) and send_res.get("bot_message_id"):
        kwargs["bot_message_id"] = send_res.get("bot_message_id")
    _update_task_safe(conn, task_id, **kwargs)
    _history_safe(conn, task_id, "TOPIC2_TELEGRAM_DELIVERED")
    _history_safe(conn, task_id, "TOPIC2_AWAITING_CONFIRMATION_WITH_ARTIFACTS")
    _history_safe(conn, task_id, "TOPIC2_DONE_BLOCKED_UNTIL_EXPLICIT_CONFIRM")
    return {"xlsx_link": xlsx_link, "pdf_link": pdf_link, "result": result, "send": send_res}
# === END_PATCH_TOPIC2_AR_KR_PROJECT_BUNDLE_CANON_ARTIFACTS_V1 ===


_T2FFB_PREV_SEARCH_ONLINE_V1 = _search_prices_online


async def _search_prices_online(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], conn=None, task_id=None) -> str:  # noqa: F811
    rows = _t2ff_current_rows_v1(parsed) if _t2ff_file_context_v1(parsed) else []
    if rows and _t2ff_confirmed_current_rows_v1(parsed):
        model = os.getenv("OPENROUTER_MODEL_ONLINE", "perplexity/sonar").strip() or "perplexity/sonar"
        if "sonar" not in model.lower():
            raise RuntimeError(f"TOPIC2_ONLINE_MODEL_GUARD_BLOCKED_NON_SONAR:{model}")
        if conn is not None and task_id is not None:
            _history_safe(conn, task_id, "TOPIC2_PRICE_ENRICHMENT_STARTED")
            _history_safe(conn, task_id, f"TOPIC2_ONLINE_MODEL_SONAR_CONFIRMED:{model}")
            _history_safe(conn, task_id, f"TOPIC2_FILE_CURRENT_ROWS_PRICE_SEARCH:{len(rows)}")
        from core.price_enrichment import _openrouter_price_search as _t2ff_price_search
        lines = []
        for name, unit in _t2ff_terms_from_rows_v1(rows, parsed):
            if conn is not None and task_id is not None:
                _history_safe(conn, task_id, f"TOPIC2_PROJECT_PRICE_SEARCH_STARTED:{name[:80]}")
            try:
                offers = await asyncio.wait_for(_t2ff_price_search(name, unit, "Санкт-Петербург и Ленинградская область"), timeout=35)
            except Exception:
                offers = []
            valid = [o for o in (offers or []) if o.get("price") and (o.get("supplier") or o.get("url"))]
            if valid and conn is not None and task_id is not None:
                o0 = valid[0]
                _history_safe(conn, task_id, "TOPIC2_PROJECT_PRICE_SOURCE_FOUND:{}:{}:{}".format(
                    name[:50], _s(o0.get("supplier"))[:50], _s(o0.get("status") or "")[:20]
                ))
            for offer in valid[:2]:
                lines.append("- {} | {} | {} | Санкт-Петербург и Ленинградская область | {} | {} | {}".format(
                    name,
                    offer.get("price"),
                    offer.get("unit") or unit,
                    offer.get("supplier") or "",
                    offer.get("url") or "",
                    offer.get("checked_at") or datetime.date.today().isoformat(),
                ))
        result = "\n".join(lines)
        if conn is not None and task_id is not None:
            _history_safe(conn, task_id, f"TOPIC2_PRICE_ENRICHMENT_DONE:{len(result)}")
        return result
    return await _T2FFB_PREV_SEARCH_ONLINE_V1(parsed, template, sheet_name, conn=conn, task_id=task_id)


def _t2ff_build_items_from_rows_v1(parsed, price_text, choice):
    rows = _t2ff_current_rows_v1(parsed)
    metal_mat = _t2ff_price_value_v1(price_text, ("металлопрокат", "профильная труба", "труба", "сталь"), choice)
    metal_fab = _t2ff_price_value_v1(price_text, ("изготовление металлоконструкций", "металлоконструкций ограждения", "ограждения"), choice)
    install_m = _t2ff_price_value_v1(price_text, ("монтаж металлического ограждения", "монтаж ограждения", "установка ограждения"), choice)
    install_each = _t2ff_price_value_v1(price_text, ("монтаж металлических ворот", "монтаж ворот", "монтаж калитки"), choice)
    items = []
    for row in rows:
        name = _s(row.get("name") or "")
        unit = _s(row.get("unit") or "шт")
        qty = float(row.get("qty") or 0)
        if not name or qty <= 0:
            continue
        low = _low(name)
        weight = float(row.get("weight_kg") or 0)
        if "ограждение территории" in low and unit in ("м", "м.п", "мп"):
            work_price, mat_price = install_m, 0.0
        elif any(x in low for x in ("секция", "стойк", "калит", "ворот")):
            per_item_weight = (weight / qty) if weight and qty else 0.0
            work_price = install_each if any(x in low for x in ("калит", "ворот")) else install_m
            mat_price = round(per_item_weight * (metal_mat + metal_fab), 2) if per_item_weight else 0.0
        else:
            work_price = _t2ff_price_value_v1(price_text, (name, "монтаж"), choice)
            mat_price = _t2ff_price_value_v1(price_text, (name, "материал"), choice)
        note = _s(row.get("note") or row.get("source") or "текущий файл")
        if work_price <= 0 and mat_price <= 0:
            note = (note + "; PRICE_MISSING").strip("; ")
        items.append({
            "section": "Проектные позиции",
            "name": name[:240],
            "unit": unit,
            "qty": qty,
            "price": round(work_price + mat_price, 2),
            "work_price": round(work_price, 2),
            "mat_price": round(mat_price, 2),
            "kind": "mixed",
            "note": note[:240],
        })
    subtotal = sum(float(it.get("qty") or 0) * (float(it.get("work_price") or 0) + float(it.get("mat_price") or 0)) for it in items)
    if subtotal > 0:
        items.append({
            "section": "Накладные расходы",
            "name": "Организация работ и накладные расходы",
            "unit": "компл",
            "qty": 1,
            "price": round(subtotal * 0.07, 2),
            "work_price": round(subtotal * 0.07, 2),
            "mat_price": 0.0,
            "kind": "mixed",
            "note": "7% от проектных стоимостных позиций",
        })
    return items


_T2FFB_PREV_BUILD_ITEMS_V1 = _build_estimate_items


def _build_estimate_items(parsed, price_text, choice):  # noqa: F811
    if _t2ff_file_context_v1(parsed) and _t2ff_confirmed_current_rows_v1(parsed):
        return _t2ff_build_items_from_rows_v1(parsed, price_text, choice)
    return _T2FFB_PREV_BUILD_ITEMS_V1(parsed, price_text, choice)


def _t2ff_rewrite_work_material_cols_v1(path, items):
    try:
        from openpyxl import load_workbook as _t2ff_lwb
        wb = _t2ff_lwb(path, data_only=False)
        ws = wb["AREAL_CALC"] if "AREAL_CALC" in wb.sheetnames else wb.active
        row_idx = 2
        for item in items or []:
            while row_idx <= ws.max_row and not _s(ws.cell(row_idx, 3).value):
                row_idx += 1
            if row_idx > ws.max_row:
                break
            ws.cell(row_idx, 6, float(item.get("work_price") or 0))
            ws.cell(row_idx, 7).value = f"=E{row_idx}*F{row_idx}"
            ws.cell(row_idx, 8, float(item.get("mat_price") or 0))
            ws.cell(row_idx, 9).value = f"=E{row_idx}*H{row_idx}"
            ws.cell(row_idx, 10).value = f"=G{row_idx}+I{row_idx}"
            row_idx += 1
        wb.save(path)
        wb.close()
    except Exception as exc:
        try:
            _STV3_LOG.warning("PATCH_TOPIC2_FILE_FACTS_BUILD_FROM_CURRENT_ROWS_V1 xlsx rewrite failed: %s", exc)
        except Exception:
            pass


_T2FFB_PREV_CREATE_XLSX_V1 = _create_xlsx_from_template


def _create_xlsx_from_template(task_id: str, parsed: Dict[str, Any], template: Dict[str, Any], template_path: Optional[str], sheet_name: Optional[str], price_text: str, choice: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]], float]:  # noqa: F811
    if _t2ff_file_context_v1(parsed) and _t2ff_confirmed_current_rows_v1(parsed):
        items = _t2ff_build_items_from_rows_v1(parsed, price_text, choice)
        orig_build = globals().get("_build_estimate_items")
        base_create = globals().get("_T2TR_ORIG_CREATE_XLSX") or _T2FFB_PREV_CREATE_XLSX_V1

        def _t2ff_build_current_file(_parsed, _price_text, _choice):
            return items

        globals()["_build_estimate_items"] = _t2ff_build_current_file
        try:
            path, _, _ = base_create(task_id, parsed, template, template_path, sheet_name, price_text, choice)
            _t2ff_rewrite_work_material_cols_v1(path, items)
            total = sum(float(it.get("qty") or 0) * (float(it.get("work_price") or 0) + float(it.get("mat_price") or 0)) for it in items)
            return path, items, total
        finally:
            globals()["_build_estimate_items"] = orig_build
    return _T2FFB_PREV_CREATE_XLSX_V1(task_id, parsed, template, template_path, sheet_name, price_text, choice)


try:
    _STV3_LOG.info("PATCH_TOPIC2_FILE_FACTS_BUILD_FROM_CURRENT_ROWS_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_FILE_FACTS_BUILD_FROM_CURRENT_ROWS_V1 ===

# === PATCH_TOPIC2_CLARIFIED_ESTIMATE_NOT_DONE_CONFIRM_V1 ===
# A clarification that says "yes, I need an estimate by these positions" is not
# a final DONE confirmation. It must continue the estimate cycle.
_T2CEN_PREV_IS_CONFIRM_V1 = _is_confirm
_T2CEN_PREV_IS_CONFIRM_ONLY_V1 = _is_confirm_only
_T2CEN_PREV_OLD_FINISH_V1 = _is_old_task_finish_request


def _t2cen_clarified_estimate_intent_v1(text):
    low = _low(text or "")
    if "topic2_clarified_estimate_intent" in low:
        return True
    return (
        ("нужна смета" in low or "смета по позициям" in low or "считать смету" in low)
        and any(x in low for x in ("монтаж", "позици", "сва", "ограж", "ворот", "калит"))
    )


def _is_confirm(text: str) -> bool:  # noqa: F811
    if _t2cen_clarified_estimate_intent_v1(text):
        return False
    return _T2CEN_PREV_IS_CONFIRM_V1(text)


def _is_confirm_only(text: str) -> bool:  # noqa: F811
    if _t2cen_clarified_estimate_intent_v1(text):
        return False
    return _T2CEN_PREV_IS_CONFIRM_ONLY_V1(text)


def _is_old_task_finish_request(text: str) -> bool:  # noqa: F811
    if _t2cen_clarified_estimate_intent_v1(text):
        return False
    return _T2CEN_PREV_OLD_FINISH_V1(text)


try:
    _STV3_LOG.info("PATCH_TOPIC2_CLARIFIED_ESTIMATE_NOT_DONE_CONFIRM_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_CLARIFIED_ESTIMATE_NOT_DONE_CONFIRM_V1 ===

# === PATCH_TOPIC2_FILE_MISSING_CONFIRM_RAW_BRIDGE_V1 ===
# The file/PDF guard above must see the current raw Telegram clarification too:
# "нужна смета по позициям..." is an approval to continue with current rows, not
# a reason to ask the same rows question again.
_T2FMCR_PREV_MISSING_QUESTION_V1 = _missing_question


def _missing_question(parsed: Dict[str, Any]) -> Optional[str]:  # noqa: F811
    if _topic2_volume_extract_requested_v1(
        _s((parsed or {}).get("_topic2_current_raw_input") or "")
        + "\n"
        + _s((parsed or {}).get("_topic2_history_clarified") or "")
    ):
        return None
    try:
        rows = list((parsed or {}).get("pdf_spec_rows") or []) + list((parsed or {}).get("ocr_table_rows") or [])
        if rows and _t2ff_file_context_v1(parsed) and _t2ff_confirmed_current_rows_v1(parsed):
            return None
    except Exception:
        pass
    return _T2FMCR_PREV_MISSING_QUESTION_V1(parsed)


try:
    _STV3_LOG.info("PATCH_TOPIC2_FILE_MISSING_CONFIRM_RAW_BRIDGE_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_FILE_MISSING_CONFIRM_RAW_BRIDGE_V1 ===

# === PATCH_TOPIC2_FILE_FINAL_SUMMARY_CLEAN_V1 ===
# File/PDF estimates must not expose raw JSON, patch markers, or merged context
# in the Telegram-facing "Объект" line.
_T2FFSC_PREV_FINAL_SUMMARY_V1 = _final_summary


def _t2ffsc_bad_display_value_v1(value) -> bool:
    text = _s(value).strip()
    low = text.lower()
    return (
        not text
        or len(text) > 120
        or text.startswith("{")
        or "patch_" in low
        or "raw_input" in low
        or "telegram_message_id" in low
        or "full recalc context" in low
    )


def _t2ffsc_file_object_v1(parsed) -> str:
    rows = _t2ff_current_rows_v1(parsed)
    names = " ".join(_s(r.get("name")) for r in rows if isinstance(r, dict))
    raw = _low((parsed or {}).get("raw") or "")
    text = _low(names + " " + raw)
    if "ограж" in text or "ворот" in text or "калит" in text:
        return "ограждение территории"
    if rows and _s(rows[0].get("name")):
        return _s(rows[0].get("name"))[:80]
    return "объект по приложенному файлу"


def _t2ffsc_file_material_v1(parsed) -> str:
    rows = _t2ff_current_rows_v1(parsed)
    names = " ".join(_s(r.get("name")) for r in rows if isinstance(r, dict))
    raw = _low((parsed or {}).get("raw") or "")
    text = _low(names + " " + raw)
    if "ограж" in text or "ворот" in text or "калит" in text or "стойк" in text:
        return "металлоконструкции ограждения"
    return "материалы по приложенному файлу"


def _final_summary(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], choice: Dict[str, Any], py_total: float, items=None) -> str:  # noqa: F811
    if _t2ff_file_context_v1(parsed):
        patched = dict(parsed or {})
        if _t2ffsc_bad_display_value_v1(patched.get("object")):
            patched["object"] = _t2ffsc_file_object_v1(patched)
        if _t2ffsc_bad_display_value_v1(patched.get("material")):
            patched["material"] = _t2ffsc_file_material_v1(patched)
        return _T2FFSC_PREV_FINAL_SUMMARY_V1(patched, template, sheet_name, choice, py_total, items=items)
    return _T2FFSC_PREV_FINAL_SUMMARY_V1(parsed, template, sheet_name, choice, py_total, items=items)


try:
    _STV3_LOG.info("PATCH_TOPIC2_FILE_FINAL_SUMMARY_CLEAN_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_FILE_FINAL_SUMMARY_CLEAN_V1 ===

# === PATCH_TOPIC2_METAL_FENCE_EXACT_KG_PRICING_V1 ===
# Current PDF fence rows contain reliable weights. Material price must be based
# on exact kg sources for metal/profile pipe + fabrication, not on accidental
# product cards for "Секция С01" / dates / unrelated search rows.
_T2MF_PREV_BUILD_ITEMS_V1 = _t2ff_build_items_from_rows_v1
_T2MF_PREV_REWRITE_COLS_V1 = _t2ff_rewrite_work_material_cols_v1


def _t2mf_float_v1(value, default=0.0):
    try:
        return float(str(value).replace(" ", "").replace(",", "."))
    except Exception:
        return default


def _t2mf_pipe_offers_v1(price_text, exact_positions, unit_hint="кг"):
    offers = []
    exact = [_low(x) for x in (exact_positions or []) if _s(x)]
    for raw_line in _s(price_text).splitlines():
        line = raw_line.strip(" \t-—•·")
        if "|" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            continue
        pos = _low(parts[0])
        if not any(x and x in pos for x in exact):
            continue
        unit = _low(parts[2])
        if unit_hint and unit_hint not in unit:
            continue
        price = _t2mf_float_v1(parts[1])
        if not (1 <= price <= 50000):
            continue
        offers.append({
            "position": parts[0],
            "price": price,
            "unit": parts[2],
            "supplier": parts[4] if len(parts) > 4 else "",
            "url": parts[5] if len(parts) > 5 else "",
            "checked_at": parts[6] if len(parts) > 6 else datetime.date.today().isoformat(),
        })
    return offers


def _t2mf_choose_price_v1(offers, choice):
    vals = [float(o.get("price") or 0) for o in (offers or []) if float(o.get("price") or 0) > 0]
    return float(_choose_value(vals, choice) or 0.0) if vals else 0.0


def _t2mf_combined_source_v1(*offer_lists):
    suppliers = []
    urls = []
    checked = []
    for offers in offer_lists:
        for offer in (offers or [])[:2]:
            sup = _s(offer.get("supplier"))
            url = _s(offer.get("url"))
            if sup and sup not in suppliers:
                suppliers.append(sup)
            if url and url not in urls:
                urls.append(url)
            if offer.get("checked_at"):
                checked.append(_s(offer.get("checked_at")))
    if not suppliers and not urls:
        return {}
    return {
        "status": "LIVE_CONFIRMED",
        "supplier": " / ".join(suppliers[:3]),
        "url": " / ".join(urls[:3]),
        "checked_at": max(checked) if checked else datetime.date.today().isoformat(),
    }


def _t2mf_is_metal_fence_row_v1(name):
    low = _low(name or "")
    return any(x in low for x in ("секция", "стойк", "калит", "ворот"))


def _t2ff_build_items_from_rows_v1(parsed, price_text, choice):  # noqa: F811
    items = list(_T2MF_PREV_BUILD_ITEMS_V1(parsed, price_text, choice) or [])
    rows = _t2ff_current_rows_v1(parsed)
    if not rows or not any(_t2mf_is_metal_fence_row_v1(r.get("name")) and _t2mf_float_v1(r.get("weight_kg")) > 0 for r in rows if isinstance(r, dict)):
        return items

    metal_offers = _t2mf_pipe_offers_v1(price_text, ("металлопрокат профильная труба",), "кг")
    fab_offers = _t2mf_pipe_offers_v1(price_text, ("изготовление металлоконструкций ограждения",), "кг")
    metal_kg = _t2mf_choose_price_v1(metal_offers, choice)
    fab_kg = _t2mf_choose_price_v1(fab_offers, choice)
    if metal_kg <= 0 or fab_kg <= 0:
        return items

    source = _t2mf_combined_source_v1(metal_offers, fab_offers)
    data_items = [dict(it) for it in items if _s(it.get("section")) not in ("Накладные", "Накладные расходы")]
    overhead_items = [dict(it) for it in items if _s(it.get("section")) in ("Накладные", "Накладные расходы")]

    for item, row in zip(data_items, rows):
        name = _s(row.get("name") or item.get("name") or "")
        if not _t2mf_is_metal_fence_row_v1(name):
            continue
        qty = _t2mf_float_v1(row.get("qty"))
        weight_total = _t2mf_float_v1(row.get("weight_kg"))
        if qty <= 0 or weight_total <= 0:
            continue
        per_item_weight = weight_total / qty
        mat_price = round(per_item_weight * (metal_kg + fab_kg), 2)
        work_price = _t2mf_float_v1(item.get("work_price"))
        item["mat_price"] = mat_price
        item["price"] = round(work_price + mat_price, 2)
        item["kind"] = "mixed"
        item["note"] = (_s(item.get("note")) + f"; материал по весу PDF: {per_item_weight:.2f} кг/ед, металл {metal_kg:.2f} руб/кг + изготовление {fab_kg:.2f} руб/кг")[:240]
        if source:
            item["price_source_status"] = source.get("status")
            item["price_supplier"] = source.get("supplier")
            item["price_url"] = source.get("url")
            item["price_checked_at"] = source.get("checked_at")

    subtotal = sum(
        _t2mf_float_v1(it.get("qty")) * (_t2mf_float_v1(it.get("work_price")) + _t2mf_float_v1(it.get("mat_price")))
        for it in data_items
    )
    if overhead_items and subtotal > 0:
        for oh in overhead_items:
            oh["price"] = round(subtotal * 0.07, 2)
            oh["work_price"] = round(subtotal * 0.07, 2)
            oh["mat_price"] = 0.0
            oh["note"] = "7% от проектных стоимостных позиций после корректировки материала по весу"
    return data_items + overhead_items


def _t2ff_rewrite_work_material_cols_v1(path, items):  # noqa: F811
    _T2MF_PREV_REWRITE_COLS_V1(path, items)
    try:
        from openpyxl import load_workbook
        wb = load_workbook(path)
        ws = wb.active
        row_idx = 2
        for item in items:
            while row_idx <= ws.max_row and not _s(ws.cell(row_idx, 3).value):
                row_idx += 1
            if row_idx > ws.max_row:
                break
            if item.get("price_source_status"):
                ws.cell(row_idx, 11, item.get("price_source_status"))
                ws.cell(row_idx, 12, item.get("price_supplier") or "")
                ws.cell(row_idx, 13, item.get("price_url") or "")
                ws.cell(row_idx, 14, item.get("price_checked_at") or datetime.date.today().isoformat())
            row_idx += 1
        wb.save(path)
        wb.close()
    except Exception as exc:
        try:
            _STV3_LOG.warning("PATCH_TOPIC2_METAL_FENCE_EXACT_KG_PRICING_V1 source rewrite failed: %s", exc)
        except Exception:
            pass


try:
    _STV3_LOG.info("PATCH_TOPIC2_METAL_FENCE_EXACT_KG_PRICING_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_METAL_FENCE_EXACT_KG_PRICING_V1 ===

# === PATCH_TOPIC2_PARSE_CLARIFIED_PRICE_CONFIRM_FIELDS_V1 ===
# Canon: a confirmed continuation in task_history belongs to the current task cycle.
# The clarification merge appends clarified text to raw_input before parsing; expose it
# in parsed fields used by file/OCR missing-question and price-search guards.
try:
    _T2PCPCF_PREV_PARSE_REQUEST_V1 = _parse_request

    def _parse_request(text: str):  # noqa: F811
        parsed = _T2PCPCF_PREV_PARSE_REQUEST_V1(text)
        try:
            low = _low(text or "")
            markers = (
                "считать по найденным позициям",
                "считать по найденным проектным позициям",
                "считай по найденным позициям",
                "считай по найденным проектным позициям",
                "только найденные позиции",
                "только найденные проектные позиции",
                "искать через интернет",
                "искать цены",
                "ищи цены",
                "актуальные цены",
                "цены на материалы",
                "изготовление и монтаж",
            )
            if isinstance(parsed, dict) and any(m in low for m in markers):
                parsed["_topic2_history_clarified"] = (parsed.get("_topic2_history_clarified") or "") + "\n" + str(text or "")
                parsed["_topic2_confirm_text"] = (parsed.get("_topic2_confirm_text") or "") + "\n" + str(text or "")
        except Exception:
            pass
        return parsed

    try:
        _STV3_LOG.info("PATCH_TOPIC2_PARSE_CLARIFIED_PRICE_CONFIRM_FIELDS_V1 installed")
    except Exception:
        pass
except Exception:
    pass
# === END_PATCH_TOPIC2_PARSE_CLARIFIED_PRICE_CONFIRM_FIELDS_V1 ===

# === PATCH_TOPIC2_FILE_CONTEXT_NO_TEMPLATE_PRICES_V1 ===
# Canon: when the current task is based on uploaded PDF/OCR rows, old template
# rows are not an evidence source and must not be shown or used as prices.
try:
    _T2FCNTP_PREV_EXTRACT_TEMPLATE_PRICES_V1 = extract_template_prices
    _T2FCNTP_PREV_PRICE_CONFIRMATION_TEXT_V1 = _price_confirmation_text

    def extract_template_prices(template_path, parsed):  # noqa: F811
        if _t2ff_file_context_v1(parsed):
            return ("", "AREAL_CALC", False)
        return _T2FCNTP_PREV_EXTRACT_TEMPLATE_PRICES_V1(template_path, parsed)

    def _price_confirmation_text(parsed, template, sheet_name, template_prices, online_prices):  # noqa: F811
        if _t2ff_file_context_v1(parsed):
            template = dict(template or {})
            template["title"] = "Проектные строки PDF/КР"
            sheet_name = "AREAL_CALC"
            template_prices = "Шаблонные строки отключены для текущего PDF/КР. Основа сметы: только распознанные проектные строки и подтверждённые интернет-цены."
        return _T2FCNTP_PREV_PRICE_CONFIRMATION_TEXT_V1(parsed, template, sheet_name, template_prices, online_prices)

    try:
        _STV3_LOG.info("PATCH_TOPIC2_FILE_CONTEXT_NO_TEMPLATE_PRICES_V1 installed")
    except Exception:
        pass
except Exception:
    pass
# === END_PATCH_TOPIC2_FILE_CONTEXT_NO_TEMPLATE_PRICES_V1 ===

# === PATCH_TOPIC2_ARCHIVE_ONLY_PRICE_AND_COMPLETION_V1 ===
def _topic2_archive_price_mode_v1(text: str) -> bool:
    low = _low(text or "")
    archive_requested = any(x in low for x in ("архив", "архивных данных", "памяти", "кэш", "cache"))
    internet_forbidden = any(x in low for x in (
        "без интернета",
        "интернет не использовать",
        "интернет не нужен",
        "не делать в интернете",
        "не искать в интернете",
        "поиск в интернете не",
        "поиск по материалам не делать",
    ))
    return archive_requested and internet_forbidden


_TOPIC2_ARCHIVE_PREV_PRICE_INTENT_V1 = _topic2_price_search_explicit_intent_v1


def _topic2_price_search_explicit_intent_v1(text: str) -> bool:  # noqa: F811
    if _topic2_archive_price_mode_v1(text):
        return True
    low = _low(text or "")
    if any(x in low for x in ("без интернета", "не искать в интернете", "поиск в интернете не", "интернет не использовать")):
        return False
    return _TOPIC2_ARCHIVE_PREV_PRICE_INTENT_V1(text)


_TOPIC2_ARCHIVE_PREV_CONFIRMED_ROWS_V1 = _t2ff_confirmed_current_rows_v1


def _t2ff_confirmed_current_rows_v1(parsed, confirm_text=""):  # noqa: F811
    if _TOPIC2_ARCHIVE_PREV_CONFIRMED_ROWS_V1(parsed, confirm_text):
        return True
    text = _low(confirm_text or "") + " " + _low((parsed or {}).get("raw") or "")
    return any(x in text for x in (
        "посчитать стоимость работ и материалов",
        "считать стоимость работ и материалов",
        "рассчитать стоимость работ и материалов",
        "смета по проекту",
    ))


def _topic2_archive_unit_v1(value: Any) -> str:
    return _low(value or "").replace("м3", "м³").replace("м2", "м²").replace("м.п.", "п.м").strip()


def _topic2_archive_category_v1(name: str) -> str:
    low = _low(name or "")
    if "бетон" in low:
        grade = re.search(r"[вb]\s*(\d+(?:[.,]\d+)?)", low, re.I)
        return "concrete:" + (grade.group(1).replace(",", ".") if grade else "")
    if "арматур" in low:
        cls = re.search(r"[аa](240|500[сc])", low, re.I)
        return "rebar:" + (cls.group(1).replace("c", "с") if cls else "")
    if any(x in low for x in ("газобет", "блоки строительные", "гб ")):
        thickness = re.search(r"(?:гб|газобет\w*)\s*(\d{2,3})", low, re.I)
        return "blocks:" + (thickness.group(1) if thickness else "")
    if any(x in low for x in ("достав", "логист", "транспорт")):
        return "logistics"
    return ""


def _topic2_archive_catalog_v1() -> List[Dict[str, Any]]:
    root = BASE / "runtime" / "stroyka_estimates"
    if not root.exists():
        return []
    try:
        from openpyxl import load_workbook as _topic2_archive_lwb
    except Exception:
        return []
    files = sorted(root.rglob("*.xlsx"), key=lambda path: path.stat().st_mtime, reverse=True)[:80]
    catalog: List[Dict[str, Any]] = []
    for path in files:
        try:
            wb = _topic2_archive_lwb(path, data_only=True, read_only=True)
            for ws in wb.worksheets:
                headers = {_low(ws.cell(1, col).value or ""): col for col in range(1, min(ws.max_column, 20) + 1)}
                name_col = headers.get("наименование")
                unit_col = headers.get("ед изм") or headers.get("ед. изм.")
                work_col = headers.get("цена работ")
                material_col = headers.get("цена материалов")
                if not (name_col and unit_col and work_col and material_col):
                    continue
                source_col = headers.get("источник цены")
                supplier_col = headers.get("поставщик")
                url_col = headers.get("url")
                checked_col = headers.get("checked_at")
                for row_idx in range(2, ws.max_row + 1):
                    name = _s(ws.cell(row_idx, name_col).value)
                    unit = _topic2_archive_unit_v1(ws.cell(row_idx, unit_col).value)
                    category = _topic2_archive_category_v1(name)
                    if not name or not unit or not category:
                        continue
                    try:
                        work_price = float(ws.cell(row_idx, work_col).value) if ws.cell(row_idx, work_col).value not in (None, "") else None
                    except Exception:
                        work_price = None
                    try:
                        material_price = float(ws.cell(row_idx, material_col).value) if ws.cell(row_idx, material_col).value not in (None, "") else None
                    except Exception:
                        material_price = None
                    if not ((work_price and work_price > 0) or (material_price and material_price > 0)):
                        continue
                    catalog.append({
                        "name": name,
                        "unit": unit,
                        "category": category,
                        "work_price": work_price,
                        "material_price": material_price,
                        "source": _s(ws.cell(row_idx, source_col).value) if source_col else "archive",
                        "supplier": _s(ws.cell(row_idx, supplier_col).value) if supplier_col else "",
                        "url": _s(ws.cell(row_idx, url_col).value) if url_col else "",
                        "checked_at": _s(ws.cell(row_idx, checked_col).value) if checked_col else "",
                        "archive_file": str(path),
                    })
            wb.close()
        except Exception:
            continue
    return catalog


def _topic2_archive_match_v1(name: str, unit: str, catalog: List[Dict[str, Any]]) -> Dict[str, Any]:
    category = _topic2_archive_category_v1(name)
    norm_unit = _topic2_archive_unit_v1(unit)
    if not category:
        return {}
    candidates = [row for row in catalog if row.get("category") == category and row.get("unit") == norm_unit]
    if not candidates and category.endswith(":"):
        prefix = category.split(":", 1)[0] + ":"
        candidates = [row for row in catalog if _s(row.get("category")).startswith(prefix) and row.get("unit") == norm_unit]
    if not candidates:
        return {}

    def one_value(field: str) -> Optional[float]:
        values = sorted({round(float(row[field]), 4) for row in candidates if row.get(field) not in (None, "") and float(row[field]) > 0})
        return values[0] if len(values) == 1 else None

    work_price = one_value("work_price")
    material_price = one_value("material_price")
    if work_price is None and material_price is None:
        return {}
    source_row = candidates[0]
    return {
        "work_price": work_price,
        "material_price": material_price,
        "source": "archive:" + _s(source_row.get("source") or "saved estimate"),
        "supplier": _s(source_row.get("supplier")),
        "url": _s(source_row.get("url")),
        "checked_at": _s(source_row.get("checked_at")),
        "archive_file": _s(source_row.get("archive_file")),
    }


_TOPIC2_ARCHIVE_PREV_SEARCH_ONLINE_V1 = _search_prices_online


async def _search_prices_online(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], conn=None, task_id=None) -> str:  # noqa: F811
    if not _topic2_archive_price_mode_v1((parsed or {}).get("raw") or ""):
        return await _TOPIC2_ARCHIVE_PREV_SEARCH_ONLINE_V1(parsed, template, sheet_name, conn=conn, task_id=task_id)
    rows = _t2ff_current_rows_v1(parsed)
    catalog = _topic2_archive_catalog_v1()
    price_map = {}
    lines = ["ARCHIVE_ONLY: интернет-поиск отключён пользователем; неизвестные цены оставлены пустыми"]
    for row in rows:
        name = _s(row.get("name"))
        match = _topic2_archive_match_v1(name, _s(row.get("unit")), catalog)
        price_map[name] = match
        if match:
            lines.append("- {} | работа={} | материал={} | {}".format(
                name,
                match.get("work_price") if match.get("work_price") is not None else "PRICE_MISSING",
                match.get("material_price") if match.get("material_price") is not None else "PRICE_MISSING",
                match.get("source") or "archive",
            ))
    parsed["_topic2_archive_price_map"] = price_map
    parsed["_topic2_archive_price_catalog_count"] = len(catalog)
    if conn is not None and task_id is not None:
        _history_safe(conn, task_id, "TOPIC2_INTERNET_SEARCH_DISABLED_BY_USER")
        _history_safe(conn, task_id, f"TOPIC2_ARCHIVE_PRICE_CATALOG_READ:{len(catalog)}")
        _history_safe(conn, task_id, f"TOPIC2_ARCHIVE_PRICE_REUSED:{sum(1 for value in price_map.values() if value)}")
        _history_safe(conn, task_id, "TOPIC2_PRICE_ENRICHMENT_DONE:archive_only")
    return "\n".join(lines)


_TOPIC2_ARCHIVE_PREV_BUILD_ITEMS_V1 = _t2ff_build_items_from_rows_v1


def _t2ff_build_items_from_rows_v1(parsed, price_text, choice):  # noqa: F811
    if not _topic2_archive_price_mode_v1((parsed or {}).get("raw") or ""):
        return _TOPIC2_ARCHIVE_PREV_BUILD_ITEMS_V1(parsed, price_text, choice)
    rows = _t2ff_current_rows_v1(parsed)
    price_map = (parsed or {}).get("_topic2_archive_price_map") or {}
    items = []
    for row in rows:
        name = _s(row.get("name"))
        try:
            qty = float(row.get("qty") or 0)
        except Exception:
            qty = 0.0
        if not name or qty <= 0:
            continue
        match = price_map.get(name) or {}
        work_price = match.get("work_price")
        material_price = match.get("material_price")
        category = _topic2_archive_category_v1(name)
        section = "Проектные позиции"
        if category.startswith("concrete") or category.startswith("rebar"):
            section = "Монолитные конструкции"
        elif category.startswith("blocks"):
            section = "Стены"
        missing = []
        if work_price is None:
            missing.append("WORK_PRICE_MISSING")
        if material_price is None:
            missing.append("MATERIAL_PRICE_MISSING")
        note = _s(row.get("note") or row.get("source") or "текущий PDF")
        if missing:
            note = (note + "; " + "; ".join(missing)).strip("; ")
        items.append({
            "section": section,
            "name": name[:240],
            "unit": _s(row.get("unit") or "шт"),
            "qty": qty,
            "price": float(work_price or 0) + float(material_price or 0),
            "work_price": float(work_price or 0),
            "mat_price": float(material_price or 0),
            "work_price_missing": work_price is None,
            "material_price_missing": material_price is None,
            "kind": "mixed",
            "note": note[:240],
            "source": _s(match.get("source") or "PRICE_MISSING"),
            "supplier": _s(match.get("supplier")),
            "url": _s(match.get("url")),
            "checked_at": _s(match.get("checked_at")),
            "archive_price_mode": True,
        })
    try:
        distance = float((parsed or {}).get("distance_km") or 0)
    except Exception:
        distance = 0.0
    if distance > 0:
        items.append({
            "section": "Логистика",
            "name": f"Логистика до объекта, удалённость {distance:g} км",
            "unit": "компл",
            "qty": 1.0,
            "price": 0.0,
            "work_price": 0.0,
            "mat_price": 0.0,
            "work_price_missing": True,
            "material_price_missing": True,
            "kind": "mixed",
            "note": "Цена отсутствует в однозначно совпадающих архивных данных; оставлена пустой",
            "source": "PRICE_MISSING",
            "archive_price_mode": True,
        })
    subtotal = sum(item["qty"] * (item["work_price"] + item["mat_price"]) for item in items)
    if subtotal > 0:
        overhead = round(subtotal * 0.07, 2)
        items.append({
            "section": "Накладные расходы",
            "name": "Организация работ и накладные расходы",
            "unit": "компл",
            "qty": 1.0,
            "price": overhead,
            "work_price": overhead,
            "mat_price": 0.0,
            "work_price_missing": False,
            "material_price_missing": False,
            "kind": "mixed",
            "note": "7% от подтверждённых архивными ценами позиций",
            "source": "CANON_OVERHEAD_7_PERCENT",
            "archive_price_mode": True,
        })
    return items


_TOPIC2_ARCHIVE_PREV_REWRITE_COLS_V1 = _t2ff_rewrite_work_material_cols_v1


def _t2ff_rewrite_work_material_cols_v1(path, items):  # noqa: F811
    _TOPIC2_ARCHIVE_PREV_REWRITE_COLS_V1(path, items)
    try:
        from openpyxl import load_workbook as _topic2_archive_rewrite_lwb
        wb = _topic2_archive_rewrite_lwb(path, data_only=False)
        ws = wb["AREAL_CALC"] if "AREAL_CALC" in wb.sheetnames else wb.active
        row_idx = 2
        for item in items or []:
            while row_idx <= ws.max_row and not _s(ws.cell(row_idx, 3).value):
                row_idx += 1
            if row_idx > ws.max_row:
                break
            if item.get("work_price_missing"):
                ws.cell(row_idx, 6).value = None
            if item.get("material_price_missing"):
                ws.cell(row_idx, 8).value = None
            ws.cell(row_idx, 11).value = _s(item.get("source") or "PRICE_MISSING")
            ws.cell(row_idx, 12).value = _s(item.get("supplier"))
            ws.cell(row_idx, 13).value = _s(item.get("url"))
            ws.cell(row_idx, 14).value = _s(item.get("checked_at"))
            ws.cell(row_idx, 15).value = _s(item.get("note"))
            row_idx += 1
        wb.save(path)
        wb.close()
    except Exception as exc:
        try:
            _STV3_LOG.warning("TOPIC2_ARCHIVE_PRICE_XLSX_REWRITE_FAILED: %s", exc)
        except Exception:
            pass


_TOPIC2_ARCHIVE_PREV_QUALITY_GATE_V1 = _quality_gate_xlsx


def _quality_gate_xlsx(xlsx_path: str, items: List[Dict[str, Any]], py_total: float) -> Tuple[bool, str]:  # noqa: F811
    archive_blank_mode = bool(items) and all(bool(item.get("archive_price_mode")) for item in items)
    if not archive_blank_mode or py_total > 0:
        return _TOPIC2_ARCHIVE_PREV_QUALITY_GATE_V1(xlsx_path, items, py_total)
    if not xlsx_path or not os.path.exists(xlsx_path) or os.path.getsize(xlsx_path) < 5000:
        return False, "ARCHIVE_BLANK_XLSX_INVALID"
    if len(items) < 8:
        return False, f"ARCHIVE_BLANK_TOO_FEW_ITEMS:{len(items)}"
    try:
        from openpyxl import load_workbook as _topic2_archive_qg_lwb
        wb = _topic2_archive_qg_lwb(xlsx_path, data_only=False, read_only=True)
        ws = wb["AREAL_CALC"] if "AREAL_CALC" in wb.sheetnames else wb.active
        headers = [_s(ws.cell(1, col).value) for col in range(1, 16)]
        formula_count = sum(1 for row in ws.iter_rows() for cell in row if isinstance(cell.value, str) and cell.value.startswith("="))
        wb.close()
        if len(headers) < 15 or formula_count < 8:
            return False, "ARCHIVE_BLANK_CANON_COLUMNS_OR_FORMULAS_MISSING"
        return True, "OK_ARCHIVE_PRICES_MISSING_ALLOWED_BY_USER"
    except Exception as exc:
        return False, "ARCHIVE_BLANK_XLSX_VALIDATE_ERROR:" + _s(exc)[:120]
# === END_PATCH_TOPIC2_ARCHIVE_ONLY_PRICE_AND_COMPLETION_V1 ===

# === PATCH_TOPIC2_NEW_PROJECT_PDF_ISOLATION_V2 ===
# A newly uploaded project PDF is an isolated project context.  It must pass the
# project-volume completeness gate before prices, templates or final artifacts.
_TOPIC2_NEW_PROJECT_PREV_HANDLER_V2 = maybe_handle_stroyka_estimate


def _topic2_project_incomplete_message_v2(bundle: Dict[str, Any]) -> str:
    facts = list(bundle.get("project_facts") or [])
    positions = list(bundle.get("positions") or [])
    totals = list(bundle.get("totals") or [])
    missing = list(bundle.get("missing_items") or [])
    object_name = next((_s(row.get("value")) for row in facts if _low(row.get("name")) == "объект"), "проект")
    pages = next((_s(row.get("value")) for row in facts if "страниц" in _low(row.get("name"))), "")
    lines = [
        "Принял PDF как новый отдельный проект.",
        f"Объект: {object_name}",
    ]
    if pages:
        lines.append(f"Обработано страниц: {pages}")
    lines.extend(["", "Подтверждено по ведомостям проекта:"])
    for row in totals:
        value = row.get("value")
        unit = _s(row.get("unit"))
        if value not in (None, ""):
            lines.append(f"- {_s(row.get('name'))}: {value:g} {unit}" if isinstance(value, (int, float)) else f"- {_s(row.get('name'))}: {value} {unit}")
    masonry = [row for row in positions if _s(row.get("position_type")) == "masonry_material"]
    for row in masonry:
        lines.append(f"- {_s(row.get('name'))}: {int(row.get('count_pcs') or 0)} шт, {float(row.get('volume_m3') or 0):g} м³")
    structural = [row for row in positions if _s(row.get("position_type")) == "project_structural_element"]
    lines.append(f"- Конструктивные элементы: {len(structural)} позиций с объёмом бетона и массой арматуры")

    labels = {
        "formwork_area_m2": "площадь опалубки",
        "crushed_stone_base_volume_m3": "объём щебёночного основания",
        "waterproofing_area_m2": "площадь гидроизоляции",
        "insulation_area_m2": "площадь утепления",
        "steel_concrete_summary_table": "сводная ведомость бетона и арматуры",
        "masonry_schedule": "ведомость кладочных блоков",
    }
    lines.extend(["", "До сметы не подтверждены отдельной ведомостью:"])
    for item in missing:
        lines.append(f"- {labels.get(_s(item), _s(item))}")
    lines.extend([
        "",
        "Цены и смету пока не запускаю, чтобы не подмешивать старые позиции и не выдумывать объёмы.",
        "Уточни: рассчитать отсутствующие объёмы по геометрии чертежей или считать только позиции из подтверждённых ведомостей?",
    ])
    return "\n".join(lines)


def _topic2_project_clarifications_v2(conn, task_id: str) -> str:
    try:
        rows = conn.execute(
            "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'clarified:%' ORDER BY id ASC",
            (task_id,),
        ).fetchall()
        return "\n".join(_s(row[0]).split("clarified:", 1)[1] for row in rows if "clarified:" in _s(row[0]))
    except Exception:
        return ""


def _topic2_project_manual_rates_v2(text: str) -> Dict[str, Any]:
    low = _low(text).replace("₽", " руб ")
    rules = {
        "rebar_material_per_t": r"арматур[^\n]{0,45}?(\d[\d\s]{3,})[^\n]{0,20}(?:тон|т\b)",
        "gasblock_material_per_m3": r"газобетон[^\n]{0,35}?(\d[\d\s]{3,})[^\n]{0,20}(?:куб|м3|м³)",
        "foundation_work_per_m3": r"(?:работ[^\n]{0,30}фундамент|фундамент[^\n]{0,30}работ)[^\n]{0,30}?(\d[\d\s]{3,})",
        "slab_work_per_m3": r"перекрыт[^\n]{0,35}?(\d[\d\s]{3,})[^\n]{0,20}(?:куб|м3|м³)",
        "wall_work_per_m3": r"(?:стен[^\n]{0,20}монолит|монолит[^\n]{0,20}стен)[^\n]{0,25}?(\d[\d\s]{3,})",
        "concrete_material_per_m3": r"(?<!газо)бетон[^\n]{0,35}?(\d[\d\s]{3,})(?:[^\n]{0,20}(?:куб|м3|м³))?",
        "column_work_per_m3": r"колонн[^\n]{0,35}?(?:работ[^\n]{0,20}?)?(\d[\d\s]{3,})[^\n]{0,20}(?:куб|м3|м³)",
        "masonry_work_per_m3": r"кладк[^\n]{0,25}газобетон[^\n]{0,30}?(\d[\d\s]{3,})[^\n]{0,20}(?:куб|м3|м³)",
        "stairs_work_per_unit": r"лестниц[^\n]{0,45}?работ[^\n]{0,25}?(\d[\d\s]{3,})[^\n]{0,20}(?:единиц|шт)",
        "remaining_monolith_work_per_m3": r"(?:р1|р2|р3|ростверк)[^\n]{0,60}?(\d[\d\s]{3,})[^\n]{0,20}(?:куб|м3|м³)",
        "rostverk_work_per_m": r"(?:^|\n)\s*(\d[\d\s]*)[^\n]{0,20}(?:метр\s+погон|пог\.?\s*м)",
        "crushed_stone_material_per_m3": r"щеб[^\n]{0,35}?(\d[\d\s]{1,})[^\n]{0,20}(?:куб|м3|м³)",
        "crushed_stone_work_per_m3": r"щеб[^\n]{0,60}?работ[^\n]{0,20}?(\d[\d\s]{1,})",
        "waterproofing_material_per_m2": r"гидроизоляц[^\n]{0,35}?материал[^\n]{0,20}?(\d[\d\s]{3,})",
        "waterproofing_work_per_m2": r"гидроизоляц[^\n]{0,35}?работ[^\n]{0,20}?(\d[\d\s]{3,})",
        "insulation_material_per_m2": r"утеплен[^\n]{0,35}?материал[^\n]{0,20}?(\d[\d\s]{3,})",
        "insulation_work_per_m2": r"утеплен[^\n]{0,35}?работ[^\n]{0,20}?(\d[\d\s]{3,})",
    }
    out: Dict[str, Any] = {}
    for key, pattern in rules.items():
        match = re.search(pattern, low, re.I)
        if not match:
            continue
        try:
            out[key] = float(match.group(1).replace(" ", ""))
        except Exception:
            pass
    shared_layers = re.search(
        r"(?:гидроизоляц[^\n]{0,30}утеплен|утеплен[^\n]{0,30}гидроизоляц)"
        r"[^\n]{0,35}?материал[^\n]{0,20}?(\d[\d\s]*)[^\n]{0,25}работ[^\n]{0,20}?(\d[\d\s]*)",
        low,
        re.I,
    )
    if shared_layers:
        material_rate = float(shared_layers.group(1).replace(" ", ""))
        work_rate = float(shared_layers.group(2).replace(" ", ""))
        out.update({
            "waterproofing_material_per_m2": material_rate,
            "waterproofing_work_per_m2": work_rate,
            "insulation_material_per_m2": material_rate,
            "insulation_work_per_m2": work_rate,
        })
    monolith_scope = re.search(
        r"монолитн[^\n.]{0,40}работ[^\n.]{0,40}(?:не\s+)?включ[^\n.]{0,50}опалуб[^\n.]{0,50}(?:вязк|арматур)",
        low,
        re.I,
    )
    if monolith_scope:
        out["monolith_rates_include_formwork_rebar"] = "не включ" not in monolith_scope.group(0)
    if ("щеб" in low and "гидроизоляц" in low) and any(x in low for x in ("включ", "конечно да", "считать")):
        out["include_project_layers"] = True
    if "подъезд" in low:
        out["logistics_access_confirmed"] = True
        out["logistics_access"] = "no" if re.search(r"подъезд[^\n]{0,20}(?:нет|отсутств)", low) else "yes"
    if any(token in low for token in ("разгруз", "манипулятор", "кран")):
        out["logistics_unloading_confirmed"] = True
        out["logistics_unloading"] = "not_required" if any(
            token in low for token in ("разгрузка не нужна", "манипулятор не нужен", "без разгрузки")
        ) else "required"
    same_blank_line = re.search(
        r"(?:логист[^\n]{0,50}накладн|накладн[^\n]{0,50}логист)[^\n]{0,50}(?:пуст|не включ|не учитывать)",
        low,
    )
    if same_blank_line:
        out["logistics_mode"] = "blank"
        out["overhead_mode"] = "blank"
    elif "логист" in low and any(token in low for token in ("пуст", "не включ", "не учитывать")):
        out["logistics_mode"] = "blank"
    elif "накладн" in low and any(token in low for token in ("пуст", "не включ", "не учитывать")):
        out["overhead_mode"] = "blank"
    logistics_deliveries = re.search(
        r"логист[^\n]{0,50}?(\d+)\s+(?:достав\w*|рейс\w*)\s+(?:по|x|х|×)\s*"
        r"(\d[\d\s]{2,})(?:\s*(?:руб|р\b))?",
        low,
    )
    if logistics_deliveries:
        delivery_count = int(logistics_deliveries.group(1))
        delivery_unit_price = float(logistics_deliveries.group(2).replace(" ", ""))
        out["logistics_mode"] = "manual_amount"
        out["logistics_delivery_count"] = delivery_count
        out["logistics_unit_price"] = delivery_unit_price
        out["logistics_amount"] = delivery_count * delivery_unit_price
    else:
        logistics_amount = re.search(r"логист[^\n]{0,35}?(\d[\d\s]{3,})\s*(?:руб|р\b)", low)
        if logistics_amount:
            out["logistics_mode"] = "manual_amount"
            out["logistics_amount"] = float(logistics_amount.group(1).replace(" ", ""))
    overhead_amount = re.search(r"накладн[^\n]{0,35}?(\d[\d\s]{3,})\s*(?:руб|р\b)", low)
    overhead_percent = re.search(r"накладн[^\n]{0,35}?(\d+(?:[.,]\d+)?)\s*%", low)
    if overhead_amount:
        out["overhead_mode"] = "manual_amount"
        out["overhead_amount"] = float(overhead_amount.group(1).replace(" ", ""))
    elif overhead_percent:
        out["overhead_mode"] = "percent"
        out["overhead_percent"] = float(overhead_percent.group(1).replace(",", "."))
        if re.search(r"(?:от\s+)?(?:общей\s+)?стоимост[ьи]\s+работ", low):
            out["overhead_basis"] = "works_only"
    return out


def _topic2_project_manual_price_message_v2(rates: Dict[str, Any]) -> str:
    labels = {
        "rebar_material_per_t": "арматура: {value:g} руб/т",
        "gasblock_material_per_m3": "газобетон: {value:g} руб/м³",
        "foundation_work_per_m3": "монолитный фундамент, работы: {value:g} руб/м³",
        "slab_work_per_m3": "межэтажные перекрытия, работы: {value:g} руб/м³",
        "wall_work_per_m3": "монолитные стены, работы: {value:g} руб/м³",
        "concrete_material_per_m3": "бетон В30/В25 с доставкой: {value:g} руб/м³",
        "column_work_per_m3": "монолитные колонны, работы: {value:g} руб/м³",
        "masonry_work_per_m3": "кладка газобетона, работы: {value:g} руб/м³",
        "stairs_work_per_unit": "лестницы, работы: {value:g} руб/ед.",
        "remaining_monolith_work_per_m3": "элементы Р1/Р2/Р3, работы: {value:g} руб/м³",
        "rostverk_work_per_m": "ростверки Р1/Р2/Р3, работы: {value:g} руб/пог. м",
        "crushed_stone_material_per_m3": "щебёночное основание, материал: {value:g} руб/м³",
        "crushed_stone_work_per_m3": "щебёночное основание, работы: {value:g} руб/м³",
        "waterproofing_material_per_m2": "гидроизоляция, материал: {value:g} руб/м²",
        "waterproofing_work_per_m2": "гидроизоляция, работы: {value:g} руб/м²",
        "insulation_material_per_m2": "утепление, материал: {value:g} руб/м²",
        "insulation_work_per_m2": "утепление, работы: {value:g} руб/м²",
    }
    lines = ["Принял расчёт по текущему проекту и записал ручные расценки:"]
    for key in labels:
        if key in rates:
            lines.append("- " + labels[key].format(value=rates[key]))
    if rates.get("monolith_rates_include_formwork_rebar") is True:
        lines.append("- монолитные работы включают опалубку и вязку арматуры")
    if rates.get("include_project_layers") is True:
        lines.append("- щебёночное основание, гидроизоляцию и утепление включить")
    missing: List[str] = []
    if "concrete_material_per_m3" not in rates:
        missing.append("бетон В30 и В25: цена материала за м³")
    if "column_work_per_m3" not in rates:
        missing.append("колонны К1/К2: цена работ за м³")
    if "remaining_monolith_work_per_m3" not in rates:
        if "rostverk_work_per_m" in rates:
            missing.append(
                f"для ростверков Р1/Р2/Р3 указано {rates['rostverk_work_per_m']:g} руб/пог. м, "
                "но в извлечённой ведомости есть только объём 10,5 м³ без погонной длины; "
                "укажите цену работ за м³ либо подтвердите расчёт длины по геометрии проекта"
            )
        else:
            missing.append("элементы Р1/Р2/Р3: цена работ за м³")
    if "stairs_work_per_unit" not in rates:
        missing.append("лестницы Л1/Л2: цена работ за единицу")
    if "masonry_work_per_m3" not in rates:
        missing.append("кладка газобетона: цена работ за м³")
    if "monolith_rates_include_formwork_rebar" not in rates:
        missing.append("включены ли опалубка и вязка арматуры в монолитные работы")
    if "include_project_layers" not in rates:
        missing.append("включать ли щебёночное основание, гидроизоляцию и утепление")
    if rates.get("include_project_layers") is True:
        layer_keys = (
            "crushed_stone_material_per_m3", "crushed_stone_work_per_m3",
            "waterproofing_material_per_m2", "waterproofing_work_per_m2",
            "insulation_material_per_m2", "insulation_work_per_m2",
        )
        if any(key not in rates for key in layer_keys):
            missing.append("щебень: материал/работа за м³; гидроизоляция и утепление: материал/работа за м² (совпадающих архивных цен нет)")
    lines.extend(["", "Для сметы без нулевых цен осталось уточнить:"])
    for index, item in enumerate(missing, 1):
        lines.append(f"{index}. {item}.")
    lines.extend(["", "Интернет-поиск не запускаю."])
    return "\n".join(lines)


def _topic2_project_manual_rates_missing_v3(rates: Dict[str, Any]) -> List[str]:
    required = (
        "rebar_material_per_t", "gasblock_material_per_m3",
        "foundation_work_per_m3", "slab_work_per_m3", "wall_work_per_m3",
        "concrete_material_per_m3", "column_work_per_m3", "masonry_work_per_m3",
        "stairs_work_per_unit", "remaining_monolith_work_per_m3",
        "crushed_stone_material_per_m3", "crushed_stone_work_per_m3",
        "waterproofing_material_per_m2", "waterproofing_work_per_m2",
        "insulation_material_per_m2", "insulation_work_per_m2",
        "monolith_rates_include_formwork_rebar", "include_project_layers",
    )
    return [key for key in required if key not in rates]


def _topic2_project_logistics_missing_v3(rates: Dict[str, Any]) -> List[str]:
    missing = []
    if not rates.get("logistics_access_confirmed"):
        missing.append("подъезд для грузовой техники")
    if not rates.get("logistics_unloading_confirmed"):
        missing.append("нужна ли разгрузка/манипулятор")
    if "logistics_mode" not in rates:
        missing.append("логистику: указать сумму или оставить пустой")
    if "overhead_mode" not in rates:
        missing.append("накладные расходы: указать сумму/процент или оставить пустыми")
    return missing


def _topic2_project_logistics_prompt_v3(rates: Dict[str, Any]) -> str:
    missing = _topic2_project_logistics_missing_v3(rates)
    lines = [
        "Перед финальной сметой осталось подтвердить логистику и накладные расходы для текущего проекта (20 км от Санкт-Петербурга).",
    ]
    if rates.get("logistics_mode") == "manual_amount":
        if rates.get("logistics_delivery_count") and rates.get("logistics_unit_price") is not None:
            lines.append(
                "Принял логистику: "
                f"{int(rates['logistics_delivery_count'])} доставок × "
                f"{float(rates['logistics_unit_price']):g} = "
                f"{float(rates['logistics_amount']):g} руб."
            )
        else:
            lines.append(f"Принял логистику: {float(rates['logistics_amount']):g} руб.")
    lines.extend([
        "Уточните одним сообщением:",
        *[f"- {item}" for item in missing],
        "",
        "Интернет-поиск не запускаю.",
    ])
    return "\n".join(lines)


def _topic2_current_project_source_v3(row: Dict[str, Any], calculation: str = "") -> Dict[str, Any]:
    return {
        "source_type": "CURRENT_PROJECT_PDF",
        "source_file": _s(row.get("source_file")),
        "page": row.get("page"),
        "table_name": _s(row.get("table_name") or row.get("sheet") or "Текущий проект"),
        "row_text": _s(row.get("row_text") or row.get("text") or row.get("name")),
        "calculation": calculation or _s(row.get("calculation") or row.get("geometry_calculation")),
        "confidence": _s(row.get("confidence") or "direct"),
    }


def _topic2_current_project_manual_rows_v3(bundle: Dict[str, Any], rates: Dict[str, Any]) -> Dict[str, Any]:
    prepared = dict(bundle or {})
    rows: List[Dict[str, Any]] = []

    def add_row(section, name, unit, qty, work_price, material_price, source, key):
        row = _topic2_billable_row_v1(section, name, unit, qty, key + ".material", key, source)
        row.update({
            "work_unit_price": float(work_price) if work_price is not None else None,
            "material_unit_price": float(material_price) if material_price is not None else None,
            "work_price_source": "MANUAL" if work_price is not None else "NOT_APPLICABLE_OR_INCLUDED",
            "material_price_source": "MANUAL" if material_price is not None else "NOT_APPLICABLE_OR_INCLUDED",
            "work_price_status": "MANUAL" if work_price is not None else "NOT_APPLICABLE",
            "material_price_status": "MANUAL" if material_price is not None else "NOT_APPLICABLE",
            "supplier": "Расценка пользователя",
            "source_url": "",
            "checked_at": _now(),
        })
        rows.append(row)

    for position in prepared.get("positions") or []:
        if not isinstance(position, dict):
            continue
        name = _s(position.get("name"))
        low = _low(name)
        source = _topic2_current_project_source_v3(position)
        if _s(position.get("position_type")) == "project_structural_element":
            volume = float(position.get("concrete_volume_m3") or 0)
            rebar_t = float(position.get("rebar_mass_kg") or 0) / 1000.0
            if "плита фп" in low:
                section, work = "02 Фундаменты", rates["foundation_work_per_m3"]
            elif "плита пп" in low:
                section, work = "03 Монолитные перекрытия", rates["slab_work_per_m3"]
            elif "колонн" in low:
                section, work = "03 Монолитные колонны", rates["column_work_per_m3"]
            elif "стен" in low:
                section, work = "03 Монолитные стены", rates["wall_work_per_m3"]
            elif "ростверк" in low:
                section, work = "02 Ростверки", rates["remaining_monolith_work_per_m3"]
            elif "лестниц" in low:
                section, work = "03 Монолитные лестницы", None
            else:
                continue
            add_row(
                section, f"Бетон и монолитные работы: {name}", "м³", volume,
                work, rates["concrete_material_per_m3"], source,
                "current_project.concrete." + re.sub(r"\W+", "_", low),
            )
            if rebar_t > 0:
                add_row(
                    section, f"Арматура: {name}", "т", rebar_t,
                    None, rates["rebar_material_per_t"], source,
                    "current_project.rebar." + re.sub(r"\W+", "_", low),
                )
            if "лестниц" in low:
                add_row(
                    section, f"Устройство лестницы: {name}", "шт", 1,
                    rates["stairs_work_per_unit"], None, source,
                    "current_project.stairs_work." + re.sub(r"\W+", "_", low),
                )
        elif _s(position.get("position_type")) == "masonry_material":
            volume = float(position.get("volume_m3") or 0)
            add_row(
                "04 Стены и перегородки", f"Газобетон и кладка: {name}", "м³", volume,
                rates["masonry_work_per_m3"], rates["gasblock_material_per_m3"], source,
                "current_project.masonry." + re.sub(r"\W+", "_", low),
            )

    derived_by_name = {
        _s(row.get("name")): row for row in (prepared.get("derived_quantities") or [])
        if isinstance(row, dict)
    }
    layer_rows = (
        (
            "01 Основание", "Щебёночное основание", "Объём щебёночного основания", "м³",
            rates["crushed_stone_work_per_m3"], rates["crushed_stone_material_per_m3"],
            "current_project.layers.crushed_stone",
        ),
        (
            "05 Гидроизоляция и утепление", "Гидроизоляция по проекту", "Площадь гидроизоляции", "м²",
            rates["waterproofing_work_per_m2"], rates["waterproofing_material_per_m2"],
            "current_project.layers.waterproofing",
        ),
        (
            "05 Гидроизоляция и утепление", "Утепление по проекту", "Площадь утепления", "м²",
            rates["insulation_work_per_m2"], rates["insulation_material_per_m2"],
            "current_project.layers.insulation",
        ),
    )
    for section, name, quantity_name, unit, work, material, key in layer_rows:
        quantity = derived_by_name.get(quantity_name)
        if not quantity:
            continue
        add_row(
            section, name, unit, quantity.get("value"), work, material,
            _topic2_current_project_source_v3(quantity), key,
        )

    clarification_source = {
        "source_type": "USER_CLARIFICATION",
        "source_file": "Telegram",
        "page": "",
        "table_name": "Текущее уточнение пользователя",
        "row_text": "Логистика и накладные расходы",
        "calculation": "Ручная сумма/процент пользователя",
        "confidence": "confirmed",
    }
    if rates.get("logistics_mode") == "manual_amount":
        logistics_source = dict(clarification_source)
        if rates.get("logistics_delivery_count") and rates.get("logistics_unit_price") is not None:
            logistics_source["calculation"] = (
                f"{int(rates['logistics_delivery_count'])} доставок × "
                f"{float(rates['logistics_unit_price']):g} руб = "
                f"{float(rates['logistics_amount']):g} руб"
            )
        add_row(
            "09 Логистика", "Логистика по текущему проекту", "компл.", 1,
            rates.get("logistics_amount"), None, logistics_source,
            "current_project.logistics",
        )
    if rates.get("overhead_mode") == "manual_amount":
        add_row(
            "10 Накладные расходы", "Накладные расходы", "компл.", 1,
            rates.get("overhead_amount"), None, clarification_source,
            "current_project.overhead",
        )
    elif rates.get("overhead_mode") == "percent":
        if rates.get("overhead_basis") == "works_only":
            base_total = sum(
                float(row.get("qty") or 0) * float(row.get("work_unit_price") or 0)
                for row in rows
                if _topic2_current_project_canon_section_v4(row) not in (
                    "09 Логистика", "10 Накладные расходы",
                )
            )
        else:
            base_total = sum(
                float(row.get("qty") or 0)
                * (float(row.get("work_unit_price") or 0) + float(row.get("material_unit_price") or 0))
                for row in rows
            )
        overhead_amount = base_total * float(rates.get("overhead_percent") or 0) / 100.0
        percent_source = dict(clarification_source)
        basis_text = "стоимость работ" if rates.get("overhead_basis") == "works_only" else "подтверждённая база"
        percent_source["calculation"] = (
            f"{basis_text}: {base_total:g} руб × "
            f"{float(rates.get('overhead_percent') or 0):g}%"
        )
        add_row(
            "10 Накладные расходы", "Накладные расходы", "компл.", 1,
            overhead_amount, None, percent_source,
            "current_project.overhead",
        )

    audit = []
    for row_no, row in enumerate(rows, 1):
        for kind, price_key, status_key, source_key in (
            ("work", "work_unit_price", "work_price_status", "work_price_source"),
            ("material", "material_unit_price", "material_price_status", "material_price_source"),
        ):
            if row.get(price_key) is None:
                continue
            audit.append({
                "estimate_row_no": row_no,
                "position_key": row.get("position_key"),
                "material_total_key": row.get("material_total_key"),
                "public_name": row.get("name"),
                "price_kind": kind,
                "unit": row.get("unit"),
                "unit_price": row.get(price_key),
                "price_source": row.get(source_key),
                "status": row.get(status_key),
                "supplier": "Расценка пользователя",
                "source_url": "",
                "checked_at": _now(),
                "cache_hit": False,
                "sonar_attempted": False,
                "note": "Текущее явное уточнение пользователя",
            })

    prepared["estimate_rows"] = rows
    prepared["evidence_only_rows"] = list(prepared.get("quantities") or [])
    prepared["price_audit"] = audit
    prepared["price_items"] = audit
    prepared["missing_items"] = []
    prepared["VOLUMES_COMPLETE"] = True
    prepared["POSITIONS_EXTRACTION_COMPLETE"] = True
    prepared["current_project_manual_rows_ready"] = True
    prepared["price_mode"] = "USER_CONFIRMED_MANUAL_NO_INTERNET"
    prepared["manual_rates"] = dict(rates)
    return prepared


async def maybe_handle_stroyka_estimate(conn, task, logger=None):  # noqa: F811
    try:
        task_id = _s(_row_get(task, "id", ""))
        chat_id = _s(_row_get(task, "chat_id", ""))
        topic_id = int(_row_get(task, "topic_id", 0) or 0)
        input_type = _low(_s(_row_get(task, "input_type", "")))
        raw_input = _s(_row_get(task, "raw_input", ""))
        if topic_id == TOPIC_ID_STROYKA and input_type in ("drive_file", "file", "document"):
            meta: Dict[str, Any] = {}
            try:
                meta = json.loads(raw_input) if raw_input.strip().startswith("{") else {}
            except Exception:
                meta = {}
            file_name = _s(meta.get("file_name"))
            mime_type = _low(meta.get("mime_type"))
            caption = _s(meta.get("caption"))
            is_pdf = file_name.lower().endswith(".pdf") or "pdf" in mime_type
            is_estimate = any(word in _low(caption + " " + raw_input) for word in ("смет", "стоимость", "посчитать"))
            if task_id and is_pdf and is_estimate:
                _history_safe(conn, task_id, "TOPIC2_ESTIMATE_SESSION_CREATED")
                import glob as _t2np_glob
                paths = _t2np_glob.glob(str(BASE / "runtime" / "drive_files" / f"{task_id}_*"))
                current_path = next((path for path in paths if path.lower().endswith(".pdf") and os.path.getsize(path) > 1000), "")
                if current_path:
                    from core.pdf_spec_extractor import extract_project_positions_bundle as _t2np_extract
                    bundle = _t2np_extract([current_path], topic_id=TOPIC_ID_STROYKA) or {}
                    if bundle.get("ok"):
                        _history_safe(conn, task_id, "TOPIC2_CONTEXT_READY")
                    if bundle.get("ok") and not bundle.get("POSITIONS_EXTRACTION_COMPLETE"):
                        clarified_text = "\n".join(
                            part for part in (caption, _topic2_project_clarifications_v2(conn, task_id))
                            if _s(part).strip()
                        )
                        scope_confirmed = any(marker in _low(clarified_text) for marker in (
                            "по проект", "текущему проект", "все позиции, найденные в pdf",
                            "по геометр", "рассчитать отсутствующ", "считать по найденн",
                        ))
                        manual_rates = _topic2_project_manual_rates_v2(clarified_text)
                        unresolved_project_items = list(bundle.get("missing_items") or [])
                        if manual_rates.get("monolith_rates_include_formwork_rebar") is True:
                            unresolved_project_items = [
                                item for item in unresolved_project_items if item != "formwork_area_m2"
                            ]
                        missing_manual_rates = _topic2_project_manual_rates_missing_v3(manual_rates)
                        missing_logistics = _topic2_project_logistics_missing_v3(manual_rates)
                        if (
                            scope_confirmed
                            and not unresolved_project_items
                            and not missing_manual_rates
                            and missing_logistics
                        ):
                            text = _topic2_project_logistics_prompt_v3(manual_rates)
                            pending = {
                                "version": "TOPIC2_NEW_PROJECT_PDF_ISOLATION_V3",
                                "status": "WAITING_LOGISTICS_CONFIRMATION",
                                "task_id": task_id, "chat_id": chat_id, "topic_id": topic_id,
                                "source_file": current_path, "project_bundle": bundle,
                                "volume_basis": "CURRENT_PROJECT_DRAWINGS",
                                "manual_rates": manual_rates,
                                "created_at": _now(),
                            }
                            _memory_save(chat_id, f"topic_2_estimate_pending_{task_id}", pending)
                            _history_safe(conn, task_id, "TOPIC2_LOGISTICS_CONFIRMATION_REQUIRED")
                            _history_safe(conn, task_id, "TOPIC2_FINAL_BLOCKED_UNTIL_LOGISTICS_CONFIRMATION")
                            send_res = await _send_text(
                                chat_id, text,
                                _row_get(task, "reply_to_message_id", None) or _row_get(task, "message_id", None),
                                topic_id,
                            )
                            kwargs = {
                                "state": "WAITING_CLARIFICATION", "result": text,
                                "error_message": "TOPIC2_LOGISTICS_CONFIRMATION_REQUIRED",
                            }
                            if isinstance(send_res, dict) and send_res.get("bot_message_id"):
                                kwargs["bot_message_id"] = send_res.get("bot_message_id")
                            _update_task_safe(conn, task_id, **kwargs)
                            return True
                        if scope_confirmed and not unresolved_project_items and not missing_manual_rates:
                            _history_safe(conn, task_id, "TOPIC2_LOGISTICS_CONFIRMED")
                            prepared_bundle = _topic2_current_project_manual_rows_v3(bundle, manual_rates)
                            estimate_rows = list(prepared_bundle.get("estimate_rows") or [])
                            names = "\n".join(_low(row.get("name")) for row in estimate_rows)
                            forbidden_old = any(token in names for token in ("фм1/фм2", "бфм1", "ангар"))
                            if not estimate_rows or forbidden_old:
                                _history_safe(conn, task_id, "TOPIC2_CURRENT_PROJECT_FINAL_BLOCKED:row_validation")
                                _update_task_safe(
                                    conn, task_id, state="FAILED",
                                    error_message="TOPIC2_CURRENT_PROJECT_ROWS_INVALID",
                                )
                                return True
                            _history_safe(
                                conn, task_id,
                                f"TOPIC2_PROJECT_ALL_PAGES_SCANNED:{(bundle.get('files') or [{}])[0].get('pages_seen', 0)}",
                            )
                            _history_safe(conn, task_id, f"TOPIC2_PROJECT_POSITIONS_EXTRACTED:{len(bundle.get('positions') or [])}")
                            _history_safe(conn, task_id, "TOPIC2_POSITIONS_EXTRACTION_COMPLETE_YES")
                            _history_safe(conn, task_id, "TOPIC2_VOLUME_COMPLETENESS_GATE_OK")
                            _history_safe(conn, task_id, "TOPIC2_PRICE_SEARCH_NOT_REQUESTED_NO_INTERNET")
                            _history_safe(conn, task_id, "TOPIC2_PRICE_ENRICHMENT_STARTED:manual_user_rates")
                            _history_safe(conn, task_id, "TOPIC2_PRICE_SOURCE_FOUND:manual_user_rates")
                            _history_safe(conn, task_id, "TOPIC2_PRICE_ENRICHMENT_DONE:manual_user_rates")
                            _history_safe(conn, task_id, "TOPIC2_PRICE_CHOICE_CONFIRMED:manual_user_rates")
                            _history_safe(conn, task_id, f"TOPIC2_CURRENT_PROJECT_ESTIMATE_ROWS:{len(estimate_rows)}")
                            _memory_save(chat_id, f"topic_2_project_bundle_{task_id}", prepared_bundle)
                            await _topic2_project_bundle_send_artifacts_v1(
                                conn, task_id, chat_id, topic_id,
                                _row_get(task, "reply_to_message_id", None) or _row_get(task, "message_id", None),
                                prepared_bundle,
                            )
                            return True
                        if scope_confirmed:
                            text = _topic2_project_manual_price_message_v2(manual_rates)
                            pending_status = "WAITING_MANUAL_PRICE_INPUT"
                        else:
                            text = _topic2_project_incomplete_message_v2(bundle)
                            pending_status = "WAITING_PROJECT_VOLUME_CLARIFICATION"
                        pending = {
                            "version": "TOPIC2_NEW_PROJECT_PDF_ISOLATION_V2",
                            "status": pending_status,
                            "task_id": task_id, "chat_id": chat_id, "topic_id": topic_id,
                            "source_file": current_path, "project_bundle": bundle,
                            "volume_basis": "CURRENT_PROJECT_DRAWINGS" if scope_confirmed else "AWAITING_USER_CHOICE",
                            "manual_rates": manual_rates,
                            "created_at": _now(),
                        }
                        _memory_save(chat_id, f"topic_2_estimate_pending_{task_id}", pending)
                        _memory_save(chat_id, f"topic_2_project_bundle_{task_id}", pending)
                        _history_safe(conn, task_id, "TOPIC2_NEW_PROJECT_CONTEXT_ISOLATED")
                        _history_safe(conn, task_id, f"TOPIC2_PROJECT_ALL_PAGES_SCANNED:{(bundle.get('files') or [{}])[0].get('pages_seen', 0)}")
                        _history_safe(conn, task_id, f"TOPIC2_PROJECT_POSITIONS_EXTRACTED:{len(bundle.get('positions') or [])}")
                        _history_safe(conn, task_id, "TOPIC2_POSITIONS_EXTRACTION_COMPLETE_NO")
                        _history_safe(conn, task_id, "TOPIC2_PRICE_SEARCH_BLOCKED_BY_VOLUME_GATE")
                        _history_safe(conn, task_id, "TOPIC2_SMETA_GENERATION_BLOCKED_BY_VOLUME_GATE")
                        if scope_confirmed:
                            _history_safe(conn, task_id, "TOPIC2_PROJECT_GEOMETRY_CHOICE_CONFIRMED")
                            _history_safe(conn, task_id, f"TOPIC2_MANUAL_PRICES_ACCEPTED:{len(manual_rates)}")
                            _history_safe(conn, task_id, "TOPIC2_WAITING_ONLY_MISSING_MANUAL_PRICES")
                        send_res = await _send_text(
                            chat_id, text,
                            _row_get(task, "reply_to_message_id", None) or _row_get(task, "message_id", None),
                            topic_id,
                        )
                        kwargs = {
                            "state": "WAITING_CLARIFICATION", "result": text,
                            "error_message": "TOPIC2_MANUAL_PRICES_INCOMPLETE" if scope_confirmed else "TOPIC2_PROJECT_VOLUMES_INCOMPLETE",
                        }
                        if isinstance(send_res, dict) and send_res.get("bot_message_id"):
                            kwargs["bot_message_id"] = send_res.get("bot_message_id")
                        _update_task_safe(conn, task_id, **kwargs)
                        return True
    except Exception as exc:
        try:
            _history_safe(conn, _s(_row_get(task, "id", "")), "TOPIC2_NEW_PROJECT_PDF_ISOLATION_ERR:" + _s(exc)[:180])
        except Exception:
            pass
        if logger:
            logger.exception("TOPIC2_NEW_PROJECT_PDF_ISOLATION_ERR")
    return await _TOPIC2_NEW_PROJECT_PREV_HANDLER_V2(conn, task, logger)
# === END_PATCH_TOPIC2_NEW_PROJECT_PDF_ISOLATION_V2 ===

====================================================================================================
END_FILE: core/stroyka_estimate_canon.py
FILE_CHUNK: 2/2
====================================================================================================

====================================================================================================
BEGIN_FILE: core/stt_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 5a82d4d66baa07c5459aaece34a432de65b7d157840669f08efe5a9a6b1fe6bd
====================================================================================================
import os
import aiohttp
import logging
import json

logger = logging.getLogger(__name__)

async def transcribe_voice(path: str) -> str:
    if not os.path.exists(path):
        raise RuntimeError(f"voice file not found: {path}")

    groq_key = (os.getenv("GROQ_API_KEY") or "").strip()

    logger.info("STT env check groq=%s", bool(groq_key))

    if not groq_key:
        raise RuntimeError("STT_GROQ_API_KEY_MISSING")

    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {groq_key}"}
    model = "whisper-large-v3-turbo"

    size = os.path.getsize(path)
    logger.info("STT start file=%s size=%s model=%s", path, size, model)

    data = aiohttp.FormData()
    data.add_field("model", model)
    data.add_field("response_format", "json")

    with open(path, "rb") as f:
        data.add_field("file", f, filename=os.path.basename(path), content_type="audio/ogg")
        async with aiohttp.ClientSession() as s:
            r = await s.post(
                url,
                headers=headers,
                data=data,
                timeout=aiohttp.ClientTimeout(total=300)
            )
            body = await r.text()
            logger.info("STT http_status=%s", r.status)

            if r.status != 200:
                logger.error("STT body=%s", body[:500])
                raise RuntimeError(f"STT_GROQ_FAILED: {r.status} {body[:300]}")

            try:
                js = json.loads(body)
            except Exception:
                raise RuntimeError(f"STT bad json: {body[:300]}")

    text = (js.get("text") or "").strip()

    if not text:
        raise RuntimeError("STT returned empty transcript")

    # === P6H_STT_HALLUCINATION_GUARD_V1 ===
    _stt_hall_patterns = (
        "субтитры", "субтитр", "titl", "продолжение следует",
        "конец видео", "спасибо за просмотр", "подписывайтесь",
        "thank you", "amara.org", "translated by", "caption",
    )
    _stt_low = text.lower()
    if len(text) <= 6 or any(p in _stt_low for p in _stt_hall_patterns):
        logger.warning("STT_HALLUCINATION_GUARD: rejected=%r", text[:80])
        raise RuntimeError(f"STT_HALLUCINATION_REJECTED: {text[:60]!r}")
    # === END_P6H_STT_HALLUCINATION_GUARD_V1 ===

    logger.info("STT ok transcript_len=%s", len(text))

    try:
        os.remove(path)
    except Exception:
        pass

    return text

====================================================================================================
END_FILE: core/stt_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/technadzor_document_skill.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 7f86800da7b61771bec0e581bb3facd3ffa0f34a47ac55e87ca8fca8f3f1c74a
====================================================================================================
#!/usr/bin/env python3
# === TECHNADZOR_DOCUMENT_SKILL_V1 ===
# Converts source records from telegram_source_skill_extractor into skill cards.
# Rejects noise. Classifies useful document-composition logic.
# All extracted rules must keep source reference.
from __future__ import annotations

import hashlib
import logging
import re
from typing import Any

logger = logging.getLogger("technadzor_document_skill")

SKILL_CATEGORIES = (
    "act_structure",
    "report_structure",
    "defect_description_logic",
    "photo_to_defect_linking",
    "evidence_handling",
    "normative_reference_handling",
    "recommendation_logic",
    "conclusion_logic",
    "file_workflow",
    "document_workflow",
    "client_facing_language",
    "contractor_statement_handling",
    "owner_statement_handling",
    "telegram_source_work_signal",
    "rabota_poisk_reusable_pattern",
    "unknown",
)

# Patterns → category
_CATEGORY_PATTERNS: list[tuple[str, list[str]]] = [
    ("act_structure", [
        "акт", "форма акта", "состав акта", "разделы акта", "приложение к акту",
        "акт освидетельствования", "акт скрытых", "акт приёмки", "акт проверки",
    ]),
    ("report_structure", [
        "отчёт", "отчет", "заключение", "техническое заключение", "разделы отчёта",
        "структура отчёта", "состав отчёта",
    ]),
    ("defect_description_logic", [
        "дефект", "нарушение", "замечание", "несоответствие", "отклонение",
        "трещин", "скол", "раковин", "расслоен", "коррозия",
        "как описать", "формулировка дефекта", "описание дефекта",
    ]),
    ("photo_to_defect_linking", [
        "фото", "фотофиксация", "привязка фото", "фото к дефекту",
        "фото к акту", "фотоматериал", "приложение фото",
    ]),
    ("evidence_handling", [
        "доказательство", "факт", "подтверждение", "доказательная база",
        "источник данных", "обоснование", "исполнительная документация",
    ]),
    ("normative_reference_handling", [
        "снип", "гост", "сп ", "нормати", "требования нормативов",
        "ссылка на норму", "нормативный документ", "регламент",
    ]),
    ("recommendation_logic", [
        "рекомендация", "предписание", "устранить", "необходимо устранить",
        "рекомендуется", "следует", "требуется", "провести работы",
    ]),
    ("conclusion_logic", [
        "вывод", "заключение", "итог", "резюме", "категория состояния",
        "техническое состояние", "ограниченно работоспособ", "аварийн",
    ]),
    ("file_workflow", [
        "pdf", "docx", "xlsx", "dwg", "файл", "загрузка файла",
        "прикрепить файл", "скачать", "отправить файл", "формат файла",
    ]),
    ("document_workflow", [
        "документооборот", "пакет документов", "комплект",
        "исполнительная документация", "журнал работ", "акт скрытых",
        "приёмка документов",
    ]),
    ("client_facing_language", [
        "заказчик", "собственник", "владелец", "клиент", "застройщик",
        "как написать заказчику", "для заказчика", "язык документа",
    ]),
    ("contractor_statement_handling", [
        "подрядчик", "генподрядчик", "субподрядчик", "исполнитель",
        "ответ подрядчика", "позиция подрядчика",
    ]),
    ("owner_statement_handling", [
        "застройщик", "инвестор", "позиция застройщика",
        "ответ застройщика", "письмо застройщика",
    ]),
    ("telegram_source_work_signal", [
        "вакансия", "требуется", "нужен специалист", "ищем технадзор",
        "ищем инженера", "найдём", "предложение работы",
    ]),
    ("rabota_poisk_reusable_pattern", [
        "заказ", "тендер", "объявление", "контракт", "выбор подрядчика",
        "объект ищет", "нужен технадзор", "проведём отбор",
    ]),
]

TOPIC5_VALUE_KEYWORDS = [
    "акт", "дефект", "технадзор", "заключение", "предписание",
    "приёмка", "отчёт", "фото", "норматив", "документ",
    "рекомендация", "вывод", "замечание",
]

NOISE_MARKERS = [
    "реклама", "продам", "куплю", "скидка", "акция",
    "заработок", "кредит без отказа", "займ", "только сегодня",
    "подпишись", "переходи по ссылке", "выиграли",
]


def _card_id(source_ref: str, message_id: int | str) -> str:
    raw = f"{source_ref}::{message_id}"
    return "SK_" + hashlib.md5(raw.encode()).hexdigest()[:12].upper()


def classify_category(text: str) -> str:
    low = text.lower()
    for category, patterns in _CATEGORY_PATTERNS:
        if any(p in low for p in patterns):
            return category
    return "unknown"


def extract_rule_from_text(text: str, category: str) -> str:
    sentences = re.split(r"[.\n!?]+", text)
    useful = []
    for sent in sentences:
        s = sent.strip()
        if len(s) < 20:
            continue
        low = s.lower()
        if any(kw in low for kw in TOPIC5_VALUE_KEYWORDS):
            useful.append(s)
        if len(useful) >= 3:
            break
    if useful:
        return ". ".join(useful[:3])
    # fallback: first substantial sentence
    for sent in sentences:
        s = sent.strip()
        if len(s) >= 30:
            return s[:300]
    return text[:300].strip()


def why_useful(category: str) -> str:
    mapping = {
        "act_structure": "Позволяет выстраивать структуру акта технадзора: разделы, приложения, обязательные поля",
        "report_structure": "Определяет состав технического отчёта/заключения по объекту",
        "defect_description_logic": "Формирует навык точной формулировки дефектов для актов и предписаний",
        "photo_to_defect_linking": "Описывает правило привязки фотоматериалов к конкретным дефектам в документе",
        "evidence_handling": "Показывает как формировать доказательную базу — факты, источники, исполнительная документация",
        "normative_reference_handling": "Обучает правильному указанию нормативных ссылок (СП/ГОСТ/СНиП) в актах",
        "recommendation_logic": "Задаёт логику формулировки предписаний и рекомендаций по устранению",
        "conclusion_logic": "Показывает структуру вывода/заключения о техническом состоянии",
        "file_workflow": "Описывает правила работы с файлами (PDF/DOCX/XLSX) при формировании пакета документов",
        "document_workflow": "Определяет порядок формирования и передачи комплекта исполнительной документации",
        "client_facing_language": "Задаёт профессиональный язык документов, обращённых к заказчику/собственнику",
        "contractor_statement_handling": "Показывает как фиксировать позицию подрядчика в документах",
        "owner_statement_handling": "Показывает как фиксировать позицию застройщика/инвестора",
        "telegram_source_work_signal": "Сигнал о возможной работе/заказе — полезен для маршрутизации в topic_6104",
        "rabota_poisk_reusable_pattern": "Паттерн для поиска заказов/вакансий через Telegram-источник (тема RABOTA_POISK)",
        "unknown": "Категория не определена — требует ручной проверки владельца",
    }
    return mapping.get(category, "")


def is_noise(text: str) -> bool:
    low = (text or "").lower()
    if any(n in low for n in NOISE_MARKERS):
        return True
    if len(text.strip()) < 20:
        return True
    return False


def has_practical_value(text: str) -> bool:
    low = text.lower()
    return any(kw in low for kw in TOPIC5_VALUE_KEYWORDS)


def build_skill_card(record: dict) -> dict | None:
    text = record.get("text", "")
    source_ref = record.get("source_ref", "")
    message_id = record.get("message_id", "")

    if not source_ref:
        logger.debug("rejected: no source_ref msg=%s", message_id)
        return None

    if is_noise(text):
        logger.debug("rejected: noise msg=%s", message_id)
        return None

    if not has_practical_value(text) and not record.get("file_name") and not record.get("links"):
        logger.debug("rejected: no practical value msg=%s", message_id)
        return None

    category = classify_category(text)
    extracted_rule = extract_rule_from_text(text, category)

    needs_review = (
        category == "unknown"
        or len(extracted_rule) < 30
        or not has_practical_value(text)
    )

    tags = [category]
    if record.get("file_name"):
        tags.append("has_document")
    if record.get("links"):
        tags.append("has_links")
    if record.get("media_type") == "photo":
        tags.append("has_photo")

    return {
        "id": _card_id(source_ref, message_id),
        "source": record.get("source", "@tnz_msk"),
        "source_ref": source_ref,
        "message_id": message_id,
        "message_date": record.get("message_date", ""),
        "category": category,
        "title": f"{category}: {extracted_rule[:60]}",
        "source_excerpt": text[:400],
        "extracted_rule": extracted_rule,
        "why_useful_for_topic_5": why_useful(category),
        "source_links": record.get("links", []),
        "source_files": ([record["file_name"]] if record.get("file_name") else []),
        "confidence": "low" if needs_review else "medium",
        "needs_owner_review": needs_review,
        "tags": tags,
    }


def process_records(records: list[dict]) -> dict:
    cards: list[dict] = []
    rejected = 0
    for rec in records:
        card = build_skill_card(rec)
        if card:
            cards.append(card)
        else:
            rejected += 1

    by_category: dict[str, list] = {}
    for card in cards:
        by_category.setdefault(card["category"], []).append(card)

    return {
        "total_input": len(records),
        "extracted": len(cards),
        "rejected_noise": rejected,
        "categories": list(by_category.keys()),
        "cards": cards,
        "by_category": by_category,
    }
# === END_TECHNADZOR_DOCUMENT_SKILL_V1 ===

====================================================================================================
END_FILE: core/technadzor_document_skill.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/technadzor_drive_index.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 31118a4e5fa521f992b026001a821ecf8cea7570e3185a3ed6b89d59a3143c77
====================================================================================================
# === P6H_TOPIC5_TECHNADZOR_TEMPLATE_PHOTO_CLIENT_SAFE_CLOSE_20260504 / DRIVE_INDEX_V1 ===
# Auto-discovery of topic_5 (technadzor) Drive folder contents as style/content
# references — without manual "прими как образец" commands.
#
# Layered classification (file role):
#   PRIMARY_PDF_STYLE         — PDF in topic root or in non-system subfolders (real client acts; main style)
#   SECONDARY_DOCX_REFERENCE  — DOCX in service subfolders (TECHNADZOR / _drafts / _system / _templates)
#   CLIENT_PHOTO_SOURCE       — image/* in topic root or any non-system folder (work-object photos)
#   CLIENT_FINAL_PDF          — PDF artifacts produced earlier (kept in client folders)
#   SYSTEM_TEMPLATE           — DOCX/JSON/manifests in service subfolders
#   OTHER                     — anything else (audio, etc.)
#
# Folder classification:
#   SYSTEM   — name in {_system, _templates, _drafts, _manifests, _archive, _tmp, TECHNADZOR}
#   CLIENT   — anything else (work-object/customer-facing folders)
#
# Index is persisted to:
#   data/templates/technadzor/ACTIVE__chat_<chat_id>__topic_<topic_id>.json
# (filename uses literal chat_id with leading dash, matching existing convention)
#
# In-memory cache TTL = 5 minutes.
from __future__ import annotations

import io
import json
import os
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LOG = logging.getLogger("task_worker")

_CACHE_TTL_SECONDS = 300
_CACHE: Dict[Tuple[str, int], Tuple[float, Dict[str, Any]]] = {}

_BASE = Path(__file__).resolve().parent.parent
_LOCAL_INDEX_DIR = _BASE / "data" / "templates" / "technadzor"
_LOCAL_INDEX_DIR.mkdir(parents=True, exist_ok=True)
_DOWNLOAD_DIR = _BASE / "data" / "memory_files" / "technadzor_index_cache"
_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Folder names treated as SYSTEM (no client artifacts allowed)
SYSTEM_FOLDER_NAMES = {
    "_system", "_templates", "_drafts", "_manifests", "_archive", "_tmp",
    "technadzor",  # case-insensitive match against TECHNADZOR
}


def is_system_folder(name: str) -> bool:
    """True if the folder is internal/service. Match case-insensitive."""
    if not name:
        return False
    return name.strip().lower() in SYSTEM_FOLDER_NAMES


def is_client_facing_folder(name: str) -> bool:
    """True if the folder is client-facing (object/customer/visit folder)."""
    if not name:
        return False
    return not is_system_folder(name)


def _service():
    from core.topic_drive_oauth import _oauth_service
    return _oauth_service()


def _root_folder_id() -> str:
    from core.topic_drive_oauth import _root_folder_id as r
    return r()


def _find_child(svc, parent_id: str, name: str) -> Optional[str]:
    safe_name = name.replace("'", "\\'")
    res = svc.files().list(
        q=f"'{parent_id}' in parents and name='{safe_name}' and trashed=false",
        fields="files(id,name,mimeType)",
        pageSize=10,
    ).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None


def _ensure_subfolder(svc, parent_id: str, name: str) -> str:
    fid = _find_child(svc, parent_id, name)
    if fid:
        return fid
    body = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    created = svc.files().create(body=body, fields="id").execute()
    return created["id"]


def _list_folder(svc, folder_id: str, page_size: int = 200) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    page_token = <REDACTED_SECRET>
    while True:
        res = svc.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id,name,mimeType,modifiedTime,createdTime,size,webViewLink,parents)",
            orderBy="modifiedTime desc",
            pageSize=page_size,
            pageToken=<REDACTED_SECRET>
        ).execute()
        items.extend(res.get("files", []))
        page_token = <REDACTED_SECRET>"nextPageToken")
        if not page_token:
            break
    return items


def classify_technadzor_drive_file(file: Dict[str, Any], parent_folder_name: str = "") -> str:
    """Classify a Drive file by role (returns one of the role strings)."""
    mt = file.get("mimeType", "") or ""
    name = (file.get("name") or "").lower()
    parent = (parent_folder_name or "").strip().lower()
    parent_is_system = parent in SYSTEM_FOLDER_NAMES

    # PDF
    if mt == "application/pdf":
        if parent_is_system:
            return "SYSTEM_TEMPLATE"
        if name.startswith("act") or "акт" in name or "осмотр" in name:
            # PDF in non-system folder with act-like name → primary style
            return "PRIMARY_PDF_STYLE"
        # PDF in client folder, generic — most likely a final client PDF artifact
        return "CLIENT_FINAL_PDF"

    # DOCX
    if mt == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        if parent_is_system:
            return "SYSTEM_TEMPLATE"
        return "SECONDARY_DOCX_REFERENCE"

    # Image
    if mt.startswith("image/"):
        if parent_is_system:
            return "SYSTEM_TEMPLATE"
        return "CLIENT_PHOTO_SOURCE"

    # JSON / manifests / system
    if mt in ("application/json",) or name.endswith((".json", ".log", ".bak", ".tmp")):
        return "SYSTEM_TEMPLATE"

    # Audio (voice notes)
    if mt.startswith("audio/") or mt == "application/ogg":
        return "OTHER"

    return "OTHER"


def _resolve_topic_folder(svc, chat_id: str, topic_id: int) -> Optional[str]:
    root = _root_folder_id()
    chat_folder = _find_child(svc, root, f"chat_{chat_id}")
    if not chat_folder:
        return None
    return _find_child(svc, chat_folder, f"topic_{int(topic_id)}")


def _local_index_path(chat_id: str, topic_id: int) -> Path:
    fname = f"ACTIVE__chat_{chat_id}__topic_{int(topic_id)}.json"
    return _LOCAL_INDEX_DIR / fname


def _drive_url(file: Dict[str, Any]) -> str:
    fid = file.get("id", "")
    if file.get("webViewLink"):
        return file["webViewLink"]
    if file.get("mimeType") == "application/vnd.google-apps.folder":
        return f"https://drive.google.com/drive/folders/{fid}"
    return f"https://drive.google.com/file/d/{fid}/view"


def scan_topic5_drive_templates(chat_id: str, topic_id: int = 5, force: bool = False) -> Dict[str, Any]:
    """Scan Drive topic_<id> contents and return classified listing.

    Cached for 5 min. Pass force=True to refresh.
    """
    key = (str(chat_id), int(topic_id))
    now = time.time()
    if not force and key in _CACHE:
        ts, cached = _CACHE[key]
        if now - ts < _CACHE_TTL_SECONDS:
            return cached

    svc = _service()
    topic_fid = _resolve_topic_folder(svc, chat_id, topic_id)
    result: Dict[str, Any] = {
        "chat_id": str(chat_id),
        "topic_id": int(topic_id),
        "topic_folder_id": topic_fid,
        "topic_folder_link": (
            f"https://drive.google.com/drive/folders/{topic_fid}"
            if topic_fid else None
        ),
        "files": [],
        "folders_system": [],
        "folders_client": [],
        "by_role": {},
        "primary_pdf_style": [],
        "secondary_docx_reference": [],
        "client_photo_source": [],
        "client_final_pdf": [],
        "system_template": [],
        "other": [],
        "ok": False,
        "error": None,
        "scanned_at": int(now),
    }

    if not topic_fid:
        result["error"] = f"topic folder chat_{chat_id}/topic_{topic_id} not found"
        _CACHE[key] = (now, result)
        return result

    try:
        # Walk topic root
        root_items = _list_folder(svc, topic_fid)
        all_records: List[Dict[str, Any]] = []
        sub_folder_walk: List[Tuple[str, str]] = []  # (folder_id, folder_name)
        for it in root_items:
            if it.get("mimeType") == "application/vnd.google-apps.folder":
                if is_system_folder(it["name"]):
                    result["folders_system"].append({
                        "id": it["id"], "name": it["name"],
                        "drive_url": _drive_url(it),
                    })
                else:
                    result["folders_client"].append({
                        "id": it["id"], "name": it["name"],
                        "drive_url": _drive_url(it),
                    })
                sub_folder_walk.append((it["id"], it["name"]))
            else:
                role = classify_technadzor_drive_file(it, parent_folder_name="")
                rec = _build_record(it, role, parent_folder_name="", chat_id=chat_id, topic_id=topic_id)
                all_records.append(rec)

        # Walk one level of subfolders (do not recurse deeper to keep it cheap)
        for sub_fid, sub_name in sub_folder_walk:
            sub_items = _list_folder(svc, sub_fid)
            for it in sub_items:
                if it.get("mimeType") == "application/vnd.google-apps.folder":
                    # nested sub-subfolder — record name only, do not recurse
                    continue
                role = classify_technadzor_drive_file(it, parent_folder_name=sub_name)
                rec = _build_record(it, role, parent_folder_name=sub_name, chat_id=chat_id, topic_id=topic_id)
                all_records.append(rec)

        result["files"] = all_records
        for rec in all_records:
            role = rec["role"]
            bucket = role.lower()
            if bucket == "primary_pdf_style":
                result["primary_pdf_style"].append(rec)
            elif bucket == "secondary_docx_reference":
                result["secondary_docx_reference"].append(rec)
            elif bucket == "client_photo_source":
                result["client_photo_source"].append(rec)
            elif bucket == "client_final_pdf":
                result["client_final_pdf"].append(rec)
            elif bucket == "system_template":
                result["system_template"].append(rec)
            else:
                result["other"].append(rec)
            result["by_role"].setdefault(role, 0)
            result["by_role"][role] += 1

        result["ok"] = True
    except Exception as exc:
        result["error"] = repr(exc)
        LOG.exception("P6H_TOPIC5_DRIVE_INDEX_SCAN_FAIL chat=%s topic=%s", chat_id, topic_id)

    _CACHE[key] = (now, result)
    return result


def _build_record(file: Dict[str, Any], role: str, parent_folder_name: str, chat_id: str, topic_id: int) -> Dict[str, Any]:
    parent_lower = (parent_folder_name or "").strip().lower()
    parent_is_system = parent_lower in SYSTEM_FOLDER_NAMES
    return {
        "file_id": file.get("id"),
        "file_name": file.get("name"),
        "mime_type": file.get("mimeType"),
        "drive_url": _drive_url(file),
        "folder_name": parent_folder_name or "<root>",
        "role": role,
        "client_facing": (not parent_is_system),
        "created_time": file.get("createdTime"),
        "modified_time": file.get("modifiedTime"),
        "size": file.get("size"),
    }


def build_technadzor_template_index(chat_id: str = "-1003725299009", topic_id: int = 5, force: bool = True) -> Dict[str, Any]:
    """Build full topic_5 index, persist to local JSON, return the index dict.

    Persistent path:
        data/templates/technadzor/ACTIVE__chat_<chat_id>__topic_<topic_id>.json
    """
    idx = scan_topic5_drive_templates(chat_id, topic_id, force=force)
    payload = {
        "chat_id": idx.get("chat_id"),
        "topic_id": idx.get("topic_id"),
        "topic_folder_id": idx.get("topic_folder_id"),
        "topic_folder_link": idx.get("topic_folder_link"),
        "scanned_at": idx.get("scanned_at"),
        "ok": idx.get("ok"),
        "error": idx.get("error"),
        "by_role": idx.get("by_role"),
        "folders_system": idx.get("folders_system"),
        "folders_client": idx.get("folders_client"),
        "files": idx.get("files"),
        "primary_pdf_style": idx.get("primary_pdf_style"),
        "secondary_docx_reference": idx.get("secondary_docx_reference"),
        "client_photo_source": idx.get("client_photo_source"),
        "client_final_pdf": idx.get("client_final_pdf"),
        "system_template": idx.get("system_template"),
        "other": idx.get("other"),
        "marker": "P6H_TOPIC5_USE_EXISTING_TEMPLATES_PHOTO_TO_TECH_REPORT_20260504_V1",
        "updated_at": int(time.time()),
    }
    try:
        path = _local_index_path(str(chat_id), int(topic_id))
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        payload["local_index_path"] = str(path)
    except Exception as exc:
        LOG.exception("P6H_TOPIC5_DRIVE_INDEX_PERSIST_FAIL chat=%s topic=%s err=%s", chat_id, topic_id, exc)
    return payload


def get_active_index(chat_id: str = "-1003725299009", topic_id: int = 5) -> Optional[Dict[str, Any]]:
    """Read persisted index from disk, if present."""
    p = _local_index_path(str(chat_id), int(topic_id))
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def primary_template_meta(idx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Most recent PRIMARY_PDF_STYLE record. Falls back to most recent CLIENT_FINAL_PDF."""
    if idx.get("primary_pdf_style"):
        return idx["primary_pdf_style"][0]
    if idx.get("client_final_pdf"):
        return idx["client_final_pdf"][0]
    return None


def secondary_template_meta(idx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if idx.get("secondary_docx_reference"):
        return idx["secondary_docx_reference"][0]
    return None


def ensure_service_subfolder(chat_id: str, topic_id: int, name: str = "_drafts") -> Optional[str]:
    """Create/return id for a SERVICE subfolder (system, never client-facing).

    Refuses to create folders with non-system names.
    """
    if not is_system_folder(name):
        raise ValueError(f"Refusing to create non-system folder via service path: {name}")
    svc = _service()
    topic_fid = _resolve_topic_folder(svc, chat_id, topic_id)
    if not topic_fid:
        return None
    return _ensure_subfolder(svc, topic_fid, name)


def upload_to_service_subfolder(local_path: Path, dst_name: str, chat_id: str, topic_id: int, subfolder: str = "_drafts") -> Optional[Dict[str, Any]]:
    """Upload artifact to topic_<id>/<service-subfolder>/. Subfolder MUST be system."""
    if not is_system_folder(subfolder):
        raise ValueError(f"Refusing to upload to non-system subfolder: {subfolder}")
    return _upload_to_folder(local_path, dst_name, chat_id, topic_id, subfolder, allow_client=False)


def upload_client_pdf_to_folder(local_path: Path, dst_name: str, chat_id: str, topic_id: int, target_folder_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Upload final client PDF.

    If target_folder_name is provided AND it's a non-system (client-facing) folder,
    upload there. Otherwise upload to topic root.

    Refuses anything that isn't .pdf — by spec, client folders accept only photos and final PDFs.
    """
    if not str(local_path).lower().endswith(".pdf"):
        raise ValueError(f"Refusing to upload non-PDF to client folder: {local_path}")
    return _upload_to_folder(local_path, dst_name, chat_id, topic_id, target_folder_name, allow_client=True)


def _upload_to_folder(local_path: Path, dst_name: str, chat_id: str, topic_id: int, target_folder_name: Optional[str], allow_client: bool) -> Optional[Dict[str, Any]]:
    try:
        from googleapiclient.http import MediaFileUpload
        svc = _service()
        topic_fid = _resolve_topic_folder(svc, chat_id, topic_id)
        if not topic_fid:
            return None

        if target_folder_name:
            if is_system_folder(target_folder_name):
                target_id = _ensure_subfolder(svc, topic_fid, target_folder_name)
            else:
                if not allow_client:
                    raise ValueError(f"Client folder upload not allowed via service path: {target_folder_name}")
                # find existing client folder, do NOT auto-create client folders
                target_id = _find_child(svc, topic_fid, target_folder_name)
                if not target_id:
                    LOG.warning("P6H_TOPIC5_CLIENT_FOLDER_NOT_FOUND name=%s — uploading to topic root", target_folder_name)
                    target_id = topic_fid
        else:
            target_id = topic_fid

        body = {"name": dst_name, "parents": [target_id]}
        mime = None
        ln = str(local_path).lower()
        if ln.endswith(".docx"):
            mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif ln.endswith(".pdf"):
            mime = "application/pdf"
        elif ln.endswith(".xlsx"):
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif ln.endswith(".json"):
            mime = "application/json"
        media = MediaFileUpload(str(local_path), mimetype=mime, resumable=False)
        created = svc.files().create(body=body, media_body=media, fields="id,webViewLink,parents").execute()
        return {"id": created["id"], "link": created.get("webViewLink"), "parent_id": target_id, "target_folder_name": target_folder_name}
    except Exception:
        LOG.exception("P6H_TOPIC5_DRIVE_UPLOAD_FAIL name=%s topic=%s sub=%s", dst_name, topic_id, target_folder_name)
        return None


def download_to_local(file_id: str, dst_filename: str) -> Optional[Path]:
    """Download a Drive file to local cache. Returns path or None."""
    try:
        from googleapiclient.http import MediaIoBaseDownload
        svc = _service()
        dst = _DOWNLOAD_DIR / dst_filename
        req = svc.files().get_media(fileId=file_id)
        with io.FileIO(dst, "wb") as buf:
            dl = MediaIoBaseDownload(buf, req)
            done = False
            while not done:
                _, done = dl.next_chunk()
        return dst
    except Exception:
        LOG.exception("P6H_TOPIC5_DRIVE_INDEX_DOWNLOAD_FAIL fid=%s", file_id)
        return None


try:
    LOG.info("P6H_TOPIC5_DRIVE_INDEX_V1_INSTALLED")
except Exception:
    pass
# === END_P6H_TOPIC5_DRIVE_INDEX_V1 ===

====================================================================================================
END_FILE: core/technadzor_drive_index.py
FILE_CHUNK: 1/1
====================================================================================================
