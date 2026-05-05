# TOPIC5 RUNTIME USAGE RULES

version: TOPIC5_RUNTIME_USAGE_RULES_V1
updated_at: 2026-05-05
status: CODE_AUDIT_VERIFIED

---

## 1. Что можно трогать / что нельзя

### Запрещено редактировать напрямую
```
task_worker.py           — overlay chain (_handle_in_progress 14 definitions)
telegram_daemon.py       — Telegram polling loop
ai_router.py             — routing logic
reply_sender.py          — delivery chain
google_io.py             — Drive OAuth
normative_engine.py      — dirty (+283 lines P6H5 expansion), не stage, не commit
.env / credentials.json  — секреты
token.json / *.session   — OAuth токены
data/core.db             — рабочая БД
data/memory.db           — memory БД
```

### Разрешено
```
docs/**                  — документация (append или новые файлы)
core/technadzor_engine.py — только append к концу файла (monkeypatch pattern)
core/normative_engine.py  — только append к концу файла (если явно разрешено)
```

---

## 2. Append-only rule

Все изменения кода в `/root/.areal-neva-core` — только дописывание к концу файла.
Это соответствует существующему паттерну wrapper/monkeypatch-цепочек.

Нельзя: редактировать существующие функции в середине файла.
Можно: добавить новую обёртку в конец, которая вызывает предыдущую версию.

---

## 3. Перед любым патчем

1. Прочитать `docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md`
2. Прочитать `HANDOFFS/LATEST_HANDOFF.md`
3. Убедиться что normative_engine.py не попадает в staged

---

## 4. Активное состояние системы (2026-05-05)

```
ActiveTechnadzorFolder:
  object: тест надзор
  folder_id: 1Jfw1VKgOi2GgdlimK-HCBw7mx9a_FbKG
  status: OPEN
  verified: true (task 5276 DONE)

process_technadzor wrapper chain:
  _p6h4tw_v1_wrapped = True
  P6H4FD → P6H4TW → ... (8 definitions)

Vision guard:
  EXTERNAL_PHOTO_ANALYSIS_ALLOWED = False
  OpenRouter Google: 403 при попытке включить

SearchMonolithV2:
  model: perplexity/sonar (via OpenRouter)
  OPENROUTER_API_KEY: confirmed in .env
  HTTP: real calls via urllib
```

---

## 5. Изоляция объектов

- Дефекты KIEVSKOE_95 → только KIEVSKOE_95
- Дефекты NOVICHKOVO → только NOVICHKOVO
- Дефекты SUSANINO → только SUSANINO
- Нельзя переносить замечания между объектами
- Нельзя применять металлокаркасные нормы к каркасному дому без проверки

---

## 6. Перед git push

```bash
mv core/context_aggregator.py /tmp/context_aggregator_backup.py
# ... push ...
mv /tmp/context_aggregator_backup.py core/context_aggregator.py
```

Это обязательный шаг перед каждым push.
