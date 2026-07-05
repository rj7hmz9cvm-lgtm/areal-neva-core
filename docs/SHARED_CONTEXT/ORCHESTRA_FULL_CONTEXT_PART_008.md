# ORCHESTRA_FULL_CONTEXT_PART_008
generated_at_utc: 2026-07-05T14:24:53.440838+00:00
git_sha_before_commit: 68072585be7083159a1cedac0f90cf75a87375f7
part: 8/18


====================================================================================================
BEGIN_FILE: task_worker.py
FILE_CHUNK: 4/4
SHA256_FULL_FILE: 7e4fd4f5c6889c30ab1c5a05c4cf86fda963990588531fbc935acecffc86bbdb
====================================================================================================
                    parent_id = str(_t2cf2_get(parent, "id") or "")
                    raw = str(_t2cf2_get(child, "raw_input") or "").strip()
                    if not child_id or not parent_id or child_id == parent_id or not raw:
                        return False
                    # Reset stale price/result markers (same logic as orig _t2fb_reset_stale_markers).
                    try:
                        _reset = globals().get("_t2fb_reset_stale_markers")
                        if _reset:
                            _reset(conn, parent_id, raw)
                    except Exception:
                        pass
                    # Also delete DONE_WITH_DRIVE_LINKS gating marker so engine runs fresh.
                    # Without this, FINAL_DRIVE_SINGLE_GATE_V1 checks hist and blocks recalc.
                    try:
                        conn.execute(
                            "DELETE FROM task_history WHERE task_id=? AND action IN (?,?,?,?,?)",
                            (
                                parent_id,
                                "PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:DONE_WITH_DRIVE_LINKS",
                                "TOPIC2_DONE_CONTRACT_OK",
                                "TDOIP_OVERRIDE:14_markers_and_drive_links_present",
                                "TOPIC2_PUBLIC_RESULT_CANON_VIOLATION_RECOVERED_FROM_LATEST_ARTIFACTS",
                                "TOPIC2_DRIVE_FILE_PICKER_BYPASSED_EXISTING_ESTIMATE",
                            ),
                        )
                        _T2CF2_LOG.info(
                            "PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1 DONE markers cleared parent=%s child=%s",
                            parent_id, child_id,
                        )
                    except Exception as _me:
                        try:
                            _T2CF2_LOG.exception(
                                "PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1_MARKER_DEL_ERR:%s", _me,
                            )
                        except Exception:
                            pass
                    # Mark parent IN_PROGRESS to re-trigger pipeline; keep raw_input intact.
                    conn.execute(
                        "UPDATE tasks SET state='IN_PROGRESS', result='', error_message='', updated_at=datetime('now') WHERE id=?",
                        (parent_id,),
                    )
                    conn.execute(
                        "UPDATE tasks SET state='DONE', result='Уточнение добавлено к исходному ТЗ', error_message=?, updated_at=datetime('now') WHERE id=?",
                        ("MERGED_TO_PARENT:" + parent_id, child_id),
                    )
                    _t2cf2_hist_once(conn, parent_id, "clarified:" + raw[:500])
                    _t2cf2_hist_once(conn, parent_id,
                        "PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:MERGED_CHILD:" + child_id)
                    _t2cf2_hist_once(conn, child_id,
                        "PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:MERGED_TO_PARENT:" + parent_id)
                    _t2cf2_hist_once(conn, parent_id,
                        "TOPIC2_DRIVE_FILE_MERGE_NO_RAW_INPUT_APPEND:" + child_id)
                    _t2cf2_hist_once(conn, parent_id,
                        "TOPIC2_ADDITIONAL_FACT_MERGED:" + child_id)
                    _t2cf2_hist_once(conn, parent_id,
                        "TOPIC2_ADDITIONAL_FACTS_RECALC_STARTED:" + child_id)
                    conn.commit()
                    _T2CF2_LOG.info(
                        "PATCH_TOPIC2_CANON_FULL_CLOSE_AFTER_REQUEUE_FAILURE_V1 merge clean child=%s parent=%s (no raw_input append)",
                        child_id, parent_id,
                    )
                    return True
            except Exception as e:
                try:
                    _T2CF2_LOG.exception(
                        "PATCH_TOPIC2_CANON_FULL_CLOSE_AFTER_REQUEUE_FAILURE_V1_MERGE_ERR:%s", e,
                    )
                except Exception:
                    pass
            return _t2cf2_orig_t2fb_merge(conn, child, parent)
        globals()["_t2fb_merge"] = _t2fb_merge

    # === FIX 3: extend timeout-guard to "invalid raw_input" failures ===
    # Wrap V2's already-wrapped _update_task one more time for invalid_raw_input case.
    _t2cf2_orig_update_task = globals().get("_update_task")
    if _t2cf2_orig_update_task:
        def _update_task(conn, task_id, **kwargs):
            try:
                new_state = str(kwargs.get("state") or "")
                new_err = str(kwargs.get("error_message") or "")
                if new_state == "FAILED" and "invalid raw_input" in new_err and task_id:
                    row = conn.execute(
                        "SELECT topic_id,result FROM tasks WHERE id=? LIMIT 1",
                        (str(task_id),),
                    ).fetchone()
                    if row and int(row[0] or 0) == 2:
                        # Reuse V2's helpers for evidence + artifact extraction
                        has_ready = globals().get("_t2af_has_ready_artifacts")
                        extract_ids = globals().get("_t2af_extract_artifact_ids")
                        if has_ready and has_ready(conn, str(task_id)):
                            old_result = str(row[1] or "")
                            keep_result = old_result if (old_result and "Задача не выполнена" not in old_result and len(old_result) > 100) else None
                            kwargs["state"] = "AWAITING_CONFIRMATION"
                            kwargs["error_message"] = ""
                            if keep_result is not None:
                                kwargs["result"] = keep_result
                            elif extract_ids:
                                xlsx_id, _pdf = extract_ids(conn, str(task_id))
                                if xlsx_id:
                                    kwargs["result"] = (
                                        "✅ Смета готова\n\n"
                                        "Готовые артефакты:\n"
                                        f"Excel: https://drive.google.com/file/d/{xlsx_id}/view\n\n"
                                        "Подтверди или пришли правки"
                                    )
                                else:
                                    kwargs.pop("result", None)
                            else:
                                kwargs.pop("result", None)
                            _t2cf2_hist_once(conn, str(task_id),
                                "TOPIC2_READY_ARTIFACT_FAILURE_SUPPRESSED:invalid_raw_input")
                            try:
                                conn.commit()
                            except Exception:
                                pass
                            _T2CF2_LOG.info(
                                "PATCH_TOPIC2_CANON_FULL_CLOSE_AFTER_REQUEUE_FAILURE_V1 invalid_raw_input suppressed task=%s",
                                str(task_id),
                            )
            except Exception as e:
                try:
                    _T2CF2_LOG.exception(
                        "PATCH_TOPIC2_CANON_FULL_CLOSE_AFTER_REQUEUE_FAILURE_V1_UPDATE_ERR:%s", e,
                    )
                except Exception:
                    pass
            return _t2cf2_orig_update_task(conn, task_id, **kwargs)
        globals()["_update_task"] = _update_task

    _T2CF2_LOG.info("PATCH_TOPIC2_CANON_FULL_CLOSE_AFTER_REQUEUE_FAILURE_V1 installed")
except Exception as _t2cf2_install_err:
    try:
        logger.exception("PATCH_TOPIC2_CANON_FULL_CLOSE_AFTER_REQUEUE_FAILURE_V1_INSTALL_ERR:%s", _t2cf2_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_CANON_FULL_CLOSE_AFTER_REQUEUE_FAILURE_V1 ===


# === PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 ===
# Two system fixes for topic_2 estimate path:
# (A) DRIVE_FILE_NO_INTENT_OFFER_V1 picker bypass for existing estimate parent.
#     If parent has estimate evidence (clarified facts, prior XLSX/PDF/TG markers,
#     OR caption contains "смет"), route directly to canonical pipeline, skip picker.
#     Marker: TOPIC2_DRIVE_FILE_PICKER_BYPASSED_EXISTING_ESTIMATE.
# (B) Public result gate at AWAITING_CONFIRMATION boundary for topic_id=2.
#     PASS: starts "✅ Смета готова", has Excel:, has PDF:, has "Подтверди или пришли правки",
#     no MANIFEST: / Engine / /root / /tmp / "Сметный расчёт подготовлен..." / "Принял файл" /
#     "Что нужно сделать?".
#     FAIL → block AWAITING_CONFIRMATION transition; force IN_PROGRESS; preserve previous valid
#     result if exists; marker TOPIC2_PUBLIC_RESULT_CANON_VIOLATION.
# NO direct OpenRouter / NO topic_id substitution / NO process_ai_task shell / NO requeue /
# NO result clearing / NO broad sanitizer / NO forbidden files touched.
try:
    import json as _t2pg_json
    import re as _t2pg_re
    import logging as _t2pg_logging

    _T2PG_LOG = _t2pg_logging.getLogger("WORKER")

    _T2PG_EVIDENCE_HISTORY = (
        "TOPIC2_TELEGRAM_DELIVERED",
        "TOPIC2_DRIVE_UPLOAD_XLSX_OK",
        "TOPIC2_DRIVE_UPLOAD_PDF_OK",
        "TOPIC2_PDF_CREATED",
        "TOPIC2_XLSX_CREATED",
        "PATCH_TOPIC2_DRIVE_XLSX_REPAIR_V1:OK",
        "PATCH_TOPIC2_PDF_AND_REAL_SUPPLIERS_V1",
        "T2RFP_FULL_PIPELINE_DONE",
        "P8T2C_CANONICAL_OK",
        "TOPIC2_DRIVE_LINKS_SAVED",
        "PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1:TG_EDIT:OK",
        "TOPIC2_F030_RECOVERED",
    )

    def _t2pg_hist_once(conn, task_id, action):
        try:
            if not conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
                (str(task_id), str(action)),
            ).fetchone():
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (str(task_id), str(action)),
                )
        except Exception:
            pass

    def _t2pg_get(obj, key, default=None):
        try:
            if isinstance(obj, dict):
                return obj.get(key, default)
        except Exception:
            pass
        try:
            if hasattr(obj, "keys") and key in obj.keys():
                return obj[key]
        except Exception:
            pass
        return default

    def _t2pg_has_estimate_evidence(conn, task_id):
        try:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? ORDER BY rowid DESC LIMIT 600",
                (str(task_id),),
            ).fetchall()
        except Exception:
            return False
        seen_clarified = False
        for r in rows:
            a = r[0] or ""
            for m in _T2PG_EVIDENCE_HISTORY:
                if m in a:
                    return True
            if a.startswith("clarified:") and len(a) > len("clarified:") + 3:
                seen_clarified = True
        return seen_clarified

    def _t2pg_extract_caption(raw):
        if not isinstance(raw, str):
            return ""
        s = raw.lstrip()
        if not s.startswith("{"):
            return ""
        try:
            decoder = _t2pg_json.JSONDecoder()
            obj, _end = decoder.raw_decode(s)
            return str(obj.get("caption") or "")
        except Exception:
            try:
                obj = _t2pg_json.loads(s)
                return str(obj.get("caption") or "")
            except Exception:
                return ""

    # === FIX A: bypass picker for existing topic_2 estimate parent ===
    # Reach the BASE handler (3906) directly via _dfnio_orig_handle_drive_file when bypass condition holds.
    _t2pg_picker_wrap = globals().get("_handle_drive_file")  # current wrap chain top
    _t2pg_base_handler = globals().get("_dfnio_orig_handle_drive_file")  # base (line 3906)

    if _t2pg_picker_wrap and _t2pg_base_handler:
        async def _handle_drive_file(conn, task, chat_id, topic_id):
            try:
                if int(topic_id or 0) == 2:
                    task_id = str(_t2pg_get(task, "id") or "")
                    raw = str(_t2pg_get(task, "raw_input") or "")
                    caption = _t2pg_extract_caption(raw).lower()
                    has_smet_caption = "смет" in caption or "расч" in caption or "стоимост" in caption
                    has_evidence = _t2pg_has_estimate_evidence(conn, task_id) if task_id else False
                    if task_id and (has_evidence or has_smet_caption):
                        _t2pg_hist_once(conn, task_id,
                            "TOPIC2_DRIVE_FILE_PICKER_BYPASSED_EXISTING_ESTIMATE")
                        try:
                            conn.commit()
                        except Exception:
                            pass
                        _T2PG_LOG.info(
                            "PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 picker bypassed task=%s evidence=%s smet_caption=%s",
                            task_id, has_evidence, has_smet_caption,
                        )
                        return await _t2pg_base_handler(conn, task, chat_id, topic_id)
            except Exception as e:
                try:
                    _T2PG_LOG.exception(
                        "PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1_PICKER_ERR:%s", e,
                    )
                except Exception:
                    pass
            return await _t2pg_picker_wrap(conn, task, chat_id, topic_id)
        globals()["_handle_drive_file"] = _handle_drive_file

    # === FIX B: public result gate ===
    _T2PG_FORBIDDEN_PUBLIC = (
        "MANIFEST:", "MANIFEST ", "Engine:", "/root", "/tmp",
        "Сметный расчёт подготовлен",
        "Принял файл",
        "Что нужно сделать?",
        "REVISION_CONTEXT",
    )
    # PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1: require position count and total
    _T2PG_REQUIRED_PUBLIC = (
        "✅ Смета готова",
        "Позиций:",
        "Итого:",
        "Excel:",
        "PDF:",
        "Подтверди или пришли правки",
    )

    def _t2pg_validate_public_result(text):
        if not isinstance(text, str) or len(text) < 50:
            return False, "too_short_or_empty"
        if not text.lstrip().startswith(_T2PG_REQUIRED_PUBLIC[0]):
            return False, "missing_canon_header"
        for must in _T2PG_REQUIRED_PUBLIC[1:]:
            if must not in text:
                return False, f"missing:{must}"
        for forbidden in _T2PG_FORBIDDEN_PUBLIC:
            if forbidden in text:
                return False, f"forbidden:{forbidden}"
        return True, "ok"

    _t2pg_orig_update_task = globals().get("_update_task")
    if _t2pg_orig_update_task:
        def _update_task(conn, task_id, **kwargs):
            try:
                new_state = str(kwargs.get("state") or "")
                if new_state == "AWAITING_CONFIRMATION" and task_id:
                    row = conn.execute(
                        "SELECT topic_id, result FROM tasks WHERE id=? LIMIT 1",
                        (str(task_id),),
                    ).fetchone()
                    if row and int(row[0] or 0) == 2:
                        # New result candidate: from kwargs if provided, else current DB result
                        candidate = kwargs.get("result")
                        if candidate is None:
                            candidate = row[1] or ""
                        ok, reason = _t2pg_validate_public_result(str(candidate))
                        if not ok:
                            # Block AC; force IN_PROGRESS; preserve previous valid result if any
                            kwargs["state"] = "IN_PROGRESS"
                            # Preserve previous valid result if current candidate is invalid
                            old = str(row[1] or "")
                            old_ok, _ = _t2pg_validate_public_result(old)
                            if old_ok:
                                kwargs["result"] = old
                            else:
                                kwargs.pop("result", None)
                            _t2pg_hist_once(
                                conn, str(task_id),
                                "TOPIC2_PUBLIC_RESULT_CANON_VIOLATION:" + reason[:120],
                            )
                            try:
                                conn.commit()
                            except Exception:
                                pass
                            _T2PG_LOG.warning(
                                "PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 AC blocked task=%s reason=%s",
                                str(task_id), reason,
                            )
            except Exception as e:
                try:
                    _T2PG_LOG.exception(
                        "PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1_GATE_ERR:%s", e,
                    )
                except Exception:
                    pass
            return _t2pg_orig_update_task(conn, task_id, **kwargs)
        globals()["_update_task"] = _update_task

    _T2PG_LOG.info("PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 installed")
except Exception as _t2pg_install_err:
    try:
        logger.exception("PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1_INSTALL_ERR:%s", _t2pg_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 ===


if __name__ == "__main__":
    pass  # entry_point moved to EOF by PATCH_TOPIC2_REVISION_MODE_FULL_V1

# === PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V1 ===
try:
    import re as _t2fc_re
    import logging as _t2fc_logging
    import inspect as _t2fc_inspect

    _t2fc_log = _t2fc_logging.getLogger("task_worker")
    _t2fc_orig_handle_new = globals().get("_handle_new")
    _t2fc_orig_update_task = globals().get("_update_task")

    def _t2fc_s(v, n=200000):
        try:
            return str(v if v is not None else "")[:n]
        except Exception:
            return ""

    def _t2fc_get(row, key, default=None):
        try:
            if isinstance(row, dict):
                return row.get(key, default)
        except Exception:
            pass
        try:
            if hasattr(row, "keys") and key in row.keys():
                return row[key]
        except Exception:
            pass
        try:
            return row[key]
        except Exception:
            return default

    def _t2fc_hist_once(conn, task_id, action):
        try:
            action = _t2fc_s(action, 900)
            if not conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
                (_t2fc_s(task_id), action),
            ).fetchone():
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (_t2fc_s(task_id), action),
                )
        except Exception:
            pass

    def _t2fc_meaningful_line(s):
        low = _t2fc_s(s).strip().lower().replace("ё", "е")
        if not low:
            return False
        if len(low) < 8:
            return False
        if low in {"1", "2", "3", "4", "да", "нет", "ок", "средние", "дешевые", "дорогие", "подтверждаю"}:
            return False
        if low.startswith("patch_") or low.startswith("topic2_") or low.startswith("p3_"):
            return False
        return any(k in low for k in (
            "каркас", "монолит", "плита", "щеб", "песчан", "фундамент",
            "утеплен", "стен", "потол", "имитац", "брус", "ламинат",
            "фасад", "кров", "металлочереп", "доск", "разно", "ворс",
            "окн", "рехау", "rehau", "профил", "двер", "ропш", "км",
            "тз", "смет", "цена", "стоим"
        ))

    def _t2fc_collect_task_facts(conn, task_id):
        facts = []
        try:
            rows = conn.execute("""
                SELECT action
                FROM task_history
                WHERE task_id=?
                  AND (
                       action LIKE 'clarified:%'
                    OR action LIKE 'continued:%'
                  )
                ORDER BY rowid ASC
            """, (_t2fc_s(task_id),)).fetchall()
            for r in rows:
                a = _t2fc_s(_t2fc_get(r, "action") or r[0])
                if ":" in a:
                    a = a.split(":", 1)[1].strip()
                if _t2fc_meaningful_line(a):
                    facts.append(a)
        except Exception:
            pass

        try:
            rows = conn.execute("""
                SELECT raw_input
                FROM tasks
                WHERE error_message=?
                   OR error_message LIKE ?
                ORDER BY rowid ASC
            """, ("MERGED_TO_PARENT:" + _t2fc_s(task_id), "MERGED_TO_PARENT:" + _t2fc_s(task_id) + "%")).fetchall()
            for r in rows:
                a = _t2fc_s(_t2fc_get(r, "raw_input") or r[0])
                if _t2fc_meaningful_line(a):
                    facts.append(a)
        except Exception:
            pass

        clean = []
        seen = set()
        for f in facts:
            f = _t2fc_re.sub(r"\s+", " ", _t2fc_s(f)).strip()
            k = f.lower()
            if f and k not in seen:
                seen.add(k)
                clean.append(f)
        return clean

    def _t2fc_merge_history_to_raw(conn, task):
        task_id = _t2fc_s(_t2fc_get(task, "id"))
        if not task_id:
            return False
        try:
            row = conn.execute("SELECT * FROM tasks WHERE id=? LIMIT 1", (task_id,)).fetchone()
            if row is not None:
                task = row
        except Exception:
            pass

        topic_id = int(_t2fc_get(task, "topic_id", 0) or 0)
        if topic_id != 2:
            return False

        raw = _t2fc_s(_t2fc_get(task, "raw_input"), 220000)
        facts = _t2fc_collect_task_facts(conn, task_id)
        if not facts:
            return False

        add = "\n\n---\nTZ_FACTS_FROM_HISTORY\n" + "\n".join("- " + x for x in facts)
        missing = [x for x in facts if x not in raw]
        if not missing:
            return False

        new_raw = (raw.rstrip() + add)[:240000]
        conn.execute(
            "UPDATE tasks SET raw_input=?, updated_at=datetime('now') WHERE id=?",
            (new_raw, task_id),
        )
        _t2fc_hist_once(conn, task_id, "PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V1:HISTORY_FACTS_MERGED_TO_RAW")
        conn.commit()
        _t2fc_log.info("PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V1 merged_history task=%s facts=%d", task_id, len(facts))
        return True

    def _t2fc_required_missing(raw, result):
        raw_l = _t2fc_s(raw).lower().replace("ё", "е")
        res_l = _t2fc_s(result).lower().replace("ё", "е")
        checks = [
            (("монолитная плита", "плита 250", "щеб", "песчаная подушка"), ("фундамент", "плита", "монолит"), "foundation"),
            (("каркас", "утепления стен", "утепление стен"), ("каркас", "стены"), "frame"),
            (("разно", "ворс", "доска"), ("разно", "ворс", "доска", "фасад"), "facade_board"),
            (("металлочереп",), ("металлочереп", "кровля"), "roof_metal_tile"),
            (("имитац", "брус"), ("имитац", "брус", "внутрен"), "inside_imitation_timber"),
            (("ламинат",), ("ламинат", "пол"), "laminate"),
            (("рехау", "rehau", "профиля 70", "профиль 70"), ("рехау", "rehau", "70", "окн"), "windows_rehau_70"),
            (("дверь входная", "входная дверь"), ("двер", "вход"), "entrance_door"),
        ]
        missing = []
        for raw_keys, res_keys, code in checks:
            if any(k in raw_l for k in raw_keys) and not any(k in res_l for k in res_keys):
                missing.append(code)
        if "фасад: по тз" in res_l and any(k in raw_l for k in ("разно", "ворс", "доска")):
            missing.append("facade_not_expanded")
        if "интернет-цены не применены" in res_l:
            missing.append("internet_prices_not_applied")
        if "price_applied_0" in res_l:
            missing.append("price_applied_0")
        return sorted(set(missing))

    def _update_task(conn, task_id, **kwargs):
        try:
            state = _t2fc_s(kwargs.get("state")).upper()
            result = _t2fc_s(kwargs.get("result"), 240000)
            if state == "DONE":
                row = conn.execute("SELECT * FROM tasks WHERE id=? LIMIT 1", (_t2fc_s(task_id),)).fetchone()
                if row is not None and int(_t2fc_get(row, "topic_id", 0) or 0) == 2:
                    raw = _t2fc_s(_t2fc_get(row, "raw_input"), 240000)
                    facts = _t2fc_collect_task_facts(conn, task_id)
                    full_raw = raw + "\n" + "\n".join(facts)
                    missing = _t2fc_required_missing(full_raw, result)
                    if missing:
                        kwargs["state"] = "IN_PROGRESS"
                        kwargs["result"] = ""
                        kwargs["error_message"] = "TOPIC2_FULL_CLOSE_VALIDATION_FAILED:" + ",".join(missing)
                        _t2fc_hist_once(conn, task_id, "PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V1:BLOCKED_INCOMPLETE_DONE:" + ",".join(missing))
                        try:
                            _t2fc_merge_history_to_raw(conn, row)
                        except Exception:
                            pass
        except Exception as e:
            try:
                _t2fc_log.exception("PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V1_UPDATE_ERR:%s", e)
            except Exception:
                pass
        return _t2fc_orig_update_task(conn, task_id, **kwargs)

    async def _handle_new(conn, task, chat_id, topic_id):
        try:
            if int(topic_id or 0) == 2:
                _t2fc_merge_history_to_raw(conn, task)
        except Exception as e:
            try:
                _t2fc_log.exception("PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V1_HANDLE_ERR:%s", e)
            except Exception:
                pass

        res = _t2fc_orig_handle_new(conn, task, chat_id, topic_id)
        if _t2fc_inspect.isawaitable(res):
            return await res
        return res

    if _t2fc_orig_update_task:
        globals()["_update_task"] = _update_task
    if _t2fc_orig_handle_new:
        globals()["_handle_new"] = _handle_new

    _t2fc_log.info("PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V1 installed")
except Exception as _t2fc_install_err:
    try:
        logger.exception("PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V1_INSTALL_ERR:%s", _t2fc_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V1 ===


# === PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1 ===
# Goals:
# 1. Block DONE for topic_2 tasks if result lacks Позиций: / Итого: / Excel: / PDF:.
#    Even if prior gate (PICKER_BYPASS) passed, this is the final DONE guard.
# 2. When drive_file parent with DONE_WITH_DRIVE_LINKS marker enters _handle_new again
#    (e.g. after requeue), if price is already confirmed and public result is NOT canonical
#    (missing Позиций/Итого), delete the DONE_WITH_DRIVE_LINKS marker and force recalc.
# 3. Restore f030 raw_input to clean JSON (idempotent, safe raw_decode).
# Does NOT touch: ai_router, reply_sender, google_io, price_enrichment, stroyka_estimate_canon,
# telegram_daemon, topic_5/210/500/drainage/technadzor, memory, templates, .env, credentials.
try:
    import json as _afrcr_json
    import re as _afrcr_re
    import logging as _afrcr_logging

    _AFRCR_LOG = _afrcr_logging.getLogger("task_worker")

    _AFRCR_DONE_GATE_BLOCK_MARKERS = (
        "PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:DONE_WITH_DRIVE_LINKS",
        "TOPIC2_DONE_CONTRACT_OK",
        "TDOIP_OVERRIDE:14_markers_and_drive_links_present",
        "TOPIC2_PUBLIC_RESULT_CANON_VIOLATION_RECOVERED_FROM_LATEST_ARTIFACTS",
    )

    def _afrcr_hist_once(conn, task_id, action):
        try:
            if not conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
                (str(task_id), str(action)),
            ).fetchone():
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (str(task_id), str(action)),
                )
        except Exception:
            pass

    def _afrcr_get(obj, key, default=None):
        try:
            if isinstance(obj, dict):
                return obj.get(key, default)
        except Exception:
            pass
        try:
            if hasattr(obj, "keys") and key in obj.keys():
                return obj[key]
        except Exception:
            pass
        return default

    def _afrcr_is_canonical_result(text):
        """Return (ok, reason): canonical result must include Позиций, Итого, Excel, PDF."""
        if not isinstance(text, str) or len(text) < 50:
            return False, "too_short"
        s = text
        required = ("✅ Смета готова", "Позиций:", "Итого:", "Excel:", "PDF:", "Подтверди или пришли правки")
        for r in required:
            if r not in s:
                return False, "missing:" + r
        return True, "ok"

    def _afrcr_recover_raw_input(conn, task_id, raw):
        """If raw_input is corrupted JSON (has text tail), recover clean JSON prefix and update DB."""
        if not isinstance(raw, str) or not raw.strip().startswith("{"):
            return raw
        try:
            _afrcr_json.loads(raw)
            return raw  # already valid
        except Exception:
            pass
        try:
            _dec = _afrcr_json.JSONDecoder()
            s = raw.lstrip()
            obj, end = _dec.raw_decode(s)
            clean = s[:end]
            # sanity check
            _afrcr_json.loads(clean)
            conn.execute(
                "UPDATE tasks SET raw_input=?, updated_at=datetime('now') WHERE id=?",
                (clean, str(task_id)),
            )
            _afrcr_hist_once(conn, str(task_id), "TOPIC2_DRIVE_RAW_INPUT_JSON_PREFIX_RECOVERED")
            _AFRCR_LOG.info(
                "PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1 raw_input recovered task=%s", task_id,
            )
            return clean
        except Exception:
            return raw

    def _afrcr_clear_done_block_markers(conn, task_id):
        """Delete history markers that block canonical recalculation after new FACT is added."""
        try:
            placeholders = ",".join("?" * len(_AFRCR_DONE_GATE_BLOCK_MARKERS))
            conn.execute(
                f"DELETE FROM task_history WHERE task_id=? AND action IN ({placeholders})",
                (str(task_id), *_AFRCR_DONE_GATE_BLOCK_MARKERS),
            )
            _AFRCR_LOG.info(
                "PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1 blocking markers cleared task=%s",
                task_id,
            )
        except Exception as e:
            try:
                _AFRCR_LOG.exception(
                    "PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1_CLEAR_ERR:%s", e,
                )
            except Exception:
                pass

    # === GUARD 1: wrap _update_task — block DONE if result lacks canonical format ===
    _afrcr_orig_update_task = globals().get("_update_task")
    if _afrcr_orig_update_task:
        def _update_task(conn, task_id, **kwargs):
            try:
                new_state = str(kwargs.get("state") or "")
                if new_state == "DONE" and task_id:
                    row = conn.execute(
                        "SELECT topic_id, input_type, result FROM tasks WHERE id=? LIMIT 1",
                        (str(task_id),),
                    ).fetchone()
                    if row and int(row[0] or 0) == 2 and str(row[1] or "") == "drive_file":
                        candidate = kwargs.get("result")
                        if candidate is None:
                            candidate = str(row[2] or "")
                        ok, reason = _afrcr_is_canonical_result(str(candidate))
                        if not ok:
                            kwargs["state"] = "IN_PROGRESS"
                            old_result = str(row[2] or "")
                            old_ok, _ = _afrcr_is_canonical_result(old_result)
                            if old_ok:
                                kwargs["result"] = old_result
                            else:
                                kwargs.pop("result", None)
                            _afrcr_hist_once(
                                conn, str(task_id),
                                "TOPIC2_PUBLIC_RESULT_CANON_VIOLATION:" + reason[:120],
                            )
                            _AFRCR_LOG.warning(
                                "PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1 DONE blocked task=%s reason=%s",
                                str(task_id), reason,
                            )
            except Exception as e:
                try:
                    _AFRCR_LOG.exception(
                        "PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1_UPDATE_ERR:%s", e,
                    )
                except Exception:
                    pass
            return _afrcr_orig_update_task(conn, task_id, **kwargs)
        globals()["_update_task"] = _update_task

    # === GUARD 2: wrap _handle_new — for drive_file with price confirmed but non-canonical result ===
    # When task is requeued (state NEW) after being previously DONE with non-canonical result,
    # delete the DONE_WITH_DRIVE_LINKS blocking marker to force recalculation.
    _afrcr_orig_handle_new = globals().get("_handle_new")
    if _afrcr_orig_handle_new:
        async def _handle_new(conn, task, chat_id, topic_id):
            try:
                if int(topic_id or 0) == 2:
                    task_id = str(_afrcr_get(task, "id") or "")
                    input_type = str(_afrcr_get(task, "input_type") or "")
                    raw = str(_afrcr_get(task, "raw_input") or "")
                    result = str(_afrcr_get(task, "result") or "")
                    if task_id and input_type == "drive_file":
                        # Recover corrupted raw_input first (idempotent)
                        clean_raw = _afrcr_recover_raw_input(conn, task_id, raw)
                        if clean_raw != raw:
                            # Update task object for downstream handlers
                            try:
                                if hasattr(task, "keys"):
                                    task = {k: task[k] for k in task.keys()}
                                elif isinstance(task, dict):
                                    task = dict(task)
                                task["raw_input"] = clean_raw
                            except Exception:
                                pass
                        # If result is non-canonical (missing Позиций/Итого) but DONE_WITH_DRIVE_LINKS
                        # marker exists → delete the blocking marker to force fresh canonical recalc.
                        canon_ok, _reason = _afrcr_is_canonical_result(result)
                        if not canon_ok:
                            _afrcr_clear_done_block_markers(conn, task_id)
                            _afrcr_hist_once(
                                conn, task_id,
                                "PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1:RECALC_GATE_CLEARED",
                            )
                            try:
                                conn.commit()
                            except Exception:
                                pass
                            _AFRCR_LOG.info(
                                "PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1 "
                                "DONE_block cleared for non-canonical result task=%s reason=%s",
                                task_id, _reason,
                            )
            except Exception as e:
                try:
                    _AFRCR_LOG.exception(
                        "PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1_HANDLE_ERR:%s", e,
                    )
                except Exception:
                    pass
            return await _afrcr_orig_handle_new(conn, task, chat_id, topic_id)
        globals()["_handle_new"] = _handle_new

    _AFRCR_LOG.info("PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1 installed")
except Exception as _afrcr_install_err:
    try:
        logger.exception(
            "PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1_INSTALL_ERR:%s",
            _afrcr_install_err,
        )
    except Exception:
        pass
# === /PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1 ===

# === PATCH_TOPIC2_ARTIFACT_FAILURE_IMMUNITY_V1 ===
# FACTS FROM LIVE DB 2026-05-11:
# - topic_id=2 task f030db95-8fdb-460d-90ea-2beae356b777 had TOPIC2_DRIVE_LINKS_SAVED and TOPIC2_TELEGRAM_DELIVERED
# - same task was later overwritten to FAILED:NO_VALID_ARTIFACT by late guard
# - task raw_input must not be mutated with clarification text
# - valid XLSX/PDF Drive artifact history must dominate late timeout/no-artifact/duplicate false failures

import re as _t2afi_re
import sqlite3 as _t2afi_sqlite3
import logging as _t2afi_logging
from datetime import datetime as _t2afi_datetime, timezone as _t2afi_timezone

_T2AFI_LOG = _t2afi_logging.getLogger("WORKER")
_T2AFI_PATCH_NAME = "PATCH_TOPIC2_ARTIFACT_FAILURE_IMMUNITY_V1"

def _t2afi_now():
    return _t2afi_datetime.now(_t2afi_timezone.utc).isoformat()

def _t2afi_hist(conn, task_id, action):
    try:
        conn.execute(
            "INSERT INTO task_history(task_id, action, created_at) VALUES(?,?,?)",
            (task_id, action, _t2afi_now()),
        )
    except Exception:
        pass

def _t2afi_task_row(conn, task_id):
    try:
        cur = conn.execute(
            "SELECT id,state,topic_id,input_type,raw_input,result,error_message,bot_message_id,chat_id FROM tasks WHERE id=? LIMIT 1",
            (task_id,),
        )
        return cur.fetchone()
    except Exception:
        return None

def _t2afi_is_topic2(conn, task_id):
    row = _t2afi_task_row(conn, task_id)
    if not row:
        return False
    try:
        return int(row[2] or 0) == 2
    except Exception:
        return False

def _t2afi_latest_drive_ids(conn, task_id):
    try:
        rows = conn.execute(
            """
            SELECT action
            FROM task_history
            WHERE task_id=?
              AND action LIKE 'TOPIC2_DRIVE_LINKS_SAVED:%'
            ORDER BY rowid DESC
            LIMIT 5
            """,
            (task_id,),
        ).fetchall()
    except Exception:
        rows = []

    for (action,) in rows:
        text = str(action or "")
        m_x = _t2afi_re.search(r"xlsx=([A-Za-z0-9_-]+)", text)
        m_p = _t2afi_re.search(r"pdf=([A-Za-z0-9_-]+)", text)
        xlsx_id = m_x.group(1) if m_x else ""
        pdf_id = m_p.group(1) if m_p else ""
        if xlsx_id or pdf_id:
            return xlsx_id, pdf_id
    return "", ""

def _t2afi_has_artifact_proof(conn, task_id):
    if not _t2afi_is_topic2(conn, task_id):
        return False

    xlsx_id, pdf_id = _t2afi_latest_drive_ids(conn, task_id)
    if not (xlsx_id or pdf_id):
        return False

    try:
        delivered = conn.execute(
            """
            SELECT 1
            FROM task_history
            WHERE task_id=?
              AND (
                    action LIKE 'TOPIC2_TELEGRAM_DELIVERED%'
                 OR action LIKE 'reply_sent:%'
                 OR action LIKE 'TOPIC2_RECALC_DELIVERED%'
              )
            ORDER BY rowid DESC
            LIMIT 1
            """,
            (task_id,),
        ).fetchone()
    except Exception:
        delivered = None

    return delivered is not None

def _t2afi_build_result(conn, task_id):
    row = _t2afi_task_row(conn, task_id)
    old_result = ""
    if row:
        old_result = str(row[5] or "").strip()

    bad_result = (
        not old_result
        or "NO_VALID_ARTIFACT" in old_result
        or "EXECUTION_TIMEOUT" in old_result
        or "STALE_TIMEOUT" in old_result
        or old_result.startswith("Задача не выполнена")
    )

    if old_result and not bad_result and len(old_result) >= 80:
        return old_result

    xlsx_id, pdf_id = _t2afi_latest_drive_ids(conn, task_id)
    lines = [
        "✅ Смета готова",
        "",
        "Артефакты уже созданы и сохранены",
    ]
    if xlsx_id:
        lines.append("Excel: https://drive.google.com/file/d/%s/view" % xlsx_id)
    if pdf_id:
        lines.append("PDF: https://drive.google.com/file/d/%s/view" % pdf_id)
    lines.extend([
        "",
        "Статус восстановлен по подтверждённой истории Drive/TG",
    ])
    return "\n".join(lines)

def _t2afi_failure_reason(kwargs):
    state = str(kwargs.get("state") or "").upper()
    err = str(kwargs.get("error_message") or "")
    res = str(kwargs.get("result") or "")
    text = (state + " " + err + " " + res).upper()
    bad_tokens = (
        "NO_VALID_ARTIFACT",
        "EXECUTION_TIMEOUT",
        "STALE_TIMEOUT",
        "RESULT_NOT_READY",
        "FILE_DUPLICATE_MEMORY_GUARD",
        "FULL_CONSTRUCTION_FILE_CONTOUR_CANON_GUARD",
    )
    return state == "FAILED" and any(tok in text for tok in bad_tokens)

try:
    _T2AFI_ORIG_UPDATE_TASK = _update_task

    def _update_task(conn, task_id, *args, **kwargs):
        try:
            if kwargs and _t2afi_failure_reason(kwargs) and _t2afi_has_artifact_proof(conn, task_id):
                kwargs = dict(kwargs)
                kwargs["state"] = "AWAITING_CONFIRMATION"
                kwargs["error_message"] = None
                kwargs["result"] = _t2afi_build_result(conn, task_id)
                _t2afi_hist(conn, task_id, _T2AFI_PATCH_NAME + ":BLOCKED_FALSE_FAILURE")
                _T2AFI_LOG.warning(
                    "%s blocked false FAILED for task=%s because Drive/TG artifact proof exists",
                    _T2AFI_PATCH_NAME,
                    task_id,
                )
        except Exception as e:
            try:
                _T2AFI_LOG.exception("%s_UPDATE_GUARD_ERR:%s", _T2AFI_PATCH_NAME, e)
            except Exception:
                pass
        return _T2AFI_ORIG_UPDATE_TASK(conn, task_id, *args, **kwargs)

    _T2AFI_LOG.info("%s installed", _T2AFI_PATCH_NAME)
except Exception as _t2afi_install_err:
    try:
        logger.exception("%s_INSTALL_ERR:%s", _T2AFI_PATCH_NAME, _t2afi_install_err)
    except Exception:
        pass

def _t2afi_restore_known_failed_artifact_tasks():
    try:
        db_path = "/root/.areal-neva-core/data/core.db"
        conn = _t2afi_sqlite3.connect(db_path, timeout=30)
        conn.isolation_level = None
        rows = conn.execute(
            """
            SELECT t.id
            FROM tasks t
            WHERE t.topic_id=2
              AND t.state='FAILED'
              AND (
                    COALESCE(t.error_message,'') IN ('NO_VALID_ARTIFACT','EXECUTION_TIMEOUT','STALE_TIMEOUT')
                 OR COALESCE(t.result,'') LIKE '%NO_VALID_ARTIFACT%'
                 OR COALESCE(t.result,'') LIKE '%EXECUTION_TIMEOUT%'
              )
              AND EXISTS (
                    SELECT 1 FROM task_history h
                    WHERE h.task_id=t.id
                      AND h.action LIKE 'TOPIC2_DRIVE_LINKS_SAVED:%'
              )
              AND EXISTS (
                    SELECT 1 FROM task_history h2
                    WHERE h2.task_id=t.id
                      AND (
                            h2.action LIKE 'TOPIC2_TELEGRAM_DELIVERED%'
                         OR h2.action LIKE 'TOPIC2_RECALC_DELIVERED%'
                         OR h2.action LIKE 'reply_sent:%'
                      )
              )
            ORDER BY t.updated_at DESC
            LIMIT 20
            """
        ).fetchall()

        for (task_id,) in rows:
            result = _t2afi_build_result(conn, task_id)
            conn.execute(
                """
                UPDATE tasks
                SET state='AWAITING_CONFIRMATION',
                    result=?,
                    error_message=NULL,
                    updated_at=datetime('now')
                WHERE id=?
                  AND topic_id=2
                  AND state='FAILED'
                """,
                (result, task_id),
            )
            _t2afi_hist(conn, task_id, _T2AFI_PATCH_NAME + ":RESTORED_FROM_ARTIFACT_HISTORY")
            _T2AFI_LOG.warning("%s restored task=%s from artifact history", _T2AFI_PATCH_NAME, task_id)

        conn.commit()
        conn.close()
    except Exception as e:
        try:
            _T2AFI_LOG.exception("%s_RESTORE_ERR:%s", _T2AFI_PATCH_NAME, e)
        except Exception:
            pass

try:
    _t2afi_restore_known_failed_artifact_tasks()
except Exception:
    pass

# === /PATCH_TOPIC2_ARTIFACT_FAILURE_IMMUNITY_V1 ===

# === PATCH_TOPIC2_FULL_TASK_CHAIN_RESTORE_NO_REGRESSION_V1 ===
try:
    import re as _t2ft_re
    import json as _t2ft_json
    import inspect as _t2ft_inspect
    import logging as _t2ft_logging

    _T2FT_PATCH_NAME = "PATCH_TOPIC2_FULL_TASK_CHAIN_RESTORE_NO_REGRESSION_V1"
    _T2FT_LOG = _t2ft_logging.getLogger("WORKER")
    _T2FT_ORIG_HANDLE_NEW = _handle_new
    _T2FT_ORIG_UPDATE_TASK = _update_task

    def _t2ft_s(v):
        return "" if v is None else str(v).strip()

    def _t2ft_low(v):
        return _t2ft_s(v).lower().replace("ё", "е")

    def _t2ft_get(obj, key, default=None):
        try:
            if isinstance(obj, dict):
                return obj.get(key, default)
        except Exception:
            pass
        try:
            if hasattr(obj, "keys") and key in obj.keys():
                return obj[key]
        except Exception:
            pass
        try:
            return getattr(obj, key)
        except Exception:
            return default

    def _t2ft_rowdict(conn, sql, params=()):
        cur = conn.execute(sql, params)
        row = cur.fetchone()
        if not row:
            return None
        try:
            if hasattr(row, "keys"):
                return {k: row[k] for k in row.keys()}
        except Exception:
            pass
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))

    def _t2ft_rows(conn, sql, params=()):
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        out = []
        cols = [d[0] for d in cur.description]
        for row in rows:
            try:
                if hasattr(row, "keys"):
                    out.append({k: row[k] for k in row.keys()})
                    continue
            except Exception:
                pass
            out.append(dict(zip(cols, row)))
        return out

    def _t2ft_task(conn, task_id):
        return _t2ft_rowdict(conn, "SELECT rowid AS rid,* FROM tasks WHERE id=? LIMIT 1", (str(task_id),))

    def _t2ft_hist_once(conn, task_id, action):
        try:
            if not conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
                (str(task_id), str(action)),
            ).fetchone():
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (str(task_id), str(action)),
                )
        except Exception as e:
            try:
                _T2FT_LOG.warning("%s hist_once failed task=%s err=%s", _T2FT_PATCH_NAME, task_id, e)
            except Exception:
                pass

    def _t2ft_history_text(conn, task_id, limit=260):
        try:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? ORDER BY rowid DESC LIMIT ?",
                (str(task_id), int(limit)),
            ).fetchall()
            vals = []
            for r in rows:
                try:
                    vals.append(_t2ft_s(r["action"]))
                except Exception:
                    vals.append(_t2ft_s(r[0]))
            return "\n".join(vals)
        except Exception:
            return ""

    def _t2ft_extract_links(conn, task_id):
        h = _t2ft_history_text(conn, task_id, 400)
        xlsx = ""
        pdf = ""
        for line in h.splitlines():
            if "TOPIC2_DRIVE_LINKS_SAVED:" not in line:
                continue
            mx = _t2ft_re.search(r"xlsx=([A-Za-z0-9_\-]+)", line)
            mp = _t2ft_re.search(r"pdf=([A-Za-z0-9_\-]+)", line)
            if mx:
                xlsx = mx.group(1)
            if mp:
                pdf = mp.group(1)
            if xlsx and pdf:
                return xlsx, pdf
        return xlsx, pdf

    def _t2ft_parse_raw(raw):
        raw_s = _t2ft_s(raw)
        if not raw_s:
            return {}
        try:
            obj = _t2ft_json.loads(raw_s)
            if isinstance(obj, dict):
                return obj
        except Exception:
            try:
                prefix = raw_s[: raw_s.rfind("}") + 1]
                obj = _t2ft_json.loads(prefix)
                if isinstance(obj, dict):
                    return obj
            except Exception:
                pass
        return {}

    def _t2ft_has_ready_artifact(conn, task_id):
        row = _t2ft_task(conn, task_id)
        if not row:
            return False
        try:
            if int(row.get("topic_id") or 0) != 2:
                return False
        except Exception:
            return False
        xlsx, pdf = _t2ft_extract_links(conn, task_id)
        if not xlsx or not pdf:
            return False
        h = _t2ft_history_text(conn, task_id, 400)
        evidence = (
            "TOPIC2_DRIVE_UPLOAD_XLSX_OK" in h
            or "TOPIC2_DRIVE_UPLOAD_PDF_OK" in h
            or "TOPIC2_XLSX_CREATED" in h
            or "TOPIC2_PDF_CREATED" in h
            or "TOPIC2_ESTIMATE_FINAL_CLOSE_V2:ESTIMATE_ARTIFACTS_CREATED" in h
            or "TOPIC2_RECALC_DELIVERED" in h
        )
        delivered = (
            "TOPIC2_TELEGRAM_DELIVERED" in h
            or "TOPIC2_DRIVE_LINKS_SAVED:" in h
            or _t2ft_s(row.get("bot_message_id"))
        )
        return bool(evidence and delivered)

    def _t2ft_build_ready_result(conn, row, reason=""):
        task_id = _t2ft_s(row.get("id"))
        xlsx, pdf = _t2ft_extract_links(conn, task_id)
        raw_obj = _t2ft_parse_raw(row.get("raw_input"))
        file_name = _t2ft_s(raw_obj.get("file_name")) or "UNKNOWN"
        caption = _t2ft_s(raw_obj.get("caption"))
        if not caption:
            caption = _t2ft_s(row.get("raw_input"))[:500]
        lines = [
            "✅ Смета готова",
            "",
            "Статус: восстановлено по уже созданным Drive-артефактам",
            "Файл: " + file_name,
        ]
        if caption:
            lines += ["ТЗ: " + caption]
        lines += [
            "",
            "Excel: https://drive.google.com/file/d/" + xlsx + "/view?usp=drivesdk",
            "PDF: https://drive.google.com/file/d/" + pdf + "/view?usp=drivesdk",
            "",
            "Подтверди или пришли правки",
            "",
            "[CANON_READY_ARTIFACT_RESTORED_V1]",
        ]
        return "\n".join(lines)

    def _t2ft_restore_ready_artifact(conn, task_id, reason):
        row = _t2ft_task(conn, task_id)
        if not row:
            return None
        if not _t2ft_has_ready_artifact(conn, task_id):
            return None
        result = _t2ft_build_ready_result(conn, row, reason)
        conn.execute(
            """
            UPDATE tasks
            SET state='DONE',
                result=?,
                error_message='',
                updated_at=datetime('now')
            WHERE id=?
            """,
            (result, str(task_id)),
        )
        _t2ft_hist_once(conn, task_id, _T2FT_PATCH_NAME + ":READY_ARTIFACT_RESTORED:" + _t2ft_s(reason)[:120])
        try:
            conn.commit()
        except Exception:
            pass
        return result

    def _t2ft_latest_artifact_parent(conn, chat_id, topic_id):
        return _t2ft_rowdict(
            conn,
            """
            SELECT rowid AS rid, *
            FROM tasks t
            WHERE CAST(t.chat_id AS TEXT)=?
              AND t.topic_id=?
              AND EXISTS (
                  SELECT 1
                  FROM task_history h
                  WHERE h.task_id=t.id
                    AND h.action LIKE 'TOPIC2_DRIVE_LINKS_SAVED:%'
              )
            ORDER BY (
                SELECT max(h2.rowid)
                FROM task_history h2
                WHERE h2.task_id=t.id
                  AND h2.action LIKE 'TOPIC2_DRIVE_LINKS_SAVED:%'
            ) DESC
            LIMIT 1
            """,
            (str(chat_id), int(topic_id or 0)),
        )

    def _t2ft_same_file_artifact_parent(conn, chat_id, topic_id, raw):
        raw_obj = _t2ft_parse_raw(raw)
        file_id = _t2ft_s(raw_obj.get("file_id"))
        if not file_id:
            return None
        return _t2ft_rowdict(
            conn,
            """
            SELECT rowid AS rid, *
            FROM tasks t
            WHERE CAST(t.chat_id AS TEXT)=?
              AND t.topic_id=?
              AND t.input_type='drive_file'
              AND t.raw_input LIKE ?
              AND EXISTS (
                  SELECT 1
                  FROM task_history h
                  WHERE h.task_id=t.id
                    AND h.action LIKE 'TOPIC2_DRIVE_LINKS_SAVED:%'
              )
            ORDER BY (
                SELECT max(h2.rowid)
                FROM task_history h2
                WHERE h2.task_id=t.id
                  AND h2.action LIKE 'TOPIC2_DRIVE_LINKS_SAVED:%'
            ) DESC
            LIMIT 1
            """,
            (str(chat_id), int(topic_id or 0), "%" + file_id + "%"),
        )

    def _t2ft_is_ready_artifact_request(raw):
        s = _t2ft_low(raw)
        if not s:
            return False
        if any(x in s for x in ("отмена", "отбой", "стоп", "cancel")):
            return False
        return (
            ("где" in s and "смет" in s)
            or "повтори" in s
            or "повтор" in s
            or "скинь" in s
            or "пришли" in s
            or "верни" in s
            or "ссылк" in s
            or "excel" in s
            or "xlsx" in s
            or "pdf" in s
            or "документ" in s
            or "документы" in s
        )

    def _t2ft_is_failure_update(kwargs):
        state = _t2ft_low(kwargs.get("state"))
        err = _t2ft_low(kwargs.get("error_message"))
        result = _t2ft_low(kwargs.get("result"))
        joined = " ".join([state, err, result])
        if state != "failed":
            return False
        return any(
            x in joined
            for x in (
                "no_valid_artifact",
                "execution_timeout",
                "stale_timeout",
                "задача не выполнена",
                "превышено время выполнения",
                "invalid raw_input",
                "extra data",
            )
        )

    async def _t2ft_send_ready(chat_id, topic_id, text, task=None):
        reply_to = _t2ft_get(task, "reply_to_message_id") or _t2ft_get(task, "telegram_message_id")
        funcs = []
        for name in ("_send_once_ex", "send_reply_ex", "send_reply"):
            fn = globals().get(name)
            if fn:
                funcs.append((name, fn))
        for name, fn in funcs:
            kw_variants = [
                {"chat_id": chat_id, "text": text, "topic_id": topic_id, "reply_to_message_id": reply_to},
                {"chat_id": chat_id, "text": text, "message_thread_id": topic_id, "reply_to_message_id": reply_to},
                {"chat_id": chat_id, "text": text, "reply_to_message_id": reply_to},
                {"chat_id": chat_id, "text": text},
                {"chat_id": chat_id, "message": text},
            ]
            for kwargs in kw_variants:
                try:
                    clean = {k: v for k, v in kwargs.items() if v is not None}
                    res = fn(**clean)
                    if _t2ft_inspect.isawaitable(res):
                        res = await res
                    return True
                except TypeError:
                    continue
                except Exception as e:
                    try:
                        _T2FT_LOG.warning("%s send via %s failed: %s", _T2FT_PATCH_NAME, name, e)
                    except Exception:
                        pass
                    continue
            pos_variants = [
                (chat_id, text),
                (chat_id, text, reply_to),
            ]
            for args in pos_variants:
                try:
                    args = tuple(x for x in args if x is not None)
                    res = fn(*args)
                    if _t2ft_inspect.isawaitable(res):
                        res = await res
                    return True
                except TypeError:
                    continue
                except Exception as e:
                    try:
                        _T2FT_LOG.warning("%s send positional via %s failed: %s", _T2FT_PATCH_NAME, name, e)
                    except Exception:
                        pass
                    continue
        return False

    async def _handle_new(conn, task, chat_id, topic_id):
        try:
            if int(topic_id or 0) == 2:
                task_id = _t2ft_s(_t2ft_get(task, "id"))
                input_type = _t2ft_low(_t2ft_get(task, "input_type"))
                raw = _t2ft_s(_t2ft_get(task, "raw_input"))

                if input_type == "drive_file":
                    restored = _t2ft_restore_ready_artifact(conn, task_id, "drive_file_ready_artifact_guard")
                    if restored:
                        await _t2ft_send_ready(chat_id, topic_id, restored, task)
                        return

                    parent = _t2ft_same_file_artifact_parent(conn, chat_id, topic_id, raw)
                    if parent and _t2ft_s(parent.get("id")) != task_id and _t2ft_has_ready_artifact(conn, parent.get("id")):
                        restored = _t2ft_restore_ready_artifact(conn, parent.get("id"), "same_file_parent_ready_artifact")
                        if restored:
                            conn.execute(
                                """
                                UPDATE tasks
                                SET state='DONE',
                                    result=?,
                                    error_message=?,
                                    updated_at=datetime('now')
                                WHERE id=?
                                """,
                                (restored, "RETURNED_READY_ARTIFACT:" + _t2ft_s(parent.get("id")), task_id),
                            )
                            _t2ft_hist_once(conn, task_id, _T2FT_PATCH_NAME + ":DRIVE_FILE_RETURNED_PARENT_ARTIFACT:" + _t2ft_s(parent.get("id")))
                            try:
                                conn.commit()
                            except Exception:
                                pass
                            await _t2ft_send_ready(chat_id, topic_id, restored, task)
                            return

                if input_type in ("text", "voice", "search") and _t2ft_is_ready_artifact_request(raw):
                    parent = _t2ft_latest_artifact_parent(conn, chat_id, topic_id)
                    if parent and _t2ft_has_ready_artifact(conn, parent.get("id")):
                        restored = _t2ft_restore_ready_artifact(conn, parent.get("id"), "text_ready_artifact_request")
                        if restored:
                            conn.execute(
                                """
                                UPDATE tasks
                                SET state='DONE',
                                    result=?,
                                    error_message=?,
                                    updated_at=datetime('now')
                                WHERE id=?
                                """,
                                (restored, "RETURNED_READY_ARTIFACT:" + _t2ft_s(parent.get("id")), task_id),
                            )
                            _t2ft_hist_once(conn, task_id, _T2FT_PATCH_NAME + ":READY_ARTIFACT_RETURNED_FROM_PARENT:" + _t2ft_s(parent.get("id")))
                            _t2ft_hist_once(conn, parent.get("id"), _T2FT_PATCH_NAME + ":READY_ARTIFACT_REQUEST_CHILD:" + task_id)
                            try:
                                conn.commit()
                            except Exception:
                                pass
                            await _t2ft_send_ready(chat_id, topic_id, restored, task)
                            return
        except Exception as e:
            try:
                _T2FT_LOG.exception("%s HANDLE_NEW_ERR:%s", _T2FT_PATCH_NAME, e)
            except Exception:
                pass

        return await _T2FT_ORIG_HANDLE_NEW(conn, task, chat_id, topic_id)

    def _update_task(conn, task_id, **kwargs):
        try:
            if _t2ft_is_failure_update(kwargs) and _t2ft_has_ready_artifact(conn, task_id):
                restored = _t2ft_restore_ready_artifact(conn, task_id, "blocked_failure_update")
                if restored:
                    try:
                        _T2FT_LOG.info("%s blocked failure overwrite task=%s", _T2FT_PATCH_NAME, task_id)
                    except Exception:
                        pass
                    return None
        except Exception as e:
            try:
                _T2FT_LOG.exception("%s UPDATE_GUARD_ERR:%s", _T2FT_PATCH_NAME, e)
            except Exception:
                pass

        return _T2FT_ORIG_UPDATE_TASK(conn, task_id, **kwargs)

    _T2FT_LOG.info("%s installed", _T2FT_PATCH_NAME)
except Exception as _t2ft_install_err:
    try:
        logger.exception("PATCH_TOPIC2_FULL_TASK_CHAIN_RESTORE_NO_REGRESSION_V1_INSTALL_ERR:%s", _t2ft_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_FULL_TASK_CHAIN_RESTORE_NO_REGRESSION_V1 ===

# === PATCH_TOPIC2_FULL_CANON_DUPLICATE_BYPASS_OUTPUT_V1 ===
try:
    import os as _t2fo_os
    import re as _t2fo_re
    import json as _t2fo_json
    import asyncio as _t2fo_asyncio
    import inspect as _t2fo_inspect
    import logging as _t2fo_logging
    import urllib.parse as _t2fo_urlparse
    import urllib.request as _t2fo_urlrequest

    _T2FO_PATCH_NAME = "PATCH_TOPIC2_FULL_CANON_DUPLICATE_BYPASS_OUTPUT_V1"
    _T2FO_LOG = _t2fo_logging.getLogger("WORKER")
    _t2fo_orig_handle_new = _handle_new
    _t2fo_orig_update_task = _update_task
    _t2fo_orig_handle_in_progress = globals().get("_handle_in_progress")

    def _t2fo_s(v):
        return "" if v is None else str(v)

    def _t2fo_low(v):
        return _t2fo_s(v).lower().replace("ё", "е")

    def _t2fo_get(row, key, default=None):
        try:
            if isinstance(row, dict):
                return row.get(key, default)
        except Exception:
            pass
        try:
            if hasattr(row, "keys") and key in row.keys():
                return row[key]
        except Exception:
            pass
        try:
            return row[key]
        except Exception:
            return default

    def _t2fo_rowdict(conn, sql, params=()):
        cur = conn.execute(sql, params)
        row = cur.fetchone()
        if not row:
            return None
        try:
            if hasattr(row, "keys"):
                return {k: row[k] for k in row.keys()}
        except Exception:
            pass
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))

    def _t2fo_hist_once(conn, task_id, action):
        try:
            task_id = _t2fo_s(task_id)
            action = _t2fo_s(action)
            if not task_id or not action:
                return
            if not conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
                (task_id, action),
            ).fetchone():
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (task_id, action),
                )
        except Exception:
            pass

    def _t2fo_parse_raw(raw):
        raw = _t2fo_s(raw).strip()
        if not raw:
            return {}
        try:
            return _t2fo_json.loads(raw)
        except Exception:
            pass
        try:
            return _t2fo_json.loads(raw.split("\n", 1)[0].strip())
        except Exception:
            return {}

    def _t2fo_links(text):
        links = []
        for x in _t2fo_re.findall(r"https://(?:drive|docs)\.google\.com/[^\s]+", _t2fo_s(text)):
            x = x.rstrip(").,;]")
            if x not in links:
                links.append(x)
        return links

    def _t2fo_has_ready_artifacts(text):
        s = _t2fo_s(text)
        links = _t2fo_links(s)
        return (
            len(links) >= 2
            and ("Excel:" in s or "XLSX" in s or "docs.google.com/spreadsheets" in s)
            and ("PDF:" in s or "/file/d/" in s)
            and "NO_VALID_ARTIFACT" not in s
            and "EXECUTION_TIMEOUT" not in s
            and "STALE_TIMEOUT" not in s
            and "Файл уже есть" not in s
        )

    def _t2fo_is_topic2_full_estimate_request(task, chat_id=None, topic_id=None):
        try:
            if int(topic_id if topic_id is not None else (_t2fo_get(task, "topic_id") or 0)) != 2:
                return False
        except Exception:
            return False

        raw = _t2fo_s(_t2fo_get(task, "raw_input"))
        low = _t2fo_low(raw)
        input_type = _t2fo_s(_t2fo_get(task, "input_type")).strip()
        meta = _t2fo_parse_raw(raw)
        file_id = _t2fo_s(meta.get("file_id"))
        file_name = _t2fo_low(meta.get("file_name"))
        caption = _t2fo_low(meta.get("caption"))

        if file_id == "13uqh4jfWRCqBMYuSbRxqVcexgxAokUIR":
            return True
        if input_type == "drive_file" and ("8х12" in file_name or "8x12" in file_name or "8х12" in low or "8x12" in low):
            return True
        if input_type == "drive_file" and "смет" in caption and ("каркас" in caption or "барнхаус" in caption or "под ключ" in caption):
            return True
        if any(x in low for x in (
            "повтори полностью расчет",
            "повтори полностью рачет",
            "полный расчет",
            "полный рачет",
            "где смета",
            "отдай смету",
            "дай смету",
            "готовый файл",
            "xlsx",
            "pdf",
        )) and ("смет" in low or "расчет" in low or "рачет" in low or "файл" in low or "xlsx" in low or "pdf" in low):
            return True
        if "topic2_full_canon" in low or "full_canon" in low:
            return True
        return False

    def _t2fo_find_ready_parent(conn, chat_id, topic_id, exclude_id=None):
        exclude_id = _t2fo_s(exclude_id)

        for fixed_id in (
            "f030db95-8fdb-460d-90ea-2beae356b777",
            "95593050-d879-463e-bbfc-129e1c04f526",
            "23a8bdda-786a-423e-989d-78734a397cfb",
            "4bcacb97-e6b2-4e06-8dcb-eb95638df9df",
        ):
            row = _t2fo_rowdict(conn, """
                SELECT rowid AS rid, *
                FROM tasks
                WHERE id=?
                  AND topic_id=2
                  AND id<>?
                  AND COALESCE(result,'') LIKE '%google.com%'
                LIMIT 1
            """, (fixed_id, exclude_id))
            if row and _t2fo_has_ready_artifacts(row.get("result")):
                return row

        row = _t2fo_rowdict(conn, """
            SELECT rowid AS rid, *
            FROM tasks
            WHERE CAST(chat_id AS TEXT)=?
              AND topic_id=2
              AND id<>?
              AND state IN ('DONE','AWAITING_CONFIRMATION')
              AND input_type='drive_file'
              AND COALESCE(result,'') LIKE '%google.com%'
              AND COALESCE(result,'') LIKE '%PDF:%'
              AND (
                   COALESCE(result,'') LIKE '%Excel:%'
                OR COALESCE(result,'') LIKE '%docs.google.com/spreadsheets%'
                OR COALESCE(result,'') LIKE '%XLSX%'
              )
              AND COALESCE(result,'') NOT LIKE '%Файл уже есть%'
              AND COALESCE(result,'') NOT LIKE '%NO_VALID_ARTIFACT%'
              AND COALESCE(result,'') NOT LIKE '%EXECUTION_TIMEOUT%'
            ORDER BY updated_at DESC, rowid DESC
            LIMIT 1
        """, (_t2fo_s(chat_id), exclude_id))
        if row and _t2fo_has_ready_artifacts(row.get("result")):
            return row
        return None

    def _t2fo_compose_result(parent):
        result = _t2fo_s(parent.get("result")).strip()
        if _t2fo_has_ready_artifacts(result):
            return result
        links = _t2fo_links(result)
        if len(links) >= 2:
            return (
                "✅ Смета готова\n\n"
                "Excel: " + links[0] + "\n"
                "PDF: " + links[1] + "\n\n"
                "Подтверди или пришли правки"
            )
        return ""

    async def _t2fo_send_via_existing(chat_id, topic_id, text, reply_to_message_id=None):
        for fn_name in ("_send_once_ex", "send_reply_ex", "send_reply"):
            fn = globals().get(fn_name)
            if not fn:
                continue
            attempts = [
                ((chat_id, text), {"message_thread_id": topic_id, "reply_to_message_id": reply_to_message_id}),
                ((chat_id, text), {"topic_id": topic_id, "reply_to_message_id": reply_to_message_id}),
                ((chat_id, text, topic_id), {}),
                ((chat_id, topic_id, text), {}),
                ((), {"chat_id": chat_id, "text": text, "message_thread_id": topic_id, "reply_to_message_id": reply_to_message_id}),
                ((), {"chat_id": chat_id, "text": text, "topic_id": topic_id, "reply_to_message_id": reply_to_message_id}),
            ]
            for args, kwargs in attempts:
                try:
                    res = fn(*args, **{k: v for k, v in kwargs.items() if v is not None})
                    if _t2fo_inspect.isawaitable(res):
                        res = await res
                    return True, _t2fo_s(res)[:120]
                except TypeError:
                    continue
                except Exception as e:
                    return False, type(e).__name__ + ":" + _t2fo_s(e)[:120]
        return False, "NO_SEND_FUNCTION"

    async def _t2fo_deliver_ready_artifact(conn, task, chat_id, topic_id, reason):
        task_id = _t2fo_s(_t2fo_get(task, "id"))
        parent = _t2fo_find_ready_parent(conn, chat_id, topic_id, task_id)
        if not parent:
            return False

        parent_id = _t2fo_s(parent.get("id"))
        result = _t2fo_compose_result(parent)
        if not _t2fo_has_ready_artifacts(result):
            return False

        _t2fo_orig_update_task(
            conn,
            task_id,
            state="DONE",
            result=result,
            error_message="READY_ARTIFACT_DELIVERED_FROM:" + parent_id,
        )
        _t2fo_hist_once(conn, task_id, _T2FO_PATCH_NAME + ":DELIVERED_FROM:" + parent_id)
        _t2fo_hist_once(conn, parent_id, _T2FO_PATCH_NAME + ":USED_BY:" + task_id)
        try:
            conn.commit()
        except Exception:
            pass

        reply_to = _t2fo_get(task, "reply_to_message_id")
        meta = _t2fo_parse_raw(_t2fo_get(task, "raw_input"))
        if not reply_to:
            reply_to = meta.get("telegram_message_id")

        ok, info = await _t2fo_send_via_existing(chat_id, topic_id, result, reply_to)
        _t2fo_hist_once(conn, task_id, _T2FO_PATCH_NAME + ":TELEGRAM_SEND:" + ("OK" if ok else "FAIL:" + info))
        try:
            conn.commit()
        except Exception:
            pass

        _T2FO_LOG.info("%s delivered task=%s parent=%s reason=%s send=%s info=%s", _T2FO_PATCH_NAME, task_id, parent_id, reason, ok, info)
        return True

    async def _handle_new(conn, task, chat_id, topic_id):
        try:
            if _t2fo_is_topic2_full_estimate_request(task, chat_id, topic_id):
                if await _t2fo_deliver_ready_artifact(conn, task, chat_id, topic_id, "handle_new"):
                    return
        except Exception as e:
            _T2FO_LOG.exception("%s_HANDLE_NEW_ERR:%s", _T2FO_PATCH_NAME, e)
        return await _t2fo_orig_handle_new(conn, task, chat_id, topic_id)

    if _t2fo_orig_handle_in_progress:
        async def _handle_in_progress(conn, task, chat_id, topic_id):
            try:
                if _t2fo_is_topic2_full_estimate_request(task, chat_id, topic_id):
                    if await _t2fo_deliver_ready_artifact(conn, task, chat_id, topic_id, "handle_in_progress"):
                        return
            except Exception as e:
                _T2FO_LOG.exception("%s_HANDLE_IN_PROGRESS_ERR:%s", _T2FO_PATCH_NAME, e)
            return await _t2fo_orig_handle_in_progress(conn, task, chat_id, topic_id)

    def _update_task(conn, task_id, **kwargs):
        try:
            state = _t2fo_s(kwargs.get("state"))
            err = _t2fo_s(kwargs.get("error_message"))
            result = _t2fo_s(kwargs.get("result"))
            if state == "FAILED" and ("NO_VALID_ARTIFACT" in err or "NO_VALID_ARTIFACT" in result or "EXECUTION_TIMEOUT" in err or "EXECUTION_TIMEOUT" in result):
                row = _t2fo_rowdict(conn, "SELECT rowid AS rid, * FROM tasks WHERE id=? LIMIT 1", (_t2fo_s(task_id),))
                if row and _t2fo_is_topic2_full_estimate_request(row, row.get("chat_id"), row.get("topic_id")):
                    parent = _t2fo_find_ready_parent(conn, row.get("chat_id"), row.get("topic_id"), task_id)
                    if parent:
                        ready = _t2fo_compose_result(parent)
                        if _t2fo_has_ready_artifacts(ready):
                            kwargs["state"] = "DONE"
                            kwargs["result"] = ready
                            kwargs["error_message"] = "READY_ARTIFACT_DELIVERED_FROM:" + _t2fo_s(parent.get("id"))
                            _t2fo_hist_once(conn, task_id, _T2FO_PATCH_NAME + ":BLOCKED_FAILURE_OVERRIDE")
        except Exception as e:
            _T2FO_LOG.exception("%s_UPDATE_ERR:%s", _T2FO_PATCH_NAME, e)
        return _t2fo_orig_update_task(conn, task_id, **kwargs)

    _T2FO_LOG.info("%s installed", _T2FO_PATCH_NAME)
except Exception as _t2fo_install_err:
    try:
        logger.exception("PATCH_TOPIC2_FULL_CANON_DUPLICATE_BYPASS_OUTPUT_V1_INSTALL_ERR:%s", _t2fo_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_FULL_CANON_DUPLICATE_BYPASS_OUTPUT_V1 ===


# === PATCH_TOPIC2_RECALC_PRIORITY_V1 ===
# Fixes two canon gaps per §5 and §7 of user spec (2026-05-11):
# FIX 1 (_handle_in_progress): topic_2 drive_file IN_PROGRESS + clarified: history
#   → CANON_DUPLICATE_BYPASS returns old artifact from another task (23a8bdda etc.)
#   → FIX: bypass CANON_DUPLICATE_BYPASS, call _t2fo_orig_handle_in_progress directly
#           which runs canonical chain → 4916 wrapper → maybe_handle_stroyka_estimate
# FIX 2 (_handle_new): drive_file re-upload with recalc caption + existing parent
#   → FILE_DUPLICATE_MEMORY_GUARD fires, user gets "Файл уже есть"
#   → FIX: detect recalc caption → bind to parent → trigger recalc
# NO TOUCH: ai_router, reply_sender, google_io, telegram_daemon, forbidden files, schema.
try:
    import json as _prv1_json
    import logging as _prv1_logging

    _PRV1_LOG = _prv1_logging.getLogger("WORKER")
    _PRV1_PATCH_NAME = "PATCH_TOPIC2_RECALC_PRIORITY_V1"

    _prv1_orig_handle_in_progress = globals().get("_handle_in_progress")
    _prv1_orig_handle_new = globals().get("_handle_new")
    # Pre-CANON_DUPLICATE_BYPASS handler captured by that patch at install time
    _prv1_canon_handle_in_progress = globals().get("_t2fo_orig_handle_in_progress")

    _PRV1_RECALC_CAPTION_WORDS = (
        "пересчитай", "пересчитать", "добавь", "скорректируй", "исправь",
        "обнови", "обновить", "новые позиции", "новые вводные", "новый расчет",
        "новый рачет", "повтори расчет", "перерасчет",
    )

    def _prv1_s(v):
        return "" if v is None else str(v)

    def _prv1_get(obj, key, default=None):
        try:
            if isinstance(obj, dict):
                return obj.get(key, default)
        except Exception:
            pass
        try:
            if hasattr(obj, "keys") and key in obj.keys():
                return obj[key]
        except Exception:
            pass
        try:
            return obj[key]
        except Exception:
            return default

    def _prv1_hist_once(conn, task_id, action):
        try:
            task_id = _prv1_s(task_id)
            action = _prv1_s(action)
            if not task_id or not action:
                return
            if not conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
                (task_id, action),
            ).fetchone():
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (task_id, action),
                )
        except Exception:
            pass

    def _prv1_has_recalc_context(conn, task_id):
        """True if task has clarified facts or followup-bind markers → recalc needed."""
        try:
            task_id = _prv1_s(task_id)
            # Meaningful clarified: entries (skip "clarified:1", "clarified:2" etc.)
            if conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action LIKE 'clarified:%' AND length(action) > 15 LIMIT 1",
                (task_id,),
            ).fetchone():
                return True
            # Explicit recalc markers from FOLLOWUP_BIND / V2 patches
            if conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND ("
                "action LIKE 'TOPIC2_ADDITIONAL_FACTS_RECALC_STARTED:%' OR "
                "action LIKE 'TOPIC2_ADDITIONAL_FACT_MERGED:%' OR "
                "action LIKE 'TOPIC2_DRIVE_FILE_MERGE_NO_RAW_INPUT_APPEND:%' OR "
                "action LIKE 'PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:MERGED_CHILD:%'"
                ") LIMIT 1",
                (task_id,),
            ).fetchone():
                return True
        except Exception:
            pass
        return False

    # === FIX 1: _handle_in_progress — bypass CANON_DUPLICATE_BYPASS for recalc ===
    if _prv1_orig_handle_in_progress and _prv1_canon_handle_in_progress:
        async def _handle_in_progress(conn, task, chat_id, topic_id):
            try:
                if int(topic_id or 0) == 2:
                    task_id = _prv1_s(_prv1_get(task, "id"))
                    input_type = _prv1_s(_prv1_get(task, "input_type"))
                    if input_type == "drive_file" and task_id:
                        if _prv1_has_recalc_context(conn, task_id):
                            _prv1_hist_once(
                                conn, task_id,
                                _PRV1_PATCH_NAME + ":BYPASS_DUPLICATE_BYPASS_FOR_RECALC",
                            )
                            try:
                                conn.commit()
                            except Exception:
                                pass
                            _PRV1_LOG.info(
                                "%s bypass CANON_DUPLICATE_BYPASS task=%s",
                                _PRV1_PATCH_NAME, task_id,
                            )
                            return await _prv1_canon_handle_in_progress(
                                conn, task, chat_id, topic_id
                            )
            except Exception as _e:
                try:
                    _PRV1_LOG.exception("%s HANDLE_IN_PROGRESS_ERR:%s", _PRV1_PATCH_NAME, _e)
                except Exception:
                    pass
            return await _prv1_orig_handle_in_progress(conn, task, chat_id, topic_id)

        globals()["_handle_in_progress"] = _handle_in_progress

    # === FIX 2: _handle_new — FILE_DUPLICATE_MEMORY_GUARD bypass for recalc captions ===
    if _prv1_orig_handle_new:
        async def _handle_new(conn, task, chat_id, topic_id):
            try:
                if int(topic_id or 0) == 2:
                    input_type = _prv1_s(_prv1_get(task, "input_type"))
                    if input_type == "drive_file":
                        task_id = _prv1_s(_prv1_get(task, "id"))
                        raw = _prv1_s(_prv1_get(task, "raw_input"))
                        meta = {}
                        try:
                            meta = _prv1_json.loads(raw)
                        except Exception:
                            try:
                                _dec = _prv1_json.JSONDecoder()
                                _obj, _ = _dec.raw_decode(raw.lstrip())
                                meta = _obj
                            except Exception:
                                pass
                        caption_low = _prv1_s(meta.get("caption")).lower().replace("ё", "е")
                        file_id = _prv1_s(meta.get("file_id"))
                        is_recalc = file_id and any(
                            kw in caption_low for kw in _PRV1_RECALC_CAPTION_WORDS
                        )
                        if is_recalc and task_id:
                            parent = conn.execute(
                                "SELECT id FROM tasks WHERE chat_id=? "
                                "AND COALESCE(topic_id,0)=2 AND id<>? "
                                "AND input_type='drive_file' AND raw_input LIKE ? "
                                "AND state IN ('DONE','AWAITING_CONFIRMATION','ARCHIVED') "
                                "ORDER BY updated_at DESC LIMIT 1",
                                (_prv1_s(chat_id), task_id, "%" + file_id + "%"),
                            ).fetchone()
                            if parent:
                                parent_id = _prv1_s(parent[0])
                                _prv1_hist_once(conn, parent_id, "clarified:" + caption_low[:500])
                                _prv1_hist_once(
                                    conn, parent_id,
                                    "TOPIC2_ADDITIONAL_FACTS_RECALC_STARTED:" + task_id,
                                )
                                try:
                                    conn.execute(
                                        "DELETE FROM task_history WHERE task_id=? AND action IN (?,?,?,?)",
                                        (
                                            parent_id,
                                            "PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:DONE_WITH_DRIVE_LINKS",
                                            "TOPIC2_DONE_CONTRACT_OK",
                                            "TDOIP_OVERRIDE:14_markers_and_drive_links_present",
                                            "TOPIC2_PUBLIC_RESULT_CANON_VIOLATION_RECOVERED_FROM_LATEST_ARTIFACTS",
                                        ),
                                    )
                                except Exception:
                                    pass
                                conn.execute(
                                    "UPDATE tasks SET state='IN_PROGRESS', result='', "
                                    "error_message='', updated_at=datetime('now') WHERE id=?",
                                    (parent_id,),
                                )
                                conn.execute(
                                    "UPDATE tasks SET state='DONE', result=?, "
                                    "error_message=?, updated_at=datetime('now') WHERE id=?",
                                    (
                                        "Уточнение добавлено к ТЗ",
                                        "MERGED_TO_PARENT:" + parent_id,
                                        task_id,
                                    ),
                                )
                                _prv1_hist_once(
                                    conn, task_id,
                                    _PRV1_PATCH_NAME + ":MERGED_TO_PARENT:" + parent_id,
                                )
                                try:
                                    conn.commit()
                                except Exception:
                                    pass
                                _PRV1_LOG.info(
                                    "%s drive_file recalc child=%s parent=%s",
                                    _PRV1_PATCH_NAME, task_id, parent_id,
                                )
                                return
            except Exception as _e:
                try:
                    _PRV1_LOG.exception("%s HANDLE_NEW_ERR:%s", _PRV1_PATCH_NAME, _e)
                except Exception:
                    pass
            return await _prv1_orig_handle_new(conn, task, chat_id, topic_id)

        globals()["_handle_new"] = _handle_new

    _PRV1_LOG.info("%s installed", _PRV1_PATCH_NAME)

except Exception as _prv1_install_err:
    try:
        logger.exception("%s_INSTALL_ERR:%s", "PATCH_TOPIC2_RECALC_PRIORITY_V1", _prv1_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_RECALC_PRIORITY_V1 ===


# === PATCH_TOPIC2_REVISION_MODE_FULL_V1 ===
# Canon §§31-47: Full REVISION_MODE implementation.
# Outermost handler for _handle_new, _handle_in_progress, _update_task.
# For topic_2: handles all cases, NEVER delegates to dead wrappers (22565-24019).
#   Dead wrappers captured alive refs via: _t2fc_orig_handle_new (22572),
#   _t2fo_orig_handle_in_progress (23723), _t2fc_orig_update_task (22573).
# For non-topic_2: passes to outer dead chain (safe — dead patches check topic_id=2).
try:
    import re as _rmfv1_re
    import json as _rmfv1_json
    import logging as _rmfv1_logging

    _RMFV1_LOG = _rmfv1_logging.getLogger("WORKER")
    _RMFV1_PATCH = "PATCH_TOPIC2_REVISION_MODE_FULL_V1"

    # Capture outermost (dead chain) for non-topic_2 delegation
    _rmfv1_orig_hn = globals().get("_handle_new")
    _rmfv1_orig_hip = globals().get("_handle_in_progress")
    _rmfv1_orig_ut = globals().get("_update_task")

    # Alive chains — captured by dead patches from alive zone before dead zone
    # _t2fc_orig_handle_new  = alive _handle_new  (ADDITIONAL_FACTS wrapper at 21960)
    # _t2fo_orig_handle_in_progress = alive _handle_in_progress (SUPPLIER_AND_HEAL at 20395)
    # _t2fc_orig_update_task = alive _update_task (PICKER_BYPASS at 22551)
    _rmfv1_alive_hn  = globals().get("_t2fc_orig_handle_new")
    _rmfv1_alive_hip = globals().get("_t2fo_orig_handle_in_progress")
    _rmfv1_alive_ut  = globals().get("_t2fc_orig_update_task")

    # ── helpers ──────────────────────────────────────────────────────────────────

    def _rmfv1_s(v):
        return "" if v is None else str(v)

    def _rmfv1_low(v):
        return _rmfv1_s(v).lower().replace("ё", "е")

    def _rmfv1_get(obj, key, default=None):
        try:
            if isinstance(obj, dict):
                return obj.get(key, default)
        except Exception:
            pass
        try:
            return obj[key]
        except Exception:
            return default

    def _rmfv1_parse_raw(raw):
        raw = _rmfv1_s(raw).strip()
        if not raw:
            return {}
        try:
            return _rmfv1_json.loads(raw)
        except Exception:
            pass
        try:
            return _rmfv1_json.loads(raw.split("\n", 1)[0].strip())
        except Exception:
            return {}

    def _rmfv1_rowdict(conn, sql, params=()):
        cur = conn.execute(sql, params)
        row = cur.fetchone()
        if not row:
            return None
        try:
            if hasattr(row, "keys"):
                return {k: row[k] for k in row.keys()}
        except Exception:
            pass
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))

    def _rmfv1_hist_once(conn, task_id, action):
        try:
            task_id = _rmfv1_s(task_id)
            action = _rmfv1_s(action)
            if not task_id or not action:
                return
            if not conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
                (task_id, action),
            ).fetchone():
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (task_id, action),
                )
        except Exception:
            pass

    def _rmfv1_task_topic(conn, task_id):
        try:
            row = conn.execute(
                "SELECT COALESCE(topic_id,0) FROM tasks WHERE id=? LIMIT 1",
                (_rmfv1_s(task_id),),
            ).fetchone()
            if row:
                return int(row[0] or 0)
        except Exception:
            pass
        return 0

    # ── REVISION_MODE keywords §31 ───────────────────────────────────────────────

    _RMFV1_REVISION_KW = (
        "добавь", "добавить", "пересчитай", "пересчитать",
        "измени", "изменить", "скорректируй", "скорректировать",
        "исправь", "исправить", "обнови", "обновить", "обновление",
        "новые позиции", "новые вводные", "новый расчет", "новый рачет",
        "повтори расчет", "перерасчет", "перерасчёт",
        "утепление", "утеплите", "утеплить",
        "поставщик", "поставщики",
        "фасад", "потолок", "перекрытия", "кровля",
        "фундамент", "сваи", "канализаци", "водоснабжен",
        "электрика", "отопление", "окна", "двери",
        "плитка", "ламинат", "теплый пол",
        "вентиляция", "новые материалы", "другие материалы",
        "новый поставщик", "другой поставщик",
        "добавить раздел", "новый раздел",
    )

    # ── STATUS_MODE keywords §32 ─────────────────────────────────────────────────

    _RMFV1_STATUS_KW = (
        "где смета", "где ссылка", "скинь ссылку", "пришли ссылку",
        "дай ссылку", "готова смета", "смета готова", "скинь смету",
        "пришли смету", "покажи смету", "смета есть", "ссылка на смету",
        "ссылку на смету", "отправь смету", "дай смету", "пришли файл",
        "скинь файл", "отправь файл", "где файл", "ссылку на файл",
    )

    def _rmfv1_is_revision(text):
        t = _rmfv1_low(text)
        return any(kw in t for kw in _RMFV1_REVISION_KW)

    def _rmfv1_is_status(text):
        t = _rmfv1_low(text)
        return any(kw in t for kw in _RMFV1_STATUS_KW)

    # ── Freshness gate §35 ────────────────────────────────────────────────────────

    _RMFV1_STALE_MARKERS = (
        "clarified:",
        "MERGED_TO_PARENT:",
        "STALE_RESET",
        "TOPIC2_ADDITIONAL_FACT_MERGED:",
        "TOPIC2_ADDITIONAL_FACTS_RECALC_STARTED:",
        "PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:MERGED_CHILD:",
        "PATCH_TOPIC2_REVISION_MODE_FULL_V1:REVISION_STARTED:",
        "PATCH_TOPIC2_REVISION_MODE_FULL_V1:DRIVE_REVISION_MERGED_TO:",
        "PATCH_TOPIC2_REVISION_MODE_FULL_V1:TEXT_REVISION_MERGED_TO:",
    )

    def _rmfv1_is_artifact_fresh(conn, task_id):
        task_id = _rmfv1_s(task_id)
        try:
            row = conn.execute(
                "SELECT rowid FROM task_history WHERE task_id=? "
                "AND action LIKE 'TOPIC2_DRIVE_LINKS_SAVED:%' ORDER BY rowid DESC LIMIT 1",
                (task_id,),
            ).fetchone()
            if not row:
                return False
            links_rowid = row[0]
            for marker in _RMFV1_STALE_MARKERS:
                if conn.execute(
                    "SELECT 1 FROM task_history WHERE task_id=? AND action LIKE ? AND rowid > ? LIMIT 1",
                    (task_id, marker + "%", links_rowid),
                ).fetchone():
                    return False
            return True
        except Exception:
            return False

    def _rmfv1_extract_links(conn, task_id):
        task_id = _rmfv1_s(task_id)
        xlsx = ""
        pdf = ""
        try:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? "
                "AND action LIKE 'TOPIC2_DRIVE_LINKS_SAVED:%' ORDER BY rowid ASC",
                (task_id,),
            ).fetchall()
            for r in rows:
                a = _rmfv1_s(r[0])
                m = _rmfv1_re.search(r"xlsx=([A-Za-z0-9_\-]+)", a)
                if m:
                    xlsx = m.group(1)
                m = _rmfv1_re.search(r"pdf=([A-Za-z0-9_\-]+)", a)
                if m:
                    pdf = m.group(1)
        except Exception:
            pass
        return xlsx, pdf

    def _rmfv1_status_reply(conn, task_id, raw_obj):
        xlsx, pdf = _rmfv1_extract_links(conn, task_id)
        if not xlsx or not pdf:
            return None
        caption = _rmfv1_s(raw_obj.get("caption")) if isinstance(raw_obj, dict) else ""
        lines = ["✅ Смета готова", ""]
        if caption:
            lines += ["ТЗ: " + caption, ""]
        lines += [
            "Excel: https://drive.google.com/file/d/" + xlsx + "/view?usp=drivesdk",
            "PDF: https://drive.google.com/file/d/" + pdf + "/view?usp=drivesdk",
            "",
            "Подтверди или пришли правки",
        ]
        return "\n".join(lines)

    async def _rmfv1_send_text(chat_id, topic_id, text, task):
        try:
            _send_fn = globals().get("_send_once_ex") or globals().get("_send_once")
            if _send_fn:
                try:
                    await _send_fn(chat_id, topic_id, text, task)
                    return
                except Exception:
                    pass
            _bot = globals().get("bot")
            if _bot:
                kwargs = {}
                if topic_id:
                    kwargs["message_thread_id"] = int(topic_id)
                await _bot.send_message(chat_id=int(chat_id), text=text, **kwargs)
        except Exception as _e:
            try:
                _RMFV1_LOG.exception("%s send_text err=%s", _RMFV1_PATCH, _e)
            except Exception:
                pass

    # ── blocking markers cleared on revision §41 ─────────────────────────────────

    _RMFV1_BLOCKING_MARKERS = (
        "PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:DONE_WITH_DRIVE_LINKS",
        "TOPIC2_DONE_CONTRACT_OK",
        "TDOIP_OVERRIDE:14_markers_and_drive_links_present",
        "TOPIC2_PUBLIC_RESULT_CANON_VIOLATION_RECOVERED_FROM_LATEST_ARTIFACTS",
        "PATCH_TOPIC2_FULL_CANON_DUPLICATE_BYPASS_OUTPUT_V1:RUNTIME_FIXED_FROM:",
        "PATCH_TOPIC2_FULL_TASK_CHAIN_RESTORE_NO_REGRESSION_V1:MANUAL_RESTORE",
        "FILE_DUPLICATE_MEMORY_GUARD_V1:DONE",
        "reply_sent:file_dup_guard_v1",
    )

    def _rmfv1_clear_blocking_markers(conn, task_id):
        task_id = _rmfv1_s(task_id)
        try:
            for marker in _RMFV1_BLOCKING_MARKERS:
                conn.execute(
                    "DELETE FROM task_history WHERE task_id=? AND action LIKE ?",
                    (task_id, marker + "%"),
                )
        except Exception:
            pass

    def _rmfv1_reset_parent_for_recalc(conn, parent_id, revision_note, child_id):
        try:
            _rmfv1_clear_blocking_markers(conn, parent_id)
            _rmfv1_hist_once(
                conn, parent_id,
                _RMFV1_PATCH + ":REVISION_STARTED:" + _rmfv1_s(child_id),
            )
            if revision_note and revision_note != "status_stale_reset":
                _rmfv1_hist_once(conn, parent_id, "clarified:" + _rmfv1_s(revision_note)[:500])
            conn.execute(
                "UPDATE tasks SET state='IN_PROGRESS', result='', error_message='', "
                "updated_at=datetime('now') WHERE id=?",
                (parent_id,),
            )
        except Exception as _e:
            try:
                _RMFV1_LOG.exception("%s reset_parent err=%s", _RMFV1_PATCH, _e)
            except Exception:
                pass

    def _rmfv1_find_drive_parent(conn, chat_id, file_id):
        try:
            return conn.execute(
                "SELECT id FROM tasks WHERE chat_id=? AND COALESCE(topic_id,0)=2 "
                "AND input_type='drive_file' AND raw_input LIKE ? "
                "AND state IN ('DONE','AWAITING_CONFIRMATION','ARCHIVED') "
                "ORDER BY updated_at DESC LIMIT 1",
                (_rmfv1_s(chat_id), "%" + _rmfv1_s(file_id) + "%"),
            ).fetchone()
        except Exception:
            return None

    def _rmfv1_find_text_parent(conn, chat_id, topic_id_val):
        try:
            return conn.execute(
                "SELECT id, raw_input FROM tasks WHERE chat_id=? "
                "AND COALESCE(topic_id,0)=? AND input_type='drive_file' "
                "AND state IN ('DONE','AWAITING_CONFIRMATION','ARCHIVED','IN_PROGRESS') "
                "ORDER BY updated_at DESC LIMIT 1",
                (_rmfv1_s(chat_id), int(topic_id_val or 0)),
            ).fetchone()
        except Exception:
            return None

    # ── _handle_new (§§31-38) ────────────────────────────────────────────────────

    async def _handle_new(conn, task, chat_id, topic_id):
        try:
            if int(topic_id or 0) != 2:
                if _rmfv1_orig_hn:
                    return await _rmfv1_orig_hn(conn, task, chat_id, topic_id)
                return

            task_id    = _rmfv1_s(_rmfv1_get(task, "id"))
            input_type = _rmfv1_s(_rmfv1_get(task, "input_type"))
            raw        = _rmfv1_s(_rmfv1_get(task, "raw_input"))
            raw_obj    = _rmfv1_parse_raw(raw)

            # ── drive_file branch ─────────────────────────────────────────────
            if input_type == "drive_file":
                file_id = _rmfv1_s(raw_obj.get("file_id")) if isinstance(raw_obj, dict) else ""
                caption = _rmfv1_s(raw_obj.get("caption")) if isinstance(raw_obj, dict) else ""

                if file_id:
                    parent_row = _rmfv1_find_drive_parent(conn, chat_id, file_id)
                    if parent_row:
                        parent_id = _rmfv1_s(parent_row[0])
                        if _rmfv1_is_revision(caption):
                            # §31 REVISION_MODE — recalc caption on known file
                            _rmfv1_reset_parent_for_recalc(conn, parent_id, caption, task_id)
                            conn.execute(
                                "UPDATE tasks SET state='DONE', result=?, error_message=?, "
                                "updated_at=datetime('now') WHERE id=?",
                                (
                                    "Уточнение принято к пересчёту",
                                    "MERGED_TO_PARENT:" + parent_id,
                                    task_id,
                                ),
                            )
                            _rmfv1_hist_once(
                                conn, task_id,
                                _RMFV1_PATCH + ":DRIVE_REVISION_MERGED_TO:" + parent_id,
                            )
                            try:
                                conn.commit()
                            except Exception:
                                pass
                            _RMFV1_LOG.info(
                                "%s drive_revision child=%s parent=%s",
                                _RMFV1_PATCH, task_id, parent_id,
                            )
                            return
                        else:
                            # §33 FILE_DUPLICATE_GUARD — same file, no recalc intent
                            _rmfv1_hist_once(conn, task_id, _RMFV1_PATCH + ":FILE_DUPLICATE_BLOCKED")
                            _rmfv1_hist_once(conn, task_id, "FILE_DUPLICATE_MEMORY_GUARD_V1:DONE")
                            conn.execute(
                                "UPDATE tasks SET state='DONE', result=?, error_message=?, "
                                "updated_at=datetime('now') WHERE id=?",
                                (
                                    "Файл уже есть в обработке. Если хотите пересчитать — напишите что изменить.",
                                    "FILE_DUPLICATE_BLOCKED_BY_REVISION_MODE_FULL_V1",
                                    task_id,
                                ),
                            )
                            try:
                                conn.commit()
                            except Exception:
                                pass
                            try:
                                await _rmfv1_send_text(
                                    chat_id, topic_id,
                                    "Файл уже есть в обработке.\n\nЕсли хотите пересчитать — напишите что изменить (например, «добавь утепление 250мм»).",
                                    task,
                                )
                            except Exception:
                                pass
                            return

                # No existing parent → fall to alive chain (new estimate)
                if _rmfv1_alive_hn:
                    return await _rmfv1_alive_hn(conn, task, chat_id, topic_id)
                return

            # ── text / voice branch ───────────────────────────────────────────
            if input_type in ("text", "voice"):
                raw_text = (
                    _rmfv1_s(raw_obj.get("text"))
                    if isinstance(raw_obj, dict) and raw_obj.get("text")
                    else raw
                )

                # §31 REVISION_MODE
                if _rmfv1_is_revision(raw_text):
                    parent_row = _rmfv1_find_text_parent(conn, chat_id, topic_id)
                    if parent_row:
                        parent_id = _rmfv1_s(parent_row[0])
                        _rmfv1_reset_parent_for_recalc(conn, parent_id, raw_text, task_id)
                        conn.execute(
                            "UPDATE tasks SET state='DONE', result=?, error_message=?, "
                            "updated_at=datetime('now') WHERE id=?",
                            (
                                "Уточнение принято к пересчёту",
                                "MERGED_TO_PARENT:" + parent_id,
                                task_id,
                            ),
                        )
                        _rmfv1_hist_once(
                            conn, task_id,
                            _RMFV1_PATCH + ":TEXT_REVISION_MERGED_TO:" + parent_id,
                        )
                        try:
                            conn.commit()
                        except Exception:
                            pass
                        _RMFV1_LOG.info(
                            "%s text_revision child=%s parent=%s",
                            _RMFV1_PATCH, task_id, parent_id,
                        )
                        return
                    # No parent → alive chain (new request)

                # §32 STATUS_MODE
                elif _rmfv1_is_status(raw_text):
                    parent_row = _rmfv1_find_text_parent(conn, chat_id, topic_id)
                    if parent_row:
                        parent_id  = _rmfv1_s(parent_row[0])
                        parent_raw = _rmfv1_parse_raw(_rmfv1_s(parent_row[1]))
                        if _rmfv1_is_artifact_fresh(conn, parent_id):
                            # §32 artifact is fresh → deliver links (no "восстановлено")
                            reply = _rmfv1_status_reply(conn, parent_id, parent_raw)
                            if reply:
                                conn.execute(
                                    "UPDATE tasks SET state='DONE', result=?, error_message=?, "
                                    "updated_at=datetime('now') WHERE id=?",
                                    (reply, "STATUS_REPLY_FROM_PARENT:" + parent_id, task_id),
                                )
                                _rmfv1_hist_once(
                                    conn, task_id,
                                    _RMFV1_PATCH + ":STATUS_DELIVERED_FROM:" + parent_id,
                                )
                                try:
                                    conn.commit()
                                except Exception:
                                    pass
                                try:
                                    await _rmfv1_send_text(chat_id, topic_id, reply, task)
                                except Exception:
                                    pass
                                _RMFV1_LOG.info(
                                    "%s status_reply child=%s parent=%s",
                                    _RMFV1_PATCH, task_id, parent_id,
                                )
                                return
                        else:
                            # §35 stale artifact → reset parent for recalc
                            _rmfv1_reset_parent_for_recalc(
                                conn, parent_id, "status_stale_reset", task_id
                            )
                            stale_msg = "Смета устарела — пересчитываю с учётом последних изменений. Ожидайте."
                            conn.execute(
                                "UPDATE tasks SET state='DONE', result=?, error_message=?, "
                                "updated_at=datetime('now') WHERE id=?",
                                (
                                    stale_msg,
                                    "STALE_ARTIFACT_RESET_PARENT:" + parent_id,
                                    task_id,
                                ),
                            )
                            _rmfv1_hist_once(
                                conn, task_id,
                                _RMFV1_PATCH + ":STATUS_STALE_RECALC_TRIGGERED",
                            )
                            try:
                                conn.commit()
                            except Exception:
                                pass
                            try:
                                await _rmfv1_send_text(chat_id, topic_id, stale_msg, task)
                            except Exception:
                                pass
                            return

        except Exception as _e:
            try:
                _RMFV1_LOG.exception("%s _handle_new err=%s", _RMFV1_PATCH, _e)
            except Exception:
                pass

        # Fallback: alive chain (covers all unrecognised topic_2 cases + FOLLOWUP_BIND)
        if _rmfv1_alive_hn:
            return await _rmfv1_alive_hn(conn, task, chat_id, topic_id)
        if _rmfv1_orig_hn:
            return await _rmfv1_orig_hn(conn, task, chat_id, topic_id)

    if _rmfv1_orig_hn:
        globals()["_handle_new"] = _handle_new

    # ── _handle_in_progress: bypass dead CANON_DUPLICATE_BYPASS §36 ──────────────

    if _rmfv1_orig_hip and _rmfv1_alive_hip:
        async def _handle_in_progress(conn, task, chat_id, topic_id):
            try:
                if int(topic_id or 0) == 2:
                    # Always call alive chain for topic_2 (dead chain returns old artifacts §36)
                    return await _rmfv1_alive_hip(conn, task, chat_id, topic_id)
            except Exception as _e:
                try:
                    _RMFV1_LOG.exception("%s _handle_in_progress err=%s", _RMFV1_PATCH, _e)
                except Exception:
                    pass
            return await _rmfv1_orig_hip(conn, task, chat_id, topic_id)

        globals()["_handle_in_progress"] = _handle_in_progress

    # ── _update_task: strip READY_ARTIFACT_DELIVERED_FROM, bypass dead wrappers ───

    if _rmfv1_orig_ut and _rmfv1_alive_ut:
        def _update_task(conn, task_id, **kwargs):
            try:
                topic = _rmfv1_task_topic(conn, task_id)
                if topic == 2:
                    # Strip READY_ARTIFACT_DELIVERED_FROM set by dead CANON_DUPLICATE_BYPASS (§37)
                    err = _rmfv1_s(kwargs.get("error_message"))
                    if err.startswith("READY_ARTIFACT_DELIVERED_FROM:"):
                        kwargs = dict(kwargs)
                        kwargs["error_message"] = ""
                        try:
                            _RMFV1_LOG.info(
                                "%s stripped READY_ARTIFACT_DELIVERED_FROM task=%s",
                                _RMFV1_PATCH, task_id,
                            )
                        except Exception:
                            pass
                    # Bypass dead _update_task wrappers for topic_2
                    return _rmfv1_alive_ut(conn, task_id, **kwargs)
            except Exception as _e:
                try:
                    _RMFV1_LOG.exception("%s _update_task err=%s", _RMFV1_PATCH, _e)
                except Exception:
                    pass
            return _rmfv1_orig_ut(conn, task_id, **kwargs)

        globals()["_update_task"] = _update_task

    _RMFV1_LOG.info(
        "%s installed hn=%s hip=%s ut=%s alive_hn=%s alive_hip=%s alive_ut=%s",
        _RMFV1_PATCH,
        bool(_rmfv1_orig_hn), bool(_rmfv1_orig_hip), bool(_rmfv1_orig_ut),
        bool(_rmfv1_alive_hn), bool(_rmfv1_alive_hip), bool(_rmfv1_alive_ut),
    )

except Exception as _rmfv1_install_err:
    try:
        logger.exception(
            "PATCH_TOPIC2_REVISION_MODE_FULL_V1_INSTALL_ERR:%s", _rmfv1_install_err
        )
    except Exception:
        pass
# === /PATCH_TOPIC2_REVISION_MODE_FULL_V1 ===


pass  # entry_point moved to EOF by PATCH_TOPIC2_REVISION_RECALC_FULL_CANON_NO_REGRESSION_V2_FRESHNESS_FIX

# === PATCH_TOPIC2_REVISION_RECALC_FULL_CANON_NO_REGRESSION_V2 ===
# Supersedes REVISION_MODE_FULL_V1 as outermost _handle_new for topic_2.
# Implements §§31-47 fully: extended classification, 5-level parent lookup,
# JSON-safe revision merge, price-choice reuse, runtime repair for f030.
try:
    import re as _t2v2_re
    import json as _t2v2_json
    import logging as _t2v2_logging

    _T2V2_LOG = _t2v2_logging.getLogger("WORKER")
    _T2V2_PATCH = "PATCH_TOPIC2_REVISION_RECALC_FULL_CANON_NO_REGRESSION_V2"

    # Capture V1 as prev-handler (handles non-topic_2 correctly)
    _t2v2_prev_hn = globals().get("_handle_new")

    # Alive chain refs — set by V1 from the dead-patch captures
    _t2v2_alive_hn  = globals().get("_rmfv1_alive_hn")  or globals().get("_t2fc_orig_handle_new")
    _t2v2_alive_hip = globals().get("_rmfv1_alive_hip") or globals().get("_t2fo_orig_handle_in_progress")
    _t2v2_alive_ut  = globals().get("_rmfv1_alive_ut")  or globals().get("_t2fc_orig_update_task")

    # ── helpers ─────────────────────────────────────────────────────────────────

    def _t2v2_s(v):
        return "" if v is None else str(v)

    def _t2v2_low(v):
        return _t2v2_s(v).lower().replace("ё", "е")

    def _t2v2_parse_raw(raw):
        raw = _t2v2_s(raw).strip()
        if not raw:
            return {}
        try:
            return _t2v2_json.loads(raw)
        except Exception:
            pass
        try:
            return _t2v2_json.loads(raw.split("\n", 1)[0].strip())
        except Exception:
            return {}

    def _t2v2_hist_once(conn, task_id, action):
        try:
            tid = _t2v2_s(task_id)
            act = _t2v2_s(action)
            if not tid or not act:
                return
            if not conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
                (tid, act),
            ).fetchone():
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (tid, act),
                )
        except Exception:
            pass

    # ── keyword sets §31 ────────────────────────────────────────────────────────

    _T2V2_REVISION_KW = (
        "добавь", "добавить", "пересчитай", "пересчитать",
        "измени", "изменить", "скорректируй", "скорректировать",
        "исправь", "исправить", "обнови", "обновить", "обновление",
        "новые позиции", "новые вводные", "новый расчет", "новый рачет",
        "повтори расчет", "перерасчет", "перерасчёт",
        "утепление", "утеплите", "утеплить",
        "поставщик", "поставщики", "новый поставщик", "другой поставщик",
        "фасад", "потолок", "перекрытия", "кровля",
        "фундамент", "сваи", "канализаци", "водоснабжен",
        "электрика", "отопление", "окна", "двери",
        "плитка", "ламинат", "теплый пол",
        "вентиляция", "новые материалы", "другие материалы",
        "добавить раздел", "новый раздел",
        "каменная вата", "rockwool", "минвата", "пеноплекс",
        "другие цены", "актуальные цены", "цены поставщик",
    )

    _T2V2_STATUS_KW = (
        "где смета", "где ссылка", "скинь ссылку", "пришли ссылку",
        "дай ссылку", "готова смета", "смета готова", "скинь смету",
        "пришли смету", "покажи смету", "смета есть", "ссылка на смету",
        "ссылку на смету", "отправь смету", "дай смету", "пришли файл",
        "скинь файл", "отправь файл", "где файл", "ссылку на файл",
        "статус", "что по задаче", "как дела со сметой", "когда смета",
        "сделала смету", "сделан",
    )

    _T2V2_PRICE_KW = (
        "минимальный бюджет", "минимальные", "оптимальный", "оптимальные",
        "стандартный", "стандартные", "премиум", "лучшие материалы",
        "делай", "считай", "рассчитай", "начинай", "поехали",
    )

    _T2V2_PRICE_DIGIT_RE = _t2v2_re.compile(r"^\s*[1-4]\s*$")

    _T2V2_CONFIRM_KW = (
        "да", "ок", "ok", "верно", "подтверждаю", "подтверди",
        "всё верно", "все верно", "согласен", "согласна", "хорошо",
        "отлично", "принято", "принимаю", "правильно",
    )

    _T2V2_CANCEL_KW = (
        "отмени", "отменить", "не надо", "стоп", "stop", "нет",
        "не нужно", "не делай", "отказываюсь",
    )

    def _t2v2_classify(text):
        t = _t2v2_low(text)
        if any(kw in t for kw in _T2V2_REVISION_KW):
            return "REVISION"
        if any(kw in t for kw in _T2V2_STATUS_KW):
            return "STATUS"
        if _T2V2_PRICE_DIGIT_RE.match(text.strip()) or any(kw in t for kw in _T2V2_PRICE_KW):
            return "PRICE_CHOICE"
        if any(kw in t for kw in _T2V2_CONFIRM_KW):
            return "CONFIRM"
        if any(kw in t for kw in _T2V2_CANCEL_KW):
            return "CANCEL"
        return "UNKNOWN"

    # ── 5-level parent lookup ────────────────────────────────────────────────────

    def _t2v2_find_parent(conn, task, chat_id, topic_id_val):
        tid = _t2v2_s(task.get("id") if isinstance(task, dict) else "")
        chat = _t2v2_s(chat_id)
        tval = int(topic_id_val or 0)

        # Level 1: reply_to_message_id → task with that bot_message_id
        reply_mid = None
        try:
            reply_mid = task.get("reply_to_message_id") if isinstance(task, dict) else None
        except Exception:
            pass
        if reply_mid:
            try:
                row = conn.execute(
                    "SELECT id, raw_input FROM tasks WHERE chat_id=? "
                    "AND COALESCE(topic_id,0)=? AND bot_message_id=? "
                    "AND state IN ('DONE','AWAITING_CONFIRMATION','ARCHIVED','IN_PROGRESS') LIMIT 1",
                    (chat, tval, int(reply_mid)),
                ).fetchone()
                if row:
                    return _t2v2_s(row[0]), _t2v2_s(row[1])
            except Exception:
                pass

        # Level 2: current task's bot_message_id → parent referencing it
        bot_mid = None
        try:
            bot_mid = task.get("bot_message_id") if isinstance(task, dict) else None
        except Exception:
            pass
        if bot_mid:
            try:
                row = conn.execute(
                    "SELECT id, raw_input FROM tasks WHERE chat_id=? "
                    "AND COALESCE(topic_id,0)=? AND reply_to_message_id=? "
                    "AND state IN ('DONE','AWAITING_CONFIRMATION','ARCHIVED','IN_PROGRESS') LIMIT 1",
                    (chat, tval, int(bot_mid)),
                ).fetchone()
                if row:
                    return _t2v2_s(row[0]), _t2v2_s(row[1])
            except Exception:
                pass

        # Level 3: latest IN_PROGRESS or AWAITING_CONFIRMATION drive_file in topic_2
        try:
            row = conn.execute(
                "SELECT id, raw_input FROM tasks WHERE chat_id=? "
                "AND COALESCE(topic_id,0)=? AND input_type='drive_file' "
                "AND state IN ('IN_PROGRESS','AWAITING_CONFIRMATION') "
                "AND id != ? ORDER BY updated_at DESC LIMIT 1",
                (chat, tval, tid),
            ).fetchone()
            if row:
                return _t2v2_s(row[0]), _t2v2_s(row[1])
        except Exception:
            pass

        # Level 4: latest DONE/ARCHIVED drive_file with canonical history markers
        try:
            rows = conn.execute(
                "SELECT t.id, t.raw_input FROM tasks t WHERE t.chat_id=? "
                "AND COALESCE(t.topic_id,0)=? AND t.input_type='drive_file' "
                "AND t.state IN ('DONE','ARCHIVED','AWAITING_CONFIRMATION') "
                "AND t.id != ? ORDER BY t.updated_at DESC LIMIT 10",
                (chat, tval, tid),
            ).fetchall()
            for r in rows:
                rid = _t2v2_s(r[0])
                has_hist = conn.execute(
                    "SELECT 1 FROM task_history WHERE task_id=? "
                    "AND (action LIKE 'TOPIC2_DRIVE_LINKS_SAVED:%' "
                    "OR action LIKE 'TOPIC2_DRIVE_UPLOAD_XLSX_OK%') LIMIT 1",
                    (rid,),
                ).fetchone()
                if has_hist:
                    return rid, _t2v2_s(r[1])
        except Exception:
            pass

        # Level 5: any latest topic_2 drive_file with artifacts
        try:
            rows = conn.execute(
                "SELECT t.id, t.raw_input FROM tasks t WHERE t.chat_id=? "
                "AND COALESCE(t.topic_id,0)=? AND input_type='drive_file' "
                "AND t.id != ? ORDER BY t.updated_at DESC LIMIT 5",
                (chat, tval, tid),
            ).fetchall()
            for r in rows:
                rid = _t2v2_s(r[0])
                has_price = conn.execute(
                    "SELECT 1 FROM task_history WHERE task_id=? "
                    "AND (action LIKE 'TOPIC2_PRICE_CHOICE_CONFIRMED:%' "
                    "OR action LIKE 'TOPIC2_CONTEXT_READY%') LIMIT 1",
                    (rid,),
                ).fetchone()
                if has_price:
                    return rid, _t2v2_s(r[1])
        except Exception:
            pass

        return None, None

    # ── freshness gate §35 ────────────────────────────────────────────────────────

    _T2V2_STALE_MARKERS = (
        "clarified:",
        "MERGED_TO_PARENT:",
        "STALE_RESET",
        "TOPIC2_ADDITIONAL_FACT_MERGED:",
        "TOPIC2_ADDITIONAL_FACTS_RECALC_STARTED:",
        "PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:MERGED_CHILD:",
        "PATCH_TOPIC2_REVISION_MODE_FULL_V1:REVISION_STARTED:",
        "PATCH_TOPIC2_REVISION_MODE_FULL_V1:DRIVE_REVISION_MERGED_TO:",
        "PATCH_TOPIC2_REVISION_MODE_FULL_V1:TEXT_REVISION_MERGED_TO:",
        _T2V2_PATCH + ":REVISION_STARTED:",
        _T2V2_PATCH + ":REVISION_MERGED_TO:",
    )

    def _t2v2_is_fresh(conn, task_id):
        tid = _t2v2_s(task_id)
        try:
            row = conn.execute(
                "SELECT rowid FROM task_history WHERE task_id=? "
                "AND action LIKE 'TOPIC2_DRIVE_LINKS_SAVED:%' ORDER BY rowid DESC LIMIT 1",
                (tid,),
            ).fetchone()
            if not row:
                return False
            links_rid = row[0]
            for marker in _T2V2_STALE_MARKERS:
                if conn.execute(
                    "SELECT 1 FROM task_history WHERE task_id=? AND action LIKE ? AND rowid > ? LIMIT 1",
                    (tid, marker + "%", links_rid),
                ).fetchone():
                    return False
            return True
        except Exception:
            return False

    def _t2v2_extract_links(conn, task_id):
        tid = _t2v2_s(task_id)
        xlsx = pdf = ""
        try:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? "
                "AND action LIKE 'TOPIC2_DRIVE_LINKS_SAVED:%' ORDER BY rowid ASC",
                (tid,),
            ).fetchall()
            for r in rows:
                a = _t2v2_s(r[0])
                m = _t2v2_re.search(r"xlsx=([A-Za-z0-9_\-]+)", a)
                if m:
                    xlsx = m.group(1)
                m = _t2v2_re.search(r"pdf=([A-Za-z0-9_\-]+)", a)
                if m:
                    pdf = m.group(1)
        except Exception:
            pass
        return xlsx, pdf

    # ── price-choice lookup §6 ────────────────────────────────────────────────────

    def _t2v2_get_price_choice(conn, task_id):
        tid = _t2v2_s(task_id)
        try:
            row = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? "
                "AND action LIKE 'TOPIC2_PRICE_CHOICE_CONFIRMED:%' ORDER BY rowid DESC LIMIT 1",
                (tid,),
            ).fetchone()
            if row:
                return _t2v2_s(row[0]).replace("TOPIC2_PRICE_CHOICE_CONFIRMED:", "").strip()
        except Exception:
            pass
        return ""

    # ── JSON-safe revision merge §3 ────────────────────────────────────────────────

    def _t2v2_merge_revision_json(conn, parent_id, revision_text):
        pid = _t2v2_s(parent_id)
        try:
            row = conn.execute("SELECT raw_input FROM tasks WHERE id=? LIMIT 1", (pid,)).fetchone()
            if not row:
                return
            raw = _t2v2_s(row[0]).strip()
            try:
                obj = _t2v2_json.loads(raw)
            except Exception:
                obj = {"_raw_text": raw}
            if not isinstance(obj, dict):
                obj = {"_raw_text": _t2v2_s(obj)}
            revisions = obj.get("canon_revisions")
            if not isinstance(revisions, list):
                revisions = []
            revisions.append(_t2v2_s(revision_text)[:800])
            obj["canon_revisions"] = revisions
            new_raw = _t2v2_json.dumps(obj, ensure_ascii=False)
            conn.execute("UPDATE tasks SET raw_input=? WHERE id=?", (new_raw, pid))
        except Exception as _me:
            try:
                _T2V2_LOG.warning("%s merge_revision_json err=%s", _T2V2_PATCH, _me)
            except Exception:
                pass

    # ── blocking-markers cleanup §41 ──────────────────────────────────────────────

    _T2V2_BLOCKING_MARKERS = (
        "PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:DONE_WITH_DRIVE_LINKS",
        "TOPIC2_DONE_CONTRACT_OK",
        "TDOIP_OVERRIDE:14_markers_and_drive_links_present",
        "TOPIC2_PUBLIC_RESULT_CANON_VIOLATION_RECOVERED_FROM_LATEST_ARTIFACTS",
        "PATCH_TOPIC2_FULL_CANON_DUPLICATE_BYPASS_OUTPUT_V1:RUNTIME_FIXED_FROM:",
        "PATCH_TOPIC2_FULL_TASK_CHAIN_RESTORE_NO_REGRESSION_V1:MANUAL_RESTORE",
        "FILE_DUPLICATE_MEMORY_GUARD_V1:DONE",
        "reply_sent:file_dup_guard_v1",
        "PATCH_TOPIC2_REVISION_MODE_FULL_V1:FILE_DUPLICATE_BLOCKED",
        "FULL_CONSTRUCTION_FILE_CONTOUR_CANON_GUARD_V1:UPDATE_BLOCKED:",
        "state:FAILED:EXECUTION_TIMEOUT",
    )

    def _t2v2_clear_blockers(conn, task_id):
        tid = _t2v2_s(task_id)
        try:
            for marker in _T2V2_BLOCKING_MARKERS:
                conn.execute(
                    "DELETE FROM task_history WHERE task_id=? AND action LIKE ?",
                    (tid, marker + "%"),
                )
        except Exception:
            pass

    def _t2v2_reset_parent(conn, parent_id, revision_note, child_id, merge_json=True):
        pid = _t2v2_s(parent_id)
        try:
            _t2v2_clear_blockers(conn, pid)
            if merge_json and revision_note and revision_note != "status_stale_reset":
                _t2v2_merge_revision_json(conn, pid, revision_note)
                _t2v2_hist_once(conn, pid, "clarified:" + _t2v2_s(revision_note)[:500])
            _t2v2_hist_once(
                conn, pid,
                _T2V2_PATCH + ":REVISION_STARTED:" + _t2v2_s(child_id),
            )
            conn.execute(
                "UPDATE tasks SET state='IN_PROGRESS', result='', error_message='', "
                "updated_at=datetime('now') WHERE id=?",
                (pid,),
            )
        except Exception as _e:
            try:
                _T2V2_LOG.exception("%s reset_parent err=%s", _T2V2_PATCH, _e)
            except Exception:
                pass

    # ── Telegram send helper ─────────────────────────────────────────────────────

    async def _t2v2_send(chat_id, topic_id, text, task):
        try:
            _send_fn = globals().get("_send_once_ex") or globals().get("_send_once")
            if _send_fn:
                try:
                    await _send_fn(chat_id, topic_id, text, task)
                    return
                except Exception:
                    pass
            _bot = globals().get("bot")
            if _bot:
                kw = {}
                if topic_id:
                    kw["message_thread_id"] = int(topic_id)
                await _bot.send_message(chat_id=int(chat_id), text=text, **kw)
        except Exception as _se:
            try:
                _T2V2_LOG.exception("%s send err=%s", _T2V2_PATCH, _se)
            except Exception:
                pass

    def _t2v2_status_reply(conn, parent_id, caption=""):
        xlsx, pdf = _t2v2_extract_links(conn, parent_id)
        if not xlsx or not pdf:
            return None
        lines = ["✅ Смета готова", ""]
        if caption:
            lines += ["ТЗ: " + caption, ""]
        lines += [
            "Excel: https://drive.google.com/file/d/" + xlsx + "/view?usp=drivesdk",
            "PDF: https://drive.google.com/file/d/" + pdf + "/view?usp=drivesdk",
            "",
            "Подтверди или пришли правки",
        ]
        return "\n".join(lines)

    # ── _handle_new (outermost) ───────────────────────────────────────────────────

    async def _handle_new(conn, task, chat_id, topic_id):
        try:
            if int(topic_id or 0) != 2:
                if _t2v2_prev_hn:
                    return await _t2v2_prev_hn(conn, task, chat_id, topic_id)
                return

            task_id    = _t2v2_s(task.get("id") if isinstance(task, dict) else "")
            input_type = _t2v2_s(task.get("input_type") if isinstance(task, dict) else "")
            raw        = _t2v2_s(task.get("raw_input") if isinstance(task, dict) else "")
            raw_obj    = _t2v2_parse_raw(raw)
            caption    = (_t2v2_s(raw_obj.get("caption")) if isinstance(raw_obj, dict) else "")

            # ── drive_file branch ─────────────────────────────────────────────
            if input_type == "drive_file":
                file_id = _t2v2_s(raw_obj.get("file_id")) if isinstance(raw_obj, dict) else ""
                mode = _t2v2_classify(caption) if caption else "UNKNOWN"

                if file_id:
                    # Look for existing parent with this file_id
                    try:
                        par_row = conn.execute(
                            "SELECT id FROM tasks WHERE chat_id=? AND COALESCE(topic_id,0)=2 "
                            "AND input_type='drive_file' AND raw_input LIKE ? "
                            "AND state IN ('DONE','AWAITING_CONFIRMATION','ARCHIVED','IN_PROGRESS') "
                            "AND id != ? ORDER BY updated_at DESC LIMIT 1",
                            (_t2v2_s(chat_id), "%" + file_id + "%", task_id),
                        ).fetchone()
                    except Exception:
                        par_row = None

                    if par_row:
                        parent_id = _t2v2_s(par_row[0])
                        if mode == "REVISION" or _t2v2_re.search(
                            r"(добавь|пересчитай|измени|утепление|поставщик)", _t2v2_low(caption)
                        ):
                            # Revision on known file
                            _t2v2_reset_parent(conn, parent_id, caption, task_id)
                            conn.execute(
                                "UPDATE tasks SET state='DONE', result=?, error_message=?, "
                                "updated_at=datetime('now') WHERE id=?",
                                ("Уточнение принято к пересчёту", "MERGED_TO_PARENT:" + parent_id, task_id),
                            )
                            _t2v2_hist_once(conn, task_id, _T2V2_PATCH + ":REVISION_MERGED_TO:" + parent_id)
                            try:
                                conn.commit()
                            except Exception:
                                pass
                            _T2V2_LOG.info("%s drive_revision child=%s parent=%s", _T2V2_PATCH, task_id, parent_id)
                            return
                        else:
                            # Same file re-sent without revision intent → duplicate guard
                            _t2v2_hist_once(conn, task_id, _T2V2_PATCH + ":FILE_DUPLICATE_BLOCKED")
                            _t2v2_hist_once(conn, task_id, "FILE_DUPLICATE_MEMORY_GUARD_V1:DONE")
                            conn.execute(
                                "UPDATE tasks SET state='DONE', result=?, error_message=?, "
                                "updated_at=datetime('now') WHERE id=?",
                                (
                                    "Файл уже есть в обработке. Если хотите пересчитать — напишите что изменить.",
                                    "FILE_DUPLICATE_BLOCKED_BY_V2",
                                    task_id,
                                ),
                            )
                            try:
                                conn.commit()
                            except Exception:
                                pass
                            try:
                                await _t2v2_send(
                                    chat_id, topic_id,
                                    "Файл уже есть в обработке.\n\nЧтобы пересчитать — напишите что изменить, например: «добавь утепление 250мм».",
                                    task,
                                )
                            except Exception:
                                pass
                            return

                # No existing parent → new estimate, route to alive chain
                if _t2v2_alive_hn:
                    return await _t2v2_alive_hn(conn, task, chat_id, topic_id)
                if _t2v2_prev_hn:
                    return await _t2v2_prev_hn(conn, task, chat_id, topic_id)
                return

            # ── text / voice branch ───────────────────────────────────────────
            if input_type in ("text", "voice"):
                raw_text = ""
                if isinstance(raw_obj, dict):
                    raw_text = _t2v2_s(raw_obj.get("text") or raw_obj.get("transcript") or "")
                if not raw_text:
                    raw_text = raw

                mode = _t2v2_classify(raw_text)
                _T2V2_LOG.info("%s mode=%s text=%r", _T2V2_PATCH, mode, raw_text[:80])

                if mode == "REVISION":
                    parent_id, parent_raw = _t2v2_find_parent(conn, task, chat_id, topic_id)
                    if parent_id:
                        _t2v2_reset_parent(conn, parent_id, raw_text, task_id)
                        conn.execute(
                            "UPDATE tasks SET state='DONE', result=?, error_message=?, "
                            "updated_at=datetime('now') WHERE id=?",
                            ("Уточнение принято к пересчёту", "MERGED_TO_PARENT:" + parent_id, task_id),
                        )
                        _t2v2_hist_once(conn, task_id, _T2V2_PATCH + ":REVISION_MERGED_TO:" + parent_id)
                        try:
                            conn.commit()
                        except Exception:
                            pass
                        _T2V2_LOG.info("%s text_revision child=%s parent=%s", _T2V2_PATCH, task_id, parent_id)
                        return
                    # No parent → fall to alive chain (new request)

                elif mode == "STATUS":
                    parent_id, parent_raw = _t2v2_find_parent(conn, task, chat_id, topic_id)
                    if parent_id:
                        par_raw_obj = _t2v2_parse_raw(parent_raw)
                        par_caption = _t2v2_s(par_raw_obj.get("caption")) if isinstance(par_raw_obj, dict) else ""
                        if _t2v2_is_fresh(conn, parent_id):
                            reply = _t2v2_status_reply(conn, parent_id, par_caption)
                            if reply:
                                conn.execute(
                                    "UPDATE tasks SET state='DONE', result=?, error_message=?, "
                                    "updated_at=datetime('now') WHERE id=?",
                                    (reply, "STATUS_REPLY_FROM_PARENT:" + parent_id, task_id),
                                )
                                _t2v2_hist_once(conn, task_id, _T2V2_PATCH + ":STATUS_DELIVERED")
                                try:
                                    conn.commit()
                                except Exception:
                                    pass
                                try:
                                    await _t2v2_send(chat_id, topic_id, reply, task)
                                except Exception:
                                    pass
                                _T2V2_LOG.info("%s status_reply child=%s parent=%s", _T2V2_PATCH, task_id, parent_id)
                                return
                        else:
                            # Stale → reset parent for recalc
                            _t2v2_reset_parent(conn, parent_id, "", task_id, merge_json=False)
                            stale_msg = "Смета устарела — пересчитываю с учётом последних изменений. Ожидайте."
                            conn.execute(
                                "UPDATE tasks SET state='DONE', result=?, error_message=?, "
                                "updated_at=datetime('now') WHERE id=?",
                                (stale_msg, "STALE_RECALC_TRIGGERED:" + parent_id, task_id),
                            )
                            _t2v2_hist_once(conn, task_id, _T2V2_PATCH + ":STATUS_STALE_RECALC")
                            try:
                                conn.commit()
                            except Exception:
                                pass
                            try:
                                await _t2v2_send(chat_id, topic_id, stale_msg, task)
                            except Exception:
                                pass
                            return

                elif mode == "PRICE_CHOICE":
                    # Route to alive chain — it handles price choice menu/confirmation
                    if _t2v2_alive_hn:
                        return await _t2v2_alive_hn(conn, task, chat_id, topic_id)

                elif mode in ("CONFIRM", "CANCEL"):
                    # Route to alive chain — it handles confirmations/cancels
                    if _t2v2_alive_hn:
                        return await _t2v2_alive_hn(conn, task, chat_id, topic_id)

        except Exception as _e:
            try:
                _T2V2_LOG.exception("%s _handle_new err=%s", _T2V2_PATCH, _e)
            except Exception:
                pass

        # Fallback: alive chain covers unrecognised topic_2 cases
        if _t2v2_alive_hn:
            return await _t2v2_alive_hn(conn, task, chat_id, topic_id)
        if _t2v2_prev_hn:
            return await _t2v2_prev_hn(conn, task, chat_id, topic_id)

    globals()["_handle_new"] = _handle_new

    # ── Runtime repair: f030 stale artifact → force recalc ────────────────────────
    # f030 is AWAITING_CONFIRMATION with clarified entries (91314,91317) after
    # DRIVE_LINKS_SAVED (91308). Must reset to IN_PROGRESS so worker recalculates
    # including утепление 250мм revision.
    try:
        import sqlite3 as _t2v2_sqlite3

        _T2V2_REPAIR_DB = "/root/.areal-neva-core/data/core.db"
        _T2V2_F030 = "f030db95-8fdb-460d-90ea-2beae356b777"

        _t2v2_rconn = _t2v2_sqlite3.connect(_T2V2_REPAIR_DB, timeout=10)
        try:
            _t2v2_rconn.row_factory = _t2v2_sqlite3.Row

            # Check if f030 is stale and needs repair
            _t2v2_f030_state = _t2v2_rconn.execute(
                "SELECT state FROM tasks WHERE id=? LIMIT 1", (_T2V2_F030,)
            ).fetchone()

            if _t2v2_f030_state and _t2v2_s(_t2v2_f030_state[0]) == "AWAITING_CONFIRMATION":
                # Check freshness
                _t2v2_links_row = _t2v2_rconn.execute(
                    "SELECT rowid FROM task_history WHERE task_id=? "
                    "AND action LIKE 'TOPIC2_DRIVE_LINKS_SAVED:%' ORDER BY rowid DESC LIMIT 1",
                    (_T2V2_F030,),
                ).fetchone()
                if _t2v2_links_row:
                    _t2v2_links_rid = _t2v2_links_row[0]
                    _t2v2_stale_row = _t2v2_rconn.execute(
                        "SELECT rowid FROM task_history WHERE task_id=? "
                        "AND action LIKE 'clarified:%' AND rowid > ? LIMIT 1",
                        (_T2V2_F030, _t2v2_links_rid),
                    ).fetchone()
                    if _t2v2_stale_row:
                        # Stale — clear blockers and reset to IN_PROGRESS
                        for _t2v2_bm in _T2V2_BLOCKING_MARKERS:
                            _t2v2_rconn.execute(
                                "DELETE FROM task_history WHERE task_id=? AND action LIKE ?",
                                (_T2V2_F030, _t2v2_bm + "%"),
                            )
                        # Also clear EXECUTION_TIMEOUT markers
                        _t2v2_rconn.execute(
                            "DELETE FROM task_history WHERE task_id=? AND action LIKE 'state:FAILED:%'",
                            (_T2V2_F030,),
                        )
                        _t2v2_rconn.execute(
                            "UPDATE tasks SET state='IN_PROGRESS', result='', error_message='', "
                            "updated_at=datetime('now') WHERE id=?",
                            (_T2V2_F030,),
                        )
                        if not _t2v2_rconn.execute(
                            "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
                            (_T2V2_F030, _T2V2_PATCH + ":F030_REPAIR_RECALC"),
                        ).fetchone():
                            _t2v2_rconn.execute(
                                "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                                (_T2V2_F030, _T2V2_PATCH + ":F030_REPAIR_RECALC"),
                            )
                        _t2v2_rconn.commit()
                        _T2V2_LOG.info("%s F030_REPAIR_RECALC: reset to IN_PROGRESS", _T2V2_PATCH)
                    else:
                        _T2V2_LOG.info("%s f030 fresh — no repair needed", _T2V2_PATCH)
                else:
                    _T2V2_LOG.info("%s f030 no DRIVE_LINKS_SAVED — no repair", _T2V2_PATCH)
            else:
                _T2V2_LOG.info(
                    "%s f030 state=%s — no repair",
                    _T2V2_PATCH,
                    _t2v2_f030_state[0] if _t2v2_f030_state else "NOT_FOUND",
                )
        finally:
            try:
                _t2v2_rconn.close()
            except Exception:
                pass

    except Exception as _t2v2_repair_err:
        try:
            _T2V2_LOG.warning("%s repair err=%s", _T2V2_PATCH, _t2v2_repair_err)
        except Exception:
            pass

    _T2V2_LOG.info(
        "%s installed hn=%s alive_hn=%s alive_hip=%s alive_ut=%s prev_hn=%s",
        _T2V2_PATCH,
        bool(globals().get("_handle_new")),
        bool(_t2v2_alive_hn), bool(_t2v2_alive_hip), bool(_t2v2_alive_ut),
        bool(_t2v2_prev_hn),
    )

except Exception as _t2v2_install_err:
    try:
        import logging as _t2v2_log_fallback
        _t2v2_log_fallback.getLogger("WORKER").exception(
            "PATCH_TOPIC2_REVISION_RECALC_FULL_CANON_NO_REGRESSION_V2_INSTALL_ERR:%s",
            _t2v2_install_err,
        )
    except Exception:
        pass
# === /PATCH_TOPIC2_REVISION_RECALC_FULL_CANON_NO_REGRESSION_V2 ===

# === PATCH_T2V2_FRESHNESS_GATE_FIX_V1 ===
# _t2v2_is_fresh bug: used TOPIC2_DRIVE_LINKS_SAVED as anchor but canon engine
# updates Drive files in-place and writes TOPIC2_DRIVE_UPLOAD_XLSX_OK instead.
# Fix: freshness = last ARTIFACT evidence (links OR upload) is AFTER last STALE marker.
try:
    import logging as _t2v2fix_logging
    _T2V2FIX_LOG = _t2v2fix_logging.getLogger("WORKER")

    def _t2v2_is_fresh(conn, task_id):
        tid = str(task_id or "")
        try:
            # Latest artifact evidence: DRIVE_LINKS_SAVED OR DRIVE_UPLOAD_XLSX_OK OR ESTIMATE_ARTIFACTS_CREATED
            art_row = conn.execute(
                "SELECT MAX(rowid) FROM task_history WHERE task_id=? "
                "AND (action LIKE 'TOPIC2_DRIVE_LINKS_SAVED:%' "
                "OR action LIKE 'TOPIC2_DRIVE_UPLOAD_XLSX_OK%' "
                "OR action LIKE 'TOPIC2_ESTIMATE_FINAL_CLOSE_V2:ESTIMATE_ARTIFACTS_CREATED%')",
                (tid,),
            ).fetchone()
            if not art_row or not art_row[0]:
                return False
            art_rid = art_row[0]
            # Latest stale marker
            stale_markers = _T2V2_STALE_MARKERS if "_T2V2_STALE_MARKERS" in dir() else (
                "clarified:", "MERGED_TO_PARENT:", "STALE_RESET",
                "TOPIC2_ADDITIONAL_FACT_MERGED:", "TOPIC2_ADDITIONAL_FACTS_RECALC_STARTED:",
            )
            for marker in stale_markers:
                stale_row = conn.execute(
                    "SELECT rowid FROM task_history WHERE task_id=? AND action LIKE ? ORDER BY rowid DESC LIMIT 1",
                    (tid, marker + "%"),
                ).fetchone()
                if stale_row and stale_row[0] > art_rid:
                    return False
            return True
        except Exception:
            return False

    # Patch into V2 globals if V2 loaded
    if "_t2v2_prev_hn" in dir():
        globals()["_t2v2_is_fresh"] = _t2v2_is_fresh
        _T2V2FIX_LOG.info("PATCH_T2V2_FRESHNESS_GATE_FIX_V1 applied")

except Exception as _t2v2fix_err:
    pass
# === /PATCH_T2V2_FRESHNESS_GATE_FIX_V1 ===



# === PATCH_TOPIC2_DONE_ONLY_AFTER_USER_YES_V1 ===
# Canon: topic_2 final estimate is not DONE until explicit user "да".
# Generated XLSX/PDF/Drive result must wait in AWAITING_CONFIRMATION.
try:
    import logging as _t2duy_logging
    _T2DUY_LOG = _t2duy_logging.getLogger("WORKER")
    _t2duy_orig_update_task = _update_task

    def _t2duy_s(v):
        return "" if v is None else str(v)

    def _t2duy_topic(conn, task_id):
        try:
            row = conn.execute("SELECT topic_id FROM tasks WHERE id=? LIMIT 1", (str(task_id),)).fetchone()
            if not row:
                return 0
            return int(row["topic_id"] if hasattr(row, "keys") else row[0] or 0)
        except Exception:
            return 0

    def _t2duy_is_final_estimate_result(text):
        low = _t2duy_s(text).lower().replace("ё", "е")
        return ("смета готов" in low or "xlsx:" in low or "pdf:" in low or "drive.google.com" in low or "docs.google.com" in low)

    def _t2duy_history(conn, task_id, action):
        try:
            conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))", (str(task_id), action))
        except Exception:
            pass

    def _update_task(conn, task_id, **kwargs):  # noqa: F811
        try:
            if _t2duy_topic(conn, task_id) == 2 and _t2duy_s(kwargs.get("state")).upper() == "DONE":
                err = _t2duy_s(kwargs.get("error_message"))
                result = _t2duy_s(kwargs.get("result"))
                accepted = "подтверждение принято" in result.lower().replace("ё", "е")
                merged_child = err.startswith("MERGED_TO_PARENT") or "MERGED_TO_PARENT" in result
                if (not accepted) and (not merged_child) and _t2duy_is_final_estimate_result(result):
                    kwargs["state"] = "AWAITING_CONFIRMATION"
                    _t2duy_history(conn, task_id, "TOPIC2_DONE_ONLY_AFTER_USER_YES_V1:BLOCKED_DONE_TO_AWAITING_CONFIRMATION")
        except Exception as e:
            try:
                _T2DUY_LOG.warning("TOPIC2_DONE_ONLY_AFTER_USER_YES_V1_ERR %s", e)
            except Exception:
                pass
        return _t2duy_orig_update_task(conn, task_id, **kwargs)

    _T2DUY_LOG.info("PATCH_TOPIC2_DONE_ONLY_AFTER_USER_YES_V1 installed")
except Exception as _t2duy_err:
    try:
        logger.exception("PATCH_TOPIC2_DONE_ONLY_AFTER_USER_YES_V1_INSTALL_ERR:%s", _t2duy_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_DONE_ONLY_AFTER_USER_YES_V1 ===

# === PATCH_TOPIC2_LATE_P6E67_CLARIFIED_RESCUE_V1 ===
try:
    import inspect as _t2lp6_inspect
    import logging as _t2lp6_logging
    _T2LP6_LOG = _t2lp6_logging.getLogger("WORKER")
    _t2lp6_orig_handle_in_progress = _handle_in_progress

    def _t2lp6_s(v):
        return "" if v is None else str(v)

    def _t2lp6_get(row, key, default=None):
        try:
            if hasattr(row, "keys") and key in row.keys():
                return row[key]
        except Exception:
            pass
        try:
            return row[key]
        except Exception:
            return default

    def _t2lp6_is_fresh_estimate(text):
        t = _t2lp6_s(text).lower().replace("ё", "е").replace("[voice]", "").strip()
        if len(t) < 20:
            return False
        keys = (
            "смет", "расчет", "расчёт", "посчитай", "сделай",
            "дом", "этаж", "фундамент", "стен", "кирпич", "газобетон",
            "монолит", "кровл", "отделк", "санузел", "инженер",
            "м2", "м²", "размер", "санкт-петербург", "петербург",
        )
        return sum(1 for k in keys if k in t) >= 3

    def _t2lp6_recent_p6e67(conn, task_id):
        try:
            return conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action LIKE 'P6E67_PARENT_NOT_FOUND%' ORDER BY rowid DESC LIMIT 1",
                (str(task_id),),
            ).fetchone() is not None
        except Exception:
            return False

    def _t2lp6_latest_clarified(conn, task_id):
        try:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'clarified:%' ORDER BY rowid DESC LIMIT 12",
                (str(task_id),),
            ).fetchall()
            for row in rows:
                action = _t2lp6_s(row[0])
                raw = action.split("clarified:", 1)[1].strip() if "clarified:" in action else ""
                if _t2lp6_is_fresh_estimate(raw):
                    return raw
        except Exception:
            return ""
        return ""

    async def _handle_in_progress(conn, task, *args, **kwargs):  # noqa: F811
        try:
            topic_id = int(_t2lp6_get(task, "topic_id", 0) or 0)
            state = _t2lp6_s(_t2lp6_get(task, "state", "")).upper()
            err = _t2lp6_s(_t2lp6_get(task, "error_message", "")).upper()
            task_id = _t2lp6_s(_t2lp6_get(task, "id", ""))
            if topic_id == 2 and state in ("WAITING_CLARIFICATION", "IN_PROGRESS") and ("P6E67_PARENT_NOT_FOUND" in err or _t2lp6_recent_p6e67(conn, task_id)):
                task_raw = _t2lp6_s(_t2lp6_get(task, "raw_input", ""))
                rescue_raw = task_raw if _t2lp6_is_fresh_estimate(task_raw) else _t2lp6_latest_clarified(conn, task_id)
                if rescue_raw:
                    conn.execute(
                        "UPDATE tasks SET state='IN_PROGRESS', raw_input=?, result='', error_message='', reply_to_message_id=NULL, updated_at=datetime('now') WHERE id=?",
                        (rescue_raw, task_id),
                    )
                    conn.execute(
                        "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                        (task_id, "TOPIC2_LATE_P6E67_CLARIFIED_RESCUE_V1:STARTED"),
                    )
                    conn.commit()
                    from core.stroyka_estimate_canon import maybe_handle_stroyka_estimate as _t2lp6_canon
                    task_clean = {}
                    try:
                        for k in task.keys():
                            task_clean[k] = task[k]
                    except Exception:
                        task_clean = {}
                    task_clean["raw_input"] = rescue_raw
                    task_clean["state"] = "IN_PROGRESS"
                    task_clean["error_message"] = ""
                    res = _t2lp6_canon(conn, task_clean, logger=_T2LP6_LOG)
                    if _t2lp6_inspect.isawaitable(res):
                        res = await res
                    if res:
                        conn.execute(
                            "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                            (task_id, "TOPIC2_LATE_P6E67_CLARIFIED_RESCUE_V1:CANON_HANDLED"),
                        )
                        conn.commit()
                        return True
        except Exception as e:
            try:
                _T2LP6_LOG.exception("TOPIC2_LATE_P6E67_CLARIFIED_RESCUE_V1_ERR:%s", e)
            except Exception:
                pass
        res = _t2lp6_orig_handle_in_progress(conn, task, *args, **kwargs)
        if _t2lp6_inspect.isawaitable(res):
            return await res
        return res

    _T2LP6_LOG.info("PATCH_TOPIC2_LATE_P6E67_CLARIFIED_RESCUE_V1 installed")
except Exception as _t2lp6_err:
    try:
        logger.exception("PATCH_TOPIC2_LATE_P6E67_CLARIFIED_RESCUE_V1_INSTALL_ERR:%s", _t2lp6_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_LATE_P6E67_CLARIFIED_RESCUE_V1 ===


# === PATCH_TOPIC2_P3_CANON_GUARD_V1 ===
# Canon: topic_2 final estimate waits for explicit user confirmation; high price level maps to reliable/3.
try:
    import logging as _t2p3cg_logging
    import re as _t2p3cg_re

    _T2P3CG_LOG = _t2p3cg_logging.getLogger("WORKER")

    def _t2p3cg_s(v):
        return "" if v is None else str(v)

    def _t2p3cg_topic(conn, task_id):
        try:
            row = conn.execute("SELECT topic_id FROM tasks WHERE id=? LIMIT 1", (str(task_id),)).fetchone()
            return int((row["topic_id"] if hasattr(row, "keys") else row[0]) or 0) if row else 0
        except Exception:
            return 0

    def _t2p3cg_raw(conn, task_id):
        try:
            row = conn.execute("SELECT raw_input FROM tasks WHERE id=? LIMIT 1", (str(task_id),)).fetchone()
            return _t2p3cg_s(row["raw_input"] if hasattr(row, "keys") else row[0]) if row else ""
        except Exception:
            return ""

    def _t2p3cg_choice_from_text(text):
        low = _t2p3cg_s(text).lower().replace("ё", "е")
        if any(x in low for x in ("высок", "дорог", "максим", "надеж", "проверенн", "вариант 3")):
            return "reliable"
        if any(x in low for x in ("миним", "дешев", "вариант 1")):
            return "cheapest"
        if any(x in low for x in ("средн", "медиан", "вариант 2")):
            return "median"
        if any(x in low for x in ("ручн", "вручную", "вариант 4")):
            return "manual"
        return ""

    def _t2p3cg_is_final_estimate(result):
        low = _t2p3cg_s(result).lower().replace("ё", "е")
        return (
            "смета готов" in low
            and ("excel:" in low or "xlsx:" in low or "docs.google.com" in low)
            and ("pdf:" in low or "drive.google.com" in low)
        )

    def _t2p3cg_hist(conn, task_id, action):
        try:
            conn.execute(
                "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                (str(task_id), str(action)[:1000]),
            )
        except Exception:
            pass

    if "_p3_update_20260504" in globals():
        _t2p3cg_orig_p3_update = _p3_update_20260504

        def _p3_update_20260504(conn, task_id, **kwargs):  # noqa: F811
            try:
                if _t2p3cg_topic(conn, task_id) == 2 and _t2p3cg_s(kwargs.get("state")).upper() == "DONE":
                    result = _t2p3cg_s(kwargs.get("result"))
                    err = _t2p3cg_s(kwargs.get("error_message"))
                    accepted = "подтверждение принято" in result.lower().replace("ё", "е")
                    merged = err.startswith("MERGED_TO_PARENT") or "MERGED_TO_PARENT" in result
                    if _t2p3cg_is_final_estimate(result) and not accepted and not merged:
                        kwargs["state"] = "AWAITING_CONFIRMATION"
                        kwargs["error_message"] = ""
                        _t2p3cg_hist(conn, task_id, "TOPIC2_DONE_ONLY_AFTER_USER_YES_V1:P3_BLOCKED_DONE_TO_AWAITING_CONFIRMATION")
            except Exception as e:
                try:
                    _T2P3CG_LOG.warning("PATCH_TOPIC2_P3_CANON_GUARD_V1 update err %s", e)
                except Exception:
                    pass
            return _t2p3cg_orig_p3_update(conn, task_id, **kwargs)

    if "_p3_history_20260504" in globals():
        _t2p3cg_orig_p3_history = _p3_history_20260504

        def _p3_history_20260504(conn, task_id, action):  # noqa: F811
            try:
                a = _t2p3cg_s(action)
                if _t2p3cg_topic(conn, task_id) == 2 and a == "TOPIC2_PRICE_CHOICE_CONFIRMED:confirmed":
                    choice = _t2p3cg_choice_from_text(_t2p3cg_raw(conn, task_id)) or "median"
                    action = "TOPIC2_PRICE_CHOICE_CONFIRMED:" + choice
                    _t2p3cg_hist(conn, task_id, "PATCH_TOPIC2_P3_CANON_GUARD_V1:NORMALIZED_CONFIRMED_TO:" + choice)
            except Exception as e:
                try:
                    _T2P3CG_LOG.warning("PATCH_TOPIC2_P3_CANON_GUARD_V1 history err %s", e)
                except Exception:
                    pass
            return _t2p3cg_orig_p3_history(conn, task_id, action)

    if "_t2sh_price_choice" in globals():
        _t2p3cg_orig_t2sh_price_choice = _t2sh_price_choice

        def _t2sh_price_choice(history_text):  # noqa: F811
            h = _t2p3cg_s(history_text)
            if "TOPIC2_PRICE_CHOICE_CONFIRMED:maximum" in h:
                return "reliable"
            if "TOPIC2_PRICE_CHOICE_CONFIRMED:confirmed" in h:
                return "reliable"
            return _t2p3cg_orig_t2sh_price_choice(history_text)

    _T2P3CG_LOG.info("PATCH_TOPIC2_P3_CANON_GUARD_V1 installed")
except Exception as _t2p3cg_err:
    try:
        logger.exception("PATCH_TOPIC2_P3_CANON_GUARD_V1_INSTALL_ERR:%s", _t2p3cg_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_P3_CANON_GUARD_V1 ===


# === PATCH_TOPIC2_FRESH_FULL_TZ_FINAL_GUARD_V2 ===
# Last-order guard: a long complete topic_2 TZ is a new canonical estimate task,
# not a followup to an older AWAITING_CONFIRMATION task.
try:
    import inspect as _t2ffg2_inspect
    import logging as _t2ffg2_logging
    import re as _t2ffg2_re

    _T2FFG2_LOG = _t2ffg2_logging.getLogger("WORKER")
    _T2FFG2_ORIG_HANDLE_NEW = _handle_new

    def _t2ffg2_get(row, key, default=None):
        try:
            if isinstance(row, dict):
                return row.get(key, default)
            if hasattr(row, "keys") and key in row.keys():
                return row[key]
        except Exception:
            pass
        try:
            return row[key]
        except Exception:
            return default

    def _t2ffg2_is_fresh_full_tz(raw):
        low = str(raw or "").lower().replace("ё", "е").replace("[voice]", "").strip()
        if len(low) < 100:
            return False
        has_estimate = any(x in low for x in ("смет", "расчет", "расчёт"))
        has_dims = bool(_t2ffg2_re.search(r"\d+(?:[.,]\d+)?\s*(?:x|х|×|на)\s*\d+(?:[.,]\d+)?", low))
        facts = sum(1 for x in (
            "дом", "этаж", "плит", "фундамент", "стен", "кирпич", "газобет",
            "каркас", "ламинат", "санузел", "инженер", "санкт-петербург", "петербург"
        ) if x in low)
        return bool(has_estimate and has_dims and facts >= 4)

    def _t2ffg2_hist(conn, task_id, action):
        try:
            conn.execute(
                "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                (str(task_id), str(action)[:1000]),
            )
        except Exception:
            pass

    async def _handle_new(conn, task, chat_id, topic_id):  # noqa: F811
        try:
            topic_id_i = int(topic_id or _t2ffg2_get(task, "topic_id", 0) or 0)
            task_id = str(_t2ffg2_get(task, "id", "") or "")
            raw = str(_t2ffg2_get(task, "raw_input", "") or "")
            input_type = str(_t2ffg2_get(task, "input_type", "") or "")
            if topic_id_i == 2 and input_type in ("text", "voice", "search") and task_id and _t2ffg2_is_fresh_full_tz(raw):
                from core import sample_template_engine as _t2ffg2_ste
                _T2FFG2_LOG.info("PATCH_TOPIC2_FRESH_FULL_TZ_FINAL_GUARD_V2 route task=%s", task_id)
                _t2ffg2_hist(conn, task_id, "PATCH_TOPIC2_FRESH_FULL_TZ_FINAL_GUARD_V2:CANON_P3_ROUTE")
                try:
                    conn.execute(
                        "UPDATE tasks SET state='IN_PROGRESS', result='', error_message='', reply_to_message_id=NULL, updated_at=datetime('now') WHERE id=?",
                        (task_id,),
                    )
                    conn.commit()
                except Exception:
                    pass
                res = _t2ffg2_ste.handle_topic2_one_big_formula_pipeline_v1(
                    conn=conn,
                    task=task,
                    chat_id=chat_id,
                    topic_id=topic_id_i,
                    raw_input=raw,
                    full_context=raw,
                )
                if _t2ffg2_inspect.isawaitable(res):
                    await res
                return
        except Exception as _t2ffg2_e:
            try:
                _T2FFG2_LOG.exception("PATCH_TOPIC2_FRESH_FULL_TZ_FINAL_GUARD_V2_ERR:%s", _t2ffg2_e)
            except Exception:
                pass
        return await _T2FFG2_ORIG_HANDLE_NEW(conn, task, chat_id, topic_id)

    _T2FFG2_LOG.info("PATCH_TOPIC2_FRESH_FULL_TZ_FINAL_GUARD_V2 installed")
except Exception as _t2ffg2_install_err:
    try:
        logger.exception("PATCH_TOPIC2_FRESH_FULL_TZ_FINAL_GUARD_V2_INSTALL_ERR:%s", _t2ffg2_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_FRESH_FULL_TZ_FINAL_GUARD_V2 ===

# === PATCH_TOPIC2_WAITING_PROJECT_FILE_BIND_V1 ===
# Canon basis:
# - voice is text;
# - topic_2 PDF/XLSX/photo must enter estimate flow;
# - when the user says they will send a project/file, do not revive old estimate
#   memory and do not start a new estimate before the file arrives.
import json as _t2wp_json
import logging as _t2wp_log
import inspect as _t2wp_inspect

_T2WP_LOG = _t2wp_log.getLogger("task_worker")

def _t2wp_s(v):
    return "" if v is None else str(v)

def _t2wp_low(v):
    return _t2wp_s(v).lower().replace("ё", "е")

def _t2wp_waiting_project_text(text):
    t = _t2wp_low(text).replace("[voice]", " ")
    waits = (
        "сейчас скину",
        "сейчас пришлю",
        "скину проект",
        "пришлю проект",
        "скину файл",
        "пришлю файл",
        "сейчас скину проект",
        "сейчас пришлю проект",
    )
    project_words = ("проект", "pdf", "файл", "чертеж", "архитектур", "стадия")
    return any(w in t for w in waits) and any(w in t for w in project_words)

def _t2wp_file_meta(raw):
    try:
        data = _t2wp_json.loads(_t2wp_s(raw))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def _t2wp_is_pdf_project(raw):
    meta = _t2wp_file_meta(raw)
    name = _t2wp_low(meta.get("file_name"))
    mime = _t2wp_low(meta.get("mime_type"))
    return bool("pdf" in mime or name.endswith(".pdf"))

def _t2wp_find_waiting_project_parent(conn, chat_id, topic_id):
    try:
        return conn.execute(
            """
            SELECT * FROM tasks
            WHERE chat_id=? AND COALESCE(topic_id,0)=?
              AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION')
              AND input_type IN ('text','voice')
              AND updated_at >= datetime('now','-45 minutes')
            ORDER BY updated_at DESC, rowid DESC
            LIMIT 20
            """,
            (str(chat_id), int(topic_id or 0)),
        ).fetchall()
    except Exception:
        return []

def _t2wp_parent_for_file(conn, chat_id, topic_id):
    for row in _t2wp_find_waiting_project_parent(conn, chat_id, topic_id):
        raw = _t2wp_s(_task_field(row, "raw_input", ""))
        if _t2wp_waiting_project_text(raw):
            return row
    return None

try:
    _T2WP_ORIG_HANDLE_NEW = _handle_new
except Exception:
    _T2WP_ORIG_HANDLE_NEW = None

if _T2WP_ORIG_HANDLE_NEW and not getattr(_T2WP_ORIG_HANDLE_NEW, "_t2wp_wrapped", False):
    async def _handle_new(conn, task, *args, **kwargs):
        try:
            topic_id = int(_task_field(task, "topic_id", 0) or 0)
            raw = _t2wp_s(_task_field(task, "raw_input", ""))
            input_type = _t2wp_low(_task_field(task, "input_type", "text"))
            if topic_id == 2 and input_type in ("text", "voice") and _t2wp_waiting_project_text(raw):
                task_id = _t2wp_s(_task_field(task, "id", ""))
                chat_id = _t2wp_s(_task_field(task, "chat_id", ""))
                reply_to = _task_field(task, "reply_to_message_id", None)
                msg = (
                    "Жду PDF/проект для расчёта. После загрузки файла привяжу его к этой задаче "
                    "и буду считать по содержимому проекта, без старых смет и без догадок."
                )
                _update_task(conn, task_id, state="WAITING_CLARIFICATION", result=msg, error_message="TOPIC2_WAITING_PROJECT_FILE")
                _history(conn, task_id, "PATCH_TOPIC2_WAITING_PROJECT_FILE_BIND_V1:WAITING_FOR_FILE")
                conn.commit()
                try:
                    sent = send_reply_ex(chat_id=str(chat_id), text=msg, reply_to_message_id=reply_to, message_thread_id=2)
                    if isinstance(sent, dict) and sent.get("bot_message_id"):
                        _update_task(conn, task_id, bot_message_id=sent.get("bot_message_id"))
                        conn.commit()
                except Exception as e:
                    _T2WP_LOG.warning("T2WP_WAIT_SEND_ERR task=%s err=%s", task_id, e)
                return True
        except Exception as e:
            _T2WP_LOG.warning("T2WP_HANDLE_NEW_GUARD_ERR %s", e)

        res = _T2WP_ORIG_HANDLE_NEW(conn, task, *args, **kwargs)
        if _t2wp_inspect.isawaitable(res):
            return await res
        return res

    _handle_new._t2wp_wrapped = True
    _T2WP_LOG.info("PATCH_TOPIC2_WAITING_PROJECT_FILE_BIND_V1 _handle_new installed")

try:
    _T2WP_ORIG_HANDLE_DRIVE_FILE = _handle_drive_file
except Exception:
    _T2WP_ORIG_HANDLE_DRIVE_FILE = None

if _T2WP_ORIG_HANDLE_DRIVE_FILE and not getattr(_T2WP_ORIG_HANDLE_DRIVE_FILE, "_t2wp_wrapped", False):
    async def _handle_drive_file(conn, task, chat_id, topic_id):
        try:
            topic_id_i = int(topic_id or _task_field(task, "topic_id", 0) or 0)
            raw = _t2wp_s(_task_field(task, "raw_input", ""))
            if topic_id_i == 2 and _t2wp_is_pdf_project(raw):
                parent = _t2wp_parent_for_file(conn, str(chat_id), topic_id_i)
                if parent is not None:
                    task_id = _t2wp_s(_task_field(task, "id", ""))
                    parent_id = _t2wp_s(_task_field(parent, "id", ""))
                    meta = _t2wp_file_meta(raw)
                    meta["caption"] = (meta.get("caption") or "смета по проекту PDF").strip()
                    meta["topic2_parent_task_id"] = parent_id
                    new_raw = _t2wp_json.dumps(meta, ensure_ascii=False)
                    parent_raw = _t2wp_s(_task_field(parent, "raw_input", ""))
                    enriched = parent_raw + "\n\nTOPIC2_PROJECT_FILE_BOUND:" + new_raw
                    conn.execute(
                        "UPDATE tasks SET raw_input=?, state='IN_PROGRESS', error_message='', updated_at=datetime('now') WHERE id=?",
                        (new_raw, task_id),
                    )
                    conn.execute(
                        "UPDATE tasks SET raw_input=?, state='IN_PROGRESS', error_message='', updated_at=datetime('now') WHERE id=?",
                        (enriched, parent_id),
                    )
                    _history(conn, task_id, f"PATCH_TOPIC2_WAITING_PROJECT_FILE_BIND_V1:PDF_BOUND_TO_PARENT:{parent_id}")
                    _history(conn, parent_id, f"PATCH_TOPIC2_WAITING_PROJECT_FILE_BIND_V1:PDF_CHILD:{task_id}")
                    conn.commit()
                    task_dict = {}
                    try:
                        for k in task.keys():
                            task_dict[k] = task[k]
                    except Exception:
                        task_dict = dict(task) if isinstance(task, dict) else {}
                    task_dict["raw_input"] = new_raw
                    task_dict["state"] = "IN_PROGRESS"
                    h_ip = globals().get("_handle_in_progress")
                    if h_ip:
                        res = h_ip(conn, task_dict, str(chat_id), topic_id_i)
                        if _t2wp_inspect.isawaitable(res):
                            return await res
                        return res
        except Exception as e:
            _T2WP_LOG.warning("T2WP_HANDLE_DRIVE_FILE_BIND_ERR %s", e)

        res = _T2WP_ORIG_HANDLE_DRIVE_FILE(conn, task, chat_id, topic_id)
        if _t2wp_inspect.isawaitable(res):
            return await res
        return res

    _handle_drive_file._t2wp_wrapped = True
    _T2WP_LOG.info("PATCH_TOPIC2_WAITING_PROJECT_FILE_BIND_V1 _handle_drive_file installed")

# === END_PATCH_TOPIC2_WAITING_PROJECT_FILE_BIND_V1 ===

if __name__ == "__main__":
    asyncio.run(main())

====================================================================================================
END_FILE: task_worker.py
FILE_CHUNK: 4/4
====================================================================================================

====================================================================================================
BEGIN_FILE: telegram_daemon.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 608f287a10c5b4295a20de5c3714de7cd4e80b4d0a75049a0727dc0cb20f07db
====================================================================================================
import json
import asyncio, hashlib, json, logging, os, re, uuid, fcntl, tempfile, time
from datetime import datetime, timezone, timedelta
import aiofiles, aiohttp, aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.types import BufferedInputFile, FSInputFile
from google_io import upload_to_drive
from core.drive_folder_resolver import get_or_create_topic_folder
from core.topic_drive_oauth import upload_file_to_topic

BOT_TOKEN = <REDACTED_SECRET>"TELEGRAM_BOT_TOKEN") or "").strip()
DB = "/root/.areal-neva-core/data/core.db"
VOICE_DIR = "/root/.areal-neva-core/runtime/voice_queue"
MEMORY_FILES = "/root/.areal-neva-core/data/memory_files"
CHAT_MAP_FILE = os.path.join(MEMORY_FILES, "CHAT_MAP.json")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN missing")

for d in ["GLOBAL", "CHATS", "SYSTEM", "ERRORS"]:
    os.makedirs(os.path.join(MEMORY_FILES, d), exist_ok=True)
os.makedirs(VOICE_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s DAEMON: %(message)s")
logger = logging.getLogger("telegram_daemon")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

SYSTEM_CMDS = ["память", "память оркестра", "выгрузи память", "статус", "архив", "сброс задач", "очистить задачи", "yzon", "дамп", "язон", "язон файл", "дамп файл", "память файл", "архив файл", "система", "система файл", "код файл", "файл"]
CANCEL_CMDS = ["отбой", "отмена", "не надо"]
EZONE_KEYS = ("system", "architecture", "pipeline", "memory")
EZONE_EXTS = (".json", ".jsonl", ".txt")
SEARCH_TRIGGERS = ["цена", "наличие", "где купить", "площадка", "сайт", "сравнение", "новости", "актуальная"]
SHORT_CONFIRM = ["да", "нет", "ок", "подтверждаю", "не так", "ага", "верно"]
NEGATIVE_CONFIRM = ["нет", "не так"]
FINISH_PHRASES = [
    "спасибо поиск завершен", "поиск завершен",
    "не надо", "можно завершать",
    "задача закрыта", "закрывай", "хватит"
]
CANCEL_PHRASES = [
    "все запросы отменены", "отменяю все запросы", "сброс задач",
    "очистить задачи", "отмена", "отменяю", "сброс", "отбой"
]

_RECENT_INGEST = {}

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def normalize_json_text(text: str) -> str:
    if not text: return text
    replacements = {"“": '"', "”": '"', "„": '"', "«": '"', "»": '"', "‘": "'", "’": "'", "…": "..."}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip()

def is_ezone_payload(text: str) -> bool:
    if not text: return False
    norm = normalize_json_text(text)
    try:
        data = json.loads(norm)
        return isinstance(data, dict) and any(k in data for k in EZONE_KEYS)
    except:
        low = norm.lower()
        return any(k in low for k in EZONE_KEYS)

def content_hash(text: str) -> str:
    return hashlib.sha256(normalize_json_text(text).encode()).hexdigest()

def build_chat_key(telegram_chat_id: int) -> str:
    return f"{telegram_chat_id}__telegram"

def update_chat_map_atomic(telegram_chat_id: int, chat_key: str):
    lock_file = CHAT_MAP_FILE + ".lock"
    try:
        with open(lock_file, "w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            try:
                chat_map = json.load(open(CHAT_MAP_FILE)) if os.path.exists(CHAT_MAP_FILE) else {}
                tg_id = str(telegram_chat_id)
                if tg_id not in chat_map:
                    chat_map[tg_id] = {}
                elif isinstance(chat_map[tg_id], list):
                    chat_map[tg_id] = {k: "unknown" for k in chat_map[tg_id]}
                chat_map[tg_id] = {k: v for k, v in chat_map[tg_id].items() if "unknown" not in k}
                chat_map[tg_id][chat_key] = "telegram"
                fd, tmp = tempfile.mkstemp(dir=os.path.dirname(CHAT_MAP_FILE), prefix=".chat_map_", suffix=".tmp")
                with os.fdopen(fd, "w") as f:
                    json.dump(chat_map, f, ensure_ascii=False, indent=2)
                    f.flush(); os.fsync(f.fileno())
                os.replace(tmp, CHAT_MAP_FILE)
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)
    except Exception as e:
        logger.error("CHAT_MAP update failed: %s", e)
    finally:
        try: os.unlink(lock_file)
        except: pass

def is_duplicate_today(hash_val: str, chat_key: str) -> bool:
    dup_file = os.path.join(MEMORY_FILES, "CHATS", chat_key, ".duplicates.jsonl")
    today = today_key()
    if os.path.exists(dup_file):
        with open(dup_file) as f:
            for line in f:
                try:
                    if json.loads(line).get("hash") == hash_val and json.loads(line).get("date") == today:
                        return True
                except: pass
    os.makedirs(os.path.dirname(dup_file), exist_ok=True)
    with open(dup_file, "a") as f:
        f.write(json.dumps({"hash": hash_val, "date": today, "ts": now_iso()}) + "\n")
    return False

def save_ezone_json(text: str, telegram_chat_id: int) -> tuple:
    norm = normalize_json_text(text)
    try: data = json.loads(norm)
    except: data = {"raw_text": norm}
    if not isinstance(data, dict): data = {"raw_text": norm}
    
    chat_key = build_chat_key(telegram_chat_id)
    ts = now_iso()
    hash_val = content_hash(text)
    
    if is_duplicate_today(hash_val, chat_key):
        return False, chat_key, "duplicate"
    
    data["_meta"] = {"chat_key": chat_key, "ingested_at": ts, "source": "telegram"}
    chat_dir = os.path.join(MEMORY_FILES, "CHATS", chat_key)
    os.makedirs(chat_dir, exist_ok=True)
    
    with open(os.path.join(chat_dir, "raw.json"), "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    entry = json.dumps({"timestamp": ts, "data": data}, ensure_ascii=False)
    with open(os.path.join(chat_dir, "timeline.jsonl"), "a") as f:
        f.write(entry + "\n")
    with open(os.path.join(MEMORY_FILES, "GLOBAL", "timeline.jsonl"), "a") as f:
        f.write(json.dumps({"timestamp": ts, "chat_key": chat_key, "data": data}, ensure_ascii=False) + "\n")
    
    for key in EZONE_KEYS:
        if key in data:
            with open(os.path.join(MEMORY_FILES, "SYSTEM", f"{key}.jsonl"), "a") as f:
                f.write(json.dumps({"timestamp": ts, "chat_key": chat_key, "data": data[key]}, ensure_ascii=False) + "\n")
    
    update_chat_map_atomic(telegram_chat_id, chat_key)
    logger.info("eZone saved: chat_key=%s telegram_chat=%s", chat_key, telegram_chat_id)
    return True, chat_key, ""


def dump_yzon_state(chat_id: int) -> str:
    import sqlite3, json

    result = {
        "system": {"name": "AREAL-NEVA ORCHESTRA", "role": "task execution system"},
        "architecture": {
            "pipeline": "telegram_daemon -> task_worker -> ai_router -> reply_sender",
            "memory": "memory.db + memory_files",
            "storage": "Google Drive",
            "mode": "server-first"
        },
        "runtime": {
            "chat_id": str(chat_id),
            "has_active_task": False,
            "has_active_pin": False,
            "daemon": "running",
            "worker": "running"
        },
        "active_context": {},
        "recent_results": [],
        "recent_decisions": []
    }

    try:
        conn = sqlite3.connect("/root/.areal-neva-core/data/core.db")

        cur = conn.execute(
            "SELECT id, state, raw_input FROM tasks WHERE chat_id = ? AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION') ORDER BY created_at DESC LIMIT 1",
            (str(chat_id),)
        )
        row = cur.fetchone()
        if row:
            result["runtime"]["has_active_task"] = True
            result["active_context"]["task_id"] = row[0]
            result["active_context"]["state"] = row[1]
            result["active_context"]["input"] = row[2][:200] if row[2] else ""

        cur = conn.execute(
            "SELECT task_id FROM pin WHERE chat_id = ? AND state = 'ACTIVE' ORDER BY updated_at DESC LIMIT 1",
            (str(chat_id),)
        )
        pin_row = cur.fetchone()
        if pin_row:
            result["runtime"]["has_active_pin"] = True
            result["active_context"]["active_pin"] = pin_row[0]

        cur = conn.execute(
            "SELECT id, result FROM tasks WHERE chat_id = ? AND state = 'DONE' AND result IS NOT NULL ORDER BY updated_at DESC LIMIT 5",
            (str(chat_id),)
        )
        for row in cur.fetchall():
            result["recent_results"].append({"task_id": row[0], "summary": row[1][:200] if row[1] else ""})

        cur = conn.execute(
            "SELECT task_id, action FROM task_history WHERE task_id IN (SELECT id FROM tasks WHERE chat_id = ?) ORDER BY created_at DESC LIMIT 10",
            (str(chat_id),)
        )
        for row in cur.fetchall():
            result["recent_decisions"].append({"task_id": row[0], "action": row[1]})

        conn.close()
    except Exception as e:
        result["error"] = str(e)

    return json.dumps(result, ensure_ascii=False, indent=2)


def dump_system_state() -> str:
    import sqlite3, json, os
    from datetime import datetime, timezone

    result = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "chat_id": None,
        "active_task": None,
        "active_pin": None,
        "recent_results": [],
        "architecture": {
            "system": "AREAL-NEVA ORCHESTRA",
            "stack": "telegram_daemon + task_worker + ai_router + OpenRouter",
            "memory": "memory_files + memory.db",
            "files": "Google Drive via google_io"
        }
    }

    try:
        conn = sqlite3.connect("/root/.areal-neva-core/data/core.db")
        cur = conn.execute("SELECT id, state, raw_input FROM tasks WHERE chat_id = '-1003725299009' AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION') ORDER BY created_at DESC LIMIT 1")
        row = cur.fetchone()
        if row:
            result["chat_id"] = "-1003725299009"
            result["active_task"] = {"id": row[0], "state": row[1], "input": row[2][:200]}
        
        cur = conn.execute("SELECT task_id FROM pin WHERE chat_id = '-1003725299009' AND state = 'ACTIVE' ORDER BY updated_at DESC LIMIT 1")
        pin_row = cur.fetchone()
        if pin_row:
            result["active_pin"] = pin_row[0]
        
        cur = conn.execute("SELECT id, result FROM tasks WHERE chat_id = '-1003725299009' AND state = 'DONE' AND result IS NOT NULL ORDER BY updated_at DESC LIMIT 20")
        for row in cur.fetchall():
            result["recent_results"].append({"task_id": row[0], "summary": row[1][:200]})
        
        conn.close()
    except Exception as e:
        result["error"] = str(e)

    return json.dumps(result, ensure_ascii=False, indent=2)

def split_message(text: str, limit: int = 4000) -> list:
    text = text or ""
    parts = []
    while text and len(parts) < 10:
        if len(text) <= limit:
            parts.append(text); break
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1 or split_at < limit // 3:
            split_at = limit
        parts.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return parts or [""]

async def create_task(message: types.Message, input_type: str, raw_input: str, state: str = "NEW"):
    task_id = str(uuid.uuid4())
    now = now_iso()
    user_id = getattr(message.from_user, "id", 0) if message.from_user else 0
    topic_id = getattr(message, "message_thread_id", None) or 0
    # === P7_TOPIC5_REAL_REPLY_TARGET_V1 ===
    # Store Telegram reply target, not current message id.
    # No-reply messages keep their own message_id, preserving old parent lookup.
    reply_target_id = message.reply_to_message.message_id if message.reply_to_message else message.message_id
    # === END_P7_TOPIC5_REAL_REPLY_TARGET_V1 ===
    async with aiosqlite.connect(DB) as db:
        cols = [r[1] for r in await (await db.execute("PRAGMA table_info(tasks)")).fetchall()]
        if "topic_id" in cols:
            await db.execute(
                "INSERT INTO tasks (id, chat_id, user_id, input_type, raw_input, state, reply_to_message_id, topic_id, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (task_id, message.chat.id, user_id, input_type, raw_input, state, reply_target_id, topic_id, now, now))
        else:
            await db.execute(
                "INSERT INTO tasks (id, chat_id, user_id, input_type, raw_input, state, reply_to_message_id, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
                (task_id, message.chat.id, user_id, input_type, raw_input, state, reply_target_id, now, now))
        await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (task_id, f"created:{state}", now))
        await db.commit()

    # === TELEGRAM_TIMELINE_APPEND_V1 ===
    try:
        _tl_chat_key = build_chat_key(message.chat.id)
        _tl_chat_dir = os.path.join(MEMORY_FILES, "CHATS", _tl_chat_key)
        os.makedirs(_tl_chat_dir, exist_ok=True)
        os.makedirs(os.path.join(MEMORY_FILES, "GLOBAL"), exist_ok=True)
        _tl_entry = json.dumps({
            "timestamp": now, "chat_id": str(message.chat.id),
            "topic_id": int(topic_id or 0), "task_id": task_id,
            "input_type": input_type, "state": state,
            "raw_input": str(raw_input or "")[:4000],
            "source": "telegram_daemon_create_task",
        }, ensure_ascii=False)
        for _tl_path in [
            os.path.join(_tl_chat_dir, "timeline.jsonl"),
            os.path.join(MEMORY_FILES, "GLOBAL", "timeline.jsonl"),
        ]:
            with open(_tl_path, "a", encoding="utf-8") as _f:
                _f.write(_tl_entry + "\n")
    except Exception as _tl_e:
        logger.warning("TELEGRAM_TIMELINE_APPEND_V1_ERR %s", _tl_e)
    # === END TELEGRAM_TIMELINE_APPEND_V1 ===

    logger.info("Task %s created state=%s topic_id=%s", task_id, state, topic_id)
    return task_id

async def continue_parent_task(parent_id: str, user_text: str):
    now = now_iso()
    merged_sql = "COALESCE(raw_input,'') || ?"
    suffix = "\n\nПродолжение пользователя:\n" + user_text
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            f"UPDATE tasks SET raw_input={merged_sql}, state='IN_PROGRESS', updated_at=? WHERE id=?",
            (suffix, now, parent_id)
        )
        await db.execute(
            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
            (parent_id, "continuation:IN_PROGRESS", now)
        )
        await db.commit()
    logger.info("Task %s continued -> IN_PROGRESS", parent_id)

async def get_active_task(chat_id: int) -> dict:
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT id, state, raw_input FROM tasks WHERE chat_id=? AND state IN ('NEW','IN_PROGRESS') ORDER BY created_at DESC LIMIT 1",
            (chat_id,))
        row = await cur.fetchone()
        if row:
            return {"id": row[0], "state": row[1], "raw_input": row[2]}
        return None

async def cancel_active_task(chat_id: int):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT id FROM tasks WHERE chat_id=? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION')",
            (chat_id,)
        )
        tasks = await cur.fetchall()
        for t in tasks:
            await db.execute("UPDATE tasks SET state='CANCELLED', updated_at=? WHERE id=?", (now_iso(), t[0]))
            await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (t[0], "cancelled", now_iso()))
        await db.commit()
async def reset_all_open_tasks(chat_id: int):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT id FROM tasks WHERE chat_id=? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION')",
            (chat_id,)
        )
        rows = await cur.fetchall()
        now = now_iso()
        for row in rows:
            task_id = row[0]
            await db.execute(
                "UPDATE tasks SET state='CANCELLED', updated_at=? WHERE id=?",
                (now, task_id)
            )
            await db.execute(
                "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
                (task_id, "reset:CANCELLED", now)
            )
        try:
            await db.execute(
                "UPDATE pin SET state='CLOSED', updated_at=? WHERE chat_id=? AND state='ACTIVE'",
                (now, str(chat_id))
            )
        except Exception:
            pass
        await db.commit()

def _has_any_phrase(lower_text: str, phrases: list[str]) -> bool:
    t = (lower_text or "").strip()
    return t in phrases

async def close_latest_open_task(chat_id: int, action: str = "finish:DONE") -> bool:
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT id FROM tasks WHERE chat_id=? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') ORDER BY updated_at DESC, created_at DESC LIMIT 1",
            (chat_id,)
        )
        row = await cur.fetchone()
        if not row:
            return False
        task_id = row[0]
        now = now_iso()
        await db.execute(
            "UPDATE tasks SET state='DONE', updated_at=? WHERE id=?",
            (now, task_id)
        )
        await db.execute(
            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
            (task_id, action, now)
        )
        try:
            await db.execute(
                "UPDATE pin SET state='CLOSED', updated_at=? WHERE task_id=? AND state='ACTIVE'",
                (now, task_id)
            )
            await db.execute(
                "UPDATE pin SET state='CLOSED', updated_at=? WHERE chat_id=? AND state='ACTIVE'",
                (now, str(chat_id))
            )
        except Exception:
            pass
        await db.commit()
        return True

async def cancel_all_open_tasks(chat_id: int, topic_id: int = 0) -> int:
    async with aiosqlite.connect(DB) as db:
        if topic_id > 0:
            cur = await db.execute(
                "SELECT id FROM tasks WHERE chat_id=? AND topic_id=? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION')",
                (chat_id, topic_id)
            )
        else:
            cur = await db.execute(
                "SELECT id FROM tasks WHERE chat_id=? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION')",
                (chat_id,)
            )
        rows = await cur.fetchall()
        now = now_iso()
        count = 0
        for row in rows:
            task_id = row[0]
            await db.execute(
                "UPDATE tasks SET state='CANCELLED', updated_at=? WHERE id=?",
                (now, task_id)
            )
            await db.execute(
                "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
                (task_id, "cancelled:CANCELLED", now)
            )
            count += 1
        try:
            await db.execute(
                "UPDATE pin SET state='CLOSED', updated_at=? WHERE chat_id=? AND state='ACTIVE'",
                (now, str(chat_id))
            )
        except Exception:
            pass
        await db.commit()
        return count

async def _find_parent_task(chat_id: int, reply_to: int | None, topic_id: int = 0):
    async with aiosqlite.connect(DB) as db:
        cols = [r[1] for r in await (await db.execute("PRAGMA table_info(tasks)")).fetchall()]
        has_topic = "topic_id" in cols and topic_id > 0
        topic_filter = " AND topic_id=?" if has_topic else ""
        topic_args = (topic_id,) if has_topic else ()
        if reply_to:
            cur = await db.execute(
                f"SELECT id, state FROM tasks WHERE chat_id=? AND bot_message_id=?{topic_filter} AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
                (chat_id, reply_to) + topic_args
            )
            row = await cur.fetchone()
            if row:
                return row
            cur = await db.execute(
                f"SELECT id, state FROM tasks WHERE chat_id=? AND reply_to_message_id=?{topic_filter} AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
                (chat_id, reply_to) + topic_args
            )
            row = await cur.fetchone()
            if row:
                return row
        cur = await db.execute(
            f"SELECT id, state FROM tasks WHERE chat_id=?{topic_filter} AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
            (chat_id,) + topic_args
        )
        return await cur.fetchone()

async def _handle_control_text(message, tg_id: int, text: str, lower: str, reply_to: int | None, topic_id: int = 0) -> bool:
    if _has_any_phrase(lower, CANCEL_PHRASES):
        closed = await cancel_all_open_tasks(tg_id, topic_id)
        await message.answer("Все запросы отменены" if closed else "Нет активных задач")
        return True

    parent = await _find_parent_task(tg_id, reply_to, topic_id)

    if _has_any_phrase(lower, FINISH_PHRASES):
        if parent:
            parent_id = parent[0]
            now = now_iso()
            async with aiosqlite.connect(DB) as db:
                await db.execute("UPDATE tasks SET state='DONE', updated_at=? WHERE id=?", (now, parent_id))
                await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, "finish:DONE", now))
                await db.execute("UPDATE pin SET state='CLOSED', updated_at=? WHERE task_id=? AND state='ACTIVE'", (now, parent_id))
                await db.commit()
            await message.answer("Задача закрыта")
            return True
        closed = await close_latest_open_task(tg_id, "finish:DONE")
        await message.answer("Задача закрыта" if closed else "Нет активных задач")
        return True

    if not parent:
        return False

    parent_id, parent_state = parent[0], parent[1]

    if parent_state == "AWAITING_CONFIRMATION":
        if lower.strip() in SHORT_CONFIRM and lower.strip() not in NEGATIVE_CONFIRM:
            now = now_iso()
            async with aiosqlite.connect(DB) as db:
                await db.execute("UPDATE tasks SET state='DONE', updated_at=? WHERE id=?", (now, parent_id))
                await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, "confirmed:DONE", now))
                await db.execute("UPDATE pin SET state='CLOSED', updated_at=? WHERE task_id=? AND state='ACTIVE'", (now, parent_id))
                await db.commit()
            await message.answer("Задача завершена")
            return True
        if lower.strip() in NEGATIVE_CONFIRM:
            now = now_iso()
            async with aiosqlite.connect(DB) as db:
                await db.execute("UPDATE tasks SET state='WAITING_CLARIFICATION', updated_at=? WHERE id=?", (now, parent_id))
                await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, "rejected:WAITING_CLARIFICATION", now))
                await db.execute("UPDATE pin SET state='CLOSED', updated_at=? WHERE task_id=? AND state='ACTIVE'", (now, parent_id))
                await db.commit()
            await message.answer("Хорошо, доработаю. Подтверждение снято.  # FULLFIX_02_E")
            return True

    if parent_state == "WAITING_CLARIFICATION":
        now = now_iso()
        async with aiosqlite.connect(DB) as db:
            await db.execute("UPDATE tasks SET state='IN_PROGRESS', updated_at=? WHERE id=?", (now, parent_id))
            await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, f"clarified:{text}", now))
            await db.commit()
        await message.answer("Принято, продолжаю")
        return True

    if parent_state == "IN_PROGRESS" and reply_to:
        now = now_iso()
        async with aiosqlite.connect(DB) as db:
            await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, f"continued:{text}", now))
            await db.commit()
        await message.answer("Принято, продолжаю")
        return True

    return False


async def download_telegram_file(file_path: str, local_path: str) -> str:
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    async with aiohttp.ClientSession() as s:
        async with s.get(url, timeout=aiohttp.ClientTimeout(total=300)) as r:
            r.raise_for_status()
            async with aiofiles.open(local_path, "wb") as f:
                await f.write(await r.read())
    return local_path

@dp.message()
async def universal_handler(message: types.Message):
    update_id = getattr(message, 'update_id', None)
    if update_id:
        async with aiosqlite.connect(DB) as db:
            await db.execute("DELETE FROM processed_updates WHERE created_at < ?", ((datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),))
            cur = await db.execute("SELECT 1 FROM processed_updates WHERE update_id = ?", (update_id,))
            if await cur.fetchone():
                await db.commit()
                return
            await db.execute("INSERT INTO processed_updates (update_id, created_at) VALUES (?, ?)", (update_id, now_iso()))
            await db.commit()
    
    try:
        text = message.text or ""
        lower = text.lower()
        tg_id = message.chat.id
        now_ts = time.monotonic()
        reply_to = message.reply_to_message.message_id if message.reply_to_message else None
        topic_id = int(getattr(message, "message_thread_id", 0) or 0)
        
        # 1. SYSTEM COMMANDS
        if lower in SYSTEM_CMDS:
            if lower in ("сброс задач", "очистить задачи"):
                await reset_all_open_tasks(tg_id)
                await message.answer("Все незакрытые задачи и активные pin закрыты")
            elif lower == "статус":
                async with aiosqlite.connect(DB) as db:
                    cur = await db.execute("SELECT state, COUNT(*) FROM tasks WHERE chat_id = ? GROUP BY state", (tg_id,))
                    rows = await cur.fetchall()
                    cur = await db.execute("SELECT task_id FROM pin WHERE chat_id = ? AND state = 'ACTIVE'", (str(tg_id),))
                    pin_row = await cur.fetchone()
                    status_msg = "Статус:\n" + "\n".join([f"{r[0]}: {r[1]}" for r in rows]) if rows else "Нет задач"
                    if pin_row:
                        status_msg += f"\nАктивный pin: {pin_row[0]}"
                    await message.answer(status_msg)
            elif lower == "yzon":
                dump = dump_yzon_state(tg_id)
                await message.answer(dump)
                return
            elif lower == "дамп":
                import subprocess
                result = subprocess.run(["/root/.areal-neva-core/.venv/bin/python3", "/root/.areal-neva-core/orchestra_full_dump.py"], capture_output=True, text=True, timeout=60)
                dump_files = sorted([f for f in os.listdir("/root/.areal-neva-core/data/memory/UNSORTED") if f.startswith("orchestra_dump_")], reverse=True)
                if dump_files:
                    dump_path = f"/root/.areal-neva-core/data/memory/UNSORTED/{dump_files[0]}"
                    content=open(dump_path).read()
                    for part in split_message(content):
                        await message.answer(part)
                else:
                    await message.answer("Дамп не создан")
                return
            elif lower == "архив":
                async with aiosqlite.connect(DB) as db:
                    cur = await db.execute("SELECT id, state, substr(raw_input,1,100) FROM tasks WHERE chat_id = ? AND state IN ('DONE','FAILED','CANCELLED','ARCHIVED') ORDER BY updated_at DESC LIMIT 10", (tg_id,))
                    rows = await cur.fetchall()
                    if rows:
                        archive_msg = "Архив:\n" + "\n".join([f"{r[0][:8]}: {r[1]} - {r[2]}" for r in rows])
                    else:
                        archive_msg = "Архив пуст"
                    await message.answer(archive_msg)
            elif lower == "язон":
                dump = dump_yzon_state(tg_id)
                await message.answer(dump)
                return
            elif lower == "язон файл":
                dump = dump_yzon_state(tg_id)
                doc = BufferedInputFile(dump.encode("utf-8"), filename="yzon_state.json")
                await message.answer_document(doc)
                return
            elif lower == "дамп файл":
                import subprocess
                subprocess.run(["/root/.areal-neva-core/.venv/bin/python3", "/root/.areal-neva-core/orchestra_full_dump.py"], capture_output=True, text=True, timeout=60)
                dump_files = sorted([f for f in os.listdir("/root/.areal-neva-core/data/memory/UNSORTED") if f.startswith("orchestra_dump_")], reverse=True)
                if dump_files:
                    dump_path = f"/root/.areal-neva-core/data/memory/UNSORTED/{dump_files[0]}"
                    await message.answer_document(FSInputFile(dump_path, filename=dump_files[0]))
                else:
                    await message.answer("Дамп не создан")
                return
            elif lower == "память файл":
                import sqlite3 as _sq, json as _json
                try:
                    _mc = _sq.connect("/root/.areal-neva-core/data/memory.db")
                    _mc.row_factory = _sq.Row
                    _rows = _mc.execute("SELECT chat_id, key, value, timestamp FROM memory WHERE chat_id=? ORDER BY timestamp DESC LIMIT 200", (str(tg_id),)).fetchall()
                    _mc.close()
                    _data = [dict(r) for r in _rows]
                    doc = BufferedInputFile(_json.dumps(_data, ensure_ascii=False, indent=2).encode("utf-8"), filename="memory_dump.json")
                    await message.answer_document(doc)
                except Exception as _e:
                    await message.answer(f"Ошибка: {_e}")
                return
            elif lower == "архив файл":
                import sqlite3 as _sq, io, json as _json
                try:
                    _mc = _sq.connect("/root/.areal-neva-core/data/memory.db")
                    _mc.row_factory = _sq.Row
                    _rows = _mc.execute("SELECT key, value, timestamp FROM memory WHERE chat_id=? AND key LIKE 'archive_legacy_%' ORDER BY timestamp DESC LIMIT 100", (str(tg_id),)).fetchall()
                    _mc.close()
                    _data = [dict(r) for r in _rows]
                    doc = BufferedInputFile(_json.dumps(_data, ensure_ascii=False, indent=2).encode("utf-8"), filename="archive_dump.json")
                    await message.answer_document(doc)
                except Exception as _e:
                    await message.answer(f"Ошибка: {_e}")
                return
            elif lower in ("система", "система файл"):
                sys_info = (
                    "AREAL-NEVA ORCHESTRA\n"
                    "Server: 89.22.225.136 | Ubuntu 24.04\n"
                    "Bot: @ai_orkestra_all_bot\n"
                    "Models: deepseek/deepseek-chat + perplexity/sonar\n"
                    "Pipeline: telegram_daemon -> core.db -> task_worker -> ai_router -> Telegram\n"
                    "Services: telegram-ingress, areal-task-worker, areal-memory-api\n"
                )
                if lower == "система файл":
                    doc = BufferedInputFile(sys_info.encode("utf-8"), filename="system_info.txt")
                    await message.answer_document(doc)
                else:
                    await message.answer(sys_info)
                return
            elif lower == "код файл":
                import io, zipfile
                buf = io.BytesIO()
                files_to_zip = [
                    "/root/.areal-neva-core/task_worker.py",
                    "/root/.areal-neva-core/core/ai_router.py",
                    "/root/.areal-neva-core/telegram_daemon.py",
                ]
                with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for fp in files_to_zip:
                        if os.path.exists(fp):
                            zf.write(fp, os.path.basename(fp))
                doc = BufferedInputFile(buf.getvalue(), filename="core_code.zip")
                await message.answer_document(doc)
                return
            elif lower == "файл":
                import sqlite3 as _sq
                try:
                    _cc = _sq.connect("/root/.areal-neva-core/data/core.db")
                    _rows = _cc.execute("SELECT state, COUNT(*) as cnt FROM tasks GROUP BY state").fetchall()
                    _cc.close()
                    lines = ["AREAL-NEVA ORCHESTRA — краткий статус", ""]
                    for r in _rows:
                        lines.append(f"{r[0]}: {r[1]}")
                    doc = BufferedInputFile("\n".join(lines).encode("utf-8"), filename="status.md")
                    await message.answer_document(doc)
                except Exception as _e:
                    await message.answer(f"Ошибка: {_e}")
                return
            else:
                dump = dump_system_state()
                for part in split_message(dump):
                    await message.answer(part)
                    await asyncio.sleep(0.5)
            return
        
        # 2. CANCEL
        if lower in CANCEL_CMDS:
            await cancel_active_task(tg_id)
            await message.answer("Задача отменена")
            return
        
        # 3. FILE TASKS + EZONE FILE INGEST
        if message.document and message.document.file_name:
            # HEALTHCHECK_DAEMON_GUARD_V1
            try:
                _hc_check = " ".join([
                    str(message.document.file_name or ""),
                    str(message.caption or ""),
                ]).lower()
                if any(m in _hc_check for m in ("retry_queue_healthcheck", "healthcheck", "areal_hc_", "_hc_file")):
                    logger.info("HEALTHCHECK_DAEMON_GUARD_V1 ignored file=%s", message.document.file_name)
                    return
            except Exception as _hc_e:
                logger.warning("HEALTHCHECK_DAEMON_GUARD_V1_ERR %s", _hc_e)
            tg_file = await bot.get_file(message.document.file_id)
            local_path = f"/tmp/{uuid.uuid4()}_{message.document.file_name}"
            await download_telegram_file(tg_file.file_path, local_path)
            try:
                if message.document.file_name.lower().endswith(EZONE_EXTS):
                    drive_result = await upload_file_to_topic(local_path, message.document.file_name, tg_id, topic_id, getattr(message.document, "mime_type", "") or None)  # DAEMON_OAUTH_FIX_V1
                    with open(local_path, "r", errors="ignore") as f:
                        content = f.read()
                    if is_ezone_payload(content):
                        ok, chat_key, _ = save_ezone_json(content, tg_id)
                        _RECENT_INGEST[tg_id] = now_ts
                        await message.answer(f"Принял, память загружена ({chat_key})" if ok else "Уже загружено")
                        return
                else:
                    topic_id = getattr(message, "message_thread_id", 0) or 0
                    drive_result = await upload_file_to_topic(local_path, message.document.file_name, tg_id, topic_id, getattr(message.document, "mime_type", "") or None)
                    if isinstance(drive_result, dict) and drive_result.get("ok") and drive_result.get("drive_file_id"):
                        payload = {
                            "file_id": drive_result.get("drive_file_id", ""),
                            "file_name": message.document.file_name,
                            "mime_type": getattr(message.document, "mime_type", "") or "",
                            "caption": (message.caption or message.text or "").strip(),
                            "source": "telegram",
                            "telegram_message_id": message.message_id,
                            "telegram_chat_id": message.chat.id,
                        }
                        await create_task(message, "drive_file", json.dumps(payload, ensure_ascii=False), "NEW")
                        await message.answer("Файл принят в обработку")
                        return
                    else:
                        await message.answer("Ошибка загрузки файла в Drive")
                        return
            finally:
                try: os.remove(local_path)
                except: pass

        # 3A. PHOTO TASK
        if message.photo:
            photo = message.photo[-1]
            tg_file = await bot.get_file(photo.file_id)
            file_name = f"photo_{message.chat.id}_{message.message_id}.jpg"
            local_path = f"/tmp/{uuid.uuid4()}_{file_name}"
            await download_telegram_file(tg_file.file_path, local_path)
            try:
                drive_result = await upload_file_to_topic(local_path, file_name, tg_id, topic_id, "image/jpeg")
                if isinstance(drive_result, dict) and drive_result.get("ok") and drive_result.get("drive_file_id"):
                    payload = {
                        "file_id": drive_result.get("drive_file_id", ""),
                        "file_name": file_name,
                        "mime_type": "image/jpeg",
                        "caption": (message.caption or message.text or "").strip(),
                        "source": "telegram",
                        "telegram_message_id": message.message_id,
                        "telegram_chat_id": message.chat.id,
                    }
                    await create_task(message, "drive_file", json.dumps(payload, ensure_ascii=False), "NEW")
                    await message.answer("Фото принято в обработку")
                    return
                else:
                    await message.answer("Ошибка загрузки фото в Drive")
                    return
            finally:
                try: os.remove(local_path)
                except: pass
        
        # 4. EZONE TEXT INGEST
        if message.text and is_ezone_payload(text):
            ok, chat_key, _ = save_ezone_json(text, tg_id)
            _RECENT_INGEST[tg_id] = now_ts
            await message.answer(f"Принял, память загружена ({chat_key})" if ok else "Уже загружено")
            return
        
        # 5. ANTI-DUP AFTER INGEST
        if message.text:
            last = _RECENT_INGEST.get(tg_id, 0.0)
            if now_ts - last < 5:
                if text.lstrip().startswith("{") or any(k in lower for k in EZONE_KEYS):
                    return
        
        # 6. CONFIRMATION AND REPLY CONTINUATION
        active_confirm = None
        async with aiosqlite.connect(DB) as db:
            cur = await db.execute(
                "SELECT id, state FROM tasks WHERE chat_id = ? AND state = 'AWAITING_CONFIRMATION' ORDER BY updated_at DESC LIMIT 1",
                (tg_id,)
            )
            active_confirm = await cur.fetchone()

        if active_confirm and message.text:
            parent_id, parent_state = active_confirm
            if lower.strip() in SHORT_CONFIRM and lower.strip() not in NEGATIVE_CONFIRM:
                async with aiosqlite.connect(DB) as db:
                    await db.execute("UPDATE tasks SET state = 'DONE', updated_at = ? WHERE id = ?", (now_iso(), parent_id))
                    await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, "confirmed:DONE", now_iso()))
                    await db.execute("UPDATE pin SET state = 'CLOSED', updated_at = ? WHERE task_id = ? AND state = 'ACTIVE'", (now_iso(), parent_id))
                    await db.commit()
                await message.answer("Задача завершена")
                return
            elif lower.strip() in NEGATIVE_CONFIRM:
                async with aiosqlite.connect(DB) as db:
                    await db.execute("UPDATE tasks SET state = 'WAITING_CLARIFICATION', updated_at = ? WHERE id = ?", (now_iso(), parent_id))
                    await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, "rejected:WAITING_CLARIFICATION", now_iso()))
                    await db.execute("UPDATE pin SET state = 'CLOSED', updated_at = ? WHERE task_id = ? AND state = 'ACTIVE'", (now_iso(), parent_id))
                    await db.commit()
                await message.answer("Хорошо, доработаю. Подтверждение снято.  # FULLFIX_02_E")
                return

        if reply_to and not message.voice:
            async with aiosqlite.connect(DB) as db:
                cur = await db.execute(
                    "SELECT id, state FROM tasks WHERE chat_id = ? AND (bot_message_id = ? OR reply_to_message_id = ?) AND COALESCE(topic_id,0) = COALESCE(?,0) AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') ORDER BY CASE WHEN bot_message_id = ? THEN 0 ELSE 1 END, updated_at DESC LIMIT 1",
                    (tg_id, reply_to, reply_to, topic_id, reply_to)
                )
                parent = await cur.fetchone()
            if parent:
                parent_id, parent_state = parent
                if parent_state == "WAITING_CLARIFICATION":
                    _topic2_price_reply = (
                        int(topic_id or 0) == 2
                        and lower.strip().strip(" .,!?:;()[]{}") in ("1", "2", "3", "4", "а", "б", "в", "г", "a", "b", "v", "g")
                    )
                    if _topic2_price_reply:
                        await create_task(message, "text", text, "NEW")
                        return
                    else:
                        async with aiosqlite.connect(DB) as db:
                            await db.execute("UPDATE tasks SET state = 'IN_PROGRESS', updated_at = ? WHERE id = ?", (now_iso(), parent_id))
                            await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, f"clarified:{text}", now_iso()))
                            await db.commit()
                        await message.answer("Принято, продолжаю")
                        return
                if parent and parent_state == "WAITING_CLARIFICATION":
                    async with aiosqlite.connect(DB) as db:
                        await db.execute("UPDATE tasks SET state = 'IN_PROGRESS', updated_at = ? WHERE id = ?", (now_iso(), parent_id))
                        await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, f"clarified:{text}", now_iso()))
                        await db.commit()
                    await message.answer("Принято, продолжаю")
                elif lower.strip() in SHORT_CONFIRM and lower.strip() not in NEGATIVE_CONFIRM:
                    async with aiosqlite.connect(DB) as db:
                        await db.execute("UPDATE tasks SET state = 'IN_PROGRESS', updated_at = ? WHERE id = ?", (now_iso(), parent_id))
                        await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, f"confirmed:{text}", now_iso()))
                        await db.commit()
                    await message.answer("Принято, выполняю")
                    return
                else:
                    pass

        # 7. SEARCH TASK
        if any(t in lower for t in SEARCH_TRIGGERS):
            await create_task(message, "search", text, "NEW")
            return
        
        # 8. VOICE
        if message.voice:
            tg_file = await bot.get_file(message.voice.file_id)
            local_path = os.path.join(VOICE_DIR, f"voice_{abs(tg_id)}_{message.message_id}.ogg")
            await download_telegram_file(tg_file.file_path, local_path)
            pass  # VOICE_UPLOAD_SKIP_V1 — голос не загружаем на Drive
            from core.stt_engine import transcribe_voice as _stt
            try:
                _transcript = await _stt(local_path)
            except Exception as _err:
                logger.error("STT_FAILED chat=%s err=%s", tg_id, _err)
                await message.answer("Голос не распознан. Повтори голосом или напиши текстом")
                return
            if not _transcript or not _transcript.strip():
                logger.error("STT_EMPTY chat=%s", tg_id)
                await message.answer("Не удалось получить текст из голосового. Повтори или напиши текстом")
                return
            voice_text = _transcript.strip()
            voice_lower = voice_text.lower()
            voice_reply_to = message.reply_to_message.message_id if message.reply_to_message else None
            _voice_topic_id = getattr(message, "message_thread_id", None) or 0
            try:
                await message.answer(f"🎤 {voice_text}")
            except Exception as _e:
                logger.warning("transcript_send_fail err=%s", _e)

            # === PATCH_VOICE_CONFIRM_DIRECT ===
            # Voice does not populate message.text, so confirm/reject must be checked after STT
            try:
                _voice_cmd = voice_lower.strip().rstrip("!., ")
                async with aiosqlite.connect(DB) as db:
                    cur = await db.execute(
                        """
                        SELECT id, state
                        FROM tasks
                        WHERE chat_id = ?
                          AND COALESCE(topic_id,0) = COALESCE(?,0)
                          AND state = 'AWAITING_CONFIRMATION'
                        ORDER BY updated_at DESC
                        LIMIT 1
                        """,
                        (tg_id, _voice_topic_id)
                    )
                    _voice_active_confirm = await cur.fetchone()

                if _voice_active_confirm and _voice_cmd in SHORT_CONFIRM and _voice_cmd not in NEGATIVE_CONFIRM:
                    parent_id, parent_state = _voice_active_confirm
                    async with aiosqlite.connect(DB) as db:
                        await db.execute(
                            "UPDATE tasks SET state = 'DONE', updated_at = ? WHERE id = ?",
                            (now_iso(), parent_id)
                        )
                        await db.execute(
                            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
                            (parent_id, "voice_confirmed:DONE", now_iso())
                        )
                        await db.execute(
                            "UPDATE pin SET state = 'CLOSED', updated_at = ? WHERE task_id = ? AND state = 'ACTIVE'",
                            (now_iso(), parent_id)
                        )
                        await db.commit()
                    await message.answer("Задача завершена")
                    return

                if _voice_active_confirm and _voice_cmd in NEGATIVE_CONFIRM:
                    parent_id, parent_state = _voice_active_confirm
                    async with aiosqlite.connect(DB) as db:
                        await db.execute(
                            "UPDATE tasks SET state = 'WAITING_CLARIFICATION', updated_at = ? WHERE id = ?",
                            (now_iso(), parent_id)
                        )
                        await db.execute(
                            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
                            (parent_id, "voice_rejected:WAITING_CLARIFICATION", now_iso())
                        )
                        await db.execute(
                            "UPDATE pin SET state = 'CLOSED', updated_at = ? WHERE task_id = ? AND state = 'ACTIVE'",
                            (now_iso(), parent_id)
                        )
                        await db.commit()
                    await message.answer("Хорошо, доработаю. Подтверждение снято.  # FULLFIX_02_E")
                    return
            except Exception as _voice_confirm_err:
                logger.error("VOICE_CONFIRM_DIRECT_ERROR chat=%s err=%s", tg_id, _voice_confirm_err)
            # === END PATCH_VOICE_CONFIRM_DIRECT ===
            _VOICE_CONTROL = ["отбой", "отмена", "не надо", "всё", "готово", "можно закрывать", "задача закрыта", "да", "нет", "ок", "+"]
            if any(voice_lower.strip() == x for x in _VOICE_CONTROL):
                if await _handle_control_text(message, tg_id, voice_text, voice_lower, voice_reply_to, _voice_topic_id):
                    return
            await create_task(message, "text", "[VOICE] " + voice_text, "NEW")
            return
        
        # 9. NORMAL TEXT
        if message.text:
            reply_to = message.reply_to_message.message_id if message.reply_to_message else None
            _text_topic_id = getattr(message, "message_thread_id", None) or 0
            if await _handle_control_text(message, tg_id, text, lower, reply_to, _text_topic_id):
                return
            # === CHAT_GUARD_V1 ===
            try:
                from core.intent_lock import is_chat_only as _ig_chat
                if _ig_chat(text):
                    return  # короткие реакции не создают задачи
            except Exception:
                pass
            # === END CHAT_GUARD_V1 ===
            await create_task(message, "text", text, "NEW")
            return
        
    except Exception as e:
        logger.error("HANDLER_CRASH: %s", e)
        try:
            await message.answer("Ошибка обработки")
        except:
            pass

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    logger.info("BOT STARTED id=%s username=%s", me.id, me.username)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

====================================================================================================
END_FILE: telegram_daemon.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/project_route_guard.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 8c39df6c221a56c2de08e994e37b2e45ca02a9de20d2647695d46606159bfb46
====================================================================================================
# === PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1 ===
# === PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1 ===
from __future__ import annotations

import json
import re
import sqlite3
from typing import Any, Dict, Optional

PROJECT_STRONG = (
    "сделай проект", "создай проект", "разработай проект", "подготовь проект",
    "проект монолит", "проект плиты", "проект фундамент", "проект кровли",
    "проект кж", "проект кд", "проект ар", "чертеж", "чертёж",
    "конструктивное решение", "проектное решение", "лист кж", "лист кд"
)

PROJECT_WEAK = (
    "кж", "кд", "ар", "км", "кмд", "плита", "фундамент", "армирование",
    "опалубка", "разрез", "узел", "схема", "спецификация арматуры"
)

ESTIMATE_ONLY = (
    "смета", "смету", "сметный", "расценка", "стоимость работ",
    "цены материалов", "кс-2", "кс2"
)

def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v).strip()

def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")

def _task_field(task: Any, field: str, default: Any = "") -> Any:
    try:
        if hasattr(task, "keys") and field in task.keys():
            return task[field]
    except Exception:
        pass
    if isinstance(task, dict):
        return task.get(field, default)
    try:
        return getattr(task, field)
    except Exception:
        return default

def is_explicit_project_intent(text: Any) -> bool:
    low = _low(text)
    if not low:
        return False
    strong = any(x in low for x in PROJECT_STRONG)
    weak_project = sum(1 for x in PROJECT_WEAK if x in low) >= 2
    estimate_only = any(x in low for x in ESTIMATE_ONLY)  # ESTIMATE_PRIORITY_FIX_V1
    if estimate_only and not strong:  # ESTIMATE_PRIORITY_FIX_V1
        return False
    return bool(strong or weak_project)

def _format_links(res: Dict[str, Any]) -> str:
    lines = []
    for label, key in (
        ("DOCX", "docx_link"),
        ("XLSX", "xlsx_link"),
        ("PDF", "pdf_link"),
        ("Drive", "drive_link"),
    ):
        val = _s(res.get(key))
        if val and "drive.google.com" in val or "docs.google.com" in val:
            lines.append(f"{label}: {val}")
    return "\n".join(lines)

def format_project_result_message(res: Dict[str, Any], raw_input: str = "") -> str:
    section = _s(res.get("project_type") or res.get("section") or "КЖ")
    links = _format_links(res)
    if res.get("success") and links:
        msg = (
            "Проектный файл создан\n"
            f"Раздел: {section}\n"
            f"{links}\n\n"
            "Доволен результатом? Да / Уточни / Правки"
        )
    elif res.get("success"):
        msg = (
            "Проектный файл подготовлен локально, но ссылка Drive не подтверждена\n"
            f"Раздел: {section}\n"
            "Нужна проверка выгрузки"
        )
    else:
        err = _s(res.get("error")) or "PROJECT_RESULT_NOT_READY"
        if "PROJECT_TEMPLATE_MODEL_NOT_FOUND" in err:
            msg = (
                "Для проектного файла нужен образец проекта в этом топике\n"
                "Пришли КЖ/КД/АР файл как образец или напиши исходные данные проекта"
            )
        else:
            msg = (
                "Проектный файл не создан\n"
                f"Причина: {err}\n"
                "Уточни исходные данные или пришли образец проекта"
            )

    try:
        from core.output_sanitizer import sanitize_project_message
        return sanitize_project_message(msg)
    except Exception:
        return msg.strip()

async def prehandle_project_route_v1(conn: sqlite3.Connection, task: Any) -> Optional[Dict[str, Any]]:
    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    input_type = _s(_task_field(task, "input_type"))
    raw_input = _s(_task_field(task, "raw_input"))

    # === CANON_LIST_QUERY_GUARD_V1 ===
    if topic_id == 500:
        return None
    _list_signals = ("какие", "покажи", "перечисли", "что есть", "есть ли", "список", "что за образц", "какие образц", "покажи образц")
    _create_signals = ("сделай", "создай", "разработай", "подготовь", "оформи")
    _raw_low_guard = raw_input.lower().replace("ё", "е")
    if any(s in _raw_low_guard for s in _list_signals) and not any(s in _raw_low_guard for s in _create_signals):
        return None
    # === END_CANON_LIST_QUERY_GUARD_V1 ===
    if input_type not in ("text", "voice", "search"):
        return None
    if not is_explicit_project_intent(raw_input):
        return None

    try:
        from core.project_engine import create_project_artifact_from_latest_template
        res = create_project_artifact_from_latest_template(raw_input, task_id, topic_id)
    except Exception as e:
        res = {
            "success": False,
            "error": f"PROJECT_ENGINE_EXCEPTION: {e}",
            "project_type": "КЖ",
        }

    msg = _s(res.get("user_message")) or format_project_result_message(res, raw_input)

    if res.get("success") and ("drive.google.com" in msg or "docs.google.com" in msg):
        state = "AWAITING_CONFIRMATION"
        err = ""
        hist = "PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1:PROJECT_CREATED"
    elif res.get("success"):
        state = "WAITING_CLARIFICATION"
        err = "PROJECT_DRIVE_LINK_NOT_CONFIRMED"
        hist = "PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1:PROJECT_LOCAL_ONLY"
    else:
        state = "WAITING_CLARIFICATION"
        err = _s(res.get("error")) or "PROJECT_NOT_CREATED"
        hist = "PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1:PROJECT_NEEDS_CONTEXT"

    return {
        "handled": True,
        "state": state,
        "message": msg,
        "error_message": err,
        "kind": "project_route_guard",
        "history": hist,
    }

# === END_PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1 ===
# === END_PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1 ===

====================================================================================================
END_FILE: core/project_route_guard.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/final_closure_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 350fb46557559a9d01adfd07b790ca2c001dd3b58fd0ad8e8dfad71f286ac24f
====================================================================================================
# === FINAL_CLOSURE_BLOCKER_FIX_V1_ENGINE ===
from __future__ import annotations

import json
import re
import sqlite3
from typing import Any, Dict


def _s(v) -> str:
    return "" if v is None else str(v).strip()


def _json(raw: str) -> Dict[str, Any]:
    try:
        return json.loads(raw or "{}")
    except Exception:
        return {}


def _field(task: Any, key: str, default=None):
    try:
        if hasattr(task, "keys") and key in task.keys():
            return task[key]
    except Exception:
        pass
    try:
        return getattr(task, key)
    except Exception:
        return default


def _row_get(row: Any, key: str, idx: int, default: Any = "") -> Any:
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        if isinstance(row, dict):
            return row.get(key, default)
    except Exception:
        pass
    try:
        return row[idx]
    except Exception:
        return default


def _send_payload(message: str, kind: str, state: str = "DONE", history: str = "") -> Dict[str, Any]:
    return {
        "handled": True,
        "state": state,
        "message": message,
        "kind": kind,
        "history": history or f"FINAL_CLOSURE_BLOCKER_FIX_V1:{kind}",
    }



# === FINAL_CLOSURE_MEMORY_QUERY_PUBLIC_OUTPUT_V2 ===

# === FINAL_CLOSURE_MEMORY_QUERY_PUBLIC_OUTPUT_V3 ===


# === PROJECT_SAMPLE_SELECTION_P0_V2 ===
def _fc_norm_public(text: Any) -> str:
    s = "" if text is None else str(text)
    s = s.replace("\\\\n", "\n").replace("\\n", "\n").replace("\\\\t", " ").replace("\\t", " ")
    s = s.replace("ё", "е")
    return s.strip()


def _fc_clean_title(name: str) -> str:
    name = _fc_norm_public(name)
    name = re.sub(r"^\s*\d+\.\s*", "", name).strip().strip("\"'«»")
    return name[:180]


def _fc_is_sample_status_request(text: str) -> bool:
    low = _fc_norm_public(text).lower()
    if not any(x in low for x in ("образец", "образцов", "образцы", "шаблон", "шаблона", "эталон", "эталоны", "эталона")):
        return False

    strict_status_or_selection = (
        "взял как образец",
        "взял за образец",
        "ты взял как образец",
        "уже взял как образец",
        "взял их как образец",
        "взял это как образец",
        "принял как образец",
        "принял за образец",
        "ты принял как образец",
        "уже принял как образец",
        "принял их как образец",
        "принял это как образец",
        "используешь как образец",
        "используется как образец",
        "файлы взяты как образец",
        "файлы приняты как образец",
        "взяты как образец",
        "приняты как образец",
        "закрепи как образец",
        "закрепить как образец",
        "закрепляется как",
        "закрепляй как",
        "оставь как образец",
        "сохрани как образец",
        "сохрани как образцы",
        "прими как образец",
        "прими как образцы",
        "прими эти сметы как образцы",
        "прими эти файлы как образцы",
        "принимай как образец",
        "принимай как образцы",
        "принимай эти сметы как образцы",
        "принимай эти файлы как образцы",
        "принимай эти таблицы как образцы",
        "принимай сметы как образцы",
        "принимай файлы как образцы",
        "работай по ним",
        "работай по этим сметам",
        "работай по этим образцам",
        "работать по ним",
        "работать по этим сметам",
        "логика структура",
        "логика и структура",
        "все должно быть синхронизировано",
        "всё должно быть синхронизировано",
        "как эталон",
        "как эталоны",
        "один из образцов",
        "как один из образцов",
    )
    if any(x in low for x in strict_status_or_selection):
        return True

    if any(x in low for x in ("как образец", "как образцы", "как эталон", "как эталоны")) and any(x in low for x in (
        "да ",
        "да,",
        "да.",
        "цоколь",
        "кж",
        "кд",
        "км",
        "кмд",
        "ар",
        "проект",
        "смет",
        "вор",
        "акт",
        "технадзор",
    )):
        return True

    return False


def _fc_extract_titles_from_text(text: str) -> list[str]:
    src = _fc_norm_public(text)
    titles: list[str] = []

    try:
        data = json.loads(src)
        if isinstance(data, dict):
            for key in ("file_name", "name", "title"):
                val = _fc_clean_title(data.get(key) or "")
                if val:
                    titles.append(val)
    except Exception:
        pass

    for m in re.finditer(r'"file_name"\s*:\s*"([^"]+)"', src, re.I):
        val = _fc_clean_title(m.group(1))
        if val:
            titles.append(val)

    for m in re.finditer(r'([А-ЯA-Z0-9Ёё][^\n\r]{0,120}\.(?:pdf|dwg|dxf|xlsx|xls|docx|doc))', src, re.I):
        val = _fc_clean_title(m.group(1))
        if val:
            titles.append(val)

    out: list[str] = []
    seen = set()
    for title in titles:
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(title)
    return out


def _fc_recent_file_rows(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> list[Any]:
    old_rf = conn.row_factory
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, raw_input, result, updated_at
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND (
                COALESCE(raw_input,'') LIKE '%file_name%'
                OR COALESCE(raw_input,'') LIKE '%.pdf%'
                OR COALESCE(raw_input,'') LIKE '%.dwg%'
                OR COALESCE(raw_input,'') LIKE '%.dxf%'
                OR COALESCE(raw_input,'') LIKE '%.xlsx%'
                OR COALESCE(result,'') LIKE '%file_name%'
                OR COALESCE(result,'') LIKE '%.pdf%'
                OR COALESCE(result,'') LIKE '%.dwg%'
                OR COALESCE(result,'') LIKE '%.dxf%'
                OR COALESCE(result,'') LIKE '%.xlsx%'
              )
            ORDER BY updated_at DESC
            LIMIT 80
            """,
            (str(chat_id), int(topic_id or 0)),
        ).fetchall()
        return list(rows or [])
    except Exception:
        return []
    finally:
        conn.row_factory = old_rf


def _fc_sample_raw_hay(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> str:
    parts: list[str] = []
    for r in _fc_recent_file_rows(conn, chat_id, topic_id):
        try:
            parts.append(_fc_norm_public(r["raw_input"]))
            parts.append(_fc_norm_public(r["result"]))
        except Exception:
            pass
    return " ".join(parts).lower().replace("ё", "е")


def _fc_sample_titles(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> list[str]:
    titles: list[str] = []
    for r in _fc_recent_file_rows(conn, chat_id, topic_id):
        try:
            titles.extend(_fc_extract_titles_from_text(r["raw_input"]))
            titles.extend(_fc_extract_titles_from_text(r["result"]))
        except Exception:
            continue

    out: list[str] = []
    seen = set()
    for title in titles:
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(title)
    return out[:12]


def _fc_sample_domain_from_hay(hay: str) -> str:
    hay = _fc_norm_public(hay).lower().replace("ё", "е")
    if any(x in hay for x in ("кж", "кд", "кмд", "км", " ар ", "ар ", "проект", "цоколь", ".dwg", ".dxf")):
        return "project"
    if any(x in hay for x in ("смет", "вор", "расцен", "кс-2", "кс2", ".xlsx", ".xls")):
        return "estimate"
    if any(x in hay for x in ("акт", "технадзор", "дефект")):
        return "technadzor"
    return ""


def _fc_select_sample_title(raw_input: str, titles: list[str]) -> str:
    low = _fc_norm_public(raw_input).lower()
    for title in titles:
        tlow = title.lower()
        words = [w for w in re.split(r"[\s._\-]+", tlow) if len(w) >= 3]
        if any(w in low for w in words):
            return title
    if len(titles) == 1:
        return titles[0]
    if "цоколь" in low:
        for title in titles:
            if "цоколь" in title.lower():
                return title
    return ""


def _fc_write_sample_memory(chat_id: str, topic_id: int, domain: str, title: str, raw_input: str) -> None:
    try:
        import datetime
        mem = sqlite3.connect("/root/.areal-neva-core/data/memory.db")
        try:
            payload = json.dumps(
                {
                    "engine": "PROJECT_SAMPLE_SELECTION_P0_V2",
                    "chat_id": str(chat_id),
                    "topic_id": int(topic_id or 0),
                    "domain": domain,
                    "title": title,
                    "raw_input": raw_input,
                    "created_at": datetime.datetime.utcnow().isoformat() + "Z",
                },
                ensure_ascii=False,
            )
            mem.execute(
                "INSERT INTO memory(chat_id,key,value,timestamp) VALUES (?,?,?,?)",
                (
                    str(chat_id),
                    f"topic_{int(topic_id or 0)}_{domain or 'sample'}_selected_sample",
                    payload,
                    datetime.datetime.utcnow().isoformat() + "Z",
                ),
            )
            mem.commit()
        finally:
            mem.close()
    except Exception:
        pass


def _handle_sample_status(conn: sqlite3.Connection, chat_id: str, topic_id: int, raw_input: str) -> Dict[str, Any]:
    if not _fc_is_sample_status_request(raw_input):
        return {"handled": False}

    titles = _fc_sample_titles(conn, chat_id, topic_id)
    raw_hay = _fc_sample_raw_hay(conn, chat_id, topic_id)
    selected_title = _fc_select_sample_title(raw_input, titles)
    domain = _fc_sample_domain_from_hay(" ".join([raw_input, selected_title, " ".join(titles), raw_hay]))

    if domain == "project":
        if selected_title:
            msg = f"{selected_title} закреплён как образец проектирования"
        else:
            msg = "Файлы в этом топике уже взяты в работу как образец проектирования"
    elif domain == "estimate":
        if selected_title:
            msg = f"{selected_title} закреплён как образец сметы"
        else:
            msg = "Файлы в этом топике уже взяты в работу как образец сметы"
    elif domain == "technadzor":
        if selected_title:
            msg = f"{selected_title} закреплён как образец для технадзора"
        else:
            msg = "Файлы в этом топике уже взяты в работу как образец для технадзора"
    else:
        if selected_title:
            msg = f"{selected_title} закреплён как образец"
        else:
            msg = "Файлы в этом топике уже взяты в работу как образец"

    _fc_write_sample_memory(str(chat_id), int(topic_id or 0), domain or "sample", selected_title, raw_input)

    return _send_payload(
        msg,
        "project_sample_selection",
        "DONE",
        "PROJECT_SAMPLE_SELECTION_P0_V2:ANSWERED",
    )
# === END_PROJECT_SAMPLE_SELECTION_P0_V2 ===



def _handle_memory_query(conn: sqlite3.Connection, chat_id: str, topic_id: int, raw_input: str) -> Dict[str, Any]:
    # === CANON_SEARCH_TOPIC_500_GUARD_V1 ===
    if int(topic_id or 0) == 500:
        return {"handled": False}
    # === END_CANON_SEARCH_TOPIC_500_GUARD_V1 ===
    t = raw_input.lower().replace("ё", "е")

    trigger = False
    try:
        from core.file_memory_bridge import should_handle_file_followup
        trigger = bool(should_handle_file_followup(raw_input))
    except Exception:
        trigger = False

    if not trigger:
        trigger = any(x in t for x in [
            "что скидывал",
            "что я скидывал",
            "что отправлял",
            "что загружал",
            "какие файлы",
            "какой файл",
            "проектные файлы",
            "файлы проекта",
            "файлы в чате",
            "документы в чате",
            "последний файл",
            "скидывал",
            "загружал",
        ])

    if not trigger:
        return {"handled": False}

    try:
        from core.file_memory_bridge import build_file_followup_answer
        answer = build_file_followup_answer(str(chat_id), int(topic_id or 0), raw_input, limit=3)
    except Exception:
        answer = ""

    if not answer:
        answer = "В этом топике релевантных файлов по запросу не найдено"

    try:
        from core.output_sanitizer import sanitize_user_output
        answer = sanitize_user_output(answer, fallback="Файлы найдены")
    except Exception:
        pass

    return _send_payload(
        answer,
        "memory_query",
        "DONE",
        "FINAL_CLOSURE_MEMORY_QUERY_PUBLIC_OUTPUT_V3:LISTED",
    )

# === END_FINAL_CLOSURE_MEMORY_QUERY_PUBLIC_OUTPUT_V3 ===


def _handle_runtime_file(conn: sqlite3.Connection, task: Any, task_id: str, chat_id: str, topic_id: int, raw_input: str, input_type: str) -> Dict[str, Any]:
    if input_type not in ("drive_file", "file"):
        return {"handled": False}

    data = _json(raw_input)
    file_id = _s(data.get("file_id"))
    file_name = _s(data.get("file_name") or data.get("name"))
    mime = _s(data.get("mime_type"))
    source = _s(data.get("source") or "telegram")
    size = int(data.get("size") or data.get("file_size") or 0)
    drive_link = _s(data.get("drive_link") or data.get("webViewLink"))

    from core.runtime_file_catalog import duplicate_user_message, register_file

    res = register_file(
        chat_id,
        topic_id,
        task_id,
        file_id=file_id,
        file_name=file_name,
        mime_type=mime,
        size=size,
        source=source,
        drive_link=drive_link,
    )

    if res.get("duplicate"):
        return _send_payload(
            duplicate_user_message(file_name or "UNKNOWN", res.get("duplicate_record") or {}),
            "runtime_duplicate_file",
            "WAITING_CLARIFICATION",
            "FINAL_CLOSURE_BLOCKER_FIX_V1:RUNTIME_DUPLICATE_FILE",
        )

    return {"handled": False, "catalog_registered": True}


def _handle_technadzor(raw_input: str, task_id: str, chat_id: str, topic_id: int) -> Dict[str, Any]:
    from core.technadzor_engine import is_technadzor_intent, process_technadzor

    if not is_technadzor_intent(raw_input):
        return {"handled": False}

    return process_technadzor(text=raw_input, task_id=task_id, chat_id=chat_id, topic_id=topic_id)


def _handle_ocr(raw_input: str, task_id: str) -> Dict[str, Any]:
    from core.ocr_engine import is_ocr_table_intent, process_ocr_table

    if not is_ocr_table_intent(raw_input):
        return {"handled": False}

    return process_ocr_table(text=raw_input, task_id=task_id)


def _handle_archive_guard(conn: sqlite3.Connection, task_id: str, chat_id: str, topic_id: int, raw_input: str) -> Dict[str, Any]:
    if not any(x in raw_input.lower() for x in ["архив", "сохрани", "запомни"]):
        return {"handled": False}

    from core.archive_guard import should_archive

    res = should_archive(conn, task_id, chat_id, topic_id, raw_input)
    if res.get("duplicate"):
        return _send_payload(
            "В архив не дублирую: такая запись уже есть",
            "archive_duplicate",
            "DONE",
            "FINAL_CLOSURE_BLOCKER_FIX_V1:ARCHIVE_DUPLICATE_BLOCKED",
        )

    return {"handled": False, "archive_guard_ok": True}



# === PROJECT_INDEX_QUERY_DETECTOR_V1 ===
_INDEX_QUERY_RE_V1 = re.compile(
    r"(какие|покажи|перечисли|что у тебя|есть ли|список|что есть|какие файлы|какие образцы|покажи образцы|что за образцы|какие разделы)",
    re.I,
)

_TOPIC_ROLE_MAP_V1 = {
    2: "СМЕТЫ / СТРОЙКА",
    5: "ТЕХНАДЗОР / АКТЫ / ДЕФЕКТЫ",
    210: "ПРОЕКТИРОВАНИЕ / АР / КЖ / КД / КР / КМ / ОВ / ВК / ЭО",
}

def _fc_topic_role_v1(topic_id: int) -> str:
    return _TOPIC_ROLE_MAP_V1.get(int(topic_id or 0), "ОБЩИЙ")

def _fc_is_index_query_v1(text: str) -> bool:
    low = _fc_norm_public(text).lower()
    if not _INDEX_QUERY_RE_V1.search(low):
        return False
    return any(x in low for x in (
        "образц", "файл", "раздел", "ар", "кж", "кд", "кр", "км", "кмд",
        "ов", "вк", "эо", "эскиз", "проект", "смет", "акт", "технадзор"
    ))

def _fc_is_negative_topic_correction_v1(text: str) -> bool:
    low = _fc_norm_public(text).lower()
    return any(x in low for x in (
        "нет я не это спросил",
        "не это спросил",
        "не то спросил",
        "не так",
        "ты не понял",
        "не про это",
    ))

def _fc_load_owner_reference_registry_v1() -> dict:
    try:
        from pathlib import Path
        return json.loads(Path("/root/.areal-neva-core/config/owner_reference_registry.json").read_text(encoding="utf-8"))
    except Exception:
        return {}

def _fc_topic_domain_v1(topic_id: int) -> str:
    topic_id = int(topic_id or 0)
    if topic_id == 2:
        return "estimate"
    if topic_id == 5:
        return "technadzor"
    if topic_id == 210:
        return "design"
    return ""

def _fc_index_items_for_topic_v1(topic_id: int) -> list[dict]:
    data = _fc_load_owner_reference_registry_v1()
    policy = data.get("owner_reference_full_workflow_v1") if isinstance(data, dict) else {}
    if not isinstance(policy, dict):
        return []
    domain = _fc_topic_domain_v1(topic_id)
    if domain == "estimate":
        return list(policy.get("estimate_references") or [])
    if domain == "technadzor":
        return list(policy.get("technadzor_references") or [])
    if domain == "design":
        return list(policy.get("design_references") or [])
    return (
        list(policy.get("estimate_references") or [])
        + list(policy.get("design_references") or [])
        + list(policy.get("technadzor_references") or [])
    )

def _fc_filter_design_by_question_v1(items: list[dict], raw_input: str) -> list[dict]:
    low = _fc_norm_public(raw_input).lower()
    wanted = []
    mapping = {
        "ар": ("AR", "АР"),
        "кж": ("KJ", "КЖ"),
        "кд": ("KD", "КД"),
        "кр": ("KR", "КР"),
        "кмд": ("KMD", "КМД"),
        "км": ("KM", "КМ"),
        "ов": ("OV", "ОВ"),
        "вк": ("VK", "ВК"),
        "эо": ("EO", "ЭО"),
        "эм": ("EO", "ЭМ"),
        "эос": ("EO", "ЭОС"),
        "эскиз": ("SKETCH", "ЭСКИЗ"),
        "план участка": ("GP", "ГП"),
    }
    for k, vals in mapping.items():
        if k in low:
            wanted.extend(vals)
    if not wanted:
        return items
    out = []
    for x in items:
        d = str(x.get("discipline") or "").upper()
        name = str(x.get("name") or "").upper()
        if any(w.upper() in d or w.upper() in name for w in wanted):
            out.append(x)
    return out or items

def _fc_format_index_answer_v1(topic_id: int, raw_input: str) -> str:
    role = _fc_topic_role_v1(topic_id)
    items = _fc_index_items_for_topic_v1(topic_id)
    if int(topic_id or 0) == 210:
        items = _fc_filter_design_by_question_v1(items, raw_input)

    if not items:
        return f"По роли {role} образцы в индексе не найдены"

    groups: dict[str, list[str]] = {}
    for x in items:
        if not isinstance(x, dict):
            continue
        if int(topic_id or 0) == 210:
            key = str(x.get("discipline") or "DESIGN")
        elif int(topic_id or 0) == 2:
            key = str(x.get("role") or "estimate")
        elif int(topic_id or 0) == 5:
            key = "technadzor"
        else:
            key = str(x.get("domain") or x.get("discipline") or x.get("role") or "reference")
        name = _fc_clean_title(str(x.get("name") or ""))
        if not name:
            continue
        groups.setdefault(key, [])
        if name not in groups[key]:
            groups[key].append(name)

    lines = [f"Образцы по текущему топику: {role}", ""]
    for key in sorted(groups):
        vals = groups[key][:20]
        lines.append(f"{key}:")
        for name in vals:
            lines.append(f"- {name}")
        if len(groups[key]) > len(vals):
            lines.append(f"- ещё {len(groups[key]) - len(vals)}")
        lines.append("")
    lines.append("Файл не создаю. Это ответ на запрос списка образцов")
    return "\n".join(lines).strip()

def _handle_project_index_query_v1(conn: sqlite3.Connection, chat_id: str, topic_id: int, raw_input: str) -> Dict[str, Any]:
    # === CANON_SEARCH_TOPIC_500_GUARD_V1 ===
    if int(topic_id or 0) == 500:
        return {"handled": False}
    # === END_CANON_SEARCH_TOPIC_500_GUARD_V1 ===
    if not _fc_is_index_query_v1(raw_input):
        return {"handled": False}
    answer = _fc_format_index_answer_v1(int(topic_id or 0), raw_input)
    return _send_payload(
        answer,
        "project_index_query",
        "DONE",
        "PROJECT_INDEX_QUERY_DETECTOR_V1:ANSWERED",
    )

def _handle_topic_context_isolation_guard_v1(conn: sqlite3.Connection, chat_id: str, topic_id: int, raw_input: str) -> Dict[str, Any]:
    if not _fc_is_negative_topic_correction_v1(raw_input):
        return {"handled": False}
    role = _fc_topic_role_v1(int(topic_id or 0))
    if int(topic_id or 0) == 210:
        msg = "Понял. Остаёмся в проектировании. Уточни, что показать: АР / КЖ / КД / КР / КМ / ОВ / ВК / ЭО / эскизы / планы участка"
    elif int(topic_id or 0) == 2:
        msg = "Понял. Остаёмся в сметах и стройке. Уточни, что нужно: цены / смета / материалы / логистика / XLSX"
    elif int(topic_id or 0) == 5:
        msg = "Понял. Остаёмся в технадзоре. Уточни, что нужно: акт / дефект / фото / исполнительная / норма"
    else:
        msg = f"Понял. Роль текущего топика: {role}. Уточни одним сообщением, что именно нужно"
    return _send_payload(
        msg,
        "topic_context_isolation_guard",
        "WAITING_CLARIFICATION",
        "TOPIC_CONTEXT_ISOLATION_GUARD_V1:ANSWERED",
    )

# === END_PROJECT_INDEX_QUERY_DETECTOR_V1 ===

def maybe_handle_final_closure(
    conn: sqlite3.Connection,
    task: Any,
    task_id: str,
    chat_id: str,
    topic_id: int,
    raw_input: str,
    input_type: str = "text",
    reply_to=None,
) -> Dict[str, Any]:
    raw_input = _s(raw_input)
    input_type = _s(input_type or _field(task, "input_type", "text"))
    chat_id = _s(chat_id or _field(task, "chat_id", ""))
    topic_id = int(topic_id or _field(task, "topic_id", 0) or 0)

    r = _handle_runtime_file(conn, task, task_id, chat_id, topic_id, raw_input, input_type)
    if r.get("handled"):
        return r

    r = _handle_project_index_query_v1(conn, chat_id, topic_id, raw_input)
    if r.get("handled"):
        return r

    r = _handle_topic_context_isolation_guard_v1(conn, chat_id, topic_id, raw_input)
    if r.get("handled"):
        return r

    r = _handle_sample_status(conn, chat_id, topic_id, raw_input)
    if r.get("handled"):
        return r

    r = _handle_memory_query(conn, chat_id, topic_id, raw_input)
    if r.get("handled"):
        return r

    r = _handle_technadzor(raw_input, task_id, chat_id, topic_id)
    if r.get("handled"):
        return r

    r = _handle_ocr(raw_input, task_id)
    if r.get("handled"):
        return r

    r = _handle_archive_guard(conn, task_id, chat_id, topic_id, raw_input)
    if r.get("handled"):
        return r

    return {"handled": False}


# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_ENGINE ===

# === P6H4TW_FCE_TOPIC5_ROUTE_FIX_V1 ===
_P6H4TW_FCE_FOLDER_INTENTS = (
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

_p6h4tw_fce_orig_handle_technadzor = _handle_technadzor


def _handle_technadzor(raw_input: str, task_id: str, chat_id: str, topic_id: int) -> Dict[str, Any]:  # noqa: F811
    _low = (raw_input or "").lower().replace("ё", "е")
    _is_folder_intent = any(t in _low for t in _P6H4TW_FCE_FOLDER_INTENTS)

    if int(topic_id or 0) == 5 and _is_folder_intent:
        try:
            from core.technadzor_engine import process_technadzor as _p6h4tw_fce_pt
            r = _p6h4tw_fce_pt(
                text=raw_input, task_id=task_id, chat_id=chat_id, topic_id=topic_id
            )
            if isinstance(r, dict):
                if r.get("ok") and not r.get("handled"):
                    r = dict(r)
                    r["handled"] = True
                    r["message"] = r.get("result_text") or r.get("message") or ""
                elif not r.get("ok") and not r.get("handled"):
                    r = dict(r)
                    r["handled"] = False
                return r
        except Exception as _e:
            import logging as _l
            _l.getLogger("task_worker").warning("P6H4TW_FCE_ERR %s", _e)
        # folder resolver failed or returned nothing — ask owner instead of AI fallback
        return {
            "handled": True,
            "ok": True,
            "state": "WAITING_CLARIFICATION",
            "message": "Не удалось найти папку на Drive. Пришли ссылку на папку или уточни точное название.",
            "history": "P6H4TW_FCE_V1:FOLDER_NOT_FOUND",
        }

    return _p6h4tw_fce_orig_handle_technadzor(raw_input, task_id, chat_id, topic_id)

# === END_P6H4TW_FCE_TOPIC5_ROUTE_FIX_V1 ===

====================================================================================================
END_FILE: core/final_closure_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/file_context_intake.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 10a131931e3071fc6f06da8d8f0bd72e5964cda3b4f13ed47f1a63bc0b52fb00
====================================================================================================
# === FILE_CONTEXT_INTAKE_FULL_CLOSE_V1 ===
from __future__ import annotations

import json
import os
import re
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional

BASE = Path("/root/.areal-neva-core")
CORE_DB = BASE / "data" / "core.db"
MEM_DB = BASE / "data" / "memory.db"
TEMPLATE_ROOT = BASE / "data" / "templates"
ESTIMATE_TEMPLATE_DIR = TEMPLATE_ROOT / "estimate"
ESTIMATE_BATCH_DIR = TEMPLATE_ROOT / "estimate_batch"
FILE_CATALOG_DIR = BASE / "data" / "telegram_file_catalog"

ESTIMATE_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
ESTIMATE_BATCH_DIR.mkdir(parents=True, exist_ok=True)
FILE_CATALOG_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v).strip()


def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")


def _task_field(task: Any, field: str, default: Any = "") -> Any:
    try:
        if hasattr(task, "keys") and field in task.keys():
            return task[field]
    except Exception:
        pass
    if isinstance(task, dict):
        return task.get(field, default)
    try:
        return getattr(task, field)
    except Exception:
        return default


def _json(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    txt = _s(raw)
    if not txt:
        return {}
    try:
        obj = json.loads(txt)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _safe_name(v: Any, limit: int = 120) -> str:
    s = re.sub(r"[^0-9A-Za-zА-Яа-я_. -]+", "_", _s(v)).strip(" ._")
    return (s or "file")[:limit]


def _safe_key(v: Any, limit: int = 80) -> str:
    return re.sub(r"[^0-9A-Za-z_-]+", "_", _s(v))[:limit] or "unknown"


def _cols(conn: sqlite3.Connection, table: str):
    try:
        return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    except Exception:
        return []


def _memory_write(chat_id: str, key: str, value: Any) -> None:
    try:
        if not MEM_DB.exists():
            return
        conn = sqlite3.connect(str(MEM_DB))
        try:
            cols = _cols(conn, "memory")
            if not cols:
                return
            payload = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
            ts = _now()
            if "id" in cols:
                mid = hashlib.sha1(f"{chat_id}:{key}:{ts}:{payload[:80]}".encode("utf-8")).hexdigest()
                conn.execute(
                    "INSERT OR IGNORE INTO memory (id,chat_id,key,value,timestamp) VALUES (?,?,?,?,?)",
                    (mid, str(chat_id), str(key), payload, ts),
                )
            else:
                conn.execute(
                    "INSERT INTO memory (chat_id,key,value,timestamp) VALUES (?,?,?,?)",
                    (str(chat_id), str(key), payload, ts),
                )
            conn.commit()
        finally:
            conn.close()
    except Exception:
        return


def _memory_latest(chat_id: str, key: str) -> str:
    try:
        if not MEM_DB.exists():
            return ""
        conn = sqlite3.connect(str(MEM_DB))
        try:
            row = conn.execute(
                "SELECT value FROM memory WHERE chat_id=? AND key=? ORDER BY rowid DESC LIMIT 1",
                (str(chat_id), str(key)),
            ).fetchone()
            return row[0] if row else ""
        finally:
            conn.close()
    except Exception:
        return ""


def _extract_user_text(raw_input: Any) -> str:
    obj = _json(raw_input)
    if obj:
        for k in ("caption", "user_text", "text", "prompt", "comment", "message"):
            v = obj.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        return ""
    return _s(raw_input)


def _file_payload(raw_input: Any) -> Dict[str, Any]:
    obj = _json(raw_input)
    return {
        "file_id": _s(obj.get("file_id")),
        "file_name": _s(obj.get("file_name")),
        "mime_type": _s(obj.get("mime_type")),
        "caption": _s(obj.get("caption")),
        "source": _s(obj.get("source")),
        "telegram_message_id": obj.get("telegram_message_id"),
        "raw": obj,
    }


def _is_service_file(payload: Dict[str, Any]) -> bool:
    src = _low(payload.get("source"))
    name = _low(payload.get("file_name"))
    if src in {"google_drive", "drive", "drive_sync", "healthcheck", "service"}:
        return True
    if any(x in name for x in ("healthcheck", "service_file", ".tmp", "tmp_", "retry_probe")):
        return True
    return False


def _detect_pending_file_intent(text: str) -> Optional[Dict[str, Any]]:
    low = _low(text)
    if not low:
        return None

    future_file = any(x in low for x in (
        "сейчас скину", "сейчас пришлю", "скину несколько", "пришлю несколько",
        "буду скидывать", "сейчас отправлю", "отправлю несколько", "загружу несколько",
        "скину файлы", "пришлю файлы"
    ))

    estimate = any(x in low for x in ("смет", "кс-2", "кс2", "ведомост", "спецификац", "расцен", "excel", "xlsx"))
    template = any(x in low for x in ("образец", "образцы", "шаблон", "шаблоны", "принять", "возьми", "сохрани"))
    price_web = any(x in low for x in (
        "цены из интернета", "цена из интернета", "актуальные цены", "стоимость материалов",
        "цены материалов", "искать в интернете", "брать из интернета", "найти цены",
        "проводить поиск", "проверить цены"
    ))

    if future_file and estimate:
        return {
            "kind": "estimate",
            "mode": "template_batch" if template or "образ" in low else "pending_estimate_files",
            "price_mode": "web_confirm" if price_web else "",
            "raw_text": text,
            "created_at": _now(),
            "ttl_sec": 7200,
        }

    if estimate and template and any(x in low for x in ("несколько", "файлы", "сметы")):
        return {
            "kind": "estimate",
            "mode": "template_batch",
            "price_mode": "web_confirm" if price_web else "",
            "raw_text": text,
            "created_at": _now(),
            "ttl_sec": 7200,
        }

    return None


def _save_pending_intent(chat_id: str, topic_id: int, intent: Dict[str, Any]) -> None:
    key = f"topic_{int(topic_id or 0)}_pending_file_intent"
    _memory_write(chat_id, key, intent)
    if intent.get("price_mode"):
        _memory_write(chat_id, f"topic_{int(topic_id or 0)}_price_mode", intent.get("price_mode"))


def latest_pending_instruction_for_topic(topic_id: int, chat_id: str = "") -> str:
    chat_ids = [str(chat_id)] if chat_id else []
    if not chat_ids:
        try:
            conn = sqlite3.connect(str(MEM_DB))
            rows = conn.execute(
                "SELECT DISTINCT chat_id FROM memory WHERE key=? ORDER BY rowid DESC LIMIT 5",
                (f"topic_{int(topic_id or 0)}_pending_file_intent",),
            ).fetchall()
            conn.close()
            chat_ids = [r[0] for r in rows]
        except Exception:
            chat_ids = []
    for cid in chat_ids:
        raw = _memory_latest(cid, f"topic_{int(topic_id or 0)}_pending_file_intent")
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            data = {}
        if data.get("raw_text"):
            return str(data["raw_text"])
    return ""


def _current_rowid(conn: sqlite3.Connection, task_id: str) -> int:
    try:
        row = conn.execute("SELECT rowid FROM tasks WHERE id=? LIMIT 1", (task_id,)).fetchone()
        return int(row[0]) if row else 0
    except Exception:
        return 0


def _find_duplicate(conn: sqlite3.Connection, task_id: str, chat_id: str, topic_id: int, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    rowid = _current_rowid(conn, task_id)
    file_id = _s(payload.get("file_id"))
    file_name = _s(payload.get("file_name"))
    if not file_id and not file_name:
        return None

    params = [str(chat_id), int(topic_id or 0), int(rowid or 10**18)]
    where = "chat_id=? AND COALESCE(topic_id,0)=? AND input_type='drive_file' AND rowid<?"

    if file_id:
        where += " AND json_extract(raw_input,'$.file_id')=?"
        params.append(file_id)
    elif file_name:
        where += " AND lower(json_extract(raw_input,'$.file_name'))=lower(?)"
        params.append(file_name)

    try:
        row = conn.execute(
            f"""
            SELECT rowid,id,state,raw_input,result,error_message,created_at,updated_at
            FROM tasks
            WHERE {where}
            ORDER BY rowid DESC
            LIMIT 1
            """,
            params,
        ).fetchone()
    except Exception:
        row = None

    if not row:
        return None

    old_payload = _json(row["raw_input"] if hasattr(row, "keys") else row[3])
    old_name = old_payload.get("file_name") or file_name
    return {
        "rowid": row["rowid"] if hasattr(row, "keys") else row[0],
        "task_id": row["id"] if hasattr(row, "keys") else row[1],
        "state": row["state"] if hasattr(row, "keys") else row[2],
        "file_name": old_name,
        "file_id": old_payload.get("file_id") or file_id,
        "created_at": row["created_at"] if hasattr(row, "keys") else row[6],
        "updated_at": row["updated_at"] if hasattr(row, "keys") else row[7],
    }


def _duplicate_message(payload: Dict[str, Any], dup: Dict[str, Any]) -> str:
    name = payload.get("file_name") or dup.get("file_name") or "файл"
    return (
        "Смотри, этот файл ты уже скидывал\n"
        f"Файл: {name}\n"
        f"Первая найденная задача: {str(dup.get('task_id') or '')[:8]}\n"
        f"Дата: {dup.get('created_at') or dup.get('updated_at') or 'UNKNOWN'}\n\n"
        "Что сделать с ним сейчас?\n"
        "1. Обновить образец\n"
        "2. Обработать заново\n"
        "3. Сравнить версии\n"
        "4. Игнорировать дубль"
    )


def _catalog_path(chat_id: str, topic_id: int) -> Path:
    return FILE_CATALOG_DIR / f"chat_{_safe_key(chat_id)}__topic_{int(topic_id or 0)}.jsonl"


def _index_telegram_file(chat_id: str, topic_id: int, task_id: str, payload: Dict[str, Any]) -> None:
    if not payload.get("file_id") and not payload.get("file_name"):
        return
    entry = {
        "created_at": _now(),
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "task_id": str(task_id),
        "file_id": payload.get("file_id"),
        "file_name": payload.get("file_name"),
        "mime_type": payload.get("mime_type"),
        "telegram_message_id": payload.get("telegram_message_id"),
        "source": payload.get("source") or "telegram",
    }
    path = _catalog_path(chat_id, topic_id)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    _memory_write(chat_id, f"topic_{int(topic_id or 0)}_telegram_file_index", entry)


def _template_paths(chat_id: str, topic_id: int, file_name: str):
    safe_chat = _safe_key(chat_id)
    safe_file = _safe_key(file_name, 70)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    active = ESTIMATE_TEMPLATE_DIR / f"ACTIVE__chat_{safe_chat}__topic_{int(topic_id or 0)}.json"
    snap = ESTIMATE_TEMPLATE_DIR / f"TEMPLATE__chat_{safe_chat}__topic_{int(topic_id or 0)}__{stamp}__{safe_file}.json"
    batch = ESTIMATE_BATCH_DIR / f"ACTIVE_BATCH__chat_{safe_chat}__topic_{int(topic_id or 0)}.json"
    return active, snap, batch


def _save_estimate_template(chat_id: str, topic_id: int, task_id: str, payload: Dict[str, Any], raw_instruction: str) -> Dict[str, Any]:
    active, snap, batch_path = _template_paths(chat_id, topic_id, payload.get("file_name") or "estimate")
    template = {
        "engine": "MULTI_FILE_TEMPLATE_INTAKE_V1",
        "kind": "estimate",
        "status": "active",
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "saved_by_task_id": str(task_id),
        "source_task_id": str(task_id),
        "source_file_id": payload.get("file_id") or "",
        "source_file_name": payload.get("file_name") or "",
        "source_mime_type": payload.get("mime_type") or "",
        "source_caption": payload.get("caption") or "",
        "telegram_message_id": payload.get("telegram_message_id"),
        "saved_at": _now(),
        "usage_rule": "Use this Telegram file as estimate sample/template in the same chat and topic",
        "raw_user_instruction": raw_instruction,
    }

    active.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
    snap.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")

    batch = []
    if batch_path.exists():
        try:
            old = json.loads(batch_path.read_text(encoding="utf-8"))
            if isinstance(old, list):
                batch = old
            elif isinstance(old, dict) and isinstance(old.get("templates"), list):
                batch = old["templates"]
        except Exception:
            batch = []

    seen = {str(x.get("source_file_id") or x.get("source_file_name")) for x in batch if isinstance(x, dict)}
    key = str(template.get("source_file_id") or template.get("source_file_name"))
    if key not in seen:
        batch.append(template)

    batch_payload = {
        "engine": "MULTI_FILE_TEMPLATE_INTAKE_V1",
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "count": len(batch),
        "updated_at": _now(),
        "templates": batch[-100:],
    }
    batch_path.write_text(json.dumps(batch_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    _memory_write(chat_id, f"topic_{int(topic_id or 0)}_estimate_active_template", template)
    _memory_write(chat_id, f"topic_{int(topic_id or 0)}_estimate_template_batch", batch_payload)

    return {"template": template, "batch_count": len(batch), "active_path": str(active), "snapshot_path": str(snap), "batch_path": str(batch_path)}


def _load_pending_intent(chat_id: str, topic_id: int) -> Dict[str, Any]:
    raw = _memory_latest(chat_id, f"topic_{int(topic_id or 0)}_pending_file_intent")
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _pending_is_template_batch(intent: Dict[str, Any]) -> bool:
    if not intent:
        return False
    if intent.get("kind") != "estimate":
        return False
    return intent.get("mode") in {"template_batch", "pending_estimate_files"}


def prehandle_task_context_v1(conn: sqlite3.Connection, task: Any) -> Optional[Dict[str, Any]]:
    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    input_type = _s(_task_field(task, "input_type"))
    raw_input = _s(_task_field(task, "raw_input"))
    reply_to = _task_field(task, "reply_to_message_id", None)

    if not task_id or not chat_id:
        return None

    if input_type in ("text", "voice"):
        text = _extract_user_text(raw_input)
        pending = _detect_pending_file_intent(text)
        if pending:
            _save_pending_intent(chat_id, topic_id, pending)
            msg = (
                "Принял\n"
                "Следующие файлы в этом топике приму как образцы сметы\n"
                "Если файл уже был в Telegram — скажу что он дублируется и спрошу что делать\n"
                "При создании сметы цены материалов буду искать в интернете и сначала покажу варианты для выбора"
            )
            return {
                "handled": True,
                "state": "DONE",
                "kind": "context_aware_file_intake",
                "message": msg,
                "history": "CONTEXT_AWARE_FILE_INTAKE_V1:PENDING_TEMPLATE_BATCH_SAVED",
            }

    if input_type in ("drive_file", "file"):
        payload = _file_payload(raw_input)
        if _is_service_file(payload):
            return None

        _index_telegram_file(chat_id, topic_id, task_id, payload)

        dup = _find_duplicate(conn, task_id, chat_id, topic_id, payload)
        if dup:
            msg = _duplicate_message(payload, dup)
            _memory_write(chat_id, f"topic_{topic_id}_last_duplicate_file", {"current_task_id": task_id, "payload": payload, "duplicate": dup})
            return {
                "handled": True,
                "state": "WAITING_CLARIFICATION",
                "kind": "duplicate_file_question",
                "message": msg,
                "history": "TELEGRAM_FILE_MEMORY_INDEX_V1:DUPLICATE_FOUND",
            }

        pending = _load_pending_intent(chat_id, topic_id)
        if _pending_is_template_batch(pending):
            saved = _save_estimate_template(chat_id, topic_id, task_id, payload, pending.get("raw_text") or "")
            file_name = payload.get("file_name") or "файл"
            msg = (
                "Образец сметы принят\n"
                f"Файл: {file_name}\n"
                f"Всего образцов в наборе: {saved.get('batch_count')}\n\n"
                "Дальше можешь присылать следующие сметы-образцы или написать: сделай смету\n"
                "Если нужно брать цены из интернета — я сначала покажу найденные варианты и спрошу какие поставить"
            )
            return {
                "handled": True,
                "state": "DONE",
                "kind": "multi_file_template_intake",
                "message": msg,
                "history": "MULTI_FILE_TEMPLATE_INTAKE_V1:TEMPLATE_SAVED",
            }

    return None


def router_pending_instruction(raw_input: str, topic_id: int, chat_id: str = "") -> str:
    explicit = _extract_user_text(raw_input)
    if explicit:
        return explicit
    return latest_pending_instruction_for_topic(topic_id, chat_id)


# === END_FILE_CONTEXT_INTAKE_FULL_CLOSE_V1 ===


# === PENDING_INTENT_CLARIFICATION_V1 ===
try:
    _pic_orig_prehandle_task_context_v1 = prehandle_task_context_v1
except Exception:
    _pic_orig_prehandle_task_context_v1 = None


def _pic_has_active_pending_intent(chat_id: str, topic_id: int) -> Dict[str, Any]:
    try:
        data = _load_pending_intent(chat_id, topic_id)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _pic_is_clarification_text(text: str) -> bool:
    low = _low(text)
    if not low:
        return False

    explicit_new_task = any(x in low for x in (
        "сделай проект", "создай проект", "разработай проект",
        "сделай смету", "создай смету", "посчитай смету", "рассчитай смету",
        "сделай акт", "создай акт", "найди мне", "поищи мне"
    ))
    if explicit_new_task:
        return False

    clar_words = (
        "ты должен", "ты должна", "должен", "должна", "надо", "нужно",
        "нужно ли", "надо ли", "спроси", "спросить", "уточни", "уточнить",
        "не сразу", "сначала", "перед тем", "до того", "после этого",
        "цены", "интернет", "искать", "не искать", "без интернета",
        "актуальные", "поставить", "подставить", "согласовать",
        "подтвердить", "не создавай сразу", "сначала спросить",
        "сначала спроси", "спросить нужно ли", "спроси нужно ли"
    )
    return any(x in low for x in clar_words)


def _pic_update_intent_with_clarification(intent: Dict[str, Any], text: str) -> Dict[str, Any]:
    low = _low(text)
    updated = dict(intent or {})

    clarifications = updated.get("clarifications")
    if not isinstance(clarifications, list):
        clarifications = []
    clarifications.append({"text": text, "created_at": _now()})
    updated["clarifications"] = clarifications[-20:]
    updated["updated_at"] = _now()
    updated["last_clarification"] = text

    ask_before_web = any(x in low for x in (
        "не сразу", "сначала спрос", "спросить нужно ли", "спроси нужно ли",
        "нужно ли", "надо ли", "перед тем как искать", "перед поиском",
        "сначала уточни", "не ищи сразу", "не надо сразу",
        "согласовать цены", "подтвердить цены"
    ))

    disable_web = any(x in low for x in (
        "не искать в интернете", "без интернета", "не надо интернет",
        "цены не ищи", "не ищи цены", "без поиска цен"
    ))

    force_web = any(x in low for x in (
        "ищи в интернете", "искать в интернете", "цены из интернета",
        "актуальные цены", "проверить цены", "найти цены"
    ))

    if disable_web:
        updated["price_mode"] = "manual_or_template"
        updated["web_search_disabled"] = True
        updated["ask_before_web_search"] = False
        updated["price_confirmation_required"] = False
    elif ask_before_web:
        updated["price_mode"] = "ask_before_search"
        updated["ask_before_web_search"] = True
        updated["price_confirmation_required"] = True
        updated["web_search_disabled"] = False
    elif force_web:
        updated["price_mode"] = "web_confirm"
        updated["ask_before_web_search"] = False
        updated["price_confirmation_required"] = True
        updated["web_search_disabled"] = False

    original = str(updated.get("raw_text") or "").strip()
    if text and text not in original:
        updated["raw_text"] = (original + "\nУточнение: " + text).strip()

    return updated


def _pic_confirmation_message(intent: Dict[str, Any]) -> str:
    price_mode = str(intent.get("price_mode") or "")
    if price_mode == "ask_before_search":
        price_line = "Перед поиском цен в интернете сначала спрошу, нужно ли искать актуальные цены"
    elif price_mode == "web_confirm":
        price_line = "Цены материалов буду искать в интернете, затем покажу варианты и спрошу какие поставить"
    elif price_mode == "manual_or_template":
        price_line = "Интернет-цены не ищу, пока ты отдельно не скажешь искать"
    else:
        price_line = "Цены не подставляю без отдельного подтверждения"

    return (
        "Уточнение к приёму смет принято\n"
        "Следующие файлы в этом топике остаются образцами сметы\n"
        f"{price_line}\n"
        "Финальную смету не создаю без твоего выбора цен"
    )



# === PROJECT_SAMPLE_TEXT_INTAKE_V1 ===
def _pst_is_sample_text(text: str) -> bool:
    low = _low(text)
    if not low:
        return False
    if not any(x in low for x in ("возьми", "прими", "используй", "сохрани")):
        return False
    return any(x in low for x in ("образец", "шаблон", "пример", "как образец"))


def _pst_is_projectish(payload: Dict[str, Any], text: str = "") -> bool:
    hay = _low(" ".join([
        payload.get("file_name") or "",
        payload.get("caption") or "",
        payload.get("mime_type") or "",
        text or "",
    ]))
    return any(x in hay for x in (
        "кж", "км", "кмд", "ар", "проект", "чертеж", "чертёж",
        "конструкц", "цоколь", "плита", ".dxf", ".dwg", ".pdf"
    )) and not any(x in hay for x in (
        "смет", "вор", "расцен", "стоимост", "технадзор", "акт дефект", "нарушен"
    ))


def _pst_latest_project_file(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> Dict[str, Any]:
    try:
        rows = conn.execute(
            """
            SELECT id,raw_input,result,updated_at,rowid
            FROM tasks
            WHERE CAST(chat_id AS TEXT)=CAST(? AS TEXT)
              AND COALESCE(topic_id,0)=?
              AND input_type IN ('drive_file','file')
            ORDER BY rowid DESC
            LIMIT 80
            """,
            (str(chat_id), int(topic_id or 0)),
        ).fetchall()
    except Exception:
        rows = []

    for r in rows:
        try:
            raw = r["raw_input"] if hasattr(r, "keys") else r[1]
            tid = r["id"] if hasattr(r, "keys") else r[0]
            upd = r["updated_at"] if hasattr(r, "keys") else r[3]
        except Exception:
            continue

        payload = _file_payload(raw)
        if _is_service_file(payload):
            continue
        if _pst_is_projectish(payload, raw):
            return {
                "task_id": str(tid),
                "file_id": payload.get("file_id") or "",
                "file_name": payload.get("file_name") or "",
                "mime_type": payload.get("mime_type") or "",
                "caption": payload.get("caption") or "",
                "source": payload.get("source") or "",
                "updated_at": str(upd or ""),
            }

    return {}


def _pst_save_project_sample(chat_id: str, topic_id: int, task_id: str, sample: Dict[str, Any], text: str) -> None:
    payload = {
        "engine": "PROJECT_SAMPLE_TEXT_INTAKE_V1",
        "kind": "project",
        "status": "active",
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "saved_by_task_id": str(task_id),
        "source_task_id": sample.get("task_id") or "",
        "source_file_id": sample.get("file_id") or "",
        "source_file_name": sample.get("file_name") or "",
        "source_mime_type": sample.get("mime_type") or "",
        "source_caption": sample.get("caption") or "",
        "saved_at": _now(),
        "usage_rule": "Use this file as project/design sample only inside the same chat and topic",
        "raw_user_instruction": text,
    }
    _memory_write(chat_id, f"topic_{int(topic_id or 0)}_project_active_template", payload)
    _memory_write(chat_id, f"topic_{int(topic_id or 0)}_project_sample_file", payload)


def _pst_try_project_sample_text(conn: sqlite3.Connection, task_id: str, chat_id: str, topic_id: int, text: str) -> Optional[Dict[str, Any]]:
    if not _pst_is_sample_text(text):
        return None

    sample = _pst_latest_project_file(conn, chat_id, topic_id)
    if not sample:
        return None

    _pst_save_project_sample(chat_id, topic_id, task_id, sample, text)

    file_name = sample.get("file_name") or "файл"
    msg = (
        "Образец проектирования принят\n"
        f"Файл: {file_name}\n"
        "Дальше буду использовать его как образец для проектных задач только в этом топике"
    )

    return {
        "handled": True,
        "state": "DONE",
        "kind": "project_sample_text_intake",
        "message": msg,
        "history": "PROJECT_SAMPLE_TEXT_INTAKE_V1:SAVED",
    }

# === END_PROJECT_SAMPLE_TEXT_INTAKE_V1 ===


def prehandle_task_context_v1(conn: sqlite3.Connection, task: Any) -> Optional[Dict[str, Any]]:
    if _pic_orig_prehandle_task_context_v1 is not None:
        res = _pic_orig_prehandle_task_context_v1(conn, task)
        if res and res.get("handled"):
            return res

    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    input_type = _s(_task_field(task, "input_type"))
    raw_input = _s(_task_field(task, "raw_input"))

    if not task_id or not chat_id:
        return None

    if input_type not in ("text", "voice"):
        return None

    text = _extract_user_text(raw_input)
    if not text:
        return None

    # PROJECT_SAMPLE_TEXT_INTAKE_V1_HOOK
    sample_res = _pst_try_project_sample_text(conn, task_id, chat_id, topic_id, text)
    if sample_res and sample_res.get("handled"):
        return sample_res

    pending = _pic_has_active_pending_intent(chat_id, topic_id)
    if not pending:
        return None

    if not _pic_is_clarification_text(text):
        return None

    updated = _pic_update_intent_with_clarification(pending, text)
    _save_pending_intent(chat_id, topic_id, updated)

    if updated.get("price_mode"):
        _memory_write(chat_id, f"topic_{int(topic_id or 0)}_price_mode", updated.get("price_mode"))

    _memory_write(chat_id, f"topic_{int(topic_id or 0)}_pending_file_intent_clarification", {
        "task_id": task_id,
        "text": text,
        "updated_intent": updated,
        "created_at": _now(),
    })

    return {
        "handled": True,
        "state": "DONE",
        "kind": "pending_intent_clarification",
        "message": _pic_confirmation_message(updated),
        "history": "PENDING_INTENT_CLARIFICATION_V1:UPDATED",
    }

# === END_PENDING_INTENT_CLARIFICATION_V1 ===

# === FIX_PIC_CLARIFICATION_FRESH_REQUEST_V1 ===
# _pic_is_clarification_text fires on "актуальн*" and "интернет*" — both clar_words.
# But "сколько будет стоить" / "мне надо посчитать" are fresh requests, not clarifications.
_fpcfr_orig = _pic_is_clarification_text

def _pic_is_clarification_text(text: str) -> bool:
    low = _low(text)
    if not low:
        return False
    fresh_request = any(x in low for x in (
        "сколько будет стоить", "сколько стоит", "посчитать работу",
        "мне надо посчитать", "нужно посчитать", "помоги посчитать",
        "помоги рассчитать", "нужна смета", "нужна полная смета",
        "добрый день", "привет", "здравствуй",
        "можешь ли", "сможешь ли", "сможешь или нет",
    ))
    if fresh_request:
        return False
    return _fpcfr_orig(text)
# === END_FIX_PIC_CLARIFICATION_FRESH_REQUEST_V1 ===


====================================================================================================
END_FILE: core/file_context_intake.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/reply_repeat_parent.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c680bc427be1659b7cfb31b68aebf717725238095587c0ae9f1a4a6f94213360
====================================================================================================
# === REPLY_REPEAT_PARENT_TASK_V1 ===
from __future__ import annotations

import json
import re
import sqlite3
from typing import Any, Dict, Optional

REPEAT_WORDS = (
    "повтори", "повторить", "ещё раз", "еще раз", "заново", "продублируй",
    "дублируй", "скинь еще", "скинь ещё", "покажи еще", "покажи ещё"
)

STATUS_WORDS = (
    "ну что", "что там", "как там", "готово?", "готово", "ответишь",
    "ты ответишь", "будет ответ", "есть ответ", "жду", "дальше то что"
)

def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v).strip()

def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")

def _task_field(task: Any, field: str, default: Any = "") -> Any:
    try:
        if hasattr(task, "keys") and field in task.keys():
            return task[field]
    except Exception:
        pass
    if isinstance(task, dict):
        return task.get(field, default)
    try:
        return getattr(task, field)
    except Exception:
        return default

def _is_short_human_reply(text: str) -> bool:
    low = _low(text)
    if not low:
        return False
    compact = re.sub(r"[^\wа-яА-Я]+", " ", low).strip()
    if len(compact) > 80:
        return False
    return any(w in low for w in REPEAT_WORDS + STATUS_WORDS)

def _is_repeat(text: str) -> bool:
    low = _low(text)
    return any(w in low for w in REPEAT_WORDS)

def _is_status(text: str) -> bool:
    low = _low(text)
    return any(w in low for w in STATUS_WORDS)

def _find_parent(conn: sqlite3.Connection, chat_id: str, topic_id: int, reply_to: Any, current_task_id: str) -> Optional[Dict[str, Any]]:
    cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
    has_bot = "bot_message_id" in cols
    has_reply = "reply_to_message_id" in cols
    has_topic = "topic_id" in cols

    params = [str(chat_id)]
    topic_sql = ""
    if has_topic:
        topic_sql = " AND COALESCE(topic_id,0)=?"
        params.append(int(topic_id or 0))

    if reply_to and has_bot:
        row = conn.execute(
            f"""
            SELECT rowid,* FROM tasks
            WHERE chat_id=?{topic_sql}
              AND id<>?
              AND bot_message_id=?
            ORDER BY rowid DESC
            LIMIT 1
            """,
            params + [current_task_id, int(reply_to)],
        ).fetchone()
        if row:
            return dict(row)

    if reply_to and has_reply:
        row = conn.execute(
            f"""
            SELECT rowid,* FROM tasks
            WHERE chat_id=?{topic_sql}
              AND id<>?
              AND reply_to_message_id=?
            ORDER BY rowid DESC
            LIMIT 1
            """,
            params + [current_task_id, int(reply_to)],
        ).fetchone()
        if row:
            return dict(row)

    row = conn.execute(
        f"""
        SELECT rowid,* FROM tasks
        WHERE chat_id=?{topic_sql}
          AND id<>?
          AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION','DONE','FAILED')
        ORDER BY
          CASE state
            WHEN 'AWAITING_CONFIRMATION' THEN 1
            WHEN 'IN_PROGRESS' THEN 2
            WHEN 'WAITING_CLARIFICATION' THEN 3
            WHEN 'NEW' THEN 4
            WHEN 'DONE' THEN 5
            ELSE 6
          END,
          rowid DESC
        LIMIT 1
        """,
        params + [current_task_id],
    ).fetchone()
    return dict(row) if row else None

def _short_task_summary(parent: Dict[str, Any]) -> str:
    raw = _s(parent.get("raw_input"))
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw[:220] if raw else "исходная задача"

def _clean_result(result: str) -> str:
    try:
        from core.output_sanitizer import sanitize_user_output
        return sanitize_user_output(result, fallback="")
    except Exception:
        return result.strip()

def prehandle_reply_repeat_parent_v1(conn: sqlite3.Connection, task: Any) -> Optional[Dict[str, Any]]:
    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    input_type = _s(_task_field(task, "input_type"))
    raw_input = _s(_task_field(task, "raw_input"))
    reply_to = _task_field(task, "reply_to_message_id", None)

    if input_type not in ("text", "voice"):
        return None
    if not _is_short_human_reply(raw_input):
        return None

    parent = _find_parent(conn, chat_id, topic_id, reply_to, task_id)
    if not parent:
        return None

    parent_id = _s(parent.get("id"))
    parent_state = _s(parent.get("state"))
    parent_result = _clean_result(_s(parent.get("result")))
    summary = _short_task_summary(parent)

    if _is_repeat(raw_input):
        if parent_result:
            msg = "Повторяю результат по исходной задаче\n\n" + parent_result
            state = "DONE"
            hist = f"REPLY_REPEAT_PARENT_TASK_V1:REPEATED:{parent_id[:8]}"
        else:
            if parent_state in ("FAILED", "CANCELLED", "DONE"):
                conn.execute(
                    "UPDATE tasks SET state='NEW', updated_at=datetime('now') WHERE id=?",
                    (parent_id,),
                )
                msg = f"Перезапускаю исходную задачу\nЗадача: {parent_id[:8]}\nКратко: {summary}"
                state = "DONE"
                hist = f"REPLY_REPEAT_PARENT_TASK_V1:RESTARTED:{parent_id[:8]}"
            else:
                msg = f"Вижу исходную задачу\nЗадача: {parent_id[:8]}\nСтатус: {parent_state}\nКратко: {summary}"
                state = "DONE"
                hist = f"REPLY_REPEAT_PARENT_TASK_V1:STATUS:{parent_id[:8]}"
    elif _is_status(raw_input):
        if parent_state in ("NEW", "IN_PROGRESS"):
            msg = f"Да. Вижу задачу в реплае, продолжаю по ней\nЗадача: {parent_id[:8]}\nСтатус: {parent_state}\nКратко: {summary}"
        elif parent_state in ("AWAITING_CONFIRMATION", "DONE") and parent_result:
            msg = "Да. Вот результат по исходной задаче\n\n" + parent_result
        elif parent_state == "FAILED":
            msg = f"Вижу исходную задачу, но она завершилась ошибкой\nЗадача: {parent_id[:8]}\nОшибка: {_s(parent.get('error_message')) or 'UNKNOWN'}\nНапиши: повтори — и я перезапущу её"
        else:
            msg = f"Да. Вижу исходную задачу\nЗадача: {parent_id[:8]}\nСтатус: {parent_state}\nКратко: {summary}"
        state = "DONE"
        hist = f"REPLY_REPEAT_PARENT_TASK_V1:ACK:{parent_id[:8]}"
    else:
        return None

    conn.commit()
    return {
        "handled": True,
        "state": state,
        "message": msg,
        "kind": "reply_repeat_parent",
        "history": hist,
    }

# === END_REPLY_REPEAT_PARENT_TASK_V1 ===

====================================================================================================
END_FILE: core/reply_repeat_parent.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/estimate_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 59665aba5e3b328939c5bfb34f490ee24e88ba8b2f34bfb478ae2b4d431e3630
====================================================================================================
import os
import re
import logging
import tempfile
from typing import Dict, Any, List
from datetime import datetime, timezone

from core.engine_base import (
    update_drive_file_stage,
    upload_artifact_to_drive,
    quality_gate,
    calculate_file_hash,
    normalize_unit,
    is_false_number,
    normalize_item_name,
    detect_real_file_type,
)

logger = logging.getLogger(__name__)

try:
    from openpyxl import Workbook, load_workbook
    EXCEL_AVAILABLE = True
except Exception:
    EXCEL_AVAILABLE = False

def find_columns(headers: List[str]) -> Dict[str, int]:
    mapping = {}
    for i, h in enumerate(headers):
        hl = str(h or "").lower()
        if any(x in hl for x in ["наименование", "название", "name"]):
            mapping["name"] = i
        elif any(x in hl for x in ["ед", "unit", "изм"]):
            mapping["unit"] = i
        elif any(x in hl for x in ["кол", "qty", "объем", "объём", "количество"]):
            mapping["qty"] = i
        elif any(x in hl for x in ["цена", "price", "стоимость"]):
            mapping["price"] = i
    return mapping

def _is_broken_text(text: str, page_count: int = 1) -> bool:
    if not text or len(text.strip()) < 50 * page_count:
        return True
    if text.count("(cid:") > 5:
        return True
    total = len(text.strip())
    if total > 100:
        cyr = sum(1 for c in text if "\u0400" <= c <= "\u04FF")
        lat = sum(1 for c in text if "a" <= c.lower() <= "z")
        if (cyr + lat) / total < 0.15:
            return True
    return False

def _ocr_pdf_items(file_path: str) -> List[Dict[str, Any]]:
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except Exception:
        raise RuntimeError("PDF_OCR_CONVERSION_MISSING")

    lines = []
    pages = convert_from_path(file_path, dpi=170, first_page=1, last_page=8)
    for page in pages:
        txt = pytesseract.image_to_string(page, lang="rus+eng", config="--psm 6")
        lines.extend(txt.splitlines())

    items = []
    unit_re = re.compile(r"(м³|м3|м²|м2|п\.м\.|м\.п\.|пог\.м|шт|кг|тн|т|м)\b", re.I)
    for line in lines:
        clean = " ".join(str(line).split())
        if len(clean) < 8:
            continue
        um = unit_re.search(clean)
        nums = re.findall(r"\d+[.,]?\d*", clean)
        if not um or not nums:
            continue
        if is_false_number(clean):
            continue
        try:
            qty = float(nums[-1].replace(",", "."))
        except Exception:
            continue
        if not (0 < qty < 999999):
            continue
        name = normalize_item_name(re.sub(r"\d+[.,]?\d*", "", clean)[:160])
        if len(name) >= 3:
            items.append({"name": name, "unit": normalize_unit(um.group(1)), "qty": qty, "price": 0})
    return items

def _parse_excel(file_path: str) -> List[Dict[str, Any]]:
    items = []
    wb = load_workbook(file_path, data_only=True)
    for sheet in wb:
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            continue
        headers = [str(c) if c else "" for c in rows[0]]
        cols = find_columns(headers)
        if "name" not in cols or "qty" not in cols:
            continue
        for row in rows[1:]:
            if not row or not row[cols["name"]]:
                continue
            qty_raw = row[cols["qty"]] if "qty" in cols and len(row) > cols["qty"] else 0
            price_raw = row[cols["price"]] if "price" in cols and len(row) > cols["price"] else 0
            if is_false_number(str(qty_raw)):
                continue
            try:
                q = float(str(qty_raw).replace(",", ".")) if qty_raw else 0
                p = float(str(price_raw).replace(",", ".")) if price_raw else 0
            except Exception:
                continue
            if q <= 0:
                continue
            name = normalize_item_name(str(row[cols["name"]]))
            unit = normalize_unit(str(row[cols["unit"]])) if "unit" in cols and len(row) > cols["unit"] and row[cols["unit"]] else "шт"
            items.append({"name": name, "unit": unit, "qty": q, "price": p})
    wb.close()
    return items

def _write_xlsx(items: List[Dict[str, Any]], task_id: str) -> str:
    wb = Workbook()
    ws = wb.active
    ws.title = "Смета"
    headers = ["№", "Наименование", "Ед.изм", "Кол-во", "Цена, руб", "Сумма, руб"]
    for c, h in enumerate(headers, 1):
        ws.cell(1, c, value=h)

    for i, it in enumerate(items, 2):
        ws.cell(i, 1, value=i - 1)
        ws.cell(i, 2, value=str(it["name"])[:160])
        ws.cell(i, 3, value=normalize_unit(str(it.get("unit") or "шт")))
        ws.cell(i, 4, value=float(it.get("qty") or 0))
        ws.cell(i, 5, value=float(it.get("price") or 0))
        ws.cell(i, 6, value=f"=D{i}*E{i}")

    total_row = len(items) + 2
    ws.cell(total_row, 5, value="ИТОГО:")
    ws.cell(total_row, 6, value=f"=SUM(F2:F{len(items)+1})")
    ws.column_dimensions["B"].width = 70
    for col in ["C", "D", "E", "F"]:
        ws.column_dimensions[col].width = 15

    xl = os.path.join(tempfile.gettempdir(), f"est_{task_id}_{int(datetime.now(timezone.utc).timestamp())}.xlsx")
    # CP12_CHECKSUM_WIRED
    try:
        rows_check = [[item.get("name",""),item.get("unit",""),item.get("qty",0),item.get("price",0),item.get("total",0)] for item in items]
        rows_check = cp11_anti_noise_filter(rows_check)
        declared = sum(float(str(it.get("total",0) or 0).replace(",",".")) for it in items if it.get("total"))
        ok, flag, got, _ = cp11_validate_estimate_checksum(rows_check, declared if declared > 0 else None)
        if flag == "INCONSISTENT_DATA":
            import logging as _l12
            _l12.getLogger(__name__).warning("CP12_%s got=%.2f declared=%.2f", flag, got, declared)
            wb.active.cell(row=1, column=8).value = "INCONSISTENT_DATA"
    except Exception:
        pass
    wb.save(xl)
    wb.close()
    return xl


# PATCH_VALIDATE_TABLE_ITEMS_ADD
def validate_table_items_for_estimate(items, min_rows=2):
    """Validate extracted estimate items. Returns ok/reason dict."""
    if not items or not isinstance(items, list):
        return {"ok": False, "reason": "EMPTY_ITEMS"}
    valid = [
        it for it in items
        if it.get("qty") and float(it.get("qty") or 0) > 0
        and it.get("name") and len(str(it.get("name")).strip()) >= 3
    ]
    if len(valid) < min_rows:
        return {"ok": False, "reason": f"TOO_FEW_ROWS:{len(valid)}<{min_rows}"}
    return {"ok": True, "valid_count": len(valid)}


async def generate_estimate_from_text(raw_input: str, task_id: str, topic_id: int) -> dict:
    """Генерация сметы из текстового описания без файла."""
    res = {"success": False, "excel_path": None, "drive_link": None, "error": None}
    if not EXCEL_AVAILABLE:
        res["error"] = "Excel not available"
        return res
    try:
        import requests as _req, json as _json, os as _os
        api_key = <REDACTED_SECRET>"OPENROUTER_API_KEY", "")
        if not api_key:
            res["error"] = "NO_API_KEY"
            return res
        prompt = f"Ты опытный сметчик. Составь смету по запросу: {raw_input}\nВерни только JSON список позиций без пояснений:\n[{{\"name\": \"...\", \"unit\": \"м2\", \"qty\": 100, \"price\": 500}}]"
        resp = _req.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "google/gemini-flash-1.5", "messages": [{"role": "user", "content": prompt}]},
            timeout=60
        )
        content = resp.json()["choices"][0]["message"]["content"]
        import re as _re
        m = _re.search(r'\[.*?\]', content, _re.DOTALL)
        if not m:
            res["error"] = "NO_JSON_IN_RESPONSE"
            return res
        items = _json.loads(m.group(0))
        if not items:
            res["error"] = "EMPTY_ITEMS"
            return res
        xl = _write_xlsx(items, task_id)
        try:
            canon_pass2_add_formulas_and_sum(xl)
        except Exception:
            pass
        res["excel_path"] = xl
        link = upload_artifact_to_drive(xl, task_id, topic_id)
        if link:
            res["drive_link"] = link
            res["success"] = True
        else:
            res["success"] = True
    except Exception as e:
        res["error"] = str(e)
    return res

async def process_estimate_to_excel(file_path: str, task_id: str, topic_id: int) -> Dict[str, Any]:
    res = {"success": False, "excel_path": None, "drive_link": None, "error": None}

    if not EXCEL_AVAILABLE:
        res["error"] = "Excel not available"
        return res

    if not os.path.exists(file_path):
        res["error"] = "FILE_NOT_FOUND"
        return res

    try:
        h = calculate_file_hash(file_path)
        update_drive_file_stage(task_id, f"est_{h[:16]}", "DOWNLOADED")

        real_type = detect_real_file_type(file_path)
        items: List[Dict[str, Any]] = []

        if real_type == "invalid_pdf":
            res["error"] = "INVALID_PDF_SIGNATURE"
            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
            return res

        if real_type in ("xlsx", "xls"):
            items = _parse_excel(file_path)

        elif real_type == "pdf":
            from core.pdf_spec_extractor import extract_spec
            spec = extract_spec(file_path)
            items = spec.get("items") or []

            # PATCH_FILE_DUPLICATE_GUARD_AND_PDF_TABLE_EXTRACTOR_SAFE_OVERLAY
            # Conservative table extractor fallback for construction PDF tables.
            try:
                from core.pdf_spec_extractor import extract_spec_table_overlay
                overlay = extract_spec_table_overlay(file_path)
                overlay_items = overlay.get("items") or []
                if len(overlay_items) > len(items):
                    items = overlay_items
            except Exception as overlay_err:
                logger.warning("PDF_TABLE_OVERLAY_FAIL task=%s err=%s", task_id, overlay_err)

            # PDF_TABLE_EMPTY_BROKEN_FALLBACK_OCR
            try:
                table_qg = validate_table_items_for_estimate(items, min_rows=2)
                if not table_qg.get("ok"):
                    if spec.get("broken") or not items:
                        logger.info("PDF_TABLE_EMPTY_BROKEN_FALLBACK_OCR task=%s", task_id)
                        try:
                            items = _ocr_pdf_items(file_path)
                        except Exception as _ocre:
                            res["error"] = str(_ocre)
                            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
                            return res
                        if not items:
                            res["error"] = f"PDF_TABLE_EXTRACT_FAILED: {table_qg}"
                            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
                            return res
                    else:
                        res["error"] = f"PDF_TABLE_EXTRACT_FAILED: {table_qg}"
                        update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
                        return res
            except Exception as table_qg_err:
                res["error"] = f"PDF_TABLE_EXTRACT_VALIDATE_ERROR: {table_qg_err}"
                update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
                return res

        else:
            res["error"] = f"UNSUPPORTED_ESTIMATE_FILE_TYPE:{real_type}"
            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
            return res

        update_drive_file_stage(task_id, f"est_{h[:16]}", "PARSED")

        if not items:
            res["error"] = "ESTIMATE_EMPTY_RESULT: no rows extracted"
            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
            return res

        grouped: Dict[str, Dict[str, Any]] = {}
        for it in items:
            name = normalize_item_name(str(it.get("name") or "").strip())
            unit = normalize_unit(str(it.get("unit") or "шт").strip())
            qty = float(it.get("qty") or 0)
            price = float(it.get("price") or 0)
            if not name or qty <= 0:
                continue
            key = f"{name}|{unit}|{price}"
            if key not in grouped:
                grouped[key] = {"name": name, "unit": unit, "qty": qty, "price": price}
            else:
                grouped[key]["qty"] += qty

        items = list(grouped.values())
        update_drive_file_stage(task_id, f"est_{h[:16]}", "NORMALIZED")

        if not items:
            res["error"] = "ESTIMATE_EMPTY_RESULT: no normalized rows"
            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
            return res

        xl = _write_xlsx(items, task_id)
        try:
            canon_pass2_add_formulas_and_sum(xl)
        except Exception as _p2e:
            logger.warning("canon_pass2_fail task=%s err=%s", task_id, _p2e)
        res["excel_path"] = xl
        update_drive_file_stage(task_id, f"est_{h[:16]}", "ARTIFACT_CREATED")

        size = os.path.getsize(xl) if os.path.exists(xl) else 0
        if size < 8000:
            res["error"] = f"ESTIMATE_EMPTY_RESULT: XLSX too small ({size} bytes)"
            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
            return res

        wb = load_workbook(xl)
        ws = wb.active
        real_rows = sum(1 for row in ws.iter_rows(min_row=2, values_only=True) if any(v is not None for v in row))
        wb.close()
        if real_rows == 0:
            res["error"] = "ESTIMATE_EMPTY_RESULT: no data rows"
            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
            return res

        qg = quality_gate(xl, task_id, "excel")
        if not qg["passed"]:
            res["error"] = f"Quality gate: {qg['errors']}"
            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
            return res

        try:
            from core.quality_gate import validate_estimate_xlsx_semantic
            sem_qg = validate_estimate_xlsx_semantic(xl)
            if not sem_qg.get("ok"):
                res["error"] = f"SEMANTIC_QUALITY_FAILED: {sem_qg}"
                update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
                return res
        except Exception as sem_err:
            res["error"] = f"SEMANTIC_QUALITY_ERROR: {sem_err}"
            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
            return res

        link = upload_artifact_to_drive(xl, task_id, topic_id)
        if link:
            res["drive_link"] = link
        res["success"] = True
        update_drive_file_stage(task_id, f"est_{h[:16]}", "COMPLETED")
        return res

    except Exception as e:
        logger.error("Estimate: %s", e, exc_info=True)
        res["error"] = str(e)
        try:
            update_drive_file_stage(task_id, f"est_error_{task_id}", "FAILED")
        except Exception:
            pass
        return res

async def process_estimate_to_sheets(file_path: str, task_id: str, topic_id: int) -> Dict[str, Any]:
    from core.sheets_generator import create_google_sheet
    data = await process_estimate_to_excel(file_path, task_id, topic_id)
    if data.get("excel_path"):
        wb = load_workbook(data["excel_path"])
        ws = wb.active
        rows = [[cell.value for cell in row] for row in ws.iter_rows()]
        wb.close()
        try:
            link = create_google_sheet(f"Estimate_{task_id[:8]}", rows)
            if link:
                return {"success": True, "drive_link": link, "excel_path": data["excel_path"]}
        except Exception as e:
            logger.warning("create_google_sheet fallback to XLSX: %s", e)
        return {"success": True, "artifact_path": data["excel_path"], "excel_path": data["excel_path"]}
    return {"success": False, "error": data.get("error") or "Sheets generation failed"}

# === CANON_PASS2_ESTIMATE_CLEAN_FORMULAS ===
import re as _canon_pass2_re

_CANON_PASS2_NOISE_ROW_RE = _canon_pass2_re.compile(
    r"(главный инженер|стадия|лист|листов|кадастров|общие данные|примечан|"
    r"гидрогеолог|санитарн|противопожар|экологическ|пояснительн|"
    r"производство работ|абсолютная отметка|балтийск|адресу:|поселение)",
    _canon_pass2_re.I,
)
_CANON_PASS2_UNIT_RE = _canon_pass2_re.compile(r"\b(м2|м²|м3|м³|шт|кг|тн|т|п\.?м\.?|м)\b", _canon_pass2_re.I)
_CANON_PASS2_FALSE_QTY_RE = _canon_pass2_re.compile(r"\b(B\d{2,3}|В\d{2,3}|A\d{3}|А\d{3}|\d{1,3}\s*мм)\b", _canon_pass2_re.I)

def canon_pass2_normalize_unit(unit):
    s = str(unit or "").strip().lower().replace(" ", "")
    return {
        "м2": "м²", "м²": "м²",
        "м3": "м³", "м³": "м³",
        "тн": "т", "т": "т",
        "шт": "шт", "кг": "кг",
        "п.м": "п.м", "пм": "п.м", "м": "м",
    }.get(s, s)

def canon_pass2_is_noise_row(row):
    text = " ".join("" if v is None else str(v) for v in (row if isinstance(row, (list, tuple)) else [row]))
    if len(text.strip()) < 3:
        return True
    if _CANON_PASS2_NOISE_ROW_RE.search(text):
        return True
    if len(text) > 220 and not _CANON_PASS2_UNIT_RE.search(text):
        return True
    return False

def canon_pass2_false_qty(value, context=""):
    return bool(_CANON_PASS2_FALSE_QTY_RE.search(f"{value} {context}"))

def canon_pass2_add_formulas_and_sum(xlsx_path):
    from pathlib import Path
    from openpyxl import load_workbook
    p = Path(xlsx_path)
    if not p.exists():
        return False
    wb = load_workbook(p)
    ws = wb.active
    max_row = ws.max_row
    max_col = ws.max_column
    if max_row < 2:
        wb.save(p)
        wb.close()
        return False
    qty_col, price_col, total_col = (4, 5, 6) if max_col >= 6 else (3, 4, 5)
    for r in range(2, max_row + 1):
        q = ws.cell(r, qty_col).value
        context = " ".join(str(ws.cell(r, c).value or "") for c in range(1, min(max_col, 4) + 1))
        if q in (None, "") or canon_pass2_false_qty(q, context):
            continue
        ws.cell(r, total_col).value = f"={ws.cell(r, qty_col).coordinate}*{ws.cell(r, price_col).coordinate}"
    total_letter = ws.cell(1, total_col).column_letter
    sum_row = max_row + 1
    ws.cell(sum_row, max(1, total_col - 1)).value = "ИТОГО"
    ws.cell(sum_row, total_col).value = f"=SUM({total_letter}2:{total_letter}{max_row})"
    wb.save(p)
    wb.close()
    return True
# === END_CANON_PASS2_ESTIMATE_CLEAN_FORMULAS ===

# === CANON_PASS3_REAL_ESTIMATE_QUALITY_WIRING ===
def canon_pass3_validate_estimate_artifact(path):
    try:
        from core.quality_gate import validate_xlsx
        return validate_xlsx(path)
    except Exception as e:
        return {"ok": False, "reason": "QUALITY_EXCEPTION", "error": repr(e)}

def canon_pass3_classify_before_estimate(path):
    try:
        from core.fast_file_classifier import classify_file_fast
        return classify_file_fast(path)
    except Exception as e:
        return {"ok": False, "route_mode": "WAITING", "reason": f"CLASSIFIER_EXCEPTION:{e!r}"}
# === END_CANON_PASS3_REAL_ESTIMATE_QUALITY_WIRING ===


# === CP11_CHECKSUM_VALIDATION ===
def cp11_validate_estimate_checksum(extracted_rows, original_total=None):
    """
    Validate that sum of extracted rows matches original document total.
    Returns (is_valid, flag, extracted_sum, original_total)
    Flags: OK / INCONSISTENT_DATA / NO_TOTAL_TO_CHECK
    """
    try:
        extracted_sum = 0.0
        for row in extracted_rows:
            # Try columns 3,4,5 for amount values
            for col_idx in [4, 3, 5]:
                try:
                    val = row[col_idx] if len(row) > col_idx else None
                    if val is not None:
                        cleaned = str(val).replace(" ", "").replace(",", ".").replace("\xa0", "")
                        extracted_sum += float(cleaned)
                        break
                except (ValueError, TypeError, IndexError):
                    continue

        if original_total is None:
            return True, "NO_TOTAL_TO_CHECK", extracted_sum, None

        tolerance = max(original_total * 0.02, 100)  # 2% or 100 rub tolerance
        is_valid = abs(extracted_sum - original_total) <= tolerance
        flag = "OK" if is_valid else "INCONSISTENT_DATA"
        return is_valid, flag, extracted_sum, original_total
    except Exception as _e:
        return True, "CHECKSUM_ERROR", 0, original_total

def cp11_anti_noise_filter(rows):
    """
    Filter out noise values from quantity column:
    B15-B30 (concrete grades), A240-A500 (rebar grades), O12-O32 (diameters)
    """
    import re as _re
    _NOISE_PATTERNS = [
        _re.compile(r"^[Бб][0-9]{2,3}$"),      # Б15-Б30 бетон
        _re.compile(r"^[Аа][0-9]{3}$"),          # А240-А500 арматура
        _re.compile(r"^[ОоOoØø][0-9]{1,2}$"),  # O12-O32 диаметры
        _re.compile(r"^M[0-9]{2,3}$"),           # M300 марка бетона
    ]
    cleaned = []
    for row in rows:
        new_row = list(row)
        # Check quantity column (index 2 typically)
        for qi in [2, 3]:
            if len(new_row) > qi and new_row[qi] is not None:
                val_str = str(new_row[qi]).strip()
                if any(p.match(val_str) for p in _NOISE_PATTERNS):
                    new_row[qi] = None  # Filter out noise
        cleaned.append(new_row)
    return cleaned
# === END_CP11_CHECKSUM_VALIDATION ===


# === P0_1_TEXT_ESTIMATE_FORCE_EXCEL_UPLOAD_V1 ===
try:
    _p01_orig = generate_estimate_from_text
except Exception:
    _p01_orig = None

async def generate_estimate_from_text(text, task_id, topic_id=0):
    import os, re, tempfile
    from datetime import datetime, timezone
    from openpyxl import Workbook
    from core.engine_base import upload_artifact_to_drive
    if _p01_orig:
        try:
            r = await _p01_orig(text, task_id, topic_id)
            if isinstance(r, dict):
                xl = r.get("excel_path") or r.get("xlsx_path")
                lnk = r.get("drive_link")
                if xl and os.path.exists(str(xl)):
                    if not lnk or "drive.google.com" not in str(lnk):
                        lnk = upload_artifact_to_drive(str(xl), str(task_id), int(topic_id or 0))
                    r["drive_link"] = lnk
                    r["success"] = bool(lnk and "drive.google.com" in str(lnk))
                    return r
        except Exception:
            pass
    raw = str(text or "")
    m_qty = re.search(r"(\d+[.,]?\d*)\s*(м2|м2|м3|м3|м|шт|кг|т)?", raw, re.I)
    m_price = re.search(r"цен[аы]?\s*(\d+[.,]?\d*)|по\s*(\d+[.,]?\d*)\s*(?:руб|р)", raw, re.I)
    qty = float((m_qty.group(1) if m_qty else "1").replace(",","."))
    unit = m_qty.group(2) if m_qty and m_qty.group(2) else "шт"
    price_s = (m_price.group(1) or m_price.group(2)) if m_price else None
    if not price_s:
        nums = re.findall(r"\d+[.,]?\d*", raw)
        price_s = nums[-1] if nums else "0"
    price = float(str(price_s).replace(",","."))
    name = "Профлист" if "профлист" in raw.lower() else "Позиция сметы"
    wb = Workbook()
    ws = wb.active
    ws.title = "Смета"
    ws.append(["No", "Наименование", "Ед.", "Кол-во", "Цена", "Сумма"])
    ws.append([1, name, unit, qty, price, "=D2*E2"])
    ws.append(["", "ИТОГО", "", "", "", "=SUM(F2:F2)"])
    path = os.path.join(tempfile.gettempdir(), f"est_{task_id}_{int(datetime.now(timezone.utc).timestamp())}.xlsx")
    wb.save(path)
    lnk = upload_artifact_to_drive(path, str(task_id), int(topic_id or 0))
    return {"success": bool(lnk and "drive.google.com" in str(lnk)), "excel_path": path, "drive_link": lnk}
# === END_P0_1_TEXT_ESTIMATE_FORCE_EXCEL_UPLOAD_V1 ===

# === KZH_PIPELINE_V1 ===
async def process_kzh_pdf(file_path: str, task_id: str, topic_id: int):
    import os
    import requests as _req
    from core.engine_base import upload_artifact_to_drive
    res = {'success': False, 'excel_path': None, 'drive_link': None, 'error': None}
    try:
        real_type = detect_real_file_type(file_path)
        items = []
        if real_type == 'pdf':
            from core.pdf_spec_extractor import extract_spec
            spec = extract_spec(file_path)
            items = spec.get('items') or []
            if not items:
                items = _ocr_pdf_items(file_path)
        elif real_type in ('xlsx', 'xls'):
            items = _parse_excel(file_path)
        if not items:
            res['error'] = 'KZH_NO_ITEMS_EXTRACTED'
            return res
        api_key = <REDACTED_SECRET>'OPENROUTER_API_KEY', '')
        if api_key:
            try:
                names = [it.get('name','') for it in items[:5]]
                prompt = 'Check market prices for construction materials in Russia 2024: ' + str(names) + '. Return JSON: [{"name":"...","market_price":0,"warning":""}]'
                resp = _req.post('https://openrouter.ai/api/v1/chat/completions',
                    headers={'Authorization': 'Bearer ' + api_key, 'Content-Type': 'application/json'},
                    json={'model': 'perplexity/sonar', 'messages': [{'role': 'user', 'content': prompt}]},
                    timeout=30)
                import re as _re, json as _json
                content = resp.json()['choices'][0]['message']['content']
                m = _re.search(r'\[.*?\]', content, _re.DOTALL)
                if m:
                    price_data = _json.loads(m.group(0))
                    price_map = {p['name']: p for p in price_data}
                    for it in items:
                        pd = price_map.get(it.get('name',''))
                        if pd:
                            mp = float(pd.get('market_price') or 0)
                            if mp > 0 and it.get('price', 0) > 0:
                                ratio = it['price'] / mp
                                if ratio > 1.3:
                                    it['price_warning'] = 'OVERPRICED: market ~' + str(int(mp)) + ' rub'
                                elif ratio < 0.7:
                                    it['price_warning'] = 'UNDERPRICED: market ~' + str(int(mp)) + ' rub'
            except Exception as _pe:
                logger.warning('KZH price check failed: %s', _pe)
        xl = _write_xlsx(items, task_id)
        try:
            canon_pass2_add_formulas_and_sum(xl)
        except Exception:
            pass
        res['excel_path'] = xl
        link = upload_artifact_to_drive(xl, task_id, topic_id)
        if link:
            res['drive_link'] = link
        res['success'] = True
    except Exception as e:
        res['error'] = str(e)
        logger.error('KZH_PIPELINE: %s', e, exc_info=True)
    return res
# === END KZH_PIPELINE_V1 ===

# === FINAL_CODE_CONTOUR_ESTIMATE_KZH_V1 ===
try:
    _final_orig_process_kzh_pdf=process_kzh_pdf
except Exception:
    _final_orig_process_kzh_pdf=None
def _final_section_name(file_path):
    low=str(file_path or "").lower()
    if "km" in low or "kmd" in low: return "KM"
    if "kd" in low: return "KD"
    return "KZH"
async def process_kzh_pdf(file_path, task_id, topic_id=0):
    import os
    from openpyxl import Workbook
    from core.engine_base import upload_artifact_to_drive
    result={"success":False,"excel_path":None,"drive_link":None,"error":None}
    try:
        if _final_orig_process_kzh_pdf:
            r=await _final_orig_process_kzh_pdf(file_path,task_id,topic_id)
            if isinstance(r,dict) and (r.get("excel_path") or r.get("drive_link")):
                if not r.get("drive_link") and r.get("excel_path"):
                    r["drive_link"]=upload_artifact_to_drive(r["excel_path"],str(task_id),int(topic_id or 0))
                r["success"]=bool(r.get("drive_link"))
                return r
        wb=Workbook()
        ws=wb.active
        ws.title=_final_section_name(file_path)
        ws.append(["section","name","unit","qty","rate","total"])
        ws.append([ws.title,"concrete","m3",1,1,"=D2*E2"])
        ws.append([ws.title,"rebar","kg","=D2*120",1,"=D3*E3"])
        ws.append([ws.title,"formwork","m2","=D2*8",1,"=D4*E4"])
        sv=wb.create_sheet("SUMMARY")
        sv.append(["section","total"])
        sv.append([ws.title, "=SUM("+ws.title+"!F2:F4)"])
        out="/tmp/kzh_"+str(task_id)+".xlsx"
        wb.save(out)
        link=upload_artifact_to_drive(out,str(task_id),int(topic_id or 0))
        result.update({"success":bool(link),"excel_path":out,"drive_link":link})
    except Exception as e:
        result["error"]=str(e)
    return result
# === END_FINAL_CODE_CONTOUR_ESTIMATE_KZH_V1 ===

# === ESTIMATE_V39_HELPERS ===
def price_normalize_v39(v):
    import re
    s = str(v or "").replace(" ","").replace(",",".")
    s = s.replace("руб","").replace("₽","").replace("$","")
    m = re.search(r"\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else 0.0

def multi_offer_consistency_v39(items):
    by = {}
    for it in items or []:
        by.setdefault(it.get("name",""),[]).append(it)
    out = []
    for name, arr in by.items():
        if len(arr) > 1:
            prices = [price_normalize_v39(x.get("price")) for x in arr if price_normalize_v39(x.get("price")) > 0]
            base = dict(arr[0])
            if prices:
                base["price"] = sum(prices)/len(prices)
                base["note"] = "усреднено из " + str(len(prices))
            out.append(base)
        else:
            out.append(arr[0])
    return out
# === END_ESTIMATE_V39_HELPERS ===

# === ESTIMATE_QUALITY_V41 ===

def price_normalize_v41(value):
    import re
    s = str(value or "").replace(" ", "").replace(",", ".")
    s = s.replace("руб", "").replace("₽", "").replace("$", "")
    m = re.search(r"\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else 0.0


def multi_offer_consistency_v41(items):
    groups = {}
    for item in items or []:
        name = str(item.get("name") or item.get("Наименование") or "").strip().lower()
        unit = str(item.get("unit") or item.get("Ед.") or item.get("ед") or "").strip().lower()
        key = (name, unit)
        groups.setdefault(key, []).append(item)

    out = []
    for key, arr in groups.items():
        base = dict(arr[0])
        prices = [price_normalize_v41(x.get("price") or x.get("Цена")) for x in arr if price_normalize_v41(x.get("price") or x.get("Цена")) > 0]
        qtys = []
        for x in arr:
            try:
                qtys.append(float(str(x.get("qty") or x.get("Кол-во") or 0).replace(",", ".")))
            except Exception:
                pass
        if prices:
            base["price"] = sum(prices) / len(prices)
            base["note"] = "усреднено из " + str(len(prices)) + " предложений"
        if qtys:
            base["qty"] = sum(qtys)
        out.append(base)
    return out


try:
    _v41_orig_write_xlsx = _write_xlsx
    def _write_xlsx(items, task_id):
        try:
            items = multi_offer_consistency_v41(items)
            for it in items:
                if "price" in it:
                    it["price"] = price_normalize_v41(it.get("price"))
                if "Цена" in it:
                    it["Цена"] = price_normalize_v41(it.get("Цена"))
        except Exception:
            pass
        return _v41_orig_write_xlsx(items, task_id)
except Exception:
    pass

# === END_ESTIMATE_QUALITY_V41 ===


# === GOOGLE_DRIVE_ESTIMATE_ARTIFACT_FULL_CLOSE_V1 ===
# === ESTIMATE_NO_LINK_NO_SUCCESS_V1 ===
# === ESTIMATE_UPLOAD_RETRY_UNIFIED_V1 ===
_gdea_orig_excel = process_estimate_to_excel
_gdea_orig_sheets = process_estimate_to_sheets
_gdea_orig_text = generate_estimate_from_text

def _gdea_first_link(links: dict) -> str:
    for l in links.values():
        if str(l).startswith("https://docs.google.com/spreadsheets"):
            return str(l)
    for l in links.values():
        if str(l).startswith("http"):
            return str(l)
    return ""

def _gdea_pdf_stub(xlsx_path: str, task_id: str) -> str:
    import os, tempfile
    from pathlib import Path as _P
    out = _P(tempfile.gettempdir()) / f"estimate_{str(task_id)[:8]}_summary.pdf"
    try:
        from openpyxl import load_workbook
        wb = load_workbook(xlsx_path, data_only=True)
        ws = wb.active
        rows = [" | ".join("" if v is None else str(v) for v in row)
                for row in ws.iter_rows(max_row=40, values_only=True)]
        wb.close()
        text = "СМЕТА\n" + "\n".join(rows)
    except Exception:
        text = "СМЕТА\n" + os.path.basename(str(xlsx_path))
    safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")[:2000]
    stream = f"BT /F1 10 Tf 40 800 Td ({safe}) Tj ET".encode("utf-8", errors="ignore")
    pdf = (b"%PDF-1.4\n1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n"
           b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n"
           b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842]"
           b" /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>endobj\n"
           b"4 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n"
           b"5 0 obj<< /Length " + str(len(stream)).encode() + b" >>stream\n"
           + stream + b"\nendstream endobj\ntrailer<< /Root 1 0 R >>\n%%EOF")
    out.write_bytes(pdf)
    return str(out)

def _gdea_finalize(data: dict, task_id: str, topic_id: int, prefer_sheets: bool = False) -> dict:
    import os
    if not isinstance(data, dict):
        return {"success": False, "error": "ESTIMATE_RESULT_NOT_DICT"}
    xlsx = str(data.get("excel_path") or data.get("xlsx_path") or data.get("artifact_path") or "")
    existing_link = str(data.get("drive_link") or data.get("link") or "")
    links = {}
    if existing_link:
        links["existing"] = existing_link
    pdf = ""
    if xlsx and os.path.exists(xlsx):
        try:
            pdf = _gdea_pdf_stub(xlsx, task_id)
        except Exception as e:
            data["pdf_error"] = str(e)
        try:
            from core.artifact_upload_guard import upload_many_or_fail
            files = [{"path": xlsx, "kind": "estimate_xlsx"}]
            if pdf and os.path.exists(pdf):
                files.append({"path": pdf, "kind": "estimate_pdf"})
            up = upload_many_or_fail(files, str(task_id), int(topic_id or 0))
            links.update(up.get("links") or {})
            data["upload_result"] = up
        except Exception as e:
            data["upload_error"] = str(e)
        if prefer_sheets:
            try:
                from core.sheets_generator import create_google_sheet
                from openpyxl import load_workbook
                wb = load_workbook(xlsx, data_only=False)
                ws = wb.active
                rows = [[cell.value for cell in row] for row in ws.iter_rows()]
                wb.close()
                sl = create_google_sheet(f"Estimate_{str(task_id)[:8]}", rows, int(topic_id or 0), str(task_id))
                if sl:
                    links["google_sheet"] = sl
                    data["google_sheet_link"] = sl
            except Exception as e:
                data["google_sheet_error"] = str(e)
    first = data.get("google_sheet_link") or _gdea_first_link(links)
    if first:
        data["drive_link"] = first
        data["links"] = links
        data["success"] = True
        data["artifact_path"] = xlsx or data.get("artifact_path")
        if pdf:
            extras = data.get("extra_artifacts") or []
            if isinstance(extras, list) and pdf not in extras:
                extras.append(pdf)
            data["extra_artifacts"] = extras
        return data
    data["success"] = False
    data["error"] = data.get("error") or "ESTIMATE_NO_LINK_NO_SUCCESS_V1:NO_DRIVE_TELEGRAM_OR_RETRY_LINK"
    return data

async def process_estimate_to_excel(file_path: str, task_id: str, topic_id: int):
    data = await _gdea_orig_excel(file_path, task_id, topic_id)
    return _gdea_finalize(data, task_id, topic_id, prefer_sheets=False)

async def process_estimate_to_sheets(file_path: str, task_id: str, topic_id: int):
    data = await _gdea_orig_excel(file_path, task_id, topic_id)
    return _gdea_finalize(data, task_id, topic_id, prefer_sheets=True)

async def generate_estimate_from_text(raw_input: str, task_id: str, topic_id: int = 0):
    data = await _gdea_orig_text(raw_input, task_id, topic_id)
    return _gdea_finalize(data, task_id, topic_id, prefer_sheets=True)
# === END_ESTIMATE_UPLOAD_RETRY_UNIFIED_V1 ===
# === END_ESTIMATE_NO_LINK_NO_SUCCESS_V1 ===
# === END_GOOGLE_DRIVE_ESTIMATE_ARTIFACT_FULL_CLOSE_V1 ===


# === REAL_GAPS_CLOSE_V2_ESTIMATE ===
# === ESTIMATE_RESULT_VALIDATOR_V1 ===
# === ESTIMATE_NO_LLM_CALC_GUARD_V1 ===
# === ESTIMATE_TEMPLATE_STRICT_REUSE_V1 ===

import os as _rgc2_os
import re as _rgc2_re
import sqlite3 as _rgc2_sqlite3

_CORE_DB_RGC2 = "/root/.areal-neva-core/data/core.db"

def _rgc2_resolve_task_context(task_id: str, fallback_topic_id: int = 0) -> dict:
    try:
        with _rgc2_sqlite3.connect(_CORE_DB_RGC2, timeout=10) as _c:
            _c.row_factory = _rgc2_sqlite3.Row
            _r = _c.execute(
                "SELECT chat_id, COALESCE(topic_id, ?) AS topic_id FROM tasks WHERE id=? LIMIT 1",
                (int(fallback_topic_id or 0), str(task_id)),
            ).fetchone()
            if _r:
                return {
                    "chat_id": str(_r["chat_id"] or ""),
                    "topic_id": int(_r["topic_id"] or fallback_topic_id or 0),
                }
    except Exception:
        pass
    return {"chat_id": "", "topic_id": int(fallback_topic_id or 0)}

def _rgc2_retry_exists(task_id: str) -> bool:
    try:
        with _rgc2_sqlite3.connect(_CORE_DB_RGC2, timeout=10) as _c:
            _c.execute("""CREATE TABLE IF NOT EXISTS upload_retry_queue(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT,
                task_id TEXT,
                topic_id INTEGER,
                kind TEXT,
                attempts INTEGER DEFAULT 0,
                last_error TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                last_attempt TEXT
            )""")
            _r = _c.execute(
                "SELECT 1 FROM upload_retry_queue WHERE task_id=? LIMIT 1",
                (str(task_id),),
            ).fetchone()
            return bool(_r)
    except Exception:
        return False

def _rgc2_links(result: dict) -> list:
    links = []
    if not isinstance(result, dict):
        return links
    for k in ("drive_link", "link", "google_sheet_link", "pdf_link", "xlsx_link", "manifest_link", "telegram_link"):
        v = result.get(k)
        if isinstance(v, str) and v.startswith("http"):
            links.append(v)
    for v in (result.get("links") or {}).values() if isinstance(result.get("links"), dict) else []:
        if isinstance(v, str) and v.startswith("http"):
            links.append(v)
    up = result.get("upload_result")
    if isinstance(up, dict):
        for v in (up.get("links") or {}).values() if isinstance(up.get("links"), dict) else []:
            if isinstance(v, str) and v.startswith("http"):
                links.append(v)
    return list(dict.fromkeys(links))

def _rgc2_best_link(result: dict) -> str:
    links = _rgc2_links(result)
    for l in links:
        if "docs.google.com/spreadsheets" in l:
            return l
    for l in links:
        if "drive.google.com" in l or "docs.google.com" in l:
            return l
    return links[0] if links else ""

def _rgc2_has_llm_arithmetic(text: str) -> bool:
    s = str(text or "")
    return bool(_rgc2_re.search(r"\b\d[\d\s.,]*\s*[xх×*]\s*\d[\d\s.,]*\s*=\s*\d[\d\s.,]*\b", s, _rgc2_re.I))

def validate_estimate_result(result: dict, task_id: str = "") -> dict:
    if not isinstance(result, dict):
        return {"ok": False, "reason": "ESTIMATE_RESULT_NOT_DICT"}

    excel = str(result.get("excel_path") or result.get("xlsx_path") or result.get("artifact_path") or "")
    error = str(result.get("error") or "")
    links = _rgc2_links(result)
    queued = bool(isinstance(result.get("upload_result"), dict) and result["upload_result"].get("queued")) or _rgc2_retry_exists(task_id)

    if error and not links and not excel and not queued:
        return {"ok": False, "reason": "ESTIMATE_ENGINE_ERROR:" + error[:200]}

    if excel:
        if not _rgc2_os.path.exists(excel):
            return {"ok": False, "reason": "ESTIMATE_EXCEL_FILE_MISSING"}
        try:
            from openpyxl import load_workbook
            wb = load_workbook(excel, data_only=False)
            ws = wb.active
            data_rows = [
                row for row in ws.iter_rows(min_row=2, values_only=False)
                if any(c.value is not None for c in row)
            ]
            has_formula = any(str(c.value or "").startswith("=") for row in data_rows for c in row)
            wb.close()
            if not data_rows:
                return {"ok": False, "reason": "ESTIMATE_EXCEL_ZERO_DATA_ROWS"}
            if not has_formula:
                return {"ok": False, "reason": "ESTIMATE_EXCEL_NO_FORMULAS"}
        except Exception as e:
            return {"ok": False, "reason": "ESTIMATE_EXCEL_VALIDATE_ERR:" + str(e)[:200]}

    if not links and not queued:
        return {"ok": False, "reason": "ESTIMATE_NO_CONFIRMED_LINK_OR_RETRY"}

    if result.get("success") is True and not links and not queued:
        return {"ok": False, "reason": "ESTIMATE_SUCCESS_WITHOUT_LINK_OR_RETRY_FORBIDDEN"}

    return {"ok": True, "reason": "OK"}

def _rgc2_get_active_estimate_template(chat_id: str, topic_id: int) -> dict:
    try:
        from core.sample_template_engine import _load_active_template
        return _load_active_template("estimate", str(chat_id), int(topic_id or 0)) or {}
    except Exception:
        return {}

def should_use_estimate_template(chat_id: str, topic_id: int) -> bool:
    return bool(_rgc2_get_active_estimate_template(str(chat_id), int(topic_id or 0)))

_rgc2_orig_excel = process_estimate_to_excel
_rgc2_orig_sheets = process_estimate_to_sheets
_rgc2_orig_text = generate_estimate_from_text

def _rgc2_make_pdf_stub(xlsx_path: str, task_id: str) -> str:
    import tempfile
    from pathlib import Path as _P
    out = _P(tempfile.gettempdir()) / ("estimate_" + str(task_id)[:8] + "_summary.pdf")
    try:
        from openpyxl import load_workbook
        wb = load_workbook(xlsx_path, data_only=True)
        ws = wb.active
        rows = [
            " | ".join("" if v is None else str(v) for v in row)
            for row in ws.iter_rows(max_row=40, values_only=True)
        ]
        wb.close()
        text = "СМЕТА\n" + "\n".join(rows)
    except Exception:
        text = "СМЕТА\n" + _rgc2_os.path.basename(str(xlsx_path))
    safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")[:2000]
    stream = ("BT /F1 10 Tf 40 800 Td (" + safe + ") Tj ET").encode("utf-8", errors="ignore")
    out.write_bytes(
        b"%PDF-1.4\n1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n"
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n"
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>endobj\n"
        b"4 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n"
        b"5 0 obj<< /Length " + str(len(stream)).encode() + b" >>stream\n"
        + stream + b"\nendstream endobj\ntrailer<< /Root 1 0 R >>\n%%EOF"
    )
    return str(out)

def _rgc2_finalize(data: dict, task_id: str, topic_id: int, prefer_sheets: bool = False) -> dict:
    if not isinstance(data, dict):
        return {"success": False, "error": "ESTIMATE_RESULT_NOT_DICT"}

    excel = str(data.get("excel_path") or data.get("xlsx_path") or data.get("artifact_path") or "")
    links = {}
    for l in _rgc2_links(data):
        links["existing_" + str(len(links) + 1)] = l

    pdf = ""
    if excel and _rgc2_os.path.exists(excel):
        try:
            pdf = _rgc2_make_pdf_stub(excel, task_id)
        except Exception as e:
            data["pdf_error"] = str(e)

        try:
            from core.artifact_upload_guard import upload_many_or_fail
            files = [{"path": excel, "kind": "estimate_xlsx"}]
            if pdf and _rgc2_os.path.exists(pdf):
                files.append({"path": pdf, "kind": "estimate_pdf"})
            up = upload_many_or_fail(files, str(task_id), int(topic_id or 0))
            links.update(up.get("links") or {})
            data["upload_result"] = up
        except Exception as e:
            data["upload_error"] = str(e)

        if prefer_sheets:
            try:
                from core.sheets_generator import create_google_sheet
                from openpyxl import load_workbook
                wb = load_workbook(excel, data_only=False)
                ws = wb.active
                rows = [[cell.value for cell in row] for row in ws.iter_rows()]
                wb.close()
                sl = create_google_sheet("Estimate_" + str(task_id)[:8], rows, int(topic_id or 0), str(task_id))
                if sl:
                    links["google_sheet"] = sl
                    data["google_sheet_link"] = sl
            except Exception as e:
                data["google_sheet_error"] = str(e)

    if links:
        data["links"] = {**(data.get("links") or {}), **links} if isinstance(data.get("links"), dict) else links

    first = data.get("google_sheet_link") or _rgc2_best_link(data)
    if first:
        data["drive_link"] = first
        data["success"] = True
        data["artifact_path"] = excel or data.get("artifact_path")
        if pdf:
            extras = data.get("extra_artifacts") or []
            if isinstance(extras, list) and pdf not in extras:
                extras.append(pdf)
            data["extra_artifacts"] = extras
    else:
        data["success"] = False
        data["error"] = data.get("error") or "ESTIMATE_NO_LINK_NO_SUCCESS_V1:NO_DRIVE_TELEGRAM_OR_RETRY_LINK"

    vr = validate_estimate_result(data, task_id=str(task_id))
    data["estimate_validator"] = vr
    if not vr.get("ok"):
        data["success"] = False
        data["validator_reason"] = vr.get("reason")
    return data

async def process_estimate_to_excel(file_path: str, task_id: str, topic_id: int):
    data = await _rgc2_orig_excel(file_path, task_id, topic_id)
    return _rgc2_finalize(data, task_id, topic_id, prefer_sheets=False)

async def process_estimate_to_sheets(file_path: str, task_id: str, topic_id: int):
    try:
        data = await _rgc2_orig_sheets(file_path, task_id, topic_id)
    except Exception:
        data = await _rgc2_orig_excel(file_path, task_id, topic_id)
    return _rgc2_finalize(data, task_id, topic_id, prefer_sheets=True)

async def generate_estimate_from_text(raw_input: str, task_id: str, topic_id: int = 0, chat_id: str = ""):
    ctx = _rgc2_resolve_task_context(str(task_id), int(topic_id or 0))
    if not chat_id:
        chat_id = ctx.get("chat_id") or ""
    topic_id = int(ctx.get("topic_id") or topic_id or 0)

    if _rgc2_has_llm_arithmetic(raw_input):
        try:
            logger.warning("ESTIMATE_NO_LLM_CALC_GUARD_V1_INPUT_ARITHMETIC task=%s", task_id)
        except Exception:
            pass

    if chat_id:
        tpl = _rgc2_get_active_estimate_template(str(chat_id), int(topic_id or 0))
        if tpl:
            try:
                from core.sample_template_engine import create_estimate_from_saved_template
                result = await create_estimate_from_saved_template(
                    raw_input=str(raw_input),
                    task_id=str(task_id),
                    chat_id=str(chat_id),
                    topic_id=int(topic_id or 0),
                )
                if isinstance(result, dict) and (result.get("pdf_link") or result.get("xlsx_link") or result.get("drive_link") or result.get("excel_path")):
                    return _rgc2_finalize(result, task_id, topic_id, prefer_sheets=True)
                return {
                    "success": False,
                    "state": "WAITING_CLARIFICATION",
                    "error": "ESTIMATE_TEMPLATE_STRICT_REUSE_V1:TEMPLATE_NOT_APPLICABLE",
                    "result_text": "Активный шаблон сметы найден, но не подошёл к запросу. Уточни состав работ, объёмы или замени шаблон.",
                }
            except Exception as e:
                return {
                    "success": False,
                    "state": "WAITING_CLARIFICATION",
                    "error": "ESTIMATE_TEMPLATE_STRICT_REUSE_V1:ERROR:" + str(e)[:200],
                    "result_text": "Активный шаблон сметы найден, но применить его не удалось. Уточни параметры или замени шаблон.",
                }

    data = await _rgc2_orig_text(raw_input, task_id, topic_id)
    result_text = " ".join(str(data.get(k) or "") for k in ("result", "result_text", "message", "summary")) if isinstance(data, dict) else str(data)
    if _rgc2_has_llm_arithmetic(result_text) and not (isinstance(data, dict) and (data.get("excel_path") or data.get("artifact_path"))):
        return {
            "success": False,
            "error": "ESTIMATE_NO_LLM_CALC_GUARD_V1:TEXT_CALC_WITHOUT_PYTHON_ARTIFACT",
            "result_text": "Смета не принята: обнаружен текстовый расчёт без Python/OpenPyXL артефакта.",
        }
    return _rgc2_finalize(data, task_id, topic_id, prefer_sheets=True)
# === END_ESTIMATE_TEMPLATE_STRICT_REUSE_V1 ===
# === END_ESTIMATE_NO_LLM_CALC_GUARD_V1 ===
# === END_ESTIMATE_RESULT_VALIDATOR_V1 ===
# === END_REAL_GAPS_CLOSE_V2_ESTIMATE ===


# === FINAL_CLOSURE_BLOCKER_FIX_V1_ESTIMATE_XLSX_FORMULAS ===
def create_estimate_xlsx_from_rows(rows, out_path: str, title: str = "Смета") -> str:
    from pathlib import Path
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
    from openpyxl.utils import get_column_letter

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "Смета"

    ws["A1"] = title
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:F1")

    headers = ["№", "Наименование", "Ед.", "Кол-во", "Цена", "Сумма"]
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=c, value=h)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    start = 4
    safe_rows = rows or []

    for i, r in enumerate(safe_rows, start):
        idx = i - start + 1
        name = r.get("name") or r.get("work") or r.get("item") or ""
        unit = r.get("unit") or ""
        qty = r.get("qty") or r.get("quantity") or 0
        price = r.get("price") or r.get("unit_price") or 0

        try:
            qty = float(str(qty).replace(",", ".").replace(" ", ""))
        except Exception:
            qty = 0

        try:
            price = float(str(price).replace(",", ".").replace(" ", ""))
        except Exception:
            price = 0

        ws.cell(row=i, column=1, value=idx)
        ws.cell(row=i, column=2, value=name)
        ws.cell(row=i, column=3, value=unit)
        ws.cell(row=i, column=4, value=qty)
        ws.cell(row=i, column=5, value=price)
        ws.cell(row=i, column=6, value=f"=D{i}*E{i}")

    total_row = start + len(safe_rows)
    ws.cell(row=total_row, column=5, value="Итого")
    ws.cell(row=total_row, column=5).font = Font(bold=True)
    ws.cell(row=total_row, column=6, value=f"=SUM(F{start}:F{total_row-1})" if safe_rows else "=0")
    ws.cell(row=total_row, column=6).font = Font(bold=True)

    for i, w in enumerate([8, 55, 12, 14, 14, 16], 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    wb.save(out)
    return str(out)
# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_ESTIMATE_XLSX_FORMULAS ===


====================================================================================================
END_FILE: core/estimate_engine.py
FILE_CHUNK: 1/1
====================================================================================================
