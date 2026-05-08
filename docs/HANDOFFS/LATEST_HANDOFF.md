# LATEST HANDOFF — 2026-05-09 ~01:15 MSK
**HEAD**: `af42c97`
**Воркер**: active (areal-task-worker)
**telegram-ingress**: active

---

## СТАТУС ТОПИКОВ

| Топик | Состояние | Примечание |
|-------|-----------|------------|
| topic_2 СТРОИКА — дренаж | AWAITING_CONFIRMATION `043e5c9f` | bot_msg=10613, итого 1 035 664 руб, WITHOUT_VAT |
| topic_5 ТЕХНАДЗОР | INSTALLED (не VERIFIED) | SA Drive upload fails 403, OAuth fallback в коде |
| topic_500 ПОИСК | INSTALLED (не VERIFIED) | 9 режимов adaptive output |
| topic_210 PROJECT | Active | без изменений |

---

## ЗАКРЫТО В СЕССИИ 08-09.05.2026

### 1. PATCH_TOPIC2_INPUT_GATE_SOURCE_OF_TRUTH_V1 — COMMITTED ✅
- `core/topic2_input_gate.py` — gate с 25 маркерами дренажа/ливнёвки
- Wrapper в конце `core/stroyka_estimate_canon.py`
- Live: `acdae011` → gate сработал, WC-ответ доставлен вручную (bot_msg=10575)

### 2. PATCH_WAITING_CLARIFICATION_DELIVERY_GUARD_V1 — COMMITTED ✅
- Патч в `task_worker.py` — перехватывает `_pick_next_task`, доставляет WC-сообщения при пустом `bot_message_id`

### 3. PATCH_TOPIC2_DRAINAGE_CHILD_MERGE_V1 — COMMITTED ✅ (af42c97)
- Патч в `task_worker.py` перед `__main__`
- При каждом цикле пикера: если есть активный дренажный родитель (WC/AC) → все NEW text-задачи topic_2 → DONE с маркером `TOPIC2_CHILD_MERGED_TO_DRAINAGE_PARENT:<parent_id>`
- Noise-задачи `9a174a37` и `85992edd` закрыты напрямую в БД

### 4. TOPIC2_DRAINAGE_FULL_CLOSE_NO_LOOP_V2 — COMMITTED ✅ (af42c97)
- `tools/topic2_drainage_repair_close.py`: legend filter в `extract_lengths`, fallback L=80м, VAT gate 22%, source filter (user PDFs only), clean public output
- PDF `file_1.pdf` — схема дренажа (120 774 chars, только отметки высот, нет машиночитаемых длин)
- PDF `file_0.pdf` — геологический отчёт (76 662 chars)
- Длины: `APPROX_FROM_SCHEME_NO_FULL_LENGTH_TABLE`, L=80м (консервативный дефолт, 3 колодца Дк-1/2/3 + ДНС-1 + ПУ-1)
- VAT: `WITHOUT_VAT` (подтверждено в history rowid 90090)
- XLSX → bot_msg=10611, PDF → bot_msg=10612, текст → bot_msg=10613
- Задача `043e5c9f` → AWAITING_CONFIRMATION, result чистый (нет /root/, runtime, drainage_estimate_)

---

## ОТКРЫТЫЕ ВОПРОСЫ

| Проблема | Статус |
|----------|--------|
| Длины дренажа не извлекаются | PDF — графическая схема, только отметки высот в тексте. Дефолт 80м. Если пользователь пришлёт реальные длины — пересчитать |
| topic_5 Drive SA 403 | live-тест не пройден |
| PDF_SPEC_EXTRACTOR_REAL_V1 | stub |
| WC задача пикается после доставки | STALE_TIMEOUT закрывает, WCG_SKIP_LOOP защищает от повтора — не критично |

---

## ДИАГНОСТИКА

```bash
# Дренажная задача
sqlite3 data/core.db "SELECT id,state,bot_message_id,substr(result,1,120),updated_at FROM tasks WHERE id='043e5c9f-e8bc-434c-9dad-a66c7e50f917';"

# Последние задачи topic_2
sqlite3 data/core.db "SELECT id,state,bot_message_id,error_message,updated_at FROM tasks WHERE topic_id=2 ORDER BY rowid DESC LIMIT 5;"

# Child merge маркеры
sqlite3 data/core.db "SELECT task_id,action FROM task_history WHERE action LIKE 'TOPIC2_CHILD_MERGED%' ORDER BY rowid DESC LIMIT 10;"

# Воркер
systemctl is-active areal-task-worker
tail -10 logs/task_worker.log
```
