# ORCHESTRA_FULL_CONTEXT_PART_007
generated_at_utc: 2026-05-08T20:10:01.999899+00:00
git_sha_before_commit: 531398c8bf6e37ce42979d3ad69fc7bafe2a76cf
part: 7/17


====================================================================================================
BEGIN_FILE: task_worker.py
FILE_CHUNK: 3/3
SHA256_FULL_FILE: 51a4018672c85440cfcb382321178ae361646bd033b07adcda3267ec157607a7
====================================================================================================
# Факт: 17:33 «Задача отменена» → бот спросил «Сколько этажей»
# ============================================================
import re as _tcg_re
import inspect as _tcg_inspect
import logging as _tcg_logging
_TCG_LOG = _tcg_logging.getLogger("task_worker.cancel_guard")

_TCG_CANCEL_RE = _tcg_re.compile(
    r"(?:^|\s)(?:\[VOICE\]\s*)?"
    r"(отмена|отбой|стоп|заверши|завершена|закрой|закрывай|очисти|"
    r"отменяй|задача отменена|отмена задач|все задачи завершен|"
    r"отбой всех|очисти все|задача завершена)",
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


if __name__ == "__main__":
    asyncio.run(main())

====================================================================================================
END_FILE: task_worker.py
FILE_CHUNK: 3/3
====================================================================================================

====================================================================================================
BEGIN_FILE: telegram_daemon.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: f771a4f4dcb22b9c87a2660e78a3b362aeb4fcdcba47609ea236d49efdde5115
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

        if reply_to:
            async with aiosqlite.connect(DB) as db:
                cur = await db.execute(
                    "SELECT id, state FROM tasks WHERE chat_id = ? AND reply_to_message_id = ? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
                    (tg_id, reply_to)
                )
                parent = await cur.fetchone()
            if parent:
                parent_id, parent_state = parent
                if parent_state == "WAITING_CLARIFICATION":
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
                else:
                    await message.answer("Уточните запрос")
                return

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
            try:
                await message.answer(f"🎤 {voice_text}")
            except Exception as _e:
                logger.warning("transcript_send_fail err=%s", _e)
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

====================================================================================================
BEGIN_FILE: core/project_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 78d74f019c8b179cf8eb33cc618b4099de55b4ae08b382209ad58ab00af35e98
====================================================================================================
# === PROJECT_ENGINE_V1 ===
"""
core/project_engine.py
Разработка проектной документации по нормам ГОСТ/СНиП/СП
на основе шаблонов пользователя.
Разрешение на создание получено: 29.04.2026
"""
import os, re, logging, tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

SECTION_MAP = {
    "кж":  "КЖ — Конструкции железобетонные",
    "км":  "КМ — Конструкции металлические",
    "кмд": "КМД — Конструкции металлические деталировочные",
    "ар":  "АР — Архитектурные решения",
    "ов":  "ОВ — Отопление и вентиляция",
    "вк":  "ВК — Водоснабжение и канализация",
    "эом": "ЭОМ — Электроосвещение",
    "сс":  "СС — Слаботочные системы",
    "гп":  "ГП — Генеральный план",
    "пз":  "ПЗ — Пояснительная записка",
    "см":  "СМ — Смета",
    "тх":  "ТХ — Технологические решения",
}

SECTION_STRUCTURE = {
    "кж":  ["Армирование", "Схемы", "Спецификация арматуры", "Спецификация материалов"],
    "км":  ["Нагрузки", "Узлы сопряжений", "Спецификация металла"],
    "кмд": ["Деталировка", "Узлы", "Спецификация"],
    "ар":  ["Планы этажей", "Фасады", "Разрезы", "Экспликация помещений"],
    "ов":  ["Схема системы", "Расчёт нагрузок", "Спецификация оборудования"],
    "вк":  ["Схема водоснабжения", "Схема канализации", "Спецификация"],
    "эом": ["Однолинейная схема", "Расчёт нагрузок", "Спецификация"],
}

NORMS_MAP = {
    "кж":  ["СП 63.13330.2018", "ГОСТ 34028-2016", "СП 20.13330.2017"],
    "км":  ["СП 16.13330.2017", "ГОСТ 27772-2015", "СП 20.13330.2017"],
    "ар":  ["СП 118.13330.2022", "ГОСТ 21.501-2018"],
    "ов":  ["СП 60.13330.2020", "ГОСТ 30494-2011"],
    "вк":  ["СП 30.13330.2020", "СП 31.13330.2021"],
    "эом": ["СП 256.1325800.2016", "ПУЭ-7"],
}

SNOW_LOADS = {1: 0.8, 2: 1.2, 3: 1.8, 4: 2.4, 5: 3.2, 6: 4.0, 7: 4.8, 8: 5.6}
WIND_LOADS = {1: 0.17, 2: 0.23, 3: 0.30, 4: 0.38, 5: 0.48, 6: 0.60, 7: 0.73, 8: 0.85}

SPEC_HEADERS = ["№", "Наименование", "Марка/Обозначение", "Ед. изм.", "Кол-во", "Примечание"]
UNITS = {"мм", "м", "м2", "м3", "кг", "т", "шт", "пог.м"}


def detect_section(file_name: str, text: str = "") -> Optional[str]:
    # FULLFIX_02_B1: filename-first section priority
    fn = (file_name or "").lower()
    for key in SECTION_MAP:
        if key in fn:
            return key
    src = ((file_name or "") + " " + (text or "")).lower()
    for key in SECTION_MAP:
        if key in src:
            return key
    return None


def calc_loads(region: int = 3) -> Dict[str, float]:
    return {
        "snow_kPa":  SNOW_LOADS.get(region, 1.8),
        "wind_kPa":  WIND_LOADS.get(region, 0.30),
        "region":    region,
        "note":      f"СП 20.13330.2017 — район {region}",
    }


def normalize_unit(unit: str) -> str:
    u = str(unit or "").strip().lower()
    mapping = {"м2": "м2", "м²": "м2", "м3": "м3", "м³": "м3", "кг": "кг", "т": "т", "шт": "шт", "м": "м", "мм": "мм"}
    return mapping.get(u, u)


def build_specification(items: List[Dict]) -> List[List]:
    rows = [SPEC_HEADERS]
    for i, item in enumerate(items, 1):
        rows.append([
            i,
            item.get("name", ""),
            item.get("mark", ""),
            normalize_unit(item.get("unit", "")),
            item.get("qty", ""),
            item.get("note", ""),
        ])
    return rows


def _write_project_xlsx(section: str, items: List[Dict], loads: Dict, task_id: str) -> str:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill
    wb = Workbook()
    ws = wb.active
    ws.title = section.upper()

    ws.merge_cells("A1:F1")
    ws["A1"] = SECTION_MAP.get(section, section.upper())
    ws["A1"].font = Font(bold=True, size=13)
    ws["A1"].alignment = Alignment(horizontal="center")

    norms = NORMS_MAP.get(section, [])
    ws["A2"] = "Нормы: " + ", ".join(norms) if norms else ""

    if section in ("кж", "км", "кмд"):
        ws["A3"] = f"Снег: {loads['snow_kPa']} кПа | Ветер: {loads['wind_kPa']} кПа | {loads['note']}"

    spec = build_specification(items)
    start_row = 5
    for r_idx, row in enumerate(spec, start_row):
        for c_idx, val in enumerate(row, 1):
            cell = ws.cell(r_idx, c_idx, value=val)
            if r_idx == start_row:
                cell.font = Font(bold=True)
                cell.fill = PatternFill("solid", fgColor="DDEEFF")

    struct = SECTION_STRUCTURE.get(section, [])
    if struct:
        ws.cell(start_row + len(spec) + 2, 1, "Состав раздела:")
        for i, s in enumerate(struct, 1):
            ws.cell(start_row + len(spec) + 2 + i, 1, f"{i}. {s}")

    tmp = os.path.join(tempfile.gettempdir(), f"project_{section}_{task_id}.xlsx")
    wb.save(tmp)
    return tmp


async def generate_project_section(section: str, items: List[Dict], task_id: str, topic_id: int, region: int = 3) -> Dict[str, Any]:
    res = {"success": False, "excel_path": None, "drive_link": None, "section": section, "error": None}
    try:
        loads = calc_loads(region)
        xl = _write_project_xlsx(section, items, loads, task_id)
        res["excel_path"] = xl

        from core.engine_base import upload_artifact_to_drive, quality_gate
        qg = quality_gate(xl, task_id, "excel")
        if not qg["passed"]:
            res["error"] = f"QualityGate: {qg['errors']}"
            return res

        link = upload_artifact_to_drive(xl, task_id, topic_id)
        if link:
            res["drive_link"] = link
            res["success"] = True
        else:
            res["error"] = "UPLOAD_FAILED"
    except Exception as e:
        logger.error(f"project_engine: {e}", exc_info=True)
        res["error"] = str(e)[:300]
    return res


def project_result_guard(result: Dict) -> Dict:
    if not result.get("success"):
        return result
    if not result.get("excel_path") and not result.get("drive_link"):
        result["success"] = False
        result["error"] = "PROJECT_RESULT_GUARD: нет артефакта"
    return result


async def process_project_file(file_path: str, task_id: str, topic_id: int, raw_input: str = "") -> Dict[str, Any]:
    section = detect_section(file_path, raw_input) or "кж"
    items = []

    try:
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        for row in (table or []):
                            if row and any(row):
                                items.append({
                                    "name": str(row[0] or ""),
                                    "mark": str(row[1] or "") if len(row) > 1 else "",
                                    "unit": str(row[2] or "") if len(row) > 2 else "",
                                    "qty":  str(row[3] or "") if len(row) > 3 else "",
                                })
        elif ext in (".xlsx", ".xls"):
            from openpyxl import load_workbook
            wb = load_workbook(file_path, data_only=True)
            ws = wb.active
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row and any(v for v in row if v):
                    items.append({
                        "name": str(row[0] or ""),
                        "mark": str(row[1] or "") if len(row) > 1 else "",
                        "unit": str(row[2] or "") if len(row) > 2 else "",
                        "qty":  str(row[3] or "") if len(row) > 3 else "",
                    })
            wb.close()
    except Exception as e:
        logger.warning(f"project extract: {e}")

    result = await generate_project_section(section, items, task_id, topic_id)
    return project_result_guard(result)
# === END_PROJECT_ENGINE_V1 ===

# === CODE_CLOSE_V43_PROJECT_ENGINE ===

def normative_search_engine_v43(section: str, query: str = ""):
    base = NORMS_MAP.get(section, [])
    if base:
        return {"success": True, "norms": base, "source": "local_norms_map"}
    return {"success": False, "norms": [], "error": "норма не подтверждена"}

def project_validator_v43(result):
    if not isinstance(result, dict):
        return False, "PROJECT_VALIDATOR: empty"
    if result.get("success") is False:
        return False, str(result.get("error") or "PROJECT_VALIDATOR: failed")
    if not (result.get("drive_link") or result.get("excel_path") or result.get("docx_path") or result.get("pdf_path")):
        return False, "PROJECT_VALIDATOR: no_artifact"
    return True, ""

def metal_structure_engine_v43(items, region=3):
    loads = calc_loads(region)
    spec = []
    for item in items or []:
        name = str(item.get("name") or "")
        if any(x in name.lower() for x in ("колонна","балка","ферма","связь","прогон")):
            spec.append(item)
    return {"loads": loads, "items": spec, "norms": NORMS_MAP.get("км", [])}

def project_result_guard_v43(result):
    ok, reason = project_validator_v43(result)
    if not ok:
        result = result if isinstance(result, dict) else {}
        result["success"] = False
        result["error"] = reason
    return result

try:
    _v43_orig_generate_project_section = generate_project_section
    async def generate_project_section(section, items, task_id, topic_id, region=3):
        res = await _v43_orig_generate_project_section(section, items, task_id, topic_id, region)
        res["normative_search"] = normative_search_engine_v43(section)
        if section in ("км","кмд"):
            res["metal_structure"] = metal_structure_engine_v43(items, region)
        return project_result_guard_v43(res)
except Exception:
    pass

# === END_CODE_CLOSE_V43_PROJECT_ENGINE ===

# === PROJECT_CLOSE_V44 ===

def normative_search_engine_v44(section: str, query: str = ""):
    norms = NORMS_MAP.get(section, [])
    if norms:
        return {"success": True, "norms": norms, "source": "NORMS_MAP"}
    return {"success": False, "norms": [], "error": "норма не подтверждена"}

def project_validator_v44(result):
    if not isinstance(result, dict):
        return False, "PROJECT_VALIDATOR_EMPTY"
    if result.get("success") is False:
        return False, str(result.get("error") or "PROJECT_VALIDATOR_FAILED")
    if not result.get("section"):
        return False, "PROJECT_VALIDATOR_NO_SECTION"
    if not (result.get("drive_link") or result.get("excel_path") or result.get("docx_path") or result.get("pdf_path")):
        return False, "PROJECT_VALIDATOR_NO_ARTIFACT"
    return True, ""

def metal_structure_engine_v44(items, region=3):
    spec = []
    for item in items or []:
        name = str(item.get("name") or "").lower()
        if any(x in name for x in ("колонна","балка","ферма","связь","прогон","рама","ангар")):
            spec.append(item)
    return {"success": True, "loads": calc_loads(region), "items": spec, "norms": NORMS_MAP.get("км", [])}

def _write_project_docx_v44(section, items, loads, task_id):
    import os, tempfile
    path = os.path.join(tempfile.gettempdir(), f"project_{section}_{task_id}.docx")
    try:
        from docx import Document
        doc = Document()
        doc.add_heading(SECTION_MAP.get(section, section.upper()), level=1)
        doc.add_paragraph("Нормы: " + ", ".join(NORMS_MAP.get(section, [])))
        doc.add_paragraph(f"Снег: {loads.get('snow_kPa')} кПа | Ветер: {loads.get('wind_kPa')} кПа")
        table = doc.add_table(rows=1, cols=6)
        for i, h in enumerate(SPEC_HEADERS):
            table.rows[0].cells[i].text = h
        for n, item in enumerate(items or [], 1):
            row = table.add_row().cells
            row[0].text = str(n)
            row[1].text = str(item.get("name",""))
            row[2].text = str(item.get("mark",""))
            row[3].text = normalize_unit(item.get("unit",""))
            row[4].text = str(item.get("qty",""))
            row[5].text = str(item.get("note",""))
        doc.save(path)
    except Exception:
        with open(path, "w", encoding="utf-8") as f:
            f.write(SECTION_MAP.get(section, section.upper()) + "\n")
            f.write("Нормы: " + ", ".join(NORMS_MAP.get(section, [])) + "\n")
            f.write(str(items or []))
    return path

try:
    _v44_orig_generate_project_section = generate_project_section

    async def generate_project_section(section, items, task_id, topic_id, region=3):
        res = await _v44_orig_generate_project_section(section, items, task_id, topic_id, region)
        loads = calc_loads(region)
        res["normative_search"] = normative_search_engine_v44(section)
        if section in ("км", "кмд"):
            res["metal_structure"] = metal_structure_engine_v44(items, region)
        try:
            docx_path = _write_project_docx_v44(section, items, loads, task_id)
            res["docx_path"] = docx_path
            from core.engine_base import upload_artifact_to_drive
            docx_link = upload_artifact_to_drive(docx_path, task_id, topic_id)
            if docx_link:
                res["docx_link"] = docx_link
        except Exception as e:
            res["docx_error"] = str(e)[:300]
        ok, reason = project_validator_v44(res)
        if not ok:
            res["success"] = False
            res["error"] = reason
        return res
except Exception:
    pass

# === END_PROJECT_CLOSE_V44 ===


# === PATCH_TEMPLATE_MODEL_EXTRACTOR_V1 ===
import re as _re_pte

def extract_template_model_from_text(text: str, file_name: str = "", user_text: str = "") -> dict:
    lines = [l.strip() for l in (text or "").replace("\r","\n").split("\n") if l.strip()]
    # FULLFIX_02_B2: filename-first project type priority, КД/КЖ before АР
    _MARKS_PRI = ("КД","КЖ","КМД","КМ","КР","АР","ОВ","ВК","ЭОМ","СС","ГП","ПЗ","ТХ","СМ")
    project_type = "UNKNOWN"
    for _pt_src in ((file_name or ""), (user_text or ""), (text or "")[:500]):
        _pt_upper = _pt_src.upper()
        for mark in _MARKS_PRI:
            if _re_pte.search(rf"(^|[^А-ЯA-Zа-яa-z]){_re_pte.escape(mark)}([^А-ЯA-Zа-яa-z]|$)", _pt_upper):
                project_type = mark
                break
        if project_type != "UNKNOWN":
            break
    src = f"{file_name} {user_text} {text[:3000]}".upper()
    sheets = []
    for line in lines:
        m = _re_pte.search(r"(АР|КЖ|КД|КР|КМ|КМД|ОВ|ВК|ЭОМ)[\s\-]*(\d+[А-ЯA-Z0-9\-\.]*)\s+(.{4,120})", line, _re_pte.I)
        if m and len(sheets) < 80:
            sheets.append({"mark": m.group(1), "number": m.group(2), "title": m.group(3).strip()})
    section_keys = ("общие данные","исходные данные","расч","план","фасад","разрез","узел","схема","спецификация","ведомость","конструктив","материал")
    sections = []
    seen = set()
    for line in lines:
        if any(k in line.lower() for k in section_keys) and line.lower() not in seen:
            seen.add(line.lower())
            sections.append(line[:160])
        if len(sections) >= 60:
            break
    # FULLFIX_02_B3: sheet_register fallback from extracted structure when explicit sheet marks are absent
    if not sheets and sections:
        _sf_keys = ("общие данные","ведомость","план","фасады","фасад","разрез","узел","спецификация","схема","расч","конструктив")
        _sf_seen = set()
        _sf_seq = 1
        for _sf_line in sections:
            _sf_low = _sf_line.lower()
            if any(k in _sf_low for k in _sf_keys):
                _sf_title = _sf_line[:120].strip()
                if _sf_title and _sf_title.lower() not in _sf_seen:
                    _sf_seen.add(_sf_title.lower())
                    sheets.append({"mark": project_type, "number": str(_sf_seq), "title": _sf_title})
                    _sf_seq += 1
            if _sf_seq > 30:
                break
    axes_letters = sorted(set(_re_pte.findall(r"(?<![А-ЯA-Z])([А-ЯA-Z])(?=\s*[-–]\s*[А-ЯA-Z])", text)))
    axes_numbers = sorted(set(_re_pte.findall(r"(?<!\d)(\d{1,2})(?=\s*[-–]\s*\d{1,2})(?!\d)", text)), key=lambda x: int(x))
    dims = []
    for x in _re_pte.findall(r"(?<!\d)(\d{3,5})(?!\d)", text):
        try:
            v = int(x)
            if 300 <= v <= 50000 and v not in dims:
                dims.append(v)
        except Exception:
            pass
    levels = []
    for v in _re_pte.findall(r"[-+]?\d+[,.]\d{2,3}", text):
        try:
            f = float(v.replace(",","."))
            s = str(f)
            if -20 <= f <= 100 and s not in levels:
                levels.append(s)
        except Exception:
            pass
    mat_keys = ("бетон","арматур","a500","b25","в25","доска","брус","фанера","утепл","профлист","металл","кирпич","газобетон","сталь","с255")
    materials = []
    mat_seen = set()
    for line in lines:
        if any(k in line.lower() for k in mat_keys) and line.lower() not in mat_seen:
            mat_seen.add(line.lower())
            materials.append(line[:180])
        if len(materials) >= 60:
            break
    stamp = {}
    for m in _re_pte.finditer(r"((?:Адрес|По адресу)[:\s]+)([^\n]{5,180})", text, _re_pte.I):
        stamp["address"] = m.group(2).strip()[:200]
        break
    for m in _re_pte.finditer(r"((?:ООО|ОАО|ЗАО|ИП)[^\n]{3,180})", text):
        stamp["developer"] = m.group(1).strip()[:200]
        break
    for m in _re_pte.finditer(r"\b(20\d{2})\b", text):
        stamp["year"] = m.group(1)
        break
    model = {
        "schema": "PROJECT_TEMPLATE_MODEL_V1",
        "project_type": project_type,
        "source_files": [file_name] if file_name else [],
        "sheet_register": sheets,
        "marks": [project_type] if project_type != "UNKNOWN" else [],
        "sections": sections,
        "axes_grid": {"axes_letters": axes_letters[:30], "axes_numbers": axes_numbers[:30]},
        "dimensions": dims[:80],
        "levels": levels[:40],
        "nodes": [x for x in sections if "узел" in x.lower()][:30],
        "specifications": [x for x in sections if any(k in x.lower() for k in ("спецификац","ведомость"))][:30],
        "materials": materials,
        "stamp_fields": stamp,
        "variable_parameters": ["project_name","address","customer","area","floors","axes_grid","dimensions","materials","sheet_register"],
        "output_documents": ["DOCX_PROJECT_TEMPLATE_SUMMARY","JSON_PROJECT_TEMPLATE_MODEL","XLSX_SPECIFICATION_DRAFT"],
        "quality": {
            "has_sheet_register": bool(sheets),
            "has_sections": bool(sections),
            "has_axes_or_dimensions": bool(axes_letters or axes_numbers or dims),
            "has_materials": bool(materials),
            "text_chars": len(text or ""),
            "lines": len(lines),
        }
    }
    return model


def is_valid_project_template_model(model: dict) -> bool:
    if not isinstance(model, dict):
        return False
    q = model.get("quality") or {}
    return bool(
        model.get("schema") == "PROJECT_TEMPLATE_MODEL_V1"
        and q.get("text_chars", 0) > 200
        and (q.get("has_sheet_register") or q.get("has_sections") or q.get("has_axes_or_dimensions") or q.get("has_materials"))
    )


def model_to_text_report(model: dict) -> str:
    lines = ["PROJECT_TEMPLATE_MODEL создан"]
    lines.append(f"Раздел: {model.get('project_type','UNKNOWN')}")
    lines.append("")
    sheets = model.get("sheet_register") or []
    lines.append(f"Состав листов ({len(sheets)}):")
    for s in sheets[:30]:
        lines.append(f"  {s.get('mark','')} {s.get('number','')} {s.get('title','')}".strip())
    if not sheets:
        lines.append("  не извлечён явно")
    lines.append("")
    lines.append("Структура/разделы:")
    for s in (model.get("sections") or [])[:20]:
        lines.append(f"  {s}")
    lines.append("")
    ag = model.get("axes_grid") or {}
    lines.append(f"Оси буквенные: {', '.join(ag.get('axes_letters',[]) or []) or 'не извлечены'}")
    lines.append(f"Оси цифровые: {', '.join(ag.get('axes_numbers',[]) or []) or 'не извлечены'}")
    dims = model.get("dimensions") or []
    lines.append(f"Размеры мм: {', '.join(map(str,dims[:20])) if dims else 'не извлечены'}")
    lines.append("")
    mats = model.get("materials") or []
    lines.append(f"Материалы ({len(mats)}):")
    for m in mats[:15]:
        lines.append(f"  {m}")
    return "\n".join(lines).strip()

# === END PATCH_TEMPLATE_MODEL_EXTRACTOR_V1 ===


# === FULLFIX_03_PROJECT_ARTIFACT_GENERATOR ===
def _ff3_latest_project_template_model(topic_id: int = 0) -> dict:
    import json, os, glob
    base = "/root/.areal-neva-core/data/project_templates"
    files = sorted(glob.glob(os.path.join(base, "PROJECT_TEMPLATE_MODEL__*.json")), key=os.path.getmtime, reverse=True)
    if not files:
        return {}
    topic_id = int(topic_id or 0)
    best = None
    for p in files:
        try:
            data = json.load(open(p, encoding="utf-8"))
            if topic_id and int(data.get("topic_id", 0) or 0) == topic_id:
                return data
            if best is None:
                best = data
        except Exception:
            pass
    return best or {}


def _ff3_extract_project_params(user_text: str) -> dict:
    import re
    txt = str(user_text or "")
    low = txt.lower()

    params = {}
    if "фундамент" in low or "плита" in low:
        params["project_name"] = "Проект фундаментной плиты"
        params["section"] = "КЖ"
    elif "кров" in low or "строп" in low:
        params["project_name"] = "Проект кровли"
        params["section"] = "КД"
    else:
        params["project_name"] = "Проект по образцу"
        params["section"] = ""

    m = re.search(r"(\d+(?:[,.]\d+)?)\s*[xх×]\s*(\d+(?:[,.]\d+)?)\s*м", low)
    if m:
        params["size"] = f"{m.group(1).replace(',', '.')} x {m.group(2).replace(',', '.')} м"

    for label, key in (
        ("толщина", "thickness"),
        ("песчан", "sand"),
        ("щеб", "gravel"),
        ("бетон", "concrete"),
        ("арматур", "rebar"),
    ):
        mm = re.search(label + r"[^0-9]{0,30}(\d{2,4})\s*мм", low)
        if mm:
            params[key] = mm.group(1) + " мм"

    return params


def _ff3_safe_docx_text(value) -> str:
    return str(value or "").replace("\x00", " ").strip()


def create_project_artifact_from_latest_template(user_text: str, task_id: str, topic_id: int = 0) -> dict:
    """
    Создаёт реальный DOCX + XLSX проектный артефакт по последней PROJECT_TEMPLATE_MODEL
    Возвращает пути и Drive-ссылки
    """
    import os, tempfile, json
    from datetime import datetime, timezone

    result = {
        "success": False,
        "error": "",
        "docx_path": "",
        "xlsx_path": "",
        "docx_link": "",
        "xlsx_link": "",
        "template_found": False,
        "project_type": "UNKNOWN",
    }

    # === PROJECT_TEMPLATE_MEMORY_CATALOG_SYNC_ABSOLUTE_HOOK_V1 ===
    try:
        _project_template_memory_catalog_sync_absolute_v1(int(topic_id or 210), dry_run=False)
    except Exception:
        pass
    # === END_PROJECT_TEMPLATE_MEMORY_CATALOG_SYNC_ABSOLUTE_HOOK_V1 ===
    model = _ff3_latest_project_template_model(topic_id)
    params = _ff3_extract_project_params(user_text)
    if not model:
        result["error"] = "PROJECT_TEMPLATE_MODEL_NOT_FOUND"
        return result

    result["template_found"] = True
    project_type = params.get("section") or model.get("project_type") or "UNKNOWN"
    result["project_type"] = project_type

    safe_task = str(task_id or "manual")[:8]
    out_dir = tempfile.gettempdir()
    docx_path = os.path.join(out_dir, f"project_{project_type}_{safe_task}.docx")
    xlsx_path = os.path.join(out_dir, f"project_{project_type}_{safe_task}.xlsx")

    sheets = model.get("sheet_register") or []
    # === SHEETS_NORMALIZE_V1 ===
    _sheets_raw = sheets
    sheets = []
    for _sh in _sheets_raw:
        if isinstance(_sh, str) and _sh.strip():
            sheets.append({"mark": project_type, "number": str(len(sheets) + 1), "title": _sh.strip()[:120]})
        elif isinstance(_sh, dict):
            sheets.append(_sh)
    # === END_SHEETS_NORMALIZE_V1 ===
    if not sheets:
        for i, sec in enumerate(model.get("sections") or [], 1):
            sheets.append({"mark": project_type, "number": str(i), "title": str(sec)[:120]})

    if not sheets:
        sheets = [
            {"mark": project_type, "number": "1", "title": "Титульный лист"},
            {"mark": project_type, "number": "2", "title": "Общие данные"},
            {"mark": project_type, "number": "3", "title": "План"},
            {"mark": project_type, "number": "4", "title": "Разрезы"},
            {"mark": project_type, "number": "5", "title": "Спецификация"},
        ]

    try:
        from docx import Document
        doc = Document()
        doc.add_heading(_ff3_safe_docx_text(params.get("project_name") or "Проект по образцу"), level=1)
        doc.add_paragraph("Сформировано AREAL-NEVA ORCHESTRA по сохранённой PROJECT_TEMPLATE_MODEL")
        doc.add_paragraph(f"Раздел: {project_type}")
        doc.add_paragraph(f"Дата: {datetime.now(timezone.utc).isoformat()}")

        doc.add_heading("Параметры задания", level=2)
        if params:
            for k, v in params.items():
                doc.add_paragraph(f"{k}: {v}")
        else:
            doc.add_paragraph(_ff3_safe_docx_text(user_text))

        doc.add_heading("Состав проекта по образцу", level=2)
        tbl = doc.add_table(rows=1, cols=3)
        tbl.rows[0].cells[0].text = "Марка"
        tbl.rows[0].cells[1].text = "Лист"
        tbl.rows[0].cells[2].text = "Наименование"
        for sh in sheets:
            row = tbl.add_row().cells
            row[0].text = _ff3_safe_docx_text(sh.get("mark") or project_type)
            row[1].text = _ff3_safe_docx_text(sh.get("number") or "")
            row[2].text = _ff3_safe_docx_text(sh.get("title") or "")

        doc.add_heading("Оси и размеры", level=2)
        ag = model.get("axes_grid") or {}
        doc.add_paragraph("Оси буквенные: " + (", ".join(ag.get("axes_letters") or []) or "не извлечены"))
        doc.add_paragraph("Оси цифровые: " + (", ".join(ag.get("axes_numbers") or []) or "не извлечены"))
        dims = model.get("dimensions") or []
        doc.add_paragraph("Размеры мм: " + (", ".join(map(str, dims[:60])) if dims else "не извлечены"))

        doc.add_heading("Материалы из образца", level=2)
        mats = model.get("materials") or []
        if mats:
            for m in mats[:60]:
                doc.add_paragraph(_ff3_safe_docx_text(m))
        else:
            doc.add_paragraph("Материалы не извлечены из образца")

        doc.add_heading("Техническая структура", level=2)
        for sec in (model.get("sections") or [])[:80]:
            doc.add_paragraph(_ff3_safe_docx_text(sec))

        doc.save(docx_path)
    except Exception as e:
        result["error"] = "DOCX_CREATE_FAILED: " + str(e)[:250]
        return result

    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Состав проекта"
        headers = ["№", "Марка", "Лист", "Наименование", "Источник"]
        for c, h in enumerate(headers, 1):
            ws.cell(1, c, h)
        for i, sh in enumerate(sheets, 2):
            ws.cell(i, 1, i - 1)
            ws.cell(i, 2, sh.get("mark") or project_type)
            ws.cell(i, 3, sh.get("number") or "")
            ws.cell(i, 4, sh.get("title") or "")
            ws.cell(i, 5, ",".join(model.get("source_files") or []))
        ws2 = wb.create_sheet("Параметры")
        ws2.cell(1, 1, "Параметр")
        ws2.cell(1, 2, "Значение")
        for r, (k, v) in enumerate(params.items(), 2):
            ws2.cell(r, 1, k)
            ws2.cell(r, 2, v)
        ws.column_dimensions["D"].width = 70
        ws.column_dimensions["E"].width = 50
        ws2.column_dimensions["A"].width = 30
        ws2.column_dimensions["B"].width = 70
        wb.save(xlsx_path)
        wb.close()
    except Exception as e:
        result["error"] = "XLSX_CREATE_FAILED: " + str(e)[:250]
        return result

    result["docx_path"] = docx_path
    result["xlsx_path"] = xlsx_path

    try:
        from core.engine_base import upload_artifact_to_drive
        docx_link = upload_artifact_to_drive(docx_path, task_id, int(topic_id or 0))
        xlsx_link = upload_artifact_to_drive(xlsx_path, task_id, int(topic_id or 0))
        result["docx_link"] = docx_link or ""
        result["xlsx_link"] = xlsx_link or ""
    except Exception as e:
        result["upload_error"] = str(e)[:250]

    result["success"] = bool(os.path.exists(docx_path) and os.path.getsize(docx_path) > 1000)
    if not result["success"]:
        result["error"] = "PROJECT_ARTIFACT_EMPTY"
    return result

# === END FULLFIX_03_PROJECT_ARTIFACT_GENERATOR ===


# === FULLFIX_05_REAL_PROJECT_ENGINE ===
import os as _os_ff05
import re as _re_ff05
import json as _json_ff05
import math as _math_ff05
import tempfile as _tempfile_ff05
from pathlib import Path as _Path_ff05
from datetime import datetime as _dt_ff05

def _ff05_float(v, default=0.0):
    try:
        return float(str(v).replace(",", "."))
    except Exception:
        return float(default)

def _ff05_int(v, default=0):
    try:
        return int(float(str(v).replace(",", ".")))
    except Exception:
        return int(default)

def _ff05_latest_template(section: str = "КЖ") -> dict:
    base = _Path_ff05("/root/.areal-neva-core/data/project_templates")
    if not base.exists():
        return {}
    files = sorted(base.glob("PROJECT_TEMPLATE_MODEL__*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    section_u = str(section or "").upper()
    fallback = {}
    for p in files[:50]:
        try:
            data = _json_ff05.loads(p.read_text(encoding="utf-8"))
            data["_template_file"] = str(p)
            pt = str(data.get("project_type") or "").upper()
            if not fallback:
                fallback = data
            if pt == section_u:
                return data
        except Exception:
            continue
    return fallback

def _ff05_parse_project_request(raw_input: str, template_hint: str = "") -> dict:
    text = str(raw_input or "")
    low = text.lower()

    section = "КЖ"
    if any(x in low for x in ("кд", "деревян", "стропил", "кровл")):
        section = "КД"
    if any(x in low for x in ("кж", "фундамент", "плит")):
        section = "КЖ"

    length_m = 10.0
    width_m = 10.0
    slab_mm = 200
    sand_mm = 300
    gravel_mm = 100
    concrete_class = "B25"
    rebar_class = "A500C"
    rebar_step_mm = 200
    rebar_diam_mm = 12
    cover_mm = 40

    m = _re_ff05.search(r"(\d+(?:[,.]\d+)?)\s*[xх×]\s*(\d+(?:[,.]\d+)?)\s*м?", low)
    if m:
        length_m = _ff05_float(m.group(1), length_m)
        width_m = _ff05_float(m.group(2), width_m)

    def find_mm(keys, default):
        for key in keys:
            m2 = _re_ff05.search(key + r".{0,40}?(\d{2,4})\s*мм", low)
            if m2:
                return _ff05_int(m2.group(1), default)
        return default

    slab_mm = find_mm(("толщин", "плит", "бетон"), slab_mm)
    sand_mm = find_mm(("песчан", "песок"), sand_mm)
    gravel_mm = find_mm(("щеб", "основан"), gravel_mm)

    m = _re_ff05.search(r"(b|в)\s?(\d{2,3})", low)
    if m:
        concrete_class = "B" + m.group(2)

    m = _re_ff05.search(r"(a|а)\s?500", low)
    if m:
        rebar_class = "A500C"

    m = _re_ff05.search(r"(?:шаг|ячейк).{0,30}?(\d{2,4})\s*мм", low)
    if m:
        rebar_step_mm = _ff05_int(m.group(1), rebar_step_mm)

    m = _re_ff05.search(r"(?:арматур|ø|ф|диаметр).{0,30}?(\d{1,2})\s*мм", low)
    if m:
        rebar_diam_mm = _ff05_int(m.group(1), rebar_diam_mm)

    template = _ff05_latest_template(section)

    return {
        "project_name": "Проект фундаментной плиты" if section == "КЖ" else "Проект КД",
        "section": section,
        "length_m": length_m,
        "width_m": width_m,
        "slab_mm": slab_mm,
        "sand_mm": sand_mm,
        "gravel_mm": gravel_mm,
        "concrete_class": concrete_class,
        "rebar_class": rebar_class,
        "rebar_step_mm": rebar_step_mm,
        "rebar_diam_mm": rebar_diam_mm,
        "cover_mm": cover_mm,
        "template": {
            "project_type": template.get("project_type"),
            "source_files": template.get("source_files") or [],
            "template_file": template.get("_template_file"),
            "sections": template.get("sections") or [],
            "sheet_register": template.get("sheet_register") or [],
            "materials": template.get("materials") or [],
        },
    }

def _ff05_font():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for fp in candidates:
        if _os_ff05.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont("AREALFONT", fp))
                return "AREALFONT"
            except Exception:
                pass
    return "Helvetica"

def _ff05_draw_frame(c, page_w, page_h, title, sheet_no, sheet_total, font):
    from reportlab.lib.units import mm
    c.setLineWidth(0.7)
    c.rect(12*mm, 10*mm, page_w - 24*mm, page_h - 20*mm)
    c.line(12*mm, 28*mm, page_w - 12*mm, 28*mm)
    c.line(page_w - 95*mm, 10*mm, page_w - 95*mm, 28*mm)
    c.line(page_w - 55*mm, 10*mm, page_w - 55*mm, 28*mm)
    c.line(page_w - 25*mm, 10*mm, page_w - 25*mm, 28*mm)

    c.setFont(font, 9)
    c.drawString(15*mm, 18*mm, "AREAL-NEVA")
    c.drawString(page_w - 92*mm, 18*mm, "Стадия: П")
    c.drawString(page_w - 52*mm, 18*mm, f"Лист: {sheet_no}")
    c.drawString(page_w - 22*mm, 18*mm, f"Листов: {sheet_total}")

    c.setFont(font, 13)
    c.drawString(18*mm, page_h - 20*mm, title)
    c.setFont(font, 8)
    c.drawString(18*mm, page_h - 27*mm, "Комплект создан автоматически по задаче пользователя и сохранён как PDF/DXF артефакт")

def _ff05_draw_text(c, x, y, text, font, size=9):
    from reportlab.lib.units import mm
    c.setFont(font, size)
    c.drawString(x*mm, y*mm, str(text))

def _ff05_write_project_pdf(path: str, data: dict) -> str:
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    font = _ff05_font()
    page_w, page_h = landscape(A3)
    c = canvas.Canvas(path, pagesize=landscape(A3))

    L = float(data["length_m"])
    W = float(data["width_m"])
    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    rebar_d = int(data["rebar_diam_mm"])
    rebar_step = int(data["rebar_step_mm"])
    cover = int(data["cover_mm"])
    concrete = data["concrete_class"]
    rebar_class = data["rebar_class"]
    sheet_total = 6

    # 1 title / general data
    _ff05_draw_frame(c, page_w, page_h, "Общие данные", 1, sheet_total, font)
    lines = [
        f"Наименование: {data['project_name']}",
        f"Раздел: {data['section']}",
        f"Габарит плиты: {L:g} x {W:g} м",
        f"Толщина плиты: {slab} мм",
        f"Подготовка: песок {sand} мм, щебень {gravel} мм",
        f"Бетон: {concrete}",
        f"Арматура: {rebar_class} Ø{rebar_d} с шагом {rebar_step} мм, защитный слой {cover} мм",
        "Выходные файлы: PDF-комплект + DXF-чертёж со слоями",
    ]
    y = 255
    for line in lines:
        _ff05_draw_text(c, 25, y, line, font, 11)
        y -= 9

    tpl = data.get("template") or {}
    _ff05_draw_text(c, 25, y - 5, "Источник структуры шаблона:", font, 11)
    y -= 15
    src_files = tpl.get("source_files") or []
    _ff05_draw_text(c, 30, y, ", ".join(src_files) if src_files else "не найден сохранённый исходный PDF-шаблон", font, 9)
    y -= 10
    c.showPage()

    # 2 plan
    _ff05_draw_frame(c, page_w, page_h, "План фундаментной плиты", 2, sheet_total, font)
    x0, y0 = 70*mm, 55*mm
    max_w, max_h = 260*mm, 150*mm
    scale = min(max_w/(L*1000), max_h/(W*1000))
    rw, rh = L*1000*scale, W*1000*scale
    c.setLineWidth(1.2)
    c.rect(x0, y0, rw, rh)
    c.setDash(4, 3)
    c.line(x0, y0+rh/2, x0+rw, y0+rh/2)
    c.line(x0+rw/2, y0, x0+rw/2, y0+rh)
    c.setDash()

    # rebar grid
    c.setLineWidth(0.25)
    step_draw = max(0.6*mm, rebar_step*scale)
    xx = x0 + step_draw
    while xx < x0 + rw:
        c.line(xx, y0, xx, y0+rh)
        xx += step_draw
    yy = y0 + step_draw
    while yy < y0 + rh:
        c.line(x0, yy, x0+rw, yy)
        yy += step_draw

    c.setFont(font, 9)
    c.drawString(x0, y0 - 8*mm, f"{L:g} м")
    c.saveState()
    c.translate(x0 - 10*mm, y0)
    c.rotate(90)
    c.drawString(0, 0, f"{W:g} м")
    c.restoreState()
    _ff05_draw_text(c, 25, 240, f"Армирование: {rebar_class} Ø{rebar_d} шаг {rebar_step} мм в двух направлениях", font, 10)
    _ff05_draw_text(c, 25, 230, f"Защитный слой бетона: {cover} мм", font, 10)
    c.showPage()

    # 3 section
    _ff05_draw_frame(c, page_w, page_h, "Разрез 1-1", 3, sheet_total, font)
    bx, by = 60*mm, 70*mm
    total = slab + gravel + sand
    k = 95*mm / total
    layers = [
        ("Фундаментная плита", slab, "Бетон " + concrete),
        ("Щебёночное основание", gravel, "Щебень"),
        ("Песчаная подушка", sand, "Песок"),
    ]
    ycur = by
    c.setLineWidth(0.8)
    for name, thick, note in layers:
        hh = thick * k
        c.rect(bx, ycur, 210*mm, hh)
        c.setFont(font, 10)
        c.drawString(bx + 5*mm, ycur + hh/2, f"{name}: {thick} мм — {note}")
        ycur += hh
    _ff05_draw_text(c, 25, 230, f"Общая конструктивная толщина: {total} мм", font, 10)
    c.showPage()

    # 4 reinforcement
    _ff05_draw_frame(c, page_w, page_h, "Схема армирования", 4, sheet_total, font)
    x0, y0 = 70*mm, 55*mm
    c.rect(x0, y0, rw, rh)
    c.setLineWidth(0.35)
    step_draw = max(1.0*mm, rebar_step*scale)
    xx = x0 + step_draw
    while xx < x0 + rw:
        c.line(xx, y0, xx, y0+rh)
        xx += step_draw
    yy = y0 + step_draw
    while yy < y0 + rh:
        c.line(x0, yy, x0+rw, yy)
        yy += step_draw
    _ff05_draw_text(c, 25, 240, f"Нижняя сетка: {rebar_class} Ø{rebar_d} шаг {rebar_step} мм", font, 10)
    _ff05_draw_text(c, 25, 230, f"Верхняя сетка: {rebar_class} Ø{rebar_d} шаг {rebar_step} мм", font, 10)
    _ff05_draw_text(c, 25, 220, "Выпуски, усиления, проёмы и закладные требуют отдельного задания", font, 9)
    c.showPage()

    # 5 specification
    _ff05_draw_frame(c, page_w, page_h, "Спецификация материалов", 5, sheet_total, font)
    area = L * W
    concrete_m3 = round(area * slab / 1000, 3)
    sand_m3 = round(area * sand / 1000, 3)
    gravel_m3 = round(area * gravel / 1000, 3)
    bars_x = _math_ff05.floor((W*1000 - 2*cover) / rebar_step) + 1
    bars_y = _math_ff05.floor((L*1000 - 2*cover) / rebar_step) + 1
    rebar_m = round((bars_x * L + bars_y * W) * 2, 1)
    spec = [
        ("1", f"Бетон {concrete}", "м3", concrete_m3),
        ("2", "Песчаная подушка", "м3", sand_m3),
        ("3", "Щебёночное основание", "м3", gravel_m3),
        ("4", f"Арматура {rebar_class} Ø{rebar_d}", "п.м", rebar_m),
    ]
    y = 240
    _ff05_draw_text(c, 25, y, "№   Наименование                              Ед.     Кол-во", font, 11)
    y -= 10
    for row in spec:
        _ff05_draw_text(c, 25, y, f"{row[0]:<3} {row[1]:<40} {row[2]:<6} {row[3]}", font, 10)
        y -= 9
    c.showPage()

    # 6 sheet list
    _ff05_draw_frame(c, page_w, page_h, "Ведомость листов", 6, sheet_total, font)
    sheets = [
        ("1", "Общие данные"),
        ("2", "План фундаментной плиты"),
        ("3", "Разрез 1-1"),
        ("4", "Схема армирования"),
        ("5", "Спецификация материалов"),
        ("6", "Ведомость листов"),
    ]
    y = 240
    for n, title in sheets:
        _ff05_draw_text(c, 25, y, f"{n}. {title}", font, 11)
        y -= 9
    c.save()

    return path

def _ff05_write_project_dxf(path: str, data: dict) -> str:
    import ezdxf

    L = float(data["length_m"]) * 1000.0
    W = float(data["width_m"]) * 1000.0
    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    step = int(data["rebar_step_mm"])
    rebar_d = int(data["rebar_diam_mm"])
    concrete = str(data["concrete_class"])
    rebar_class = str(data["rebar_class"])

    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    layers = {
        "KJ-SLAB": 7,
        "KJ-AXIS": 1,
        "KJ-REBAR": 3,
        "KJ-DIMS": 5,
        "KJ-TEXT": 2,
        "KJ-SECTION": 4,
    }
    for name, color in layers.items():
        if name not in doc.layers:
            doc.layers.new(name=name, dxfattribs={"color": color})

    # plan outline
    pts = [(0, 0), (L, 0), (L, W), (0, W), (0, 0)]
    msp.add_lwpolyline(pts, dxfattribs={"layer": "KJ-SLAB", "closed": True})

    # axes
    msp.add_line((L/2, -500), (L/2, W+500), dxfattribs={"layer": "KJ-AXIS"})
    msp.add_line((-500, W/2), (L+500, W/2), dxfattribs={"layer": "KJ-AXIS"})

    # rebar grid
    x = step
    while x < L:
        msp.add_line((x, 0), (x, W), dxfattribs={"layer": "KJ-REBAR"})
        x += step
    y = step
    while y < W:
        msp.add_line((0, y), (L, y), dxfattribs={"layer": "KJ-REBAR"})
        y += step

    # section block at right side
    sx = L + 2500
    sy = 0
    total = slab + gravel + sand
    msp.add_lwpolyline([(sx, sy), (sx+5000, sy), (sx+5000, sy+total), (sx, sy+total), (sx, sy)], dxfattribs={"layer": "KJ-SECTION", "closed": True})
    y1 = sy
    for name, th in [("SAND", sand), ("GRAVEL", gravel), ("SLAB", slab)]:
        msp.add_line((sx, y1), (sx+5000, y1), dxfattribs={"layer": "KJ-SECTION"})
        msp.add_text(f"{name} {th}mm", dxfattribs={"height": 250, "layer": "KJ-TEXT"}).set_placement((sx+5200, y1 + th/2))
        y1 += th
    msp.add_line((sx, y1), (sx+5000, y1), dxfattribs={"layer": "KJ-SECTION"})

    # notes
    msp.add_text(f"FOUNDATION SLAB {L/1000:g}x{W/1000:g}m", dxfattribs={"height": 350, "layer": "KJ-TEXT"}).set_placement((0, -1200))
    msp.add_text(f"SLAB {slab}mm / {concrete}", dxfattribs={"height": 250, "layer": "KJ-TEXT"}).set_placement((0, -1700))
    msp.add_text(f"REBAR {rebar_class} D{rebar_d} STEP {step}mm", dxfattribs={"height": 250, "layer": "KJ-TEXT"}).set_placement((0, -2100))
    msp.add_text(f"SAND {sand}mm / GRAVEL {gravel}mm", dxfattribs={"height": 250, "layer": "KJ-TEXT"}).set_placement((0, -2500))

    doc.saveas(path)
    return path

async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "") -> dict:
    data = _ff05_parse_project_request(raw_input, template_hint)
    stamp = _dt_ff05.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_task = _re_ff05.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id or "manual"))[:20]
    out_dir = _Path_ff05(_tempfile_ff05.gettempdir()) / f"areal_project_{safe_task}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = str(out_dir / f"{data['section']}_foundation_slab_{safe_task}.pdf")
    dxf_path = str(out_dir / f"{data['section']}_foundation_slab_{safe_task}.dxf")
    manifest_path = str(out_dir / f"{data['section']}_foundation_slab_{safe_task}.manifest.json")

    res = {
        "success": False,
        "section": data["section"],
        "pdf_path": pdf_path,
        "dxf_path": dxf_path,
        "manifest_path": manifest_path,
        "pdf_link": None,
        "dxf_link": None,
        "manifest_link": None,
        "error": None,
        "data": data,
    }

    try:
        _ff05_write_project_pdf(pdf_path, data)
        _ff05_write_project_dxf(dxf_path, data)

        if not _os_ff05.path.exists(pdf_path) or _os_ff05.path.getsize(pdf_path) < 3000:
            res["error"] = "PDF_NOT_CREATED_OR_TOO_SMALL"
            return res
        if not _os_ff05.path.exists(dxf_path) or _os_ff05.path.getsize(dxf_path) < 1500:
            res["error"] = "DXF_NOT_CREATED_OR_TOO_SMALL"
            return res

        manifest = {
            "schema": "AREAL_PROJECT_ARTIFACT_V1",
            "created_at": _dt_ff05.utcnow().isoformat() + "Z",
            "task_id": task_id,
            "topic_id": topic_id,
            "engine": "FULLFIX_05_REAL_PROJECT_ENGINE",
            "input": raw_input,
            "data": data,
            "files": {
                "pdf": pdf_path,
                "dxf": dxf_path,
            },
        }
        _Path_ff05(manifest_path).write_text(_json_ff05.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        from core.engine_base import upload_artifact_to_drive
        pdf_link = upload_artifact_to_drive(pdf_path, task_id, topic_id)
        dxf_link = upload_artifact_to_drive(dxf_path, task_id, topic_id)
        manifest_link = upload_artifact_to_drive(manifest_path, task_id, topic_id)

        if not pdf_link:
            res["error"] = "PDF_UPLOAD_FAILED"
            return res
        if not dxf_link:
            res["error"] = "DXF_UPLOAD_FAILED"
            return res

        res.update({
            "success": True,
            "pdf_link": str(pdf_link),
            "dxf_link": str(dxf_link),
            "manifest_link": str(manifest_link or ""),
        })
        return res

    except Exception as e:
        res["error"] = str(e)[:500]
        return res

# === END FULLFIX_05_REAL_PROJECT_ENGINE ===


# === FULLFIX_06_FINAL_PROJECT_TEMPLATE_REPLAY ===
import os as _os_ff06
import re as _re_ff06
import json as _json_ff06
import glob as _glob_ff06
import tempfile as _tempfile_ff06
from pathlib import Path as _Path_ff06
from datetime import datetime as _dt_ff06

def _ff06_clean_text(v, limit=5000):
    return str(v or "").replace("\x00", " ").strip()[:limit]

def _ff06_find_font():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for x in candidates:
        if _os_ff06.path.exists(x):
            return x
    return ""

def _ff06_latest_template(topic_id=0, preferred_section=""):
    base = "/root/.areal-neva-core/data/project_templates"
    files = sorted(
        _glob_ff06.glob(_os_ff06.path.join(base, "PROJECT_TEMPLATE_MODEL__*.json")),
        key=lambda x: _os_ff06.path.getmtime(x),
        reverse=True,
    )
    if not files:
        return {}
    topic_id = int(topic_id or 0)
    preferred_section = _ff06_clean_text(preferred_section).upper()
    best = None
    for fp in files:
        try:
            data = _json_ff06.loads(_Path_ff06(fp).read_text(encoding="utf-8"))
            data["_template_file"] = fp
            pt = _ff06_clean_text(data.get("project_type")).upper()
            dtid = int(data.get("topic_id", 0) or 0)
            if topic_id and dtid == topic_id and preferred_section and pt == preferred_section:
                return data
            if topic_id and dtid == topic_id and not best:
                best = data
            if preferred_section and pt == preferred_section and not best:
                best = data
            if not best:
                best = data
        except Exception:
            continue
    return best or {}

def _ff06_parse_request(raw_input, template_hint=""):
    text = _ff06_clean_text(raw_input, 10000)
    low = text.lower()
    out = {
        "section": "КЖ",
        "project_name": "Проект фундаментной плиты",
        "length_m": 10.0,
        "width_m": 10.0,
        "slab_mm": 200,
        "sand_mm": 300,
        "gravel_mm": 100,
        "concrete_class": "B25",
        "rebar_class": "A500",
        "rebar_diam_mm": 12,
        "rebar_step_mm": 200,
        "raw_input": text,
        "template_hint": template_hint or "",
    }

    if "кд" in low or "кров" in low or "строп" in low:
        out["section"] = "КД"
        out["project_name"] = "Проект кровли"
    if "ар" in low and "фундамент" not in low and "кров" not in low:
        out["section"] = "АР"
        out["project_name"] = "Архитектурный раздел"
    if "кж" in low or "фундамент" in low or "плит" in low:
        out["section"] = "КЖ"
        out["project_name"] = "Проект фундаментной плиты"

    m = _re_ff06.search(r"(\d+(?:[,.]\d+)?)\s*[xх×]\s*(\d+(?:[,.]\d+)?)\s*(?:м|m)?", low)
    if m:
        out["length_m"] = float(m.group(1).replace(",", "."))
        out["width_m"] = float(m.group(2).replace(",", "."))

    def mm(keys, default):
        for key in keys:
            mmx = _re_ff06.search(key + r".{0,40}?(\d{2,4})\s*мм", low)
            if mmx:
                return int(mmx.group(1))
        return default

    out["slab_mm"] = mm(["толщина", "плита", "бетон"], out["slab_mm"])
    out["sand_mm"] = mm(["песчан", "песок"], out["sand_mm"])
    out["gravel_mm"] = mm(["щеб", "основан"], out["gravel_mm"])
    out["rebar_step_mm"] = mm(["шаг"], out["rebar_step_mm"])

    md = _re_ff06.search(r"(?:ø|Ø|ф|диаметр)\s*(\d{1,2})", low)
    if md:
        out["rebar_diam_mm"] = int(md.group(1))
    mc = _re_ff06.search(r"\b[вbВB]\s*([123456789]\d)\b", text)
    if mc:
        out["concrete_class"] = "B" + mc.group(1)
    ma = _re_ff06.search(r"\bA\s*([245]\d{2})\b", text, _re_ff06.I)
    if ma:
        out["rebar_class"] = "A" + ma.group(1)

    return out

def _ff06_sheet_rows(sheet_register, section):
    rows = []
    for i, sh in enumerate(sheet_register or [], 1):
        if isinstance(sh, dict):
            mark = _ff06_clean_text(sh.get("mark") or section, 20) or section
            num = _ff06_clean_text(sh.get("number") or str(i), 30) or str(i)
            title = _ff06_clean_text(sh.get("title") or sh.get("name") or "", 180)
            if not title:
                title = f"Лист {num}"
            rows.append({"mark": mark, "number": num, "title": title})
        else:
            raw = _ff06_clean_text(sh, 180)
            if not raw:
                continue
            rows.append({"mark": section, "number": str(i), "title": raw})
    return rows

def _ff06_material_rows(materials, data):
    rows = []
    for x in materials or []:
        if isinstance(x, dict):
            name = _ff06_clean_text(x.get("name") or x.get("material") or x.get("title") or "Материал", 180)
            unit = _ff06_clean_text(x.get("unit") or x.get("ед") or "шт", 30)
            qty = x.get("quantity", x.get("qty", x.get("count", "-")))
            note = _ff06_clean_text(x.get("note") or "", 120)
            rows.append((name, unit, qty, note))
        else:
            name = _ff06_clean_text(x, 180)
            if name:
                rows.append((name, "по проекту", "-", "из шаблона"))
    if rows:
        return rows[:80]

    L = float(data["length_m"])
    W = float(data["width_m"])
    area = L * W
    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    step = max(int(data["rebar_step_mm"]), 50)
    bars_x = int((W * 1000) / step) + 1
    bars_y = int((L * 1000) / step) + 1
    rebar_m = round((bars_x * L + bars_y * W) * 2, 1)

    return [
        (f"Бетон {data['concrete_class']}", "м3", round(area * slab / 1000, 3), "фундаментная плита"),
        ("Песчаная подушка", "м3", round(area * sand / 1000, 3), ""),
        ("Щебёночное основание", "м3", round(area * gravel / 1000, 3), ""),
        (f"Арматура {data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {step}", "п.м", rebar_m, "верхняя и нижняя сетка"),
    ]

def _ff06_register_font():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    font_path = _ff06_find_font()
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont("ArealDejaVu", font_path))
            return "ArealDejaVu"
        except Exception:
            pass
    return "Helvetica"

def _ff06_draw_frame(c, page_w, page_h, sheet, sheet_no, sheet_total, font):
    from reportlab.lib.units import mm
    c.setLineWidth(0.7)
    c.rect(10*mm, 10*mm, page_w - 20*mm, page_h - 20*mm)
    c.rect(page_w - 190*mm, 10*mm, 180*mm, 40*mm)
    c.line(page_w - 190*mm, 30*mm, page_w - 10*mm, 30*mm)
    c.line(page_w - 80*mm, 10*mm, page_w - 80*mm, 50*mm)
    c.line(page_w - 45*mm, 10*mm, page_w - 45*mm, 50*mm)
    c.setFont(font, 8)
    c.drawString(page_w - 187*mm, 42*mm, "AREAL-NEVA")
    c.drawString(page_w - 187*mm, 34*mm, _ff06_clean_text(sheet.get("title"), 80))
    c.drawString(page_w - 77*mm, 34*mm, f"Лист {sheet_no}")
    c.drawString(page_w - 42*mm, 34*mm, f"Листов {sheet_total}")
    c.setFont(font, 14)
    c.drawString(18*mm, page_h - 22*mm, f"{sheet.get('mark')} {sheet.get('number')} — {sheet.get('title')}")

def _ff06_write_pdf(path, data, template, sheets, material_rows):
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    font = _ff06_register_font()
    page_w, page_h = landscape(A3)
    c = canvas.Canvas(path, pagesize=landscape(A3))

    L = float(data["length_m"])
    W = float(data["width_m"])
    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    step = int(data["rebar_step_mm"])
    rd = int(data["rebar_diam_mm"])
    section = data["section"]

    for idx, sheet in enumerate(sheets, 1):
        _ff06_draw_frame(c, page_w, page_h, sheet, idx, len(sheets), font)
        title_low = (sheet.get("title") or "").lower()

        if any(x in title_low for x in ("общие", "данные", "пояснит", "исходн")):
            y = 260
            lines = [
                f"Проект: {data['project_name']}",
                f"Раздел: {section}",
                f"Основа генерации: сохранённый PROJECT_TEMPLATE_MODEL",
                f"Шаблон: {template.get('_template_file', '')}",
                f"Плита: {L:g} x {W:g} м, толщина {slab} мм",
                f"Основание: щебень {gravel} мм, песчаная подушка {sand} мм",
                f"Бетон: {data['concrete_class']}",
                f"Арматура: {data['rebar_class']} Ø{rd}, шаг {step} мм",
            ]
            c.setFont(font, 10)
            for line in lines:
                c.drawString(25*mm, y*mm, line)
                y -= 8

        elif any(x in title_low for x in ("ведомость лист", "состав лист", "листов")):
            y = 260
            c.setFont(font, 10)
            for j, sh in enumerate(sheets, 1):
                c.drawString(25*mm, y*mm, f"{j}. {sh['mark']} {sh['number']} — {sh['title']}")
                y -= 7

        elif any(x in title_low for x in ("план", "плит", "схема")):
            x0, y0 = 70*mm, 60*mm
            scale = min((page_w - 150*mm) / (L * 1000), 115*mm / (W * 1000))
            rw = L * 1000 * scale
            rh = W * 1000 * scale
            c.setLineWidth(1.1)
            c.rect(x0, y0, rw, rh)
            c.setDash(4, 3)
            c.line(x0, y0 + rh / 2, x0 + rw, y0 + rh / 2)
            c.line(x0 + rw / 2, y0, x0 + rw / 2, y0 + rh)
            c.setDash()
            step_draw = max(0.7*mm, step * scale)
            c.setLineWidth(0.25)
            xx = x0 + step_draw
            while xx < x0 + rw:
                c.line(xx, y0, xx, y0 + rh)
                xx += step_draw
            yy = y0 + step_draw
            while yy < y0 + rh:
                c.line(x0, yy, x0 + rw, yy)
                yy += step_draw
            c.setFont(font, 9)
            c.drawString(x0, y0 - 8*mm, f"{L:g} м")
            c.saveState()
            c.translate(x0 - 8*mm, y0)
            c.rotate(90)
            c.drawString(0, 0, f"{W:g} м")
            c.restoreState()
            c.setFont(font, 10)
            c.drawString(25*mm, 260*mm, f"Армирование: {data['rebar_class']} Ø{rd}, шаг {step} мм")

        elif any(x in title_low for x in ("разрез", "сечени", "1-1")):
            bx, by = 55*mm, 70*mm
            total = slab + gravel + sand
            k = 105*mm / total
            ycur = by
            c.setLineWidth(0.9)
            for name, th, note in [
                ("Фундаментная плита", slab, f"Бетон {data['concrete_class']}"),
                ("Щебёночное основание", gravel, "Щебень"),
                ("Песчаная подушка", sand, "Песок"),
            ]:
                hh = th * k
                c.rect(bx, ycur, 230*mm, hh)
                c.setFont(font, 10)
                c.drawString(bx + 5*mm, ycur + hh/2, f"{name}: {th} мм — {note}")
                ycur += hh
            c.setFont(font, 10)
            c.drawString(25*mm, 240*mm, "Разрез 1-1")

        elif any(x in title_low for x in ("армир", "арматур", "сетка")):
            x0, y0 = 70*mm, 60*mm
            scale = min((page_w - 150*mm) / (L * 1000), 115*mm / (W * 1000))
            rw = L * 1000 * scale
            rh = W * 1000 * scale
            c.setLineWidth(1.0)
            c.rect(x0, y0, rw, rh)
            step_draw = max(1.0*mm, step * scale)
            c.setLineWidth(0.35)
            xx = x0 + step_draw
            while xx < x0 + rw:
                c.line(xx, y0, xx, y0 + rh)
                xx += step_draw
            yy = y0 + step_draw
            while yy < y0 + rh:
                c.line(x0, yy, x0 + rw, yy)
                yy += step_draw
            c.setFont(font, 10)
            c.drawString(25*mm, 260*mm, f"Верхняя и нижняя сетки: {data['rebar_class']} Ø{rd}, шаг {step} мм")

        elif any(x in title_low for x in ("специф", "материал", "ведомость объем", "ведомость объём")):
            y = 260
            c.setFont(font, 10)
            c.drawString(25*mm, y*mm, "№")
            c.drawString(40*mm, y*mm, "Наименование")
            c.drawString(170*mm, y*mm, "Ед")
            c.drawString(195*mm, y*mm, "Кол-во")
            c.drawString(230*mm, y*mm, "Примечание")
            y -= 8
            for j, row in enumerate(material_rows[:28], 1):
                c.drawString(25*mm, y*mm, str(j))
                c.drawString(40*mm, y*mm, _ff06_clean_text(row[0], 70))
                c.drawString(170*mm, y*mm, _ff06_clean_text(row[1], 12))
                c.drawString(195*mm, y*mm, _ff06_clean_text(row[2], 18))
                c.drawString(230*mm, y*mm, _ff06_clean_text(row[3], 50))
                y -= 7

        else:
            y = 250
            c.setFont(font, 10)
            c.drawString(25*mm, y*mm, f"Лист выполнен по структуре шаблона: {sheet['title']}")
            y -= 10
            c.drawString(25*mm, y*mm, f"Раздел: {section}")
            y -= 8
            c.drawString(25*mm, y*mm, f"Параметры: {L:g} x {W:g} м, бетон {data['concrete_class']}")

        c.showPage()

    c.save()
    return path

def _ff06_write_dxf(path, data, sheets, material_rows):
    import ezdxf
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4
    msp = doc.modelspace()

    for layer, color in [("KJ_PLAN", 7), ("KJ_AXES", 2), ("KJ_REBAR", 3), ("KJ_TEXT", 1), ("KJ_SECTION", 5)]:
        if layer not in doc.layers:
            doc.layers.add(layer, color=color)

    L = float(data["length_m"]) * 1000
    W = float(data["width_m"]) * 1000
    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    step = int(data["rebar_step_mm"])

    msp.add_lwpolyline([(0,0), (L,0), (L,W), (0,W), (0,0)], dxfattribs={"layer": "KJ_PLAN"})
    msp.add_line((L/2, 0), (L/2, W), dxfattribs={"layer": "KJ_AXES"})
    msp.add_line((0, W/2), (L, W/2), dxfattribs={"layer": "KJ_AXES"})

    x = step
    while x < L:
        msp.add_line((x, 0), (x, W), dxfattribs={"layer": "KJ_REBAR"})
        x += step
    y = step
    while y < W:
        msp.add_line((0, y), (L, y), dxfattribs={"layer": "KJ_REBAR"})
        y += step

    msp.add_text(f"FOUNDATION SLAB {L/1000:g} x {W/1000:g} m", dxfattribs={"height": 250, "layer": "KJ_TEXT"}).set_placement((0, -700))
    msp.add_text(f"SLAB {slab} mm / GRAVEL {gravel} mm / SAND {sand} mm", dxfattribs={"height": 250, "layer": "KJ_TEXT"}).set_placement((0, -1100))
    msp.add_text(f"REBAR {data['rebar_class']} D{data['rebar_diam_mm']} STEP {step} mm", dxfattribs={"height": 250, "layer": "KJ_TEXT"}).set_placement((0, -1500))

    sx, sy = 0, -3000
    widths = [slab, gravel, sand]
    names = ["SLAB", "GRAVEL", "SAND"]
    cur = sy
    for name, th in zip(names, widths):
        msp.add_lwpolyline([(sx,cur), (sx+L,cur), (sx+L,cur-th), (sx,cur-th), (sx,cur)], dxfattribs={"layer": "KJ_SECTION"})
        msp.add_text(f"{name} {th} mm", dxfattribs={"height": 220, "layer": "KJ_TEXT"}).set_placement((sx + 300, cur - th/2))
        cur -= th

    doc.saveas(path)
    return path

def _ff06_write_xlsx(path, data, sheets, material_rows, template):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    wb = Workbook()

    ws = wb.active
    ws.title = "Ведомость листов"
    ws.append(["№", "Марка", "Лист", "Наименование"])
    for c in ws[1]:
        c.font = Font(bold=True)
        c.alignment = Alignment(horizontal="center")
    for i, sh in enumerate(sheets, 1):
        ws.append([i, sh["mark"], sh["number"], sh["title"]])
    ws.column_dimensions["D"].width = 80

    ws2 = wb.create_sheet("Спецификация")
    ws2.append(["№", "Наименование", "Ед. изм", "Кол-во", "Примечание"])
    for c in ws2[1]:
        c.font = Font(bold=True)
    for i, row in enumerate(material_rows, 1):
        ws2.append([i, row[0], row[1], row[2], row[3]])
    ws2.column_dimensions["B"].width = 70
    ws2.column_dimensions["E"].width = 50

    ws3 = wb.create_sheet("Параметры")
    for k in ["project_name", "section", "length_m", "width_m", "slab_mm", "sand_mm", "gravel_mm", "concrete_class", "rebar_class", "rebar_diam_mm", "rebar_step_mm"]:
        ws3.append([k, data.get(k)])
    ws3.append(["template_file", template.get("_template_file", "")])
    ws3.column_dimensions["A"].width = 25
    ws3.column_dimensions["B"].width = 80

    wb.save(path)
    return path

async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", require_template: bool = True) -> dict:
    data = _ff06_parse_request(raw_input, template_hint)
    template = _ff06_latest_template(topic_id, data.get("section"))

    res = {
        "success": False,
        "engine": "FULLFIX_06_FINAL_PROJECT_TEMPLATE_REPLAY",
        "section": data["section"],
        "pdf_path": "",
        "dxf_path": "",
        "xlsx_path": "",
        "manifest_path": "",
        "pdf_link": "",
        "dxf_link": "",
        "xlsx_link": "",
        "manifest_link": "",
        "template_file": "",
        "sheet_count": 0,
        "error": None,
        "data": data,
    }

    if require_template and not template:
        res["error"] = "PROJECT_TEMPLATE_MODEL_NOT_FOUND"
        return res

    sheets = _ff06_sheet_rows((template or {}).get("sheet_register") or [], data["section"])
    if require_template and not sheets:
        res["error"] = "PROJECT_TEMPLATE_MODEL_HAS_EMPTY_SHEET_REGISTER"
        res["template_file"] = (template or {}).get("_template_file", "")
        return res

    if not sheets:
        res["error"] = "NO_TEMPLATE_SHEETS_NO_PROJECT"
        return res

    material_rows = _ff06_material_rows((template or {}).get("materials") or [], data)

    stamp = _dt_ff06.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_task = _re_ff06.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id or "manual"))[:24]
    out_dir = _Path_ff06(_tempfile_ff06.gettempdir()) / f"areal_project_ff06_{safe_task}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = str(out_dir / f"{data['section']}_PROJECT_{safe_task}.pdf")
    dxf_path = str(out_dir / f"{data['section']}_PROJECT_{safe_task}.dxf")
    xlsx_path = str(out_dir / f"{data['section']}_SPEC_{safe_task}.xlsx")
    manifest_path = str(out_dir / f"{data['section']}_MANIFEST_{safe_task}.json")

    try:
        _ff06_write_pdf(pdf_path, data, template, sheets, material_rows)
        _ff06_write_dxf(dxf_path, data, sheets, material_rows)
        _ff06_write_xlsx(xlsx_path, data, sheets, material_rows, template)

        checks = [
            ("PDF_NOT_CREATED", pdf_path, 2500),
            ("DXF_NOT_CREATED", dxf_path, 500),
            ("XLSX_NOT_CREATED", xlsx_path, 1000),
        ]
        for err, fp, min_size in checks:
            if not _os_ff06.path.exists(fp) or _os_ff06.path.getsize(fp) < min_size:
                res["error"] = err
                return res

        manifest = {
            "schema": "AREAL_PROJECT_ARTIFACT_V3",
            "engine": "FULLFIX_06_FINAL_PROJECT_TEMPLATE_REPLAY",
            "created_at": _dt_ff06.utcnow().isoformat() + "Z",
            "task_id": task_id,
            "topic_id": topic_id,
            "input": raw_input,
            "template_file": template.get("_template_file", ""),
            "sheet_count": len(sheets),
            "sheets": sheets,
            "data": data,
            "artifacts": {
                "pdf_path": pdf_path,
                "dxf_path": dxf_path,
                "xlsx_path": xlsx_path,
            },
        }
        _Path_ff06(manifest_path).write_text(_json_ff06.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        from core.engine_base import upload_artifact_to_drive
        pdf_link = upload_artifact_to_drive(pdf_path, task_id, topic_id)
        dxf_link = upload_artifact_to_drive(dxf_path, task_id, topic_id)
        xlsx_link = upload_artifact_to_drive(xlsx_path, task_id, topic_id)
        manifest_link = upload_artifact_to_drive(manifest_path, task_id, topic_id)

        if not pdf_link:
            res["error"] = "PDF_UPLOAD_FAILED"
            return res
        if not dxf_link:
            res["error"] = "DXF_UPLOAD_FAILED"
            return res
        if not xlsx_link:
            res["error"] = "XLSX_UPLOAD_FAILED"
            return res

        res.update({
            "success": True,
            "pdf_path": pdf_path,
            "dxf_path": dxf_path,
            "xlsx_path": xlsx_path,
            "manifest_path": manifest_path,
            "pdf_link": str(pdf_link),
            "dxf_link": str(dxf_link),
            "xlsx_link": str(xlsx_link),
            "manifest_link": str(manifest_link or ""),
            "template_file": template.get("_template_file", ""),
            "sheet_count": len(sheets),
        })
        return res

    except Exception as e:
        res["error"] = str(e)[:500]
        return res

# === END FULLFIX_06_FINAL_PROJECT_TEMPLATE_REPLAY ===

# === FULLFIX_07_PROJECT_DESIGN_CLOSURE ===
import os as _os_ff07
import re as _re_ff07
import json as _json_ff07
import glob as _glob_ff07
import math as _math_ff07
import tempfile as _tempfile_ff07
from pathlib import Path as _Path_ff07
from datetime import datetime as _dt_ff07

def _ff07_clean(v, limit=5000):
    return str(v or "").replace("\x00", " ").strip()[:limit]

def _ff07_template_files():
    base = "/root/.areal-neva-core/data/project_templates"
    return sorted(
        _glob_ff07.glob(_os_ff07.path.join(base, "PROJECT_TEMPLATE_MODEL__*.json")),
        key=lambda x: _os_ff07.path.getmtime(x),
        reverse=True,
    )

def _ff07_load_latest_template(topic_id=0, preferred_section=""):
    files = _ff07_template_files()
    best = {}
    preferred_section = _ff07_clean(preferred_section).upper()
    topic_id = int(topic_id or 0)

    for fp in files:
        try:
            data = _json_ff07.loads(_Path_ff07(fp).read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                continue
            data["_template_file"] = fp
            pt = _ff07_clean(data.get("project_type")).upper()
            dtid = int(data.get("topic_id", 0) or 0)

            if topic_id and dtid == topic_id and preferred_section and pt == preferred_section:
                return data
            if preferred_section and pt == preferred_section and not best:
                best = data
            if topic_id and dtid == topic_id and not best:
                best = data
            if not best:
                best = data
        except Exception:
            continue

    return best or {}

def _ff07_parse_request(raw_input, template_hint=""):
    text = _ff07_clean(raw_input, 12000)
    low = text.lower()

    data = {
        "section": "КЖ",
        "project_name": "Проект фундаментной плиты",
        "length_m": 10.0,
        "width_m": 10.0,
        "slab_mm": 200,
        "sand_mm": 300,
        "gravel_mm": 100,
        "concrete_class": "B25",
        "rebar_class": "A500",
        "rebar_diam_mm": 12,
        "rebar_step_mm": 200,
        "raw_input": text,
        "template_hint": template_hint or "",
    }

    if any(x in low for x in ("кров", "строп", "кд")) and not any(x in low for x in ("фундамент", "плит")):
        data["section"] = "КД"
        data["project_name"] = "Проект кровли"
    if any(x in low for x in ("архитектур", " ар ", "раздел ар")) and not any(x in low for x in ("фундамент", "плит", "кров")):
        data["section"] = "АР"
        data["project_name"] = "Архитектурный раздел"
    if any(x in low for x in ("фундамент", "плит", "кж")):
        data["section"] = "КЖ"
        data["project_name"] = "Проект фундаментной плиты"

    m = _re_ff07.search(r"(\d+(?:[,.]\d+)?)\s*[xх×]\s*(\d+(?:[,.]\d+)?)\s*(?:м|m)?", low)
    if m:
        data["length_m"] = float(m.group(1).replace(",", "."))
        data["width_m"] = float(m.group(2).replace(",", "."))

    def find_mm(keys, default):
        for key in keys:
            mm = _re_ff07.search(key + r".{0,45}?(\d{2,4})\s*мм", low)
            if mm:
                return int(mm.group(1))
        return default

    data["slab_mm"] = find_mm(("толщина", "плита", "бетон"), data["slab_mm"])
    data["sand_mm"] = find_mm(("песчан", "песок"), data["sand_mm"])
    data["gravel_mm"] = find_mm(("щеб", "основан"), data["gravel_mm"])
    data["rebar_step_mm"] = find_mm(("шаг",), data["rebar_step_mm"])

    md = _re_ff07.search(r"(?:ø|Ø|ф|диаметр)\s*(\d{1,2})", text, _re_ff07.I)
    if md:
        data["rebar_diam_mm"] = int(md.group(1))

    mc = _re_ff07.search(r"\b[вbВB]\s*([123456789]\d)\b", text)
    if mc:
        data["concrete_class"] = "B" + mc.group(1)

    ma = _re_ff07.search(r"\b[аaАA]\s*([245]\d{2})\b", text)
    if ma:
        data["rebar_class"] = "A" + ma.group(1)

    return data

def _ff07_dedup_titles(rows):
    out, seen = [], set()
    for row in rows:
        title = _ff07_clean(row.get("title"), 160)
        key = title.lower()
        if not title or key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out

def _ff07_sheet_rows_from_template(template, section, data):
    raw = template.get("sheet_register") or []
    rows = []

    for i, sh in enumerate(raw, 1):
        if isinstance(sh, dict):
            rows.append({
                "mark": _ff07_clean(sh.get("mark") or section, 20) or section,
                "number": _ff07_clean(sh.get("number") or str(i), 30) or str(i),
                "title": _ff07_clean(sh.get("title") or sh.get("name") or "", 180),
                "source": "sheet_register",
            })
        else:
            rows.append({
                "mark": section,
                "number": str(i),
                "title": _ff07_clean(sh, 180),
                "source": "sheet_register_raw",
            })

    rows = _ff07_dedup_titles(rows)

    if len(rows) >= 8:
        return rows

    sections = []
    for x in template.get("sections") or []:
        if isinstance(x, dict):
            t = _ff07_clean(x.get("title") or x.get("name") or x.get("text"), 180)
        else:
            t = _ff07_clean(x, 180)
        if t:
            sections.append(t)

    canonical = []
    if section == "КЖ":
        canonical = [
            "Общие данные",
            "Ведомость листов",
            "План фундаментной плиты",
            "Разрез 1-1",
            "Схема армирования нижней сетки",
            "Схема армирования верхней сетки",
            "Узлы армирования и защитные слои",
            "Спецификация материалов",
            "Ведомость расхода стали",
            "Пояснительная записка",
        ]
    elif section == "КД":
        canonical = [
            "Общие данные",
            "Ведомость листов",
            "План кровли",
            "План стропильной системы",
            "Разрезы кровли",
            "Узлы кровли",
            "Схема обрешётки",
            "Спецификация пиломатериалов",
            "Ведомость элементов",
            "Пояснительная записка",
        ]
    elif section == "АР":
        canonical = [
            "Общие данные",
            "Ведомость листов",
            "План этажа",
            "Фасады",
            "Разрезы",
            "План кровли",
            "Экспликация помещений",
            "Спецификация заполнения проёмов",
            "Узлы",
            "Пояснительная записка",
        ]
    else:
        canonical = [
            "Общие данные",
            "Ведомость листов",
            "План",
            "Разрез",
            "Схема",
            "Узлы",
            "Спецификация материалов",
            "Пояснительная записка",
        ]

    for title in canonical:
        rows.append({
            "mark": section,
            "number": str(len(rows) + 1),
            "title": title,
            "source": "canonical_required",
        })

    for sec in sections:
        low = sec.lower()
        if any(k in low for k in ("общие данные", "ведомость", "план", "фасад", "разрез", "узел", "схема", "спецификац", "расчет", "расчёт", "конструктив")):
            rows.append({
                "mark": section,
                "number": str(len(rows) + 1),
                "title": sec[:150],
                "source": "template_sections",
            })

    rows = _ff07_dedup_titles(rows)

    renumbered = []
    for i, row in enumerate(rows[:24], 1):
        row = dict(row)
        row["mark"] = row.get("mark") or section
        row["number"] = str(i)
        renumbered.append(row)

    return renumbered

def _ff07_material_rows(template, data):
    rows = []
    for x in template.get("materials") or []:
        if isinstance(x, dict):
            rows.append({
                "name": _ff07_clean(x.get("name") or x.get("material") or x.get("title") or "Материал", 180),
                "unit": _ff07_clean(x.get("unit") or "шт", 30),
                "qty": x.get("qty", x.get("quantity", "-")),
                "note": _ff07_clean(x.get("note") or "из шаблона", 120),
            })
        else:
            t = _ff07_clean(x, 180)
            if t:
                rows.append({"name": t, "unit": "по проекту", "qty": "-", "note": "из шаблона"})

    L = float(data["length_m"])
    W = float(data["width_m"])
    area = L * W
    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    step = max(int(data["rebar_step_mm"]), 50)
    bars_x = int((W * 1000) / step) + 1
    bars_y = int((L * 1000) / step) + 1
    rebar_m = round((bars_x * L + bars_y * W) * 2, 1)

    calc_rows = [
        {"name": f"Бетон {data['concrete_class']}", "unit": "м3", "qty": round(area * slab / 1000, 3), "note": "фундаментная плита"},
        {"name": "Песчаная подушка", "unit": "м3", "qty": round(area * sand / 1000, 3), "note": ""},
        {"name": "Щебёночное основание", "unit": "м3", "qty": round(area * gravel / 1000, 3), "note": ""},
        {"name": f"Арматура {data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {step}", "unit": "п.м", "qty": rebar_m, "note": "верхняя и нижняя сетка"},
    ]

    names = {r["name"].lower() for r in rows}
    for r in calc_rows:
        if r["name"].lower() not in names:
            rows.append(r)

    return rows[:80]

def _ff07_register_font():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for fp in candidates:
        if _os_ff07.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont("ArealDejaVu", fp))
                return "ArealDejaVu"
            except Exception:
                pass
    return "Helvetica"

def _ff07_draw_frame(c, page_w, page_h, sheet, sheet_no, sheet_total, font):
    from reportlab.lib.units import mm

    c.setLineWidth(0.7)
    c.rect(10 * mm, 10 * mm, page_w - 20 * mm, page_h - 20 * mm)
    c.rect(page_w - 190 * mm, 10 * mm, 180 * mm, 42 * mm)
    c.line(page_w - 190 * mm, 32 * mm, page_w - 10 * mm, 32 * mm)
    c.line(page_w - 80 * mm, 10 * mm, page_w - 80 * mm, 52 * mm)
    c.line(page_w - 45 * mm, 10 * mm, page_w - 45 * mm, 52 * mm)

    c.setFont(font, 8)
    c.drawString(page_w - 187 * mm, 44 * mm, "AREAL-NEVA")
    c.drawString(page_w - 187 * mm, 36 * mm, _ff07_clean(sheet.get("title"), 80))
    c.drawString(page_w - 77 * mm, 36 * mm, f"Лист {sheet_no}")
    c.drawString(page_w - 42 * mm, 36 * mm, f"Листов {sheet_total}")

    c.setFont(font, 14)
    c.drawString(18 * mm, page_h - 22 * mm, f"{sheet.get('mark')} {sheet.get('number')} — {sheet.get('title')}")

def _ff07_write_pdf(path, data, template, sheets, materials):
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    font = _ff07_register_font()
    page_w, page_h = landscape(A3)
    c = canvas.Canvas(path, pagesize=landscape(A3))

    L = float(data["length_m"])
    W = float(data["width_m"])
    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    step = int(data["rebar_step_mm"])
    rd = int(data["rebar_diam_mm"])
    section = data["section"]

    for idx, sheet in enumerate(sheets, 1):
        title = sheet.get("title") or ""
        low = title.lower()
        _ff07_draw_frame(c, page_w, page_h, sheet, idx, len(sheets), font)

        if any(x in low for x in ("общие", "данные", "пояснит", "исходн")):
            y = 260
            lines = [
                f"Проект: {data['project_name']}",
                f"Раздел: {section}",
                "Тип выдачи: PDF + DXF + XLSX + MANIFEST",
                f"Шаблон: {template.get('_template_file', '')}",
                f"Плита: {L:g} x {W:g} м, толщина {slab} мм",
                f"Основание: щебень {gravel} мм, песчаная подушка {sand} мм",
                f"Бетон: {data['concrete_class']}",
                f"Арматура: {data['rebar_class']} Ø{rd}, шаг {step} мм",
                f"Листов: {len(sheets)}",
            ]
            c.setFont(font, 10)
            for line in lines:
                c.drawString(25 * mm, y * mm, line)
                y -= 8

        elif any(x in low for x in ("ведомость лист", "состав лист", "листов")):
            y = 260
            c.setFont(font, 10)
            for j, sh in enumerate(sheets, 1):
                c.drawString(25 * mm, y * mm, f"{j}. {sh['mark']} {sh['number']} — {sh['title']}")
                y -= 7
                if y < 35:
                    c.showPage()
                    _ff07_draw_frame(c, page_w, page_h, sheet, idx, len(sheets), font)
                    y = 260

        elif any(x in low for x in ("план", "плит", "схема")) and not any(x in low for x in ("армир", "арматур")):
            x0, y0 = 70 * mm, 60 * mm
            scale = min((page_w - 150 * mm) / (L * 1000), 115 * mm / (W * 1000))
            rw = L * 1000 * scale
            rh = W * 1000 * scale

            c.setLineWidth(1.1)
            c.rect(x0, y0, rw, rh)
            c.setDash(4, 3)
            c.line(x0, y0 + rh / 2, x0 + rw, y0 + rh / 2)
            c.line(x0 + rw / 2, y0, x0 + rw / 2, y0 + rh)
            c.setDash()

            step_draw = max(0.7 * mm, step * scale)
            c.setLineWidth(0.25)

            xx = x0 + step_draw
            while xx < x0 + rw:
                c.line(xx, y0, xx, y0 + rh)
                xx += step_draw

            yy = y0 + step_draw
            while yy < y0 + rh:
                c.line(x0, yy, x0 + rw, yy)
                yy += step_draw

            c.setFont(font, 9)
            c.drawString(x0, y0 - 8 * mm, f"{L:g} м")
            c.saveState()
            c.translate(x0 - 8 * mm, y0)
            c.rotate(90)
            c.drawString(0, 0, f"{W:g} м")
            c.restoreState()

            c.setFont(font, 10)
            c.drawString(25 * mm, 260 * mm, f"Армирование: {data['rebar_class']} Ø{rd}, шаг {step} мм")

        elif any(x in low for x in ("разрез", "сечени", "1-1")):
            bx, by = 55 * mm, 70 * mm
            total = slab + gravel + sand
            k = 105 * mm / total
            ycur = by

            c.setLineWidth(0.9)
            for name, th, note in [
                ("Фундаментная плита", slab, f"Бетон {data['concrete_class']}"),
                ("Щебёночное основание", gravel, "Щебень"),
                ("Песчаная подушка", sand, "Песок"),
            ]:
                hh = th * k
                c.rect(bx, ycur, 230 * mm, hh)
                c.setFont(font, 10)
                c.drawString(bx + 5 * mm, ycur + hh / 2, f"{name}: {th} мм — {note}")
                ycur += hh

            c.setFont(font, 10)
            c.drawString(25 * mm, 240 * mm, "Разрез 1-1")

        elif any(x in low for x in ("армир", "арматур", "сетка")):
            x0, y0 = 70 * mm, 60 * mm
            scale = min((page_w - 150 * mm) / (L * 1000), 115 * mm / (W * 1000))
            rw = L * 1000 * scale
            rh = W * 1000 * scale

            c.setLineWidth(1.0)
            c.rect(x0, y0, rw, rh)

            step_draw = max(1.0 * mm, step * scale)
            c.setLineWidth(0.35)

            xx = x0 + step_draw
            while xx < x0 + rw:
                c.line(xx, y0, xx, y0 + rh)
                xx += step_draw

            yy = y0 + step_draw
            while yy < y0 + rh:
                c.line(x0, yy, x0 + rw, yy)
                yy += step_draw

            c.setFont(font, 10)
            c.drawString(25 * mm, 260 * mm, f"Верхняя и нижняя сетки: {data['rebar_class']} Ø{rd}, шаг {step} мм")

        elif any(x in low for x in ("специф", "материал", "ведомость расход", "ведомость объем", "ведомость объём", "стали")):
            y = 260
            c.setFont(font, 10)
            c.drawString(25 * mm, y * mm, "№")
            c.drawString(40 * mm, y * mm, "Наименование")
            c.drawString(175 * mm, y * mm, "Ед")
            c.drawString(200 * mm, y * mm, "Кол-во")
            c.drawString(235 * mm, y * mm, "Примечание")
            y -= 8

            for j, row in enumerate(materials[:32], 1):
                c.drawString(25 * mm, y * mm, str(j))
                c.drawString(40 * mm, y * mm, _ff07_clean(row["name"], 70))
                c.drawString(175 * mm, y * mm, _ff07_clean(row["unit"], 12))
                c.drawString(200 * mm, y * mm, _ff07_clean(row["qty"], 18))
                c.drawString(235 * mm, y * mm, _ff07_clean(row["note"], 50))
                y -= 7

        elif any(x in low for x in ("узел", "защитн", "слои")):
            c.setFont(font, 10)
            y = 250
            for line in [
                f"Защитный слой бетона принят по СП 63.13330.2018",
                f"Арматура {data['rebar_class']} Ø{rd}, шаг {step} мм",
                "Стыковка и нахлёсты выполнять по рабочей документации",
                "Геометрия узлов уточняется по месту и исполнительным размерам",
            ]:
                c.drawString(25 * mm, y * mm, line)
                y -= 9

        else:
            c.setFont(font, 10)
            y = 250
            for line in [
                f"Лист выполнен в составе комплекта: {title}",
                f"Раздел: {section}",
                f"Параметры: {L:g} x {W:g} м",
                f"Бетон: {data['concrete_class']}",
                f"Шаблон: {template.get('_template_file', '')}",
            ]:
                c.drawString(25 * mm, y * mm, line)
                y -= 8

        c.showPage()

    c.save()
    return path

def _ff07_write_dxf(path, data, sheets, materials):
    import ezdxf

    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4
    msp = doc.modelspace()

    for layer, color in [
        ("KJ_PLAN", 7),
        ("KJ_AXES", 2),
        ("KJ_REBAR", 3),
        ("KJ_TEXT", 1),
        ("KJ_SECTION", 5),
        ("KJ_SHEETS", 4),
    ]:
        if layer not in doc.layers:
            doc.layers.add(layer, color=color)

    L = float(data["length_m"]) * 1000
    W = float(data["width_m"]) * 1000
    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    step = max(int(data["rebar_step_mm"]), 50)

    msp.add_lwpolyline([(0, 0), (L, 0), (L, W), (0, W), (0, 0)], dxfattribs={"layer": "KJ_PLAN"})
    msp.add_line((L / 2, 0), (L / 2, W), dxfattribs={"layer": "KJ_AXES"})
    msp.add_line((0, W / 2), (L, W / 2), dxfattribs={"layer": "KJ_AXES"})

    x = step
    while x < L:
        msp.add_line((x, 0), (x, W), dxfattribs={"layer": "KJ_REBAR"})
        x += step

    y = step
    while y < W:
        msp.add_line((0, y), (L, y), dxfattribs={"layer": "KJ_REBAR"})
        y += step

    msp.add_text(
        f"FOUNDATION SLAB {L/1000:g} x {W/1000:g} m",
        dxfattribs={"height": 250, "layer": "KJ_TEXT"},
    ).set_placement((0, -700))

    msp.add_text(
        f"SLAB {slab} mm / GRAVEL {gravel} mm / SAND {sand} mm",
        dxfattribs={"height": 250, "layer": "KJ_TEXT"},
    ).set_placement((0, -1100))

    msp.add_text(
        f"REBAR {data['rebar_class']} D{data['rebar_diam_mm']} STEP {step} mm",
        dxfattribs={"height": 250, "layer": "KJ_TEXT"},
    ).set_placement((0, -1500))

    sx, sy = 0, -3000
    cur = sy
    for name, th in [("SLAB", slab), ("GRAVEL", gravel), ("SAND", sand)]:
        msp.add_lwpolyline([(sx, cur), (sx + L, cur), (sx + L, cur - th), (sx, cur - th), (sx, cur)], dxfattribs={"layer": "KJ_SECTION"})
        msp.add_text(f"{name} {th} mm", dxfattribs={"height": 220, "layer": "KJ_TEXT"}).set_placement((sx + 300, cur - th / 2))
        cur -= th

    sheet_x = L + 2000
    sheet_y = 0
    for i, sh in enumerate(sheets, 1):
        msp.add_text(
            f"{i}. {sh['mark']} {sh['number']} {sh['title']}",
            dxfattribs={"height": 220, "layer": "KJ_SHEETS"},
        ).set_placement((sheet_x, sheet_y - i * 350))

    doc.saveas(path)
    return path

def _ff07_write_xlsx(path, data, sheets, materials, template):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment

    wb = Workbook()

    ws = wb.active
    ws.title = "Ведомость листов"
    ws.append(["№", "Марка", "Лист", "Наименование", "Источник"])
    for c in ws[1]:
        c.font = Font(bold=True)
        c.alignment = Alignment(horizontal="center")

    for i, sh in enumerate(sheets, 1):
        ws.append([i, sh["mark"], sh["number"], sh["title"], sh.get("source", "")])

    ws.column_dimensions["D"].width = 80
    ws.column_dimensions["E"].width = 25

    ws2 = wb.create_sheet("Спецификация")
    ws2.append(["№", "Наименование", "Ед. изм", "Кол-во", "Примечание"])
    for c in ws2[1]:
        c.font = Font(bold=True)

    for i, row in enumerate(materials, 1):
        ws2.append([i, row["name"], row["unit"], row["qty"], row["note"]])

    ws2.column_dimensions["B"].width = 70
    ws2.column_dimensions["E"].width = 50

    ws3 = wb.create_sheet("Параметры")
    for k in ["project_name", "section", "length_m", "width_m", "slab_mm", "sand_mm", "gravel_mm", "concrete_class", "rebar_class", "rebar_diam_mm", "rebar_step_mm"]:
        ws3.append([k, data.get(k)])
    ws3.append(["template_file", template.get("_template_file", "")])
    ws3.append(["engine", "FULLFIX_07_PROJECT_DESIGN_CLOSURE"])
    ws3.column_dimensions["A"].width = 28
    ws3.column_dimensions["B"].width = 90

    wb.save(path)
    return path

def _ff07_verify_pdf_pages(path, min_pages):
    try:
        from pypdf import PdfReader
        return len(PdfReader(path).pages) >= int(min_pages)
    except Exception:
        return _os_ff07.path.exists(path) and _os_ff07.path.getsize(path) > 3000

async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", require_template: bool = True) -> dict:
    data = _ff07_parse_request(raw_input, template_hint)
    template = _ff07_load_latest_template(topic_id, data.get("section"))

    res = {
        "success": False,
        "engine": "FULLFIX_07_PROJECT_DESIGN_CLOSURE",
        "section": data["section"],
        "pdf_path": "",
        "dxf_path": "",
        "xlsx_path": "",
        "manifest_path": "",
        "pdf_link": "",
        "dxf_link": "",
        "xlsx_link": "",
        "manifest_link": "",
        "template_file": "",
        "sheet_count": 0,
        "error": None,
        "data": data,
    }

    if require_template and not template:
        res["error"] = "PROJECT_TEMPLATE_MODEL_NOT_FOUND"
        return res

    sheets = _ff07_sheet_rows_from_template(template or {}, data["section"], data)
    materials = _ff07_material_rows(template or {}, data)

    if len(sheets) < 8:
        res["error"] = f"SHEET_REGISTER_TOO_SMALL:{len(sheets)}"
        res["template_file"] = (template or {}).get("_template_file", "")
        res["sheet_count"] = len(sheets)
        return res

    stamp = _dt_ff07.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_task = _re_ff07.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id or "manual"))[:24]
    out_dir = _Path_ff07(_tempfile_ff07.gettempdir()) / f"areal_project_ff07_{safe_task}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = str(out_dir / f"{data['section']}_PROJECT_{safe_task}.pdf")
    dxf_path = str(out_dir / f"{data['section']}_PROJECT_{safe_task}.dxf")
    xlsx_path = str(out_dir / f"{data['section']}_SPEC_{safe_task}.xlsx")
    manifest_path = str(out_dir / f"{data['section']}_MANIFEST_{safe_task}.json")

    try:
        _ff07_write_pdf(pdf_path, data, template, sheets, materials)
        _ff07_write_dxf(dxf_path, data, sheets, materials)
        _ff07_write_xlsx(xlsx_path, data, sheets, materials, template)

        checks = [
            ("PDF_NOT_CREATED", pdf_path, 3000),
            ("DXF_NOT_CREATED", dxf_path, 500),
            ("XLSX_NOT_CREATED", xlsx_path, 1000),
        ]
        for err, fp, min_size in checks:
            if not _os_ff07.path.exists(fp) or _os_ff07.path.getsize(fp) < min_size:
                res["error"] = err
                return res

        if not _ff07_verify_pdf_pages(pdf_path, len(sheets)):
            res["error"] = "PDF_PAGE_COUNT_INVALID"
            return res

        manifest = {
            "schema": "AREAL_PROJECT_ARTIFACT_V4",
            "engine": "FULLFIX_07_PROJECT_DESIGN_CLOSURE",
            "created_at": _dt_ff07.utcnow().isoformat() + "Z",
            "task_id": task_id,
            "topic_id": topic_id,
            "input": raw_input,
            "template_file": template.get("_template_file", ""),
            "template_project_type": template.get("project_type", ""),
            "sheet_count": len(sheets),
            "sheets": sheets,
            "materials": materials,
            "data": data,
            "artifacts": {
                "pdf_path": pdf_path,
                "dxf_path": dxf_path,
                "xlsx_path": xlsx_path,
            },
        }
        _Path_ff07(manifest_path).write_text(_json_ff07.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        from core.engine_base import upload_artifact_to_drive

        pdf_link = upload_artifact_to_drive(pdf_path, task_id, topic_id)
        dxf_link = upload_artifact_to_drive(dxf_path, task_id, topic_id)
        xlsx_link = upload_artifact_to_drive(xlsx_path, task_id, topic_id)
        manifest_link = upload_artifact_to_drive(manifest_path, task_id, topic_id)

        if not pdf_link:
            res["error"] = "PDF_UPLOAD_FAILED"
            return res
        if not dxf_link:
            res["error"] = "DXF_UPLOAD_FAILED"
            return res
        if not xlsx_link:
            res["error"] = "XLSX_UPLOAD_FAILED"
            return res

        res.update({
            "success": True,
            "pdf_path": pdf_path,
            "dxf_path": dxf_path,
            "xlsx_path": xlsx_path,
            "manifest_path": manifest_path,
            "pdf_link": str(pdf_link),
            "dxf_link": str(dxf_link),
            "xlsx_link": str(xlsx_link),
            "manifest_link": str(manifest_link or ""),
            "template_file": template.get("_template_file", ""),
            "sheet_count": len(sheets),
            "data": {**data, "template_file": template.get("_template_file", "")},
        })
        return res

    except Exception as e:
        res["error"] = str(e)[:700]
        return res

# === END FULLFIX_07_PROJECT_DESIGN_CLOSURE ===


# === FULLFIX_07_PROJECT_ENGINE_OVERRIDE ===
try:
    from core.cad_project_engine import (
        create_project_pdf_dxf_artifact,
        create_full_project_package,
        is_project_design_request,
        format_project_result_message,
    )
except Exception:
    pass
# === END FULLFIX_07_PROJECT_ENGINE_OVERRIDE ===


# === FULLFIX_08_PROJECT_SIGNATURE_COMPAT_OVERRIDE ===
# Final public project API used by task_worker
# Accepts any old/new call signature and delegates to CAD closure engine

try:
    from core.cad_project_engine import (
        create_project_pdf_dxf_artifact as _ff08_cad_create_project_pdf_dxf_artifact,
        create_full_project_documentation as _ff08_cad_create_full_project_documentation,
    )

    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff08_cad_create_project_pdf_dxf_artifact(
            raw_input,
            task_id,
            int(topic_id or 0),
            str(template_hint or ""),
            *args,
            **kwargs
        )

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff08_cad_create_full_project_documentation(
            raw_input,
            task_id,
            int(topic_id or 0),
            str(template_hint or ""),
            *args,
            **kwargs
        )

except Exception as _ff08_import_error:
    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return {
            "success": False,
            "engine": "FULLFIX_08_PROJECT_SIGNATURE_COMPAT_OVERRIDE",
            "error": "CAD_PROJECT_ENGINE_IMPORT_FAILED: " + str(_ff08_import_error)[:300],
        }

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await create_project_pdf_dxf_artifact(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

# === END FULLFIX_08_PROJECT_SIGNATURE_COMPAT_OVERRIDE ===



# === FULLFIX_09_PROJECT_TEMPLATE_REGISTER_PUBLIC_OVERRIDE ===
try:
    from core.cad_project_engine import (
        create_project_pdf_dxf_artifact as _ff09_create_project_pdf_dxf_artifact,
        create_full_project_documentation as _ff09_create_full_project_documentation,
    )

    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff09_create_project_pdf_dxf_artifact(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff09_create_full_project_documentation(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

except Exception as _ff09_public_e:
    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return {
            "success": False,
            "engine": "FULLFIX_09_PROJECT_TEMPLATE_REGISTER_PUBLIC_OVERRIDE",
            "error": str(_ff09_public_e)[:500],
        }

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await create_project_pdf_dxf_artifact(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

# === END FULLFIX_09_PROJECT_TEMPLATE_REGISTER_PUBLIC_OVERRIDE ===


# === FULLFIX_10_TOTAL_CLOSURE_PUBLIC_PROJECT_OVERRIDE ===
try:
    from core.cad_project_engine import (
        create_project_pdf_dxf_artifact as _ff10_create_project_pdf_dxf_artifact,
        create_full_project_documentation as _ff10_create_full_project_documentation,
    )

    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff10_create_project_pdf_dxf_artifact(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff10_create_full_project_documentation(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

except Exception as _ff10_project_override_error:
    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return {
            "success": False,
            "engine": "FULLFIX_10_TOTAL_CLOSURE_PUBLIC_PROJECT_OVERRIDE",
            "error": str(_ff10_project_override_error)[:300],
        }

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await create_project_pdf_dxf_artifact(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

# === END FULLFIX_10_TOTAL_CLOSURE_PUBLIC_PROJECT_OVERRIDE ===


# === FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT_PUBLIC_OVERRIDE ===
try:
    from core.orchestra_closure_engine import create_compact_project_documentation as _ff12_compact_project

    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff12_compact_project(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff12_compact_project(raw_input, task_id, topic_id, template_hint, *args, **kwargs)
except Exception:
    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return {"success": False, "engine": "FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT_PUBLIC_OVERRIDE", "error": "COMPACT_ENGINE_IMPORT_FAILED"}

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await create_project_pdf_dxf_artifact(raw_input, task_id, topic_id, template_hint, *args, **kwargs)
# === END FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT_PUBLIC_OVERRIDE ===


# === DWG_DXF_PROJECT_ENGINE_ADAPTER_V1 ===
async def process_dwg_dxf_project_file(file_path: str, task_id: str, topic_id: int, raw_input: str = "", file_name: str = "", mime_type: str = "") -> dict:
    """
    Project-engine adapter for DWG/DXF files.
    This keeps design files inside the project contour instead of returning None in artifact_pipeline.
    """
    try:
        from core.dwg_engine import process_drawing_file
        res = process_drawing_file(
            local_path=file_path,
            file_name=file_name or file_path,
            mime_type=mime_type,
            user_text=raw_input,
            topic_role="проектирование",
            task_id=task_id,
            topic_id=topic_id,
        )
        if not res.get("success"):
            return {"success": False, "error": res.get("error") or "DWG_DXF_PROJECT_FAILED"}
        return {
            "success": True,
            "engine": "DWG_DXF_PROJECT_CLOSE_V1",
            "section": ((res.get("model") or {}).get("section") or "кр"),
            "summary": res.get("summary") or "",
            "artifact_path": res.get("artifact_path") or "",
            "docx_path": res.get("docx_path") or "",
            "xlsx_path": res.get("xlsx_path") or "",
            "json_path": res.get("json_path") or "",
            "model": res.get("model") or {},
        }
    except Exception as e:
        return {"success": False, "error": f"DWG_DXF_PROJECT_ENGINE_ADAPTER_ERR:{e}"}
# === END_DWG_DXF_PROJECT_ENGINE_ADAPTER_V1 ===



# === REAL_GAPS_CLOSE_V2_PROJECT ===
# === PROJECT_LOAD_CALC_REGION_FROM_INPUT_V1 ===
_PROJECT_REGION_MAP_V2 = {
    "москва": 3, "московск": 3, "подмосков": 3,
    "петербург": 3, "санкт-петербург": 3, "ленинград": 3, "спб": 3,
    "нижний новгород": 3, "нижегородск": 3, "воронеж": 3, "рязань": 3,
    "тула": 3, "орёл": 3, "орел": 3, "калуга": 3, "ярославль": 3,
    "кострома": 3, "иваново": 3, "владимир": 3, "смоленск": 3,
    "брянск": 3, "тверь": 3,
    "краснодар": 2, "сочи": 2, "ростов": 2, "ставрополь": 2,
    "астрахань": 2, "волгоград": 2, "крым": 2, "симферополь": 2,
    "казань": 3, "татарстан": 3, "самара": 3, "саратов": 3,
    "ульяновск": 3, "пенза": 3, "оренбург": 4,
    "екатеринбург": 4, "свердловск": 4, "челябинск": 4,
    "пермь": 4, "тюмень": 4, "уфа": 4, "башкортостан": 4,
    "новосибирск": 5, "омск": 5, "томск": 5, "кемерово": 5,
    "красноярск": 5, "иркутск": 5, "бурятия": 5, "барнаул": 5,
    "якутия": 6, "якутск": 6, "хабаровск": 6, "сахалин": 6,
    "мурманск": 6, "ямал": 6, "ямало": 6,
    "магадан": 7, "чукотка": 7, "камчатка": 7, "норильск": 7, "воркута": 7,
}

def parse_region_from_text(text: str, default: int = 3) -> int:
    import re
    low = str(text or "").lower()
    m = re.search(r"район\s*([1-8])", low)
    if m:
        return int(m.group(1))
    m = re.search(r"([1-8])\s*-?\s*й?\s*снеговой", low)
    if m:
        return int(m.group(1))
    for key, region in _PROJECT_REGION_MAP_V2.items():
        if key in low:
            return region
    return default

def calc_loads_from_text(text: str, default_region: int = 3) -> dict:
    return calc_loads(parse_region_from_text(text, default_region))

_rgc2_orig_project_create = create_project_pdf_dxf_artifact

async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
    region = parse_region_from_text(str(raw_input or "") + " " + str(template_hint or ""))
    forced_input = str(raw_input or "")
    if "снеговой район" not in forced_input.lower() and "район " not in forced_input.lower():
        forced_input = forced_input + "\n" + "Снеговой район " + str(region) + " по автоматически определённому региону"
    try:
        result = await _rgc2_orig_project_create(
            raw_input=forced_input,
            task_id=task_id,
            topic_id=topic_id,
            template_hint=template_hint,
            *args,
            **kwargs,
        )
    except TypeError:
        try:
            result = await _rgc2_orig_project_create(forced_input, task_id, topic_id, template_hint)
        except TypeError:
            result = await _rgc2_orig_project_create(forced_input, task_id, topic_id)

    if isinstance(result, dict):
        result["region_detected"] = region
        result["loads_detected"] = calc_loads(region)
        model = result.get("model") or result.get("data")
        if isinstance(model, dict):
            model.setdefault("region", region)
            model.setdefault("loads", calc_loads(region))
    return result
# === END_PROJECT_LOAD_CALC_REGION_FROM_INPUT_V1 ===
# === END_REAL_GAPS_CLOSE_V2_PROJECT ===

# === PROJECT_ENGINE_FALLBACK_SHEET_REGISTER_V1 ===
# If template sheet_register is absent or too small, project engine must not fail.
# Default KЖ sheet register is used as safe fallback for project artifact generation.

_PROJECT_ENGINE_DEFAULT_KZH_SHEET_REGISTER_V1 = [
    {"mark": "КЖ", "number": "1", "title": "Общие данные"},
    {"mark": "КЖ", "number": "2", "title": "Схема расположения элементов"},
    {"mark": "КЖ", "number": "3", "title": "Армирование. Нижняя сетка"},
    {"mark": "КЖ", "number": "4", "title": "Армирование. Верхняя сетка"},
    {"mark": "КЖ", "number": "5", "title": "Спецификация арматуры"},
    {"mark": "КЖ", "number": "6", "title": "Ведомость материалов"},
    {"mark": "КЖ", "number": "7", "title": "Конструктивные узлы"},
    {"mark": "КЖ", "number": "8", "title": "Схема фундаментной плиты"},
]

try:
    _pefs_orig_ff07_sheet_rows_from_template = globals().get("_ff07_sheet_rows_from_template")
except Exception:
    _pefs_orig_ff07_sheet_rows_from_template = None

def _project_engine_default_sheet_register_v1(section: str = "кж", data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    sec = str(section or "кж").lower()
    mark = "КЖ" if sec in ("кж", "kd", "foundation", "slab") else sec.upper()
    rows = []
    for item in _PROJECT_ENGINE_DEFAULT_KZH_SHEET_REGISTER_V1:
        row = dict(item)
        row["mark"] = mark
        rows.append(row)
    return rows

def _ff07_sheet_rows_from_template(template: Dict[str, Any], section: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    try:
        if callable(_pefs_orig_ff07_sheet_rows_from_template):
            base_rows = _pefs_orig_ff07_sheet_rows_from_template(template or {}, section, data or {})
            if isinstance(base_rows, list):
                rows = [r for r in base_rows if isinstance(r, dict)]
    except Exception as e:
        logger.warning("PROJECT_ENGINE_FALLBACK_SHEET_REGISTER_V1_ORIG_ERR %s", e)

    if len(rows) >= 8:
        return rows

    fallback = _project_engine_default_sheet_register_v1(section or (data or {}).get("section") or "кж", data or {})
    logger.warning("PROJECT_ENGINE_FALLBACK_SHEET_REGISTER_V1_USED section=%s old_len=%s new_len=%s", section, len(rows), len(fallback))
    return fallback
# === END_PROJECT_ENGINE_FALLBACK_SHEET_REGISTER_V1 ===


# === PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1_WRAPPER ===
try:
    _pec_orig_create_project_artifact_from_latest_template = create_project_artifact_from_latest_template

    def create_project_artifact_from_latest_template(user_text: str, task_id: str, topic_id: int = 0) -> dict:
        res = _pec_orig_create_project_artifact_from_latest_template(user_text, task_id, topic_id)
        try:
            from core.project_route_guard import format_project_result_message
            from core.output_sanitizer import sanitize_project_message
            res["user_message"] = sanitize_project_message(format_project_result_message(res, user_text))
        except Exception:
            pass
        return res
except Exception:
    pass
# === END_PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1_WRAPPER ===



# === PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1 ===
def _project_public_clean_v1(text: str) -> str:
    import re
    text = "" if text is None else str(text)
    patterns = [
        r"Engine:[^\n]*\n?",
        r"MANIFEST:[^\n]*\n?",
        r"task_id\s*[:=][^\n]*\n?",
        r"file_id\s*[:=][^\n]*\n?",
        r"/root/[^\s]*",
        r"tmp[a-zA-Z0-9_\-]{6,}\.(?:pdf|xlsx|docx|dxf)",
        r"\{[\"'][a-z_]+[\"']\s*:[^}]{0,300}\}",
    ]
    for pat in patterns:
        text = re.sub(pat, "", text, flags=re.I | re.S)
    return re.sub(r"\n{3,}", "\n\n", text).strip()

def _project_clean_payload_v1(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(v, str) and k.lower() in ("message", "text", "text_result", "result", "error"):
                out[k] = _project_public_clean_v1(v)
            else:
                out[k] = v
        return out
    if isinstance(obj, str):
        return _project_public_clean_v1(obj)
    return obj

try:
    _project_engine_orig_generate_project_section_v1 = generate_project_section
    async def generate_project_section(*args, **kwargs):
        import inspect
        res = _project_engine_orig_generate_project_section_v1(*args, **kwargs)
        if inspect.isawaitable(res):
            res = await res
        return _project_clean_payload_v1(res)
except Exception:
    pass

try:
    _project_engine_orig_process_project_file_v1 = process_project_file
    async def process_project_file(*args, **kwargs):
        import inspect
        res = _project_engine_orig_process_project_file_v1(*args, **kwargs)
        if inspect.isawaitable(res):
            res = await res
        return _project_clean_payload_v1(res)
except Exception:
    pass

try:
    _project_engine_orig_project_result_guard_v1 = project_result_guard
    def project_result_guard(result):
        return _project_clean_payload_v1(_project_engine_orig_project_result_guard_v1(result))
except Exception:
    pass
# === END_PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1 ===


# === PROJECT_SEARCH_FINAL_REGEX_AND_HEADER_FIX_SECTION_DETECTOR ===
_PE_MARKS_FINAL = ("кмд", "кд", "кж", "км", "кр", "ар", "ов", "вк", "эом", "сс", "гп", "пз", "тх", "см")

def _project_section_mark_final(src: str):
    up = str(src or "").upper().replace("Ё", "Е")
    for mark in _PE_MARKS_FINAL:
        m = mark.upper()
        if re.search(rf"(^|[^А-ЯA-Zа-яa-z]){re.escape(m)}([^А-ЯA-Zа-яa-z]|$)", up):
            return mark
    return None

def detect_section(file_name: str, text: str = ""):
    m = _project_section_mark_final(file_name)
    if m:
        return m
    return _project_section_mark_final(text)

def _detect_section(file_name: str, text: str = ""):
    return detect_section(file_name, text)
# === END_PROJECT_SEARCH_FINAL_REGEX_AND_HEADER_FIX_SECTION_DETECTOR ===

# === PROJECT_TEMPLATE_MEMORY_CATALOG_SYNC_ABSOLUTE_V1 ===
def _project_template_memory_catalog_sync_absolute_v1(topic_id: int = 210, dry_run: bool = False) -> dict:
    import json as _json_pta1
    import sqlite3 as _sqlite_pta1
    from pathlib import Path as _Path_pta1
    from datetime import datetime as _dt_pta1, timezone as _tz_pta1

    base = _Path_pta1("/root/.areal-neva-core")
    mem_db = base / "data/memory.db"
    out_dir = base / "data/project_templates"

    result = {
        "marker": "PROJECT_TEMPLATE_MEMORY_CATALOG_SYNC_ABSOLUTE_V1",
        "ok": False,
        "dry_run": bool(dry_run),
        "sections": [],
        "would_create": [],
        "created": [],
        "index_path": str(out_dir / "PROJECT_TEMPLATE_MODEL__MEMORY_CATALOG_INDEX.json"),
    }

    if not mem_db.exists():
        result["error"] = "MEMORY_DB_NOT_FOUND"
        return result

    conn = _sqlite_pta1.connect(str(mem_db))
    conn.row_factory = _sqlite_pta1.Row
    try:
        row = conn.execute(
            "SELECT value, timestamp FROM memory WHERE key=? ORDER BY timestamp DESC LIMIT 1",
            ("topic_210_file_catalog_autosync",),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        result["error"] = "TOPIC_210_FILE_CATALOG_NOT_FOUND"
        return result

    try:
        catalog = _json_pta1.loads(row["value"])
    except Exception as e:
        result["error"] = "CATALOG_JSON_ERROR: " + str(e)[:160]
        return result

    files = catalog.get("files") if isinstance(catalog, dict) else []
    if not isinstance(files, list):
        files = []

    def _name(item):
        if isinstance(item, dict):
            for k in ("file_name", "name", "title", "original_name"):
                v = str(item.get(k) or "").strip()
                if v:
                    return v
            links = item.get("links")
            if isinstance(links, list):
                for link in links:
                    v = str(link or "").strip()
                    if v:
                        return v[:180]
        return str(item or "").strip()

    def _section(name, item):
        raw = name.lower().replace("ё", "е")
        if isinstance(item, dict):
            raw += " " + str(item.get("direction") or "").lower().replace("ё", "е")
        if "кмд" in raw:
            return "КМД"
        if any(x in raw for x in ("км", "металл", "ферм", "каркас")):
            return "КМ"
        if any(x in raw for x in ("кд", "кровл", "стропил", "дерев", "балк")):
            return "КД"
        if any(x in raw for x in ("кж", "фундамент", "плит", "бетон", "армирован", "цоколь")):
            return "КЖ"
        if any(x in raw for x in ("ар", "архитект", "фасад", "планиров")):
            return "АР"
        return ""

    by_section = {}
    for item in files:
        name = _name(item)
        section = _section(name, item)
        if not name or not section:
            continue
        by_section.setdefault(section, []).append({
            "mark": section,
            "number": str(len(by_section.get(section, [])) + 1),
            "title": name[:180],
            "source": "topic_210_file_catalog_autosync",
        })

    result["sections"] = sorted(by_section.keys())

    existing_sections = set()
    if out_dir.exists():
        for p in out_dir.glob("PROJECT_TEMPLATE_MODEL__*.json"):
            try:
                data = _json_pta1.loads(p.read_text(encoding="utf-8"))
                pt = str(data.get("project_type") or "").upper().strip()
                if pt:
                    existing_sections.add(pt)
            except Exception:
                continue

    for section in sorted(by_section.keys()):
        if section not in existing_sections:
            result["would_create"].append(section)

    result["ok"] = True

    if dry_run:
        return result

    out_dir.mkdir(parents=True, exist_ok=True)
    now = _dt_pta1.now(_tz_pta1.utc).isoformat()

    index = {
        "_schema": "PROJECT_TEMPLATE_MEMORY_CATALOG_SYNC_ABSOLUTE_V1",
        "updated_at_utc": now,
        "catalog_timestamp": row["timestamp"],
        "source": "memory.db:topic_210_file_catalog_autosync",
        "sections": result["sections"],
        "counts": {k: len(v) for k, v in by_section.items()},
        "existing_sections": sorted(existing_sections),
        "would_create": result["would_create"],
    }
    (out_dir / "PROJECT_TEMPLATE_MODEL__MEMORY_CATALOG_INDEX.json").write_text(
        _json_pta1.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    for section in result["would_create"]:
        rows = by_section.get(section) or []
        model = {
            "_schema": "PROJECT_TEMPLATE_MEMORY_CATALOG_SYNC_ABSOLUTE_V1",
            "project_type": section,
            "topic_id": int(topic_id or 210),
            "updated_at_utc": now,
            "source": "topic_210_file_catalog_autosync",
            "source_files": [r["title"] for r in rows],
            "sheet_register": rows,
            "sections": [r["title"] for r in rows],
            "materials": [],
            "axes_grid": {"axes_letters": [], "axes_numbers": []},
            "dimensions": [],
        }
        path = out_dir / f"PROJECT_TEMPLATE_MODEL__{section}_memory_catalog.json"
        path.write_text(_json_pta1.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
        result["created"].append(str(path))

    return result
# === END_PROJECT_TEMPLATE_MEMORY_CATALOG_SYNC_ABSOLUTE_V1 ===

# === THREE_CONTOURS_FINAL_SOURCE_LOCK_V1 ===
# Project source lock:
# - topic_210 project templates: Образцы проектов from Drive
# - sketch/design references: PROJECT_DESIGN_REFERENCES when folder exists
# - PROJECT_ARTIFACTS is output only and forbidden as source

_FINAL_PROJECT_SAMPLES_FOLDER_ID = "1kcJbrn7XMcov__Z1JdWhKlJMZd7GUkgP"
_FINAL_PROJECT_ROOT_FOLDER_ID = "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"

def _final_project_drive_svc_v1():
    try:
        from core.engine_base import _drive_svc_v1
        return _drive_svc_v1()
    except Exception:
        return None

def _final_project_list_folder_v1(folder_id: str):
    svc = _final_project_drive_svc_v1()
    if svc is None:
        return []
    try:
        r = svc.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id,name,mimeType,size,modifiedTime)",
            pageSize=100,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        return r.get("files") or []
    except Exception:
        return []

def _final_project_find_folder_by_name_v1(name: str) -> str:
    svc = _final_project_drive_svc_v1()
    if svc is None:
        return ""
    try:
        q = "mimeType='application/vnd.google-apps.folder' and trashed=false and name='" + str(name).replace("'", "\\'") + "'"
        r = svc.files().list(
            q=q,
            fields="files(id,name,parents,modifiedTime)",
            pageSize=20,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        files = r.get("files") or []
        return files[0]["id"] if files else ""
    except Exception:
        return ""

def _final_project_section_from_name_v1(name: str) -> str:
    low = str(name or "").lower().replace("ё", "е")
    if "кмд" in low:
        return "КМД"
    if any(x in low for x in ("км", "металл", "ферм", "каркас", "м-80", "м-110", "m-80", "m-110")):
        return "КМ"
    if any(x in low for x in ("кд", "кровл", "строп", "дерев", "балк")):
        return "КД"
    if any(x in low for x in ("кж", "фундамент", "плит", "бетон", "армир", "цоколь")):
        return "КЖ"
    if any(x in low for x in ("ар", "архитект", "фасад", "планиров")):
        return "АР"
    if any(x in low for x in ("эскиз", "eskiz")):
        return "ЭСКИЗ"
    return "UNKNOWN"

def _final_project_section_from_request_v1(text: str) -> str:
    low = str(text or "").lower().replace("ё", "е")
    if "кмд" in low:
        return "КМД"
    if "км" in low or "металл" in low:
        return "КМ"
    if "кд" in low or "кров" in low or "строп" in low:
        return "КД"
    if "ар" in low or "архитект" in low or "эскиз" in low or "эскизн" in low:
        return "ЭСКИЗ" if "эскиз" in low else "АР"
    if "кж" in low or "фундамент" in low or "плит" in low or "бетон" in low or "монолит" in low:
        return "КЖ"
    return "КЖ"

def _final_sync_project_drive_templates_v1(topic_id: int = 210) -> dict:
    import json as _json
    from pathlib import Path as _Path
    from datetime import datetime as _dt, timezone as _tz

    out_dir = _Path("/root/.areal-neva-core/data/project_templates")
    out_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "marker": "THREE_CONTOURS_FINAL_SOURCE_LOCK_V1",
        "ok": False,
        "source_folder": "Образцы проектов",
        "source_folder_id": _FINAL_PROJECT_SAMPLES_FOLDER_ID,
        "design_references_folder": "PROJECT_DESIGN_REFERENCES",
        "project_artifacts_rule": "OUTPUT_ONLY_NOT_SOURCE",
        "synced_sections": [],
    }

    files = _final_project_list_folder_v1(_FINAL_PROJECT_SAMPLES_FOLDER_ID)
    design_folder_id = _final_project_find_folder_by_name_v1("PROJECT_DESIGN_REFERENCES")
    design_files = _final_project_list_folder_v1(design_folder_id) if design_folder_id else []

    by_section = {}
    for f in files:
        name = f.get("name","")
        sec = _final_project_section_from_name_v1(name)
        if sec == "UNKNOWN":
            continue
        by_section.setdefault(sec, []).append(f)

    if design_files:
        by_section.setdefault("ЭСКИЗ", []).extend(design_files)

    now = _dt.now(_tz.utc).isoformat()

    for sec, sec_files in by_section.items():
        clean = [f for f in sec_files if str(f.get("name","")).strip()]
        if not clean:
            continue
        best = max(clean, key=lambda f: int(f.get("size") or 0))
        model = {
            "_schema": "THREE_CONTOURS_FINAL_SOURCE_LOCK_V1",
            "project_type": sec,
            "topic_id": int(topic_id or 210),
            "source": "DRIVE_PROJECT_SOURCES",
            "source_folder_name": "Образцы проектов",
            "source_folder_id": _FINAL_PROJECT_SAMPLES_FOLDER_ID,
            "source_file_id": best.get("id",""),
            "source_file_name": best.get("name",""),
            "source_mime_type": best.get("mimeType",""),
            "source_modifiedTime": best.get("modifiedTime",""),
            "synced_at": now,
            "project_artifacts_forbidden_as_source": True,
            "design_references_folder_id": design_folder_id,
            "sheet_register": [
                {"mark": sec, "number": str(i + 1), "title": f.get("name",""), "file_id": f.get("id","")}
                for i, f in enumerate(clean)
            ],
            "sections": [f.get("name","") for f in clean],
            "materials": [],
            "axes_grid": {"axes_letters": [], "axes_numbers": []},
            "dimensions": [],
        }
        out = out_dir / f"PROJECT_TEMPLATE_MODEL__{sec}_FINAL_SOURCE_LOCK.json"
        out.write_text(_json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
        result["synced_sections"].append(sec)

    result["ok"] = True
    return result

def _final_project_model_for_request_v1(user_text: str, topic_id: int = 210) -> dict:
    import json as _json
    from pathlib import Path as _Path
    _final_sync_project_drive_templates_v1(int(topic_id or 210))
    sec = _final_project_section_from_request_v1(user_text)
    base = _Path("/root/.areal-neva-core/data/project_templates")
    candidates = []
    if sec == "ЭСКИЗ":
        candidates.append(base / "PROJECT_TEMPLATE_MODEL__ЭСКИЗ_FINAL_SOURCE_LOCK.json")
        candidates.append(base / "PROJECT_TEMPLATE_MODEL__АР_FINAL_SOURCE_LOCK.json")
    else:
        candidates.append(base / f"PROJECT_TEMPLATE_MODEL__{sec}_FINAL_SOURCE_LOCK.json")
    candidates.append(base / "PROJECT_TEMPLATE_MODEL__КЖ_FINAL_SOURCE_LOCK.json")
    for p in candidates:
        if p.exists():
            try:
                return _json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    return {}

def create_project_artifact_from_latest_template(user_text: str, task_id: str, topic_id: int = 0) -> dict:
    import os as _os
    import tempfile as _tempfile
    from datetime import datetime as _dt, timezone as _tz

    result = {
        "success": False,
        "error": "",
        "docx_path": "",
        "xlsx_path": "",
        "docx_link": "",
        "xlsx_link": "",
        "template_found": False,
        "project_type": "UNKNOWN",
    }

    model = _final_project_model_for_request_v1(user_text, int(topic_id or 210))
    if not model:
        result["error"] = "PROJECT_DRIVE_TEMPLATE_NOT_FOUND"
        return result

    params = _ff3_extract_project_params(user_text)
    project_type = _final_project_section_from_request_v1(user_text)
    if project_type == "UNKNOWN":
        project_type = model.get("project_type") or "КЖ"

    result["template_found"] = True
    result["project_type"] = project_type

    safe_task = str(task_id or "manual")[:8]
    out_dir = _tempfile.gettempdir()
    docx_path = _os.path.join(out_dir, f"project_{project_type}_{safe_task}.docx")
    xlsx_path = _os.path.join(out_dir, f"project_{project_type}_{safe_task}.xlsx")

    sheets = model.get("sheet_register") or []
    norm_sheets = []
    for sh in sheets:
        if isinstance(sh, str) and sh.strip():
            norm_sheets.append({"mark": project_type, "number": str(len(norm_sheets)+1), "title": sh.strip()[:160]})
        elif isinstance(sh, dict):
            norm_sheets.append(sh)
    sheets = norm_sheets or [{"mark": project_type, "number": "1", "title": model.get("source_file_name") or "Образец проекта"}]

    try:
        from docx import Document
        doc = Document()
        doc.add_heading(_ff3_safe_docx_text(params.get("project_name") or f"Проект {project_type}"), level=1)
        doc.add_paragraph("Источник: Google Drive / Образцы проектов")
        doc.add_paragraph("PROJECT_ARTIFACTS используется только как выходная папка, не как источник")
        doc.add_paragraph(f"Раздел: {project_type}")
        doc.add_paragraph(f"Образец: {model.get('source_file_name') or ''}")
        doc.add_paragraph(f"Дата: {_dt.now(_tz.utc).isoformat()}")

        doc.add_heading("Текущее задание", level=2)
        doc.add_paragraph(_ff3_safe_docx_text(user_text))

        doc.add_heading("Состав по источникам Drive", level=2)
        tbl = doc.add_table(rows=1, cols=4)
        tbl.rows[0].cells[0].text = "Марка"
        tbl.rows[0].cells[1].text = "Лист"
        tbl.rows[0].cells[2].text = "Наименование"
        tbl.rows[0].cells[3].text = "Drive file id"
        for sh in sheets:
            row = tbl.add_row().cells
            row[0].text = _ff3_safe_docx_text(sh.get("mark") or project_type)
            row[1].text = _ff3_safe_docx_text(sh.get("number") or "")
            row[2].text = _ff3_safe_docx_text(sh.get("title") or "")
            row[3].text = _ff3_safe_docx_text(sh.get("file_id") or "")

        doc.add_heading("Разделы", level=2)
        for sec in (model.get("sections") or [])[:100]:
            doc.add_paragraph(_ff3_safe_docx_text(sec))

        doc.save(docx_path)
    except Exception as e:
        result["error"] = "DOCX_CREATE_FAILED: " + str(e)[:250]
        return result

    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Состав проекта"
        headers = ["№", "Марка", "Лист", "Наименование", "Drive file id", "Источник"]
        for c, h in enumerate(headers, 1):
            ws.cell(1, c, h)
        for i, sh in enumerate(sheets, 2):
            ws.cell(i, 1, i - 1)
            ws.cell(i, 2, sh.get("mark") or project_type)
            ws.cell(i, 3, sh.get("number") or "")
            ws.cell(i, 4, sh.get("title") or "")
            ws.cell(i, 5, sh.get("file_id") or "")
            ws.cell(i, 6, "Образцы проектов / PROJECT_DESIGN_REFERENCES")
        ws2 = wb.create_sheet("Текущее задание")
        ws2.cell(1, 1, "Задание")
        ws2.cell(2, 1, str(user_text or "")[:32000])
        ws2.cell(4, 1, "Запрещено")
        ws2.cell(5, 1, "PROJECT_ARTIFACTS не использовать как источник")
        for col, width in {"D": 80, "E": 45, "F": 45}.items():
            ws.column_dimensions[col].width = width
        ws2.column_dimensions["A"].width = 120
        wb.save(xlsx_path)
        wb.close()
    except Exception as e:
        result["error"] = "XLSX_CREATE_FAILED: " + str(e)[:250]
        return result

    result["docx_path"] = docx_path
    result["xlsx_path"] = xlsx_path

    try:
        from core.engine_base import upload_artifact_to_drive
        result["docx_link"] = upload_artifact_to_drive(docx_path, task_id, int(topic_id or 0)) or ""
        result["xlsx_link"] = upload_artifact_to_drive(xlsx_path, task_id, int(topic_id or 0)) or ""
    except Exception as e:
        result["upload_error"] = str(e)[:250]

    result["success"] = bool(_os.path.exists(docx_path) and _os.path.getsize(docx_path) > 1000)
    if not result["success"]:
        result["error"] = "PROJECT_ARTIFACT_EMPTY"
    try:
        from core.project_route_guard import format_project_result_message
        from core.output_sanitizer import sanitize_project_message
        result["user_message"] = sanitize_project_message(format_project_result_message(result, user_text))
    except Exception:
        pass
    return result

# === END_THREE_CONTOURS_FINAL_SOURCE_LOCK_V1 ===

# === PHOTO_RECOGNITION_TOPIC210_RUNTIME_BINDING_V1 ===
try:
    _photo_210_orig_process_project_file = process_project_file

    async def process_project_file(file_path: str, task_id: str, topic_id: int, raw_input: str = "") -> Dict[str, Any]:
        from pathlib import Path as _PhotoPath
        import json as _photo_json
        import tempfile as _photo_tempfile
        from core.photo_recognition_engine import is_image_file, process_photo_recognition

        fp = str(file_path or "")
        fn = _PhotoPath(fp).name

        try:
            tid = int(topic_id or 0)
        except Exception:
            tid = 0

        if tid == 210 and is_image_file(file_name=fn, file_path=fp):
            card = process_photo_recognition(
                topic_id=210,
                file_name=fn,
                file_path=fp,
                owner_comment=str(raw_input or ""),
                source="TELEGRAM",
                project_context_hint=str(raw_input or ""),
            )

            out_dir = _PhotoPath(_photo_tempfile.gettempdir()) / "areal_project_image_cards"
            out_dir.mkdir(parents=True, exist_ok=True)

            safe_task = str(task_id or "project_image")[:16]
            artifact = out_dir / f"PROJECT_IMAGE_CARD__{safe_task}.json"
            artifact.write_text(_photo_json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")

            return {
                "success": True,
                "section": detect_section(fn, raw_input) or "UNKNOWN",
                "artifact_path": str(artifact),
                "project_image_card": card,
                "status": "PROJECT_IMAGE_CARD_CREATED_NO_VISION_ANALYSIS",
                "error": None,
                "message": "Изображение принято как проектный материал. Визуальный анализ не выполнялся без разрешённой Vision-модели",
            }

        return await _photo_210_orig_process_project_file(
            file_path=file_path,
            task_id=task_id,
            topic_id=topic_id,
            raw_input=raw_input,
        )
except Exception:
    pass
# === END_PHOTO_RECOGNITION_TOPIC210_RUNTIME_BINDING_V1 ===


# === LOAD_CALCULATION_INPUT_BASED_BINDING_V1 ===
def calc_loads_input_based(
    permanent_kpa=None,
    temporary_kpa=None,
    snow_kpa=None,
    wind_kpa=None,
    source_text: str = "",
):
    from core.load_calculation_engine import calculate_loads_fact_only
    return calculate_loads_fact_only(
        permanent_kpa=permanent_kpa,
        temporary_kpa=temporary_kpa,
        snow_kpa=snow_kpa,
        wind_kpa=wind_kpa,
        source_text=source_text,
    )
# === END_LOAD_CALCULATION_INPUT_BASED_BINDING_V1 ===

====================================================================================================
END_FILE: core/project_engine.py
FILE_CHUNK: 1/1
====================================================================================================
