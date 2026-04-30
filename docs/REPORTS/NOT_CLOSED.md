# NOT_CLOSED — 30.04.2026 FINAL 05:40

## ЗАКРЫТО КОДОМ И VERIFIED

| Что | Патч | Статус |
|---|---|---|
| OAuth invalid_scope в daemon | PATCH_SCOPE_FULL_V1 | VERIFIED ✅ |
| Daemon без OAuth переменных | PATCH_DAEMON_OAUTH_OVERRIDE_V1 | VERIFIED ✅ |
| Daemon использовал Service Account | PATCH_DAEMON_USE_OAUTH_V1 | INSTALLED |
| Voice upload через SA | PATCH_VOICE_OAUTH_V1 | INSTALLED |
| Все predыдущие drive_file патчи | смотри HANDOFF | VERIFIED ✅ |
| Stale tasks cleanup | db | DONE ✅ |

## НЕ ЗАКРЫТО — P1 (нужен live-тест)

- Голосовой confirm при AWAITING_CONFIRMATION (telegram_daemon.py:601)
- Полный цикл после PATCH_SCOPE_FULL_V1: file → meню → choice → result
- File error retry с реальным reply
- DUPLICATE_GUARD/MULTI_FILE/LINK_INTAKE — все INSTALLED, тесты не проводились

## НЕ ЗАКРЫТО — P2

- Смета PDF → Excel → Drive end-to-end
- КЖ PDF pipeline
- project_engine end-to-end
- Gemini vision
- Excel формулы / нормы СП/ГОСТ
- Multi-file один артефакт
- Google Sheets / Шаблоны
- MODEL_ROUTER, FALLBACK_CHAIN
- STT "Олег" — Whisper галлюцинация

## АРХИТЕКТУРА FINAL

Drive Upload: OAuth scope=drive в trois файлах
Daemon → upload_file_to_topic (документы, фото, voice)
task_worker → engine_base.upload_artifact_to_drive
Retry: cron 10min → topic_drive_oauth._upload_file_sync
Healthcheck: list API (не upload — избегаем INGEST загрязнения)
