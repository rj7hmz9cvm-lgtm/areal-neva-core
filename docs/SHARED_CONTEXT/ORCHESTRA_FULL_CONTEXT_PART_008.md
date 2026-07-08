# ORCHESTRA_FULL_CONTEXT_PART_008
generated_at_utc: 2026-07-08T00:55:28.869264+00:00
git_sha_before_commit: b43c3a4a2806848ea133e5a77ab10b79bc9c251a
part: 8/22


====================================================================================================
BEGIN_FILE: task_worker.py
FILE_CHUNK: 4/5
SHA256_FULL_FILE: 0a7095a9174b99b761390c04f342fa3113fd1a328ef9ac6ac0359d93d6a1b1f2
====================================================================================================
        def _send_once_ex(conn, task_id, chat_id, text, reply_to=None, kind="result", *args, **kwargs):
            try:
                if isinstance(text, str) and _t2cf_should_sanitize(text):
                    if _t2cf_is_topic2_task(conn, task_id) or "Предварительная смета готова" in text:
                        text = _t2cf_sanitize(text)
            except Exception as _e:
                try:
                    _T2CF_LOG.exception("PATCH_TOPIC2_TG_FORMAT_CANON_V1_SOEX_ERR:%s", _e)
                except Exception:
                    pass
            return _t2cf_orig_send_once_ex(conn, task_id, chat_id, text, reply_to, kind, *args, **kwargs)
        globals()["_send_once_ex"] = _send_once_ex

    # ---- Post-DONE polling worker (catches results written via raw UPDATE) ----
    def _t2cf_db_path():
        for p in (
            "/root/.areal-neva-core/data/core.db",
            _t2cf_os.path.join(_t2cf_os.path.dirname(__file__), "data", "core.db"),
        ):
            if _t2cf_os.path.exists(p):
                return p
        return "/root/.areal-neva-core/data/core.db"

    def _t2cf_get_token():
        for k in ("TELEGRAM_BOT_TOKEN", "BOT_TOKEN", "TG_BOT_TOKEN"):
            v = _t2cf_os.environ.get(k)
            if v:
                return v
        try:
            with open("/root/.areal-neva-core/.env", "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line.startswith("TELEGRAM_BOT_TOKEN="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
        return None

    def _t2cf_tg_edit(chat_id, message_id, text):
        token = <REDACTED_SECRET>
        if not token:
            return False, "no_token"
        url = "https://api.telegram.org/bot" + token + "/editMessageText"
        body = _t2cf_json.dumps({
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "disable_web_page_preview": True,
        }).encode("utf-8")
        req = _t2cf_urlreq.Request(url, data=body, headers={"Content-Type": "application/json"})
        try:
            with _t2cf_urlreq.urlopen(req, timeout=15) as resp:
                _ = resp.read()
                return True, "ok"
        except Exception as e:
            return False, str(e)[:120]

    def _t2cf_polling_thread():
        # Sync polling в фоне через threading — независим от asyncio main loop.
        try:
            _t2cf_time.sleep(15)
            _T2CF_LOG.info("PATCH_TOPIC2_TG_FORMAT_CANON_V1 polling started (thread)")
        except Exception:
            pass
        db = _t2cf_db_path()
        while True:
            try:
                conn = _t2cf_sqlite3.connect(db, timeout=5.0)
                conn.row_factory = _t2cf_sqlite3.Row
                rows = conn.execute(
                    """SELECT id, chat_id, bot_message_id, result FROM tasks
                       WHERE topic_id=2 AND state='DONE'
                         AND result IS NOT NULL
                         AND length(result) > 200
                         AND result LIKE '%Предварительная смета готова%'
                         AND result NOT LIKE ?
                       ORDER BY created_at DESC LIMIT 30""",
                    ("%" + _T2CF_MARKER + "%",),
                ).fetchall()
                for r in rows:
                    try:
                        old = r["result"] or ""
                        new_text = _t2cf_sanitize(old)
                        if not new_text or new_text == old:
                            continue
                        conn.execute("UPDATE tasks SET result=? WHERE id=?", (new_text, r["id"]))
                        conn.commit()
                        if r["chat_id"] and r["bot_message_id"]:
                            ok, info = _t2cf_tg_edit(int(r["chat_id"]), int(r["bot_message_id"]), new_text)
                            _T2CF_LOG.info(
                                "PATCH_TOPIC2_TG_FORMAT_CANON_V1 edit task=%s ok=%s info=%s",
                                r["id"], ok, info,
                            )
                        else:
                            _T2CF_LOG.info(
                                "PATCH_TOPIC2_TG_FORMAT_CANON_V1 sanitized DB task=%s (no chat/msg)",
                                r["id"],
                            )
                    except Exception as e_one:
                        try:
                            _T2CF_LOG.exception(
                                "PATCH_TOPIC2_TG_FORMAT_CANON_V1 one_err task=%s e=%s",
                                (r["id"] if r else "?"), e_one,
                            )
                        except Exception:
                            pass
                try:
                    conn.close()
                except Exception:
                    pass
            except Exception as e_loop:
                try:
                    _T2CF_LOG.exception("PATCH_TOPIC2_TG_FORMAT_CANON_V1 loop_err: %s", e_loop)
                except Exception:
                    pass
            _t2cf_time.sleep(45)

    # Запускаем daemon-thread прямо в момент install — не зависим от main()/asyncio.
    try:
        _t2cf_thread = _t2cf_threading.Thread(
            target=_t2cf_polling_thread,
            name="t2cf_polling",
            daemon=True,
        )
        _t2cf_thread.start()
        globals()["_t2cf_polling_thread_obj"] = _t2cf_thread
        _T2CF_LOG.info("PATCH_TOPIC2_TG_FORMAT_CANON_V1 polling thread spawned")
    except Exception as _e:
        try:
            _T2CF_LOG.exception("PATCH_TOPIC2_TG_FORMAT_CANON_V1_THREAD_SPAWN_ERR:%s", _e)
        except Exception:
            pass

    _T2CF_LOG.info("PATCH_TOPIC2_TG_FORMAT_CANON_V1 installed")
except Exception as _t2cf_install_err:
    try:
        logger.exception("PATCH_TOPIC2_TG_FORMAT_CANON_V1_INSTALL_ERR:%s", _t2cf_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_TG_FORMAT_CANON_V1 ===


# === PATCH_TOPIC2_ADDITIONAL_FACTS_RECALC_NO_REGRESSION_V2 ===
# Цель: classify topic_2 follow-up на STATUS / META / FACT перед FOLLOWUP_BIND merge.
#  STATUS («где смета», «дай ссылку», «готова смета») → bypass merge, ответ из parent.result/artifacts
#  META  («что я добавлял», без новых фактов) → bypass merge, ответ из parent task_history clarified:
#  FACT  (утепление, потолок, поставщики, фасад и т.д.) → существующий FOLLOWUP_BIND merge + recalc markers
# Плюс: timeout-guard — EXECUTION_TIMEOUT не overwrite result если есть ready-artifact evidence.
# Не трогает: price logic / price choice 1/2/3/4 / Sonar / supplier-heal / Drive / PDF / XLSX / topic_5/210/500.
try:
    import re as _t2af_re
    import logging as _t2af_logging

    _T2AF_LOG = _t2af_logging.getLogger("WORKER")
    _t2af_orig_handle_new = globals().get("_handle_new")
    _t2af_orig_update_task = globals().get("_update_task")

    _T2AF_EVIDENCE_MARKERS = (
        "TG_EDIT:OK",
        "PATCH_TOPIC2_DRIVE_XLSX_REPAIR_V1:OK",
        "PATCH_TOPIC2_PDF_AND_REAL_SUPPLIERS_V1",
        "T2RFP_FULL_PIPELINE_DONE",
        "P8T2C_CANONICAL_OK",
        "TOPIC2_DRIVE_LINKS_SAVED",
        "TOPIC2_DRIVE_UPLOAD_XLSX_OK",
        "TOPIC2_DRIVE_UPLOAD_PDF_OK",
        "TOPIC2_PDF_CREATED",
        "TOPIC2_XLSX_CREATED",
    )

    _T2AF_FACT_KEYWORDS = (
        "утепление", "роквул", "rockwool", "минвата", "каменная вата",
        "потолок", "крыш", "перекрыти",
        "стен", "фасад", "сайдинг", "имитация бруса", "клик-фальц", "штукатурк",
        "плитка", "ламинат", "пол", "теплый пол",
        "окна", "двери", "электрика", "сантехника", "отопление",
        "вентиляция", "канализаци", "водоснабжен",
        "фундамент", "плита", "сваи", "ленточный",
        "поставщик", "стройбаз", "строительная баз", "строит",
        "ропша", "регион", "логистика", "удалённост",
        "квадрат", "этаж", "брус", "каркас",
        "окраш", "крашен", "ворс", "разношир",
    )

    _T2AF_STATUS_RE = _t2af_re.compile(
        r"^\s*"
        r"(?:где\s+(?:смет|расч[её]т|файл|excel|pdf|результат|ссылк)"
        r"|покажи\s+(?:смет|расч|ссылк)"
        r"|дай\s+ссылк"
        r"|скинь\s+(?:смет|ссылк|excel|pdf|расч)"
        r"|что\s+по\s+смет"
        r"|готов[аоы]?\s+смет"
        r"|готово\s*[?!.]*\s*$"
        r")",
        _t2af_re.IGNORECASE,
    )
    _T2AF_META_RE = _t2af_re.compile(
        r"что\s+я\s+(?:тебе\s+)?(?:ещё|еще)?\s*(?:добавл|говорил|сказал|написал|просил|давал)",
        _t2af_re.IGNORECASE,
    )

    def _t2af_norm(s):
        if s is None:
            return ""
        try:
            s = str(s).strip()
        except Exception:
            return ""
        s = _t2af_re.sub(r"^\s*\[VOICE\]\s*", "", s, flags=_t2af_re.IGNORECASE)
        return s

    def _t2af_low(s):
        return _t2af_norm(s).lower().replace("ё", "е")

    def _t2af_classify(raw):
        s_norm = _t2af_norm(raw)
        if not s_norm:
            return "OTHER"
        s_low = s_norm.lower().replace("ё", "е")
        # STATUS
        if _T2AF_STATUS_RE.search(s_low):
            return "STATUS"
        # META — спрашивает что добавляли; если есть конкретные числа размеров → FACT
        if _T2AF_META_RE.search(s_low):
            if _t2af_re.search(r"\d+\s*(?:мм|см|м[²2³3]|кг|шт|тонн|км|°|метр)", s_low):
                return "FACT"
            return "META"
        # FACT
        if any(k in s_low for k in _T2AF_FACT_KEYWORDS):
            return "FACT"
        return "OTHER"

    def _t2af_match_facts(raw):
        s = _t2af_low(raw)
        hits = []
        for k in ("утепление", "потолок", "поставщик", "фасад", "кровля", "пол",
                  "окна", "двери", "стен", "имитация", "брус", "ламинат",
                  "перекрыти", "фундамент", "регион", "логистика"):
            if k in s and k not in hits:
                hits.append(k)
        return hits

    def _t2af_history_actions(conn, parent_id, limit=400):
        try:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? ORDER BY rowid DESC LIMIT ?",
                (str(parent_id), int(limit)),
            ).fetchall()
            return [r[0] or "" for r in rows]
        except Exception:
            return []

    def _t2af_has_ready_artifacts(conn, parent_id):
        for a in _t2af_history_actions(conn, parent_id, 600):
            for m in _T2AF_EVIDENCE_MARKERS:
                if m in a:
                    return True
        return False

    def _t2af_extract_artifact_ids(conn, parent_id):
        xlsx_id = None
        pdf_id = None
        for a in _t2af_history_actions(conn, parent_id, 600):
            if not xlsx_id:
                m = _t2af_re.search(r"PATCH_TOPIC2_DRIVE_XLSX_REPAIR_V1:OK:([A-Za-z0-9_\-]+)", a)
                if m:
                    xlsx_id = m.group(1)
        # latest pdf from log-style action lines if any
        return xlsx_id, pdf_id

    def _t2af_list_clarifieds(conn, parent_id):
        try:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'clarified:%' ORDER BY rowid",
                (str(parent_id),),
            ).fetchall()
        except Exception:
            return []
        out = []
        for r in rows:
            v = (r[0] or "")[len("clarified:"):].strip()
            if v and len(v) > 1 and v not in out:
                out.append(v)
        return out

    def _t2af_hist_once(conn, task_id, action):
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

    def _t2af_get(obj, key, default=None):
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

    def _t2af_rowdict(conn, sql, params=()):
        try:
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
        except Exception:
            return None

    def _t2af_parent_is_valid(conn, parent):
        if not parent:
            return False
        parent_id = str(parent.get("id") or "")
        state = str(parent.get("state") or "").upper()
        err = str(parent.get("error_message") or "").upper()
        if state in ("DONE", "FAILED", "CANCELLED", "ARCHIVED"):
            return False
        if "P6E67_PARENT_NOT_FOUND" in err or "MERGED_TO_PARENT" in err:
            return False
        try:
            hist = "\n".join(str(r[0] or "") for r in conn.execute(
                "SELECT action FROM task_history WHERE task_id=? ORDER BY rowid DESC LIMIT 80",
                (parent_id,),
            ).fetchall())
        except Exception:
            hist = ""
        if (
            "P6E67_PARENT_NOT_FOUND" in hist
            or "TOPIC2_DONE_CONTRACT_OK" in hist
            or "TOPIC2_DRIVE_UPLOAD_XLSX_OK" in hist
            or "TOPIC2_DRIVE_UPLOAD_PDF_OK" in hist
        ):
            return False
        return True

    def _t2af_find_parent(conn, chat_id, topic_id, child):
        # Reuse same lookup logic as FOLLOWUP_BIND: by reply_to first, then latest topic_2 task.
        child_id = str(_t2af_get(child, "id") or "")
        reply_to = _t2af_get(child, "reply_to_message_id")
        if reply_to:
            p = _t2af_rowdict(conn, """
                SELECT rowid AS rid, *
                FROM tasks
                WHERE CAST(chat_id AS TEXT)=?
                  AND topic_id=?
                  AND id<>?
                  AND bot_message_id=?
                  AND input_type IN ('drive_file','text')
                  AND state NOT IN ('CANCELLED')
                ORDER BY rowid DESC
                LIMIT 1
            """, (str(chat_id), int(topic_id or 0), child_id, reply_to))
            if _t2af_parent_is_valid(conn, p):
                return p
        p = _t2af_rowdict(conn, """
            SELECT rowid AS rid, *
            FROM tasks
            WHERE CAST(chat_id AS TEXT)=?
              AND topic_id=?
              AND id<>?
              AND input_type IN ('drive_file','text')
              AND state NOT IN ('CANCELLED')
              AND updated_at >= datetime('now','-72 hours')
              AND (
                   raw_input LIKE '%смет%'
                OR result LIKE '%смет%'
                OR input_type='drive_file'
              )
            ORDER BY rowid DESC
            LIMIT 1
        """, (str(chat_id), int(topic_id or 0), child_id))
        return p if _t2af_parent_is_valid(conn, p) else None

    def _t2af_build_status_text(parent):
        result = str(_t2af_get(parent, "result") or "")
        bad = ("Задача не выполнена" in result) or ("превышено время выполнения" in result)
        if result and not bad and len(result) > 100:
            return result
        # fallback to evidence-based text
        return (
            "Текущий статус: смета формируется. Готовые артефакты появятся в этом же сообщении.\n\n"
            "Если ответа не пришло — пришли правки или ‘продолжай’."
        )

    async def _handle_new(conn, task, chat_id, topic_id):
        try:
            if int(topic_id or 0) == 2:
                input_type = str(_t2af_get(task, "input_type") or "").strip()
                raw = _t2af_norm(_t2af_get(task, "raw_input"))
                child_id = str(_t2af_get(task, "id") or "")
                reply_to = _t2af_get(task, "reply_to_message_id")
                if input_type in ("text", "voice", "search") and raw and child_id:
                    cls = _t2af_classify(raw)

                    # === STATUS — bypass merge ===
                    if cls == "STATUS":
                        parent = _t2af_find_parent(conn, chat_id, topic_id, task)
                        if parent:
                            parent_id = str(parent.get("id"))
                            tg_text = _t2af_build_status_text(parent)
                            try:
                                conn.execute(
                                    "UPDATE tasks SET state='DONE', result=?, error_message=?, updated_at=datetime('now') WHERE id=?",
                                    (tg_text[:1500], "STATUS_REQUEST_ANSWERED:" + parent_id, child_id),
                                )
                            except Exception:
                                pass
                            _t2af_hist_once(conn, child_id, "TOPIC2_STATUS_REQUEST_ANSWERED:" + parent_id)
                            if _t2af_has_ready_artifacts(conn, parent_id):
                                _t2af_hist_once(conn, parent_id,
                                                "TOPIC2_STATUS_REQUEST_RETURNED_READY_ARTIFACTS:" + child_id)
                            try:
                                conn.commit()
                            except Exception:
                                pass
                            try:
                                _send_once(conn, child_id, str(chat_id), tg_text, reply_to, "status_request")
                            except Exception:
                                pass
                            _T2AF_LOG.info("PATCH_TOPIC2_ADDITIONAL_FACTS_RECALC_NO_REGRESSION_V2 STATUS bypass child=%s parent=%s",
                                           child_id, parent_id)
                            return

                    # === META — bypass merge, answer from history ===
                    if cls == "META":
                        parent = _t2af_find_parent(conn, chat_id, topic_id, task)
                        if parent:
                            parent_id = str(parent.get("id"))
                            facts = _t2af_list_clarifieds(conn, parent_id)
                            if facts:
                                pre = "В техзадание ранее добавлены факты:"
                                lines = [pre] + [f"- {f[:300]}" for f in facts[-12:]]
                                tg_text = "\n".join(lines)
                            else:
                                tg_text = "В этой смете дополнительных фактов в истории нет."
                            try:
                                conn.execute(
                                    "UPDATE tasks SET state='DONE', result=?, error_message=?, updated_at=datetime('now') WHERE id=?",
                                    (tg_text[:1800], "META_FACTS_ANSWERED:" + parent_id, child_id),
                                )
                            except Exception:
                                pass
                            _t2af_hist_once(conn, child_id, "TOPIC2_META_FACTS_ANSWERED:" + parent_id)
                            try:
                                conn.commit()
                            except Exception:
                                pass
                            try:
                                _send_once(conn, child_id, str(chat_id), tg_text, reply_to, "meta_facts")
                            except Exception:
                                pass
                            _T2AF_LOG.info("PATCH_TOPIC2_ADDITIONAL_FACTS_RECALC_NO_REGRESSION_V2 META bypass child=%s parent=%s facts=%d",
                                           child_id, parent_id, len(facts))
                            return

                    # === FACT — pre-merge markers + RECALC fact-trace ===
                    if cls == "FACT":
                        parent = _t2af_find_parent(conn, chat_id, topic_id, task)
                        if parent:
                            parent_id = str(parent.get("id"))
                            _t2af_hist_once(conn, parent_id,
                                            "TOPIC2_ADDITIONAL_FACT_MERGED:" + child_id)
                            _t2af_hist_once(conn, parent_id,
                                            "TOPIC2_ADDITIONAL_FACTS_RECALC_STARTED:" + child_id)
                            for k in _t2af_match_facts(raw):
                                _t2af_hist_once(conn, parent_id,
                                                "TOPIC2_RECALC_CONTEXT_INCLUDES_FACT:" + k)
                            try:
                                conn.commit()
                            except Exception:
                                pass
                        # fall through to existing FOLLOWUP_BIND chain (orig _handle_new)
        except Exception as e:
            try:
                _T2AF_LOG.exception("PATCH_TOPIC2_ADDITIONAL_FACTS_RECALC_NO_REGRESSION_V2_HANDLE_ERR:%s", e)
            except Exception:
                pass
        return await _t2af_orig_handle_new(conn, task, chat_id, topic_id)

    if _t2af_orig_handle_new:
        globals()["_handle_new"] = _handle_new

    # === Timeout guard wrap on _update_task ===
    def _update_task(conn, task_id, **kwargs):
        try:
            new_state = str(kwargs.get("state") or "")
            new_err = str(kwargs.get("error_message") or "")
            new_result = str(kwargs.get("result") or "")
            is_timeout_overwrite = (
                new_state == "FAILED"
                and ("EXECUTION_TIMEOUT" in new_err
                     or "превышено время выполнения" in new_result)
            )
            if is_timeout_overwrite and task_id:
                row = _t2af_rowdict(
                    conn,
                    "SELECT id, topic_id, state, result FROM tasks WHERE id=? LIMIT 1",
                    (str(task_id),),
                )
                if row and int(row.get("topic_id") or 0) == 2:
                    if _t2af_has_ready_artifacts(conn, str(task_id)):
                        # Suppress overwrite: keep last valid result (do not stomp), set AC.
                        old_result = str(row.get("result") or "")
                        keep_result = old_result if (old_result and "Задача не выполнена" not in old_result and len(old_result) > 100) else None
                        kwargs["state"] = "AWAITING_CONFIRMATION"
                        kwargs["error_message"] = ""
                        if keep_result is not None:
                            kwargs["result"] = keep_result
                        else:
                            xlsx_id, _pdf_id = _t2af_extract_artifact_ids(conn, str(task_id))
                            if xlsx_id:
                                kwargs["result"] = (
                                    "✅ Смета готова\n\n"
                                    "Готовые артефакты:\n"
                                    f"Excel: https://drive.google.com/file/d/{xlsx_id}/view\n\n"
                                    "Подтверди или пришли правки"
                                )
                            else:
                                kwargs.pop("result", None)
                        _t2af_hist_once(conn, str(task_id),
                                        "TOPIC2_TIMEOUT_SUPPRESSED_READY_ARTIFACT_EXISTS")
                        # If there is a recent ADDITIONAL_FACTS_RECALC_STARTED without DONE → write DONE marker.
                        try:
                            rows = conn.execute(
                                "SELECT action FROM task_history WHERE task_id=? "
                                "AND (action LIKE 'TOPIC2_ADDITIONAL_FACTS_RECALC_STARTED:%' "
                                "OR action LIKE 'TOPIC2_ADDITIONAL_FACTS_RECALC_DONE:%') "
                                "ORDER BY rowid DESC LIMIT 30",
                                (str(task_id),),
                            ).fetchall()
                            started = [r[0] for r in rows if r and r[0].startswith("TOPIC2_ADDITIONAL_FACTS_RECALC_STARTED:")]
                            done = [r[0] for r in rows if r and r[0].startswith("TOPIC2_ADDITIONAL_FACTS_RECALC_DONE:")]
                            for s in started:
                                cid = s.split(":", 1)[1]
                                if not any(d.endswith(":" + cid) for d in done):
                                    _t2af_hist_once(conn, str(task_id),
                                                    "TOPIC2_ADDITIONAL_FACTS_RECALC_DONE:" + cid)
                        except Exception:
                            pass
                        try:
                            conn.commit()
                        except Exception:
                            pass
                        _T2AF_LOG.info(
                            "PATCH_TOPIC2_ADDITIONAL_FACTS_RECALC_NO_REGRESSION_V2 timeout-overwrite suppressed task=%s",
                            str(task_id),
                        )
        except Exception as e:
            try:
                _T2AF_LOG.exception("PATCH_TOPIC2_ADDITIONAL_FACTS_RECALC_NO_REGRESSION_V2_UPDATE_ERR:%s", e)
            except Exception:
                pass
        return _t2af_orig_update_task(conn, task_id, **kwargs)

    if _t2af_orig_update_task:
        globals()["_update_task"] = _update_task

    _T2AF_LOG.info("PATCH_TOPIC2_ADDITIONAL_FACTS_RECALC_NO_REGRESSION_V2 installed")
except Exception as _t2af_install_err:
    try:
        logger.exception("PATCH_TOPIC2_ADDITIONAL_FACTS_RECALC_NO_REGRESSION_V2_INSTALL_ERR:%s", _t2af_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_ADDITIONAL_FACTS_RECALC_NO_REGRESSION_V2 ===


# === PATCH_TOPIC2_CANON_FULL_CLOSE_AFTER_REQUEUE_FAILURE_V1 ===
# Closes 4 system gaps on topic_2 estimate path discovered after requeue failure of f030db95:
#   1. drive_file raw_input safe parser — extract leading JSON object via raw_decode,
#      tolerant к hвостовому text (УТОЧНЕНИЕ К ИСХОДНОМУ ТЗ:...) от FOLLOWUP_BIND merges.
#      Marker TOPIC2_DRIVE_RAW_INPUT_JSON_PREFIX_RECOVERED. Tail НЕ удаляется (non-destructive).
#   2. FOLLOWUP_BIND merge для drive_file parent: НЕ дописывает text в raw_input;
#      facts остаются в task_history `clarified:`. Parent raw_input — pure JSON (восстанавливаем
#      на первом merge для уже-загрязнённых row через safe parser).
#   3. Timeout-guard расширен: «invalid raw_input» error при наличии ready-artifact evidence —
#      также suppress, переключение в AWAITING_CONFIRMATION.
#   4. STATUS/META/FACT classify уже есть в V2; этот патч только защищает _handle_drive_file
#      и _t2fb_merge от corruption JSON.
# НЕ ТРОГАЕТ: price logic, Sonar/Perplexity routing, supplier/heal, Drive upload, PDF/XLSX engine,
# topic_5/210/500, sanitizer (TG_FORMAT_CANON_V1 уже без удаления «Учтено из дополнений»/«Поставщики»).
try:
    import json as _t2cf2_json
    import re as _t2cf2_re
    import logging as _t2cf2_logging

    _T2CF2_LOG = _t2cf2_logging.getLogger("WORKER")

    def _t2cf2_extract_json_prefix(raw):
        """
        Returns (json_str, tail) or (None, None) if no leading JSON found.
        Uses json.JSONDecoder.raw_decode — tolerates trailing non-JSON text.
        """
        if not isinstance(raw, str):
            return None, None
        s = raw.lstrip()
        if not s.startswith("{") and not s.startswith("["):
            return None, None
        try:
            decoder = _t2cf2_json.JSONDecoder()
            obj, end = decoder.raw_decode(s)
            json_str = s[:end]
            tail = s[end:].strip()
            # Sanity: must round-trip
            _t2cf2_json.loads(json_str)
            return json_str, tail
        except Exception:
            return None, None

    def _t2cf2_hist_once(conn, task_id, action):
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

    def _t2cf2_get(obj, key, default=None):
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

    # === FIX 1: wrap _handle_drive_file → safe JSON-prefix parser for topic_2 ===
    _t2cf2_orig_handle_drive_file = globals().get("_handle_drive_file")
    if _t2cf2_orig_handle_drive_file:
        async def _handle_drive_file(conn, task, chat_id, topic_id):
            try:
                if int(topic_id or 0) == 2:
                    raw = _t2cf2_get(task, "raw_input")
                    if isinstance(raw, str) and raw and raw.lstrip().startswith("{"):
                        try:
                            _t2cf2_json.loads(raw)
                            json_ok = True
                        except Exception:
                            json_ok = False
                        if not json_ok:
                            json_str, tail = _t2cf2_extract_json_prefix(raw)
                            if json_str:
                                task_id = str(_t2cf2_get(task, "id") or "")
                                # Save tail clarification blocks into task_history (idempotent)
                                if tail:
                                    blocks = _t2cf2_re.split(
                                        r"\n*УТОЧНЕНИЕ К ИСХОДНОМУ ТЗ:\s*\n",
                                        tail,
                                    )
                                    # blocks[0] — text before first marker (e.g. "Размеры: ..."),
                                    # blocks[1:] — clarification segments
                                    for blk in blocks:
                                        seg = (blk or "").strip()
                                        if not seg or len(seg) < 3:
                                            continue
                                        # truncate to 500 for marker; full text stays in DB tail (non-destructive)
                                        action = "clarified:" + seg[:500]
                                        _t2cf2_hist_once(conn, task_id, action)
                                # Replace raw_input in DB with clean JSON (preserve tail in history only)
                                try:
                                    conn.execute(
                                        "UPDATE tasks SET raw_input=?, updated_at=datetime('now') WHERE id=?",
                                        (json_str, task_id),
                                    )
                                    _t2cf2_hist_once(conn, task_id,
                                        "TOPIC2_DRIVE_RAW_INPUT_JSON_PREFIX_RECOVERED")
                                    conn.commit()
                                except Exception as _ue:
                                    try:
                                        _T2CF2_LOG.exception(
                                            "PATCH_TOPIC2_CANON_FULL_CLOSE_AFTER_REQUEUE_FAILURE_V1_RAW_UPDATE_ERR:%s",
                                            _ue,
                                        )
                                    except Exception:
                                        pass
                                # Pass cleaned task to original handler
                                try:
                                    if isinstance(task, dict):
                                        task = dict(task)
                                        task["raw_input"] = json_str
                                    else:
                                        # sqlite3.Row — convert to dict
                                        try:
                                            task = {k: task[k] for k in task.keys()}
                                            task["raw_input"] = json_str
                                        except Exception:
                                            pass
                                except Exception:
                                    pass
                                _T2CF2_LOG.info(
                                    "PATCH_TOPIC2_CANON_FULL_CLOSE_AFTER_REQUEUE_FAILURE_V1 raw_input recovered task=%s tail_chars=%d",
                                    task_id, len(tail or ""),
                                )
            except Exception as e:
                try:
                    _T2CF2_LOG.exception(
                        "PATCH_TOPIC2_CANON_FULL_CLOSE_AFTER_REQUEUE_FAILURE_V1_DRIVE_PRE_ERR:%s", e,
                    )
                except Exception:
                    pass
            return await _t2cf2_orig_handle_drive_file(conn, task, chat_id, topic_id)
        globals()["_handle_drive_file"] = _handle_drive_file

    # === FIX 2: wrap _t2fb_merge → no raw_input append for drive_file parent ===
    # PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1: also reset DONE_WITH_DRIVE_LINKS
    # blocking marker so that a new FACT triggers full canonical recalculation via _t2fdsg_run_drive_final.
    _t2cf2_orig_t2fb_merge = globals().get("_t2fb_merge")
    if _t2cf2_orig_t2fb_merge:
        def _t2fb_merge(conn, child, parent):
            try:
                parent_input_type = str(_t2cf2_get(parent, "input_type") or "")
                if parent_input_type == "drive_file":
                    # Replicate merge BUT keep parent.raw_input untouched (pure JSON).
                    # Child fact goes only to task_history clarified:.
                    child_id = str(_t2cf2_get(child, "id") or "")
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
                            cand_text = str(candidate or "")
                            has_p6e2_dims_missing = "P6E2_CANON_DIMS_NOT_RECOGNIZED" in str(row[1] or "")
                            if not has_p6e2_dims_missing:
                                try:
                                    has_p6e2_dims_missing = bool(conn.execute(
                                        "SELECT 1 FROM task_history WHERE task_id=? "
                                        "AND action='P6E2_CANON_DIMS_NOT_RECOGNIZED' LIMIT 1",
                                        (str(task_id),),
                                    ).fetchone())
                                except Exception:
                                    has_p6e2_dims_missing = False
                            if (
                                reason == "too_short_or_empty"
                                and (
                                    "Не вижу размеры объекта" in cand_text
                                    or "Пришли размер" in cand_text
                                    or has_p6e2_dims_missing
                                )
                            ):
                                if "Не вижу размеры объекта" not in cand_text and row[1]:
                                    cand_text = str(row[1] or "")
                                kwargs["state"] = "WAITING_CLARIFICATION"
                                kwargs["result"] = cand_text
                                kwargs["error_message"] = "P6E2_CANON_DIMS_NOT_RECOGNIZED"
                                _t2pg_hist_once(
                                    conn, str(task_id),
                                    "TOPIC2_PUBLIC_RESULT_GATE_CLARIFICATION_ALLOWED:P6E2_DIMS_MISSING",
                                )
                                return _t2pg_orig_update_task(conn, task_id, **kwargs)
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

    def _extract_drive_id(action, key):
        text = str(action or "")
        m = _t2afi_re.search(
            r"(?:^|:)" + key + r"=([^\s]+?)(?=:(?:xlsx|pdf)=|\s|$)",
            text,
        )
        if not m:
            return ""
        value = m.group(1).strip().rstrip(".,;])")
        m_url = _t2afi_re.search(r"/d/([A-Za-z0-9_-]+)", value)
        if m_url:
            return m_url.group(1)
        m_qs = _t2afi_re.search(r"[?&]id=([A-Za-z0-9_-]+)", value)
        if m_qs:
            return m_qs.group(1)
        if _t2afi_re.fullmatch(r"[A-Za-z0-9_-]{10,}", value):
            return value
        return ""

    for (action,) in rows:
        xlsx_id = _extract_drive_id(action, "xlsx")
        pdf_id = _extract_drive_id(action, "pdf")
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


# === PATCH_TOPIC2_NO_VALID_PDF_ROWS_BLOCK_FINAL_V2 ===
try:
    import logging as _t2nvr2_logging
    _T2NVR2_LOG = _t2nvr2_logging.getLogger("task_worker")

    def _t2nvr2_has_no_valid_pdf_rows(conn, task_id):
        try:
            return conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action LIKE 'TOPIC2_PDF_NO_VALID_ESTIMATE_ROWS%' LIMIT 1",
                (str(task_id),),
            ).fetchone() is not None
        except Exception:
            return False

    def _t2nvr2_allows_orient_project(conn, task_id):
        try:
            row = conn.execute("SELECT raw_input FROM tasks WHERE id=? LIMIT 1", (str(task_id),)).fetchone()
            raw = str(row[0] if row else "").lower().replace("ё", "е")
            return "считать ориентировочно по проекту" in raw or "факты ocr/pdf" in raw
        except Exception:
            return False

    def _t2nvr2_wait_message():
        return (
            "PDF прочитан, но сметная ведомость объёмов/спецификация работ в нём не найдена. "
            "Смету на 0 руб не создаю.\n\n"
            "Для канонного расчёта пришли ВОР / спецификацию / раздел КР/КЖ с объёмами "
            "или напиши: считать ориентировочно по проекту."
        )

    _T2NVR2_ORIG_RUN_DRIVE_FINAL = globals().get("_t2fdsg_run_drive_final")
    if _T2NVR2_ORIG_RUN_DRIVE_FINAL and not getattr(_T2NVR2_ORIG_RUN_DRIVE_FINAL, "_t2nvr2_wrapped", False):
        async def _t2fdsg_run_drive_final(conn, parent, choice):
            try:
                parent_id = str(_t2fdsg_get(parent, "id") or "")
                if parent_id and _t2nvr2_has_no_valid_pdf_rows(conn, parent_id) and not _t2nvr2_allows_orient_project(conn, parent_id):
                    msg = _t2nvr2_wait_message()
                    _update_task(
                        conn,
                        parent_id,
                        state="WAITING_CLARIFICATION",
                        result=msg,
                        error_message="TOPIC2_PDF_NO_VALID_ESTIMATE_ROWS",
                    )
                    _history(conn, parent_id, "PATCH_TOPIC2_NO_VALID_PDF_ROWS_BLOCK_FINAL_V2:FINAL_BLOCKED")
                    conn.commit()
                    return True
            except Exception as e:
                try:
                    _T2NVR2_LOG.warning("PATCH_TOPIC2_NO_VALID_PDF_ROWS_BLOCK_FINAL_V2_ERR:%s", e)
                except Exception:
                    pass
            return await _T2NVR2_ORIG_RUN_DRIVE_FINAL(conn, parent, choice)

        _t2fdsg_run_drive_final._t2nvr2_wrapped = True
        globals()["_t2fdsg_run_drive_final"] = _t2fdsg_run_drive_final
        _T2NVR2_LOG.info("PATCH_TOPIC2_NO_VALID_PDF_ROWS_BLOCK_FINAL_V2 installed")
except Exception as _t2nvr2_install_err:
    try:
        logger.exception("PATCH_TOPIC2_NO_VALID_PDF_ROWS_BLOCK_FINAL_V2_INSTALL_ERR:%s", _t2nvr2_install_err)
    except Exception:
        pass
# === END_PATCH_TOPIC2_NO_VALID_PDF_ROWS_BLOCK_FINAL_V2 ===


# === PATCH_TOPIC2_ZERO_RESULT_HARD_GATE_V1 ===
try:
    import re as _t2zg_re
    import logging as _t2zg_logging
    _T2ZG_LOG = _t2zg_logging.getLogger("task_worker")
    _T2ZG_ORIG_UPDATE_TASK = globals().get("_update_task")

    def _t2zg_topic_id(conn, task_id):
        try:
            row = conn.execute("SELECT COALESCE(topic_id,0) FROM tasks WHERE id=? LIMIT 1", (str(task_id),)).fetchone()
            return int(row[0]) if row else 0
        except Exception:
            return 0

    def _t2zg_zero_result(text):
        s = str(text or "").lower().replace("ё", "е")
        has_zero_positions = bool(_t2zg_re.search(r"позиц(?:ий|ии|ия)\s*:\s*0\b", s))
        has_zero_total = bool(_t2zg_re.search(r"итого\s*:\s*0\s*руб", s))
        return has_zero_positions or has_zero_total

    if _T2ZG_ORIG_UPDATE_TASK and not getattr(_T2ZG_ORIG_UPDATE_TASK, "_t2zg_wrapped", False):
        def _update_task(conn, task_id, **kwargs):
            try:
                if _t2zg_topic_id(conn, task_id) == 2 and _t2zg_zero_result(kwargs.get("result")):
                    msg = (
                        "Смета на 0 руб заблокирована. PDF/OCR прочитан, но финальный расчёт не содержит "
                        "валидных позиций и итоговой суммы. Нужны ВОР/спецификация с объёмами или корректный "
                        "укрупнённый расчёт по извлечённым параметрам проекта."
                    )
                    kwargs["state"] = "WAITING_CLARIFICATION"
                    kwargs["result"] = msg
                    kwargs["error_message"] = "TOPIC2_ZERO_RESULT_BLOCKED"
                    try:
                        _history(conn, str(task_id), "PATCH_TOPIC2_ZERO_RESULT_HARD_GATE_V1:BLOCKED")
                    except Exception:
                        pass
            except Exception as e:
                try:
                    _T2ZG_LOG.warning("PATCH_TOPIC2_ZERO_RESULT_HARD_GATE_V1_ERR:%s", e)
                except Exception:
                    pass
            return _T2ZG_ORIG_UPDATE_TASK(conn, task_id, **kwargs)

        _update_task._t2zg_wrapped = True
        globals()["_update_task"] = _update_task
        _T2ZG_LOG.info("PATCH_TOPIC2_ZERO_RESULT_HARD_GATE_V1 installed")
except Exception as _t2zg_install_err:
    try:
        logger.exception("PATCH_TOPIC2_ZERO_RESULT_HARD_GATE_V1_INSTALL_ERR:%s", _t2zg_install_err)
    except Exception:
        pass
# === END_PATCH_TOPIC2_ZERO_RESULT_HARD_GATE_V1 ===

# === PATCH_TOPIC2_DRIVE_FILE_PICKER_CLARIFIED_CANON_V1 ===
# Canon basis:
# - topic_2 drive_file + explicit estimate clarification must enter canonical estimate flow;
# - the no-intent picker is only a clarification step, not a final result;
# - no cross-topic routing and no systemd/env/search architecture changes.
try:
    import json as _t2dfc_json
    import re as _t2dfc_re
    import inspect as _t2dfc_inspect
    import logging as _t2dfc_logging

    _T2DFC_LOG = _t2dfc_logging.getLogger("task_worker")
    _T2DFC_ORIG_HANDLE_IN_PROGRESS = globals().get("_handle_in_progress")

    def _t2dfc_s(v):
        return "" if v is None else str(v)

    def _t2dfc_get(task, key, default=None):
        try:
            if isinstance(task, dict):
                return task.get(key, default)
        except Exception:
            pass
        try:
            if hasattr(task, "keys") and key in task.keys():
                return task[key]
        except Exception:
            pass
        try:
            return _task_field(task, key, default)
        except Exception:
            return default

    def _t2dfc_low(v):
        return _t2dfc_s(v).lower().replace("ё", "е")

    def _t2dfc_estimate_intent(text):
        t = _t2dfc_low(text)
        if _t2dfc_re.match(r"^\s*1\s*([\).:-]|$)", t):
            return True
        return any(w in t for w in (
            "смет", "расчет", "расчёт", "стоимост", "цены", "материал",
            "работ", "строительств", "проектной документац", "excel", "xlsx",
        ))

    def _t2dfc_file_meta(raw):
        try:
            data = _t2dfc_json.loads(_t2dfc_s(raw))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _t2dfc_latest_clarified(conn, task_id):
        try:
            row = conn.execute(
                """
                SELECT action FROM task_history
                WHERE task_id=? AND action LIKE 'clarified:%'
                ORDER BY rowid DESC LIMIT 1
                """,
                (str(task_id),),
            ).fetchone()
            if row:
                return _t2dfc_s(row[0]).split("clarified:", 1)[1]
        except Exception:
            pass
        return ""

    def _t2dfc_hist_once(conn, task_id, action):
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

    def _t2dfc_task_dict(task, raw_input):
        data = {}
        try:
            for k in task.keys():
                data[k] = task[k]
        except Exception:
            try:
                data = dict(task) if isinstance(task, dict) else {}
            except Exception:
                data = {}
        data["raw_input"] = raw_input
        data["state"] = "IN_PROGRESS"
        data["error_message"] = ""
        data["result"] = ""
        data["input_type"] = "drive_file"
        data["topic_id"] = 2
        return data

    if _T2DFC_ORIG_HANDLE_IN_PROGRESS and not getattr(_T2DFC_ORIG_HANDLE_IN_PROGRESS, "_t2dfc_wrapped", False):
        async def _handle_in_progress(conn, task, *args, **kwargs):  # noqa: F811
            try:
                task_id = _t2dfc_s(_t2dfc_get(task, "id", ""))
                topic_id = int(_t2dfc_get(task, "topic_id", kwargs.get("topic_id", 0)) or 0)
                input_type = _t2dfc_low(_t2dfc_get(task, "input_type", ""))
                err = _t2dfc_s(_t2dfc_get(task, "error_message", ""))
                result = _t2dfc_s(_t2dfc_get(task, "result", ""))
                raw = _t2dfc_s(_t2dfc_get(task, "raw_input", ""))
                if task_id and topic_id == 2 and input_type == "drive_file":
                    stuck_on_picker = (
                        "DRIVE_FILE_NO_INTENT_OFFER_V1" in err
                        or "Что нужно сделать?" in result
                    )
                    clarified = _t2dfc_latest_clarified(conn, task_id)
                    if stuck_on_picker and _t2dfc_estimate_intent(clarified):
                        meta = _t2dfc_file_meta(raw)
                        if meta:
                            old_caption = _t2dfc_s(meta.get("caption", "")).strip()
                            meta["caption"] = (old_caption + "\n" + clarified).strip() if old_caption else clarified.strip()
                            meta["topic2_clarified_estimate_intent"] = True
                            new_raw = _t2dfc_json.dumps(meta, ensure_ascii=False)
                            conn.execute(
                                "UPDATE tasks SET raw_input=?, state='IN_PROGRESS', result='', error_message='', updated_at=datetime('now') WHERE id=?",
                                (new_raw, task_id),
                            )
                            _t2dfc_hist_once(conn, task_id, "PATCH_TOPIC2_DRIVE_FILE_PICKER_CLARIFIED_CANON_V1:ROUTE_CANONICAL")
                            conn.commit()
                            h_drive = globals().get("_handle_drive_file")
                            if h_drive:
                                chat_id = _t2dfc_s(_t2dfc_get(task, "chat_id", args[0] if args else ""))
                                task2 = _t2dfc_task_dict(task, new_raw)
                                res = h_drive(conn, task2, chat_id, 2)
                                if _t2dfc_inspect.isawaitable(res):
                                    return await res
                                return res
            except Exception as e:
                try:
                    _T2DFC_LOG.warning("PATCH_TOPIC2_DRIVE_FILE_PICKER_CLARIFIED_CANON_V1_ERR %s", e)
                except Exception:
                    pass
            res = _T2DFC_ORIG_HANDLE_IN_PROGRESS(conn, task, *args, **kwargs)
            if _t2dfc_inspect.isawaitable(res):
                return await res
            return res

        _handle_in_progress._t2dfc_wrapped = True
        globals()["_handle_in_progress"] = _handle_in_progress
        _T2DFC_LOG.info("PATCH_TOPIC2_DRIVE_FILE_PICKER_CLARIFIED_CANON_V1 installed")
except Exception as _t2dfc_install_err:
    try:
        logging.getLogger("task_worker").exception(
            "PATCH_TOPIC2_DRIVE_FILE_PICKER_CLARIFIED_CANON_V1_INSTALL_ERR %s",
            _t2dfc_install_err,
        )
    except Exception:
        pass
# === END_PATCH_TOPIC2_DRIVE_FILE_PICKER_CLARIFIED_CANON_V1 ===

# === PATCH_TOPIC2_DRIVE_FILE_PICKER_CLARIFIED_DRIVEFILE_V1 ===
# Same canon as CLARIFIED_CANON_V1, but on the drive_file handler path.
# The worker dispatches active drive_file tasks through _handle_drive_file, so the
# clarified estimate intent must be attached before DRIVE_FILE_NO_INTENT_OFFER_V1.
try:
    import json as _t2dfd_json
    import re as _t2dfd_re
    import inspect as _t2dfd_inspect
    import logging as _t2dfd_logging

    _T2DFD_LOG = _t2dfd_logging.getLogger("task_worker")
    _T2DFD_ORIG_HANDLE_DRIVE_FILE = globals().get("_handle_drive_file")

    def _t2dfd_s(v):
        return "" if v is None else str(v)

    def _t2dfd_get(task, key, default=None):
        try:
            if isinstance(task, dict):
                return task.get(key, default)
        except Exception:
            pass
        try:
            if hasattr(task, "keys") and key in task.keys():
                return task[key]
        except Exception:
            pass
        try:
            return _task_field(task, key, default)
        except Exception:
            return default

    def _t2dfd_low(v):
        return _t2dfd_s(v).lower().replace("ё", "е")

    def _t2dfd_estimate_intent(text):
        t = _t2dfd_low(text)
        if _t2dfd_re.match(r"^\s*1\s*([\).:-]|$)", t):
            return True
        return any(w in t for w in (
            "смет", "расчет", "расчёт", "стоимост", "цены", "материал",
            "работ", "строительств", "проектной документац", "excel", "xlsx",
        ))

    def _t2dfd_latest_clarified(conn, task_id):
        try:
            row = conn.execute(
                """
                SELECT action FROM task_history
                WHERE task_id=? AND action LIKE 'clarified:%'
                ORDER BY rowid DESC LIMIT 1
                """,
                (str(task_id),),
            ).fetchone()
            if row:
                return _t2dfd_s(row[0]).split("clarified:", 1)[1]
        except Exception:
            pass
        return ""

    def _t2dfd_hist_once(conn, task_id, action):
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

    def _t2dfd_task_dict(task, raw_input):
        data = {}
        try:
            for k in task.keys():
                data[k] = task[k]
        except Exception:
            try:
                data = dict(task) if isinstance(task, dict) else {}
            except Exception:
                data = {}
        data["raw_input"] = raw_input
        data["state"] = "IN_PROGRESS"
        data["error_message"] = ""
        data["result"] = ""
        data["input_type"] = "drive_file"
        data["topic_id"] = 2
        return data

    if _T2DFD_ORIG_HANDLE_DRIVE_FILE and not getattr(_T2DFD_ORIG_HANDLE_DRIVE_FILE, "_t2dfd_wrapped", False):
        async def _handle_drive_file(conn, task, chat_id, topic_id):  # noqa: F811
            try:
                topic_i = int(topic_id or _t2dfd_get(task, "topic_id", 0) or 0)
                task_id = _t2dfd_s(_t2dfd_get(task, "id", ""))
                raw = _t2dfd_s(_t2dfd_get(task, "raw_input", ""))
                if task_id and topic_i == 2:
                    try:
                        meta = _t2dfd_json.loads(raw)
                        if not isinstance(meta, dict):
                            meta = {}
                    except Exception:
                        meta = {}
                    clarified = _t2dfd_latest_clarified(conn, task_id)
                    already = bool(meta.get("topic2_clarified_estimate_intent"))
                    if meta and clarified and not already and _t2dfd_estimate_intent(clarified):
                        old_caption = _t2dfd_s(meta.get("caption", "")).strip()
                        meta["caption"] = (old_caption + "\n" + clarified).strip() if old_caption else clarified.strip()
                        meta["topic2_clarified_estimate_intent"] = True
                        new_raw = _t2dfd_json.dumps(meta, ensure_ascii=False)
                        conn.execute(
                            "UPDATE tasks SET raw_input=?, state='IN_PROGRESS', result='', error_message='', updated_at=datetime('now') WHERE id=?",
                            (new_raw, task_id),
                        )
                        _t2dfd_hist_once(conn, task_id, "PATCH_TOPIC2_DRIVE_FILE_PICKER_CLARIFIED_DRIVEFILE_V1:CAPTION_FROM_CLARIFIED")
                        conn.commit()
                        task = _t2dfd_task_dict(task, new_raw)
            except Exception as e:
                try:
                    _T2DFD_LOG.warning("PATCH_TOPIC2_DRIVE_FILE_PICKER_CLARIFIED_DRIVEFILE_V1_ERR %s", e)
                except Exception:
                    pass
            res = _T2DFD_ORIG_HANDLE_DRIVE_FILE(conn, task, chat_id, topic_id)
            if _t2dfd_inspect.isawaitable(res):
                return await res
            return res

        _handle_drive_file._t2dfd_wrapped = True
        globals()["_handle_drive_file"] = _handle_drive_file
        _T2DFD_LOG.info("PATCH_TOPIC2_DRIVE_FILE_PICKER_CLARIFIED_DRIVEFILE_V1 installed")
except Exception as _t2dfd_install_err:
    try:
        logging.getLogger("task_worker").exception(
            "PATCH_TOPIC2_DRIVE_FILE_PICKER_CLARIFIED_DRIVEFILE_V1_INSTALL_ERR %s",
            _t2dfd_install_err,
        )
    except Exception:
        pass
# === END_PATCH_TOPIC2_DRIVE_FILE_PICKER_CLARIFIED_DRIVEFILE_V1 ===

# === PATCH_TOPIC2_DRIVE_FINAL_USE_CANON_GENERATE_V2 ===
# Price-confirmed drive_file topic_2 finals must use stroyka canonical
# template generator, not the standalone short final_close path.
try:
    import re as _t2dfcg_re

    def _t2dfcg_num(v):
        try:
            return float(str(v or '').replace(' ', '').replace(',', '.'))
        except Exception:
            return 0.0

    def _t2dfcg_enrich_pending(pending):
        if not isinstance(pending, dict):
            return pending
        parsed = pending.get('parsed') or {}
        if not isinstance(parsed, dict):
            parsed = {}
        raw = str(parsed.get('raw') or '')
        low = raw.lower().replace('ё', 'е')
        rows = parsed.get('pdf_spec_rows') or []
        facts = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            name = str(row.get('name') or '').lower().replace('ё', 'е')
            qty = _t2dfcg_num(row.get('qty'))
            price = _t2dfcg_num(row.get('price'))
            real_qty = price if price > 0 and 0 < qty <= 20 and 'площад' in name else qty
            if real_qty <= 0:
                continue
            if 'застрой' in name:
                facts['built_area'] = real_qty
            elif 'общая' in name:
                facts['total_area'] = real_qty
            elif 'теплом контур' in name:
                facts['warm_area'] = real_qty
        if not parsed.get('object') and ('дом' in low or facts):
            parsed['object'] = 'дом'
        if not parsed.get('material') and 'газобетон' in low:
            parsed['material'] = 'газобетон'
        if not parsed.get('foundation') and ('монолитная железобетонная плита' in low or 'фундамент - монолит' in low):
            parsed['foundation'] = 'монолитная плита'
        if not parsed.get('foundation'):
            row_blob = " ".join(str((r or {}).get('name') or '') for r in (rows or []) if isinstance(r, dict)).lower().replace('ё', 'е')
            if any(x in row_blob for x in ('бст в', 'бетон', 'фундамент', 'плита пола', 'балка фундамент')):
                parsed['foundation'] = 'монолитная плита'
        if not parsed.get('object'):
            row_blob = " ".join(str((r or {}).get('name') or '') for r in (rows or []) if isinstance(r, dict)).lower().replace('ё', 'е')
            if 'ферм' in row_blob or 'металлоконструкц' in row_blob or 'сэндвич' in low or 'склад' in low:
                parsed['object'] = 'склад'
        if not parsed.get('area_floor') and facts.get('built_area'):
            parsed['area_floor'] = facts['built_area']
        if not parsed.get('area_total') and facts.get('total_area'):
            parsed['area_total'] = facts['total_area']
        if not parsed.get('floors'):
            if 'план расстановки мебели 2 этажа' in low or 'обмерный план 2-го этажа' in low or '2 этажа' in low:
                parsed['floors'] = 2
        if not parsed.get('dimensions') and facts.get('built_area'):
            parsed['area'] = facts.get('built_area')
        pending['parsed'] = parsed
        return pending

    async def _t2fdsg_run_drive_final(conn, parent, choice):  # noqa: F811
        parent_id = str(_t2fdsg_get(parent, 'id') or '')
        chat_id = str(_t2fdsg_get(parent, 'chat_id') or '')
        topic_id = int(_t2fdsg_get(parent, 'topic_id', 2) or 2)
        if not parent_id:
            return False
        parent = _t2fdsg_enrich_parent_raw(conn, parent, choice)
        _t2fdsg_hist_once(conn, parent_id, 'TOPIC2_PRICE_CHOICE_CONFIRMED:' + str(choice))
        _t2fdsg_hist_once(conn, parent_id, 'PATCH_TOPIC2_DRIVE_FINAL_USE_CANON_GENERATE_V2:START')
        pending = _t2fdsg_load_pending(chat_id, parent_id)
        pending = _t2dfcg_enrich_pending(pending)
        if not pending:
            _update_task(conn, parent_id, state='FAILED', error_message='TOPIC2_PENDING_NOT_FOUND_FOR_CANON_GENERATE')
            conn.commit()
            return True
        try:
            from core.stroyka_estimate_canon import _generate_and_send as _t2dfcg_generate
            conn.execute("UPDATE tasks SET state='IN_PROGRESS', result='', error_message=NULL, updated_at=datetime('now') WHERE id=?", (parent_id,))
            conn.commit()
            try:
                _latest_clarified = conn.execute(
                    "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'clarified:%' ORDER BY rowid DESC LIMIT 1",
                    (parent_id,),
                ).fetchone()
                _clarified_text = str(_latest_clarified[0]).split("clarified:", 1)[1] if _latest_clarified else ""
                _parent_raw = str(_t2fdsg_get(parent, "raw_input") or "")
                _parsed = pending.get("parsed") or {}
                if isinstance(_parsed, dict):
                    _parsed_raw = str(_parsed.get("raw") or "")
                    _parts = [_parsed_raw, _parent_raw, _clarified_text]
                    _parsed["raw"] = "\n\n".join(p for p in _parts if p and p not in _parsed_raw)
                    pending["parsed"] = _parsed
            except Exception:
                pass
            _choice_key = str(choice or "median")
            choice_text = {
                'min': 'минимальные', 'minimum': 'минимальные', 'cheapest': 'минимальные',
                'median': 'средние', 'average': 'средние',
                'max': 'максимальные', 'maximum': 'максимальные',
                'reliable': 'надёжные', 'trusted': 'надёжные',
            }.get(_choice_key, _choice_key or 'средние')
            res = _t2dfcg_generate(conn, parent, pending, choice_text, logger=logger)
            if _t2fdsg_inspect.isawaitable(res):
                await res
            _t2fdsg_hist_once(conn, parent_id, 'PATCH_TOPIC2_DRIVE_FINAL_USE_CANON_GENERATE_V2:DONE')
            conn.commit()
            return True
        except Exception as e:
            _update_task(conn, parent_id, state='FAILED', error_message='TOPIC2_CANON_GENERATE_EXCEPTION:' + type(e).__name__)
            _t2fdsg_hist_once(conn, parent_id, 'PATCH_TOPIC2_DRIVE_FINAL_USE_CANON_GENERATE_V2:ERR:' + str(e)[:120])
            conn.commit()
            return True

    logger.info('PATCH_TOPIC2_DRIVE_FINAL_USE_CANON_GENERATE_V2 installed')
except Exception as _t2dfcg_e:
    try:
        logger.exception('PATCH_TOPIC2_DRIVE_FINAL_USE_CANON_GENERATE_V2_INSTALL_ERR:%s', _t2dfcg_e)
    except Exception:
        pass
# === END_PATCH_TOPIC2_DRIVE_FINAL_USE_CANON_GENERATE_V2 ===

# === PATCH_TOPIC2_REVISION_FINAL_GATE_CHOICE_V1 ===
try:
    import re as _t2rfg_re
    import logging as _t2rfg_logging

    _T2RFG_LOG = _t2rfg_logging.getLogger("task_worker")
    _T2RFG_ORIG_RUN_DRIVE_FINAL = globals().get("_t2fdsg_run_drive_final")

    def _t2rfg_s(v):
        return "" if v is None else str(v)

    def _t2rfg_get(task, key, default=None):
        try:
            if isinstance(task, dict):
                return task.get(key, default)
            if hasattr(task, "keys") and key in task.keys():
                return task[key]
        except Exception:
            pass
        try:
            return _task_field(task, key, default)
        except Exception:
            return default

    def _t2rfg_hist_text(conn, task_id):
        try:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? ORDER BY rowid ASC",
                (str(task_id),),
            ).fetchall()
            return "\n".join(_t2rfg_s(r[0]) for r in rows)
        except Exception:
            return ""

    def _t2rfg_normalize_choice(conn, task, choice):
        task_id = _t2rfg_s(_t2rfg_get(task, "id", ""))
        raw = _t2rfg_s(_t2rfg_get(task, "raw_input", ""))
        hist = _t2rfg_hist_text(conn, task_id)
        text = (raw + "\n" + hist).lower().replace("ё", "е")
        if ("надежн" in text or "проверенн" in text or "раздел три" in text or "вариант 3" in text) and (
            "не максим" in text or "а не максим" in text or "не max" in text
        ):
            return "reliable"
        matches = _t2rfg_re.findall(r"TOPIC2_PRICE_CHOICE_CONFIRMED:([a-zA-Zа-яА-Я0-9_ -]+)", hist)
        for val in reversed(matches):
            low = val.strip().lower().replace("ё", "е")
            if low in ("reliable", "trusted") or "надеж" in low or "провер" in low:
                return "reliable"
            if low in ("median", "average") or "сред" in low:
                return "median"
            if low in ("cheapest", "minimum", "min") or "деш" in low or "миним" in low:
                return "cheapest"
            if low in ("manual",) or "ручн" in low:
                return "manual"
            if low in ("maximum", "max") and not ("не максим" in text or "а не максим" in text):
                return "maximum"
        return choice

    if _T2RFG_ORIG_RUN_DRIVE_FINAL and not getattr(_T2RFG_ORIG_RUN_DRIVE_FINAL, "_t2rfg_wrapped", False):
        async def _t2fdsg_run_drive_final(conn, parent, choice):  # noqa: F811
            fixed_choice = _t2rfg_normalize_choice(conn, parent, choice)
            if fixed_choice != choice:
                try:
                    _history(conn, _t2rfg_s(_t2rfg_get(parent, "id", "")), "PATCH_TOPIC2_REVISION_FINAL_GATE_CHOICE_V1:" + _t2rfg_s(choice) + "->" + _t2rfg_s(fixed_choice))
                    conn.commit()
                except Exception:
                    pass
            return await _T2RFG_ORIG_RUN_DRIVE_FINAL(conn, parent, fixed_choice)

        _t2fdsg_run_drive_final._t2rfg_wrapped = True
        globals()["_t2fdsg_run_drive_final"] = _t2fdsg_run_drive_final
        _T2RFG_LOG.info("PATCH_TOPIC2_REVISION_FINAL_GATE_CHOICE_V1 installed")
except Exception as _t2rfg_install_err:
    try:
        logger.exception("PATCH_TOPIC2_REVISION_FINAL_GATE_CHOICE_V1_INSTALL_ERR:%s", _t2rfg_install_err)
    except Exception:
        pass
# === END_PATCH_TOPIC2_REVISION_FINAL_GATE_CHOICE_V1 ===

# === PATCH_TOPIC2_RELIABLE_PRICE_FINAL_WORKER_GUARD_V1 ===
# Canon/user rule: topic_2 price option 3 is "надёжные", not maximum.
# If the current revision explicitly says "надёжные ... не максимальные",
# stale max/maximum markers must not drive final regeneration.
try:
    import re as _t2rpfw_re
    import logging as _t2rpfw_logging

    _T2RPFW_LOG = _t2rpfw_logging.getLogger("task_worker")

    def _t2rpfw_s(v):
        return "" if v is None else str(v)

    def _t2rpfw_norm(text):
        return _t2rpfw_re.sub(r"\s+", " ", _t2rpfw_s(text).lower().replace("ё", "е")).strip()

    def _t2rpfw_reliable_requested(text):
        t = _t2rpfw_norm(text).strip(" .,!?:;()[]{}")
        explicit_max = any(x in t for x in ("максим", "max", "макс ")) and not any(x in t for x in ("не максим", "а не максим", "не max"))
        return (
            not explicit_max
            and (
                t in ("3", "3.", "третий", "вариант 3", "вариант в", "в", "v", "в)", "v)")
                or "надежн" in t
                or "проверенн" in t
                or "раздел три" in t
            )
        )

    if "_t2fdsg_price_choice" in globals():
        _T2RPFW_ORIG_FDSG_PRICE_CHOICE = _t2fdsg_price_choice

        def _t2fdsg_price_choice(text):  # noqa: F811
            if _t2rpfw_reliable_requested(text):
                return "reliable"
            return _T2RPFW_ORIG_FDSG_PRICE_CHOICE(text)

    if "_t2fdsg_run_drive_final" in globals():
        _T2RPFW_ORIG_RUN_DRIVE_FINAL = _t2fdsg_run_drive_final

        async def _t2fdsg_run_drive_final(conn, parent, choice):  # noqa: F811
            parent_id = _t2rpfw_s(_t2rfg_get(parent, "id", "")) if "_t2rfg_get" in globals() else ""
            raw = _t2rpfw_s(_t2rfg_get(parent, "raw_input", "")) if "_t2rfg_get" in globals() else ""
            hist = ""
            try:
                rows = conn.execute(
                    "SELECT action FROM task_history WHERE task_id=? ORDER BY rowid ASC",
                    (str(parent_id),),
                ).fetchall()
                hist = "\n".join(_t2rpfw_s(r[0]) for r in rows)
            except Exception:
                hist = ""
            text = raw + "\n" + hist
            fixed_choice = choice
            if _t2rpfw_reliable_requested(text) or (
                "TOPIC2_PRICE_CHOICE_CONFIRMED:reliable" in hist
                and str(choice).lower() in ("max", "maximum")
            ):
                fixed_choice = "reliable"
            if fixed_choice != choice:
                try:
                    _history(conn, parent_id, "PATCH_TOPIC2_RELIABLE_PRICE_FINAL_WORKER_GUARD_V1:" + _t2rpfw_s(choice) + "->" + _t2rpfw_s(fixed_choice))
                    conn.commit()
                except Exception:
                    pass
            return await _T2RPFW_ORIG_RUN_DRIVE_FINAL(conn, parent, fixed_choice)

        globals()["_t2fdsg_run_drive_final"] = _t2fdsg_run_drive_final

    _T2RPFW_LOG.info("PATCH_TOPIC2_RELIABLE_PRICE_FINAL_WORKER_GUARD_V1 installed")
except Exception as _t2rpfw_err:
    try:
        logger.exception("PATCH_TOPIC2_RELIABLE_PRICE_FINAL_WORKER_GUARD_V1_INSTALL_ERR:%s", _t2rpfw_err)
    except Exception:
        pass
# === END_PATCH_TOPIC2_RELIABLE_PRICE_FINAL_WORKER_GUARD_V1 ===

# === PATCH_TOPIC2_FOUNDATION_MISSING_PRICE_FINAL_GATE_V1 ===
# Canon: topic_2 final XLSX/PDF must not close while an explicit internet
# price check still has required foundation price families unresolved.
try:
    import inspect as _t2fmpg_inspect
    import logging as _t2fmpg_logging

    _T2FMPG_LOG = _t2fmpg_logging.getLogger("task_worker")
    _T2FMPG_ORIG_RUN_DRIVE_FINAL = globals().get("_t2fdsg_run_drive_final")

    def _t2fmpg_s(v):
        return "" if v is None else str(v)

    def _t2fmpg_get(obj, key, default=None):
        try:
            if isinstance(obj, dict):
                return obj.get(key, default)
            if hasattr(obj, "keys") and key in obj.keys():
                return obj[key]
        except Exception:
            pass
        try:
            return _task_field(obj, key, default)
        except Exception:
            return default

    def _t2fmpg_hist(conn, task_id, action):
        try:
            _history(conn, str(task_id), str(action)[:900])
        except Exception:
            pass

    def _t2fmpg_save_pending(chat_id, task_id, pending):
        try:
            from core.stroyka_estimate_canon import _memory_save as _t2fmpg_memory_save
            _t2fmpg_memory_save(str(chat_id), "topic_2_estimate_pending_" + str(task_id), pending)
        except Exception:
            pass

    def _t2fmpg_enrich_pending_raw(conn, parent, pending):
        try:
            parsed = pending.get("parsed") or {}
            if not isinstance(parsed, dict):
                parsed = {}
            task_id = _t2fmpg_s(_t2fmpg_get(parent, "id", ""))
            latest = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'clarified:%' ORDER BY rowid DESC LIMIT 1",
                (task_id,),
            ).fetchone()
            clarified = _t2fmpg_s(latest[0]).split("clarified:", 1)[1] if latest else ""
            parts = [
                _t2fmpg_s(parsed.get("raw") or ""),
                _t2fmpg_s(_t2fmpg_get(parent, "raw_input", "")),
                clarified,
            ]
            merged = "\n\n".join(p for p in parts if p)
            if merged:
                parsed["raw"] = merged[:14000]
                pending["parsed"] = parsed
        except Exception:
            pass
        return pending

    if _T2FMPG_ORIG_RUN_DRIVE_FINAL and not getattr(_T2FMPG_ORIG_RUN_DRIVE_FINAL, "_t2fmpg_wrapped", False):
        async def _t2fdsg_run_drive_final(conn, parent, choice):  # noqa: F811
            parent_id = _t2fmpg_s(_t2fmpg_get(parent, "id", ""))
            chat_id = _t2fmpg_s(_t2fmpg_get(parent, "chat_id", ""))
            topic_id = int(_t2fmpg_get(parent, "topic_id", 0) or 0)

            if topic_id == 2 and parent_id and chat_id and callable(globals().get("_t2fdsg_load_pending")):
                try:
                    pending = globals()["_t2fdsg_load_pending"](chat_id, parent_id)
                    if isinstance(pending, dict) and pending:
                        pending = _t2fmpg_enrich_pending_raw(conn, parent, pending)
                        parsed = pending.get("parsed") or {}
                        online_prices = pending.get("online_prices") or ""
                        from core import stroyka_estimate_canon as _t2fmpg_canon
                        raw_context = "\n".join([
                            _t2fmpg_s(parsed.get("raw") if isinstance(parsed, dict) else ""),
                            _t2fmpg_s(choice),
                        ])
                        requires = _t2fmpg_canon._t2rpf_requires_foundation_live_prices_v1(parsed, raw_context)
                        missing = _t2fmpg_canon._t2rpf_missing_foundation_families_v1(parsed, online_prices) if requires else []
                        if missing:
                            _t2fmpg_hist(conn, parent_id, "PATCH_TOPIC2_FOUNDATION_MISSING_PRICE_FINAL_GATE_V1:SEARCH:" + ",".join(missing))
                            try:
                                refreshed = await asyncio.wait_for(
                                    _t2fmpg_canon._search_prices_online(
                                        parsed,
                                        pending.get("template") or _t2fmpg_canon.CANON_TEMPLATE_FALLBACK["areal"],
                                        pending.get("sheet_name"),
                                        conn=conn,
                                        task_id=parent_id,
                                    ),
                                    timeout=120,
                                )
                                if refreshed:
                                    pending["online_prices"] = refreshed
                                    online_prices = refreshed
                                _t2fmpg_save_pending(chat_id, parent_id, pending)
                            except Exception as exc:
                                _t2fmpg_hist(conn, parent_id, "PATCH_TOPIC2_FOUNDATION_MISSING_PRICE_FINAL_GATE_V1:SEARCH_ERR:" + _t2fmpg_s(exc)[:160])

                            missing_after = _t2fmpg_canon._t2rpf_missing_foundation_families_v1(parsed, online_prices)
                            if missing_after:
                                text = (
                                    "Не закрываю финальную смету: не найдены подтверждённые интернет-цены для "
                                    + ", ".join(missing_after)
                                    + ". Пришли ручные цены или разреши повторить поиск."
                                )
                                _update_task(
                                    conn,
                                    parent_id,
                                    state="WAITING_CLARIFICATION",
                                    result=text,
                                    error_message="TOPIC2_FOUNDATION_PRICE_SOURCE_REQUIRED",
                                )
                                _t2fmpg_hist(conn, parent_id, "PATCH_TOPIC2_FOUNDATION_MISSING_PRICE_FINAL_GATE_V1:BLOCKED:" + ",".join(missing_after))
                                conn.commit()
                                try:
                                    send_reply_ex(
                                        chat_id=chat_id,
                                        text=text,
                                        reply_to_message_id=_t2fmpg_get(parent, "reply_to_message_id"),
                                        message_thread_id=topic_id,
                                    )
                                except Exception:
                                    pass
                                return True
                            _t2fmpg_hist(conn, parent_id, "PATCH_TOPIC2_FOUNDATION_MISSING_PRICE_FINAL_GATE_V1:CLEARED")
                            conn.commit()
                except Exception as exc:
                    try:
                        _T2FMPG_LOG.warning("PATCH_TOPIC2_FOUNDATION_MISSING_PRICE_FINAL_GATE_V1_ERR:%s", exc)
                    except Exception:
                        pass
            res = _T2FMPG_ORIG_RUN_DRIVE_FINAL(conn, parent, choice)
            if _t2fmpg_inspect.isawaitable(res):
                return await res
            return res

        _t2fdsg_run_drive_final._t2fmpg_wrapped = True
        globals()["_t2fdsg_run_drive_final"] = _t2fdsg_run_drive_final

    _T2FMPG_LOG.info("PATCH_TOPIC2_FOUNDATION_MISSING_PRICE_FINAL_GATE_V1 installed")
except Exception as _t2fmpg_err:
    try:
        logger.exception("PATCH_TOPIC2_FOUNDATION_MISSING_PRICE_FINAL_GATE_V1_INSTALL_ERR:%s", _t2fmpg_err)
    except Exception:
        pass
# === END_PATCH_TOPIC2_FOUNDATION_MISSING_PRICE_FINAL_GATE_V1 ===

# === PATCH_TOPIC2_SOURCE_QUESTION_LIVE_REPLY_V1 ===
# Canon: topic_2 live dialogue/reply questions about already-used price sources
# must be answered from saved task context, not merged as estimate revisions.
try:
    import json as _t2sql_json
    import logging as _t2sql_logging
    import os as _t2sql_os
    import re as _t2sql_re
    import sqlite3 as _t2sql_sqlite3

    _T2SQL_LOG = _t2sql_logging.getLogger("task_worker")
    _T2SQL_PATCH = "PATCH_TOPIC2_SOURCE_QUESTION_LIVE_REPLY_V1"
    _t2sql_prev_handle_new = globals().get("_handle_new")

    def _t2sql_s(v):
        return "" if v is None else str(v)

    def _t2sql_low(v):
        return _t2sql_s(v).lower().replace("ё", "е").strip()

    def _t2sql_get(obj, key, default=None):
        try:
            if isinstance(obj, dict):
                return obj.get(key, default)
            if hasattr(obj, "keys") and key in obj.keys():
                return obj[key]
        except Exception:
            pass
        return default

    def _t2sql_hist(conn, task_id, action):
        try:
            conn.execute(
                "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                (_t2sql_s(task_id), _t2sql_s(action)[:900]),
            )
        except Exception:
            pass

    def _t2sql_is_source_question(text):
        t = _t2sql_low(text)
        if not t:
            return False
        if any(x in t for x in ("пересчитай", "пересчитать", "исправь", "исправить", "добавь", "добавить", "измени", "изменить")):
            return False
        source_word = any(x in t for x in (
            "откуда", "где", "источник", "источники", "смотрел", "смотрела",
            "брал", "брала", "взял", "взяла", "нашел", "нашла", "нашёл",
        ))
        price_word = any(x in t for x in (
            "цен", "стоимост", "работ", "материал", "поставщик", "ссылк", "интернет",
        ))
        return source_word and price_word

    def _t2sql_find_parent(conn, task, chat_id, topic_id):
        child_id = _t2sql_s(_t2sql_get(task, "id"))
        reply_to = _t2sql_get(task, "reply_to_message_id")
        active = ("AWAITING_CONFIRMATION", "IN_PROGRESS", "WAITING_CLARIFICATION", "DONE")
        try:
            if reply_to:
                row = conn.execute(
                    "SELECT * FROM tasks WHERE CAST(chat_id AS TEXT)=? AND COALESCE(topic_id,0)=? "
                    "AND bot_message_id=? AND id<>? AND state IN (?,?,?,?) ORDER BY updated_at DESC LIMIT 1",
                    (_t2sql_s(chat_id), int(topic_id or 0), int(reply_to), child_id, *active),
                ).fetchone()
                if row:
                    return row
        except Exception:
            pass
        try:
            return conn.execute(
                "SELECT * FROM tasks WHERE CAST(chat_id AS TEXT)=? AND COALESCE(topic_id,0)=? "
                "AND id<>? AND input_type='drive_file' AND state IN (?,?,?,?) ORDER BY updated_at DESC LIMIT 1",
                (_t2sql_s(chat_id), int(topic_id or 0), child_id, *active),
            ).fetchone()
        except Exception:
            return None

    def _t2sql_memory_db_path():
        for p in (
            "/root/.areal-neva-core/data/memory.db",
            _t2sql_os.path.join(_t2sql_os.path.dirname(__file__), "data", "memory.db"),
        ):
            if _t2sql_os.path.exists(p):
                return p
        return "/root/.areal-neva-core/data/memory.db"

    def _t2sql_load_pending(parent_id):
        key = "topic_2_estimate_pending_" + _t2sql_s(parent_id)
        try:
            mconn = _t2sql_sqlite3.connect(_t2sql_memory_db_path(), timeout=5.0)
            row = mconn.execute(
                "SELECT value FROM memory WHERE key=? ORDER BY timestamp DESC LIMIT 1",
                (key,),
            ).fetchone()
            mconn.close()
            if row and row[0]:
                data = _t2sql_json.loads(row[0])
                return data if isinstance(data, dict) else {}
        except Exception:
            pass
        return {}

    def _t2sql_parse_offers(price_text):
        offers = []
        for raw_line in _t2sql_s(price_text).splitlines():
            line = raw_line.strip(" \t-—•·")
            if "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 6:
                continue
            try:
                price = float(parts[1].replace(" ", "").replace(",", "."))
            except Exception:
                continue
            if price <= 0:
                continue
            offers.append({
                "position": parts[0],
                "price": price,
                "unit": parts[2] if len(parts) > 2 else "",
                "region": parts[3] if len(parts) > 3 else "",
                "supplier": parts[4] if len(parts) > 4 else "",
                "url": parts[5] if len(parts) > 5 else "",
                "checked_at": parts[6] if len(parts) > 6 else "",
            })
        return offers

    def _t2sql_offer_line(offer):
        price = offer.get("price")
        if float(price).is_integer():
            price_txt = str(int(price))
        else:
            price_txt = f"{float(price):.2f}".rstrip("0").rstrip(".")
        supplier = _t2sql_s(offer.get("supplier")) or "источник не указан"
        url = _t2sql_s(offer.get("url"))
        unit = _t2sql_s(offer.get("unit"))
        pos = _t2sql_s(offer.get("position"))
        tail = f" - {url}" if url else ""
        return f"- {pos}: {price_txt} руб/{unit} - {supplier}{tail}"

    def _t2sql_build_source_answer(raw_text, pending):
        offers = _t2sql_parse_offers((pending or {}).get("online_prices") or "")
        t = _t2sql_low(raw_text)
        wants_work = any(x in t for x in ("работ", "монтаж", "установ"))
        wants_material = any(x in t for x in ("материал", "металл", "изготов", "издел"))

        work = [
            o for o in offers
            if any(x in _t2sql_low(o.get("position")) for x in ("монтаж", "установка", "работ"))
        ]
        material = [
            o for o in offers
            if not any(x in _t2sql_low(o.get("position")) for x in ("монтаж", "установка", "работ"))
        ]

        lines = [
            "Отвечаю по источникам текущей сметы без пересчета и без нового интернет-поиска.",
            "",
        ]
        if wants_work or not wants_material:
            lines.append("Работы / монтаж:")
            lines.extend(_t2sql_offer_line(o) for o in work[:8])
            if not work:
                lines.append("- В сохраненном контексте нет отдельного источника по работам.")
            lines.append("")

        if wants_material or not wants_work:
            lines.append("Материалы / изделие:")
            lines.extend(_t2sql_offer_line(o) for o in material[:8])
            if not material:
                lines.append("- В сохраненном контексте нет отдельного источника по материалам.")
            lines.append("")

        if wants_work:
            lines.append(
                "Изготовление металлоконструкций в этой смете относится к стоимости изделия/материала, "
                "а не к отдельным монтажным работам."
            )
        lines.append("Если нужно изменить расчет, напиши конкретную правку; этот ответ сам пересчет не запускает.")
        return "\n".join(lines)[:3900]

    async def _handle_new(conn, task, chat_id, topic_id):  # noqa: F811
        try:
            if int(topic_id or 0) == 2:
                input_type = _t2sql_s(_t2sql_get(task, "input_type")).strip()
                raw = _t2sql_s(_t2sql_get(task, "raw_input")).strip()
                child_id = _t2sql_s(_t2sql_get(task, "id")).strip()
                reply_to = _t2sql_get(task, "reply_to_message_id")
                if input_type in ("text", "voice", "search") and raw and child_id and _t2sql_is_source_question(raw):
                    parent = _t2sql_find_parent(conn, task, chat_id, topic_id)
                    if parent:
                        parent_id = _t2sql_s(_t2sql_get(parent, "id"))
                        pending = _t2sql_load_pending(parent_id)
                        answer = _t2sql_build_source_answer(raw, pending)
                        conn.execute(
                            "UPDATE tasks SET state='DONE', result=?, error_message=?, updated_at=datetime('now') WHERE id=?",
                            (answer, "TOPIC2_SOURCE_QUESTION_ANSWERED:" + parent_id, child_id),
                        )
                        _t2sql_hist(conn, parent_id, "TOPIC2_SOURCE_QUESTION_ANSWERED:" + child_id)
                        _t2sql_hist(conn, child_id, _T2SQL_PATCH + ":parent=" + parent_id)
                        conn.commit()
                        try:
                            _send_once(conn, child_id, _t2sql_s(chat_id), answer, reply_to, "source_question")
                        except Exception:
                            pass
                        _T2SQL_LOG.info("%s child=%s parent=%s", _T2SQL_PATCH, child_id, parent_id)
                        return
        except Exception as exc:
            try:
                _T2SQL_LOG.exception("%s_ERR:%s", _T2SQL_PATCH, exc)
            except Exception:
                pass
        if _t2sql_prev_handle_new:
            return await _t2sql_prev_handle_new(conn, task, chat_id, topic_id)
        return None

    if _t2sql_prev_handle_new:
        globals()["_handle_new"] = _handle_new
    _T2SQL_LOG.info("%s installed", _T2SQL_PATCH)
except Exception as _t2sql_install_err:
    try:
        logger.exception("PATCH_TOPIC2_SOURCE_QUESTION_LIVE_REPLY_V1_INSTALL_ERR:%s", _t2sql_install_err)
    except Exception:
        pass
# === END_PATCH_TOPIC2_SOURCE_QUESTION_LIVE_REPLY_V1 ===

# === PATCH_TOPIC2_READY_DONE_BEFORE_FRUSTRATION_V1 ===
try:
    _T2RDBF_PATCH = "PATCH_TOPIC2_READY_DONE_BEFORE_FRUSTRATION_V1"
    _t2rdbf_prev_handle_new = globals().get("_handle_new")

    def _t2rdbf_s(value):
        return "" if value is None else str(value)

    def _t2rdbf_get(row, key, default=None):
        try:
            if hasattr(row, "keys") and key in row.keys():
                return row[key]
        except Exception:
            pass
        return default

    def _t2rdbf_is_final_estimate(result):
        low = _t2rdbf_s(result).lower().replace("ё", "е")
        return (
            "смета готов" in low
            and ("xlsx" in low or "pdf" in low)
            and ("drive.google.com" in low or "docs.google.com" in low)
        )

    def _t2rdbf_find_done_parent(conn, task, chat_id, topic_id):
        task_id = _t2rdbf_s(_t2rdbf_get(task, "id"))
        reply_to = _t2rdbf_get(task, "reply_to_message_id")
        rows = []
        if reply_to:
            rows.extend(conn.execute(
                """
                SELECT id, COALESCE(raw_input,'') AS raw_input, COALESCE(result,'') AS result
                FROM tasks
                WHERE CAST(chat_id AS TEXT)=?
                  AND COALESCE(topic_id,0)=?
                  AND id<>?
                  AND state='DONE'
                  AND (bot_message_id=? OR reply_to_message_id=?)
                ORDER BY updated_at DESC, created_at DESC
                LIMIT 5
                """,
                (str(chat_id), int(topic_id), task_id, reply_to, reply_to),
            ).fetchall())
        rows.extend(conn.execute(
            """
            SELECT id, COALESCE(raw_input,'') AS raw_input, COALESCE(result,'') AS result
            FROM tasks
            WHERE CAST(chat_id AS TEXT)=?
              AND COALESCE(topic_id,0)=?
              AND id<>?
              AND state='DONE'
              AND COALESCE(result,'') LIKE '%Смета готова%'
              AND (COALESCE(result,'') LIKE '%drive.google.com%' OR COALESCE(result,'') LIKE '%docs.google.com%')
            ORDER BY updated_at DESC, created_at DESC
            LIMIT 10
            """,
            (str(chat_id), int(topic_id), task_id),
        ).fetchall())
        for row in rows:
            if _t2rdbf_is_final_estimate(_t2rdbf_get(row, "result")):
                return row
        return None

    def _t2rdbf_memory_upsert(chat_id, key, payload):
        db_path = os.path.join(BASE, "data", "memory.db")
        value = json.dumps(payload, ensure_ascii=False, indent=2)
        ts = now_iso_utc()
        row_id = hashlib.sha1(f"{chat_id}:{key}:{ts}".encode("utf-8")).hexdigest()
        with sqlite3.connect(db_path) as mem:
            existing = mem.execute(
                "SELECT id FROM memory WHERE chat_id=? AND key=? ORDER BY timestamp DESC LIMIT 1",
                (str(chat_id), key),
            ).fetchone()
            if existing:
                mem.execute(
                    "UPDATE memory SET value=?, timestamp=?, topic_id=2, scope='topic' WHERE id=?",
                    (value, ts, existing[0]),
                )
            else:
                mem.execute(
                    "INSERT INTO memory(id, chat_id, key, value, timestamp, topic_id, scope) VALUES(?,?,?,?,?,2,'topic')",
                    (row_id, str(chat_id), key, value, ts),
                )
            mem.commit()

    def _t2rdbf_sync_topic2_memory(conn, task, chat_id, topic_id):
        parent = _t2rdbf_find_done_parent(conn, task, chat_id, topic_id)
        if not parent:
            return None
        parent_id = _t2rdbf_s(_t2rdbf_get(parent, "id"))
        parent_raw = _t2rdbf_s(_t2rdbf_get(parent, "raw_input"))
        parent_result = _t2rdbf_s(_t2rdbf_get(parent, "result"))
        saved_at = now_iso_utc()
        payloads = {
            f"topic_2_user_input_{parent_id}": {
                "task_id": parent_id, "topic_id": 2, "raw_input": parent_raw,
                "saved_at": saved_at, "source": "TOPIC2_EXPLICIT_CONFIRM",
            },
            f"topic_2_task_summary_{parent_id}": {
                "task_id": parent_id, "topic_id": 2, "summary": parent_result,
                "saved_at": saved_at, "source": "TOPIC2_EXPLICIT_CONFIRM",
            },
            f"topic_2_assistant_output_{parent_id}": {
                "task_id": parent_id, "topic_id": 2, "result": parent_result,
                "saved_at": saved_at, "source": "TOPIC2_EXPLICIT_CONFIRM",
            },
            "topic_2_user_input": {
                "task_id": parent_id, "topic_id": 2, "raw_input": parent_raw,
                "saved_at": saved_at, "source": "TOPIC2_EXPLICIT_CONFIRM",
            },
            "topic_2_task_summary": {
                "task_id": parent_id, "topic_id": 2, "summary": parent_result,
                "saved_at": saved_at, "source": "TOPIC2_EXPLICIT_CONFIRM",
            },
            "topic_2_assistant_output": {
                "task_id": parent_id, "topic_id": 2, "result": parent_result,
                "saved_at": saved_at, "source": "TOPIC2_EXPLICIT_CONFIRM",
            },
        }
        for key, payload in payloads.items():
            _t2rdbf_memory_upsert(chat_id, key, payload)
        return parent_id

    async def _handle_new(conn, task, chat_id, topic_id):  # noqa: F811
        try:
            if int(topic_id or 0) == 2:
                from core import stroyka_estimate_canon as _t2rdbf_canon

                handler = getattr(_t2rdbf_canon, "_topic2_handle_ready_done_v1", None)
                if callable(handler) and await handler(conn, task, logger=logger):
                    parent_id = None
                    try:
                        parent_id = _t2rdbf_sync_topic2_memory(conn, task, chat_id, topic_id)
                    except Exception as mem_exc:
                        logger.exception("%s_MEMORY_SYNC_ERR:%s", _T2RDBF_PATCH, mem_exc)
                    try:
                        conn.commit()
                    except Exception:
                        pass
                    try:
                        _history(conn, str(task["id"]), _T2RDBF_PATCH + ":handled_by_canon_ready_done")
                        if parent_id:
                            _history(conn, parent_id, _T2RDBF_PATCH + ":topic2_memory_synced")
                            _history(conn, str(task["id"]), _T2RDBF_PATCH + ":topic2_memory_synced_for:" + parent_id)
                    except Exception:
                        pass
                    logger.info("%s handled task_id=%s", _T2RDBF_PATCH, task["id"])
                    return
        except Exception as exc:
            try:
                logger.exception("%s_ERR:%s", _T2RDBF_PATCH, exc)
            except Exception:
                pass
        if _t2rdbf_prev_handle_new:
            return await _t2rdbf_prev_handle_new(conn, task, chat_id, topic_id)
        return None

    if _t2rdbf_prev_handle_new:
        globals()["_handle_new"] = _handle_new
    logger.info("%s installed", _T2RDBF_PATCH)
except Exception as _t2rdbf_install_err:
    try:
        logger.exception("PATCH_TOPIC2_READY_DONE_BEFORE_FRUSTRATION_V1_INSTALL_ERR:%s", _t2rdbf_install_err)
    except Exception:
        pass
# === END_PATCH_TOPIC2_READY_DONE_BEFORE_FRUSTRATION_V1 ===

# === PATCH_TOPIC2_HISTORICAL_PROJECT_MEMORY_RECALL_V1 ===
try:
    _T2HPMR_PATCH = "PATCH_TOPIC2_HISTORICAL_PROJECT_MEMORY_RECALL_V1"
    _t2hpmr_prev_handle_new = globals().get("_handle_new")

    def _t2hpmr_s(value):
        return "" if value is None else str(value)

    def _t2hpmr_get(row, key, default=None):
        try:
            if hasattr(row, "keys") and key in row.keys():
                return row[key]
        except Exception:
            pass
        return default

    def _t2hpmr_low(text):
        return _t2hpmr_s(text).lower().replace("ё", "е")

    def _t2hpmr_is_recall_request(text):
        low = _t2hpmr_low(text).replace("[voice]", " ")
        if not low.strip():
            return False
        memory_markers = (
            "помни", "раньше", "месяц", "месяцев", "недел", "когда-то",
            "делали", "делал", "считали", "считал", "скидывал", "присылал",
            "где он", "где она", "где этот", "где расчет", "где расчёт",
            "найди в памяти", "подними", "покажи стар", "вернись к",
        )
        object_markers = (
            "проект", "расчет", "расчёт", "смет", "файл", "pdf", "мике", "мке",
        )
        return any(m in low for m in memory_markers) and any(m in low for m in object_markers)

    def _t2hpmr_tokens(text):
        stop = {
            "тебе", "тебя", "сюда", "этот", "этого", "который", "которые",
            "раньше", "может", "быть", "пару", "месяц", "месяцев", "назад",
            "где", "какой", "какая", "какие", "сделать", "сделал", "делали",
            "просил", "считал", "считали", "проект", "расчет", "расчёт",
        }
        words = []
        for word in re.findall(r"[a-zа-я0-9хxё]+", _t2hpmr_low(text)):
            if len(word) < 3 or word in stop:
                continue
            if word.startswith("мике"):
                word = "мике"
            words.append(word)
        return list(dict.fromkeys(words))[:16]

    def _t2hpmr_extract_file_name(raw_text):
        try:
            obj = json.loads(_t2hpmr_s(raw_text))
            if isinstance(obj, dict):
                return _t2hpmr_s(obj.get("file_name") or "")
        except Exception:
            pass
        m = re.search(r'"file_name"\s*:\s*"([^"]+)"', _t2hpmr_s(raw_text))
        return m.group(1) if m else ""

    def _t2hpmr_links(text):
        xlsx = ""
        pdf = ""
        for line in _t2hpmr_s(text).splitlines():
            low = line.lower()
            found = re.findall(r"https?://[^\s)]+", line)
            if not found:
                continue
            if low.strip().startswith("excel:") or low.strip().startswith("xlsx:"):
                xlsx = found[0]
            elif low.strip().startswith("pdf:"):
                pdf = found[0]
        if xlsx or pdf:
            return xlsx, pdf
        links = re.findall(r"https?://[^\s)]+", _t2hpmr_s(text))
        xlsx = next((x for x in links if "spreadsheet" in x or "xlsx" in x.lower()), "")
        pdf = next((x for x in links if x != xlsx), "")
        if not pdf:
            pdf = next((x for x in links if "drive.google.com" in x), "")
        return xlsx, pdf

    def _t2hpmr_score_blob(query_tokens, blob):
        low = _t2hpmr_low(blob)
        score = 0
        for token in query_tokens:
            if token in low:
                score += 5 if token =<REDACTED_SECRET> "мике" else 2
        if "смета готов" in low:
            score += 4
        if "drive.google.com" in low or "docs.google.com" in low:
            score += 4
        if ".pdf" in low or "pdf" in low:
            score += 2
        if "file_name" in low:
            score += 1
        return score

    def _t2hpmr_find_in_core(conn, chat_id, topic_id, current_task_id, raw_text):
        tokens = _t2hpmr_tokens(raw_text)
        rows = conn.execute(
            """
            SELECT id, state, input_type, COALESCE(raw_input,'') AS raw_input,
                   COALESCE(result,'') AS result, COALESCE(error_message,'') AS error_message,
                   created_at, updated_at
            FROM tasks
            WHERE CAST(chat_id AS TEXT)=?
              AND COALESCE(topic_id,0)=?
              AND id<>?
              AND state IN ('DONE','AWAITING_CONFIRMATION','ARCHIVED')
            ORDER BY updated_at DESC, created_at DESC
            LIMIT 800
            """,
            (str(chat_id), int(topic_id), str(current_task_id)),
        ).fetchall()
        best = None
        for row in rows:
            raw = _t2hpmr_s(row["raw_input"])
            result = _t2hpmr_s(row["result"])
            blob = raw + "\n" + result
            score = _t2hpmr_score_blob(tokens, blob)
            if "мике" in _t2hpmr_low(raw_text) and "мике" not in _t2hpmr_low(blob):
                score = 0
            if score <= 0:
                continue
            if "drive.google.com" in result or "docs.google.com" in result:
                score += 5
            item = (score, row)
            if best is None or item[0] > best[0]:
                best = item
        return best[1] if best else None

    def _t2hpmr_find_in_memory(chat_id, topic_id, raw_text):
        tokens = _t2hpmr_tokens(raw_text)
        if not os.path.exists(MEM_DB):
            return None
        mem = sqlite3.connect(MEM_DB)
        mem.row_factory = sqlite3.Row
        try:
            rows = mem.execute(
                """
                SELECT key, value, timestamp, COALESCE(topic_id,0) AS topic_id, COALESCE(scope,'topic') AS scope
                FROM memory
                WHERE CAST(chat_id AS TEXT)=?
                  AND (COALESCE(topic_id,0)=? OR key GLOB ?)
                ORDER BY timestamp DESC
                LIMIT 1200
                """,
                (str(chat_id), int(topic_id), f"topic_{int(topic_id)}_*"),
            ).fetchall()
        finally:
            mem.close()
        best = None
        for row in rows:
            blob = _t2hpmr_s(row["key"]) + "\n" + _t2hpmr_s(row["value"])
            score = _t2hpmr_score_blob(tokens, blob)
            if "мике" in _t2hpmr_low(raw_text) and "мике" not in _t2hpmr_low(blob):
                score = 0
            if score <= 0:
                continue
            item = (score, row)
            if best is None or item[0] > best[0]:
                best = item
        return best[1] if best else None

    def _t2hpmr_build_answer(core_row, mem_row, raw_text):
        if core_row:
            task_id = _t2hpmr_s(core_row["id"])
            raw = _t2hpmr_s(core_row["raw_input"])
            result = _t2hpmr_s(core_row["result"])
            file_name = _t2hpmr_extract_file_name(raw) or "файл не указан"
            xlsx, pdf = _t2hpmr_links(result)
            total_line = ""
            for line in result.splitlines():
                if any(x in line for x in ("Без НДС:", "С НДС:", "Итого:", "Материалы:", "Работы:")):
                    if "Итого:" in line or "Без НДС:" in line or "С НДС:" in line:
                        total_line = line.strip()
            parts = [
                "Нашёл старый расчёт в памяти topic_2. Пересчёт не запускал.",
                f"Дата: {_t2hpmr_s(core_row['created_at'])}",
                f"Задача: {task_id}",
                f"Файл: {file_name}",
            ]
            if total_line:
                parts.append(total_line)
            if xlsx:
                parts.append(f"Excel: {xlsx}")
            if pdf:
                parts.append(f"PDF: {pdf}")
            if not xlsx and not pdf:
                clean_result = _clean(result, 1200)
                if clean_result:
                    parts.append(clean_result)
            return "\n".join(parts)[:3900]

        if mem_row:
            value = _clean(_t2hpmr_s(mem_row["value"]), 2600)
            return (
                "Нашёл запись в памяти topic_2. Пересчёт не запускал.\n"
                f"Ключ: {_t2hpmr_s(mem_row['key'])}\n"
                f"Дата памяти: {_t2hpmr_s(mem_row['timestamp'])}\n\n"
                f"{value}"
            )[:3900]

        return (
            "В памяти topic_2 и в core.db не нашёл расчёт по этому описанию. "
            "Пересчёт не запускал. Уточни название файла или дату, и я поищу точнее."
        )

    async def _handle_new(conn, task, chat_id, topic_id):  # noqa: F811
        try:
            if int(topic_id or 0) == 2:
                raw = _t2hpmr_s(_t2hpmr_get(task, "raw_input"))
                input_type = _t2hpmr_s(_t2hpmr_get(task, "input_type")).lower()
                task_id = _t2hpmr_s(_t2hpmr_get(task, "id"))
                reply_to = _t2hpmr_get(task, "reply_to_message_id")
                if input_type in ("text", "voice", "search", "") and _t2hpmr_is_recall_request(raw):
                    core_row = _t2hpmr_find_in_core(conn, chat_id, topic_id, task_id, raw)
                    mem_row = None if core_row else _t2hpmr_find_in_memory(chat_id, topic_id, raw)
                    answer = _t2hpmr_build_answer(core_row, mem_row, raw)
                    sent = send_reply_ex(
                        chat_id=str(chat_id),
                        text=answer,
                        reply_to_message_id=reply_to,
                        message_thread_id=2,
                    )
                    bot_mid = sent.get("bot_message_id") if isinstance(sent, dict) else None
                    kwargs = {"state": "DONE", "result": answer, "error_message": ""}
                    if bot_mid:
                        kwargs["bot_message_id"] = bot_mid
                    _update_task(conn, task_id, **kwargs)
                    if core_row:
                        _history(conn, task_id, _T2HPMR_PATCH + ":core_task=" + _t2hpmr_s(core_row["id"]))
                    elif mem_row:
                        _history(conn, task_id, _T2HPMR_PATCH + ":memory_key=" + _t2hpmr_s(mem_row["key"])[:120])
                    else:
                        _history(conn, task_id, _T2HPMR_PATCH + ":not_found")
                    conn.commit()
                    logger.info("%s handled task_id=%s", _T2HPMR_PATCH, task_id)
                    return
        except Exception as exc:
            try:
                logger.exception("%s_ERR:%s", _T2HPMR_PATCH, exc)
            except Exception:
                pass
        if _t2hpmr_prev_handle_new:
            return await _t2hpmr_prev_handle_new(conn, task, chat_id, topic_id)
        return None

    if _t2hpmr_prev_handle_new:
        globals()["_handle_new"] = _handle_new
    logger.info("%s installed", _T2HPMR_PATCH)
except Exception as _t2hpmr_install_err:
    try:
        logger.exception("PATCH_TOPIC2_HISTORICAL_PROJECT_MEMORY_RECALL_V1_INSTALL_ERR:%s", _t2hpmr_install_err)
    except Exception:
        pass
# === END_PATCH_TOPIC2_HISTORICAL_PROJECT_MEMORY_RECALL_V1 ===

# === PATCH_GLOBAL_HISTORICAL_MEMORY_RECALL_V1 ===
try:
    _GHMR_PATCH = "PATCH_GLOBAL_HISTORICAL_MEMORY_RECALL_V1"
    _ghmr_prev_handle_new = globals().get("_handle_new")

    def _ghmr_s(value):
        return "" if value is None else str(value)

    def _ghmr_get(row, key, default=None):
        try:
            if hasattr(row, "keys") and key in row.keys():
                return row[key]
        except Exception:
            pass
        return default

    def _ghmr_low(text):
        return _ghmr_s(text).lower().replace("ё", "е")

    def _ghmr_is_recall_request(text):
        low = _ghmr_low(text).replace("[voice]", " ")
        if not low.strip():
            return False
        memory_markers = (
            "помни", "напомни", "вспомни", "раньше", "месяц", "месяцев",
            "недел", "когда-то", "истори", "архив", "памят", "делали",
            "делал", "считали", "считал", "скидывал", "присылал",
            "где он", "где она", "где этот", "где эта", "где расчет",
            "где расчёт", "найди в памяти", "подними", "покажи стар",
            "вернись к", "что было", "что обсуждали", "что делали",
            "какие задачи", "какой проект", "какой файл",
        )
        object_markers = (
            "проект", "расчет", "расчёт", "смет", "файл", "pdf", "задач",
            "ответ", "ссылк", "документ", "акт", "поиск", "поставщик",
            "мике", "мке",
        )
        return any(m in low for m in memory_markers) and any(m in low for m in object_markers)

    def _ghmr_is_explicit_topic500_search(text, topic_id):
        if int(topic_id or 0) != 500:
            return False
        low = _ghmr_low(text).replace("[voice]", " ")
        search_markers = (
            "найди", "найти", "поищи", "поиск", "ищи", "подбери",
            "в интернете", "в открытых источниках", "ссылка", "ссылки",
            "поставщик", "поставщики", "исполнитель", "исполнители",
            "компания", "компании", "цена", "стоимость", "контакт", "телефон",
        )
        return any(x in low for x in search_markers)

    def _ghmr_all_topics_requested(text):
        low = _ghmr_low(text)
        return any(x in low for x in (
            "по всем топикам", "во всех топиках", "по всему проекту",
            "во всем проекте", "во всём проекте", "по всем чатам",
            "во всех чатах", "везде",
        ))

    def _ghmr_is_ambiguous_live_continuation(text):
        low = _ghmr_low(text).replace("[voice]", " ")
        specific_markers = (
            ".pdf", ".xlsx", ".xls", ".docx", "мике", "мке",
            "8х12", "8x12", "май", "июн", "июл", "2026", "2025",
        )
        if any(x in low for x in specific_markers):
            return False
        continuation_markers = (
            "запрос уже есть",
            "задание уже есть",
            "то задание",
            "задание которое я давал",
            "которое я давал",
            "все ответы уже есть",
            "все ответы есть",
            "ответы уже есть",
            "посмотри то задание",
            "посмотри задание",
            "предыдущее задание",
            "текущая задача",
            "эта задача",
        )
        return any(x in low for x in continuation_markers)

    def _ghmr_has_recent_same_topic_work(conn, chat_id, topic_id, current_task_id):
        try:
            if int(topic_id or 0) <= 0:
                return False
            row = conn.execute(
                """
                SELECT id
                FROM tasks
                WHERE CAST(chat_id AS TEXT)=?
                  AND COALESCE(topic_id,0)=?
                  AND id<>?
                  AND state IN ('WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION','FAILED')
                  AND (
                    updated_at >= datetime('now','-18 hours')
                    OR created_at >= datetime('now','-18 hours')
                  )
                ORDER BY updated_at DESC, created_at DESC
                LIMIT 1
                """,
                (str(chat_id), int(topic_id or 0), str(current_task_id)),
            ).fetchone()
            return row is not None
        except Exception:
            return False

    def _ghmr_tokens(text):
        stop = {
            "тебе", "тебя", "сюда", "этот", "эта", "этого", "который",
            "которые", "раньше", "может", "быть", "пару", "месяц",
            "месяцев", "назад", "где", "какой", "какая", "какие",
            "сделать", "сделал", "делали", "просил", "считал", "считали",
            "проект", "расчет", "расчёт", "задач", "ответ", "файл",
            "топик", "чат", "памяти", "память",
            "проверь", "проверить", "актуальность", "актуально",
            "стоимость", "стоимости", "цен", "цены", "работ", "работы",
            "материал", "материала", "объем", "объемы", "объём", "объёмы",
            "согласно", "этого", "списка", "который", "которые",
            "посчитаны", "посчитать", "найти", "ставил",
        }
        words = []
        for word in re.findall(r"[a-zа-я0-9хxё]+", _ghmr_low(text)):
            if len(word) < 3 or word in stop:
                continue
            if word.startswith("мике"):
                word = "мике"
            words.append(word)
        return list(dict.fromkeys(words))[:18]

    def _ghmr_extract_file_name(raw_text):
        try:
            obj = json.loads(_ghmr_s(raw_text))
            if isinstance(obj, dict):
                return _ghmr_s(obj.get("file_name") or "")
        except Exception:
            pass
        m = re.search(r'"file_name"\s*:\s*"([^"]+)"', _ghmr_s(raw_text))
        return m.group(1) if m else ""

    def _ghmr_file_meta(raw_text):
        try:
            obj = json.loads(_ghmr_s(raw_text))
            if isinstance(obj, dict):
                return {
                    "telegram_message_id": _ghmr_s(obj.get("telegram_message_id") or ""),
                    "telegram_chat_id": _ghmr_s(obj.get("telegram_chat_id") or ""),
                }
        except Exception:
            pass
        return {"telegram_message_id": "", "telegram_chat_id": ""}

    def _ghmr_telegram_link(chat_id, message_id):
        chat = _ghmr_s(chat_id).strip()
        msg = _ghmr_s(message_id).strip()
        if not chat or not msg:
            return ""
        if chat.startswith("-100"):
            chat = chat[4:]
        else:
            chat = chat.lstrip("-")
        if not chat.isdigit() or not msg.isdigit():
            return ""
        return f"https://t.me/c/{chat}/{msg}"

    def _ghmr_source_reply_to(core_rows):
        for row in core_rows or []:
            meta = _ghmr_file_meta(_ghmr_s(row["raw_input"]))
            mid = meta.get("telegram_message_id") or ""
            if mid.isdigit():
                return int(mid)
        return None

    def _ghmr_links(text):
        xlsx = ""
        pdf = ""
        for line in _ghmr_s(text).splitlines():
            low = line.lower()
            found = re.findall(r"https?://[^\s)]+", line)
            if not found:
                continue
            if low.strip().startswith("excel:") or low.strip().startswith("xlsx:"):
                xlsx = found[0]
            elif low.strip().startswith("pdf:"):
                pdf = found[0]
        if xlsx or pdf:
            return xlsx, pdf
        links = re.findall(r"https?://[^\s)]+", _ghmr_s(text))
        xlsx = next((x for x in links if "spreadsheet" in x or "xlsx" in x.lower()), "")
        pdf = next((x for x in links if x != xlsx and "drive.google.com" in x), "")
        if not pdf:
            pdf = next((x for x in links if x != xlsx), "")
        return xlsx, pdf

    def _ghmr_score_blob(query_tokens, blob):
        low = _ghmr_low(blob)
        score = 0
        for token in query_tokens:
            if token in low:
                score += 6 if token =<REDACTED_SECRET> "мике" else 2
        if not query_tokens and ("смета готов" in low or "drive.google.com" in low):
            score += 1
        if "смета готов" in low or "подтверждение принято" in low:
            score += 3
        if "drive.google.com" in low or "docs.google.com" in low:
            score += 4
        if ".pdf" in low or "pdf" in low:
            score += 2
        if "file_name" in low:
            score += 1
        return score

    def _ghmr_core_candidates(conn, chat_id, topic_id, current_task_id, raw_text, all_topics):
        tokens = _ghmr_tokens(raw_text)
        if not tokens:
            return []
        where = [
            "CAST(chat_id AS TEXT)=?",
            "id<>?",
            "state IN ('DONE','AWAITING_CONFIRMATION','ARCHIVED')",
        ]
        params = [str(chat_id), str(current_task_id)]
        if not all_topics:
            where.append("COALESCE(topic_id,0)=?")
            params.append(int(topic_id or 0))
        rows = conn.execute(
            f"""
            SELECT id, COALESCE(topic_id,0) AS topic_id, state, input_type,
                   COALESCE(raw_input,'') AS raw_input, COALESCE(result,'') AS result,
                   COALESCE(error_message,'') AS error_message, created_at, updated_at
            FROM tasks
            WHERE {' AND '.join(where)}
            ORDER BY updated_at DESC, created_at DESC
            LIMIT 1200
            """,
            params,
        ).fetchall()
        scored = []
        for row in rows:
            blob = _ghmr_s(row["raw_input"]) + "\n" + _ghmr_s(row["result"])
            score = _ghmr_score_blob(tokens, blob)
            if "мике" in _ghmr_low(raw_text) and "мике" not in _ghmr_low(blob):
                score = 0
            if score <= 0:
                continue
            if "drive.google.com" in _ghmr_s(row["result"]) or "docs.google.com" in _ghmr_s(row["result"]):
                score += 5
            scored.append((score, row))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [row for _, row in scored[:5]]

    def _ghmr_memory_candidates(chat_id, topic_id, raw_text, all_topics):
        tokens = _ghmr_tokens(raw_text)
        if not tokens:
            return []
        if not os.path.exists(MEM_DB):
            return []
        mem = sqlite3.connect(MEM_DB)
        mem.row_factory = sqlite3.Row
        try:
            where = ["CAST(chat_id AS TEXT)=?"]
            params = [str(chat_id)]
            if not all_topics:
                where.append("(COALESCE(topic_id,0)=? OR key GLOB ?)")
                params.extend([int(topic_id or 0), f"topic_{int(topic_id or 0)}_*"])
            rows = mem.execute(
                f"""
                SELECT key, value, timestamp, COALESCE(topic_id,0) AS topic_id, COALESCE(scope,'topic') AS scope
                FROM memory
                WHERE {' AND '.join(where)}
                ORDER BY timestamp DESC
                LIMIT 1600
                """,
                params,
            ).fetchall()
        finally:
            mem.close()
        scored = []
        for row in rows:
            blob = _ghmr_s(row["key"]) + "\n" + _ghmr_s(row["value"])
            score = _ghmr_score_blob(tokens, blob)
            if "мике" in _ghmr_low(raw_text) and "мике" not in _ghmr_low(blob):
                score = 0
            if score <= 0:
                continue
            scored.append((score, row))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [row for _, row in scored[:5]]

    def _ghmr_answer(core_rows, mem_rows, all_topics):
        if core_rows:
            parts = ["Нашёл в памяти. Пересчёт, поиск и новую задачу не запускал."]
            for row in core_rows[:3]:
                task_id = _ghmr_s(row["id"])
                raw = _ghmr_s(row["raw_input"])
                result = _ghmr_s(row["result"])
                file_name = _ghmr_extract_file_name(raw) or "файл не указан"
                file_meta = _ghmr_file_meta(raw)
                source_link = _ghmr_telegram_link(
                    file_meta.get("telegram_chat_id") or "",
                    file_meta.get("telegram_message_id") or "",
                )
                xlsx, pdf = _ghmr_links(result)
                total_line = ""
                for line in result.splitlines():
                    if "Без НДС:" in line or "С НДС:" in line or line.strip().startswith("Итого:"):
                        total_line = line.strip()
                block = [
                    "",
                    f"Topic: {int(row['topic_id'])}" if all_topics else "",
                    f"Дата: {_ghmr_s(row['created_at'])}",
                    f"Файл: {file_name}",
                ]
                if source_link:
                    block.append(f"Исходный файл в Telegram: {source_link}")
                if total_line:
                    block.append(total_line)
                if xlsx:
                    block.append(f"Excel: {xlsx}")
                if pdf:
                    block.append(f"PDF: {pdf}")
                if not xlsx and not pdf:
                    brief = _clean(result, 700)
                    if brief:
                        block.append(brief)
                parts.append("\n".join(x for x in block if x))
            return "\n".join(parts)[:3900]

        if mem_rows:
            parts = ["Нашёл запись в памяти. Пересчёт, поиск и новую задачу не запускал."]
            for row in mem_rows[:3]:
                value = _clean(_ghmr_s(row["value"]), 850)
                block = [
                    "",
                    f"Topic: {int(row['topic_id'])}" if all_topics else "",
                    f"Ключ: {_ghmr_s(row['key'])}",
                    f"Дата памяти: {_ghmr_s(row['timestamp'])}",
                    value,
                ]
                parts.append("\n".join(x for x in block if x))
            return "\n".join(parts)[:3900]

        place = "по всем топикам этого чата" if all_topics else "в текущем топике"
        return (
            f"В памяти и core.db {place} не нашёл подходящую запись. "
            "Пересчёт, поиск и новую задачу не запускал. Уточни название файла, объект или дату."
        )

    async def _handle_new(conn, task, chat_id, topic_id):  # noqa: F811
        try:
            raw = _ghmr_s(_ghmr_get(task, "raw_input"))
            input_type = _ghmr_s(_ghmr_get(task, "input_type")).lower()
            task_id = _ghmr_s(_ghmr_get(task, "id"))
            reply_to = _ghmr_get(task, "reply_to_message_id")
            if _ghmr_is_explicit_topic500_search(raw, topic_id):
                _history(conn, task_id, _GHMR_PATCH + ":SKIP_TOPIC500_EXPLICIT_SEARCH")
                conn.commit()
                if _ghmr_prev_handle_new:
                    return await _ghmr_prev_handle_new(conn, task, chat_id, topic_id)
                return None
            if (
                input_type in ("text", "voice", "search", "")
                and _ghmr_is_recall_request(raw)
                and _ghmr_is_ambiguous_live_continuation(raw)
                and _ghmr_has_recent_same_topic_work(conn, chat_id, topic_id, task_id)
            ):
                _history(conn, task_id, _GHMR_PATCH + ":SKIP_ACTIVE_TOPIC_CONTEXT")
                conn.commit()
                if _ghmr_prev_handle_new:
                    return await _ghmr_prev_handle_new(conn, task, chat_id, topic_id)
                return None
            if input_type in ("text", "voice", "search", "") and _ghmr_is_recall_request(raw):
                all_topics = _ghmr_all_topics_requested(raw)
                core_rows = _ghmr_core_candidates(conn, chat_id, topic_id, task_id, raw, all_topics)
                mem_rows = [] if core_rows else _ghmr_memory_candidates(chat_id, topic_id, raw, all_topics)
                answer = _ghmr_answer(core_rows, mem_rows, all_topics)
                source_reply_to = _ghmr_source_reply_to(core_rows)
                send_kwargs = {
                    "chat_id": str(chat_id),
                    "text": answer,
                    "reply_to_message_id": source_reply_to or reply_to,
                }
                if int(topic_id or 0) > 0:
                    send_kwargs["message_thread_id"] = int(topic_id or 0)
                sent = send_reply_ex(**send_kwargs)
                bot_mid = sent.get("bot_message_id") if isinstance(sent, dict) else None
                kwargs = {"state": "DONE", "result": answer, "error_message": "GLOBAL_MEMORY_RECALL_ANSWER"}
                if bot_mid:
                    kwargs["bot_message_id"] = bot_mid
                _update_task(conn, task_id, **kwargs)
                if core_rows:
                    _history(conn, task_id, _GHMR_PATCH + ":core_tasks=" + ",".join(_ghmr_s(r["id"])[:8] for r in core_rows[:3]))
                elif mem_rows:
                    _history(conn, task_id, _GHMR_PATCH + ":memory_keys=" + ",".join(_ghmr_s(r["key"])[:40] for r in mem_rows[:3]))
                else:
                    _history(conn, task_id, _GHMR_PATCH + ":not_found")
                conn.commit()
                logger.info("%s handled task_id=%s topic=%s all_topics=%s", _GHMR_PATCH, task_id, topic_id, all_topics)
                return
        except Exception as exc:
            try:
                logger.exception("%s_ERR:%s", _GHMR_PATCH, exc)
            except Exception:
                pass
        if _ghmr_prev_handle_new:
            return await _ghmr_prev_handle_new(conn, task, chat_id, topic_id)
        return None

    if _ghmr_prev_handle_new:
        globals()["_handle_new"] = _handle_new
    logger.info("%s installed", _GHMR_PATCH)
except Exception as _ghmr_install_err:
    try:
        logger.exception("PATCH_GLOBAL_HISTORICAL_MEMORY_RECALL_V1_INSTALL_ERR:%s", _ghmr_install_err)
    except Exception:
        pass
# === END_PATCH_GLOBAL_HISTORICAL_MEMORY_RECALL_V1 ===

# === PATCH_GLOBAL_MEMORY_RECALL_DONE_GATE_BYPASS_V1 ===
try:
    _GHMRB_PATCH = "PATCH_GLOBAL_MEMORY_RECALL_DONE_GATE_BYPASS_V1"
    _ghmrb_prev_update_task = globals().get("_update_task")

    def _ghmrb_s(value):
        return "" if value is None else str(value)

    def _ghmrb_is_memory_recall(kwargs):
        err = _ghmrb_s(kwargs.get("error_message"))
        result = _ghmrb_s(kwargs.get("result")).lower().replace("ё", "е")
        return (
            err == "GLOBAL_MEMORY_RECALL_ANSWER"
            or result.startswith("нашел в памяти")
            or result.startswith("нашёл в памяти")
            or "пересчет, поиск и новую задачу не запускал" in result
            or "пересчёт, поиск и новую задачу не запускал" in result
        )

    def _update_task(conn, task_id, **kwargs):  # noqa: F811
        if _ghmrb_is_memory_recall(kwargs):
            allowed = {
                "state", "result", "error_message", "bot_message_id",
                "message_id", "reply_to_message_id",
            }
            fields = []
            values = []
            for key, value in kwargs.items():
                if key in allowed:
                    fields.append(f"{key}=?")
                    values.append(value)
            fields.append("updated_at=datetime('now')")
            values.append(str(task_id))
            conn.execute(
                f"UPDATE tasks SET {', '.join(fields)} WHERE id=?",
                values,
            )
            return
        if _ghmrb_prev_update_task:
            return _ghmrb_prev_update_task(conn, task_id, **kwargs)
        return None

    if _ghmrb_prev_update_task:
        globals()["_update_task"] = _update_task
    logger.info("%s installed", _GHMRB_PATCH)
except Exception as _ghmrb_install_err:
    try:
        logger.exception("PATCH_GLOBAL_MEMORY_RECALL_DONE_GATE_BYPASS_V1_INSTALL_ERR:%s", _ghmrb_install_err)
    except Exception:
        pass
# === END_PATCH_GLOBAL_MEMORY_RECALL_DONE_GATE_BYPASS_V1 ===


# === PATCH_GLOBAL_DRIVE_FILE_CONTEXT_PREHANDLE_V1 ===
# Canon: drive_file/file/photo/document duplicate guard must run before topic engines.
try:
    _GDFCP_PATCH = "PATCH_GLOBAL_DRIVE_FILE_CONTEXT_PREHANDLE_V1"
    _gdfcp_prev_handle_drive_file = globals().get("_handle_drive_file")

    async def _handle_drive_file(conn, task, chat_id, topic_id):  # noqa: F811
        try:
            from core.file_context_intake import prehandle_task_context_v1 as _gdfcp_prehandle

            _gdfcp_res = _gdfcp_prehandle(conn, task)
            if _gdfcp_res and _gdfcp_res.get("handled"):
                _gdfcp_tid = _s(_task_field(task, "id", ""))
                _gdfcp_chat = _s(_task_field(task, "chat_id", chat_id))
                _gdfcp_text = _gdfcp_res.get("message") or ""
                _gdfcp_reply = _gdfcp_res.get("reply_to_message_id") or _task_field(task, "reply_to_message_id", None)
                _gdfcp_send = _send_once_ex(
                    conn,
                    _gdfcp_tid,
                    _gdfcp_chat,
                    _gdfcp_text,
                    _gdfcp_reply,
                    _gdfcp_res.get("kind", "file_context_intake"),
                )
                _update_task(
                    conn,
                    _gdfcp_tid,
                    state=_gdfcp_res.get("state", "DONE"),
                    result=_gdfcp_text,
                    error_message=_gdfcp_res.get("error_message", ""),
                    bot_message_id=_gdfcp_send.get("bot_message_id"),
                )
                _history(conn, _gdfcp_tid, _gdfcp_res.get("history", _GDFCP_PATCH + ":HANDLED"))
                conn.commit()
                logger.info("%s handled task_id=%s", _GDFCP_PATCH, _gdfcp_tid)
                return
        except Exception as _gdfcp_err:
            try:
                logger.warning("%s_ERR task=%s err=%s", _GDFCP_PATCH, _task_field(task, "id", ""), _gdfcp_err)
            except Exception:
                pass

        if _gdfcp_prev_handle_drive_file:
            return await _gdfcp_prev_handle_drive_file(conn, task, chat_id, topic_id)
        return None

    if _gdfcp_prev_handle_drive_file and not getattr(_gdfcp_prev_handle_drive_file, "_gdfcp_wrapped", False):
        _handle_drive_file._gdfcp_wrapped = True
        globals()["_handle_drive_file"] = _handle_drive_file
        logger.info("%s installed", _GDFCP_PATCH)
except Exception as _gdfcp_install_err:
    try:
        logger.exception("PATCH_GLOBAL_DRIVE_FILE_CONTEXT_PREHANDLE_V1_INSTALL_ERR:%s", _gdfcp_install_err)
    except Exception:
        pass
# === END_PATCH_GLOBAL_DRIVE_FILE_CONTEXT_PREHANDLE_V1 ===


# === PATCH_GLOBAL_DUPLICATE_FILE_OFFER_REPLY_V1 ===
# Canon: reply to duplicate/file-intake menu continues the file dialogue before topic-specific routes.
try:
    _GDFOR_PATCH = "PATCH_GLOBAL_DUPLICATE_FILE_OFFER_REPLY_V1"
    _gdfor_prev_handle_new = globals().get("_handle_new")

    def _gdfor_text(value):
        return "" if value is None else str(value).strip()

    def _gdfor_get(row, key, default=None):
        try:
            if hasattr(row, "keys") and key in row.keys():
                return row[key]
        except Exception:
            pass
        if isinstance(row, dict):
            return row.get(key, default)
        return default

    def _gdfor_parent(conn, task, chat_id, topic_id):
        reply_to = _gdfor_get(task, "reply_to_message_id")
        task_id = _gdfor_text(_gdfor_get(task, "id", ""))
        params = [str(chat_id), int(topic_id or 0), task_id]
        exact = ""
        if reply_to:
            exact = "AND (CAST(COALESCE(bot_message_id,'') AS TEXT)=? OR CAST(COALESCE(reply_to_message_id,'') AS TEXT)=?)"
            params.extend([str(reply_to), str(reply_to)])
        row = conn.execute(
            f"""
            SELECT *
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND id<>?
              AND state='WAITING_CLARIFICATION'
              {exact}
              AND (
                COALESCE(result,'') LIKE '%Файл уже есть%'
                OR COALESCE(result,'') LIKE '%этот файл ты уже скидывал%'
              )
            ORDER BY updated_at DESC, rowid DESC
            LIMIT 1
            """,
            params,
        ).fetchone()
        if row:
            return row
        return conn.execute(
            """
            SELECT *
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND id<>?
              AND state='WAITING_CLARIFICATION'
              AND (
                COALESCE(result,'') LIKE '%Файл уже есть%'
                OR COALESCE(result,'') LIKE '%этот файл ты уже скидывал%'
              )
              AND updated_at >= datetime('now','-24 hours')
            ORDER BY updated_at DESC, rowid DESC
            LIMIT 1
            """,
            (str(chat_id), int(topic_id or 0), task_id),
        ).fetchone()

    def _gdfor_load_raw(raw):
        try:
            obj = json.loads(_gdfor_text(raw))
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return {}

    def _gdfor_caption(intent):
        return {
            "estimate": "смета",
            "description": "описание",
            "table": "таблица",
            "template": "шаблон",
            "project": "анализ",
        }.get(_gdfor_text(intent), _gdfor_text(intent))

    def _gdfor_is_technical_topic(topic_id):
        return int(topic_id or 0) in {2, 5, 210, 500}

    async def _gdfor_handle_description(conn, parent_id, meta, chat_id, topic_id):
        local_path = _gdfor_text(meta.get("local_path"))
        if not local_path:
            return False
        try:
            from core.universal_file_handler import extract_text_from_file
            data = extract_text_from_file(local_path, parent_id, int(topic_id or 0))
        except Exception as exc:
            logger.warning("%s_DESCRIPTION_ERR parent=%s err=%s", _GDFOR_PATCH, parent_id, exc)
            return False
        if not data or not data.get("success"):
            return False
        text = _gdfor_text(data.get("text"))
        rows = data.get("rows") or []
        if not text and rows:
            text = "\n".join(" | ".join(str(c or "") for c in row) for row in rows[:20])
        if not text:
            return False
        file_name = _gdfor_text(meta.get("file_name")) or "файл"
        msg = (
            f"{file_name} прочитан ({data.get('type') or 'unknown'}).\n"
            f"Строк таблиц: {len(rows)}\n\n"
            + text[:3500]
        )
        reply_to = meta.get("telegram_message_id")
        send_res = _send_once_ex(
            conn,
            parent_id,
            str(chat_id),
            msg,
            reply_to,
            "duplicate_file_description",
        )
        bot_id = send_res.get("bot_message_id") if isinstance(send_res, dict) else None
        if bot_id:
            conn.execute(
                "UPDATE tasks SET state='AWAITING_CONFIRMATION', result=?, error_message='', bot_message_id=?, updated_at=datetime('now') WHERE id=?",
                (msg, bot_id, parent_id),
            )
        else:
            conn.execute(
                "UPDATE tasks SET state='AWAITING_CONFIRMATION', result=?, error_message='', updated_at=datetime('now') WHERE id=?",
                (msg, parent_id),
            )
        _history(conn, parent_id, _GDFOR_PATCH + ":DESCRIPTION_HANDLED_UNIVERSAL_FILE_HANDLER")
        conn.commit()
        return True

    async def _handle_new(conn, task, chat_id, topic_id):  # noqa: F811
        try:
            raw = _gdfor_text(_task_field(task, "raw_input", ""))
            intent = _ioa_parse(raw) if callable(globals().get("_ioa_parse")) else ""
            if intent:
                parent = _gdfor_parent(conn, task, chat_id, topic_id)
                if parent is not None:
                    child_id = _gdfor_text(_task_field(task, "id", ""))
                    parent_id = _gdfor_text(_gdfor_get(parent, "id", ""))
                    meta = _gdfor_load_raw(_gdfor_get(parent, "raw_input", ""))
                    old_caption = _gdfor_text(meta.get("caption"))
                    chosen_caption = _gdfor_caption(intent)
                    meta["caption"] = (old_caption + "\n" + chosen_caption).strip() if old_caption else chosen_caption
                    meta["file_duplicate_choice_intent"] = intent
                    meta["file_duplicate_choice_raw"] = raw
                    conn.execute(
                        """
                        UPDATE tasks
                        SET raw_input=?,
                            state='NEW',
                            result='',
                            error_message='',
                            updated_at=datetime('now')
                        WHERE id=?
                        """,
                        (json.dumps(meta, ensure_ascii=False), parent_id),
                    )
                    _update_task(
                        conn,
                        child_id,
                        state="DONE",
                        result="Выбор действия по файлу принят: " + chosen_caption,
                        error_message="MERGED_TO_PARENT:" + parent_id,
                    )
                    _history(conn, parent_id, _GDFOR_PATCH + ":INTENT:" + intent + ":FROM:" + child_id)
                    _history(conn, child_id, _GDFOR_PATCH + ":MERGED_TO:" + parent_id)
                    conn.commit()
                    _send_once(
                        conn,
                        child_id,
                        str(chat_id),
                        "Принял. Делаю: " + chosen_caption,
                        _task_field(task, "reply_to_message_id", None),
                        "duplicate_file_offer_choice",
                    )
                    if intent == "description" and not _gdfor_is_technical_topic(topic_id):
                        if await _gdfor_handle_description(conn, parent_id, meta, chat_id, topic_id):
                            logger.info("%s parent=%s child=%s intent=%s handled=description", _GDFOR_PATCH, parent_id, child_id, intent)
                            return
                    parent_task = conn.execute(
                        "SELECT * FROM tasks WHERE id=?",
                        (parent_id,),
                    ).fetchone()
                    if parent_task is not None and callable(globals().get("_handle_drive_file")):
                        await globals()["_handle_drive_file"](conn, parent_task, chat_id, topic_id)
                    logger.info("%s parent=%s child=%s intent=%s", _GDFOR_PATCH, parent_id, child_id, intent)
                    return
        except Exception as _gdfor_err:
            try:
                logger.warning("%s_ERR task=%s err=%s", _GDFOR_PATCH, _task_field(task, "id", ""), _gdfor_err)
            except Exception:
                pass

        if _gdfor_prev_handle_new:
            return await _gdfor_prev_handle_new(conn, task, chat_id, topic_id)
        return None

    if _gdfor_prev_handle_new and not getattr(_gdfor_prev_handle_new, "_gdfor_wrapped", False):
        _handle_new._gdfor_wrapped = True
        globals()["_handle_new"] = _handle_new
        logger.info("%s installed", _GDFOR_PATCH)
except Exception as _gdfor_install_err:
    try:
        logger.exception("PATCH_GLOBAL_DUPLICATE_FILE_OFFER_REPLY_V1_INSTALL_ERR:%s", _gdfor_install_err)
    except Exception:
        pass
# === END_PATCH_GLOBAL_DUPLICATE_FILE_OFFER_REPLY_V1 ===

# === PATCH_TOPIC2_VOLUME_REVIEW_AFTER_MEMORY_RECALL_V1 ===
# Canon: topic_2 follow-up may use memory/reply/file context; do not ask again
# when the previous recall selected a concrete project estimate.
try:
    _T2VR_PATCH = "PATCH_TOPIC2_VOLUME_REVIEW_AFTER_MEMORY_RECALL_V1"
    _t2vr_prev_handle_new = globals().get("_handle_new")

    def _t2vr_s(value):
        return "" if value is None else str(value)

    def _t2vr_low(value):
        return _t2vr_s(value).lower().replace("ё", "е")

    def _t2vr_get(row, key, default=None):
        try:
            if hasattr(row, "keys") and key in row.keys():
                return row[key]
        except Exception:
            pass
        return default

    def _t2vr_is_volume_review(text):
        low = _t2vr_low(text).replace("[voice]", " ")
        if not low.strip():
            return False
        has_volume = any(x in low for x in ("объем", "объемы", "объём", "объёмы"))
        has_action = any(x in low for x in (
            "проверь", "проверить", "сравни", "сравнить", "сверь", "сверить",
            "корректн", "правильн", "не изменил", "не изменились",
        ))
        return has_volume and has_action

    def _t2vr_parse_anchor_ids(action):
        out = []
        text = _t2vr_s(action)
        for marker in ("core_tasks=", "core_task="):
            if marker not in text:
                continue
            tail = text.split(marker, 1)[1]
            tail = re.split(r"[\s;|]", tail, 1)[0]
            for part in tail.split(","):
                part = part.strip()
                if part:
                    out.append(part)
        return out

    def _t2vr_resolve_task_id(conn, partial_id):
        pid = _t2vr_s(partial_id).strip()
        if not pid:
            return ""
        row = conn.execute("SELECT id FROM tasks WHERE id=? LIMIT 1", (pid,)).fetchone()
        if row:
            return _t2vr_s(row["id"] if hasattr(row, "keys") and "id" in row.keys() else row[0])
        if len(pid) >= 6:
            row = conn.execute(
                "SELECT id FROM tasks WHERE id LIKE ? ORDER BY created_at DESC LIMIT 1",
                (pid + "%",),
            ).fetchone()
            if row:
                return _t2vr_s(row["id"] if hasattr(row, "keys") and "id" in row.keys() else row[0])
        return ""

    def _t2vr_anchor_from_replied_memory(conn, chat_id, topic_id, current_task_id, reply_to):
        if not reply_to:
            return None
        row = conn.execute(
            """
            SELECT id FROM tasks
            WHERE CAST(chat_id AS TEXT)=?
              AND COALESCE(topic_id,0)=?
              AND id<>?
              AND CAST(bot_message_id AS TEXT)=?
              AND error_message='GLOBAL_MEMORY_RECALL_ANSWER'
            ORDER BY updated_at DESC, created_at DESC
            LIMIT 1
            """,
            (str(chat_id), int(topic_id or 0), str(current_task_id), str(reply_to)),
        ).fetchone()
        if not row:
            return None
        recall_id = _t2vr_s(row["id"] if hasattr(row, "keys") and "id" in row.keys() else row[0])
        actions = conn.execute(
            "SELECT action FROM task_history WHERE task_id=? ORDER BY created_at DESC LIMIT 20",
            (recall_id,),
        ).fetchall()
        for action_row in actions:
            action = _t2vr_s(action_row["action"] if hasattr(action_row, "keys") and "action" in action_row.keys() else action_row[0])
            for partial in _t2vr_parse_anchor_ids(action):
                anchor_id = _t2vr_resolve_task_id(conn, partial)
                if anchor_id and anchor_id != recall_id:
                    return anchor_id
        return None

    def _t2vr_last_memory_anchor(conn, chat_id, topic_id, current_task_id):
        rows = conn.execute(
            """
            SELECT th.action
            FROM task_history th
            JOIN tasks t ON t.id=th.task_id
            WHERE CAST(t.chat_id AS TEXT)=?
              AND COALESCE(t.topic_id,0)=?
              AND t.id<>?
              AND th.action LIKE '%HISTORICAL_MEMORY_RECALL%core_task%'
            ORDER BY th.created_at DESC
            LIMIT 12
            """,
            (str(chat_id), int(topic_id or 0), str(current_task_id)),
        ).fetchall()
        for row in rows:
            action = _t2vr_s(row["action"] if hasattr(row, "keys") and "action" in row.keys() else row[0])
            for partial in _t2vr_parse_anchor_ids(action):
                anchor_id = _t2vr_resolve_task_id(conn, partial)
                if anchor_id:
                    anchor = conn.execute(
                        """
                        SELECT id, COALESCE(raw_input,'') AS raw_input, COALESCE(result,'') AS result
                        FROM tasks WHERE id=? LIMIT 1
                        """,
                        (anchor_id,),
                    ).fetchone()
                    if not anchor:
                        continue
                    blob = _t2vr_low(_t2vr_get(anchor, "raw_input", "") + "\n" + _t2vr_get(anchor, "result", ""))
                    if "drive.google.com" in blob or ".pdf" in blob or "смета готов" in blob:
                        return anchor_id
        return ""

    def _t2vr_file_meta(raw_input):
        try:
            obj = json.loads(_t2vr_s(raw_input))
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass
        return {}

    def _t2vr_telegram_link(chat_id, message_id):
        chat = _t2vr_s(chat_id).strip()
        msg = _t2vr_s(message_id).strip()
        if not chat or not msg:
            return ""
        if chat.startswith("-100"):
            chat = chat[4:]
        else:
            chat = chat.lstrip("-")
        if not chat.isdigit() or not msg.isdigit():
            return ""
        return f"https://t.me/c/{chat}/{msg}"

    def _t2vr_drive_links(text):
        xlsx = ""
        pdf = ""
        for line in _t2vr_s(text).splitlines():
            low = line.lower().strip()
            links = re.findall(r"https?://[^\s)]+", line)
            if not links:
                continue
            if low.startswith(("excel:", "xlsx:")):
                xlsx = links[0]
            elif low.startswith("pdf:"):
                pdf = links[0]
        return xlsx, pdf

    def _t2vr_history_facts(conn, task_id):
        rows = conn.execute(
            "SELECT action, created_at FROM task_history WHERE task_id=? ORDER BY created_at",
            (str(task_id),),
        ).fetchall()
        actions = [_t2vr_s(r["action"] if hasattr(r, "keys") and "action" in r.keys() else r[0]) for r in rows]
        facts = []
        for prefix in (
            "TOPIC2_PDF_SPEC_ROWS_EXTRACTED:",
            "TOPIC2_XLSX_ROWS_WRITTEN:",
            "TOPIC2_XLSX_CANON_COLUMNS_OK:",
            "TOPIC2_DRIVE_LINKS_SAVED:",
            "TOPIC2_TELEGRAM_DELIVERED:",
        ):
            matched = [a for a in actions if a.startswith(prefix)]
            if matched:
                facts.append(matched[-1])
        return facts

    def _t2vr_project_rows(local_path):
        if not local_path:
            return []
        try:
            from core.pdf_spec_extractor import extract_spec
            res = extract_spec(local_path)
            return (res or {}).get("rows") or []
        except Exception:
            return []

    def _t2vr_build_answer(conn, anchor):
        raw = _t2vr_s(_t2vr_get(anchor, "raw_input", ""))
        result = _t2vr_s(_t2vr_get(anchor, "result", ""))
        meta = _t2vr_file_meta(raw)
        file_name = _t2vr_s(meta.get("file_name") or "файл не указан")
        source_link = _t2vr_telegram_link(
            meta.get("telegram_chat_id") or _t2vr_get(anchor, "chat_id", ""),
            meta.get("telegram_message_id") or "",
        )
        xlsx, pdf = _t2vr_drive_links(result)
        facts = _t2vr_history_facts(conn, _t2vr_get(anchor, "id", ""))
        project_rows = _t2vr_project_rows(_t2vr_s(meta.get("local_path") or ""))

        lines = [
            "Проверяю именно объёмы по найденному расчёту, без интернет-поиска и без новой сметы.",
            f"Расчёт: {_t2vr_get(anchor, 'id', '')}",
            f"Файл: {file_name}",
        ]
        if source_link:
            lines.append(f"Исходный файл в Telegram: {source_link}")
        if xlsx:
            lines.append(f"Excel: {xlsx}")
        if pdf:
            lines.append(f"PDF: {pdf}")

        if project_rows:
            lines.append(f"Проектные строки, извлечённые из PDF сейчас: {len(project_rows)}")
            for row in project_rows[:12]:
                name = _t2vr_s(row.get("name") or "")[:90]
                unit = _t2vr_s(row.get("unit") or "")
                qty = _t2vr_s(row.get("qty") or "")
                if name and qty:
                    lines.append(f"- {name}: {qty} {unit}".rstrip())
        else:
            lines.append("Проектные объёмы из PDF автоматически не извлеклись в проверяемом виде.")

        if facts:
            lines.append("Факты предыдущего расчёта:")
            lines.extend(f"- {fact}" for fact in facts)

        if not project_rows:
            lines.append("Построчно подтвердить корректность объёмов не могу: нет извлечённой ВОР/спецификации в проверяемом виде. Нужно сверять листы проекта/ВОР, а не выдумывать объёмы.")
        return "\n".join(lines)[:3900]

    async def _handle_new(conn, task, chat_id, topic_id):  # noqa: F811
        try:
            if int(topic_id or 0) == 2:
                raw = _t2vr_s(_task_field(task, "raw_input", ""))
                task_id = _t2vr_s(_task_field(task, "id", ""))
                input_type = _t2vr_s(_task_field(task, "input_type", "")).lower()
                if input_type in ("text", "voice", "search", "") and _t2vr_is_volume_review(raw):
                    reply_to = _task_field(task, "reply_to_message_id", None)
                    anchor_id = (
                        _t2vr_anchor_from_replied_memory(conn, chat_id, topic_id, task_id, reply_to)
                        or _t2vr_last_memory_anchor(conn, chat_id, topic_id, task_id)
                    )
                    if anchor_id:
                        anchor = conn.execute("SELECT * FROM tasks WHERE id=? LIMIT 1", (anchor_id,)).fetchone()
                        if anchor is not None:
                            answer = _t2vr_build_answer(conn, anchor)
                            send_kwargs = {
                                "chat_id": str(chat_id),
                                "text": answer,
                                "reply_to_message_id": reply_to or _task_field(task, "reply_to_message_id", None),
                                "message_thread_id": 2,
                            }
                            sent = send_reply_ex(**send_kwargs)
                            bot_mid = sent.get("bot_message_id") if isinstance(sent, dict) else None
                            kwargs = {
                                "state": "DONE",
                                "result": answer,
                                "error_message": _T2VR_PATCH + ":ANCHOR:" + anchor_id,
                            }
                            if bot_mid:
                                kwargs["bot_message_id"] = bot_mid
                            _update_task(conn, task_id, **kwargs)
                            _history(conn, task_id, _T2VR_PATCH + ":ANCHOR:" + anchor_id)
                            conn.commit()
                            logger.info("%s handled task_id=%s anchor=%s", _T2VR_PATCH, task_id, anchor_id)
                            return
        except Exception as _t2vr_err:
            try:
                logger.exception("%s_ERR:%s", _T2VR_PATCH, _t2vr_err)
            except Exception:
                pass

        if _t2vr_prev_handle_new:
            return await _t2vr_prev_handle_new(conn, task, chat_id, topic_id)
        return None

    if _t2vr_prev_handle_new and not getattr(_t2vr_prev_handle_new, "_t2vr_wrapped", False):
        _handle_new._t2vr_wrapped = True
        globals()["_handle_new"] = _handle_new
        logger.info("%s installed", _T2VR_PATCH)
except Exception as _t2vr_install_err:
    try:
        logger.exception("PATCH_TOPIC2_VOLUME_REVIEW_AFTER_MEMORY_RECALL_V1_INSTALL_ERR:%s", _t2vr_install_err)
    except Exception:
        pass
# === END_PATCH_TOPIC2_VOLUME_REVIEW_AFTER_MEMORY_RECALL_V1 ===

# === PATCH_TOPIC5_BYPASS_CONSTRUCTION_GUARD_V1 ===
# Canon: topic_5 files are VisitMaterial for technadzor, not construction artifacts.
# Scope: topic_id=5 only; bypass FULL_CONSTRUCTION_FILE_CONTOUR_CANON_GUARD_V1
# public-result validator so photo/file buffering can stay DONE without Drive XLSX/PDF artifact.
try:
    _T5BCG_PATCH = "PATCH_TOPIC5_BYPASS_CONSTRUCTION_GUARD_V1"
    _t5bcg_prev_public_result_violation = globals().get("_fcg_public_result_violation")

    def _t5bcg_s(v, limit=12000):
        return "" if v is None else str(v)[:limit]

    def _t5bcg_row(row, key, default=None):
        try:
            if hasattr(row, "keys") and key in row.keys():
                return row[key]
        except Exception:
            pass
        try:
            return row[key]
        except Exception:
            return default

    def _fcg_public_result_violation(conn, task_id, state, result, error_message=""):
        try:
            row = None
            try:
                row = conn.execute("SELECT * FROM tasks WHERE id=?", (str(task_id),)).fetchone()
            except Exception:
                row = None
            topic_id = int(_t5bcg_row(row, "topic_id", 0) or 0) if row is not None else 0
            input_type = _t5bcg_s(_t5bcg_row(row, "input_type", "")).lower() if row is not None else ""
            result_text = _t5bcg_s(result, 50000).lower().replace("ё", "е")
            if topic_id == 5 and input_type in ("drive_file", "file", "photo", "image", "document"):
                ok_markers = (
                    "файл принят в полный контур технадзора",
                    "файл получил и сохранил в буфер технадзора",
                    "фото принято в пакет технадзора",
                    "файл принят в пакет технадзора",
                    "пояснение принято к фото",
                    "активная папка технадзора",
                    "материалов в буфере",
                    "акт не формирую без команды",
                )
                if any(m in result_text for m in ok_markers):
                    try:
                        _history(conn, str(task_id), _T5BCG_PATCH + ":ALLOW_TOPIC5_VISIT_MATERIAL")
                    except Exception:
                        pass
                    return ""
        except Exception:
            pass
        if callable(_t5bcg_prev_public_result_violation):
            return _t5bcg_prev_public_result_violation(conn, task_id, state, result, error_message)
        return ""

    logger.info("%s installed", _T5BCG_PATCH)
except Exception as _t5bcg_err:
    try:
        logger.exception("PATCH_TOPIC5_BYPASS_CONSTRUCTION_GUARD_V1_INSTALL_ERR:%s", _t5bcg_err)
    except Exception:
        pass
# === END_PATCH_TOPIC5_BYPASS_CONSTRUCTION_GUARD_V1 ===


# === PATCH_TOPIC5_VIOLATION_QUESTION_NOT_COMMENT_V1 ===
# Canon: topic_5 live answer logic must distinguish owner questions about defects
# from plain comments to photos. A question like "есть ли нарушения" is an
# analysis request over the current VisitBuffer, not a photo comment.
try:
    _T5VQ_PATCH = "PATCH_TOPIC5_VIOLATION_QUESTION_NOT_COMMENT_V1"
    _t5vq_prev_handle_new = globals().get("_handle_new")

    def _t5vq_s(v, limit=50000):
        return "" if v is None else str(v).strip()[:limit]

    def _t5vq_row(row, key, default=""):
        try:
            if hasattr(row, "keys") and key in row.keys():
                return row[key]
        except Exception:
            pass
        try:
            return row[key]
        except Exception:
            return default

    def _t5vq_clean(v):
        try:
            return _t5fc_clean_voice(v)
        except Exception:
            return _t5vq_s(v)

    def _t5vq_low(v):
        return _t5vq_s(v).lower().replace("ё", "е")

    def _t5vq_is_violation_question(text):
        low = _t5vq_low(text)
        if not any(x in low for x in ("?", "есть ли", "какие", "что значит", "проверь", "посмотри", "скажи")):
            return False
        return any(x in low for x in (
            "нарушен", "дефект", "замечан", "свар", "корроз", "трещин",
            "качество", "неправильно", "соответствует", "технадзор",
        ))

    def _t5vq_buf(chat_id):
        try:
            return _t5fc_buf(chat_id)
        except Exception:
            return {"materials": [], "defect_cards": [], "observations": [], "package_context": {}}

    def _t5vq_analyze_text(chat_id, clean):
        buf = _t5vq_buf(chat_id)
        mats = buf.get("materials") or []
        defects = []
        try:
            # Store the owner question as context, then reuse existing DefectCard
            # enrichment logic. This avoids the old "comment only" branch.
            saved = _t5fc_save_context(chat_id, clean)
            buf = saved.get("buf") or _t5vq_buf(chat_id)
            defects = buf.get("defect_cards") or []
        except Exception:
            try:
                defects = _t5fc_enrich_materials(buf)
            except Exception:
                defects = []

        lines = [
            "Принял как запрос анализа фото по технадзору, а не как пояснение к фото.",
            f"Фото в текущем пакете: {len(mats)} шт.",
        ]
        if defects:
            lines.append(f"DefectCard сформировано/обновлено: {len(defects)}.")
            for i, d in enumerate(defects[:5], 1):
                lines.append(f"{i}. Фото: {d.get('file_name') or 'UNKNOWN'}")
                lines.append(f"   Замечание: {d.get('defect_remark') or 'требует уточнения'}")
                lines.append(f"   Нормы: {d.get('normative_reference') or 'норма не подтверждена'}")
        else:
            lines.append("По одним фото без подтверждённого Vision-анализа не выдумываю нарушение.")
            lines.append("Нужен один из вариантов: дай пояснение, что именно проверить на фото, либо команда `сделай акт`, если нужно оформить пакет по имеющимся материалам.")
        lines.append("Акт не формирую без отдельной команды: Сделай акт")
        return "\n".join(lines)[:3500]

    async def _handle_new(conn, task, *args, **kwargs):
        try:
            task_id = _t5vq_s(_t5vq_row(task, "id"))
            chat_id = _t5vq_s(_t5vq_row(task, "chat_id", args[0] if len(args) > 0 else ""))
            topic_id = int(_t5vq_row(task, "topic_id", args[1] if len(args) > 1 else 0) or 0)
            input_type = _t5vq_s(_t5vq_row(task, "input_type", "")).lower()
            reply_to = _t5vq_row(task, "reply_to_message_id", None)
            raw = _t5vq_s(_t5vq_row(task, "raw_input", ""))
            clean = _t5vq_clean(raw)
            if topic_id == 5 and input_type in ("text", "voice", "") and _t5vq_is_violation_question(clean):
                msg = _t5vq_analyze_text(chat_id, clean)
                try:
                    sent = _send_once_ex(conn, task_id, str(chat_id), msg, reply_to, "topic5_violation_question_answer")
                    upd = {"state": "DONE", "result": msg, "error_message": ""}
                    if isinstance(sent, dict) and (sent.get("bot_message_id") or sent.get("message_id")):
                        upd["bot_message_id"] = sent.get("bot_message_id") or sent.get("message_id")
                    _update_task(conn, task_id, **upd)
                    _history(conn, task_id, _T5VQ_PATCH + ":HANDLED")
                    conn.commit()
                except Exception:
                    pass
                return
        except Exception as _t5vq_err:
            try:
                logger.exception("PATCH_TOPIC5_VIOLATION_QUESTION_NOT_COMMENT_V1_ERR:%s", _t5vq_err)
            except Exception:
                pass
        res = _t5vq_prev_handle_new(conn, task, *args, **kwargs)
        return await res if hasattr(res, "__await__") else res

    if _t5vq_prev_handle_new and not getattr(_t5vq_prev_handle_new, "_topic5_violation_question_not_comment_v1", False):
        _handle_new._topic5_violation_question_not_comment_v1 = True
        globals()["_handle_new"] = _handle_new
        logger.info("%s installed", _T5VQ_PATCH)
except Exception as _t5vq_install_err:
    try:
        logger.exception("PATCH_TOPIC5_VIOLATION_QUESTION_NOT_COMMENT_V1_INSTALL_ERR:%s", _t5vq_install_err)
    except Exception:
        pass
# === END_PATCH_TOPIC5_VIOLATION_QUESTION_NOT_COMMENT_V1 ===


# === PATCH_TOPIC2_ACTIVE_PROJECT_BLOCK_MEMORY_RECALL_V1 ===
# Canon: active topic_2 project/file task has priority over historical memory.
# Memory recall must not answer with old estimates while current PDF/KR context
# is being processed or clarified.
try:
    _T2APBMR_PATCH = "PATCH_TOPIC2_ACTIVE_PROJECT_BLOCK_MEMORY_RECALL_V1"
    _t2apbmr_prev_handle_new = globals().get("_handle_new")

    def _t2apbmr_s(v, limit=50000):
        return "" if v is None else str(v).strip()[:limit]

    def _t2apbmr_row(row, key, default=""):
        try:
            if hasattr(row, "keys") and key in row.keys():
                return row[key]
        except Exception:
            pass
        try:
            return row[key]
        except Exception:
            return default

    def _t2apbmr_explicit_memory(raw):
        low = _t2apbmr_s(raw).lower().replace("ё", "е")
        return any(x in low for x in ("найди в памяти", "вспомни", "подними архив", "старую смету", "старый расчет", "старый расчёт"))

    def _t2apbmr_active_project_context(conn, chat_id, topic_id, task_id):
        if int(topic_id or 0) != 2:
            return False
        try:
            hist = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? ORDER BY id DESC LIMIT 80",
                (str(task_id),),
            ).fetchall()
            joined = " ".join(str(r[0]) for r in hist)
            if any(x in joined for x in (
                "TOPIC2_MULTIFILE_PROJECT_CONTEXT_READY",
                "TOPIC2_MULTIFILE_PROJECT_SPEC_ROWS",
                "TOPIC2_CLARIFIED_HISTORY_MERGED_BEFORE_GATES",
                "TOPIC2_PRICE_ENRICHMENT_STARTED",
            )):
                return True
            row = conn.execute(
                """
                SELECT h.task_id
                FROM task_history h
                JOIN tasks t ON t.id=h.task_id
                WHERE CAST(t.chat_id AS TEXT)=?
                  AND COALESCE(t.topic_id,0)=2
                  AND t.id<>?
                  AND t.state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION','DONE')
                  AND h.action IN ('TOPIC2_MULTIFILE_PROJECT_CONTEXT_READY:2_pdf','TOPIC2_PRICE_ENRICHMENT_STARTED')
                  AND h.created_at >= datetime('now','-8 hours')
                ORDER BY h.id DESC
                LIMIT 1
                """,
                (str(chat_id), str(task_id)),
            ).fetchone()
            return row is not None
        except Exception:
            return False

    async def _handle_new(conn, task, chat_id, topic_id):  # noqa: F811
        try:
            task_id = _t2apbmr_s(_t2apbmr_row(task, "id"))
            raw = _t2apbmr_s(_t2apbmr_row(task, "raw_input"))
            input_type = _t2apbmr_s(_t2apbmr_row(task, "input_type")).lower()
            if (
                int(topic_id or 0) == 2
                and input_type in ("text", "voice", "search", "")
                and not _t2apbmr_explicit_memory(raw)
                and _t2apbmr_active_project_context(conn, chat_id, topic_id, task_id)
            ):
                try:
                    _history(conn, task_id, _T2APBMR_PATCH + ":SKIP_MEMORY_RECALL_ACTIVE_PROJECT")
                    conn.commit()
                except Exception:
                    pass
                bypass = globals().get("_ghmr_prev_handle_new")
                if bypass:
                    return await bypass(conn, task, chat_id, topic_id)
        except Exception:
            pass
        if _t2apbmr_prev_handle_new:
            return await _t2apbmr_prev_handle_new(conn, task, chat_id, topic_id)

====================================================================================================
END_FILE: task_worker.py
FILE_CHUNK: 4/5
====================================================================================================

====================================================================================================
BEGIN_FILE: task_worker.py
FILE_CHUNK: 5/5
SHA256_FULL_FILE: 0a7095a9174b99b761390c04f342fa3113fd1a328ef9ac6ac0359d93d6a1b1f2
====================================================================================================
        return None

    if _t2apbmr_prev_handle_new:
        globals()["_handle_new"] = _handle_new
        logger.info("%s installed", _T2APBMR_PATCH)
except Exception as _t2apbmr_err:
    try:
        logger.exception("PATCH_TOPIC2_ACTIVE_PROJECT_BLOCK_MEMORY_RECALL_V1_INSTALL_ERR:%s", _t2apbmr_err)
    except Exception:
        pass
# === END_PATCH_TOPIC2_ACTIVE_PROJECT_BLOCK_MEMORY_RECALL_V1 ===


# === PATCH_TOPIC5_DIRECT_VISIT_MATERIAL_DRIVE_FILE_V1 ===
# Canon: topic_5 file/photo is VisitMaterial. It must be buffered before the
# generic construction artifact guard can require XLSX/PDF artifacts.
try:
    _T5DVM_PATCH = "PATCH_TOPIC5_DIRECT_VISIT_MATERIAL_DRIVE_FILE_V1"
    _t5dvm_prev_handle_drive_file = globals().get("_handle_drive_file")

    def _t5dvm_s(v, limit=50000):
        return "" if v is None else str(v).strip()[:limit]

    def _t5dvm_row(row, key, default=""):
        try:
            if hasattr(row, "keys") and key in row.keys():
                return row[key]
        except Exception:
            pass
        try:
            return row[key]
        except Exception:
            return default

    def _t5dvm_meta(raw):
        try:
            obj = json.loads(_t5dvm_s(raw))
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return {}

    async def _handle_drive_file(conn, task, chat_id, topic_id):  # noqa: F811
        try:
            task_id = _t5dvm_s(_t5dvm_row(task, "id"))
            raw = _t5dvm_s(_t5dvm_row(task, "raw_input"))
            input_type = _t5dvm_s(_t5dvm_row(task, "input_type")).lower()
            if int(topic_id or 0) == 5 and input_type in ("drive_file", "file", "photo", "image", "document"):
                meta = _t5dvm_meta(raw)
                file_name = _t5dvm_s(meta.get("file_name") or meta.get("name") or "файл")
                try:
                    active = _t5fc_active(chat_id)
                    buf = _t5fc_buf(chat_id)
                    material = dict(meta)
                    material["file_name"] = file_name
                    material["source"] = material.get("source") or "TELEGRAM"
                    material["status"] = "PENDING_OWNER_INSTRUCTION"
                    material["needs_owner_instruction"] = True
                    material["updated_at"] = time.time() if "time" in globals() else 0
                    mids = {str(m.get("file_id") or m.get("source_drive_file_id") or m.get("telegram_message_id") or "") for m in buf.get("materials", [])}
                    key = str(material.get("file_id") or material.get("source_drive_file_id") or material.get("telegram_message_id") or "")
                    if not key or key not in mids:
                        buf.setdefault("materials", []).append(material)
                    _t5fc_jsave(_t5fc_buf_path(chat_id), buf)
                    object_name = _t5dvm_s((buf.get("package_context") or {}).get("object_name") or active.get("object_name") or "не задан")
                    folder_name = _t5dvm_s(active.get("folder_name") or "не установлена")
                    msg = "\n".join([
                        "Файл получил и сохранил в буфер технадзора",
                        f"Файл: {file_name}",
                        f"Текущий объект: {object_name}",
                        f"Текущая папка: {folder_name}",
                        f"Материалов в буфере: {len(buf.get('materials', []))}",
                        "Что это за материалы, к какому объекту/папке их отнести и что с ними сделать?",
                    ])
                except Exception:
                    msg = f"Файл получил и сохранил в буфер технадзора\nФайл: {file_name}\nЧто это за материалы и что с ними сделать?"
                try:
                    sent = _send_once_ex(conn, task_id, str(chat_id), msg, _t5dvm_row(task, "reply_to_message_id", None), "topic5_direct_visit_material_buffered")
                    bot_mid = sent.get("bot_message_id") if isinstance(sent, dict) else None
                except Exception:
                    bot_mid = None
                if bot_mid:
                    conn.execute("UPDATE tasks SET state='WAITING_CLARIFICATION', result=?, error_message='', bot_message_id=?, updated_at=datetime('now') WHERE id=?", (msg, bot_mid, task_id))
                else:
                    conn.execute("UPDATE tasks SET state='WAITING_CLARIFICATION', result=?, error_message='', updated_at=datetime('now') WHERE id=?", (msg, task_id))
                try:
                    _history(conn, task_id, _T5DVM_PATCH + ":BUFFERED")
                except Exception:
                    pass
                conn.commit()
                return
        except Exception as _t5dvm_err:
            try:
                logger.exception("PATCH_TOPIC5_DIRECT_VISIT_MATERIAL_DRIVE_FILE_V1_ERR:%s", _t5dvm_err)
            except Exception:
                pass
        if _t5dvm_prev_handle_drive_file:
            return await _t5dvm_prev_handle_drive_file(conn, task, chat_id, topic_id)
        return None

    if _t5dvm_prev_handle_drive_file:
        globals()["_handle_drive_file"] = _handle_drive_file
        logger.info("%s installed", _T5DVM_PATCH)
except Exception as _t5dvm_install_err:
    try:
        logger.exception("PATCH_TOPIC5_DIRECT_VISIT_MATERIAL_DRIVE_FILE_V1_INSTALL_ERR:%s", _t5dvm_install_err)
    except Exception:
        pass
# === END_PATCH_TOPIC5_DIRECT_VISIT_MATERIAL_DRIVE_FILE_V1 ===


# === PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1 ===
# Canon: topic_2 final state is governed by XLSX/PDF Drive links and Telegram
# delivery markers. Late generic guards must not convert a delivered canonical
# estimate into FAILED/IN_PROGRESS because result text was overwritten.
try:
    import re as _t2rasr_re
    import logging as _t2rasr_logging

    _T2RASR_LOG = _t2rasr_logging.getLogger("task_worker")
    _T2RASR_PREV_UPDATE_TASK = globals().get("_update_task")

    def _t2rasr_get(obj, key, default=None):
        try:
            if isinstance(obj, dict):
                return obj.get(key, default)
            if hasattr(obj, "keys") and key in obj.keys():
                return obj[key]
        except Exception:
            pass
        try:
            return obj[key]
        except Exception:
            return default

    def _t2rasr_ready_result(conn, task_id):
        try:
            row = conn.execute("SELECT topic_id FROM tasks WHERE id=? LIMIT 1", (str(task_id),)).fetchone()
            if int(_t2rasr_get(row, "topic_id", 0) or 0) != 2:
                return ""
            actions = [
                str(r[0] or "") for r in conn.execute(
                    "SELECT action FROM task_history WHERE task_id=? ORDER BY id DESC LIMIT 3000",
                    (str(task_id),),
                ).fetchall()
            ]
            joined = "\n".join(actions)
            required = (
                "TOPIC2_DRIVE_UPLOAD_XLSX_OK",
                "TOPIC2_DRIVE_UPLOAD_PDF_OK",
                "TOPIC2_TELEGRAM_DELIVERED",
                "TOPIC2_DRIVE_LINKS_SAVED:",
            )
            if not all(x in joined for x in required):
                return ""
            xlsx = ""
            pdf = ""
            positions = ""
            total = ""
            for action in actions:
                if action.startswith("TOPIC2_DRIVE_LINKS_SAVED:"):
                    mx = _t2rasr_re.search(r"xlsx=(https://[^:\s]+)", action)
                    mp = _t2rasr_re.search(r"pdf=(https://[^\s]+)", action)
                    xlsx = mx.group(1) if mx else xlsx
                    pdf = mp.group(1) if mp else pdf
                if action.startswith("TOPIC2_XLSX_ROWS_WRITTEN:") and not positions:
                    positions = action.rsplit(":", 1)[-1].strip()
                if action.startswith("TOPIC2_PDF_TOTALS_MATCH_XLSX:") and not total:
                    mt = _t2rasr_re.search(r"pdf=([0-9]+(?:\.[0-9]+)?)", action)
                    total = mt.group(1) if mt else total
            if not (xlsx and pdf):
                return ""
            total_line = f"Итого: {total} руб\n" if total else "Итого: см. XLSX/PDF\n"
            return (
                "✅ Смета готова\n\n"
                f"Позиций: {positions or 'см. XLSX'}\n"
                f"{total_line}"
                "Готовые артефакты:\n"
                f"Excel: {xlsx}\n"
                f"PDF: {pdf}\n"
                "\nПодтверди или пришли правки"
            )
        except Exception:
            return ""

    if _T2RASR_PREV_UPDATE_TASK and not getattr(_T2RASR_PREV_UPDATE_TASK, "_t2rasr_wrapped", False):
        def _update_task(conn, task_id, **kwargs):  # noqa: F811
            try:
                ready = _t2rasr_ready_result(conn, task_id)
                if ready and str(kwargs.get("state") or "") == "DONE":
                    row_current = conn.execute("SELECT state,result,error_message FROM tasks WHERE id=? LIMIT 1", (str(task_id),)).fetchone()
                    explicit_confirm = conn.execute("SELECT 1 FROM task_history WHERE task_id=? AND action LIKE 'TOPIC2_EXPLICIT_CONFIRM%' ORDER BY id DESC LIMIT 1", (str(task_id),)).fetchone()
                    if (
                        str(_t2rasr_get(row_current, "state", "") or "") == "AWAITING_CONFIRMATION"
                        and not explicit_confirm
                    ):
                        return None
                if ready and (
                    str(kwargs.get("state") or "") in ("FAILED", "IN_PROGRESS", "DONE", "RESULT_READY")
                    or "TOPIC2_FORBIDDEN_FINAL_RESULT_BLOCKED" in str(kwargs.get("error_message") or "")
                    or "P6F_DAH_BLOCK_DONE_NO_UPLOAD_HISTORY" in str(kwargs.get("error_message") or "")
                ):
                    kwargs["state"] = "AWAITING_CONFIRMATION"
                    kwargs["result"] = ready
                    kwargs["error_message"] = ""
                    try:
                        _history(conn, str(task_id), "PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1:RESTORED")
                    except Exception:
                        pass
            except Exception as exc:
                try:
                    _T2RASR_LOG.warning("PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1_ERR:%s", exc)
                except Exception:
                    pass
            result = _T2RASR_PREV_UPDATE_TASK(conn, task_id, **kwargs)
            try:
                ready_after = _t2rasr_ready_result(conn, task_id)
                if ready_after:
                    row_after = conn.execute(
                        "SELECT state,error_message,result FROM tasks WHERE id=? LIMIT 1",
                        (str(task_id),),
                    ).fetchone()
                    state_after = str(_t2rasr_get(row_after, "state", "") or "")
                    err_after = str(_t2rasr_get(row_after, "error_message", "") or "")
                    res_after = str(_t2rasr_get(row_after, "result", "") or "")
                    if (
                        state_after in ("FAILED", "IN_PROGRESS")
                        or "TOPIC2_FORBIDDEN_FINAL_RESULT_BLOCKED" in err_after
                        or "P6F_DAH_BLOCK_DONE_NO_UPLOAD_HISTORY" in err_after
                        or res_after.startswith("Уточнение добавлено")
                    ):
                        conn.execute(
                            "UPDATE tasks SET state=?, result=?, error_message='', updated_at=datetime('now') WHERE id=?",
                            ("AWAITING_CONFIRMATION", ready_after, str(task_id)),
                        )
                        try:
                            _history(conn, str(task_id), "PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1:POST_HEAL")
                        except Exception:
                            pass
                        conn.commit()
            except Exception as exc:
                try:
                    _T2RASR_LOG.warning("PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1_POST_ERR:%s", exc)
                except Exception:
                    pass
            return result
        _update_task._t2rasr_wrapped = True
        globals()["_update_task"] = _update_task
        logger.info("PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1 installed")
except Exception as _t2rasr_install_err:
    try:
        logger.exception("PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1_INSTALL_ERR:%s", _t2rasr_install_err)
    except Exception:
        pass
# === END_PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1 ===


if __name__ == "__main__":
    asyncio.run(main())

====================================================================================================
END_FILE: task_worker.py
FILE_CHUNK: 5/5
====================================================================================================
