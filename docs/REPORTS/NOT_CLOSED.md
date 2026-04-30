# NOT_CLOSED — 30.04.2026 UPDATE 06:30

## ЗАКРЫТО КОДОМ И VERIFIED (30.04.2026)

| Что | Патч | Статус |
|---|---|---|
| OAuth invalid_scope в daemon | PATCH_SCOPE_FULL_V1 | VERIFIED ✅ |
| Daemon без OAuth переменных | PATCH_DAEMON_OAUTH_OVERRIDE_V1 | VERIFIED ✅ |
| Drive file lifecycle (intake → choice → process) | мн. патчей | VERIFIED ✅ |
| upload_retry_queue cron 10min | core/upload_retry_queue.py | VERIFIED ✅ |
| topic folder isolation | PATCH_RETRY_TOPIC_FOLDER_V1 | VERIFIED ✅ |
| source guard (не-telegram → CANCELLED) | PATCH_SOURCE_GUARD_V1 | INSTALLED |
| file error retry (reply → restart) | PATCH_FILE_ERROR_RETRY_V1 | INSTALLED |
| OAuth scope=drive везде | PATCH_SCOPE_FULL_V1 | VERIFIED ✅ |

## НЕ ЗАКРЫТО — P1 (следующая сессия)

### PATCH_CONFIRM_ONLY_ON_DONE_V1
**Проблема:** бот спрашивает "Доволен результатом?" даже когда задача не выполнена
- result = "скачан, ожидает анализа" → НЕ должен показывать confirmation
- result = "Ошибка..." → НЕ должен показывать confirmation
- Confirmation только если state=AWAITING_CONFIRMATION И result содержит реальный результат
- Файл: task_worker.py — функция _handle_drive_file / _handle_in_progress

### project_engine (P1 новый)
**Проблема:** шаблон из PDF = просто текст, не структура
- Пользователь хочет: дать PDF проекта → получить структурный шаблон (разделы, нормативы, сетка, узлы)
- Пользователь хочет: давать задания в чате → получать проектные документы
- Нужно: project_engine.py который разбирает PDF на структурные элементы
- Хранит шаблон как JSON с параметрами (не просто текст)
- По заданию генерирует новый документ на основе шаблона
- Файл: core/project_engine.py (создать)

### Голосовой confirm при AWAITING_CONFIRMATION
- telegram_daemon.py строка ~601
- Голосовое "да" не закрывает задачу

### Live-тесты INSTALLED патчей
- PATCH_FILE_ERROR_RETRY_V1 — reply на ошибку → перезапуск
- PATCH_CRASH_BOTMSG_V1 — crash сохраняет bot_message_id
- PATCH_DUPLICATE_GUARD_V1, PATCH_MULTI_FILE_INTAKE_V1, PATCH_LINK_INTAKE_NEEDS_CONTEXT_V1

## НЕ ЗАКРЫТО — P2

- Смета PDF → Excel → Drive end-to-end
- КЖ PDF pipeline
- Gemini vision live-тест
- Excel формулы =C2*D2 / =SUM
- Нормы СП/ГОСТ в technadzor_engine
- Multi-file один артефакт
- Google Sheets интеграция
- Шаблоны end-to-end
- MODEL_ROUTER, FALLBACK_CHAIN
- STT "Олег" — Whisper галлюцинирует имя (не баг кода — баг модели)

## НОВЫЕ ФАКТЫ СЕССИИ 30.04 (дополнение)

- §0.8 ОБНОВЛЕНО: telegram_daemon.py можно редактировать с явного «да» пользователя
- OAuth scope: refresh_token должен соответствовать scope в коде — drive.file ≠ drive
- systemd override.conf нужен для КАЖДОГО сервиса отдельно
- AI router контекст: старые AWAITING_CONFIRMATION задачи загрязняют контекст → нужна периодическая чистка
- Whisper STT иногда галлюцинирует имена (слышит "Олег" вместо "Илья") — не баг кода

## АРХИТЕКТУРА FINAL (30.04.2026)

```
Telegram → daemon → upload_file_to_topic (OAuth, scope=drive)
                         ↓ OK
                    drive_file_id → create_task → task_worker
                         ↓ download
                    _download_from_drive (OAuth, scope=drive)
                         ↓ analyze
                    engine (estimate/project/technadzor/ocr/vision)
                         ↓ artifact
                    upload_artifact_to_drive → Drive topic folder
                         ↓ если упал
                    Telegram fallback → cron retry 10min
```

Cron:
- */10 upload_retry_queue.py
- */30 context_aggregator.py
- */5  monitor_jobs.py
- 0 */6 auto_memory_dump.sh
