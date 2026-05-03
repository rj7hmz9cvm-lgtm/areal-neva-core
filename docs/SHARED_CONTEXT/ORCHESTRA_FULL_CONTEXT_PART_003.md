# ORCHESTRA_FULL_CONTEXT_PART_003
generated_at_utc: 2026-05-03T10:23:42.275442+00:00
git_sha_before_commit: 875b3f9e5f53a13b3b4d1eca6d3c1bbde885b61b
part: 3/7


====================================================================================================
BEGIN_FILE: chat_exports/CHAT_EXPORT__areal-neva-orchestra-dev__2026-04-29.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c669b92dcea070f78a044fbb0732dbaf38d549be814bfc94ea7b5d422443528a
====================================================================================================
{
  "chat_id": "claude_session_29_04_2026_MAIN",
  "chat_name": "AREAL-NEVA ORCHESTRA — Claude Session 29.04.2026 — MAIN DEV SESSION",
  "exported_at": "2026-04-29T20:45:00+03:00",
  "source_model": "Claude Sonnet 4.6",
  "session_summary": "Полная сессия разработки 29.04.2026. Закрыто 39 пунктов кодом.",
  "patches_confirmed_by_terminal": [
    "CRON_AGGREGATOR — tools/context_aggregator.py — AGG_OK",
    "P0_1_TEXT_ESTIMATE_FORCE_EXCEL_UPLOAD_V1 — core/estimate_engine.py — SYNTAX_OK active",
    "ALL_CONTOURS_ROUTE_FILE_V2 — core/file_intake_router.py — SYNTAX_OK active",
    "ALL_CONTOURS_TECHNADZOR_NORMS_V2 — core/technadzor_engine.py — SYNTAX_OK active",
    "ALL_CONTOURS_TEMPLATE_MANAGER_V2 — core/template_manager.py — SYNTAX_OK active",
    "ALL_CONTOURS_CP8_DRIVE_LINK_V2 — task_worker.py — SYNTAX_OK active",
    "ALL_CONTOURS_SHORT_VOICE_CONFIRM_V2 — telegram_daemon.py — SYNTAX_OK active",
    "FINAL_CODE_CONTOUR_FILE_INTAKE_V1 — core/file_intake_router.py — SYNTAX_OK active",
    "FINAL_CODE_CONTOUR_ESTIMATE_KZH_V1 — core/estimate_engine.py — SYNTAX_OK active",
    "FINAL_CODE_CONTOUR_TEMPLATE_APPLY_V1 — core/template_manager.py — SYNTAX_OK active",
    "FINAL_CODE_CONTOUR_SHEETS_SIGNATURE_V1 — core/sheets_generator.py — SYNTAX_OK active",
    "FINAL_CODE_CONTOUR_WORKER_V1 — task_worker.py — SYNTAX_OK active",
    "TECHNADZOR_RU_NORMS_V39 — core/technadzor_engine.py — SYNTAX_OK active",
    "FILE_INTAKE_KM_V39 — core/file_intake_router.py — SYNTAX_OK active",
    "DWG_EZDXF_V39 — core/dwg_engine.py — SYNTAX_OK active",
    "ESTIMATE_V39_HELPERS — core/estimate_engine.py — SYNTAX_OK active",
    "TASK_WORKER_V39_HELPERS — task_worker.py — SYNTAX_OK active",
    "MONITOR_HISTORY_V39 — monitor_jobs.py — SYNTAX_OK active",
    "SEARCH_POSTPROCESS_WIRED — task_worker.py:2348 — SYNTAX_OK active",
    "DUPLICATE_GUARD_WIRED — task_worker.py INSERT INTO tasks — SYNTAX_OK active",
    "REGION_WIRED — task_worker.py payload — SYNTAX_OK active",
    "TOPIC_MISMATCH_GUARD — task_worker.py — SYNTAX_OK active",
    "SEARCH_DEPTH_LIMIT — task_worker.py — SYNTAX_OK active",
    "PRICE_AGING — task_worker.py — SYNTAX_OK active",
    "OUTPUT_DECISION_LOGIC — task_worker.py — SYNTAX_OK active",
    "TRUST_RISK_SCORE — task_worker.py — SYNTAX_OK active",
    "SHORT_VOICE_CONFIRM_WIRED — telegram_daemon.py — SYNTAX_OK active",
    "AI_ROUTER_RU_PROMPT — core/ai_router.py — SYNTAX_OK active",
    "search_session TABLE — core.db + memory.db — OK",
    "retry_worker.py, media_group.py, context_engine.py, delivery.py, startup_recovery.py — CREATED",
    "HANDLE_MULTIPLE_FILES — core/file_intake_router.py — SYNTAX_OK active",
    "CACHE_LAYER_V1 — task_worker.py — SYNTAX_OK active",
    "REGION_PRIORITY_V1 — task_worker.py — SYNTAX_OK active"
  ],
  "already_existed_confirmed": [
    "CACHE_LAYER — core/ai_router.py строки 485-498",
    "SOURCE_DEDUPLICATION — task_worker.py _cp11_sha256_file строки 4357-4359",
    "apply_template — task_worker.py CANON_PASS12 строки 4405-4419"
  ],
  "not_closed_live_test_required": [
    "Голосовой confirm при AWAITING_CONFIRMATION — P1 баг подтверждён живым тестом 16:28",
    "Смета PDF -> Excel -> Drive",
    "КЖ PDF pipeline end-to-end",
    "DWG -> Excel -> Drive",
    "project_engine end-to-end через Telegram",
    "Поиск с постпроцессингом V41"
  ],
  "services_at_end_of_session": {
    "areal-task-worker": "active",
    "telegram-ingress": "active BOT STARTED id=8216054898",
    "areal-memory-api": "active"
  },
  "key_facts": [
    "SYNTAX_OK все файлы",
    "active NRestarts=0",
    "BOT STARTED id=8216054898",
    "200 OK GitHub handoff",
    "AGG_OK ONE_SHARED_CONTEXT 49 файлов"
  ]
}
====================================================================================================
END_FILE: chat_exports/CHAT_EXPORT__areal-neva-orchestra-dev__2026-04-29.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/CHAT_EXPORT__areal_neva__2026-04-23.txt
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 5041f18a62cd71ba76ae3465b70110c58910a3ca3c1323c8f2a0034c82061920
====================================================================================================
﻿{
  "chat_id": "-1003725299009",
  "chat_name": "areal_neva_orchestra",
  "exported_at": "2026-04-23T09:30:00Z",
  "source_model": "claude-sonnet-4-6",
  "system": {
    "server": "89.22.225.136",
    "os": "Ubuntu 24.04",
    "base": "/root/.areal-neva-core",
    "venv": "/root/.areal-neva-core/.venv/bin/python3",
    "bot": "@ai_orkestra_all_bot id=8216054898",
    "db_path": "/root/.areal-neva-core/data/core.db",
    "memory_db": "/root/.areal-neva-core/data/memory.db"
  },
  "architecture": [
    "telegram_daemon.py â€” intake Ð³Ð¾Ð»Ð¾Ñ�/Ñ‚ÐµÐºÑ�Ô¿Ñ„Ð°Ð¹Ð»Ñ‹",
    "task_worker.py â€” Ð¾Ð±Ñ€Ð°Ð±Ð¾Ñ‚ÐºÐ° Ð·Ð°Ð´Ð°Ñ‡, polling",
    "core/ai_router.py â€” routing Ð² LLM (deepseek/openrouter)",
    "core/reply_sender.py â€” Ð¾Ñ‚Ð¿Ñ€Ð°Ð²ÐºÐ° Ð¾ Telegram",
    "core/artifact_pipeline.py â€” Ð¾Ð±Ñ€Ð°Ð±Ð¾Ñ‚ÐºÐ° Ñ„Ð°Ð¹Ð»Ð¾Ð²",
    "core/file_intake_router.py â€” Ð¸Ð½Ñ‚ÐµÐ½Ñ‚ Ñ„Ð°Ð¹Ð»Ð¾Ð² Ð¿Ð¾ route",
    "core/technadzor_engine.py â€” Ñ‚ÐµÑ…Ð½Ð°Ð´Ð·Ð¾Ñ€",
    "core/estimate_engine.py â€” Ñ�Ð¼ÐµÑ‚Ñ‹",
    "core/ocr_engine.py â€” OCR (pytesseract not installed)",
    "core/engine_base.py â€” Ð±Ð°Ð·Ð¾Ð²Ñ‹Ðµ ÑƒÑ‚Ð¸Ð»Ð¸Ñ‚Ñ‹",
    "core/pin_manager.py â€” Ð·Ð°ÐºÑ€ÐµÐ¿Ð»Ñ‘Ð½Ð½Ñ‹Ð¹ ÐºÐ¾Ð½Ñ‚ÐµÐºÑ�Ñ‚",
    "google_io.py â€” Ð·Ð°Ð³Ñ€ÑƒÐ·ÐºÐ° Ð² Google Drive",
    "data/core.db â€” runtime Ñ�Ð¾Ñ�Ñ‚Ð¾Ñ�Ð½Ð¸Ðµ Ð·Ð°Ð´Ð°Ñ‡",
    "data/memory.db â€” Ð´Ð¾Ð»Ð³Ð°Ñ� Ð¿Ð°Ð¼Ñ�Ñ‚ÑŒ"
  ],
  "pipeline": {
    "text_voice": "TeeÐ ram â†’ telegram_daemon.py â†’ create_task(core.db) â†’ task_worker.py â†’ ai_router.py â€’ deepseek/Ð¾Ñ‚Ð²ÐµÑ‚ â†’ reply_sender.py â†’ Telegram",
    "file": "TeeÐ ram file â†’ upload_file_to_topic â€’ Google Drive â†’ drive_file Ñ‚Ð°Ñ�ÐºÐ°  ask_worker â†’ download â†’ file_intake_router â†’ engine â†’ artifact"
  },
  "files": {
    "modified": [
      "/root/.areal-neva-core/task_worker.py",
      "/root/.areal-neva-core/core/artifact_pipeline.py",
      "/root/.areal-neva-core/core/ai_router.py"
    ]
  },
  "patches": [
    {
      "file": "task_worker.py",
      "change": "DRIVE_FILE CRASH except â€” dobavlen _update_task state=FAILED",
      "verified": true
    },
    {
      "file": "task_worker.py _download_from_drive",
      "change": "EXPOPTH_MAP to Export Google Docs/Sheets via export_media",
      "verified": "kod viimod stan korectnyj"
    },
    {
      "file": "core/artifact_pipeline.py",
      "change": "1) kind=audio dla ogg 2) asyncio.to_thread dla vseh sync functions",
      "verified": "COMPILE_OK"
    }
  ],
  "services": {
    "areal-task-worker": "active",
    "areal-telegram-ingress": "inactive",
    "areal-memory-api": "active",
    "areal-automation-daemon": "activating (zavis)",
    "areal-email-ingress": "activating (zavis)",
    "areal-drive-ingest": "active"
  },
  "errors": [
    "DRIVE_FILE CRASH beskonechnyj retry â†’ except ne perevodil v FAILED â†’ ô£ÐºÑ€ÐµÐ¿Ð»ÐµÐ½ dOM-FAILED",
    "HttpError 403 Google Docs/Sheets â†’ get_media ne rabotaet â†’ EXPORT_MAP *ne protestirovano na livom)",
    "OGG STALE_TIMEOUT â†’ kind=binary ï»¿ kind=audio â†’ fix primenen",
    "route_file intent=technadzor fmt=excel â†’ no result â†’ upload_to_drive async/sync ne provereno",
    "OCR v\dostupen â†’ pytesseract ne ustanovlen"
  ],
  "what_working": [
    "task_worker active",
    "ai_router router_ok",
    "reply_sender reply_ok",
    "memory.db pishetsya po topikam",
    "STT Groq",
    "OGG ne zavisaet",
    "download files iz Drive"
  ],
  "what_broken": [
    "technadzor route_file no result",
    "OCR pytesseract missing",
    "telegram-ingress inactive",
    "automation-daemon activating",
    "email-ingress activating"
  ],
  "what_not_done": [
    "Excel formulas =C2*D2 =SUM",
    "OCR foto j excel",
    "shelony actov technadzora",
    "multi-file obedinenie",
    "DWG/DXF obrabotka",
    "Google Sheets sozdanie",
    "save_pin dla drive_file",
    "retry mekhanizm",
    "link validation",
    "temp file cleanup",
    "versionirovanie artefaktov"
  ],
  "current_breakpoint": "upload_artifact_to_drive vyzyvaet google_io.upload_to_drive synkhronno -- async/sync status ne proveren",
  "root_causes": [
    "upload_to_drive async/sync neyasno",
    "pytesseract ne ustanovlen",
    "telegram-ingress inactive - prichina neizvestna"
  ],
  "db": {
    "task_states": {"ARCHIVED": 371, "AWAITING_CONFIRMATION": 32, "CANCELLED": 58, "DONE": 6, "FAILED": 622},
    "drive_file_failed_reasons": {"legacy_drive_task_replaced": 305, "drive_file_queue_unblocked": 20, "drive_upload_stale": 10, "STALE_TIMEOUT": 7}
  },
  "memory": {
    "confirmed_keys": ["topic_5_assistant_output", "topic_5_task_summary", "topic_500_assistant_output", "topic_961_assistant_output"]
  },
  "limits": {
    "STALE_TIMEOUT": 600,
    "AI_TIMEOUT": 300,
    "MEMORY_LIMIT": 100
  }
}
====================================================================================================
END_FILE: chat_exports/CHAT_EXPORT__areal_neva__2026-04-23.txt
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/CHAT_EXPORT__claude_full_restore_01_05_2026__2026-05-01.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 587d2828b6b841dac9139c193a713e98c8a0bccfc5011f1b0422acc52e644dc7
====================================================================================================
{
  "chat_id": "claude_session_01_05_2026_FULL_RESTORE",
  "chat_name": "AREAL-NEVA — Полное восстановление системы 01.05.2026",
  "exported_at": "2026-05-01T16:10:18.154174",
  "source_model": "Claude Sonnet 4.6",
  "patches_verified": [
    "AI_LOGIC_FIX_V1 — task_worker.py — if/else перевёрнут исправлен — VERIFIED",
    "AI_RESULT_INIT_V1 — task_worker.py строка 2166 — VERIFIED",
    "SAVE_MEM_DONE_V2 — task_worker.py строки 2487/2506/2528 — VERIFIED",
    "DAEMON_OAUTH_FIX_V1 — telegram_daemon.py строка 707 — VERIFIED",
    "INPUT_TYPE_DRIVE_FIX_V1 — task_worker.py строка 2648 — VERIFIED",
    "SCOPE_FULL_V2 — topic_drive_oauth.py + drive_folder_resolver.py — VERIFIED",
    "PORT_FIX_V1 — archive_engine.py — 8765→8091 — VERIFIED",
    "MEMORY_API_SERVER_V1 — core/memory_api_server.py создан — VERIFIED",
    "IMPORT_FIX_V1 — core/topic_autodiscovery.py — VERIFIED",
    "ZOMBIE_UNITS_REMOVED — 4 unit-файла удалены — VERIFIED",
    "HOTFIX_FILE_NAME_EARLY_V1 — task_worker.py — VERIFIED",
    "HOTFIX_OK_BEFORE_SIZE_CHECK_V1 — task_worker.py — VERIFIED"
  ],
  "live_tests": [
    "СТРОЙКА topic=2: вспомнил сметы 55000р с Drive ссылками ✅",
    "ТЕХНАДЗОР topic=5: вспомнил архив чата ✅",
    "save_memory_ok: topic=2,5,794,6104 в 16:00-16:01 ✅",
    "archive_distributor: ok=True ✅",
    "Drive ALIVE PENDING_RETRY_COUNT=0 ✅",
    "telegram-ingress restarts=0 ✅"
  ],
  "services": {
    "areal-task-worker": "active restarts=0",
    "telegram-ingress": "active restarts=0",
    "areal-memory-api": "active restarts=0",
    "areal-monitor-jobs": "active restarts=1",
    "areal-upload-retry": "active restarts=3",
    "areal-drive-ingest": "active restarts=5"
  },
  "db_state": {
    "FAILED": 2811,
    "CANCELLED": 543,
    "ARCHIVED": 381,
    "DONE": 348,
    "AWAITING_CONFIRMATION": 19
  },
  "memory_state": {
    "archive_records": 969,
    "last_save_memory_ok": "2026-05-01 16:01:52 topic=6104",
    "topics_with_meta": 11
  },
  "not_closed": [
    "Voice confirm при AWAITING_CONFIRMATION",
    "Estimate PDF→Excel→Drive live-тест",
    "Technadzor фото→акт live-тест",
    "detect_intent() takes 1 arg warning",
    "19 задач в AWAITING_CONFIRMATION — проверить"
  ],
  "canon_rules": {
    "§15.1": "AI_LOGIC_FIX — if ai_result is None запускать AI",
    "§15.2": "Зомби-сервисы — удалять unit-файл физически",
    "§15.3": "Три слоя памяти: _save_memory + archive_engine + archive_distributor",
    "§15.4": "11 топиков в meta.json, autodiscovery 24h"
  }
}
====================================================================================================
END_FILE: chat_exports/CHAT_EXPORT__claude_full_restore_01_05_2026__2026-05-01.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/CHAT_EXPORT__claude_orchestra__2026-04-30_evening.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c3f50812c15a211e50a2350f5916e917e5bcc4db0d21bcb23e19ed32dd66fffd
====================================================================================================
# CHAT_EXPORT — claude_orchestra — 2026-04-30 evening

## SOURCE
- model: Claude Opus 4.7
- chat: -1003725299009 (orchestra)
- exported_at: 2026-04-30 evening MSK
- protocol: §37 EXPORT_CANON

## SYSTEM
Ubuntu 24.04, /root/.areal-neva-core, IP 89.22.225.136
Сервисы (5/5 active): areal-task-worker, telegram-ingress, areal-memory-api, areal-monitor-jobs, areal-upload-retry

## PIPELINE STATE
Базовый pipeline работает. Stage 1 Direction Kernel — proposal, не установлен.

## ЧТО ЗАКРЫТО КОДОМ В ЭТОЙ СЕССИИ

### Утренние коммиты
- 5eb59b9 FINAL_CLOSURE photo_linkage + template_engine + drive_link_mandatory
- 18a91ee TELEGRAM_FALLBACK_V1 Drive fail → send file directly to Telegram
- b92b074 TG_FALLBACK_WIRED в upload_or_fail (Drive fail → Telegram замкнут)

### Вечерние коммиты (если установлены)
- SEARCH_PLANNER_V1 (criteria + clarification + expand + profiles + tco + risk) — установлен в core/search_planner.py + ai_router

## ИСТОРИЯ ОБСУЖДЕНИЙ

### 1. Сверка с каноном
Проверены §1-§11 главного канона + ТЗ Lifecycle. Закрыто кодом большинство пунктов. §19 LIVE VERIFICATION — ни один из 9 сценариев не пройден живым тестом.

### 2. TELEGRAM_FALLBACK при Drive fail
Цепочка замкнута:
- Drive падает → upload_retry_queue (отложенный retry)
- Параллельно → _telegram_fallback_send() (немедленно)
- Возвращает telegram://file/{file_id}
- Пользователь получает файл даже без Drive

### 3. SEARCH_PLANNER_V1
Установлены модули:
- core/search_planner.py: extract_criteria, needs_clarification, expand_queries, plan_sources, classify_supplier, calculate_tco, score_risk, format_search_output
- Профили BUILDING/AUTO/GENERAL
- SEARCH_PLANNER_V1_INJECTED в ai_router.py (расширение SEARCH_SYSTEM_PROMPT)
- SEARCH_PLANNER_WIRE_V1 в process_ai_task

### 4. Архитектурное обсуждение Stage 1
Три позиции: ChatGPT (8 модулей сразу), третий участник (pipeline/state machine), Claude (поэтапно). Финальный синтез — FULLFIX_DIRECTION_KERNEL_STAGE_1 как минимальный shadow-mode слой.

См. docs/ARCHITECTURE/STAGE_1_DIRECTION_KERNEL_PROPOSAL.md

## ERRORS И ИХ ИСПРАВЛЕНИЕ
- EXCEPT_ANCHOR_NOT_FOUND в engine_base — auto-fallback на artifact_upload_guard
- GUARD_ANCHOR_NOT_FOUND — потребовал второй проход через TG_FALLBACK_WIRED
- Scoring mismatch в первом draft DirectionRegistry — исправлен strong_aliases + specificity bonus

## PENDING
- Stage 1 Direction Kernel — код готов, ждёт явного запуска
- §19 LIVE VERIFICATION 9 сценариев — не проводилось
- KZH PDF live test — не проводилось
- Excel формулы =C2*D2 live test — не проводилось

## DECISIONS СЕССИИ
1. Stage 1 в shadow-mode (не переносим execution)
2. 26 направлений в YAML, 13 active / 13 passive
3. Score-based detection с strong_aliases override
4. Tarball для скачивания на Mac → Drive вручную
5. Три параллельных артефакта: GitHub чистый / сервер полный / tarball

## SECRETS
В этом файле — нет. Полная версия со всеми секретами в /root/BACKUPS/areal-neva-core/full_export_2026-04-30_evening/

====================================================================================================
END_FILE: chat_exports/CHAT_EXPORT__claude_orchestra__2026-04-30_evening.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/CHAT_EXPORT__claude_session_01_05_2026_FIXES__2026-05-01.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 9b9612745e73cd4dafbc64fccf05823cc22a88edb0f99d9661ebb115b94b5c22
====================================================================================================
{
  "chat_id": "claude_session_01_05_2026_FIXES",
  "chat_name": "AREAL-NEVA ORCHESTRA — Claude Session 01.05.2026 FIXES",
  "exported_at": "2026-05-01T15:00:00+03:00",
  "source_model": "Claude Sonnet 4.6",
  "patches_verified": [
    "HOTFIX_FILE_NAME_EARLY_V1 — task_worker.py — file_name до TASK_TYPE_DETECT_V1 — VERIFIED",
    "HOTFIX_OK_BEFORE_SIZE_CHECK_V1 — task_worker.py — ok = _download перед FILE_SIZE_LIMIT — VERIFIED",
    "TOPIC_META_LOADER_V1_IMPORT — task_worker.py — импорт topic_meta_loader — VERIFIED",
    "TOPIC_META_ROLE_INJECT_V1 — task_worker.py — topic_role из meta.json — VERIFIED",
    "WHAT_IS_THIS_META_V1 — task_worker.py — ответ на кто ты из meta.json — VERIFIED",
    "SCOPE_FULL_V2 — core/topic_drive_oauth.py — drive.file → drive — VERIFIED",
    "SCOPE_FULL_V2 — core/drive_folder_resolver.py — drive.file → drive — VERIFIED"
  ],
  "root_cause": "TOPIC_AUTODISCOVERY_V2 + TOPIC_NAMING_24H коммиты вставили TASK_TYPE_DETECT_V1 и FILE_SIZE_LIMIT_V1 в task_worker.py используя переменные file_name и ok до их присвоения",
  "key_decisions": [
    "task_worker.py только правится — запрещённые файлы не тронуты",
    "topic_meta_loader.py подключён через try/except — безопасный импорт",
    "SCOPE_FULL drive вместо drive.file в обоих oauth файлах",
    "11 топиков синхронизированы в data/topics/*/meta.json через TOPIC_SYNC_FULL_V1"
  ],
  "topics_synced": [
    {"topic_id": 0, "name": "ЛИДЫ АМО", "direction": "crm_leads"},
    {"topic_id": 2, "name": "СТРОЙКА", "direction": "estimates"},
    {"topic_id": 5, "name": "ТЕХНАДЗОР", "direction": "technical_supervision"},
    {"topic_id": 11, "name": "ВИДЕОКОНТЕНТ", "direction": "video_production"},
    {"topic_id": 210, "name": "ПРОЕКТИРОВАНИЕ", "direction": "structural_design"},
    {"topic_id": 500, "name": "ВЕБ ПОИСК", "direction": "internet_search"},
    {"topic_id": 794, "name": "НЕЙРОНКИ СОФТ ВПН ВПС", "direction": "devops_server"},
    {"topic_id": 961, "name": "АВТО ЗАПЧАСТИ", "direction": "auto_parts_search"},
    {"topic_id": 3008, "name": "КОДЫ МОЗГОВ", "direction": "orchestration_core"},
    {"topic_id": 4569, "name": "ЛИДЫ РЕКЛАМА", "direction": "crm_leads"},
    {"topic_id": 6104, "name": "РАБОТА ПОИСК", "direction": "job_search"}
  ],
  "services": {
    "areal-task-worker": "active",
    "telegram-ingress": "active",
    "areal-memory-api": "active"
  },
  "not_closed": [
    "invalid_scope на Drive upload при analyze — SCOPE_FULL_V2 применён, тест pending",
    "detect_intent() takes 1 arg — warning, не блокирует обработку",
    "Голосовой confirm при AWAITING_CONFIRMATION — telegram_daemon.py ~601",
    "FULLFIX_DIRECTION_KERNEL Stage 2 dispatch — execution_plan не используется реально"
  ],
  "lessons": [
    "TOPIC_AUTODISCOVERY коммиты вставили код с forward reference на переменные",
    "Всегда проверять якорь в файле перед патчем — NOT_FOUND = неверный якорь",
    "SCOPE drive.file не позволяет создавать папки — нужен scope drive"
  ]
}

====================================================================================================
END_FILE: chat_exports/CHAT_EXPORT__claude_session_01_05_2026_FIXES__2026-05-01.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/CHAT_EXPORT__claude_session_29_04_2026__2026-04-29.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: bfb57e11d657b3bae5df3f09d3b4355f29f1706ced1b15bd81c4305a83ac9939
====================================================================================================
{
  "chat_id": "claude_session_29_04_2026",
  "chat_name": "AREAL-NEVA ORCHESTRA — Claude Session 28-29.04.2026",
  "exported_at": "2026-04-29T01:45:00+03:00",
  "source_model": "Claude Sonnet 4.6",
  "system": "AREAL-NEVA ORCHESTRA Ubuntu 24.04 89.22.225.136 /root/.areal-neva-core",
  "architecture": "Telegram → telegram_daemon.py → core.db → task_worker.py → ai_router.py → OpenRouter → reply_sender.py → Telegram",
  "pipeline": "NEW → INTAKE → IN_PROGRESS → RESULT_READY → AWAITING_CONFIRMATION → DONE → ARCHIVED",
  "patches": [
    "FIX_VOICE_GUARD_20260428 → telegram_daemon.py:961 → word-boundary → SYNTAX_OK active",
    "FIX_IS_SEARCH_20260428 → task_worker.py:2266 → is_search в payload → SYNTAX_OK active",
    "FIX_SEARCH_CONTEXT_20260428 → task_worker.py:2248 → clear search_context → SYNTAX_OK active",
    "FIX_VOICE_REVISION_V2 → telegram_daemon.py:880+ → empty revision fix → SYNTAX_OK active",
    "FIX_VOICE_CONFIRM_IN_PROGRESS → telegram_daemon.py:560 → голос confirm → SYNTAX_OK active",
    "FIX_CRASHLOOP_3981 → task_worker.py:3981 → NameError p=__file__ → SYNTAX_OK active",
    "FIX_CP8_ERROR_CLOSE → task_worker.py → estimate errors → FAILED не повисают → SYNTAX_OK active",
    "FIX_CP8_SEARCH_TYPE → task_worker.py → input_type search → CP8 estimate hook → SYNTAX_OK active",
    "FIX_EMPTY_AI_RETRY → task_worker.py:2297 → retry 3x при chars=0 → SYNTAX_OK active",
    "FIX_DRIVE_OAUTH → task_worker.py:2569 → _download_from_drive_oauth token.json → SYNTAX_OK active",
    "FIX_ENV_EXPORT → .env:16 → убран export GITHUB_TOKEN → active"
  ],
  "what_working": [
    "areal-task-worker active NRestarts=0",
    "telegram-ingress active",
    "areal-memory-api active",
    "Смета текстом из topic_500 → ответ ✅",
    "Голос revision ✅",
    "GitHub SSOT → 3 канона + 40 chat_exports + HANDOFF + PROTOCOL",
    "context_aggregator.py → ONE_SHARED_CONTEXT.md ✅ 47 файлов",
    "Drive OAuth token.json ✅"
  ],
  "what_not_done": [
    "Смета → Excel файл на Drive (не протестировано)",
    "КЖ PDF pipeline",
    "Дублирование ответа в разные топики",
    "Голос 00:02-00:04 → revision вместо confirm",
    "Нормы СП/ГОСТ в technadzor_engine",
    "Шаблоны, multi-file"
  ],
  "current_breakpoint": "Все патчи applied. Завтра тест: смета Excel на Drive, КЖ PDF, дублирование",
  "github": {
    "repo": "rj7hmz9cvm-lgtm/areal-neva-core",
    "files": [
      "docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md",
      "docs/ARCHITECTURE/SEARCH_MONOLITH_V1.md",
      "docs/ARCHITECTURE/ORCHESTRA_MASTER_BLOCK.md",
      "docs/HANDOFFS/LATEST_HANDOFF.md",
      "docs/HANDOFFS/CHAT_EXPORT_PROTOCOL.md",
      "docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md",
      "chat_exports/ (40 файлов)",
      "tools/context_aggregator.py",
      "tools/secret_scan.sh"
    ]
  },
  "db": "ARCHIVED 371 | DONE 98 | CANCELLED 165 | FAILED 60",
  "services": ["areal-task-worker: active", "telegram-ingress: active", "areal-memory-api: active"],
  "state": "Система стабильна. Все патчи applied. GitHub SSOT настроен. Тест завтра."
}

====================================================================================================
END_FILE: chat_exports/CHAT_EXPORT__claude_session_29_04_2026__2026-04-29.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/CHAT_EXPORT__claude_session_29_04_2026_v2__2026-04-29.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: daa4ba0443e9fac1ff0842ef376e7be95ae893128908720a0e8e859a24dd9edd
====================================================================================================
{
  "chat_id": "claude_session_29_04_2026_v2",
  "chat_name": "AREAL-NEVA ORCHESTRA — Claude Session 29.04.2026 v2",
  "exported_at": "2026-04-29T16:00:00+03:00",
  "source_model": "Claude Sonnet 4.6",
  "decisions": [
    "project_engine.py — новый файл, разрешение получено 29.04.2026",
    "Орик разрабатывает проектную документацию КЖ/КМ/АР по ГОСТ/СНиП/СП",
    "Шаблоны пользователя — основа для генерации разделов",
    "Python создаёт файлы, LLM не считает цифры",
    "Промпт v8 обновлён — heredoc обязателен, монолитные блоки, запрет повторных запросов"
  ],
  "not_closed": [
    "AVAILABILITY_CHECK","CONTACT_VALIDATION","STALE_CONTEXT_GUARD",
    "NEGATIVE_SELECTION","SOURCE_TRACE",
    "PROJECT_SECTION_DETECTOR","PROJECT_STRUCTURE_BUILDER",
    "NORMATIVE_SEARCH_ENGINE","PROJECT_ARTIFACT_GENERATOR",
    "PROJECT_CALC_ENGINE","METAL_STRUCTURE_ENGINE",
    "PROJECT_RESULT_GUARD","PROJECT_VALIDATOR",
    "PROJECT_TEMPLATE_ENGINE","TEMPLATE_LEARN","TEMPLATE_PRIORITY_RULE",
    "ERROR_GUARD_PROJECT","OUTPUT_DECISION_LOGIC",
    "UNIT_STANDARDIZATION","SPECIFICATION_FORMAT","VERSIONING"
  ]
}

====================================================================================================
END_FILE: chat_exports/CHAT_EXPORT__claude_session_29_04_2026_v2__2026-04-29.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/CHAT_EXPORT__claude_session_29_04_2026_v3__2026-04-29.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: ee06dacc65448b748034d32d24276fde1fe70edaa84b194d017f93e23601da64
====================================================================================================
{
  "chat_id": "claude_session_29_04_2026_v3",
  "chat_name": "AREAL-NEVA ORCHESTRA — Claude Session 29.04.2026 v3 FINAL",
  "exported_at": "2026-04-29T17:00:00+03:00",
  "source_model": "Claude Sonnet 4.6",
  "patches_installed": [
    "PIPELINE_INTEGRATION_V40 — task_worker.py — SYNTAX_OK active",
    "PIPELINE_INTEGRATION_V41 — task_worker.py — SYNTAX_OK active",
    "FILE_INTAKE_PROJECT_V41 — file_intake_router.py — SYNTAX_OK active",
    "ESTIMATE_QUALITY_V41 — estimate_engine.py — SYNTAX_OK active",
    "TEMPLATE_SYSTEM_V41 — template_manager.py — SYNTAX_OK active",
    "PROJECT_ENGINE_V1 — core/project_engine.py — создан SYNTAX_OK",
    "CLARIFICATION_UI — get_clarification_message + Проектирование пункт"
  ],
  "p1_bug_confirmed": {
    "bug": "SHORT_VOICE_CONFIRM_WIRED",
    "file": "telegram_daemon.py:601",
    "symptom": "голос 00:02-00:04 при AWAITING_CONFIRMATION → revision вместо confirm",
    "root_cause": "_all_contours_short_voice_confirm перехватывает до STT результата",
    "fix_needed": "читать STT текст → да/ок/принято → confirm, иначе revision"
  },
  "not_closed_live_test": [
    "Смета PDF → Excel → Drive",
    "КЖ PDF pipeline",
    "DWG → Excel → Drive",
    "Фото дефекта → акт",
    "Шаблон → новый файл",
    "project_engine end-to-end",
    "Поиск с постпроцессингом"
  ],
  "decisions": [
    "project_engine.py — разрешение получено 29.04.2026",
    "detect_intent не переопределять — пользователь выбирает через clarification",
    "Орик спрашивает Смета/Проектирование/Распознать — ждёт ответа",
    "Python создаёт файлы LLM не считает цифры",
    "Без артефакта FAILED Без ссылки FAILED"
  ],
  "prompt_v8": "Обновлён — heredoc обязателен, монолитные блоки, запрет повторных запросов, структура сервера CANON_FINAL/"
}

====================================================================================================
END_FILE: chat_exports/CHAT_EXPORT__claude_session_29_04_2026_v3__2026-04-29.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/CHAT_EXPORT__claude_session_29_04_2026_v4__2026-04-29.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 02c66460abc20112a90d6b0e1aa723d5bc4d9748bcdeb06796bfbb8a8ee68983
====================================================================================================
{
  "chat_id": "claude_session_29_04_2026_v4",
  "chat_name": "AREAL-NEVA ORCHESTRA — Claude Session 29.04.2026 FINAL",
  "exported_at": "2026-04-29T17:30:00+03:00",
  "source_model": "Claude Sonnet 4.6",
  "patches_installed": [
    "PIPELINE_INTEGRATION_V40 — task_worker.py — SYNTAX_OK active",
    "PIPELINE_INTEGRATION_V41 — task_worker.py — SYNTAX_OK active",
    "FILE_INTAKE_PROJECT_V41 — file_intake_router.py — SYNTAX_OK active",
    "ESTIMATE_QUALITY_V41 — estimate_engine.py — SYNTAX_OK active",
    "TEMPLATE_SYSTEM_V41 — template_manager.py — SYNTAX_OK active",
    "PROJECT_ENGINE_V1 — core/project_engine.py — создан SYNTAX_OK",
    "CLARIFICATION_UI — get_clarification_message + Проектирование/Расчёт нагрузок",
    "VOICE_CONFIRM_EMPTY_REVISION_FIX_V42 — telegram_daemon.py — SYNTAX_OK active",
    "search_session TABLE — core.db + memory.db"
  ],
  "services": {
    "telegram-ingress": "active",
    "areal-task-worker": "active",
    "bot": "@ai_orkestra_all_bot started 16:38:18"
  },
  "decisions": [
    "detect_intent не переопределять — пользователь выбирает через clarification",
    "Орик спрашивает Смета/Проектирование/Распознать — ждёт ответа пользователя",
    "project_engine.py — разрешение получено 29.04.2026",
    "Python создаёт файлы LLM не считает цифры",
    "Без артефакта FAILED Без ссылки FAILED",
    "Нормы не придумывать — только СП/ГОСТ/СНиП через Perplexity"
  ],
  "not_closed_live_test": [
    "Голосовой confirm при AWAITING_CONFIRMATION",
    "Смета PDF → Excel → Drive",
    "КЖ PDF pipeline",
    "DWG → Excel → Drive",
    "Фото дефекта → акт",
    "project_engine end-to-end",
    "Поиск с постпроцессингом V41"
  ],
  "prompt_v8": "Обновлён — heredoc обязателен, монолитные блоки, запрет повторных запросов, CANON_FINAL/ структура сервера"
}

====================================================================================================
END_FILE: chat_exports/CHAT_EXPORT__claude_session_29_04_2026_v4__2026-04-29.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/CHAT_EXPORT__claude_session_29_04_2026_v5__2026-04-29.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 50322e4673f34525a8f9dd9d9340e25fcb19cd799bd928e9fc7dad51374eb08c
====================================================================================================
{
  "chat_id": "claude_session_29_04_2026_v5",
  "chat_name": "AREAL-NEVA ORCHESTRA — Claude Session 29.04.2026 FINAL V5",
  "exported_at": "2026-04-29T23:00:14.611516",
  "source_model": "Claude Sonnet 4.6",
  "patches_installed": [
    "TECHNADZOR_RU_NORMS_V39 — core/technadzor_engine.py — SYNTAX_OK active",
    "FILE_INTAKE_KM_V39 — core/file_intake_router.py — SYNTAX_OK active",
    "DWG_EZDXF_V39 — core/dwg_engine.py — SYNTAX_OK active",
    "ESTIMATE_V39_HELPERS — core/estimate_engine.py — SYNTAX_OK active",
    "TASK_WORKER_V39_HELPERS — task_worker.py — SYNTAX_OK active",
    "MONITOR_HISTORY_V39 — monitor_jobs.py — SYNTAX_OK active",
    "SEARCH_POSTPROCESS_WIRED — task_worker.py:2348 — SYNTAX_OK active",
    "DUPLICATE_GUARD_WIRED — task_worker.py INSERT INTO tasks — SYNTAX_OK active",
    "REGION_WIRED — task_worker.py payload — SYNTAX_OK active",
    "TOPIC_MISMATCH_GUARD — task_worker.py — SYNTAX_OK active",
    "SEARCH_DEPTH_LIMIT — task_worker.py — SYNTAX_OK active",
    "PRICE_AGING — task_worker.py — SYNTAX_OK active",
    "OUTPUT_DECISION_LOGIC — task_worker.py — SYNTAX_OK active",
    "TRUST_RISK_SCORE — task_worker.py — SYNTAX_OK active",
    "SHORT_VOICE_CONFIRM_WIRED — telegram_daemon.py — SYNTAX_OK active",
    "AI_ROUTER_RU_PROMPT — core/ai_router.py — SYNTAX_OK active",
    "search_session TABLE — core.db + memory.db — OK",
    "retry_worker.py, media_group.py, context_engine.py, delivery.py, startup_recovery.py — CREATED"
  ],
  "not_closed": [
    "Голосовой confirm при AWAITING_CONFIRMATION — live-тест не проводился",
    "Смета PDF -> Excel -> Drive — live-тест не проводился",
    "КЖ PDF pipeline end-to-end — live-тест не проводился",
    "DWG -> Excel -> Drive — live-тест не проводился",
    "project_engine end-to-end через Telegram — live-тест не проводился"
  ],
  "services": {
    "areal-task-worker": "active",
    "telegram-ingress": "active",
    "areal-memory-api": "active"
  },
  "confirmed_by_terminal": [
    "SYNTAX_OK все файлы",
    "active NRestarts=0",
    "BOT STARTED id=8216054898"
  ]
}
====================================================================================================
END_FILE: chat_exports/CHAT_EXPORT__claude_session_29_04_2026_v5__2026-04-29.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/CHAT_EXPORT__claude_session_30_04_2026_FINAL__2026-04-30.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 7581dd230cfb4e31dcc42afcb45c084ea5069f142628cbbeb98220d26bd815bd
====================================================================================================
{
  "chat_id": "claude_session_30_04_2026_FINAL",
  "chat_name": "AREAL-NEVA ORCHESTRA — Claude Session 30.04.2026 FINAL",
  "exported_at": "2026-04-30T05:40:00+03:00",
  "source_model": "Claude Sonnet 4.6",
  "session_duration_hours": 8,
  "patches_total": 25,
  "patches_verified": [
    "PATCH_FILE_INTAKE_NEEDS_CONTEXT_V3_MINIMAL",
    "PATCH_DRIVE_GUARD_BEFORE_DOWNLOAD_V1",
    "PATCH_WORKER_PICK_BEFORE_STALE_V1",
    "PATCH_FIX_PFIN3_MENU_SHADOW_V1",
    "PATCH_FILE_CHOICE_PRIORITY_V1",
    "PATCH_FILE_PARENT_STRICT_OPEN_ONLY_V1",
    "PATCH_ENGINE_BASE_RESTORE_SA_UPLOAD_V1",
    "PATCH_DRIVE_DIRECT_OAUTH_V1",
    "PATCH_DRIVE_UPLOAD_AND_TG_FALLBACK_V1",
    "PATCH_RETRY_TOPIC_FOLDER_V1",
    "PATCH_DAEMON_OAUTH_OVERRIDE_V1",
    "PATCH_SCOPE_FULL_V1"
  ],
  "patches_installed_no_live_test": [
    "PATCH_DOWNLOAD_OAUTH_V1",
    "PATCH_SOURCE_GUARD_V1",
    "PATCH_FILE_ERROR_RETRY_V1",
    "PATCH_DRIVE_BOTMSG_SAVE_V1",
    "PATCH_DRIVE_DOWNLOAD_FAIL_MSG_V1",
    "PATCH_CRASH_BOTMSG_V1",
    "PATCH_RETRY_TG_MSG_V1",
    "PATCH_HC_NO_UPLOAD",
    "PATCH_DAEMON_USE_OAUTH_V1",
    "PATCH_VOICE_OAUTH_V1",
    "PATCH_DUPLICATE_GUARD_V1",
    "PATCH_MULTI_FILE_INTAKE_V1",
    "PATCH_LINK_INTAKE_NEEDS_CONTEXT_V1"
  ],
  "key_decisions_chronological": [
    "OAuth app переведён в Production",
    "engine_base.py восстановлен из bak",
    "Direct OAuth заменил Service Account",
    "Telegram fallback при упавшем Drive",
    "upload_retry_queue cron 10min",
    "retry в topic папку не INGEST",
    "healthcheck через list API",
    "Source guard для не-telegram файлов",
    "File error retry на reply",
    "Расширенный retry поиск (bot_message_id + reply_to + tg_msg_id)",
    "Crash bot_message_id save",
    "Daemon OAuth override.conf",
    "Daemon переключен на upload_file_to_topic",
    "Voice через OAuth",
    "Scope full=drive в 3 файлах (РЕШИЛ invalid_scope)"
  ],
  "key_lessons": [
    "Service Account не работает с My Drive — только OAuth",
    "Refresh token и scope должны совпадать иначе invalid_scope",
    "systemd Environment не наследуется — override.conf для каждого сервиса",
    "bot_message_id критичен для retry",
    "AI router цепляет stale задачи — нужна чистка",
    "drive_ingest подхватывает healthcheck — нужен list API",
    "STT Whisper галлюцинирует имена (Олег вместо Илья)"
  ],
  "new_canon_rules": {
    "0.11": "Самопроверка AI обязательна",
    "drive_folder_isolation": "Артефакты только в chat_{id}/topic_{id}/",
    "retry_chain": "TG → cron retry → topic папка",
    "source_guard": "Только source=telegram обрабатывается",
    "error_retry": "Reply на ошибку = автоматический перезапуск",
    "scope_full": "OAuth scope=drive (не drive.file) во всех файлах"
  },
  "services_at_end": {
    "areal-task-worker": "active",
    "telegram-ingress": "active",
    "areal-memory-api": "active"
  }
}
====================================================================================================
END_FILE: chat_exports/CHAT_EXPORT__claude_session_30_04_2026_FINAL__2026-04-30.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/CHAT_EXPORT__claude_session_30_04_2026_final__2026-04-30.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 9d9a6413946071b18dead80d5e3e3c967092b0ea741a7d87971f4fc4b2787517
====================================================================================================
{
  "chat_id": "claude_session_30_04_2026_final",
  "chat_name": "AREAL-NEVA ORCHESTRA — Claude Session 30.04.2026 FINAL",
  "exported_at": "2026-04-30T04:15:00+03:00",
  "source_model": "Claude Sonnet 4.6",
  "patches_verified": [
    "PATCH_FILE_INTAKE_NEEDS_CONTEXT_V3_MINIMAL — task_worker.py — VERIFIED",
    "PATCH_DRIVE_GUARD_BEFORE_DOWNLOAD_V1 — task_worker.py — VERIFIED",
    "PATCH_WORKER_PICK_BEFORE_STALE_V1 — task_worker.py — VERIFIED",
    "PATCH_FIX_PFIN3_MENU_SHADOW_V1 — task_worker.py — VERIFIED",
    "PATCH_FILE_CHOICE_PRIORITY_V1 — task_worker.py — VERIFIED",
    "PATCH_FILE_PARENT_STRICT_OPEN_ONLY_V1 — task_worker.py — VERIFIED",
    "PATCH_ENGINE_BASE_RESTORE_SA_UPLOAD_V1 — core/engine_base.py — VERIFIED",
    "PATCH_DRIVE_DIRECT_OAUTH_V1 — core/engine_base.py — VERIFIED",
    "PATCH_DRIVE_UPLOAD_AND_TG_FALLBACK_V1 — task_worker.py — VERIFIED",
    "core/upload_retry_queue.py + cron 10min — VERIFIED",
    "core/telegram_artifact_fallback.py — VERIFIED",
    "OAuth app In Production — VERIFIED",
    "override.conf fix — VERIFIED",
    "Stale test tasks cancelled — DONE"
  ],
  "patches_installed": [
    "PATCH_DUPLICATE_GUARD_V1 — task_worker.py — INSTALLED",
    "PATCH_MULTI_FILE_INTAKE_V1 — task_worker.py — INSTALLED",
    "PATCH_LINK_INTAKE_NEEDS_CONTEXT_V1 — task_worker.py — INSTALLED",
    "core/duplicate_guard.py — INSTALLED",
    "core/multi_file_intake.py — INSTALLED",
    "core/storage_adapter.py — INSTALLED",
    "core/storage_healthcheck.py — INSTALLED",
    "core/runtime_cleanup.py — INSTALLED",
    "tools/canon_updater.py — INSTALLED"
  ],
  "new_architecture_rules": {
    "drive_upload": "Direct OAuth primary → TG fallback → retry queue 10min",
    "file_task_isolation": "parent lookup только NEEDS_CONTEXT, topic_id=0 без cross-topic fallback",
    "storage_resilience": "Drive fail → TG → retry восстанавливает Drive upload автоматически",
    "server_storage": "Сервер НЕ постоянное хранилище — артефакты удаляются после выдачи",
    "cron_jobs": [
      "context_aggregator.py — каждые 30 минут",
      "upload_retry_queue.py — каждые 10 минут",
      "storage_healthcheck.py — каждые 30 минут"
    ]
  },
  "key_incidents": [
    "engine_base.py отсутствовал — восстановлен из core.bak.before_rollback_20260427_202634",
    "Service Account storageQuotaExceeded — переключились на Direct OAuth",
    "OAuth token протухал — приложение переведено в Production mode",
    "override.conf GDRIVE_REFRESH_TOKEN без закрывающей кавычки — исправлено",
    "task_history колонка action не event — исправлено до запуска"
  ],
  "services": {
    "areal-task-worker": "active",
    "telegram-ingress": "active",
    "areal-memory-api": "active"
  },
  "not_closed_p1": [
    "Голосовой confirm при AWAITING_CONFIRMATION — telegram_daemon.py:601",
    "DUPLICATE_GUARD live-тест",
    "MULTI_FILE live-тест",
    "LINK_INTAKE live-тест"
  ]
}
====================================================================================================
END_FILE: chat_exports/CHAT_EXPORT__claude_session_30_04_2026_final__2026-04-30.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/CHAT_EXPORT__claude_session_30_04_2026_v2__2026-04-30.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: be1be754218a969a632469249c5371ce25591ab5f1604e16fb31953e69bcf565
====================================================================================================
{
  "chat_id": "claude_session_30_04_2026_v2",
  "chat_name": "AREAL-NEVA ORCHESTRA — Claude Session 30.04.2026 V2 FINAL",
  "exported_at": "2026-04-30T04:30:00+03:00",
  "source_model": "Claude Sonnet 4.6",
  "patches_verified": [
    "PATCH_FILE_INTAKE_NEEDS_CONTEXT_V3_MINIMAL — VERIFIED",
    "PATCH_DRIVE_GUARD_BEFORE_DOWNLOAD_V1 — VERIFIED",
    "PATCH_WORKER_PICK_BEFORE_STALE_V1 — VERIFIED",
    "PATCH_FIX_PFIN3_MENU_SHADOW_V1 — VERIFIED",
    "PATCH_FILE_CHOICE_PRIORITY_V1 — VERIFIED",
    "PATCH_FILE_PARENT_STRICT_OPEN_ONLY_V1 — VERIFIED",
    "PATCH_ENGINE_BASE_RESTORE_SA_UPLOAD_V1 — VERIFIED",
    "PATCH_DRIVE_DIRECT_OAUTH_V1 — VERIFIED",
    "PATCH_DRIVE_UPLOAD_AND_TG_FALLBACK_V1 — VERIFIED",
    "PATCH_RETRY_TOPIC_FOLDER_V1 — VERIFIED",
    "core/upload_retry_queue.py + cron 10min — VERIFIED",
    "OAuth app In Production — VERIFIED",
    "override.conf fix — VERIFIED",
    "Stale test tasks cancelled — DONE"
  ],
  "new_canon_rules": {
    "0.11": "Обязательная самопроверка AI перед и после кода — для любой нейросети",
    "drive_folder_isolation": "Артефакты только в chat_{id}/topic_{id}/, не в INGEST корень",
    "retry_upload_chain": "Drive FAIL → TG → cron 10min retry → topic папка → уведомление",
    "topic_auto_folder": "При новом топике папка создаётся автоматически через _ensure_folder"
  },
  "key_decisions": [
    "upload_retry_queue использует topic_drive_oauth._upload_file_sync не engine_base",
    "engine_base.upload_artifact_to_drive только для healthcheck и тестов",
    "drive.file scope достаточен для создания папок топиков",
    "task_history колонка называется action не event",
    "PYTHONPATH=/root/.areal-neva-core обязателен для cron скриптов"
  ],
  "services": {
    "areal-task-worker": "active",
    "telegram-ingress": "active",
    "areal-memory-api": "active"
  }
}
====================================================================================================
END_FILE: chat_exports/CHAT_EXPORT__claude_session_30_04_2026_v2__2026-04-30.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/CHAT_EXPORT__claude_session_30_04_2026_v3__2026-04-30.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e894f4f9ff692216ad4f3d1ac7cd5acda722a974965a76a60f0a23c1b2df4b07
====================================================================================================
{
  "chat_id": "claude_session_30_04_2026_v3",
  "chat_name": "AREAL-NEVA ORCHESTRA — Claude Session 30.04.2026 V3",
  "exported_at": "2026-04-30T04:45:00+03:00",
  "source_model": "Claude Sonnet 4.6",
  "patches_installed": [
    "PATCH_DOWNLOAD_OAUTH_V1 — _download_from_drive через OAuth не SA",
    "PATCH_SOURCE_GUARD_V1 — файлы не из Telegram → CANCELLED",
    "PATCH_FILE_ERROR_RETRY_V1 — reply на ошибку → перезапуск файла",
    "PATCH_HC_NO_UPLOAD — healthcheck через list API не upload"
  ],
  "key_decisions": [
    "Service Account не может скачивать файлы My Drive пользователя — только OAuth",
    "drive_ingest подхватывал healthcheck файлы — исправлено через list API",
    "Reply на ошибку обработки перезапускает файл автоматически",
    "source=google_drive файлы игнорируются — только source=telegram"
  ],
  "new_canon_rules": {
    "0.11": "Самопроверка AI обязательна перед и после кода",
    "source_guard": "Только файлы source=telegram проходят обработку",
    "error_retry": "Reply на ошибку = перезапуск, не повторная отправка файла",
    "download_oauth": "_download_from_drive использует OAuth scope=drive"
  }
}
====================================================================================================
END_FILE: chat_exports/CHAT_EXPORT__claude_session_30_04_2026_v3__2026-04-30.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/CHAT_EXPORT__github_ssot_technical_orchestra__2026-04-29.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 601e59d54b1f6c1380ddf09a665fecccd8369cf4f3973ff616252ca844a4a83f
====================================================================================================
{
  "chat_id": "UNKNOWN",
  "chat_name": "github_ssot_technical_orchestra",
  "exported_at": "2026-04-29T00:00:00+02:00",
  "source_model": "ChatGPT GPT-5.5 Thinking",
  "system": "AREAL-NEVA ORCHESTRA: сервер 89.22.225.136, base /root/.areal-neva-core, Telegram bot @ai_orkestra_all_bot, GitHub repo rj7hmz9cvm-lgtm/areal-neva-core, GitHub используется как SSOT для канонов и shared context, сервер используется как runtime, Google Drive оставлен как резерв и хранилище тяжёлых файлов",
  "architecture": "Telegram -> telegram_daemon/task_worker -> ai_router/OpenRouter/DeepSeek -> engines/Python -> validator -> HUMAN_DECISION_EDITOR -> Telegram. GitHub docs/CANON_FINAL и docs/SHARED_CONTEXT являются текстовым SSOT. Сервер хранит runtime, core.db, memory.db, обработку файлов. Drive не является главным мозгом",
  "pipeline": "Базовый lifecycle задач: NEW -> IN_PROGRESS -> AWAITING_CONFIRMATION -> DONE -> ARCHIVED. Для файлового контура целевой pipeline: INGESTED -> DOWNLOADED -> PARSED -> CLEANED -> NORMALIZED -> CALCULATED -> ARTIFACT_CREATED -> UPLOADED",
  "files": [
    "README.md -> описание GitHub SSOT",
    "docs/ARCHITECTURE/SEARCH_MONOLITH_V1.md -> канон интернет-поиска topic_500",
    "docs/CANON_FINAL/00_INDEX.md -> индекс канонов",
    "docs/HANDOFFS/LATEST_HANDOFF.md -> handoff состояния 28.04.2026",
    "docs/REPORTS/NOT_CLOSED.md -> незакрытые задачи",
    "docs/ARCHITECTURE/ORCHESTRA_MASTER_BLOCK.md -> master architecture block v1",
    "tools/context_aggregator.py -> заготовка агрегатора контекста",
    "tools/secret_scan.sh -> pre-commit secret scan",
    "runtime/.gitkeep -> заглушка runtime без хранения мусора",
    "/root/.areal-neva-core/task_worker.py -> worker, был crashloop из-за NameError p на строке 3981, исправлен терминалом"
  ],
  "code": "Python 3 venv /root/.areal-neva-core/.venv/bin/python3, SQLite core.db/memory.db, systemd services, GitHub API/git, Telegram, OpenRouter/DeepSeek, планируемые модели: Gemini, Mistral, Cerebras, Cohere, Perplexity, Cloudflare/HuggingFace fallback, Python engines для расчётов и файлов",
  "patches": [
    "INIT_GITHUB_SSOT_STRUCTURE -> GitHub repo -> README/docs/tools/runtime -> status: applied_by_terminal commit 21a0e95",
    "ORCHESTRA_MASTER_BLOCK_V1 -> docs/ARCHITECTURE/ORCHESTRA_MASTER_BLOCK.md -> status: applied_by_terminal commit 3e98117",
    "FIX_NAMEERROR_P_20260429 -> /root/.areal-neva-core/task_worker.py line 3981 -> status: applied_by_terminal, SYNTAX_OK, service active",
    "CONTEXT_AGGREGATOR_DRAFT -> /root/.areal-neva-core/tools/context_aggregator.py -> status: drafted in chat, terminal execution result not provided"
  ],
  "commands": [
    "ssh areal ... git clone repo, create docs/CANON_FINAL docs/SHARED_CONTEXT docs/ARCHITECTURE docs/HANDOFFS docs/REPORTS tools scripts runtime, write README, secret_scan, SEARCH_MONOLITH, handoff, NOT_CLOSED, context_aggregator stub, git commit/push",
    "bash tools/secret_scan.sh -> initial scan failed because patterns inside secret_scan.sh matched itself",
    "secret patterns moved to /root/.areal-neva-core/.secret_patterns, tools/secret_scan.sh committed and pushed",
    "git commit -m 'FIX: secret_scan паттерны вынесены из репо 28.04.2026' -> commit 21a0e95",
    "git commit -m 'ARCH: ORCHESTRA_MASTER_BLOCK v1 верифицировано Claude+GPT 28.04.2026' -> commit 3e98117",
    "diagnostic command checked journalctl, DB files, sqlite tables, worker direct start, grep DB paths",
    "patch command replaced open(p).read() with open(__file__, encoding='utf-8', errors='ignore').read() in task_worker.py line 3981",
    "py_compile task_worker.py -> SYNTAX_OK",
    "systemctl restart areal-task-worker -> active",
    "sqlite3 /root/.areal-neva-core/data/core.db 'SELECT count(*) FROM tasks;' -> 694"
  ],
  "db": "Факт диагностики: /root/.areal-neva-core/core.db существует, размер 0, tasks table отсутствует и считается мусором. Рабочая БД: /root/.areal-neva-core/data/core.db, таблицы drive_files, processed_updates, tasks, pin, task_history, templates, tasks_count=694. task_worker.py CORE_DB строка 30 указывает на /root/.areal-neva-core/data/core.db",
  "memory": "memory.db находится в /root/.areal-neva-core/data/memory.db, размер 728K по выводу терминала. Детальная проверка содержимого memory.db в этом чате не выполнялась",
  "services": [
    "areal-task-worker.service: active после FIX_NAMEERROR_P_20260429",
    "telegram-ingress.service: ранее active по диагностике пользователя",
    "areal-memory-api.service: ранее active по диагностике пользователя"
  ],
  "canons": [
    "GitHub SSOT: GitHub = мозг для канонов, shared context, handoff, reports, scripts; сервер = runtime; Drive = резерв и тяжёлые файлы",
    "GITHUB_SSOT_RULES: каноны не перетирать, только version/add, secret_scan обязателен, секреты/БД/логи/тяжёлые файлы не коммитить",
    "SEARCH_MONOLITH_V1: topic_500 работает как цифровой снабженец, не просто поиск ссылок; этапы включают Search Session, Review Trust Score, SELLER_RISK, TCO, живой рынок, technical audit",
    "ORCHESTRA_MASTER_BLOCK: три блока — technical file pipeline, multi-model orchestra layer, GitHub SSOT + aggregator",
    "Python считает и создаёт файлы, LLM анализирует и понимает смысл, финальный вывод проходит через validator и HUMAN_DECISION_EDITOR",
    "Все модели должны работать внутри оркестра, получать общий ORCHESTRA_SHARED_CONTEXT и не отвечать пользователю напрямую"
  ],
  "decisions": [
    "РЕШЕНИЕ -> перенести каноны и shared context в GitHub SSOT -> применено созданием структуры docs/* и push в main",
    "РЕШЕНИЕ -> Google Drive оставить резервом и хранилищем тяжёлых файлов -> применено в архитектуре",
    "РЕШЕНИЕ -> агрегатор пока отсутствует, временно человек вручную собирает монолит и пушит в GitHub -> применено как текущая схема",
    "РЕШЕНИЕ -> multi-model layer должен работать до финальной сборки DeepSeek/OpenRouter и иметь общий контекст -> применено в ORCHESTRA_MASTER_BLOCK",
    "РЕШЕНИЕ -> HUMAN_DECISION_EDITOR обязателен, чтобы технический мусор переводился в человеческое решение -> применено в master block"
  ],
  "errors": [
    "SECRET_SCAN false positive -> secret_scan.sh ловил собственные паттерны sk-ant/sk-or/ghp_ -> паттерны вынесены в /root/.areal-neva-core/.secret_patterns, commit 21a0e95",
    "GITHUB_TOKEN leaked in chat/terminal text -> причина: токен был вставлен открытым текстом -> решение: токен должен быть отозван и заменён, в коде использовать env only",
    "areal-task-worker crashloop -> причина: task_worker.py line 3981 NameError name 'p' is not defined -> решение: заменить open(p).read() на open(__file__, encoding='utf-8', errors='ignore').read(), SYNTAX_OK, service active",
    "no such table: tasks -> причина: sqlite3 смотрел в пустой /root/.areal-neva-core/core.db -> решение: подтверждено что worker использует /root/.areal-neva-core/data/core.db, пустой core.db не трогать",
    ".env invalid environment assignment -> причина: строка export GITHUB_TOKEN=<REDACTED_SECRET> в .env невалидна для systemd EnvironmentFile -> решение: заменить на GITHUB_TOKEN=<REDACTED_SECRET> и ротировать токен"
  ],
  "solutions": [
    "ПРОБЛЕМА -> ручная передача контекста между чатами -> РЕШЕНИЕ -> GitHub SSOT + ONE_SHARED_CONTEXT + будущий aggregator -> СТАТУС -> структура GitHub создана, aggregator не реализован",
    "ПРОБЛЕМА -> много моделей могут создать хаос -> РЕШЕНИЕ -> MODEL_ROUTER, MODEL_REGISTRY, FALLBACK_CHAIN, ORCHESTRA_SHARED_CONTEXT, PRE_OPENROUTER_MODEL_LAYER -> СТАТУС -> зафиксировано в ORCHESTRA_MASTER_BLOCK",
    "ПРОБЛЕМА -> технический контур должен работать с PDF/XLSX/CSV/PNG/JPG/DWG/DXF -> РЕШЕНИЕ -> TECHNICAL_FILE_PIPELINE 8 стадий + engines + FILE_RESULT_GUARD -> СТАТУС -> архитектура зафиксирована, полная реализация не подтверждена",
    "ПРОБЛЕМА -> пользователю не нужен технический мусор -> РЕШЕНИЕ -> HUMAN_DECISION_EDITOR + USER_MODE_SWITCH -> СТАТУС -> зафиксировано в master block",
    "ПРОБЛЕМА -> task_worker crashloop -> РЕШЕНИЕ -> точечный patch line 3981 -> СТАТУС -> active, tasks_count 694"
  ],
  "state": "GitHub SSOT структура создана и запушена; ORCHESTRA_MASTER_BLOCK v1 запушен; task_worker crashloop по NameError p исправлен; агрегатор контекста пока только в ТЗ/драфте и должен быть реализован следующим шагом",
  "what_working": [
    "GitHub push в main работает: commit 21a0e95 и 3e98117 подтверждены терминалом",
    "secret_scan после выноса паттернов показал SECRET_SCAN_OK",
    "areal-task-worker после патча task_worker.py line 3981 показал active",
    "py_compile task_worker.py показал SYNTAX_OK",
    "core.db рабочая БД /root/.areal-neva-core/data/core.db содержит tasks_count=694"
  ],
  "what_broken": [
    ".env содержит невалидную для systemd строку export GITHUB_TOKEN=<REDACTED_SECRET> по journalctl",
    "GITHUB_TOKEN был засвечен в чате/терминале и должен быть ротирован",
    "context_aggregator.py на сервере пока stub или draft, нет подтверждённого DONE: ONE_SHARED_CONTEXT pushed",
    "Drive/GitHub aggregator в полном виде не реализован"
  ],
  "what_not_done": [
    "docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md ещё не подтверждён как автоматически созданный агрегатором",
    "context_aggregator.py не подтверждён успешным запуском",
    "tools/watch_exports.py не создан",
    "TECHNICAL_FULL_CONTOUR не закрыт live-тестами для PDF/XLSX/CSV/PNG/JPG/DWG/DXF",
    "MODEL_ROUTER полный не реализован в коде",
    "RESULT_VALIDATOR, RESULT_FORMAT_ENFORCER, FILE_RESULT_GUARD, HUMAN_DECISION_EDITOR не подтверждены кодом",
    "FALLBACK_CHAIN и MODEL_REGISTRY не подтверждены кодом",
    "SEARCH_MONOLITH_V1 live-test не проводился"
  ],
  "current_breakpoint": "Следующее действие: реализовать и запустить /root/.areal-neva-core/tools/context_aggregator.py так, чтобы он создал docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md в GitHub и вывел DONE: ONE_SHARED_CONTEXT pushed; перед этим ротировать GITHUB_TOKEN и исправить .env без export",
  "root_causes": [
    "task_worker crashloop -> NameError p undefined on line 3981 -> подтверждение direct start traceback и patched context",
    "no such table tasks -> пустой /root/.areal-neva-core/core.db использовался в ручной проверке, не worker -> подтверждение CORE_DB line 30 and /root/.areal-neva-core/data/core.db tasks_count=694",
    "secret_scan initial fail -> script scanned its own secret pattern literals -> подтверждение SECRET FOUND lines before moving patterns out of repo"
  ],
  "verification": [
    "INIT_GITHUB_SSOT_STRUCTURE -> terminal output commit 21a0e95, push main -> main",
    "ORCHESTRA_MASTER_BLOCK -> terminal output commit 3e98117, create docs/ARCHITECTURE/ORCHESTRA_MASTER_BLOCK.md, push main -> main",
    "FIX_NAMEERROR_P_20260429 -> terminal output PATCH_OK, SYNTAX_OK, systemctl is-active active, tasks_count 694",
    "DB_PATH -> grep output task_worker.py line 30 CORE_DB = f'{BASE}/data/core.db'",
    "working DB -> sqlite output tables drive_files processed_updates tasks pin task_history templates and tasks_count 694",
    "secret_scan -> terminal output SECRET_SCAN_OK before commits"
  ],
  "limits": [
    "Не трогать .env без отдельного явного действия и ротации токена",
    "Не коммитить секреты, core.db, memory.db, logs, sessions, credentials, token files, heavy files",
    "Не трогать estimate_engine.py, file_intake_router.py, ai_router.py, reply_sender.py в рамках task_worker crashloop fix",
    "Файлы экспорта чата создавать только в chat_exports/",
    "Каноны не перетирать, только version/add",
    "Любой патч: backup -> patch -> py_compile -> restart -> logs -> DB/service check",
    "Неподтверждённое не писать как working"
  ]
}

====================================================================================================
END_FILE: chat_exports/CHAT_EXPORT__github_ssot_technical_orchestra__2026-04-29.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/HANDOFF__CLAUDE_TO_NEXT_AI__2026-04-27.txt
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 0e296e4868864602a55902aa28577033bf9a7a7531a4f125f94275529408538e
====================================================================================================
﻿AREAL-NEVA ORCHESTRA - SESSION HANDOFF 2026-04-27 02:10 MSK
SOURCE: Claude session 26-27.04.2026
FOR: Next AI - read this FIRST before any action


== SYSTEM STATE ==
Server: 89.22.225.136 Path: /root/.areal-neva-core
Services: areal-telegram-daemon PID 1566302 running since 01:37 (systemd shows inactive but process alive), areal-task-worker ACTIVE, areal-memory-api ACTIVE


== VOICE FIX APPLIED TODAY ==
ROOT CAUSE: telegram_daemon.py line 902-903 referenced CHAT_ONLY_PHRASES (NameError). CANON_PASS13 defined it at line 940 after main() runs.
FIX: sed -i 902-903 commented out with DISABLED_PASS13. Voice now works.


== BROKEN - FIX NEXT ==


P0 CONFIRMATION HANDLER:
- Da after Dovolet? creates NEW task instead of closing existing AWAITING_CONFIRMATION
- Canon 2.1 violation: CONFIRM must close task
- Canon 2.3 violation: reply to bot must NOT create new task
- FIX: grep -n _handle_control_text telegram_daemon.py, read function, verify bot_message_id lookup vs reply_to_message_id
- CHECK: sqlite3 data/core.db SELECT bot_message_id FROM tasks WHERE state=AWAITING_CONFIRMATION LIMIT 5


P1 CHAT INTENT AUTO-CLOSE:
- Conversational responses hang 600s STALE_TIMEOUT
- Fix: task_worker.py overlay after AI responds, if intent==CHAT immediately DONE


P2 DRIVE DOWNLOAD_FAILED:
- drive_file tasks fail DOWNLOAD_FAILED
- Check CANON_PASS3_REAL_DRIVEFILE_WIRING lines 2237-2403 task_worker.py


== KEY CODE LOCATIONS ==
telegram_daemon.py:
- Lines 10-23: CANON_PASS6 fcntl.flock lock
- Lines 902-903: DISABLED_PASS13 (commented out)
- Lines 940-950: CANON_PASS13 CHAT_ONLY_PHRASES def
task_worker.py:
- Line 47: _auto_close_trash_awaiting
- Line 1842: _auto_close_trash_awaiting called
- Lines 2237-2403: CANON_PASS3_REAL_DRIVEFILE_WIRING
- Lines 2573-2598: CANON_PASS6_LIVE_CORE_OVERLAY with _cp6_save_topic_directions


== API KEYS ==
WORKING: OpenRouter (DeepSeek+Perplexity), Google API
DEAD: Anthropic 401, OpenAI 429, Grok 403, DeepSeek 402, Groq 403


== DB STATE ==
AWAITING_CONFIRMATION: 45+, FAILED: 677, DONE: 24, ARCHIVED: 371


== CANON KEY RULES ==
2.1: FINISH>CONFIRM>REVISION>TASK>SEARCH>CHAT
2.3: Reply to bot = NO NEW TASK, find old task via bot_message_id
8.3: ok/ponyat/spasibo = CHAT, no new tasks
10.1: STALE_TIMEOUT=600s AI_TIMEOUT=300s


== DRIVE FOLDERS ==
Chat exports: 14bYA9bHaKahkE8d4IDwWxL4Ojn-G0sDl
CANON_FINAL: 1U_IrEOtIJfUVAdjH-kHwms2M2z3FXan0
Main canon: 1k_KIpQ7jD15_w83sMz4WfqoEIINIXTHTaTOtUovf2gU
====================================================================================================
END_FILE: chat_exports/HANDOFF__CLAUDE_TO_NEXT_AI__2026-04-27.txt
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/README.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 8b26ad697db3033319a6b8c9325a1b0d3699b4f4ab4bf5737933f7cbf7fc863e
====================================================================================================
# CHAT_EXPORTS — Выгрузки чатов

Сюда сохраняются все экспорты сессий.
Формат имени: CHAT_EXPORT__<имя>__<YYYY-MM-DD>.json
Папка только пополняется. Ничего не удалять, не перезаписывать.

====================================================================================================
END_FILE: chat_exports/README.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: chat_exports/ZAPROS_DLY_AI_AGENTOV_2026-04-27.txt
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 36bf345fa1f47863ccecd10e2c19246fb1fca79dcf8ef64b9a93d373397f3e33
====================================================================================================
﻿ZAPROS K AI-AGENTU — AREAL-NEVA ORCHESTRA
Data: 27.04.2026 09:10 MSK


TY OBYAZAN VYPOLNIT SLEDUYUSCHIE SHAGI PO PORYADKU:


1. Zaydi na Google Drive
2. Prochitay VSE fayly v papke CANON_FINAL id=1U_IrEOtIJfUVAdjH-kHwms2M2z3FXan0
3. Prochitay VSE fayly v papke vygruzki chatov id=14bYA9bHaKahkE8d4IDwWxL4Ojn-G0sDl
4. Glavnyy kanon: id=1k_KIpQ7jD15_w83sMz4WfqoEIINIXTHTaTOtUovf2gU
5. Posle prochteniya — zaydi na server SSH areal (89.22.225.136)
6. Prover zhivoe sostoyanie sistemy komandami nizhe
7. Day reshenie TOLKO po faktam


DIAGNOSTICHESKIE KOMANDY:
ssh areal 'bash -s' << 'ENDSSH'
cd /root/.areal-neva-core
sed -n '475,560p' telegram_daemon.py
sqlite3 data/core.db 'SELECT state, COUNT(*) FROM tasks GROUP BY state'
tail -30 logs/telegram_daemon.log
grep -n 'SHORT_CONFIRM\|CANCEL_PHRASES\|CHAT_ONLY\|FINISH_PHRASES' telegram_daemon.py | head -20
ENDSSH


FAKTY (tolko fakty, bez interpretatsii):
- Golosovye soobshcheniya v bolshinstve chatov: otvet 'Utochnite zapros'
- Polzovatel govorit 'Da' — bot ne vsegda zakryvaet zadachu
- Reply na soobshchenie bota — sozdaet novuyu zadachu vmesto prodolzheniya
- 'Dobryy vecher/ok/ponyat' — sozdaet zadachu vmesto prostogo otveta


DB sostoyanie: ARCHIVED 369, CANCELLED 154, DONE 31, FAILED 78, AWAITING_CONFIRMATION 0


TVOYA ZADACHA:
1. Prochti VSE kanony na Drive
2. Prochti VSE vygruzki chatov na Drive
3. Proydi po diagnosticheskim komandam
4. Day tochnye root cause + patch po kanonu
5. Prover chto patch ne narushaet ni odnogo pravila kanona


ZAPRESCHENO: gadat, predlagat bez proverki zhivogo koda, trogat .env credentials google_io.py ai_router.py reply_sender.py memory.db schema systemd
====================================================================================================
END_FILE: chat_exports/ZAPROS_DLY_AI_AGENTOV_2026-04-27.txt
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: config/directions.yaml
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 47e82fed54578b491775c7717e09542b35ecfa317ff3cdb067ea8c99dfeb90f2
====================================================================================================
{
  "version": "DIRECTION_REGISTRY_V1",
  "marker": "FULLFIX_DIRECTION_KERNEL_STAGE_1_DIRECTIONS",
  "directions": {
    "general_chat": {
      "title": "Общий чат",
      "enabled": true,
      "topic_ids": [],
      "aliases": [],
      "input_types": [
        "text",
        "voice"
      ],
      "input_formats": [
        "text"
      ],
      "output_formats": [
        "telegram_text"
      ],
      "engine": "ai_router",
      "requires_search": false,
      "quality_gates": [
        "non_empty_answer"
      ]
    },
    "orchestration_core": {
      "title": "Мозги оркестра",
      "enabled": true,
      "topic_ids": [
        3008
      ],
      "aliases": [
        "оркестр",
        "канон",
        "kernel",
        "workitem",
        "direction",
        "архитектур"
      ],
      "input_types": [
        "text",
        "voice",
        "file"
      ],
      "input_formats": [
        "text",
        "json",
        "md"
      ],
      "output_formats": [
        "telegram_text",
        "json",
        "md"
      ],
      "engine": "ai_router",
      "requires_search": false,
      "quality_gates": [
        "canon_consistency"
      ]
    },
    "telegram_automation": {
      "title": "Telegram automation",
      "enabled": true,
      "topic_ids": [],
      "aliases": [
        "bot_message_id",
        "message_thread_id",
        "telegram daemon"
      ],
      "input_types": [
        "text",
        "voice"
      ],
      "input_formats": [
        "text"
      ],
      "output_formats": [
        "telegram_text"
      ],
      "engine": "telegram_pipeline",
      "requires_search": false,
      "quality_gates": [
        "reply_thread_required"
      ]
    },
    "memory_archive": {
      "title": "Память и архив",
      "enabled": true,
      "topic_ids": [],
      "aliases": [
        "chat_exports",
        "выгрузк",
        "архив",
        "memory.db",
        "short_memory",
        "long_memory"
      ],
      "input_types": [
        "text",
        "file"
      ],
      "input_formats": [
        "text",
        "json",
        "md",
        "txt"
      ],
      "output_formats": [
        "telegram_text",
        "json"
      ],
      "engine": "context_search_archive_engine",
      "requires_search": false,
      "quality_gates": [
        "verified_sources_only"
      ]
    },
    "internet_search": {
      "title": "Интернет-поиск",
      "enabled": true,
      "topic_ids": [
        500
      ],
      "aliases": [
        "найд",
        "поиск",
        "перплексити",
        "в интернете"
      ],
      "input_types": [
        "text",
        "voice"
      ],
      "input_formats": [
        "text",
        "url"
      ],
      "output_formats": [
        "telegram_text",
        "table",
        "sources"
      ],
      "engine": "search_supplier",
      "requires_search": true,
      "quality_gates": [
        "sources_required"
      ]
    },
    "product_search": {
      "title": "Товарный поиск",
      "enabled": true,
      "topic_ids": [],
      "strong_aliases": [
        "avito",
        "ozon",
        "wildberries",
        "авито",
        "озон",
        "вб"
      ],
      "aliases": [
        "куп",
        "цен",
        "дешевл",
        "товар",
        "поставщик",
        "заказ"
      ],
      "input_types": [
        "text",
        "voice",
        "photo"
      ],
      "input_formats": [
        "text",
        "photo",
        "url"
      ],
      "output_formats": [
        "telegram_table",
        "json",
        "xlsx"
      ],
      "engine": "search_supplier",
      "requires_search": true,
      "quality_gates": [
        "price_required",
        "source_required",
        "tco_required"
      ]
    },
    "auto_parts_search": {
      "title": "Автозапчасти",
      "enabled": true,
      "topic_ids": [
        961
      ],
      "strong_aliases": [
        "drom",
        "auto.ru",
        "exist",
        "emex",
        "zzap",
        "brembo",
        "брембо",
        "дром"
      ],
      "aliases": [
        "авто",
        "запчаст",
        "фара",
        "рычаг",
        "суппорт",
        "oem",
        "разборк",
        "toyota",
        "hiace"
      ],
      "input_types": [
        "text",
        "voice",
        "photo"
      ],
      "input_formats": [
        "text",
        "photo",
        "url"
      ],
      "output_formats": [
        "telegram_table",
        "json"
      ],
      "engine": "search_supplier",
      "requires_search": true,
      "quality_gates": [
        "compatibility_required"
      ]
    },
    "construction_search": {
      "title": "Строительный поиск",
      "enabled": true,
      "topic_ids": [],
      "aliases": [
        "металлочерепиц",
        "профнастил",
        "газобетон",
        "утеплител",
        "арматур",
        "ral",
        "grand line",
        "петрович",
        "леруа"
      ],
      "input_types": [
        "text",
        "voice",
        "photo"
      ],
      "input_formats": [
        "text",
        "photo",
        "url"
      ],
      "output_formats": [
        "telegram_table",
        "xlsx"
      ],
      "engine": "search_supplier",
      "requires_search": true,
      "quality_gates": [
        "price_required",
        "delivery_required"
      ]
    },
    "technical_supervision": {
      "title": "Технадзор",
      "enabled": true,
      "topic_ids": [
        5
      ],
      "aliases": [
        "технадзор",
        "наруш",
        "дефект",
        "осмотр",
        "замечан",
        "снип",
        "гост"
      ],
      "input_types": [
        "text",
        "voice",
        "photo",
        "file"
      ],
      "input_formats": [
        "text",
        "photo",
        "pdf"
      ],
      "output_formats": [
        "telegram_text",
        "docx",
        "pdf"
      ],
      "engine": "defect_act",
      "requires_search": false,
      "quality_gates": [
        "defect_description_required",
        "normative_section_required"
      ]
    },
    "estimates": {
      "title": "Сметы",
      "enabled": true,
      "topic_ids": [
        2
      ],
      "aliases": [
        "смет",
        "расценк",
        "ведомост",
        "объем работ",
        "вор",
        "фер",
        "тер"
      ],
      "input_types": [
        "text",
        "voice",
        "file",
        "drive_file"
      ],
      "input_formats": [
        "text",
        "pdf",
        "xlsx",
        "csv",
        "photo"
      ],
      "output_formats": [
        "xlsx",
        "pdf",
        "drive_link",
        "telegram_text"
      ],
      "engine": "estimate_unified",
      "requires_search": false,
      "quality_gates": [
        "items_required",
        "total_required",
        "xlsx_required"
      ]
    },
    "defect_acts": {
      "title": "Акты дефектов",
      "enabled": true,
      "topic_ids": [],
      "aliases": [
        "акт дефект",
        "акт осмотр",
        "дефектный акт",
        "трещин",
        "протечк",
        "фото дефект"
      ],
      "input_types": [
        "text",
        "voice",
        "photo",
        "file"
      ],
      "input_formats": [
        "text",
        "photo",
        "pdf"
      ],
      "output_formats": [
        "docx",
        "pdf",
        "drive_link"
      ],
      "engine": "defect_act",
      "requires_search": false,
      "quality_gates": [
        "document_required"
      ]
    },
    "documents": {
      "title": "Документы",
      "enabled": true,
      "topic_ids": [],
      "aliases": [
        "docx",
        "документ word",
        "напиши письмо",
        "напиши отчет",
        "напиши отчёт"
      ],
      "input_types": [
        "text",
        "voice",
        "file",
        "drive_file"
      ],
      "input_formats": [
        "text",
        "pdf",
        "docx"
      ],
      "output_formats": [
        "docx",
        "pdf",
        "drive_link"
      ],
      "engine": "document_engine",
      "requires_search": false,
      "quality_gates": [
        "document_output_required"
      ]
    },
    "spreadsheets": {
      "title": "Таблицы",
      "enabled": true,
      "topic_ids": [],
      "aliases": [
        "xlsx",
        "excel таблиц",
        "google sheets",
        "гугл таблиц",
        "csv файл"
      ],
      "input_types": [
        "text",
        "voice",
        "file",
        "drive_file"
      ],
      "input_formats": [
        "text",
        "xlsx",
        "csv",
        "pdf"
      ],
      "output_formats": [
        "xlsx",
        "google_sheet",
        "csv",
        "drive_link"
      ],
      "engine": "sheets_route",
      "requires_search": false,
      "quality_gates": [
        "table_required"
      ]
    },
    "google_drive_storage": {
      "title": "Google Drive",
      "enabled": true,
      "topic_ids": [],
      "aliases": [
        "загрузи на drive",
        "залей на гугл диск",
        "сохрани на drive"
      ],
      "input_types": [
        "text",
        "file",
        "drive_file"
      ],
      "input_formats": [
        "text",
        "file",
        "url"
      ],
      "output_formats": [
        "drive_link",
        "telegram_text"
      ],
      "engine": "drive_storage",
      "requires_search": false,
      "quality_gates": [
        "drive_link_required"
      ]
    },
    "devops_server": {
      "title": "Сервер DevOps",
      "enabled": false,
      "topic_ids": [
        794
      ],
      "aliases": [
        "systemctl",
        "journalctl",
        "docker",
        "nginx"
      ],
      "input_types": [
        "text",
        "voice"
      ],
      "input_formats": [
        "text"
      ],
      "output_formats": [
        "telegram_text"
      ],
      "engine": "ai_router",
      "requires_search": false,
      "quality_gates": [],
      "status": "active"
    },
    "vpn_network": {
      "title": "VPN",
      "enabled": false,
      "topic_ids": [],
      "aliases": [
        "vpn",
        "vless",
        "wireguard",
        "xray",
        "reality"
      ],
      "input_types": [
        "text",
        "voice"
      ],
      "input_formats": [
        "text"
      ],
      "output_formats": [
        "telegram_text"
      ],
      "engine": "ai_router",
      "requires_search": false,
      "quality_gates": []
    },
    "ocr_photo": {
      "title": "OCR фото",
      "enabled": false,
      "topic_ids": [],
      "aliases": [
        "ocr",
        "распознай текст",
        "фото в таблицу"
      ],
      "input_types": [
        "photo",
        "file"
      ],
      "input_formats": [
        "photo",
        "pdf"
      ],
      "output_formats": [
        "text",
        "xlsx"
      ],
      "engine": "ocr_engine",
      "requires_search": false,
      "quality_gates": []
    },
    "cad_dwg": {
      "title": "CAD DWG",
      "enabled": false,
      "topic_ids": [],
      "aliases": [
        "dwg",
        "cad",
        "autocad",
        "чертеж",
        "чертёж"
      ],
      "input_types": [
        "file",
        "drive_file"
      ],
      "input_formats": [
        "dwg",
        "pdf"
      ],
      "output_formats": [
        "pdf",
        "xlsx"
      ],
      "engine": "dwg_engine",
      "requires_search": false,
      "quality_gates": []
    },
    "structural_design": {
      "title": "КЖ КМ",
      "enabled": false,
      "topic_ids": [
        210
      ],
      "aliases": [
        "кж",
        "км",
        "проект",
        "расчет",
        "расчёт",
        "балка",
        "плита"
      ],
      "input_types": [
        "text",
        "file",
        "drive_file"
      ],
      "input_formats": [
        "text",
        "pdf",
        "dwg"
      ],
      "output_formats": [
        "pdf",
        "xlsx",
        "docx"
      ],
      "engine": "project_engine",
      "requires_search": false,
      "quality_gates": []
    },
    "roofing": {
      "title": "Кровля",
      "enabled": false,
      "topic_ids": [],
      "aliases": [
        "кровля",
        "стропил",
        "обрешетк",
        "обрешётк"
      ],
      "input_types": [
        "text",
        "file",
        "photo"
      ],
      "input_formats": [
        "text",
        "pdf",
        "photo"
      ],
      "output_formats": [
        "xlsx",
        "pdf"
      ],
      "engine": "estimate_unified",
      "requires_search": false,
      "quality_gates": []
    },
    "monolith_concrete": {
      "title": "Монолит бетон",
      "enabled": false,
      "topic_ids": [],
      "aliases": [
        "монолит",
        "бетон",
        "опалубк"
      ],
      "input_types": [
        "text",
        "file",
        "photo"
      ],
      "input_formats": [
        "text",
        "pdf",
        "photo"
      ],
      "output_formats": [
        "xlsx",
        "pdf"
      ],
      "engine": "estimate_unified",
      "requires_search": false,
      "quality_gates": []
    },
    "crm_leads": {
      "title": "CRM лиды",
      "enabled": false,
      "topic_ids": [
        4569
      ],
      "aliases": [
        "лид",
        "amocrm",
        "заявк",
        "заказчик"
      ],
      "input_types": [
        "text",
        "voice"
      ],
      "input_formats": [
        "text"
      ],
      "output_formats": [
        "telegram_text",
        "json"
      ],
      "engine": "ai_router",
      "requires_search": true,
      "quality_gates": [],
      "status": "active"
    },
    "email_ingress": {
      "title": "Почта",
      "enabled": false,
      "topic_ids": [],
      "aliases": [
        "почта",
        "email",
        "gmail",
        "письмо вложением"
      ],
      "input_types": [
        "text",
        "file"
      ],
      "input_formats": [
        "text",
        "file"
      ],
      "output_formats": [
        "telegram_text",
        "docx"
      ],
      "engine": "email_ingress",
      "requires_search": false,
      "quality_gates": []
    },
    "social_content": {
      "title": "Соцсети",
      "enabled": false,
      "topic_ids": [],
      "aliases": [
        "instagram",
        "youtube",
        "рилс",
        "tiktok",
        "личный бренд"
      ],
      "input_types": [
        "text",
        "photo",
        "video"
      ],
      "input_formats": [
        "text",
        "photo",
        "video"
      ],
      "output_formats": [
        "telegram_text",
        "script"
      ],
      "engine": "content_engine",
      "requires_search": false,
      "quality_gates": []
    },
    "video_production": {
      "title": "Видео",
      "enabled": false,
      "topic_ids": [
        11
      ],
      "aliases": [
        "монтаж видео",
        "shorts",
        "reels",
        "voiceover"
      ],
      "input_types": [
        "text",
        "file",
        "video"
      ],
      "input_formats": [
        "text",
        "video",
        "audio"
      ],
      "output_formats": [
        "mp4",
        "script",
        "drive_link"
      ],
      "engine": "video_production_agent",
      "requires_search": false,
      "quality_gates": [],
      "status": "active"
    },
    "photo_cleanup": {
      "title": "Чистка фото",
      "enabled": false,
      "topic_ids": [],
      "aliases": [
        "почисти фото",
        "убери мусор с фото"
      ],
      "input_types": [
        "photo",
        "file"
      ],
      "input_formats": [
        "photo"
      ],
      "output_formats": [
        "photo",
        "drive_link"
      ],
      "engine": "photo_cleanup",
      "requires_search": false,
      "quality_gates": []
    },
    "isolated_project_ivan": {
      "title": "Ivan project",
      "enabled": false,
      "topic_ids": [],
      "aliases": [
        "проект иван",
        "ivan project"
      ],
      "input_types": [
        "text",
        "voice"
      ],
      "input_formats": [
        "text"
      ],
      "output_formats": [
        "telegram_text"
      ],
      "engine": "ivan_project",
      "requires_search": false,
      "quality_gates": []
    },
    "job_search": {
      "id": "job_search",
      "name": "Поиск работы",
      "status": "active",
      "topic_ids": [
        6104
      ],
      "engine": "search_engine"
    }
  }
}
====================================================================================================
END_FILE: config/directions.yaml
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: config/estimate_template_registry.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 813628e662cc10d221a470368e0329ca38fe8b23ba0aa72f442af26606f54628
====================================================================================================
{
  "estimate_top_templates_logistics_canon_v4": {
    "version": "ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4",
    "status": "ACTIVE_CANON",
    "updated_at": "2026-05-02T13:37:39.354912+00:00",
    "purpose": "Use top estimate files as scalable estimate calculation logic templates with mandatory logistics and web price confirmation",
    "source_files": [
      {
        "key": "M80",
        "title": "М-80.xlsx",
        "template_role": "full_house_estimate_template",
        "description": "Эталон полной сметы М-80",
        "file_id": "1yt-RJsGRhO13zmPKNAn6bMuGrpXY7kWp",
        "drive_url": "https://docs.google.com/spreadsheets/d/1yt-RJsGRhO13zmPKNAn6bMuGrpXY7kWp/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "modifiedTime": "2025-12-02T09:12:35.000Z",
        "parents": [
          "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
        ],
        "formula_total": 1670,
        "formula_samples": [
          {
            "sheet": "Каркас под ключ",
            "cell": "E1",
            "formula": "=E2+E3+E4+E5+E6+E7+E8"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "E2",
            "formula": "=I40"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "E3",
            "formula": "=I63"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "E4",
            "formula": "=I102"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "E5",
            "formula": "=I121"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "E6",
            "formula": "=I158"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "E7",
            "formula": "=I230"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "E8",
            "formula": "=I264"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F12",
            "formula": "=E12*D12"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H12",
            "formula": "=D12*G12"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I12",
            "formula": "=F12+H12"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F13",
            "formula": "=E13*D13"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F14",
            "formula": "=E14*D14"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H14",
            "formula": "=D14*G14"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I14",
            "formula": "=F14+H14"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "D15",
            "formula": "=D14/2"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F15",
            "formula": "=E15*D15"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H15",
            "formula": "=D15*G15"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I15",
            "formula": "=F15+H15"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F16",
            "formula": "=E16*D16"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H16",
            "formula": "=D16*G16"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I16",
            "formula": "=F16+H16"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "D17",
            "formula": "=D14+D16"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F17",
            "formula": "=E17*D17"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H17",
            "formula": "=D17*G17"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I17",
            "formula": "=F17+H17"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F18",
            "formula": "=E18*D18"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H18",
            "formula": "=D18*G18"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I18",
            "formula": "=F18+H18"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F19",
            "formula": "=E19*D19"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H19",
            "formula": "=D19*G19"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I19",
            "formula": "=F19+H19"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F20",
            "formula": "=E20*D20"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H20",
            "formula": "=D20*G20"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I20",
            "formula": "=F20+H20"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F21",
            "formula": "=E21*D21"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H21",
            "formula": "=D21*G21"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I21",
            "formula": "=F21+H21"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F22",
            "formula": "=E22*D22"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H22",
            "formula": "=D22*G22"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I22",
            "formula": "=F22+H22"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F23",
            "formula": "=E23*D23"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H23",
            "formula": "=D23*G23"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I23",
            "formula": "=F23+H23"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F24",
            "formula": "=E24*D24"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H24",
            "formula": "=D24*G24"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I24",
            "formula": "=F24+H24"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F25",
            "formula": "=E25*D25"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F26",
            "formula": "=E26*D26"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H26",
            "formula": "=D26*G26"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "E1",
            "formula": "=E2+E3+E4+E5+E6+E7+E8"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "E2",
            "formula": "=I58"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "E3",
            "formula": "=I112"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "E4",
            "formula": "=I156"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "E5",
            "formula": "=I175"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "E6",
            "formula": "=I205"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "E7",
            "formula": "=I257"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "E8",
            "formula": "=I291"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "F12",
            "formula": "=E12*D12"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "H12",
            "formula": "=D12*G12"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "I12",
            "formula": "=F12+H12"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "F13",
            "formula": "=E13*D13"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "H13",
            "formula": "=D13*G13"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "I13",
            "formula": "=F13+H13"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "D14",
            "formula": "=D13"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "F14",
            "formula": "=E14*D14"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "H14",
            "formula": "=D14*G14"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "I14",
            "formula": "=F14+H14"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "F15",
            "formula": "=E15*D15"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "H15",
            "formula": "=D15*G15"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "I15",
            "formula": "=F15+H15"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "D16",
            "formula": "=138+48"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "F16",
            "formula": "=E16*D16"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "H16",
            "formula": "=D16*G16"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "I16",
            "formula": "=F16+H16"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "D17",
            "formula": "=ROUNDUP(D15*0.2*1.4,)"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "F17",
            "formula": "=E17*D17"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "H17",
            "formula": "=D17*G17"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "I17",
            "formula": "=F17+H17"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "F18",
            "formula": "=E18*D18"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "H18",
            "formula": "=D18*G18"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "I18",
            "formula": "=F18+H18"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "D19",
            "formula": "=D17"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "F19",
            "formula": "=E19*D19"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "H19",
            "formula": "=D19*G19"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "I19",
            "formula": "=F19+H19"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "D20",
            "formula": "=ROUNDUP(D15*0.1*1.2,)"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "F20",
            "formula": "=E20*D20"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "H20",
            "formula": "=D20*G20"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "I20",
            "formula": "=F20+H20"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "F21",
            "formula": "=E21*D21"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "H21",
            "formula": "=D21*G21"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "I21",
            "formula": "=F21+H21"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "D22",
            "formula": "=D20"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "F22",
            "formula": "=E22*D22"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "H22",
            "formula": "=D22*G22"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "I22",
            "formula": "=F22+H22"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "F23",
            "formula": "=E23*D23"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "F24",
            "formula": "=E24*D24"
          },
          {
            "sheet": "Газобетон_под ключ",
            "cell": "H24",
            "formula": "=D24*G24"
          }
        ],
        "sheets": [
          {
            "sheet_name": "Каркас под ключ",
            "scenario": "frame_house",
            "sections": [
              "Фундамент",
              "Каркас",
              "Кровля",
              "Окна, двери",
              "Внешняя отделка",
              "Внутренняя отделка",
              "Инженерные коммуникации"
            ],
            "header_rows": [
              9,
              41,
              64,
              103,
              122,
              159,
              231
            ],
            "total_rows": [
              {
                "row": 38,
                "text": "Итого работа: 177630.50303999998"
              },
              {
                "row": 39,
                "text": "Итого материалы: 187078.848"
              },
              {
                "row": 40,
                "text": "Итого фундамент: 364709.35104"
              },
              {
                "row": 61,
                "text": "Итого работа: 421719.7464864"
              },
              {
                "row": 62,
                "text": "Итого материалы: 370590.989583808"
              },
              {
                "row": 63,
                "text": "Итого каркас : 792310.736070208"
              },
              {
                "row": 100,
                "text": "Итого работа: 489854.65233"
              },
              {
                "row": 101,
                "text": "Итого материалы: 594110.925088848"
              },
              {
                "row": 102,
                "text": "Итого кровля: 1083965.577418848"
              },
              {
                "row": 119,
                "text": "Итого работа: 157905"
              },
              {
                "row": 120,
                "text": "Итого материалы: 677320.8"
              },
              {
                "row": 121,
                "text": "Итого окна, двери: 835225.8"
              },
              {
                "row": 156,
                "text": "Итого работа: 339034.9049999999"
              },
              {
                "row": 157,
                "text": "Итого материалы: 327018.077824976"
              },
              {
                "row": 158,
                "text": "Итого внешняя отделка: 666052.9828249759"
              },
              {
                "row": 228,
                "text": "Итого работа: 819488.08396"
              },
              {
                "row": 229,
                "text": "Итого материалы: 918336.176296875"
              },
              {
                "row": 230,
                "text": "Итого внутренняя отделка: 1737824.2602568748"
              },
              {
                "row": 262,
                "text": "Итого работа: 207549.06"
              },
              {
                "row": 263,
                "text": "Итого материалы: 323128.186"
              },
              {
                "row": 264,
                "text": "Итого инженерные коммуникации: 530677.246"
              },
              {
                "row": 266,
                "text": "Итого РАБОТЫ: 2405632.8908164"
              },
              {
                "row": 267,
                "text": "Итого МАТЕРИАЛЫ: 3074455.816794507"
              },
              {
                "row": 268,
                "text": "ИТОГО СМЕТНАЯ СТОИМОСТЬ: 6010765.953610907"
              }
            ],
            "material_rows": 130,
            "work_rows": 96,
            "logistics_rows": 17,
            "sample_rows": [
              {
                "row": 9,
                "name": "Наименование",
                "unit": "Ед. изм.",
                "qty": "Кол-во",
                "work_price": "Работа",
                "material_price": "Материалы"
              },
              {
                "row": 12,
                "name": "Вынос осей в натуру",
                "unit": "м2",
                "qty": "95.4",
                "work_price": "100",
                "material_price": "0"
              },
              {
                "row": 14,
                "name": "Укладка канализационной трубы в грунт",
                "unit": "мп",
                "qty": "20",
                "work_price": "800",
                "material_price": "0"
              },
              {
                "row": 15,
                "name": "Труба канализационная Ostendorf d110x2000 мм для наружной канализации",
                "unit": "шт",
                "qty": "10",
                "work_price": "0",
                "material_price": "670"
              },
              {
                "row": 16,
                "name": "Труба канализационная Ostendorf d110x1000 мм для наружной канализации",
                "unit": "шт",
                "qty": "3",
                "work_price": "0",
                "material_price": "400"
              },
              {
                "row": 17,
                "name": "Теплоизоляция для труб стенофлекс 114х13х2000 мм",
                "unit": "мп",
                "qty": "23",
                "work_price": "0",
                "material_price": "118"
              },
              {
                "row": 18,
                "name": "Комплект тройников, отводов, уголков для наружной канализации.",
                "unit": "к-т",
                "qty": "1",
                "work_price": "0",
                "material_price": "3500"
              },
              {
                "row": 19,
                "name": "Укладка закладной трубы в грунт под электрокабель",
                "unit": "мп",
                "qty": "15",
                "work_price": "400",
                "material_price": "0"
              },
              {
                "row": 20,
                "name": "Кабель NVO ВБШвнг(А) LS 5х2.5 20 м",
                "unit": "шт",
                "qty": "1",
                "work_price": "0",
                "material_price": "6600"
              },
              {
                "row": 21,
                "name": "Труба двустенная гофрированная ПНД/ПВД d63/52",
                "unit": "мп",
                "qty": "15",
                "work_price": "0",
                "material_price": "114"
              },
              {
                "row": 22,
                "name": "Укладка трубы ХВС в грунт на глубину 1,5м.",
                "unit": "мп",
                "qty": "10",
                "work_price": "1000",
                "material_price": "0"
              },
              {
                "row": 23,
                "name": "Труба двустенная гофрированная ПНД/ПВД d63/52",
                "unit": "мп",
                "qty": "20",
                "work_price": "0",
                "material_price": "114"
              },
              {
                "row": 24,
                "name": "Труба ПНД (ПЭ-100) для систем водоснабжения премиум синяя 32 мм",
                "unit": "мп",
                "qty": "20",
                "work_price": "0",
                "material_price": "81"
              },
              {
                "row": 26,
                "name": "Разметка свайного поля, забивка свай, установка оголовков",
                "unit": "шт",
                "qty": "31",
                "work_price": "2000",
                "material_price": "0"
              },
              {
                "row": 27,
                "name": "Свая винтовая d108 мм h2500 мм",
                "unit": "шт",
                "qty": "31",
                "work_price": "0",
                "material_price": "2632"
              },
              {
                "row": 28,
                "name": "Оголовок для сваи винтовой d108 мм",
                "unit": "шт",
                "qty": "31",
                "work_price": "0",
                "material_price": "260"
              },
              {
                "row": 29,
                "name": "Обвязка свай по гидроизоляции",
                "unit": "мп",
                "qty": "72.72",
                "work_price": "750",
                "material_price": "0"
              },
              {
                "row": 30,
                "name": "Гидроизоляция Линокром ХПП Технониколь черный 15 кв.м",
                "unit": "рул",
                "qty": "1",
                "work_price": "0",
                "material_price": "1900"
              },
              {
                "row": 31,
                "name": "Брус сух 150х150",
                "unit": "м3",
                "qty": "1.9634399999999999",
                "work_price": "0",
                "material_price": "22000"
              },
              {
                "row": 32,
                "name": "Крепеж и расходные материалы по разделу",
                "unit": "к-т",
                "qty": "31",
                "work_price": "0",
                "material_price": "200"
              },
              {
                "row": 33,
                "name": "Антисептирование конструкционной доски в 2 слоя",
                "unit": "м2",
                "qty": "1.9634399999999999",
                "work_price": "200",
                "material_price": "0"
              },
              {
                "row": 34,
                "name": "Антисептик Neomid 450 огнебиозащитный I группа красный 10 кг",
                "unit": "шт",
                "qty": "1",
                "work_price": "0",
                "material_price": "2800"
              },
              {
                "row": 35,
                "name": "Погрузо-разгрузочные работы",
                "unit": "усл",
                "qty": "1",
                "work_price": "6000",
                "material_price": "0"
              },
              {
                "row": 36,
                "name": "Транспортные расходы",
                "unit": "",
                "qty": "0.1",
                "work_price": "",
                "material_price": ""
              },
              {
                "row": 37,
                "name": "Накладные расходы",
                "unit": "",
                "qty": "0.08",
                "work_price": "",
                "material_price": ""
              },
              {
                "row": 41,
                "name": "Наименование",
                "unit": "Ед. изм.",
                "qty": "Кол-во",
                "work_price": "Работа",
                "material_price": "Материалы"
              },
              {
                "row": 44,
                "name": "Монтаж лаг цокольного перекрытия вкл террасы, крыльца",
                "unit": "м2",
                "qty": "91.7",
                "work_price": "1000",
                "material_price": "0"
              },
              {
                "row": 45,
                "name": "доска с/к 40х200",
                "unit": "м3",
                "qty": "2.2008",
                "work_price": "0",
                "material_price": "24300"
              },
              {
                "row": 46,
                "name": "Устройство каркаса стен/перегородок",
                "unit": "м2",
                "qty": "157.62825",
                "work_price": "1000",
                "material_price": "0"
              },
              {
                "row": 47,
                "name": "Монтаж стоек и балок террасы",
                "unit": "мп",
                "qty": "8.8",
                "work_price": "800",
                "material_price": "0"
              },
              {
                "row": 48,
                "name": "доска с/к 40х150",
                "unit": "м3",
                "qty": "4.4977464000000005",
                "work_price": "0",
                "material_price": "24300"
              },
              {
                "row": 49,
                "name": "доска с/к 40х100",
                "unit": "м3",
                "qty": "0.2945808",
                "work_price": "0",
                "material_price": "24300"
              },
              {
                "row": 50,
                "name": "бру с/с 150х150",
                "unit": "м3",
                "qty": "0.26999999999999996",
                "work_price": "0",
                "material_price": "30000"
              },
              {
                "row": 51,
                "name": "Монтаж баллок перекрытия",
                "unit": "м2",
                "qty": "0",
                "work_price": "1000",
                "material_price": "0"
              },
              {
                "row": 52,
                "name": "доска с/к 40х150",
                "unit": "м3",
                "qty": "0",
                "work_price": "0",
                "material_price": "24300"
              }
            ],
            "formula_count": 799,
            "formula_samples": [
              {
                "sheet": "Каркас под ключ",
                "cell": "E1",
                "formula": "=E2+E3+E4+E5+E6+E7+E8"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "E2",
                "formula": "=I40"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "E3",
                "formula": "=I63"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "E4",
                "formula": "=I102"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "E5",
                "formula": "=I121"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "E6",
                "formula": "=I158"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "E7",
                "formula": "=I230"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "E8",
                "formula": "=I264"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "F12",
                "formula": "=E12*D12"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "H12",
                "formula": "=D12*G12"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "I12",
                "formula": "=F12+H12"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "F13",
                "formula": "=E13*D13"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "F14",
                "formula": "=E14*D14"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "H14",
                "formula": "=D14*G14"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "I14",
                "formula": "=F14+H14"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "D15",
                "formula": "=D14/2"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "F15",
                "formula": "=E15*D15"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "H15",
                "formula": "=D15*G15"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "I15",
                "formula": "=F15+H15"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "F16",
                "formula": "=E16*D16"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "H16",
                "formula": "=D16*G16"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "I16",
                "formula": "=F16+H16"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "D17",
                "formula": "=D14+D16"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "F17",
                "formula": "=E17*D17"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "H17",
                "formula": "=D17*G17"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "I17",
                "formula": "=F17+H17"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "F18",
                "formula": "=E18*D18"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "H18",
                "formula": "=D18*G18"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "I18",
                "formula": "=F18+H18"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "F19",
                "formula": "=E19*D19"
              }
            ],
            "row_count": 285
          },
          {
            "sheet_name": "Газобетон_под ключ",
            "scenario": "gasbeton_or_masonry_with_monolithic_foundation",
            "sections": [
              "Фундамент",
              "Стены",
              "Кровля",
              "Окна, двери",
              "Внешняя отделка",
              "Внутренняя отделка",
              "Инженерные коммуникации"
            ],
            "header_rows": [
              9,
              59,
              113,
              157,
              176,
              206,
              258
            ],
            "total_rows": [
              {
                "row": 56,
                "text": "Итого работа: 371647.66"
              },
              {
                "row": 57,
                "text": "Итого материалы: 564147.06331776"
              },
              {
                "row": 58,
                "text": "Итого фундамент: 935794.72331776"
              },
              {
                "row": 110,
                "text": "Итого работа: 436810.7232500001"
              },
              {
                "row": 111,
                "text": "Итого материалы: 611460.929728"
              },
              {
                "row": 112,
                "text": "Итого каркас : 1048271.652978"
              },
              {
                "row": 154,
                "text": "Итого работа: 618251.94353"
              },
              {
                "row": 155,
                "text": "Итого материалы: 681975.5442550561"
              },
              {
                "row": 156,
                "text": "Итого кровля: 1300227.4877850562"
              },
              {
                "row": 173,
                "text": "Итого работа: 157905"
              },
              {
                "row": 174,
                "text": "Итого материалы: 677320.8"
              },
              {
                "row": 175,
                "text": "Итого окна, двери: 835225.8"
              },
              {
                "row": 203,
                "text": "Итого работа: 293332.36899999995"
              },
              {
                "row": 204,
                "text": "Итого материалы: 252704.802632"
              },
              {
                "row": 205,
                "text": "Итого внешняя отделка: 546037.171632"
              },
              {
                "row": 255,
                "text": "Итого работа: 613355.61856"
              },
              {
                "row": 256,
                "text": "Итого материалы: 619625.761125"
              },
              {
                "row": 257,
                "text": "Итого внутренняя отделка: 1232981.379685"
              },
              {
                "row": 289,
                "text": "Итого работа: 207549.06"
              },
              {
                "row": 290,
                "text": "Итого материалы: 323128.186"
              },
              {
                "row": 291,
                "text": "Итого инженерные коммуникации: 530677.246"
              },
              {
                "row": 293,
                "text": "Итого РАБОТЫ: 2698852.37434"
              },
              {
                "row": 294,
                "text": "Итого МАТЕРИАЛЫ: 3730363.087057816"
              },
              {
                "row": 295,
                "text": "ИТОГО СМЕТНАЯ СТОИМОСТЬ: 6429215.4613978155"
              }
            ],
            "material_rows": 156,
            "work_rows": 99,
            "logistics_rows": 23,
            "sample_rows": [
              {
                "row": 9,
                "name": "Наименование",
                "unit": "Ед. изм.",
                "qty": "Кол-во",
                "work_price": "Работа",
                "material_price": "Материалы"
              },
              {
                "row": 12,
                "name": "Вынос осей в натуру",
                "unit": "м2",
                "qty": "95.4",
                "work_price": "80",
                "material_price": "0"
              },
              {
                "row": 13,
                "name": "Земляные работы, сопровождение работы экскаватора",
                "unit": "см",
                "qty": "1",
                "work_price": "12000",
                "material_price": "0"
              },
              {
                "row": 14,
                "name": "Аренда экскаватора",
                "unit": "см",
                "qty": "1",
                "work_price": "0",
                "material_price": "22000"
              },
              {
                "row": 15,
                "name": "Доработка грунта вручную",
                "unit": "м2",
                "qty": "138",
                "work_price": "150",
                "material_price": "0"
              },
              {
                "row": 16,
                "name": "Настил геотекстиля по основанию и стенам котлована (Геотекстиль 300 г/кв.м иглопробивной)",
                "unit": "м2",
                "qty": "186",
                "work_price": "80",
                "material_price": "60"
              },
              {
                "row": 17,
                "name": "Устройство песчаной подготовки т 200 мм с уплотнением.",
                "unit": "м3",
                "qty": "39",
                "work_price": "800",
                "material_price": "0"
              },
              {
                "row": 18,
                "name": "Аренда виброплиты (трамбовка)",
                "unit": "сут",
                "qty": "4",
                "work_price": "0",
                "material_price": "2500"
              },
              {
                "row": 19,
                "name": "Песок карьерный",
                "unit": "м3",
                "qty": "39",
                "work_price": "0",
                "material_price": "900"
              },
              {
                "row": 20,
                "name": "Устройство щебеночной подготовки т 100 мм с уплотнением.",
                "unit": "м3",
                "qty": "17",
                "work_price": "800",
                "material_price": "0"
              },
              {
                "row": 21,
                "name": "Аренда виброплиты (трамбовка)",
                "unit": "сут",
                "qty": "4",
                "work_price": "0",
                "material_price": "2500"
              },
              {
                "row": 22,
                "name": "Щебень фр 20-40",
                "unit": "м3",
                "qty": "17",
                "work_price": "0",
                "material_price": "1880"
              },
              {
                "row": 24,
                "name": "Укладка канализационной трубы в грунт",
                "unit": "мп",
                "qty": "20",
                "work_price": "900",
                "material_price": "0"
              },
              {
                "row": 25,
                "name": "Труба канализационная Ostendorf d110x2000 мм для наружной канализации",
                "unit": "шт",
                "qty": "10",
                "work_price": "0",
                "material_price": "670"
              },
              {
                "row": 26,
                "name": "Труба канализационная Ostendorf d110x1000 мм для наружной канализации",
                "unit": "шт",
                "qty": "3",
                "work_price": "0",
                "material_price": "400"
              },
              {
                "row": 27,
                "name": "Теплоизоляция для труб стенофлекс 114х13х2000 мм",
                "unit": "мп",
                "qty": "23",
                "work_price": "0",
                "material_price": "118"
              },
              {
                "row": 28,
                "name": "Комплект тройников, отводов, уголков для наружной канализации.",
                "unit": "к-т",
                "qty": "1",
                "work_price": "0",
                "material_price": "3500"
              },
              {
                "row": 29,
                "name": "Укладка закладной трубы в грунт под электрокабель",
                "unit": "мп",
                "qty": "15",
                "work_price": "400",
                "material_price": "0"
              },
              {
                "row": 30,
                "name": "Кабель NVO ВБШвнг(А) LS 5х2.5 20 м",
                "unit": "шт",
                "qty": "1",
                "work_price": "0",
                "material_price": "6600"
              },
              {
                "row": 31,
                "name": "Труба двустенная гофрированная ПНД/ПВД d63/52",
                "unit": "мп",
                "qty": "15",
                "work_price": "0",
                "material_price": "114"
              },
              {
                "row": 32,
                "name": "Укладка трубы ХВС в грунт на глубину 1,5м.",
                "unit": "мп",
                "qty": "10",
                "work_price": "850",
                "material_price": "0"
              },
              {
                "row": 33,
                "name": "Труба двустенная гофрированная ПНД/ПВД d63/52",
                "unit": "мп",
                "qty": "20",
                "work_price": "0",
                "material_price": "114"
              },
              {
                "row": 34,
                "name": "Труба ПНД (ПЭ-100) для систем водоснабжения премиум синяя 32 мм",
                "unit": "мп",
                "qty": "20",
                "work_price": "0",
                "material_price": "81"
              },
              {
                "row": 35,
                "name": "Настил технической пленки",
                "unit": "м2",
                "qty": "120",
                "work_price": "50",
                "material_price": "40"
              },
              {
                "row": 37,
                "name": "Устройство опалубки",
                "unit": "мп",
                "qty": "40.7",
                "work_price": "1100",
                "material_price": "0"
              },
              {
                "row": 38,
                "name": "Доска 50х150(100)х6000 мм е/в",
                "unit": "м3",
                "qty": "1.8315000000000001",
                "work_price": "0",
                "material_price": "17500"
              },
              {
                "row": 39,
                "name": "Устройство арматурного каркаса",
                "unit": "м2",
                "qty": "95.4",
                "work_price": "1200",
                "material_price": "0"
              },
              {
                "row": 40,
                "name": "Арматура металлическая д.12 А500",
                "unit": "т",
                "qty": "2.0331648",
                "work_price": "0",
                "material_price": "70000"
              },
              {
                "row": 41,
                "name": "Арматура металлическая д.8 А500",
                "unit": "т",
                "qty": "0.22364812800000003",
                "work_price": "0",
                "material_price": "73000"
              },
              {
                "row": 42,
                "name": "Пеноплэкс Фундамент 100х585х1185",
                "unit": "шт",
                "qty": "5",
                "work_price": "0",
                "material_price": "709"
              },
              {
                "row": 43,
                "name": "Проволока вязальная 1,2мм",
                "unit": "кг",
                "qty": "50",
                "work_price": "0",
                "material_price": "160"
              },
              {
                "row": 44,
                "name": "Фиксаторы арматуры гориз.уп 250 шт",
                "unit": "уп",
                "qty": "3",
                "work_price": "0",
                "material_price": "1456"
              },
              {
                "row": 45,
                "name": "Бетонирование монолитной плиты с вибрированием",
                "unit": "м3",
                "qty": "21",
                "work_price": "2000",
                "material_price": "0"
              },
              {
                "row": 46,
                "name": "Бетон В20 W8 с доставкой*",
                "unit": "м3",
                "qty": "21",
                "work_price": "0",
                "material_price": "6500"
              },
              {
                "row": 47,
                "name": "глубинный вибратор",
                "unit": "сут",
                "qty": "1",
                "work_price": "0",
                "material_price": "1500"
              }
            ],
            "formula_count": 871,
            "formula_samples": [
              {
                "sheet": "Газобетон_под ключ",
                "cell": "E1",
                "formula": "=E2+E3+E4+E5+E6+E7+E8"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "E2",
                "formula": "=I58"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "E3",
                "formula": "=I112"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "E4",
                "formula": "=I156"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "E5",
                "formula": "=I175"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "E6",
                "formula": "=I205"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "E7",
                "formula": "=I257"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "E8",
                "formula": "=I291"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "F12",
                "formula": "=E12*D12"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "H12",
                "formula": "=D12*G12"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "I12",
                "formula": "=F12+H12"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "F13",
                "formula": "=E13*D13"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "H13",
                "formula": "=D13*G13"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "I13",
                "formula": "=F13+H13"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "D14",
                "formula": "=D13"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "F14",
                "formula": "=E14*D14"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "H14",
                "formula": "=D14*G14"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "I14",
                "formula": "=F14+H14"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "F15",
                "formula": "=E15*D15"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "H15",
                "formula": "=D15*G15"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "I15",
                "formula": "=F15+H15"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "D16",
                "formula": "=138+48"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "F16",
                "formula": "=E16*D16"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "H16",
                "formula": "=D16*G16"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "I16",
                "formula": "=F16+H16"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "D17",
                "formula": "=ROUNDUP(D15*0.2*1.4,)"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "F17",
                "formula": "=E17*D17"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "H17",
                "formula": "=D17*G17"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "I17",
                "formula": "=F17+H17"
              },
              {
                "sheet": "Газобетон_под ключ",
                "cell": "F18",
                "formula": "=E18*D18"
              }
            ],
            "row_count": 312
          }
        ]
      },
      {
        "key": "M110",
        "title": "М-110.xlsx",
        "template_role": "full_house_estimate_template",
        "description": "Эталон полной сметы М-110",
        "file_id": "1Ub9fcwOcJ4pV30dcX88yf1225WOIdpWo",
        "drive_url": "https://docs.google.com/spreadsheets/d/1Ub9fcwOcJ4pV30dcX88yf1225WOIdpWo/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "modifiedTime": "2025-05-15T06:18:08.000Z",
        "parents": [
          "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
        ],
        "formula_total": 1647,
        "formula_samples": [
          {
            "sheet": "Каркас под ключ",
            "cell": "E1",
            "formula": "=E2+E3+E4+E5+E6+E7+E8"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "E2",
            "formula": "=I40"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "E3",
            "formula": "=I63"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "E4",
            "formula": "=I102"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "E5",
            "formula": "=I121"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "E6",
            "formula": "=I158"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "E7",
            "formula": "=I230"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "E8",
            "formula": "=I264"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F12",
            "formula": "=E12*D12"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H12",
            "formula": "=D12*G12"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I12",
            "formula": "=F12+H12"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F13",
            "formula": "=E13*D13"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F14",
            "formula": "=E14*D14"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H14",
            "formula": "=D14*G14"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I14",
            "formula": "=F14+H14"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "D15",
            "formula": "=D14/2"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F15",
            "formula": "=E15*D15"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H15",
            "formula": "=D15*G15"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I15",
            "formula": "=F15+H15"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F16",
            "formula": "=E16*D16"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H16",
            "formula": "=D16*G16"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I16",
            "formula": "=F16+H16"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "D17",
            "formula": "=D14+D16"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F17",
            "formula": "=E17*D17"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H17",
            "formula": "=D17*G17"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I17",
            "formula": "=F17+H17"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F18",
            "formula": "=E18*D18"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H18",
            "formula": "=D18*G18"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I18",
            "formula": "=F18+H18"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F19",
            "formula": "=E19*D19"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H19",
            "formula": "=D19*G19"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I19",
            "formula": "=F19+H19"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F20",
            "formula": "=E20*D20"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H20",
            "formula": "=D20*G20"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I20",
            "formula": "=F20+H20"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F21",
            "formula": "=E21*D21"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H21",
            "formula": "=D21*G21"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I21",
            "formula": "=F21+H21"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F22",
            "formula": "=E22*D22"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H22",
            "formula": "=D22*G22"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I22",
            "formula": "=F22+H22"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F23",
            "formula": "=E23*D23"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H23",
            "formula": "=D23*G23"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I23",
            "formula": "=F23+H23"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F24",
            "formula": "=E24*D24"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H24",
            "formula": "=D24*G24"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "I24",
            "formula": "=F24+H24"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F25",
            "formula": "=E25*D25"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "F26",
            "formula": "=E26*D26"
          },
          {
            "sheet": "Каркас под ключ",
            "cell": "H26",
            "formula": "=D26*G26"
          },
          {
            "sheet": "Газобетон",
            "cell": "E1",
            "formula": "=E2+E3+E4+E5+E6+E7+E8"
          },
          {
            "sheet": "Газобетон",
            "cell": "E2",
            "formula": "=I58"
          },
          {
            "sheet": "Газобетон",
            "cell": "E3",
            "formula": "=I110"
          },
          {
            "sheet": "Газобетон",
            "cell": "E4",
            "formula": "=I154"
          },
          {
            "sheet": "Газобетон",
            "cell": "E5",
            "formula": "=I173"
          },
          {
            "sheet": "Газобетон",
            "cell": "E6",
            "formula": "=I203"
          },
          {
            "sheet": "Газобетон",
            "cell": "E7",
            "formula": "=I255"
          },
          {
            "sheet": "Газобетон",
            "cell": "E8",
            "formula": "=I289"
          },
          {
            "sheet": "Газобетон",
            "cell": "F12",
            "formula": "=E12*D12"
          },
          {
            "sheet": "Газобетон",
            "cell": "H12",
            "formula": "=D12*G12"
          },
          {
            "sheet": "Газобетон",
            "cell": "I12",
            "formula": "=F12+H12"
          },
          {
            "sheet": "Газобетон",
            "cell": "F13",
            "formula": "=E13*D13"
          },
          {
            "sheet": "Газобетон",
            "cell": "H13",
            "formula": "=D13*G13"
          },
          {
            "sheet": "Газобетон",
            "cell": "I13",
            "formula": "=F13+H13"
          },
          {
            "sheet": "Газобетон",
            "cell": "D14",
            "formula": "=D13"
          },
          {
            "sheet": "Газобетон",
            "cell": "F14",
            "formula": "=E14*D14"
          },
          {
            "sheet": "Газобетон",
            "cell": "H14",
            "formula": "=D14*G14"
          },
          {
            "sheet": "Газобетон",
            "cell": "I14",
            "formula": "=F14+H14"
          },
          {
            "sheet": "Газобетон",
            "cell": "F15",
            "formula": "=E15*D15"
          },
          {
            "sheet": "Газобетон",
            "cell": "H15",
            "formula": "=D15*G15"
          },
          {
            "sheet": "Газобетон",
            "cell": "I15",
            "formula": "=F15+H15"
          },
          {
            "sheet": "Газобетон",
            "cell": "D16",
            "formula": "=155+50"
          },
          {
            "sheet": "Газобетон",
            "cell": "F16",
            "formula": "=E16*D16"
          },
          {
            "sheet": "Газобетон",
            "cell": "H16",
            "formula": "=D16*G16"
          },
          {
            "sheet": "Газобетон",
            "cell": "I16",
            "formula": "=F16+H16"
          },
          {
            "sheet": "Газобетон",
            "cell": "D17",
            "formula": "=ROUNDUP(D15*0.2*1.4,)"
          },
          {
            "sheet": "Газобетон",
            "cell": "F17",
            "formula": "=E17*D17"
          },
          {
            "sheet": "Газобетон",
            "cell": "H17",
            "formula": "=D17*G17"
          },
          {
            "sheet": "Газобетон",
            "cell": "I17",
            "formula": "=F17+H17"
          },
          {
            "sheet": "Газобетон",
            "cell": "F18",
            "formula": "=E18*D18"
          },
          {
            "sheet": "Газобетон",
            "cell": "H18",
            "formula": "=D18*G18"
          },
          {
            "sheet": "Газобетон",
            "cell": "I18",
            "formula": "=F18+H18"
          },
          {
            "sheet": "Газобетон",
            "cell": "D19",
            "formula": "=D17"
          },
          {
            "sheet": "Газобетон",
            "cell": "F19",
            "formula": "=E19*D19"
          },
          {
            "sheet": "Газобетон",
            "cell": "H19",
            "formula": "=D19*G19"
          },
          {
            "sheet": "Газобетон",
            "cell": "I19",
            "formula": "=F19+H19"
          },
          {
            "sheet": "Газобетон",
            "cell": "D20",
            "formula": "=ROUNDUP(D15*0.1*1.2,)"
          },
          {
            "sheet": "Газобетон",
            "cell": "F20",
            "formula": "=E20*D20"
          },
          {
            "sheet": "Газобетон",
            "cell": "H20",
            "formula": "=D20*G20"
          },
          {
            "sheet": "Газобетон",
            "cell": "I20",
            "formula": "=F20+H20"
          },
          {
            "sheet": "Газобетон",
            "cell": "F21",
            "formula": "=E21*D21"
          },
          {
            "sheet": "Газобетон",
            "cell": "H21",
            "formula": "=D21*G21"
          },
          {
            "sheet": "Газобетон",
            "cell": "I21",
            "formula": "=F21+H21"
          },
          {
            "sheet": "Газобетон",
            "cell": "D22",
            "formula": "=D20"
          },
          {
            "sheet": "Газобетон",
            "cell": "F22",
            "formula": "=E22*D22"
          },
          {
            "sheet": "Газобетон",
            "cell": "H22",
            "formula": "=D22*G22"
          },
          {
            "sheet": "Газобетон",
            "cell": "I22",
            "formula": "=F22+H22"
          },
          {
            "sheet": "Газобетон",
            "cell": "F23",
            "formula": "=E23*D23"
          },
          {
            "sheet": "Газобетон",
            "cell": "F24",
            "formula": "=E24*D24"
          },
          {
            "sheet": "Газобетон",
            "cell": "H24",
            "formula": "=D24*G24"
          }
        ],
        "sheets": [
          {
            "sheet_name": "Каркас под ключ",
            "scenario": "frame_house",
            "sections": [
              "Фундамент",
              "Каркас",
              "Кровля",
              "Окна, двери",
              "Внешняя отделка",
              "Внутренняя отделка",
              "Инженерные коммуникации"
            ],
            "header_rows": [
              9,
              41,
              64,
              103,
              122,
              159,
              231
            ],
            "total_rows": [
              {
                "row": 38,
                "text": "Итого работа: 186528.8088"
              },
              {
                "row": 39,
                "text": "Итого материалы: 186206.46000000002"
              },
              {
                "row": 40,
                "text": "Итого фундамент: 372735.2688"
              },
              {
                "row": 61,
                "text": "Итого работа: 477629.94104"
              },
              {
                "row": 62,
                "text": "Итого материалы: 437064.3309088"
              },
              {
                "row": 63,
                "text": "Итого каркас : 914694.2719488"
              },
              {
                "row": 100,
                "text": "Итого работа: 529936.4"
              },
              {
                "row": 101,
                "text": "Итого материалы: 628855.6559680001"
              },
              {
                "row": 102,
                "text": "Итого кровля: 1158792.055968"
              },
              {
                "row": 119,
                "text": "Итого работа: 177210"
              },
              {
                "row": 120,
                "text": "Итого материалы: 713674"
              },
              {
                "row": 121,
                "text": "Итого окна, двери: 890884"
              },
              {
                "row": 156,
                "text": "Итого работа: 391133.64"
              },
              {
                "row": 157,
                "text": "Итого материалы: 438006.42710880004"
              },
              {
                "row": 158,
                "text": "Итого внешняя отделка: 829140.0671088"
              },
              {
                "row": 228,
                "text": "Итого работа: 966280.5451999999"
              },
              {
                "row": 229,
                "text": "Итого материалы: 1080968.6829375"
              },
              {
                "row": 230,
                "text": "Итого внутренняя отделка: 2047249.2281375001"
              },
              {
                "row": 262,
                "text": "Итого работа: 230232"
              },
              {
                "row": 263,
                "text": "Итого материалы: 346375"
              },
              {
                "row": 264,
                "text": "Итого инженерные коммуникации: 576607"
              },
              {
                "row": 266,
                "text": "Итого РАБОТЫ: 2728719.33504"
              },
              {
                "row": 267,
                "text": "Итого МАТЕРИАЛЫ: 3484775.5569231003"
              },
              {
                "row": 268,
                "text": "ИТОГО СМЕТНАЯ СТОИМОСТЬ: 6790101.8919631"
              }
            ],
            "material_rows": 130,
            "work_rows": 96,
            "logistics_rows": 17,
            "sample_rows": [
              {
                "row": 9,
                "name": "Наименование",
                "unit": "Ед. изм.",
                "qty": "Кол-во",
                "work_price": "Работа",
                "material_price": "Материалы"
              },
              {
                "row": 12,
                "name": "Вынос осей в натуру",
                "unit": "м2",
                "qty": "112",
                "work_price": "100",
                "material_price": "0"
              },
              {
                "row": 14,
                "name": "Укладка канализационной трубы в грунт",
                "unit": "мп",
                "qty": "28",
                "work_price": "800",
                "material_price": "0"
              },
              {
                "row": 15,
                "name": "Труба канализационная Ostendorf d110x2000 мм для наружной канализации",
                "unit": "шт",
                "qty": "14",
                "work_price": "0",
                "material_price": "670"
              },
              {
                "row": 16,
                "name": "Труба канализационная Ostendorf d110x1000 мм для наружной канализации",
                "unit": "шт",
                "qty": "3",
                "work_price": "0",
                "material_price": "400"
              },
              {
                "row": 17,
                "name": "Теплоизоляция для труб стенофлекс 114х13х2000 мм",
                "unit": "мп",
                "qty": "31",
                "work_price": "0",
                "material_price": "118"
              },
              {
                "row": 18,
                "name": "Комплект тройников, отводов, уголков для наружной канализации.",
                "unit": "к-т",
                "qty": "1",
                "work_price": "0",
                "material_price": "3500"
              },
              {
                "row": 19,
                "name": "Укладка закладной трубы в грунт под электрокабель",
                "unit": "мп",
                "qty": "15",
                "work_price": "400",
                "material_price": "0"
              },
              {
                "row": 20,
                "name": "Кабель NVO ВБШвнг(А) LS 5х2.5 20 м",
                "unit": "шт",
                "qty": "1",
                "work_price": "0",
                "material_price": "6600"
              },
              {
                "row": 21,
                "name": "Труба двустенная гофрированная ПНД/ПВД d63/52",
                "unit": "мп",
                "qty": "15",
                "work_price": "0",
                "material_price": "114"
              },
              {
                "row": 22,
                "name": "Укладка трубы ХВС в грунт на глубину 1,5м.",
                "unit": "мп",
                "qty": "10",
                "work_price": "1000",
                "material_price": "0"
              },
              {
                "row": 23,
                "name": "Труба двустенная гофрированная ПНД/ПВД d63/52",
                "unit": "мп",
                "qty": "20",
                "work_price": "0",
                "material_price": "114"
              },
              {
                "row": 24,
                "name": "Труба ПНД (ПЭ-100) для систем водоснабжения премиум синяя 32 мм",
                "unit": "мп",
                "qty": "20",
                "work_price": "0",
                "material_price": "81"
              },
              {
                "row": 26,
                "name": "Разметка свайного поля, забивка свай, установка оголовков",
                "unit": "шт",
                "qty": "28",
                "work_price": "2000",
                "material_price": "0"
              },
              {
                "row": 27,
                "name": "Свая винтовая d108 мм h2500 мм",
                "unit": "шт",
                "qty": "28",
                "work_price": "0",
                "material_price": "2632"
              },
              {
                "row": 28,
                "name": "Оголовок для сваи винтовой d108 мм",
                "unit": "шт",
                "qty": "28",
                "work_price": "0",
                "material_price": "260"
              },
              {
                "row": 29,
                "name": "Обвязка свай по гидроизоляции",
                "unit": "мп",
                "qty": "80.9",
                "work_price": "750",
                "material_price": "0"
              },
              {
                "row": 30,
                "name": "Гидроизоляция Линокром ХПП Технониколь черный 15 кв.м",
                "unit": "рул",
                "qty": "1",
                "work_price": "0",
                "material_price": "1900"
              },
              {
                "row": 31,
                "name": "Брус сух 150х150",
                "unit": "м3",
                "qty": "2.1843",
                "work_price": "0",
                "material_price": "22000"
              },
              {
                "row": 32,
                "name": "Крепеж и расходные материалы по разделу",
                "unit": "к-т",
                "qty": "28",
                "work_price": "0",
                "material_price": "200"
              },
              {
                "row": 33,
                "name": "Антисептирование конструкционной доски в 2 слоя",
                "unit": "м2",
                "qty": "2.1843",
                "work_price": "200",
                "material_price": "0"
              },
              {
                "row": 34,
                "name": "Антисептик Neomid 450 огнебиозащитный I группа красный 10 кг",
                "unit": "шт",
                "qty": "1",
                "work_price": "0",
                "material_price": "2800"
              },
              {
                "row": 35,
                "name": "Погрузо-разгрузочные работы",
                "unit": "усл",
                "qty": "1",
                "work_price": "6000",
                "material_price": "0"
              },
              {
                "row": 36,
                "name": "Транспортные расходы",
                "unit": "",
                "qty": "0.1",
                "work_price": "",
                "material_price": ""
              },
              {
                "row": 37,
                "name": "Накладные расходы",
                "unit": "",
                "qty": "0.08",
                "work_price": "",
                "material_price": ""
              },
              {
                "row": 41,
                "name": "Наименование",
                "unit": "Ед. изм.",
                "qty": "Кол-во",
                "work_price": "Работа",
                "material_price": "Материалы"
              },
              {
                "row": 44,
                "name": "Монтаж лаг цокольного перекрытия вкл террасы, крыльца",
                "unit": "м2",
                "qty": "109",
                "work_price": "1000",
                "material_price": "0"
              },
              {
                "row": 45,
                "name": "доска с/к 40х200",
                "unit": "м3",
                "qty": "2.616",
                "work_price": "0",
                "material_price": "24300"
              },
              {
                "row": 46,
                "name": "Устройство каркаса стен/перегородок",
                "unit": "м2",
                "qty": "180.135",
                "work_price": "1000",
                "material_price": "0"
              },
              {
                "row": 47,
                "name": "Монтаж стоек и балок террасы",
                "unit": "мп",
                "qty": "9",
                "work_price": "800",
                "material_price": "0"
              },
              {
                "row": 48,
                "name": "доска с/к 40х150",
                "unit": "м3",
                "qty": "5.0454",
                "work_price": "0",
                "material_price": "24300"
              },
              {
                "row": 49,
                "name": "доска с/к 40х100",
                "unit": "м3",
                "qty": "0.768",
                "work_price": "0",
                "material_price": "24300"
              },
              {
                "row": 50,
                "name": "бру с/с 150х150",
                "unit": "м3",
                "qty": "0.26999999999999996",
                "work_price": "0",
                "material_price": "30000"
              },
              {
                "row": 51,
                "name": "Монтаж баллок перекрытия",
                "unit": "м2",
                "qty": "0",
                "work_price": "1000",
                "material_price": "0"
              },
              {
                "row": 52,
                "name": "доска с/к 40х150",
                "unit": "м3",
                "qty": "0",
                "work_price": "0",
                "material_price": "24300"
              }
            ],
            "formula_count": 791,
            "formula_samples": [
              {
                "sheet": "Каркас под ключ",
                "cell": "E1",
                "formula": "=E2+E3+E4+E5+E6+E7+E8"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "E2",
                "formula": "=I40"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "E3",
                "formula": "=I63"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "E4",
                "formula": "=I102"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "E5",
                "formula": "=I121"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "E6",
                "formula": "=I158"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "E7",
                "formula": "=I230"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "E8",
                "formula": "=I264"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "F12",
                "formula": "=E12*D12"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "H12",
                "formula": "=D12*G12"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "I12",
                "formula": "=F12+H12"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "F13",
                "formula": "=E13*D13"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "F14",
                "formula": "=E14*D14"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "H14",
                "formula": "=D14*G14"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "I14",
                "formula": "=F14+H14"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "D15",
                "formula": "=D14/2"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "F15",
                "formula": "=E15*D15"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "H15",
                "formula": "=D15*G15"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "I15",
                "formula": "=F15+H15"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "F16",
                "formula": "=E16*D16"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "H16",
                "formula": "=D16*G16"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "I16",
                "formula": "=F16+H16"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "D17",
                "formula": "=D14+D16"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "F17",
                "formula": "=E17*D17"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "H17",
                "formula": "=D17*G17"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "I17",
                "formula": "=F17+H17"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "F18",
                "formula": "=E18*D18"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "H18",
                "formula": "=D18*G18"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "I18",
                "formula": "=F18+H18"
              },
              {
                "sheet": "Каркас под ключ",
                "cell": "F19",
                "formula": "=E19*D19"
              }
            ],
            "row_count": 285
          },
          {
            "sheet_name": "Газобетон",
            "scenario": "gasbeton_or_masonry_with_monolithic_foundation",
            "sections": [
              "Фундамент",
              "Стены",
              "Кровля",
              "Окна, двери",
              "Внешняя отделка",
              "Внутренняя отделка",
              "Инженерные коммуникации"
            ],
            "header_rows": [
              9,
              59,
              111,
              155,
              174,
              204,
              256
            ],
            "total_rows": [
              {
                "row": 56,
                "text": "Итого работа: 423924.316"
              },
              {
                "row": 57,
                "text": "Итого материалы: 633049.0299328001"
              },
              {
                "row": 58,
                "text": "Итого фундамент: 1056973.3459328"
              },
              {
                "row": 108,
                "text": "Итого работа: 556830.175"
              },
              {
                "row": 109,
                "text": "Итого материалы: 742975.012384"
              },
              {
                "row": 110,
                "text": "Итого стены : 1299805.187384"
              },
              {
                "row": 152,
                "text": "Итого работа: 529936.4"
              },
              {
                "row": 153,
                "text": "Итого материалы: 628855.6559680001"
              },
              {
                "row": 154,
                "text": "Итого кровля: 1158792.055968"
              },
              {
                "row": 171,
                "text": "Итого работа: 182710"
              },
              {
                "row": 172,
                "text": "Итого материалы: 743834"
              },
              {
                "row": 173,
                "text": "Итого окна, двери: 926544"
              },
              {
                "row": 201,
                "text": "Итого работа: 305167.64"
              },
              {
                "row": 202,
                "text": "Итого материалы: 318469.1861888"
              },
              {
                "row": 203,
                "text": "Итого внешняя отделка: 623636.8261888"
              },
              {
                "row": 253,
                "text": "Итого работа: 683979.2252"
              },
              {
                "row": 254,
                "text": "Итого материалы: 697688.6923125"
              },
              {
                "row": 255,
                "text": "Итого внутренняя отделка: 1381667.9175125"
              },
              {
                "row": 287,
                "text": "Итого работа: 230232"
              },
              {
                "row": 288,
                "text": "Итого материалы: 346375"
              },
              {
                "row": 289,
                "text": "Итого инженерные коммуникации: 576607"
              },
              {
                "row": 291,
                "text": "Итого РАБОТЫ: 2912779.7562"
              },
              {
                "row": 292,
                "text": "Итого МАТЕРИАЛЫ: 4111246.5767861004"
              },
              {
                "row": 293,
                "text": "ИТОГО СМЕТНАЯ СТОИМОСТЬ: 7024026.332986101"
              }
            ],
            "material_rows": 154,
            "work_rows": 99,
            "logistics_rows": 23,
            "sample_rows": [
              {
                "row": 9,
                "name": "Наименование",
                "unit": "Ед. изм.",
                "qty": "Кол-во",
                "work_price": "Работа",
                "material_price": "Материалы"
              },
              {
                "row": 12,
                "name": "Вынос осей в натуру",
                "unit": "м2",
                "qty": "112",
                "work_price": "80",
                "material_price": "0"
              },
              {
                "row": 13,
                "name": "Земляные работы, сопровождение работы экскаватора",
                "unit": "см",
                "qty": "1",
                "work_price": "12000",
                "material_price": "0"
              },
              {
                "row": 14,
                "name": "Аренда экскаватора",
                "unit": "см",
                "qty": "1",
                "work_price": "0",
                "material_price": "22000"
              },
              {
                "row": 15,
                "name": "Доработка грунта вручную",
                "unit": "м2",
                "qty": "155",
                "work_price": "150",
                "material_price": "0"
              },
              {
                "row": 16,
                "name": "Настил геотекстиля по основанию и стенам котлована (Геотекстиль 300 г/кв.м иглопробивной)",
                "unit": "м2",
                "qty": "205",
                "work_price": "80",
                "material_price": "60"
              },
              {
                "row": 17,
                "name": "Устройство песчаной подготовки т 200 мм с уплотнением.",
                "unit": "м3",
                "qty": "44",
                "work_price": "800",
                "material_price": "0"
              },
              {
                "row": 18,
                "name": "Аренда виброплиты (трамбовка)",
                "unit": "сут",
                "qty": "4",
                "work_price": "0",
                "material_price": "2500"
              },
              {
                "row": 19,
                "name": "Песок карьерный",
                "unit": "м3",
                "qty": "44",
                "work_price": "0",
                "material_price": "900"
              },
              {
                "row": 20,
                "name": "Устройство щебеночной подготовки т 100 мм с уплотнением.",
                "unit": "м3",
                "qty": "19",
                "work_price": "800",
                "material_price": "0"
              },
              {
                "row": 21,
                "name": "Аренда виброплиты (трамбовка)",
                "unit": "сут",
                "qty": "4",
                "work_price": "0",
                "material_price": "2500"
              },
              {
                "row": 22,
                "name": "Щебень фр 20-40",
                "unit": "м3",
                "qty": "19",
                "work_price": "0",
                "material_price": "1880"
              },
              {
                "row": 24,
                "name": "Укладка канализационной трубы в грунт",
                "unit": "мп",
                "qty": "28",
                "work_price": "900",
                "material_price": "0"
              },
              {
                "row": 25,
                "name": "Труба канализационная Ostendorf d110x2000 мм для наружной канализации",
                "unit": "шт",
                "qty": "10",
                "work_price": "0",
                "material_price": "670"
              },
              {
                "row": 26,
                "name": "Труба канализационная Ostendorf d110x1000 мм для наружной канализации",
                "unit": "шт",
                "qty": "3",
                "work_price": "0",
                "material_price": "400"
              },
              {
                "row": 27,
                "name": "Теплоизоляция для труб стенофлекс 114х13х2000 мм",
                "unit": "мп",
                "qty": "31",
                "work_price": "0",
                "material_price": "118"
              },
              {
                "row": 28,
                "name": "Комплект тройников, отводов, уголков для наружной канализации.",
                "unit": "к-т",
                "qty": "1",
                "work_price": "0",
                "material_price": "3500"
              },
              {
                "row": 29,
                "name": "Укладка закладной трубы в грунт под электрокабель",
                "unit": "мп",
                "qty": "15",
                "work_price": "400",
                "material_price": "0"
              },
              {
                "row": 30,
                "name": "Кабель NVO ВБШвнг(А) LS 5х2.5 20 м",
                "unit": "шт",
                "qty": "1",
                "work_price": "0",
                "material_price": "6600"
              },
              {
                "row": 31,
                "name": "Труба двустенная гофрированная ПНД/ПВД d63/52",
                "unit": "мп",
                "qty": "15",
                "work_price": "0",
                "material_price": "114"
              },
              {
                "row": 32,
                "name": "Укладка трубы ХВС в грунт на глубину 1,5м.",
                "unit": "мп",
                "qty": "10",
                "work_price": "850",
                "material_price": "0"
              },
              {
                "row": 33,
                "name": "Труба двустенная гофрированная ПНД/ПВД d63/52",
                "unit": "мп",
                "qty": "20",
                "work_price": "0",
                "material_price": "114"
              },
              {
                "row": 34,
                "name": "Труба ПНД (ПЭ-100) для систем водоснабжения премиум синяя 32 мм",
                "unit": "мп",
                "qty": "20",
                "work_price": "0",
                "material_price": "81"
              },
              {
                "row": 35,
                "name": "Настил технической пленки",
                "unit": "м2",
                "qty": "140",
                "work_price": "50",
                "material_price": "40"
              },
              {
                "row": 37,
                "name": "Устройство опалубки",
                "unit": "мп",
                "qty": "42.58",
                "work_price": "1100",
                "material_price": "0"
              },
              {
                "row": 38,
                "name": "Доска 50х150(100)х6000 мм е/в",
                "unit": "м3",
                "qty": "1.9160999999999997",
                "work_price": "0",
                "material_price": "17500"
              },
              {
                "row": 39,
                "name": "Устройство арматурного каркаса",
                "unit": "м2",
                "qty": "112",
                "work_price": "1200",
                "material_price": "0"
              },
              {
                "row": 40,
                "name": "Арматура металлическая д.12 А500",
                "unit": "т",
                "qty": "2.386944",
                "work_price": "0",
                "material_price": "70000"
              },
              {
                "row": 41,
                "name": "Арматура металлическая д.8 А500",
                "unit": "т",
                "qty": "0.26256384000000005",
                "work_price": "0",
                "material_price": "73000"
              },
              {
                "row": 42,
                "name": "Пеноплэкс Фундамент 100х585х1185",
                "unit": "шт",
                "qty": "3",
                "work_price": "0",
                "material_price": "709"
              },
              {
                "row": 43,
                "name": "Проволока вязальная 1,2мм",
                "unit": "кг",
                "qty": "59",
                "work_price": "0",
                "material_price": "160"
              },
              {
                "row": 44,
                "name": "Фиксаторы арматуры гориз.уп 250 шт",
                "unit": "уп",
                "qty": "3",
                "work_price": "0",
                "material_price": "1456"
              },
              {
                "row": 45,
                "name": "Бетонирование монолитной плиты с вибрированием",
                "unit": "м3",
                "qty": "25",
                "work_price": "2000",
                "material_price": "0"
              },
              {
                "row": 46,
                "name": "Бетон В20 W8 с доставкой*",
                "unit": "м3",
                "qty": "25",
                "work_price": "0",
                "material_price": "6500"
              },
              {
                "row": 47,
                "name": "глубинный вибратор",
                "unit": "сут",
                "qty": "1",
                "work_price": "0",
                "material_price": "1500"
              }
            ],
            "formula_count": 856,
            "formula_samples": [
              {
                "sheet": "Газобетон",
                "cell": "E1",
                "formula": "=E2+E3+E4+E5+E6+E7+E8"
              },
              {
                "sheet": "Газобетон",
                "cell": "E2",
                "formula": "=I58"
              },
              {
                "sheet": "Газобетон",
                "cell": "E3",
                "formula": "=I110"
              },
              {
                "sheet": "Газобетон",
                "cell": "E4",
                "formula": "=I154"
              },
              {
                "sheet": "Газобетон",
                "cell": "E5",
                "formula": "=I173"
              },
              {
                "sheet": "Газобетон",
                "cell": "E6",
                "formula": "=I203"
              },
              {
                "sheet": "Газобетон",
                "cell": "E7",
                "formula": "=I255"
              },
              {
                "sheet": "Газобетон",
                "cell": "E8",
                "formula": "=I289"
              },
              {
                "sheet": "Газобетон",
                "cell": "F12",
                "formula": "=E12*D12"
              },
              {
                "sheet": "Газобетон",
                "cell": "H12",
                "formula": "=D12*G12"
              },
              {
                "sheet": "Газобетон",
                "cell": "I12",
                "formula": "=F12+H12"
              },
              {
                "sheet": "Газобетон",
                "cell": "F13",
                "formula": "=E13*D13"
              },
              {
                "sheet": "Газобетон",
                "cell": "H13",
                "formula": "=D13*G13"
              },
              {
                "sheet": "Газобетон",
                "cell": "I13",
                "formula": "=F13+H13"
              },
              {
                "sheet": "Газобетон",
                "cell": "D14",
                "formula": "=D13"
              },
              {
                "sheet": "Газобетон",
                "cell": "F14",
                "formula": "=E14*D14"
              },
              {
                "sheet": "Газобетон",
                "cell": "H14",
                "formula": "=D14*G14"
              },
              {
                "sheet": "Газобетон",
                "cell": "I14",
                "formula": "=F14+H14"
              },
              {
                "sheet": "Газобетон",
                "cell": "F15",
                "formula": "=E15*D15"
              },
              {
                "sheet": "Газобетон",
                "cell": "H15",
                "formula": "=D15*G15"
              },
              {
                "sheet": "Газобетон",
                "cell": "I15",
                "formula": "=F15+H15"
              },
              {
                "sheet": "Газобетон",
                "cell": "D16",
                "formula": "=155+50"
              },
              {
                "sheet": "Газобетон",
                "cell": "F16",
                "formula": "=E16*D16"
              },
              {
                "sheet": "Газобетон",
                "cell": "H16",
                "formula": "=D16*G16"
              },
              {
                "sheet": "Газобетон",
                "cell": "I16",
                "formula": "=F16+H16"
              },
              {
                "sheet": "Газобетон",
                "cell": "D17",
                "formula": "=ROUNDUP(D15*0.2*1.4,)"
              },
              {
                "sheet": "Газобетон",
                "cell": "F17",
                "formula": "=E17*D17"
              },
              {
                "sheet": "Газобетон",
                "cell": "H17",
                "formula": "=D17*G17"
              },
              {
                "sheet": "Газобетон",
                "cell": "I17",
                "formula": "=F17+H17"
              },
              {
                "sheet": "Газобетон",
                "cell": "F18",
                "formula": "=E18*D18"
              }
            ],
            "row_count": 310
          }
        ]
      },
      {
        "key": "ROOF_FLOORS",
        "title": "крыша и перекр.xlsx",
        "template_role": "roof_and_floor_estimate_template",
        "description": "Эталон расчёта кровли и перекрытий",
        "file_id": "16YecwnJ9umnVprFu9V77UCV6cPrYbNh3",
        "drive_url": "https://docs.google.com/spreadsheets/d/16YecwnJ9umnVprFu9V77UCV6cPrYbNh3/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "modifiedTime": "2025-03-14T11:17:00.000Z",
        "parents": [
          "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
        ],
        "formula_total": 136,
        "formula_samples": [
          {
            "sheet": "расчет кровли",
            "cell": "F5",
            "formula": "=E5*D5"
          },
          {
            "sheet": "расчет кровли",
            "cell": "H5",
            "formula": "=G5*D5"
          },
          {
            "sheet": "расчет кровли",
            "cell": "I5",
            "formula": "=F5+H5"
          },
          {
            "sheet": "расчет кровли",
            "cell": "D6",
            "formula": "=11.27+0.19+0.052+0.011+0.031"
          },
          {
            "sheet": "расчет кровли",
            "cell": "F6",
            "formula": "=E6*D6"
          },
          {
            "sheet": "расчет кровли",
            "cell": "H6",
            "formula": "=G6*D6"
          },
          {
            "sheet": "расчет кровли",
            "cell": "I6",
            "formula": "=F6+H6"
          },
          {
            "sheet": "расчет кровли",
            "cell": "F7",
            "formula": "=E7*D7"
          },
          {
            "sheet": "расчет кровли",
            "cell": "H7",
            "formula": "=G7*D7"
          },
          {
            "sheet": "расчет кровли",
            "cell": "I7",
            "formula": "=F7+H7"
          },
          {
            "sheet": "расчет кровли",
            "cell": "D8",
            "formula": "=D5"
          },
          {
            "sheet": "расчет кровли",
            "cell": "F8",
            "formula": "=E8*D8"
          },
          {
            "sheet": "расчет кровли",
            "cell": "H8",
            "formula": "=G8*D8"
          },
          {
            "sheet": "расчет кровли",
            "cell": "I8",
            "formula": "=F8+H8"
          },
          {
            "sheet": "расчет кровли",
            "cell": "D9",
            "formula": "=D5"
          },
          {
            "sheet": "расчет кровли",
            "cell": "F9",
            "formula": "=E9*D9"
          },
          {
            "sheet": "расчет кровли",
            "cell": "H9",
            "formula": "=G9*D9"
          },
          {
            "sheet": "расчет кровли",
            "cell": "I9",
            "formula": "=F9+H9"
          },
          {
            "sheet": "расчет кровли",
            "cell": "D10",
            "formula": "=D5"
          },
          {
            "sheet": "расчет кровли",
            "cell": "F10",
            "formula": "=E10*D10"
          },
          {
            "sheet": "расчет кровли",
            "cell": "H10",
            "formula": "=G10*D10"
          },
          {
            "sheet": "расчет кровли",
            "cell": "I10",
            "formula": "=F10+H10"
          },
          {
            "sheet": "расчет кровли",
            "cell": "D11",
            "formula": "=D5"
          },
          {
            "sheet": "расчет кровли",
            "cell": "F11",
            "formula": "=E11*D11"
          },
          {
            "sheet": "расчет кровли",
            "cell": "H11",
            "formula": "=G11*D11"
          },
          {
            "sheet": "расчет кровли",
            "cell": "I11",
            "formula": "=F11+H11"
          },
          {
            "sheet": "расчет кровли",
            "cell": "F13",
            "formula": "=E13*D13"
          },
          {
            "sheet": "расчет кровли",
            "cell": "H13",
            "formula": "=D13*G13"
          },
          {
            "sheet": "расчет кровли",
            "cell": "I13",
            "formula": "=F13+H13"
          },
          {
            "sheet": "расчет кровли",
            "cell": "F14",
            "formula": "=E14*D14"
          },
          {
            "sheet": "расчет кровли",
            "cell": "H14",
            "formula": "=D14*G14"
          },
          {
            "sheet": "расчет кровли",
            "cell": "I14",
            "formula": "=F14+H14"
          },
          {
            "sheet": "расчет кровли",
            "cell": "F15",
            "formula": "=E15*D15"
          },
          {
            "sheet": "расчет кровли",
            "cell": "H15",
            "formula": "=D15*G15"
          },
          {
            "sheet": "расчет кровли",
            "cell": "I15",
            "formula": "=F15+H15"
          },
          {
            "sheet": "расчет кровли",
            "cell": "F16",
            "formula": "=D16*E16"
          },
          {
            "sheet": "расчет кровли",
            "cell": "H16",
            "formula": "=D16*G16"
          },
          {
            "sheet": "расчет кровли",
            "cell": "I16",
            "formula": "=F16+H16"
          },
          {
            "sheet": "расчет кровли",
            "cell": "L16",
            "formula": "=4.3+1.92+0.48+0.012"
          },
          {
            "sheet": "расчет кровли",
            "cell": "N16",
            "formula": "=L16/0.05*2"
          },
          {
            "sheet": "расчет кровли",
            "cell": "O16",
            "formula": "=L16/0.2*2"
          },
          {
            "sheet": "расчет кровли",
            "cell": "P16",
            "formula": "=O16+N16"
          },
          {
            "sheet": "расчет кровли",
            "cell": "D17",
            "formula": "=D16"
          },
          {
            "sheet": "расчет кровли",
            "cell": "F17",
            "formula": "=D17*E17"
          },
          {
            "sheet": "расчет кровли",
            "cell": "H17",
            "formula": "=D17*G17"
          },
          {
            "sheet": "расчет кровли",
            "cell": "I17",
            "formula": "=F17+H17"
          },
          {
            "sheet": "расчет кровли",
            "cell": "L17",
            "formula": "=0.027+0.023+0.034+0.01+0.014+0.021+0.017+0.016+0.032+0.087+0.054+0.034+0.047+0.16+0.032+0.032+0.016+0.02+1.76+0.41+0.041"
          },
          {
            "sheet": "расчет кровли",
            "cell": "N17",
            "formula": "=L17/0.05*2"
          },
          {
            "sheet": "расчет кровли",
            "cell": "O17",
            "formula": "=L17/0.2*2"
          },
          {
            "sheet": "расчет кровли",
            "cell": "P17",
            "formula": "=O17+N17"
          }
        ],
        "sheets": [
          {
            "sheet_name": "расчет кровли",
            "scenario": "roof_and_floors",
            "sections": [
              "Кровля"
            ],
            "header_rows": [
              1
            ],
            "total_rows": [
              {
                "row": 30,
                "text": "Итого работа: 2236634.6100000003"
              },
              {
                "row": 31,
                "text": "Итого материалы: 0"
              },
              {
                "row": 32,
                "text": "Итого кровля: 2236634.6100000003"
              }
            ],
            "material_rows": 1,
            "work_rows": 24,
            "logistics_rows": 1,
            "sample_rows": [
              {
                "row": 1,
                "name": "Наименование",
                "unit": "Ед. изм.",
                "qty": "Кол-во",
                "work_price": "Работа",
                "material_price": "Материалы"
              },
              {
                "row": 5,
                "name": "Устройство чердачного перекрытия",
                "unit": "м2",
                "qty": "191",
                "work_price": "1000",
                "material_price": "0"
              },
              {
                "row": 6,
                "name": "Антисептирование пиломатериалов с 4х сторон",
                "unit": "м3",
                "qty": "11.553999999999998",
                "work_price": "2800",
                "material_price": "0"
              },
              {
                "row": 7,
                "name": "Монтаж пароизоляции с проклейкой швов",
                "unit": "м2",
                "qty": "170",
                "work_price": "220",
                "material_price": "0"
              },
              {
                "row": 8,
                "name": "Монтаж обрешетки под утеплитель шаг 200",
                "unit": "м2",
                "qty": "191",
                "work_price": "380",
                "material_price": "0"
              },
              {
                "row": 9,
                "name": "Монтаж утепления 200 мм",
                "unit": "м2",
                "qty": "191",
                "work_price": "600",
                "material_price": "0"
              },
              {
                "row": 10,
                "name": "Монтаж гидро-ветрозащиты",
                "unit": "м2",
                "qty": "191",
                "work_price": "220",
                "material_price": "0"
              },
              {
                "row": 11,
                "name": "Монтаж разряженой обрешетки шаг 400",
                "unit": "м2",
                "qty": "191",
                "work_price": "360",
                "material_price": "0"
              },
              {
                "row": 13,
                "name": "Укладка мауэрлата по гидроизоляции",
                "unit": "мп",
                "qty": "78",
                "work_price": "850",
                "material_price": "0"
              },
              {
                "row": 14,
                "name": "Монтаж стропильной системы",
                "unit": "м2",
                "qty": "280",
                "work_price": "1400",
                "material_price": "0"
              },
              {
                "row": 15,
                "name": "Монтаж опорных стоек, каркасов стропильной системы",
                "unit": "к-т",
                "qty": "1",
                "work_price": "20000",
                "material_price": "0"
              },
              {
                "row": 16,
                "name": "Монтаж кровельной мембраны",
                "unit": "м2",
                "qty": "280",
                "work_price": "250",
                "material_price": "0"
              },
              {
                "row": 17,
                "name": "Монтаж контробрешетки",
                "unit": "м2",
                "qty": "280",
                "work_price": "360",
                "material_price": "0"
              },
              {
                "row": 18,
                "name": "Монтаж обрешётки шаг 350 мм",
                "unit": "м2",
                "qty": "280",
                "work_price": "360",
                "material_price": "0"
              },
              {
                "row": 19,
                "name": "Монтаж Металлочерепицы",
                "unit": "м2",
                "qty": "280",
                "work_price": "850",
                "material_price": "0"
              },
              {
                "row": 20,
                "name": "Монтаж доборных элементов",
                "unit": "мп",
                "qty": "231",
                "work_price": "550",
                "material_price": "0"
              },
              {
                "row": 21,
                "name": "Монтаж крюка длинного",
                "unit": "шт",
                "qty": "110",
                "work_price": "300",
                "material_price": "0"
              },
              {
                "row": 22,
                "name": "Монтаж вентвыходов на кровле",
                "unit": "к-т",
                "qty": "6",
                "work_price": "8500",
                "material_price": "0"
              },
              {
                "row": 23,
                "name": "Отделка лобовой доски (доской крашеной в заводских условиях)",
                "unit": "мп",
                "qty": "78",
                "work_price": "800",
                "material_price": "0"
              },
              {
                "row": 24,
                "name": "Подшивка потолка крыльца, террасы, свесов (доской крашеной в заводских условиях)",
                "unit": "м2",
                "qty": "118",
                "work_price": "1200",
                "material_price": "0"
              },
              {
                "row": 25,
                "name": "Монтаж водосточной системы",
                "unit": "мп",
                "qty": "104.63",
                "work_price": "900",
                "material_price": "0"
              },
              {
                "row": 26,
                "name": "Монтаж снегозадержания",
                "unit": "мп",
                "qty": "6",
                "work_price": "1200",
                "material_price": "0"
              },
              {
                "row": 27,
                "name": "Антисептирование пиломатериалов",
                "unit": "м3",
                "qty": "15.7",
                "work_price": "3000",
                "material_price": "0"
              },
              {
                "row": 28,
                "name": "Погрузо-разгрузочные работы",
                "unit": "усл",
                "qty": "2",
                "work_price": "10000",
                "material_price": "0"
              },
              {
                "row": 29,
                "name": "Накладные расходы",
                "unit": "",
                "qty": "0.05",
                "work_price": "",
                "material_price": ""
              }
            ],
            "formula_count": 136,
            "formula_samples": [
              {
                "sheet": "расчет кровли",
                "cell": "F5",
                "formula": "=E5*D5"
              },
              {
                "sheet": "расчет кровли",
                "cell": "H5",
                "formula": "=G5*D5"
              },
              {
                "sheet": "расчет кровли",
                "cell": "I5",
                "formula": "=F5+H5"
              },
              {
                "sheet": "расчет кровли",
                "cell": "D6",
                "formula": "=11.27+0.19+0.052+0.011+0.031"
              },
              {
                "sheet": "расчет кровли",
                "cell": "F6",
                "formula": "=E6*D6"
              },
              {
                "sheet": "расчет кровли",
                "cell": "H6",
                "formula": "=G6*D6"
              },
              {
                "sheet": "расчет кровли",
                "cell": "I6",
                "formula": "=F6+H6"
              },
              {
                "sheet": "расчет кровли",
                "cell": "F7",
                "formula": "=E7*D7"
              },
              {
                "sheet": "расчет кровли",
                "cell": "H7",
                "formula": "=G7*D7"
              },
              {
                "sheet": "расчет кровли",
                "cell": "I7",
                "formula": "=F7+H7"
              },
              {
                "sheet": "расчет кровли",
                "cell": "D8",
                "formula": "=D5"
              },
              {
                "sheet": "расчет кровли",
                "cell": "F8",
                "formula": "=E8*D8"
              },
              {
                "sheet": "расчет кровли",
                "cell": "H8",
                "formula": "=G8*D8"
              },
              {
                "sheet": "расчет кровли",
                "cell": "I8",
                "formula": "=F8+H8"
              },
              {
                "sheet": "расчет кровли",
                "cell": "D9",
                "formula": "=D5"
              },
              {
                "sheet": "расчет кровли",
                "cell": "F9",
                "formula": "=E9*D9"
              },
              {
                "sheet": "расчет кровли",
                "cell": "H9",
                "formula": "=G9*D9"
              },
              {
                "sheet": "расчет кровли",
                "cell": "I9",
                "formula": "=F9+H9"
              },
              {
                "sheet": "расчет кровли",
                "cell": "D10",
                "formula": "=D5"
              },
              {
                "sheet": "расчет кровли",
                "cell": "F10",
                "formula": "=E10*D10"
              },
              {
                "sheet": "расчет кровли",
                "cell": "H10",
                "formula": "=G10*D10"
              },
              {
                "sheet": "расчет кровли",
                "cell": "I10",
                "formula": "=F10+H10"
              },
              {
                "sheet": "расчет кровли",
                "cell": "D11",
                "formula": "=D5"
              },
              {
                "sheet": "расчет кровли",
                "cell": "F11",
                "formula": "=E11*D11"
              },
              {
                "sheet": "расчет кровли",
                "cell": "H11",
                "formula": "=G11*D11"
              },
              {
                "sheet": "расчет кровли",
                "cell": "I11",
                "formula": "=F11+H11"
              },
              {
                "sheet": "расчет кровли",
                "cell": "F13",
                "formula": "=E13*D13"
              },
              {
                "sheet": "расчет кровли",
                "cell": "H13",
                "formula": "=D13*G13"
              },
              {
                "sheet": "расчет кровли",
                "cell": "I13",
                "formula": "=F13+H13"
              },
              {
                "sheet": "расчет кровли",
                "cell": "F14",
                "formula": "=E14*D14"
              }
            ],
            "row_count": 747
          }
        ]
      },
      {
        "key": "FOUNDATION_WAREHOUSE",
        "title": "фундамент_Склад2.xlsx",
        "template_role": "foundation_estimate_template",
        "description": "Эталон расчёта фундамента",
        "file_id": "1KuoSI4OI7gJoIBPVqBQGXtQnolXKMiDp",
        "drive_url": "https://docs.google.com/spreadsheets/d/1KuoSI4OI7gJoIBPVqBQGXtQnolXKMiDp/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "modifiedTime": "2025-05-27T08:01:58.000Z",
        "parents": [
          "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
        ],
        "formula_total": 88,
        "formula_samples": [
          {
            "sheet": "смета",
            "cell": "F4",
            "formula": "=E4*D4"
          },
          {
            "sheet": "смета",
            "cell": "F5",
            "formula": "=E5*D5"
          },
          {
            "sheet": "смета",
            "cell": "H5",
            "formula": "=D5*G5"
          },
          {
            "sheet": "смета",
            "cell": "I5",
            "formula": "=F5+H5"
          },
          {
            "sheet": "смета",
            "cell": "D6",
            "formula": "=ROUNDUP((680*0.62)/200,0)"
          },
          {
            "sheet": "смета",
            "cell": "F6",
            "formula": "=E6*D6"
          },
          {
            "sheet": "смета",
            "cell": "H6",
            "formula": "=D6*G6"
          },
          {
            "sheet": "смета",
            "cell": "I6",
            "formula": "=F6+H6"
          },
          {
            "sheet": "смета",
            "cell": "D7",
            "formula": "=D6"
          },
          {
            "sheet": "смета",
            "cell": "F7",
            "formula": "=E7*D7"
          },
          {
            "sheet": "смета",
            "cell": "H7",
            "formula": "=D7*G7"
          },
          {
            "sheet": "смета",
            "cell": "I7",
            "formula": "=F7+H7"
          },
          {
            "sheet": "смета",
            "cell": "F8",
            "formula": "=E8*D8"
          },
          {
            "sheet": "смета",
            "cell": "H8",
            "formula": "=D8*G8"
          },
          {
            "sheet": "смета",
            "cell": "I8",
            "formula": "=F8+H8"
          },
          {
            "sheet": "смета",
            "cell": "F9",
            "formula": "=E9*D9"
          },
          {
            "sheet": "смета",
            "cell": "H9",
            "formula": "=D9*G9"
          },
          {
            "sheet": "смета",
            "cell": "I9",
            "formula": "=F9+H9"
          },
          {
            "sheet": "смета",
            "cell": "F10",
            "formula": "=E10*D10"
          },
          {
            "sheet": "смета",
            "cell": "H10",
            "formula": "=D10*G10"
          },
          {
            "sheet": "смета",
            "cell": "I10",
            "formula": "=F10+H10"
          },
          {
            "sheet": "смета",
            "cell": "D11",
            "formula": "=114+493"
          },
          {
            "sheet": "смета",
            "cell": "F11",
            "formula": "=E11*D11"
          },
          {
            "sheet": "смета",
            "cell": "H11",
            "formula": "=G11*D11"
          },
          {
            "sheet": "смета",
            "cell": "I11",
            "formula": "=F11+H11"
          },
          {
            "sheet": "смета",
            "cell": "F12",
            "formula": "=E12*D12"
          },
          {
            "sheet": "смета",
            "cell": "H12",
            "formula": "=G12*D12"
          },
          {
            "sheet": "смета",
            "cell": "I12",
            "formula": "=F12+H12"
          },
          {
            "sheet": "смета",
            "cell": "F13",
            "formula": "=E13*D13"
          },
          {
            "sheet": "смета",
            "cell": "H13",
            "formula": "=G13*D13"
          },
          {
            "sheet": "смета",
            "cell": "I13",
            "formula": "=F13+H13"
          },
          {
            "sheet": "смета",
            "cell": "F14",
            "formula": "=E14*D14"
          },
          {
            "sheet": "смета",
            "cell": "H14",
            "formula": "=G14*D14"
          },
          {
            "sheet": "смета",
            "cell": "I14",
            "formula": "=F14+H14"
          },
          {
            "sheet": "смета",
            "cell": "F15",
            "formula": "=E15*D15"
          },
          {
            "sheet": "смета",
            "cell": "H15",
            "formula": "=G15*D15"
          },
          {
            "sheet": "смета",
            "cell": "I15",
            "formula": "=F15+H15"
          },
          {
            "sheet": "смета",
            "cell": "D16",
            "formula": "=ROUNDUP(171.2*1.1,)"
          },
          {
            "sheet": "смета",
            "cell": "F16",
            "formula": "=E16*D16"
          },
          {
            "sheet": "смета",
            "cell": "H16",
            "formula": "=G16*D16"
          },
          {
            "sheet": "смета",
            "cell": "I16",
            "formula": "=F16+H16"
          },
          {
            "sheet": "смета",
            "cell": "F17",
            "formula": "=E17*D17"
          },
          {
            "sheet": "смета",
            "cell": "H17",
            "formula": "=D17*G17"
          },
          {
            "sheet": "смета",
            "cell": "I17",
            "formula": "=F17+H17"
          },
          {
            "sheet": "смета",
            "cell": "F18",
            "formula": "=E18*D18"
          },
          {
            "sheet": "смета",
            "cell": "F19",
            "formula": "=E19*D19"
          },
          {
            "sheet": "смета",
            "cell": "H19",
            "formula": "=G19*D19"
          },
          {
            "sheet": "смета",
            "cell": "I19",
            "formula": "=F19+H19"
          },
          {
            "sheet": "смета",
            "cell": "F20",
            "formula": "=E20*D20"
          },
          {
            "sheet": "смета",
            "cell": "F21",
            "formula": "=E21*D21"
          }
        ],
        "sheets": [
          {
            "sheet_name": "смета",
            "scenario": "foundation",
            "sections": [
              "Фундамент"
            ],
            "header_rows": [
              1
            ],
            "total_rows": [
              {
                "row": 33,
                "text": "Итого работа: 2915677.0762500004"
              },
              {
                "row": 35,
                "text": "Итого материалы: 84240"
              },
              {
                "row": 36,
                "text": "Итого фундамент: 3116917.0762500004"
              }
            ],
            "material_rows": 6,
            "work_rows": 17,
            "logistics_rows": 0,
            "sample_rows": [
              {
                "row": 1,
                "name": "Наименование",
                "unit": "Ед. изм.",
                "qty": "Кол-во",
                "work_price": "Работа",
                "material_price": "Материалы"
              },
              {
                "row": 5,
                "name": "Вынос осей в натуру",
                "unit": "см",
                "qty": "1",
                "work_price": "18000",
                "material_price": "0"
              },
              {
                "row": 6,
                "name": "Земляные работы, сопровождение работы экскаватора",
                "unit": "см",
                "qty": "3",
                "work_price": "10000",
                "material_price": "0"
              },
              {
                "row": 7,
                "name": "Аренда экскаватора",
                "unit": "см",
                "qty": "3",
                "work_price": "0",
                "material_price": "24000"
              },
              {
                "row": 8,
                "name": "Доработка грунта вручную",
                "unit": "м2",
                "qty": "680",
                "work_price": "50",
                "material_price": "0"
              },
              {
                "row": 10,
                "name": "Настил геотекстиля",
                "unit": "м2",
                "qty": "608",
                "work_price": "80",
                "material_price": "0"
              },
              {
                "row": 11,
                "name": "Отсыпка основания щебнем и песком с формированием откосов под ребра жесткости",
                "unit": "м3",
                "qty": "607",
                "work_price": "850",
                "material_price": "0"
              },
              {
                "row": 12,
                "name": "Настил п/э пленки",
                "unit": "м2",
                "qty": "606",
                "work_price": "80",
                "material_price": "0"
              },
              {
                "row": 14,
                "name": "Монтаж опалубки",
                "unit": "мп",
                "qty": "108.46",
                "work_price": "1100",
                "material_price": "0"
              },
              {
                "row": 15,
                "name": "Устройство арматурного каркаса",
                "unit": "м2",
                "qty": "507.23",
                "work_price": "1300",
                "material_price": "0"
              },
              {
                "row": 16,
                "name": "Бетонирование с уплотнением",
                "unit": "м3",
                "qty": "189",
                "work_price": "2000",
                "material_price": "0"
              },
              {
                "row": 17,
                "name": "Аренда бетононасоса",
                "unit": "см",
                "qty": "2",
                "work_price": "0",
                "material_price": "31000"
              },
              {
                "row": 19,
                "name": "Монтаж анкерных групп",
                "unit": "шт",
                "qty": "23",
                "work_price": "6500",
                "material_price": "0"
              },
              {
                "row": 21,
                "name": "Устройство ростверка поверх фундаментной плиты (опалубка, арматура, бетонирование)",
                "unit": "мп",
                "qty": "86.257",
                "work_price": "2800",
                "material_price": "0"
              },
              {
                "row": 22,
                "name": "Аренда бетононасоса",
                "unit": "см",
                "qty": "1",
                "work_price": "0",
                "material_price": "31000"
              },
              {
                "row": 24,
                "name": "Устройство обмазочной гидроизоляции в 2 слоя торца плиты с ребрами жесткости и внешней стороны ростверка",
                "unit": "м2",
                "qty": "121.14304999999999",
                "work_price": "350",
                "material_price": "0"
              },
              {
                "row": 25,
                "name": "Утепление торца плиты с ребрами жесткости и внешней стороны ростверка ЭППс 100 мм",
                "unit": "м2",
                "qty": "121.14304999999999",
                "work_price": "400",
                "material_price": "0"
              },
              {
                "row": 27,
                "name": "Монтаж опалубки",
                "unit": "мп",
                "qty": "30",
                "work_price": "1100",
                "material_price": "0"
              },
              {
                "row": 28,
                "name": "Устройство арматурного каркаса",
                "unit": "м2",
                "qty": "108",
                "work_price": "1200",
                "material_price": "0"
              },
              {
                "row": 29,
                "name": "Бетонирование с уплотнением",
                "unit": "м3",
                "qty": "24",
                "work_price": "2000",
                "material_price": "0"
              },
              {
                "row": 30,
                "name": "Аренда бетононасоса",
                "unit": "см",
                "qty": "1",
                "work_price": "0",
                "material_price": "31000"
              },
              {
                "row": 31,
                "name": "Крепеж и расходные материалы по разделу",
                "unit": "к-т",
                "qty": "702",
                "work_price": "0",
                "material_price": "120"
              },
              {
                "row": 32,
                "name": "Накладные расходы",
                "unit": "",
                "qty": "0.1",
                "work_price": "",
                "material_price": ""
              }
            ],
            "formula_count": 88,
            "formula_samples": [
              {
                "sheet": "смета",
                "cell": "F4",
                "formula": "=E4*D4"
              },
              {
                "sheet": "смета",
                "cell": "F5",
                "formula": "=E5*D5"
              },
              {
                "sheet": "смета",
                "cell": "H5",
                "formula": "=D5*G5"
              },
              {
                "sheet": "смета",
                "cell": "I5",
                "formula": "=F5+H5"
              },
              {
                "sheet": "смета",
                "cell": "D6",
                "formula": "=ROUNDUP((680*0.62)/200,0)"
              },
              {
                "sheet": "смета",
                "cell": "F6",
                "formula": "=E6*D6"
              },
              {
                "sheet": "смета",
                "cell": "H6",
                "formula": "=D6*G6"
              },
              {
                "sheet": "смета",
                "cell": "I6",
                "formula": "=F6+H6"
              },
              {
                "sheet": "смета",
                "cell": "D7",
                "formula": "=D6"
              },
              {
                "sheet": "смета",
                "cell": "F7",
                "formula": "=E7*D7"
              },
              {
                "sheet": "смета",
                "cell": "H7",
                "formula": "=D7*G7"
              },
              {
                "sheet": "смета",
                "cell": "I7",
                "formula": "=F7+H7"
              },
              {
                "sheet": "смета",
                "cell": "F8",
                "formula": "=E8*D8"
              },
              {
                "sheet": "смета",
                "cell": "H8",
                "formula": "=D8*G8"
              },
              {
                "sheet": "смета",
                "cell": "I8",
                "formula": "=F8+H8"
              },
              {
                "sheet": "смета",
                "cell": "F9",
                "formula": "=E9*D9"
              },
              {
                "sheet": "смета",
                "cell": "H9",
                "formula": "=D9*G9"
              },
              {
                "sheet": "смета",
                "cell": "I9",
                "formula": "=F9+H9"
              },
              {
                "sheet": "смета",
                "cell": "F10",
                "formula": "=E10*D10"
              },
              {
                "sheet": "смета",
                "cell": "H10",
                "formula": "=D10*G10"
              },
              {
                "sheet": "смета",
                "cell": "I10",
                "formula": "=F10+H10"
              },
              {
                "sheet": "смета",
                "cell": "D11",
                "formula": "=114+493"
              },
              {
                "sheet": "смета",
                "cell": "F11",
                "formula": "=E11*D11"
              },
              {
                "sheet": "смета",
                "cell": "H11",
                "formula": "=G11*D11"
              },
              {
                "sheet": "смета",
                "cell": "I11",
                "formula": "=F11+H11"
              },
              {
                "sheet": "смета",
                "cell": "F12",
                "formula": "=E12*D12"
              },
              {
                "sheet": "смета",
                "cell": "H12",
                "formula": "=G12*D12"
              },
              {
                "sheet": "смета",
                "cell": "I12",
                "formula": "=F12+H12"
              },
              {
                "sheet": "смета",
                "cell": "F13",
                "formula": "=E13*D13"
              },
              {
                "sheet": "смета",
                "cell": "H13",
                "formula": "=G13*D13"
              }
            ],
            "row_count": 50
          }
        ]
      },
      {
        "key": "AREAL_NEVA",
        "title": "Ареал Нева.xlsx",
        "template_role": "general_company_estimate_template",
        "description": "Общий эталон сметной структуры Ареал-Нева",
        "file_id": "1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm",
        "drive_url": "https://docs.google.com/spreadsheets/d/1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "modifiedTime": "2026-05-02T12:04:37.000Z",
        "parents": [
          "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
        ],
        "formula_total": 1192,
        "formula_samples": [
          {
            "sheet": "смета",
            "cell": "H1",
            "formula": "=SUM(H2:I9)"
          },
          {
            "sheet": "смета",
            "cell": "H2",
            "formula": "=L59"
          },
          {
            "sheet": "смета",
            "cell": "H3",
            "formula": "=L88"
          },
          {
            "sheet": "смета",
            "cell": "H4",
            "formula": "=L108"
          },
          {
            "sheet": "смета",
            "cell": "H5",
            "formula": "=L134"
          },
          {
            "sheet": "смета",
            "cell": "H6",
            "formula": "=L175"
          },
          {
            "sheet": "смета",
            "cell": "H7",
            "formula": "=L190"
          },
          {
            "sheet": "смета",
            "cell": "H8",
            "formula": "=L228"
          },
          {
            "sheet": "смета",
            "cell": "H9",
            "formula": "=L256"
          },
          {
            "sheet": "смета",
            "cell": "F13",
            "formula": "=E13*D13"
          },
          {
            "sheet": "смета",
            "cell": "H13",
            "formula": "=G13*E13"
          },
          {
            "sheet": "смета",
            "cell": "I13",
            "formula": "=H13*D13"
          },
          {
            "sheet": "смета",
            "cell": "K13",
            "formula": "=J13*D13"
          },
          {
            "sheet": "смета",
            "cell": "L13",
            "formula": "=K13+I13"
          },
          {
            "sheet": "смета",
            "cell": "D14",
            "formula": "=_xlfn.CEILING.MATH(D13*1.2/30,)"
          },
          {
            "sheet": "смета",
            "cell": "F14",
            "formula": "=E14*D14"
          },
          {
            "sheet": "смета",
            "cell": "H14",
            "formula": "=G14*E14"
          },
          {
            "sheet": "смета",
            "cell": "I14",
            "formula": "=H14*D14"
          },
          {
            "sheet": "смета",
            "cell": "K14",
            "formula": "=J14*D14"
          },
          {
            "sheet": "смета",
            "cell": "L14",
            "formula": "=K14+I14"
          },
          {
            "sheet": "смета",
            "cell": "M14",
            "formula": "=D14*3.6*15/1000"
          },
          {
            "sheet": "смета",
            "cell": "D15",
            "formula": "=21.1+10.48+92.15"
          },
          {
            "sheet": "смета",
            "cell": "F15",
            "formula": "=E15*D15"
          },
          {
            "sheet": "смета",
            "cell": "H15",
            "formula": "=G15*E15"
          },
          {
            "sheet": "смета",
            "cell": "I15",
            "formula": "=H15*D15"
          },
          {
            "sheet": "смета",
            "cell": "K15",
            "formula": "=J15*D15"
          },
          {
            "sheet": "смета",
            "cell": "L15",
            "formula": "=K15+I15"
          },
          {
            "sheet": "смета",
            "cell": "D16",
            "formula": "=88+20"
          },
          {
            "sheet": "смета",
            "cell": "F16",
            "formula": "=E16*D16"
          },
          {
            "sheet": "смета",
            "cell": "H16",
            "formula": "=G16*E16"
          },
          {
            "sheet": "смета",
            "cell": "I16",
            "formula": "=H16*D16"
          },
          {
            "sheet": "смета",
            "cell": "K16",
            "formula": "=J16*D16"
          },
          {
            "sheet": "смета",
            "cell": "L16",
            "formula": "=K16+I16"
          },
          {
            "sheet": "смета",
            "cell": "M16",
            "formula": "=D16*25/1000"
          },
          {
            "sheet": "смета",
            "cell": "F17",
            "formula": "=E17*D17"
          },
          {
            "sheet": "смета",
            "cell": "H17",
            "formula": "=G17*E17"
          },
          {
            "sheet": "смета",
            "cell": "I17",
            "formula": "=H17*D17"
          },
          {
            "sheet": "смета",
            "cell": "K17",
            "formula": "=J17*D17"
          },
          {
            "sheet": "смета",
            "cell": "L17",
            "formula": "=K17+I17"
          },
          {
            "sheet": "смета",
            "cell": "F18",
            "formula": "=E18*D18"
          },
          {
            "sheet": "смета",
            "cell": "H18",
            "formula": "=G18*E18"
          },
          {
            "sheet": "смета",
            "cell": "I18",
            "formula": "=H18*D18"
          },
          {
            "sheet": "смета",
            "cell": "K18",
            "formula": "=J18*D18"
          },
          {
            "sheet": "смета",
            "cell": "L18",
            "formula": "=K18+I18"
          },
          {
            "sheet": "смета",
            "cell": "F19",
            "formula": "=E19*D19"
          },
          {
            "sheet": "смета",
            "cell": "H19",
            "formula": "=G19*E19"
          },
          {
            "sheet": "смета",
            "cell": "I19",
            "formula": "=H19*D19"
          },
          {
            "sheet": "смета",
            "cell": "K19",
            "formula": "=J19*D19"
          },
          {
            "sheet": "смета",
            "cell": "L19",
            "formula": "=K19+I19"
          },
          {
            "sheet": "смета",
            "cell": "D20",
            "formula": "=D15*4*1.15/1000"
          }
        ],
        "sheets": [
          {
            "sheet_name": "смета",
            "scenario": "gasbeton_or_masonry_with_monolithic_foundation",
            "sections": [
              "Кровля",
              "Окна, двери",
              "Внешняя отделка"
            ],
            "header_rows": [
              10,
              60,
              89,
              109,
              135,
              176,
              191,
              229
            ],
            "total_rows": [
              {
                "row": 58,
                "text": "Итого материалы: 1680034.1595788796"
              },
              {
                "row": 59,
                "text": "Итого стены, перегородки: 3241241.2684789114"
              },
              {
                "row": 87,
                "text": "Итого материалы: 1090794.738551488"
              },
              {
                "row": 88,
                "text": "Итого перекрытие: 1769547.369441491"
              },
              {
                "row": 107,
                "text": "Итого материалы: 102555.32"
              },
              {
                "row": 108,
                "text": "Итого Монолитная лестница: 215046.5296"
              },
              {
                "row": 133,
                "text": "Итого материалы: 653804.812"
              },
              {
                "row": 134,
                "text": "Итого Плита покрытия: 1112208.3857600002"
              },
              {
                "row": 174,
                "text": "Итого материалы: 1341914.6016"
              },
              {
                "row": 175,
                "text": "Итого крыша: 2323433.1369439997"
              },
              {
                "row": 189,
                "text": "Итого материалы: 746966.3"
              },
              {
                "row": 190,
                "text": "Итого Окна, двери: 906743.5"
              },
              {
                "row": 227,
                "text": "Итого материалы: 1888361.2"
              },
              {
                "row": 228,
                "text": "Итого внешняя отделка: 3125622.04768"
              },
              {
                "row": 255,
                "text": "Итого материалы: 569074.08"
              },
              {
                "row": 256,
                "text": "Итого Внутренняя черновая отделка: 1392456.54324"
              },
              {
                "row": 258,
                "text": "Итого РАБОТЫ: 6012793.569414035"
              },
              {
                "row": 259,
                "text": "Итого МАТЕРИАЛЫ: 8073505.2117303675"
              },
              {
                "row": 260,
                "text": "ИТОГО СМЕТНАЯ СТОИМОСТЬ: 14086298.781144403"
              }
            ],
            "material_rows": 194,
            "work_rows": 78,
            "logistics_rows": 18,
            "sample_rows": [
              {
                "row": 10,
                "name": "Наименование",
                "unit": "Ед. изм.",
                "qty": "Кол-во",
                "work_price": "Себестоимость работ",
                "material_price": "коэф на работы"
              },
              {
                "row": 13,
                "name": "Устройство отсечной гидроизоляции основания стен",
                "unit": "мп",
                "qty": "52",
                "work_price": "100",
                "material_price": "2"
              },
              {
                "row": 14,
                "name": "Гидроизоляция Линокром ХПП Технониколь черный 15 кв.м",
                "unit": "рул",
                "qty": "3",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 15,
                "name": "Кладка стен из газобетона, вкл парапет",
                "unit": "м3",
                "qty": "123.73",
                "work_price": "3000",
                "material_price": "2.2"
              },
              {
                "row": 16,
                "name": "Цементно-песчаная смесь ЦПС-300 25 кг.",
                "unit": "шт",
                "qty": "108",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 17,
                "name": "БЛОК 625X400X250",
                "unit": "м3",
                "qty": "98",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 18,
                "name": "БЛОК 625X300X250",
                "unit": "м3",
                "qty": "12",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 19,
                "name": "БЛОК 625X250X250",
                "unit": "м3",
                "qty": "24",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 20,
                "name": "Арматура А3 А240 8мм рифленая",
                "unit": "т",
                "qty": "0.569158",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 21,
                "name": "Клей для газобетона 25 кг",
                "unit": "шт",
                "qty": "154",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 22,
                "name": "Кладка перегородок из газобетона",
                "unit": "м3",
                "qty": "13.72",
                "work_price": "6500",
                "material_price": "2"
              },
              {
                "row": 23,
                "name": "Цементно-песчаная смесь ЦПС-300 25 кг.",
                "unit": "шт",
                "qty": "7",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 24,
                "name": "БЛОК 625X150X250",
                "unit": "м3",
                "qty": "16",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 25,
                "name": "Арматура класс А3 500С 8мм рифленая",
                "unit": "т",
                "qty": "0.07948600000000001",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 26,
                "name": "Клей для газобетона 25 кг",
                "unit": "шт",
                "qty": "17",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 27,
                "name": "Аренда крана",
                "unit": "см",
                "qty": "3",
                "work_price": "27000",
                "material_price": "1.15"
              },
              {
                "row": 28,
                "name": "Устройство ж/б колонн",
                "unit": "мп",
                "qty": "8.75",
                "work_price": "1300",
                "material_price": "2"
              },
              {
                "row": 29,
                "name": "Арматура металлическая д.12 А500",
                "unit": "т",
                "qty": "0.041503500000000006",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 30,
                "name": "Арматура металлическая д.8 А240",
                "unit": "т",
                "qty": "0.028151999999999996",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 31,
                "name": "Проволока вязальная 1,2мм",
                "unit": "кг",
                "qty": "2",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 32,
                "name": "Пескобетон (ЦПС М300) 40 кг",
                "unit": "шт",
                "qty": "32",
                "work_price": "",
                "material_price": ""
              },
              {
                "row": 33,
                "name": "Доска обрезная 40*150(100/200)*6000мм е/в",
                "unit": "м3",
                "qty": "0.4725",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 34,
                "name": "Устройство армопояса парапета",
                "unit": "мп",
                "qty": "75.93",
                "work_price": "900",
                "material_price": "2"
              },
              {
                "row": 35,
                "name": "Арматура металлическая д.12 А500",
                "unit": "т",
                "qty": "0.16182201599999999",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 36,
                "name": "Арматура металлическая д.8 А500",
                "unit": "т",
                "qty": "0.06998215",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 37,
                "name": "Проволока вязальная 1,2мм",
                "unit": "кг",
                "qty": "4",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 38,
                "name": "Бетон В25 W6",
                "unit": "м3",
                "qty": "4",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 39,
                "name": "Доска обрезная 40*150*6000мм е/в хв/п",
                "unit": "м3",
                "qty": "0.9111600000000001",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 40,
                "name": "Устройство перемычки/ армопояс из U блоков",
                "unit": "мп",
                "qty": "36.1",
                "work_price": "1000",
                "material_price": "2"
              },
              {
                "row": 41,
                "name": "U-блок 300 300х250х500мм",
                "unit": "шт",
                "qty": "7",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 42,
                "name": "U-блок 400 400х250х500мм",
                "unit": "шт",
                "qty": "66",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 43,
                "name": "Арматура металлическая д.12 А500",
                "unit": "т",
                "qty": "0.15387263999999998",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 44,
                "name": "Арматура металлическая д.8 А500",
                "unit": "т",
                "qty": "0.059411",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 45,
                "name": "Проволока вязальная 1,2мм",
                "unit": "кг",
                "qty": "4",
                "work_price": "",
                "material_price": "2"
              },
              {
                "row": 46,
                "name": "Пескобетон (ЦПС М300) 40 кг",
                "unit": "шт",
                "qty": "36",
                "work_price": "",
                "material_price": ""
              }
            ],
            "formula_count": 1192,
            "formula_samples": [
              {
                "sheet": "смета",
                "cell": "H1",
                "formula": "=SUM(H2:I9)"
              },
              {
                "sheet": "смета",
                "cell": "H2",
                "formula": "=L59"
              },
              {
                "sheet": "смета",
                "cell": "H3",
                "formula": "=L88"
              },
              {
                "sheet": "смета",
                "cell": "H4",
                "formula": "=L108"
              },
              {
                "sheet": "смета",
                "cell": "H5",
                "formula": "=L134"
              },
              {
                "sheet": "смета",
                "cell": "H6",
                "formula": "=L175"
              },
              {
                "sheet": "смета",
                "cell": "H7",
                "formula": "=L190"
              },
              {
                "sheet": "смета",
                "cell": "H8",
                "formula": "=L228"
              },
              {
                "sheet": "смета",
                "cell": "H9",
                "formula": "=L256"
              },
              {
                "sheet": "смета",
                "cell": "F13",
                "formula": "=E13*D13"
              },
              {
                "sheet": "смета",
                "cell": "H13",
                "formula": "=G13*E13"
              },
              {
                "sheet": "смета",
                "cell": "I13",
                "formula": "=H13*D13"
              },
              {
                "sheet": "смета",
                "cell": "K13",
                "formula": "=J13*D13"
              },
              {
                "sheet": "смета",
                "cell": "L13",
                "formula": "=K13+I13"
              },
              {
                "sheet": "смета",
                "cell": "D14",
                "formula": "=_xlfn.CEILING.MATH(D13*1.2/30,)"
              },
              {
                "sheet": "смета",
                "cell": "F14",
                "formula": "=E14*D14"
              },
              {
                "sheet": "смета",
                "cell": "H14",
                "formula": "=G14*E14"
              },
              {
                "sheet": "смета",
                "cell": "I14",
                "formula": "=H14*D14"
              },
              {
                "sheet": "смета",
                "cell": "K14",
                "formula": "=J14*D14"
              },
              {
                "sheet": "смета",
                "cell": "L14",
                "formula": "=K14+I14"
              },
              {
                "sheet": "смета",
                "cell": "M14",
                "formula": "=D14*3.6*15/1000"
              },
              {
                "sheet": "смета",
                "cell": "D15",
                "formula": "=21.1+10.48+92.15"
              },
              {
                "sheet": "смета",
                "cell": "F15",
                "formula": "=E15*D15"
              },
              {
                "sheet": "смета",
                "cell": "H15",
                "formula": "=G15*E15"
              },
              {
                "sheet": "смета",
                "cell": "I15",
                "formula": "=H15*D15"
              },
              {
                "sheet": "смета",
                "cell": "K15",
                "formula": "=J15*D15"
              },
              {
                "sheet": "смета",
                "cell": "L15",
                "formula": "=K15+I15"
              },
              {
                "sheet": "смета",
                "cell": "D16",
                "formula": "=88+20"
              },
              {
                "sheet": "смета",
                "cell": "F16",
                "formula": "=E16*D16"
              },
              {
                "sheet": "смета",
                "cell": "H16",
                "formula": "=G16*E16"
              }
            ],
            "row_count": 274
          }
        ]
      }
    ],
    "canonical_columns": [
      "№ п/п",
      "Наименование",
      "Ед. изм.",
      "Кол-во",
      "Работа Цена",
      "Работа Стоимость",
      "Материалы Цена",
      "Материалы Стоимость",
      "Всего",
      "Примечание"
    ],
    "canonical_sections": [
      "Фундамент",
      "Каркас",
      "Стены",
      "Перекрытия",
      "Кровля",
      "Окна, двери",
      "Внешняя отделка",
      "Внутренняя отделка",
      "Инженерные коммуникации",
      "Логистика",
      "Накладные расходы"
    ],
    "universal_material_groups": {
      "стены": [
        "кирпич",
        "газобетон",
        "керамоблок",
        "арболит",
        "монолит",
        "каркас",
        "брус"
      ],
      "фундамент": [
        "монолитная плита",
        "лента",
        "сваи",
        "ростверк",
        "утеплённая плита",
        "складской фундамент"
      ],
      "кровля": [
        "металлочерепица",
        "профнастил",
        "гибкая черепица",
        "фальц",
        "мембрана",
        "стропильная система"
      ],
      "перекрытия": [
        "деревянные балки",
        "монолит",
        "плиты",
        "металлические балки"
      ],
      "утепление": [
        "минвата",
        "роквул",
        "пеноплэкс",
        "pir",
        "эковата"
      ],
      "отделка": [
        "имитация бруса",
        "штукатурка",
        "плитка",
        "гкл",
        "цсп",
        "фасадная доска"
      ],
      "инженерия": [
        "электрика",
        "водоснабжение",
        "канализация",
        "отопление",
        "вентиляция"
      ],
      "логистика": [
        "доставка",
        "разгрузка",
        "манипулятор",
        "кран",
        "проживание",
        "транспорт бригады",
        "удалённость"
      ]
    },
    "formula_policy": [
      "Топовые сметы являются эталонами логики расчёта, а не прайс-листами",
      "Новые сметы считаются по такой же структуре: разделы, строки, колонки, формулы, итоги, примечания, исключения",
      "Материал может быть любым: кирпич, газобетон, каркас, монолит, кровля, перекрытия, отделка, инженерия",
      "При замене материала сохраняется расчётная логика: количество × цена = сумма; работа + материалы = всего; разделы = итоги; финальный итог = сумма разделов",
      "Каркасный сценарий, газобетон/монолитная плита, кровля/перекрытия и фундамент считаются как разные сценарии и не смешиваются",
      "Если объёмов не хватает — оркестр спрашивает только недостающие объёмы",
      "Если пользователь прислал файл как образец — сначала принять как образец, а не запускать поиск цен"
    ],
    "price_confirmation_flow": [
      "Интернет-цены материалов и техники не подставляются молча",
      "Для финальной сметы оркестр ищет актуальные цены по материалам, технике, доставке и разгрузке",
      "По каждой позиции показывает: источник, цена, единица, дата/регион, ссылка",
      "Оркестр предлагает среднюю/медианную цену без явных выбросов",
      "Пользователь выбирает: средняя / минимальная / максимальная / конкретная ссылка / ручная цена",
      "Пользователь может добавить наценку, запас, скидку, поправку по позиции, разделу или всей смете",
      "До подтверждения цен финальный XLSX/PDF не выпускается",
      "После подтверждения цены пересчитываются по формулам шаблона"
    ],
    "logistics_policy": [
      "Перед финальной сметой оркестр обязан запросить локацию объекта или расстояние от города",
      "Стоимость объекта рядом с городом и объекта за 200 км не может быть одинаковой",
      "Оркестр обязан учитывать доставку материалов, транспорт бригады, разгрузку, манипулятор/кран, проживание, удалённость, дорожные условия",
      "Если логистика неизвестна — оркестр задаёт один короткий вопрос: город/населённый пункт или расстояние от города, подъезд для грузовой техники, нужна ли разгрузка/манипулятор",
      "Логистика считается отдельным блоком сметы или отдельным коэффициентом, но не смешивается молча с ценами материалов",
      "Перед финальным результатом оркестр показывает логистические допущения и спрашивает подтверждение"
    ],
    "runtime_rule": "ai_router injects this context through core.estimate_template_policy.build_estimate_template_context"
  },
  "active_estimate_template_policy": "ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4",
  "estimate_formula_logic_preserve_required": true,
  "estimate_material_price_web_refresh_required": true,
  "estimate_price_confirmation_required": true,
  "estimate_logistics_required": true,
  "estimate_final_xlsx_forbidden_before_price_and_logistics_confirmation": true
}

====================================================================================================
END_FILE: config/estimate_template_registry.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: config/owner_reference_registry.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 9c30429f4a333023450a0bc614f55d0e1449877063cc7ecb7953e347f93714fc
====================================================================================================
{
  "owner_reference_full_workflow_v1": {
    "version": "AREAL_REFERENCE_FULL_MONOLITH_V1",
    "status": "ACTIVE",
    "updated_at": "2026-05-02T20:20:56.522887+00:00",
    "drive_account": "nadzor812@gmail.com",
    "counts": {
      "estimate_files": 6,
      "design_files": 231,
      "technadzor_files": 1,
      "formula_total": 4733,
      "all_files": 261
    },
    "estimate_references": [
      {
        "name": "Ареал Нева.xlsx",
        "file_id": "1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "ESTIMATES_TEMPLATES/Ареал Нева.xlsx",
        "size": "151108",
        "modifiedTime": "2026-05-02T12:04:37.000Z",
        "url": "https://docs.google.com/spreadsheets/d/1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "estimate",
        "role": "areal_neva",
        "formula_total": 1192,
        "sheets": [
          {
            "sheet_name": "смета",
            "formula_count": 1192,
            "material_hits": 95,
            "work_hits": 55,
            "logistics_hits": 18
          }
        ]
      },
      {
        "name": "М-80.xlsx",
        "file_id": "1yt-RJsGRhO13zmPKNAn6bMuGrpXY7kWp",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "ESTIMATES_TEMPLATES/М-80.xlsx",
        "size": "403589",
        "modifiedTime": "2025-12-02T09:12:35.000Z",
        "url": "https://docs.google.com/spreadsheets/d/1yt-RJsGRhO13zmPKNAn6bMuGrpXY7kWp/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "estimate",
        "role": "m80",
        "formula_total": 1670,
        "sheets": [
          {
            "sheet_name": "Каркас под ключ",
            "formula_count": 799,
            "material_hits": 48,
            "work_hits": 77,
            "logistics_hits": 13
          },
          {
            "sheet_name": "Газобетон_под ключ",
            "formula_count": 871,
            "material_hits": 69,
            "work_hits": 82,
            "logistics_hits": 18
          }
        ]
      },
      {
        "name": "фундамент_Склад2.xlsx",
        "file_id": "1KuoSI4OI7gJoIBPVqBQGXtQnolXKMiDp",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "ESTIMATES_TEMPLATES/фундамент_Склад2.xlsx",
        "size": "15910",
        "modifiedTime": "2025-05-27T08:01:58.000Z",
        "url": "https://docs.google.com/spreadsheets/d/1KuoSI4OI7gJoIBPVqBQGXtQnolXKMiDp/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "estimate",
        "role": "foundation",
        "formula_total": 88,
        "sheets": [
          {
            "sheet_name": "смета",
            "formula_count": 88,
            "material_hits": 14,
            "work_hits": 17,
            "logistics_hits": 0
          }
        ]
      },
      {
        "name": "М-110.xlsx",
        "file_id": "1Ub9fcwOcJ4pV30dcX88yf1225WOIdpWo",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "ESTIMATES_TEMPLATES/М-110.xlsx",
        "size": "2024326",
        "modifiedTime": "2025-05-15T06:18:08.000Z",
        "url": "https://docs.google.com/spreadsheets/d/1Ub9fcwOcJ4pV30dcX88yf1225WOIdpWo/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "estimate",
        "role": "m110",
        "formula_total": 1647,
        "sheets": [
          {
            "sheet_name": "Каркас под ключ",
            "formula_count": 791,
            "material_hits": 48,
            "work_hits": 77,
            "logistics_hits": 13
          },
          {
            "sheet_name": "Газобетон",
            "formula_count": 856,
            "material_hits": 66,
            "work_hits": 82,
            "logistics_hits": 18
          }
        ]
      },
      {
        "name": "крыша и перекр.xlsx",
        "file_id": "16YecwnJ9umnVprFu9V77UCV6cPrYbNh3",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "ESTIMATES_TEMPLATES/крыша и перекр.xlsx",
        "size": "58430",
        "modifiedTime": "2025-03-14T11:17:00.000Z",
        "url": "https://docs.google.com/spreadsheets/d/16YecwnJ9umnVprFu9V77UCV6cPrYbNh3/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "estimate",
        "role": "roof_floor",
        "formula_total": 136,
        "sheets": [
          {
            "sheet_name": "расчет кровли",
            "formula_count": 136,
            "material_hits": 8,
            "work_hits": 21,
            "logistics_hits": 1
          }
        ]
      },
      {
        "name": "Проект М-80 КД_финал.pdf",
        "file_id": "1MjB2yjfZv4qnX6CYwLdlDodqN3kPlw6_",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Проект М-80 КД_финал.pdf",
        "size": "6398193",
        "modifiedTime": "2026-05-02T13:26:45.000Z",
        "url": "https://drive.google.com/file/d/1MjB2yjfZv4qnX6CYwLdlDodqN3kPlw6_/view?usp=drivesdk",
        "domain": "estimate",
        "role": "m80",
        "formula_total": 0,
        "sheets": []
      }
    ],
    "design_references": [
      {
        "name": "Проект АР+КР Беседка Красный маяк.pln",
        "file_id": "134x4QteMFhFuY2tDLJlfZj2dsAAfR5Yp",
        "mimeType": "application/octet-stream",
        "path": "TOPIC_210/Образцы проектов/Проект АР+КР Беседка Красный маяк.pln",
        "size": "64480656",
        "modifiedTime": "2026-05-02T18:55:50.092Z",
        "url": "https://drive.google.com/file/d/134x4QteMFhFuY2tDLJlfZj2dsAAfR5Yp/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Баня.pln",
        "file_id": "1G0obdndF7a6Yo84gyWBZgoCfdweWvTHF",
        "mimeType": "application/octet-stream",
        "path": "TOPIC_210/Образцы проектов/Баня.pln",
        "size": "149124080",
        "modifiedTime": "2026-05-02T18:55:23.238Z",
        "url": "https://drive.google.com/file/d/1G0obdndF7a6Yo84gyWBZgoCfdweWvTHF/view?usp=drivesdk",
        "domain": "design",
        "discipline": "OV"
      },
      {
        "name": "Проект АР+КР Баня красный маяк (с открыванием окон).pdf",
        "file_id": "1-1tJTQ0DBhJCbjs1_vfirxLhIYfdZVdJ",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Проект АР+КР Баня красный маяк (с открыванием окон).pdf",
        "size": "6469624",
        "modifiedTime": "2026-05-02T18:54:26.036Z",
        "url": "https://drive.google.com/file/d/1-1tJTQ0DBhJCbjs1_vfirxLhIYfdZVdJ/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Проект АР КЖ КД СП АК-160.pln",
        "file_id": "1SHQMLpAAMtyLZ1cXgf3s-o8WhjYilYFf",
        "mimeType": "application/octet-stream",
        "path": "TOPIC_210/Образцы проектов/Проект АР КЖ КД СП АК-160.pln",
        "size": "181841472",
        "modifiedTime": "2026-05-02T18:54:02.448Z",
        "url": "https://drive.google.com/file/d/1SHQMLpAAMtyLZ1cXgf3s-o8WhjYilYFf/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "АР.pdf",
        "file_id": "1zLSsbpjzqvM78KWcE6u5bWpkKdVe1TuZ",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/АР.pdf",
        "size": "2860694",
        "modifiedTime": "2026-05-02T18:52:10.989Z",
        "url": "https://drive.google.com/file/d/1zLSsbpjzqvM78KWcE6u5bWpkKdVe1TuZ/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "КЖ.pdf",
        "file_id": "1monrudsc6f6DxEB6NfKXBT5mEr_0YMgA",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КЖ.pdf",
        "size": "934279",
        "modifiedTime": "2026-05-02T18:49:19.613Z",
        "url": "https://drive.google.com/file/d/1monrudsc6f6DxEB6NfKXBT5mEr_0YMgA/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КД.pdf",
        "file_id": "1I97ooIkESySQirOUGc-yh3KYlSD8OiOz",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КД.pdf",
        "size": "899800",
        "modifiedTime": "2026-05-02T18:49:19.601Z",
        "url": "https://drive.google.com/file/d/1I97ooIkESySQirOUGc-yh3KYlSD8OiOz/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KD"
      },
      {
        "name": "Березовый проезд, уч.5 посадка здания.dwg",
        "file_id": "12e4F19syQkHHf8OjZJrvPsxGauWhC99T",
        "mimeType": "image/vnd.dwg",
        "path": "TOPIC_210/Образцы проектов/Березовый проезд, уч.5 посадка здания.dwg",
        "size": "126641",
        "modifiedTime": "2026-05-02T18:49:17.931Z",
        "url": "https://drive.google.com/file/d/12e4F19syQkHHf8OjZJrvPsxGauWhC99T/view?usp=drivesdk",
        "domain": "design",
        "discipline": "OV"
      },
      {
        "name": "Спецификации.pdf",
        "file_id": "19IGBcZWEzSEUwROKimsqLiDP6EW2K7p3",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Спецификации.pdf",
        "size": "84358",
        "modifiedTime": "2026-05-02T18:49:17.789Z",
        "url": "https://drive.google.com/file/d/19IGBcZWEzSEUwROKimsqLiDP6EW2K7p3/view?usp=drivesdk",
        "domain": "design",
        "discipline": "OV"
      },
      {
        "name": "Проект_АБ_ИНД_М_80_КР_КД_в8_ФорматА3.pdf",
        "file_id": "1h2whh7itQWCU4j7zUBqfG7LrTs1dNAl4",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Проект_АБ_ИНД_М_80_КР_КД_в8_ФорматА3.pdf",
        "size": "31884746",
        "modifiedTime": "2026-05-02T13:30:16.000Z",
        "url": "https://drive.google.com/file/d/1h2whh7itQWCU4j7zUBqfG7LrTs1dNAl4/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KD"
      },
      {
        "name": "Открыть Микеа 3 РП 3 (1) (3) (3).pdf",
        "file_id": "1cr_4vqkt4ycFv3cnYsuc-lCAGGGH5BmX",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Открыть Микеа 3 РП 3 (1) (3) (3).pdf",
        "size": "62929250",
        "modifiedTime": "2026-05-02T13:29:31.000Z",
        "url": "https://drive.google.com/file/d/1cr_4vqkt4ycFv3cnYsuc-lCAGGGH5BmX/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KR"
      },
      {
        "name": "КЖ Цоколь.pdf",
        "file_id": "19MV-8ewgZCMlsKf9b_BBrTgqVpKo4cOT",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КЖ Цоколь.pdf",
        "size": "9333419",
        "modifiedTime": "2026-05-02T13:24:35.000Z",
        "url": "https://drive.google.com/file/d/19MV-8ewgZCMlsKf9b_BBrTgqVpKo4cOT/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "Барн план участка 2.pdf",
        "file_id": "1d2rSNtQeELMZNhbfJY_27iuZ32ceLCD1",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Барн план участка 2.pdf",
        "size": "163258",
        "modifiedTime": "2026-05-02T13:19:20.000Z",
        "url": "https://drive.google.com/file/d/1d2rSNtQeELMZNhbfJY_27iuZ32ceLCD1/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Шувалово Озерки - АР (1).pdf",
        "file_id": "1uyuMMqy1U0JaTfqelz2mPzsBn_7EpUfo",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Шувалово Озерки - АР (1).pdf",
        "size": "14574210",
        "modifiedTime": "2026-05-02T13:13:45.000Z",
        "url": "https://drive.google.com/file/d/1uyuMMqy1U0JaTfqelz2mPzsBn_7EpUfo/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Шувалово Озерки - КЖ.pdf",
        "file_id": "1Bop92pLWOk36WA_I2XZTkYiMLBiCTT7J",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Шувалово Озерки - КЖ.pdf",
        "size": "13675946",
        "modifiedTime": "2026-05-02T13:11:22.000Z",
        "url": "https://drive.google.com/file/d/1Bop92pLWOk36WA_I2XZTkYiMLBiCTT7J/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ Цоколь 1.1.pdf",
        "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5kCvUWuy3",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КЖ Цоколь 1.1.pdf",
        "size": "9345053",
        "modifiedTime": "2026-05-02T01:40:13.267Z",
        "url": "https://drive.google.com/file/d/16V3s5DcAvnXj8f-3CcfZE2g5kCvUWuy3/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "АР_КД_Агалатово_02.pdf",
        "file_id": "1YdC8pccl0dITkNFJ-j_xzNrbJEPH5ey3",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/АР_КД_Агалатово_02.pdf",
        "size": "17117525",
        "modifiedTime": "2026-04-30T07:46:38.632Z",
        "url": "https://drive.google.com/file/d/1YdC8pccl0dITkNFJ-j_xzNrbJEPH5ey3/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "КЖ АК-М-160.pdf",
        "file_id": "1KTyJ0i2WWXrSIq-S_rHs7l2YQjY07StY",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КЖ АК-М-160.pdf",
        "size": "934279",
        "modifiedTime": "2026-04-30T02:55:00.086Z",
        "url": "https://drive.google.com/file/d/1KTyJ0i2WWXrSIq-S_rHs7l2YQjY07StY/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КД АК-М-160.pdf",
        "file_id": "13CVDyIpUDKvf0dcnMrsXwAsnJiRMlLgu",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КД АК-М-160.pdf",
        "size": "899800",
        "modifiedTime": "2026-04-30T02:54:59.987Z",
        "url": "https://drive.google.com/file/d/13CVDyIpUDKvf0dcnMrsXwAsnJiRMlLgu/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KD"
      },
      {
        "name": "АР АК-М-160.pdf",
        "file_id": "1je7nzCaFFJO7S3DmGm6PhmG7uUsXS1EW",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/АР АК-М-160.pdf",
        "size": "2860694",
        "modifiedTime": "2026-04-30T02:53:15.687Z",
        "url": "https://drive.google.com/file/d/1je7nzCaFFJO7S3DmGm6PhmG7uUsXS1EW/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Проект АБ_ИНД_М_80_20_03_24.pdf",
        "file_id": "1qiYnPw2wpULiiWIlkJFnw6QJBcLYdvkE",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Проект АБ_ИНД_М_80_20_03_24.pdf",
        "size": "10324596",
        "modifiedTime": "2026-04-30T02:45:52.986Z",
        "url": "https://drive.google.com/file/d/1qiYnPw2wpULiiWIlkJFnw6QJBcLYdvkE/view?usp=drivesdk",
        "domain": "design",
        "discipline": "OV"
      },
      {
        "name": "КЖ Барн (со спецификациями).pdf",
        "file_id": "1JBmfpGopg2l-Qu_yblQ1udz7bYBRw-fP",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КЖ Барн (со спецификациями).pdf",
        "size": "3982597",
        "modifiedTime": "2025-11-21T07:48:36.000Z",
        "url": "https://drive.google.com/file/d/1JBmfpGopg2l-Qu_yblQ1udz7bYBRw-fP/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "КЖ Барн (со спецификациями).pdf",
        "file_id": "13I18VQ7HpfDXMrZPkCVIqjaSIRmeDUfM",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КЖ Барн (со спецификациями).pdf",
        "size": "3982597",
        "modifiedTime": "2025-11-21T07:48:36.000Z",
        "url": "https://drive.google.com/file/d/13I18VQ7HpfDXMrZPkCVIqjaSIRmeDUfM/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Шувалово Озерки - КД (1).pdf",
        "file_id": "1S9pgv3OLJ-fi36baYYID5WQp2FmPghyW",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Шувалово Озерки - КД (1).pdf",
        "size": "6147642",
        "modifiedTime": "2025-11-15T14:38:43.000Z",
        "url": "https://drive.google.com/file/d/1S9pgv3OLJ-fi36baYYID5WQp2FmPghyW/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KD"
      },
      {
        "name": "КЖ без лестницы.pdf",
        "file_id": "1XCTt2CP3NOGiDmFLr_Y6iLC3r2REhoGD",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КЖ без лестницы.pdf",
        "size": "835492",
        "modifiedTime": "2025-09-01T07:04:46.000Z",
        "url": "https://drive.google.com/file/d/1XCTt2CP3NOGiDmFLr_Y6iLC3r2REhoGD/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "АР_КЖ_КД_Вадим_Старая_Буря.pdf",
        "file_id": "1pz-mf691fd1gK3Ak7s1jqzbkF2LmZI6E",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/АР_КЖ_КД_Вадим_Старая_Буря.pdf",
        "size": "30864059",
        "modifiedTime": "2025-04-28T21:13:27.000Z",
        "url": "https://drive.google.com/file/d/1pz-mf691fd1gK3Ak7s1jqzbkF2LmZI6E/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "КД барн (со спец).pdf",
        "file_id": "1VHRafGQ244bcMQojhASvNFEzWRIewmSg",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КД барн (со спец).pdf",
        "size": "1563796",
        "modifiedTime": "2025-04-26T13:38:59.000Z",
        "url": "https://drive.google.com/file/d/1VHRafGQ244bcMQojhASvNFEzWRIewmSg/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Эскиз.pdf",
        "file_id": "147vYZj0kGTt2tWiI4PJ3Cd6LBgJV9BU8",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Эскиз.pdf",
        "size": "3692744",
        "modifiedTime": "2025-04-26T13:35:23.000Z",
        "url": "https://drive.google.com/file/d/147vYZj0kGTt2tWiI4PJ3Cd6LBgJV9BU8/view?usp=drivesdk",
        "domain": "design",
        "discipline": "OV"
      },
      {
        "name": "АР Красная Горка.docx",
        "file_id": "1PwptoS4wM5zY8ZN9deYX899MxRKoU_b2",
        "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "path": "TOPIC_210/Образцы проектов/АР Красная Горка.docx",
        "size": "1957539",
        "modifiedTime": "2024-02-03T11:54:46.000Z",
        "url": "https://docs.google.com/document/d/1PwptoS4wM5zY8ZN9deYX899MxRKoU_b2/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Спецификации (1).pdf",
        "file_id": "1wtB1srqUUKGkHH-QDXykI-z7m5YSBkgw",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Спецификации (1).pdf",
        "size": "36450",
        "modifiedTime": "2023-10-04T22:34:28.000Z",
        "url": "https://drive.google.com/file/d/1wtB1srqUUKGkHH-QDXykI-z7m5YSBkgw/view?usp=drivesdk",
        "domain": "design",
        "discipline": "OV"
      },
      {
        "name": "КД (1).pdf",
        "file_id": "1lt6UQbrmy74ilcLHJVUzhHYNDM3GTabT",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КД (1).pdf",
        "size": "708733",
        "modifiedTime": "2023-10-04T22:34:12.000Z",
        "url": "https://drive.google.com/file/d/1lt6UQbrmy74ilcLHJVUzhHYNDM3GTabT/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KD"
      },
      {
        "name": "АР (1).pdf",
        "file_id": "1iESkIUKEd5SLs3O63iz3CYHTEqllJU93",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/АР (1).pdf",
        "size": "2556565",
        "modifiedTime": "2023-10-04T22:33:52.000Z",
        "url": "https://drive.google.com/file/d/1iESkIUKEd5SLs3O63iz3CYHTEqllJU93/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Проект АР КЖ КД СП АА-120 (1).pln",
        "file_id": "1bbP8Ex--YQHciKFTLxAYmm9fHk8s_Qkw",
        "mimeType": "application/octet-stream",
        "path": "TOPIC_210/Образцы проектов/Проект АР КЖ КД СП АА-120 (1).pln",
        "size": "73015840",
        "modifiedTime": "2023-10-04T22:18:18.000Z",
        "url": "https://drive.google.com/file/d/1bbP8Ex--YQHciKFTLxAYmm9fHk8s_Qkw/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Проект АР КЖ КД СП АА-120.pln",
        "file_id": "1TkG8M0HBlz5jazLWfPewWYqDbYt49mLx",
        "mimeType": "application/octet-stream",
        "path": "TOPIC_210/Образцы проектов/Проект АР КЖ КД СП АА-120.pln",
        "size": "73015840",
        "modifiedTime": "2023-10-04T22:18:18.000Z",
        "url": "https://drive.google.com/file/d/1TkG8M0HBlz5jazLWfPewWYqDbYt49mLx/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "КЖ (1).pdf",
        "file_id": "1pkzqfwfJCjlwtQJSqBbq2ly1JKCVW-3Z",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КЖ (1).pdf",
        "size": "721463",
        "modifiedTime": "2023-10-02T10:09:40.000Z",
        "url": "https://drive.google.com/file/d/1pkzqfwfJCjlwtQJSqBbq2ly1JKCVW-3Z/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "Узел крепления вентфасада.pdf",
        "file_id": "1Ibs_myUd2tz523ViHgeXgb8e1TlXbQHC",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Узел крепления вентфасада.pdf",
        "size": "14044",
        "modifiedTime": "2023-10-01T08:38:10.000Z",
        "url": "https://drive.google.com/file/d/1Ibs_myUd2tz523ViHgeXgb8e1TlXbQHC/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KR"
      },
      {
        "name": "Узел крепления вентфасада (1).pdf",
        "file_id": "1SdpL4FQDdpTk7x-NqxiAqq02UQsmlos5",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Узел крепления вентфасада (1).pdf",
        "size": "14044",
        "modifiedTime": "2023-10-01T08:38:10.000Z",
        "url": "https://drive.google.com/file/d/1SdpL4FQDdpTk7x-NqxiAqq02UQsmlos5/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KR"
      },
      {
        "name": "Проект АР КЖ КД СП АК-160 (1).pln",
        "file_id": "1hRpfhhxD6-8kUkmd8uyOn7tjtkSXYD34",
        "mimeType": "application/octet-stream",
        "path": "TOPIC_210/Образцы проектов/Проект АР КЖ КД СП АК-160 (1).pln",
        "size": "181841472",
        "modifiedTime": "2023-10-01T08:21:16.000Z",
        "url": "https://drive.google.com/file/d/1hRpfhhxD6-8kUkmd8uyOn7tjtkSXYD34/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Спецификации (2).pdf",
        "file_id": "1JyW-sRM8DZOvYx0R-uAWeoWbiAl9QYs7",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Спецификации (2).pdf",
        "size": "84358",
        "modifiedTime": "2023-09-26T07:13:56.000Z",
        "url": "https://drive.google.com/file/d/1JyW-sRM8DZOvYx0R-uAWeoWbiAl9QYs7/view?usp=drivesdk",
        "domain": "design",
        "discipline": "OV"
      },
      {
        "name": "КД (2).pdf",
        "file_id": "17rRcxSKohIo1hHRrbxKYI_QFS6m_M9DN",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КД (2).pdf",
        "size": "899800",
        "modifiedTime": "2023-09-26T07:13:30.000Z",
        "url": "https://drive.google.com/file/d/17rRcxSKohIo1hHRrbxKYI_QFS6m_M9DN/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KD"
      },
      {
        "name": "КЖ (2).pdf",
        "file_id": "1KGgcjNSjMN30EXJc3yH7aL3vCUAb2l_l",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КЖ (2).pdf",
        "size": "934279",
        "modifiedTime": "2023-09-20T10:06:10.000Z",
        "url": "https://drive.google.com/file/d/1KGgcjNSjMN30EXJc3yH7aL3vCUAb2l_l/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "АР (1).pdf",
        "file_id": "1d_PaxsyDn9eY1kx4Q2ATkopXxO6j7u1z",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/АР (1).pdf",
        "size": "2860694",
        "modifiedTime": "2023-09-20T09:10:38.000Z",
        "url": "https://drive.google.com/file/d/1d_PaxsyDn9eY1kx4Q2ATkopXxO6j7u1z/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Дом у озера.pln",
        "file_id": "1_5I5DW6LeB2BG6pF9tfMI2pFnJSbDPz9",
        "mimeType": "application/octet-stream",
        "path": "TOPIC_210/Образцы проектов/Дом у озера.pln",
        "size": "99996848",
        "modifiedTime": "2023-09-20T08:49:46.000Z",
        "url": "https://drive.google.com/file/d/1_5I5DW6LeB2BG6pF9tfMI2pFnJSbDPz9/view?usp=drivesdk",
        "domain": "design",
        "discipline": "OV"
      },
      {
        "name": "Дом у озера (1).pln",
        "file_id": "1hcVp0U2rPb94tHDzMljilx95_TVaXtO2",
        "mimeType": "application/octet-stream",
        "path": "TOPIC_210/Образцы проектов/Дом у озера (1).pln",
        "size": "99996848",
        "modifiedTime": "2023-09-20T08:49:46.000Z",
        "url": "https://drive.google.com/file/d/1hcVp0U2rPb94tHDzMljilx95_TVaXtO2/view?usp=drivesdk",
        "domain": "design",
        "discipline": "OV"
      },
      {
        "name": "Березовый проезд, уч.5 посадка здания (1).dwg",
        "file_id": "1nJE2Xc3fEuLX_OfFDt-tzuTeMkMISiQp",
        "mimeType": "image/vnd.dwg",
        "path": "TOPIC_210/Образцы проектов/Березовый проезд, уч.5 посадка здания (1).dwg",
        "size": "126641",
        "modifiedTime": "2023-09-19T10:05:08.000Z",
        "url": "https://drive.google.com/file/d/1nJE2Xc3fEuLX_OfFDt-tzuTeMkMISiQp/view?usp=drivesdk",
        "domain": "design",
        "discipline": "OV"
      },
      {
        "name": "Дом у озера АР+КР (полный).pdf",
        "file_id": "1mzeaJtvjUMDPrlj6UpeHj23JmrirEV_h",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Дом у озера АР+КР (полный).pdf",
        "size": "6187020",
        "modifiedTime": "2023-09-13T07:29:52.000Z",
        "url": "https://drive.google.com/file/d/1mzeaJtvjUMDPrlj6UpeHj23JmrirEV_h/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Дом у озера АР+КР (полный) (1).pdf",
        "file_id": "18yOW7YncQcnuESjTFl3NvDzRdIYSUxNb",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Дом у озера АР+КР (полный) (1).pdf",
        "size": "6187020",
        "modifiedTime": "2023-09-13T07:29:52.000Z",
        "url": "https://drive.google.com/file/d/18yOW7YncQcnuESjTFl3NvDzRdIYSUxNb/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Дом у озера АР+КР (1).pdf",
        "file_id": "12Ud-2p4w68Me-sXBuK14xcwfrUkcg0lH",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Дом у озера АР+КР (1).pdf",
        "size": "2528669",
        "modifiedTime": "2023-09-11T18:24:54.000Z",
        "url": "https://drive.google.com/file/d/12Ud-2p4w68Me-sXBuK14xcwfrUkcg0lH/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Дом у озера АР+КР.pdf",
        "file_id": "1JEQNo8K5ExIAyfz71byZyEcx7JiszXMP",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Дом у озера АР+КР.pdf",
        "size": "2528669",
        "modifiedTime": "2023-09-11T18:24:54.000Z",
        "url": "https://drive.google.com/file/d/1JEQNo8K5ExIAyfz71byZyEcx7JiszXMP/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Дом у леса АР+КР (1).pdf",
        "file_id": "1JF6WOXIfQpFOX540a22Vc8w2lG0Rj3Hc",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Дом у леса АР+КР (1).pdf",
        "size": "2245744",
        "modifiedTime": "2023-09-04T08:10:52.000Z",
        "url": "https://drive.google.com/file/d/1JF6WOXIfQpFOX540a22Vc8w2lG0Rj3Hc/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Дом у леса АР+КР.pdf",
        "file_id": "1GGXmVceVCE9Rzir6Zo5bAh1-Tr_XxWKR",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Дом у леса АР+КР.pdf",
        "size": "2245744",
        "modifiedTime": "2023-09-04T08:10:52.000Z",
        "url": "https://drive.google.com/file/d/1GGXmVceVCE9Rzir6Zo5bAh1-Tr_XxWKR/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Дом у леса АР+КР полный.pdf",
        "file_id": "1SPkBzPVYJuFVkmoDz4uM56rRZj_Cfd87",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Дом у леса АР+КР полный.pdf",
        "size": "3079792",
        "modifiedTime": "2023-09-04T08:10:38.000Z",
        "url": "https://drive.google.com/file/d/1SPkBzPVYJuFVkmoDz4uM56rRZj_Cfd87/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Дом у леса АР+КР полный (1).pdf",
        "file_id": "1WuLxfrnE4EVJJINowlc5_bH2pSb5hhK3",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/Дом у леса АР+КР полный (1).pdf",
        "size": "3079792",
        "modifiedTime": "2023-09-04T08:10:38.000Z",
        "url": "https://drive.google.com/file/d/1WuLxfrnE4EVJJINowlc5_bH2pSb5hhK3/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "Дом у леса.pln",
        "file_id": "1uDpAnidXD3Ni22CvNIVE_JVxyCl97A2T",
        "mimeType": "application/octet-stream",
        "path": "TOPIC_210/Образцы проектов/Дом у леса.pln",
        "size": "138398560",
        "modifiedTime": "2023-09-04T08:10:06.000Z",
        "url": "https://drive.google.com/file/d/1uDpAnidXD3Ni22CvNIVE_JVxyCl97A2T/view?usp=drivesdk",
        "domain": "design",
        "discipline": "OV"
      },
      {
        "name": "Дом у леса (1).pln",
        "file_id": "1AOClYMOd7EFZrpDXx8K6tTrryggnYv3n",
        "mimeType": "application/octet-stream",
        "path": "TOPIC_210/Образцы проектов/Дом у леса (1).pln",
        "size": "138398560",
        "modifiedTime": "2023-09-04T08:10:06.000Z",
        "url": "https://drive.google.com/file/d/1AOClYMOd7EFZrpDXx8K6tTrryggnYv3n/view?usp=drivesdk",
        "domain": "design",
        "discipline": "OV"
      },
      {
        "name": "АР+КР Беседка Красный маяк.pdf",
        "file_id": "16LVte90G6bH2zNCJyf993gO2ce-Pgtbi",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/АР+КР Беседка Красный маяк.pdf",
        "size": "5061538",
        "modifiedTime": "2023-08-16T08:57:54.000Z",
        "url": "https://drive.google.com/file/d/16LVte90G6bH2zNCJyf993gO2ce-Pgtbi/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "АБК.pln",
        "file_id": "1YIOpV9XvrCsytqY2ROc_S-FOptz-wjug",
        "mimeType": "application/octet-stream",
        "path": "TOPIC_210/Образцы проектов/АБК.pln",
        "size": "80436464",
        "modifiedTime": "2023-07-09T13:25:28.000Z",
        "url": "https://drive.google.com/file/d/1YIOpV9XvrCsytqY2ROc_S-FOptz-wjug/view?usp=drivesdk",
        "domain": "design",
        "discipline": "OV"
      },
      {
        "name": "АБК (1).pln",
        "file_id": "130L-CaMU56dMYlBi36HE6NuLA1PEa2Pb",
        "mimeType": "application/octet-stream",
        "path": "TOPIC_210/Образцы проектов/АБК (1).pln",
        "size": "80436464",
        "modifiedTime": "2023-07-09T13:25:28.000Z",
        "url": "https://drive.google.com/file/d/130L-CaMU56dMYlBi36HE6NuLA1PEa2Pb/view?usp=drivesdk",
        "domain": "design",
        "discipline": "OV"
      },
      {
        "name": "КР АБК (1).pdf",
        "file_id": "1XfoP7NRge-MljufZOevywHUgWme2NaD9",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КР АБК (1).pdf",
        "size": "1698669",
        "modifiedTime": "2023-07-04T10:47:40.000Z",
        "url": "https://drive.google.com/file/d/1XfoP7NRge-MljufZOevywHUgWme2NaD9/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KR"
      },
      {
        "name": "КР АБК.pdf",
        "file_id": "1aIz-B_NgPx7GxVwk3opSSGbm8KDv0eG9",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КР АБК.pdf",
        "size": "1698669",
        "modifiedTime": "2023-07-04T10:47:40.000Z",
        "url": "https://drive.google.com/file/d/1aIz-B_NgPx7GxVwk3opSSGbm8KDv0eG9/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KR"
      },
      {
        "name": "АР АБК.pdf",
        "file_id": "1IFPjU1q-BiXAMPTw4Vyt3mDEUAncKRIZ",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/АР АБК.pdf",
        "size": "2846857",
        "modifiedTime": "2023-07-03T20:47:02.000Z",
        "url": "https://drive.google.com/file/d/1IFPjU1q-BiXAMPTw4Vyt3mDEUAncKRIZ/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "АР АБК (1).pdf",
        "file_id": "1MWGuj6-GPNpbbpSlWawqK45ndbaXGH1A",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/АР АБК (1).pdf",
        "size": "2846857",
        "modifiedTime": "2023-07-03T20:47:02.000Z",
        "url": "https://drive.google.com/file/d/1MWGuj6-GPNpbbpSlWawqK45ndbaXGH1A/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "КЖ Красная Горка.pdf",
        "file_id": "1HzaHi2p_wGvCsYkfYg2mNUHS8Puvsgck",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КЖ Красная Горка.pdf",
        "size": "2488933",
        "modifiedTime": "2023-07-01T05:19:22.000Z",
        "url": "https://drive.google.com/file/d/1HzaHi2p_wGvCsYkfYg2mNUHS8Puvsgck/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КД Красная Горка.pdf",
        "file_id": "1qcIjErSKQrs-yKTJ9wZF__nYwb1Sggmt",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/КД Красная Горка.pdf",
        "size": "1268786",
        "modifiedTime": "2023-07-01T05:19:10.000Z",
        "url": "https://drive.google.com/file/d/1qcIjErSKQrs-yKTJ9wZF__nYwb1Sggmt/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KD"
      },
      {
        "name": "проект КЖ плиты.pdf",
        "file_id": "1ONM08NLp8VrSi99KJNk2pZemL0rjhkdC",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/проект КЖ плиты.pdf",
        "size": "173534",
        "modifiedTime": "2023-07-01T05:16:20.000Z",
        "url": "https://drive.google.com/file/d/1ONM08NLp8VrSi99KJNk2pZemL0rjhkdC/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "МЛ2023ИЖС278-АР.pdf",
        "file_id": "1JaDR-qNXVC8N5uc5f6xkiQMRL39CEQhm",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/МЛ2023ИЖС278-АР.pdf",
        "size": "4499207",
        "modifiedTime": "2023-04-13T23:01:36.000Z",
        "url": "https://drive.google.com/file/d/1JaDR-qNXVC8N5uc5f6xkiQMRL39CEQhm/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "МЛ2023ИЖС278-ОВ.pdf",
        "file_id": "1loGJIdWakOoSJ_VCxWK1vJo9KDriIkxE",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/МЛ2023ИЖС278-ОВ.pdf",
        "size": "1607504",
        "modifiedTime": "2023-04-13T23:01:34.000Z",
        "url": "https://drive.google.com/file/d/1loGJIdWakOoSJ_VCxWK1vJo9KDriIkxE/view?usp=drivesdk",
        "domain": "design",
        "discipline": "OV"
      },
      {
        "name": "МЛ.2022.pdf",
        "file_id": "1YVt767NFci7Zi0Yded4plB07ATeWss5a",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/Образцы проектов/МЛ.2022.pdf",
        "size": "881563",
        "modifiedTime": "2023-04-13T22:56:42.000Z",
        "url": "https://drive.google.com/file/d/1YVt767NFci7Zi0Yded4plB07ATeWss5a/view?usp=drivesdk",
        "domain": "design",
        "discipline": "OV"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_0de22d01-0615-4fc7-8cbb-bf9624.manifest.json",
        "file_id": "1wCbkC60Ed5lTO2OfCPcOIwqt6SgC5HYA",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_COMPACT_PROJECT_0de22d01-0615-4fc7-8cbb-bf9624.manifest.json",
        "size": "1596",
        "modifiedTime": "2026-05-01T19:35:28.326Z",
        "url": "https://drive.google.com/file/d/1wCbkC60Ed5lTO2OfCPcOIwqt6SgC5HYA/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_3598cf90-2986-4c40-a5be-6b77e6.manifest.json",
        "file_id": "1DI0TH2MuSHq8ONkZNUSmMjOfZZT2cgDp",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_COMPACT_PROJECT_3598cf90-2986-4c40-a5be-6b77e6.manifest.json",
        "size": "1632",
        "modifiedTime": "2026-05-01T19:25:50.858Z",
        "url": "https://drive.google.com/file/d/1DI0TH2MuSHq8ONkZNUSmMjOfZZT2cgDp/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_32fe5a92-3a1f-4901-b8df-9b39b2.manifest.json",
        "file_id": "102m--_OyQMke5AmpUUqg9h5mbnAuuRsx",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_COMPACT_PROJECT_32fe5a92-3a1f-4901-b8df-9b39b2.manifest.json",
        "size": "2207",
        "modifiedTime": "2026-05-01T08:36:19.002Z",
        "url": "https://drive.google.com/file/d/102m--_OyQMke5AmpUUqg9h5mbnAuuRsx/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_a23dade9-48dc-4a1f-9ba9-26ebb6.manifest.json",
        "file_id": "14q0pOR8qSMJ7jhys1AcLtpbYYNP1eK9S",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_COMPACT_PROJECT_a23dade9-48dc-4a1f-9ba9-26ebb6.manifest.json",
        "size": "1692",
        "modifiedTime": "2026-05-01T08:35:36.114Z",
        "url": "https://drive.google.com/file/d/14q0pOR8qSMJ7jhys1AcLtpbYYNP1eK9S/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_8656edda-d8ea-450c-b59d-d737fd.manifest.json",
        "file_id": "1L6iz7R-LtcomX5Ntyvj8Is8tf9oGPtyE",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_COMPACT_PROJECT_8656edda-d8ea-450c-b59d-d737fd.manifest.json",
        "size": "1636",
        "modifiedTime": "2026-05-01T08:33:12.828Z",
        "url": "https://drive.google.com/file/d/1L6iz7R-LtcomX5Ntyvj8Is8tf9oGPtyE/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_1d292ac4-f427-49b8-9a81-779580.manifest.json",
        "file_id": "1VY-neLIdPHjwcapcjjrHEMV3607r4x8E",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_COMPACT_PROJECT_1d292ac4-f427-49b8-9a81-779580.manifest.json",
        "size": "1422",
        "modifiedTime": "2026-05-01T07:20:49.837Z",
        "url": "https://drive.google.com/file/d/1VY-neLIdPHjwcapcjjrHEMV3607r4x8E/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_82faa050-f5df-4986-a0e6-32ea2c.manifest.json",
        "file_id": "1pItsDSkBQu2ZQGWsPEZ7x1yFtYFPwFki",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_COMPACT_PROJECT_82faa050-f5df-4986-a0e6-32ea2c.manifest.json",
        "size": "1242",
        "modifiedTime": "2026-05-01T07:20:21.683Z",
        "url": "https://drive.google.com/file/d/1pItsDSkBQu2ZQGWsPEZ7x1yFtYFPwFki/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_673bf651-1db3-4300-ab85-33c4a2.manifest.json",
        "file_id": "1u3G2jAUaV7d0N8J3i6CQPYjh0sLUdGtS",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_COMPACT_PROJECT_673bf651-1db3-4300-ab85-33c4a2.manifest.json",
        "size": "1734",
        "modifiedTime": "2026-04-30T12:36:48.448Z",
        "url": "https://drive.google.com/file/d/1u3G2jAUaV7d0N8J3i6CQPYjh0sLUdGtS/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_b669d105-4dbe-446b-9a6f-0a773b.manifest.json",
        "file_id": "1w_vHPxVbdSKNMFoVtZIzuGCddHw9JfUK",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_COMPACT_PROJECT_b669d105-4dbe-446b-9a6f-0a773b.manifest.json",
        "size": "1104",
        "modifiedTime": "2026-04-30T10:03:47.957Z",
        "url": "https://drive.google.com/file/d/1w_vHPxVbdSKNMFoVtZIzuGCddHw9JfUK/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_smoke_ff12_compact.manifest.json",
        "file_id": "1qS6IauZK7VwJg1inaRnC4LVL7rTnjm5C",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_COMPACT_PROJECT_smoke_ff12_compact.manifest.json",
        "size": "1169",
        "modifiedTime": "2026-04-30T09:37:38.533Z",
        "url": "https://drive.google.com/file/d/1qS6IauZK7VwJg1inaRnC4LVL7rTnjm5C/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_6c7d0a0d-2b80-4b92-b.manifest.json",
        "file_id": "1E-p3UoEaSi-zzYwjpPGiZx-uu_2rhnLC",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_project_6c7d0a0d-2b80-4b92-b.manifest.json",
        "size": "4434",
        "modifiedTime": "2026-04-30T09:29:49.825Z",
        "url": "https://drive.google.com/file/d/1E-p3UoEaSi-zzYwjpPGiZx-uu_2rhnLC/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff10_project.manifest.json",
        "file_id": "1MacajqphpkojNHo85-v3-Q5riNTHaRno",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_project_smoke_ff10_project.manifest.json",
        "size": "4388",
        "modifiedTime": "2026-04-30T09:27:25.247Z",
        "url": "https://drive.google.com/file/d/1MacajqphpkojNHo85-v3-Q5riNTHaRno/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КД_project_87b491a5-3ec8-4cf0-a.manifest.json",
        "file_id": "1G6Uu_pNr3w1rwiWtRS4J5gb6bNG9cYZw",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КД_project_87b491a5-3ec8-4cf0-a.manifest.json",
        "size": "6343",
        "modifiedTime": "2026-04-30T09:18:49.180Z",
        "url": "https://drive.google.com/file/d/1G6Uu_pNr3w1rwiWtRS4J5gb6bNG9cYZw/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KD"
      },
      {
        "name": "АР_project_smoke_ff09_АР.manifest.json",
        "file_id": "1--Cw92bcTcTB_nTXcCOfATYPyZMfeOV2",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/АР_project_smoke_ff09_АР.manifest.json",
        "size": "4424",
        "modifiedTime": "2026-04-30T09:15:24.296Z",
        "url": "https://drive.google.com/file/d/1--Cw92bcTcTB_nTXcCOfATYPyZMfeOV2/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "КД_project_smoke_ff09_КД.manifest.json",
        "file_id": "1LCabegaMIvg4yTgzzZU14j1KIL4P6liV",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КД_project_smoke_ff09_КД.manifest.json",
        "size": "5244",
        "modifiedTime": "2026-04-30T09:15:16.849Z",
        "url": "https://drive.google.com/file/d/1LCabegaMIvg4yTgzzZU14j1KIL4P6liV/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KD"
      },
      {
        "name": "КЖ_project_smoke_ff09_КЖ.manifest.json",
        "file_id": "1yVcBXwAE64kQGpdTS6RkuIryvsfLrGhX",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_project_smoke_ff09_КЖ.manifest.json",
        "size": "5115",
        "modifiedTime": "2026-04-30T09:15:09.625Z",
        "url": "https://drive.google.com/file/d/1yVcBXwAE64kQGpdTS6RkuIryvsfLrGhX/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_0f869439-a7ce-4daf-9.manifest.json",
        "file_id": "15znz4spDIeGzzm0gTBmqlWsisL_RySHT",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_project_0f869439-a7ce-4daf-9.manifest.json",
        "size": "5559",
        "modifiedTime": "2026-04-30T09:09:26.895Z",
        "url": "https://drive.google.com/file/d/15znz4spDIeGzzm0gTBmqlWsisL_RySHT/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff08d.manifest.json",
        "file_id": "1kuRbK4V9zJagSNNn57HKb5g3E-ba3br2",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_project_smoke_ff08d.manifest.json",
        "size": "5480",
        "modifiedTime": "2026-04-30T09:06:00.293Z",
        "url": "https://drive.google.com/file/d/1kuRbK4V9zJagSNNn57HKb5g3E-ba3br2/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff08c.manifest.json",
        "file_id": "1PneYHvZXXFwRNbme8VBEgFQAB2uRjuZ4",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_project_smoke_ff08c.manifest.json",
        "size": "5480",
        "modifiedTime": "2026-04-30T09:05:52.538Z",
        "url": "https://drive.google.com/file/d/1PneYHvZXXFwRNbme8VBEgFQAB2uRjuZ4/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff08b.manifest.json",
        "file_id": "1wr8MyUY_ZF9ikcf-JWfzZsAUZgNwsNCQ",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_project_smoke_ff08b.manifest.json",
        "size": "5480",
        "modifiedTime": "2026-04-30T09:05:44.993Z",
        "url": "https://drive.google.com/file/d/1wr8MyUY_ZF9ikcf-JWfzZsAUZgNwsNCQ/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff08a.manifest.json",
        "file_id": "1FIxsbud2eTx7IGWJk7sk-CBr4XunfRR-",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_project_smoke_ff08a.manifest.json",
        "size": "5480",
        "modifiedTime": "2026-04-30T09:05:37.722Z",
        "url": "https://drive.google.com/file/d/1FIxsbud2eTx7IGWJk7sk-CBr4XunfRR-/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff07.manifest.json",
        "file_id": "174cYmJwf8KWJcX_MH9ituAaDWaSnn3Ts",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_project_smoke_ff07.manifest.json",
        "size": "5603",
        "modifiedTime": "2026-04-30T09:00:26.910Z",
        "url": "https://drive.google.com/file/d/174cYmJwf8KWJcX_MH9ituAaDWaSnn3Ts/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_MANIFEST_smoke_ff07.json",
        "file_id": "1p6sHQllzOAe8FTpMgnvXa6DcyhX0kKTG",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_MANIFEST_smoke_ff07.json",
        "size": "7379",
        "modifiedTime": "2026-04-30T08:56:02.318Z",
        "url": "https://drive.google.com/file/d/1p6sHQllzOAe8FTpMgnvXa6DcyhX0kKTG/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_MANIFEST_smoke_ff06_final.json",
        "file_id": "1j6VonhkfsXpeQfvL4ipreeqAsm1d8Aak",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_MANIFEST_smoke_ff06_final.json",
        "size": "1710",
        "modifiedTime": "2026-04-30T08:50:51.596Z",
        "url": "https://drive.google.com/file/d/1j6VonhkfsXpeQfvL4ipreeqAsm1d8Aak/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_foundation_slab_smoke_ff05.manifest.json",
        "file_id": "1yUTFojZz6OPp5lqDCtmcX8UhrH4oe0H1",
        "mimeType": "application/json",
        "path": "TOPIC_210/_manifests/КЖ_foundation_slab_smoke_ff05.manifest.json",
        "size": "7427",
        "modifiedTime": "2026-04-30T08:43:42.103Z",
        "url": "https://drive.google.com/file/d/1yUTFojZz6OPp5lqDCtmcX8UhrH4oe0H1/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_0de22d01-0615-4fc7-8cbb-bf9624.pdf",
        "file_id": "12dw_Zdxmpfg6i2aAuvTtig8S9Xd0UB4M",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_COMPACT_PROJECT_0de22d01-0615-4fc7-8cbb-bf9624.pdf",
        "size": "35232",
        "modifiedTime": "2026-05-01T19:35:26.481Z",
        "url": "https://drive.google.com/file/d/12dw_Zdxmpfg6i2aAuvTtig8S9Xd0UB4M/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_3598cf90-2986-4c40-a5be-6b77e6.pdf",
        "file_id": "1lbQT1ZyCv8StjCa9hh7XPgNGvpFOQoCU",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_COMPACT_PROJECT_3598cf90-2986-4c40-a5be-6b77e6.pdf",
        "size": "35232",
        "modifiedTime": "2026-05-01T19:25:48.911Z",
        "url": "https://drive.google.com/file/d/1lbQT1ZyCv8StjCa9hh7XPgNGvpFOQoCU/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_32fe5a92-3a1f-4901-b8df-9b39b2.pdf",
        "file_id": "1MrQ3j-ej_Mle4nK81_e3-z8dMPQk7X_v",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_COMPACT_PROJECT_32fe5a92-3a1f-4901-b8df-9b39b2.pdf",
        "size": "35232",
        "modifiedTime": "2026-05-01T08:36:17.272Z",
        "url": "https://drive.google.com/file/d/1MrQ3j-ej_Mle4nK81_e3-z8dMPQk7X_v/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_a23dade9-48dc-4a1f-9ba9-26ebb6.pdf",
        "file_id": "1jRtJkdlhOZNOBQOxeR57TvL7t7fO-uiz",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_COMPACT_PROJECT_a23dade9-48dc-4a1f-9ba9-26ebb6.pdf",
        "size": "35232",
        "modifiedTime": "2026-05-01T08:35:34.142Z",
        "url": "https://drive.google.com/file/d/1jRtJkdlhOZNOBQOxeR57TvL7t7fO-uiz/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_8656edda-d8ea-450c-b59d-d737fd.pdf",
        "file_id": "1P4vdF86xqFSFOv3VwoT8ZEzt8G-Z1Wvd",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_COMPACT_PROJECT_8656edda-d8ea-450c-b59d-d737fd.pdf",
        "size": "35232",
        "modifiedTime": "2026-05-01T08:33:10.900Z",
        "url": "https://drive.google.com/file/d/1P4vdF86xqFSFOv3VwoT8ZEzt8G-Z1Wvd/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_1d292ac4-f427-49b8-9a81-779580.pdf",
        "file_id": "1ppCTbw6bM9y2Efjmx9_O5vQMmNA_sWZP",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_COMPACT_PROJECT_1d292ac4-f427-49b8-9a81-779580.pdf",
        "size": "35232",
        "modifiedTime": "2026-05-01T07:20:48.069Z",
        "url": "https://drive.google.com/file/d/1ppCTbw6bM9y2Efjmx9_O5vQMmNA_sWZP/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_82faa050-f5df-4986-a0e6-32ea2c.pdf",
        "file_id": "1gGmdE8FSnog-2egC3FmCL6Bac89nmhZ2",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_COMPACT_PROJECT_82faa050-f5df-4986-a0e6-32ea2c.pdf",
        "size": "35232",
        "modifiedTime": "2026-05-01T07:20:19.987Z",
        "url": "https://drive.google.com/file/d/1gGmdE8FSnog-2egC3FmCL6Bac89nmhZ2/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_673bf651-1db3-4300-ab85-33c4a2.pdf",
        "file_id": "1wrEWUF5BoeLukRGYuytxJypjVdr84ZAF",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_COMPACT_PROJECT_673bf651-1db3-4300-ab85-33c4a2.pdf",
        "size": "35232",
        "modifiedTime": "2026-04-30T12:36:46.270Z",
        "url": "https://drive.google.com/file/d/1wrEWUF5BoeLukRGYuytxJypjVdr84ZAF/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_b669d105-4dbe-446b-9a6f-0a773b.pdf",
        "file_id": "1-RHKbjSfMgO_74B1bABrk0Ht8VUUL9NB",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_COMPACT_PROJECT_b669d105-4dbe-446b-9a6f-0a773b.pdf",
        "size": "35232",
        "modifiedTime": "2026-04-30T10:03:46.133Z",
        "url": "https://drive.google.com/file/d/1-RHKbjSfMgO_74B1bABrk0Ht8VUUL9NB/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_COMPACT_PROJECT_smoke_ff12_compact.pdf",
        "file_id": "1lyAazVNk2RuZl6pQJEZNzQ4osNyEbDWS",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_COMPACT_PROJECT_smoke_ff12_compact.pdf",
        "size": "35200",
        "modifiedTime": "2026-04-30T09:37:36.752Z",
        "url": "https://drive.google.com/file/d/1lyAazVNk2RuZl6pQJEZNzQ4osNyEbDWS/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_6c7d0a0d-2b80-4b92-b.xlsx",
        "file_id": "16-CFB_R1JRH_mxRV_SrIVtRBR5eyObYv",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_6c7d0a0d-2b80-4b92-b.xlsx",
        "size": "7488",
        "modifiedTime": "2026-04-30T09:29:48.010Z",
        "url": "https://docs.google.com/spreadsheets/d/16-CFB_R1JRH_mxRV_SrIVtRBR5eyObYv/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_6c7d0a0d-2b80-4b92-b.dxf",
        "file_id": "1h0JqxRh9j2CRDfhaknu7zmTnjiLc3dTx",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_6c7d0a0d-2b80-4b92-b.dxf",
        "size": "29711",
        "modifiedTime": "2026-04-30T09:29:46.008Z",
        "url": "https://drive.google.com/file/d/1h0JqxRh9j2CRDfhaknu7zmTnjiLc3dTx/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_6c7d0a0d-2b80-4b92-b.pdf",
        "file_id": "1_8xQ-QcAsGRMXyd9Dr56Qj3m-EGgkwgy",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_6c7d0a0d-2b80-4b92-b.pdf",
        "size": "46121",
        "modifiedTime": "2026-04-30T09:29:44.374Z",
        "url": "https://drive.google.com/file/d/1_8xQ-QcAsGRMXyd9Dr56Qj3m-EGgkwgy/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff10_project.xlsx",
        "file_id": "1MOQYN0IjLM0mg5wEUPqbVnUuLBDmPyvq",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff10_project.xlsx",
        "size": "7488",
        "modifiedTime": "2026-04-30T09:27:23.503Z",
        "url": "https://docs.google.com/spreadsheets/d/1MOQYN0IjLM0mg5wEUPqbVnUuLBDmPyvq/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff10_project.dxf",
        "file_id": "1LWTl7e_RMPtzWgP61WcF6IplkHP-I2c2",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff10_project.dxf",
        "size": "29713",
        "modifiedTime": "2026-04-30T09:27:21.645Z",
        "url": "https://drive.google.com/file/d/1LWTl7e_RMPtzWgP61WcF6IplkHP-I2c2/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff10_project.pdf",
        "file_id": "1Itkz-lWw8tIdu9uZ3O6lfClJrcswi9hd",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff10_project.pdf",
        "size": "46121",
        "modifiedTime": "2026-04-30T09:27:19.897Z",
        "url": "https://drive.google.com/file/d/1Itkz-lWw8tIdu9uZ3O6lfClJrcswi9hd/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КД_project_87b491a5-3ec8-4cf0-a.xlsx",
        "file_id": "14b5a4lxgHDIrO6gt00SaYE44PR2xeOOh",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КД_project_87b491a5-3ec8-4cf0-a.xlsx",
        "size": "7748",
        "modifiedTime": "2026-04-30T09:18:47.403Z",
        "url": "https://docs.google.com/spreadsheets/d/14b5a4lxgHDIrO6gt00SaYE44PR2xeOOh/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KD"
      },
      {
        "name": "КД_project_87b491a5-3ec8-4cf0-a.dxf",
        "file_id": "1QJ7Ia4AYGn4lekB_sPwQ4tGKVZQkAoUf",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КД_project_87b491a5-3ec8-4cf0-a.dxf",
        "size": "29695",
        "modifiedTime": "2026-04-30T09:18:45.376Z",
        "url": "https://drive.google.com/file/d/1QJ7Ia4AYGn4lekB_sPwQ4tGKVZQkAoUf/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KD"
      },
      {
        "name": "КД_project_87b491a5-3ec8-4cf0-a.pdf",
        "file_id": "1dJzAz1r43g9hXNfsrjx_iFLeu7jk4I0V",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КД_project_87b491a5-3ec8-4cf0-a.pdf",
        "size": "50788",
        "modifiedTime": "2026-04-30T09:18:43.149Z",
        "url": "https://drive.google.com/file/d/1dJzAz1r43g9hXNfsrjx_iFLeu7jk4I0V/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KD"
      },
      {
        "name": "АР_project_smoke_ff09_АР.xlsx",
        "file_id": "1UwbBLpz2-Fx-KL-RGhAv1e7hSIJa_6F3",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/АР_project_smoke_ff09_АР.xlsx",
        "size": "7534",
        "modifiedTime": "2026-04-30T09:15:22.579Z",
        "url": "https://docs.google.com/spreadsheets/d/1UwbBLpz2-Fx-KL-RGhAv1e7hSIJa_6F3/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "АР_project_smoke_ff09_АР.dxf",
        "file_id": "1_go1pmIzHeNuK-rNdyteXX-X7chr_jpt",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/АР_project_smoke_ff09_АР.dxf",
        "size": "29695",
        "modifiedTime": "2026-04-30T09:15:20.595Z",
        "url": "https://drive.google.com/file/d/1_go1pmIzHeNuK-rNdyteXX-X7chr_jpt/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "АР_project_smoke_ff09_АР.pdf",
        "file_id": "1T1tuHlONXoCKe_Wi4tvXWzgvHLsxnXrB",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/АР_project_smoke_ff09_АР.pdf",
        "size": "49386",
        "modifiedTime": "2026-04-30T09:15:18.793Z",
        "url": "https://drive.google.com/file/d/1T1tuHlONXoCKe_Wi4tvXWzgvHLsxnXrB/view?usp=drivesdk",
        "domain": "design",
        "discipline": "AR"
      },
      {
        "name": "КД_project_smoke_ff09_КД.xlsx",
        "file_id": "1XbQrcL26RU_keloJzvuwe5Krs5q03y53",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КД_project_smoke_ff09_КД.xlsx",
        "size": "7748",
        "modifiedTime": "2026-04-30T09:15:15.215Z",
        "url": "https://docs.google.com/spreadsheets/d/1XbQrcL26RU_keloJzvuwe5Krs5q03y53/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KD"
      },
      {
        "name": "КД_project_smoke_ff09_КД.dxf",
        "file_id": "1M6NpUSY0VEbeLQC5HqDjbaD78uSFKxMl",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КД_project_smoke_ff09_КД.dxf",
        "size": "29697",
        "modifiedTime": "2026-04-30T09:15:13.408Z",
        "url": "https://drive.google.com/file/d/1M6NpUSY0VEbeLQC5HqDjbaD78uSFKxMl/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KD"
      },
      {
        "name": "КД_project_smoke_ff09_КД.pdf",
        "file_id": "1p6nxTgonAlIq7v0o9AS3dIB8SBjFH9cV",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КД_project_smoke_ff09_КД.pdf",
        "size": "50794",
        "modifiedTime": "2026-04-30T09:15:11.548Z",
        "url": "https://drive.google.com/file/d/1p6nxTgonAlIq7v0o9AS3dIB8SBjFH9cV/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KD"
      },
      {
        "name": "КЖ_project_smoke_ff09_КЖ.xlsx",
        "file_id": "1PtjboTm3EA_boROOb8JI_BTdszk-ML5E",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff09_КЖ.xlsx",
        "size": "7754",
        "modifiedTime": "2026-04-30T09:15:07.837Z",
        "url": "https://docs.google.com/spreadsheets/d/1PtjboTm3EA_boROOb8JI_BTdszk-ML5E/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff09_КЖ.dxf",
        "file_id": "1UKnIaYGuGli9berV5MR4QD9aWFjd9QTz",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff09_КЖ.dxf",
        "size": "29711",
        "modifiedTime": "2026-04-30T09:15:06.028Z",
        "url": "https://drive.google.com/file/d/1UKnIaYGuGli9berV5MR4QD9aWFjd9QTz/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff09_КЖ.pdf",
        "file_id": "1fGdnnh3JBqor3dDHlQg91-woOQQWUXV-",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff09_КЖ.pdf",
        "size": "57325",
        "modifiedTime": "2026-04-30T09:15:04.076Z",
        "url": "https://drive.google.com/file/d/1fGdnnh3JBqor3dDHlQg91-woOQQWUXV-/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_0f869439-a7ce-4daf-9.xlsx",
        "file_id": "1t_dPRvn4A6yMO0_Ix6BHSC9SPAeZq64t",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_0f869439-a7ce-4daf-9.xlsx",
        "size": "7829",
        "modifiedTime": "2026-04-30T09:09:25.115Z",
        "url": "https://docs.google.com/spreadsheets/d/1t_dPRvn4A6yMO0_Ix6BHSC9SPAeZq64t/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_0f869439-a7ce-4daf-9.dxf",
        "file_id": "1QpT4KF2-6yuIj1THgGOJP7te_Bsqzcdl",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_0f869439-a7ce-4daf-9.dxf",
        "size": "29713",
        "modifiedTime": "2026-04-30T09:09:23.166Z",
        "url": "https://drive.google.com/file/d/1QpT4KF2-6yuIj1THgGOJP7te_Bsqzcdl/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_0f869439-a7ce-4daf-9.pdf",
        "file_id": "1PBs0bL4Gl04suQOhSlGqeYfvaWvxzF0C",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_0f869439-a7ce-4daf-9.pdf",
        "size": "53507",
        "modifiedTime": "2026-04-30T09:09:20.983Z",
        "url": "https://drive.google.com/file/d/1PBs0bL4Gl04suQOhSlGqeYfvaWvxzF0C/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff08d.xlsx",
        "file_id": "1YyN1r60051Aj1qstEo-5YS5jJkELJnN0",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff08d.xlsx",
        "size": "7829",
        "modifiedTime": "2026-04-30T09:05:58.342Z",
        "url": "https://docs.google.com/spreadsheets/d/1YyN1r60051Aj1qstEo-5YS5jJkELJnN0/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff08d.dxf",
        "file_id": "1cuW2T_b6sfE9Zn-kIyBPeRPmnPokhJmV",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff08d.dxf",
        "size": "29713",
        "modifiedTime": "2026-04-30T09:05:56.334Z",
        "url": "https://drive.google.com/file/d/1cuW2T_b6sfE9Zn-kIyBPeRPmnPokhJmV/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff08d.pdf",
        "file_id": "1ydJB1fNAhKfhHRt4pj8vjrS9FsipDjBM",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff08d.pdf",
        "size": "53497",
        "modifiedTime": "2026-04-30T09:05:54.537Z",
        "url": "https://drive.google.com/file/d/1ydJB1fNAhKfhHRt4pj8vjrS9FsipDjBM/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff08c.xlsx",
        "file_id": "1ZI_8E2-Gs6nzZ6Qh3UqCXuKG2d6oGiHv",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff08c.xlsx",
        "size": "7829",
        "modifiedTime": "2026-04-30T09:05:50.728Z",
        "url": "https://docs.google.com/spreadsheets/d/1ZI_8E2-Gs6nzZ6Qh3UqCXuKG2d6oGiHv/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff08c.dxf",
        "file_id": "1DACQLUAR5M_oZJ_4FPlCzqZcvTZWLBs5",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff08c.dxf",
        "size": "29711",
        "modifiedTime": "2026-04-30T09:05:48.802Z",
        "url": "https://drive.google.com/file/d/1DACQLUAR5M_oZJ_4FPlCzqZcvTZWLBs5/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff08c.pdf",
        "file_id": "1fS1lEwgU2UM1a3B9PevTbkZmnvRPw2sO",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff08c.pdf",
        "size": "53497",
        "modifiedTime": "2026-04-30T09:05:46.976Z",
        "url": "https://drive.google.com/file/d/1fS1lEwgU2UM1a3B9PevTbkZmnvRPw2sO/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff08b.xlsx",
        "file_id": "1U6SU1iDDUR_Cqn74fUin3Rt9hbaJjFW_",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff08b.xlsx",
        "size": "7829",
        "modifiedTime": "2026-04-30T09:05:43.288Z",
        "url": "https://docs.google.com/spreadsheets/d/1U6SU1iDDUR_Cqn74fUin3Rt9hbaJjFW_/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff08b.dxf",
        "file_id": "1keWIZnVTDQ-2rM34NA82hlWGLzrzB4yQ",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff08b.dxf",
        "size": "29713",
        "modifiedTime": "2026-04-30T09:05:41.191Z",
        "url": "https://drive.google.com/file/d/1keWIZnVTDQ-2rM34NA82hlWGLzrzB4yQ/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff08b.pdf",
        "file_id": "15zse5XF48iCTWXPifG6NoGtAkqOAlRis",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff08b.pdf",
        "size": "53497",
        "modifiedTime": "2026-04-30T09:05:39.443Z",
        "url": "https://drive.google.com/file/d/15zse5XF48iCTWXPifG6NoGtAkqOAlRis/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff08a.xlsx",
        "file_id": "1nRBr22TH-jDUrebHMm-ZrbcN9te5etWw",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff08a.xlsx",
        "size": "7829",
        "modifiedTime": "2026-04-30T09:05:35.995Z",
        "url": "https://docs.google.com/spreadsheets/d/1nRBr22TH-jDUrebHMm-ZrbcN9te5etWw/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff08a.dxf",
        "file_id": "13MXJD00kwlFjK9ssBX3QeuMUX-YsyTOU",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff08a.dxf",
        "size": "29711",
        "modifiedTime": "2026-04-30T09:05:34.074Z",
        "url": "https://drive.google.com/file/d/13MXJD00kwlFjK9ssBX3QeuMUX-YsyTOU/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff08a.pdf",
        "file_id": "1SOvtx5wa2gcxqN5b3njIiDEw3pFP3FvM",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff08a.pdf",
        "size": "53497",
        "modifiedTime": "2026-04-30T09:05:31.843Z",
        "url": "https://drive.google.com/file/d/1SOvtx5wa2gcxqN5b3njIiDEw3pFP3FvM/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff07.xlsx",
        "file_id": "1EOAsBaB_vqRjy7t8_Sf6SkdnTjB4i6HV",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff07.xlsx",
        "size": "7829",
        "modifiedTime": "2026-04-30T09:00:24.806Z",
        "url": "https://docs.google.com/spreadsheets/d/1EOAsBaB_vqRjy7t8_Sf6SkdnTjB4i6HV/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff07.dxf",
        "file_id": "146ezdb9dCk0zXuTnuChXSV5NZo4vcq_u",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff07.dxf",
        "size": "29711",
        "modifiedTime": "2026-04-30T09:00:22.648Z",
        "url": "https://drive.google.com/file/d/146ezdb9dCk0zXuTnuChXSV5NZo4vcq_u/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_project_smoke_ff07.pdf",
        "file_id": "1ts_nkbmFuitaZjnYRpRmnkJTfjVhoQ4T",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_project_smoke_ff07.pdf",
        "size": "53497",
        "modifiedTime": "2026-04-30T09:00:20.753Z",
        "url": "https://drive.google.com/file/d/1ts_nkbmFuitaZjnYRpRmnkJTfjVhoQ4T/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_SPEC_smoke_ff07.xlsx",
        "file_id": "1mRBlljXex0kAshb86voE9mfa9z8gqiZm",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_SPEC_smoke_ff07.xlsx",
        "size": "8595",
        "modifiedTime": "2026-04-30T08:56:00.618Z",
        "url": "https://docs.google.com/spreadsheets/d/1mRBlljXex0kAshb86voE9mfa9z8gqiZm/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_PROJECT_smoke_ff07.dxf",
        "file_id": "16zn4tfKfLsBO-pzxIvgSlxxQPomlBkud",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_PROJECT_smoke_ff07.dxf",
        "size": "35488",
        "modifiedTime": "2026-04-30T08:55:58.642Z",
        "url": "https://drive.google.com/file/d/16zn4tfKfLsBO-pzxIvgSlxxQPomlBkud/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_PROJECT_smoke_ff07.pdf",
        "file_id": "1D1gDkGF7O78qIXwzT6SGvUzdXKgv483B",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_PROJECT_smoke_ff07.pdf",
        "size": "62030",
        "modifiedTime": "2026-04-30T08:55:56.715Z",
        "url": "https://drive.google.com/file/d/1D1gDkGF7O78qIXwzT6SGvUzdXKgv483B/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_SPEC_smoke_ff06_final.xlsx",
        "file_id": "1qoQSt_9HF9wSvfKF7aBORvBy5PwCzztv",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_SPEC_smoke_ff06_final.xlsx",
        "size": "7156",
        "modifiedTime": "2026-04-30T08:50:49.949Z",
        "url": "https://docs.google.com/spreadsheets/d/1qoQSt_9HF9wSvfKF7aBORvBy5PwCzztv/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_PROJECT_smoke_ff06_final.dxf",
        "file_id": "1p1N9XLh4nzX9cd_d2XPklbAF1KbhCfYF",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_PROJECT_smoke_ff06_final.dxf",
        "size": "29866",
        "modifiedTime": "2026-04-30T08:50:47.815Z",
        "url": "https://drive.google.com/file/d/1p1N9XLh4nzX9cd_d2XPklbAF1KbhCfYF/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_PROJECT_smoke_ff06_final.pdf",
        "file_id": "1zWr4DEbQlOemH-F8YbUTV6fbayrkP_81",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_PROJECT_smoke_ff06_final.pdf",
        "size": "25108",
        "modifiedTime": "2026-04-30T08:50:45.731Z",
        "url": "https://drive.google.com/file/d/1zWr4DEbQlOemH-F8YbUTV6fbayrkP_81/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_foundation_slab_smoke_ff05.dxf",
        "file_id": "1Pu_JamfluXP9bO_ZqP108C_OiDrQ3XsY",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_foundation_slab_smoke_ff05.dxf",
        "size": "30252",
        "modifiedTime": "2026-04-30T08:43:39.866Z",
        "url": "https://drive.google.com/file/d/1Pu_JamfluXP9bO_ZqP108C_OiDrQ3XsY/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "КЖ_foundation_slab_smoke_ff05.pdf",
        "file_id": "1YCsURMnuaoSPOVTWuLgrQxbu8wPhco7i",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/КЖ_foundation_slab_smoke_ff05.pdf",
        "size": "35346",
        "modifiedTime": "2026-04-30T08:43:38.089Z",
        "url": "https://drive.google.com/file/d/1YCsURMnuaoSPOVTWuLgrQxbu8wPhco7i/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "project_КЖ_9fac561b_20260430_083807.dxf",
        "file_id": "17zKT6ELGmpNQD_i5jE7dNvIsoMKbeKlx",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/project_КЖ_9fac561b_20260430_083807.dxf",
        "size": "548",
        "modifiedTime": "2026-04-30T08:38:10.616Z",
        "url": "https://drive.google.com/file/d/17zKT6ELGmpNQD_i5jE7dNvIsoMKbeKlx/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "project_КЖ_9fac561b_20260430_083807.pdf",
        "file_id": "1Ascj52KEybUoL1HYhli9h05kwhSli8Rx",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/project_КЖ_9fac561b_20260430_083807.pdf",
        "size": "3779",
        "modifiedTime": "2026-04-30T08:38:08.720Z",
        "url": "https://drive.google.com/file/d/1Ascj52KEybUoL1HYhli9h05kwhSli8Rx/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "project_КЖ_smoke_ff_20260430_083643.dxf",
        "file_id": "1sZ2lDlTKZHbvcY_te6u7xZvqFahf7BX6",
        "mimeType": "image/vnd.dxf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/project_КЖ_smoke_ff_20260430_083643.dxf",
        "size": "554",
        "modifiedTime": "2026-04-30T08:36:46.631Z",
        "url": "https://drive.google.com/file/d/1sZ2lDlTKZHbvcY_te6u7xZvqFahf7BX6/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "project_КЖ_smoke_ff_20260430_083643.pdf",
        "file_id": "1rOfnpnmL1I9Bt1fxdhaIUZn6E0rqRRQz",
        "mimeType": "application/pdf",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/project_КЖ_smoke_ff_20260430_083643.pdf",
        "size": "3754",
        "modifiedTime": "2026-04-30T08:36:44.933Z",
        "url": "https://drive.google.com/file/d/1rOfnpnmL1I9Bt1fxdhaIUZn6E0rqRRQz/view?usp=drivesdk",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "project_КЖ_4e06863a.xlsx",
        "file_id": "1EhQbI74E3vRU3l9WhuEgeu8hqliVxMGD",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/project_КЖ_4e06863a.xlsx",
        "size": "5931",
        "modifiedTime": "2026-04-30T08:23:23.249Z",
        "url": "https://docs.google.com/spreadsheets/d/1EhQbI74E3vRU3l9WhuEgeu8hqliVxMGD/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "project_КЖ_4e06863a.docx",
        "file_id": "1lPXSrx7LWM64J8VT4K0ZD92R73164VvR",
        "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/project_КЖ_4e06863a.docx",
        "size": "37422",
        "modifiedTime": "2026-04-30T08:23:21.440Z",
        "url": "https://docs.google.com/document/d/1lPXSrx7LWM64J8VT4K0ZD92R73164VvR/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "project_КЖ_smoke_ff.xlsx",
        "file_id": "15NS2sE74pyNqUsni3LEMOhjQglQn8ZFr",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/project_КЖ_smoke_ff.xlsx",
        "size": "5953",
        "modifiedTime": "2026-04-30T08:19:33.355Z",
        "url": "https://docs.google.com/spreadsheets/d/15NS2sE74pyNqUsni3LEMOhjQglQn8ZFr/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "project_КЖ_smoke_ff.docx",
        "file_id": "1W-Gdx5y0vVDNdtnEOujkZTEDTwKDScFI",
        "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "path": "TOPIC_210/PROJECT_ARTIFACTS/project_КЖ_smoke_ff.docx",
        "size": "37431",
        "modifiedTime": "2026-04-30T08:19:31.555Z",
        "url": "https://docs.google.com/document/d/1W-Gdx5y0vVDNdtnEOujkZTEDTwKDScFI/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "design",
        "discipline": "KJ"
      },
      {
        "name": "Image19.png",
        "file_id": "1_RgOdU_hfu9InSRO0TaTKma3_D65-Sw_",
        "mimeType": "image/png",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/Image19.png",
        "size": "2942111",
        "modifiedTime": "2026-05-02T19:13:21.293Z",
        "url": "https://drive.google.com/file/d/1_RgOdU_hfu9InSRO0TaTKma3_D65-Sw_/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "ImagePT1.png",
        "file_id": "1nwOPDMIkLoETIAiUtobUrBKUZ3QVXPyq",
        "mimeType": "image/png",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/ImagePT1.png",
        "size": "3328286",
        "modifiedTime": "2026-05-02T19:13:12.851Z",
        "url": "https://drive.google.com/file/d/1nwOPDMIkLoETIAiUtobUrBKUZ3QVXPyq/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "ImagePT4.png",
        "file_id": "1UPmZiCwRxnILSSeeE3FERDjjOWmX-bMQ",
        "mimeType": "image/png",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/ImagePT4.png",
        "size": "7744455",
        "modifiedTime": "2026-05-02T19:13:04.173Z",
        "url": "https://drive.google.com/file/d/1UPmZiCwRxnILSSeeE3FERDjjOWmX-bMQ/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "ImagePT5.png",
        "file_id": "15d7lR1PzFsHP3nBH5C9M-c-AnwLjdCtO",
        "mimeType": "image/png",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/ImagePT5.png",
        "size": "9351026",
        "modifiedTime": "2026-05-02T19:12:47.022Z",
        "url": "https://drive.google.com/file/d/15d7lR1PzFsHP3nBH5C9M-c-AnwLjdCtO/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "ImagePT2.png",
        "file_id": "1x1ECaJmfpyRv0FPF9hIoTVuBjW1lZEGj",
        "mimeType": "image/png",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/ImagePT2.png",
        "size": "3054484",
        "modifiedTime": "2026-05-02T19:10:23.939Z",
        "url": "https://drive.google.com/file/d/1x1ECaJmfpyRv0FPF9hIoTVuBjW1lZEGj/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "Image26.png",
        "file_id": "10Y1r86HHTatpojUafGmsmHxtm_zkl4pO",
        "mimeType": "image/png",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/Image26.png",
        "size": "3016436",
        "modifiedTime": "2026-05-02T19:09:29.000Z",
        "url": "https://drive.google.com/file/d/10Y1r86HHTatpojUafGmsmHxtm_zkl4pO/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "Image25.png",
        "file_id": "1vzE8EPqCxXJo_4o5J9QxiXEXsbqez8yx",
        "mimeType": "image/png",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/Image25.png",
        "size": "2771264",
        "modifiedTime": "2026-05-02T19:09:25.000Z",
        "url": "https://drive.google.com/file/d/1vzE8EPqCxXJo_4o5J9QxiXEXsbqez8yx/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "ImagePT3.png",
        "file_id": "1fQeIRNpsTgWAP05Mt0rcNrZcvjqa5Hkm",
        "mimeType": "image/png",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/ImagePT3.png",
        "size": "3378713",
        "modifiedTime": "2026-05-02T19:09:10.000Z",
        "url": "https://drive.google.com/file/d/1fQeIRNpsTgWAP05Mt0rcNrZcvjqa5Hkm/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_1.jpg",
        "file_id": "1C-QSIlLePSneSy2ZLm6Ovek7X38FxvLB",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_1.jpg",
        "size": "2019061",
        "modifiedTime": "2026-05-02T13:51:42.533Z",
        "url": "https://drive.google.com/file/d/1C-QSIlLePSneSy2ZLm6Ovek7X38FxvLB/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "4 (1).jpg",
        "file_id": "13kao8QXwa7p9lFmvky8WwdQzFoPDEcsy",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/4 (1).jpg",
        "size": "4790475",
        "modifiedTime": "2025-04-28T22:03:02.000Z",
        "url": "https://drive.google.com/file/d/13kao8QXwa7p9lFmvky8WwdQzFoPDEcsy/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "ImagePT5 2.PNG",
        "file_id": "12YpCv8J7Vcg160SuAlbYAm16ums4LAB5",
        "mimeType": "image/png",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/ImagePT5 2.PNG",
        "size": "9351026",
        "modifiedTime": "2025-04-26T09:03:19.000Z",
        "url": "https://drive.google.com/file/d/12YpCv8J7Vcg160SuAlbYAm16ums4LAB5/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "ImagePT1 2.PNG",
        "file_id": "1NCq7VPdQst2fIgBQE0wp81cV25Iw0cVc",
        "mimeType": "image/png",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/ImagePT1 2.PNG",
        "size": "3328286",
        "modifiedTime": "2025-04-26T09:03:18.000Z",
        "url": "https://drive.google.com/file/d/1NCq7VPdQst2fIgBQE0wp81cV25Iw0cVc/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "Image28.png",
        "file_id": "1saVizX2MTaHfSyxP3L7yaImFJj0RA8mt",
        "mimeType": "image/png",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/Image28.png",
        "size": "3070003",
        "modifiedTime": "2025-04-11T15:41:05.000Z",
        "url": "https://drive.google.com/file/d/1saVizX2MTaHfSyxP3L7yaImFJj0RA8mt/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "Image23.png",
        "file_id": "1c_lrrRSa2GLF9bUEI_Y5GAX5SGMAt1kl",
        "mimeType": "image/png",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/Image23.png",
        "size": "3280899",
        "modifiedTime": "2025-02-17T21:08:21.000Z",
        "url": "https://drive.google.com/file/d/1c_lrrRSa2GLF9bUEI_Y5GAX5SGMAt1kl/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "Image22.png",
        "file_id": "1KNsukR8JbxIN8F3MZEJe3eZFCOvDp7eG",
        "mimeType": "image/png",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/Image22.png",
        "size": "2588259",
        "modifiedTime": "2025-02-17T21:08:20.000Z",
        "url": "https://drive.google.com/file/d/1KNsukR8JbxIN8F3MZEJe3eZFCOvDp7eG/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "Image20.png",
        "file_id": "1Iv5XDVKzYkeuamsQy2onzbBbpYZbfebb",
        "mimeType": "image/png",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/Image20.png",
        "size": "2756011",
        "modifiedTime": "2025-02-17T21:08:20.000Z",
        "url": "https://drive.google.com/file/d/1Iv5XDVKzYkeuamsQy2onzbBbpYZbfebb/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "Image19 (2).png",
        "file_id": "1uCSjUuJiYNhE7Reqfvopt60h37y-s9RU",
        "mimeType": "image/png",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/Image19 (2).png",
        "size": "3253780",
        "modifiedTime": "2025-02-17T21:08:16.000Z",
        "url": "https://drive.google.com/file/d/1uCSjUuJiYNhE7Reqfvopt60h37y-s9RU/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "Image14.png",
        "file_id": "1YSjVzrFSK4fMVXYaZ9tg4jNou3xfP9UR",
        "mimeType": "image/png",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/Image14.png",
        "size": "2844079",
        "modifiedTime": "2025-02-17T21:08:15.000Z",
        "url": "https://drive.google.com/file/d/1YSjVzrFSK4fMVXYaZ9tg4jNou3xfP9UR/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_6 (1).jpg",
        "file_id": "19w5gknPo_AQTFcwUXoMlRAaOnwkYwxP9",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_6 (1).jpg",
        "size": "2109520",
        "modifiedTime": "2023-10-01T09:43:32.000Z",
        "url": "https://drive.google.com/file/d/19w5gknPo_AQTFcwUXoMlRAaOnwkYwxP9/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_5 (1).jpg",
        "file_id": "1MIqPykHklFmIyrutwFs1F628YrXW5vjL",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_5 (1).jpg",
        "size": "1947998",
        "modifiedTime": "2023-10-01T09:42:04.000Z",
        "url": "https://drive.google.com/file/d/1MIqPykHklFmIyrutwFs1F628YrXW5vjL/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_4 (1).jpg",
        "file_id": "1ilhBlNU5TP2p6vkfvCwWtPaXc-n14yMF",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_4 (1).jpg",
        "size": "1609715",
        "modifiedTime": "2023-10-01T09:40:52.000Z",
        "url": "https://drive.google.com/file/d/1ilhBlNU5TP2p6vkfvCwWtPaXc-n14yMF/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_3 (1).jpg",
        "file_id": "1Zg4WLzRHrQztdM3FPjQsboDN53jCuRcA",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_3 (1).jpg",
        "size": "1697732",
        "modifiedTime": "2023-10-01T09:39:38.000Z",
        "url": "https://drive.google.com/file/d/1Zg4WLzRHrQztdM3FPjQsboDN53jCuRcA/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_2 (1).jpg",
        "file_id": "1nqbmOlaYgu3aCuWh-a7Z6-Qo9VUhAqzR",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_2 (1).jpg",
        "size": "1842008",
        "modifiedTime": "2023-10-01T09:38:22.000Z",
        "url": "https://drive.google.com/file/d/1nqbmOlaYgu3aCuWh-a7Z6-Qo9VUhAqzR/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_1 (1).jpg",
        "file_id": "16STiMgKaoK31RtExPivkkfN5Dvqh4mXm",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_1 (1).jpg",
        "size": "1730158",
        "modifiedTime": "2023-10-01T09:37:24.000Z",
        "url": "https://drive.google.com/file/d/16STiMgKaoK31RtExPivkkfN5Dvqh4mXm/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_6.jpg",
        "file_id": "1KQmT9yIQEGTzrnlkGjRioNxg5TZc20nD",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_6.jpg",
        "size": "2257046",
        "modifiedTime": "2023-09-11T20:31:24.000Z",
        "url": "https://drive.google.com/file/d/1KQmT9yIQEGTzrnlkGjRioNxg5TZc20nD/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_6.jpg",
        "file_id": "1FaD5v0qlKLAhlSQmTf59T48d1YfWMVU3",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_6.jpg",
        "size": "2257046",
        "modifiedTime": "2023-09-11T20:31:24.000Z",
        "url": "https://drive.google.com/file/d/1FaD5v0qlKLAhlSQmTf59T48d1YfWMVU3/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_6 (1).jpg",
        "file_id": "1WgId7UisrG5-bVfVsbvvN3uqOXVA5CYB",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_6 (1).jpg",
        "size": "2257046",
        "modifiedTime": "2023-09-11T20:31:24.000Z",
        "url": "https://drive.google.com/file/d/1WgId7UisrG5-bVfVsbvvN3uqOXVA5CYB/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_5 (1).jpg",
        "file_id": "1JuVpmjvJWlSTnqaEBlUlKR68c1MBOYT3",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_5 (1).jpg",
        "size": "2266153",
        "modifiedTime": "2023-09-11T20:30:00.000Z",
        "url": "https://drive.google.com/file/d/1JuVpmjvJWlSTnqaEBlUlKR68c1MBOYT3/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_5.jpg",
        "file_id": "14DoGA2CtlFYRB_q5zYOfJrpxPbQEpSj7",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_5.jpg",
        "size": "2266153",
        "modifiedTime": "2023-09-11T20:30:00.000Z",
        "url": "https://drive.google.com/file/d/14DoGA2CtlFYRB_q5zYOfJrpxPbQEpSj7/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_5.jpg",
        "file_id": "1_VTZbf6p6_X8SOSQqdbTMhdSAnj7djxg",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_5.jpg",
        "size": "2266153",
        "modifiedTime": "2023-09-11T20:30:00.000Z",
        "url": "https://drive.google.com/file/d/1_VTZbf6p6_X8SOSQqdbTMhdSAnj7djxg/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_4 (1).jpg",
        "file_id": "1m6ZpNPby_KLvqYyFr3C_LJSyLqUxSxcc",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_4 (1).jpg",
        "size": "1977877",
        "modifiedTime": "2023-09-11T20:28:36.000Z",
        "url": "https://drive.google.com/file/d/1m6ZpNPby_KLvqYyFr3C_LJSyLqUxSxcc/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_4.jpg",
        "file_id": "1ZJwBaJ4a5uvM9pj4-nADLL3hYUgWK3JH",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_4.jpg",
        "size": "1977877",
        "modifiedTime": "2023-09-11T20:28:36.000Z",
        "url": "https://drive.google.com/file/d/1ZJwBaJ4a5uvM9pj4-nADLL3hYUgWK3JH/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_4.jpg",
        "file_id": "1st649_TOOlADrrYSgBoO6aMx4va_KnOf",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_4.jpg",
        "size": "1977877",
        "modifiedTime": "2023-09-11T20:28:36.000Z",
        "url": "https://drive.google.com/file/d/1st649_TOOlADrrYSgBoO6aMx4va_KnOf/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_3 (1).jpg",
        "file_id": "168xwcolMMD7czjbn1Ve26oni-_mOUS6E",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_3 (1).jpg",
        "size": "1957306",
        "modifiedTime": "2023-09-11T20:27:16.000Z",
        "url": "https://drive.google.com/file/d/168xwcolMMD7czjbn1Ve26oni-_mOUS6E/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_3.jpg",
        "file_id": "11YuMjRjXWhsgkkr96QqodfrQWMyBMJDG",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_3.jpg",
        "size": "1957306",
        "modifiedTime": "2023-09-11T20:27:16.000Z",
        "url": "https://drive.google.com/file/d/11YuMjRjXWhsgkkr96QqodfrQWMyBMJDG/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_3.jpg",
        "file_id": "109RcIVHmLeVXjZicXKU-mJ7VTT2LoC9e",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_3.jpg",
        "size": "1957306",
        "modifiedTime": "2023-09-11T20:27:16.000Z",
        "url": "https://drive.google.com/file/d/109RcIVHmLeVXjZicXKU-mJ7VTT2LoC9e/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_2.jpg",
        "file_id": "18kdkkJfu86k11LduzD7321Xd2XbzMm9r",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_2.jpg",
        "size": "2098627",
        "modifiedTime": "2023-09-11T20:25:56.000Z",
        "url": "https://drive.google.com/file/d/18kdkkJfu86k11LduzD7321Xd2XbzMm9r/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_2 (1).jpg",
        "file_id": "1oBwvRfLp-_Etz1Wp3yWeOelq6p_M0Gol",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_2 (1).jpg",
        "size": "2098627",
        "modifiedTime": "2023-09-11T20:25:56.000Z",
        "url": "https://drive.google.com/file/d/1oBwvRfLp-_Etz1Wp3yWeOelq6p_M0Gol/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_2.jpg",
        "file_id": "1DDTYMQUx8i7oGECFF50bgsdSozzzALhe",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_2.jpg",
        "size": "2098627",
        "modifiedTime": "2023-09-11T20:25:56.000Z",
        "url": "https://drive.google.com/file/d/1DDTYMQUx8i7oGECFF50bgsdSozzzALhe/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_1.jpg",
        "file_id": "1HSsAi2s1RzGJiGXVJ09ZxJK692-3jWeJ",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_1.jpg",
        "size": "2034848",
        "modifiedTime": "2023-09-11T20:24:34.000Z",
        "url": "https://drive.google.com/file/d/1HSsAi2s1RzGJiGXVJ09ZxJK692-3jWeJ/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_1 (1).jpg",
        "file_id": "1tPAcGd-UxBirRvxC9cK8RGsz3MfC4WA7",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_1 (1).jpg",
        "size": "2034848",
        "modifiedTime": "2023-09-11T20:24:34.000Z",
        "url": "https://drive.google.com/file/d/1tPAcGd-UxBirRvxC9cK8RGsz3MfC4WA7/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_6.jpg",
        "file_id": "1w2GH5d1zwvSnz1wWg7s1n4KYIoFdZGjk",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_6.jpg",
        "size": "1690996",
        "modifiedTime": "2023-08-10T21:19:44.000Z",
        "url": "https://drive.google.com/file/d/1w2GH5d1zwvSnz1wWg7s1n4KYIoFdZGjk/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_6.jpg",
        "file_id": "1NckXBov8jNalg-NAbq-QAJ3MY1s-jQDz",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_6.jpg",
        "size": "1690996",
        "modifiedTime": "2023-08-10T21:19:44.000Z",
        "url": "https://drive.google.com/file/d/1NckXBov8jNalg-NAbq-QAJ3MY1s-jQDz/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_6.jpg",
        "file_id": "1Y0Wq6VJ3MoD6T-TiOLFvMpWR-FUnQ9RO",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_6.jpg",
        "size": "1690996",
        "modifiedTime": "2023-08-10T21:19:44.000Z",
        "url": "https://drive.google.com/file/d/1Y0Wq6VJ3MoD6T-TiOLFvMpWR-FUnQ9RO/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_6 (1).jpg",
        "file_id": "1CIsQYxD605lhvn3fQ2LDQ5wQoiJhr5ST",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_6 (1).jpg",
        "size": "1690996",
        "modifiedTime": "2023-08-10T21:19:44.000Z",
        "url": "https://drive.google.com/file/d/1CIsQYxD605lhvn3fQ2LDQ5wQoiJhr5ST/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_5.jpg",
        "file_id": "1-RYyvmc2xW3wmDt6L51Z_PD-R8UREFzh",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_5.jpg",
        "size": "1997780",
        "modifiedTime": "2023-08-10T21:19:18.000Z",
        "url": "https://drive.google.com/file/d/1-RYyvmc2xW3wmDt6L51Z_PD-R8UREFzh/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_5 (1).jpg",
        "file_id": "1Zj6F59nfu1fvQTFmqPL29WhErDjE5GCc",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_5 (1).jpg",
        "size": "1997780",
        "modifiedTime": "2023-08-10T21:19:18.000Z",
        "url": "https://drive.google.com/file/d/1Zj6F59nfu1fvQTFmqPL29WhErDjE5GCc/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_5.jpg",
        "file_id": "1sd0pNdi8rGYJWCfdmjeuwbxlT5d3zpVn",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_5.jpg",
        "size": "1997780",
        "modifiedTime": "2023-08-10T21:19:18.000Z",
        "url": "https://drive.google.com/file/d/1sd0pNdi8rGYJWCfdmjeuwbxlT5d3zpVn/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_5.jpg",
        "file_id": "1xZ7hAxODc6-cEnWy1638RnnA9ijc0xZG",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_5.jpg",
        "size": "1997780",
        "modifiedTime": "2023-08-10T21:19:18.000Z",
        "url": "https://drive.google.com/file/d/1xZ7hAxODc6-cEnWy1638RnnA9ijc0xZG/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_4.jpg",
        "file_id": "1eXcHkTY_MAc7pHWBLoCmvbPzyy17RScE",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_4.jpg",
        "size": "1662302",
        "modifiedTime": "2023-08-10T21:18:46.000Z",
        "url": "https://drive.google.com/file/d/1eXcHkTY_MAc7pHWBLoCmvbPzyy17RScE/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_4.jpg",
        "file_id": "1RC18t8xyquzrXKK_Ip7CPROf6A7L6K4b",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_4.jpg",
        "size": "1662302",
        "modifiedTime": "2023-08-10T21:18:46.000Z",
        "url": "https://drive.google.com/file/d/1RC18t8xyquzrXKK_Ip7CPROf6A7L6K4b/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_4 (1).jpg",
        "file_id": "1b6LwACWjbAgnp_4FOcGLnYe-wPhmFRmT",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_4 (1).jpg",
        "size": "1662302",
        "modifiedTime": "2023-08-10T21:18:46.000Z",
        "url": "https://drive.google.com/file/d/1b6LwACWjbAgnp_4FOcGLnYe-wPhmFRmT/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_4.jpg",
        "file_id": "10pjjSjEG9TreYS0YJ6NTwTmcDlaJlQma",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_4.jpg",
        "size": "1662302",
        "modifiedTime": "2023-08-10T21:18:46.000Z",
        "url": "https://drive.google.com/file/d/10pjjSjEG9TreYS0YJ6NTwTmcDlaJlQma/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_3.jpg",
        "file_id": "1NolfhSKQF298hyK_0QI3UDjyPs89ZDm6",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_3.jpg",
        "size": "1900588",
        "modifiedTime": "2023-08-10T21:18:18.000Z",
        "url": "https://drive.google.com/file/d/1NolfhSKQF298hyK_0QI3UDjyPs89ZDm6/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_3.jpg",
        "file_id": "1cddWWyyTzVMtY_fsrwg4v4mNz0DVhyYN",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_3.jpg",
        "size": "1900588",
        "modifiedTime": "2023-08-10T21:18:18.000Z",
        "url": "https://drive.google.com/file/d/1cddWWyyTzVMtY_fsrwg4v4mNz0DVhyYN/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_3 (1).jpg",
        "file_id": "1ZZyNYgvQDCDj3b7H6OdFOcmQtwsoeG5U",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_3 (1).jpg",
        "size": "1900588",
        "modifiedTime": "2023-08-10T21:18:18.000Z",
        "url": "https://drive.google.com/file/d/1ZZyNYgvQDCDj3b7H6OdFOcmQtwsoeG5U/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_3.jpg",
        "file_id": "1IgGNs2OR2CHe4nfUTh0oyGCvVLaq1aY7",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_3.jpg",
        "size": "1900588",
        "modifiedTime": "2023-08-10T21:18:18.000Z",
        "url": "https://drive.google.com/file/d/1IgGNs2OR2CHe4nfUTh0oyGCvVLaq1aY7/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_2.jpg",
        "file_id": "1jTgmebnj5dItbEs4WjCYq4m3wtQTAzVY",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_2.jpg",
        "size": "1842251",
        "modifiedTime": "2023-08-10T21:17:54.000Z",
        "url": "https://drive.google.com/file/d/1jTgmebnj5dItbEs4WjCYq4m3wtQTAzVY/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_2.jpg",
        "file_id": "1HZl4VNOkVAb9sRppQNDOzZe_6vJTpuJd",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_2.jpg",
        "size": "1842251",
        "modifiedTime": "2023-08-10T21:17:54.000Z",
        "url": "https://drive.google.com/file/d/1HZl4VNOkVAb9sRppQNDOzZe_6vJTpuJd/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_2 (1).jpg",
        "file_id": "1gST8FbU61rfkVwqSZvsvloPfSJRfqVuU",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_2 (1).jpg",
        "size": "1842251",
        "modifiedTime": "2023-08-10T21:17:54.000Z",
        "url": "https://drive.google.com/file/d/1gST8FbU61rfkVwqSZvsvloPfSJRfqVuU/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_2.jpg",
        "file_id": "1G9hbdZM8Q8D4vfD63t0Zg1SCv0oFI3Of",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_2.jpg",
        "size": "1842251",
        "modifiedTime": "2023-08-10T21:17:54.000Z",
        "url": "https://drive.google.com/file/d/1G9hbdZM8Q8D4vfD63t0Zg1SCv0oFI3Of/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_1.jpg",
        "file_id": "1qyzqzRcjpxiTh-JON9_OBkQP44kmvyQz",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_1.jpg",
        "size": "2019061",
        "modifiedTime": "2023-08-10T21:17:24.000Z",
        "url": "https://drive.google.com/file/d/1qyzqzRcjpxiTh-JON9_OBkQP44kmvyQz/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_1 (1).jpg",
        "file_id": "19xdgSgZP2g59gMDe3bUEqjDW-rkwIvVu",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_1 (1).jpg",
        "size": "2019061",
        "modifiedTime": "2023-08-10T21:17:24.000Z",
        "url": "https://drive.google.com/file/d/19xdgSgZP2g59gMDe3bUEqjDW-rkwIvVu/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "1_1.jpg",
        "file_id": "17IXAMZ_mVD7SfDHgmVK6c-AZ_LRKOINT",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/1_1.jpg",
        "size": "2019061",
        "modifiedTime": "2023-08-10T21:17:24.000Z",
        "url": "https://drive.google.com/file/d/17IXAMZ_mVD7SfDHgmVK6c-AZ_LRKOINT/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "2_5.jpg",
        "file_id": "19mPHPNpV2Yy8unGnnn0ZakozdXs_mvGA",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/2_5.jpg",
        "size": "1816264",
        "modifiedTime": "2023-08-10T19:04:38.000Z",
        "url": "https://drive.google.com/file/d/19mPHPNpV2Yy8unGnnn0ZakozdXs_mvGA/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "2_5.jpg",
        "file_id": "15fhN3gAHZqzWSDrtm3pPMc8xGdQvjzzm",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/2_5.jpg",
        "size": "1816264",
        "modifiedTime": "2023-08-10T19:04:38.000Z",
        "url": "https://drive.google.com/file/d/15fhN3gAHZqzWSDrtm3pPMc8xGdQvjzzm/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "2_4.jpg",
        "file_id": "1GIFEMQkzqj_gsqv5QghNj4jkc0ZMjGWT",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/2_4.jpg",
        "size": "1805911",
        "modifiedTime": "2023-08-10T19:03:38.000Z",
        "url": "https://drive.google.com/file/d/1GIFEMQkzqj_gsqv5QghNj4jkc0ZMjGWT/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "2_4.jpg",
        "file_id": "1VzuAFb5u6nv9g2_YmDdq9x_92elwRAvr",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/2_4.jpg",
        "size": "1805911",
        "modifiedTime": "2023-08-10T19:03:38.000Z",
        "url": "https://drive.google.com/file/d/1VzuAFb5u6nv9g2_YmDdq9x_92elwRAvr/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "2_3.jpg",
        "file_id": "1z2I2_BihM0EAH1sw2aVar5EdSt10GSD6",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/2_3.jpg",
        "size": "2241840",
        "modifiedTime": "2023-08-10T19:02:40.000Z",
        "url": "https://drive.google.com/file/d/1z2I2_BihM0EAH1sw2aVar5EdSt10GSD6/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "2_3.jpg",
        "file_id": "1mv9mVGtJh1CkvlhwFXp8DpfCISysHyJj",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/2_3.jpg",
        "size": "2241840",
        "modifiedTime": "2023-08-10T19:02:40.000Z",
        "url": "https://drive.google.com/file/d/1mv9mVGtJh1CkvlhwFXp8DpfCISysHyJj/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "2_2.jpg",
        "file_id": "1g2_p7BBcZbV-6o2skAigITEDGT7NY802",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/2_2.jpg",
        "size": "2125562",
        "modifiedTime": "2023-08-10T19:01:42.000Z",
        "url": "https://drive.google.com/file/d/1g2_p7BBcZbV-6o2skAigITEDGT7NY802/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "2_2.jpg",
        "file_id": "1oZAARqcJaWkgMD7dKdJidxtzm0DJBp70",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/2_2.jpg",
        "size": "2125562",
        "modifiedTime": "2023-08-10T19:01:42.000Z",
        "url": "https://drive.google.com/file/d/1oZAARqcJaWkgMD7dKdJidxtzm0DJBp70/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "2_1.jpg",
        "file_id": "1FXaTOUx7-MQ_l_apQhBPou8-eEN_gBjo",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/2_1.jpg",
        "size": "2131773",
        "modifiedTime": "2023-08-10T19:00:40.000Z",
        "url": "https://drive.google.com/file/d/1FXaTOUx7-MQ_l_apQhBPou8-eEN_gBjo/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "2_1.jpg",
        "file_id": "1y0dW-nimJoPxw3VJ7XkfI1fXXtIujTUE",
        "mimeType": "image/jpeg",
        "path": "TOPIC_210/PROJECT_DESIGN_REFERENCES/2_1.jpg",
        "size": "2131773",
        "modifiedTime": "2023-08-10T19:00:40.000Z",
        "url": "https://drive.google.com/file/d/1y0dW-nimJoPxw3VJ7XkfI1fXXtIujTUE/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "photo_-1003725299009_8397.jpg",
        "file_id": "1artij2WG1SYUvzi8SmUnjxrojzpLK0Fe",
        "mimeType": "image/jpeg",
        "path": "TOPIC_5/photo_-1003725299009_8397.jpg",
        "size": "1012523",
        "modifiedTime": "2026-04-30T02:49:26.735Z",
        "url": "https://drive.google.com/file/d/1artij2WG1SYUvzi8SmUnjxrojzpLK0Fe/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      },
      {
        "name": "photo_-1003725299009_8372.jpg",
        "file_id": "1qEOW24i2n74o55z7RvDVDAn8fh2VoRUp",
        "mimeType": "image/jpeg",
        "path": "TOPIC_5/photo_-1003725299009_8372.jpg",
        "size": "1327420",
        "modifiedTime": "2026-04-30T02:43:44.815Z",
        "url": "https://drive.google.com/file/d/1qEOW24i2n74o55z7RvDVDAn8fh2VoRUp/view?usp=drivesdk",
        "domain": "design",
        "discipline": "SKETCH"
      }
    ],
    "technadzor_references": [
      {
        "name": "act_дефект_бетон.docx",
        "file_id": "1IFiaZW7BI4zjL37NTbQZO5razfNBhzWz",
        "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "path": "TOPIC_5/TECHNADZOR/act_дефект_бетон.docx",
        "size": "37414",
        "modifiedTime": "2026-05-01T22:49:05.182Z",
        "url": "https://docs.google.com/document/d/1IFiaZW7BI4zjL37NTbQZO5razfNBhzWz/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
        "domain": "technadzor",
        "role": "technadzor_reference"
      }
    ]
  },
  "active": "AREAL_REFERENCE_FULL_MONOLITH_V1",
  "topic_isolation": {
    "estimate": 2,
    "technadzor": 5,
    "design": 210
  }
}

====================================================================================================
END_FILE: config/owner_reference_registry.json
FILE_CHUNK: 1/1
====================================================================================================
