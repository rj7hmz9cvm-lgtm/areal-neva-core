# LATEST HANDOFF — 2026-05-08 ~13:30 MSK
**HEAD**: `8a4de2b` (до push текущей сессии)
**Воркер**: active
**telegram-ingress**: active + bigfile wrapper

---

## СТАТУС ТОПИКОВ

| Топик | Состояние | Примечание |
|-------|-----------|------------|
| topic_2 СТРОИКА | FAILED c94ec497 / TOPIC2_CANONICAL_FULL_CLOSE_NOT_PROVEN | Смета не принята, 6 missing markers |
| topic_5 ТЕХНАДЗОР | INSTALLED (не VERIFIED) | SA Drive upload fails 403, OAuth fallback в коде |
| topic_500 ПОИСК | INSTALLED (не VERIFIED) | 9 режимов adaptive output |
| topic_210 PROJECT | Active | без изменений |

---

## ЗАКРЫТО В ЭТОЙ СЕССИИ

### 1. PATCH_TELEGRAM_BIG_FILE_LOCAL_BOT_API_V1 — ACTIVATED ✅
- `/usr/local/bin/telegram-bot-api` — бинарь собран, active
- `/etc/systemd/system/telegram-ingress.service.d/bigfile.conf` — скопирован
- Credentials в `/etc/areal/telegram-local-api.env` (TELEGRAM_API_ID / TELEGRAM_API_HASH)
- `telegram-ingress` перезапущен, лог: `BIG_FILE_LOCAL_BOT_API_USED: local server active`
- Файлы >20MB поступают через `/var/lib/telegram-bot-api/{TOKEN}/documents/`

### 2. Bot name restored ✅
- Был: "Sport VIP" → Восстановлен: "AREAL-NEVA ORCHESTRA"
- via `setMyName` API

### 3. PATCH_TOPIC5_ACT_DISPATCH_V3 — INSTALLED (не VERIFIED)
- Файл: `task_worker.py` (append перед `if __name__`)
- Вызывает `t5_canonical_act_generate` из `core/technadzor_engine.py`
- Если SA upload fails → fallback `_fcg_upload` (OAuth)
- **Проблема**: `storageQuotaExceeded` для Service Account; OAuth fallback в коде, не проверен live
- Маркеры: `T5CA_SA_UPLOAD_WARN`, `P8D_OAUTH_DOCX_UPLOAD`, `P8D_OAUTH_PDF_UPLOAD`

### 4. PATCH_TOPIC2_PDF_CANONICAL_GATE_HANDLE_IN_PROGRESS_V1 — INSTALLED
- Файл: `task_worker.py` (append перед PATCH_TOPIC5_ACT_DISPATCH_V3)
- Перехватывает `_handle_in_progress` для topic_2 + drive_file + PDF + estimate intent
- Блокирует старый P6C route
- Роутит в `maybe_handle_stroyka_estimate`

### 5. c94ec497 — задача создана, результат INVALID
- PDF: `Открыть Микеа 3 РП 3 (1) (3) (3).pdf` (62MB), local_path: `/root/.areal-neva-core/runtime/drive_files/mikea_rp3.pdf`
- Drive file_id: `1EBmfcyns9UOm4S9tg0CYqCpIIidfLgwl`
- Откатена в FAILED / `TOPIC2_CANONICAL_FULL_CLOSE_NOT_PROVEN`
- Причина: 6 missing canonical markers

---

## ОТКРЫТО: c94ec497 — PENDING PATCH_TOPIC2_BIGPDF_CANONICAL_FULL_CLOSE_V2

### Проблема
Смета сгенерирована неканонично:
- PDF не парсился (`TOPIC2_PDF_SPEC_EXTRACTOR_STARTED` отсутствует)
- `Этажность: не указана` в результате
- `TOPIC2_LOGISTICS_DISTANCE_KM:0` — но пользователь уточнил **30 км**
- Использован FALLBACK лист (`TOPIC2_TEMPLATE_SHEET_FALLBACK`) вместо «газобетон»
- message_id=10539 — невалиден как proof of full close

### Таблица маркеров (последняя проверка)

| Маркер | Статус |
|--------|--------|
| `BIG_FILE_LOCAL_DOWNLOAD_OK` | ✅ FOUND |
| `FILE_INTAKE_ROUTER_LOCAL_PATH_PASSED` | ❌ MISSING |
| `FILE_INTAKE_ROUTER_TOPIC2_CANONICAL_ROUTE` | ❌ MISSING |
| `TOPIC2_PDF_SPEC_EXTRACTOR_STARTED` | ❌ MISSING |
| `TOPIC2_PDF_SPEC_ROWS_EXTRACTED` | ❌ MISSING |
| `TOPIC2_FULL_ESTIMATE_MATRIX_ENFORCED` | ❌ MISSING |
| `TOPIC2_TEMPLATE_SELECTED` | ✅ FOUND |
| `TOPIC2_XLSX_CANON_COLUMNS_OK` | ✅ FOUND |
| `TOPIC2_PDF_CREATED` | ✅ FOUND |
| `TOPIC2_PDF_CYRILLIC_OK` | ✅ FOUND |
| `TOPIC2_PDF_TOTALS_MATCH_XLSX` | ✅ FOUND |
| `TOPIC2_DRIVE_UPLOAD_XLSX_OK` | ✅ FOUND |
| `TOPIC2_DRIVE_UPLOAD_PDF_OK` | ✅ FOUND |
| `TOPIC2_TELEGRAM_MATCHES_ARTIFACTS` | ❌ MISSING |
| `TOPIC2_PUBLIC_OUTPUT_CLEAN_OK` | ❌ MISSING |

### Факты из PDF (извлечено fitz, 42 страницы)
- **Этажность**: 1 этаж (Маркировочный план 1 этажа)
- **Площадь**: 99.91 м² (жилая) + 24.6 м² (наружные площадки)
- **Помещения 1 этажа**: прихожая 6.6, коридор 6.0, бойлерная 2.18, гостиная 24.79, кухня 9.46, коридор2 2.86, санузел 3.85, спальня хозяйская 14.08, спальня1 10.16, спальня2 10.16, санузел2 4.3, сауна 2.79, прачечная 2.69
- **Материал**: Газобетон 400мм (внешние стены), 250мм (внутренние), 150мм (перегородки)
- **Фундамент**: Монолитная плита «перевёрнутая чаша»
- **Кровля**: Фальцевая кровля 185 м², RAL7024
- **Фасад**: Оштукатуривание 96м² белый + цоколь 20м² RAL7012 + рейка 27.1м²
- **Окна**: 9 типов (Ок-1…Ок-9), все ПВХ с энергосберегающими стеклопакетами
- **Двери**: 5 типов (ДуМО1 входная, ДЧ чердачная, Д-1, Д-2, Д-3 межкомнатные)
- **Инженерка**: ОВ (3 листа), ВК (2 листа), ЭОМ
- **Тёплый пол**: экспликация тёплых полов — лист 37

### Уточнение от пользователя (из task_history)
```
clarified: Этажи написаны в проекте удалённость от города 30 км средние цены
```
- Удалённость: **30 км**
- Цены: **средние (median)** — подтверждено
- Этажи: в проекте → **1 этаж** (подтверждено PDF)

### Следующий шаг: PATCH_TOPIC2_BIGPDF_CANONICAL_FULL_CLOSE_V2

Требования по ТЗ (2026-05-08):
1. PDF spec extractor: извлечь все параметры из lokального PDF
2. Лист шаблона: «газобетон» (не fallback)
3. Дистанция: 30 км (не 0)
4. Полная матрица 11 секций
5. Все 15 canonical markers
6. Отправка только через нормальный send path (не curl)
7. TOPIC2_BOT_MESSAGE_ID_SAVED обязателен
8. AWAITING_CONFIRMATION только после full marker set

### Запрещено
- Новая task_id
- Брать d72028da
- Generic LLM fallback для финала
- median без подтверждения (подтверждено — можно использовать)
- AWAITING_CONFIRMATION без full marker set
- message_id=10539 как валидный proof

---

## НЕ СДЕЛАНО / ИЗВЕСТНЫЕ ПРОБЛЕМЫ

| Проблема | Статус |
|----------|--------|
| topic_5 Drive upload (SA 403) | Код OAuth fallback есть, live-тест не пройден |
| c94ec497 canonical estimate | FAILED, нужен PATCH_TOPIC2_BIGPDF_CANONICAL_FULL_CLOSE_V2 |
| topic_2 `_handle_in_progress` wrapper | INSTALLED, live-тест не пройден на новом файле |

---

## ДИАГНОСТИКА

```bash
# Воркер
systemctl is-active areal-task-worker
tail -20 /root/.areal-neva-core/logs/task_worker.log

# Bigfile wrapper
systemctl is-active telegram-bot-api-local
systemctl is-active telegram-ingress
grep "BIG_FILE_LOCAL_BOT_API_USED" /root/.areal-neva-core/logs/task_worker.log | tail -3

# c94ec497 состояние
sqlite3 /root/.areal-neva-core/data/core.db "SELECT state, error_message FROM tasks WHERE id='c94ec497-4351-43a7-a106-b3dab1633838';"
sqlite3 /root/.areal-neva-core/data/core.db "SELECT action, created_at FROM task_history WHERE task_id='c94ec497-4351-43a7-a106-b3dab1633838' ORDER BY created_at;"

# Local PDF
ls -la /root/.areal-neva-core/runtime/drive_files/mikea_rp3.pdf
```

---

## CANON REFS
- `docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md` — §4, §11.9
- `docs/CANON_FINAL/TOPIC_2_CANONICAL_ESTIMATE_CONTRACT.md` — §10 DONE contract
- `core/stroyka_estimate_canon.py:2808` — `maybe_handle_stroyka_estimate` (последняя def)
- `areal_telegram_wrapper.py` — PATCH_TELEGRAM_BIG_FILE_LOCAL_BOT_API_V1 (активен)
- `tools/verify_local_bot_api.sh` — activation gate script
- `runtime/drive_files/mikea_rp3.pdf` — исходный PDF (62MB, 42 страницы)
