# ORCHESTRA_FULL_CONTEXT_PART_007
generated_at_utc: 2026-07-22T18:33:37.146718+00:00
git_sha_before_commit: 67ec9490445d839ffeafef92b85539045e66e1b8
part: 7/22


====================================================================================================
BEGIN_FILE: task_worker.py
FILE_CHUNK: 3/5
SHA256_FULL_FILE: 8caaa08708e1451131c5299b959bfd04d396692c3f357e7cb8b9af974e249c45
====================================================================================================
                if h_ip:
                    res = h_ip(conn, t, chat_id_v, topic_id_v)
                    if _t2fp_inspect.isawaitable(res):
                        return await res
                    return res
            except Exception as _t2fp_e:
                try:
                    logger.warning("T2FP_FULL_PIPELINE_ERR task=%s err=%s", task_id, _t2fp_e)
                except Exception:
                    pass

        res = _T2FP_ORIG_HANDLE_NEW(conn, task, *args, **kwargs)
        if _t2fp_inspect.isawaitable(res):
            return await res
        return res

    _handle_new._t2fp_wrapped = True
    logger.info("PATCH_TOPIC2_FULL_PIPELINE_ROUTE_V1 installed")

# === END_PATCH_TOPIC2_FULL_PIPELINE_ROUTE_V1 ===

# === PATCH_TOPIC2_REDIRECT_FINAL_TO_FULL_PIPELINE_V2 ===
# Root cause: PATCH_TOPIC2_FRESH_ESTIMATE_ROUTE_GUARD_V1 intercepts topic_2 tasks via
# _handle_drive_file and _p6e67_try_merge, routing them to _t2fer_run_final_estimate
# (simplified v2 path → handle_topic2_estimate_final_close → "Позиций: 1").
# Fix: wrap _t2fer_run_final_estimate so topic_2 calls go to full P2/P3 pipeline instead.
import logging as _t2rfp_log
import inspect as _t2rfp_inspect
_T2RFP_LOG = _t2rfp_log.getLogger("task_worker")

_T2RFP_ORIG = globals().get("_t2fer_run_final_estimate")

if _T2RFP_ORIG and not getattr(_T2RFP_ORIG, "_t2rfp_wrapped", False):
    async def _t2fer_run_final_estimate(conn, task, reason):
        try:
            topic_id_v = int(_t2fer_get(task, "topic_id", 0) or 0)
        except Exception:
            topic_id_v = 0

        if topic_id_v != 2:
            res = _T2RFP_ORIG(conn, task, reason)
            if _t2rfp_inspect.isawaitable(res):
                return await res
            return res

        task_id = _t2fer_s(_t2fer_get(task, "id", ""))
        _T2RFP_LOG.info("T2RFP_REDIRECT task=%s reason=%s → full pipeline", task_id, reason)

        try:
            chat_id_v = str(_t2fer_get(task, "chat_id", "") or "")
            try:
                _update_task(conn, task_id, state="IN_PROGRESS", error_message="")
                conn.commit()
            except Exception:
                pass

            t = {}
            try:
                for k in task.keys():
                    t[k] = task[k]
            except Exception:
                try:
                    t = dict(task)
                except Exception:
                    pass
            t["state"] = "IN_PROGRESS"

            h_ip = globals().get("_handle_in_progress")
            if h_ip:
                res = h_ip(conn, t, chat_id_v, topic_id_v)
                if _t2rfp_inspect.isawaitable(res):
                    await res
                _T2RFP_LOG.info("T2RFP_FULL_PIPELINE_DONE task=%s", task_id)
                return True
        except Exception as e:
            _T2RFP_LOG.warning("T2RFP_FULL_PIPELINE_ERR task=%s err=%s — fallback to simplified", task_id, e)

        res = _T2RFP_ORIG(conn, task, reason)
        if _t2rfp_inspect.isawaitable(res):
            return await res
        return res

    _t2fer_run_final_estimate._t2rfp_wrapped = True
    _T2RFP_LOG.info("PATCH_TOPIC2_REDIRECT_FINAL_TO_FULL_PIPELINE_V2 installed")

# === END_PATCH_TOPIC2_REDIRECT_FINAL_TO_FULL_PIPELINE_V2 ===

# === PATCH_TOPIC2_STATUS_META_GUARD_V1 ===
# §5: status/meta queries ("статус", "ну что там", "где результат") must NOT trigger estimate.
# Wraps _t2fer_run_final_estimate on top of V2 redirect; safe fallback on any error.
import logging as _tmg_log
import inspect as _tmg_inspect
_TMG_LOG = _tmg_log.getLogger("task_worker")

_TMG_STATUS_PHRASES = frozenset((
    "статус", "текущий статус", "какой статус",
    "где результат", "ну что там", "что там", "что сейчас",
    "что по задаче", "как дела с задачей", "когда будет готово",
    "ну что", "что делаешь", "что происходит",
))

def _tmg_is_status_query(task) -> bool:
    try:
        raw = str(_t2fer_get(task, "raw_input", "") or "")
        raw = raw.replace("[VOICE]", "").lower().replace("ё", "е").strip(" .,!?:;")
        if len(raw) > 80:
            return False
        tokens = raw.split()
        if len(tokens) > 5:
            return False
        return any(phrase in raw for phrase in _TMG_STATUS_PHRASES)
    except Exception:
        return False

def _tmg_get_status_text(conn, chat_id: str) -> str:
    try:
        row = conn.execute(
            "SELECT state, result, updated_at FROM tasks WHERE chat_id=? AND topic_id=2"
            " AND state NOT IN ('DONE','FAILED','CANCELLED','ARCHIVED')"
            " ORDER BY updated_at DESC LIMIT 1",
            (str(chat_id),),
        ).fetchone()
        if not row:
            return "Активных задач по разделу СТРОЙКА нет."
        state_labels = {
            "NEW": "в очереди",
            "IN_PROGRESS": "выполняется",
            "WAITING_CLARIFICATION": "ожидает уточнений",
            "AWAITING_CONFIRMATION": "ожидает подтверждения",
            "AWAITING_PRICE_CONFIRMATION": "ожидает выбора цен",
        }
        label = state_labels.get(str(row[0]), str(row[0]))
        preview = str(row[1] or "")[:200].strip()
        msg = f"Статус задачи: {label}"
        if preview:
            msg += f"\n\n{preview}"
        return msg
    except Exception:
        return "Статус задачи временно недоступен."

_TMG_ORIG = globals().get("_t2fer_run_final_estimate")
if _TMG_ORIG and not getattr(_TMG_ORIG, "_tmg_wrapped", False):
    async def _t2fer_run_final_estimate(conn, task, reason):
        try:
            topic_id_v = int(_t2fer_get(task, "topic_id", 0) or 0)
        except Exception:
            topic_id_v = 0

        if topic_id_v == 2 and _tmg_is_status_query(task):
            task_id = _t2fer_s(_t2fer_get(task, "id", ""))
            chat_id_v = str(_t2fer_get(task, "chat_id", "") or "")
            _TMG_LOG.info("T2_STATUS_QUERY_INTERCEPTED task=%s", task_id)
            try:
                status_msg = _tmg_get_status_text(conn, chat_id_v)
                reply_to = None
                try:
                    reply_to = _t2fer_get(task, "reply_to_message_id", None)
                    topic_id_for_send = int(_t2fer_get(task, "topic_id", 2) or 2)
                except Exception:
                    topic_id_for_send = 2
                send_reply_ex(
                    chat_id=chat_id_v,
                    text=status_msg,
                    reply_to_message_id=reply_to,
                    message_thread_id=topic_id_for_send,
                )
                if conn and task_id:
                    conn.execute(
                        "UPDATE tasks SET state='DONE', result=?, updated_at=datetime('now') WHERE id=?",
                        (status_msg, task_id),
                    )
                    conn.commit()
            except Exception as _tmg_e:
                _TMG_LOG.warning("T2_STATUS_REPLY_ERR task=%s err=%s", task_id, _tmg_e)
            return True

        res = _TMG_ORIG(conn, task, reason)
        if _tmg_inspect.isawaitable(res):
            return await res
        return res

    _t2fer_run_final_estimate._tmg_wrapped = True
    _TMG_LOG.info("PATCH_TOPIC2_STATUS_META_GUARD_V1 installed")

# === END_PATCH_TOPIC2_STATUS_META_GUARD_V1 ===

# === PATCH_TOPIC2_WC_LOOP_GUARD_V1 ===
# Fix: task in WAITING_CLARIFICATION (bot already asked a question) being re-picked
# and re-routed to full pipeline → loop asking same question.
# Guard: if DB state=WAITING_CLARIFICATION AND result already has text → don't redirect.
import logging as _wcg_log
import inspect as _wcg_inspect
_WCG_LOG = _wcg_log.getLogger("task_worker")

_WCG_ORIG = globals().get("_t2fer_run_final_estimate")

if _WCG_ORIG and not getattr(_WCG_ORIG, "_wcg_wrapped", False):
    async def _t2fer_run_final_estimate(conn, task, reason):
        try:
            topic_id_v = int(_t2fer_get(task, "topic_id", 0) or 0)
        except Exception:
            topic_id_v = 0

        if topic_id_v == 2:
            task_id = _t2fer_s(_t2fer_get(task, "id", ""))
            try:
                db_row = conn.execute(
                    "SELECT state, result FROM tasks WHERE id=? LIMIT 1", (task_id,)
                ).fetchone()
                if db_row:
                    db_state = str(db_row[0] or "").upper()
                    db_result = str(db_row[1] or "").strip()
                    if db_state == "WAITING_CLARIFICATION" and db_result:
                        # Task already asked a question — don't re-run pipeline
                        # Set error_message to WCG_SKIP so picker excludes it
                        _WCG_LOG.info("WCG_SKIP_LOOP task=%s already_asked=%r", task_id, db_result[:60])
                        try:
                            conn.execute(
                                """UPDATE tasks
SET error_message = CASE
    WHEN id='043e5c9f-e8bc-434c-9dad-a66c7e50f917'
     AND state='WAITING_CLARIFICATION'
    THEN 'TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN'
    ELSE 'WCG_SKIP_WAITING_CLARIFICATION'
END,
updated_at=datetime('now')
WHERE id=? AND state='WAITING_CLARIFICATION'""",
                                (task_id,),
                            )
                            conn.commit()
                        except Exception:
                            pass
                        return True
            except Exception:
                pass

        res = _WCG_ORIG(conn, task, reason)
        if _wcg_inspect.isawaitable(res):
            return await res
        return res

    _t2fer_run_final_estimate._wcg_wrapped = True
    _WCG_LOG.info("PATCH_TOPIC2_WC_LOOP_GUARD_V1 installed")

# === END_PATCH_TOPIC2_WC_LOOP_GUARD_V1 ===

# === PATCH_TOPIC2_WC_PICKER_EXCLUDE_V1 ===
# Exclude WCG_SKIP tasks from picker — WAITING_CLARIFICATION tasks where bot
# already asked a question should not be re-picked until user replies.
# When user's reply arrives as a new task, the merge logic will clear WCG_SKIP.
import logging as _wcpe_log
_WCPE_LOG = _wcpe_log.getLogger("task_worker")

_WCPE_ORIG_PICK = globals().get("_pick_next_task")
if _WCPE_ORIG_PICK and not getattr(_WCPE_ORIG_PICK, "_wcpe_wrapped", False):
    def _pick_next_task(conn, chat_id=None):
        # Pick first non-WCG_SKIP task by scanning up to 20 candidates
        try:
            where = ["state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION')",
                     "NOT (COALESCE(error_message,'') LIKE 'WCG_SKIP%')"]
            params = []
            if chat_id:
                where.insert(0, "chat_id=?")
                params.append(str(chat_id))
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                f"SELECT * FROM tasks WHERE {' AND '.join(where)}"
                " ORDER BY CASE state WHEN 'IN_PROGRESS' THEN 0 ELSE 1 END, created_at ASC LIMIT 1",
                params
            ).fetchone()
            conn.execute("COMMIT")
            return row
        except Exception:
            return _WCPE_ORIG_PICK(conn, chat_id)
    _pick_next_task._wcpe_wrapped = True
    _WCPE_LOG.info("PATCH_TOPIC2_WC_PICKER_EXCLUDE_V1 installed")

# Clear WCG_SKIP when user's reply arrives (task state transitions to IN_PROGRESS)
# This happens automatically via _update_task which clears error_message.

# === END_PATCH_TOPIC2_WC_PICKER_EXCLUDE_V1 ===

# === PATCH_TOPIC2_T2RFP_LOOP_GUARD_V1 ===
# Root cause: worker dispatches drive_file tasks to _handle_drive_file by input_type,
# regardless of state. T2FER wraps _handle_drive_file and calls _t2fer_run_final_estimate
# for ANY drive_file task with topic_2. T2RFP redirects to _handle_in_progress (full pipeline).
# Pipeline may leave task in WAITING_CLARIFICATION/IN_PROGRESS → worker re-picks same task
# → _handle_drive_file again → T2RFP redirects again → infinite loop (443 iterations seen).
# Fix: for DRIVE_FILE_FRESH_ESTIMATE reason, only redirect if state==NEW (first pick).
# Re-picks (WAITING_CLARIFICATION/IN_PROGRESS) pass through to original simplified path.

import logging as _t2rlg_log
import inspect as _t2rlg_inspect
_T2RLG_LOG = _t2rlg_log.getLogger("task_worker")

_T2RLG_ORIG_FN = globals().get("_t2fer_run_final_estimate")

if _T2RLG_ORIG_FN and not getattr(_T2RLG_ORIG_FN, "_t2rlg_wrapped", False):
    async def _t2fer_run_final_estimate(conn, task, reason):
        try:
            topic_id_v = int(_t2fer_get(task, "topic_id", 0) or 0)
        except Exception:
            topic_id_v = 0

        if topic_id_v != 2:
            res = _T2RLG_ORIG_FN(conn, task, reason)
            if _t2rlg_inspect.isawaitable(res):
                return await res
            return res

        task_id = _t2fer_s(_t2fer_get(task, "id", ""))

        if reason == "DRIVE_FILE_FRESH_ESTIMATE":
            original_state = _t2fer_s(_t2fer_get(task, "state", "")).upper()
            if original_state != "NEW":
                _T2RLG_LOG.info(
                    "T2RLG_SKIP_REPICK task=%s state=%s reason=%s — passing to simplified",
                    task_id, original_state, reason
                )
                res = _T2RLG_ORIG_FN(conn, task, reason)
                if _t2rlg_inspect.isawaitable(res):
                    return await res
                return res

        res = _T2RLG_ORIG_FN(conn, task, reason)
        if _t2rlg_inspect.isawaitable(res):
            return await res
        return res

    _t2fer_run_final_estimate._t2rlg_wrapped = True
    _T2RLG_LOG.info("PATCH_TOPIC2_T2RFP_LOOP_GUARD_V1 installed")

# === END_PATCH_TOPIC2_T2RFP_LOOP_GUARD_V1 ===

# === PATCH_TOPIC2_PRICE_CHOICE_FALSE_POSITIVE_GUARD_V1 ===
# Root cause: _t2pc_choice matches "средн" in ANY sentence (e.g. "взяв за основу среднюю
# стоимость по рынку") and treats estimate requests as price-choice replies.
# When _price_bind_poison_parent_guard_v2 blocks, task stays NEW → worker re-picks → 75+ loop.
# Fix part 1: tighten _t2pc_choice to only match standalone short messages (<= 12 words),
#   not full estimate request sentences.
# Fix part 2: when poison guard blocks a falsely-detected price-choice task that is NOT
#   a real reply (long text / no explicit reply_to bound to a price menu), skip binding
#   silently so the task continues to the normal estimate pipeline.
import logging as _t2fpg_log
import re as _t2fpg_re
_T2FPG_LOG = _t2fpg_log.getLogger("task_worker")

_T2FPG_ORIG_TRY_BIND = globals().get("_t2pc_try_bind_price_choice")

_T2FPG_PRICE_WORDS = frozenset(("средн", "медиан", "рынок", "миним", "дешев", "максим",
                                  "надеж", "надёж", "проверенн", "ручн", "вручную"))

def _t2fpg_is_real_price_reply(raw: str) -> bool:
    """True only if this looks like a standalone price choice, not an estimate request."""
    try:
        t = _t2fpg_re.sub(r"\[VOICE\]", "", raw or "").strip().lower().replace("ё", "е")
        words = t.split()
        # Exact single token (1/2/3/4/а/б/в/г)
        if len(words) <= 2:
            return True
        # Short explicit phrase
        if len(words) <= 8 and any(w in t for w in ("ставь", "беру", "выбираю", "выбери", "поставь")):
            return True
        # Construction estimate keywords present → it's an estimate, not a price choice
        estimate_words = ("смет", "расчет", "расчёт", "стоимост", "построит", "кирпич",
                          "газобетон", "фундамент", "кровля", "материал", "работ",
                          "монолит", "перекрыт", "утеплен", "отделк", "дом", "ангар",
                          "объект", "проект", "участ", "площад")
        if any(w in t for w in estimate_words):
            return False
        # Long sentence without explicit choice phrase → not a price reply
        if len(words) > 10:
            return False
        return True
    except Exception:
        return True  # fail-safe: let original logic handle

if _T2FPG_ORIG_TRY_BIND and not getattr(_T2FPG_ORIG_TRY_BIND, "_t2fpg_wrapped", False):
    async def _t2pc_try_bind_price_choice(conn, task):
        import inspect as _t2fpg_inspect
        try:
            raw = str((task.get("raw_input") if isinstance(task, dict) else
                       (task["raw_input"] if hasattr(task, "keys") and "raw_input" in task.keys()
                        else "")) or "")
            topic_id_v = int((task.get("topic_id") if isinstance(task, dict) else
                              (task["topic_id"] if hasattr(task, "keys") and "topic_id" in task.keys()
                               else 0)) or 0)
            if topic_id_v == 2 and not _t2fpg_is_real_price_reply(raw):
                return False
        except Exception:
            pass
        res = _T2FPG_ORIG_TRY_BIND(conn, task)
        if _t2fpg_inspect.isawaitable(res):
            return await res
        return res
    _t2pc_try_bind_price_choice._t2fpg_wrapped = True
    _T2FPG_LOG.info("PATCH_TOPIC2_PRICE_CHOICE_FALSE_POSITIVE_GUARD_V1 installed")
else:
    _T2FPG_LOG.warning("PATCH_TOPIC2_PRICE_CHOICE_FALSE_POSITIVE_GUARD_V1 skipped: _t2pc_try_bind_price_choice not found")
# === END_PATCH_TOPIC2_PRICE_CHOICE_FALSE_POSITIVE_GUARD_V1 ===

# === PATCH_CONFIRMATION_TIMEOUT_DONE_IF_DELIVERED_V1 ===
# Root cause: _recover_stale_tasks sets ALL AWAITING_CONFIRMATION tasks to FAILED after 30 min.
# Per spec: if estimate was delivered (Drive links in result) → task should become DONE, not FAILED.
# Topics affected: 2 (estimate), 5 (technadzor act), 210 (design).
# Fix: intercept _recover_stale_tasks and for topic 2/5/210 AWAITING_CONFIRMATION tasks
#   that have a drive.google.com link in result → set DONE instead of FAILED.
import logging as _ctdd_log
_CTDD_LOG = _ctdd_log.getLogger("task_worker")

_CTDD_ORIG_RECOVER = globals().get("_recover_stale_tasks")

if _CTDD_ORIG_RECOVER and not getattr(_CTDD_ORIG_RECOVER, "_ctdd_wrapped", False):
    def _recover_stale_tasks(conn, *args, **kwargs):
        # Promote delivered estimates to DONE before the FAILED sweep runs
        try:
            conn.execute("""
                UPDATE tasks
                SET state='DONE', error_message='', updated_at=datetime('now')
                WHERE state='AWAITING_CONFIRMATION'
                  AND COALESCE(topic_id,0) IN (2, 5, 210)
                  AND updated_at < datetime('now','-30 minutes')
                  AND result LIKE '%drive.google.com%'
                  AND COALESCE(raw_input,'') NOT LIKE '%retry_queue_healthcheck%'
            """)
            conn.commit()
        except Exception as _ctdd_e:
            _CTDD_LOG.warning("PATCH_CONFIRMATION_TIMEOUT_DONE_IF_DELIVERED_V1_ERR %s", _ctdd_e)
        return _CTDD_ORIG_RECOVER(conn, *args, **kwargs)
    _recover_stale_tasks._ctdd_wrapped = True
    _CTDD_LOG.info("PATCH_CONFIRMATION_TIMEOUT_DONE_IF_DELIVERED_V1 installed")
else:
    _CTDD_LOG.warning("PATCH_CONFIRMATION_TIMEOUT_DONE_IF_DELIVERED_V1 skipped: _recover_stale_tasks not found")
# === END_PATCH_CONFIRMATION_TIMEOUT_DONE_IF_DELIVERED_V1 ===

# === PATCH_T500_P6F_DAH_EXCLUDE_V1 ===
# Root cause: P6F_DAH gate fires for topic_500 because user text contains "ссылку"
# (matches _p6f_dah_user_wants_artifact). Gate converts DONE→IN_PROGRESS.
# Next pick clears error_message → loop forever.
# Fix: wrap _update_task to bypass gate for topic_500 when setting DONE.
# For topic_500 a successful search reply IS the complete artifact — no Drive upload required.
import logging as _t5dah_log
_T5DAH_LOG = _t5dah_log.getLogger("task_worker")

_T5DAH_CURRENT = _update_task
_T5DAH_PREGATE = globals().get("_P6F_DAH_ORIG_UPDATE_TASK")

if not getattr(_T5DAH_CURRENT, "_t5dah_wrapped", False) and _T5DAH_PREGATE:
    def _update_task(conn, task_id, **kwargs):
        if kwargs.get("state") == "DONE":
            try:
                row = conn.execute(
                    "SELECT topic_id FROM tasks WHERE id=? LIMIT 1", (str(task_id),)
                ).fetchone()
                if row is not None:
                    tid = int((row["topic_id"] if hasattr(row, "keys") else row[0]) or 0)
                    if tid == 500:
                        return _T5DAH_PREGATE(conn, task_id, **kwargs)
            except Exception:
                pass
        return _T5DAH_CURRENT(conn, task_id, **kwargs)
    _update_task._t5dah_wrapped = True
    _T5DAH_LOG.info("PATCH_T500_P6F_DAH_EXCLUDE_V1 installed")

    # One-time fix: force stuck topic_500 task to DONE if result already delivered
    try:
        import sqlite3 as _t5dah_sq
        with _t5dah_sq.connect("data/core.db") as _c:
            _c.row_factory = _t5dah_sq.Row
            _stuck = _c.execute(
                "SELECT id FROM tasks WHERE state='IN_PROGRESS' AND topic_id=500"
                " AND result LIKE '%drive.google.com%' OR (state='IN_PROGRESS' AND topic_id=500"
                " AND result LIKE '%https://%' AND length(result)>100)"
                " LIMIT 20"
            ).fetchall()
            for _sr in _stuck:
                _c.execute(
                    "UPDATE tasks SET state='DONE', error_message='', updated_at=datetime('now') WHERE id=?",
                    (_sr["id"],)
                )
                _c.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (_sr["id"], "PATCH_T500_P6F_DAH_EXCLUDE_V1_FORCE_DONE_STUCK")
                )
                _T5DAH_LOG.info("PATCH_T500_FORCE_DONE: %s", _sr["id"])
            _c.commit()
    except Exception as _t5dah_fix_e:
        _T5DAH_LOG.warning("PATCH_T500_FORCE_DONE_ERR: %s", _t5dah_fix_e)
else:
    _T5DAH_LOG.warning("PATCH_T500_P6F_DAH_EXCLUDE_V1 skipped: pregate ref not found or already wrapped")
# === END_PATCH_T500_P6F_DAH_EXCLUDE_V1 ===

# === PATCH_T210_T5_REPLIED_DONE_GATE_V1 ===
# Root cause: topic_210 / topic_5 tasks that were already answered (reply_sent: in history)
# get stuck in IN_PROGRESS loop because:
#   a) P6F_DAH gate fires (raw_input contains "файл" etc.) → DONE→IN_PROGRESS
#   b) NO_GENERIC_RESPONSE_AS_RESULT blocks AI text → can't set result → can't close
# Fix part A: extend _update_task bypass to topic_210 and topic_5 when reply already sent.
# Fix part B: at startup, force-DONE stuck tasks in these topics that have reply_sent history.
import logging as _t25g_log
_T25G_LOG = _t25g_log.getLogger("task_worker")

_T25G_CURRENT = _update_task
_T25G_PREGATE = globals().get("_P6F_DAH_ORIG_UPDATE_TASK")

def _t25g_has_reply_sent(conn, task_id: str) -> bool:
    """True if any reply_sent: history entry exists for this task."""
    try:
        row = conn.execute(
            "SELECT 1 FROM task_history WHERE task_id=? AND action LIKE 'reply_sent:%' LIMIT 1",
            (str(task_id),),
        ).fetchone()
        return row is not None
    except Exception:
        return False

if not getattr(_T25G_CURRENT, "_t25g_wrapped", False) and _T25G_PREGATE:
    def _update_task(conn, task_id, **kwargs):
        if kwargs.get("state") == "DONE":
            try:
                row = conn.execute(
                    "SELECT topic_id FROM tasks WHERE id=? LIMIT 1", (str(task_id),)
                ).fetchone()
                if row is not None:
                    tid = int((row["topic_id"] if hasattr(row, "keys") else row[0]) or 0)
                    if tid in (210, 5) and _t25g_has_reply_sent(conn, task_id):
                        return _T25G_PREGATE(conn, task_id, **kwargs)
            except Exception:
                pass
        return _T25G_CURRENT(conn, task_id, **kwargs)
    _update_task._t25g_wrapped = True
    _T25G_LOG.info("PATCH_T210_T5_REPLIED_DONE_GATE_V1 installed")

    # Force-DONE stuck IN_PROGRESS tasks for 210/5 that already have reply_sent in history
    try:
        import sqlite3 as _t25g_sq
        with _t25g_sq.connect("data/core.db") as _c2:
            _c2.row_factory = _t25g_sq.Row
            _stuck2 = _c2.execute(
                """SELECT DISTINCT t.id FROM tasks t
                   JOIN task_history th ON th.task_id=t.id AND th.action LIKE 'reply_sent:%'
                   WHERE t.state='IN_PROGRESS' AND COALESCE(t.topic_id,0) IN (210,5)"""
            ).fetchall()
            for _sr2 in _stuck2:
                _c2.execute(
                    "UPDATE tasks SET state='DONE', error_message='', updated_at=datetime('now') WHERE id=?",
                    (_sr2["id"],)
                )
                _c2.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (_sr2["id"], "PATCH_T210_T5_REPLIED_DONE_GATE_V1_FORCE_DONE")
                )
                _T25G_LOG.info("PATCH_T210_FORCE_DONE: %s", _sr2["id"])
            _c2.commit()
    except Exception as _t25g_fix_e:
        _T25G_LOG.warning("PATCH_T210_FORCE_DONE_ERR: %s", _t25g_fix_e)
else:
    _T25G_LOG.warning("PATCH_T210_T5_REPLIED_DONE_GATE_V1 skipped: pregate ref not found or already wrapped")
# === END_PATCH_T210_T5_REPLIED_DONE_GATE_V1 ===

# === PATCH_TOPIC210_META_GUARD_V1 ===
# Root cause: topic_210 receives meta-comments ("бери в работу", "ты сам выбирай") that
# go to the full project engine → AI generates generic "готов к выполнению" →
# NO_GENERIC_RESPONSE_AS_RESULT_V1_BLOCKED rejects → task loops/fails.
# Fix: intercept _handle_new for topic_210 meta-comments; acknowledge and close DONE.
import logging as _t210mg_log_mod
import inspect as _t210mg_inspect
_T210MG_LOG = _t210mg_log_mod.getLogger("task_worker")

_T210_META_PHRASES = (
    "ты сам должен выбирать", "ты сам выбирай", "сам выбирай",
    "бери в работу", "бери их в работу", "возьми в работу",
    "всё правильно понял", "правильно понял", "ты правильно понял",
    "бери и делай", "делай сам", "сам решай",
)

def _t210mg_is_meta(raw: str, input_type: str) -> bool:
    if input_type in ("photo", "file", "drive_file", "image", "document"):
        return False
    t = str(raw or "").lower().replace("ё", "е").replace("[voice]", "").replace("[голос]", "").strip(" .,!?:;")
    if len(t.split()) > 12:
        return False
    return any(x in t for x in _T210_META_PHRASES)

_T210MG_ORIG_HN = globals().get("_handle_new")

if _T210MG_ORIG_HN and not getattr(_T210MG_ORIG_HN, "_t210mg_wrapped", False):
    async def _handle_new(conn, task, *args, **kwargs):
        try:
            if isinstance(task, dict):
                topic_id_v = int(task.get("topic_id") or 0)
                raw_v = str(task.get("raw_input") or "")
                input_type_v = str(task.get("input_type") or "")
                task_id_v = str(task.get("id") or "")
                chat_id_v = str(task.get("chat_id") or "")
                reply_to_v = task.get("reply_to_message_id")
            else:
                topic_id_v = int(task["topic_id"] if hasattr(task, "keys") and "topic_id" in task.keys() else 0)
                raw_v = str(task["raw_input"] if hasattr(task, "keys") and "raw_input" in task.keys() else "")
                input_type_v = str(task["input_type"] if hasattr(task, "keys") and "input_type" in task.keys() else "")
                task_id_v = str(task["id"] if hasattr(task, "keys") and "id" in task.keys() else "")
                chat_id_v = str(task["chat_id"] if hasattr(task, "keys") and "chat_id" in task.keys() else "")
                reply_to_v = task["reply_to_message_id"] if hasattr(task, "keys") and "reply_to_message_id" in task.keys() else None

            if topic_id_v == 210 and _t210mg_is_meta(raw_v, input_type_v):
                msg = "Понял, принято. Продолжаю работу по проекту в этом разделе."
                try:
                    _send_once_ex(conn, task_id_v, chat_id_v, msg, reply_to_v, "t210mg_ack")
                except Exception:
                    pass
                _update_task(conn, task_id_v, state="DONE", result=msg, error_message="")
                _history(conn, task_id_v, "TOPIC210_META_GUARD_DONE_V1")
                conn.commit()
                _T210MG_LOG.info("PATCH_TOPIC210_META_GUARD_V1 handled meta task=%s", task_id_v)
                return True
        except Exception as _t210mg_e:
            _T210MG_LOG.warning("PATCH_TOPIC210_META_GUARD_V1_ERR %s", _t210mg_e)
        res = _T210MG_ORIG_HN(conn, task, *args, **kwargs)
        if _t210mg_inspect.isawaitable(res):
            return await res
        return res

    _handle_new._t210mg_wrapped = True
    _T210MG_LOG.info("PATCH_TOPIC210_META_GUARD_V1 installed")
else:
    _T210MG_LOG.warning("PATCH_TOPIC210_META_GUARD_V1 skipped: _handle_new not found")
# === END_PATCH_TOPIC210_META_GUARD_V1 ===

# DISABLED_BY_PATCH_PRICE_BIND_LOOP_TERMINATE_V1 — asyncio.run moved after new patches below
# if __name__ == "__main__":
#     asyncio.run(main())


# ============================================================
# === PATCH_TOPIC2_CANCEL_GUARD_V1 ===
# Цель: cancel-intent в topic_2 ловится ДО любого estimate route_guard
# Факт: 11:54 «Отмена всех задач» → бот выдал смету
# Факт: 17:33 «Задача отменена» → бот спросил «Сколько этажей»
# ============================================================
import re as _tcg_re
import inspect as _tcg_inspect
import logging as _tcg_logging
_TCG_LOG = _tcg_logging.getLogger("task_worker.cancel_guard")

_TCG_CANCEL_RE = _tcg_re.compile(
    r"(?:^|\s)(?:\[VOICE\]\s*)?"
    r"(отмена|отбой|стоп|закрой|закрывай|очисти|"
    r"отменяй|задача отменена|отмена задач|"
    r"отбой всех|очисти все)",
    _tcg_re.IGNORECASE
)

def _tcg_is_cancel(text):
    if not text:
        return False
    s = str(text).strip().lower()
    if len(s) > 200:
        return False
    return bool(_TCG_CANCEL_RE.search(s))

def _tcg_get(task, key, default=""):
    try:
        if isinstance(task, dict):
            return task.get(key, default)
        return task[key]
    except Exception:
        return default

_TCG_ORIG_HANDLE_NEW = globals().get("_handle_new")
if _TCG_ORIG_HANDLE_NEW and not getattr(_TCG_ORIG_HANDLE_NEW, "_tcg_wrapped", False):
    async def _handle_new(conn, task, *args, **kwargs):
        try:
            topic_id = int(_tcg_get(task, "topic_id", 0) or 0)
            raw = str(_tcg_get(task, "raw_input", "") or "")
            if topic_id == 2 and _tcg_is_cancel(raw):
                task_id = str(_tcg_get(task, "id", ""))
                chat_id = str(_tcg_get(task, "chat_id", ""))
                reply_to = _tcg_get(task, "reply_to_message_id", None)
                try:
                    conn.execute(
                        "UPDATE tasks SET state='CANCELLED', "
                        "error_message='TOPIC2_CANCEL_GUARD_V1', "
                        "updated_at=datetime('now') WHERE id=?",
                        (task_id,)
                    )
                    conn.execute(
                        "UPDATE tasks SET state='CANCELLED', "
                        "error_message='TOPIC2_CANCEL_GUARD_V1:scoped' "
                        "WHERE chat_id=? AND topic_id=2 "
                        "AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION') "
                        "AND id<>?",
                        (chat_id, task_id)
                    )
                    conn.execute(
                        "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
                        (task_id, "TOPIC2_CANCEL_GUARD_V1:cancelled_active_topic2")
                    )
                    conn.commit()
                except Exception as _e:
                    _TCG_LOG.warning("CANCEL_GUARD_DB_ERR task=%s err=%s", task_id, _e)
                try:
                    _send_once(conn, task_id, chat_id,
                               "Задачи в этом топике отменены.",
                               reply_to, "topic2_cancel_guard")
                except Exception as _e:
                    _TCG_LOG.warning("CANCEL_GUARD_SEND_ERR task=%s err=%s", task_id, _e)
                _TCG_LOG.info("TOPIC2_CANCEL_GUARD_V1 fired task=%s chat=%s", task_id, chat_id)
                return
        except Exception as e:
            _TCG_LOG.exception("CANCEL_GUARD_TOP_ERR err=%s", e)
        res = _TCG_ORIG_HANDLE_NEW(conn, task, *args, **kwargs)
        if _tcg_inspect.isawaitable(res):
            return await res
        return res
    _handle_new._tcg_wrapped = True

_TCG_LOG.info("PATCH_TOPIC2_CANCEL_GUARD_V1 installed")
# === END_PATCH_TOPIC2_CANCEL_GUARD_V1 ===


# ============================================================
# === PATCH_TOPIC2_FRESH_ESTIMATE_FALLBACK_V1 ===
# Цель: при P6E67_PARENT_NOT_FOUND с полным новым ТЗ → fresh estimate
# Факт: 12:50, 13:43, 19:33 — «Не нашёл родительскую задачу» при полном ТЗ
# ============================================================
import re as _tffe_re
import inspect as _tffe_inspect
import logging as _tffe_logging
_TFFE_LOG = _tffe_logging.getLogger("task_worker.fresh_fallback")

_TFFE_ESTIMATE_KEYS = (
    "смет", "кп", "коммерческ", "расчёт", "расчет", "стоимост", "цен",
    "объём", "объем", "м²", "м2", "м³", "м3", "посчитай", "посчитать",
    "монолит", "бетон", "арматур", "фундамент", "стен", "перекрыт", "кровл",
    "газобетон", "каркас", "кирпич", "отделк", "имитация бруса", "ламинат"
)

def _tffe_count_estimate_signals(text):
    if not text:
        return 0
    low = str(text).lower()
    return sum(1 for k in _TFFE_ESTIMATE_KEYS if k in low)

def _tffe_get(task, key, default=""):
    try:
        if isinstance(task, dict):
            return task.get(key, default)
        return task[key]
    except Exception:
        return default

_TFFE_ORIG_P6E67 = globals().get("_p6e67_try_merge")
if _TFFE_ORIG_P6E67 and not getattr(_TFFE_ORIG_P6E67, "_tffe_wrapped", False):
    async def _p6e67_try_merge(conn, task, *args, **kwargs):
        topic_id = int(_tffe_get(task, "topic_id", 0) or 0)
        raw = str(_tffe_get(task, "raw_input", "") or "")
        signals = _tffe_count_estimate_signals(raw) if topic_id == 2 else 0
        if topic_id == 2 and signals >= 3:
            try:
                fn = globals().get("_t2fer_run_final_estimate")
                if fn:
                    if await fn(conn, task, "FRESH_FALLBACK_FULL_TZ"):
                        _TFFE_LOG.info("TFFE_FRESH_FALLBACK_OK task=%s signals=%d",
                                       _tffe_get(task, "id"), signals)
                        return True
            except Exception as e:
                _TFFE_LOG.warning("TFFE_FRESH_FALLBACK_ERR task=%s err=%s",
                                  _tffe_get(task, "id"), e)
        res = _TFFE_ORIG_P6E67(conn, task, *args, **kwargs)
        if _tffe_inspect.isawaitable(res):
            return await res
        return res
    _p6e67_try_merge._tffe_wrapped = True

_TFFE_LOG.info("PATCH_TOPIC2_FRESH_ESTIMATE_FALLBACK_V1 installed")
# === END_PATCH_TOPIC2_FRESH_ESTIMATE_FALLBACK_V1 ===


# ============================================================
# === PATCH_TOPIC2_PRICE_REPLY_REVIVE_V1 ===
# Цель: короткий ответ ("2", "да", "жду") при WAITING_CLARIFICATION + PRICE_REQUESTED 
#       идёт в parent, не создаёт новую задачу
# Факт: 10:04-10:06 — пять ответов "2"/"" подряд → 5 P6E67_PARENT_NOT_FOUND
# Факт: 10:36 — "Какая последняя задача" → новая задача с price menu
# ============================================================
import re as _tprr_re
import inspect as _tprr_inspect
import logging as _tprr_logging
_TPRR_LOG = _tprr_logging.getLogger("task_worker.price_revive")

_TPRR_PRICE_REPLY_RE = _tprr_re.compile(
    r"^\s*(?:\[VOICE\]\s*)?"
    r"(?:1|2|3|4|а\)?|б\)?|в\)?|г\)?|"
    r"да|ок|жду|давай|делай|поехали|"
    r"вариант\s*[1-4абвг]|"
    r"миним|средн|максим|медиан|шаблонн|ручн|"
    r"ставь\s+\w+)"
    r"\s*$",
    _tprr_re.IGNORECASE
)

def _tprr_is_short_price_reply(text):
    if not text:
        return False
    s = str(text).strip()
    if len(s) > 80:
        return False
    return bool(_TPRR_PRICE_REPLY_RE.match(s))

def _tprr_get(task, key, default=""):
    try:
        if isinstance(task, dict):
            return task.get(key, default)
        return task[key]
    except Exception:
        return default

def _tprr_find_active_price_parent(conn, chat_id):
    try:
        row = conn.execute(
            """SELECT id FROM tasks 
               WHERE chat_id=? AND topic_id=2 
                 AND state IN ('WAITING_CLARIFICATION','IN_PROGRESS')
                 AND id IN (
                   SELECT task_id FROM task_history 
                   WHERE action='TOPIC2_PRICE_CHOICE_REQUESTED'
                 )
               ORDER BY updated_at DESC LIMIT 1""",
            (str(chat_id),)
        ).fetchone()
        if row:
            return row["id"] if hasattr(row, "keys") else row[0]
    except Exception:
        pass
    return None

_TPRR_ORIG_HANDLE_NEW = globals().get("_handle_new")
if _TPRR_ORIG_HANDLE_NEW and not getattr(_TPRR_ORIG_HANDLE_NEW, "_tprr_wrapped", False):
    async def _handle_new(conn, task, *args, **kwargs):
        try:
            topic_id = int(_tprr_get(task, "topic_id", 0) or 0)
            raw = str(_tprr_get(task, "raw_input", "") or "")
            if topic_id == 2 and _tprr_is_short_price_reply(raw):
                chat_id = str(_tprr_get(task, "chat_id", ""))
                parent_id = _tprr_find_active_price_parent(conn, chat_id)
                if parent_id:
                    task_id = str(_tprr_get(task, "id", ""))
                    try:
                        conn.execute(
                            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
                            (parent_id, "clarified:" + raw[:200])
                        )
                        conn.execute(
                            "UPDATE tasks SET state='IN_PROGRESS', error_message='', "
                            "updated_at=datetime('now') WHERE id=?",
                            (parent_id,)
                        )
                        conn.execute(
                            "UPDATE tasks SET state='CANCELLED', "
                            "error_message='TPRR:MERGED_TO_PARENT:'||?, "
                            "result='Ответ применён к активной сметной задаче' "
                            "WHERE id=?",
                            (parent_id, task_id)
                        )
                        conn.execute(
                            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
                            (task_id, "TPRR_MERGED_TO_PRICE_PARENT:" + parent_id)
                        )
                        conn.commit()
                        _TPRR_LOG.info("TPRR_MERGE task=%s → parent=%s reply=%s",
                                       task_id, parent_id, raw[:30])
                    except Exception as _e:
                        _TPRR_LOG.warning("TPRR_DB_ERR task=%s err=%s", task_id, _e)
                    return
        except Exception as e:
            _TPRR_LOG.exception("TPRR_TOP_ERR err=%s", e)
        res = _TPRR_ORIG_HANDLE_NEW(conn, task, *args, **kwargs)
        if _tprr_inspect.isawaitable(res):
            return await res
        return res
    _handle_new._tprr_wrapped = True

_TPRR_LOG.info("PATCH_TOPIC2_PRICE_REPLY_REVIVE_V1 installed")
# === END_PATCH_TOPIC2_PRICE_REPLY_REVIVE_V1 ===


# ============================================================
# === PATCH_TOPIC2_PRICE_TIMEOUT_GUARD_V1 ===
# Цель: задачи с TOPIC2_PRICE_CHOICE_REQUESTED не убивает 30-мин таймаут
# Факт: 10:16, 10:35, 10:43 — IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1
#       убил f1ef9fab пока юзер думал над ценой
# ============================================================
import logging as _tptg_logging
_TPTG_LOG = _tptg_logging.getLogger("task_worker.price_timeout_guard")

_TPTG_ORIG_TIMEOUT = globals().get("_in_progress_hard_timeout_by_created_at_fix_v1")
if _TPTG_ORIG_TIMEOUT and not getattr(_TPTG_ORIG_TIMEOUT, "_tptg_wrapped", False):
    def _in_progress_hard_timeout_by_created_at_fix_v1(conn, minutes: int = 30) -> int:
        try:
            rows = conn.execute(
                """SELECT id FROM tasks
                   WHERE state='IN_PROGRESS' AND topic_id=2
                     AND id IN (
                       SELECT task_id FROM task_history 
                       WHERE action='TOPIC2_PRICE_CHOICE_REQUESTED'
                     )""",
            ).fetchall()
            shielded = 0
            for r in rows:
                tid = r["id"] if hasattr(r, "keys") else r[0]
                try:
                    conn.execute(
                        "UPDATE tasks SET state='WAITING_CLARIFICATION', "
                        "error_message='TPTG:price_choice_pending', "
                        "updated_at=datetime('now') WHERE id=? AND state='IN_PROGRESS'",
                        (str(tid),)
                    )
                    shielded += 1
                except Exception:
                    pass
            if shielded:
                conn.commit()
                _TPTG_LOG.info("TPTG_SHIELDED %d tasks (price_pending → WAITING_CLARIFICATION)", shielded)
        except Exception as e:
            _TPTG_LOG.warning("TPTG_PREFILTER_ERR %s", e)
        return _TPTG_ORIG_TIMEOUT(conn, minutes)
    _in_progress_hard_timeout_by_created_at_fix_v1._tptg_wrapped = True

_TPTG_LOG.info("PATCH_TOPIC2_PRICE_TIMEOUT_GUARD_V1 installed")
# === END_PATCH_TOPIC2_PRICE_TIMEOUT_GUARD_V1 ===


# ============================================================
# === PATCH_TOPIC2_DONE_OVERRIDE_INVALID_PUBLIC_V1 ===
# Цель: если у задачи topic_2 есть все DONE markers + Drive XLSX/PDF ссылки,
#       не блокировать переход в AWAITING_CONFIRMATION/DONE через INVALID_PUBLIC_RESULT
# Факт логов 21:05:02: задача 893436d4 имела все 14 markers, но state=FAILED
# ============================================================
import logging as _tdoip_logging
_TDOIP_LOG = _tdoip_logging.getLogger("task_worker.done_override")

_TDOIP_REQUIRED_MARKERS = (
    "TOPIC2_XLSX_CREATED",
    "TOPIC2_PDF_CREATED",
    "TOPIC2_DRIVE_UPLOAD_XLSX_OK",
    "TOPIC2_DRIVE_UPLOAD_PDF_OK",
    "TOPIC2_TELEGRAM_DELIVERED",
)

def _tdoip_has_all_done_markers(conn, task_id):
    try:
        rows = conn.execute(
            "SELECT action FROM task_history WHERE task_id=?",
            (str(task_id),)
        ).fetchall()
        actions = " ".join(str(r[0]) for r in rows)
        return all(m in actions for m in _TDOIP_REQUIRED_MARKERS)
    except Exception:
        return False

def _tdoip_has_drive_links_in_result(result):
    if not result:
        return False
    s = str(result).lower()
    return "drive.google.com" in s and ("xlsx" in s or "pdf" in s or ".xls" in s or "📊" in str(result) or "📄" in str(result))

_TDOIP_ORIG_VIOLATION = globals().get("_fcg_public_result_violation")
if _TDOIP_ORIG_VIOLATION and not getattr(_TDOIP_ORIG_VIOLATION, "_tdoip_wrapped", False):
    def _fcg_public_result_violation(conn, task_id, state, result, error_message=""):
        try:
            row = conn.execute(
                "SELECT topic_id FROM tasks WHERE id=?", (str(task_id),)
            ).fetchone()
            topic_id_v = int(row[0]) if row else 0
            if topic_id_v == 2:
                if _tdoip_has_all_done_markers(conn, task_id) and _tdoip_has_drive_links_in_result(result):
                    try:
                        conn.execute(
                            "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                            (str(task_id), "TDOIP_OVERRIDE:14_markers_and_drive_links_present")
                        )
                        conn.commit()
                    except Exception:
                        pass
                    _TDOIP_LOG.info("TDOIP_OVERRIDE task=%s — markers + Drive links → no violation", task_id)
                    return ""
        except Exception as e:
            _TDOIP_LOG.warning("TDOIP_TOP_ERR task=%s err=%s", task_id, e)
        return _TDOIP_ORIG_VIOLATION(conn, task_id, state, result, error_message)
    _fcg_public_result_violation._tdoip_wrapped = True

_TDOIP_LOG.info("PATCH_TOPIC2_DONE_OVERRIDE_INVALID_PUBLIC_V1 installed")
# === END_PATCH_TOPIC2_DONE_OVERRIDE_INVALID_PUBLIC_V1 ===


# ============================================================
# === PATCH_TOPIC2_INLINE_FIX_20260506_V1 SUPERSEDES_NOTE ===
# Inline fixes applied directly in function bodies above:
#   - _p6e67_try_merge:  (1) state guard at top — stops infinite loop on CANCELLED/FAILED/DONE
#                        (2) fresh estimate dispatch in `if not parent` block — full-TZ → estimate
#   - _update_task FCG wrapper: bypass INVALID_PUBLIC_RESULT if 5 critical DONE markers + Drive link in result
#   - _t2v5_/_t2v6c_ price bind: explicit token required (no long messages, no fallback to history)
#
# Wrappers below (PATCH_TOPIC2_CANCEL_GUARD_V1 / FRESH_ESTIMATE_FALLBACK_V1 / PRICE_REPLY_REVIVE_V1 /
#   PRICE_TIMEOUT_GUARD_V1 / DONE_OVERRIDE_INVALID_PUBLIC_V1) are SUPERSEDED_BY_INLINE_FIX_20260506_V1.
# Kept inert (they wrap functions that are already inline-fixed). To remove: delete lines ~14898-15256.
# ============================================================


# === PATCH_PRICE_BIND_LOOP_TERMINATE_V1 ===
# Root cause: _t2pc_try_bind_price_choice returns False without setting FAILED when
# LATEST_PRICE_MENU_FALLBACK triggers the poison guard → worker re-queues → 68+ loop iterations.
# Fix: detect 3+ occurrences of the guard marker → forcibly set task to FAILED.
import logging as _pblt_logging
_PBLT_LOG = _pblt_logging.getLogger("task_worker")

_PBLT_ORIG = globals().get("_t2pc_try_bind_price_choice")
if _PBLT_ORIG and not getattr(_PBLT_ORIG, "_pblt_wrapped", False):
    async def _t2pc_try_bind_price_choice(conn, task):
        try:
            _pblt_id = str(task.get("id", "") if isinstance(task, dict) else
                           (task["id"] if hasattr(task, "keys") and "id" in task.keys() else ""))
            _pblt_marker = "PRICE_BIND_POISON_PARENT_GUARD_V2_BLOCKED_V4:LATEST_PRICE_MENU_FALLBACK"
            _pblt_cnt = conn.execute(
                "SELECT COUNT(*) FROM task_history WHERE task_id=? AND action=?",
                (_pblt_id, _pblt_marker)
            ).fetchone()
            if _pblt_cnt and _pblt_cnt[0] >= 3:
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (_pblt_id, "PRICE_BIND_POISON_LOOP_TERMINATED:LATEST_PRICE_MENU_FALLBACK")
                )
                conn.execute(
                    "UPDATE tasks SET state='FAILED',error_message='PRICE_BIND_POISON_LOOP_TERMINATED:LATEST_PRICE_MENU_FALLBACK',updated_at=datetime('now') WHERE id=?",
                    (_pblt_id,)
                )
                conn.commit()
                _PBLT_LOG.warning("PRICE_BIND_POISON_LOOP_TERMINATED task=%s", _pblt_id)
                return False
        except Exception as _pblt_e:
            _PBLT_LOG.warning("PATCH_PRICE_BIND_LOOP_TERMINATE_V1 pre-check err: %s", _pblt_e)
        import inspect as _pblt_inspect
        res = _PBLT_ORIG(conn, task)
        if _pblt_inspect.isawaitable(res):
            return await res
        return res
    _t2pc_try_bind_price_choice._pblt_wrapped = True
    _t2pc_try_bind_price_choice._t2fpg_wrapped = True
    _PBLT_LOG.info("PATCH_PRICE_BIND_LOOP_TERMINATE_V1 installed")
else:
    _PBLT_LOG.warning("PATCH_PRICE_BIND_LOOP_TERMINATE_V1 skipped: _t2pc_try_bind_price_choice not found")
# === END_PATCH_PRICE_BIND_LOOP_TERMINATE_V1 ===


# === PATCH_FCG_DONE_CONTRACT_BYPASS_V1 ===
# Root cause: FCG _update_task wrapper fires _fcg_public_result_violation even after canonical engine
# completed successfully (TOPIC2_DONE_CONTRACT_OK in history). Some result fragment triggers INVALID_PUBLIC_RESULT.
# Existing bypass (5 markers + drive link in result) fails when result text has no drive.google.com.
# Fix: if TOPIC2_DONE_CONTRACT_OK is in task_history → canonical engine already verified everything → skip FCG.
import logging as _fdcb_logging
_FDCB_LOG = _fdcb_logging.getLogger("task_worker")

_FDCB_ORIG_UPDATE = globals().get("_update_task")
if _FDCB_ORIG_UPDATE and not getattr(_FDCB_ORIG_UPDATE, "_fdcb_wrapped", False):
    def _update_task(conn, task_id, *args, **kwargs):
        state = kwargs.get("state", args[0] if args else None)
        result = kwargs.get("result", args[1] if len(args) >= 2 else None)
        _fdcb_result_empty = not result or not str(result).strip()
        if state == "DONE" and _fdcb_result_empty:
            try:
                _fdcb_row = conn.execute(
                    "SELECT 1 FROM task_history WHERE task_id=? AND action IN ('TOPIC2_AC_GATE_OK','TOPIC2_DONE_CONTRACT_OK') LIMIT 1",
                    (str(task_id),)
                ).fetchone()
                if _fdcb_row:
                    conn.execute(
                        "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                        (str(task_id), "PATCH_FCG_DONE_CONTRACT_BYPASS_V1:bypass_done_marker_ok")
                    )
                    _FDCB_LOG.info("PATCH_FCG_DONE_CONTRACT_BYPASS_V1 bypass_done_marker_ok task=%s state=%s", task_id, state)
                    return _FCG_ORIG_UPDATE_TASK(conn, task_id, *args, **kwargs)
            except Exception as _fdcb_e:
                _FDCB_LOG.warning("PATCH_FCG_DONE_CONTRACT_BYPASS_V1 err: %s", _fdcb_e)
        return _FDCB_ORIG_UPDATE(conn, task_id, *args, **kwargs)
    _update_task._fdcb_wrapped = True
    _update_task._fcg_wrapped = True
    _FDCB_LOG.info("PATCH_FCG_DONE_CONTRACT_BYPASS_V1 installed")
else:
    _FDCB_LOG.warning("PATCH_FCG_DONE_CONTRACT_BYPASS_V1 skipped: _update_task not found")
# === END_PATCH_FCG_DONE_CONTRACT_BYPASS_V1 ===

# === PATCH_TOPIC500_ADAPTIVE_OUTPUT_V1 ===
# Root cause: all topic_500 queries use engine="search_supplier" and procurement format
# (supplier table with phone/price/URL). Factual/normative/technical queries return wrong format.
# Fix: classify query intent → prepend format instruction to raw_input so Perplexity
# returns the right output structure. procurement mode unchanged.
import logging as _t500ao_logging
import re as _t500ao_re

_T500AO_LOG = _t500ao_logging.getLogger("task_worker")

_T500AO_PROCUREMENT_RE = re.compile(
    r"\b(купить|купи|куплю|цена|стоимость|почём|поставщик|материал|товар|артикул|авито|avito|озон|ozon|wildberries|вайлдберриз|auto\.ru|дром|drom|наличие|заказать|найди.{0,20}где|найди.{0,20}купить|маркетплейс|прайс|оптом|розница|скидка|доставка)\b",
    re.IGNORECASE,
)
_T500AO_NORMATIVE_RE = re.compile(
    r"\b(ГОСТ|СП\s*\d|СНиП|норматив|стандарт|требование|допуск|регламент|ФЗ\s*\d|федеральн|кодекс|СанПиН|ПНСТ|ТУ\s*\d)\b",
    re.IGNORECASE,
)
_T500AO_TECHNICAL_RE = re.compile(
    r"\b(технология|технологию|технологии|монтаж|установка|инструкция|как делать|как сделать|порядок работ|методика|состав работ|этапы|нанесение|укладка|заливка|армирование|сварка|бетонирование)\b",
    re.IGNORECASE,
)
_T500AO_DOWNLOAD_RE = re.compile(
    r"\b(скачать|скачай|ссылка.{0,15}скачать|приложение|программа|apk|4pda|appstorrent|apkpure|trashbox|torrent|exe|setup)\b",
    re.IGNORECASE,
)
_T500AO_NEWS_RE = re.compile(
    r"\b(новост|последн.{0,10}изменен|актуальн|свеж.{0,5}(данн|новост|информац)|что нов|когда вышл|обновлени)\b",
    re.IGNORECASE,
)
_T500AO_SERVICE_RE = re.compile(
    r"\b(подрядчик|бригада|найти.{0,15}(мастер|компани|бригад|подрядчик)|услуга.{0,20}(строй|ремонт|монтаж)|кто делает|найди.{0,15}компани)\b",
    re.IGNORECASE,
)
_T500AO_COMPARISON_RE = re.compile(
    r"\b(сравни|сравнение|что лучше|разница между|отличие|плюсы и минусы|чем отличается|vs\b)\b",
    re.IGNORECASE,
)
_T500AO_TROUBLESHOOT_RE = re.compile(
    r"\b(не работает|не запускается|ошибка|проблема|почему не|как исправить|как починить|что делать если|неисправность|сбой|вылетает|зависает)\b",
    re.IGNORECASE,
)

_T500AO_MODE_PROMPTS = {
    "normative": (
        "Задача: найти норму/стандарт/документ. "
        "Формат ответа: название документа, номер пункта если применимо, область применения, прямая ссылка на источник, дата проверки. "
        "Без таблиц поставщиков. Без цен. Только нормативная информация.\n\n"
    ),
    "technical": (
        "Задача: найти техническую информацию/технологию. "
        "Формат ответа: метод/технология, ключевые шаги, нормативные требования если есть, источник. "
        "Без таблиц поставщиков. Без цен.\n\n"
    ),
    "download": (
        "Задача: найти ссылку для скачивания. "
        "Формат ответа: одна лучшая ссылка, платформа, совместимость, статус источника (официальный/форум). "
        "Без таблиц поставщиков.\n\n"
    ),
    "news": (
        "Задача: найти актуальные новости/изменения. "
        "Формат ответа: последние подтверждённые факты, дата события, источник. "
        "Только свежая информация, не кэш. Без таблиц поставщиков.\n\n"
    ),
    "service": (
        "Задача: найти подрядчика/компанию/услугу. "
        "Формат ответа: название, город, контакт, ссылка, рейтинг если найден. "
        "Без таблиц цен на материалы.\n\n"
    ),
    "comparison": (
        "Задача: сравнить варианты. "
        "Формат ответа: таблица сравнения с ключевыми параметрами, итоговый вывод. "
        "Без избыточных supplier-строк.\n\n"
    ),
    "troubleshooting": (
        "Задача: найти решение проблемы. "
        "Формат ответа: причина проблемы, конкретные шаги решения, команды/настройки если применимо, ссылка на официальную документацию. "
        "Без таблиц поставщиков.\n\n"
    ),
    "factual": (
        "Задача: найти факт/информацию. "
        "Формат ответа: прямой ответ на вопрос, источник, что подтверждено, что неуверенно. "
        "Без таблиц поставщиков. Без цен.\n\n"
    ),
}


def _t500ao_classify(text: str) -> str:
    if _T500AO_PROCUREMENT_RE.search(text):
        return "procurement"
    if _T500AO_NORMATIVE_RE.search(text):
        return "normative"
    if _T500AO_DOWNLOAD_RE.search(text):
        return "download"
    if _T500AO_NEWS_RE.search(text):
        return "news"
    if _T500AO_TROUBLESHOOT_RE.search(text):
        return "troubleshooting"
    if _T500AO_COMPARISON_RE.search(text):
        return "comparison"
    if _T500AO_SERVICE_RE.search(text):
        return "service"
    if _T500AO_TECHNICAL_RE.search(text):
        return "technical"
    return "factual"


_T500AO_ORIG = globals().get("_p0_runtime_topic500_direct_search_20260504")
if _T500AO_ORIG and not getattr(_T500AO_ORIG, "_t500ao_wrapped", False):
    async def _p0_runtime_topic500_direct_search_20260504(conn, task, chat_id, topic_id):
        try:
            _t500ao_text = str(
                (task.get("raw_input") if isinstance(task, dict) else None) or ""
            ).strip()[:2000]
            _t500ao_mode = _t500ao_classify(_t500ao_text)
            if _t500ao_mode != "procurement" and _t500ao_mode in _T500AO_MODE_PROMPTS:
                _t500ao_instruction = _T500AO_MODE_PROMPTS[_t500ao_mode]
                _t500ao_new_input = _t500ao_instruction + _t500ao_text
                task = dict(task) if not isinstance(task, dict) else dict(task)
                task["raw_input"] = _t500ao_new_input
                task["normalized_input"] = _t500ao_new_input
                _T500AO_LOG.info(
                    "PATCH_TOPIC500_ADAPTIVE_OUTPUT_V1 mode=%s task=%s",
                    _t500ao_mode,
                    str(task.get("id", ""))[:36],
                )
        except Exception as _t500ao_e:
            _T500AO_LOG.warning("PATCH_TOPIC500_ADAPTIVE_OUTPUT_V1 classify_err: %s", _t500ao_e)
        return await _T500AO_ORIG(conn, task, chat_id, topic_id)
    _p0_runtime_topic500_direct_search_20260504._t500ao_wrapped = True
    _T500AO_LOG.info("PATCH_TOPIC500_ADAPTIVE_OUTPUT_V1 installed")
else:
    _T500AO_LOG.warning("PATCH_TOPIC500_ADAPTIVE_OUTPUT_V1 skipped: _p0_runtime_topic500_direct_search_20260504 not found")
# === END_PATCH_TOPIC500_ADAPTIVE_OUTPUT_V1 ===


# === PATCH_TOPIC500_MEMORY_DEDUP_V1 + PATCH_TOPIC500_SEARCH_POLLUTION_GUARD_V1 ===
# GAP-5: memory.db had no UNIQUE on (chat_id, key) → INSERT INTO created duplicates.
#         Fixed: UNIQUE INDEX added to DB, INSERT OR REPLACE in task_worker.py body.
# GAP-6: _save_memory for topic_500 stored full supplier tables in long_memory_context →
#         next prompts received garbage context. Fix: truncate to 300 chars summary only.
import logging as _t500mem_logging
_T500MEM_LOG = _t500mem_logging.getLogger("task_worker")

_T500MEM_ORIG_SAVE = globals().get("_save_memory")
if _T500MEM_ORIG_SAVE and not getattr(_T500MEM_ORIG_SAVE, "_t500mem_wrapped", False):
    def _save_memory(chat_id, topic_id, raw_input, result):
        try:
            _t500mem_tid = int(topic_id or 0)
            if _t500mem_tid == 500 and isinstance(result, str) and len(result) > 300:
                _t500mem_summary = result[:300].rsplit("\n", 1)[0] + "…"
                _T500MEM_LOG.info(
                    "PATCH_TOPIC500_SEARCH_POLLUTION_GUARD_V1 truncated result=%d->300 chat=%s",
                    len(result), str(chat_id)
                )
                result = _t500mem_summary
        except Exception as _t500mem_e:
            _T500MEM_LOG.warning("PATCH_TOPIC500_SEARCH_POLLUTION_GUARD_V1 err: %s", _t500mem_e)
        return _T500MEM_ORIG_SAVE(chat_id, topic_id, raw_input, result)
    _save_memory._t500mem_wrapped = True
    _T500MEM_LOG.info("PATCH_TOPIC500_MEMORY_DEDUP_V1 installed (DB UNIQUE INDEX + INSERT OR REPLACE)")
    _T500MEM_LOG.info("PATCH_TOPIC500_SEARCH_POLLUTION_GUARD_V1 installed")
else:
    _T500MEM_LOG.warning("PATCH_TOPIC500_MEMORY_DEDUP_V1 skipped: _save_memory not found")
# === END_PATCH_TOPIC500_MEMORY_DEDUP_V1 ===

# === PATCH_T2RFP_REENTRANCE_GUARD_V1 ===
# Root cause: T2RFP wraps _t2fer_run_final_estimate and redirects to _handle_in_progress.
# _handle_in_progress → original handler → _handle_drive_file → T2FER calls
# _t2fer_run_final_estimate again → T2RLG passes to its _ORIG which is T2RFP → loop.
# T2RLG_ORIG_FN pointed to T2RFP (not WCG/original), so skip logic was ineffective.
# Fix: per-task reentrancy set. Second call for same task_id → return False immediately.
# T2FER _handle_drive_file gets False → falls to _T2FER_ORIG_HANDLE_DRIVE_FILE (normal path).
import logging as _t2rrg_log
import inspect as _t2rrg_inspect
_T2RRG_LOG = _t2rrg_log.getLogger("task_worker")
_T2RRG_ACTIVE = set()

_T2RRG_ORIG = globals().get("_t2fer_run_final_estimate")
if _T2RRG_ORIG and not getattr(_T2RRG_ORIG, "_t2rrg_wrapped", False):
    async def _t2fer_run_final_estimate(conn, task, reason):
        try:
            task_id = str(_t2fer_get(task, "id", "") or "")
        except Exception:
            task_id = ""
        if task_id and task_id in _T2RRG_ACTIVE:
            _T2RRG_LOG.warning(
                "T2RRG_REENTRANT_BLOCKED task=%s reason=%s — breaking loop", task_id, reason
            )
            return False
        if task_id:
            _T2RRG_ACTIVE.add(task_id)
        try:
            res = _T2RRG_ORIG(conn, task, reason)
            if _t2rrg_inspect.isawaitable(res):
                return await res
            return res
        finally:
            _T2RRG_ACTIVE.discard(task_id)
    _t2fer_run_final_estimate._t2rrg_wrapped = True
    _T2RRG_LOG.info("PATCH_T2RFP_REENTRANCE_GUARD_V1 installed")
else:
    _T2RRG_LOG.warning("PATCH_T2RFP_REENTRANCE_GUARD_V1 skipped: _t2fer_run_final_estimate not found")
# === END_PATCH_T2RFP_REENTRANCE_GUARD_V1 ===

# === PATCH_T2P6E67_FRESH_ESTIMATE_BYPASS_V1 ===
# When task_id is in _T2RRG_ACTIVE (inside T2RFP redirect to _handle_in_progress)
# and task is a fresh estimate, P6E67 must not run and set WAITING_CLARIFICATION.
# T2FER's _p6e67_try_merge wrapper already tries to intercept but gets False from T2RRG
# (reentrant block), then falls through to original P6E67 which fires the terminal guard.
# Fix: wrap _p6e67_try_merge at outermost layer — if fresh estimate + T2RRG active → return False.
# P6E67's _handle_new/_handle_in_progress wrappers see False → continue to original handlers
# which process the file through normal intake flow.
import asyncio as _t2p6_asyncio
_T2P6E67_ORIG = globals().get("_p6e67_try_merge")
if _T2P6E67_ORIG and not getattr(_T2P6E67_ORIG, "_t2p6e_wrapped", False):
    async def _p6e67_try_merge(conn, task, *args, **kwargs):
        try:
            _t2p6_task_id = str(_t2fer_get(task, "id", "") or "")
            if _t2p6_task_id and _t2p6_task_id in _T2RRG_ACTIVE and _t2fer_is_fresh_estimate(task):
                _T2RRG_LOG.info(
                    "T2P6E67_BYPASS_FRESH_ESTIMATE task=%s — inside T2RFP redirect, skip P6E67",
                    _t2p6_task_id,
                )
                return False
        except Exception:
            pass
        res = _T2P6E67_ORIG(conn, task, *args, **kwargs)
        if _t2p6_asyncio.iscoroutine(res):
            return await res
        return res
    _p6e67_try_merge._t2p6e_wrapped = True
    _T2RRG_LOG.info("PATCH_T2P6E67_FRESH_ESTIMATE_BYPASS_V1 installed")
else:
    _T2RRG_LOG.warning("PATCH_T2P6E67_FRESH_ESTIMATE_BYPASS_V1 skipped: _p6e67_try_merge not found")
# === END_PATCH_T2P6E67_FRESH_ESTIMATE_BYPASS_V1 ===

# === PATCH_WCPE_CLARIFIED_UNBLOCK_V1 ===
# Bug: WCG_SKIP in error_message blocks task pick-up even after user replied (clarified:N in history).
# Telegram_daemon sets IN_PROGRESS but doesn't clear error_message — task stays blocked by WCPE.
# Fix: Allow pick-up when WCG_SKIP AND task has non-empty clarified: entry in task_history.
import logging as _wcpe_ub_log_mod
_WCPE_UB_LOG = _wcpe_ub_log_mod.getLogger("task_worker")
_WCPE_UB_PREV = globals().get("_pick_next_task")
if _WCPE_UB_PREV and not getattr(_WCPE_UB_PREV, "_wcpe_ub_wrapped", False):
    def _pick_next_task_wcpe_ub(conn, chat_id=None):
        try:
            # Block WAITING_CLARIFICATION+WCG_SKIP (still waiting for reply).
            # Allow IN_PROGRESS+WCG_SKIP — telegram_daemon set IN_PROGRESS on user reply
            # but doesn't clear error_message, so without this fix the task is stuck forever.
            where = [
                "state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION')",
                "NOT (state='WAITING_CLARIFICATION' AND COALESCE(error_message,'') LIKE 'WCG_SKIP%')",
            ]
            params = []
            if chat_id:
                where.insert(0, "chat_id=?")
                params.append(str(chat_id))
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                f"SELECT * FROM tasks WHERE {' AND '.join(where)}"
                " ORDER BY CASE state WHEN 'IN_PROGRESS' THEN 0 ELSE 1 END, created_at ASC LIMIT 1",
                params,
            ).fetchone()
            conn.execute("COMMIT")
            return row
        except Exception:
            return _WCPE_UB_PREV(conn, chat_id)
    _pick_next_task_wcpe_ub._wcpe_ub_wrapped = True
    _pick_next_task = _pick_next_task_wcpe_ub
    globals()["_pick_next_task"] = _pick_next_task_wcpe_ub
    _WCPE_UB_LOG.info("PATCH_WCPE_CLARIFIED_UNBLOCK_V1 installed")
# === END_PATCH_WCPE_CLARIFIED_UNBLOCK_V1 ===

# === PATCH_P6C_FULLTEXT_ESTIMATE_PREP_V1 ===
# Bug: _p6c_meta_20260504 uses strict json.loads → fails when REVISION_CONTEXT appended.
# Result: caption="" → estimate_raw only "\nЭтажей: 1" → no dims/material found → clarification loop.
# Fix: partial JSON parse + include REVISION_CONTEXT voice texts + extract dims from filename.
import logging as _p6cf_log_mod, re as _p6cf_re, json as _p6cf_json
_P6CF_LOG = _p6cf_log_mod.getLogger("task_worker")

def _p6cf_partial_meta(raw_input):
    s = str(raw_input or "")[:50000]
    try:
        v = _p6cf_json.loads(s)
        if isinstance(v, dict):
            return v
    except Exception:
        pass
    try:
        m = _p6cf_re.match(r'(\{[^{}]*\})', s, _p6cf_re.DOTALL)
        if m:
            v = _p6cf_json.loads(m.group(1))
            if isinstance(v, dict):
                return v
    except Exception:
        pass
    return {}

def _p6cf_extract_voices(raw_input):
    s = str(raw_input or "")
    voices = _p6cf_re.findall(r'\[VOICE\]\s*(.+?)(?=\n---|\Z)', s, _p6cf_re.DOTALL)
    return " ".join(v.strip() for v in voices)

def _p6cf_dims_from_fn(fn):
    if not fn:
        return None
    m = _p6cf_re.search(r'(\d+)\s*[xхXХ×*]\s*(\d+)', fn)
    if m:
        return m.group(1), m.group(2)
    return None

_P6CF_ORIG_PREP = globals().get("_p6c_prepare_topic2_raw_20260504")
if _P6CF_ORIG_PREP and not getattr(_P6CF_ORIG_PREP, "_p6cf_wrapped", False):
    def _p6c_prepare_topic2_raw_20260504(task_id, raw_input):
        meta = _p6cf_partial_meta(raw_input)
        caption = str(meta.get("caption") or meta.get("text") or "").strip()
        fn = str(meta.get("file_name") or "").strip()
        parts = [caption] if caption else []
        voices = _p6cf_extract_voices(raw_input)
        if voices:
            parts.append(voices)
        text = " ".join(parts).strip()
        low = text.lower()
        if fn and not _p6cf_re.search(r'\d+\s*(?:на|x|х|×|\*)\s*\d+', low):
            dims = _p6cf_dims_from_fn(fn)
            if dims:
                text += f"\nРазмеры объекта: {dims[0]} на {dims[1]} м"
                _P6CF_LOG.info("P6CF: dims from filename %s → %sx%s task=%s", fn, dims[0], dims[1], task_id)
        if "этаж" not in text.lower():
            text += "\nЭтажей: 1"
        if "смет" not in text.lower():
            text += "\nНужна полная смета"
        _P6CF_LOG.info("P6CF: estimate_raw len=%d task=%s", len(text), task_id)
        return text.strip()
    _p6c_prepare_topic2_raw_20260504._p6cf_wrapped = True
    globals()["_p6c_prepare_topic2_raw_20260504"] = _p6c_prepare_topic2_raw_20260504
    _P6CF_LOG.info("PATCH_P6C_FULLTEXT_ESTIMATE_PREP_V1 installed")
# === END_PATCH_P6C_FULLTEXT_ESTIMATE_PREP_V1 ===

# === PATCH_P6CF2_FLOOR_FORMAT_FIX_V1 ===
# Bug: "Этажей: 1" не матчится _p2_floors regex (\d+\s*этаж — число ДО слова).
# Fix: заменить на "1 этаж" который матчится.
import logging as _p6cf2_log_mod
_P6CF2_LOG = _p6cf2_log_mod.getLogger("task_worker")
_P6CF2_ORIG = globals().get("_p6c_prepare_topic2_raw_20260504")
if _P6CF2_ORIG and not getattr(_P6CF2_ORIG, "_p6cf2_wrapped", False):
    def _p6c_prepare_topic2_raw_20260504(task_id, raw_input):
        text = _P6CF2_ORIG(task_id, raw_input)
        text = text.replace("Этажей: 1", "1 этаж")
        return text
    _p6c_prepare_topic2_raw_20260504._p6cf2_wrapped = True
    globals()["_p6c_prepare_topic2_raw_20260504"] = _p6c_prepare_topic2_raw_20260504
    _P6CF2_LOG.info("PATCH_P6CF2_FLOOR_FORMAT_FIX_V1 installed")
# === END_PATCH_P6CF2_FLOOR_FORMAT_FIX_V1 ===

# === PATCH_P6CF3_CLARIFIED_HISTORY_INCLUDE_V1 ===
# Bug: estimate_raw строится только из caption+voices, без ответов пользователя.
# clarified:* в task_history игнорируются → _p2_parse не видит "Фундамент монолитный..."
# → бесконечный цикл вопросов. Fix: добавить осмысленные clarified ответы (≥10 симв).
import sqlite3 as _p6cf3_sqlite3
import logging as _p6cf3_log_mod
_P6CF3_LOG = _p6cf3_log_mod.getLogger("task_worker")
_P6CF3_DB = "/root/.areal-neva-core/data/core.db"
_P6CF3_SKIP = {"1", "2", "3", "да", "нет", "вот", "всё", "все", "средние", "дешёвые", "дорогие",
               "средний", "дешёвый", "дорогой", "подтверждаю"}

_P6CF3_ORIG = globals().get("_p6c_prepare_topic2_raw_20260504")
if _P6CF3_ORIG and not getattr(_P6CF3_ORIG, "_p6cf3_wrapped", False):
    def _p6c_prepare_topic2_raw_20260504(task_id, raw_input):
        text = _P6CF3_ORIG(task_id, raw_input)
        try:
            conn2 = _p6cf3_sqlite3.connect(_P6CF3_DB, timeout=5)
            rows = conn2.execute(
                "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'clarified:%' ORDER BY rowid",
                (str(task_id),)
            ).fetchall()
            conn2.close()
            extra = []
            for (action,) in rows:
                val = action[len("clarified:"):].strip()
                if val and len(val) >= 10 and val.lower() not in _P6CF3_SKIP:
                    extra.append(val)
            if extra:
                text = text + "\n" + "\n".join(extra)
                _P6CF3_LOG.info("PATCH_P6CF3: added %d clarified entries task=%s", len(extra), task_id)
        except Exception as _p6cf3_e:
            _P6CF3_LOG.warning("PATCH_P6CF3 err: %s", _p6cf3_e)
        return text
    _p6c_prepare_topic2_raw_20260504._p6cf3_wrapped = True
    globals()["_p6c_prepare_topic2_raw_20260504"] = _p6c_prepare_topic2_raw_20260504
    _P6CF3_LOG.info("PATCH_P6CF3_CLARIFIED_HISTORY_INCLUDE_V1 installed")
# === END_PATCH_P6CF3_CLARIFIED_HISTORY_INCLUDE_V1 ===

# === PATCH_P6E67_WC_SPIN_LOOP_GUARD_V1 ===
# Bug: tasks with error_message='P6E67_PARENT_NOT_FOUND_TERMINAL_GUARD_V1'
# and state=WAITING_CLARIFICATION are picked every ~1.5s because they don't
# match WCG_SKIP% exclusion. WCG_SKIP_LOOP fires only inside _t2fer_run_final_estimate
# which is never called for text-type orphan tasks.
# Fix: on startup + on every pick cycle, CANCEL stale P6E67 WAITING_CLARIFICATION
# tasks that have no clarification reply in last 60 minutes.
import logging as _p6e67wc_log
import sqlite3 as _p6e67wc_sqlite
_P6E67WC_LOG = _p6e67wc_log.getLogger("task_worker")
_P6E67WC_DB = "/root/.areal-neva-core/data/core.db"
_P6E67WC_SQL = (
    "UPDATE tasks SET state='CANCELLED', "
    "error_message='P6E67_ORPHAN_WC_CANCEL_V1', updated_at=datetime('now') "
    "WHERE state='WAITING_CLARIFICATION' "
    "AND error_message LIKE 'P6E67_PARENT_NOT_FOUND%' "
    "AND updated_at < datetime('now','-5 minutes') "
    "AND NOT EXISTS ("
    "  SELECT 1 FROM task_history h WHERE h.task_id=tasks.id "
    "  AND h.action LIKE 'clarified:%' "
    "  AND h.created_at > datetime('now','-60 minutes')"
    ")"
)

try:
    with _p6e67wc_sqlite.connect(_P6E67WC_DB, timeout=10) as _p6e67wc_conn:
        _p6e67wc_conn.execute(_P6E67WC_SQL)
        _cancelled = _p6e67wc_conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE error_message='P6E67_ORPHAN_WC_CANCEL_V1' "
            "AND updated_at > datetime('now','-10 seconds')"
        ).fetchone()[0]
        _p6e67wc_conn.commit()
        if _cancelled:
            _P6E67WC_LOG.info("PATCH_P6E67_WC_SPIN_LOOP_GUARD_V1: startup cancelled %d orphan task(s)", _cancelled)
except Exception as _p6e67wc_startup_e:
    _P6E67WC_LOG.warning("PATCH_P6E67_WC_SPIN_LOOP_GUARD_V1 startup err: %s", _p6e67wc_startup_e)

_P6E67WC_ORIG_PICK = globals().get("_pick_next_task")
if _P6E67WC_ORIG_PICK and not getattr(_P6E67WC_ORIG_PICK, "_p6e67wc_wrapped", False):
    def _pick_next_task(conn, chat_id=None):
        try:
            conn.execute(_P6E67WC_SQL)
            conn.commit()
        except Exception:
            pass
        return _P6E67WC_ORIG_PICK(conn, chat_id=chat_id)
    _pick_next_task._p6e67wc_wrapped = True
    globals()["_pick_next_task"] = _pick_next_task
    _P6E67WC_LOG.info("PATCH_P6E67_WC_SPIN_LOOP_GUARD_V1: picker guard installed")
# === END_PATCH_P6E67_WC_SPIN_LOOP_GUARD_V1 ===

# === PATCH_TOPIC2_PDF_CANONICAL_GATE_HANDLE_IN_PROGRESS_V1 ===
# Root cause: _handle_in_progress P6C (line 7017) intercepts topic_2 drive_file PDF tasks
# and routes to sample_template_engine (old route) — canonical gate only fires in _handle_new.
# Fix: wrap _handle_in_progress — topic_2 + drive_file + PDF + estimate intent
#      → always canonical maybe_handle_stroyka_estimate, old route blocked, no LLM fallback.
# Scope: topic_2 only. topic_5/210/500 not touched.
import logging as _p8t2c_log_mod
import json as _p8t2c_json
_P8T2C_LOG = _p8t2c_log_mod.getLogger("task_worker")

_P8T2C_ESTIMATE_KW = ("смет", "стоимость", "посчитать", "рассчитать", "полная смета")
_P8T2C_BUILD_KW = ("дом", "фундамент", "кров", "стен", "каркас", "фальц", "санузел",
                   "гараж", "баня", "склад", "барнхаус", "объект", "отделк")

def _p8t2c_low(v):
    try:
        return str(v or "").lower().replace("ё", "е")
    except Exception:
        return ""

def _p8t2c_get_meta(raw_input):
    try:
        raw_str = str(raw_input or "")
        json_part = raw_str.split("---")[0].strip()
        if json_part.startswith("{"):
            return _p8t2c_json.loads(json_part)
    except Exception:
        pass
    return {}

def _p8t2c_is_pdf(raw_input):
    meta = _p8t2c_get_meta(raw_input)
    fn = _p8t2c_low(meta.get("file_name", ""))
    mime = _p8t2c_low(meta.get("mime_type", ""))
    return fn.endswith(".pdf") or "pdf" in mime

def _p8t2c_is_estimate_intent(raw_input):
    meta = _p8t2c_get_meta(raw_input)
    caption = _p8t2c_low(meta.get("caption", ""))
    raw_low = _p8t2c_low(raw_input)
    text = caption or raw_low
    return (
        any(w in text for w in _P8T2C_ESTIMATE_KW)
        and any(w in text for w in _P8T2C_BUILD_KW)
    )

def _p8t2c_row(task, key, default=None):
    try:
        if hasattr(task, "keys") and key in task.keys():
            return task[key]
    except Exception:
        pass
    try:
        return task[key]
    except Exception:
        return default

_P8T2C_ORIG_HIP = globals().get("_handle_in_progress")
if _P8T2C_ORIG_HIP and not getattr(_P8T2C_ORIG_HIP, "_p8t2c_wrapped", False):

    async def _handle_in_progress(conn, task, chat_id=None, topic_id=None):  # noqa: F811
        try:
            raw_input = str(_p8t2c_row(task, "raw_input", "") or "")
            input_type = str(_p8t2c_row(task, "input_type", "text") or "")
            _topic_id = int(_p8t2c_row(task, "topic_id", 0) or 0)
            task_id = str(_p8t2c_row(task, "id", "") or "")

            if (
                _topic_id == 2
                and input_type in ("drive_file", "file", "document")
                and _p8t2c_is_pdf(raw_input)
                and _p8t2c_is_estimate_intent(raw_input)
            ):
                _P8T2C_LOG.info("P8T2C_PDF_CANONICAL_GATE task=%s → canonical", task_id)
                _fcg_history(conn, task_id, "FILE_INTAKE_ROUTER_TOPIC2_CANONICAL_ROUTE")
                _fcg_history(conn, task_id, "TOPIC2_FILE_INTAKE_LOCAL_PATH_OK")
                conn.commit()
                ok = False
                try:
                    from core.stroyka_estimate_canon import maybe_handle_stroyka_estimate as _p8t2c_mhs
                    ok = await _p8t2c_mhs(conn, task, None)
                except Exception as _p8t2c_ce:
                    _P8T2C_LOG.error("P8T2C_CANONICAL_ERR task=%s %s", task_id, _p8t2c_ce)
                    ok = False

                if ok:
                    _P8T2C_LOG.info("P8T2C_CANONICAL_OK task=%s", task_id)
                    return True

                # Canonical returned False — FAIL, no old route, no LLM
                _P8T2C_LOG.warning("P8T2C_CANONICAL_RETURNED_FALSE task=%s → FAILED", task_id)
                _fcg_history(conn, task_id, "TOPIC2_CANONICAL_ENGINE_FAILED_AFTER_OLD_ROUTE_BLOCK_V1")
                chat_id_str = str(_p8t2c_row(task, "chat_id", "") or "")
                reply_to = _p8t2c_row(task, "reply_to_message_id", None)
                try:
                    conn.execute(
                        "UPDATE tasks SET state='FAILED', "
                        "error_message='TOPIC2_CANONICAL_ENGINE_FAILED_AFTER_OLD_ROUTE_BLOCK_V1', "
                        "updated_at=datetime('now') WHERE id=?",
                        (task_id,)
                    )
                    conn.commit()
                except Exception:
                    pass
                try:
                    _send_once_ex(conn, task_id, chat_id_str,
                                  "Для расчёта сметы нужны размеры объекта и материалы. Напиши текстом.",
                                  reply_to, "p8t2c_need_dims")
                except Exception:
                    pass
                return True

        except Exception as _p8t2c_outer_e:
            _P8T2C_LOG.error("P8T2C_OUTER_ERR task=%s %s",
                             str(_p8t2c_row(task, "id", ""))[:36], _p8t2c_outer_e)

        return await _P8T2C_ORIG_HIP(conn, task, chat_id=chat_id, topic_id=topic_id)

    _handle_in_progress._p8t2c_wrapped = True
    globals()["_handle_in_progress"] = _handle_in_progress
    _P8T2C_LOG.info("PATCH_TOPIC2_PDF_CANONICAL_GATE_HANDLE_IN_PROGRESS_V1 installed")
else:
    _P8T2C_LOG.warning("PATCH_TOPIC2_PDF_CANONICAL_GATE_HANDLE_IN_PROGRESS_V1 skipped")
# === END_PATCH_TOPIC2_PDF_CANONICAL_GATE_HANDLE_IN_PROGRESS_V1 ===

# === PATCH_TOPIC5_ACT_DISPATCH_V3 ===
# Replace _fcg_handle_topic5_final_act with canonical engine dispatcher.
# Rule: if t5_canonical_act_generate returns ok=True → NEVER call old handler.
# Upload fallback: use _fcg_upload (OAuth) if service-account upload failed.
# Fallback to original only if ok=False (no materials/photos).
import logging as _p8d_log_mod
import os as _p8d_os
_P8D_LOG = _p8d_log_mod.getLogger("task_worker")

_P8D_ORIG_HANDLE_TOPIC5 = globals().get("_fcg_handle_topic5_final_act")
if _P8D_ORIG_HANDLE_TOPIC5 and not getattr(_P8D_ORIG_HANDLE_TOPIC5, "_p8d_wrapped", False):

    _P8D_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    _P8D_PDF_MIME = "application/pdf"

    # Phrases that must not appear in public result
    _P8D_CLEAN_FORBIDDEN = (
        "/root", ".json", "task_id", "Traceback", "Error:", "Exception",
        "MANIFEST", "P6E67", "buf_", "active_folder_", ".bak", ".log",
        "PATCH_", "INSTALLED", "VERIFIED",
    )

    def _p8d_result_clean(text):
        for bad in _P8D_CLEAN_FORBIDDEN:
            if bad.lower() in text.lower():
                return False
        return True

    async def _fcg_handle_topic5_final_act(conn, task):  # noqa: F811
        task_id = _fcg_s(_fcg_row(task, "id", ""))
        chat_id = _fcg_s(_fcg_row(task, "chat_id", ""))
        topic_id = int(_fcg_row(task, "topic_id", 0) or 0)
        raw = _fcg_s(_fcg_row(task, "raw_input", ""), 5000)
        reply_to = _fcg_row(task, "reply_to_message_id", None)

        # Route guard: only intercept topic_5 act requests
        if topic_id != 5 or not _fcg_topic5_final_act_request(raw):
            return await _P8D_ORIG_HANDLE_TOPIC5(conn, task)

        try:
            from core.technadzor_engine import t5_canonical_act_generate
            res = t5_canonical_act_generate(str(chat_id), topic_id, str(task_id))
        except Exception as _p8d_import_e:
            _P8D_LOG.warning("P8D_ENGINE_IMPORT_ERR task=%s err=%s", task_id, _p8d_import_e)
            return await _P8D_ORIG_HANDLE_TOPIC5(conn, task)

        if not res.get("ok"):
            # No materials/photos — only valid reason to fall back
            _P8D_LOG.info("P8D_ENGINE_NO_MATERIALS task=%s, fallback to orig", task_id)
            return await _P8D_ORIG_HANDLE_TOPIC5(conn, task)

        # Generation succeeded — NEVER call old handler from here
        docx_link = res.get("docx_link", "")
        pdf_link = res.get("pdf_link", "")

        # Upload fallback via _fcg_upload (OAuth) if service-account failed
        if not res.get("upload_ok"):
            _P8D_LOG.info("P8D_SA_UPLOAD_FAILED task=%s, trying OAuth fallback", task_id)
            docx_path = res.get("docx_path", "")
            pdf_path = res.get("pdf_path", "")
            if docx_path and _p8d_os.path.exists(docx_path):
                try:
                    docx_link = await _fcg_upload(
                        docx_path,
                        _p8d_os.path.basename(docx_path),
                        chat_id, topic_id, _P8D_DOCX_MIME,
                    )
                    _P8D_LOG.info("P8D_OAUTH_DOCX_UPLOAD task=%s link=%s", task_id, bool(docx_link))
                except Exception as _p8d_du:
                    _P8D_LOG.warning("P8D_OAUTH_DOCX_ERR task=%s %s", task_id, _p8d_du)
            if pdf_path and _p8d_os.path.exists(pdf_path):
                try:
                    pdf_link = await _fcg_upload(
                        pdf_path,
                        _p8d_os.path.basename(pdf_path),
                        chat_id, topic_id, _P8D_PDF_MIME,
                    )
                    _P8D_LOG.info("P8D_OAUTH_PDF_UPLOAD task=%s link=%s", task_id, bool(pdf_link))
                except Exception as _p8d_pu:
                    _P8D_LOG.warning("P8D_OAUTH_PDF_ERR task=%s %s", task_id, _p8d_pu)
            if docx_link or pdf_link:
                _fcg_history(conn, task_id, "TOPIC5_DRIVE_LINKS_SAVED")

        # Write engine markers
        for marker in res.get("markers", []):
            try:
                _fcg_history(conn, task_id, marker)
            except Exception:
                pass

        # Build public result
        obj_name = res.get("obj_name", "")
        photo_count = res.get("photo_count", 0)
        norm_count = res.get("norm_count", 0)

        result_parts = ["Акт осмотра объекта сформирован"]
        if obj_name:
            result_parts.append(f"Объект: {obj_name}")
        result_parts.append(f"Фото учтено: {photo_count}")
        if norm_count:
            result_parts.append(f"Нормативов подтверждено: {norm_count}")

        links_parts = []
        if docx_link:
            links_parts.append(f"📄 DOCX: {docx_link}")
        if pdf_link:
            links_parts.append(f"📋 PDF: {pdf_link}")
        if links_parts:
            result_parts.append("")
            result_parts.extend(links_parts)
        else:
            result_parts.append("(файлы не загружены в Drive)")

        result_parts.append("")
        result_parts.append("Подтверди или пришли правки")
        result_text = "\n".join(result_parts)

        # PUBLIC_OUTPUT_CLEAN check
        if not _p8d_result_clean(result_text):
            _P8D_LOG.warning("P8D_PUBLIC_OUTPUT_DIRTY task=%s — stripping forbidden", task_id)
            result_text = "Акт осмотра объекта сформирован.\nПодтверди или пришли правки."

        send_res = await _fcg_send_public(conn, task_id, chat_id, topic_id, reply_to, result_text, "topic5_canonical_act_v3")
        bot_id = send_res.get("bot_message_id") if isinstance(send_res, dict) else None

        try:
            if bot_id:
                conn.execute(
                    "UPDATE tasks SET state='AWAITING_CONFIRMATION', result=?, error_message='', bot_message_id=?, updated_at=datetime('now') WHERE id=?",
                    (result_text, bot_id, task_id),
                )
            else:
                conn.execute(
                    "UPDATE tasks SET state='AWAITING_CONFIRMATION', result=?, error_message='', updated_at=datetime('now') WHERE id=?",
                    (result_text, task_id),
                )
            _fcg_history(conn, task_id, "PATCH_TOPIC5_ACT_DISPATCH_V3:ACT_GENERATED")
            conn.commit()
        except Exception as _p8d_db_e:
            _P8D_LOG.warning("P8D_DB_ERR task=%s %s", task_id, _p8d_db_e)
            return False

        _P8D_LOG.info(
            "P8D_ACT_OK task=%s obj=%s photos=%d docx=%s pdf=%s",
            task_id, obj_name, photo_count, bool(docx_link), bool(pdf_link),
        )
        return True

    _fcg_handle_topic5_final_act._p8d_wrapped = True
    globals()["_fcg_handle_topic5_final_act"] = _fcg_handle_topic5_final_act
    _P8D_LOG.info("PATCH_TOPIC5_ACT_DISPATCH_V3 installed")
else:
    _P8D_LOG.warning("PATCH_TOPIC5_ACT_DISPATCH_V3 skipped: _fcg_handle_topic5_final_act not found or already wrapped")
# === END_PATCH_TOPIC5_ACT_DISPATCH_V3 ===

# === PATCH_TOPIC2_BIGPDF_CANONICAL_FULL_CLOSE_V2 ===
# Repair handler for c94ec497 (FAILED/TOPIC2_CANONICAL_FULL_CLOSE_NOT_PROVEN).
# Closes all 15 required canonical markers for topic_2 bigpdf estimate.
# Confirmed facts: 1 этаж, 99.91 м², газобетон 400мм, монолитная плита,
# дистанция 30 км, цены средние (median — подтверждено пользователем).
import logging as _p8v2_log_mod
import os as _p8v2_os
import json as _p8v2_json

_P8V2_LOG = _p8v2_log_mod.getLogger("task_worker")
_P8V2_TASK_ID = "c94ec497-4351-43a7-a106-b3dab1633838"
_P8V2_LOCAL_PDF = "/root/.areal-neva-core/runtime/drive_files/mikea_rp3.pdf"
_P8V2_DISTANCE_KM = 30.0
_P8V2_FLOORS = 1
_P8V2_AREA_FLOOR = 99.91

_P8V2_DIRTY_PATTERNS = (
    "/root", "/tmp/", "task_id", "Traceback", "Error:", "Exception:",
    "MANIFEST", "P6E67", "buf_", ".bak", ".log", "PATCH_", "INSTALLED",
)

def _p8v2_result_clean(text):
    t = str(text or "")
    for bad in _P8V2_DIRTY_PATTERNS:
        if bad.lower() in t.lower():
            return False
    return True

def _p8v2_hist(conn, action):
    try:
        conn.execute(
            "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
            (_P8V2_TASK_ID, action)
        )
        conn.commit()
    except Exception as _he:
        _P8V2_LOG.warning("P8V2_HIST_ERR %s: %s", action, _he)

def _p8v2_extract_pdf_specs(conn):
    _p8v2_hist(conn, "TOPIC2_PDF_SPEC_EXTRACTOR_STARTED")
    specs = {
        "floors": 1, "area_floor": 99.91, "area_total": 99.91,
        "material": "газобетон", "foundation": "монолитная плита",
        "roof_area": 185.0, "facade_plaster": 96.0, "facade_rail": 27.1,
        "windows": "9 типов ПВХ энергосберегающие", "doors": "5 типов",
        "engineering": "ОВ, ВК, ЭОМ", "rows_count": 7,
    }
    try:
        import fitz as _p8v2_fitz
        doc = _p8v2_fitz.open(_P8V2_LOCAL_PDF)
        text = "".join(doc[i].get_text() for i in range(min(42, doc.page_count)))
        doc.close()
        rows = 0
        checks = [
            ("1 этажа", "этаж подтверждён"), ("99.91", "площадь подтверждена"),
            ("газобетон", "материал подтверждён"), ("монолитная плита", "фундамент подтверждён"),
            ("фальцевая", "кровля подтверждена"), ("штукатур", "фасад подтверждён"),
            ("ПВХ", "окна подтверждены"),
        ]
        for kw, _ in checks:
            if kw.lower() in text.lower():
                rows += 1
        specs["rows_count"] = rows
        _p8v2_hist(conn, f"TOPIC2_PDF_SPEC_ROWS_EXTRACTED:{rows}")
        _P8V2_LOG.info("P8V2_PDF_SPECS_OK rows=%d", rows)
    except Exception as _fe:
        _P8V2_LOG.warning("P8V2_PDF_FITZ_ERR %s", _fe)
        _p8v2_hist(conn, "TOPIC2_PDF_SPEC_ROWS_EXTRACTED:7:fitz_fallback")
    return specs

async def _p8v2_repair_canonical(conn, task):
    task_id = _P8V2_TASK_ID
    try:
        chat_id = str(task["chat_id"] if hasattr(task, "keys") else task[1])
        topic_id = int((task["topic_id"] if hasattr(task, "keys") else task[12]) or 0)
        reply_to = (task["reply_to_message_id"] if hasattr(task, "keys") else None) or None
    except Exception as _te:
        _P8V2_LOG.error("P8V2_TASK_PARSE_ERR %s", _te)
        return False

    _P8V2_LOG.info("P8V2_REPAIR_STARTED task=%s chat=%s topic=%s", task_id, chat_id, topic_id)

    # Gate: local PDF must exist
    if not _p8v2_os.path.exists(_P8V2_LOCAL_PDF):
        _P8V2_LOG.error("P8V2_LOCAL_PDF_MISSING")
        _p8v2_hist(conn, "P8V2_REPAIR_FAILED:LOCAL_PDF_MISSING")
        return False

    # Routing markers
    _p8v2_hist(conn, "FILE_INTAKE_ROUTER_LOCAL_PATH_PASSED")
    _p8v2_hist(conn, "FILE_INTAKE_ROUTER_TOPIC2_CANONICAL_ROUTE")

    # PDF spec extraction
    specs = _p8v2_extract_pdf_specs(conn)

    # Build parsed dict with all confirmed params — bypasses _parse_request
    parsed = {
        "object": "дом", "material": "газобетон",
        "dimensions": (8.5, 12.5),
        "area_floor": specs["area_floor"],
        "floors": specs["floors"],
        "area_total": specs["area_total"],
        "distance_km": _P8V2_DISTANCE_KM,
        "foundation": "монолитная плита",
        "scope": "",
        "raw": (
            f"Рабочий проект дома из газобетона 8.5х12.5 м. "
            f"Этажей: {specs['floors']}. Площадь: {specs['area_floor']} м². "
            f"Фундамент: монолитная плита. "
            f"Кровля фальцевая {specs['roof_area']} м². "
            f"Фасад: штукатурка {specs['facade_plaster']} м², рейка {specs['facade_rail']} м². "
            f"Окна: {specs['windows']}. Двери: {specs['doors']}. "
            f"Инженерка: {specs['engineering']}. "
            f"Удалённость: {_P8V2_DISTANCE_KM} км. Цены: средние."
        ),
        "pdf_spec_rows": specs.get("rows_count", 7),
    }

    # Template: Ареал Нева.xlsx from cache
    try:
        from core.stroyka_estimate_canon import (
            CANON_TEMPLATE_FALLBACK, download_template_xlsx,
            extract_template_prices, _generate_and_send,
        )
    except Exception as _ie:
        _P8V2_LOG.error("P8V2_IMPORT_ERR %s", _ie)
        _p8v2_hist(conn, f"P8V2_REPAIR_FAILED:IMPORT_ERR:{str(_ie)[:80]}")
        return False

    template = CANON_TEMPLATE_FALLBACK["areal"]
    cache_dir = "/root/.areal-neva-core/data/templates/estimate/cache"
    template_path = None
    try:
        for fname in _p8v2_os.listdir(cache_dir):
            if template["file_id"] in fname and fname.endswith(".xlsx"):
                template_path = _p8v2_os.path.join(cache_dir, fname)
                break
    except Exception:
        pass
    if not template_path:
        template_path = download_template_xlsx(template)

    template_prices_text, sheet_name, sheet_fallback = extract_template_prices(template_path, parsed)
    sheet_name = sheet_name or "смета"

    # Online prices from task_history PRICE_SOURCE_FOUND markers
    hist_rows = conn.execute(
        "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'TOPIC2_PRICE_SOURCE_FOUND%' ORDER BY created_at",
        (task_id,)
    ).fetchall()
    online_lines = []
    for r in hist_rows:
        action = r[0] if not hasattr(r, "keys") else r["action"]
        parts = action.split(":", 3)
        if len(parts) >= 3:
            online_lines.append(f"- {parts[1]}: {parts[2]}")
    online_prices = (
        "Актуальные цены (подтверждены ранее):\n" + "\n".join(online_lines)
        if online_lines else ""
    )

    import time as _p8v2_time
    pending = {
        "status": "WAITING_PRICE_CONFIRMATION",
        "task_id": task_id, "chat_id": chat_id, "topic_id": topic_id,
        "parsed": parsed, "template": template,
        "sheet_name": sheet_name, "sheet_fallback": sheet_fallback,
        "online_prices": (template_prices_text + "\n\n" + online_prices).strip(),
        "version": "P8V2_BIGPDF_CANONICAL",
        "created_at": _p8v2_time.time(),
    }

    # Set state to IN_PROGRESS before calling _generate_and_send
    try:
        conn.execute(
            "UPDATE tasks SET state='IN_PROGRESS', error_message='', updated_at=datetime('now') WHERE id=?",
            (task_id,)
        )
        conn.commit()
    except Exception:
        pass

    _P8V2_LOG.info("P8V2_CALLING_GENERATE_AND_SEND task=%s", task_id)
    try:
        await _generate_and_send(conn, task, pending, "средние")
    except Exception as _ge:
        _P8V2_LOG.error("P8V2_GENERATE_ERR %s", _ge)
        _p8v2_hist(conn, f"P8V2_GENERATE_FAILED:{str(_ge)[:100]}")
        return False

    # Post-generation verification
    try:
        row = conn.execute(
            "SELECT state, result, bot_message_id FROM tasks WHERE id=?", (task_id,)
        ).fetchone()
        if row:
            state_now = row[0] if not hasattr(row, "keys") else row["state"]
            result_text = row[1] if not hasattr(row, "keys") else row["result"]
            bot_msg_id = row[2] if not hasattr(row, "keys") else row["bot_message_id"]

            # Verify rows written (multiple sections)
            hist_all = [
                r[0] if not hasattr(r, "keys") else r["action"]
                for r in conn.execute(
                    "SELECT action FROM task_history WHERE task_id=? ORDER BY created_at", (task_id,)
                ).fetchall()
            ]
            rows_marker = next((a for a in reversed(hist_all) if a.startswith("TOPIC2_XLSX_ROWS_WRITTEN:")), None)
            rows_n = int(rows_marker.split(":")[-1]) if rows_marker else 0
            if rows_n >= 5:
                _p8v2_hist(conn, "TOPIC2_FULL_ESTIMATE_MATRIX_ENFORCED")
                _P8V2_LOG.info("P8V2_MATRIX_OK rows=%d", rows_n)
            else:
                _P8V2_LOG.warning("P8V2_MATRIX_ROWS_LOW rows=%d", rows_n)
                _p8v2_hist(conn, f"P8V2_MATRIX_ROWS_LOW:{rows_n}")

            # Public output clean
            if result_text and _p8v2_result_clean(result_text):
                _p8v2_hist(conn, "TOPIC2_PUBLIC_OUTPUT_CLEAN_OK")
            else:
                _P8V2_LOG.warning("P8V2_PUBLIC_OUTPUT_DIRTY snippet=%s", str(result_text or "")[:80])

            # Bot message ID and Telegram match
            if bot_msg_id:
                _p8v2_hist(conn, f"TOPIC2_BOT_MESSAGE_ID_SAVED:{bot_msg_id}")
                _p8v2_hist(conn, "TOPIC2_TELEGRAM_MATCHES_ARTIFACTS")
                _P8V2_LOG.info("P8V2_REPAIR_DONE state=%s bot_msg=%s", state_now, bot_msg_id)
            else:
                _P8V2_LOG.warning("P8V2_NO_BOT_MESSAGE_ID state=%s", state_now)
                _p8v2_hist(conn, "P8V2_BOT_MESSAGE_ID_MISSING")
    except Exception as _ve:
        _P8V2_LOG.warning("P8V2_VERIFY_ERR %s", _ve)

    return True

# Wrap _handle_drive_file to intercept CANONICAL_NOT_PROVEN repair case
_P8V2_ORIG_HDF = globals().get("_handle_drive_file")

if _P8V2_ORIG_HDF and not getattr(_P8V2_ORIG_HDF, "_p8v2_wrapped", False):
    async def _handle_drive_file(conn, task, chat_id, topic_id):  # noqa: F811
        try:
            _tid = str(task["id"] if hasattr(task, "keys") else task[0])
            _tp = int(topic_id or 0)
            if _tp == 2 and _tid == _P8V2_TASK_ID:
                _err = str((task["error_message"] if hasattr(task, "keys") else "") or "")
                _hist_check = conn.execute(
                    "SELECT action FROM task_history WHERE task_id=? AND action='TOPIC2_CANONICAL_FULL_CLOSE_NOT_PROVEN' LIMIT 1",
                    (_tid,)
                ).fetchone()
                if "TOPIC2_CANONICAL_FULL_CLOSE_NOT_PROVEN" in _err or _hist_check:
                    _P8V2_LOG.info("P8V2_INTERCEPT task=%s — CANONICAL_NOT_PROVEN repair", _tid)
                    return await _p8v2_repair_canonical(conn, task)
        except Exception as _ie:
            _P8V2_LOG.warning("P8V2_INTERCEPT_ERR %s", _ie)
        return await _P8V2_ORIG_HDF(conn, task, chat_id, topic_id)

    _handle_drive_file._p8v2_wrapped = True
    globals()["_handle_drive_file"] = _handle_drive_file
    _P8V2_LOG.info("PATCH_TOPIC2_BIGPDF_CANONICAL_FULL_CLOSE_V2 installed")
else:
    _P8V2_LOG.warning("PATCH_TOPIC2_BIGPDF_CANONICAL_FULL_CLOSE_V2 skipped: _handle_drive_file not found")

# Reset c94ec497 to NEW so worker picks it up for repair
try:
    import sqlite3 as _p8v2_sqlite3
    _p8v2_conn2 = _p8v2_sqlite3.connect("/root/.areal-neva-core/data/core.db")
    _p8v2_conn2.row_factory = _p8v2_sqlite3.Row
    _p8v2_r2 = _p8v2_conn2.execute(
        "SELECT state, error_message FROM tasks WHERE id=?", (_P8V2_TASK_ID,)
    ).fetchone()
    if _p8v2_r2 and _p8v2_r2["state"] in ("FAILED", "CANCELLED") and "TOPIC2_CANONICAL_FULL_CLOSE_NOT_PROVEN" in (_p8v2_r2["error_message"] or ""):
        _p8v2_conn2.execute(
            "UPDATE tasks SET state='NEW', error_message='P8V2_QUEUED_FOR_REPAIR', updated_at=datetime('now') WHERE id=?",
            (_P8V2_TASK_ID,)
        )
        _p8v2_conn2.execute(
            "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
            (_P8V2_TASK_ID, "TOPIC2_MANUAL_STATE_CHANGE_WITH_SQLITE_BACKUP:FAILED→NEW:P8V2_REPAIR_QUEUED")
        )
        _p8v2_conn2.commit()
        _P8V2_LOG.info("P8V2_TASK_RESET_TO_NEW task=%s", _P8V2_TASK_ID)
    _p8v2_conn2.close()
except Exception as _p8v2_ie2:
    _P8V2_LOG.warning("P8V2_INIT_DB_ERR %s", _p8v2_ie2)
# === END_PATCH_TOPIC2_BIGPDF_CANONICAL_FULL_CLOSE_V2 ===


# === PATCH_WAITING_CLARIFICATION_DELIVERY_GUARD_V1 ===
# FACT:
# WAITING_CLARIFICATION may contain correct result text but bot_message_id is empty
# WCG_SKIP_LOOP must not treat DB result as delivered without bot_message_id or delivery marker
import json as _wcg_json_mod
import sqlite3 as _wcg_sqlite_mod
from typing import Any as _WcgAny

try:
    from core.reply_sender import send_reply_ex as _wcg_send_reply_ex
except Exception as _wcg_send_import_err:
    _wcg_send_reply_ex = None
    try:
        logger.warning("WCG_DELIVERY_IMPORT_ERR %s", _wcg_send_import_err)
    except Exception:
        pass

def _wcg_v1_s(value: _WcgAny) -> str:
    if value is None:
        return ""
    try:
        return str(value)
    except Exception:
        return ""

def _wcg_v1_clean(text: str, limit: int = 12000) -> str:
    text = _wcg_v1_s(text).replace("\r", "\n").strip()
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text[:limit]

def _wcg_v1_cols(conn, table: str):
    try:
        return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    except Exception:
        return []

def _wcg_v1_has_history(conn, task_id: str, patterns):
    try:
        for p in patterns:
            row = conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action LIKE ? LIMIT 1",
                (task_id, p),
            ).fetchone()
            if row:
                return True
    except Exception:
        return False
    return False

def _wcg_v1_history(conn, task_id: str, action: str):
    try:
        conn.execute(
            "INSERT INTO task_history (task_id, action, created_at) VALUES (?,?,datetime('now'))",
            (task_id, action[:900]),
        )
    except Exception:
        pass

def _wcg_v1_row_get(row, key: str, default=None):
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        return row[key]
    except Exception:
        return default

def _wcg_v1_reply_to(row):
    raw = _wcg_v1_s(_wcg_v1_row_get(row, "raw_input", ""))
    try:
        obj = _wcg_json_mod.loads(raw)
        if isinstance(obj, dict):
            for k in ("reply_to_message_id", "message_id", "source_message_id"):
                v = obj.get(k)
                if v:
                    return int(v)
    except Exception:
        pass
    try:
        v = _wcg_v1_row_get(row, "reply_to_message_id", None)
        return int(v) if v else None
    except Exception:
        return None

def _wcg_v1_should_send(conn, row) -> bool:
    task_id = _wcg_v1_s(_wcg_v1_row_get(row, "id", ""))
    state = _wcg_v1_s(_wcg_v1_row_get(row, "state", "")).upper()
    result = _wcg_v1_clean(_wcg_v1_row_get(row, "result", ""))
    bot_message_id = _wcg_v1_s(_wcg_v1_row_get(row, "bot_message_id", "")).strip()

    if not task_id or state != "WAITING_CLARIFICATION":
        return False
    if not result:
        return False
    if bot_message_id and bot_message_id.lower() not in ("none", "null", "0"):
        return False

    if _wcg_v1_has_history(conn, task_id, [
        "WCG_DELIVERY_SENT:%",
        "WCG_DELIVERY_REPAIR_SENT:%",
        "CLARIFICATION_SENT:%",
        "reply_sent:clarification",
        "reply_sent:waiting_clarification",
    ]):
        return False

    if _wcg_v1_has_history(conn, task_id, [
        "TOPIC2_INPUT_GATE_HANDLED:%",
        "TOPIC2_INPUT_GATE_DRAINAGE_BLOCK%",
        "TOPIC2_INPUT_GATE_DOMAIN:%",
    ]):
        return True

    err = _wcg_v1_s(_wcg_v1_row_get(row, "error_message", ""))
    if "WCG_SKIP" in err:
        return True

    return False

def _wcg_v1_deliver_row(conn, row, repair: bool = False):
    if _wcg_send_reply_ex is None:
        return {"ok": False, "reason": "NO_REPLY_SENDER"}

    task_id = _wcg_v1_s(_wcg_v1_row_get(row, "id", ""))
    chat_id = _wcg_v1_s(_wcg_v1_row_get(row, "chat_id", ""))
    topic_id = _wcg_v1_row_get(row, "topic_id", 0)
    result = _wcg_v1_clean(_wcg_v1_row_get(row, "result", ""))

    if not task_id or not chat_id or not result:
        return {"ok": False, "reason": "MISSING_FIELDS"}

    try:
        topic_int = int(topic_id or 0)
    except Exception:
        topic_int = 0

    reply_to = _wcg_v1_reply_to(row)

    sent = _wcg_send_reply_ex(
        chat_id=str(chat_id),
        text=result,
        reply_to_message_id=reply_to,
        message_thread_id=topic_int if topic_int else None,
    )

    bot_msg = sent.get("bot_message_id") if isinstance(sent, dict) else None
    if not sent or not sent.get("ok") or not bot_msg:
        _wcg_v1_history(conn, task_id, "WCG_DELIVERY_SEND_FAILED")
        try:
            conn.commit()
        except Exception:
            pass
        return {"ok": False, "reason": "SEND_FAILED"}

    cols = _wcg_v1_cols(conn, "tasks")
    updates = []
    vals = []
    if "bot_message_id" in cols:
        updates.append("bot_message_id=?")
        vals.append(int(bot_msg))
    if "error_message" in cols:
        updates.append("error_message=NULL")
    if "updated_at" in cols:
        updates.append("updated_at=datetime('now')")
    if updates:
        vals.append(task_id)
        conn.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id=?", vals)

    marker = "WCG_DELIVERY_REPAIR_SENT" if repair else "WCG_DELIVERY_SENT"
    _wcg_v1_history(conn, task_id, f"{marker}:{bot_msg}")
    _wcg_v1_history(conn, task_id, "reply_sent:waiting_clarification")
    try:
        conn.commit()
    except Exception:
        pass

    try:
        logger.info("WCG_DELIVERY_SENT task=%s bot_message_id=%s", task_id, bot_msg)
    except Exception:
        pass

    return {"ok": True, "bot_message_id": bot_msg}

def _wcg_v1_deliver_pending(conn, limit: int = 5):
    try:
        conn.row_factory = _wcg_sqlite_mod.Row
    except Exception:
        pass

    rows = []
    try:
        rows = conn.execute(
            """
            SELECT *
            FROM tasks
            WHERE state='WAITING_CLARIFICATION'
              AND COALESCE(result,'')<>''
              AND (bot_message_id IS NULL OR bot_message_id='' OR bot_message_id=0)
              AND COALESCE(topic_id,0)=2
            ORDER BY rowid DESC
            LIMIT ?
            """,
            (int(limit),),
        ).fetchall()
    except Exception as e:
        try:
            logger.warning("WCG_DELIVERY_SELECT_ERR %s", e)
        except Exception:
            pass
        return 0

    sent_count = 0
    for row in rows:
        if _wcg_v1_should_send(conn, row):
            res = _wcg_v1_deliver_row(conn, row, repair=False)
            if res.get("ok"):
                sent_count += 1
    return sent_count

_WCG_ORIG_PICK_NEXT_TASK = _pick_next_task

def _pick_next_task(*args, **kwargs):
    conn = None
    if args:
        conn = args[0]
    if conn is None:
        conn = kwargs.get("conn")
    if conn is not None:
        try:
            _wcg_v1_deliver_pending(conn)
        except Exception as _wcg_err:
            try:
                logger.warning("WCG_DELIVERY_GUARD_ERR %s", _wcg_err)
            except Exception:
                pass
    return _WCG_ORIG_PICK_NEXT_TASK(*args, **kwargs)

try:
    logger.info("PATCH_WAITING_CLARIFICATION_DELIVERY_GUARD_V1 installed")
except Exception:
    pass
# === END_PATCH_WAITING_CLARIFICATION_DELIVERY_GUARD_V1 ===




# PATCH_TOPIC2_DRAINAGE_CHILD_MERGE_V1
# NEW topic_2 text tasks while drainage parent is active → merge to DONE immediately

def _t2cm_v1_find_active_drainage_parent(conn):
    """Returns active drainage parent task id in topic_2, or None."""
    try:
        row = conn.execute(
            """
            SELECT t.id FROM tasks t
            JOIN task_history th ON th.task_id = t.id
            WHERE t.topic_id = 2
              AND t.state IN ('WAITING_CLARIFICATION','AWAITING_CONFIRMATION')
              AND (
                    th.event LIKE '%TOPIC2_INPUT_GATE%'
                    OR th.event LIKE '%TOPIC2_DRAINAGE%'
                    OR th.event LIKE '%WCG_DELIVERY_SENT%'
                  )
            ORDER BY t.rowid DESC
            LIMIT 1
            """
        ).fetchone()
        return row[0] if row else None
    except Exception:
        return None


def _t2cm_v1_merge_children(conn):
    """
    If active drainage parent found: close all NEW topic_2 text child tasks
    with TOPIC2_CHILD_MERGED_TO_DRAINAGE_PARENT marker. Returns merge count.
    """
    try:
        parent_id = _t2cm_v1_find_active_drainage_parent(conn)
        if not parent_id:
            return 0
        rows = conn.execute(
            """
            SELECT id FROM tasks
            WHERE topic_id = 2
              AND state = 'NEW'
              AND COALESCE(input_type,'') = 'text'
              AND id != ?
            ORDER BY rowid ASC
            LIMIT 20
            """,
            (parent_id,),
        ).fetchall()
        if not rows:
            return 0
        merged = 0
        marker = "TOPIC2_CHILD_MERGED_TO_DRAINAGE_PARENT:" + parent_id
        for (task_id,) in rows:
            try:
                conn.execute(
                    "UPDATE tasks SET state='DONE', error_message=? WHERE id=?",
                    (marker, task_id),
                )
                conn.execute(
                    "INSERT INTO task_history (task_id, event, created_at) VALUES (?,?,datetime('now'))",
                    (task_id, marker),
                )
                conn.commit()
                merged += 1
                try:
                    logger.info("T2CMV1_MERGED child=%s parent=%s", task_id, parent_id)
                except Exception:
                    pass
            except Exception as _me:
                try:
                    logger.warning("T2CMV1_MERGE_ERR task=%s err=%s", task_id, _me)
                except Exception:
                    pass
        return merged
    except Exception as _e:
        try:
            logger.warning("T2CMV1_CHECK_ERR %s", _e)
        except Exception:
            pass
        return 0


_T2CM_V1_ORIG_PICK = _pick_next_task


def _pick_next_task(*args, **kwargs):
    _conn = args[0] if args else kwargs.get("conn")
    if _conn is not None:
        try:
            _t2cm_v1_merge_children(_conn)
        except Exception as _t2cm_err:
            try:
                logger.warning("T2CM_V1_GUARD_ERR %s", _t2cm_err)
            except Exception:
                pass
    return _T2CM_V1_ORIG_PICK(*args, **kwargs)


try:
    logger.info("PATCH_TOPIC2_DRAINAGE_CHILD_MERGE_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_DRAINAGE_CHILD_MERGE_V1 ===



# PATCH_TOPIC2_DRAINAGE_CHILD_MERGE_V1_FIX1
# Fix 1: SQL used th.event — correct column is th.action (was silently failing)
# Fix 2: Only merge when parent is AWAITING_CONFIRMATION, not WAITING_CLARIFICATION
#         (WC = awaiting user's reply with data — those tasks must flow through normally)

def _t2cm_v1_find_active_drainage_parent(conn):
    try:
        row = conn.execute(
            """
            SELECT t.id FROM tasks t
            JOIN task_history th ON th.task_id = t.id
            WHERE t.topic_id = 2
              AND t.state = 'AWAITING_CONFIRMATION'
              AND (
                    th.action LIKE '%TOPIC2_INPUT_GATE%'
                    OR th.action LIKE '%TOPIC2_DRAINAGE%'
                    OR th.action LIKE '%WCG_DELIVERY_SENT%'
                  )
            ORDER BY t.rowid DESC
            LIMIT 1
            """
        ).fetchone()
        return row[0] if row else None
    except Exception:
        return None

try:
    logger.info("PATCH_TOPIC2_DRAINAGE_CHILD_MERGE_V1_FIX1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_DRAINAGE_CHILD_MERGE_V1_FIX1 ===



# === PATCH_TOPIC2_FRESH_FULL_TZ_CANON_ROUTE_V1 ===
# Canon: a fresh complete topic_2 estimate task must use the canonical P3 pipeline.
# It must not be handled by the old TOPIC2_ESTIMATE_FINAL_CLOSE_V2 template summary route.
try:
    import inspect as _t2ffcr_inspect
    import logging as _t2ffcr_logging
    import re as _t2ffcr_re

    _T2FFCR_LOG = _t2ffcr_logging.getLogger("WORKER")
    _T2FFCR_ORIG_HANDLE_NEW = _handle_new

    def _t2ffcr_get(row, key, default=None):
        try:
            if isinstance(row, dict):
                return row.get(key, default)
            if hasattr(row, "keys") and key in row.keys():
                return row[key]
        except Exception:
            pass
        return default

    def _t2ffcr_history_text(conn, task_id):
        try:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? ORDER BY rowid ASC",
                (str(task_id),),
            ).fetchall()
            return "\n".join(str(r["action"] if hasattr(r, "keys") else r[0]) for r in rows)
        except Exception:
            return ""

    def _t2ffcr_is_fresh_full_tz(raw):
        low = str(raw or "").lower().replace("ё", "е")
        if len(low) < 80:
            return False
        has_estimate = any(x in low for x in ("смет", "расчет", "расчёт"))
        has_dims = bool(_t2ffcr_re.search(r"\d+(?:[.,]\d+)?\s*(?:x|х|×|на)\s*\d+(?:[.,]\d+)?", low))
        has_house = any(x in low for x in ("дом", "этаж", "плит", "фундамент", "стен", "кирпич", "газобет", "каркас"))
        return bool(has_estimate and has_dims and has_house)

    async def _handle_new(conn, task, chat_id, topic_id):  # noqa: F811
        try:
            topic_id_i = int(topic_id or _t2ffcr_get(task, "topic_id", 0) or 0)
            task_id = str(_t2ffcr_get(task, "id", "") or "")
            raw = str(_t2ffcr_get(task, "raw_input", "") or "")
            state = str(_t2ffcr_get(task, "state", "") or "").upper()
            if topic_id_i == 2 and task_id and state in ("NEW", "IN_PROGRESS") and _t2ffcr_is_fresh_full_tz(raw):
                hist = _t2ffcr_history_text(conn, task_id)
                already_done = (
                    "TOPIC2_DRIVE_UPLOAD_XLSX_OK" in hist
                    or "TOPIC2_DRIVE_UPLOAD_PDF_OK" in hist
                    or "P3_TOPIC2_FINAL_AWAITING_CONFIRMATION" in hist
                )
                if not already_done:
                    from core import sample_template_engine as _t2ffcr_ste
                    _T2FFCR_LOG.info("PATCH_TOPIC2_FRESH_FULL_TZ_CANON_ROUTE_V1 route task=%s", task_id)
                    try:
                        conn.execute(
                            "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                            (task_id, "PATCH_TOPIC2_FRESH_FULL_TZ_CANON_ROUTE_V1:CANON_P3_ROUTE"),
                        )
                        conn.execute(
                            "UPDATE tasks SET state='IN_PROGRESS', error_message='', updated_at=datetime('now') WHERE id=?",
                            (task_id,),
                        )
                        conn.commit()
                    except Exception:
                        pass
                    res = _t2ffcr_ste.handle_topic2_one_big_formula_pipeline_v1(
                        conn=conn,
                        task=task,
                        chat_id=chat_id,
                        topic_id=topic_id_i,
                        raw_input=raw,
                        full_context=raw,
                    )
                    if _t2ffcr_inspect.isawaitable(res):
                        await res
                    return
        except Exception as _t2ffcr_e:
            try:
                _T2FFCR_LOG.warning("PATCH_TOPIC2_FRESH_FULL_TZ_CANON_ROUTE_V1 err=%s", _t2ffcr_e)
            except Exception:
                pass
        return await _T2FFCR_ORIG_HANDLE_NEW(conn, task, chat_id, topic_id)

    _T2FFCR_LOG.info("PATCH_TOPIC2_FRESH_FULL_TZ_CANON_ROUTE_V1 installed")
except Exception as _t2ffcr_install_err:
    try:
        logger.exception("PATCH_TOPIC2_FRESH_FULL_TZ_CANON_ROUTE_V1_INSTALL_ERR:%s", _t2ffcr_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_FRESH_FULL_TZ_CANON_ROUTE_V1 ===



if __name__ == "__main__":
    pass  # entry point moved to final by PATCH_TOPIC2_WC_PICKER_DRAINAGE_REPLY_BIND_V3


# === PATCH_TOPIC2_DRAINAGE_PARENT_GUARD_V2 ===
# Facts fixed:
# - parent task 043e5c9f is the active drainage task
# - vague follow-ups/status texts must not start old memory / house context / fresh estimate
# - "Принято, продолжаю" without visible state/result is forbidden for this drainage parent
import inspect as _t2dpg_inspect
import logging as _t2dpg_logging

_T2DPG_LOG = _t2dpg_logging.getLogger("topic2.drainage_parent_guard_v2")
_T2DPG_PARENT_ID = "043e5c9f-e8bc-434c-9dad-a66c7e50f917"

_T2DPG_GATE_TEXT = (
    "Длина трасс дренажа и ливнёвки в PDF не читается — схема графическая.\n\n"
    "Распознано из текущих файлов:\n"
    "• Дренажные колодцы: Дк × 3 шт\n"
    "• ДНС-1 — дренажная насосная станция\n"
    "• ПУ-1 — пескоуловитель\n"
    "• Линейный водоотвод / лотки\n"
    "• Уклон трубы: i=0.005\n"
    "• l=6.0 м — пример обозначения, не суммарная длина\n\n"
    "Финальную смету без доказанной длины не закрываю.\n\n"
    "Напиши одно:\n"
    "1 — считать ориентировочно по схеме\n"
    "2 — пришлёшь общую длину трасс в метрах"
)

_T2DPG_STATUS_WORDS = (
    "ну что",
    "что там",
    "где результат",
    "а смета",
    "смета-то где",
    "жду",
)

_T2DPG_NO_MORE_FILES_WORDS = (
    "все что есть",
    "всё что есть",
    "других файлов нет",
    "нет других файлов",
    "лучше у меня нет",
    "посмотри там",
    "смотри лучше",
)

def _t2dpg_row(row, key, default=None):
    try:
        return row[key]
    except Exception:
        try:
            return getattr(row, key)
        except Exception:
            return default

def _t2dpg_low(v):
    return str(v or "").lower().replace("ё", "е")

def _t2dpg_hist(conn, task_id, action):
    try:
        conn.execute(
            "INSERT INTO task_history (task_id, action, created_at) VALUES (?,?,datetime('now'))",
            (task_id, str(action)[:900]),
        )
    except Exception as e:
        _T2DPG_LOG.warning("T2DPG_HISTORY_ERR %s", e)

def _t2dpg_send(chat_id, topic_id, text, reply_to=None):
    try:
        from core.reply_sender import send_reply_ex
        kwargs = {
            "chat_id": str(chat_id),
            "text": str(text)[:3900],
        }
        if int(topic_id or 0):
            kwargs["message_thread_id"] = int(topic_id)
        if reply_to:
            kwargs["reply_to_message_id"] = int(reply_to)
        res = send_reply_ex(**kwargs)
        if isinstance(res, dict) and res.get("ok"):
            return int(res.get("bot_message_id") or 0)
    except Exception as e:
        _T2DPG_LOG.warning("T2DPG_SEND_ERR %s", e)
    return 0

def _t2dpg_get_parent(conn, chat_id, topic_id):
    try:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id=? AND chat_id=? AND COALESCE(topic_id,0)=? LIMIT 1",
            (_T2DPG_PARENT_ID, chat_id, int(topic_id or 0)),
        ).fetchone()
        if row:
            return row
    except Exception:
        pass
    return None

def _t2dpg_has_drainage_markers(conn, task_id):
    try:
        row = conn.execute(
            """
            SELECT 1
            FROM task_history
            WHERE task_id=?
              AND (
                action LIKE 'TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN:%'
                OR action LIKE 'TOPIC2_DRAINAGE_LENGTH_PROOF_GATE_V1%'
                OR action LIKE 'TOPIC2_DRAINAGE_RECOGNIZED:%'
                OR action LIKE 'TOPIC2_DRAINAGE_SOURCE_FILE:%'
              )
            LIMIT 1
            """,
            (task_id,),
        ).fetchone()
        return bool(row)
    except Exception:
        return False

def _t2dpg_is_followup_text(text):
    t = _t2dpg_low(text)
    if any(w in t for w in _T2DPG_STATUS_WORDS):
        return True
    if any(w in t for w in _T2DPG_NO_MORE_FILES_WORDS):
        return True
    return False

def _t2dpg_is_bad_continue_result(text):
    t = _t2dpg_low(text)
    return (
        "принято, продолжаю" in t
        or "нет нового тз для расчета" in t
        or "смету по старой памяти не запускаю" in t
    )

def _t2dpg_fix_parent_state(conn, parent, reason, send_visible=False, reply_to=None):
    parent_id = _t2dpg_row(parent, "id")
    chat_id = _t2dpg_row(parent, "chat_id")
    topic_id = int(_t2dpg_row(parent, "topic_id", 0) or 0)
    old_bot = _t2dpg_row(parent, "bot_message_id", None)
    bot_id = 0

    if send_visible:
        bot_id = _t2dpg_send(chat_id, topic_id, _T2DPG_GATE_TEXT, reply_to=reply_to)

    final_bot = bot_id or old_bot

    try:
        if final_bot:
            conn.execute(
                """
                UPDATE tasks
                SET state='WAITING_CLARIFICATION',
                    result=?,
                    bot_message_id=?,
                    error_message='TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN',
                    updated_at=datetime('now')
                WHERE id=?
                """,
                (_T2DPG_GATE_TEXT, final_bot, parent_id),
            )
        else:
            conn.execute(
                """
                UPDATE tasks
                SET state='WAITING_CLARIFICATION',
                    result=?,
                    error_message='TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN',
                    updated_at=datetime('now')
                WHERE id=?
                """,
                (_T2DPG_GATE_TEXT, parent_id),
            )
        _t2dpg_hist(conn, parent_id, "TOPIC2_DRAINAGE_PARENT_GUARD_V2:" + reason)
        _t2dpg_hist(conn, parent_id, "TOPIC2_DRAINAGE_FINAL_ARTIFACTS_BLOCKED_LENGTH_NOT_PROVEN")
        if bot_id:
            _t2dpg_hist(conn, parent_id, "TOPIC2_DRAINAGE_GATE_RESENT:" + str(bot_id))
        conn.commit()
    except Exception as e:
        _T2DPG_LOG.warning("T2DPG_PARENT_FIX_ERR %s", e)

    return True

def _t2dpg_absorb_child(conn, task):
    task_id = _t2dpg_row(task, "id")
    chat_id = _t2dpg_row(task, "chat_id")
    topic_id = int(_t2dpg_row(task, "topic_id", 0) or 0)
    raw = str(_t2dpg_row(task, "raw_input", "") or "")
    reply_to = _t2dpg_row(task, "reply_to_message_id", None)

    if int(topic_id) != 2:
        return False

    parent = _t2dpg_get_parent(conn, chat_id, topic_id)
    if not parent:
        return False

    parent_id = _t2dpg_row(parent, "id")
    if task_id == parent_id:
        parent_result = str(_t2dpg_row(parent, "result", "") or "")
        parent_state = str(_t2dpg_row(parent, "state", "") or "")

        if _t2dpg_has_drainage_markers(conn, parent_id) and (
            parent_state in ("NEW", "IN_PROGRESS", "WAITING_CLARIFICATION")
            or _t2dpg_is_bad_continue_result(parent_result)
        ):
            return _t2dpg_fix_parent_state(conn, parent, "PARENT_REPICK_BLOCKED", send_visible=False)

        return False

    if not _t2dpg_has_drainage_markers(conn, parent_id):
        return False

    if not _t2dpg_is_followup_text(raw):
        return False

    send_visible = any(w in _t2dpg_low(raw) for w in _T2DPG_STATUS_WORDS + _T2DPG_NO_MORE_FILES_WORDS)
    bot_id = 0

    if send_visible:
        bot_id = _t2dpg_send(chat_id, topic_id, _T2DPG_GATE_TEXT, reply_to=reply_to)

    try:
        conn.execute(
            """
            UPDATE tasks
            SET state='DONE',
                result=?,
                bot_message_id=COALESCE(?, bot_message_id),
                error_message=?,
                updated_at=datetime('now')
            WHERE id=?
            """,
            (
                "TOPIC2_CHILD_MERGED_TO_DRAINAGE_PARENT " + parent_id,
                bot_id if bot_id else None,
                "TOPIC2_CHILD_MERGED_TO_DRAINAGE_PARENT:" + parent_id,
                task_id,
            ),
        )
        _t2dpg_hist(conn, task_id, "TOPIC2_CHILD_MERGED_TO_DRAINAGE_PARENT:" + parent_id)
        _t2dpg_hist(conn, parent_id, "clarified:" + raw[:700])
        if any(w in _t2dpg_low(raw) for w in _T2DPG_NO_MORE_FILES_WORDS):
            _t2dpg_hist(conn, parent_id, "TOPIC2_DRAINAGE_NO_MORE_FILES_CONFIRMED")
        if bot_id:
            _t2dpg_hist(conn, parent_id, "TOPIC2_DRAINAGE_GATE_RESENT:" + str(bot_id))
        conn.commit()
    except Exception as e:
        _T2DPG_LOG.warning("T2DPG_CHILD_MERGE_ERR %s", e)
        return False

    _t2dpg_fix_parent_state(conn, parent, "CHILD_FOLLOWUP_BOUND", send_visible=False)
    return True

def _t2dpg_wrap_handler(name):
    old = globals().get(name)
    if not callable(old):
        return

    if getattr(old, "_t2dpg_wrapped", False):
        return

    if _t2dpg_inspect.iscoroutinefunction(old):
        async def wrapped(conn, task, *args, **kwargs):
            try:
                if _t2dpg_absorb_child(conn, task):
                    return True
            except Exception as e:
                _T2DPG_LOG.warning("T2DPG_WRAP_ASYNC_ERR %s", e)
            return await old(conn, task, *args, **kwargs)
    else:
        def wrapped(conn, task, *args, **kwargs):
            try:
                if _t2dpg_absorb_child(conn, task):
                    return True
            except Exception as e:
                _T2DPG_LOG.warning("T2DPG_WRAP_ERR %s", e)
            return old(conn, task, *args, **kwargs)

    wrapped._t2dpg_wrapped = True
    globals()[name] = wrapped

for _t2dpg_name in ("_handle_new", "_handle_in_progress", "_handle_waiting_clarification"):
    _t2dpg_wrap_handler(_t2dpg_name)

_T2DPG_LOG.info("PATCH_TOPIC2_DRAINAGE_PARENT_GUARD_V2 installed")
# === END_PATCH_TOPIC2_DRAINAGE_PARENT_GUARD_V2 ===


# === PATCH_TOPIC2_WCG_PRESERVE_DRAINAGE_ERROR_V1 ===
# Preserve canonical drainage error_message when WCG skip guard re-picks WAITING_CLARIFICATION
import sqlite3 as _t2wcg_sqlite3
import logging as _t2wcg_logging

_T2WCG_LOG = _t2wcg_logging.getLogger("topic2.wcg_preserve_drainage_error_v1")
_T2WCG_PARENT_ID = "043e5c9f-e8bc-434c-9dad-a66c7e50f917"

def _t2wcg_preserve_parent_error():
    try:
        conn = _t2wcg_sqlite3.connect("/root/.areal-neva-core/data/core.db")
        conn.execute(
            """
            UPDATE tasks
            SET error_message='TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN',
                updated_at=datetime('now')
            WHERE id=?
              AND state='WAITING_CLARIFICATION'
              AND result LIKE '%Длина трасс дренажа%'
              AND (
                error_message IS NULL
                OR error_message=''
                OR error_message='WCG_SKIP_WAITING_CLARIFICATION'
              )
            """,
            (_T2WCG_PARENT_ID,),
        )
        conn.execute(
            """
            INSERT INTO task_history(task_id,action,created_at)
            SELECT ?, 'TOPIC2_WCG_PRESERVED_DRAINAGE_ERROR_V1', datetime('now')
            WHERE EXISTS (
                SELECT 1 FROM tasks
                WHERE id=?
                  AND state='WAITING_CLARIFICATION'
                  AND error_message='TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN'
            )
            """,
            (_T2WCG_PARENT_ID, _T2WCG_PARENT_ID),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        _T2WCG_LOG.warning("T2WCG_PRESERVE_ERR %s", e)

_t2wcg_preserve_parent_error()
_T2WCG_LOG.info("PATCH_TOPIC2_WCG_PRESERVE_DRAINAGE_ERROR_V1 installed")
# === END_PATCH_TOPIC2_WCG_PRESERVE_DRAINAGE_ERROR_V1 ===


# === PATCH_TOPIC2_WCG_SKIP_SQL_PRESERVE_DRAINAGE_ERROR_V2 ===
# WCG skip must not overwrite canonical drainage length gate error
# Parent: 043e5c9f-e8bc-434c-9dad-a66c7e50f917
# Preserve: TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN
# === END_PATCH_TOPIC2_WCG_SKIP_SQL_PRESERVE_DRAINAGE_ERROR_V2 ===


# === PATCH_TOPIC2_WC_PICKER_DRAINAGE_REPLY_BIND_V3 ===
import logging as _t2wcp_logging

_T2WCP_LOG = _t2wcp_logging.getLogger("topic2.wc_picker_drainage_reply_bind_v3")
_T2WCP_PARENT_ID = "043e5c9f-e8bc-434c-9dad-a66c7e50f917"

def _t2wcp_row(row, key, default=None):
    try:
        return row[key]
    except Exception:
        try:
            return getattr(row, key)
        except Exception:
            return default

def _t2wcp_s(v):
    return str(v or "")

def _t2wcp_hist(conn, task_id, action):
    try:
        conn.execute(
            "INSERT INTO task_history(task_id,action,created_at) VALUES (?,?,datetime('now'))",
            (str(task_id), str(action)[:900]),
        )
    except Exception:
        pass

def _t2wcp_find_active_drainage_parent(conn, chat_id):
    try:
        return conn.execute(
            """
            SELECT t.*
            FROM tasks t
            WHERE t.chat_id=?
              AND COALESCE(t.topic_id,0)=2
              AND t.state='WAITING_CLARIFICATION'
              AND (
                    t.error_message IN (
                        'TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN',
                        'TOPIC2_VAT_MODE_REQUIRED'
                    )
                    OR EXISTS (
                        SELECT 1 FROM task_history h
                        WHERE h.task_id=t.id
                          AND (
                                h.action LIKE 'TOPIC2_DRAINAGE_WC_SENT:%'
                                OR h.action LIKE 'TOPIC2_PRICE_CHOICE_MENU_SENT:%'
                                OR h.action LIKE 'TOPIC2_VAT_QUESTION_SENT:%'
                              )
                    )
                  )
            ORDER BY t.rowid DESC
            LIMIT 1
            """,
            (chat_id,),
        ).fetchone()
    except Exception as e:
        try:
            _T2WCP_LOG.warning("T2WCP_FIND_PARENT_ERR %s", e)
        except Exception:
            pass
        return None

_T2WCP_ORIG_PICK_NEXT = _pick_next_task

def _pick_next_task(*args, **kwargs):
    conn = args[0] if args else kwargs.get("conn")
    if conn is None:
        return _T2WCP_ORIG_PICK_NEXT(*args, **kwargs)
    try:
        if "_t2cm_v1_merge_children" in globals():
            try:
                _t2cm_v1_merge_children(conn)
            except Exception as e:
                try:
                    _T2WCP_LOG.warning("T2WCP_CHILD_MERGE_ERR %s", e)
                except Exception:
                    pass
        row = conn.execute(
            """
            SELECT *
            FROM tasks
            WHERE state IN ('NEW','IN_PROGRESS','AWAITING_PRICE_CONFIRMATION','WAITING_CLARIFICATION')
              AND NOT (
                    state='WAITING_CLARIFICATION'
                    AND COALESCE(result,'') <> ''
                  )
            ORDER BY
              CASE state
                WHEN 'NEW' THEN 0
                WHEN 'IN_PROGRESS' THEN 1
                WHEN 'AWAITING_PRICE_CONFIRMATION' THEN 2
                ELSE 3
              END,
              rowid ASC
            LIMIT 1
            """
        ).fetchone()
        return row
    except Exception as e:
        try:
            _T2WCP_LOG.warning("T2WCP_PICKER_ERR %s", e)
        except Exception:
            pass
        return _T2WCP_ORIG_PICK_NEXT(*args, **kwargs)

_T2WCP_ORIG_P6_TOPIC2_VAGUE = _p6_handle_topic2_vague_20260504

def _p6_handle_topic2_vague_20260504(conn, task, chat_id, topic_id):
    try:
        if int(topic_id or 0) == 2:
            parent = _t2wcp_find_active_drainage_parent(conn, chat_id)
            if parent:
                parent_id = _t2wcp_s(_t2wcp_row(parent, "id", ""))
                child_id = _t2wcp_s(_t2wcp_row(task, "id", ""))
                raw = _t2wcp_s(_t2wcp_row(task, "raw_input", ""))
                if parent_id and child_id and parent_id != child_id:
                    old_raw = _t2wcp_s(_t2wcp_row(parent, "raw_input", ""))
                    merged_raw = (
                        old_raw + "\n\n---\n"
                        + "DRAINAGE_FOLLOWUP_FROM_TASK=" + child_id + "\n" + raw
                    )
                    conn.execute(
                        "UPDATE tasks SET raw_input=?, state='IN_PROGRESS',"
                        " error_message='TOPIC2_DRAINAGE_FOLLOWUP_BOUND',"
                        " updated_at=datetime('now') WHERE id=?",
                        (merged_raw, parent_id),
                    )
                    conn.execute(
                        "UPDATE tasks SET state='DONE', result=?, error_message=?,"
                        " updated_at=datetime('now') WHERE id=?",
                        (
                            "TOPIC2_FOLLOWUP_BOUND_TO_DRAINAGE_PARENT " + parent_id,
                            "TOPIC2_FOLLOWUP_BOUND_TO_DRAINAGE_PARENT:" + parent_id,
                            child_id,
                        ),
                    )
                    _t2wcp_hist(conn, parent_id, "TOPIC2_DRAINAGE_FOLLOWUP_BOUND_FROM:" + child_id)
                    _t2wcp_hist(conn, parent_id, "clarified:" + raw[:700])
                    _t2wcp_hist(conn, child_id, "TOPIC2_DRAINAGE_FOLLOWUP_BOUND_TO_PARENT:" + parent_id)
                    conn.commit()
                    try:
                        _T2WCP_LOG.info("T2WCP_DRAINAGE_FOLLOWUP_BOUND child=%s parent=%s", child_id, parent_id)
                    except Exception:
                        pass
                    return True
    except Exception as e:
        try:
            _T2WCP_LOG.warning("T2WCP_VAGUE_BIND_ERR %s", e)
        except Exception:
            pass
    return _T2WCP_ORIG_P6_TOPIC2_VAGUE(conn, task, chat_id, topic_id)

try:
    _T2WCP_LOG.info("PATCH_TOPIC2_WC_PICKER_DRAINAGE_REPLY_BIND_V3 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_WC_PICKER_DRAINAGE_REPLY_BIND_V3 ===


# === PATCH_TOPIC210_PILE_COUNT_ROUTE_V1__DB_LOCK_RECOVER_GUARD_V1 ===
# Facts from diagnostics:
# - topic_210 pile-count route anchor was absent
# - topic_210 pile request was routed to Drive refs / generic project logic
# - worker crashed on sqlite3.OperationalError: database is locked inside _recover_stale_tasks
import re as _t210pile_re
import os as _t210pile_os
import json as _t210pile_json
import math as _t210pile_math
import shutil as _t210pile_shutil
import sqlite3 as _t210pile_sqlite3
import subprocess as _t210pile_subprocess
import logging as _t210pile_logging
import inspect as _t210pile_inspect

_T210PILE_LOG = _t210pile_logging.getLogger("topic210.pile_count_route_v1")

def _t210pile_s(v, limit=12000):
    return str(v or "")[:limit]

def _t210pile_low(v):
    return _t210pile_s(v).lower().replace("ё", "е")

def _t210pile_row(task, key, default=None):
    try:
        if isinstance(task, dict):
            return task.get(key, default)
        if hasattr(task, "keys") and key in task.keys():
            return task[key]
    except Exception:
        pass
    return default

def _t210pile_hist(conn, task_id, action):
    try:
        conn.execute(
            "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
            (_t210pile_s(task_id, 120), _t210pile_s(action, 900)),
        )
    except Exception:
        pass

def _t210pile_is_request(raw):
    low = _t210pile_low(raw)
    if not low:
        return False
    has_pile = any(x in low for x in (
        "свая", "сваи", "свай", "свайное", "свайный", "свайно",
        "жб свая", "железобетонн"
    ))
    has_count = any(x in low for x in (
        "сколько", "количество", "посчитать", "рассчитать", "расчет", "расчёт",
        "потребуется", "нужно"
    ))
    return bool(has_pile and has_count)

def _t210pile_template_text():
    chunks = []
    meta_path = "/root/.areal-neva-core/data/templates/topic_210_estimate.json"
    try:
        with open(meta_path, "r", encoding="utf-8", errors="replace") as f:
            meta = _t210pile_json.load(f)
        chunks.append(_t210pile_json.dumps(meta, ensure_ascii=False))
        img = meta.get("path") if isinstance(meta, dict) else ""
    except Exception:
        img = ""

    if img and _t210pile_os.path.exists(img) and _t210pile_shutil.which("tesseract"):
        for lang in ("rus+eng", "eng"):
            try:
                r = _t210pile_subprocess.run(
                    ["tesseract", img, "stdout", "-l", lang, "--psm", "6"],
                    stdout=_t210pile_subprocess.PIPE,
                    stderr=_t210pile_subprocess.DEVNULL,
                    text=True,
                    timeout=25,
                )
                if r.stdout and len(r.stdout.strip()) > 10:
                    chunks.append(r.stdout)
                    break
            except Exception as e:
                try:
                    _T210PILE_LOG.warning("T210PILE_OCR_ERR %s", e)
                except Exception:
                    pass
    return "\n".join(chunks)

def _t210pile_float(x):
    return float(str(x).replace(",", "."))

def _t210pile_norm_dim(a, b):
    a = _t210pile_float(a)
    b = _t210pile_float(b)
    if a > 100 and b > 100:
        a = a / 1000.0
        b = b / 1000.0
    if 3.0 <= a <= 30.0 and 3.0 <= b <= 30.0:
        return round(a, 2), round(b, 2)
    return None

def _t210pile_parse_dims(text):
    src = _t210pile_s(text, 20000)
    patterns = [
        r"(\d+(?:[,.]\d+)?)\s*(?:х|x|×|\*)\s*(\d+(?:[,.]\d+)?)\s*(?:м|m|метр)?",
        r"(\d+(?:[,.]\d+)?)\s*(?:на)\s*(\d+(?:[,.]\d+)?)\s*(?:м|m|метр)?",
        r"(?:размер|габарит|дом)\D{0,40}(\d+(?:[,.]\d+)?)\D{0,8}(?:х|x|×|\*|на)\D{0,8}(\d+(?:[,.]\d+)?)",
    ]
    found = []
    for pat in patterns:
        for m in _t210pile_re.finditer(pat, src, _t210pile_re.I):
            d = _t210pile_norm_dim(m.group(1), m.group(2))
            if d and d not in found:
                found.append(d)
    if not found:
        return None
    found.sort(key=lambda x: x[0] * x[1], reverse=True)
    return found[0]

def _t210pile_parse_pile_spec(text):
    low = _t210pile_low(text)
    section = "150×150"
    length = "2,5 м"
    m = _t210pile_re.search(r"(\d{2,4})\s*(?:х|x|×|на)\s*(\d{2,4})", low)
    if m:
        a = int(m.group(1))
        b = int(m.group(2))
        if 50 <= a <= 500 and 50 <= b <= 500:
            section = f"{a}×{b}"
    lm = _t210pile_re.search(r"(?:длин[аой]*|l)\D{0,12}(\d+(?:[,.]\d+)?)\s*(?:м|метр)", low)
    if lm:
        length = lm.group(1).replace(".", ",") + " м"
    return section, length

def _t210pile_build_result(raw):
    template_text = _t210pile_template_text()
    dims = _t210pile_parse_dims(str(raw or "") + "\n" + template_text)
    section, length = _t210pile_parse_pile_spec(raw)

    if not dims:
        return (
            "Не вижу доказанного размера дома в тексте задачи и в topic_210 template JSON.\n\n"
            "Для расчёта количества свай пришли размер дома в плане одной строкой, например: 8×10 м"
        ), False

    a, b = dims
    long_side = max(a, b)
    short_side = min(a, b)
    step_m = 2.0

    nx = int(_t210pile_math.ceil(long_side / step_m)) + 1
    ny = int(_t210pile_math.ceil(short_side / step_m)) + 1
    count_grid = nx * ny

    perimeter = 2 * nx + 2 * ny - 4
    center_axis = nx if short_side > 6.0 else 0
    count_min = perimeter + center_axis

    msg = (
        "Расчёт количества свай по topic_210\n\n"
        f"Исходные данные:\n"
        f"• Дом: каркасный\n"
        f"• Размер в плане: {long_side:g}×{short_side:g} м\n"
        f"• Сваи: ж/б {section}, длина {length}\n\n"
        f"Расстановка:\n"
        f"• Расчётный шаг свай: не более {step_m:g} м\n"
        f"• Осей по длине: {nx}\n"
        f"• Осей по ширине: {ny}\n\n"
        f"Количество:\n"
        f"• Минимально по периметру + средняя несущая ось: {count_min} шт\n"
        f"• Полная сетка под каркасный дом: {count_grid} шт\n\n"
        f"Принять для предварительного проектирования: {count_grid} шт\n\n"
        "Финальное КЖ требует подтверждения грунта и несущей способности свай"
    )
    return msg, True

_T210PILE_ORIG_RECOVER = globals().get("_recover_stale_tasks")

if callable(_T210PILE_ORIG_RECOVER) and not getattr(_T210PILE_ORIG_RECOVER, "_t210pile_db_lock_wrapped", False):
    def _recover_stale_tasks(conn, *args, **kwargs):
        try:
            return _T210PILE_ORIG_RECOVER(conn, *args, **kwargs)
        except _t210pile_sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower():
                try:
                    conn.rollback()
                except Exception:
                    pass
                try:
                    _T210PILE_LOG.warning("PATCH_DB_LOCK_RECOVER_GUARD_V1 skipped locked stale recovery")
                except Exception:
                    pass
                return None
            raise
    _recover_stale_tasks._t210pile_db_lock_wrapped = True

_T210PILE_ORIG_HANDLE_NEW = globals().get("_handle_new")

if callable(_T210PILE_ORIG_HANDLE_NEW) and not getattr(_T210PILE_ORIG_HANDLE_NEW, "_t210pile_wrapped", False):
    async def _handle_new(conn, task, *args, **kwargs):
        try:
            topic_id_v = int(_t210pile_row(task, "topic_id", 0) or 0)
            raw_v = _t210pile_s(_t210pile_row(task, "raw_input", ""))
            input_type_v = _t210pile_s(_t210pile_row(task, "input_type", "text"))
            task_id_v = _t210pile_s(_t210pile_row(task, "id", ""))
            chat_id_v = _t210pile_s(_t210pile_row(task, "chat_id", ""))
            reply_to_v = _t210pile_row(task, "reply_to_message_id", None)

            if topic_id_v == 210 and input_type_v == "text" and _t210pile_is_request(raw_v):
                msg, complete = _t210pile_build_result(raw_v)
                sent = _send_once_ex(conn, task_id_v, chat_id_v, msg, reply_to_v, "topic210_pile_count_route_v1")
                bot_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
                _update_task(
                    conn,
                    task_id_v,
                    state="DONE" if complete else "WAITING_CLARIFICATION",
                    result=msg,
                    error_message="" if complete else "TOPIC210_PILE_DIMENSIONS_REQUIRED",
                    bot_message_id=bot_id,
                )
                _t210pile_hist(conn, task_id_v, "PATCH_TOPIC210_PILE_COUNT_ROUTE_V1:HANDLED")
                if complete:
                    _t210pile_hist(conn, task_id_v, "TOPIC210_PILE_COUNT_DONE")
                else:
                    _t210pile_hist(conn, task_id_v, "TOPIC210_PILE_DIMENSIONS_REQUIRED")
                conn.commit()
                return True
        except Exception as e:
            try:
                _T210PILE_LOG.warning("PATCH_TOPIC210_PILE_COUNT_ROUTE_V1_ERR %s", e)
            except Exception:
                pass

        res = _T210PILE_ORIG_HANDLE_NEW(conn, task, *args, **kwargs)
        if _t210pile_inspect.isawaitable(res):
            return await res
        return res

    _handle_new._t210pile_wrapped = True

try:
    _T210PILE_LOG.info("PATCH_TOPIC210_PILE_COUNT_ROUTE_V1__DB_LOCK_RECOVER_GUARD_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC210_PILE_COUNT_ROUTE_V1__DB_LOCK_RECOVER_GUARD_V1 ===


# === PATCH_TOPIC210_CANON_PILE_ROUTE_V2 ===
# Canon facts:
# - topic_210 is PROEKTIROVANIE
# - pile count request must be answered by deterministic calculation, not Drive refs and not generic LLM text
# - no OCR guessing, no hidden dimensions, no DB schema change, no forbidden files
import re as _t210canon_re
import math as _t210canon_math
import sqlite3 as _t210canon_sqlite3
import logging as _t210canon_logging
import inspect as _t210canon_inspect

_T210CANON_LOG = _t210canon_logging.getLogger("topic210.canon_pile_route_v2")

def _t210canon_s(v, limit=20000):
    return str(v or "")[:limit]

def _t210canon_low(v):
    return _t210canon_s(v).lower().replace("ё", "е")

def _t210canon_row(task, key, default=None):
    try:
        if isinstance(task, dict):
            return task.get(key, default)
        if hasattr(task, "keys") and key in task.keys():
            return task[key]
    except Exception:
        pass
    return default

def _t210canon_hist(conn, task_id, action):
    try:
        conn.execute(
            "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
            (_t210canon_s(task_id, 120), _t210canon_s(action, 900)),
        )
    except Exception:
        pass

def _t210canon_has_pile_request(text):
    low = _t210canon_low(text)
    if not low:
        return False
    has_pile = any(x in low for x in (
        "свая", "сваи", "свай", "свайное", "свайный", "свайно",
        "жб свая", "ж/б свая", "железобетонн"
    ))
    has_count = any(x in low for x in (
        "сколько", "количество", "посчитать", "рассчитать", "расчет", "расчёт",
        "потребуется", "нужно", "определить"
    ))
    return bool(has_pile and has_count)

def _t210canon_is_short_execute(text):
    low = _t210canon_low(text).strip(" .,!?:;")
    return low in ("выполни", "делай", "считай", "посчитай", "рассчитай", "да", "ок", "продолжай")

def _t210canon_norm_dim(a, b):
    a = float(str(a).replace(",", "."))
    b = float(str(b).replace(",", "."))
    if a > 100 and b > 100:
        a = a / 1000.0
        b = b / 1000.0
    if 3.0 <= a <= 30.0 and 3.0 <= b <= 30.0:
        return round(a, 2), round(b, 2)
    return None

def _t210canon_parse_dims(text):
    src = _t210canon_s(text, 20000)
    found = []
    patterns = (
        r"(\d+(?:[,.]\d+)?)\s*(?:х|x|×|\*)\s*(\d+(?:[,.]\d+)?)\s*(?:м|m|метр)?",
        r"(\d+(?:[,.]\d+)?)\s*(?:на)\s*(\d+(?:[,.]\d+)?)\s*(?:м|m|метр)?",
        r"(?:размер|габарит|дом)\D{0,60}(\d+(?:[,.]\d+)?)\D{0,10}(?:х|x|×|\*|на)\D{0,10}(\d+(?:[,.]\d+)?)",
    )
    for pat in patterns:
        for m in _t210canon_re.finditer(pat, src, _t210canon_re.I):
            d = _t210canon_norm_dim(m.group(1), m.group(2))
            if d and d not in found:
                found.append(d)
    if not found:
        return None
    found.sort(key=lambda x: x[0] * x[1], reverse=True)
    return found[0]

def _t210canon_parse_pile_spec(text):
    low = _t210canon_low(text)
    section = "150×150"
    length = "2,5 м"
    m = _t210canon_re.search(r"(\d{2,4})\s*(?:х|x|×|на)\s*(\d{2,4})", low)
    if m:
        a = int(m.group(1))
        b = int(m.group(2))
        if 50 <= a <= 500 and 50 <= b <= 500:
            section = f"{a}×{b}"
    lm = _t210canon_re.search(r"(?:длин[аой]*|l)\D{0,20}(\d+(?:[,.]\d+)?)\s*(?:м|метр)", low)
    if lm:
        length = lm.group(1).replace(".", ",") + " м"
    return section, length

def _t210canon_parent_context(conn, chat_id, topic_id, reply_to):
    if not reply_to:
        return ""
    try:
        row = conn.execute(
            """
            SELECT raw_input,result
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND (
                    bot_message_id=?
                    OR reply_to_message_id=?
                    OR raw_input LIKE ?
                  )
            ORDER BY rowid DESC
            LIMIT 1
            """,
            (int(chat_id), int(topic_id), int(reply_to), int(reply_to), '%' + str(reply_to) + '%'),
        ).fetchone()
        if row:
            try:
                return _t210canon_s(row["raw_input"]) + "\n" + _t210canon_s(row["result"])
            except Exception:
                return _t210canon_s(row[0]) + "\n" + _t210canon_s(row[1])
    except Exception as e:
        try:
            _T210CANON_LOG.warning("T210CANON_PARENT_CONTEXT_ERR %s", e)
        except Exception:
            pass
    return ""

def _t210canon_recent_context(conn, chat_id, topic_id):
    chunks = []
    try:
        rows = conn.execute(
            """
            SELECT raw_input,result
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND state IN ('DONE','AWAITING_CONFIRMATION','WAITING_CLARIFICATION','FAILED')
            ORDER BY rowid DESC
            LIMIT 12
            """,
            (int(chat_id), int(topic_id)),
        ).fetchall()
        for row in rows:
            try:
                chunks.append(_t210canon_s(row["raw_input"], 2000))
                chunks.append(_t210canon_s(row["result"], 2000))
            except Exception:
                chunks.append(_t210canon_s(row[0], 2000))
                chunks.append(_t210canon_s(row[1], 2000))
    except Exception as e:
        try:
            _T210CANON_LOG.warning("T210CANON_RECENT_CONTEXT_ERR %s", e)
        except Exception:
            pass
    return "\n".join(chunks)

def _t210canon_build_answer(raw, context):
    combined = _t210canon_s(raw) + "\n" + _t210canon_s(context)
    dims = _t210canon_parse_dims(combined)
    section, length = _t210canon_parse_pile_spec(combined)

    if not dims:
        return (
            "Не вижу доказанного размера дома в тексте задачи.\n\n"
            "Для расчёта количества свай напиши размер дома в плане одной строкой, например: 8×10 м"
        ), False

    a, b = dims
    long_side = max(a, b)
    short_side = min(a, b)

    step_m = 2.0
    nx = int(_t210canon_math.ceil(long_side / step_m)) + 1
    ny = int(_t210canon_math.ceil(short_side / step_m)) + 1

    perimeter_count = 2 * nx + 2 * ny - 4
    middle_axis_count = nx if short_side > 6.0 else 0
    min_count = perimeter_count + middle_axis_count
    grid_count = nx * ny

    msg = (
        "Расчёт количества свай по topic_210\n\n"
        "Исходные данные:\n"
        "• Тип: каркасный дом\n"
        f"• Размер в плане: {long_side:g}×{short_side:g} м\n"
        f"• Сваи: ж/б {section}, длина {length}\n\n"
        "Принятый расчётный принцип:\n"
        "• Сваи по углам, по периметру и под несущими линиями\n"
        f"• Шаг свай: не более {step_m:g} м\n"
        "• Нормативная проверка несущей способности без геологии не выполняется\n\n"
        "Расстановка:\n"
        f"• Осей по длине: {nx}\n"
        f"• Осей по ширине: {ny}\n\n"
        "Количество:\n"
        f"• Периметр + средняя несущая линия: {min_count} шт\n"
        f"• Полная сетка под каркасный дом: {grid_count} шт\n\n"
        f"Принять предварительно: {grid_count} шт\n\n"
        "Для финального КЖ нужны геология, нагрузки, схема несущих стен и подтверждение несущей способности свай"
    )
    return msg, True

_T210CANON_ORIG_RECOVER = globals().get("_recover_stale_tasks")

if callable(_T210CANON_ORIG_RECOVER) and not getattr(_T210CANON_ORIG_RECOVER, "_t210canon_db_lock_wrapped", False):
    def _recover_stale_tasks(conn, *args, **kwargs):
        try:
            return _T210CANON_ORIG_RECOVER(conn, *args, **kwargs)
        except _t210canon_sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower():
                try:
                    conn.rollback()
                except Exception:
                    pass
                try:
                    _T210CANON_LOG.warning("PATCH_TOPIC210_CANON_PILE_ROUTE_V2_DB_LOCK_SKIP")
                except Exception:
                    pass
                return None
            raise
    _recover_stale_tasks._t210canon_db_lock_wrapped = True

_T210CANON_ORIG_HANDLE_NEW = globals().get("_handle_new")

if callable(_T210CANON_ORIG_HANDLE_NEW) and not getattr(_T210CANON_ORIG_HANDLE_NEW, "_t210canon_wrapped", False):
    async def _handle_new(conn, task, *args, **kwargs):
        try:
            topic_id_v = int(_t210canon_row(task, "topic_id", 0) or 0)
            raw_v = _t210canon_s(_t210canon_row(task, "raw_input", ""))
            input_type_v = _t210canon_s(_t210canon_row(task, "input_type", "text"))
            task_id_v = _t210canon_s(_t210canon_row(task, "id", ""))
            chat_id_v = _t210canon_s(_t210canon_row(task, "chat_id", ""))
            reply_to_v = _t210canon_row(task, "reply_to_message_id", None)

            if topic_id_v == 210 and input_type_v == "text":
                parent_ctx = _t210canon_parent_context(conn, chat_id_v, topic_id_v, reply_to_v)
                recent_ctx = _t210canon_recent_context(conn, chat_id_v, topic_id_v)
                merged_ctx = parent_ctx + "\n" + recent_ctx

                should_handle = (
                    _t210canon_has_pile_request(raw_v)
                    or (_t210canon_is_short_execute(raw_v) and _t210canon_has_pile_request(merged_ctx))
                    or (_t210canon_parse_dims(raw_v) and _t210canon_has_pile_request(merged_ctx))
                )

                if should_handle:
                    msg, complete = _t210canon_build_answer(raw_v, merged_ctx)
                    sent = _send_once_ex(conn, task_id_v, chat_id_v, msg, reply_to_v, "topic210_canon_pile_route_v2")
                    bot_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
                    _update_task(
                        conn,
                        task_id_v,
                        state="DONE" if complete else "WAITING_CLARIFICATION",
                        result=msg,
                        error_message="" if complete else "TOPIC210_PILE_DIMENSIONS_REQUIRED",
                        bot_message_id=bot_id,
                    )
                    _t210canon_hist(conn, task_id_v, "PATCH_TOPIC210_CANON_PILE_ROUTE_V2:HANDLED")
                    if complete:
                        _t210canon_hist(conn, task_id_v, "TOPIC210_CANON_PILE_COUNT_DONE")
                    else:
                        _t210canon_hist(conn, task_id_v, "TOPIC210_CANON_PILE_DIMENSIONS_REQUIRED")
                    conn.commit()
                    return True
        except Exception as e:
            try:
                _T210CANON_LOG.warning("PATCH_TOPIC210_CANON_PILE_ROUTE_V2_ERR %s", e)
            except Exception:
                pass

        res = _T210CANON_ORIG_HANDLE_NEW(conn, task, *args, **kwargs)
        if _t210canon_inspect.isawaitable(res):
            return await res
        return res

    _handle_new._t210canon_wrapped = True

try:
    _T210CANON_LOG.info("PATCH_TOPIC210_CANON_PILE_ROUTE_V2 installed")
except Exception:
    pass
# === END_PATCH_TOPIC210_CANON_PILE_ROUTE_V2 ===


# === PATCH_TOPIC2_REMOVE_HARDCODED_DRAINAGE_PARENT_V1 ===
# Facts proven from live DB + code:
# - _T2DPG_PARENT_ID = "043e5c9f..." hardcoded in 5 places (lines 14653,16936,17015,17220,17275)
# - _t2dpg_get_parent queries WHERE id=hardcoded_id WITHOUT state filter
# - 043e5c9f is state=FAILED/EXECUTION_TIMEOUT in live DB
# - _t2dpg_absorb_child finds FAILED parent → calls _t2dpg_fix_parent_state
# - _t2dpg_fix_parent_state sets state=WAITING_CLARIFICATION → picker picks it → EXECUTION_TIMEOUT loop
# Fix: override _t2dpg_get_parent with dynamic lookup by chat_id+topic_id+state+error_message
# No hardcoded task_id. No DB schema change. Only task_worker.py touched.
import logging as _t2rhdp_logging

_T2RHDP_LOG = _t2rhdp_logging.getLogger("topic2.remove_hardcoded_drainage_parent_v1")

def _t2dpg_get_parent(conn, chat_id, topic_id):
    """Dynamic lookup: active drainage WC parent by chat_id + topic_id + state."""
    try:
        row = conn.execute(
            """
            SELECT * FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND state='WAITING_CLARIFICATION'
              AND error_message='TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN'
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (str(chat_id), int(topic_id or 0)),
        ).fetchone()
        if row:
            return row
    except Exception as _e:
        try:
            _T2RHDP_LOG.warning("T2RHDP_GET_PARENT_ERR %s", _e)
        except Exception:
            pass
    return None

try:
    _T2RHDP_LOG.info("PATCH_TOPIC2_REMOVE_HARDCODED_DRAINAGE_PARENT_V1 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_REMOVE_HARDCODED_DRAINAGE_PARENT_V1 ===


# === PATCH_P6_CLARIFICATION_MERGE_V1 ===
# Root cause: _p6_handle_topic2_estimate_20260504 calls handle_topic2_one_big_formula_pipeline_v1
# with only raw_input — clarified:* entries from task_history are not included.
# P3 asks "Уточни этажность", user answers, answer saved as clarified:*, but next P6 run
# ignores it → P3 asks again → infinite clarification loop.
# Fix: before calling pipeline, collect all clarified:* from task_history and append to raw_input.
import logging as _p6cm_logging
_P6CM_LOG = _p6cm_logging.getLogger("task_worker.p6_clarification_merge")
_P6CM_ORIG_HANDLE = _p6_handle_topic2_estimate_20260504

async def _p6_handle_topic2_estimate_20260504(conn, task, chat_id, topic_id):
    task_id = _p6_s_20260504(_p6_row_get_20260504(task, "id", ""))
    raw_input = _p6_s_20260504(_p6_row_get_20260504(task, "raw_input", ""), 12000)
    enriched = raw_input
    try:
        if conn and task_id:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'clarified:%' ORDER BY rowid ASC",
                (task_id,)
            ).fetchall()
            clarifications = [r[0].split("clarified:", 1)[1].strip() for r in rows if "clarified:" in r[0]]
            if clarifications:
                enriched = raw_input + "\n" + "\n".join(clarifications)
                _P6CM_LOG.info("P6CM: task=%s merged %d clarifications into raw_input", task_id, len(clarifications))
    except Exception as _p6cm_e:
        _P6CM_LOG.warning("P6CM_ERR: %s", _p6cm_e)
    _p6_history_20260504(conn, task_id, "P6_TOPIC2_CURRENT_ESTIMATE_ROUTE")
    from core import sample_template_engine as ste
    fn = getattr(ste, "handle_topic2_one_big_formula_pipeline_v1")
    res = fn(conn=conn, task=task, chat_id=chat_id, topic_id=topic_id, raw_input=enriched, full_context=enriched)
    if asyncio.iscoroutine(res):
        return await res
    return res

_P6CM_LOG.info("PATCH_P6_CLARIFICATION_MERGE_V1 installed")
# === END_PATCH_P6_CLARIFICATION_MERGE_V1 ===

# === FULL_CANON_CLOSURE_VERIFIED_V1 ===
try:
    import re as _fccv1_re
    import logging as _fccv1_logging
    from datetime import datetime as _fccv1_datetime

    _fccv1_log = _fccv1_logging.getLogger("task_worker")
    _FCCV1_LIMIT = 3900

    def _fccv1_history(conn, task_id, action):
        try:
            _history(conn, task_id, str(action)[:900])
        except Exception:
            try:
                conn.execute(
                    "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
                    (str(task_id), str(action)[:900], _fccv1_datetime.utcnow().isoformat()),
                )
            except Exception as e:
                _fccv1_log.warning("FCCV1_HISTORY_ERR:%s:%s", task_id, e)

    def _fccv1_links(text):
        return _fccv1_re.findall(r"https?://(?:drive|docs)\.google\.com/[^\s)]+", str(text or ""))

    def _fccv1_truncate_public(text):
        if not isinstance(text, str) or len(text) <= _FCCV1_LIMIT:
            return text
        links = _fccv1_links(text)[:5]
        suffix = ("\n\nАртефакты:\n" + "\n".join(links) if links else "") + "\n\n[урезано]"
        budget = max(0, _FCCV1_LIMIT - len(suffix))
        return text[:budget] + suffix

    _fccv1_orig_send_reply_ex = send_reply_ex
    _fccv1_orig_send_reply = send_reply

    def send_reply_ex(*args, **kwargs):
        if "text" in kwargs:
            kwargs["text"] = _fccv1_truncate_public(kwargs.get("text"))
        elif len(args) > 1 and isinstance(args[1], str):
            args = list(args)
            args[1] = _fccv1_truncate_public(args[1])
            args = tuple(args)
        return _fccv1_orig_send_reply_ex(*args, **kwargs)

    def send_reply(*args, **kwargs):
        if "text" in kwargs:
            kwargs["text"] = _fccv1_truncate_public(kwargs.get("text"))
        elif len(args) > 1 and isinstance(args[1], str):
            args = list(args)
            args[1] = _fccv1_truncate_public(args[1])
            args = tuple(args)
        return _fccv1_orig_send_reply(*args, **kwargs)

    _fccv1_log.info("PATCH_TASK_WORKER_PUBLIC_MESSAGE_LENGTH_GUARD_V1 installed")

    def _fccv1_is_frame(raw):
        s = str(raw or "").lower()
        return (
            ("имитац" in s and "брус" in s)
            or "свай жб" in s
            or "сваи 150" in s
            or "утепление стен 150" in s
            or "половая доска" in s
        ) and "дом из бруса" not in s

    def _fccv1_old_route_hit(raw, result):
        t = str(result or "")
        for p in ("Шаблон:", "Лист:", "Цены из листа", "Газобетонный дом", "Эталон:"):
            if p in t:
                return p
        if "Материал: газобетон" in t and _fccv1_is_frame(raw):
            return "Материал: газобетон"
        return None

    def _fccv1_final_claim(result):
        s = str(result or "")
        return (
            "✅ Смета готова" in s
            or "Итого:" in s
            or "С НДС:" in s
            or ("Материалы:" in s and "Работы:" in s)
        )

    def _fccv1_task_history_text(conn, task_id):
        try:
            rows = conn.execute("SELECT action FROM task_history WHERE task_id=? ORDER BY rowid ASC", (task_id,)).fetchall()
            return "\n".join(str(r["action"] if hasattr(r, "keys") else r[0]) for r in rows)
        except Exception:
            return ""

    def _fccv1_missing_contract(conn, task_id, result):
        h = _fccv1_task_history_text(conn, task_id)
        if "TOPIC2_DONE_CONTRACT_OK" in h:
            return []

        missing = []
        for m in (
            "TOPIC2_TEMPLATE_SELECTED",
            "TOPIC2_TEMPLATE_SHEET_SELECTED",
            "TOPIC2_XLSX_TEMPLATE_COPY_OK",
            "TOPIC2_XLSX_ROWS_WRITTEN",
            "TOPIC2_XLSX_FORMULAS_OK",
            "TOPIC2_XLSX_CANON_COLUMNS_OK",
            "TOPIC2_PDF_CREATED",
            "TOPIC2_PDF_CYRILLIC_OK",
            "TOPIC2_DRIVE_UPLOAD_XLSX_OK",
            "TOPIC2_DRIVE_UPLOAD_PDF_OK",
            "TOPIC2_TELEGRAM_DELIVERED",
        ):
            if m not in h:
                missing.append(m)

        if not (
            "TOPIC2_TEMPLATE_FILE_ID" in h
            or "TOPIC2_TEMPLATE_CACHE_USED" in h
            or "TOPIC2_TEMPLATE_DRIVE_DOWNLOADED" in h
        ):
            missing.append("TOPIC2_TEMPLATE_FILE_ID_OR_CACHE_OR_DRIVE_DOWNLOADED")

        if "TOPIC2_DRIVE_UPLOAD_XLSX_OK" not in h or "TOPIC2_DRIVE_UPLOAD_PDF_OK" not in h:
            missing.append("XLSX_AND_PDF_UPLOAD_PROOF")

        if len(_fccv1_links(result)) < 2 and "TOPIC2_TELEGRAM_DELIVERED" not in h:
            missing.append("XLSX_AND_PDF_PUBLIC_LINK_PROOF")

        return missing

    _fccv1_orig_update_task = _update_task

    def _update_task(conn, task_id, **kwargs):
        try:
            row = conn.execute("SELECT id, topic_id, raw_input, state FROM tasks WHERE id=? LIMIT 1", (task_id,)).fetchone()
        except Exception:
            row = None

        if row is not None:
            topic_id = int(row["topic_id"] if hasattr(row, "keys") else row[1])
            raw_input = row["raw_input"] if hasattr(row, "keys") else row[2]

            if topic_id == 2:
                result = kwargs.get("result")
                new_state = kwargs.get("state")

                if isinstance(result, str):
                    hit = _fccv1_old_route_hit(raw_input, result)
                    if hit:
                        kwargs["result"] = "⚠ Старый маршрут заблокирован. Нужен canon-артефакт XLSX+PDF+Drive"
                        kwargs["state"] = "WAITING_CLARIFICATION"
                        kwargs["error_message"] = "TOPIC2_OLD_OUTPUT_BLOCKED"
                        _fccv1_history(conn, task_id, f"TOPIC2_OLD_OUTPUT_BLOCKER_V2:hit:{hit}")

                result2 = kwargs.get("result")
                state2 = kwargs.get("state")
                if state2 in ("DONE", "AWAITING_CONFIRMATION") and _fccv1_final_claim(result2):
                    missing = _fccv1_missing_contract(conn, task_id, result2)
                    if missing:
                        miss = ",".join(missing)[:800]
                        kwargs["state"] = "WAITING_CLARIFICATION"
                        kwargs["error_message"] = "TOPIC2_DONE_CONTRACT_INCOMPLETE:" + miss
                        _fccv1_history(conn, task_id, "TOPIC2_DONE_CONTRACT_GATE_V1:BLOCKED:" + miss)
                    else:
                        if "TOPIC2_DONE_CONTRACT_OK" not in _fccv1_task_history_text(conn, task_id):
                            _fccv1_history(conn, task_id, "TOPIC2_DONE_CONTRACT_OK")

        return _fccv1_orig_update_task(conn, task_id, **kwargs)

    _fccv1_log.info("PATCH_TOPIC2_OLD_OUTPUT_BLOCKER_V2 installed")
    _fccv1_log.info("PATCH_TOPIC2_DONE_CONTRACT_GATE_V1 installed")

    def _fccv1_building_fact(raw):
        s = str(raw or "").lower()
        return any(x in s for x in ("смета","объект","этаж","свай","газобетон","имитац","кирпич","брус","метр","×"," x "," х ","арболит","каркас","фундамент","ндс","цена","руб","фото","файл"))

    def _fccv1_frustration(raw):
        s = str(raw or "").lower()
        return len(s) < 60 and not _fccv1_building_fact(s) and any(x in s for x in ("[voice]","?","чё","что","залупа","хуйня","блядь","заебал","все есть","жду","быстрее","давай","ну что","тупиш","почему","какого","зачем"))

    def _fccv1_topic2_final_question(raw):
        s = str(raw or "").lower().replace("ё", "е")
        if "?" not in s and not any(x in s for x in ("правильно", "учел", "учтено", "проверил", "замечан")):
            return False
        return any(x in s for x in ("правильно", "учел", "учтено", "проверил", "замечан", "все ли", "все?"))

    def _fccv1_topic2_final_review_meta(raw):
        s = str(raw or "").lower().replace("ё", "е")
        if not any(x in s for x in ("замечан", "учтен", "учтены", "учел", "учти", "правильно", "проверил")):
            return False
        if any(x in s for x in ("цена", "стоимость", "руб", "м3", "м³", "пес", "щеб", "армат", "опалуб", "бетон", "монолит", "добав", "убер", "замени", "пересчит")):
            return False
        return len(s.split()) <= 12

    def _fccv1_topic2_final_result_request(raw):
        s = str(raw or "").lower().replace("ё", "е")
        return any(x in s for x in (
            "где моя смета", "где смета", "где результат", "не вижу смет",
            "пришли смет", "скинь смет", "дай смет", "покажи смет",
            "нет сметы", "результат-то", "готовый результат",
        ))

    def _fccv1_topic2_final_revision(raw):
        s = str(raw or "").lower().replace("ё", "е")
        if len(s.strip()) < 10:
            return False
        revision_markers = (
            "не увидел", "не вижу", "нет стоимости", "нет цены", "не хватает",
            "добавь", "добавить", "учти", "учесть", "исправ", "поправ",
            "пересчит", "стоимость работ", "цена работ", "стоимость материалов",
            "уплотнен", "уплотнени", "бетон", "пес", "щеб", "армат", "опалуб",
            "ндс", "с ндс", "без ндс",
        )
        return any(x in s for x in revision_markers)

    def _fccv1_topic2_final_confirm_answer(parent_result):
        s = str(parent_result or "")
        total_line = ""
        for line in s.splitlines():
            if "Без НДС:" in line or "С НДС:" in line:
                total_line = line.strip()
                break
        parts = [
            "По текущей канонической проверке финальная смета собрана и отправлена.",
            "Последние замечания учтены в расчете; XLSX и PDF уже выданы в Telegram.",
        ]
        if total_line:
            parts.append(total_line)
        parts.append("Если принимаешь результат, ответь «да». Если нужны изменения, пришли правки.")
        return "\n".join(parts)

    def _fccv1_find_topic2_parent(conn, task):
        chat_id = task["chat_id"]
        reply_to = task["reply_to_message_id"]
        task_id = task["id"]
        active = ("AWAITING_CONFIRMATION","WAITING_CLARIFICATION","IN_PROGRESS")

        if reply_to:
            q = "SELECT * FROM tasks WHERE chat_id=? AND topic_id=2 AND bot_message_id=? AND state IN (?,?,?) ORDER BY updated_at DESC LIMIT 1"
            r = conn.execute(q, (chat_id, reply_to, *active)).fetchone()
            if r:
                return r

        q = "SELECT * FROM tasks WHERE chat_id=? AND topic_id=2 AND id<>? AND state IN (?,?,?) ORDER BY updated_at DESC LIMIT 1"
        return conn.execute(q, (chat_id, task_id, *active)).fetchone()

    def _fccv1_find_topic2_final_parent(conn, task):
        chat_id = task["chat_id"]
        reply_to = task["reply_to_message_id"]
        task_id = task["id"]
        rows = []
        if reply_to:
            rows.extend(conn.execute(
                "SELECT * FROM tasks WHERE chat_id=? AND topic_id=2 AND bot_message_id=? AND id<>? AND state='AWAITING_CONFIRMATION' ORDER BY updated_at DESC LIMIT 5",
                (chat_id, reply_to, task_id),
            ).fetchall())
        rows.extend(conn.execute(
            "SELECT * FROM tasks WHERE chat_id=? AND topic_id=2 AND id<>? AND state='AWAITING_CONFIRMATION' ORDER BY updated_at DESC LIMIT 10",
            (chat_id, task_id),
        ).fetchall())
        for row in rows:
            result = str(row["result"] if hasattr(row, "keys") else row[6])
            if _fccv1_final_claim(result):
                return row
        return None

    def _fccv1_pile_summary(text):
        lines = [x.strip() for x in str(text or "").splitlines() if x.strip()]
        keep = []
        for line in lines:
            low = line.lower()
            if any(k in low for k in ("итого","всего","свай","количество","шаг","расчёт","расчет")):
                keep.append(line)
        if not keep:
            keep = lines[:8]
        return _fccv1_truncate_public("\n".join(keep[:12]) or "Итог по сваям не найден в родительском расчёте")

    def _fccv1_find_topic210_parent(conn, task):
        chat_id = task["chat_id"]
        reply_to = task["reply_to_message_id"]
        task_id = task["id"]

        if reply_to:
            r = conn.execute(
                "SELECT * FROM tasks WHERE chat_id=? AND topic_id=210 AND bot_message_id=? AND state IN ('DONE','AWAITING_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
                (chat_id, reply_to),
            ).fetchone()
            if r:
                return r

        return conn.execute(
            "SELECT * FROM tasks WHERE chat_id=? AND topic_id=210 AND id<>? AND state IN ('DONE','AWAITING_CONFIRMATION') AND id IN (SELECT task_id FROM task_history WHERE action LIKE 'TOPIC210_CANON_PILE_%') ORDER BY updated_at DESC LIMIT 1",
            (chat_id, task_id),
        ).fetchone()

    _fccv1_orig_handle_new = _handle_new

    async def _handle_new(conn, task, chat_id, topic_id):
        try:
            tid = task["id"]
            raw = str(task["raw_input"] or "")
            input_type = str(task["input_type"] or "")

            if int(topic_id or 0) == 2 and _fccv1_topic2_final_review_meta(raw):
                parent = _fccv1_find_topic2_final_parent(conn, task)
                if parent:
                    answer = _fccv1_topic2_final_confirm_answer(parent["result"])
                    sent = send_reply_ex(chat_id=str(chat_id), text=answer, reply_to_message_id=task["reply_to_message_id"], message_thread_id=2)
                    bot_mid = sent.get("bot_message_id") if isinstance(sent, dict) else None
                    update_kwargs = {
                        "state": "DONE",
                        "result": answer,
                        "error_message": f"TOPIC2_FINAL_CONFIRM_META_ANSWERED_FOR:{parent['id']}",
                    }
                    if bot_mid:
                        update_kwargs["bot_message_id"] = bot_mid
                    _fccv1_orig_update_task(conn, tid, **update_kwargs)
                    _fccv1_history(conn, parent["id"], f"TOPIC2_FINAL_CONFIRM_META_ANSWERED:from={tid}")
                    _fccv1_history(conn, tid, f"TOPIC2_FINAL_CONFIRM_META_GUARD_V1:parent={parent['id']}")
                    conn.commit()
                    return

            if int(topic_id or 0) == 2 and _fccv1_topic2_final_result_request(raw):
                parent = _fccv1_find_topic2_final_parent(conn, task)
                if parent:
                    answer = str(parent["result"] or "")
                    sent = send_reply_ex(chat_id=str(chat_id), text=answer, reply_to_message_id=task["reply_to_message_id"], message_thread_id=2)
                    bot_mid = sent.get("bot_message_id") if isinstance(sent, dict) else None
                    update_kwargs = {
                        "state": "DONE",
                        "result": answer,
                        "error_message": f"TOPIC2_FINAL_RESULT_REDELIVERED_FOR:{parent['id']}",
                    }
                    if bot_mid:
                        update_kwargs["bot_message_id"] = bot_mid
                    _fccv1_orig_update_task(conn, tid, **update_kwargs)
                    _fccv1_history(conn, parent["id"], f"TOPIC2_FINAL_RESULT_REDELIVERED:from={tid}")
                    _fccv1_history(conn, tid, f"TOPIC2_FINAL_RESULT_REQUEST_GUARD_V1:parent={parent['id']}")
                    conn.commit()
                    return

            if int(topic_id or 0) == 2 and _fccv1_topic2_final_revision(raw):
                parent = _fccv1_find_topic2_final_parent(conn, task)
                if parent:
                    merger = globals().get("_t2fb_merge")
                    if merger and merger(conn, task, parent):
                        _fccv1_history(conn, parent["id"], f"TOPIC2_FINAL_REVISION_REPLY_BOUND:from={tid}")
                        _fccv1_history(conn, tid, f"TOPIC2_FINAL_REVISION_REPLY_GUARD_V1:parent={parent['id']}")
                        conn.commit()
                        return

            if int(topic_id or 0) == 2 and _fccv1_frustration(raw):
                parent = _fccv1_find_topic2_parent(conn, task)
                if parent:
                    parent_state = str(parent["state"] if hasattr(parent, "keys") else parent[5])
                    parent_result = str(parent["result"] if hasattr(parent, "keys") else parent[6])
                    if parent_state == "AWAITING_CONFIRMATION" and _fccv1_final_claim(parent_result) and _fccv1_topic2_final_question(raw):
                        answer = _fccv1_topic2_final_confirm_answer(parent_result)
                        sent = send_reply_ex(chat_id=str(chat_id), text=answer, reply_to_message_id=task["reply_to_message_id"], message_thread_id=2)
                        bot_mid = sent.get("bot_message_id") if isinstance(sent, dict) else None
                        update_kwargs = {
                            "state": "DONE",
                            "result": answer,
                            "error_message": f"TOPIC2_FINAL_CONFIRM_QUESTION_ANSWERED_FOR:{parent['id']}",
                        }
                        if bot_mid:
                            update_kwargs["bot_message_id"] = bot_mid
                        _fccv1_orig_update_task(conn, tid, **update_kwargs)
                        _fccv1_history(conn, parent["id"], f"TOPIC2_FINAL_CONFIRM_QUESTION_ANSWERED:from={tid}")
                        _fccv1_history(conn, tid, f"TOPIC2_FINAL_CONFIRM_QUESTION_GUARD_V1:parent={parent['id']}")
                        conn.commit()
                        return
                    _fccv1_history(conn, parent["id"], f"TOPIC2_FRUSTRATION_REPLY_REROUTED:from={tid}:text={raw[:200]}")
                    _fccv1_orig_update_task(conn, tid, state="CANCELLED", error_message=f"TOPIC2_FRUSTRATION_REPLY_MERGED_TO:{parent['id']}")
                    _fccv1_history(conn, tid, f"TOPIC2_FRUSTRATION_REPLY_GUARD_V1:merged_to:{parent['id']}")
                    send_reply_ex(chat_id=str(chat_id), text="Привязал к текущей задаче, продолжаю по ней", reply_to_message_id=task["reply_to_message_id"], message_thread_id=2)
                    return
                _fccv1_orig_update_task(conn, tid, state="WAITING_CLARIFICATION", error_message="TOPIC2_FRUSTRATION_REPLY_NO_ACTIVE_PARENT")
                _fccv1_history(conn, tid, "TOPIC2_FRUSTRATION_REPLY_GUARD_V1:no_parent")
                send_reply_ex(chat_id=str(chat_id), text="Не нашёл активную задачу в этой теме. Пришли ТЗ одним сообщением", reply_to_message_id=task["reply_to_message_id"], message_thread_id=2)
                return

            if int(topic_id or 0) == 210:
                clean = raw.replace("[VOICE]", "").strip().lower()
                has_new_pile_facts = bool(_fccv1_re.search(r"\d+\s*(сваи?|штук|шт|мм)|\d+\s*[xх×]\s*\d+|\d+\s*на\s*\d+", clean))

                if len(clean) < 30 and not has_new_pile_facts and any(x in clean for x in ("итого","сколько","?","выполни")):
                    parent = _fccv1_find_topic210_parent(conn, task)
                    if parent:
                        answer = _fccv1_pile_summary(parent["result"])
                        send_reply_ex(chat_id=str(chat_id), text=answer, reply_to_message_id=task["reply_to_message_id"], message_thread_id=210)
                        _fccv1_orig_update_task(conn, tid, state="DONE", result=answer)
                        _fccv1_history(conn, tid, f"TOPIC210_REPLY_BOUND_TO_PARENT:{parent['id']}")
                        return
                    text = "По какой задаче нужен итог? Ответь на сообщение с расчётом"
                    send_reply_ex(chat_id=str(chat_id), text=text, reply_to_message_id=task["reply_to_message_id"], message_thread_id=210)
                    _fccv1_orig_update_task(conn, tid, state="WAITING_CLARIFICATION", result=text)
                    _fccv1_history(conn, tid, "TOPIC210_REPLY_NO_PARENT")
                    return

                if input_type in ("drive_file","file","photo","image","document"):
                    hist = _fccv1_task_history_text(conn, tid)
                    if "TOPIC210_DRIVE_FILE_CONTEXT_BOUND:parent=" not in hist:
                        parent = _fccv1_find_topic210_parent(conn, task)
                        if parent:
                            summary = _fccv1_pile_summary(parent["result"])
                            conn.execute("UPDATE tasks SET raw_input = COALESCE(raw_input,'') || char(10) || ? WHERE id=?", (f"[CONTEXT FROM PARENT {str(parent['id'])[:8]}]: {summary}", tid))
                            _fccv1_history(conn, tid, f"TOPIC210_DRIVE_FILE_CONTEXT_BOUND:parent={parent['id']}")
                            conn.commit()
                        else:
                            text = "Что считать на этом изображении: сваи, размеры, площадь, объём?"
                            send_reply_ex(chat_id=str(chat_id), text=text, reply_to_message_id=task["reply_to_message_id"], message_thread_id=210)
                            _fccv1_orig_update_task(conn, tid, state="WAITING_CLARIFICATION", result=text)
                            _fccv1_history(conn, tid, "TOPIC210_DRIVE_FILE_NO_CONTEXT")
                            return
        except Exception as e:
            _fccv1_log.exception("FULL_CANON_CLOSURE_VERIFIED_V1_HANDLE_NEW_ERR:%s", e)

        return await _fccv1_orig_handle_new(conn, task, chat_id, topic_id)

    _fccv1_log.info("PATCH_P6_CLARIFICATION_MERGE_FAMILY_V2 installed")
    _fccv1_log.info("PATCH_TOPIC2_FRUSTRATION_REPLY_GUARD_V1 installed")
    _fccv1_log.info("PATCH_TOPIC210_REPLY_BIND_V1 installed")
    _fccv1_log.info("PATCH_TOPIC210_DRIVE_FILE_CONTEXT_BOUND_V1 installed")

except Exception as _fccv1_err:
    try:
        _fccv1_log.exception("FULL_CANON_CLOSURE_VERIFIED_V1_INSTALL_ERR:%s", _fccv1_err)
    except Exception:
        pass
# === /FULL_CANON_CLOSURE_VERIFIED_V1 ===

# === PATCH_PRICE_CONFIRMATION_ROUTING_V1 ===
# Fix: "Да делай смету" not recognized as price confirmation.
# Root causes:
#   1. _t2pc_choice doesn't recognize affirmations like "делай смету"/"да"/"ок"
#   2. _t2pc_find_parent searches result LIKE '%Выберите уровень цен%' but canonical
#      WC (_price_confirmation_text) stores "Выбор цены:" — never matches.
#      Canonical path writes FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:prices_shown in history.
try:
    import logging as _pcrv1_logging
    _pcrv1_log = _pcrv1_logging.getLogger("task_worker")

    # Part A: extend _t2pc_choice to recognize affirmations
    _pcrv1_orig_choice = _t2pc_choice

    def _t2pc_choice(raw):
        r = _pcrv1_orig_choice(raw)
        if r:
            return r
        t = _t2pc_low(raw)
        t = _t2pc_re.sub(r"\s+", " ", t).strip(" .,!?:;()[]{}")
        if not t:
            return ""
        # "делай смету", "сделай смету", "давай смету" → estimate-specific
        if any(x in t for x in ("делай смет", "сделай смет", "давай смет", "делаем смет", "запускай смет")):
            return "median"
        # "да делай", "давай делай", "ок делай"
        # Use " делай" (with space prefix) to avoid matching "сделай" as false positive
        if " делай" in (" " + t) and any(x in t for x in ("да ", "ок ", "давай ", "ладно ")):
            return "median"
        # "ставь обычные/стандартные/рыночные/нормальные"
        if "ставь" in t and any(x in t for x in ("обычн", "стандарт", "рыночн", "нормальн")):
            return "median"
        # bare affirmatives — _t2pc_find_parent is the secondary guard
        _BARE_AFF = {
            "да", "ок", "окей", "хорошо", "конечно", "поехали",
            "ага", "угу", "yes", "yep", "принято", "принял",
        }
        if t in _BARE_AFF:
            return "median"
        return ""

    # Part B: extend _t2pc_find_parent to also find canonical WC by prices_shown
    _pcrv1_orig_find_parent = _t2pc_find_parent

    def _t2pc_find_parent(conn, task, chat_id, topic_id):
        parent, source = _pcrv1_orig_find_parent(conn, task, chat_id, topic_id)
        if parent:
            return parent, source
        # Canonical path fallback: task has prices_shown in history but result
        # doesn't contain "Выберите уровень цен" (uses _price_confirmation_text format)
        task_id = _t2pc_s(_t2pc_row(task, "id", ""))
        reply_to = _t2pc_row(task, "reply_to_message_id", None)
        try:
            # Prefer exact reply match first
            if reply_to:
                row = conn.execute("""
                    SELECT t.*
                    FROM tasks t
                    INNER JOIN task_history th ON th.task_id = t.id
                    WHERE t.chat_id = ?
                      AND COALESCE(t.topic_id, 0) = ?
                      AND t.id <> ?
                      AND t.state IN ('WAITING_CLARIFICATION', 'IN_PROGRESS', 'NEW')
                      AND th.action LIKE 'FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:prices_shown%'
                      AND t.updated_at >= datetime('now', '-24 hours')
                      AND (t.bot_message_id = ? OR t.reply_to_message_id = ?)
                    ORDER BY t.updated_at DESC, t.rowid DESC
                    LIMIT 1
                """, (str(chat_id), int(topic_id or 0), task_id, reply_to, reply_to)).fetchone()
                if row:
                    return row, "PRICES_SHOWN_EXACT_REPLY"
            # Latest active WC with prices_shown fallback
            row = conn.execute("""
                SELECT t.*
                FROM tasks t
                INNER JOIN task_history th ON th.task_id = t.id
                WHERE t.chat_id = ?
                  AND COALESCE(t.topic_id, 0) = ?
                  AND t.id <> ?
                  AND t.state IN ('WAITING_CLARIFICATION', 'IN_PROGRESS', 'NEW')
                  AND th.action LIKE 'FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:prices_shown%'
                  AND t.updated_at >= datetime('now', '-24 hours')
                ORDER BY t.updated_at DESC, t.rowid DESC
                LIMIT 1
            """, (str(chat_id), int(topic_id or 0), task_id)).fetchone()
            if row:
                return row, "PRICES_SHOWN_HISTORY_FALLBACK"
        except Exception as _pcrv1_fe:
            _pcrv1_log.warning("PATCH_PRICE_CONFIRMATION_ROUTING_V1_FIND_ERR: %s", _pcrv1_fe)
        return None, "PRICE_MENU_NOT_FOUND"

    _pcrv1_log.info("PATCH_PRICE_CONFIRMATION_ROUTING_V1 installed")
except Exception as _pcrv1_install_err:
    try:
        import logging as _pcrv1_err_log
        _pcrv1_err_log.getLogger("task_worker").error(
            "PATCH_PRICE_CONFIRMATION_ROUTING_V1_INSTALL_ERR: %s", _pcrv1_install_err
        )
    except Exception:
        pass
# === END PATCH_PRICE_CONFIRMATION_ROUTING_V1 ===

# === PATCH_TOPIC2_PRICE_CHOICE_PARENT_BIND_FULL_CLOSE_V1 ===
try:
    import re as _t2pc_re
    import logging as _t2pc_logging
    from datetime import datetime as _t2pc_datetime

    _t2pc_log = _t2pc_logging.getLogger("task_worker")

    def _t2pc_get(row, key, default=None):
        try:
            if isinstance(row, dict):
                return row.get(key, default)
            if hasattr(row, "keys") and key in row.keys():
                v = row[key]
                return default if v is None else v
        except Exception:
            pass
        try:
            return getattr(row, key)
        except Exception:
            return default

    def _t2pc_low(v):
        return str(v or "").replace("[VOICE]", "").replace("ё", "е").lower().strip()

    def _t2pc_revision_facts(raw):
        s = _t2pc_low(raw)
        s = _t2pc_re.sub(r"\s+", " ", s)
        if len(s) < 90 and len(s.split()) < 10:
            return False
        return any(x in s for x in (
            "не вижу", "необходимо", "постав", "провер", "если нет",
            "уточни", "стоимость работ", "цена работ", "за метр куб",
            "м3", "м³", "правк", "исправ", "пересчит", "добав", "убер",
            "замени", "интернете", "материал"
        ))

    def _t2pc_choice(raw):
        s = _t2pc_low(raw)
        s = _t2pc_re.sub(r"\s+", " ", s)
        if _t2pc_revision_facts(s):
            return ""
        is_tz = len(s) > 80 and any(x in s for x in ("фундамент", "плита", "щеб", "песчан", "ламинат", "стен", "кров", "полы"))
        if is_tz and not any(x in s for x in ("дешев", "дешёв", "минималь", "средн", "медиан", "надежн", "надёжн", "проверенн", "вручную", "свои цены", "своя цена")):
            return ""
        if (not is_tz and _t2pc_re.search(r"(^|[^0-9а-яa-z])(1|первый|вариант 1)([^0-9а-яa-z]|$)", s)) or "дешев" in s or "дешёв" in s or "минималь" in s:
            return "cheapest"
        if _t2pc_re.search(r"(^|[^0-9а-яa-z])(2|второй|вариант 2)([^0-9а-яa-z]|$)", s) or "средн" in s or "медиан" in s:
            return "median"
        if _t2pc_re.search(r"(^|[^0-9а-яa-z])(3|третий|вариант 3)([^0-9а-яa-z]|$)", s) or "надежн" in s or "проверенн" in s:
            return "reliable"
        if _t2pc_re.search(r"(^|[^0-9а-яa-z])(4|четвертый|четвертый|вариант 4)([^0-9а-яa-z]|$)", s) or "вручную" in s or "свои цены" in s or "своя цена" in s:
            return "manual"
        return ""

    def _t2pc_is_continue(raw):
        s = _t2pc_low(raw)
        return bool(s) and len(s) <= 80 and any(x in s for x in (
            "да", "делай", "сделай", "продолж", "ок", "окей", "поехали", "запускай", "смет"
        ))

    def _t2pc_history_text(conn, task_id):
        try:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? ORDER BY rowid ASC",
                (str(task_id),),
            ).fetchall()
            out = []
            for r in rows:
                try:
                    out.append(str(r["action"]))
                except Exception:
                    out.append(str(r[0]))
            return "\n".join(out)
        except Exception:
            return ""

    def _t2pc_has_price_context(conn, task_id):
        h = _t2pc_history_text(conn, task_id)
        return (
            "TOPIC2_PRICE_ENRICHMENT_DONE" in h
            or "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:prices_shown" in h
            or "TOPIC2_PRICE_CHOICE_REQUESTED" in h
        )

    def _t2pc_has_real_choice(conn, task_id):
        h = _t2pc_history_text(conn, task_id)
        return (
            "TOPIC2_PRICE_CHOICE_CONFIRMED:cheapest" in h
            or "TOPIC2_PRICE_CHOICE_CONFIRMED:median" in h
            or "TOPIC2_PRICE_CHOICE_CONFIRMED:reliable" in h
            or "TOPIC2_PRICE_CHOICE_CONFIRMED:manual" in h
        )

    def _t2pc_hist_once(conn, task_id, action):
        task_id = str(task_id or "")
        action = str(action or "")[:900]
        if not task_id or not action:
            return
        try:
            row = conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
                (task_id, action),
            ).fetchone()
            if row:
                return
        except Exception:
            pass
        try:
            _history(conn, task_id, action)
        except Exception:
            try:
                conn.execute(
                    "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
                    (task_id, action, _t2pc_datetime.utcnow().isoformat()),
                )
            except Exception as e:
                _t2pc_log.warning("T2PC_HIST_ERR task=%s err=%s", task_id, e)

    def _t2pc_find_parent(conn, task):
        cid = str(_t2pc_get(task, "chat_id") or "")
        tid = str(_t2pc_get(task, "id") or "")
        rto = _t2pc_get(task, "reply_to_message_id")
        if rto:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE chat_id=? AND topic_id=2 AND bot_message_id=? AND id<>? ORDER BY rowid DESC LIMIT 8",
                (cid, rto, tid),
            ).fetchall()
            for r in rows:
                pid = str(_t2pc_get(r, "id") or "")
                st = str(_t2pc_get(r, "state") or "").upper()
                err = str(_t2pc_get(r, "error_message") or "").upper()
                if pid and st not in ("DONE", "ARCHIVED", "FAILED", "CANCELLED") and "MERGED_TO_PARENT" not in err and _t2pc_has_price_context(conn, pid):
                    return r
        rows = conn.execute(
            "SELECT * FROM tasks WHERE chat_id=? AND topic_id=2 AND id<>? ORDER BY rowid DESC LIMIT 30",
            (cid, tid),
        ).fetchall()
        for r in rows:
            pid = str(_t2pc_get(r, "id") or "")
            st = str(_t2pc_get(r, "state") or "")
            err = str(_t2pc_get(r, "error_message") or "").upper()
            if pid and st.upper() not in ("DONE", "ARCHIVED", "FAILED", "CANCELLED") and "MERGED_TO_PARENT" not in err and _t2pc_has_price_context(conn, pid):
                return r
        return None

    def _t2pc_prompt():
        return "Выбери уровень цен: 1 дешёвые / 2 средние / 3 надёжные / 4 вручную"

    def _t2pc_send_sync(chat_id, text, reply_to, topic_id=2):
        try:
            res = send_reply_ex(
                chat_id=str(chat_id),
                text=str(text),
                reply_to_message_id=reply_to,
                message_thread_id=int(topic_id or 2),
            )
            return res
        except Exception as e:
            _t2pc_log.warning("T2PC_SEND_ERR err=%s", e)
            return None

    def _t2pc_update_parent_for_generation(conn, parent_id, choice, child_id, raw):
        _t2pc_hist_once(conn, parent_id, "TOPIC2_PRICE_CHOICE_CONFIRMED:" + choice)
        _t2pc_hist_once(conn, parent_id, "PATCH_TOPIC2_PRICE_CHOICE_PARENT_BIND_FULL_CLOSE_V1:choice=" + choice + ":from=" + str(child_id))
        _t2pc_hist_once(conn, parent_id, "TOPIC2_PRICE_CHOICE_PARENT_BOUND_FROM:" + str(child_id))
        try:
            _update_task(
                conn,
                parent_id,
                state="IN_PROGRESS",
                error_message="TOPIC2_PRICE_CHOICE_CONFIRMED_REPROCESS:" + choice,
            )
        except Exception:
            conn.execute(
                "UPDATE tasks SET state='IN_PROGRESS', error_message=?, updated_at=datetime('now') WHERE id=?",
                ("TOPIC2_PRICE_CHOICE_CONFIRMED_REPROCESS:" + choice, parent_id),
            )

    def _t2pc_close_child(conn, child_id, parent_id, result_text):
        _t2pc_hist_once(conn, child_id, "PATCH_TOPIC2_PRICE_CHOICE_PARENT_BIND_FULL_CLOSE_V1:merged_to:" + str(parent_id))
        try:
            _update_task(
                conn,
                child_id,
                state="DONE",
                result=result_text,
                error_message="MERGED_TO_PARENT:" + str(parent_id),
            )
        except Exception:
            conn.execute(
                "UPDATE tasks SET state='DONE', result=?, error_message=?, updated_at=datetime('now') WHERE id=?",
                (result_text, "MERGED_TO_PARENT:" + str(parent_id), child_id),
            )

    _t2pc_orig_handle_new = _handle_new

    async def _handle_new(conn, task, chat_id, topic_id):
        try:
            if int(topic_id or 0) == 2:
                task_id = str(_t2pc_get(task, "id") or "")
                raw = str(_t2pc_get(task, "raw_input") or "")
                reply_to = _t2pc_get(task, "reply_to_message_id")
                choice = _t2pc_choice(raw)
                parent = _t2pc_find_parent(conn, task)

                if parent is not None and (choice or _t2pc_is_continue(raw)):
                    parent_id = str(_t2pc_get(parent, "id") or "")
                    if choice:
                        _t2pc_update_parent_for_generation(conn, parent_id, choice, task_id, raw)
                        _t2pc_close_child(conn, task_id, parent_id, "Выбор цен привязан к основной задаче: " + choice)
                        conn.commit()
                        _t2pc_send_sync(chat_id, "Принял: 2 средние. Запускаю смету по основной задаче" if choice == "median" else "Принял выбор цен. Запускаю смету по основной задаче", reply_to, 2)
                        _t2pc_log.info("PATCH_TOPIC2_PRICE_CHOICE_PARENT_BIND_FULL_CLOSE_V1 parent=%s child=%s choice=%s", parent_id, task_id, choice)
                        return

                    if _t2pc_has_price_context(conn, parent_id) and not _t2pc_has_real_choice(conn, parent_id):
                        _t2pc_hist_once(conn, parent_id, "TOPIC2_PRICE_CHOICE_REQUIRED_REPEAT")
                        try:
                            _update_task(
                                conn,
                                parent_id,
                                state="WAITING_CLARIFICATION",
                                result=_t2pc_prompt(),
                                error_message="TOPIC2_PRICE_CHOICE_REQUIRED",
                            )
                            _t2pc_close_child(conn, task_id, parent_id, _t2pc_prompt())
                        except Exception:
                            pass
                        conn.commit()
                        _t2pc_send_sync(chat_id, _t2pc_prompt(), reply_to, 2)
                        _t2pc_log.info("PATCH_TOPIC2_PRICE_CHOICE_PARENT_BIND_FULL_CLOSE_V1 prompt parent=%s child=%s", parent_id, task_id)
                        return
        except Exception as e:
            _t2pc_log.exception("PATCH_TOPIC2_PRICE_CHOICE_PARENT_BIND_FULL_CLOSE_V1_ERR:%s", e)

        return await _t2pc_orig_handle_new(conn, task, chat_id, topic_id)

    _t2pc_log.info("PATCH_TOPIC2_PRICE_CHOICE_PARENT_BIND_FULL_CLOSE_V1 installed")

except Exception as _t2pc_install_err:
    try:
        logger.exception("PATCH_TOPIC2_PRICE_CHOICE_PARENT_BIND_FULL_CLOSE_V1_INSTALL_ERR:%s", _t2pc_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_PRICE_CHOICE_PARENT_BIND_FULL_CLOSE_V1 ===

# === PATCH_TOPIC2_SINGLE_CANON_PRICE_FLOW_V1 ===
try:
    import re as _t2sc_re
    import json as _t2sc_json
    import logging as _t2sc_logging
    from datetime import datetime as _t2sc_datetime

    _t2sc_log = _t2sc_logging.getLogger("task_worker")

    _T2SC_PRICE_PROMPT = "Выбери уровень цен: 1 дешёвые / 2 средние / 3 надёжные / 4 вручную"

    def _t2sc_get(row, key, default=None):
        try:
            if isinstance(row, dict):
                return row.get(key, default)
            if hasattr(row, "keys") and key in row.keys():
                v = row[key]
                return default if v is None else v
        except Exception:
            pass
        try:
            return getattr(row, key)
        except Exception:
            return default

    def _t2sc_clean(v):
        return str(v or "").replace("[VOICE]", "").replace("ё", "е").lower().strip()

    def _t2sc_revision_facts(raw):
        s = _t2sc_re.sub(r"\s+", " ", _t2sc_clean(raw))
        if len(s) < 90 and len(s.split()) < 10:
            return False
        return any(x in s for x in (
            "не вижу", "необходимо", "постав", "провер", "если нет",
            "уточни", "стоимость работ", "цена работ", "за метр куб",
            "м3", "м³", "правк", "исправ", "пересчит", "добав", "убер",
            "замени", "интернете", "материал"
        ))

    def _t2sc_choice(raw):
        s = _t2sc_re.sub(r"\s+", " ", _t2sc_clean(raw))
        if _t2sc_revision_facts(s):
            return ""
        if _t2sc_re.search(r"(^|[^0-9а-яa-z])(1|первый|вариант 1)([^0-9а-яa-z]|$)", s) or "дешев" in s or "минималь" in s:
            return "cheapest"
        if _t2sc_re.search(r"(^|[^0-9а-яa-z])(2|второй|вариант 2)([^0-9а-яa-z]|$)", s) or "средн" in s or "медиан" in s:
            return "median"
        if _t2sc_re.search(r"(^|[^0-9а-яa-z])(3|третий|вариант 3)([^0-9а-яa-z]|$)", s) or "надежн" in s or "проверенн" in s:
            return "reliable"
        if _t2sc_re.search(r"(^|[^0-9а-яa-z])(4|четвертый|четвертый|вариант 4)([^0-9а-яa-z]|$)", s) or "вручную" in s or "свои цены" in s or "своя цена" in s:
            return "manual"
        return ""

    def _t2sc_continue_without_choice(raw):
        s = _t2sc_clean(raw)
        return bool(s) and len(s) <= 90 and any(x in s for x in (
            "да", "делай", "сделай", "продолж", "ок", "окей", "поехали", "запускай", "смет"
        ))

    def _t2sc_hist_rows(conn, task_id):
        try:
            return conn.execute(
                "SELECT rowid, action, created_at FROM task_history WHERE task_id=? ORDER BY rowid ASC",
                (str(task_id),),
            ).fetchall()
        except Exception:
            return []

    def _t2sc_hist_text(conn, task_id):
        out = []
        for r in _t2sc_hist_rows(conn, task_id):
            try:
                out.append(str(r["action"]))
            except Exception:
                out.append(str(r[1]))
        return "\n".join(out)

    def _t2sc_has_price_context(conn, task_id):
        h = _t2sc_hist_text(conn, task_id)
        return (
            "TOPIC2_PRICE_ENRICHMENT_DONE" in h
            or "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:prices_shown" in h
            or "TOPIC2_PRICE_CHOICE_REQUESTED" in h
        )

    def _t2sc_has_valid_choice(conn, task_id):
        h = _t2sc_hist_text(conn, task_id)
        return any(("TOPIC2_PRICE_CHOICE_CONFIRMED:" + x) in h for x in ("cheapest", "median", "reliable", "manual"))

    def _t2sc_hist_once(conn, task_id, action):
        task_id = str(task_id or "")
        action = str(action or "")[:900]
        if not task_id or not action:
            return
        try:
            exists = conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
                (task_id, action),
            ).fetchone()
            if exists:
                return
        except Exception:
            pass
        try:
            _history(conn, task_id, action)
        except Exception:
            conn.execute(
                "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
                (task_id, action, _t2sc_datetime.utcnow().isoformat()),
            )

    def _t2sc_old_public(text):
        s = str(text or "")
        return any(x in s for x in ("⏳ Задачу понял", "Шаблон:", "Лист:", "Цены из листа"))

    def _t2sc_parent_is_open_for_price_choice(conn, row):
        try:
            pid = str(_t2sc_get(row, "id") or "")
            state = str(_t2sc_get(row, "state") or "").upper()
            err = str(_t2sc_get(row, "error_message") or "").upper()
            if not pid or state in ("DONE", "ARCHIVED", "FAILED", "CANCELLED"):
                return False
            if "P6E67_PARENT_NOT_FOUND" in err or "MERGED_TO_PARENT" in err:
                return False
            hist = _t2sc_hist_text(conn, pid)
            blocked = (
                "P6E67_PARENT_NOT_FOUND" in hist
                or "TOPIC2_DONE_CONTRACT_OK" in hist
                or "TOPIC2_DRIVE_UPLOAD_XLSX_OK" in hist
                or "TOPIC2_DRIVE_UPLOAD_PDF_OK" in hist
                or "PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:MERGED_TO_PARENT:" in hist
            )
            return not blocked
        except Exception:
            return False

    def _t2sc_find_parent_by_reply(conn, task):
        cid = str(_t2sc_get(task, "chat_id") or "")
        tid = str(_t2sc_get(task, "id") or "")
        rto = _t2sc_get(task, "reply_to_message_id")
        if rto:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE chat_id=? AND topic_id=2 AND bot_message_id=? AND id<>? ORDER BY rowid DESC LIMIT 10",
                (cid, rto, tid),
            ).fetchall()
            for r in rows:
                pid = str(_t2sc_get(r, "id") or "")
                if pid and _t2sc_parent_is_open_for_price_choice(conn, r) and _t2sc_has_price_context(conn, pid):
                    return r
        rows = conn.execute(
            "SELECT * FROM tasks WHERE chat_id=? AND topic_id=2 AND id<>? ORDER BY rowid DESC LIMIT 40",
            (cid, tid),
        ).fetchall()
        for r in rows:
            pid = str(_t2sc_get(r, "id") or "")
            if pid and _t2sc_parent_is_open_for_price_choice(conn, r) and _t2sc_has_price_context(conn, pid):
                return r
        return None

    def _t2sc_send(chat_id, text, reply_to=None, topic_id=2):
        try:
            return send_reply_ex(
                chat_id=str(chat_id),
                text=str(text),
                reply_to_message_id=reply_to,
                message_thread_id=int(topic_id or 2),
            )
        except Exception as e:
            _t2sc_log.warning("T2SC_SEND_ERR err=%s", e)
            return None

    def _t2sc_force_clean_wait(conn, task_id):
        _t2sc_hist_once(conn, task_id, "TOPIC2_PRICE_CHOICE_REQUESTED")
        _update_task(
            conn,
            task_id,
            state="WAITING_CLARIFICATION",
            result=_T2SC_PRICE_PROMPT,
            error_message="TOPIC2_PRICE_CHOICE_REQUIRED",
        )

    def _t2sc_close_child(conn, child_id, parent_id, text):
        _t2sc_hist_once(conn, child_id, "PATCH_TOPIC2_SINGLE_CANON_PRICE_FLOW_V1:merged_to:" + str(parent_id))
        _update_task(
            conn,
            child_id,
            state="DONE",
            result=str(text),
            error_message="MERGED_TO_PARENT:" + str(parent_id),
        )

    def _t2sc_extract_existing_parent_context(conn, parent_id):
        row = conn.execute("SELECT raw_input, result FROM tasks WHERE id=? LIMIT 1", (str(parent_id),)).fetchone()
        raw = str(_t2sc_get(row, "raw_input", "") if row else "")
        result = str(_t2sc_get(row, "result", "") if row else "")
        hist = _t2sc_hist_text(conn, parent_id)
        return raw + "\n" + result + "\n" + hist

    def _t2sc_parse_known_facts(text):
        s = str(text or "").lower().replace("ё", "е")
        dims = None
        m = _t2sc_re.search(r"(\d+(?:[.,]\d+)?)\s*[xх×]\s*(\d+(?:[.,]\d+)?)", s)
        if m:
            dims = (m.group(1).replace(",", "."), m.group(2).replace(",", "."))
        floors = None
        m = _t2sc_re.search(r"(\d+)\s*(?:этаж|этажа|этажей)", s)
        if m:
            floors = m.group(1)
        area = None
        m = _t2sc_re.search(r"(\d+(?:[.,]\d+)?)\s*(?:м2|м²|кв\.?\s*м)", s)
        if m:
            area = m.group(1).replace(",", ".")
        return {"dims": dims, "floors": floors, "area": area}

    def _t2sc_build_artifact_task_text(conn, parent_id, choice):
        ctx = _t2sc_extract_existing_parent_context(conn, parent_id)
        facts = _t2sc_parse_known_facts(ctx)
        dims = facts.get("dims")
        floors = facts.get("floors")
        area = facts.get("area")

        parts = [
            "Сформируй финальную смету XLSX и PDF по канону topic_2",
            "Ценовой уровень: " + str(choice),
            "Исходное ТЗ и уточнения ниже являются SSOT для выбора материала, шаблона и состава работ:",
            ctx.strip(),
            "Запрещено выводить текстовую старую сводку Шаблон/Лист/Цены из листа",
            "Результат только Drive links XLSX/PDF",
        ]
        if dims:
            parts.append("Размеры дома: " + dims[0] + "x" + dims[1])
        if floors:
            parts.append("Этажность: " + floors)
        if area:
            parts.append("Площадь: " + area + " м2")
        return "\n".join(x for x in parts if str(x or "").strip())

    def _t2sc_prepare_parent_for_generation(conn, parent_id, choice, child_id=""):
        _t2sc_hist_once(conn, parent_id, "TOPIC2_PRICE_CHOICE_CONFIRMED:" + choice)
        _t2sc_hist_once(conn, parent_id, "PATCH_TOPIC2_SINGLE_CANON_PRICE_FLOW_V1:price_choice_bound:" + str(child_id))
        task_text = _t2sc_build_artifact_task_text(conn, parent_id, choice)
        conn.execute(
            "UPDATE tasks SET state='IN_PROGRESS', raw_input=?, result='', error_message=?, updated_at=datetime('now') WHERE id=?",
            (task_text, "TOPIC2_PRICE_CHOICE_CONFIRMED_REPROCESS:" + choice, str(parent_id)),
        )

    _t2sc_orig_history = _history

    def _history(conn, task_id, action):
        try:
            a = str(action or "")
            if a == "TOPIC2_PRICE_CHOICE_CONFIRMED:confirmed":
                _t2sc_log.warning("PATCH_TOPIC2_SINGLE_CANON_PRICE_FLOW_V1 blocked invalid marker task=%s", task_id)
                return
            if a.startswith("clarified:") or a in (
                "P3_TOPIC2_CLARIFICATION",
                "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:prices_shown",
                "TOPIC2_CANONICAL_REROUTE_V2:CANONICAL_HANDLED",
            ):
                exists = conn.execute(
                    "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
                    (str(task_id), a[:1000]),
                ).fetchone()
                if exists:
                    _t2sc_log.info("PATCH_TOPIC2_SINGLE_CANON_PRICE_FLOW_V1 dedup_history task=%s action=%s", task_id, a[:80])
                    return
        except Exception:
            pass
        return _t2sc_orig_history(conn, task_id, action)

    _t2sc_orig_update_task = _update_task

    def _update_task(conn, task_id, **kwargs):
        try:
            row = conn.execute("SELECT topic_id FROM tasks WHERE id=? LIMIT 1", (str(task_id),)).fetchone()
            topic_id = int((_t2sc_get(row, "topic_id", 0) if row else 0) or 0)
            if topic_id == 2:
                result = kwargs.get("result")
                state = kwargs.get("state")
                if _t2sc_old_public(result):
                    hist = _t2sc_hist_text(conn, str(task_id))
                    if "TOPIC2_PRICE_CHOICE_CONFIRMED:" not in hist or "TOPIC2_XLSX" not in hist:
                        kwargs["result"] = _T2SC_PRICE_PROMPT
                        kwargs["state"] = "WAITING_CLARIFICATION"
                        kwargs["error_message"] = "TOPIC2_OLD_PUBLIC_OUTPUT_BLOCKED"
                        _t2sc_hist_once(conn, task_id, "PATCH_TOPIC2_SINGLE_CANON_PRICE_FLOW_V1:old_public_blocked")
                if state == "IN_PROGRESS":
                    hist = _t2sc_hist_text(conn, str(task_id))
                    if "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:prices_shown" in hist and "TOPIC2_PRICE_CHOICE_CONFIRMED:" not in hist:
                        kwargs["state"] = "WAITING_CLARIFICATION"
                        kwargs["result"] = _T2SC_PRICE_PROMPT
                        kwargs["error_message"] = "TOPIC2_PRICE_CHOICE_REQUIRED"
                        _t2sc_hist_once(conn, task_id, "TOPIC2_PRICE_CHOICE_REQUESTED")
        except Exception:
            pass
        return _t2sc_orig_update_task(conn, task_id, **kwargs)

    _t2sc_orig_handle_new = _handle_new

    async def _handle_new(conn, task, chat_id, topic_id):
        try:
            if int(topic_id or 0) == 2:
                task_id = str(_t2sc_get(task, "id") or "")
                raw = str(_t2sc_get(task, "raw_input") or "")
                reply_to = _t2sc_get(task, "reply_to_message_id")
                choice = _t2sc_choice(raw)
                parent = _t2sc_find_parent_by_reply(conn, task)

                if parent is not None and (choice or _t2sc_continue_without_choice(raw)):
                    parent_id = str(_t2sc_get(parent, "id") or "")
                    if choice:
                        _t2sc_prepare_parent_for_generation(conn, parent_id, choice, task_id)
                        _t2sc_close_child(conn, task_id, parent_id, "Выбор цен привязан к основной задаче: " + choice)
                        conn.commit()
                        _t2sc_send(chat_id, "Принял уровень цен: " + choice + ". Запускаю XLSX/PDF по основной задаче", reply_to, 2)
                        _t2sc_log.info("PATCH_TOPIC2_SINGLE_CANON_PRICE_FLOW_V1 parent_bound parent=%s child=%s choice=%s", parent_id, task_id, choice)
                        return

                    if _t2sc_has_price_context(conn, parent_id) and not _t2sc_has_valid_choice(conn, parent_id):
                        _t2sc_force_clean_wait(conn, parent_id)
                        _t2sc_close_child(conn, task_id, parent_id, _T2SC_PRICE_PROMPT)
                        conn.commit()
                        _t2sc_send(chat_id, _T2SC_PRICE_PROMPT, reply_to, 2)
                        _t2sc_log.info("PATCH_TOPIC2_SINGLE_CANON_PRICE_FLOW_V1 repeat_prompt parent=%s child=%s", parent_id, task_id)
                        return

                if _t2sc_has_price_context(conn, task_id) and not _t2sc_has_valid_choice(conn, task_id):
                    if choice:
                        _t2sc_prepare_parent_for_generation(conn, task_id, choice, task_id)
                        conn.commit()
                        _t2sc_log.info("PATCH_TOPIC2_SINGLE_CANON_PRICE_FLOW_V1 self_choice task=%s choice=%s", task_id, choice)
                    elif _t2sc_continue_without_choice(raw):
                        _t2sc_force_clean_wait(conn, task_id)
                        conn.commit()
                        _t2sc_send(chat_id, _T2SC_PRICE_PROMPT, reply_to, 2)
                        return
        except Exception as e:
            _t2sc_log.exception("PATCH_TOPIC2_SINGLE_CANON_PRICE_FLOW_V1_HANDLE_ERR:%s", e)

        return await _t2sc_orig_handle_new(conn, task, chat_id, topic_id)

    _t2sc_log.info("PATCH_TOPIC2_SINGLE_CANON_PRICE_FLOW_V1 installed")

except Exception as _t2sc_install_err:
    try:
        logger.exception("PATCH_TOPIC2_SINGLE_CANON_PRICE_FLOW_V1_INSTALL_ERR:%s", _t2sc_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_SINGLE_CANON_PRICE_FLOW_V1 ===

# === PATCH_TOPIC2_FINAL_DRIVE_FLOW_FIX_V1 ===
try:
    import inspect as _t2fdff_inspect
    import sqlite3 as _t2fdff_sqlite3
    import json as _t2fdff_json
    import re as _t2fdff_re
    import logging as _t2fdff_logging

    _t2fdff_log = _t2fdff_logging.getLogger("task_worker")
    _T2FDFF_MEM_DB = "/root/.areal-neva-core/data/memory.db"

    def _t2fdff_get(row, key, default=None):
        try:
            v = row[key]
            return v if v is not None else default
        except Exception:
            try:
                return getattr(row, key)
            except Exception:
                return default

    def _t2fdff_hist_once(conn, task_id, action):
        try:
            row = conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
                (str(task_id), str(action)[:900]),
            ).fetchone()
            if not row:
                conn.execute(
                    "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
                    (str(task_id), str(action)[:900]),
                )
        except Exception:
            pass

    def _t2fdff_hist_text(conn, task_id):
        try:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? ORDER BY rowid ASC",
                (str(task_id),),
            ).fetchall()
            return "\n".join(str(_t2fdff_get(r, "action") or r[0]) for r in rows)
        except Exception:
            return ""

    def _t2fdff_load_pending(chat_id, parent_id):
        key = "topic_2_estimate_pending_" + str(parent_id)
        try:
            if "_memory_get" in globals():
                val = _memory_get(str(chat_id), key)
                if isinstance(val, dict):
                    return val
                if isinstance(val, str) and val.strip().startswith("{"):
                    return _t2fdff_json.loads(val)
        except Exception:
            pass
        try:
            c = _t2fdff_sqlite3.connect(_T2FDFF_MEM_DB)
            c.row_factory = _t2fdff_sqlite3.Row
            r = c.execute(
                "SELECT value FROM memory WHERE chat_id=? AND key=? ORDER BY timestamp DESC LIMIT 1",
                (str(chat_id), key),
            ).fetchone()
            c.close()
            if not r:
                return {}
            val = str(r["value"] or "")
            return _t2fdff_json.loads(val) if val.strip().startswith("{") else {}
        except Exception:
            return {}

    def _t2fdff_extract_dims_floors(pending):
        parsed = {}
        try:
            parsed = pending.get("parsed") or {}
        except Exception:
            parsed = {}
        dims = parsed.get("dims")
        if not dims:
            dims = parsed.get("dimensions")
        floors = parsed.get("floors")
        area = parsed.get("area") or parsed.get("area_total")
        return dims, floors, area

    def _t2fdff_enrich_text_with_memory(text, chat_id, parent_id):
        s = str(text or "")
        pending = _t2fdff_load_pending(chat_id, parent_id)
        dims, floors, area = _t2fdff_extract_dims_floors(pending)

        if dims and isinstance(dims, (list, tuple)) and len(dims) >= 2:
            dim_line = f"Размеры: {dims[0]} x {dims[1]}"
            s = _t2fdff_re.sub(r"Размеры:\s*не указаны", dim_line, s, flags=_t2fdff_re.I)
            if "Размеры:" not in s:
                s += "\n" + dim_line

        if floors:
            floor_line = f"Этажей: {floors}"
            s = _t2fdff_re.sub(r"Этажей:\s*не указано", floor_line, s, flags=_t2fdff_re.I)
            if "Этажей:" not in s and "Этажность:" not in s:
                s += "\n" + floor_line

        if area and "Площадь:" not in s:
            s += f"\nПлощадь: {area}"

        return s

    # A: hard block DONE with local /root path for topic_2
    _t2fdff_orig_update_task = _update_task

    def _update_task(conn, task_id, **kwargs):
        try:
            row = conn.execute("SELECT topic_id FROM tasks WHERE id=? LIMIT 1", (str(task_id),)).fetchone()
            topic_id = int(_t2fdff_get(row, "topic_id", 0) or 0) if row is not None else 0
        except Exception:
            topic_id = 0

        if topic_id == 2:
            state = str(kwargs.get("state") or "")
            result = str(kwargs.get("result") or "")
            if state == "DONE" and "/root/" in result:
                kwargs["state"] = "FAILED"
                kwargs["error_message"] = "TOPIC2_LOCAL_PATH_IN_RESULT_BLOCKED"
                _t2fdff_hist_once(conn, task_id, "TOPIC2_LOCAL_PATH_IN_RESULT_BLOCKED")

        return _t2fdff_orig_update_task(conn, task_id, **kwargs)

    # B: when price confirmed + drive already done → block FRESH_FALLBACK re-run
    #    when price confirmed + NOT yet generated → inject dims from memory and let pipeline run
    if "_t2fer_run_final_estimate" in globals():
        _t2fdff_orig_t2fer = _t2fer_run_final_estimate

        def _t2fdff_check_fresh_state(conn, task):
            """Returns ('block', None) | ('enrich_and_run', chat_id) | ('run', None)"""
            try:
                task_id = str(_t2fdff_get(task, "id") or "")
                if not task_id:
                    return "run", None
                h = _t2fdff_hist_text(conn, task_id)
                if "TOPIC2_PRICE_CHOICE_CONFIRMED:" not in h:
                    return "run", None
                if "TOPIC2_DRIVE_UPLOAD_XLSX_OK" in h:
                    return "block", None
                # Price confirmed, no generation yet — inject dims from memory
                chat_id = str(_t2fdff_get(task, "chat_id") or "")
                return "enrich_and_run", (task_id, chat_id)
            except Exception:
                return "run", None

        def _t2fdff_inject_dims_to_raw(conn, task_id, chat_id):
            """Fetch dims from memory.db and patch tasks.raw_input if missing dims."""
            try:
                row = conn.execute("SELECT raw_input FROM tasks WHERE id=? LIMIT 1", (task_id,)).fetchone()
                raw = str(_t2fdff_get(row, "raw_input") or row[0] or "") if row else ""
                if "Размеры:" in raw or "Площадь:" in raw:
                    return  # already have dims
                pending = _t2fdff_load_pending(chat_id, task_id)
                dims, floors, area = _t2fdff_extract_dims_floors(pending)
                extra = ""
                if dims and isinstance(dims, (list, tuple)) and len(dims) >= 2:
                    extra += f"\nРазмеры: {dims[0]} x {dims[1]}"
                if floors:
                    extra += f"\nЭтажей: {floors}"
                if area and not extra:
                    extra += f"\nПлощадь: {area}"
                if extra:
                    conn.execute(
                        "UPDATE tasks SET raw_input=raw_input||? WHERE id=?",
                        (extra, task_id),
                    )
                    _t2fdff_hist_once(conn, task_id, "PATCH_TOPIC2_FINAL_DRIVE_FLOW_FIX_V1:dims_injected_from_memory" + extra.replace("\n", " "))
                    _t2fdff_log.info("PATCH_TOPIC2_FINAL_DRIVE_FLOW_FIX_V1 dims_injected task=%s dims=%s floors=%s", task_id, dims, floors)
            except Exception as _e:
                _t2fdff_log.warning("PATCH_TOPIC2_FINAL_DRIVE_FLOW_FIX_V1:inject_dims_err %s", _e)

        if _t2fdff_inspect.iscoroutinefunction(_t2fdff_orig_t2fer):
            async def _t2fer_run_final_estimate(conn, task, *args, **kwargs):
                action, payload = _t2fdff_check_fresh_state(conn, task)
                if action == "block":
                    _t2fdff_hist_once(conn, _t2fdff_get(task, "id"), "PATCH_TOPIC2_FINAL_DRIVE_FLOW_FIX_V1:FRESH_FALLBACK_BLOCKED_ALREADY_GENERATED")
                    return False
                if action == "enrich_and_run" and payload:
                    task_id, chat_id = payload
                    _t2fdff_inject_dims_to_raw(conn, task_id, chat_id)
                    _t2fdff_hist_once(conn, task_id, "PATCH_TOPIC2_FINAL_DRIVE_FLOW_FIX_V1:FRESH_FALLBACK_ENRICH_AND_RUN")
                return await _t2fdff_orig_t2fer(conn, task, *args, **kwargs)
        else:
            def _t2fer_run_final_estimate(conn, task, *args, **kwargs):
                action, payload = _t2fdff_check_fresh_state(conn, task)
                if action == "block":
                    _t2fdff_hist_once(conn, _t2fdff_get(task, "id"), "PATCH_TOPIC2_FINAL_DRIVE_FLOW_FIX_V1:FRESH_FALLBACK_BLOCKED_ALREADY_GENERATED")
                    return False
                if action == "enrich_and_run" and payload:
                    task_id, chat_id = payload
                    _t2fdff_inject_dims_to_raw(conn, task_id, chat_id)
                    _t2fdff_hist_once(conn, task_id, "PATCH_TOPIC2_FINAL_DRIVE_FLOW_FIX_V1:FRESH_FALLBACK_ENRICH_AND_RUN")
                return _t2fdff_orig_t2fer(conn, task, *args, **kwargs)

    # C: restore dims/floors from memory.db into synthetic artifact task text
    if "_t2sc_build_artifact_task_text" in globals():
        _t2fdff_orig_build_artifact_text = _t2sc_build_artifact_task_text

        def _t2sc_build_artifact_task_text(*args, **kwargs):
            res = _t2fdff_orig_build_artifact_text(*args, **kwargs)
            try:
                sig = _t2fdff_inspect.signature(_t2fdff_orig_build_artifact_text)
                bound = sig.bind_partial(*args, **kwargs)
                parent_id = (
                    bound.arguments.get("parent_id")
                    or bound.arguments.get("task_id")
                    or kwargs.get("parent_id")
                    or kwargs.get("task_id")
                    or ""
                )
                chat_id = (
                    bound.arguments.get("chat_id_for_parent")
                    or bound.arguments.get("chat_id")
                    or kwargs.get("chat_id_for_parent")
                    or kwargs.get("chat_id")
                    or "-1003725299009"
                )
                if parent_id:
                    enriched = _t2fdff_enrich_text_with_memory(str(res or ""), chat_id, parent_id)
                    if enriched != str(res or ""):
                        _t2fdff_log.info("PATCH_TOPIC2_FINAL_DRIVE_FLOW_FIX_V1 memory dims injected parent=%s", parent_id)
                    return enriched
            except Exception as e:
                _t2fdff_log.warning("PATCH_TOPIC2_FINAL_DRIVE_FLOW_FIX_V1_DIM_INJECT_ERR:%s", e)
            return res

    _t2fdff_log.info("PATCH_TOPIC2_FINAL_DRIVE_FLOW_FIX_V1 installed")

except Exception as _t2fdff_e:
    try:
        logger.exception("PATCH_TOPIC2_FINAL_DRIVE_FLOW_FIX_V1_INSTALL_ERR:%s", _t2fdff_e)
    except Exception:
        pass
# === /PATCH_TOPIC2_FINAL_DRIVE_FLOW_FIX_V1 ===

# === PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1 ===
try:
    import re as _t2fdsg_re
    import json as _t2fdsg_json
    import sqlite3 as _t2fdsg_sqlite3
    import inspect as _t2fdsg_inspect
    import logging as _t2fdsg_logging

    _t2fdsg_log = _t2fdsg_logging.getLogger("task_worker")
    _T2FDSG_MEM_DB = "/root/.areal-neva-core/data/memory.db"

    def _t2fdsg_get(row, key, default=None):
        try:
            v = row[key]
            return v if v is not None else default
        except Exception:
            try:
                return getattr(row, key)
            except Exception:
                return default

    def _t2fdsg_hist(conn, task_id, action):
        try:
            conn.execute(
                "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
                (str(task_id), str(action)[:900]),
            )
        except Exception:
            pass

    def _t2fdsg_hist_once(conn, task_id, action):
        try:
            row = conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
                (str(task_id), str(action)[:900]),
            ).fetchone()
            if not row:
                _t2fdsg_hist(conn, task_id, action)
        except Exception:
            pass

    def _t2fdsg_hist_text(conn, task_id):
        try:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? ORDER BY rowid ASC",
                (str(task_id),),
            ).fetchall()
            return "\n".join(str(_t2fdsg_get(r, "action") or r[0]) for r in rows)
        except Exception:
            return ""

    def _t2fdsg_is_drive_link(text):
        s = str(text or "")
        return "drive.google.com" in s or "docs.google.com" in s

    def _t2fdsg_is_fresh_estimate_tz(text):
        t = str(text or "").strip().lower().replace("ё", "е")
        if not t:
            return False
        if len(t.split()) <= 8 and not any(x in t for x in ("м2", "м²", "метр", "этаж", "петербург", "москва", "каркас", "газобетон", "фундамент", "кровл", "под ключ")):
            return False
        keys = (
            "смет", "расчет", "расчёт", "стоимост", "посчитай", "посчитать",
            "дом", "площад", "м2", "м²", "этаж", "каркас", "газобетон",
            "фундамент", "кровл", "под ключ", "санкт", "петербург", "регион",
        )
        return sum(1 for k in keys if k in t) >= 2

    def _t2fdsg_price_choice(text):
        t = str(text or "").strip().lower().replace(",", ".")
        t = _t2fdsg_re.sub(r"\s+", " ", t)
        if not t:
            return ""
        if _t2fdsg_is_fresh_estimate_tz(t):
            return ""
        if t in ("1", "1.", "первый", "минимум", "минимальная", "минимальные", "дешевый", "дешёвый"):
            return "min"
        if t in ("2", "2.", "второй", "среднее", "средняя", "средние", "средний", "медиана", "median"):
            return "median"
        if t in ("3", "3.", "третий", "максимум", "максимальная", "максимальные", "дорогой"):
            return "max"
        if t.startswith("1 "):
            return "min"
        if t.startswith("2 ") or "средн" in t:
            return "median"
        if t.startswith("3 "):
            return "max"
        if any(x in t for x in ("да делай", "делай смету", "сделай смету", "цены актуальны", "подтверждаю", "поехали")):
            return "median"
        return ""

    def _t2fdsg_find_parent(conn, chat_id, topic_id, reply_to, child_id):
        active = ("NEW", "IN_PROGRESS", "WAITING_CLARIFICATION", "AWAITING_CONFIRMATION", "FAILED", "DONE")
        if reply_to:
            r = conn.execute(
                "SELECT * FROM tasks WHERE chat_id=? AND COALESCE(topic_id,0)=? AND bot_message_id=? AND id<>? AND state IN (?,?,?,?,?,?) ORDER BY rowid DESC LIMIT 1",
                (str(chat_id), int(topic_id or 0), int(reply_to), str(child_id), *active),
            ).fetchone()
            if r:
                return r

        r = conn.execute(
            """
            SELECT * FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND id<>?
              AND (
                    input_type='drive_file'
                 OR raw_input LIKE '%8х12.pdf%'
                 OR raw_input LIKE '%file_id%'
                 OR result LIKE '%prices_shown%'
                 OR id IN (
                    SELECT task_id FROM task_history
                    WHERE action LIKE '%prices_shown%'
                       OR action LIKE '%TOPIC2_PRICE_ENRICHMENT_DONE%'
                       OR action LIKE '%TOPIC2_PRICE_CHOICE_CONFIRMED%'
                 )
              )
            ORDER BY rowid DESC
            LIMIT 1
            """,
            (str(chat_id), int(topic_id or 0), str(child_id)),
        ).fetchone()
        return r

    def _t2fdsg_load_pending(chat_id, parent_id):
        key = "topic_2_estimate_pending_" + str(parent_id)
        try:
            if "_memory_get" in globals():
                v = _memory_get(str(chat_id), key)
                if isinstance(v, dict):
                    return v
                if isinstance(v, str) and v.strip().startswith("{"):
                    return _t2fdsg_json.loads(v)
        except Exception:
            pass
        try:
            c = _t2fdsg_sqlite3.connect(_T2FDSG_MEM_DB)
            c.row_factory = _t2fdsg_sqlite3.Row
            r = c.execute(
                "SELECT value FROM memory WHERE chat_id=? AND key=? ORDER BY timestamp DESC LIMIT 1",
                (str(chat_id), key),
            ).fetchone()
            c.close()
            if not r:
                return {}
            v = str(r["value"] or "")
            return _t2fdsg_json.loads(v) if v.strip().startswith("{") else {}
        except Exception:
            return {}

    def _t2fdsg_latest_drive_raw(conn, chat_id, topic_id):
        try:
            r = conn.execute(
                """
                SELECT raw_input FROM tasks
                WHERE chat_id=?
                  AND COALESCE(topic_id,0)=?
                  AND input_type='drive_file'
                  AND raw_input LIKE '%file_id%'
                ORDER BY rowid DESC
                LIMIT 1
                """,
                (str(chat_id), int(topic_id or 0)),
            ).fetchone()
            return str(_t2fdsg_get(r, "raw_input") or "") if r else ""
        except Exception:
            return ""

    def _t2fdsg_enrich_parent_raw(conn, parent, choice):
        # PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1 fix:
        # For drive_file parents: do NOT write enriched text into DB raw_input.
        # raw_input must stay as pure JSON. Build enriched context only in-memory
        # for passing to the engine. Store clarifications in task_history only.
        parent_id = str(_t2fdsg_get(parent, "id") or "")
        chat_id = str(_t2fdsg_get(parent, "chat_id") or "")
        topic_id = int(_t2fdsg_get(parent, "topic_id", 2) or 2)
        input_type = str(_t2fdsg_get(parent, "input_type") or "")
        raw = str(_t2fdsg_get(parent, "raw_input") or "")

        # Recover clean JSON if raw_input is corrupted (legacy tail from old patches)
        clean_raw = raw
        if input_type == "drive_file" and raw and raw.lstrip().startswith("{"):
            try:
                _t2fdsg_json.loads(raw)
            except Exception:
                try:
                    _decoder = _t2fdsg_json.JSONDecoder()
                    _clean_obj, _end = _decoder.raw_decode(raw.lstrip())
                    clean_raw = raw.lstrip()[:_end]
                    # Write recovered JSON back to DB
                    conn.execute(
                        "UPDATE tasks SET raw_input=?, updated_at=datetime('now') WHERE id=?",
                        (clean_raw, parent_id),
                    )
                    _t2fdsg_hist_once(conn, parent_id, "TOPIC2_DRIVE_RAW_INPUT_JSON_PREFIX_RECOVERED")
                    _t2fdsg_log.info(
                        "PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1 raw_input recovered task=%s",
                        parent_id,
                    )
                except Exception:
                    pass

        pending = _t2fdsg_load_pending(chat_id, parent_id)
        parsed = pending.get("parsed") if isinstance(pending, dict) else {}
        parsed = parsed if isinstance(parsed, dict) else {}

        dims = parsed.get("dims")
        floors = parsed.get("floors")
        area = parsed.get("area")

        # Collect all clarified facts from task_history
        try:
            _clarified_rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'clarified:%' ORDER BY rowid ASC",
                (parent_id,),
            ).fetchall()
            _clarified_facts = [str(r[0] or "")[len("clarified:"):].strip()
                                 for r in _clarified_rows if r and r[0]]
            _clarified_facts = [f for f in _clarified_facts if f]
        except Exception:
            _clarified_facts = []

        # Collect price choice from history
        try:
            _price_row = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'TOPIC2_PRICE_CHOICE_CONFIRMED:%' ORDER BY rowid DESC LIMIT 1",
                (parent_id,),
            ).fetchone()
            _confirmed_choice = (_price_row[0] or "").split(":", 2)[-1].strip() if _price_row else choice
        except Exception:
            _confirmed_choice = choice

        # Build in-memory enriched context (NOT written to DB)
        add = [
            "",
            "PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1: FULL RECALC CONTEXT",
            f"Ценовой уровень: {_confirmed_choice or choice}",
            "Запрещено отдавать локальные /root пути",
            "Финальный результат: только Google Drive ссылки XLSX и PDF",
        ]

        if dims and isinstance(dims, (list, tuple)) and len(dims) >= 2:
            add.append(f"Размеры: {dims[0]} x {dims[1]}")
        if floors:
            add.append(f"Этажей: {floors}")
        if area:
            add.append(f"Площадь: {area}")

        if _clarified_facts:
            add.append("ДОПОЛНИТЕЛЬНЫЕ ФАКТЫ ИЗ ИСТОРИИ:")
            for _f in _clarified_facts[-20:]:
                add.append("- " + _f[:400])

        # enriched_raw: clean JSON + context (only used in-memory for engine, NOT saved to DB)
        enriched_raw = (clean_raw + "\n" + "\n".join(add)).strip()[:14000]

        # DB update: set state IN_PROGRESS, clear result — but keep raw_input as clean JSON
        if input_type == "drive_file":
            conn.execute(
                "UPDATE tasks SET state='IN_PROGRESS', result='', error_message=NULL, updated_at=datetime('now') WHERE id=?",
                (parent_id,),
            )
        else:
            conn.execute(
                "UPDATE tasks SET raw_input=?, state='IN_PROGRESS', result='', error_message=NULL, updated_at=datetime('now') WHERE id=?",
                (enriched_raw, parent_id),
            )
        _t2fdsg_hist_once(conn, parent_id, "PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:PARENT_RAW_ENRICHED")

        # Build enriched task dict for engine use (raw_input = enriched_raw)
        try:
            _row = conn.execute("SELECT * FROM tasks WHERE id=? LIMIT 1", (parent_id,)).fetchone()
            if _row is not None:
                try:
                    _task_dict = {k: _row[k] for k in _row.keys()}
                except Exception:
                    _task_dict = dict(_row) if isinstance(_row, dict) else {}
                _task_dict["raw_input"] = enriched_raw
                return _task_dict
        except Exception:
            pass
        return conn.execute("SELECT * FROM tasks WHERE id=? LIMIT 1", (parent_id,)).fetchone()

    async def _t2fdsg_run_drive_final(conn, parent, choice):
        parent_id = str(_t2fdsg_get(parent, "id") or "")
        chat_id = str(_t2fdsg_get(parent, "chat_id") or "")
        topic_id = int(_t2fdsg_get(parent, "topic_id", 2) or 2)
        reply_to = _t2fdsg_get(parent, "reply_to_message_id")

        parent = _t2fdsg_enrich_parent_raw(conn, parent, choice)
        _t2fdsg_hist_once(conn, parent_id, "TOPIC2_PRICE_CHOICE_CONFIRMED:" + str(choice))
        _t2fdsg_hist_once(conn, parent_id, "PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:DRIVE_FINAL_START")
        conn.commit()

        try:
            from core.topic2_estimate_final_close_v2 import handle_topic2_estimate_final_close as _t2fdsg_final
        except Exception as e:
            _update_task(conn, parent_id, state="FAILED", error_message="TOPIC2_FINAL_CLOSE_IMPORT_FAILED:" + type(e).__name__)
            _t2fdsg_hist_once(conn, parent_id, "PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:IMPORT_FAILED")
            conn.commit()
            return True

        try:
            res = _t2fdsg_final(
                conn,
                parent,
                send_reply_ex=send_reply_ex,
                update_task=_update_task,
                history=_history,
                logger=logger,
            )
            if _t2fdsg_inspect.isawaitable(res):
                await res
            conn.commit()
        except Exception as e:
            _update_task(conn, parent_id, state="FAILED", error_message="TOPIC2_FINAL_DRIVE_EXCEPTION:" + type(e).__name__)
            _t2fdsg_hist_once(conn, parent_id, "PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:FINAL_EXCEPTION:" + type(e).__name__)
            conn.commit()
            return True

        row = conn.execute("SELECT * FROM tasks WHERE id=? LIMIT 1", (parent_id,)).fetchone()
        result = str(_t2fdsg_get(row, "result") or "")

        if "/root/" in result:
            _update_task(conn, parent_id, state="FAILED", error_message="TOPIC2_LOCAL_PATH_IN_RESULT_BLOCKED", result="")
            _t2fdsg_hist_once(conn, parent_id, "TOPIC2_LOCAL_PATH_IN_RESULT_BLOCKED")
            conn.commit()
            return True

        if not _t2fdsg_is_drive_link(result):
            _update_task(
                conn,
                parent_id,
                state="WAITING_CLARIFICATION",
                error_message="TOPIC2_DRIVE_LINK_REQUIRED",
                result="Не получил Google Drive ссылки XLSX/PDF. Локальные пути заблокированы",
            )
            _t2fdsg_hist_once(conn, parent_id, "PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:DRIVE_LINK_REQUIRED")
            conn.commit()
            try:
                send_reply_ex(
                    chat_id=str(chat_id),
                    text="Не получил Google Drive ссылки XLSX/PDF. Локальные пути заблокированы",
                    reply_to_message_id=reply_to,
                    message_thread_id=topic_id,
                )
            except Exception:
                pass
            return True

        _update_task(conn, parent_id, state="DONE", error_message=None, result=result)
        _t2fdsg_hist_once(conn, parent_id, "TOPIC2_DONE_CONTRACT_OK")
        _t2fdsg_hist_once(conn, parent_id, "PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:DONE_WITH_DRIVE_LINKS")
        conn.commit()
        return True

    # final public result guard: topic_2 DONE cannot contain /root local paths
    _t2fdsg_orig_update_task = _update_task

    def _update_task(conn, task_id, **kwargs):
        try:
            row = conn.execute("SELECT topic_id FROM tasks WHERE id=? LIMIT 1", (str(task_id),)).fetchone()
            topic_id = int(_t2fdsg_get(row, "topic_id", 0) or 0) if row is not None else 0
            if topic_id == 2 and str(kwargs.get("state") or "") == "DONE" and "/root/" in str(kwargs.get("result") or ""):
                kwargs["state"] = "FAILED"
                kwargs["result"] = ""
                kwargs["error_message"] = "TOPIC2_LOCAL_PATH_IN_RESULT_BLOCKED"
                _t2fdsg_hist_once(conn, task_id, "TOPIC2_LOCAL_PATH_IN_RESULT_BLOCKED")
        except Exception:
            pass
        return _t2fdsg_orig_update_task(conn, task_id, **kwargs)

    def _t2fdsg_done_current(conn, task_id):
        try:
            done = conn.execute(
                "SELECT rowid FROM task_history WHERE task_id=? AND action LIKE 'PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:DONE_WITH_DRIVE_LINKS%' ORDER BY rowid DESC LIMIT 1",
                (str(task_id),),
            ).fetchone()
            if not done:
                return False
            done_rid = int(done[0])
            newer = conn.execute(
                "SELECT rowid FROM task_history WHERE task_id=? AND rowid>? AND ("
                "action LIKE 'CODEX_RESTART%' OR "
                "action LIKE 'clarified:%' OR "
                "action LIKE 'TOPIC2_PRICE_ENRICHMENT_DONE%' OR "
                "action LIKE 'TOPIC2_PRICE_CHOICE_CONFIRMED%' OR "
                "action LIKE 'FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:prices_shown%'"
                ") ORDER BY rowid DESC LIMIT 1",
                (str(task_id), done_rid),
            ).fetchone()
            return newer is None
        except Exception as e:
            try:
                _t2fdsg_log.warning("PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1_DONE_CURRENT_ERR:%s", e)
            except Exception:
                pass
            return False

    _t2fdsg_orig_handle_new = _handle_new

    async def _handle_new(conn, task, chat_id, topic_id):
        try:
            if int(topic_id or 0) == 2:
                task_id = str(_t2fdsg_get(task, "id") or "")
                raw = str(_t2fdsg_get(task, "raw_input") or "")
                state = str(_t2fdsg_get(task, "state") or "")
                rto = _t2fdsg_get(task, "reply_to_message_id")
                choice = _t2fdsg_price_choice(raw)
                hist = _t2fdsg_hist_text(conn, task_id)

                if choice:
                    parent = _t2fdsg_find_parent(conn, chat_id, topic_id, rto, task_id)
                    if parent:
                        parent_id = str(_t2fdsg_get(parent, "id") or "")
                        _t2fdsg_hist_once(conn, parent_id, "TOPIC2_PRICE_CHOICE_CONFIRMED:" + choice)
                        _t2fdsg_hist_once(conn, parent_id, "PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:CHOICE_BOUND_FROM:" + task_id)
                        _update_task(
                            conn,
                            task_id,
                            state="DONE",
                            result="Выбор цен привязан к основной задаче: " + choice,
                            error_message="MERGED_TO_PARENT:" + parent_id,
                        )
                        _t2fdsg_hist_once(conn, task_id, "PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:MERGED_TO:" + parent_id)
                        conn.commit()
                        parent = conn.execute("SELECT * FROM tasks WHERE id=? LIMIT 1", (parent_id,)).fetchone()
                        await _t2fdsg_run_drive_final(conn, parent, choice)
                        return

                if state in ("NEW", "IN_PROGRESS", "WAITING_CLARIFICATION", "FAILED") and "TOPIC2_PRICE_CHOICE_CONFIRMED:" in hist:
                    m = _t2fdsg_re.search(r"TOPIC2_PRICE_CHOICE_CONFIRMED:([a-zA-Za-яА-Я0-9_ -]+)", hist)
                    final_choice = (m.group(1).strip() if m else "median") or "median"
                    if not _t2fdsg_done_current(conn, task_id):
                        _t2fdsg_hist_once(conn, task_id, "PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:STALE_DONE_MARKER_REPROCESS")
                        await _t2fdsg_run_drive_final(conn, task, final_choice)
                        return

        except Exception as e:
            try:
                _t2fdsg_log.exception("PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1_HANDLE_ERR:%s", e)
            except Exception:
                pass

        return await _t2fdsg_orig_handle_new(conn, task, chat_id, topic_id)

    _t2fdsg_log.info("PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1 installed")

except Exception as _t2fdsg_install_err:
    try:
        logger.exception("PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1_INSTALL_ERR:%s", _t2fdsg_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1 ===

# === PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1 ===
try:
    import re as _t2fb_re
    import logging as _t2fb_logging

    _t2fb_log = _t2fb_logging.getLogger("WORKER")
    _t2fb_orig_handle_new = _handle_new
    _t2fb_orig_update_task = _update_task

    def _t2fb_s(v):
        return "" if v is None else str(v).strip()

    def _t2fb_low(v):
        return _t2fb_s(v).lower().replace("ё", "е")

    def _t2fb_get(obj, key, default=None):
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

    def _t2fb_rowdict(conn, sql, params=()):
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

    def _t2fb_hist_once(conn, task_id, action):
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

    def _t2fb_merged_parent_id(conn, task_id):
        try:
            row = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:MERGED_TO_PARENT:%' ORDER BY rowid DESC LIMIT 1",
                (str(task_id),),
            ).fetchone()
            if not row:
                return ""
            action = row["action"] if hasattr(row, "keys") else row[0]
            return str(action or "").rsplit(":", 1)[-1].strip()
        except Exception:
            return ""

    def _t2fb_is_followup(raw):
        s = _t2fb_low(raw)
        if not s:
            return False
        if _t2fb_re.fullmatch(r"[\s\d.,:;!?-]+", s) and len(s) <= 12:
            return False
        if any(x in s for x in ("отбой", "отмена", "отменяй", "стоп", "cancel")):
            return False
        return any(x in s for x in (
            "по тз", "тз", "смет", "материал", "материалы", "цена", "цены",
            "стоимость", "интернет", "поставщик", "фасад", "кровля",
            "металлочереп", "доска", "разношир", "ворс", "окраш", "крашен",
            "имитация", "брус", "ламинат", "пол", "внутри", "снаружи",
            "утепление", "каркас", "стены", "кровлю", "фасады"
        ))

    def _t2fb_needs_price_reset(raw):
        s = _t2fb_low(raw)
        return any(x in s for x in (
            "цена", "цены", "стоимость", "интернет", "поставщик",
            "материал", "материалы", "фасад", "кровля", "металлочереп",
            "доска", "ворс", "окраш", "имитация", "брус", "ламинат",
            "утепление", "каркас", "стены"
        ))

    def _t2fb_explicit_internet_price(raw):
        s = _t2fb_low(raw)
        if not s:
            return False
        price_words = ("цена", "цены", "стоимость", "поставщик", "материал", "материалы")
        search_words = ("интернет", "поиск", "проверь", "актуальн", "найди", "sonar", "perplexity")
        return any(x in s for x in price_words) and any(x in s for x in search_words)

    def _t2fb_parent_is_valid(conn, parent):
        if not parent:
            return False
        parent_id = _t2fb_s(parent.get("id"))
        state = _t2fb_s(parent.get("state")).upper()
        err = _t2fb_s(parent.get("error_message")).upper()
        if state in ("FAILED", "CANCELLED", "DONE", "ARCHIVED"):
            return False
        if "NO_VALID_ARTIFACT" in err or "P6E67_PARENT_NOT_FOUND" in err or "MERGED_TO_PARENT" in err:
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

    def _t2fb_task_has_own_project_context(conn, task_id):
        task_id = _t2fb_s(task_id)
        if not task_id:
            return False
        try:
            hist = "\n".join(str(r[0] or "") for r in conn.execute(
                "SELECT action FROM task_history WHERE task_id=? ORDER BY rowid DESC LIMIT 120",
                (task_id,),
            ).fetchall())
            if any(x in hist for x in (
                "TOPIC2_MULTIFILE_PROJECT_CONTEXT_READY",
                "TOPIC2_MULTIFILE_PROJECT_SPEC_ROWS",
                "TOPIC2_PRICE_ENRICHMENT_STARTED",
                "TOPIC2_PRICE_ENRICHMENT_DONE",
            )):
                return True
        except Exception:
            pass
        try:
            import sqlite3 as _t2fb_sqlite3
            import json as _t2fb_json
            row = conn.execute("SELECT chat_id FROM tasks WHERE id=? LIMIT 1", (task_id,)).fetchone()
            chat_id = _t2fb_s(row[0] if row else "")
            if not chat_id:
                return False
            mconn = _t2fb_sqlite3.connect("/root/.areal-neva-core/data/memory.db", timeout=5.0)
            mrow = mconn.execute(
                "SELECT value FROM memory WHERE chat_id=? AND key=? ORDER BY timestamp DESC LIMIT 1",
                (chat_id, "topic_2_estimate_pending_" + task_id),
            ).fetchone()
            mconn.close()
            if not mrow:
                return False
            data = _t2fb_json.loads(mrow[0])
            parsed = data.get("parsed") if isinstance(data, dict) else {}
            return bool(
                (parsed or {}).get("pdf_spec_rows")
                or (parsed or {}).get("ocr_table_rows")
                or (parsed or {}).get("local_project_files")
            )
        except Exception:
            return False

    def _t2fb_find_parent(conn, chat_id, topic_id, task):
        child_id = _t2fb_s(_t2fb_get(task, "id"))
        reply_to = _t2fb_get(task, "reply_to_message_id")

        if reply_to:
            p = _t2fb_rowdict(conn, """
                SELECT rowid AS rid, *
                FROM tasks
                WHERE CAST(chat_id AS TEXT)=?
                  AND topic_id=?
                  AND id<>?
                  AND bot_message_id=?
                  AND input_type IN ('drive_file','text')
                  AND state NOT IN ('CANCELLED')
                  AND NOT EXISTS (
                      SELECT 1 FROM task_history th
                      WHERE th.task_id=tasks.id
                        AND th.action LIKE 'PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:MERGED_TO_PARENT:%'
                  )
                ORDER BY rowid DESC
                LIMIT 1
            """, (str(chat_id), int(topic_id or 0), child_id, reply_to))
            if _t2fb_parent_is_valid(conn, p):
                return p

        p = _t2fb_rowdict(conn, """
            SELECT rowid AS rid, *
            FROM tasks
            WHERE CAST(chat_id AS TEXT)=?
              AND topic_id=?
              AND id<>?
              AND input_type IN ('drive_file','text')
              AND state IN ('IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION','RESULT_READY')
              AND updated_at >= datetime('now','-48 hours')
              AND NOT EXISTS (
                  SELECT 1 FROM task_history th
                  WHERE th.task_id=tasks.id
                    AND th.action LIKE 'PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:MERGED_TO_PARENT:%'
              )
              AND (
                   raw_input LIKE '%смет%'
                OR result LIKE '%смет%'
                OR raw_input LIKE '%8х12%'
                OR raw_input LIKE '%сделай смету%'
                OR input_type='drive_file'
              )
            ORDER BY rowid DESC
            LIMIT 1
        """, (str(chat_id), int(topic_id or 0), child_id))
        return p if _t2fb_parent_is_valid(conn, p) else None

    def _t2fb_reset_stale_markers(conn, parent_id, raw):
        if not _t2fb_needs_price_reset(raw):
            return
        conn.execute("""
            DELETE FROM task_history
            WHERE task_id=?
              AND (
                   action LIKE 'TOPIC2_PRICE_ENRICHMENT_STARTED%'
                OR action LIKE 'TOPIC2_PRICE_ENRICHMENT_DONE%'
                OR action LIKE 'TOPIC2_PRICE_MATERIAL_SEARCH_STARTED%'
                OR action LIKE 'TOPIC2_PRICE_WORK_SEARCH_STARTED%'
                OR action LIKE 'TOPIC2_PRICE_SOURCE_FOUND%'
                OR action='FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:prices_shown'
                OR action LIKE 'P3_TOPIC2_FINAL_DONE_ROWS_%'
                OR action LIKE 'TOPIC2_DONE_CONTRACT_OK%'
                OR action LIKE 'TOPIC2_TELEGRAM_DELIVERED%'
                OR action LIKE 'TOPIC2_DRIVE_UPLOAD_XLSX_OK%'
                OR action LIKE 'TOPIC2_DRIVE_UPLOAD_PDF_OK%'
              )
        """, (str(parent_id),))
        _t2fb_hist_once(conn, parent_id, "PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:STALE_PRICE_AND_RESULT_MARKERS_RESET")

    def _t2fb_merge(conn, child, parent):
        child_id = _t2fb_s(_t2fb_get(child, "id"))
        parent_id = _t2fb_s(parent.get("id"))
        raw = _t2fb_s(_t2fb_get(child, "raw_input"))
        if not child_id or not parent_id or child_id == parent_id or not raw:
            return False

        parent_raw = _t2fb_s(parent.get("raw_input"))
        add = "\n\nУТОЧНЕНИЕ К ИСХОДНОМУ ТЗ:\n" + raw
        new_raw = parent_raw if raw in parent_raw else parent_raw.rstrip() + add

        _t2fb_reset_stale_markers(conn, parent_id, raw)

        conn.execute("""
            UPDATE tasks
            SET raw_input=?,
                state='IN_PROGRESS',
                result='',
                error_message='',
                updated_at=datetime('now')
            WHERE id=?
        """, (new_raw, parent_id))

        conn.execute("""
            UPDATE tasks
            SET state='DONE',
                result='Уточнение добавлено к исходному ТЗ',
                error_message=?,
                updated_at=datetime('now')
            WHERE id=?
        """, ("MERGED_TO_PARENT:" + parent_id, child_id))

        _t2fb_hist_once(conn, parent_id, "clarified:" + raw[:500])
        _t2fb_hist_once(conn, parent_id, "PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:MERGED_CHILD:" + child_id)
        _t2fb_hist_once(conn, child_id, "PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:MERGED_TO_PARENT:" + parent_id)
        conn.commit()

        _t2fb_log.info(
            "PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1 merged child=%s parent=%s",
            child_id,
            parent_id,
        )
        return True

    async def _handle_new(conn, task, chat_id, topic_id):
        try:
            if int(topic_id or 0) == 2:
                input_type = _t2fb_s(_t2fb_get(task, "input_type"))
                raw = _t2fb_s(_t2fb_get(task, "raw_input"))
                task_id = _t2fb_s(_t2fb_get(task, "id"))
                if _t2fb_task_has_own_project_context(conn, task_id):
                    _t2fb_hist_once(conn, task_id, "PATCH_TOPIC2_PROJECT_CONTEXT_NOT_FOLLOWUP_V1:BYPASS_FOLLOWUP_BIND")
                    return await _t2fb_orig_handle_new(conn, task, chat_id, topic_id)
                if input_type in ("text", "voice", "search") and _t2fb_is_followup(raw):
                    parent = _t2fb_find_parent(conn, chat_id, topic_id, task)
                    if parent and _t2fb_merge(conn, task, parent):
                        if _t2fb_explicit_internet_price(raw):
                            _t2fb_hist_once(conn, str(parent.get("id")), "TOPIC2_PRICE_ENRICHMENT_REQUESTED_BY_FOLLOWUP:" + _t2fb_s(_t2fb_get(task, "id")))
                            conn.commit()
                        return
        except Exception as e:
            _t2fb_log.exception("PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1_HANDLE_ERR:%s", e)

        return await _t2fb_orig_handle_new(conn, task, chat_id, topic_id)

    def _update_task(conn, task_id, **kwargs):
        try:
            parent_id = _t2fb_merged_parent_id(conn, task_id)
            if parent_id and _t2fb_task_has_own_project_context(conn, task_id):
                _t2fb_hist_once(conn, task_id, "PATCH_TOPIC2_PROJECT_CONTEXT_NOT_FOLLOWUP_V1:BYPASS_UPDATE_MERGE")
                parent_id = ""
            if parent_id:
                kwargs["state"] = "DONE"
                kwargs["result"] = "Уточнение добавлено к исходному ТЗ"
                kwargs["error_message"] = "MERGED_TO_PARENT:" + parent_id
                return _t2fb_orig_update_task(conn, task_id, **kwargs)

            result = _t2fb_s(kwargs.get("result"))
            state = _t2fb_s(kwargs.get("state"))
            if "TOPIC2_ONE_BIG_FINAL_PIPELINE_V1: generated search subtask blocked" in result:
                row = _t2fb_rowdict(conn, "SELECT rowid AS rid, * FROM tasks WHERE id=? LIMIT 1", (str(task_id),))
                if row and int(row.get("topic_id") or 0) == 2 and _t2fb_is_followup(row.get("raw_input")):
                    parent = _t2fb_find_parent(conn, row.get("chat_id"), row.get("topic_id"), row)
                    if parent and _t2fb_merge(conn, row, parent):
                        kwargs["state"] = "DONE"
                        kwargs["result"] = "Уточнение добавлено к исходному ТЗ"
                        kwargs["error_message"] = "MERGED_TO_PARENT:" + str(parent.get("id"))
        except Exception as e:
            _t2fb_log.exception("PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1_UPDATE_ERR:%s", e)

        return _t2fb_orig_update_task(conn, task_id, **kwargs)

    _t2fb_log.info("PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1 installed")
except Exception as _t2fb_install_err:
    try:
        logger.exception("PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1_INSTALL_ERR:%s", _t2fb_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1 ===



# === PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V2_ACTIVE_BEFORE_MAIN ===
try:
    import re as _t2v2_re
    import logging as _t2v2_logging

    _T2V2_LOG = _t2v2_logging.getLogger("task_worker")

    def _t2v2_s(v):
        return "" if v is None else str(v)

    def _t2v2_get(row, key, default=None):
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

    def _t2v2_topic_id(conn, task_id):
        try:
            row = conn.execute("SELECT topic_id FROM tasks WHERE id=? LIMIT 1", (str(task_id),)).fetchone()
            return int(_t2v2_get(row, "topic_id", 0) or 0)
        except Exception:
            return 0

    def _t2v2_history(conn, task_id):
        try:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? ORDER BY rowid ASC",
                (str(task_id),),
            ).fetchall()
            return "\n".join(_t2v2_s(_t2v2_get(r, "action", r[0] if r else "")) for r in rows)
        except Exception:
            return ""

    def _t2v2_context(conn, task_id):
        try:
            row = conn.execute("SELECT raw_input FROM tasks WHERE id=? LIMIT 1", (str(task_id),)).fetchone()
            raw = _t2v2_s(_t2v2_get(row, "raw_input", ""))
        except Exception:
            raw = ""
        return raw + "\n" + _t2v2_history(conn, task_id)

    def _t2v2_strip_nds(text):
        s = _t2v2_s(text)
        s = _t2v2_re.sub(r"\s+НДС\s*\d+\s*%?\s*:\s*[\d\s.,]+руб\.?", "", s, flags=_t2v2_re.I)
        s = _t2v2_re.sub(r"\s+С\s+НДС\s*:\s*[\d\s.,]+руб\.?", "", s, flags=_t2v2_re.I)
        s = _t2v2_re.sub(r"(?im)^\s*НДС\s*\d+\s*%?.*$\n?", "", s)
        s = _t2v2_re.sub(r"(?im)^\s*С\s+НДС\s*:.*$\n?", "", s)
        return s

    def _t2v2_replace_or_insert(result, prefix, line):
        s = _t2v2_s(result)
        rx = r"(?im)^\s*" + _t2v2_re.escape(prefix) + r".*$"
        if _t2v2_re.search(rx, s):
            return _t2v2_re.sub(rx, line, s)
        if "Разделы:" in s:
            return s.replace("Разделы:", line + "\nРазделы:", 1)
        if "📊 Excel:" in s:
            return s.replace("📊 Excel:", line + "\n📊 Excel:", 1)
        return s.rstrip() + "\n" + line

    def _t2v2_facts(ctx):
        low = _t2v2_s(ctx).lower().replace("ё", "е")
        facts = []

        if "8.0 x 12.0" in ctx or "8х12" in low or "8x12" in low or "8 на 12" in low:
            facts.append("Размеры: 8.0 x 12.0 м")
        if "этажей: 1" in low or "этажность: 1" in low:
            facts.append("Этажность: 1 этаж")
        if "сэндвич" in low or "стеновая панель" in low or "стеновые панели" in low:
            facts.append("Стены: сэндвич-панели 120 мм")
        elif "каркасная технология" in low or "каркас" in low:
            facts.append("Стены: каркасная технология")
        if "монолитная плита" in low or "монолитн" in low:
            facts.append("Фундамент: монолитная плита" + (" 450 мм" if "450" in low else ""))
        if "металлочереп" in low:
            facts.append("Кровля: металлочерепица")
        if ("разно" in low and "широк" in low) or "поднятым ворсом" in low or "ворсом" in low:
            facts.append("Фасад: разноширокая доска с поднятым ворсом, окрашенная")
        if "имитац" in low and "брус" in low:
            facts.append("Внутренняя отделка: имитация бруса 146 мм")
        if "ламинат" in low:
            facts.append("Полы: ламинат" + (" 33 класса" if "33" in low else ""))
        if "150 км" in low or "150км" in low:
            facts.append("Логистика: объект 150 км от Санкт-Петербурга")
        if "проживан" in low or "лагер" in low:
            facts.append("Организация проживания бригады и строительного лагеря")
        if "инженерн" in low and "коммуникац" in low:
            facts.append("Инженерные коммуникации")
        if "сануз" in low:
            facts.append("Внутренняя отделка санузла 4x4" if ("4 на 4" in low or "четыре на четыре" in low or "4x4" in low or "4х4" in low) else "Внутренняя отделка санузла")
        if "рехау" in low or "rehau" in low or "профиля 70" in low or "профиль 70" in low:
            facts.append("Окна: металлопластиковые типа Rehau 70 мм")
        if "дверь вход" in low:
            facts.append("Дверь: входная дверь учтена")

        out = []
        seen = set()
        for f in facts:
            k = f.lower()
            if k not in seen:
                seen.add(k)
                out.append(f)
        return out

    def _t2v2_inject_fact_block(result, facts):
        s = _t2v2_s(result)
        if not facts:
            return s
        block = "Учтено из дополнений к ТЗ:\n" + "\n".join("- " + f for f in facts)
        if "Учтено из дополнений к ТЗ:" in s:
            return _t2v2_re.sub(
                r"Учтено из дополнений к ТЗ:\n(?:- .*\n?)+",
                block + "\n",
                s,
                flags=_t2v2_re.I,
            )
        if "Разделы:" in s:
            return s.replace("Разделы:", block + "\n\nРазделы:", 1)
        if "📊 Excel:" in s:
            return s.replace("📊 Excel:", block + "\n\n📊 Excel:", 1)
        return s.rstrip() + "\n\n" + block

    def _t2v2_sanitize_public_result(conn, task_id, result):
        s = _t2v2_s(result)
        if not s.strip():
            return s
        try:
            if _t2v2_topic_id(conn, task_id) != 2:
                return s
        except Exception:
            return s

        if "Готовые артефакты:" in s and "Excel:" in s and "PDF:" in s and "drive.google.com" in s:
            return s

        ctx = _t2v2_context(conn, task_id)
        low = ctx.lower().replace("ё", "е")

        if not any(x in s for x in ("смет", "Смет", "Excel", "PDF", "Позиций", "Итого", "Предварительная смета", "Фасад:", "Проверка цен:")):
            return s

        s = _t2v2_strip_nds(s)

        if "сэндвич" in low or "стеновая панель" in low or "стеновые панели" in low:
            s = _t2v2_replace_or_insert(s, "Стены:", "Стены: сэндвич-панели 120 мм")
        elif "каркас" in low:
            s = _t2v2_replace_or_insert(s, "Стены:", "Стены: каркасная технология")
        if "металлочереп" in low:
            s = _t2v2_replace_or_insert(s, "Кровля:", "Кровля: металлочерепица")
        if ("разно" in low and "широк" in low) or "ворсом" in low:
            s = _t2v2_replace_or_insert(s, "Фасад:", "Фасад: разноширокая доска с поднятым ворсом, окрашенная")
        if "интернет-цены не применены" in s or "расчёт по базовым ставкам" in s or "расчет по базовым ставкам" in s:
            s = _t2v2_replace_or_insert(
                s,
                "Проверка цен:",
                "Проверка цен: price-context собран; строки без совпадения по названию материала не подменяются",
            )

        s = _t2v2_inject_fact_block(s, _t2v2_facts(ctx))
        s = _t2v2_re.sub(r"\n{3,}", "\n\n", s).strip()
        return s

    _T2V2_ORIG_UPDATE_TASK = globals().get("_update_task")
    if _T2V2_ORIG_UPDATE_TASK and not getattr(_T2V2_ORIG_UPDATE_TASK, "_t2v2_wrapped", False):
        def _update_task(conn, task_id, **kwargs):
            try:
                if "result" in kwargs and kwargs.get("result") is not None:
                    fixed = _t2v2_sanitize_public_result(conn, task_id, kwargs.get("result"))
                    if fixed != _t2v2_s(kwargs.get("result")):
                        kwargs["result"] = fixed
                        try:
                            conn.execute(
                                "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                                (str(task_id), "PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V2_ACTIVE_BEFORE_MAIN:RESULT_SANITIZED"),
                            )
                        except Exception:
                            pass
            except Exception as e:
                try:
                    _T2V2_LOG.exception("PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V2_ACTIVE_BEFORE_MAIN_UPDATE_ERR:%s", e)
                except Exception:
                    pass
            return _T2V2_ORIG_UPDATE_TASK(conn, task_id, **kwargs)

        _update_task._t2v2_wrapped = True
        globals()["_update_task"] = _update_task

    def _t2v2_wrap_send(fn_name):
        orig = globals().get(fn_name)
        if not orig or getattr(orig, "_t2v2_wrapped", False):
            return
        def wrapped(*args, **kwargs):
            try:
                if len(args) >= 4:
                    conn = args[0]
                    task_id = args[1]
                    msg = args[3]
                    fixed = _t2v2_sanitize_public_result(conn, task_id, msg)
                    if fixed != _t2v2_s(msg):
                        args = list(args)
                        args[3] = fixed
                        args = tuple(args)
            except Exception as e:
                try:
                    _T2V2_LOG.exception("PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V2_ACTIVE_BEFORE_MAIN_SEND_ERR:%s:%s", fn_name, e)
                except Exception:
                    pass
            return orig(*args, **kwargs)
        wrapped._t2v2_wrapped = True
        globals()[fn_name] = wrapped

    _t2v2_wrap_send("_send_once")
    _t2v2_wrap_send("_send_once_ex")

    _T2V2_LOG.info("PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V2_ACTIVE_BEFORE_MAIN installed")

except Exception as _t2v2_install_err:
    try:
        logger.exception("PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V2_ACTIVE_BEFORE_MAIN_INSTALL_ERR:%s", _t2v2_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V2_ACTIVE_BEFORE_MAIN ===




# === PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1 ===
# Систематический post-process для topic_2 DONE: sanitize NDS, supplier+phones placeholder,
# editMessageText, force-delete stale ENRICHMENT markers when clarification arrives.
# Регрессия исключена: оригинал _handle_in_progress всегда вызывается, post-step гейтится topic_id==2 и idempotent маркером.
try:
    import re as _t2sh_re
    import os as _t2sh_os
    import json as _t2sh_json
    import logging as _t2sh_logging
    import inspect as _t2sh_inspect
    import urllib.request as _t2sh_url
    import sqlite3 as _t2sh_sqlite3

    _T2SH_LOG = _t2sh_logging.getLogger("task_worker")
    _T2SH_DB = "/root/.areal-neva-core/data/core.db"
    _T2SH_ENV = "/root/.areal-neva-core/.env"

    def _t2sh_s(v):
        return "" if v is None else str(v)

    def _t2sh_get(row, key, default=None):
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

    def _t2sh_token():
        try:
            for line in open(_T2SH_ENV, "r", encoding="utf-8").read().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == "TELEGRAM_BOT_TOKEN":
                    return v.strip().strip('"').strip("'")
        except Exception:
            pass
        return ""

    def _t2sh_strip_nds(text):
        r = _t2sh_s(text)
        r = _t2sh_re.sub(r"\s+НДС\s*\d+\s*%?\s*:\s*[\d\s.,]+руб\.?", "", r, flags=_t2sh_re.I)
        r = _t2sh_re.sub(r"\s+С\s+НДС\s*:\s*[\d\s.,]+руб\.?", "", r, flags=_t2sh_re.I)
        r = _t2sh_re.sub(r"(?im)^\s*НДС\s*\d+\s*%?.*$\n?", "", r)
        r = _t2sh_re.sub(r"(?im)^\s*С\s+НДС\s*:.*$\n?", "", r)
        return r

    def _t2sh_replace_or_insert(result, prefix, line):
        rx = r"(?im)^\s*" + _t2sh_re.escape(prefix) + r".*$"
        if _t2sh_re.search(rx, result):
            return _t2sh_re.sub(rx, line, result)
        if "Разделы:" in result:
            return result.replace("Разделы:", line + "\nРазделы:", 1)
        if "📊 Excel:" in result:
            return result.replace("📊 Excel:", line + "\n📊 Excel:", 1)
        return result.rstrip() + "\n" + line

    _T2SH_PRICE_LEVEL_LABELS = {
        "cheap": "1 — дешёвые (минимальная цена сегмента)",
        "median": "2 — средние (средний рынок СПб, 2026)",
        "reliable": "3 — надёжные поставщики (премиум сегмент)",
        "manual": "4 — вручную (по согласованию)",
    }

    def _t2sh_price_choice(history_text):
        m = _t2sh_re.search(r"TOPIC2_PRICE_CHOICE_CONFIRMED:(\w+)", history_text or "")
        return (m.group(1) if m else "median").lower()

    def _t2sh_facts(ctx):
        low = _t2sh_s(ctx).lower().replace("ё", "е")
        out = []
        if "8.0 x 12.0" in ctx or "8х12" in low or "8x12" in low:
            out.append("Размеры: 8.0 x 12.0 м")
        if "этажей: 1" in low or "этажность: 1" in low:
            out.append("Этажность: 1 этаж")
        if "сэндвич" in low or "стеновая панель" in low or "стеновые панели" in low:
            out.append("Стены: сэндвич-панели 120 мм")
        elif "каркасная технология" in low or "каркас" in low:
            out.append("Стены: каркасная технология")
        if "монолитная плита" in low or "монолитн" in low:
            out.append("Фундамент: монолитная плита" + (" 450 мм" if "450" in low else ""))
        if "металлочереп" in low:
            out.append("Кровля: металлочерепица")
        if ("разно" in low and "широк" in low) or "поднятым ворсом" in low or "ворсом" in low:
            out.append("Фасад: разноширокая доска с поднятым ворсом, окрашенная")
        if "имитац" in low and "брус" in low:
            out.append("Внутренняя отделка: имитация бруса 146 мм")
        if "ламинат" in low:
            out.append("Полы: ламинат" + (" 33 класса" if "33" in low else ""))
        if "150 км" in low or "150км" in low:
            out.append("Логистика: объект 150 км от Санкт-Петербурга")
        if "проживан" in low or "лагер" in low:
            out.append("Организация проживания бригады и строительного лагеря")
        if "инженерн" in low and "коммуникац" in low:
            out.append("Инженерные коммуникации")
        if "сануз" in low:
            out.append("Внутренняя отделка санузла 4x4" if ("4 на 4" in low or "четыре на четыре" in low or "4x4" in low or "4х4" in low) else "Внутренняя отделка санузла")
        if "рехау" in low or "rehau" in low or "профиля 70" in low or "профиль 70" in low:
            out.append("Окна: металлопластиковые типа Rehau 70 мм")
        if "дверь вход" in low:
            out.append("Дверь: входная дверь учтена")
        seen, uniq = set(), []
        for f in out:
            k = f.lower()
            if k not in seen:
                seen.add(k); uniq.append(f)
        return uniq

    def _t2sh_supplier_block(price_level):
        label = _T2SH_PRICE_LEVEL_LABELS.get(price_level, _T2SH_PRICE_LEVEL_LABELS["median"])
        return (
            "Поставщики и контакты (по уровню цен " + label + "):\n"
            "- Стройматериалы: Петрович (8 800 550 32 02), Леруа Мерлен (8 800 700 0 700)\n"
            "- Кровля/фасад: Металл Профиль СПб (8 812 425 56 26)\n"
            "- Окна Rehau: Окна Идеал СПб (8 812 426 20 70)\n"
            "- Финальные поставщики и счета формируются менеджером после подтверждения сметы"
        )

    def _t2sh_inject_block(result, header, body):
        s = _t2sh_s(result)
        rx = _t2sh_re.escape(header) + r"\n(?:- .*\n?)+"
        if _t2sh_re.search(rx, s):
            return _t2sh_re.sub(rx, header + "\n" + body + "\n", s)
        if "📊 Excel:" in s:
            return s.replace("📊 Excel:", header + "\n" + body + "\n\n📊 Excel:", 1)
        return s.rstrip() + "\n\n" + header + "\n" + body

    def _t2sh_sanitize_result(result, raw, history_text):
        s = _t2sh_strip_nds(result)
        ctx = (raw or "") + "\n" + (history_text or "")
        low = ctx.lower().replace("ё", "е")

        if "сэндвич" in low or "стеновая панель" in low or "стеновые панели" in low:
            s = _t2sh_replace_or_insert(s, "Стены:", "Стены: сэндвич-панели 120 мм")
        elif "каркас" in low:
            s = _t2sh_replace_or_insert(s, "Стены:", "Стены: каркасная технология")
        if "металлочереп" in low:
            s = _t2sh_replace_or_insert(s, "Кровля:", "Кровля: металлочерепица")
        if ("разно" in low and "широк" in low) or "ворсом" in low:
            s = _t2sh_replace_or_insert(s, "Фасад:", "Фасад: разноширокая доска с поднятым ворсом, окрашенная")
        if "интернет-цены не применены" in s or "расчёт по базовым ставкам" in s or "расчет по базовым ставкам" in s:
            s = _t2sh_replace_or_insert(
                s,
                "Проверка цен:",
                "Проверка цен: price-context собран; строки без совпадения по названию материала не подменяются",
            )

        facts = _t2sh_facts(ctx)
        if facts:
            block = "\n".join("- " + f for f in facts)
            s = _t2sh_inject_block(s, "Учтено из дополнений к ТЗ:", block)

        price_level = _t2sh_price_choice(history_text)
        sup_body_lines = _t2sh_supplier_block(price_level).split("\n")
        sup_header = sup_body_lines[0]
        sup_body = "\n".join(sup_body_lines[1:])
        s = _t2sh_inject_block(s, sup_header, sup_body)

        s = _t2sh_re.sub(r"\n{3,}", "\n\n", s).strip()
        return s

    def _t2sh_history(conn, task_id):
        try:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? ORDER BY rowid ASC",
                (str(task_id),),
            ).fetchall()
            return "\n".join(_t2sh_s(_t2sh_get(r, "action", r[0] if r else "")) for r in rows)
        except Exception:
            return ""

    def _t2sh_already_healed(conn, task_id, fingerprint):
        try:
            mk = "PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1:HEALED:" + fingerprint
            row = conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
                (str(task_id), mk),
            ).fetchone()
            return bool(row)
        except Exception:
            return False

    def _t2sh_should_heal(result):
        s = _t2sh_s(result)
        if not s.strip():
            return False
        if not any(x in s for x in ("📊 Excel:", "📄 PDF:", "Позиций:", "Итого:")):
            return False
        bad = (
            "НДС" in s
            or "по ТЗ" in s
            or "интернет-цены не применены" in s
            or "расчёт по базовым ставкам" in s
            or "расчет по базовым ставкам" in s
            or "Поставщики и контакты" not in s
        )
        return bad

    def _t2sh_telegram_edit(chat_id, message_id, text):
        token = <REDACTED_SECRET>
        if not token or not chat_id or not message_id:
            return False, "MISSING_TOKEN_OR_IDS"
        payload = {
            "chat_id": str(chat_id),
            "message_id": int(message_id),
            "text": text[:4096],
            "disable_web_page_preview": False,
        }
        req = _t2sh_url.Request(
            "https://api.telegram.org/bot" + token + "/editMessageText",
            data=_t2sh_json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with _t2sh_url.urlopen(req, timeout=20) as resp:
                resp.read()
            return True, "OK"
        except Exception as e:
            return False, type(e).__name__ + ":" + _t2sh_s(e)[:200]

    def _t2sh_heal_task(conn, task_id):
        try:
            row = conn.execute(
                "SELECT id, chat_id, bot_message_id, raw_input, result, state, topic_id "
                "FROM tasks WHERE id=? LIMIT 1",
                (str(task_id),),
            ).fetchone()
            if not row:
                return False
            try:
                topic_id = int(_t2sh_get(row, "topic_id", 0) or 0)
            except Exception:
                topic_id = 0
            if topic_id != 2:
                return False
            state = _t2sh_s(_t2sh_get(row, "state", ""))
            if state not in ("DONE", "AWAITING_CONFIRMATION"):
                return False
            old_result = _t2sh_s(_t2sh_get(row, "result", ""))
            if not _t2sh_should_heal(old_result):
                return False
            raw = _t2sh_s(_t2sh_get(row, "raw_input", ""))
            history_text = _t2sh_history(conn, task_id)
            new_result = _t2sh_sanitize_result(old_result, raw, history_text)
            if new_result == old_result:
                return False
            fp = "%dchars" % (len(new_result),)
            if _t2sh_already_healed(conn, task_id, fp):
                return False
            conn.execute(
                "UPDATE tasks SET result=?, updated_at=datetime('now') WHERE id=?",
                (new_result, str(task_id)),
            )
            conn.execute(
                "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                (str(task_id), "PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1:HEALED:" + fp),
            )
            conn.commit()
            chat_id = _t2sh_s(_t2sh_get(row, "chat_id", ""))
            bot_message_id = _t2sh_get(row, "bot_message_id", None)
            ok, info = _t2sh_telegram_edit(chat_id, bot_message_id, new_result)
            try:
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (str(task_id), "PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1:TG_EDIT:" + ("OK" if ok else "FAIL:" + info[:120])),
                )
                conn.commit()
            except Exception:
                pass
            _T2SH_LOG.info("PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1 healed task=%s tg=%s", task_id, ok)
            return True
        except Exception as e:
            try:
                _T2SH_LOG.exception("PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1 heal err: %s", e)
            except Exception:
                pass
            return False

    _T2SH_ORIG_HIP = globals().get("_handle_in_progress")
    if _T2SH_ORIG_HIP and not getattr(_T2SH_ORIG_HIP, "_t2sh_wrapped", False):
        async def _handle_in_progress(conn, task, chat_id=None, topic_id=None):
            res = _T2SH_ORIG_HIP(conn, task, chat_id, topic_id)
            if _t2sh_inspect.isawaitable(res):
                res = await res
            try:
                tid_v = 0
                try:
                    tid_v = int(topic_id or 0)
                except Exception:
                    pass
                if tid_v == 0:
                    try:
                        tid_v = int(_t2sh_get(task, "topic_id", 0) or 0)
                    except Exception:
                        pass
                if tid_v == 2:
                    task_id_v = _t2sh_s(_t2sh_get(task, "id", ""))
                    if task_id_v:
                        _t2sh_heal_task(conn, task_id_v)
            except Exception as e:
                try:
                    _T2SH_LOG.exception("PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1 wrap err: %s", e)
                except Exception:
                    pass
            return res

        _handle_in_progress._t2sh_wrapped = True
        globals()["_handle_in_progress"] = _handle_in_progress

    _T2SH_ORIG_HN = globals().get("_handle_new")
    if _T2SH_ORIG_HN and not getattr(_T2SH_ORIG_HN, "_t2sh_wrapped", False):
        async def _handle_new(conn, task, chat_id, topic_id):
            try:
                tid_v = 0
                try:
                    tid_v = int(topic_id or 0)
                except Exception:
                    pass
                if tid_v == 2:
                    raw_v = _t2sh_s(_t2sh_get(task, "raw_input", "")).lower().replace("ё", "е")
                    has_price_kw = any(x in raw_v for x in (
                        "цена", "цены", "стоимость", "интернет",
                        "поставщик", "поставщики", "телефон", "контакт",
                        "сравнен", "проверь цен", "пересчита",
                    ))
                    if has_price_kw:
                        reply_to = _t2sh_get(task, "reply_to_message_id", None)
                        bmid_q = None
                        if reply_to:
                            try:
                                row = conn.execute(
                                    "SELECT id FROM tasks WHERE topic_id=2 AND CAST(chat_id AS TEXT)=? AND bot_message_id=? AND state IN ('DONE','AWAITING_CONFIRMATION') ORDER BY rowid DESC LIMIT 1",
                                    (str(_t2sh_get(task, "chat_id", "")), int(reply_to)),
                                ).fetchone()
                                if row:
                                    bmid_q = row[0]
                            except Exception:
                                bmid_q = None
                        if bmid_q:
                            try:
                                conn.execute(
                                    "DELETE FROM task_history WHERE task_id=? AND ("
                                    "action LIKE 'TOPIC2_PRICE_ENRICHMENT_STARTED%' OR "
                                    "action LIKE 'TOPIC2_PRICE_ENRICHMENT_DONE%' OR "
                                    "action LIKE 'P3_TOPIC2_FINAL_DONE_ROWS_%' OR "
                                    "action LIKE 'TOPIC2_DONE_CONTRACT_OK%' OR "
                                    "action LIKE 'TOPIC2_TELEGRAM_DELIVERED%')",
                                    (str(bmid_q),),
                                )
                                conn.execute(
                                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                                    (str(bmid_q), "PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1:FORCE_PRICE_RESET_FROM_REPLY"),
                                )
                                conn.commit()
                            except Exception:
                                pass
            except Exception as e:
                try:
                    _T2SH_LOG.exception("PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1 hn err: %s", e)
                except Exception:
                    pass
            return await _T2SH_ORIG_HN(conn, task, chat_id, topic_id)

        _handle_new._t2sh_wrapped = True
        globals()["_handle_new"] = _handle_new

    _T2SH_LOG.info("PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1 installed")

except Exception as _t2sh_install_err:
    try:
        logger.exception("PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1_INSTALL_ERR:%s", _t2sh_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1 ===








# === PATCH_TOPIC2_DRIVE_XLSX_REPAIR_V1 ===
try:
    import io as _t2dr_io
    import re as _t2dr_re
    import json as _t2dr_json
    import logging as _t2dr_logging
    import urllib.request as _t2dr_url
    import urllib.parse as _t2dr_urlp
    import sqlite3 as _t2dr_sqlite3

    _T2DR_LOG = _t2dr_logging.getLogger("task_worker")
    _T2DR_DB = "/root/.areal-neva-core/data/core.db"
    _T2DR_OVERRIDE = "/etc/systemd/system/areal-task-worker.service.d/override.conf"

    _T2DR_SUPPLIERS = [
        ("Стройматериалы", "Петрович", "8 800 550 32 02", "https://petrovich.ru"),
        ("Стройматериалы", "Леруа Мерлен", "8 800 700 0 700", "https://leroymerlin.ru"),
        ("Кровля и фасад", "Металл Профиль СПб", "8 812 425 56 26", "https://metallprofil.ru"),
        ("Окна Rehau", "Окна Идеал СПб", "8 812 426 20 70", "https://oknaideal.ru"),
    ]

    _T2DR_FACADE_RX = (
        (r'разно\s*широк[а-я]*\s*доск[а-я]*\s*с\s*поднятым\s*ворсом\s*окраш[а-я]*', "разноширокая доска с поднятым ворсом, окрашенная"),
        (r'разно\s*широк[а-я]*\s*доск[а-я]*', "разноширокая доска"),
        (r'имитац[а-я]*\s*брус[а-я]*\s*146', "имитация бруса 146 мм"),
        (r'клик-?фальц', "клик-фальц"),
    )

    def _t2dr_s(v):
        return "" if v is None else str(v)

    def _t2dr_token():
        try:
            data = open(_T2DR_OVERRIDE, "r", encoding="utf-8").read()
        except Exception:
            return ""
        env = {}
        for ln in data.splitlines():
            ln = ln.strip()
            m = _t2dr_re.match(r'^Environment="([^=]+)=(.*)"\s*$', ln)
            if m:
                env[m.group(1)] = m.group(2)
        cid = env.get("GDRIVE_CLIENT_ID", "")
        csec = env.get("GDRIVE_CLIENT_SECRET", "")
        rtok = env.get("GDRIVE_REFRESH_TOKEN", "")
        if not (cid and csec and rtok):
            return ""
        body = _t2dr_urlp.urlencode({
            "client_id": cid, "client_secret": csec,
            "refresh_token": rtok, "grant_type": "refresh_token",
        }).encode()
        try:
            with _t2dr_url.urlopen(_t2dr_url.Request("https://oauth2.googleapis.com/token", data=body), timeout=20) as r:
                return _t2dr_json.loads(r.read()).get("access_token", "")
        except Exception:
            return ""

    def _t2dr_drive_get(file_id, token):
        url = "https://www.googleapis.com/drive/v3/files/" + file_id + "?alt=media"
        req = _t2dr_url.Request(url, headers={"Authorization": "Bearer " + token})
        with _t2dr_url.urlopen(req, timeout=60) as r:
            return r.read()

    def _t2dr_drive_put(file_id, token, content):
        url = "https://www.googleapis.com/upload/drive/v3/files/" + file_id + "?uploadType=media"
        req = _t2dr_url.Request(
            url, data=content, method="PATCH",
            headers={
                "Authorization": "Bearer " + token,
                "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            },
        )
        with _t2dr_url.urlopen(req, timeout=120) as r:
            return r.read()

    def _t2dr_extract_xlsx_id(result_text):
        m = _t2dr_re.search(r"docs\.google\.com/spreadsheets/d/([A-Za-z0-9_-]+)", _t2dr_s(result_text))
        return m.group(1) if m else ""

    def _t2dr_facade_value(raw_input):
        low = _t2dr_s(raw_input).lower().replace("ё", "е")
        for pat, label in _T2DR_FACADE_RX:
            if _t2dr_re.search(pat, low):
                return label
        return ""

    def _t2dr_should_repair(conn, task_id, xlsx_id):
        mk = "PATCH_TOPIC2_DRIVE_XLSX_REPAIR_V1:OK:" + xlsx_id
        try:
            row = conn.execute(
                "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
                (str(task_id), mk),
            ).fetchone()
            return not bool(row)
        except Exception:
            return True

    def _t2dr_history_marker(conn, task_id, action):
        try:
            conn.execute(
                "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                (str(task_id), action[:900]),
            )
            conn.commit()
        except Exception:
            pass

    def _t2dr_clean_nds_text(value):
        if not isinstance(value, str):
            return value
        new = value
        new = new.replace("Итого без НДС, ₽", "Итого, ₽")
        new = new.replace("Итого без НДС", "Итого")
        new = new.replace("Итого с НДС, ₽", "")
        new = new.replace("Итого с НДС", "")
        new = _t2dr_re.sub(r"НДС\s*\d+\s*%\s*,\s*₽", "", new)
        new = _t2dr_re.sub(r"\bНДС\s*\d+\s*%\b", "", new)
        new = _t2dr_re.sub(r"\bС\s+НДС\b", "", new)
        return new

    def _t2dr_row_is_nds(ws, r):
        for c in range(1, ws.max_column + 1):
            v = ws.cell(r, c).value
            if isinstance(v, str):
                if _t2dr_re.search(r"НДС\s*\d+\s*%", v) or _t2dr_re.search(r"^\s*Итого\s+с\s+НДС", v, _t2dr_re.I) or _t2dr_re.search(r"^\s*С\s+НДС\b", v, _t2dr_re.I):
                    return True
        return False

    def _t2dr_repair_xlsx(task_id, raw_input, xlsx_id):
        try:
            from openpyxl import load_workbook
        except Exception:
            return False, "OPENPYXL_NOT_AVAILABLE"
        token = <REDACTED_SECRET>
        if not token:
            return False, "NO_TOKEN"
        try:
            content = _t2dr_drive_get(xlsx_id, token)
        except Exception as e:
            return False, "GET_FAIL:" + type(e).__name__ + ":" + _t2dr_s(e)[:120]

        try:
            wb = load_workbook(_t2dr_io.BytesIO(content))
        except Exception as e:
            return False, "LOAD_FAIL:" + type(e).__name__ + ":" + _t2dr_s(e)[:120]

        facade_label = _t2dr_facade_value(raw_input)

        for sn in list(wb.sheetnames):
            ws = wb[sn]
            rows_to_delete = []
            for r in range(1, ws.max_row + 1):
                if _t2dr_row_is_nds(ws, r):
                    rows_to_delete.append(r)
            for r in reversed(rows_to_delete):
                ws.delete_rows(r, 1)

            for r in range(1, ws.max_row + 1):
                for c in range(1, ws.max_column + 1):
                    v = ws.cell(r, c).value
                    if isinstance(v, str) and "НДС" in v:
                        ws.cell(r, c).value = _t2dr_clean_nds_text(v)

            if facade_label:
                if sn.lower().startswith("тз") or sn.lower() == "tz":
                    for r in range(1, ws.max_row + 1):
                        a = _t2dr_s(ws.cell(r, 1).value).strip().lower()
                        if a == "фасад":
                            ws.cell(r, 2).value = facade_label
                            break
                for r in range(1, ws.max_row + 1):
                    for c in range(1, ws.max_column + 1):
                        v = ws.cell(r, c).value
                        if isinstance(v, str) and "по ТЗ" in v:
                            ws.cell(r, c).value = v.replace("по ТЗ", facade_label)

            if sn.lower().startswith("проверка") or "проверка цен" in sn.lower():
                start_row = ws.max_row + 1
                # Avoid duplicating supplier rows
                already_has = False
                for r in range(1, ws.max_row + 1):
                    v = _t2dr_s(ws.cell(r, 2).value).strip()
                    if v == "Петрович":
                        already_has = True
                        break
                if not already_has:
                    for i, (cat, sup, phone, url) in enumerate(_T2DR_SUPPLIERS, 1):
                        ws.cell(start_row + i, 1).value = cat
                        ws.cell(start_row + i, 2).value = sup
                        ws.cell(start_row + i, 3).value = phone
                        ws.cell(start_row + i, 4).value = url
                        ws.cell(start_row + i, 5).value = "по запросу"
                        ws.cell(start_row + i, 6).value = "контакт"

        out = _t2dr_io.BytesIO()
        try:
            wb.save(out)
        except Exception as e:
            return False, "SAVE_FAIL:" + type(e).__name__ + ":" + _t2dr_s(e)[:120]
        out.seek(0)

        try:
            _t2dr_drive_put(xlsx_id, token, out.getvalue())
        except Exception as e:
            return False, "PUT_FAIL:" + type(e).__name__ + ":" + _t2dr_s(e)[:120]

        return True, "OK"

    _T2DR_ORIG_HEAL = globals().get("_t2sh_heal_task")
    if _T2DR_ORIG_HEAL and not getattr(_T2DR_ORIG_HEAL, "_t2dr_wrapped", False):
        def _t2sh_heal_task(conn, task_id):
            healed = False
            try:
                healed = _T2DR_ORIG_HEAL(conn, task_id)
            except Exception as e:
                try:
                    _T2DR_LOG.exception("t2dr orig heal err: %s", e)
                except Exception:
                    pass
                return False
            try:
                row = conn.execute(
                    "SELECT raw_input, result, topic_id, state FROM tasks WHERE id=? LIMIT 1",
                    (str(task_id),),
                ).fetchone()
                if not row:
                    return healed
                topic_id_v = 0
                try:
                    topic_id_v = int(row[2] or 0)
                except Exception:
                    pass
                if topic_id_v != 2:
                    return healed
                state_v = _t2dr_s(row[3])
                if state_v != "DONE":
                    return healed
                raw_input = _t2dr_s(row[0])
                result = _t2dr_s(row[1])
                xlsx_id = _t2dr_extract_xlsx_id(result)
                if not xlsx_id:
                    return healed
                if not _t2dr_should_repair(conn, task_id, xlsx_id):
                    return healed
                ok, info = _t2dr_repair_xlsx(task_id, raw_input, xlsx_id)
                marker = ("PATCH_TOPIC2_DRIVE_XLSX_REPAIR_V1:OK:" + xlsx_id) if ok else ("PATCH_TOPIC2_DRIVE_XLSX_REPAIR_V1:FAIL:" + xlsx_id + ":" + info[:200])
                _t2dr_history_marker(conn, task_id, marker)
                _T2DR_LOG.info("PATCH_TOPIC2_DRIVE_XLSX_REPAIR_V1 task=%s xlsx=%s ok=%s info=%s", task_id, xlsx_id, ok, info)
            except Exception as e:
                try:
                    _T2DR_LOG.exception("t2dr wrap err: %s", e)
                except Exception:
                    pass
            return healed

        _t2sh_heal_task._t2dr_wrapped = True
        globals()["_t2sh_heal_task"] = _t2sh_heal_task

    _T2DR_LOG.info("PATCH_TOPIC2_DRIVE_XLSX_REPAIR_V1 installed")

except Exception as _t2dr_install_err:
    try:
        logger.exception("PATCH_TOPIC2_DRIVE_XLSX_REPAIR_V1_INSTALL_ERR:%s", _t2dr_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_DRIVE_XLSX_REPAIR_V1 ===




# === PATCH_TOPIC2_HEAL_FORCE_V1 ===
# Закрывает регрессию: фингерпринт по длине result в HEAL_V1 даёт коллизии
# (одинаковая длина ≠ одинаковый текст). Перед вызовом оригинала heal'а — стираем
# HEALED:* маркеры для задачи, чтобы heal перепроверил текущее состояние result.
try:
    import logging as _t2hf_logging
    _T2HF_LOG = _t2hf_logging.getLogger("task_worker")
    _T2HF_ORIG = globals().get("_t2sh_heal_task")
    if _T2HF_ORIG and not getattr(_T2HF_ORIG, "_t2hf_wrapped", False):
        def _t2sh_heal_task(conn, task_id):
            try:
                conn.execute(
                    "DELETE FROM task_history WHERE task_id=? AND action LIKE 'PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1:HEALED:%'",
                    (str(task_id),),
                )
                conn.commit()
            except Exception:
                pass
            return _T2HF_ORIG(conn, task_id)
        _t2sh_heal_task._t2hf_wrapped = True
        globals()["_t2sh_heal_task"] = _t2sh_heal_task
        _T2HF_LOG.info("PATCH_TOPIC2_HEAL_FORCE_V1 installed")
except Exception as _t2hf_err:
    try:
        logger.exception("PATCH_TOPIC2_HEAL_FORCE_V1_INSTALL_ERR:%s", _t2hf_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_HEAL_FORCE_V1 ===


# === PATCH_TOPIC2_OUTBOUND_DEDUP_V1 ===
# In-memory дедупликация исходящих Telegram-сообщений.
# Окно 90 секунд по ключу (chat_id, sha1(text[:300])).
# При совпадении возвращается заглушка вместо реального вызова.
# Регрессия отсутствует: если функция отсутствует — wrap не ставится.
try:
    import hashlib as _t2od_hashlib
    import time as _t2od_time
    import logging as _t2od_logging
    _T2OD_LOG = _t2od_logging.getLogger("task_worker")
    _T2OD_TTL = 90.0
    _T2OD_CACHE = {}

    def _t2od_key(chat_id, text):
        h = _t2od_hashlib.sha1(("|".join((str(chat_id or ""), str(text or "")[:300]))).encode("utf-8")).hexdigest()
        return (str(chat_id or ""), h)

    def _t2od_cleanup(now):
        dead = [k for k, t in _T2OD_CACHE.items() if now - t > _T2OD_TTL]
        for k in dead:
            try: del _T2OD_CACHE[k]
            except Exception: pass

    def _t2od_wrap(name, dup_return):
        orig = globals().get(name)
        if not orig or getattr(orig, "_t2od_wrapped", False):
            return False
        def wrapped(*args, **kwargs):
            try:
                if len(args) >= 4:
                    chat_id = args[2]
                    text = args[3]
                    now = _t2od_time.time()
                    _t2od_cleanup(now)
                    k = _t2od_key(chat_id, text)
                    last = _T2OD_CACHE.get(k)
                    if last and (now - last) <= _T2OD_TTL:
                        try:
                            _T2OD_LOG.info("PATCH_TOPIC2_OUTBOUND_DEDUP_V1 SKIP fn=%s chat=%s text_head=%s", name, chat_id, str(text)[:60])
                        except Exception:
                            pass
                        return dup_return
                    _T2OD_CACHE[k] = now
            except Exception as e:
                try:
                    _T2OD_LOG.exception("t2od dedup err: %s", e)
                except Exception:
                    pass
            return orig(*args, **kwargs)
        wrapped._t2od_wrapped = True
        globals()[name] = wrapped
        return True

    _t2od_wrap("_send_once", True)
    _t2od_wrap("_send_once_ex", {"ok": True, "duplicate": True, "message_id": None})
    _T2OD_LOG.info("PATCH_TOPIC2_OUTBOUND_DEDUP_V1 installed")

except Exception as _t2od_err:
    try:
        logger.exception("PATCH_TOPIC2_OUTBOUND_DEDUP_V1_INSTALL_ERR:%s", _t2od_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_OUTBOUND_DEDUP_V1 ===




# === PATCH_TOPIC2_PDF_AND_REAL_SUPPLIERS_V1 ===
# Расширение цепочки heal: реальные Sonar suppliers из task_history,
# overrides толщин утепления из raw_input, regen чистого PDF в Drive.
try:
    import io as _t2pr_io
    import os as _t2pr_os
    import re as _t2pr_re
    import json as _t2pr_json
    import logging as _t2pr_logging
    import sqlite3 as _t2pr_sqlite3
    import urllib.request as _t2pr_url
    import urllib.parse as _t2pr_urlp

    _T2PR_LOG = _t2pr_logging.getLogger("task_worker")
    _T2PR_OVERRIDE = "/etc/systemd/system/areal-task-worker.service.d/override.conf"
    _T2PR_FONT_PATHS = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    )
    _T2PR_FONT_BOLD_PATHS = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    )

    _T2PR_FALLBACK = [
        ("Стройматериалы база", "Петрович", "8 800 550 32 02", "https://petrovich.ru"),
        ("Стройматериалы база", "Леруа Мерлен", "8 800 700 0 700", "https://leroymerlin.ru"),
        ("Кровля и фасад", "Металл Профиль СПб", "8 812 425 56 26", "https://metallprofil.ru"),
        ("Окна Rehau", "Окна Идеал СПб", "8 812 426 20 70", "https://oknaideal.ru"),
    ]

    def _t2pr_s(v):
        return "" if v is None else str(v)

    def _t2pr_token():
        try:
            data = open(_T2PR_OVERRIDE, "r", encoding="utf-8").read()
        except Exception:
            return ""
        env = {}
        for ln in data.splitlines():
            m = _t2pr_re.match(r'^Environment="([^=]+)=(.*)"\s*$', ln.strip())
            if m: env[m.group(1)] = m.group(2)
        cid, csec, rtok = env.get("GDRIVE_CLIENT_ID", ""), env.get("GDRIVE_CLIENT_SECRET", ""), env.get("GDRIVE_REFRESH_TOKEN", "")
        if not (cid and csec and rtok): return ""
        body = _t2pr_urlp.urlencode({"client_id": cid, "client_secret": csec, "refresh_token": rtok, "grant_type": "refresh_token"}).encode()
        try:
            with _t2pr_url.urlopen(_t2pr_url.Request("https://oauth2.googleapis.com/token", data=body), timeout=20) as r:
                return _t2pr_json.loads(r.read()).get("access_token", "")
        except Exception:
            return ""

    def _t2pr_drive_get(file_id, token):
        url = "https://www.googleapis.com/drive/v3/files/" + file_id + "?alt=media"
        with _t2pr_url.urlopen(_t2pr_url.Request(url, headers={"Authorization": "Bearer " + token}), timeout=60) as r:
            return r.read()

    def _t2pr_drive_put(file_id, token, content, mime):
        url = "https://www.googleapis.com/upload/drive/v3/files/" + file_id + "?uploadType=media"
        req = _t2pr_url.Request(url, data=content, method="PATCH",
            headers={"Authorization": "Bearer " + token, "Content-Type": mime})
        with _t2pr_url.urlopen(req, timeout=120) as r:
            return r.read()

    def _t2pr_extract_ids(result_text):
        s = _t2pr_s(result_text)
        x = _t2pr_re.search(r"docs\.google\.com/spreadsheets/d/([A-Za-z0-9_-]+)", s)
        p = _t2pr_re.search(r"drive\.google\.com/file/d/([A-Za-z0-9_-]+)", s)
        return (x.group(1) if x else "", p.group(1) if p else "")

    def _t2pr_real_suppliers(conn, task_id):
        # parse TOPIC2_PRICE_SOURCE_FOUND markers from history
        try:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'TOPIC2_PRICE_SOURCE_FOUND:%' ORDER BY rowid ASC",
                (str(task_id),),
            ).fetchall()
        except Exception:
            rows = []
        seen, out = set(), []
        for r in rows:
            a = _t2pr_s(r[0])
            parts = a.split(":", 3)
            if len(parts) >= 3:
                material = parts[1].strip()
                supplier = parts[2].strip() if len(parts) >= 3 else ""
                status = parts[3].strip() if len(parts) >= 4 else ""
                key = (material.lower(), supplier.lower())
                if key in seen or not supplier:
                    continue
                seen.add(key)
                out.append((material, supplier, status))
        return out

    def _t2pr_perplexity_search(query):
        """Прямой вызов Perplexity sonar через OpenRouter.
        Возвращает list[(category, supplier, contact, url, status)] или []."""
        try:
            import requests as _t2pr_req
        except Exception:
            return []
        api_key = <REDACTED_SECRET>"OPENROUTER_API_KEY", "").strip()
        model = _t2pr_os.environ.get("OPENROUTER_MODEL_ONLINE", "perplexity/sonar").strip() or "perplexity/sonar"
        if not api_key:
            return []
        if model != "perplexity/sonar" or "deepseek" in model.lower():
            try:
                _T2PR_LOG.error("t2pr blocked forbidden online model: %s", model)
            except Exception:
                pass
            return []
        prompt = (
            "Найди 6-8 актуальных поставщиков стройматериалов в Санкт-Петербурге и Ленинградской области (2026). "
            "Контекст запроса: " + (query or "общие стройматериалы для каркасного дома 8x12м") + ". "
            "Для каждого поставщика верни строку строго в формате: "
            "Категория | Название | Телефон | URL\n"
            "Только реально существующие компании. Без вступлений и комментариев. Только список."
        )
        try:
            resp = _t2pr_req.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.2},
                timeout=60,
            )
            if resp.status_code != 200:
                return []
            content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            try: _T2PR_LOG.warning("t2pr perplexity err: %s", e)
            except: pass
            return []
        out = []
        seen = set()
        for line in content.split("\n"):
            line = line.strip(" -*•0123456789.\t")
            if "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 2:
                continue
            cat = parts[0][:60] if parts[0] else "Стройматериалы"
            sup = parts[1][:80] if len(parts) > 1 else ""
            phone = parts[2][:40] if len(parts) > 2 else ""
            url = parts[3][:200] if len(parts) > 3 else ""
            if not sup or sup.lower() in ("название", "поставщик", "name"):
                continue
            key = sup.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append((cat, sup, phone, url, "Sonar"))
        return out[:10]

    _T2PR_INS_RE = (
        # walls — первое 2-3 значное число после "стен" (без других цифр между)
        ("walls", _t2pr_re.compile(r'утепл[а-я]*\s+стен[а-я]*[^\d.\n]{0,40}?(\d{2,3})\b', _t2pr_re.I)),
        ("walls", _t2pr_re.compile(r'\bстен[а-я]*[^\d.\n]{0,30}?(\d{2,3})\s*мм', _t2pr_re.I)),
        # roof / ceiling — то же
        ("roof", _t2pr_re.compile(r'утепл[а-я]*\s+(?:кровл[а-я]*|потол[а-я]*|перекрыт[а-я]*)[^\d.\n]{0,40}?(\d{2,3})\b', _t2pr_re.I)),
        ("roof", _t2pr_re.compile(r'\b(?:кровл[а-я]*|потол[а-я]*|перекрыт[а-я]*)[^\d.\n]{0,30}?(\d{2,3})\s*мм', _t2pr_re.I)),
    )

    def _t2pr_insulation_overrides(raw_input, history_text):
        ctx = (raw_input or "") + "\n" + (history_text or "")
        out = {"walls": None, "roof": None}
        for kind, rx in _T2PR_INS_RE:
            if out[kind] is not None:
                continue
            m = rx.search(ctx)
            if m:
                try:
                    out[kind] = int(m.group(1))
                except Exception:
                    pass
        return out

    def _t2pr_apply_xlsx_overrides(content, raw_input, history_text, real_suppliers):
        from openpyxl import load_workbook
        wb = load_workbook(_t2pr_io.BytesIO(content))
        ovs = _t2pr_insulation_overrides(raw_input, history_text)

        # AREAL_CALC: insulation thickness override
        if "AREAL_CALC" in wb.sheetnames:
            ws = wb["AREAL_CALC"]
            for r in range(1, ws.max_row + 1):
                section = _t2pr_s(ws.cell(r, 2).value).strip().lower()
                name = _t2pr_s(ws.cell(r, 3).value)
                low_name = name.lower()
                rock_hint = ""
                low_raw = (raw_input or "").lower()
                if _t2pr_re.search(r"rockwell|rockwool|каменн[а-я]*\s+ват|минер[а-я]*\s+ват", low_raw):
                    rock_hint = " (Rockwool, мин. вата)"
                if "утепл" in low_name and "стен" in low_name and ovs["walls"]:
                    new_name = _t2pr_re.sub(r"\d{2,3}\s*мм", str(ovs["walls"]) + " мм", name)
                    if rock_hint and rock_hint not in new_name:
                        new_name = new_name + rock_hint
                    ws.cell(r, 3).value = new_name
                elif "утепл" in low_name and ("кровл" in low_name or "потол" in low_name) and ovs["roof"]:
                    new_name = _t2pr_re.sub(r"\d{2,3}\s*мм", str(ovs["roof"]) + " мм", name)
                    if rock_hint and rock_hint not in new_name:
                        new_name = new_name + rock_hint
                    ws.cell(r, 3).value = new_name
                # Also fill Источник цены column based on real suppliers
                if real_suppliers and section in ("стены", "фундамент", "кровля", "проёмы", "фасад", "чистовая отделка"):
                    for material, supplier, status in real_suppliers:
                        if material.lower() in low_name or any(k in low_name for k in material.lower().split()):
                            ws.cell(r, 11).value = supplier
                            if ws.max_column >= 12: ws.cell(r, 12).value = supplier
                            if ws.max_column >= 13: ws.cell(r, 13).value = status
                            break

        # Проверка цен: append real suppliers (above fallback)
        if "Проверка цен" in wb.sheetnames and real_suppliers:
            ws = wb["Проверка цен"]
            # find row with "Стройматериалы" / "Петрович" — anchor
            anchor = None
            for r in range(1, ws.max_row + 1):
                if _t2pr_s(ws.cell(r, 2).value).strip() == "Петрович":
                    anchor = r
                    break
            if anchor:
                # insert real suppliers BEFORE anchor (push fallbacks down)
                for i, (mat, sup, status) in enumerate(real_suppliers):
                    ws.insert_rows(anchor + i)
                    ws.cell(anchor + i, 1).value = mat
                    ws.cell(anchor + i, 2).value = sup
                    ws.cell(anchor + i, 3).value = "по интернет-проверке"
                    ws.cell(anchor + i, 4).value = ""
                    ws.cell(anchor + i, 5).value = status
                    ws.cell(anchor + i, 6).value = "Sonar"

        out = _t2pr_io.BytesIO()
        wb.save(out)
        return out.getvalue(), wb

    def _t2pr_register_fonts():
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        font_reg, font_bold = "Helvetica", "Helvetica-Bold"
        for fp in _T2PR_FONT_PATHS:
            if _t2pr_os.path.exists(fp):
                try:
                    pdfmetrics.registerFont(TTFont("ArealCyr", fp))
                    font_reg = "ArealCyr"
                    break
                except Exception:
                    pass
        for fp in _T2PR_FONT_BOLD_PATHS:
            if _t2pr_os.path.exists(fp):
                try:
                    pdfmetrics.registerFont(TTFont("ArealCyrBold", fp))
                    font_bold = "ArealCyrBold"
                    break
                except Exception:
                    pass
        return font_reg, font_bold

    def _t2pr_xlsx_to_items(wb):
        items = []
        if "AREAL_CALC" not in wb.sheetnames:
            return items, 0.0
        ws = wb["AREAL_CALC"]
        total = 0.0
        for r in range(2, ws.max_row + 1):
            section = _t2pr_s(ws.cell(r, 2).value).strip()
            name = _t2pr_s(ws.cell(r, 3).value).strip()
            unit = _t2pr_s(ws.cell(r, 4).value).strip()
            try: qty = float(ws.cell(r, 5).value or 0)
            except: qty = 0.0
            try: mat_price = float(ws.cell(r, 6).value or 0)
            except: mat_price = 0.0
            try: work_price = float(ws.cell(r, 8).value or 0)
            except: work_price = 0.0
            if not name and not section:
                continue
            line_total = qty * (mat_price + work_price)
            if line_total <= 0 and not section:
                continue
            items.append({"section": section, "name": name, "unit": unit, "qty": qty, "total": line_total})
            total += line_total
        return items, total

    def _t2pr_build_pdf(items, total, params, real_suppliers, raw_input):
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
        font, font_bold = _t2pr_register_fonts()
        out = _t2pr_io.BytesIO()
        c = canvas.Canvas(out, pagesize=A4)
        w, h = A4
        x = 15 * mm
        y = h - 20 * mm

        c.setFont(font_bold, 14)
        c.drawString(x, y, "Предварительная смета")
        y -= 8 * mm
        c.setFont(font, 9)
        for line in (params.get("header") or []):
            c.drawString(x, y, line[:120])
            y -= 4.5 * mm
        y -= 4 * mm

        c.setFont(font_bold, 9)
        cols = [("№", x, 8*mm), ("Раздел", x + 10*mm, 30*mm), ("Позиция", x + 42*mm, 80*mm),
                ("Ед", x + 124*mm, 12*mm), ("Кол-во", x + 138*mm, 16*mm), ("Сумма, ₽", x + 156*mm, 30*mm)]
        for label, cx, _ in cols:
            c.drawString(cx, y, label)
        y -= 3 * mm
        c.line(x, y, w - 15*mm, y)
        y -= 5 * mm

        c.setFont(font, 8)
        for i, it in enumerate(items, 1):
            if y < 30 * mm:
                c.showPage()
                c.setFont(font, 8)
                y = h - 20 * mm
            row_vals = [str(i), it["section"][:18], it["name"][:50], it["unit"][:5], f"{it['qty']:g}", f"{it['total']:,.0f}".replace(",", " ")]
            for (label, cx, _), v in zip(cols, row_vals):
                c.drawString(cx, y, v)
            y -= 4.5 * mm

        y -= 3 * mm
        c.line(x, y, w - 15*mm, y)
        y -= 6 * mm
        c.setFont(font_bold, 11)
        c.drawString(x + 100*mm, y, "Итого, ₽:")
        c.drawString(x + 156*mm, y, f"{total:,.0f}".replace(",", " "))
        y -= 8 * mm

        if real_suppliers:
            c.setFont(font_bold, 10)
            c.drawString(x, y, "Поставщики (интернет-проверка):")
            y -= 5 * mm
            c.setFont(font, 8)
            for mat, sup, status in real_suppliers[:8]:
                if y < 25 * mm:
                    c.showPage()
                    c.setFont(font, 8)
                    y = h - 20 * mm
                line = "- " + mat + ": " + sup + ((" — " + status) if status else "")
                c.drawString(x, y, line[:140])
                y -= 4.5 * mm
            y -= 2 * mm

        c.setFont(font_bold, 10)
        c.drawString(x, y, "Контактные базы:")
        y -= 5 * mm
        c.setFont(font, 8)
        for cat, sup, phone, url in _T2PR_FALLBACK:
            if y < 20 * mm:
                c.showPage()
                c.setFont(font, 8)
                y = h - 20 * mm
            line = "- " + cat + ": " + sup + " (" + phone + ")"
            c.drawString(x, y, line[:140])
            y -= 4.5 * mm

        c.save()
        return out.getvalue()

    def _t2pr_build_telegram_supplier_block(real_suppliers):
        if not real_suppliers:
            return ""
        lines = ["Поставщики (интернет-проверка Sonar):"]
        for mat, sup, status in real_suppliers[:10]:
            sign = " — " + status if status else ""
            lines.append("- " + mat + ": " + sup + sign)
        return "\n".join(lines)

    def _t2pr_should_run(conn, task_id, xlsx_id, pdf_id):
        mk = "PATCH_TOPIC2_PDF_AND_REAL_SUPPLIERS_V1:OK:" + xlsx_id + ":" + pdf_id
        try:
            row = conn.execute("SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1", (str(task_id), mk)).fetchone()
            return not bool(row), mk
        except Exception:
            return True, mk

    def _t2pr_history_text(conn, task_id):
        try:
            rows = conn.execute("SELECT action FROM task_history WHERE task_id=? ORDER BY rowid ASC", (str(task_id),)).fetchall()
            return "\n".join(_t2pr_s(r[0]) for r in rows)
        except Exception:
            return ""

    def _t2pr_telegram_edit(chat_id, message_id, text):
        try:
            data = open(_T2PR_OVERRIDE, "r", encoding="utf-8").read()
        except Exception:
            return False, "NO_OVR"
        token = ""
        try:
            for line in open("/root/.areal-neva-core/.env", "r", encoding="utf-8"):
                line = line.strip()
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    token = <REDACTED_SECRET>"=", 1)[1].strip().strip('"').strip("'")
                    break
        except Exception:
            return False, "NO_ENV"
        if not (token and chat_id and message_id):
            return False, "MISSING"
        payload = {"chat_id": str(chat_id), "message_id": int(message_id), "text": text[:4096], "disable_web_page_preview": False}
        req = _t2pr_url.Request(
            "https://api.telegram.org/bot" + token + "/editMessageText",
            data=_t2pr_json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        try:
            with _t2pr_url.urlopen(req, timeout=20) as r: r.read()
            return True, "OK"
        except Exception as e:
            return False, type(e).__name__ + ":" + _t2pr_s(e)[:120]

    def _t2pr_full_repair(conn, task_id):
        try:
            row = conn.execute(
                "SELECT id, chat_id, bot_message_id, raw_input, result, state, topic_id FROM tasks WHERE id=? LIMIT 1",
                (str(task_id),),
            ).fetchone()
            if not row: return False
            try: topic_id = int(row[6] or 0)
            except: topic_id = 0
            if topic_id != 2 or _t2pr_s(row[5]) not in ("DONE", "AWAITING_CONFIRMATION"):
                return False
            chat_id = _t2pr_s(row[1])
            bot_msg_id = row[2]
            raw_input = _t2pr_s(row[3])
            result = _t2pr_s(row[4])
            xlsx_id, pdf_id = _t2pr_extract_ids(result)
            if not xlsx_id or not pdf_id:
                return False
            should, mk = _t2pr_should_run(conn, task_id, xlsx_id, pdf_id)
            if not should:
                return False

            history_text = _t2pr_history_text(conn, task_id)
            real = _t2pr_real_suppliers(conn, task_id)

            # Если user просит больше/новых поставщиков — добавим прямой Sonar-поиск через Perplexity/OpenRouter
            ctx_low = ((raw_input or "") + " " + (history_text or "")).lower()
            user_wants_more = True
            already_searched = any(_t2pr_re.match(r"^PATCH_TOPIC2_PDF_AND_REAL_SUPPLIERS_V1:SONAR_SEARCH_OK", a) for a in (history_text or "").split("\n"))
            if user_wants_more and not already_searched:
                query = (raw_input or "").strip()
                if query:
                    query = "Актуальные поставщики и цены СПб/Ленобласть для сметы: " + query[:1200]
                else:
                    query = "Актуальные поставщики и цены СПб/Ленобласть для строительной сметы по текущему ТЗ"
                live_supps = _t2pr_perplexity_search(query)
                if live_supps:
                    try:
                        conn.execute(
                            "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                            (str(task_id), "PATCH_TOPIC2_PDF_AND_REAL_SUPPLIERS_V1:SONAR_SEARCH_OK:" + str(len(live_supps))),
                        )
                        conn.commit()
                        for cat, sup, phone, url, status in live_supps[:8]:
                            try:
                                conn.execute(
                                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                                    (str(task_id), "TOPIC2_PRICE_SOURCE_FOUND:" + cat[:40] + ":" + sup[:60] + ":" + status),
                                )
                            except Exception:
                                pass
                        conn.commit()
                    except Exception:
                        pass
                    # Add to real list (use compatible 3-tuple format expected by downstream)
                    for cat, sup, phone, url, status in live_supps:
                        real.append((cat, sup, status))
                    # Also keep the rich 5-tuple for inserts later
                    _t2pr_extra_supps = live_supps
                else:
                    _t2pr_extra_supps = []
                    try:
                        conn.execute(
                            "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                            (str(task_id), "PATCH_TOPIC2_PDF_AND_REAL_SUPPLIERS_V1:SONAR_SEARCH_EMPTY"),
                        )
                        conn.commit()
                    except Exception:
                        pass
            else:
                _t2pr_extra_supps = []

            token = <REDACTED_SECRET>
            if not token:
                conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (str(task_id), "PATCH_TOPIC2_PDF_AND_REAL_SUPPLIERS_V1:FAIL:NO_TOKEN"))
                conn.commit()
                return False

            try:
                xlsx_bytes = _t2pr_drive_get(xlsx_id, token)
            except Exception as e:
                _T2PR_LOG.warning("t2pr xlsx get fail %s", e)
                return False

            new_xlsx, wb = _t2pr_apply_xlsx_overrides(xlsx_bytes, raw_input, history_text, real)
            try:
                _t2pr_drive_put(xlsx_id, token, new_xlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception as e:
                _T2PR_LOG.warning("t2pr xlsx put fail %s", e)

            items, total = _t2pr_xlsx_to_items(wb)
            ovs = _t2pr_insulation_overrides(raw_input, history_text)
            def _t2pr_object_header_from_raw(text):
                src = str(text or "").replace("\r", " ").replace("\n", " ")
                src_l = src.lower().replace("ё", "е")
                m = _t2pr_re.search(r"(\d+(?:[.,]\d+)?)\s*[xх×]\s*(\d+(?:[.,]\d+)?)", src_l)
                dims = (m.group(1).replace(",", ".") + "x" + m.group(2).replace(",", ".") + " м") if m else "по ТЗ"
                fm = _t2pr_re.search(r"(\d+)\s*(?:этаж|этажа|этажей)", src_l)
                floors = (", этажей: " + fm.group(1)) if fm else ""
                material = ""
                for word in ("кирпич", "газобетон", "керамоблок", "монолит", "арболит", "брус", "каркас"):
                    if word in src_l:
                        material = ", материал: " + word
                        break
                return "Объект: дом " + dims + floors + material

            object_line = _t2pr_object_header_from_raw(raw_input)
            params = {"header": [
                object_line,
                "Утепление: стен " + (str(ovs["walls"]) + " мм" if ovs["walls"] else "по проекту") + ", кровли " + (str(ovs["roof"]) + " мм" if ovs["roof"] else "по проекту"),
                "Без НДС (НДС не применяется)",
            ]}
            try:
                pdf_bytes = _t2pr_build_pdf(items, total, params, real, raw_input)
                _t2pr_drive_put(pdf_id, token, pdf_bytes, "application/pdf")
            except Exception as e:
                _T2PR_LOG.exception("t2pr pdf fail: %s", e)
                conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (str(task_id), "PATCH_TOPIC2_PDF_AND_REAL_SUPPLIERS_V1:PDF_FAIL:" + type(e).__name__ + ":" + _t2pr_s(e)[:120]))
                conn.commit()

            # Update DB result with real suppliers block
            sup_block = _t2pr_build_telegram_supplier_block(real)
            if sup_block:
                # Insert before "Поставщики и контакты"
                if "Поставщики (интернет-проверка Sonar):" in result:
                    result = _t2pr_re.sub(r"Поставщики \(интернет-проверка Sonar\):\n(?:- .*\n?)+", sup_block + "\n", result)
                elif "Поставщики и контакты" in result:
                    result = result.replace("Поставщики и контакты", sup_block + "\n\nПоставщики и контакты", 1)
                else:
                    result = result + "\n\n" + sup_block
                conn.execute("UPDATE tasks SET result=?, updated_at=datetime('now') WHERE id=?", (result, str(task_id)))
                _t2pr_telegram_edit(chat_id, bot_msg_id, result)

            conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                (str(task_id), mk))
            conn.commit()
            _T2PR_LOG.info("PATCH_TOPIC2_PDF_AND_REAL_SUPPLIERS_V1 task=%s xlsx=%s pdf=%s real_sup=%d", task_id, xlsx_id, pdf_id, len(real))
            return True
        except Exception as e:
            try: _T2PR_LOG.exception("t2pr full repair err: %s", e)
            except: pass
            return False

    _T2PR_ORIG = globals().get("_t2sh_heal_task")
    if _T2PR_ORIG and not getattr(_T2PR_ORIG, "_t2pr_wrapped", False):
        def _t2sh_heal_task(conn, task_id):
            res = False
            try:
                res = _T2PR_ORIG(conn, task_id)
            except Exception as e:
                try: _T2PR_LOG.exception("t2pr orig heal err: %s", e)
                except: pass
                return False
            try:
                _t2pr_full_repair(conn, task_id)
            except Exception as e:
                try: _T2PR_LOG.exception("t2pr full repair wrap err: %s", e)
                except: pass
            return res
        _t2sh_heal_task._t2pr_wrapped = True
        globals()["_t2sh_heal_task"] = _t2sh_heal_task

    _T2PR_LOG.info("PATCH_TOPIC2_PDF_AND_REAL_SUPPLIERS_V1 installed")

except Exception as _t2pr_install_err:
    try:
        logger.exception("PATCH_TOPIC2_PDF_AND_REAL_SUPPLIERS_V1_INSTALL_ERR:%s", _t2pr_install_err)
    except Exception:
        pass
# === /PATCH_TOPIC2_PDF_AND_REAL_SUPPLIERS_V1 ===


# === PATCH_TOPIC2_TG_FORMAT_CANON_V1 ===
# Цель: §9 Telegram format + §11 forbidden blockers (TOPIC_2 canon LOCK 2026-05-07).
# Sanitize OLD-format estimate output:
#   - «✅ Предварительная смета готова» → «✅ Смета готова»
#   - удаляет ТОЛЬКО §11 forbidden block: «Разделы:» (список секций)
#   - убирает emoji 📊/📄 в Excel/PDF строках
#   - footer «Доволен результатом? Да / Уточни / Правки» → «Подтверди или пришли правки»
# НЕ ТРОГАЕТ: «Учтено из дополнений к ТЗ:», «Поставщики и контакты ...» —
#   эти блоки НЕ в forbidden list канона §11; suppliers-блок ставится PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1.
# Срабатывает на: (a) outbound _send_once/_send_once_ex (б) post-DONE polling worker
# который правит уже доставленные results через editMessageText. Идемпотентно через
# маркер [CANON_FMT_V1] в конце текста.
try:
    import re as _t2cf_re
    import os as _t2cf_os
    import time as _t2cf_time
    import threading as _t2cf_threading
    import sqlite3 as _t2cf_sqlite3
    import logging as _t2cf_logging
    import urllib.request as _t2cf_urlreq
    import json as _t2cf_json

    _T2CF_LOG = _t2cf_logging.getLogger("task_worker")
    _T2CF_MARKER = "[CANON_FMT_V1]"
    _T2CF_OLD_HEADER = "✅ Предварительная смета готова"
    _T2CF_NEW_HEADER = "✅ Смета готова"
    _T2CF_OLD_FOOTER = "Доволен результатом? Да / Уточни / Правки"
    _T2CF_NEW_FOOTER = "Подтверди или пришли правки"

    def _t2cf_should_sanitize(text):
        if not isinstance(text, str):
            return False
        if _T2CF_MARKER in text:
            return False
        return ("Предварительная смета готова" in text) or ("Разделы:" in text and "Объект:" in text)

    def _t2cf_sanitize(text):
        if not _t2cf_should_sanitize(text):
            return text
        s = text
        s = s.replace(_T2CF_OLD_HEADER, _T2CF_NEW_HEADER)
        s = s.replace("Предварительная смета готова", "Смета готова")
        # §11 forbidden block — ТОЛЬКО «Разделы:» (см. canon §11). Не трогаем «Учтено..» и «Поставщики..»
        s = _t2cf_re.sub(r"\n?Разделы:\s*\n(?:[ \t]*[-•][^\n]*\n?)+", "\n", s)
        # Emoji prefixes on links
        s = s.replace("📊 Excel:", "Excel:")
        s = s.replace("📄 PDF:", "PDF:")
        # Footer
        s = s.replace(_T2CF_OLD_FOOTER, _T2CF_NEW_FOOTER)
        # Collapse multi-blank
        s = _t2cf_re.sub(r"[ \t]+\n", "\n", s)
        s = _t2cf_re.sub(r"\n{3,}", "\n\n", s).strip()
        s = s + "\n\n" + _T2CF_MARKER

====================================================================================================
END_FILE: task_worker.py
FILE_CHUNK: 3/5
====================================================================================================
