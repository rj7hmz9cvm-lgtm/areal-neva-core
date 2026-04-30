# WORKITEM_V1

Канон Stage 1 структуры WorkItem — единая рама любой задачи в AREAL-NEVA ORCHESTRA.

## Назначение

WorkItem — нормализованная единица работы. Создаётся один раз на входе в task_worker, движется через все слои, накапливает контекст и аудит. Никакие движки и слои не работают с raw payload — только с WorkItem или его сериализованным представлением.

## Поля

| Поле | Тип | Назначение |
|---|---|---|
| work_id | str | task_id из БД, уникальный ключ |
| chat_id | str | Telegram chat |
| topic_id | int | Telegram message_thread_id |
| user_id | str | Telegram user |
| message_id | int | id входящего сообщения |
| reply_to_message_id | int | для thread reply |
| bot_message_id | int | id сообщения бота для редактирования |
| source_type | str | telegram / api / cron |
| input_type | str | text / voice / photo / file / drive_file / url / mixed |
| raw_text | str | исходный текст или транскрипт |
| state | str | NEW / INTAKE / IN_PROGRESS / RESULT_READY / DONE |
| intent | str | детектированное намерение (UNKNOWN до Stage 2) |
| direction | str | id направления из directions.yaml |
| direction_profile | dict | профиль направления (срез на момент детекции) |
| formats_in | list[str] | детектированные форматы входа |
| formats_out | list[str] | требуемые форматы выхода |
| attachments | list[dict] | приложенные файлы |
| parsed_data | dict | результаты парсинга (Stage 3+) |
| context_refs | dict | ссылки на short/long memory (Stage 3) |
| execution_plan | list[dict] | план выполнения (Stage 2) |
| quality_gates | list[str] | gate-и из direction_profile |
| result | dict | финальный результат |
| audit | dict | трасса всех решений по WorkItem |
| errors | list[dict] | накопленные ошибки |
| metadata | dict | произвольные данные |

## Жизненный цикл

1. task_worker берёт строку из tasks → from_task_row(row) → WorkItem
2. Stage 1 (текущий): DirectionRegistry.detect() → set_direction() → audit
3. Stage 2 (план): Capability Router → execution_plan
4. Stage 3 (план): Context Engine → context_refs, parsed_data
5. Stage 4 (план): Engines выполняют execution_plan → result
6. Stage 5 (план): Quality Gate → проверка quality_gates
7. Stage 6 (план): Format Adapter → formats_out → доставка
8. Stage 7 (план): Archive Engine → длительная память

## Текущий статус

Stage 1 shadow mode: WorkItem создаётся, direction детектируется и кладётся в payload как `direction`, `direction_profile`, `direction_audit`, `work_item`. Старый pipeline продолжает работать как раньше — direction только наблюдается, не маршрутизирует.

## Контракт

- `WorkItem.from_task_row(row, extra=None)` — конструктор
- `WorkItem.set_direction(direction, profile)` — установка направления
- `WorkItem.set_intent(intent)` — установка намерения
- `WorkItem.add_audit(key, value)` — запись в trail
- `WorkItem.add_error(code, message, fatal)` — регистрация ошибки
- `WorkItem.to_dict()` — сериализация
- `WorkItem.to_payload()` — обратная совместимость с старым pipeline

## Расположение

- Код: `core/work_item.py`
- Маркер: `FULLFIX_DIRECTION_KERNEL_STAGE_1_WORKITEM`
