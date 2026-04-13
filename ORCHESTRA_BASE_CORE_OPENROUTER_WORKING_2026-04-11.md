# ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026-04-11.md

Статус: базовое рабочее ядро оркестра через OpenRouter

## Контур
Telegram -> telegram_daemon.py -> core.db -> task_worker.py -> core/ai_router.py -> OpenRouter -> Telegram

## Память
memory_api_server.py -> data/memory.db

## Ключевые файлы
- telegram_daemon: /root/.areal-neva-core/telegram_daemon.py
- task_worker: /root/.areal-neva-core/task_worker.py
- ai_router: /root/.areal-neva-core/core/ai_router.py
- memory_api_server: /root/.areal-neva-core/memory_api_server.py
- core_db: /root/.areal-neva-core/data/core.db
- memory_db: /root/.areal-neva-core/data/memory.db

## Процессы
```
931211 /root/.areal-neva-core/.venv/bin/python3 -u /root/.areal-neva-core/memory_api_server.py
931217 /root/.areal-neva-core/.venv/bin/python3 -u /root/.areal-neva-core/telegram_daemon.py
934122 .venv/bin/python3 -u task_worker.py
939864 /bin/sh -c pgrep -af 'memory_api_server.py|telegram_daemon.py|task_worker.py' || true
```

## Git
- branch: fatal: not a git repository (or any of the parent directories): .git
- commit: fatal: not a git repository (or any of the parent directories): .git

## Memory
- rows: 3
- export: ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026-04-11.memory.json

## Последние задачи
```json
[
  {
    "id": "14d0fefb-ecb0-4ce2-9e56-8fbbd9dc546b",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "",
    "state": "DONE",
    "result": "Всё в порядке, спасибо. А у тебя?",
    "error_message": null,
    "reply_to_message_id": 2795,
    "created_at": "2026-04-11T13:57:16.333447+00:00",
    "updated_at": "2026-04-11T13:57:17.465609+00:00"
  },
  {
    "id": "a51d0e33-bf9f-42be-bc3a-0ae2c7d2ccbf",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "Как настроение всё ли в порядке?",
    "state": "DONE",
    "result": "Настроение нормальное, всё в порядке. А у тебя?",
    "error_message": null,
    "reply_to_message_id": 2793,
    "created_at": "2026-04-11T13:57:04.883321+00:00",
    "updated_at": "2026-04-11T13:57:06.373296+00:00"
  },
  {
    "id": "a4c08fda-eaa7-428f-9575-1bd8bd8d7600",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "",
    "state": "DONE",
    "result": "Понял, готов отвечать.",
    "error_message": null,
    "reply_to_message_id": 2791,
    "created_at": "2026-04-11T13:56:51.395517+00:00",
    "updated_at": "2026-04-11T13:56:53.152799+00:00"
  },
  {
    "id": "fd6a77c5-1d85-4f62-bf45-ead1d76c0cbd",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "",
    "state": "DONE",
    "result": "Hello! How can I assist you today?",
    "error_message": null,
    "reply_to_message_id": 2789,
    "created_at": "2026-04-11T13:41:11.612250+00:00",
    "updated_at": "2026-04-11T13:41:18.307618+00:00"
  },
  {
    "id": "9ca9f754-eb00-4959-be75-0a11672418c9",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "",
    "state": "DONE",
    "result": "Hello! How can I assist you today?",
    "error_message": null,
    "reply_to_message_id": 2787,
    "created_at": "2026-04-11T13:40:55.751820+00:00",
    "updated_at": "2026-04-11T13:40:57.070533+00:00"
  },
  {
    "id": "8a2c53a3-e9c4-43c6-b8c4-32a73a9eb603",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "",
    "state": "DONE",
    "result": "It seems you might have intended to provide more context or a specific question. How can I assist you today?",
    "error_message": null,
    "reply_to_message_id": 2785,
    "created_at": "2026-04-11T13:40:34.152693+00:00",
    "updated_at": "2026-04-11T13:40:40.956432+00:00"
  },
  {
    "id": "b1abbf1b-a698-4cbb-bc02-db807d320c60",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "тест",
    "state": "DONE",
    "result": "Привет! Как я могу помочь вам сегодня?",
    "error_message": null,
    "reply_to_message_id": 2783,
    "created_at": "2026-04-11T13:40:20.148758+00:00",
    "updated_at": "2026-04-11T13:40:21.554233+00:00"
  }
]
```
