# ORCHESTRA_FULL_CONTEXT_PART_015
generated_at_utc: 2026-07-07T18:54:08.412433+00:00
git_sha_before_commit: c68b0dc28c81012640c7c52bc5e4765016af155f
part: 15/22


====================================================================================================
BEGIN_FILE: core/stroyka_estimate_canon.py
FILE_CHUNK: 2/2
SHA256_FULL_FILE: b6843f1c2d43cf262f810db30db01f9ef30c8900b040d42ef8787c043e3b6de2
====================================================================================================
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
        "задачу завершить",
        "задачу закрыть",
        "хорошая работа",
        "можно закрывать",
    ))


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
    if not parent:
        parent = conn.execute(
            """
            SELECT id, COALESCE(raw_input,'') AS raw_input, COALESCE(result,'') AS result
            FROM tasks
            WHERE CAST(chat_id AS TEXT)=?
              AND COALESCE(topic_id,0)=?
              AND state='AWAITING_CONFIRMATION'
              AND id<>?
              AND COALESCE(result,'') LIKE '%Смета готова%'
              AND (COALESCE(result,'') LIKE '%drive.google.com%' OR COALESCE(result,'') LIKE '%docs.google.com%')
            ORDER BY updated_at DESC, created_at DESC
            LIMIT 1
            """,
            (str(chat_id), int(topic_id), str(task_id)),
        ).fetchone()
    if not parent:
        return False

    parent_id = _s(parent["id"])
    parent_raw = _s(parent["raw_input"])
    parent_result = _s(parent["result"])
    parent_low = _low(parent_result)
    if not ("смета готов" in parent_low and ("xlsx" in parent_low or "pdf" in parent_low or "drive.google.com" in parent_low or "docs.google.com" in parent_low)):
        return False

    _history_safe(conn, parent_id, "TOPIC2_EXPLICIT_CONFIRM:ready_done_phrase")
    _update_task_safe(conn, parent_id, state="DONE", error_message="")
    _history_safe(conn, parent_id, "state:DONE")
    try:
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

====================================================================================================
BEGIN_FILE: core/technadzor_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 23ad1be4c83a5d078344ec017ea6069bbed68fcab1d3951c031befc110a26820
====================================================================================================
# === FINAL_CLOSURE_BLOCKER_FIX_V1_TECHNADZOR_ENGINE ===
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

BASE = Path("/root/.areal-neva-core")
OUT = BASE / "outputs" / "technadzor"
OUT.mkdir(parents=True, exist_ok=True)


def is_technadzor_intent(text: str = "", file_name: str = "") -> bool:
    t = f"{text} {file_name}".lower().replace("ё", "е")
    return bool(re.search(r"\b(акт|технадзор|техническ.*надзор|дефект|замечан|нарушен|освидетельств|стройконтроль|сп|гост|снип)\b", t))


def _norm_refs(text: str) -> str:
    refs = []
    for m in re.findall(r"\b(сп\s*\d+[.\d]*|гост\s*\d+[.\d-]*|снип\s*[\w.\-]+)\b", text or "", flags=re.I):
        refs.append(m.upper().replace("  ", " "))
    return ", ".join(sorted(set(refs))) if refs else "Норма не подтверждена"


def process_technadzor(text: str = "", task_id: str = "", chat_id: str = "", topic_id: int = 0, file_path: str = "", file_name: str = "") -> Dict[str, Any]:
    if not is_technadzor_intent(text, file_name):
        return {"ok": False, "handled": False, "reason": "NOT_TECHNADZOR"}

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"TECHNADZOR_ACT__{task_id[:8] or ts}"
    txt_path = OUT / f"{stem}.txt"

    body = [
        "АКТ ТЕХНИЧЕСКОГО НАДЗОРА",
        "",
        f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Задача: {task_id}",
        f"Топик: {topic_id}",
    ]

    if file_name:
        body.append(f"Файл: {file_name}")

    body.extend(
        [
            "",
            "Исходное описание:",
            (text or "").strip() or "UNKNOWN",
            "",
            "Нормативная база:",
            _norm_refs(text),
            "",
            "Вывод:",
            "Черновик акта создан. Если норматив не подтверждён источником, в акте указано: Норма не подтверждена",
        ]
    )

    txt_path.write_text("\n".join(body) + "\n", encoding="utf-8")

    return {
        "ok": True,
        "handled": True,
        "kind": "technadzor_act",
        "state": "DONE",
        "artifact_path": str(txt_path),
        "message": "Технадзорный акт подготовлен",  # TECHNADZOR_PUBLIC_MESSAGE_NO_LOCAL_PATH_V1
        "history": "FINAL_CLOSURE_BLOCKER_FIX_V1:TECHNADZOR_ACT_CREATED",
    }


# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_TECHNADZOR_ENGINE ===


# === P6_TECHNADZOR_TEMPLATE_AND_ARTIFACT_CLOSE_20260504_V1 ===
# Scope:
# - technadzor sample/template files can be saved as active reference per chat/topic
# - future technadzor acts use active reference metadata
# - produces TXT and DOCX when python-docx exists; no DB schema changes

import json as _p6tz_json
import re as _p6tz_re
from datetime import datetime as _p6tz_datetime
from pathlib import Path as _p6tz_Path

_P6TZ_BASE = _p6tz_Path("/root/.areal-neva-core")
_P6TZ_TEMPLATE_DIR = _P6TZ_BASE / "data/templates/technadzor"
_P6TZ_OUT = _P6TZ_BASE / "outputs/technadzor"
_P6TZ_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
_P6TZ_OUT.mkdir(parents=True, exist_ok=True)

def _p6tz_s(v, limit=12000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6tz_low(v):
    return _p6tz_s(v).lower().replace("ё", "е")

def _p6tz_template_path(chat_id, topic_id):
    safe_chat = _p6tz_re.sub(r"[^0-9a-zA-Z_-]+", "_", str(chat_id or "unknown"))
    return _P6TZ_TEMPLATE_DIR / f"ACTIVE__chat_{safe_chat}__topic_{int(topic_id or 0)}.json"

def _p6tz_is_template_intent(text="", file_name=""):
    low = _p6tz_low(str(text) + " " + str(file_name))
    return any(x in low for x in ("образец", "шаблон", "пример", "как образец", "как шаблон", "возьми его как образец", "сохрани как образец")) and any(x in low for x in ("технадзор", "акт", "замечан", "дефект", "строительный контроль", "стройконтроль"))

def _p6tz_save_template(text="", task_id="", chat_id="", topic_id=0, file_path="", file_name=""):
    meta = {
        "engine": "P6_TECHNADZOR_TEMPLATE_AND_ARTIFACT_CLOSE_20260504_V1",
        "kind": "technadzor_template",
        "status": "active",
        "chat_id": str(chat_id or ""),
        "topic_id": int(topic_id or 0),
        "source_task_id": str(task_id or ""),
        "source_file_path": str(file_path or ""),
        "source_file_name": str(file_name or ""),
        "raw_user_instruction": _p6tz_s(text, 4000),
        "usage_rule": "Use this file as formatting/sample reference for future technadzor acts in same chat/topic",
        "saved_at": _p6tz_datetime.now().isoformat(),
    }
    path = _p6tz_template_path(chat_id, topic_id)
    path.write_text(_p6tz_json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

def _p6tz_load_template(chat_id, topic_id):
    path = _p6tz_template_path(chat_id, topic_id)
    if not path.exists():
        return {}
    try:
        return _p6tz_json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _p6tz_refs(text):
    refs = []
    for m in _p6tz_re.findall(r"\b(сп\s*\d+[.\d]*|гост\s*\d+[.\d-]*|снип\s*[\w.\-]+)\b", text or "", flags=_p6tz_re.I):
        refs.append(m.upper().replace("  ", " "))
    return ", ".join(sorted(set(refs))) if refs else "Норма не подтверждена"

def _p6tz_make_docx(path, lines):
    try:
        from docx import Document
        doc = Document()
        for i, line in enumerate(lines):
            if i == 0:
                doc.add_heading(line, level=1)
            elif line == "":
                doc.add_paragraph("")
            else:
                doc.add_paragraph(line)
        doc.save(str(path))
        return str(path)
    except Exception:
        return ""

try:
    _p6tz_orig_is_intent = is_technadzor_intent
    def is_technadzor_intent(text: str = "", file_name: str = "") -> bool:
        low = _p6tz_low(str(text) + " " + str(file_name))
        if _p6tz_is_template_intent(text, file_name):
            return True
        if any(x in low for x in ("технадзор", "акт", "замечан", "дефект", "нарушен", "освидетельств", "стройконтроль", "строительный контроль", "сп ", "гост", "снип")):
            return True
        return _p6tz_orig_is_intent(text, file_name)
except Exception:
    pass

try:
    _p6tz_orig_process = process_technadzor
    def process_technadzor(text: str = "", task_id: str = "", chat_id: str = "", topic_id: int = 0, file_path: str = "", file_name: str = ""):
        if _p6tz_is_template_intent(text, file_name):
            meta_path = _p6tz_save_template(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id, file_path=file_path, file_name=file_name)
            return {
                "ok": True,
                "handled": True,
                "kind": "technadzor_template_saved",
                "state": "DONE",
                "artifact_path": str(meta_path),
                "message": "Образец технадзора сохранён для этого топика",
                "history": "P6_TECHNADZOR_TEMPLATE_SAVED",
            }

        if not is_technadzor_intent(text, file_name):
            return {"ok": False, "handled": False, "reason": "NOT_TECHNADZOR"}

        tpl = _p6tz_load_template(chat_id, topic_id)
        ts = _p6tz_datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = str(task_id or ts)[:8] or ts
        stem = f"TECHNADZOR_ACT__{safe}"
        txt_path = _P6TZ_OUT / f"{stem}.txt"
        docx_path = _P6TZ_OUT / f"{stem}.docx"

        lines = [
            "АКТ ТЕХНИЧЕСКОГО НАДЗОРА",
            "",
            f"Дата: {_p6tz_datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Задача: {task_id}",
            f"Топик: {topic_id}",
        ]
        if file_name:
            lines.append(f"Файл: {file_name}")
        if tpl:
            lines.append(f"Образец: {tpl.get('source_file_name') or tpl.get('source_file_path') or 'активный шаблон топика'}")
        lines += [
            "",
            "Исходное описание:",
            _p6tz_s(text, 6000) or "UNKNOWN",
            "",
            "Нормативная база:",
            _p6tz_refs(text),
            "",
            "Выявленные замечания:",
            "1. Требуется заполнение по присланным фото/файлам и описанию",
            "",
            "Требуемые действия:",
            "1. Устранить замечания",
            "2. Предоставить фотофиксацию устранения",
            "3. Повторно предъявить участок работ техническому надзору",
            "",
            "Статус:",
            "Черновик подготовлен по текущим данным",
        ]

        txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        docx_created = _p6tz_make_docx(docx_path, lines)
        return {
            "ok": True,
            "handled": True,
            "kind": "technadzor_act",
            "state": "DONE",
            "artifact_path": docx_created or str(txt_path),
            "extra_artifact_path": str(txt_path),
            "message": "Технадзорный акт подготовлен",
            "history": "P6_TECHNADZOR_ACT_CREATED",
        }
except Exception:
    pass

# === END_P6_TECHNADZOR_TEMPLATE_AND_ARTIFACT_CLOSE_20260504_V1 ===

# === P6C_TECHNADZOR_CONN_COMPAT_TEMPLATE_ACT_CLOSE_20260504_V1 ===
import json as _p6c_te_json
import re as _p6c_te_re
from pathlib import Path as _p6c_te_Path
from datetime import datetime as _p6c_te_datetime

_P6C_TE_BASE = _p6c_te_Path("/root/.areal-neva-core")
_P6C_TE_OUT = _P6C_TE_BASE / "outputs" / "technadzor"
_P6C_TE_TPL = _P6C_TE_BASE / "data" / "templates" / "technadzor"
_P6C_TE_OUT.mkdir(parents=True, exist_ok=True)
_P6C_TE_TPL.mkdir(parents=True, exist_ok=True)

def _p6c_te_s(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6c_te_low(v):
    return _p6c_te_s(v).lower().replace("ё", "е")

def is_technadzor_intent(text: str = "", file_name: str = "") -> bool:
    low = _p6c_te_low(f"{text} {file_name}")
    return any(x in low for x in (
        "технадзор", "акт", "осмотр", "выезд", "дефект", "замечан",
        "образец написания", "образец акта", "как образец"
    ))

def _p6c_te_is_template(text, file_name):
    low = _p6c_te_low(f"{text} {file_name}")
    return any(x in low for x in (
        "образец", "как образец", "прими это как факт", "образец написания",
        "возьми это как образец", "шаблон"
    ))

def _p6c_te_read_text(file_path):
    fp = _p6c_te_Path(_p6c_te_s(file_path))
    if not fp.exists():
        return ""
    suf = fp.suffix.lower()
    try:
        if suf == ".txt":
            return fp.read_text(encoding="utf-8", errors="ignore")[:30000]
        if suf == ".pdf":
            try:
                import fitz
                doc = fitz.open(str(fp))
                return "\n".join(page.get_text("text") for page in doc)[:30000]
            except Exception:
                return ""
        if suf == ".docx":
            try:
                import docx
                d = docx.Document(str(fp))
                return "\n".join(p.text for p in d.paragraphs)[:30000]
            except Exception:
                return ""
    except Exception:
        return ""
    return ""

def _p6c_te_save_template(chat_id, topic_id, task_id, text, file_name, file_path):
    data = {
        "engine": "P6C_TECHNADZOR_CONN_COMPAT_TEMPLATE_ACT_CLOSE_20260504_V1",
        "chat_id": str(chat_id or ""),
        "topic_id": int(topic_id or 0),
        "task_id": str(task_id or ""),
        "file_name": _p6c_te_s(file_name),
        "file_path": _p6c_te_s(file_path),
        "saved_at": _p6c_te_datetime.utcnow().isoformat() + "Z",
        "template_text": _p6c_te_s(text, 25000),
    }
    out = _P6C_TE_TPL / f"ACTIVE__chat_{chat_id}__topic_{int(topic_id or 0)}.json"
    out.write_text(_p6c_te_json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(out)

def _p6c_te_load_template(chat_id, topic_id):
    p = _P6C_TE_TPL / f"ACTIVE__chat_{chat_id}__topic_{int(topic_id or 0)}.json"
    if not p.exists():
        return {}
    try:
        return _p6c_te_json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _p6c_te_write_act(task_id, chat_id, topic_id, body):
    out = _P6C_TE_OUT / f"TECHNADZOR_ACT__{str(task_id)[:8]}.txt"
    out.write_text(body, encoding="utf-8")
    return str(out)

def process_technadzor(text: str = "", task_id: str = "", chat_id: str = "", topic_id: int = 0, file_path: str = "", file_name: str = "", **kwargs):
    conn = kwargs.get("conn")
    raw_text = _p6c_te_s(text, 50000)
    file_name = _p6c_te_s(file_name or kwargs.get("name") or "")
    file_path = _p6c_te_s(file_path or kwargs.get("local_path") or "")
    task_id = _p6c_te_s(task_id or kwargs.get("id") or kwargs.get("task_id") or "technadzor")
    chat_id = _p6c_te_s(chat_id or kwargs.get("chat_id") or "")
    try:
        topic_id = int(topic_id or kwargs.get("topic_id") or 0)
    except Exception:
        topic_id = 0

    extracted = _p6c_te_read_text(file_path)
    combined = "\n".join(x for x in [raw_text, extracted] if x).strip()

    if _p6c_te_is_template(raw_text, file_name):
        tpl_path = _p6c_te_save_template(chat_id, topic_id, task_id, combined, file_name, file_path)
        return {
            "ok": True,
            "status": "DONE",
            "result_text": f"Образец технадзора принят и сохранён\nФайл: {file_name}\nШаблон: активен для topic_{topic_id}",
            "artifact_path": tpl_path,
            "history": "P6C_TECHNADZOR_TEMPLATE_SAVED",
        }

    tpl = _p6c_te_load_template(chat_id, topic_id)
    tpl_note = "Использован сохранённый образец" if tpl else "Сохранённый образец не найден"

    body = "\n".join([
        "АКТ ОСМОТРА ПО ФАКТУ ВЫЕЗДА",
        "",
        f"Дата формирования: {_p6c_te_datetime.now().strftime('%d.%m.%Y %H:%M')}",
        f"Файл: {file_name or 'без файла'}",
        f"Источник: topic_{topic_id}",
        f"Шаблон: {tpl_note}",
        "",
        "Исходные данные:",
        combined[:12000] if combined else "Данные из файла не извлечены автоматически",
        "",
        "Вывод технического надзора:",
        "Документ сформирован как рабочий черновик акта. Требуется проверка владельцем перед выдачей заказчику.",
    ])
    artifact = _p6c_te_write_act(task_id, chat_id, topic_id, body)

    return {
        "ok": True,
        "status": "DONE",
        "result_text": f"Акт технадзора сформирован\nФайл: {file_name or 'без файла'}\nАртефакт: {artifact}",
        "artifact_path": artifact,
        "history": "P6C_TECHNADZOR_ACT_CREATED",
    }
# === END_P6C_TECHNADZOR_CONN_COMPAT_TEMPLATE_ACT_CLOSE_20260504_V1 ===

# === P6E2_TECHNADZOR_FOLDER_AWARE_NO_DRIVE_POLLUTION_20260504_V1 ===
import json as _p6e2_te_json
import re as _p6e2_te_re
from pathlib import Path as _p6e2_te_Path
from datetime import datetime as _p6e2_te_datetime

_P6E2_TE_BASE = _p6e2_te_Path("/root/.areal-neva-core")
_P6E2_TE_OUT = _P6E2_TE_BASE / "outputs" / "technadzor"
_P6E2_TE_TPL = _P6E2_TE_BASE / "data" / "templates" / "technadzor"
_P6E2_TE_OUT.mkdir(parents=True, exist_ok=True)
_P6E2_TE_TPL.mkdir(parents=True, exist_ok=True)

def _p6e2_te_s(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6e2_te_low(v):
    return _p6e2_te_s(v).lower().replace("ё", "е")

def _p6e2_te_is_template(text, file_name=""):
    low = _p6e2_te_low(text + " " + file_name)
    return any(x in low for x in ("как образец", "образец написания", "прими это как факт", "возьми это как образец", "шаблон акта"))

def _p6e2_te_extract_links(text):
    return _p6e2_te_re.findall(r"https?://\S+", _p6e2_te_s(text, 50000))

def _p6e2_te_read_file(path):
    p = _p6e2_te_Path(_p6e2_te_s(path))
    if not p.exists():
        return ""
    try:
        if p.suffix.lower() == ".txt":
            return p.read_text(encoding="utf-8", errors="ignore")[:50000]
        if p.suffix.lower() == ".docx":
            import docx
            d = docx.Document(str(p))
            return "\n".join(x.text for x in d.paragraphs)[:50000]
        if p.suffix.lower() == ".pdf":
            try:
                import fitz
                doc = fitz.open(str(p))
                return "\n".join(page.get_text("text") for page in doc)[:50000]
            except Exception:
                return ""
    except Exception:
        return ""
    return ""

def _p6e2_te_tpl_path(chat_id, topic_id):
    return _P6E2_TE_TPL / f"ACTIVE__chat_{chat_id}__topic_{int(topic_id or 0)}.json"

def _p6e2_te_save_template(chat_id, topic_id, task_id, body, file_name, file_path, links):
    data = {
        "engine": "P6E2_TECHNADZOR_FOLDER_AWARE_NO_DRIVE_POLLUTION_20260504_V1",
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "task_id": str(task_id),
        "file_name": _p6e2_te_s(file_name),
        "file_path": _p6e2_te_s(file_path),
        "drive_links_seen": links,
        "saved_at": _p6e2_te_datetime.utcnow().isoformat() + "Z",
        "template_text": _p6e2_te_s(body, 30000),
    }
    p = _p6e2_te_tpl_path(chat_id, topic_id)
    p.write_text(_p6e2_te_json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(p)

def _p6e2_te_load_template(chat_id, topic_id):
    p = _p6e2_te_tpl_path(chat_id, topic_id)
    if not p.exists():
        return {}
    try:
        return _p6e2_te_json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def is_technadzor_intent(text: str = "", file_name: str = "") -> bool:
    low = _p6e2_te_low(text + " " + file_name)
    return any(x in low for x in ("технадзор", "акт", "осмотр", "выезд", "дефект", "замечан", "нарушен", "образец написания", "как образец", "прими это как факт"))

def process_technadzor(text: str = "", task_id: str = "", chat_id: str = "", topic_id: int = 0, file_path: str = "", file_name: str = "", **kwargs):
    raw = _p6e2_te_s(text, 50000)
    extracted = _p6e2_te_read_file(file_path)
    combined = "\n".join(x for x in (raw, extracted) if x).strip()
    links = _p6e2_te_extract_links(combined)
    task_id = _p6e2_te_s(task_id or kwargs.get("task_id") or kwargs.get("id") or "technadzor")
    chat_id = _p6e2_te_s(chat_id or kwargs.get("chat_id") or "")
    try:
        topic_id = int(topic_id or kwargs.get("topic_id") or 0)
    except Exception:
        topic_id = 0
    file_name = _p6e2_te_s(file_name or kwargs.get("file_name") or kwargs.get("name") or "")
    file_path = _p6e2_te_s(file_path or kwargs.get("local_path") or "")

    if _p6e2_te_is_template(raw, file_name):
        tpl = _p6e2_te_save_template(chat_id, topic_id, task_id, combined, file_name, file_path, links)
        return {
            "ok": True,
            "handled": True,
            "status": "DONE",
            "state": "DONE",
            "result_text": f"Образец технадзора принят и сохранён\nФайл: {file_name or 'без файла'}\nШаблон: active topic_{topic_id}\nDrive-ссылки учтены: {len(links)}",
            "message": "Образец технадзора принят и сохранён",
            "artifact_path": tpl,
            "history": "P6E2_TECHNADZOR_TEMPLATE_SAVED",
        }

    if not is_technadzor_intent(combined, file_name):
        return {"ok": False, "handled": False, "reason": "NOT_TECHNADZOR"}

    tpl = _p6e2_te_load_template(chat_id, topic_id)
    tpl_note = "использован сохранённый образец" if tpl else "сохранённый образец не найден"
    out = _P6E2_TE_OUT / f"TECHNADZOR_ACT__{str(task_id)[:8]}.txt"
    body = "\n".join([
        "АКТ ОСМОТРА ПО ФАКТУ ВЫЕЗДА",
        "",
        f"Дата формирования: {_p6e2_te_datetime.now().strftime('%d.%m.%Y %H:%M')}",
        f"Файл: {file_name or 'без файла'}",
        f"Источник: topic_{topic_id}",
        f"Шаблон: {tpl_note}",
        f"Drive-ссылки в исходных данных: {len(links)}",
        "",
        "Исходные данные:",
        combined[:15000] if combined else "UNKNOWN",
        "",
        "Вывод технического надзора:",
        "Документ сформирован по текущим данным и сохранён локально без записи мусора в Google Drive",
    ])
    out.write_text(body + "\n", encoding="utf-8")
    return {
        "ok": True,
        "handled": True,
        "status": "DONE",
        "state": "DONE",
        "result_text": f"Акт технадзора сформирован\nФайл: {file_name or 'без файла'}\nАртефакт: {out}",
        "message": "Акт технадзора сформирован",
        "artifact_path": str(out),
        "history": "P6E2_TECHNADZOR_ACT_CREATED",
    }
# === END_P6E2_TECHNADZOR_FOLDER_AWARE_NO_DRIVE_POLLUTION_20260504_V1 ===


# === P6F_TECHNADZOR_CLEAN_OUTPUT_AND_NORM_GATE_V1 ===
# FACT: wraps process_technadzor to ensure clean user-facing output.
# Uses core.normative_engine for confirmed references; if no confidence
# >= PARTIAL — explicitly states "норма не подтверждена" (per canon).
# Forbids JSON output to user.
import json as _p6f_tnz_json
import logging as _p6f_tnz_logging

_P6F_TNZ_LOG = _p6f_tnz_logging.getLogger("technadzor_engine")

def _p6f_tnz_clean_for_user(text):
    if not text:
        return ""
    s = str(text).strip()
    if (s.startswith("{") and s.rstrip().endswith("}")) or (s.startswith("[") and s.rstrip().endswith("]")):
        try:
            obj = _p6f_tnz_json.loads(s)
            if isinstance(obj, dict):
                summary = str(obj.get("summary") or obj.get("message") or "").strip()
                if summary:
                    return summary
                lines = []
                for k in ("kind", "state", "artifact_path", "history"):
                    if k in obj:
                        v = obj[k]
                        if k == "artifact_path":
                            lines.append("Артефакт: создан")
                        else:
                            lines.append(str(k) + ": " + str(v))
                if lines:
                    return "\n".join(lines)
                return "Технадзорный результат подготовлен"
        except Exception:
            pass
    return s

def _p6f_tnz_norm_block(text):
    try:
        from core.normative_engine import search_norms_sync, format_norms_for_act
    except Exception:
        return ""
    try:
        norms = search_norms_sync(text or "", limit=3)
    except Exception:
        return ""
    if not norms:
        return "Норма не подтверждена. Акт оформлен без ссылки на конкретный пункт СП/ГОСТ"
    confirmed_or_partial = [n for n in norms if str(n.get("confidence", "")).upper() in ("CONFIRMED", "PARTIAL")]
    if not confirmed_or_partial:
        return "Норма не подтверждена. Источник не найден"
    try:
        return format_norms_for_act(confirmed_or_partial)
    except Exception:
        out = []
        for n in confirmed_or_partial:
            nid = str(n.get("norm_id", "")).strip()
            sec = str(n.get("section", "")).strip()
            req = str(n.get("requirement", "")).strip()
            conf = str(n.get("confidence", "")).strip()
            if nid:
                out.append(f"- {nid} | {sec} | {req} | confidence={conf}")
        return "\n".join(out)

try:
    _P6F_TNZ_ORIG_PROCESS = process_technadzor
    if not getattr(_P6F_TNZ_ORIG_PROCESS, "_p6f_tnz_wrapped", False):
        def process_technadzor(text="", task_id="", chat_id="", topic_id=0, file_path="", file_name="", **kwargs):
            try:
                res = _P6F_TNZ_ORIG_PROCESS(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs)
            except TypeError:
                res = _P6F_TNZ_ORIG_PROCESS(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id, file_path=file_path, file_name=file_name)
            try:
                if isinstance(res, dict) and res.get("ok") and res.get("handled"):
                    raw_msg = res.get("message") or ""
                    clean = _p6f_tnz_clean_for_user(raw_msg)
                    norm_block = _p6f_tnz_norm_block(text)
                    artifact_line = ""
                    if res.get("artifact_path"):
                        artifact_line = "Артефакт акта: создан"
                    parts = [clean]
                    if norm_block:
                        parts.append("\nНормативная база:\n" + norm_block)
                    if artifact_line:
                        parts.append("\n" + artifact_line)
                    res["message"] = "\n".join([p for p in parts if p]).strip()
                    res["history"] = (res.get("history") or "") + ";P6F_TNZ_CLEANED_OUTPUT"
            except Exception as _e:
                try:
                    _P6F_TNZ_LOG.warning("P6F_TNZ_WRAP_ERR %s", _e)
                except Exception:
                    pass
            return res
        process_technadzor._p6f_tnz_wrapped = True
        _P6F_TNZ_LOG.info("P6F_TECHNADZOR_CLEAN_OUTPUT_AND_NORM_GATE_INSTALLED")
except Exception as _e:
    try:
        _P6F_TNZ_LOG.exception("P6F_TNZ_INSTALL_ERR %s", _e)
    except Exception:
        pass
# === END_P6F_TECHNADZOR_CLEAN_OUTPUT_AND_NORM_GATE_V1 ===


# === P6F_TECHNADZOR_PHOTO_TO_DOCX_REAL_V1 ===
# FACT: real photo defect → Vision (OpenRouter) → DOCX акт →
# Drive upload via topic_drive_oauth.upload_file_to_topic.
# No direct Google API. Norms only via core.normative_engine
# (no invented references).
import os as _p6f_tnz_os
import base64 as _p6f_tnz_base64
import asyncio as _p6f_tnz_asyncio
import json as _p6f_tnz_json2
import logging as _p6f_tnz_logging2

_P6F_TNZ_REAL_LOG = _p6f_tnz_logging2.getLogger("technadzor_engine")

_P6F_TNZ_REAL_PROMPT = (
    "Ты эксперт технического надзора в строительстве. На фото фиксация состояния "
    "конструкций или дефекта. Верни СТРОГО JSON без пояснений со схемой:\n"
    "{\n"
    "  \"summary\": \"кратко что видно\",\n"
    "  \"defects\": [{\n"
    "    \"title\": \"короткое название\",\n"
    "    \"location\": \"место\",\n"
    "    \"severity\": \"low|medium|high|critical\",\n"
    "    \"description\": \"что не так\",\n"
    "    \"recommendation\": \"что делать\"\n"
    "  }],\n"
    "  \"confidence\": \"HIGH|MEDIUM|LOW\"\n"
    "}\n"
    "Если на фото нет дефектов — defects=[]. "
    "Не выдумывай нормы СП/ГОСТ — это не твоя задача."
)

def _p6f_tnz_is_image_path(path):
    if not path:
        return False
    p = str(path).lower()
    return any(p.endswith(e) for e in (".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".bmp"))

async def _p6f_tnz_vision_via_openrouter(local_path):
    if not _p6f_tnz_is_image_path(local_path) or not _p6f_tnz_os.path.exists(str(local_path)):
        return None, "PATH_MISSING"
    api_key = <REDACTED_SECRET>"OPENROUTER_API_KEY") or "").strip()
    if not api_key:
        return None, "NO_OPENROUTER_KEY"
    base_url = (_p6f_tnz_os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1").strip().rstrip("/")
    model = (_p6f_tnz_os.getenv("OPENROUTER_VISION_MODEL") or "google/gemini-2.5-flash").strip()
    ext = _p6f_tnz_os.path.splitext(str(local_path))[1].lower().lstrip(".") or "jpeg"
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/{}".format(ext)
    try:
        with open(str(local_path), "rb") as f:
            b64 = _p6f_tnz_base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        return None, "READ_ERR:{}".format(e)

    body = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": _P6F_TNZ_REAL_PROMPT},
                {"type": "image_url", "image_url": {"url": "data:" + mime + ";base64," + b64}},
            ],
        }],
        "temperature": 0.1,
    }
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    try:
        import httpx
        async with httpx.AsyncClient(timeout=httpx.Timeout(180.0, connect=30.0)) as client:
            r = await client.post(base_url + "/chat/completions", headers=headers, json=body)
            r.raise_for_status()
            data = r.json()
        content = data["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "\n".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in content)
    except Exception as e:
        return None, "OPENROUTER_CALL_ERR:{}".format(type(e).__name__)

    s = str(content).strip()
    if s.startswith("```"):
        import re as _re
        s = _re.sub(r"^```(?:json)?\s*", "", s)
        s = _re.sub(r"\s*```\s*$", "", s)
    try:
        return _p6f_tnz_json2.loads(s), "OK"
    except Exception:
        return {"summary": s[:2000], "defects": [], "confidence": "LOW"}, "PARTIAL"

def _p6f_tnz_norms_block(text_for_search):
    try:
        from core.normative_engine import search_norms_sync
    except Exception:
        return [], ""
    try:
        norms = search_norms_sync(text_for_search or "", limit=3)
    except Exception:
        return [], ""
    confirmed = [n for n in norms if str(n.get("confidence", "")).upper() in ("CONFIRMED", "PARTIAL")]
    if not confirmed:
        return [], "Норма не подтверждена"
    return confirmed, ""

def _p6f_tnz_build_docx_lines(vision_result, norms, file_name, task_id):
    from datetime import datetime as _dt
    lines = [
        "АКТ ТЕХНИЧЕСКОГО НАДЗОРА",
        "",
        "Дата: " + _dt.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Задача: " + str(task_id),
        "",
    ]
    if file_name:
        lines.append("Источник: фото " + str(file_name))
        lines.append("")
    summary = (vision_result.get("summary") or "").strip() if isinstance(vision_result, dict) else ""
    if summary:
        lines.extend(["Сводка по фото:", summary, ""])
    defects = vision_result.get("defects") or [] if isinstance(vision_result, dict) else []
    if defects:
        lines.append("Выявленные дефекты:")
        for i, d in enumerate(defects, 1):
            lines.append("{}. {}".format(i, d.get("title", "Дефект")))
            if d.get("location"):
                lines.append("   Место: " + str(d["location"]))
            if d.get("severity"):
                lines.append("   Степень: " + str(d["severity"]))
            if d.get("description"):
                lines.append("   Описание: " + str(d["description"]))
            if d.get("recommendation"):
                lines.append("   Рекомендация: " + str(d["recommendation"]))
            lines.append("")
    else:
        lines.extend(["Дефекты на фото не выявлены или фото недостаточно информативно", ""])

    if norms:
        lines.append("Нормативная база:")
        for n in norms:
            lines.append("- " + str(n.get("norm_id", "")) + " — " + str(n.get("section", "")))
            req = str(n.get("requirement", "")).strip()
            if req:
                lines.append("  " + req)
            lines.append("  confidence=" + str(n.get("confidence", "")))
        lines.append("")
    else:
        lines.extend(["Нормативная база: норма не подтверждена", ""])

    confidence = vision_result.get("confidence", "LOW") if isinstance(vision_result, dict) else "LOW"
    lines.append("Источник анализа: OpenRouter Vision (model=google/gemini-2.5-flash, confidence={})".format(confidence))
    return lines

async def _p6f_tnz_upload_to_topic(local_path, file_name, chat_id, topic_id):
    try:
        from core.topic_drive_oauth import upload_file_to_topic
    except Exception as e:
        _P6F_TNZ_REAL_LOG.warning("P6F_TNZ_UPLOAD_IMPORT_ERR %s", e)
        return None, "NO_UPLOADER"
    try:
        result = await upload_file_to_topic(
            file_path=str(local_path),
            file_name=str(file_name),
            chat_id=str(chat_id),
            topic_id=int(topic_id or 5),
        )
        if isinstance(result, dict) and result.get("ok"):
            file_id = result.get("drive_file_id") or result.get("id") or ""
            if file_id:
                return "https://drive.google.com/file/d/" + str(file_id) + "/view", "OK"
            link = result.get("link") or result.get("web_view_link") or ""
            return link, "OK_NO_ID"
        return None, "UPLOAD_FAIL:" + str(result)[:200]
    except Exception as e:
        return None, "UPLOAD_ERR:{}".format(type(e).__name__)

async def p6f_tnz_handle_photo_act_real(file_path, file_name, task_id, chat_id, topic_id, user_text=""):
    """
    Real entry point: photo → Vision → DOCX → Drive upload → return dict.
    Used by topic_5 photo-act flow.
    """
    vision, vstatus = await _p6f_tnz_vision_via_openrouter(file_path)
    if vision is None:
        return {
            "ok": False, "handled": True, "kind": "technadzor_photo_act",
            "state": "WAITING_CLARIFICATION",
            "message": "Не удалось проанализировать фото через Vision ({}). Пришли фото крупнее или текстовое описание дефекта".format(vstatus),
            "history": "P6F_TNZ_VISION_FAIL:{}".format(vstatus),
        }
    norms_text = (vision.get("summary", "") or "") + " " + " ".join(
        str(d.get("title", "")) + " " + str(d.get("description", ""))
        for d in (vision.get("defects") or [])
    ) + " " + str(user_text or "")
    confirmed_norms, _ = _p6f_tnz_norms_block(norms_text)
    docx_lines = _p6f_tnz_build_docx_lines(vision, confirmed_norms, file_name, task_id)

    from datetime import datetime as _dt
    ts = _dt.now().strftime("%Y%m%d_%H%M%S")
    safe = (str(task_id or ts)[:8] or ts).replace("/", "_").replace("\\", "_")
    out_dir = "/root/.areal-neva-core/outputs/technadzor_acts"
    _p6f_tnz_os.makedirs(out_dir, exist_ok=True)
    docx_path = "{}/TECHNADZOR_ACT_PHOTO__{}_{}.docx".format(out_dir, safe, ts)

    try:
        from core.technadzor_engine import _p6tz_make_docx as _make_docx
    except Exception:
        _make_docx = None
    if _make_docx is None:
        return {
            "ok": False, "handled": True, "kind": "technadzor_photo_act",
            "state": "FAILED",
            "message": "DOCX-генератор недоступен (python-docx не установлен)",
            "history": "P6F_TNZ_DOCX_GEN_MISSING",
        }
    written = _make_docx(docx_path, docx_lines)
    if not written:
        return {
            "ok": False, "handled": True, "kind": "technadzor_photo_act",
            "state": "FAILED",
            "message": "Ошибка создания DOCX акта",
            "history": "P6F_TNZ_DOCX_WRITE_FAIL",
        }

    drive_link, ustatus = await _p6f_tnz_upload_to_topic(
        docx_path, _p6f_tnz_os.path.basename(docx_path), chat_id or "-1003725299009", topic_id or 5
    )
    confidence = vision.get("confidence", "LOW")
    summary = vision.get("summary", "") or ""
    defects_count = len(vision.get("defects") or [])
    norms_count = len(confirmed_norms)

    public_lines = [
        "Акт технадзора по фото готов",
        "Файл: " + str(file_name or "photo"),
        "Уверенность Vision: " + str(confidence),
        "Дефектов на фото: " + str(defects_count),
        "Нормативных ссылок: " + str(norms_count) + (" (confidence=PARTIAL/CONFIRMED)" if norms_count else " — норма не подтверждена"),
    ]
    if drive_link:
        public_lines.append("Drive DOCX: " + str(drive_link))
    else:
        public_lines.append("Drive upload: не выполнен (" + str(ustatus) + "). DOCX лежит локально, доставка через Telegram fallback в следующей итерации")
    if summary:
        public_lines.append("")
        public_lines.append("Краткое описание: " + summary[:600])

    history_marker = "P6F_TNZ_PHOTO_ACT_DONE_DEFECTS_{}_NORMS_{}_DRIVE_{}".format(
        defects_count, norms_count, "OK" if drive_link else "FAIL"
    )
    return {
        "ok": True,
        "handled": True,
        "kind": "technadzor_photo_act",
        "state": "DONE" if drive_link else "AWAITING_CONFIRMATION",
        "artifact_path": docx_path,
        "drive_link": drive_link or "",
        "message": "\n".join(public_lines),
        "history": history_marker,
    }

_P6F_TNZ_REAL_LOG.info("P6F_TECHNADZOR_PHOTO_TO_DOCX_REAL_V1_INSTALLED")
# === END_P6F_TECHNADZOR_PHOTO_TO_DOCX_REAL_V1 ===


# === P6H_TOPIC5_USE_EXISTING_TEMPLATES_PHOTO_TO_TECH_REPORT_20260504_V1 ===
# Append-only wrapper.
# - Auto-indexes Drive topic_5 contents (PRIMARY_PDF_STYLE, SECONDARY_DOCX_REFERENCE, etc.)
#   on first photo / "акт" request per chat — without manual "образец" command.
# - On photo: Vision (existing _p6f_tnz_vision_via_openrouter) → section classifier
#   → clean Telegram text (no JSON, no /root, no internal paths).
# - On "сделай акт" / "оформи акт": same + DOCX (service folder _drafts) +
#   client-grade PDF A4 with cyrillic + clickable hyperlinks.
# - DOCX always lands in topic_5/_drafts/ (system).  PDF lands in topic root by default;
#   if user explicitly named a client folder, drop PDF there (only PDF allowed in client
#   folders per spec).
# - Telegram fallback when Drive upload fails — handled by existing P6F path
#   (we keep returning local artifact_path in that case so caller can retry).
import logging as _p6h_logging
import os as _p6h_os
import asyncio as _p6h_asyncio
from pathlib import Path as _P6H_Path
from datetime import datetime as _p6h_dt

_P6H_LOG = _p6h_logging.getLogger("task_worker")

# Eager import so drive_index install marker fires at worker startup
try:
    from core import technadzor_drive_index as _p6h_tdi  # noqa: F401
except Exception as _e_imp:
    _P6H_LOG.warning("P6H_DRIVE_INDEX_IMPORT_FAIL: %s", _e_imp)
_P6H_BASE = _P6H_Path(__file__).resolve().parent.parent
_P6H_OUTDIR = _P6H_BASE / "outputs" / "technadzor_p6h"
_P6H_OUTDIR.mkdir(parents=True, exist_ok=True)

_P6H_DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_P6H_DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Section classifier — keyword (lowercase substring) → canonical section title.
_P6H_SECTIONS = [
    ("Опорные узлы колонн",                        ["опорн", "анкерн", "колонн", "подлив", "опорная плита", "узел опор"]),
    ("Сварные соединения металлоконструкций",      ["сварн", "сварка", "шов", "провар", "наплыв", "сварные стык"]),
    ("Антикоррозионная защита",                    ["окрас", "лакокрас", "корроз", "защитн", "ржавчин", "антикорроз"]),
    ("Состояние основания и прилегающей территории", ["грунт", "основан", "замачив", "размыв", "просадк", "водоотвод", "канав", "лужа"]),
    ("Перекрытия",                                  ["перекрыт", "ригел", "балк перекрыт", "плита перекрыт"]),
    ("Узлы пересечения укосин",                     ["укосин", "связи", "диагональн", "жесткост", "пространств"]),
    ("Узлы крепления элементов покрытия",           ["крепл", "примыкан", "покрыт", "узел кров"]),
    ("Бетонные / железобетонные конструкции",       ["бетон", "железобетон", "арматур", "ж/б", "опалуб", "монолит"]),
    ("Гидроизоляция",                               ["гидроизол", "пароизол", "мембран"]),
    ("Кровля",                                       ["кровл", "крыш", "водосток", "желоб", "конек"]),
    ("Фасад",                                        ["фасад", "облиц", "сайдинг"]),
    ("Общие обзорные материалы",                    ["обзор", "общ вид", "общий вид"]),
]


def _p6h_classify_defect(d):
    text_pool = " ".join([
        str(d.get("title", "") or ""),
        str(d.get("description", "") or ""),
        str(d.get("section_hint", "") or ""),
        str(d.get("category", "") or ""),
    ]).lower()
    for section, kws in _P6H_SECTIONS:
        for kw in kws:
            if kw in text_pool:
                return section
    return "Прочие выявленные замечания"


def _p6h_group_defects_by_section(defects):
    groups = {}
    for d in defects or []:
        sec = _p6h_classify_defect(d)
        groups.setdefault(sec, []).append(d)
    ordered = []
    for sec, _ in _P6H_SECTIONS:
        if sec in groups:
            ordered.append((sec, groups[sec]))
    if "Прочие выявленные замечания" in groups:
        ordered.append(("Прочие выявленные замечания", groups["Прочие выявленные замечания"]))
    return ordered


def _p6h_clean_text(s, limit=4000):
    """Strip JSON/system markers, /root paths, traceback patterns, internal markers
    so result text is safe to send to Telegram."""
    if not s:
        return ""
    txt = str(s)
    # Strip lines starting with /root or containing internal markers
    bad_substrings = ["/root/", "task_id=", "TRACEBACK", "Traceback (most recent",
                       "P6F_", "P6G_", "P6H_", "P6E", "INSTALLED",
                       "MARKER:", "DEBUG:", "DEBUG ", "MANIFEST", "raw_input"]
    cleaned_lines = []
    for ln in txt.splitlines():
        keep = True
        for bad in bad_substrings:
            if bad in ln:
                keep = False
                break
        if keep:
            cleaned_lines.append(ln)
    out = "\n".join(cleaned_lines).strip()
    # Collapse triple+ blank lines
    while "\n\n\n" in out:
        out = out.replace("\n\n\n", "\n\n")
    return out[:limit]


def _p6h_norms_for_haystack(text):
    try:
        from core.normative_engine import search_norms_sync
        return search_norms_sync(text or "", limit=8)
    except Exception:
        return []


def _p6h_norms_for_section(section_title, defect_texts):
    haystack = (section_title + " " + " ".join(defect_texts)).strip()
    return _p6h_norms_for_haystack(haystack)


def _p6h_human_act_number(task_id):
    """Pretty act number 12-03/26 style — fall back to short task_id if missing."""
    today = _p6h_dt.now()
    n = today.strftime("%d-%m") + "/" + today.strftime("%y")
    if task_id:
        suffix = str(task_id)[:6]
        return f"{n}-{suffix}"
    return n


# ────────────────────────────────────────────────────────────────────
# DOCX builder — service-side, draft, with clickable hyperlinks
# ────────────────────────────────────────────────────────────────────
def _p6h_docx_add_hyperlink(paragraph, url, text):
    try:
        from docx.oxml.shared import OxmlElement, qn
    except Exception:
        paragraph.add_run(text + " (" + url + ")")
        return None
    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    rPr.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    rPr.append(underline)
    new_run.append(rPr)
    text_el = OxmlElement("w:t")
    text_el.text = text
    new_run.append(text_el)
    hyperlink.append(new_run)
    paragraph._element.append(hyperlink)
    return hyperlink


def _p6h_build_docx_act(payload, dst_path):
    """payload = {
        act_number, date_str, place, object_descr, method, performer, specialist,
        photos_link, general_purpose, sections=[(title, defects=[{title,description,norm_id,section_norms}], norms=[...], photos_block=[...])],
        recommendations=[str], consequences=[str], violations_table=[(violation, norm_id, photo)]
    }"""
    from docx import Document
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    # Header
    h = doc.add_paragraph()
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = h.add_run(f"АКТ ОСМОТРА ОБЪЕКТА № {payload.get('act_number','')}")
    r.bold = True
    r.font.size = Pt(14)
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.add_run("Методом визуального неразрушающего контроля").italic = True

    doc.add_paragraph(f"Дата осмотра: {payload.get('date_str','')}")
    doc.add_paragraph(f"Место осмотра: {payload.get('place','')}")
    doc.add_paragraph(f"Объект осмотра: {payload.get('object_descr','')}")
    doc.add_paragraph(f"Метод обследования: {payload.get('method','визуальный неразрушающий контроль с выездом на объект')}")
    if payload.get("performer"):
        doc.add_paragraph(f"Представитель подрядчика: {payload['performer']}")
    doc.add_paragraph(f"Технический специалист: {payload.get('specialist','Кузнецов Илья Владимирович')}")

    if payload.get("photos_link"):
        p = doc.add_paragraph("Ссылка на фотоматериалы: ")
        _p6h_docx_add_hyperlink(p, payload["photos_link"], payload["photos_link"])

    # 1. Общие сведения
    doc.add_paragraph()
    h1 = doc.add_paragraph()
    h1.add_run("1. Общие сведения").bold = True
    doc.add_paragraph(payload.get("general_purpose",
        "Осмотр выполнен методом визуального неразрушающего контроля с выездом на "
        "объект. Цель осмотра — выявление фактически наблюдаемых дефектов, определение "
        "рекомендаций к устранению и возможных последствий для заказчика при сохранении "
        "текущего состояния объекта"))

    # 2. Установлено по факту осмотра
    doc.add_paragraph()
    h2 = doc.add_paragraph()
    h2.add_run("2. Установлено по факту осмотра").bold = True
    sections = payload.get("sections") or []
    for i, sec in enumerate(sections, 1):
        ph = doc.add_paragraph()
        ph.add_run(f"2.{i} {sec.get('title','')}").bold = True
        # facts
        for d in sec.get("defects") or []:
            line = (d.get("title") or "").strip()
            descr = (d.get("description") or "").strip()
            if line and descr:
                doc.add_paragraph(f"— {line}: {descr}")
            elif line:
                doc.add_paragraph(f"— {line}")
            elif descr:
                doc.add_paragraph(f"— {descr}")
        # norm refs for section
        norms = sec.get("norms") or []
        if norms:
            np = doc.add_paragraph()
            np.add_run("Нормативная отсылка: ").italic = True
            np.add_run("; ".join(f"{n.get('norm_id','')} — {n.get('section','')}" for n in norms if n.get("norm_id")))
        else:
            np = doc.add_paragraph()
            np.add_run("Нормативная отсылка: ").italic = True
            np.add_run("норма не подтверждена").italic = True
        # photos
        photos = sec.get("photos_block") or []
        if photos:
            pp = doc.add_paragraph()
            pp.add_run("Фотоматериалы: ").italic = True
            pp.add_run(", ".join(photos))

    # Рекомендации
    if payload.get("recommendations"):
        doc.add_paragraph()
        rh = doc.add_paragraph()
        rh.add_run("3. Рекомендовано к устранению").bold = True
        for i, line in enumerate(payload["recommendations"], 1):
            doc.add_paragraph(f"{i}. {line}")

    # Возможные последствия
    if payload.get("consequences"):
        doc.add_paragraph()
        ch = doc.add_paragraph()
        ch.add_run("4. Возможные последствия при отсутствии устранения").bold = True
        for line in payload["consequences"]:
            doc.add_paragraph(f"— {line}")

    # Таблица: Нарушение / Норматив / Фото
    if payload.get("violations_table"):
        doc.add_paragraph()
        th = doc.add_paragraph()
        th.add_run("5. Сводная таблица нарушений").bold = True
        tbl = doc.add_table(rows=1, cols=3)
        tbl.style = "Light Grid"
        hdr = tbl.rows[0].cells
        hdr[0].text = "Нарушение"
        hdr[1].text = "Норматив"
        hdr[2].text = "Фото"
        for v, n, ph in payload["violations_table"]:
            row = tbl.add_row().cells
            row[0].text = str(v or "")
            row[1].text = str(n or "норма не подтверждена")
            row[2].text = str(ph or "")

    # Подпись
    doc.add_paragraph()
    doc.add_paragraph()
    sig = doc.add_paragraph()
    sig.add_run(f"Технический специалист: {payload.get('specialist','Кузнецов Илья Владимирович')}").bold = True
    doc.add_paragraph(f"Дата: {payload.get('date_str','')}")

    doc.save(str(dst_path))
    return str(dst_path)


# ────────────────────────────────────────────────────────────────────
# PDF builder — A4, cyrillic, clickable hyperlinks (reportlab platypus)
# ────────────────────────────────────────────────────────────────────
def _p6h_register_fonts():
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        if "DejaVuSans" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("DejaVuSans", _P6H_DEJAVU))
        if "DejaVuSans-Bold" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", _P6H_DEJAVU_BOLD))
        return True
    except Exception:
        return False


def _p6h_build_pdf_act(payload, dst_path):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
    from reportlab.lib.units import cm
    from reportlab.lib import colors

    _p6h_register_fonts()

    styles = getSampleStyleSheet()
    base_font = "DejaVuSans"
    bold_font = "DejaVuSans-Bold"

    sty_title = ParagraphStyle("title", parent=styles["Title"], fontName=bold_font, fontSize=14, alignment=1, spaceAfter=4)
    sty_subtitle = ParagraphStyle("subtitle", parent=styles["Normal"], fontName=base_font, fontSize=10, alignment=1, textColor=colors.grey, spaceAfter=10)
    sty_h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName=bold_font, fontSize=12, spaceBefore=8, spaceAfter=4)
    sty_h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontName=bold_font, fontSize=11, spaceBefore=6, spaceAfter=2)
    sty_body = ParagraphStyle("body", parent=styles["Normal"], fontName=base_font, fontSize=10, leading=13, spaceAfter=2)
    sty_italic = ParagraphStyle("italic", parent=sty_body, textColor=colors.grey)
    sty_small = ParagraphStyle("small", parent=sty_body, fontSize=9)

    flow = []
    flow.append(Paragraph(f"АКТ ОСМОТРА ОБЪЕКТА № {payload.get('act_number','')}", sty_title))
    flow.append(Paragraph("Методом визуального неразрушающего контроля", sty_subtitle))
    flow.append(Paragraph(f"<b>Дата осмотра:</b> {payload.get('date_str','')}", sty_body))
    flow.append(Paragraph(f"<b>Место осмотра:</b> {payload.get('place','')}", sty_body))
    flow.append(Paragraph(f"<b>Объект осмотра:</b> {payload.get('object_descr','')}", sty_body))
    flow.append(Paragraph(f"<b>Метод обследования:</b> {payload.get('method','визуальный неразрушающий контроль с выездом на объект')}", sty_body))
    if payload.get("performer"):
        flow.append(Paragraph(f"<b>Представитель подрядчика:</b> {payload['performer']}", sty_body))
    flow.append(Paragraph(f"<b>Технический специалист:</b> {payload.get('specialist','Кузнецов Илья Владимирович')}", sty_body))
    if payload.get("photos_link"):
        flow.append(Paragraph(
            f'<b>Ссылка на фотоматериалы:</b> <link href="{payload["photos_link"]}"><font color="#0563C1"><u>{payload["photos_link"]}</u></font></link>',
            sty_body,
        ))

    flow.append(Spacer(1, 8))
    flow.append(Paragraph("1. Общие сведения", sty_h2))
    flow.append(Paragraph(payload.get("general_purpose",
        "Осмотр выполнен методом визуального неразрушающего контроля с выездом на "
        "объект. Цель осмотра — выявление фактически наблюдаемых дефектов, определение "
        "рекомендаций к устранению и возможных последствий для заказчика."), sty_body))

    flow.append(Paragraph("2. Установлено по факту осмотра", sty_h2))
    sections = payload.get("sections") or []
    for i, sec in enumerate(sections, 1):
        flow.append(Paragraph(f"2.{i} {sec.get('title','')}", sty_h3))
        for d in sec.get("defects") or []:
            line = (d.get("title") or "").strip()
            descr = (d.get("description") or "").strip()
            txt = (line + ((": " + descr) if descr and line else descr)).strip()
            if txt:
                flow.append(Paragraph("— " + txt, sty_body))
        norms = sec.get("norms") or []
        if norms:
            ns = "; ".join(f"{n.get('norm_id','')} — {n.get('section','')}" for n in norms if n.get("norm_id"))
            flow.append(Paragraph(f"<i>Нормативная отсылка:</i> {ns}", sty_italic))
        else:
            flow.append(Paragraph("<i>Нормативная отсылка: норма не подтверждена</i>", sty_italic))
        photos = sec.get("photos_block") or []
        if photos:
            flow.append(Paragraph(f"<i>Фотоматериалы:</i> {', '.join(photos)}", sty_italic))

    if payload.get("recommendations"):
        flow.append(Spacer(1, 4))
        flow.append(Paragraph("3. Рекомендовано к устранению", sty_h2))
        for i, line in enumerate(payload["recommendations"], 1):
            flow.append(Paragraph(f"{i}. {line}", sty_body))

    if payload.get("consequences"):
        flow.append(Spacer(1, 4))
        flow.append(Paragraph("4. Возможные последствия при отсутствии устранения", sty_h2))
        for line in payload["consequences"]:
            flow.append(Paragraph("— " + line, sty_body))

    if payload.get("violations_table"):
        flow.append(Spacer(1, 6))
        flow.append(Paragraph("5. Сводная таблица нарушений", sty_h2))
        rows = [["Нарушение", "Норматив", "Фото"]]
        for v, n, ph in payload["violations_table"]:
            rows.append([Paragraph(str(v or ""), sty_small),
                         Paragraph(str(n or "норма не подтверждена"), sty_small),
                         Paragraph(str(ph or ""), sty_small)])
        tbl = Table(rows, colWidths=[7*cm, 6*cm, 4*cm], repeatRows=1)
        tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), base_font),
            ("FONTNAME", (0, 0), (-1, 0), bold_font),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        flow.append(tbl)

    flow.append(Spacer(1, 16))
    flow.append(Paragraph(
        f"<b>Технический специалист:</b> {payload.get('specialist','Кузнецов Илья Владимирович')}",
        sty_body,
    ))
    flow.append(Paragraph(f"<b>Дата:</b> {payload.get('date_str','')}", sty_body))

    doc = SimpleDocTemplate(
        str(dst_path), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title=f"Акт осмотра № {payload.get('act_number','')}",
    )
    doc.build(flow)
    return str(dst_path)


# ────────────────────────────────────────────────────────────────────
# Async pipeline: photo → Vision → sections → response (and optionally DOCX+PDF)
# ────────────────────────────────────────────────────────────────────
async def _p6h_process_photo_async(file_path, file_name, task_id, chat_id, topic_id, user_text="", make_act=False, place="", object_descr=""):
    # Ensure Drive index is built (silently, best-effort)
    try:
        from core import technadzor_drive_index as _tdi
        idx = _tdi.build_technadzor_template_index(str(chat_id), int(topic_id), force=False)
    except Exception:
        idx = {}

    # Vision
    vision, vstatus = await _p6f_tnz_vision_via_openrouter(file_path)
    if vstatus == "FAIL" or vision is None:
        return {
            "ok": False, "handled": True, "kind": "technadzor_p6h_photo",
            "state": "WAITING_CLARIFICATION",
            "message": "Не удалось проанализировать фото через Vision. Пришли крупнее или текстовое описание дефекта",
            "history": "P6H_VISION_FAIL",
        }

    summary = (vision.get("summary") or "").strip() if isinstance(vision, dict) else ""
    defects = (vision.get("defects") or []) if isinstance(vision, dict) else []
    confidence = vision.get("confidence", "LOW") if isinstance(vision, dict) else "LOW"

    grouped = _p6h_group_defects_by_section(defects)

    # Norms per section + global
    section_norms = []
    all_haystack = summary + " " + (user_text or "") + " " + " ".join(
        str(d.get("title", "")) + " " + str(d.get("description", "")) for d in defects
    )
    global_norms = _p6h_norms_for_haystack(all_haystack)

    # Build sections payload (used by both DOCX and PDF, and partly by Telegram)
    sections_payload = []
    for sec_title, ds in grouped:
        defect_texts = [str(d.get("title", "")) + " " + str(d.get("description", "")) for d in ds]
        snorms = _p6h_norms_for_section(sec_title, defect_texts)
        section_norms.append((sec_title, snorms))
        sections_payload.append({
            "title": sec_title,
            "defects": ds,
            "norms": snorms,
            "photos_block": [str(file_name or "")] if file_name else [],
        })

    # Topic folder link from index for "Ссылка на фотоматериалы"
    topic_folder_link = (idx or {}).get("topic_folder_link", "")

    # Build clean Telegram text response.
    # If make_act=False — photo-only response (template per spec).
    # If make_act=True  — short summary + DOCX/PDF links.
    if not make_act:
        out_lines = ["Технический осмотр по фото", ""]
        # 1. Что видно
        out_lines.append("1. Что видно:")
        if summary:
            out_lines.append(_p6h_clean_text(summary, 700))
        else:
            out_lines.append("Описание не сформировано")
        out_lines.append("")
        # 2. Замечания
        out_lines.append("2. Обнаруженные замечания:")
        if grouped:
            for sec_title, ds in grouped:
                titles = []
                for d in ds:
                    t = str(d.get("title") or d.get("description") or "").strip()
                    if t:
                        titles.append(t[:120])
                line = f"— {sec_title}: " + ("; ".join(titles) if titles else "замечания зафиксированы")
                out_lines.append(_p6h_clean_text(line, 500))
        else:
            out_lines.append("Дефектов на фото не выявлено")
        out_lines.append("")
        # 3. Почему плохо — берём severity/why из Vision если есть, иначе общий
        out_lines.append("3. Почему это плохо:")
        why_lines = []
        for d in defects:
            w = str(d.get("why") or d.get("severity") or d.get("impact") or "").strip()
            if w:
                why_lines.append("— " + w[:200])
        if why_lines:
            out_lines.extend(why_lines[:6])
        elif grouped:
            out_lines.append("Зафиксированные отклонения снижают эксплуатационную надёжность и/или несущую способность конструкции и требуют проверки и устранения")
        else:
            out_lines.append("Отклонений не выявлено")
        out_lines.append("")
        # 4. Как исправить
        out_lines.append("4. Как исправить:")
        fix_lines = []
        for d in defects:
            f = str(d.get("fix") or d.get("recommendation") or "").strip()
            if f:
                fix_lines.append("— " + f[:200])
        if fix_lines:
            out_lines.extend(fix_lines[:6])
        else:
            out_lines.append("Привести узлы и покрытия к нормативному состоянию по соответствующим СП/ГОСТ. Уточнить решения по проектной документации")
        out_lines.append("")
        # 5. Что проверить на объекте
        out_lines.append("5. Что проверить на объекте:")
        check_lines = []
        for d in defects:
            c = str(d.get("verify") or d.get("check") or "").strip()
            if c:
                check_lines.append("— " + c[:200])
        if check_lines:
            out_lines.extend(check_lines[:6])
        else:
            out_lines.append("Состояние конструкции в полном объёме, наличие и соответствие исполнительной документации, ранее выданные предписания и их устранение")
        out_lines.append("")
        # 6. Норма
        out_lines.append("6. Нормативная отсылка:")
        if global_norms:
            for n in global_norms[:5]:
                out_lines.append("— " + str(n.get("norm_id","")) + ": " + str(n.get("section","")) + f" [{n.get('confidence','PARTIAL')}]")
        else:
            out_lines.append("норма не подтверждена")
        out_lines.append("")
        # 7. Акт
        out_lines.append("7. Акт:")
        out_lines.append("Могу оформить акт по текущим фото — напишите «сделай акт» / «оформи акт»")

        return {
            "ok": True, "handled": True, "kind": "technadzor_p6h_photo",
            "state": "DONE",
            "message": _p6h_clean_text("\n".join(out_lines), 6000),
            "history": "P6H_PHOTO_REPORT_DEFECTS_{}_NORMS_{}".format(len(defects), len(global_norms)),
        }

    # ── Build DOCX (service _drafts) + PDF (client topic root) ──
    ts = _p6h_dt.now().strftime("%Y%m%d_%H%M%S")
    safe_tid = (str(task_id or ts)[:8] or ts).replace("/", "_").replace("\\", "_")
    docx_local = _P6H_OUTDIR / f"P6H_TNZ_ACT_DRAFT__{safe_tid}_{ts}.docx"
    pdf_local = _P6H_OUTDIR / f"АКТ_ОСМОТРА__{safe_tid}_{ts}.pdf"

    # Recommendations / consequences — pulled from defects
    recs = []
    cons = []
    for d in defects:
        r = str(d.get("fix") or d.get("recommendation") or "").strip()
        if r:
            recs.append(r[:300])
        c = str(d.get("consequence") or d.get("why") or "").strip()
        if c:
            cons.append(c[:300])
    # Violation table rows
    vtable = []
    for sec_title, ds in grouped:
        for d in ds:
            v = str(d.get("title") or d.get("description") or sec_title)[:200]
            sn = ""
            for n in section_norms:
                if n[0] == sec_title and n[1]:
                    sn = n[1][0].get("norm_id", "")
                    break
            ph = str(file_name or "")
            vtable.append((v, sn or "норма не подтверждена", ph))

    payload = {
        "act_number": _p6h_human_act_number(task_id),
        "date_str": _p6h_dt.now().strftime("%d.%m.%Y"),
        "place": place or "место уточняется по запросу владельца",
        "object_descr": object_descr or "объект уточняется по запросу владельца",
        "method": "визуальный неразрушающий контроль с выездом на объект",
        "performer": "",
        "specialist": "Кузнецов Илья Владимирович",
        "photos_link": topic_folder_link or "",
        "general_purpose": (
            "Осмотр выполнен методом визуального неразрушающего контроля. "
            "Цель осмотра — выявление фактически наблюдаемых дефектов, определение "
            "рекомендаций к устранению и возможных последствий для заказчика при "
            "сохранении текущего состояния объекта."
        ),
        "sections": sections_payload,
        "recommendations": recs[:20] if recs else ["Привести выявленные узлы и покрытия к нормативному состоянию по соответствующим СП/ГОСТ"],
        "consequences": cons[:10] if cons else ["Снижение несущей способности и эксплуатационной надёжности конструкций"],
        "violations_table": vtable[:30],
    }

    docx_ok = False
    pdf_ok = False
    try:
        _p6h_build_docx_act(payload, docx_local)
        docx_ok = True
    except Exception:
        _P6H_LOG.exception("P6H_DOCX_BUILD_FAIL")
    try:
        _p6h_build_pdf_act(payload, pdf_local)
        pdf_ok = True
    except Exception:
        _P6H_LOG.exception("P6H_PDF_BUILD_FAIL")

    drive_docx = None
    drive_pdf = None
    if docx_ok or pdf_ok:
        try:
            from core import technadzor_drive_index as _tdi
            if docx_ok:
                drive_docx = _tdi.upload_to_service_subfolder(
                    docx_local, docx_local.name, str(chat_id), int(topic_id), subfolder="_drafts",
                )
            if pdf_ok:
                drive_pdf = _tdi.upload_client_pdf_to_folder(
                    pdf_local, pdf_local.name, str(chat_id), int(topic_id), target_folder_name=None,
                )
        except Exception:
            _P6H_LOG.exception("P6H_UPLOAD_FAIL")

    pdf_link = (drive_pdf or {}).get("link", "") if drive_pdf else ""
    docx_link = (drive_docx or {}).get("link", "") if drive_docx else ""

    msg_lines = ["Акт сформирован"]
    if pdf_link:
        msg_lines.append(f"PDF: {pdf_link}")
    elif pdf_ok:
        msg_lines.append("PDF: подготовлен локально, загрузка на Drive не выполнена — повторная попытка через retry queue")
    else:
        msg_lines.append("PDF: ошибка генерации")
    if docx_link:
        msg_lines.append(f"DOCX (черновик, служебно): {docx_link}")
    if topic_folder_link:
        msg_lines.append(f"Фото: {topic_folder_link}")
    msg_lines.append("Норма: " + ("подтверждена" if global_norms else "не подтверждена"))

    return {
        "ok": True if (pdf_ok or docx_ok) else False,
        "handled": True,
        "kind": "technadzor_p6h_act",
        "state": "DONE" if pdf_link else "AWAITING_CONFIRMATION",
        "artifact_path": str(pdf_local if pdf_ok else docx_local),
        "extra_artifact_path": str(docx_local if docx_ok else ""),
        "drive_link": pdf_link or docx_link or "",
        "message": _p6h_clean_text("\n".join(msg_lines), 4000),
        "history": "P6H_ACT_DOCX_{}_PDF_{}_DRIVE_PDF_{}".format(
            "OK" if docx_ok else "FAIL",
            "OK" if pdf_ok else "FAIL",
            "OK" if pdf_link else "FAIL",
        ),
    }


# ────────────────────────────────────────────────────────────────────
# Sync wrapper around process_technadzor — only intercepts topic_5
# ────────────────────────────────────────────────────────────────────
def _p6h_is_image_path(path):
    if not path:
        return False
    p = str(path).lower()
    return p.endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp", ".heic"))


_P6H_ACT_TRIGGERS = (
    "сделай акт", "оформи акт", "выдай акт", "финальн", "акт по фото",
    "сформируй акт", "подготовь акт", "сделать акт", "оформить акт",
)


def _p6h_should_handle(topic_id, file_path, user_text):
    if int(topic_id or 0) != 5:
        return False
    if file_path and _p6h_is_image_path(file_path):
        return True
    low = (user_text or "").lower()
    if any(t in low for t in _P6H_ACT_TRIGGERS):
        return True
    return False


def _p6h_run_async(coro):
    """Run coro from sync context. Mimics codebase pattern."""
    try:
        return _p6h_asyncio.run(coro)
    except RuntimeError:
        # Already in a loop — schedule in a worker thread with its own loop
        import threading
        result = {"v": None, "exc": None}
        def _runner():
            new_loop = _p6h_asyncio.new_event_loop()
            try:
                _p6h_asyncio.set_event_loop(new_loop)
                result["v"] = new_loop.run_until_complete(coro)
            except Exception as e:
                result["exc"] = e
            finally:
                new_loop.close()
        t = threading.Thread(target=_runner, daemon=True)
        t.start()
        t.join()
        if result["exc"]:
            raise result["exc"]
        return result["v"]


try:
    _p6h_orig_process = process_technadzor
    if not getattr(_p6h_orig_process, "_p6h_wrapped", False):
        def process_technadzor(text="", task_id="", chat_id="", topic_id=0, file_path="", file_name="", **kwargs):
            try:
                if _p6h_should_handle(topic_id, file_path, text):
                    is_image = _p6h_is_image_path(file_path)
                    low = (text or "").lower()
                    make_act = any(t in low for t in _P6H_ACT_TRIGGERS)
                    if is_image or make_act:
                        return _p6h_run_async(
                            _p6h_process_photo_async(
                                file_path=file_path,
                                file_name=file_name,
                                task_id=task_id,
                                chat_id=chat_id,
                                topic_id=topic_id,
                                user_text=text,
                                make_act=make_act,
                            )
                        )
            except Exception:
                _P6H_LOG.exception("P6H_WRAPPER_FAIL — falling back to original")
            return _p6h_orig_process(
                text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id,
                file_path=file_path, file_name=file_name, **kwargs,
            )
        process_technadzor._p6h_wrapped = True
        _p6h_orig_process._p6h_wrapped = True
    _P6H_LOG.info("P6H_TOPIC5_USE_EXISTING_TEMPLATES_PHOTO_TO_TECH_REPORT_20260504_V1_INSTALLED")
except Exception as _exc:
    _P6H_LOG.exception("P6H_TOPIC5_INSTALL_FAIL: %s", _exc)
# === END_P6H_TOPIC5_USE_EXISTING_TEMPLATES_PHOTO_TO_TECH_REPORT_20260504_V1 ===


# === P6H_PART_2: PHOTO_NUMBER_DEFECT_NORM_CLARIFICATION_LOGIC + VOICE_LIVE_DIALOG_CLARIFICATION_GATE_20260504 ===
# Adds on top of P6H_PART_1:
# - voice transcript parser (extracts object_hint, folder_hint, visit_date_hint, client_facing flag, raw user-stated defects)
# - clarification gate (returns WAITING_CLARIFICATION with concrete questions, never «что строим?»)
# - photo-numbered Telegram output («Фото №N — <file>»)
# - 8-column violations_table for акты
# - memory summary write after DONE (key topic_5_technadzor_photo_report_summary)
# - replaces _p6h_process_photo_async with enhanced version
import re as _p6h2_re
import json as _p6h2_json

_P6H2_LOG = _p6h_logging.getLogger("task_worker")

_P6H2_FOLDER_HINT_PATTERNS = [
    _p6h2_re.compile(r"папк[аеу]?\s+[«\"\'']?([^«»\"\'\.,;\n]{2,80})[»\"\'']?", _p6h2_re.IGNORECASE),
    _p6h2_re.compile(r"директор[ияю]?\s+[«\"\'']?([^«»\"\'\.,;\n]{2,80})[»\"\'']?", _p6h2_re.IGNORECASE),
]
_P6H2_OBJECT_HINTS = [
    "ангар", "склад", "цех", "корпус", "коттедж", "дом", "здание", "сооружение",
    "фундамент", "кровл", "фасад", "перекрыт", "колонн", "балк", "ферм", "плита",
    "паркинг", "гараж", "трибун", "купол", "теплиц",
]
_P6H2_DATE_RE = _p6h2_re.compile(
    r"(?P<d>\d{1,2})[\s\-./](?P<m>\d{1,2}|январ|феврал|март|апрел|ма[яй]|июн|июл|август|сентябр|октябр|ноябр|декабр)[\s\-./а-я]*?(?P<y>\d{2,4})?",
    _p6h2_re.IGNORECASE,
)
_P6H2_CLIENT_HINTS = ("заказчик", "клиент", "генподряд", "застройщ", "владельцу объекта")
_P6H2_INTERNAL_HINTS = ("служебн", "не для клиента", "черновик", "внутрен", "тестов", "smoke")


def _p6h_parse_voice_instruction(raw_input):
    """Parse [VOICE] transcript into structured TZ context.

    Returns dict with keys:
      object_hint, folder_hint, visit_date_hint, client_facing,
      explicit_include, explicit_exclude, output_kind, requires_act
    All values are conservative — present only when transcript explicitly mentioned them.
    """
    text = (raw_input or "").strip()
    if text.startswith("[VOICE]"):
        text_body = text[len("[VOICE]"):].strip()
    else:
        text_body = text
    low = text_body.lower()
    ctx = {
        "is_voice": text.startswith("[VOICE]"),
        "transcript": text_body,
        "object_hint": "",
        "folder_hint": "",
        "visit_date_hint": "",
        "client_facing": None,  # None=unknown, True/False=explicit
        "explicit_include": [],
        "explicit_exclude": [],
        "output_kind": "",  # text|act|pdf|docx|description
        "requires_act": False,
    }
    if not text_body:
        return ctx

    # Object
    for h in _P6H2_OBJECT_HINTS:
        if h in low:
            ctx["object_hint"] = h
            break

    # Folder hint
    for pat in _P6H2_FOLDER_HINT_PATTERNS:
        m = pat.search(text_body)
        if m:
            ctx["folder_hint"] = m.group(1).strip()
            break

    # Date hint
    m = _P6H2_DATE_RE.search(text_body)
    if m:
        ctx["visit_date_hint"] = m.group(0).strip()

    # Client-facing
    if any(h in low for h in _P6H2_CLIENT_HINTS):
        ctx["client_facing"] = True
    if any(h in low for h in _P6H2_INTERNAL_HINTS):
        ctx["client_facing"] = False

    # Output
    if any(t in low for t in _P6H_ACT_TRIGGERS):
        ctx["requires_act"] = True
        ctx["output_kind"] = "act"
    elif "pdf" in low or "пдф" in low:
        ctx["output_kind"] = "pdf"
    elif "docx" in low or "ворд" in low or "word" in low:
        ctx["output_kind"] = "docx"
    elif "описан" in low or "опиши" in low or "посмотри" in low:
        ctx["output_kind"] = "description"

    # Explicit include/exclude lists
    for marker, key in (("включ", "explicit_include"), ("не включ", "explicit_exclude"),
                         ("исключ", "explicit_exclude")):
        i = low.find(marker)
        if i >= 0:
            tail = text_body[i:i + 240]
            ctx[key].append(tail.strip())
    return ctx


def _p6h_should_wait_for_clarification(vision, defects, voice_ctx, drive_idx):
    """Returns (should_wait: bool, questions: [str]).

    Triggers:
      • Vision confidence=LOW AND no defects → ask what's on the photo, before/after, side
      • voice_ctx folder_hint set but folder not in Drive index
      • voice_ctx client_facing is None AND folder_hint set (need to know if it's customer-visible)
    Never asks "что строим?" / "что это?" / "пришлите шаблон".
    """
    questions = []
    confidence = (vision or {}).get("confidence", "LOW") if isinstance(vision, dict) else "LOW"
    nd = len(defects or [])

    # 1. Folder named by owner — check it exists
    fh = (voice_ctx or {}).get("folder_hint", "").strip()
    if fh:
        folders = []
        for f in (drive_idx or {}).get("folders_client", []) + (drive_idx or {}).get("folders_system", []):
            folders.append(f.get("name", ""))
        if not any(fh.lower() == n.lower() or fh.lower() in n.lower() for n in folders if n):
            questions.append(
                f"Не нашёл папку «{fh}» в Drive topic_5. "
                "Уточни точное имя или создай её перед загрузкой фото"
            )

    # 2. Folder client_facing flag uncertain
    if fh and (voice_ctx or {}).get("client_facing") is None:
        questions.append(
            f"Папку «{fh}» считать клиентской (туда складывать только фото и чистовой PDF) "
            "или служебной (тогда туда можно DOCX-черновик)?"
        )

    # 3. Vision low-confidence + no defects on a photo
    if confidence == "LOW" and nd == 0:
        questions.append(
            "Фото не позволяет однозначно определить дефект. "
            "Это до или после исправления? С какой стороны конструкции снято? "
            "Что именно нужно зафиксировать на этом фото?"
        )

    # Never trigger generic clarifier
    return (bool(questions), questions)


def _p6h_save_summary_to_memory(chat_id, topic_id, summary_dict):
    """Persist a compact summary to memory.db under topic_5_technadzor_photo_report_summary.

    Uses task_worker._save_memory_safe if exposed; falls back to direct memory_client write.
    Stores ONLY: folder, object, date, owner_directives, defect_brief, pdf_link, status.
    """
    try:
        payload = {
            "folder": str(summary_dict.get("folder") or "")[:200],
            "object": str(summary_dict.get("object") or "")[:200],
            "date": str(summary_dict.get("date") or "")[:40],
            "owner_directives": (summary_dict.get("owner_directives") or [])[:6],
            "defect_brief": (summary_dict.get("defect_brief") or [])[:12],
            "pdf_link": str(summary_dict.get("pdf_link") or "")[:400],
            "docx_link": str(summary_dict.get("docx_link") or "")[:400],
            "status": str(summary_dict.get("status") or "")[:60],
            "ts": int(_p6h_dt.now().timestamp()),
        }
        body = _p6h2_json.dumps(payload, ensure_ascii=False)[:4000]
    except Exception:
        return False
    try:
        from core.memory_client import save_memory  # type: ignore
        key = f"topic_{int(topic_id or 5)}_technadzor_photo_report_summary"
        save_memory(chat_id=str(chat_id), key=key, value=body)
        return True
    except Exception:
        try:
            import sqlite3 as _sql
            db = _P6H_BASE / "data" / "memory.db"
            con = _sql.connect(str(db))
            cur = con.cursor()
            cur.execute(
                "INSERT INTO memory(chat_id,key,value,timestamp) VALUES (?,?,?,strftime('%s','now'))",
                (str(chat_id), f"topic_{int(topic_id or 5)}_technadzor_photo_report_summary", body),
            )
            con.commit()
            con.close()
            return True
        except Exception:
            _P6H2_LOG.exception("P6H2_MEMORY_SAVE_FAIL")
            return False


def _p6h_format_photo_numbered_response(vision, defects, grouped, global_norms, file_name, photo_no=1, voice_ctx=None):
    """Build per-photo numbered Telegram text per spec section 'Формат текстового ответа без акта'."""
    fname = str(file_name or "photo")
    out = ["Технический осмотр по фото", ""]
    if voice_ctx and (voice_ctx.get("folder_hint") or voice_ctx.get("object_hint")):
        out.append("Объект / папка:")
        parts = []
        if voice_ctx.get("object_hint"):
            parts.append(voice_ctx["object_hint"])
        if voice_ctx.get("folder_hint"):
            parts.append(f"папка «{voice_ctx['folder_hint']}»")
        if voice_ctx.get("visit_date_hint"):
            parts.append(f"дата {voice_ctx['visit_date_hint']}")
        out.append(" / ".join(parts))
        out.append("")

    out.append(f"Фото №{photo_no} — {fname}")

    summary = (vision or {}).get("summary", "") if isinstance(vision, dict) else ""
    out.append("Что видно:")
    if summary:
        out.append(_p6h_clean_text(summary, 600))
    else:
        out.append("по фото однозначно не определяется")

    out.append("")
    out.append("Замечание:")
    if grouped:
        per_section = []
        for sec_title, ds in grouped:
            tt = []
            for d in ds:
                t = str(d.get("title") or d.get("description") or "").strip()
                if t:
                    tt.append(t[:120])
            per_section.append(f"— {sec_title}: " + ("; ".join(tt) if tt else "замечания зафиксированы"))
        out.extend(per_section)
    else:
        out.append("Дефектов на фото не выявлено")

    out.append("")
    out.append("Чем опасно:")
    risks = []
    for d in defects or []:
        r = str(d.get("risk") or d.get("why") or d.get("severity") or d.get("impact") or "").strip()
        if r:
            risks.append("— " + r[:200])
    if risks:
        out.extend(risks[:6])
    elif grouped:
        out.append("Зафиксированные отклонения снижают эксплуатационную надёжность и/или несущую способность конструкции")
    else:
        out.append("Отклонений не выявлено")

    out.append("")
    out.append("Как исправить:")
    fixes = []
    for d in defects or []:
        f = str(d.get("recommended_fix") or d.get("fix") or d.get("recommendation") or "").strip()
        if f:
            fixes.append("— " + f[:200])
    if fixes:
        out.extend(fixes[:6])
    else:
        out.append("Привести к нормативному состоянию по соответствующим СП/ГОСТ; уточнить решения по проектной документации")

    out.append("")
    out.append("Что проверить:")
    checks = []
    for d in defects or []:
        c = d.get("site_checks") or d.get("verify") or d.get("check")
        if isinstance(c, list):
            for x in c[:3]:
                xs = str(x).strip()
                if xs:
                    checks.append("— " + xs[:200])
        elif c:
            checks.append("— " + str(c)[:200])
    if checks:
        out.extend(checks[:6])
    else:
        out.append("Состояние конструкции в полном объёме, исполнительная документация, ранее выданные предписания")

    out.append("")
    out.append("Нормативная отсылка:")
    if global_norms:
        for n in global_norms[:5]:
            out.append("— " + str(n.get("norm_id", "")) + ": " + str(n.get("section", "")) + f" [{n.get('confidence', 'PARTIAL')}]")
    else:
        out.append("норма не подтверждена")

    out.append("")
    out.append("Итог:")
    crit = [d for d in (defects or []) if str(d.get("severity", "")).lower() in ("high", "critical", "критическ", "high_risk")]
    out.append(f"— критичные замечания: {len(crit)}")
    out.append(f"— рабочие замечания: {len(defects or []) - len(crit)}")
    out.append("— нужен ли акт: могу оформить акт по текущим фото — напиши «сделай акт»")

    return _p6h_clean_text("\n".join(out), 6000)


# Override _p6h_process_photo_async with the enhanced version
async def _p6h_process_photo_async(file_path, file_name, task_id, chat_id, topic_id, user_text="", make_act=False, place="", object_descr=""):
    # 1. Drive index — best-effort eager build
    try:
        from core import technadzor_drive_index as _tdi
        idx = _tdi.build_technadzor_template_index(str(chat_id), int(topic_id), force=False)
    except Exception:
        idx = {}

    # 2. Voice transcript parsing
    voice_ctx = _p6h_parse_voice_instruction(user_text or "")

    # 3. Vision
    vision, vstatus = await _p6f_tnz_vision_via_openrouter(file_path)
    if vstatus == "FAIL" or vision is None:
        return {
            "ok": False, "handled": True, "kind": "technadzor_p6h_photo",
            "state": "WAITING_CLARIFICATION",
            "message": "Не удалось проанализировать фото через Vision. "
                       "Пришли крупнее или короткое описание дефекта текстом",
            "history": "P6H_VISION_FAIL",
        }

    summary = (vision.get("summary") or "").strip() if isinstance(vision, dict) else ""
    defects = (vision.get("defects") or []) if isinstance(vision, dict) else []

    # Tag defects with photo_no/file_name (single-photo task = #1)
    photo_no = 1
    for d in defects:
        if isinstance(d, dict):
            d.setdefault("photo_no", photo_no)
            d.setdefault("file_name", file_name or "")

    grouped = _p6h_group_defects_by_section(defects)

    # 4. Clarification gate
    should_wait, questions = _p6h_should_wait_for_clarification(vision, defects, voice_ctx, idx)
    if should_wait and not make_act:
        return {
            "ok": True, "handled": True, "kind": "technadzor_p6h_clarify",
            "state": "WAITING_CLARIFICATION",
            "message": _p6h_clean_text(
                "Технадзор topic_5 — нужны уточнения перед разбором:\n\n" + "\n".join(f"— {q}" for q in questions),
                3000,
            ),
            "history": "P6H_CLARIFY:{}".format(len(questions)),
        }

    # 5. Norms
    haystack = " ".join([
        summary, voice_ctx.get("transcript", "") or "",
    ] + [str(d.get("title", "")) + " " + str(d.get("description", "")) for d in defects])
    global_norms = _p6h_norms_for_haystack(haystack)

    # 6. Per-section payload
    sections_payload = []
    for sec_title, ds in grouped:
        defect_texts = [str(d.get("title", "")) + " " + str(d.get("description", "")) for d in ds]
        snorms = _p6h_norms_for_section(sec_title, defect_texts)
        sections_payload.append({
            "title": sec_title,
            "defects": ds,
            "norms": snorms,
            "photos_block": [str(file_name or "")] if file_name else [],
        })

    topic_folder_link = (idx or {}).get("topic_folder_link", "")

    # 7a. Photo-only response (numbered format)
    if not make_act:
        msg = _p6h_format_photo_numbered_response(
            vision, defects, grouped, global_norms, file_name or "photo",
            photo_no=photo_no, voice_ctx=voice_ctx,
        )
        # Save compact summary to memory
        _p6h_save_summary_to_memory(chat_id, topic_id, {
            "folder": voice_ctx.get("folder_hint") or "",
            "object": voice_ctx.get("object_hint") or "",
            "date": voice_ctx.get("visit_date_hint") or "",
            "owner_directives": (voice_ctx.get("explicit_include") or []) + (voice_ctx.get("explicit_exclude") or []),
            "defect_brief": [str(d.get("title") or d.get("description") or "")[:200] for d in defects][:8],
            "pdf_link": "",
            "docx_link": "",
            "status": "PHOTO_REPORT_DONE",
        })
        return {
            "ok": True, "handled": True, "kind": "technadzor_p6h_photo",
            "state": "DONE",
            "message": msg,
            "history": "P6H_PHOTO_REPORT_PHOTO{}_DEFECTS_{}_NORMS_{}".format(photo_no, len(defects), len(global_norms)),
        }

    # 7b. Build act: DOCX (service) + PDF (client topic root) + upload
    ts = _p6h_dt.now().strftime("%Y%m%d_%H%M%S")
    safe_tid = (str(task_id or ts)[:8] or ts).replace("/", "_").replace("\\", "_")
    docx_local = _P6H_OUTDIR / f"P6H_TNZ_ACT_DRAFT__{safe_tid}_{ts}.docx"
    pdf_local = _P6H_OUTDIR / f"АКТ_ОСМОТРА__{safe_tid}_{ts}.pdf"

    recs = []
    cons = []
    for d in defects:
        r = str(d.get("recommended_fix") or d.get("fix") or d.get("recommendation") or "").strip()
        if r:
            recs.append(r[:300])
        c = str(d.get("consequence") or d.get("risk") or d.get("why") or "").strip()
        if c:
            cons.append(c[:300])

    # 8-column violations table per spec
    violations_8 = []
    for sec_title, ds in grouped:
        for d in ds:
            num = len(violations_8) + 1
            ph = str(d.get("file_name") or file_name or "")
            place_node = sec_title
            violation = str(d.get("title") or d.get("description") or sec_title)[:200]
            consequence = str(d.get("consequence") or d.get("risk") or "")[:200]
            fix = str(d.get("recommended_fix") or d.get("fix") or "")[:200]
            # find norm for this defect's section
            norm_id = ""
            for s in sections_payload:
                if s["title"] == sec_title and s["norms"]:
                    norm_id = s["norms"][0].get("norm_id", "") or ""
                    break
            status = ""
            conf = (vision or {}).get("confidence", "LOW")
            if conf == "HIGH" and norm_id:
                status = "CONFIRMED_BY_PHOTO"
            elif conf in ("HIGH", "MEDIUM") and not norm_id:
                status = "NORM_NOT_CONFIRMED"
            elif conf == "MEDIUM":
                status = "PARTIAL_BY_PHOTO"
            else:
                status = "NEEDS_OWNER_CLARIFICATION"
            violations_8.append((num, ph, place_node, violation, consequence, fix, norm_id or "норма не подтверждена", status))

    payload = {
        "act_number": _p6h_human_act_number(task_id),
        "date_str": _p6h_dt.now().strftime("%d.%m.%Y"),
        "place": place or (voice_ctx.get("folder_hint") or "место уточняется по запросу владельца"),
        "object_descr": object_descr or (voice_ctx.get("object_hint") or "объект уточняется по запросу владельца"),
        "method": "визуальный неразрушающий контроль с выездом на объект",
        "performer": "",
        "specialist": "Кузнецов Илья Владимирович",
        "photos_link": topic_folder_link or "",
        "general_purpose": (
            "Осмотр выполнен методом визуального неразрушающего контроля. "
            "Цель осмотра — выявление фактически наблюдаемых дефектов, определение "
            "рекомендаций к устранению и возможных последствий для заказчика."
        ),
        "sections": sections_payload,
        "recommendations": (recs[:20] if recs else
                             ["Привести выявленные узлы и покрытия к нормативному состоянию по соответствующим СП/ГОСТ"]),
        "consequences": (cons[:10] if cons else
                          ["Снижение несущей способности и эксплуатационной надёжности конструкций"]),
        # 8-col rich table
        "violations_table_8col": violations_8[:30],
        # 3-col simple table (back-compat for DOCX/PDF builders that use violations_table)
        "violations_table": [(v, n, p) for (_no, p, _pl, v, _co, _fi, n, _st) in violations_8[:30]],
    }

    docx_ok = False
    pdf_ok = False
    try:
        _p6h_build_docx_act(payload, docx_local)
        docx_ok = True
    except Exception:
        _P6H2_LOG.exception("P6H2_DOCX_BUILD_FAIL")
    try:
        _p6h_build_pdf_act(payload, pdf_local)
        pdf_ok = True
    except Exception:
        _P6H2_LOG.exception("P6H2_PDF_BUILD_FAIL")

    drive_docx = None
    drive_pdf = None
    if docx_ok or pdf_ok:
        try:
            from core import technadzor_drive_index as _tdi2
            if docx_ok:
                drive_docx = _tdi2.upload_to_service_subfolder(
                    docx_local, docx_local.name, str(chat_id), int(topic_id), subfolder="_drafts",
                )
            if pdf_ok:
                target_folder = None
                # Owner explicitly named a client folder for the final PDF?
                fh = voice_ctx.get("folder_hint", "") or ""
                if fh:
                    # Only allow target placement if folder is explicitly client-facing per voice
                    if voice_ctx.get("client_facing") is True:
                        from core.technadzor_drive_index import is_system_folder as _is_sys
                        if not _is_sys(fh):
                            target_folder = fh
                drive_pdf = _tdi2.upload_client_pdf_to_folder(
                    pdf_local, pdf_local.name, str(chat_id), int(topic_id),
                    target_folder_name=target_folder,
                )
        except Exception:
            _P6H2_LOG.exception("P6H2_UPLOAD_FAIL")

    pdf_link = (drive_pdf or {}).get("link", "") if drive_pdf else ""
    docx_link = (drive_docx or {}).get("link", "") if drive_docx else ""

    msg_lines = ["Акт сформирован"]
    if pdf_link:
        msg_lines.append(f"PDF: {pdf_link}")
    elif pdf_ok:
        msg_lines.append("PDF: подготовлен локально, загрузка на Drive не выполнена — Telegram fallback в следующей итерации")
    else:
        msg_lines.append("PDF: ошибка генерации — повторите позже")
    if docx_link:
        msg_lines.append(f"DOCX (черновик, служебно): {docx_link}")
    if topic_folder_link:
        msg_lines.append(f"Фото: {topic_folder_link}")
    msg_lines.append("Норма: " + ("подтверждена" if global_norms else "не подтверждена"))

    # Memory save
    _p6h_save_summary_to_memory(chat_id, topic_id, {
        "folder": voice_ctx.get("folder_hint") or "",
        "object": voice_ctx.get("object_hint") or "",
        "date": voice_ctx.get("visit_date_hint") or "",
        "owner_directives": (voice_ctx.get("explicit_include") or []) + (voice_ctx.get("explicit_exclude") or []),
        "defect_brief": [str(d.get("title") or d.get("description") or "")[:200] for d in defects][:8],
        "pdf_link": pdf_link,
        "docx_link": docx_link,
        "status": "ACT_DONE" if pdf_link else ("ACT_PARTIAL" if (pdf_ok or docx_ok) else "ACT_FAIL"),
    })

    return {
        "ok": True if (pdf_ok or docx_ok) else False,
        "handled": True,
        "kind": "technadzor_p6h_act",
        "state": "DONE" if pdf_link else "AWAITING_CONFIRMATION",
        "artifact_path": str(pdf_local if pdf_ok else docx_local),
        "extra_artifact_path": str(docx_local if docx_ok else ""),
        "drive_link": pdf_link or docx_link or "",
        "message": _p6h_clean_text("\n".join(msg_lines), 4000),
        "history": "P6H_ACT_DOCX_{}_PDF_{}_DRIVE_PDF_{}".format(
            "OK" if docx_ok else "FAIL",
            "OK" if pdf_ok else "FAIL",
            "OK" if pdf_link else "FAIL",
        ),
    }


_P6H2_LOG.info("P6H_TOPIC5_PHOTO_NUMBER_DEFECT_NORM_CLARIFICATION_LOGIC_20260504_INSTALLED")
_P6H2_LOG.info("P6H_TOPIC5_VOICE_LIVE_DIALOG_CLARIFICATION_GATE_20260504_INSTALLED")
# === END_P6H_PART_2 ===


# === P6H_PART_3: TOPIC5_OBJECT_REGISTRY_INSPECTION_CHAIN_20260504 ===
# Final wiring of object registry into the photo pipeline.
# Replaces _p6h_process_photo_async with a registry-aware version that:
#   • Identifies object_id from voice/Drive/file_name signals.
#   • Loads existing card and prior inspection_chain.
#   • Detects visit_mode (initial / repeat / extension / description_only).
#   • Adds clarification questions when object_id is ambiguous OR when voice/Vision conflict.
#   • For follow-up acts: carries forward open_items with statuses
#     (УСТРАНЕНО / УСТРАНЕНО ЧАСТИЧНО / НЕ УСТРАНЕНО / ТРЕБУЕТ УТОЧНЕНИЯ / ...).
#   • After the act is built, appends an inspection record to the chain
#     (server JSON + memory + timeline).
#   • Never writes registry/system files into client-facing folders.

try:
    from core import technadzor_object_registry as _p6h3_reg
except Exception as _exc_reg:
    _p6h3_reg = None
    _P6H2_LOG.warning("P6H3_REGISTRY_IMPORT_FAIL: %s", _exc_reg)


async def _p6h_process_photo_async(file_path, file_name, task_id, chat_id, topic_id, user_text="", make_act=False, place="", object_descr=""):
    # 1. Drive index
    try:
        from core import technadzor_drive_index as _tdi
        idx = _tdi.build_technadzor_template_index(str(chat_id), int(topic_id), force=False)
    except Exception:
        idx = {}

    # 2. Voice context
    voice_ctx = _p6h_parse_voice_instruction(user_text or "")

    # 3. Object registry — identify object_id
    object_id = ""
    object_card = None
    visit_mode = "initial"
    derive_sources = {}
    if _p6h3_reg is not None:
        try:
            object_id, derive_sources = _p6h3_reg.derive_object_id_from_context(
                voice_ctx, idx, file_path or "", file_name or "",
            )
            if object_id:
                object_card = _p6h3_reg.load_object(object_id)
            visit_mode = _p6h3_reg.detect_visit_mode(object_card, voice_ctx)
        except Exception:
            _P6H2_LOG.exception("P6H3_REGISTRY_DERIVE_FAIL")

    # 4. Vision
    vision, vstatus = await _p6f_tnz_vision_via_openrouter(file_path)
    if vstatus == "FAIL" or vision is None:
        return {
            "ok": False, "handled": True, "kind": "technadzor_p6h_photo",
            "state": "WAITING_CLARIFICATION",
            "message": "Не удалось проанализировать фото через Vision. "
                       "Пришли крупнее или короткое описание дефекта текстом",
            "history": "P6H_VISION_FAIL",
        }

    summary = (vision.get("summary") or "").strip() if isinstance(vision, dict) else ""
    defects = (vision.get("defects") or []) if isinstance(vision, dict) else []
    photo_no = 1
    for d in defects:
        if isinstance(d, dict):
            d.setdefault("photo_no", photo_no)
            d.setdefault("file_name", file_name or "")

    grouped = _p6h_group_defects_by_section(defects)

    # 5. Clarification gate (registry + Vision + voice/Vision conflict)
    should_wait_basic, basic_questions = _p6h_should_wait_for_clarification(vision, defects, voice_ctx, idx)
    questions = list(basic_questions)

    # Object identity question — only if no folder/object hints AND no object_id derived
    if not object_id and not voice_ctx.get("folder_hint") and not voice_ctx.get("object_hint"):
        existing_summaries = []
        if _p6h3_reg is not None:
            try:
                existing_summaries = _p6h3_reg.list_object_summaries()
            except Exception:
                existing_summaries = []
        if existing_summaries:
            names = ", ".join(
                f"«{e.get('object_name') or e.get('object_id')}»"
                for e in existing_summaries[:5]
            )
            questions.append(
                f"Это новый объект или продолжение одного из существующих ({names})? "
                "Уточни — иначе не смогу привязать к истории объекта"
            )
        else:
            questions.append(
                "Назови объект (адрес / папка / имя), чтобы я завёл карточку и привязал акт"
            )

    # Voice/Vision conflict
    if _p6h3_reg is not None and voice_ctx.get("transcript"):
        try:
            conflict_flags = _p6h3_reg.detect_voice_vision_conflict(voice_ctx, grouped)
        except Exception:
            conflict_flags = []
        for cf in conflict_flags:
            if cf not in questions:
                questions.append(cf)
    else:
        conflict_flags = []

    # If photo-only mode AND we have questions — return WAITING_CLARIFICATION
    if questions and not make_act:
        return {
            "ok": True, "handled": True, "kind": "technadzor_p6h_clarify",
            "state": "WAITING_CLARIFICATION",
            "message": _p6h_clean_text(
                "Технадзор topic_5 — нужны уточнения перед разбором:\n\n"
                + "\n".join(f"— {q}" for q in questions),
                3000,
            ),
            "history": "P6H_CLARIFY_WITH_REGISTRY:{}_visit_{}".format(len(questions), visit_mode),
        }

    # 6. Norms
    haystack = " ".join([
        summary, voice_ctx.get("transcript", "") or "",
    ] + [str(d.get("title", "")) + " " + str(d.get("description", "")) for d in defects])
    global_norms = _p6h_norms_for_haystack(haystack)

    # 7. Sections payload
    sections_payload = []
    for sec_title, ds in grouped:
        defect_texts = [str(d.get("title", "")) + " " + str(d.get("description", "")) for d in ds]
        snorms = _p6h_norms_for_section(sec_title, defect_texts)
        sections_payload.append({
            "title": sec_title,
            "defects": ds,
            "norms": snorms,
            "photos_block": [str(file_name or "")] if file_name else [],
        })

    topic_folder_link = (idx or {}).get("topic_folder_link", "")

    # 7a. Photo-only response (numbered) ── append registry context if known
    if not make_act:
        msg = _p6h_format_photo_numbered_response(
            vision, defects, grouped, global_norms, file_name or "photo",
            photo_no=photo_no, voice_ctx=voice_ctx,
        )
        if object_id and object_card:
            registry_tail = (
                "\n\nКарточка объекта: "
                f"{object_card.get('object_name') or object_id}"
                f" (осмотров в истории: {len(object_card.get('inspection_chain') or [])})"
            )
            msg = (msg + registry_tail).strip()

        # Update memory summary
        try:
            _p6h_save_summary_to_memory(chat_id, topic_id, {
                "folder": voice_ctx.get("folder_hint") or "",
                "object": voice_ctx.get("object_hint") or object_id or "",
                "date": voice_ctx.get("visit_date_hint") or "",
                "owner_directives": (voice_ctx.get("explicit_include") or []) + (voice_ctx.get("explicit_exclude") or []),
                "defect_brief": [str(d.get("title") or d.get("description") or "")[:200] for d in defects][:8],
                "pdf_link": "",
                "docx_link": "",
                "status": f"PHOTO_REPORT_DONE:visit={visit_mode}",
            })
        except Exception:
            pass

        return {
            "ok": True, "handled": True, "kind": "technadzor_p6h_photo",
            "state": "DONE",
            "message": msg,
            "history": "P6H_PHOTO_REPORT_PHOTO{}_DEFECTS_{}_NORMS_{}_VISIT_{}".format(
                photo_no, len(defects), len(global_norms), visit_mode,
            ),
        }

    # 7b. Act build — DOCX (service _drafts) + PDF (client topic root or named client folder)
    ts = _p6h_dt.now().strftime("%Y%m%d_%H%M%S")
    safe_tid = (str(task_id or ts)[:8] or ts).replace("/", "_").replace("\\", "_")
    docx_local = _P6H_OUTDIR / f"P6H_TNZ_ACT_DRAFT__{safe_tid}_{ts}.docx"
    pdf_local = _P6H_OUTDIR / f"АКТ_ОСМОТРА__{safe_tid}_{ts}.pdf"

    # Recommendations / consequences
    recs, cons = [], []
    for d in defects:
        r = str(d.get("recommended_fix") or d.get("fix") or d.get("recommendation") or "").strip()
        if r:
            recs.append(r[:300])
        c = str(d.get("consequence") or d.get("risk") or d.get("why") or "").strip()
        if c:
            cons.append(c[:300])

    # Carry forward open_items for follow-up acts
    carried_open_items = []
    if _p6h3_reg is not None and visit_mode in ("repeat", "extension"):
        try:
            carried_open_items = _p6h3_reg.carry_forward_open_items(object_card, defects)
        except Exception:
            carried_open_items = []

    # Build follow-up section payload (added before regular sections in act)
    if carried_open_items:
        follow_section = {
            "title": "Состояние ранее выданных замечаний (повторный осмотр)",
            "defects": [
                {
                    "title": f"[{it.get('status','?')}] {it.get('title','') or it.get('description','')}",
                    "description": (it.get("description", "") or "")[:300]
                                    + (f" (из акта № {it.get('from_act_no')})" if it.get("from_act_no") else ""),
                }
                for it in carried_open_items
            ],
            "norms": [],
            "photos_block": [],
        }
        sections_payload.insert(0, follow_section)

    # 8-column violations table
    violations_8 = []
    for sec_title, ds in grouped:
        for d in ds:
            num = len(violations_8) + 1
            ph = str(d.get("file_name") or file_name or "")
            place_node = sec_title
            violation = str(d.get("title") or d.get("description") or sec_title)[:200]
            consequence = str(d.get("consequence") or d.get("risk") or "")[:200]
            fix = str(d.get("recommended_fix") or d.get("fix") or "")[:200]
            norm_id = ""
            for s in sections_payload:
                if s["title"] == sec_title and s["norms"]:
                    norm_id = s["norms"][0].get("norm_id", "") or ""
                    break
            conf = (vision or {}).get("confidence", "LOW")
            if conf == "HIGH" and norm_id:
                status = "CONFIRMED_BY_PHOTO"
            elif conf in ("HIGH", "MEDIUM") and not norm_id:
                status = "NORM_NOT_CONFIRMED"
            elif conf == "MEDIUM":
                status = "PARTIAL_BY_PHOTO"
            else:
                status = "NEEDS_OWNER_CLARIFICATION"
            violations_8.append((num, ph, place_node, violation, consequence, fix, norm_id or "норма не подтверждена", status))

    # Determine general_purpose by visit_mode
    if visit_mode == "repeat":
        gen_purpose = (
            "Повторный осмотр выполнен в развитие предыдущих актов по объекту. "
            "Цель — фиксация выполненных исправлений и неустранённых замечаний, "
            "определение рекомендаций к доведению конструктивных решений до нормативного состояния."
        )
    elif visit_mode == "extension":
        gen_purpose = (
            "Дополнение к предыдущему акту по объекту. "
            "Фиксируются дополнительные материалы и замечания, обнаруженные после основного осмотра."
        )
    else:
        gen_purpose = (
            "Осмотр выполнен методом визуального неразрушающего контроля. "
            "Цель осмотра — выявление фактически наблюдаемых дефектов, определение "
            "рекомендаций к устранению и возможных последствий для заказчика."
        )

    # Act number — for follow-up, hint at parent
    act_number = _p6h_human_act_number(task_id)
    if visit_mode == "repeat" and object_card and (object_card.get("last_act_no") or ""):
        act_number = act_number + f" (в развитие акта № {object_card['last_act_no']})"

    payload = {
        "act_number": act_number,
        "date_str": _p6h_dt.now().strftime("%d.%m.%Y"),
        "place": place or (voice_ctx.get("folder_hint") or "место уточняется по запросу владельца"),
        "object_descr": object_descr or (voice_ctx.get("object_hint") or
                                          (object_card.get("object_name") if object_card else "")
                                          or "объект уточняется по запросу владельца"),
        "method": "визуальный неразрушающий контроль с выездом на объект",
        "performer": "",
        "specialist": "Кузнецов Илья Владимирович",
        "photos_link": topic_folder_link or "",
        "general_purpose": gen_purpose,
        "sections": sections_payload,
        "recommendations": (recs[:20] if recs else
                             ["Привести выявленные узлы и покрытия к нормативному состоянию по соответствующим СП/ГОСТ"]),
        "consequences": (cons[:10] if cons else
                          ["Снижение несущей способности и эксплуатационной надёжности конструкций"]),
        "violations_table_8col": violations_8[:30],
        "violations_table": [(v, n, p) for (_no, p, _pl, v, _co, _fi, n, _st) in violations_8[:30]],
    }

    # Build files
    docx_ok = pdf_ok = False
    try:
        _p6h_build_docx_act(payload, docx_local)
        docx_ok = True
    except Exception:
        _P6H2_LOG.exception("P6H3_DOCX_BUILD_FAIL")
    try:
        _p6h_build_pdf_act(payload, pdf_local)
        pdf_ok = True
    except Exception:
        _P6H2_LOG.exception("P6H3_PDF_BUILD_FAIL")

    # Upload — DOCX → _drafts (system).  PDF → client folder if explicitly named, else topic root.
    drive_docx = drive_pdf = None
    if docx_ok or pdf_ok:
        try:
            from core import technadzor_drive_index as _tdi2
            if docx_ok:
                drive_docx = _tdi2.upload_to_service_subfolder(
                    docx_local, docx_local.name, str(chat_id), int(topic_id), subfolder="_drafts",
                )
            if pdf_ok:
                target_folder = None
                fh = voice_ctx.get("folder_hint", "") or ""
                if fh and voice_ctx.get("client_facing") is True:
                    from core.technadzor_drive_index import is_system_folder as _is_sys
                    if not _is_sys(fh):
                        target_folder = fh
                drive_pdf = _tdi2.upload_client_pdf_to_folder(
                    pdf_local, pdf_local.name, str(chat_id), int(topic_id),
                    target_folder_name=target_folder,
                )
        except Exception:
            _P6H2_LOG.exception("P6H3_UPLOAD_FAIL")

    pdf_link = (drive_pdf or {}).get("link", "") if drive_pdf else ""
    docx_link = (drive_docx or {}).get("link", "") if drive_docx else ""

    # Record inspection in chain
    if _p6h3_reg is not None and (object_id or pdf_ok or docx_ok):
        try:
            # If we still don't have object_id by here (e.g., act forced through),
            # create a synthetic stable id from file/date so chain still records.
            if not object_id:
                object_id = _p6h3_reg._slug(
                    voice_ctx.get("object_hint") or
                    voice_ctx.get("folder_hint") or
                    (file_name.rsplit(".", 1)[0] if file_name else "") or
                    f"obj_{ts}"
                )
            new_open = []
            for sec_title, ds in grouped:
                for d in ds:
                    new_open.append({
                        "title": str(d.get("title") or "")[:200],
                        "description": str(d.get("description") or "")[:300],
                        "section": sec_title,
                        "act_no": payload["act_number"],
                    })
            _p6h3_reg.record_inspection(
                object_id, str(chat_id),
                act_no=payload["act_number"],
                date_str=payload["date_str"],
                mode=visit_mode,
                pdf_link=pdf_link,
                docx_link=docx_link,
                source_photo_folder=voice_ctx.get("folder_hint") or "",
                findings=[{"section": s["title"],
                            "defects": s["defects"][:10],
                            "norms": [n.get("norm_id") for n in (s.get("norms") or [])]}
                           for s in sections_payload],
                open_items=new_open,
                closed_items=[
                    {"title": it.get("title"), "from_act_no": it.get("from_act_no")}
                    for it in carried_open_items if it.get("status") == "УСТРАНЕНО"
                ],
                new_items=new_open,
                owner_observation=voice_ctx.get("transcript", "")[:1000],
                conflict_flags=conflict_flags or [],
                object_name=(voice_ctx.get("object_hint") or
                              (object_card.get("object_name") if object_card else "") or ""),
                object_folder_url=topic_folder_link or "",
            )
        except Exception:
            _P6H2_LOG.exception("P6H3_RECORD_INSPECTION_FAIL")

    msg_lines = ["Акт сформирован"]
    if pdf_link:
        msg_lines.append(f"PDF: {pdf_link}")
    elif pdf_ok:
        msg_lines.append("PDF: подготовлен локально, загрузка на Drive не выполнена — Telegram fallback")
    else:
        msg_lines.append("PDF: ошибка генерации — повторите позже")
    if docx_link:
        msg_lines.append(f"DOCX (черновик, служебно): {docx_link}")
    if topic_folder_link:
        msg_lines.append(f"Фото: {topic_folder_link}")
    msg_lines.append("Норма: " + ("подтверждена" if global_norms else "не подтверждена"))
    if visit_mode == "repeat":
        msg_lines.append(f"Тип осмотра: повторный (история объекта: {len((object_card or {}).get('inspection_chain') or []) + 1} записей)")
    elif visit_mode == "extension":
        msg_lines.append("Тип осмотра: дополнение к предыдущему акту")
    else:
        msg_lines.append("Тип осмотра: первичный")

    # Memory summary
    try:
        _p6h_save_summary_to_memory(chat_id, topic_id, {
            "folder": voice_ctx.get("folder_hint") or "",
            "object": voice_ctx.get("object_hint") or object_id or "",
            "date": payload["date_str"],
            "owner_directives": (voice_ctx.get("explicit_include") or []) + (voice_ctx.get("explicit_exclude") or []),
            "defect_brief": [str(d.get("title") or d.get("description") or "")[:200] for d in defects][:8],
            "pdf_link": pdf_link,
            "docx_link": docx_link,
            "status": ("ACT_DONE" if pdf_link else ("ACT_PARTIAL" if (pdf_ok or docx_ok) else "ACT_FAIL"))
                       + f":visit={visit_mode}",
        })
    except Exception:
        pass

    return {
        "ok": True if (pdf_ok or docx_ok) else False,
        "handled": True,
        "kind": "technadzor_p6h_act",
        "state": "DONE" if pdf_link else "AWAITING_CONFIRMATION",
        "artifact_path": str(pdf_local if pdf_ok else docx_local),
        "extra_artifact_path": str(docx_local if docx_ok else ""),
        "drive_link": pdf_link or docx_link or "",
        "message": _p6h_clean_text("\n".join(msg_lines), 4000),
        "history": "P6H_ACT_VISIT_{}_DOCX_{}_PDF_{}_DRIVE_PDF_{}_OPEN_CARRIED_{}".format(
            visit_mode,
            "OK" if docx_ok else "FAIL",
            "OK" if pdf_ok else "FAIL",
            "OK" if pdf_link else "FAIL",
            len(carried_open_items),
        ),
    }


_P6H2_LOG.info("P6H_TOPIC5_OBJECT_REGISTRY_INSPECTION_CHAIN_20260504_INSTALLED")
# === END_P6H_PART_3 ===

# ─── P6H_EXTERNAL_VISION_GUARD_V1 ──────────────────────────────────────────
# CANON: TECHNADZOR_DOMAIN_LOGIC_CANON_V2 §33
# EXTERNAL_PHOTO_ANALYSIS_ALLOWED = False by default
# Vision запускается только после явного разрешения владельца

_P6H_EXTERNAL_VISION_ALLOWED = False

_p6h_vision_orig = _p6f_tnz_vision_via_openrouter  # сохраняем оригинал

async def _p6f_tnz_vision_via_openrouter(local_path):  # noqa: F811
    if not _P6H_EXTERNAL_VISION_ALLOWED:
        _P6H2_LOG.warning("EXTERNAL_VISION_BLOCKED path=%s EXTERNAL_PHOTO_ANALYSIS_ALLOWED=False", local_path)
        return {}, "EXTERNAL_PHOTO_ANALYSIS_BLOCKED"
    return await _p6h_vision_orig(local_path)

def _p6h_allow_external_vision():
    global _P6H_EXTERNAL_VISION_ALLOWED
    _P6H_EXTERNAL_VISION_ALLOWED = True
    _P6H2_LOG.info("EXTERNAL_VISION_ALLOWED_SET owner_approved=True")

_P6H2_LOG.info("P6H_EXTERNAL_VISION_GUARD_V1_INSTALLED allowed=%s", _P6H_EXTERNAL_VISION_ALLOWED)
# ─── END P6H_EXTERNAL_VISION_GUARD_V1 ──────────────────────────────────────

# ─── P6H_PART_4_VISIT_BUFFER_V1 ────────────────────────────────────────────
# CANON: TECHNADZOR_DOMAIN_LOGIC_CANON_V2
# ActiveTechnadzorFolder / VisitMaterial / visit_buffer_add / visit_buffer_flush

import os as _p6h4_os
import json as _p6h4_json
import time as _p6h4_time
import logging as _p6h4_logging

_P6H4_LOG = _p6h4_logging.getLogger("task_worker")

_P6H4_BASE = _p6h4_os.path.join(
    _p6h4_os.path.dirname(_p6h4_os.path.dirname(_p6h4_os.path.abspath(__file__))),
    "data", "technadzor"
)


def _p6h4_ensure():
    _p6h4_os.makedirs(_P6H4_BASE, exist_ok=True)


def _p6h4_buf_path(chat_id, topic_id):
    _p6h4_ensure()
    return _p6h4_os.path.join(_P6H4_BASE, f"buf_{chat_id}_{topic_id}.json")


def _p6h4_folder_path(chat_id, topic_id):
    _p6h4_ensure()
    return _p6h4_os.path.join(_P6H4_BASE, f"active_folder_{chat_id}_{topic_id}.json")


def visit_buffer_add(chat_id, topic_id, material: dict) -> int:
    """Append VisitMaterial to persistent buffer. Returns new total count."""
    path = _p6h4_buf_path(str(chat_id), int(topic_id))
    try:
        with open(path, "r", encoding="utf-8") as _f:
            buf = _p6h4_json.load(_f)
    except Exception:
        buf = {"materials": [], "created_at": _p6h4_time.time()}
    if "material_id" not in material:
        material["material_id"] = f"{int(_p6h4_time.time() * 1000)}"
    material.setdefault("added_at", _p6h4_time.time())
    buf["materials"].append(material)
    buf["updated_at"] = _p6h4_time.time()
    with open(path, "w", encoding="utf-8") as _f:
        _p6h4_json.dump(buf, _f, ensure_ascii=False, indent=2)
    count = len(buf["materials"])
    _P6H4_LOG.info("P6H4_VISIT_BUFFER_ADD chat=%s topic=%s count=%s", chat_id, topic_id, count)
    return count


def visit_buffer_flush(chat_id, topic_id) -> list:
    """Return all buffered VisitMaterials and clear buffer."""
    path = _p6h4_buf_path(str(chat_id), int(topic_id))
    try:
        with open(path, "r", encoding="utf-8") as _f:
            buf = _p6h4_json.load(_f)
        materials = buf.get("materials", [])
        _p6h4_os.remove(path)
        _P6H4_LOG.info("P6H4_VISIT_BUFFER_FLUSH chat=%s topic=%s count=%s", chat_id, topic_id, len(materials))
        return materials
    except Exception:
        _P6H4_LOG.info("P6H4_VISIT_BUFFER_FLUSH_EMPTY chat=%s topic=%s", chat_id, topic_id)
        return []


def visit_buffer_count(chat_id, topic_id) -> int:
    path = _p6h4_buf_path(str(chat_id), int(topic_id))
    try:
        with open(path, "r", encoding="utf-8") as _f:
            buf = _p6h4_json.load(_f)
        return len(buf.get("materials", []))
    except Exception:
        return 0


def set_active_folder(chat_id, topic_id, folder_data: dict):
    path = _p6h4_folder_path(str(chat_id), int(topic_id))
    folder_data["set_at"] = _p6h4_time.time()
    with open(path, "w", encoding="utf-8") as _f:
        _p6h4_json.dump(folder_data, _f, ensure_ascii=False, indent=2)
    _P6H4_LOG.info(
        "P6H4_ACTIVE_FOLDER_SET chat=%s topic=%s name=%s",
        chat_id, topic_id, folder_data.get("folder_name", "?"),
    )


def get_active_folder(chat_id, topic_id) -> dict:
    path = _p6h4_folder_path(str(chat_id), int(topic_id))
    try:
        with open(path, "r", encoding="utf-8") as _f:
            return _p6h4_json.load(_f)
    except Exception:
        return {}


def process_drive_folder_batch(chat_id, topic_id, folder_id: str, folder_name: str = "") -> int:
    """Scan Drive folder, add all files as VisitMaterials. Returns count added."""
    added = 0
    try:
        from core.topic_drive_oauth import get_drive_service as _p6h4_get_drive
        svc = _p6h4_get_drive(chat_id=str(chat_id), topic_id=int(topic_id))
        items = svc.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id,name,mimeType,webViewLink)",
            pageSize=200,
        ).execute().get("files", [])
        for item in items:
            mime = item.get("mimeType", "")
            if "folder" in mime:
                continue
            ftype = "PHOTO" if mime.startswith("image/") else "PDF" if "pdf" in mime else "OTHER"
            mat = {
                "source": "DRIVE",
                "file_type": ftype,
                "file_name": item.get("name", ""),
                "drive_url": item.get("webViewLink", ""),
                "drive_file_id": item.get("id", ""),
                "include_in_act": True,
                "include_in_report": True,
                "group_label": folder_name or "",
            }
            visit_buffer_add(str(chat_id), int(topic_id), mat)
            added += 1
        _P6H4_LOG.info("P6H4_DRIVE_FOLDER_BATCH chat=%s topic=%s folder=%s added=%s", chat_id, topic_id, folder_id, added)
    except Exception as _p6h4_batch_err:
        _P6H4_LOG.warning("P6H4_DRIVE_FOLDER_BATCH_ERR %s", _p6h4_batch_err)
    return added


_P6H4_LOG.info("P6H_PART_4_VISIT_BUFFER_V1_INSTALLED")
# ─── END P6H_PART_4_VISIT_BUFFER_V1 ─────────────────────────────────────────


# === P6H4TW_BATCH_TRIGGER_V1 ===
# FIX: original P6H_PART_4 hook in task_worker.py is after asyncio.run() and never fires.
# This wrapper hooks process_technadzor here (before asyncio.run()), intercepting all topic_5 calls.
# Handles: photo/file buffering, Drive folder batch load, visit buffer flush to process_technadzor.
# EXTERNAL_PHOTO_ANALYSIS_ALLOWED=False: no Vision without explicit owner permission.
import logging as _p6h4tw_v1_log_mod
import os as _p6h4tw_v1_os
import re as _p6h4tw_v1_re

_P6H4TW_V1_LOG = _p6h4tw_v1_log_mod.getLogger("task_worker")
_P6H4TW_V1_DRIVE_RE = _p6h4tw_v1_re.compile(
    r"https://drive\.google\.com/drive/folders/([A-Za-z0-9_-]+)"
)
_P6H4TW_V1_BATCH_TRIGGERS = (
    "загрузи все файлы из папки", "загрузи все файлы",
    "возьми файлы из папки", "прочитай папку",
    "обработай папку", "сделай разбор по папке", "сделай акт по папке",
    "разбор по папке", "акт по папке",
    "загрузи папку", "возьми из папки",
)
_P6H4TW_V1_BATCH_AND_FLUSH = (
    "сделай разбор по папке", "сделай акт по папке",
    "разбор по папке", "акт по папке",
)
_P6H4TW_V1_FLUSH_TRIGGERS = (
    "сделай акт", "собери акт", "сделай разбор", "сделай анализ",
    "собери разбор", "разберись", "сделай отчет", "сделай отчёт",
    "начни анализ", "сформируй акт",
)
_P6H4TW_V1_ACTIVE_FOLDER_TRIGGERS = (
    "работаем по этой папке", "установи папку", "активная папка это",
    "drive.google.com/drive/folders/",
)
_P6H4TW_V1_SHOW_FOLDER_TRIGGERS = (
    "покажи активную папку", "какая активная папка", "какая папка",
    "текущая папка", "покажи папку",
)


def _p6h4tw_v1_low(v):
    return str(v or "").lower().replace("ё", "е")


try:
    _p6h4tw_v1_orig = process_technadzor
    if not getattr(_p6h4tw_v1_orig, "_p6h4tw_v1_wrapped", False):

        def process_technadzor(text="", task_id="", chat_id="", topic_id=0, file_path="", file_name="", **kwargs):  # noqa: F811
            if int(topic_id or 0) != 5:
                return _p6h4tw_v1_orig(
                    text=text, task_id=task_id, chat_id=chat_id,
                    topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs
                )

            chat_str = str(chat_id)
            txt_low = _p6h4tw_v1_low(text)

            # ── Photo / Drive file → buffer (no Vision) ──────────────────────
            if file_path or file_name:
                fn = file_name or _p6h4tw_v1_os.path.basename(file_path or "")
                fn_low = fn.lower()
                is_photo = fn_low.endswith((".jpg", ".jpeg", ".png", ".webp", ".heic"))
                ftype = "PHOTO" if is_photo else "PDF" if fn_low.endswith(".pdf") else "DOCUMENT"
                material = {
                    "source": "telegram",
                    "file_type": ftype,
                    "file_name": fn,
                    "drive_file_id": "",
                    "drive_url": file_path or "",
                    "caption": text or "",
                    "include_in_act": True,
                    "include_in_report": True,
                }
                try:
                    count = visit_buffer_add(chat_str, 5, material)
                    _P6H4TW_V1_LOG.info(
                        "P6H4TW_V1_PHOTO_BUFFERED chat=%s count=%s fn=%s", chat_str, count, fn
                    )
                    return {
                        "ok": True,
                        "result_text": f"Добавлено в пакет ({count} шт.). Когда готово — скажи «сделай разбор».",
                        "history": "P6H4TW_V1_PHOTO_BUFFERED",
                    }
                except Exception as _e:
                    _P6H4TW_V1_LOG.warning("P6H4TW_V1_BUF_ADD_ERR %s", _e)
                    return _p6h4tw_v1_orig(
                        text=text, task_id=task_id, chat_id=chat_id,
                        topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs
                    )

            # ── Drive folder URL / set active folder ─────────────────────────
            m_drive = _P6H4TW_V1_DRIVE_RE.search(text or "")
            if m_drive or any(t in txt_low for t in _P6H4TW_V1_ACTIVE_FOLDER_TRIGGERS):
                folder_id = m_drive.group(1) if m_drive else ""
                folder_name = ""
                if folder_id:
                    try:
                        from core.topic_drive_oauth import get_drive_service as _p6h4tw_v1_gds
                        svc = _p6h4tw_v1_gds(chat_id=chat_str, topic_id=5)
                        folder_name = (
                            svc.files().get(fileId=folder_id, fields="name").execute().get("name", "")
                        )
                    except Exception:
                        pass
                try:
                    set_active_folder(chat_str, 5, {
                        "folder_id": folder_id,
                        "folder_name": folder_name,
                        "source_text": (text or "")[:500],
                    })
                    return {
                        "ok": True,
                        "result_text": f"Активная папка установлена: {folder_name or folder_id or '(из текста)'}.",
                        "history": "P6H4TW_V1_ACTIVE_FOLDER_SET",
                    }
                except Exception as _e:
                    _P6H4TW_V1_LOG.warning("P6H4TW_V1_SET_FOLDER_ERR %s", _e)

            # ── Show active folder ────────────────────────────────────────────
            if any(t in txt_low for t in _P6H4TW_V1_SHOW_FOLDER_TRIGGERS):
                try:
                    af = get_active_folder(chat_str, 5)
                    if af:
                        name = af.get("folder_name") or af.get("folder_id", "(нет имени)")
                        fid = af.get("folder_id", "")
                        link = f"https://drive.google.com/drive/folders/{fid}" if fid else "—"
                        msg = f"Активная папка: {name}\n{link}"
                    else:
                        msg = "Активная папка не установлена. Пришли ссылку на папку."
                    return {"ok": True, "result_text": msg, "history": "P6H4TW_V1_SHOW_FOLDER"}
                except Exception as _e:
                    _P6H4TW_V1_LOG.warning("P6H4TW_V1_SHOW_FOLDER_ERR %s", _e)

            # ── Drive folder batch load ───────────────────────────────────────
            if any(t in txt_low for t in _P6H4TW_V1_BATCH_TRIGGERS):
                try:
                    m_drive2 = _P6H4TW_V1_DRIVE_RE.search(text or "")
                    if m_drive2:
                        batch_fid = m_drive2.group(1)
                        batch_fname = ""
                        try:
                            from core.topic_drive_oauth import get_drive_service as _p6h4tw_v1_gds2
                            svc2 = _p6h4tw_v1_gds2(chat_id=chat_str, topic_id=5)
                            batch_fname = (
                                svc2.files().get(fileId=batch_fid, fields="name").execute().get("name", "")
                            )
                        except Exception:
                            pass
                    else:
                        af2 = get_active_folder(chat_str, 5) or {}
                        batch_fid = af2.get("folder_id", "")
                        batch_fname = af2.get("folder_name", "")
                    if not batch_fid:
                        return {
                            "ok": True,
                            "result_text": "Не найдена активная папка. Пришли ссылку на папку Drive.",
                            "history": "P6H4TW_V1_BATCH_NO_FOLDER",
                        }
                    added = process_drive_folder_batch(chat_str, 5, batch_fid, batch_fname)
                    _P6H4TW_V1_LOG.info(
                        "P6H4TW_V1_BATCH_LOADED chat=%s folder=%s added=%s", chat_str, batch_fid, added
                    )
                    do_flush = any(t in txt_low for t in _P6H4TW_V1_BATCH_AND_FLUSH)
                    if not do_flush:
                        return {
                            "ok": True,
                            "result_text": (
                                f"Принял. Файлы из папки добавлены в пакет выезда: {added} шт. "
                                "Vision не запускаю без разрешения владельца. Скажи «сделай разбор» когда готово."
                            ),
                            "history": "P6H4TW_V1_BATCH_LOADED",
                        }
                    txt_low = "сделай разбор"  # fall through to flush
                except Exception as _e:
                    _P6H4TW_V1_LOG.warning("P6H4TW_V1_BATCH_ERR %s", _e)

            # ── Flush buffer → process_technadzor ────────────────────────────
            if any(t in txt_low for t in _P6H4TW_V1_FLUSH_TRIGGERS):
                try:
                    count = visit_buffer_count(chat_str, 5)
                    if count == 0:
                        return {
                            "ok": True,
                            "result_text": "Буфер пуст — сначала пришли фото или файлы.",
                            "history": "P6H4TW_V1_FLUSH_EMPTY",
                        }
                    materials = visit_buffer_flush(chat_str, 5)
                    lines = ["Технический надзор. Акт по материалам выезда:", "VISIT_PACKAGE:"]
                    for i, m in enumerate(materials, 1):
                        fn2 = m.get("file_name", f"файл {i}")
                        url2 = m.get("drive_url", "")
                        note2 = (m.get("caption", "") or m.get("voice_comment", "") or "").strip()
                        line = f"  {i}. {fn2}"
                        if url2:
                            line += f" {url2}"
                        if note2:
                            line += f" — {note2}"
                        lines.append(line)
                    package_text = "\n".join(lines)
                    _P6H4TW_V1_LOG.info(
                        "P6H4TW_V1_FLUSH chat=%s count=%s", chat_str, len(materials)
                    )
                    return _p6h4tw_v1_orig(
                        text=package_text, task_id=task_id, chat_id=chat_id,
                        topic_id=topic_id, file_path="", file_name="", **kwargs
                    )
                except Exception as _e:
                    _P6H4TW_V1_LOG.warning("P6H4TW_V1_FLUSH_ERR %s", _e)

            # ── Default pass-through ──────────────────────────────────────────
            return _p6h4tw_v1_orig(
                text=text, task_id=task_id, chat_id=chat_id,
                topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs
            )

        process_technadzor._p6h4tw_v1_wrapped = True
        _p6h4tw_v1_orig._p6h4tw_v1_wrapped = True
        _P6H4TW_V1_LOG.info("P6H4TW_BATCH_TRIGGER_V1_INSTALLED")
except Exception as _p6h4tw_v1_err:
    _P6H4TW_V1_LOG.exception("P6H4TW_V1_INSTALL_ERR %s", _p6h4tw_v1_err)
# === END_P6H4TW_BATCH_TRIGGER_V1 ===

# === P6H4FD_FOLDER_DISCOVERY_V1 ===
import re as _p6h4fd_re
import logging as _p6h4fd_log_mod

_P6H4FD_LOG = _p6h4fd_log_mod.getLogger("technadzor_engine.p6h4fd")

_P6H4FD_FOLDER_INTENTS = (
    "папка",
    "новая папка",
    "создана папка",
    "создал папку",
    "обнаружь папку",
    "найди папку",
    "папка называется",
    "работаем по папке",
    "текущая папка",
    "прими папку",
    "туда складывать",
    "туда загружать",
    "все материалы туда",
)

# Matches "папк[у/а/и] <name>" — captures up to 60 chars until punctuation or end
_P6H4FD_NAME_RE = _p6h4fd_re.compile(
    r"(?:папк[уаи]|папка)\s+([А-Яа-яёЁA-Za-z0-9][А-Яа-яёЁA-Za-z0-9 \-_]{0,60}?)(?:[,.\n!?]|$)",
    _p6h4fd_re.IGNORECASE,
)


def _p6h4fd_extract_name(text: str) -> str:
    m = _P6H4FD_NAME_RE.search(text)
    if m:
        return m.group(1).strip()
    return ""


def _p6h4fd_norm(s: str) -> str:
    return " ".join(s.lower().replace("ё", "е").split())


def _p6h4fd_match_score(candidate: str, folder_name: str) -> int:
    c = _p6h4fd_norm(candidate)
    f = _p6h4fd_norm(folder_name)
    if not c:
        return 0
    if c == f:
        return 100
    if c in f or f in c:
        return 80
    cw = set(c.split())
    fw = set(f.split())
    overlap = len(cw & fw)
    return overlap * 10 if overlap else 0


try:
    _p6h4fd_orig_pt = process_technadzor
    if not getattr(_p6h4fd_orig_pt, "_p6h4fd_wrapped", False):

        def process_technadzor(  # noqa: F811
            text="", task_id="", chat_id="", topic_id=0,
            file_path="", file_name="", **kwargs
        ):
            if int(topic_id or 0) != 5:
                return _p6h4fd_orig_pt(
                    text=text, task_id=task_id, chat_id=chat_id,
                    topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs
                )

            txt_low = (text or "").lower().replace("ё", "е")
            if not any(t in txt_low for t in _P6H4FD_FOLDER_INTENTS):
                return _p6h4fd_orig_pt(
                    text=text, task_id=task_id, chat_id=chat_id,
                    topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs
                )

            # — folder/context intent: fresh Drive lookup by name —
            try:
                candidate = _p6h4fd_extract_name(text or "")
                chat_str = str(chat_id or "")
                _P6H4FD_LOG.info(
                    "P6H4FD_DISCOVERY_START candidate=%r chat=%s", candidate, chat_str
                )

                from core.technadzor_drive_index import _service as _p6h4fd_svc

                # system/container names — never a valid active folder result
                _P6H4FD_NEVER_RESULT = frozenset({
                    "technadzor", "технадзор", "topic_5", "_orchestra_work",
                    "_system", "_tmp", "_archive", "_drafts", "_templates", "_manifests",
                })

                def _p6h4fd_is_container(name):
                    return (name or "").strip().lower() in _P6H4FD_NEVER_RESULT

                svc = _p6h4fd_svc()

                def _p6h4fd_list_subfolders(parent_fid):
                    r = svc.files().list(
                        q=(
                            f"'{parent_fid}' in parents"
                            " and mimeType='application/vnd.google-apps.folder'"
                            " and trashed=false"
                        ),
                        fields="files(id,name,createdTime,modifiedTime)",
                        orderBy="createdTime desc",
                        pageSize=50,
                    ).execute()
                    return r.get("files", [])

                # Step A: search inside correct user ТЕХНАДЗОР root
                _TECHNADZOR_ROOT_FID = "1s2y5l2mJFTb7P90XVokErXYVzmoH-VtD"
                raw_a = _p6h4fd_list_subfolders(_TECHNADZOR_ROOT_FID)
                folders = [f for f in raw_a if not _p6h4fd_is_container(f.get("name", ""))]
                _P6H4FD_LOG.info("P6H4FD_ROOT_SEARCH count=%s", len(folders))

                # Step D: fallback — Drive-wide exact name search
                if not folders and candidate:
                    _safe = candidate.replace("'", "\\'")
                    _gr = svc.files().list(
                        q=(
                            f"name='{_safe}'"
                            " and mimeType='application/vnd.google-apps.folder'"
                            " and trashed=false"
                        ),
                        fields="files(id,name,createdTime,modifiedTime)",
                        orderBy="createdTime desc",
                        pageSize=10,
                    ).execute()
                    folders = [
                        f for f in _gr.get("files", [])
                        if not _p6h4fd_is_container(f.get("name", ""))
                    ]
                    _P6H4FD_LOG.info("P6H4FD_GLOBAL_SEARCH count=%s candidate=%r", len(folders), candidate)

                if not folders:
                    msg_nf = (
                        "Папку не нашёл"
                        + (f" «{candidate}»" if candidate else "")
                        + ". Укажи точное название или пришли ссылку."
                    )
                    return {
                        "ok": True,
                        "handled": True,
                        "state": "DONE",
                        "result_text": msg_nf,
                        "message": msg_nf,
                        "history": "P6H4FD_V1:NO_USER_FOLDERS",
                    }

                # exact match first, then fuzzy, then newest
                best = None
                best_score = 0
                if candidate:
                    for f in folders:
                        score = _p6h4fd_match_score(candidate, f.get("name", ""))
                        if score > best_score:
                            best_score = score
                            best = f

                if best is None or best_score == 0:
                    best = folders[0]

                fid = best["id"]
                fname = best.get("name", "")
                link = f"https://drive.google.com/drive/folders/{fid}"

                set_active_folder(chat_str, 5, {
                    "folder_id": fid,
                    "folder_name": fname,
                    "source_text": (text or "")[:500],
                })
                msg = f"Нашёл папку «{fname}» и установил её как активную.\n{link}"
                _P6H4FD_LOG.info(
                    "P6H4FD_SET_ACTIVE folder_id=%s name=%r score=%s chat=%s",
                    fid, fname, best_score, chat_str,
                )
                return {
                    "ok": True,
                    "handled": True,
                    "result_text": msg,
                    "message": msg,
                    "history": f"P6H4FD_V1:SET_ACTIVE:{fid}",
                }

            except Exception as _e:
                _P6H4FD_LOG.warning("P6H4FD_ERR %s", _e)
                # on error fall through to lower wrapper
                return _p6h4fd_orig_pt(
                    text=text, task_id=task_id, chat_id=chat_id,
                    topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs
                )

        process_technadzor._p6h4fd_wrapped = True
        _p6h4fd_orig_pt._p6h4fd_wrapped = True
        _P6H4FD_LOG.info("P6H4FD_FOLDER_DISCOVERY_V1_INSTALLED")
except Exception as _p6h4fd_err:
    _P6H4FD_LOG.exception("P6H4FD_INSTALL_ERR %s", _p6h4fd_err)
# === END_P6H4FD_FOLDER_DISCOVERY_V1 ===

# === PHOTO_RECOGNITION_TOPIC5_RUNTIME_BINDING_V1 ===
try:
    _photo_t5_orig_process_technadzor = process_technadzor

    def process_technadzor(
        text: str = "",
        task_id: str = "",
        chat_id: str = "",
        topic_id: int = 0,
        file_path: str = "",
        file_name: str = "",
        **kwargs,
    ):
        from core.photo_recognition_engine import is_image_file, process_photo_recognition

        clean_kwargs = dict(kwargs)
        for key in (
            "text", "raw_input", "task_id", "id", "chat_id", "topic_id",
            "file_path", "local_path", "file_name", "name",
        ):
            clean_kwargs.pop(key, None)

        raw_text = str(text or kwargs.get("raw_input") or "")
        fp = str(file_path or kwargs.get("local_path") or "")
        fn = str(file_name or kwargs.get("file_name") or kwargs.get("name") or "")
        resolved_task_id = str(task_id or kwargs.get("task_id") or kwargs.get("id") or "")
        resolved_chat_id = str(chat_id or kwargs.get("chat_id") or "")

        try:
            tid = int(topic_id or kwargs.get("topic_id") or 0)
        except Exception:
            tid = 0

        photo_result = None
        if tid == 5 and is_image_file(file_name=fn, file_path=fp):
            photo_result = process_photo_recognition(
                topic_id=5,
                file_name=fn,
                file_path=fp,
                owner_comment=raw_text,
                source="TELEGRAM",
            )

            if not raw_text.strip():
                return {
                    "ok": True,
                    "handled": True,
                    "status": "WAITING_CLARIFICATION",
                    "state": "WAITING_CLARIFICATION",
                    "kind": "technadzor_photo_material",
                    "message": "Фото принято как материал технадзора. Укажи, к какому замечанию или разделу его отнести",
                    "result_text": "Фото принято как материал технадзора. Укажи, к какому замечанию или разделу его отнести",
                    "photo_recognition": photo_result,
                    "history": "PHOTO_RECOGNITION_TOPIC5_RUNTIME_BINDING_V1:WAITING_OWNER_COMMENT",
                }

        result = _photo_t5_orig_process_technadzor(
            text=raw_text,
            task_id=resolved_task_id,
            chat_id=resolved_chat_id,
            topic_id=tid,
            file_path=fp,
            file_name=fn,
            **clean_kwargs,
        )

        if photo_result and isinstance(result, dict):
            result["photo_recognition"] = photo_result
            result["photo_recognition_status"] = photo_result.get("status")
            result["history"] = str(result.get("history") or "") + "|PHOTO_RECOGNITION_TOPIC5_RUNTIME_BINDING_V1"
            if "message" not in result and "result_text" not in result:
                result["message"] = "Фото принято и связано с технадзорным материалом"

        return result
except Exception:
    pass
# === END_PHOTO_RECOGNITION_TOPIC5_RUNTIME_BINDING_V1 ===


# === P7_TOPIC5_REPLY_VOICE_BINDING_V1 ===
# Binds Telegram text/voice reply to the VisitMaterial created from the replied photo/file.
import json as _p7_t5_json
import re as _p7_t5_re
import time as _p7_t5_time
from pathlib import Path as _p7_t5_Path

_P7_T5_ORIG_PROCESS_TECHNADZOR = process_technadzor
_P7_T5_DATA = _p7_t5_Path("/root/.areal-neva-core/data/technadzor")

def _p7_t5_s(v, limit=20000):
    try:
        return "" if v is None else str(v).strip()[:limit]
    except Exception:
        return ""

def _p7_t5_low(v):
    return _p7_t5_s(v).lower().replace("ё", "е")

def _p7_t5_task_get(task, key, default=None):
    if task is None:
        return default
    try:
        if isinstance(task, dict):
            return task.get(key, default)
        return task[key]
    except Exception:
        return getattr(task, key, default)

def _p7_t5_parse_payload(text):
    raw = _p7_t5_s(text, 50000)
    try:
        obj = _p7_t5_json.loads(raw)
        return obj if isinstance(obj, dict) else {"text": raw}
    except Exception:
        return {"text": raw}

def _p7_t5_buf_path(chat_id):
    _P7_T5_DATA.mkdir(parents=True, exist_ok=True)
    return _P7_T5_DATA / f"buf_{chat_id}_5.json"

def _p7_t5_active_folder(chat_id):
    p = _P7_T5_DATA / f"active_folder_{chat_id}_5.json"
    try:
        obj = _p7_t5_json.loads(p.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}

def _p7_t5_load_buf(chat_id):
    p = _p7_t5_buf_path(chat_id)
    try:
        obj = _p7_t5_json.loads(p.read_text(encoding="utf-8"))
        if isinstance(obj, dict):
            obj.setdefault("materials", [])
            return obj
    except Exception:
        pass
    return {"materials": [], "created_at": _p7_t5_time.time()}

def _p7_t5_save_buf(chat_id, buf):
    p = _p7_t5_buf_path(chat_id)
    buf["updated_at"] = _p7_t5_time.time()
    p.write_text(_p7_t5_json.dumps(buf, ensure_ascii=False, indent=2), encoding="utf-8")

def _p7_t5_msg_id_from_name(name):
    m = _p7_t5_re.search(r"_([0-9]{3,})\.[A-Za-z0-9]+$", _p7_t5_s(name))
    return m.group(1) if m else ""

def _p7_t5_add_material(chat_id, material):
    buf = _p7_t5_load_buf(chat_id)
    mid = _p7_t5_s(material.get("telegram_message_id"))
    fname = _p7_t5_s(material.get("file_name"))
    for old in buf.get("materials", []):
        if mid and _p7_t5_s(old.get("telegram_message_id")) == mid:
            old.update({k: v for k, v in material.items() if v not in ("", None)})
            _p7_t5_save_buf(chat_id, buf)
            return len(buf.get("materials", [])), old
        if fname and _p7_t5_s(old.get("file_name")) == fname:
            old.update({k: v for k, v in material.items() if v not in ("", None)})
            _p7_t5_save_buf(chat_id, buf)
            return len(buf.get("materials", [])), old
    buf["materials"].append(material)
    _p7_t5_save_buf(chat_id, buf)
    return len(buf.get("materials", [])), material

def _p7_t5_bind_comment(chat_id, reply_to_message_id, comment, is_voice=False):
    reply_id = _p7_t5_s(reply_to_message_id)
    if not reply_id:
        return None
    comment = _p7_t5_s(comment, 8000)
    if not comment:
        return None

    buf = _p7_t5_load_buf(chat_id)
    for m in buf.get("materials", []):
        ids = {
            _p7_t5_s(m.get("telegram_message_id")),
            _p7_t5_s(m.get("reply_to_message_id")),
            _p7_t5_msg_id_from_name(m.get("file_name")),
        }
        if reply_id in ids:
            field = "voice_comment" if is_voice else "owner_comment"
            prev = _p7_t5_s(m.get(field))
            m[field] = (prev + "\n" + comment).strip() if prev and comment not in prev else comment
            m["status"] = "LINKED"
            m["linked_reply_to_message_id"] = reply_id
            m["updated_at"] = _p7_t5_time.time()
            _p7_t5_save_buf(chat_id, buf)
            return m
    return None

def _p7_t5_is_flush_command(text):
    low = _p7_t5_low(text)
    return any(x in low for x in (
        "сделай акт", "собери акт", "сделай разбор", "сделай анализ",
        "собери разбор", "сформируй акт", "сделай отчет", "сделай отчёт"
    ))

def process_technadzor(text: str = "", task_id: str = "", chat_id: str = "", topic_id: int = 0, file_path: str = "", file_name: str = "", **kwargs):
    if int(topic_id or 0) != 5:
        return _P7_T5_ORIG_PROCESS_TECHNADZOR(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs)

    chat = _p7_t5_s(chat_id or _p7_t5_task_get(kwargs.get("task"), "chat_id", ""))
    payload = _p7_t5_parse_payload(text)
    task = kwargs.get("task")
    reply_to = payload.get("telegram_reply_to_message_id") or _p7_t5_task_get(task, "reply_to_message_id", "")
    current_msg = payload.get("telegram_message_id") or _p7_t5_msg_id_from_name(file_name)
    comment = payload.get("transcript") or payload.get("text") or text
    is_voice = _p7_t5_low(comment).startswith("[voice]") or _p7_t5_low(payload.get("input_type", "")) == "voice"
    comment_clean = _p7_t5_re.sub(r"^\s*\[VOICE\]\s*", "", _p7_t5_s(comment), flags=_p7_t5_re.I)

    if (file_path or file_name) and not _p7_t5_is_flush_command(comment_clean):
        af = _p7_t5_active_folder(chat)
        fn = _p7_t5_s(file_name or payload.get("file_name") or payload.get("name") or "")
        low_fn = fn.lower()
        ftype = "PHOTO" if low_fn.endswith((".jpg", ".jpeg", ".png", ".webp", ".heic")) else "PDF" if low_fn.endswith(".pdf") else "DOCUMENT"
        material = {
            "source": "TELEGRAM",
            "file_type": ftype,
            "file_name": fn,
            "telegram_message_id": _p7_t5_s(current_msg),
            "reply_to_message_id": _p7_t5_s(reply_to),
            "drive_file_id": _p7_t5_s(payload.get("drive_file_id")),
            "drive_url": _p7_t5_s(payload.get("drive_url") or payload.get("webViewLink") or file_path),
            "active_folder_id": _p7_t5_s(af.get("folder_id")),
            "active_folder_name": _p7_t5_s(af.get("folder_name")),
            "caption": _p7_t5_s(payload.get("caption") or comment_clean),
            "include_in_act": True,
            "include_in_report": True,
            "status": "PENDING",
            "added_at": _p7_t5_time.time(),
        }
        count, _ = _p7_t5_add_material(chat, material)
        return {
            "ok": True,
            "handled": True,
            "state": "DONE",
            "result_text": f"Фото/файл принят в пакет выезда: {count} шт. Активная папка: {material.get('active_folder_name') or material.get('active_folder_id')}.",
            "message": "Фото/файл принят в пакет выезда",
            "history": "P7_TOPIC5_MATERIAL_BUFFERED_WITH_ACTIVE_FOLDER",
        }

    if reply_to and comment_clean and not _p7_t5_is_flush_command(comment_clean):
        linked = _p7_t5_bind_comment(chat, reply_to, comment_clean, is_voice=is_voice)
        if linked:
            return {
                "ok": True,
                "handled": True,
                "state": "DONE",
                "result_text": f"Пояснение привязано к фото: {linked.get('file_name', '')}",
                "message": "Пояснение привязано к фото",
                "history": "P7_TOPIC5_REPLY_VOICE_BOUND_TO_MATERIAL",
            }

    return _P7_T5_ORIG_PROCESS_TECHNADZOR(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs)
# === END_P7_TOPIC5_REPLY_VOICE_BINDING_V1 ===

# === FULLFIX_TOPIC5_TECHNADZOR_CANON_CONTOUR_V2_TECHNADZOR ===
import json as _t5v2_json
import sqlite3 as _t5v2_sqlite3
import time as _t5v2_time
import uuid as _t5v2_uuid
from pathlib import Path as _t5v2_Path

_T5V2_ORIG_PROCESS_TECHNADZOR = process_technadzor
_T5V2_DB = "/root/.areal-neva-core/data/core.db"
_T5V2_DATA = _t5v2_Path("/root/.areal-neva-core/data/technadzor")
_T5V2_DATA.mkdir(parents=True, exist_ok=True)

def _t5v2_s(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _t5v2_low(v):
    return _t5v2_s(v).lower().replace("ё", "е")

def _t5v2_json_load(raw):
    try:
        d = _t5v2_json.loads(_t5v2_s(raw))
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}

def _t5v2_get(obj, key, default=""):
    try:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return obj[key]
    except Exception:
        return getattr(obj, key, default)

def _t5v2_task(task_id, kwargs):
    task = kwargs.get("task")
    if task:
        return {
            "id": _t5v2_s(_t5v2_get(task, "id", task_id)),
            "chat_id": _t5v2_s(_t5v2_get(task, "chat_id", kwargs.get("chat_id", ""))),
            "topic_id": int(_t5v2_get(task, "topic_id", kwargs.get("topic_id", 0)) or 0),
            "reply_to_message_id": _t5v2_s(_t5v2_get(task, "reply_to_message_id", "")),
            "bot_message_id": _t5v2_s(_t5v2_get(task, "bot_message_id", "")),
            "input_type": _t5v2_s(_t5v2_get(task, "input_type", "")),
            "raw_input": _t5v2_s(_t5v2_get(task, "raw_input", "")),
        }

    if not task_id:
        return {}

    con = _t5v2_sqlite3.connect(_T5V2_DB)
    try:
        r = con.execute(
            "SELECT id,chat_id,topic_id,reply_to_message_id,bot_message_id,input_type,raw_input FROM tasks WHERE id=? LIMIT 1",
            (_t5v2_s(task_id),)
        ).fetchone()
    finally:
        con.close()

    if not r:
        return {}

    return {
        "id": _t5v2_s(r[0]),
        "chat_id": _t5v2_s(r[1]),
        "topic_id": int(r[2] or 0),
        "reply_to_message_id": _t5v2_s(r[3]),
        "bot_message_id": _t5v2_s(r[4]),
        "input_type": _t5v2_s(r[5]),
        "raw_input": _t5v2_s(r[6]),
    }

def _t5v2_is_photo_meta(meta):
    fn = _t5v2_s(meta.get("file_name") or meta.get("name"))
    mt = _t5v2_s(meta.get("mime_type"))
    return fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".heic")) or mt.startswith("image/")

def _t5v2_msg_id(meta):
    for k in ("telegram_message_id", "_reply_to_message_id", "reply_to_message_id"):
        v = _t5v2_s(meta.get(k))
        if v:
            return v
    fn = _t5v2_s(meta.get("file_name"))
    import re as _re
    m = _re.search(r"_(\d+)\.(?:jpg|jpeg|png|webp|heic)$", fn, _re.I)
    return m.group(1) if m else ""

def _t5v2_photo_rows(chat_id, topic_id=5):
    con = _t5v2_sqlite3.connect(_T5V2_DB)
    try:
        rows = con.execute(
            """
            SELECT rowid,id,raw_input,reply_to_message_id,created_at
            FROM tasks
            WHERE chat_id=?
              AND topic_id=?
              AND input_type='drive_file'
            ORDER BY rowid DESC
            LIMIT 300
            """,
            (_t5v2_s(chat_id), int(topic_id or 0))
        ).fetchall()
    finally:
        con.close()

    out = []
    for rowid, tid, raw, reply_to, created_at in rows:
        meta = _t5v2_json_load(raw)
        if not _t5v2_is_photo_meta(meta):
            continue
        meta["_rowid"] = int(rowid)
        meta["_task_id"] = _t5v2_s(tid)
        meta["_reply_to_message_id"] = _t5v2_s(reply_to)
        meta["_created_at"] = _t5v2_s(created_at)
        out.append(meta)
    return out

def _t5v2_parent_reply_by_bot(chat_id, topic_id, bot_message_id):
    if not bot_message_id:
        return ""
    con = _t5v2_sqlite3.connect(_T5V2_DB)
    try:
        r = con.execute(
            """
            SELECT reply_to_message_id
            FROM tasks
            WHERE chat_id=?
              AND topic_id=?
              AND CAST(bot_message_id AS TEXT)=?
            ORDER BY rowid DESC
            LIMIT 1
            """,
            (_t5v2_s(chat_id), int(topic_id or 0), _t5v2_s(bot_message_id))
        ).fetchone()
    finally:
        con.close()
    return _t5v2_s(r[0]) if r else ""

def _t5v2_find_anchor_photo(chat_id, topic_id, reply_to_message_id):
    rid = _t5v2_s(reply_to_message_id)
    if not rid:
        return {}

    rows = _t5v2_photo_rows(chat_id, topic_id)

    for meta in rows:
        ids = {
            _t5v2_s(meta.get("_reply_to_message_id")),
            _t5v2_s(meta.get("telegram_message_id")),
            _t5v2_msg_id(meta),
        }
        if rid in ids:
            return meta

    parent_reply = _t5v2_parent_reply_by_bot(chat_id, topic_id, rid)
    if parent_reply and parent_reply != rid:
        for meta in rows:
            ids = {
                _t5v2_s(meta.get("_reply_to_message_id")),
                _t5v2_s(meta.get("telegram_message_id")),
                _t5v2_msg_id(meta),
            }
            if parent_reply in ids:
                return meta

    return {}

def _t5v2_group_requested(text):
    low = _t5v2_low(text)
    return any(x in low for x in (
        "этими фото",
        "эти фото",
        "этих фото",
        "все фото",
        "всеми фото",
        "несколько фото",
        "три фото",
        "фотографии",
        "с ними",
        "по ним",
        "их",
        "фото",
        "пакет",
    ))

def _t5v2_select_photo_group(chat_id, topic_id, anchor, text):
    if not anchor:
        return []

    if not _t5v2_group_requested(text):
        return [anchor]

    rows = _t5v2_photo_rows(chat_id, topic_id)

    try:
        anchor_rowid = int(anchor.get("_rowid") or 0)
    except Exception:
        anchor_rowid = 0

    try:
        anchor_msg = int(_t5v2_msg_id(anchor) or 0)
    except Exception:
        anchor_msg = 0

    selected = []
    for meta in rows:
        try:
            rowid = int(meta.get("_rowid") or 0)
        except Exception:
            rowid = 0

        try:
            msg = int(_t5v2_msg_id(meta) or 0)
        except Exception:
            msg = 0

        same_row_cluster = bool(anchor_rowid and abs(rowid - anchor_rowid) <= 10)
        same_msg_cluster = bool(anchor_msg and msg and abs(msg - anchor_msg) <= 20)

        if same_row_cluster and same_msg_cluster:
            selected.append(meta)

    selected = sorted(selected, key=lambda m: int(m.get("_rowid") or 0))
    return selected or [anchor]

def _t5v2_active_folder(chat_id):
    try:
        if "get_active_folder" in globals():
            af = get_active_folder(str(chat_id), 5)
            if isinstance(af, dict):
                return af
    except Exception:
        pass

    try:
        p = _T5V2_DATA / f"active_folder_{chat_id}_5.json"
        d = _t5v2_json.loads(p.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}

def _t5v2_buf_path(chat_id):
    return _T5V2_DATA / f"buf_{chat_id}_5.json"

def _t5v2_load_buf(chat_id):
    p = _t5v2_buf_path(chat_id)
    try:
        d = _t5v2_json.loads(p.read_text(encoding="utf-8"))
        if isinstance(d, dict):
            d.setdefault("materials", [])
            return d
    except Exception:
        pass
    return {"source": "topic5_visit_buffer", "materials": [], "created_at": _t5v2_time.time()}

def _t5v2_save_buf(chat_id, buf):
    buf["updated_at"] = _t5v2_time.time()
    _t5v2_buf_path(chat_id).write_text(_t5v2_json.dumps(buf, ensure_ascii=False, indent=2), encoding="utf-8")

def _t5v2_material(chat_id, meta, comment=""):
    af = _t5v2_active_folder(chat_id)
    fid = _t5v2_s(meta.get("drive_file_id") or meta.get("file_id") or meta.get("id"))
    fn = _t5v2_s(meta.get("file_name") or meta.get("name"))
    mid = _t5v2_msg_id(meta)
    clean = _t5v2_s(comment, 20000)

    if clean.upper().startswith("[VOICE]"):
        clean = clean[7:].strip()

    return {
        "material_id": str(_t5v2_uuid.uuid4()),
        "source": "TELEGRAM",
        "file_type": "PHOTO",
        "file_name": fn,
        "drive_file_id": fid,
        "drive_url": _t5v2_s(meta.get("drive_url") or meta.get("webViewLink") or (f"https://drive.google.com/file/d/{fid}/view?usp=drivesdk" if fid else "")),
        "telegram_message_id": mid,
        "reply_to_message_id": mid,
        "source_task_id": _t5v2_s(meta.get("_task_id")),
        "active_folder_id": _t5v2_s(af.get("folder_id")),
        "active_folder_name": _t5v2_s(af.get("folder_name")),
        "include_in_report": True,
        "include_in_act": True,
        "status": "LINKED" if clean else "PENDING",
        "voice_comment": clean,
        "added_at": _t5v2_time.time(),
        "updated_at": _t5v2_time.time(),
    }

def _t5v2_upsert_material(chat_id, material):
    buf = _t5v2_load_buf(chat_id)
    mid = _t5v2_s(material.get("telegram_message_id"))
    fn = _t5v2_s(material.get("file_name"))

    target = None
    for old in buf.get("materials", []):
        if (mid and _t5v2_s(old.get("telegram_message_id")) == mid) or (fn and _t5v2_s(old.get("file_name")) == fn):
            target = old
            break

    if target is None:
        buf["materials"].append(material)
    else:
        old_comment = _t5v2_s(target.get("voice_comment"), 20000)
        new_comment = _t5v2_s(material.get("voice_comment"), 20000)
        target.update({k: v for k, v in material.items() if v not in ("", None)})

        if old_comment and new_comment and new_comment not in old_comment:
            target["voice_comment"] = old_comment + "\n" + new_comment
        elif old_comment and not new_comment:
            target["voice_comment"] = old_comment

    _t5v2_save_buf(chat_id, buf)
    return len(buf.get("materials", []))

def _t5v2_bind_photos(chat_id, photos, comment):
    count = 0
    for meta in photos:
        count = _t5v2_upsert_material(chat_id, _t5v2_material(chat_id, meta, comment))
    return count

def _t5v2_positive_act(text):
    low = _t5v2_low(text)

    negated = any(x in low for x in (
        "не делай акт",
        "не надо акт",
        "не нужно акт",
        "не формируй акт",
        "не должен был сделать акт",
        "не должен делать акт",
        "акт не для каждого",
        "не для каждого из",
        "принять к сведению",
        "принять это к сведению",
        "прими к сведению",
        "прими это к сведению",
    ))

    positive = any(x in low for x in (
        "сделай акт",
        "сформируй акт",
        "собери акт",
        "готовь акт",
        "акт по этим фото",
        "сделай разбор",
        "сформируй документ",
    ))

    return positive and not negated

def _t5v2_buffer_summary(chat_id):
    buf = _t5v2_load_buf(chat_id)
    mats = buf.get("materials", [])

    lines = []
    for i, m in enumerate(mats, 1):
        lines.append(f"Фото №{i}: {m.get('file_name','')}")
        if m.get("voice_comment"):
            lines.append(f"Пояснение: {m.get('voice_comment')}")
        if m.get("drive_url"):
            lines.append(f"Ссылка: {m.get('drive_url')}")

    return "\n".join(lines), len(mats)

def process_technadzor(text: str = "", task_id: str = "", chat_id: str = "", topic_id: int = 0, file_path: str = "", file_name: str = "", **kwargs):
    task = _t5v2_task(task_id, kwargs)

    try:
        tid = int(topic_id or task.get("topic_id") or kwargs.get("topic_id") or 0)
    except Exception:
        tid = 0

    if tid != 5:
        return _T5V2_ORIG_PROCESS_TECHNADZOR(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs)

    chat = _t5v2_s(chat_id or task.get("chat_id") or kwargs.get("chat_id"))
    raw = _t5v2_s(text or task.get("raw_input"))
    input_type = _t5v2_s(task.get("input_type"))
    reply_to = _t5v2_s(task.get("reply_to_message_id"))

    if input_type == "drive_file":
        meta = _t5v2_json_load(raw)
        if _t5v2_is_photo_meta(meta):
            count = _t5v2_upsert_material(chat, _t5v2_material(chat, meta, ""))
            return {
                "ok": True,
                "handled": True,
                "state": "DONE",
                "status": "DONE",
                "result_text": f"Фото принято в пакет технадзора: {count} шт. Акт не формирую без отдельной команды.",
                "message": "Фото принято в пакет технадзора",
                "history": "FULLFIX_TOPIC5_PHOTO_TO_VISITBUFFER",
            }

    if input_type in ("text", "voice", "") and reply_to and raw and not _t5v2_positive_act(raw):
        anchor = _t5v2_find_anchor_photo(chat, 5, reply_to)
        if anchor:
            photos = _t5v2_select_photo_group(chat, 5, anchor, raw)
            count = _t5v2_bind_photos(chat, photos, raw)
            names = ", ".join(_t5v2_s(p.get("file_name")) for p in photos if p.get("file_name"))
            return {
                "ok": True,
                "handled": True,
                "state": "DONE",
                "status": "DONE",
                "result_text": f"Пояснение принято к фото: {len(photos)} шт. В пакете технадзора: {count} шт. Акт не формирую без отдельной команды.\nФайлы: {names}",
                "message": "Пояснение принято к фото",
                "history": "FULLFIX_TOPIC5_REPLY_TO_PHOTO_BOUND",
            }

    if input_type in ("text", "voice", "") and _t5v2_positive_act(raw):
        summary, n = _t5v2_buffer_summary(chat)
        if n <= 0:
            return {
                "ok": True,
                "handled": True,
                "state": "DONE",
                "status": "DONE",
                "result_text": "В пакете технадзора нет фото. Сначала пришли фото или ответь голосом на фото.",
                "message": "В пакете технадзора нет фото",
                "history": "FULLFIX_TOPIC5_ACT_NO_MATERIALS",
            }

        enriched = raw + "\n\nПакет фото технадзора:\n" + summary
        return _T5V2_ORIG_PROCESS_TECHNADZOR(text=enriched, task_id=task_id, chat_id=chat, topic_id=5, file_path=file_path, file_name=file_name, **kwargs)

    return _T5V2_ORIG_PROCESS_TECHNADZOR(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs)
# === END_FULLFIX_TOPIC5_TECHNADZOR_CANON_CONTOUR_V2_TECHNADZOR ===

# === P6H_VISION_BLOCKED_FALLBACK_V1 ===
# CANON §17: когда Vision заблокирован — строить акт из текста/голоса владельца
# + метаданных файла + предыдущих актов, не останавливаться.
# Сообщение в документе: "Визуальный анализ фото не выполнялся..."
import logging as _p6hvbf_log
_P6HVBF_LOG = _p6hvbf_log.getLogger("technadzor_engine")

_P6HVBF_ORIG = p6f_tnz_handle_photo_act_real

async def p6f_tnz_handle_photo_act_real(file_path, file_name, task_id, chat_id, topic_id, user_text=""):  # noqa: F811
    vision, vstatus = await _p6f_tnz_vision_via_openrouter(file_path)
    if vstatus == "EXTERNAL_PHOTO_ANALYSIS_BLOCKED":
        # Canon §17: Vision blocked → build act from owner text + file metadata
        _P6HVBF_LOG.info("P6HVBF_VISION_BLOCKED_FALLBACK file=%s user_text_len=%s", file_name, len(user_text or ""))
        vision = {
            "summary": (
                "Автоматический визуальный анализ фото не выполнялся, так как Vision заблокирован. "
                "Выводы основаны на предыдущих актах, пояснениях владельца и доступных именах/метаданных файлов."
            ),
            "defects": [],
            "confidence": "LOW",
            "_vision_blocked": True,
        }
        if user_text and str(user_text).strip():
            vision["summary"] += "\n\nПояснение владельца: " + str(user_text).strip()
        if file_name:
            vision["summary"] += "\n\nФайл: " + str(file_name)
        vstatus = "BLOCKED_FALLBACK"
    # delegate to original with resolved vision
    # re-enter original logic but skip first vision call
    if vision is None:
        return await _P6HVBF_ORIG(file_path, file_name, task_id, chat_id, topic_id, user_text)
    # replicate original body with already-resolved vision
    import os as _p6hvbf_os
    from datetime import datetime as _p6hvbf_dt
    norms_text = (vision.get("summary", "") or "") + " " + str(user_text or "")
    confirmed_norms, _ = _p6f_tnz_norms_block(norms_text)
    docx_lines = _p6f_tnz_build_docx_lines(vision, confirmed_norms, file_name, task_id)
    ts = _p6hvbf_dt.now().strftime("%Y%m%d_%H%M%S")
    safe = (str(task_id or ts)[:8] or ts).replace("/", "_").replace("\\", "_")
    out_dir = "/root/.areal-neva-core/outputs/technadzor_acts"
    _p6hvbf_os.makedirs(out_dir, exist_ok=True)
    docx_path = "{}/TECHNADZOR_ACT_PHOTO__{}_{}.docx".format(out_dir, safe, ts)
    written = _p6tz_make_docx(docx_path, docx_lines)
    if not written:
        return {
            "ok": False, "handled": True, "kind": "technadzor_photo_act",
            "state": "FAILED",
            "message": "Ошибка создания DOCX акта",
            "history": "P6HVBF_DOCX_WRITE_FAIL",
        }
    drive_link, ustatus = await _p6f_tnz_upload_to_topic(
        docx_path, _p6hvbf_os.path.basename(docx_path), chat_id or "-1003725299009", topic_id or 5
    )
    defects_count = len(vision.get("defects") or [])
    norms_count = len(confirmed_norms)
    public_lines = [
        "Акт технического надзора сформирован (Vision заблокирован — анализ по тексту владельца)",
        "Файл: " + str(file_name or ""),
        "Дефектов в тексте: {}".format(defects_count),
        "Нормативных ссылок: {}".format(norms_count) if norms_count else "Нормативная база: норма не подтверждена",
    ]
    if drive_link:
        public_lines.append("Drive DOCX: " + str(drive_link))
    return {
        "ok": bool(drive_link),
        "handled": True,
        "kind": "technadzor_photo_act",
        "message": "\n".join(public_lines),
        "state": "DONE" if drive_link else "AWAITING_CONFIRMATION",
        "drive_link": drive_link or "",
        "history": "P6HVBF:vision={},defects={},norms={},upload={}".format(
            vstatus, defects_count, norms_count, "OK" if drive_link else "FAIL"
        ),
    }

p6f_tnz_handle_photo_act_real._p6hvbf_wrapped = True
_P6HVBF_LOG.info("P6H_VISION_BLOCKED_FALLBACK_V1_INSTALLED")
# === END_P6H_VISION_BLOCKED_FALLBACK_V1 ===

# === P6_ACT_MATERIAL_FILTER_V1 ===
# Canon §4/§5: в акт только реальные фото + пояснения к дефектам.
# Фильтрует буфер перед тем как enriched-текст попадёт в LLM:
# - исключает PDF/XLSX/DOCX (образцы, старые акты, таблицы)
# - удаляет служебные команды из voice_comment
# - передаёт объект/адрес/основание из active_folder в заголовок акта
import logging as _p6amf_log
import re as _p6amf_re

_P6AMF_LOG = _p6amf_log.getLogger("technadzor_engine")

_P6AMF_SERVICE_PATTERNS = [
    "сделай акт", "делай акт", "оформи акт", "собери акт", "готовь акт",
    "формируй акт", "сделать акт", "финальный акт",
    "добавь в папку", "добавить в папку", "добавить в эту папку",
    "не в тот чат", "не туда", "ошибочно",
    "это тест", "тест надзор", "проверка связи",
    "ты добавил", "добавил все", "ты все добавил",
    "какой адрес", "какой у него адрес",
    "дай мне нормы", "дай нормы",
]

_P6AMF_NON_PHOTO_EXT = (".xlsx", ".xls", ".pdf", ".docx", ".doc", ".pptx")
_P6AMF_NON_PHOTO_TYPES = ("PDF", "XLSX", "XLS", "DOCX", "DOC", "OTHER")

def _p6amf_is_service_comment(text):
    if not text:
        return False
    low = str(text).lower().strip()
    return any(p in low for p in _P6AMF_SERVICE_PATTERNS)

def _p6amf_is_real_photo(m):
    """True only for real photo materials that belong in the act."""
    ft = str(m.get("file_type", "PHOTO")).upper()
    if ft in _P6AMF_NON_PHOTO_TYPES:
        return False
    fn = str(m.get("file_name", "")).lower()
    if any(fn.endswith(ext) for ext in _P6AMF_NON_PHOTO_EXT):
        return False
    if m.get("include_in_act") is False:
        return False
    return True

def _p6amf_clean_comment(text):
    """Return comment if substantive, empty string if service command."""
    if _p6amf_is_service_comment(text):
        return ""
    return str(text or "").strip()

def _p6amf_build_enriched(raw, active_folder, materials):
    """Build structured enriched text for act LLM call."""
    obj = active_folder.get("object_name") or active_folder.get("folder_name") or ""
    addr = active_folder.get("object_address") or obj
    basis = active_folder.get("visit_basis") or ""
    src = active_folder.get("source_request") or ""
    instructions = active_folder.get("owner_instructions") or []

    # Filter to real photos only
    photos = [m for m in materials if _p6amf_is_real_photo(m)]
    # Excluded non-photo files (for reference note only)
    excluded = [m for m in materials if not _p6amf_is_real_photo(m)]

    lines = ["КОМАНДА: Сформировать акт технического надзора", ""]
    if obj:
        lines.append(f"ОБЪЕКТ: {obj}")
    if addr and addr != obj:
        lines.append(f"АДРЕС: {addr}")
    if basis:
        lines.append(f"ОСНОВАНИЕ: {basis}")
    if src:
        lines.append(f"ИСТОЧНИК ЗАЯВКИ: {src}")
    lines.append("")

    if instructions:
        lines.append("ИНСТРУКЦИИ ВЛАДЕЛЬЦА:")
        # Skip command-like instructions
        for ins in instructions:
            if not _p6amf_is_service_comment(ins):
                lines.append("— " + str(ins).strip())
        lines.append("")

    lines.append(f"ФОТОМАТЕРИАЛЫ ОБЪЕКТА ({len(photos)} шт.):")
    for i, m in enumerate(photos, 1):
        fn = m.get("file_name", "")
        lines.append(f"Фото №{i}: {fn}")
        vc = _p6amf_clean_comment(m.get("voice_comment", ""))
        if vc:
            lines.append(f"  Пояснение: {vc}")
        du = m.get("drive_url", "")
        if du:
            lines.append(f"  Ссылка: {du}")
    lines.append("")

    if excluded:
        lines.append(f"Справочные файлы (не входят в фотофиксацию): {', '.join(m.get('file_name','') for m in excluded)}")
        lines.append("")

    return "\n".join(lines)

# Wrap process_technadzor to intercept act command path
_P6AMF_ORIG_PT = process_technadzor

def process_technadzor(text="", task_id="", chat_id="", topic_id=0, file_path="", file_name="", **kwargs):  # noqa: F811
    try:
        tid = int(topic_id or (kwargs.get("topic_id") or 0))
    except Exception:
        tid = 0
    if tid != 5:
        return _P6AMF_ORIG_PT(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id,
                               file_path=file_path, file_name=file_name, **kwargs)

    # Only intercept act command path
    raw = str(text or "").strip()
    if not _t5v2_positive_act(raw):
        return _P6AMF_ORIG_PT(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id,
                               file_path=file_path, file_name=file_name, **kwargs)

    try:
        chat = str(chat_id or "")
        buf = _t5v2_load_buf(chat)
        materials = buf.get("materials", [])
        if not materials:
            return _P6AMF_ORIG_PT(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id,
                                   file_path=file_path, file_name=file_name, **kwargs)

        active_folder = get_active_folder(chat, 5) or {}
        enriched = _p6amf_build_enriched(raw, active_folder, materials)

        photo_count = len([m for m in materials if _p6amf_is_real_photo(m)])
        excluded_count = len(materials) - photo_count
        _P6AMF_LOG.info(
            "P6AMF_ACT_FILTER chat=%s photos=%s excluded=%s obj=%s",
            chat, photo_count, excluded_count, active_folder.get("object_name", "")
        )
        return _P6AMF_ORIG_PT(text=enriched, task_id=task_id, chat_id=chat, topic_id=5,
                               file_path=file_path, file_name=file_name, **kwargs)
    except Exception as _e:
        _P6AMF_LOG.exception("P6AMF_ERR %s", _e)
        return _P6AMF_ORIG_PT(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id,
                               file_path=file_path, file_name=file_name, **kwargs)

process_technadzor._p6amf_wrapped = True
_P6AMF_LOG.info("P6_ACT_MATERIAL_FILTER_V1_INSTALLED")
# === END_P6_ACT_MATERIAL_FILTER_V1 ===


# === PATCH_TOPIC5_CANONICAL_ACT_ENGINE_V3 ===
# АКТ ОСМОТРА ОБЪЕКТА — TECHNADZOR_DOMAIN_LOGIC_CANON
# 8 разделов, таблица замечаний 8 колонок.
# ok=True если файлы сгенерированы, даже если upload упал.
# Dispatcher отвечает за upload fallback и НИКОГДА не вызывает старый дамп при ok=True.

import json as _t5ca_json
import logging as _t5ca_logging
import tempfile as _t5ca_tmp
from datetime import datetime as _t5ca_dt
from pathlib import Path as _t5ca_Path

_T5CA_LOG = _t5ca_logging.getLogger("technadzor_engine")
_T5CA_DATA = _t5ca_Path("/root/.areal-neva-core/data/technadzor")
_T5CA_SPECIALIST = "Кузнецов Илья Владимирович"
_T5CA_DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_T5CA_DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_T5CA_NORM_NONE = "норма не подтверждена"

_T5CA_PHOTO_EXT = (".jpg", ".jpeg", ".png", ".webp", ".heic")
_T5CA_NON_PHOTO_TYPES = ("PDF", "XLSX", "XLS", "DOCX", "DOC", "OTHER")
# Фразы-мусор — не включать в замечания
_T5CA_GARBAGE = [
    "сделай акт", "делай акт", "оформи акт", "финальный акт", "итоговый акт",
    "добавь в папку", "добавить в папку", "нужно добавить в папку",
    "не в тот чат", "это тест", "тест надзор", "проверка связи",
    "ты добавил", "добавил все", "какой адрес", "дай нормы", "дай мне нормы",
    "какую задачу", "что по итогу", "видишь их да или нет",
    "делай финальный", "сделай мне пожалуйста акт", "положи в правильную папку",
]


def _t5ca_s(v, limit=50000):
    try:
        return "" if v is None else str(v).strip()[:limit]
    except Exception:
        return ""


def _t5ca_read_json(path):
    try:
        with open(str(path), encoding="utf-8") as _f:
            return _t5ca_json.load(_f)
    except Exception:
        return {}


def _t5ca_is_photo(m):
    fn = _t5ca_s(m.get("file_name", "")).lower()
    ft = _t5ca_s(m.get("file_type", "")).upper()
    if ft == "PHOTO":
        return True
    if ft in _T5CA_NON_PHOTO_TYPES:
        return False
    return any(fn.endswith(e) for e in _T5CA_PHOTO_EXT)


def _t5ca_is_garbage(text):
    low = _t5ca_s(text).lower()
    return any(p in low for p in _T5CA_GARBAGE)


def _t5ca_match_norms(text):
    """Нормы только если norm_id непустой — не выдумывать."""
    if not text or not text.strip():
        return []
    try:
        from core.normative_engine import search_norms_sync
        raw = search_norms_sync(str(text), limit=5)
        return [n for n in (raw or []) if n.get("norm_id")]
    except Exception:
        return []


def _t5ca_norm_str(comment):
    norms = _t5ca_match_norms(comment)
    if norms:
        parts = []
        for n in norms[:2]:
            nid = _t5ca_s(n.get("norm_id", ""))
            sec = _t5ca_s(n.get("section", ""))
            parts.append(f"{nid} — {sec}" if sec else nid)
        return "; ".join(parts)
    return _T5CA_NORM_NONE


def _t5ca_register_fonts():
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        if "T5CADejavu" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("T5CADejavu", _T5CA_DEJAVU))
        if "T5CADejavuB" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("T5CADejavuB", _T5CA_DEJAVU_BOLD))
        return True
    except Exception:
        return False


def _t5ca_cell_w(cell, emu):
    try:
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        twips = str(max(1, int(emu / 635)))
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        for old in tcPr.findall(qn("w:tcW")):
            tcPr.remove(old)
        tcW = OxmlElement("w:tcW")
        tcW.set(qn("w:w"), twips)
        tcW.set(qn("w:type"), "dxa")
        tcPr.append(tcW)
    except Exception:
        pass


def _t5ca_build_sections(af, materials):
    """Build all content lists needed for the act."""
    obj_name = _t5ca_s(af.get("object_name", ""))
    obj_addr = _t5ca_s(af.get("object_address") or af.get("object_name") or "")
    obj_loc = (obj_addr or obj_name)[:40]
    visit_basis = _t5ca_s(af.get("visit_basis", "запрос заказчика"))
    source_req = _t5ca_s(af.get("source_request", ""))

    file_count = len(materials)
    photo_count = sum(1 for m in materials if _t5ca_is_photo(m))

    # remark_rows: №, Фото, Узел/место, Нарушение, Последствия, Что сделать, Норматив, Статус
    remark_rows = []
    all_comments = []
    all_files = []

    for idx, m in enumerate(materials, 1):
        fn = _t5ca_s(m.get("file_name", f"файл_{idx}"), 80)
        all_files.append(fn)
        if not _t5ca_is_photo(m):
            continue
        raw = _t5ca_s(m.get("voice_comment") or m.get("comment") or "")
        comment = "" if _t5ca_is_garbage(raw) else raw[:300]
        if comment:
            all_comments.append(comment)

        norm_col = _t5ca_norm_str(comment) if comment else _T5CA_NORM_NONE

        lc = comment.lower() if comment else ""
        if "заменить" in lc or "старое оборудование" in lc or "вышло из строя" in lc:
            rec = "Рекомендуется заменить"
        elif "сварн" in lc or "шов" in lc:
            rec = "Необходимо проверить качество сварных соединений"
        elif "примыкание" in lc or "щельник" in lc:
            rec = "Рекомендуется выполнить нормальное примыкание"
        elif comment:
            rec = "Рекомендуется повторный осмотр после устранения"
        else:
            rec = ""

        remark_rows.append([
            str(idx), fn, obj_loc,
            comment or "—", "",   # Нарушение, Последствия (manual)
            rec, norm_col, "Открыто",
        ])

    facts = list(dict.fromkeys(c for c in all_comments if c))[:20]

    recs = []
    for comment in all_comments:
        lc = comment.lower()
        if "заменить" in lc or "старое оборудование" in lc:
            recs.append(f"Рекомендуется заменить: {comment[:200]}")
        elif "примыкание" in lc or "щельник" in lc:
            recs.append(f"Рекомендуется выполнить нормальное примыкание: {comment[:200]}")
        elif "сварн" in lc:
            recs.append(f"Необходимо проверить сварные соединения: {comment[:200]}")
    for inst in af.get("owner_instructions", []):
        ci = _t5ca_s(inst)
        if _t5ca_is_garbage(ci):
            continue
        lc = ci.lower()
        if any(x in lc for x in ("рекоменд", "нужно", "необходимо")):
            recs.append(ci[:300])
    recs = list(dict.fromkeys(recs))[:20]

    conseqs = []
    for comment in all_comments:
        lc = comment.lower()
        if "старое оборудование" in lc or "вышло из строя" in lc:
            conseqs.append("Выход оборудования из строя, аварийная ситуация")
        if "сварн" in lc or "шов" in lc:
            conseqs.append("Разрушение сварного соединения, нарушение несущей способности")
        if "примыкание" in lc or "щельник" in lc:
            conseqs.append("Проникновение влаги, нарушение теплоизоляции")
    conseqs = list(dict.fromkeys(conseqs))[:10]

    norms_global = _t5ca_match_norms(" ".join(all_comments))
    norms_found = [r[6] for r in remark_rows if r[6] and r[6] != _T5CA_NORM_NONE]

    basis = f"Основание: {visit_basis}." + (f" Источник: {source_req}." if source_req else "")

    return dict(
        obj_name=obj_name, obj_addr=obj_addr, file_count=file_count,
        photo_count=photo_count, all_files=all_files,
        remark_rows=remark_rows, facts=facts, recs=recs, conseqs=conseqs,
        norms_global=norms_global, norms_found=norms_found, basis=basis,
    )


def _t5ca_write_docx(dst, act_num, date_str, af, sec):
    try:
        from docx import Document
        from docx.shared import Cm, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        obj_name = sec["obj_name"]
        obj_addr = sec["obj_addr"]
        folder_name = _t5ca_s(af.get("folder_name", ""))

        doc = Document()
        s = doc.sections[0]
        s.page_width, s.page_height = s.page_height, s.page_width
        s.left_margin = s.right_margin = Cm(2)
        s.top_margin = Cm(2)
        s.bottom_margin = Cm(1.5)

        h = doc.add_heading(f"АКТ ОСМОТРА ОБЪЕКТА № {act_num}", level=1)
        h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub = doc.add_paragraph("Методом визуального неразрушающего контроля")
        sub.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph(f"Дата осмотра: {date_str}")
        doc.add_paragraph(f"Место осмотра: {obj_addr or obj_name}")
        doc.add_paragraph(f"Объект осмотра: {obj_name}")
        doc.add_paragraph(f"Основание осмотра: {sec['basis']}")
        doc.add_paragraph(f"Метод обследования: визуальный неразрушающий контроль с выездом на объект")
        doc.add_paragraph(f"Технический специалист: {_T5CA_SPECIALIST}")
        if folder_name:
            doc.add_paragraph(f"Ссылка на фотоматериалы: папка Drive «{folder_name}»")

        doc.add_heading("1. Общие сведения", level=2)
        doc.add_paragraph(
            "Осмотр выполнен методом визуального неразрушающего контроля с выездом на объект. "
            "Цель — выявление фактически наблюдаемых дефектов и формирование рекомендаций "
            "по их устранению."
        )
        doc.add_paragraph(
            f"Файлов в пакете: {sec['file_count']}. Фотоматериалов: {sec['photo_count']}."
        )

        doc.add_heading("2. Основание текущего осмотра", level=2)
        doc.add_paragraph(sec["basis"])

        doc.add_heading("3. Установлено по факту осмотра", level=2)
        if sec["facts"]:
            for i, f in enumerate(sec["facts"], 1):
                doc.add_paragraph(f"{i}. {f[:400]}", style="List Number")
        else:
            doc.add_paragraph("Данные фиксируются по пояснениям владельца и фотоматериалам.")

        doc.add_heading("4. Рекомендовано к устранению", level=2)
        if sec["recs"]:
            for i, r in enumerate(sec["recs"], 1):
                doc.add_paragraph(f"{i}. {r[:400]}", style="List Number")
        else:
            doc.add_paragraph("Рекомендации формируются по результатам детального осмотра.")

        doc.add_heading("5. Возможные последствия при отсутствии устранения", level=2)
        if sec["conseqs"]:
            for c in sec["conseqs"]:
                doc.add_paragraph(f"— {c[:300]}", style="List Bullet")
        else:
            doc.add_paragraph("Последствия определяются по характеру выявленных дефектов.")

        doc.add_heading("6. Таблица замечаний", level=2)
        col_hdrs = ["№", "Фото", "Узел/место", "Нарушение",
                    "Последствия", "Что сделать", "Норматив", "Статус"]
        col_emu = [int(c * 360000) for c in [0.7, 3.2, 2.5, 5.0, 3.0, 4.0, 4.5, 1.8]]
        tbl = doc.add_table(rows=1, cols=8)
        tbl.style = "Table Grid"
        hc = tbl.rows[0].cells
        for i, ht in enumerate(col_hdrs):
            hc[i].text = ht
            _t5ca_cell_w(hc[i], col_emu[i])
            for p in hc[i].paragraphs:
                for run in p.runs:
                    run.bold = True
                    run.font.size = Pt(8)
        for row_data in sec["remark_rows"]:
            row = tbl.add_row().cells
            for i, val in enumerate(row_data):
                row[i].text = _t5ca_s(val, 300)
                _t5ca_cell_w(row[i], col_emu[i])
                for p in row[i].paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(8)

        doc.add_heading("7. Заключение", level=2)
        if sec["norms_found"]:
            doc.add_paragraph(
                f"По результатам осмотра выявлены дефекты. "
                f"Нормативные документы: {'; '.join(dict.fromkeys(sec['norms_found'][:3]))}. "
                "Рекомендуется выполнить мероприятия из раздела 4 "
                "и провести повторный осмотр после их устранения."
            )
        else:
            doc.add_paragraph(
                "По результатам осмотра зафиксированы замечания согласно таблице. "
                "Нормативные пункты не подтверждены без дополнительного анализа. "
                "Рекомендуется повторный осмотр после устранения."
            )

        doc.add_heading("8. Приложение: перечень фото и документов", level=2)
        doc.add_paragraph(
            f"Фотоматериалов: {sec['photo_count']} шт. "
            f"Файлов в пакете: {sec['file_count']} шт."
        )
        for fn in sec["all_files"]:
            doc.add_paragraph(f"— {fn}", style="List Bullet")

        doc.add_paragraph("")
        doc.add_paragraph(
            f"Технический специалист: {_T5CA_SPECIALIST}     _____________     {date_str}"
        )
        doc.add_paragraph(
            "Представитель заказчика: _______________________     _____________     ___________"
        )

        doc.save(str(dst))
        return True
    except Exception as _e:
        _T5CA_LOG.exception("T5CA_DOCX_ERR %s", _e)
        return False


def _t5ca_write_pdf(dst, act_num, date_str, af, sec):
    try:
        from reportlab.lib.pagesizes import A4, landscape as _ls
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors

        ok = _t5ca_register_fonts()
        base = "T5CADejavu" if ok else "Helvetica"
        bold = "T5CADejavuB" if ok else "Helvetica-Bold"

        st = lambda name, **kw: ParagraphStyle(name, fontName=base, **kw)  # noqa: E731
        sb = lambda name, **kw: ParagraphStyle(name, fontName=bold, **kw)  # noqa: E731

        sty_t = sb("t5t", fontSize=13, alignment=1, spaceAfter=3)
        sty_s = st("t5s", fontSize=10, alignment=1, spaceAfter=6, textColor=colors.grey)
        sty_h = sb("t5h", fontSize=11, spaceBefore=8, spaceAfter=3)
        sty_b = st("t5b", fontSize=10, leading=13, spaceAfter=2)
        sty_sm = st("t5sm", fontSize=7, leading=9)
        sty_smb = sb("t5smb", fontSize=7, leading=9)

        obj_name = sec["obj_name"]
        obj_addr = sec["obj_addr"]
        folder_name = _t5ca_s(af.get("folder_name", ""))

        flow = []
        flow.append(Paragraph(f"АКТ ОСМОТРА ОБЪЕКТА № {act_num}", sty_t))
        flow.append(Paragraph("Методом визуального неразрушающего контроля", sty_s))
        flow.append(Paragraph(f"Дата: {date_str}  |  Объект: {obj_name}", sty_b))
        flow.append(Paragraph(f"Место: {obj_addr or obj_name}", sty_b))
        flow.append(Paragraph(f"Основание: {sec['basis']}", sty_b))
        flow.append(Paragraph(f"Технический специалист: {_T5CA_SPECIALIST}", sty_b))
        if folder_name:
            flow.append(Paragraph(f"Фотоматериалы: папка Drive «{folder_name}»", sty_b))
        flow.append(Spacer(1, 6))

        flow.append(Paragraph("1. Общие сведения", sty_h))
        flow.append(Paragraph(
            "Осмотр выполнен методом визуального неразрушающего контроля. "
            f"Файлов в пакете: {sec['file_count']}. Фотоматериалов: {sec['photo_count']}.",
            sty_b,
        ))

        flow.append(Paragraph("2. Основание текущего осмотра", sty_h))
        flow.append(Paragraph(sec["basis"], sty_b))

        flow.append(Paragraph("3. Установлено по факту осмотра", sty_h))
        if sec["facts"]:
            for i, f in enumerate(sec["facts"], 1):
                flow.append(Paragraph(f"{i}. {f[:400]}", sty_b))
        else:
            flow.append(Paragraph(
                "Данные фиксируются по пояснениям владельца и фотоматериалам.", sty_b))

        flow.append(Paragraph("4. Рекомендовано к устранению", sty_h))
        if sec["recs"]:
            for i, r in enumerate(sec["recs"], 1):
                flow.append(Paragraph(f"{i}. {r[:400]}", sty_b))
        else:
            flow.append(Paragraph("Рекомендации формируются по результатам осмотра.", sty_b))

        flow.append(Paragraph("5. Возможные последствия при отсутствии устранения", sty_h))
        if sec["conseqs"]:
            for c in sec["conseqs"]:
                flow.append(Paragraph(f"— {c[:300]}", sty_b))
        else:
            flow.append(Paragraph(
                "Последствия определяются по характеру выявленных дефектов.", sty_b))

        flow.append(Paragraph("6. Таблица замечаний", sty_h))
        col_hdrs = ["№", "Фото", "Узел/место", "Нарушение",
                    "Последствия", "Что сделать", "Норматив", "Статус"]
        col_w = [0.7*cm, 3.2*cm, 2.5*cm, 5.0*cm, 3.0*cm, 4.0*cm, 4.5*cm, 1.8*cm]
        rows = [[Paragraph(h, sty_smb) for h in col_hdrs]]
        for r in sec["remark_rows"]:
            rows.append([Paragraph(_t5ca_s(c, 250), sty_sm) for c in r])
        tbl = Table(rows, colWidths=col_w, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), base),
            ("FONTNAME", (0, 0), (-1, 0), bold),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        flow.append(tbl)
        flow.append(Spacer(1, 6))

        flow.append(Paragraph("7. Заключение", sty_h))
        if sec["norms_found"]:
            flow.append(Paragraph(
                f"Выявлены дефекты. Нормативные документы: "
                f"{'; '.join(dict.fromkeys(sec['norms_found'][:3]))}. "
                "Рекомендуется повторный осмотр после устранения.",
                sty_b,
            ))
        else:
            flow.append(Paragraph(
                "Зафиксированы замечания. Нормативные пункты не подтверждены без анализа. "
                "Рекомендуется повторный осмотр после устранения.",
                sty_b,
            ))

        flow.append(Paragraph("8. Приложение: перечень фото и документов", sty_h))
        flow.append(Paragraph(
            f"Фото: {sec['photo_count']} шт., файлов в пакете: {sec['file_count']} шт.",
            sty_b,
        ))
        for fn in sec["all_files"]:
            flow.append(Paragraph(f"— {fn}", sty_sm))

        flow.append(Spacer(1, 12))
        flow.append(Paragraph(
            f"Технический специалист: {_T5CA_SPECIALIST}     ___________     {date_str}",
            sty_b,
        ))
        flow.append(Paragraph(
            "Представитель заказчика: _______________________     ___________     ___________",
            sty_b,
        ))

        SimpleDocTemplate(
            str(dst), pagesize=_ls(A4),
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm,
        ).build(flow)
        return True
    except Exception as _e:
        _T5CA_LOG.exception("T5CA_PDF_ERR %s", _e)
        return False


def t5_canonical_act_generate(chat_id: str, topic_id: int, task_id: str) -> dict:
    """
    PATCH_TOPIC5_CANONICAL_ACT_ENGINE_V3
    ok=True если DOCX или PDF сгенерированы (даже без upload).
    Dispatcher отвечает за fallback upload.
    """
    markers = []
    result = {
        "ok": False, "docx_link": "", "pdf_link": "",
        "docx_path": "", "pdf_path": "",
        "photo_count": 0, "file_count": 0, "norm_count": 0,
        "obj_name": "", "obj_addr": "", "folder_name": "", "folder_id": "",
        "upload_ok": False, "error": "", "markers": markers,
    }
    try:
        buf = _t5ca_read_json(_T5CA_DATA / f"buf_{chat_id}_{topic_id}.json")
        af = _t5ca_read_json(_T5CA_DATA / f"active_folder_{chat_id}_{topic_id}.json")
        materials = buf.get("materials", [])

        result["obj_name"] = _t5ca_s(af.get("object_name", ""))
        result["obj_addr"] = _t5ca_s(af.get("object_address") or af.get("object_name") or "")
        result["folder_name"] = _t5ca_s(af.get("folder_name", ""))
        result["folder_id"] = _t5ca_s(af.get("folder_id", ""))

        if not materials:
            result["error"] = "NO_MATERIALS"
            return result

        sec = _t5ca_build_sections(af, materials)
        result["file_count"] = sec["file_count"]
        result["photo_count"] = sec["photo_count"]
        result["norm_count"] = len(sec["norms_global"])

        markers.append("TOPIC5_GARBAGE_FILTER_OK")
        markers.append("TOPIC5_ACT_STRUCTURE_OK")
        if sec["remark_rows"]:
            markers.append("TOPIC5_DEFECT_TABLE_OK")
        markers.append("TOPIC5_RECOMMENDATIONS_SECTION_OK")
        markers.append("TOPIC5_NORMATIVE_SECTION_OK")

        date_str = _t5ca_dt.now().strftime("%d.%m.%Y")
        act_num = _t5ca_dt.now().strftime("%d.%m/%y")
        safe = (task_id[:6] if task_id else "000000").upper()
        base_name = f"AKT_OSMOTRA_{safe}_{_t5ca_dt.now().strftime('%Y%m%d')}"

        out_dir = _t5ca_Path(_t5ca_tmp.gettempdir()) / f"areal_t5ca_{task_id}"
        out_dir.mkdir(parents=True, exist_ok=True)
        docx_path = out_dir / f"{base_name}.docx"
        pdf_path = out_dir / f"{base_name}.pdf"

        docx_ok = _t5ca_write_docx(docx_path, act_num, date_str, af, sec)
        if docx_ok and docx_path.exists():
            markers.append("TOPIC5_DOCX_CREATED")
            result["docx_path"] = str(docx_path)

        pdf_ok = _t5ca_write_pdf(pdf_path, act_num, date_str, af, sec)
        if pdf_ok and pdf_path.exists():
            markers.append("TOPIC5_PDF_CREATED")
            result["pdf_path"] = str(pdf_path)

        if not docx_ok and not pdf_ok:
            result["error"] = "FILE_GENERATION_FAILED"
            return result

        # ok=True means files are ready — dispatcher handles upload
        result["ok"] = True

        # Try service account upload
        folder_id = result["folder_id"]
        for path_key, link_key in (("docx_path", "docx_link"), ("pdf_path", "pdf_link")):
            fpath = result.get(path_key, "")
            if not fpath:
                continue
            try:
                from core.drive_service_account_uploader import upload_artifact_service_account
                lnk = upload_artifact_service_account(
                    fpath, name=_t5ca_Path(fpath).name,
                    folder_id=folder_id or None,
                ) or ""
                result[link_key] = lnk
            except Exception as _ue:
                _T5CA_LOG.warning("T5CA_SA_UPLOAD_WARN %s %s", path_key, _ue)

        if result["docx_link"] or result["pdf_link"]:
            markers.append("TOPIC5_DRIVE_LINKS_SAVED")
            result["upload_ok"] = True

        _T5CA_LOG.info(
            "T5CA_DONE task=%s photos=%s files=%s norms=%s docx=%s pdf=%s upload=%s",
            task_id, sec["photo_count"], sec["file_count"], len(sec["norms_global"]),
            docx_ok, pdf_ok, result["upload_ok"],
        )
        return result

    except Exception as _e:
        _T5CA_LOG.exception("T5CA_ERR task=%s %s", task_id, _e)
        result["error"] = _t5ca_s(str(_e), 200)
        return result


_T5CA_LOG.info("PATCH_TOPIC5_CANONICAL_ACT_ENGINE_V3 installed")
# === END_PATCH_TOPIC5_CANONICAL_ACT_ENGINE_V3 ===


# === CANON_TOPIC5_TECHNADZOR_ISOLATION_GUARD_V1 ===
_CANON_TOPIC5_ORIG_PROCESS_TECHNADZOR = process_technadzor


def process_technadzor(text="", task_id="", chat_id="", topic_id=0, file_path="", file_name="", **kwargs):  # noqa: F811
    try:
        tid = int(topic_id or kwargs.get("topic_id") or 0)
    except Exception:
        tid = 0
    if tid != 5:
        return {
            "ok": False,
            "handled": False,
            "state": "SKIPPED",
            "message": "",
            "history": "CANON_TOPIC5_TECHNADZOR_ISOLATION_GUARD_V1:SKIPPED_NON_TOPIC5",
        }
    return _CANON_TOPIC5_ORIG_PROCESS_TECHNADZOR(
        text=text,
        task_id=task_id,
        chat_id=chat_id,
        topic_id=topic_id,
        file_path=file_path,
        file_name=file_name,
        **kwargs,
    )


# === END_CANON_TOPIC5_TECHNADZOR_ISOLATION_GUARD_V1 ===

====================================================================================================
END_FILE: core/technadzor_engine.py
FILE_CHUNK: 1/1
====================================================================================================
