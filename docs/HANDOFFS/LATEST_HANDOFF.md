# LATEST HANDOFF — 2026-05-08 ~11:00 MSK
**HEAD**: `8760011`
**Воркер**: active

---

## СТАТУС ТОПИКОВ

| Топик | Состояние | Примечание |
|-------|-----------|------------|
| topic_2 СТРОИКА | INSTALLED (не VERIFIED) | TOPIC2_CANONICAL_PDF_GATE_V1 в task_worker.py, d72028da → DONE |
| topic_5 ТЕХНАДЗОР | Stable | без изменений |
| topic_500 ПОИСК | INSTALLED (не VERIFIED) | 9 режимов adaptive output |
| topic_210 PROJECT | Active | без изменений |

---

## ТЕКУЩАЯ ЗАДАЧА: PATCH_TELEGRAM_BIG_FILE_LOCAL_BOT_API_V1

### Проблема
`telegram-ingress.service` (telegram_daemon.py, строка 743) — `bot.get_file(file_id)` → `HANDLER_CRASH: file is too big` для файлов >20MB. Задача в БД не создаётся.

### Что сделано (сессия 08.05 ~11:00)

| Файл | Статус | Описание |
|------|--------|----------|
| `/opt/telegram-bot-api-build/` | **BUILD IN PROGRESS ~36%** | PID 2332600, лог `/opt/telegram-bot-api-build.log` |
| `/etc/areal/telegram-local-api.env` | **READY** | chmod 600, root:root, значения ПУСТЫЕ — нужны api_id/api_hash |
| `/etc/systemd/system/telegram-bot-api-local.service` | **READY, NOT STARTED** | ConditionPathExists=/usr/local/bin/telegram-bot-api |
| `/root/.areal-neva-core/areal_telegram_wrapper.py` | **READY, NOT ACTIVE** | wrapper patching aiogram + download URL в памяти |
| `/root/.areal-neva-core/tmp/bigfile_ingress_override.conf.pending` | **PENDING** | НЕ скопировать до gates |
| `/root/.areal-neva-core/tools/verify_local_bot_api.sh` | **READY** | 4-step activation gate |

### Activation Gate (все 4 обязательны)
```
1. binary OK      → /usr/local/bin/telegram-bot-api -x
2. service active → systemctl is-active telegram-bot-api-local
3. local getMe OK → curl http://localhost:8081/bot${TOKEN}/getMe → ok:true
4. wrapper dry-run OK → tools/verify_local_bot_api.sh
```

### Что НУЖНО от пользователя
```
TELEGRAM_API_ID=<число>
TELEGRAM_API_HASH=<hex строка>
```
Источник: https://my.telegram.org → API Development Tools

### Как заполнить credentials и активировать
```bash
# 1. Заполнить credentials (root only, не печатать в chat)
nano /etc/areal/telegram-local-api.env

# 2. Запустить local сервер
systemctl daemon-reload
systemctl start telegram-bot-api-local

# 3. Прогнать все проверки
/root/.areal-neva-core/tools/verify_local_bot_api.sh

# 4. Только если verify_local_bot_api.sh вернул 0:
mkdir -p /etc/systemd/system/telegram-ingress.service.d
cp /root/.areal-neva-core/tmp/bigfile_ingress_override.conf.pending \
   /etc/systemd/system/telegram-ingress.service.d/bigfile.conf
systemctl daemon-reload
systemctl restart telegram-ingress
```

### Ожидаемое поведение после активации
- Файл >20MB из Telegram → задача создаётся → `_handle_drive_file`
- `TOPIC2_CANONICAL_PDF_GATE_V1` → `maybe_handle_stroyka_estimate` → полный pipeline
- Маркеры: `BIG_FILE_LOCAL_BOT_API_USED` → `FILE_INTAKE_ROUTER_LOCAL_PATH_PASSED`
- topic_5/topic_210/topic_500 не изменяются

### Запрещённые файлы (не трогать никогда)
telegram_daemon.py, .env, ai_router.py, reply_sender.py, google_io.py, credentials.json

---

## ПРОШЛАЯ P0 (ЗАКРЫТО в 8760011)

### TOPIC2_CANONICAL_PDF_GATE_V1 — task_worker.py body-edit
- Вставлена до generic route_file (строки ~4122-4148)
- topic_2 + PDF + intent=estimate → `maybe_handle_stroyka_estimate` → canonical pipeline
- d72028da: DONE, 25 позиций, 5 425 839 руб, Excel+PDF в Drive ✅

---

## ДИАГНОСТИКА

```bash
# Прогресс сборки
tail -5 /opt/telegram-bot-api-build.log

# Готовность бинаря
ls -la /usr/local/bin/telegram-bot-api 2>/dev/null || echo "not built yet"

# Проверка gates
/root/.areal-neva-core/tools/verify_local_bot_api.sh

# Воркер
systemctl is-active areal-task-worker
grep "TOPIC2_CANONICAL_PDF_GATE\|BIG_FILE_LOCAL" \
  /root/.areal-neva-core/logs/task_worker.log | tail -10
```

---

## CANON REFS
- `docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md` — §4, §11.9
- `core/stroyka_estimate_canon.py:1930` — `maybe_handle_stroyka_estimate`
- `areal_telegram_wrapper.py` — PATCH_TELEGRAM_BIG_FILE_LOCAL_BOT_API_V1 (не активен)
- `tools/verify_local_bot_api.sh` — activation gate script
- `docs/HANDOFFS/LATEST_HANDOFF.md` — этот файл
