# TOPIC5 TECHNADZOR — SYSTEM LOGIC FINAL

version: TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL_V1
updated_at: 2026-05-05
status: FINAL_DOCUMENTED
topic: topic_5 / ТЕХНАДЗОР
references:
  canon: docs/CANON_FINAL/TECHNADZOR_DOMAIN_LOGIC_CANON.md
  unified_context: docs/TECHNADZOR/unified_context/TOPIC5_UNIFIED_TECHNADZOR_CONTEXT.md

---

## 1. Главный принцип

```
Google Drive папка = контейнер работы
Telegram topic_5   = пояснение владельца и управление задачей
Файлы              = материалы (не задачи)
Голос/текст владельца = техническое ТЗ + привязка замечаний
Оркестр            = связывает файлы, пояснения, объект, нормы, историю
Финал              = один разбор или один документ по всей задаче
```

Файл сам по себе — не задача.
61 фото = один выезд = один акт.
Никаких задач на каждое фото.

---

## 2. Составные части TechnadzorTask

```
TechnadzorTask =
  OwnerInstruction (голос или текст владельца)
  + InputFiles     (фото / PDF / DOCX из Drive или Telegram)
  + ActiveFolder   (текущая рабочая Drive-папка)
  + ObjectContext  (ObjectCard — история объекта)
  + PreviousActs   (предыдущие акты если есть)
```

---

## 3. Два пути передачи материалов

### Путь A — Drive (предпочтительный)
1. Владелец создаёт папку на Drive в ТЕХНАДЗОР root
2. Загружает фото, документы
3. В Telegram topic_5 поясняет: объект, задача, что проверить
4. Оркестр принимает папку как ActiveTechnadzorFolder
5. По команде "сделай разбор/акт" — формирует один результат

### Путь B — Telegram
1. Владелец присылает фото/файлы напрямую в topic_5
2. Комментирует голосом или текстом
3. Оркестр копит в VisitBuffer
4. По команде — flush → VisitPackage → один результат

**Смешивание путей допустимо:** файлы из Drive + голос из Telegram = норма.

---

## 4. Жизненный цикл задачи topic_5

```
Владелец → папка / фото / объяснение
→ Оркестр: ActiveTechnadzorFolder открыта?
     НЕТ → "К какой папке отнести материалы?"
     ДА  → принять, связать с объектом
→ VisitMaterial создаётся (COLLECTING_VISIT_MATERIALS)
→ По команде "сделай разбор/акт/документ":
     → VisitPackage собирается
     → ObjectContext загружается (история, предыдущие акты)
     → Нормы подбираются через normative_engine
     → Один результат: текстовый разбор / PDF акт / DOCX / XLSX
→ ObjectCard обновляется
→ Drive upload (только PDF/DOCX итогового документа в topic-папку)
```

---

## 5. ActiveTechnadzorFolder

```python
ActiveTechnadzorFolder:
  chat_id:           str
  topic_id:          int = 5
  object_name:       str        # название объекта
  visit_date:        str        # дата выезда
  drive_folder_url:  str        # ссылка на Drive папку
  drive_folder_id:   str        # id папки
  folder_name:       str        # название папки как на Drive
  client_facing:     bool       # true = клиентская папка
  mode_hint:         str        # INITIAL_INSPECTION / FOLLOWUP / NEXT_INSPECTION / ...
  active_since:      str        # timestamp открытия
  last_update:       str        # timestamp последнего изменения
  owner_instructions: list[str] # инструкции владельца
  status:            str        # OPEN / FLUSHED / CLOSED
```

**Файл состояния:** `data/technadzor/active_folder_{chat_id}_{topic_id}.json`

**Системные папки — НИКОГДА не становятся ActiveTechnadzorFolder:**
- TECHNADZOR
- ТЕХНАДЗОР
- topic_5
- _system / _tmp / _archive / _drafts / _templates / _manifests

**Верифицированное Drive дерево:**
- ТЕХНАДЗОР root: `1s2y5l2mJFTb7P90XVokErXYVzmoH-VtD`
- topic_5 system folder: `1yWIJdSrypH3BbIozCz-OAw1R6hmnMRHK`
- TECHNADZOR system: `1vKQM0Z2qBmiKtgeyx95JaNEQAp5mJLOm`

---

## 6. VisitMaterial

```python
VisitMaterial:
  material_id:          str         # uuid
  source:               str         # TELEGRAM / DRIVE
  file_type:            str         # PHOTO / VIDEO / PDF / DOCX / XLSX / TEXT / VOICE / OTHER
  file_name:            str
  drive_url:            str | None
  telegram_message_id:  int | None
  added_at:             str         # iso timestamp
  owner_comment:        str | None  # пояснение владельца
  group_label:          str | None  # "опорные узлы" / "сварные соединения" / ...
  include_in_report:    bool = True
  include_in_act:       bool = True
  defect_hint:          str | None  # краткое описание дефекта из голоса владельца
  section_hint:         str | None  # к какому разделу отнести
  status:               str         # PENDING / LINKED / EXCLUDED
```

**Буфер:** `data/technadzor/buf_{chat_id}_{topic_id}.json`

---

## 7. VisitPackage

```python
VisitPackage:
  active_folder:        ActiveTechnadzorFolder
  object_name:          str
  visit_date:           str
  previous_acts:        list[str]   # ссылки на Drive или file_id предыдущих актов
  photos:               list[VisitMaterial]
  videos:               list[VisitMaterial]
  documents:            list[VisitMaterial]
  owner_instructions:   list[str]
  client_comments:      list[str]
  contractor_comments:  list[str]
  material_groups:      dict[str, list[VisitMaterial]]  # group_label → materials
  excluded_materials:   list[VisitMaterial]
  requested_output:     str    # TEXT_REPORT / PDF_ACT / DOCX / XLSX / TELEGRAM
```

---

## 8. ObservationCard

```python
ObservationCard:
  source:             str   # OWNER_VOICE / OWNER_TEXT / PHOTO_EVIDENCE /
                            # PREVIOUS_ACT / CLIENT_TEXT / CONTRACTOR_TEXT /
                            # PROJECT_DOCUMENT / EXECUTIVE_DOCUMENT
  author:             str
  author_role:        str   # owner / client / contractor
  material_type:      str   # photo / voice / text / document
  object:             str
  date:               str
  claim:              str   # суть наблюдения
  linked_files:       list[str]
  confirmed:          str   # yes / no / partial
  contradiction:      bool
  needs_owner_question: bool
```

---

## 9. DefectCard

```python
DefectCard:
  photo_no:             int | None    # номер фото в разборе
  file_name:            str
  source:               str
  node_location:        str           # узел / место
  what_visible:         str           # что видно на фото/в материале
  defect_remark:        str           # дефект или замечание
  why_bad:              str           # почему плохо
  possible_consequences: str
  what_to_fix:          str
  what_to_check_on_site: str
  normative_reference:  str | None
  norm_status:          str           # CONFIRMED / PARTIAL / NOT_FOUND / SOURCE_MENTIONED_ONLY
  remark_status:        str           # см. список статусов замечаний
  confirmation_source:  str
  owner_question:       str | None    # вопрос к владельцу если нужен
```

---

## 10. Статусы замечаний

- новое замечание
- подтверждено по фото
- частично видно по фото
- устранено
- устранено частично
- не устранено
- требует доведения
- не проверялось на текущем выезде
- требует уточнения

---

## 11. Группировка замечаний

Группировка по смыслу, не по порядку фото.

Базовые секции:
- опорные узлы
- сварные соединения
- антикоррозионная защита
- основание и водоотведение
- крепления и узлы покрытия
- связи / укосины / элементы жёсткости
- бетонные и железобетонные конструкции
- кровля / фасад / ограждающие конструкции
- прочие замечания

Профили добавляют секции: металлокаркас / бетон / кровля / фасад / инженерные сети / электрика / отделка / каркасный дом / нагрузки.

---

## 12. Логика работы с предыдущими актами

Если предыдущие акты есть:
- не начинать с нуля
- добавить раздел "Связь с предыдущими актами"
- показать что было → что проверено → что устранено → что не устранено → что новое
- если акт не распарсить → "предыдущий акт найден, содержание требует ручной сверки"

---

## 13. Правила противоречий

| Ситуация | Формулировка |
|---|---|
| Владелец говорит одно, фото показывает другое | задать уточнение |
| Подрядчик говорит "устранено", фото не подтверждает | "устранение по представленным фото не подтверждено" |
| Предыдущий акт имел дефект, фото нет | "не проверялось на текущем выезде" |
| Только слова заказчика | "по информации заказчика, требуется проверка" |
| Только слова подрядчика | "по информации подрядчика, требуется фотофиксация результата и проверка на объекте" |

---

## 14. Нормы

- Если найден документ + пункт → цитировать документ + пункт
- Если найден только документ → цитировать документ
- Если ничего не найдено → "норма не подтверждена"
- Никогда не изобретать пункты нормативов
- Упоминание нормы в старом акте = SOURCE_MENTIONED_CLAUSE, не автоматически подтверждено

---

## 15. Форматы вывода

- PDF (приоритетный финальный формат)
- DOCX / Word (если владелец запросил для клиента)
- Google Docs (если владелец запросил)
- Telegram текстовый разбор (для оперативного ответа)
- XLSX (реестр замечаний)
- Приложение к акту

Нет жёсткой привязки к PDF-only. Нет жёсткой привязки к металлокаркасу.

---

## 16. Клиентская vs служебная папка

**Клиентская папка (client_facing=True) может содержать:**
- оригинальные фото объекта
- финальный PDF акт
- чистый акт + приложения
- материалы, одобренные владельцем для клиента

**Клиентская папка НЕ должна содержать:**
- черновики
- рабочий DOCX (если владелец не запросил явно Word для клиента)
- JSON / манифесты / логи / debug / temp / кэш
- файлы с task_id
- реестр объектов
- runtime-файлы
- smoke/test файлы
- пути /root/...

---

## 17. Vision guard

`EXTERNAL_PHOTO_ANALYSIS_ALLOWED = False` по умолчанию.

Без явного разрешения владельца — никакой отправки фото наружу.

Если Vision заблокирован:
- использовать голос/текст владельца
- использовать предыдущие акты
- использовать документы
- использовать имена/метаданные файлов
- чётко указать в результате: "Автоматический визуальный анализ фото не выполнялся, так как Vision заблокирован. Выводы основаны на предыдущих актах, пояснениях владельца и доступных именах/метаданных файлов"

---

## 18. Язык вывода

Все клиентские и владельческие тексты — только **русский**:
- Telegram ответы
- акты / разборы / документы
- имена файлов (результирующих)
- таблицы замечаний
- рекомендации / последствия / выводы

English — только внутри кода (функции, классы, enum, маркеры).

---

## 19. Правило одного вопроса

Если данных не хватает — задать один конкретный вопрос.
Никогда не спрашивать "что строим?" если объект уже был активен.
Никогда не спрашивать несколько вопросов сразу без крайней необходимости.

---

## 20. Статусы задачи

CODE_CLOSED_ITEMS (topic_5 контур, верифицировано):
- topic_5 photo/file buffer ✅
- active folder set/get ✅
- Drive folder batch trigger ✅ (P6H4TW_BATCH_TRIGGER_V1)
- flush to process_technadzor ✅
- external Vision guarded (EXTERNAL_PHOTO_ANALYSIS_ALLOWED=False) ✅
- STT hallucination guard ✅
- folder discovery LIVE CLOSED (task 5276 DONE) ✅

VISION_BLOCKED_OWNER_DECISION_REQUIRED:
- OpenRouter Google → 403
- Ни одна Vision модель не включена без явного разрешения владельца
- Решение о включении Vision остаётся за владельцем

---

## 21. Контракт вывода документов

Полный контракт: `docs/TECHNADZOR/TOPIC5_DOCUMENT_OUTPUT_CONTRACT.md`

Ключевые правила:

```
CLIENT_DOCUMENT_DELIVERED = задача выполнена
LOCAL_DRAFT_CREATED        ≠ задача выполнена
DOCX_DRAFT_CREATED         ≠ задача выполнена

Рабочий путь (2026-05-05): TEXT_REPORT → Telegram text
PDF/DOCX: NOT_IMPLEMENTED (reportlab / python-docx не установлены, local-check подтверждён)
```

Именование файлов:
```
Черновик_акта_<объект>_<дата>.docx
Акт_осмотра_<объект>_<дата>.pdf
Реестр_замечаний_<объект>_<дата>.xlsx
```

Drive placement:
- client_facing папка → финальный PDF; DOCX только по явной команде владельца
- Путь /root/... → никогда не отправлять клиенту

---

## 22. Реестр unified_context файлов

Полный индекс: `docs/TECHNADZOR/unified_context/TOPIC5_UNIFIED_TECHNADZOR_CONTEXT.md`

Ключевые файлы:
- OBJECT_CONTEXT_INDEX.json — индекс объектов
- OWNER_ACT_STYLE_PROFILE.md — стиль актов (из 3 реальных Drive актов)
- OWNER_ACTS_INDEX.json — индекс всех актов (5 актов, все DRIVE_VERIFIED)
- NORMATIVE_CONTEXT_INDEX.json — нормативная база
- TNZ_MSK_SKILL_BINDING.json — @tnz_msk как скилл оформления (не нормативная база)
