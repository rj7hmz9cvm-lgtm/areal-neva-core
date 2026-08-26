# AREAL-NEVA ORCHESTRA — GITHUB SSOT
Создан: 28.04.2026

GitHub = каноны / архитектура / shared context / handoff / reports / tools
Сервер = runtime / обработка / memory.db / core.db / временные файлы
Drive = резерв и тяжёлые файлы

Регламент:
- только добавление, не перезатирание
- версионирование: v1 v2 v3
- patch-правило: было -> станет -> применить
- backup перед изменением
- токены никогда в репо

## Основные рабочие инструменты

- [Универсальный калькулятор смет](https://smeta-teplograd.ky3bkuh6at9l.chatgpt.site/) — отопление, водоснабжение и общестроительные сметы
- Канонический реестр: `core/estimate_calculator_registry.py`
