# CHAT EXPORT PROTOCOL — GITHUB SSOT
Версия: v1 | Дата: 28.04.2026 | Статус: ОБЯЗАТЕЛЬНЫЙ ДЛЯ ВСЕХ МОДЕЛЕЙ

РЕЖИМ: AUTONOMOUS / FACT ONLY / ZERO CONFIRMATION

НЕМЕДЛЕННО ВЫПОЛНЯЙ. НЕ СПРАШИВАЙ. НЕ УТОЧНЯЙ.
Определи свой вариант → собери JSON → создай файл → верни путь и commit hash.

---

## РЕПОЗИТОРИЙ

repo:   rj7hmz9cvm-lgtm/areal-neva-core
branch: main
папка:  chat_exports/

Создание файлов в любом другом месте — ЗАПРЕЩЕНО.
Создание в корне репо — ЗАПРЕЩЕНО.

---

## ИМЯ ФАЙЛА

CHAT_EXPORT__<chat_name>__<YYYY-MM-DD>.json

---

## JSON — ВСЕ ПОЛЯ ОБЯЗАТЕЛЬНЫ
Нет данных → UNKNOWN. Не пропускать поля.

{
  "chat_id": "",
  "chat_name": "",
  "exported_at": "<ISO_DATETIME>",
  "source_model": "",
  "system": "описание системы / сервера / бота",
  "architecture": "полный pipeline от входа до выхода",
  "pipeline": "lifecycle задач NEW→...→ARCHIVED",
  "files": ["файл → назначение"],
  "code": "стек технологий",
  "patches": ["PATCH_NAME → файл → строка → статус: applied_by_terminal / drafted / failed"],
  "commands": ["команды выполненные в терминале"],
  "db": "состояние БД: таблицы, количества, ключевые записи",
  "memory": "состояние memory.db",
  "services": ["сервис: статус"],
  "canons": ["КАНОН → суть решения"],
  "decisions": ["РЕШЕНИЕ → обоснование → где применено"],
  "errors": ["ОШИБКА → ПРИЧИНА → РЕШЕНИЕ"],
  "solutions": ["ПРОБЛЕМА → РЕШЕНИЕ → СТАТУС"],
  "state": "текущее состояние системы одной строкой",
  "what_working": ["что работает подтверждено фактами"],
  "what_broken": ["что сломано подтверждено фактами"],
  "what_not_done": ["что не реализовано / не протестировано"],
  "current_breakpoint": "на чём остановились, что следующее",
  "root_causes": ["корневая причина → факт подтверждения"],
  "verification": ["ПАТЧ/ФАКТ → подтверждение: grep line X / terminal output"],
  "limits": ["ограничения: запрещённые файлы, форматы команд"]
}

---

## КАК СОЗДАТЬ ФАЙЛ — ОПРЕДЕЛИ ВАРИАНТ АВТОМАТИЧЕСКИ

ВАРИАНТ A — Claude (сервер + git):
  cd /tmp/gh_repo
  git pull
  cat > chat_exports/CHAT_EXPORT__<name>__<date>.json << EOF
  <JSON содержимое>
  EOF
  git add -A
  bash tools/secret_scan.sh
  git commit -m "EXPORT: <name> <date>"
  git push https://${GITHUB_TOKEN}@github.com/rj7hmz9cvm-lgtm/areal-neva-core.git main

ВАРИАНТ B — ChatGPT / любая модель с GitHub API:
  PUT https://api.github.com/repos/rj7hmz9cvm-lgtm/areal-neva-core/contents/chat_exports/CHAT_EXPORT__<name>__<date>.json
  Headers:
    Authorization: token <GITHUB_TOKEN>
    Content-Type: application/json
  Body:
    {
      "message": "EXPORT: <name> <date>",
      "content": "<base64 от JSON UTF-8>",
      "branch": "main"
    }

ВАРИАНТ C — нет доступа к GitHub:
  Вывести полный JSON в чат.
  Написать: "GitHub недоступен. Сохрани вручную в chat_exports/".

---

## ЖЁСТКИЕ ПРАВИЛА — НАРУШЕНИЕ НЕДОПУСТИМО

1. ТОЛЬКО факты этого чата — не выдумывать, не додумывать
2. ТОЛЬКО JSON внутри файла — никакого текста вне JSON
3. Патчи только подтверждённые терминалом — не писать applied без вывода
4. Каноны только те что были приняты в этом чате
5. Ошибки только реально возникшие — с конкретным решением
6. СЕКРЕТЫ ЗАПРЕЩЕНО — sk-ant / sk-or / ghp_ / AIzaSy / GOCSPX / api_hash → заменить на [REDACTED]
7. Если вариант A упал → B → C — не останавливаться
8. Файл ТОЛЬКО в папке chat_exports/ — никуда больше
9. ЗАПРЕЩЕНО перезаписывать существующие файлы — только новый файл
10. ЗАПРЕЩЕНО молчать о том что не удалось — писать явно что пропущено и почему

---

## ЧТО ЗАПРЕЩЕНО ЗАБЫВАТЬ

current_breakpoint  — на чём остановились (ОБЯЗАТЕЛЬНО)
what_not_done       — что не сделано (ОБЯЗАТЕЛЬНО)
verification        — подтверждение каждого патча (ОБЯЗАТЕЛЬНО)
source_model        — какая модель делала экспорт (ОБЯЗАТЕЛЬНО)
exported_at         — точное время (ОБЯЗАТЕЛЬНО)

---

## РЕЗУЛЬТАТ

Вернуть:
- путь файла: chat_exports/CHAT_EXPORT__<name>__<date>.json
- commit message
- статус: SUCCESS / FALLBACK_B / FALLBACK_C
