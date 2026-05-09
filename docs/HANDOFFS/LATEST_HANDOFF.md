# LATEST HANDOFF — 2026-05-09 ~15:30 MSK
**HEAD**: `8b21d75`
**Воркер**: active (areal-task-worker)
**telegram-ingress**: active

---

## СТАТУС ТОПИКОВ

| Топик | Состояние | Примечание |
|-------|-----------|------------|
| topic_2 СТРОИКА | AWAITING_CONFIRMATION `076e4350` | bot_msg=10757, 8 348 317 руб — сгенерирована БЕЗ price WC (до патча), требует подтверждения/правок от пользователя |
| topic_5 ТЕХНАДЗОР | INSTALLED (не VERIFIED) | SA Drive upload fails 403, OAuth fallback в коде |
| topic_500 ПОИСК | INSTALLED (не VERIFIED) | 9 режимов adaptive output |
| topic_210 PROJECT | Active | без изменений |

---

## ЗАКРЫТО В СЕССИИ 09.05.2026 (вторая смена)

### PATCH_TOPIC2_PRICE_ALWAYS_ASK_V1 — COMMITTED ✅ (8b21d75)
**Файл**: `core/stroyka_estimate_canon.py` — append в конец

**Проблема**: "сделай по заданию смету" → `_is_confirm(startswith "сделай ")` = True + `_pending_is_fresh` override 24h (строка 2470-2472) → `CANONICAL_OLD_ROUTE_HARD_BLOCK` подхватывал pending от предыдущего запуска → пропускал price WC → estimate без TOPIC2_PRICE_CHOICE_CONFIRMED.

**Фикс**: Wrapper вокруг `maybe_handle_stroyka_estimate` — если pending активен AND `not _is_confirm_only(raw)` (raw содержит ESTIMATE_WORDS, напр. "смет") → помечает pending stale. `_is_confirm_only("сделай по заданию смету")` = False (содержит "смет") → pending очищается → полный flow → price WC.

Легитимные подтверждения ("да", "средняя", "ок") — `_is_confirm_only` = True → pending НЕ очищается → estimate генерируется ✓.

### Gate stale-context fixes — COMMITTED ✅ (8b21d75)
**Файл**: `core/topic2_input_gate.py`

- `_text_from_task`: убран `result` из текста gate — estimate result "Не входит: дренаж" → ложная блокировка user-clarification как drainage
- `_latest_file_task` / `_recent_file_tasks`: фильтр `IN (NEW/IP/WC/AC)` — DONE задача с mikea_rp3.pdf (ливневая канализация) давала false positive
- `_collect_current_file_text`: filesystem-scan заменён DB-lookup по активным задачам — `_recent_runtime_pdfs()` находила 4 old drainage PDF из FAILED задач

### task_worker.py fixes — COMMITTED ✅ (8b21d75)
- FULLFIX_14: добавлен `topic_id==2` guard — topic_11 (видео) больше не роутится в estimate
- `_p6_is_topic2_vague`: исключение correction-фраз ("это не", "это план", "план дома" и т.д.)

---

## ОТКРЫТЫЕ ВОПРОСЫ

| Проблема | Статус |
|----------|--------|
| topic_2 `076e4350` — estimate без price WC | AWAITING_CONFIRMATION, bot_msg=10757. Сгенерирован ДО патча. Ждёт ответа пользователя |
| topic_5 Drive SA 403 | live-тест не пройден |
| Длины дренажа из PDF | PDF-схема графическая, дефолт 80м — дренажная задача 043e5c9f уже закрыта |

---

## ДИАГНОСТИКА

```bash
# Текущая house-смета
sqlite3 data/core.db "SELECT id,state,bot_message_id,substr(result,1,100),updated_at FROM tasks WHERE id='076e4350-c8e7-4fea-bca6-b980faad2a64';"

# Проверка price WC в истории следующей задачи
sqlite3 data/core.db "SELECT action,created_at FROM task_history WHERE task_id='076e4350-c8e7-4fea-bca6-b980faad2a64' ORDER BY rowid DESC LIMIT 10;"

# Последние topic_2 задачи
sqlite3 data/core.db "SELECT id,state,bot_message_id,substr(raw_input,1,60),updated_at FROM tasks WHERE topic_id=2 ORDER BY rowid DESC LIMIT 5;"

# Воркер
systemctl is-active areal-task-worker
tail -10 logs/task_worker.log

# Проверка патча в памяти модуля
python3 -c "from core.stroyka_estimate_canon import maybe_handle_stroyka_estimate; import inspect; print('PRICE_ALWAYS_ASK' in inspect.getsource(maybe_handle_stroyka_estimate))"
```
