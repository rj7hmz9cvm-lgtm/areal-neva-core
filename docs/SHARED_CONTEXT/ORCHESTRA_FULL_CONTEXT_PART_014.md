# ORCHESTRA_FULL_CONTEXT_PART_014
generated_at_utc: 2026-05-08T23:35:02.205581+00:00
git_sha_before_commit: 876e5d24f1c376e211a9e6002c5002abbf642daf
part: 14/17


====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/NORMATIVE_ENGINE_SHARED_CONTEXT.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 9011f21b0b01ee1ac4003c659691ab5e1f7cae2cdde825f9eb706352568f28a0
====================================================================================================
{
  "version": "NORMATIVE_ENGINE_SHARED_CONTEXT_V2",
  "updated_at": "2026-05-05",
  "status": "VERIFIED_FROM_CODE",
  "git_head": "73b4946",
  "sources": {
    "normative_engine": "core/normative_engine.py",
    "norms_map": "core/project_engine.py NORMS_MAP lines 39-45"
  },

  "normative_engine_committed": {
    "total_entries": 59,
    "blocks": {
      "NORMATIVE_ENGINE_SAFE_V1": 8,
      "P6H_NORMATIVE_INDEX_EXTRA_V1": 10,
      "P6H5_NORMATIVE_FULL_EXPAND_V1": 36,
      "P6H6_LOADS_V1": 5
    },
    "smoke_test": "11/11 PASS at commit 73b4946",
    "shared_topic5_topic210": [
      "СП 70.13330.2012",
      "СП 63.13330.2018",
      "СП 20.13330.2016/2017",
      "СП 16.13330.2017",
      "СП 17.13330.2017"
    ],
    "primarily_topic5": [
      "СП 28.13330.2017",
      "ГОСТ 23118-2019",
      "СП 48.13330.2019",
      "СП 13-102-2003",
      "ГОСТ 31937-2024",
      "ГОСТ Р ИСО 17637-2014",
      "СП 22.13330.2016"
    ],
    "primarily_topic210": [
      "ГОСТ 21.101-2020",
      "ГОСТ 21.501-2018",
      "СП 71.13330.2017"
    ],
    "p6h5_topic210_ov_vk_eom": [
      "СП 60.13330.2020", "СП 73.13330.2016", "СП 61.13330.2012",
      "СП 30.13330.2020", "СП 31.13330.2021", "СП 32.13330.2018",
      "ПУЭ (7-е изд.)", "СП 256.1325800.2016", "ГОСТ Р 50571-4-41-2022"
    ],
    "p6h6_loads_sp20": [
      "снеговые нагрузки",
      "ветровые нагрузки",
      "постоянные нагрузки",
      "временные нагрузки",
      "сочетания нагрузок"
    ]
  },

  "norms_map_committed": {
    "кж": ["СП 63.13330.2018", "ГОСТ 34028-2016", "СП 20.13330.2017"],
    "км": ["СП 16.13330.2017", "ГОСТ 27772-2015", "СП 20.13330.2017"],
    "ар": ["СП 118.13330.2022", "ГОСТ 21.501-2018"],
    "ов": ["СП 60.13330.2020", "ГОСТ 30494-2011"],
    "вк": ["СП 30.13330.2020", "СП 31.13330.2021"],
    "эом": ["СП 256.1325800.2016", "ПУЭ-7"],
    "overlap_with_normative_engine": ["СП 63.13330.2018", "СП 20.13330.2017", "СП 16.13330.2017", "ГОСТ 21.501-2018"],
    "only_in_norms_map": ["ГОСТ 34028-2016", "ГОСТ 30494-2011", "СП 118.13330.2022", "ПУЭ-7", "ГОСТ 27772-2015"]
  },

  "loads_calculation": {
    "normative_binding_status": "CLOSED",
    "normative_binding_note": "P6H6 committed — все виды нагрузок покрыты ключевыми словами СП 20",
    "calc_logic_status": "PARTIAL_CALC",
    "calc_logic_note": "calc_loads() покрывает только снег/ветер по районам",
    "committed": {
      "calc_loads_fn": "core/project_engine.py:68",
      "covers": ["snow_kPa by region (1-8)", "wind_kPa by region (1-8)"],
      "norm_reference": "СП 20.13330.2017"
    },
    "not_implemented": [
      "постоянные нагрузки (собственный вес)",
      "временные нагрузки (полезная нагрузка по назначению помещения)",
      "сочетания нагрузок",
      "проверка предельных состояний"
    ]
  },

  "open_items": {
    "calc_logic": "PARTIAL_CALC — автоматический расчёт постоянных/временных/сочетаний не реализован",
    "topic5_live_test": "NOT_DONE — фото/буфер/разбор через реальный Telegram не пройден",
    "document_output_live": "NOT_DONE — PDF/DOCX/Drive link/fallback не подтверждены живым тестом",
    "topic210_live": "NOT_DONE — ОВ/ВК/ЭОМ/КЖ/КМ через реальные файлы не прогнаны",
    "vision": "BLOCKED — EXTERNAL_PHOTO_ANALYSIS_ALLOWED=False, owner decision required",
    "missing_in_norms_map": ["сс", "гп", "пз", "см", "тх"]
  }
}

====================================================================================================
END_FILE: docs/TECHNADZOR/NORMATIVE_ENGINE_SHARED_CONTEXT.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/NORMATIVE_ENGINE_SHARED_CONTEXT.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: fbe4915ea50f48d499b50d5e242969fe82790379f9887fbfe5a08c6aff1cb1cd
====================================================================================================
# NORMATIVE ENGINE — SHARED CONTEXT (topic_5 + topic_210)

version: NORMATIVE_ENGINE_SHARED_CONTEXT_V2
updated_at: 2026-05-05
status: VERIFIED_FROM_CODE
source_1: core/normative_engine.py — git HEAD 73b4946 (P6H5+P6H6 committed)
source_2: core/project_engine.py NORMS_MAP — git HEAD 73b4946
note: Только нормы из committed кода. Не изобретать новые нормы. Не добавлять пункты.

---

## 1. Два нормативных контура

```
normative_engine.py — SHARED
  keyword-based search_norms_sync(text)
  Используется: topic_5 (технадзор) + topic_210 (проектирование)
  Committed: 59 записей (HEAD 73b4946)
    — base 8 (NORMATIVE_ENGINE_SAFE_V1)
    — P6H extension 10 (P6H_NORMATIVE_INDEX_EXTRA_V1)
    — P6H5 expansion 36 (P6H5_NORMATIVE_FULL_EXPAND_V1) ← теперь COMMITTED
    — P6H6 loads 5 (P6H6_LOADS_V1) ← теперь COMMITTED

project_engine.py NORMS_MAP — topic_210 ONLY
  section-based NORMS_MAP[section] → list of norm_ids
  Используется: topic_210 — АР / КЖ / КМ / ОВ / ВК / ЭОМ
  Committed: 6 разделов (HEAD 2deb7c8)
```

---

## 2. normative_engine.py — committed 18 записей

### 2.1 Общие (topic_5 + topic_210)

| norm_id | Раздел | topic_5 | topic_210 |
|---|---|---|---|
| СП 70.13330.2012 | Несущие и ограждающие конструкции | акты: бетон, трещины | КЖ: несущая способность |
| СП 63.13330.2018 | Бетонные и железобетонные конструкции | акты: ЖБ дефекты | КЖ: армирование, защитный слой |
| СП 20.13330.2016/2017 | Нагрузки и воздействия | акты: основания, перекрытия | КЖ/КМ: расчётные нагрузки |
| СП 16.13330.2017 | Стальные конструкции | акты: сварка, связи, узлы | КМ: металлокаркас |
| СП 17.13330.2017 | Кровли | акты: протечки, примыкания | АР: кровельные решения |

### 2.2 Преимущественно topic_5

| norm_id | Раздел |
|---|---|
| СП 28.13330.2017 | Защита строительных конструкций от коррозии |
| ГОСТ 23118-2019 | Конструкции стальные строительные. Общие ТУ |
| СП 48.13330.2019 | Организация строительства (стройконтроль) |
| СП 13-102-2003 | Обследование несущих строительных конструкций |
| ГОСТ 31937-2024 | Обследование и мониторинг технического состояния |
| ГОСТ Р ИСО 17637-2014 | Визуальный контроль сварных соединений |
| СП 22.13330.2016 | Основания зданий и сооружений |
| СП 70.13330.2012 *(2-я запись)* | Опорные узлы металлоконструкций |
| СП 16.13330.2017 *(2-я запись)* | Пространственные связи |
| СП 20.13330.2016 *(2-я запись)* | Нагрузки — перекрытия |

### 2.3 Преимущественно topic_210

| norm_id | Раздел |
|---|---|
| ГОСТ 21.101-2020 | Основные требования к проектной и рабочей документации |
| ГОСТ 21.501-2018 | Рабочая документация АР и КР |
| СП 71.13330.2017 | Изоляционные и отделочные покрытия |

---

## 3. project_engine.py NORMS_MAP — topic_210, 6 разделов

Источник: `core/project_engine.py`, строки 39–45, HEAD 2deb7c8.

```python
NORMS_MAP = {
    "кж":  ["СП 63.13330.2018", "ГОСТ 34028-2016", "СП 20.13330.2017"],
    "км":  ["СП 16.13330.2017", "ГОСТ 27772-2015", "СП 20.13330.2017"],
    "ар":  ["СП 118.13330.2022", "ГОСТ 21.501-2018"],
    "ов":  ["СП 60.13330.2020", "ГОСТ 30494-2011"],
    "вк":  ["СП 30.13330.2020", "СП 31.13330.2021"],
    "эом": ["СП 256.1325800.2016", "ПУЭ-7"],
}
```

NORMS_MAP частично пересекается с normative_engine.py (committed):
- СП 63.13330.2018 — в NORMS_MAP["кж"] и в normative_engine base
- СП 20.13330.2017 — в NORMS_MAP["кж","км"] и в normative_engine ("СП 20.13330.2016/2017")
- СП 16.13330.2017 — в NORMS_MAP["км"] и в normative_engine base
- ГОСТ 21.501-2018 — в NORMS_MAP["ар"] и в normative_engine base

Только в NORMS_MAP (не в normative_engine committed):
- ГОСТ 34028-2016 — прокат арматурный (КЖ)
- ГОСТ 30494-2011 — параметры микроклимата (ОВ)
- СП 118.13330.2022 — общественные здания (АР)
- ПУЭ-7 — электроустановки (ЭОМ)
- ГОСТ 27772-2015 — прокат стальной (КМ)

---

## 4. Расчёт нагрузок и несущей способности — PARTIAL

### Что есть в committed коде

`core/project_engine.py` — `calc_loads(region)`, строки 68–73:
```python
{"snow_kPa": ..., "wind_kPa": ..., "region": region, "note": "СП 20.13330.2017 — район N"}
```

Закрыто только:
- снеговая нагрузка по 8 районам (SNOW_LOADS)
- ветровая нагрузка по 8 районам (WIND_LOADS)
- нормативная привязка: СП 20.13330.2017

Нормативные документы в committed движке (оба контура):
- СП 20.13330.2016/2017 — нагрузки и воздействия (normative_engine)
- СП 16.13330.2017 — стальные конструкции (normative_engine + NORMS_MAP КМ)
- СП 63.13330.2018 — ЖБ конструкции (normative_engine + NORMS_MAP КЖ)
- СП 22.13330.2016 — основания (normative_engine)

### Что НЕ закрыто

```
FULL расчёт несущей способности: НЕ ЗАКРЫТ

Отсутствует в committed коде:
- постоянные нагрузки (собственный вес конструкций)
- временные нагрузки (полезная нагрузка на перекрытия по назначению)
- особые нагрузки (сейсмика, взрыв, обрушение)
- крановые нагрузки
- нагрузки на фундаменты от надземных конструкций
- расчёт сечений элементов по нормативным требованиям
- проверка предельных состояний (1-я группа, 2-я группа)
```

### Что необходимо добавить (в оба направления)

**topic_5 (ТЕХНАДЗОР):**
Нормы ветровых и снеговых нагрузок нужны при проверке несущих конструкций в актах осмотра:
- установить соответствие пролётов, прогонов, связей расчётным нагрузкам
- фиксировать нагрузочный класс объекта при документировании дефектов несущих элементов

**topic_210 (ПРОЕКТИРОВАНИЕ):**
Для полноценного разбора КЖ/КМ разделов проектной документации:
- нормативная привязка по видам нагрузок (не только снег/ветер)
- расчётные сочетания нагрузок
- классы ответственности и коэффициенты надёжности

Статус: `PARTIAL — базовая нормативная привязка закрыта; полный расчётный контур не реализован`

---

## 5. P6H5 + P6H6 — COMMITTED (73b4946)

`core/normative_engine.py` — оба блока зафиксированы в коммите 73b4946.
Статус: `COMMITTED`

**P6H5_NORMATIVE_FULL_EXPAND_V1** (36 норм):
- ИД / журналы: РД-11-02-2006, РД-11-05-2007, СП 11-110-99
- Бетонные смеси: ГОСТ 7473-2010, ГОСТ 18105-2018, ГОСТ 26633-2015
- Газобетон / кладка: ГОСТ 31360-2007, СП 339.1325800.2017, СП 15.13330.2020
- КМ: СП 294.1325800.2017, ГОСТ 27772-2015, СП 260.1325800.2016
- ГКЛ: СП 163.1325800.2014, ГОСТ 6266-2018
- Фасады / окна: СП 50.13330.2012, СП 293.1325800.2017, ГОСТ 30674-99
- ОВ: СП 60.13330.2020, СП 73.13330.2016, СП 61.13330.2012
- ВК: СП 30.13330.2020, СП 31.13330.2021, СП 32.13330.2018
- ЭОМ: ПУЭ (7-е изд.), СП 256.1325800.2016, ГОСТ Р 50571-4-41-2022
- Пожарная безопасность: 123-ФЗ, СП 1.13130.2020, СП 2.13130.2020
- Охрана труда: СНиП 12-03-2001, СНиП 12-04-2002, Приказ №336н/№883н, ГОСТ 12.0.004-2015, ГОСТ 12.4.011-89, СП 49.13330.2010

**P6H6_LOADS_V1** (5 записей — СП 20.13330.2017):
снеговые, ветровые, постоянные, временные, сочетания нагрузок

P6H5 частично дублирует NORMS_MAP (ОВ, ВК, ЭОМ) — оба источника теперь committed.
smoke 11/11 PASS при commit.

---

## 6. Правила использования нормативного контура

```
1. topic_5 (ТЕХНАДЗОР):
   - Использовать search_norms_sync() из normative_engine.py
   - NORMS_MAP не применяется
   - Если норма не найдена → "норма не подтверждена"

2. topic_210 (ПРОЕКТИРОВАНИЕ):
   - Раздел: detect_section() → NORMS_MAP[section]
   - normative_engine дополнительно для текстового поиска
   - Нельзя смешивать нормы разных разделов

3. Общий запрет:
   - Не изобретать новые СП/ГОСТ
   - Не придумывать пункты нормативов
   - Confidence=PARTIAL у всех committed записей

4. Нагрузки:
   - Нормативная привязка по всем видам нагрузок: ЗАКРЫТА (P6H6, СП 20)
   - calc_loads() в project_engine: только снег/ветер по районам
   - Автоматический расчёт постоянных/временных/сочетаний нагрузок: НЕ РЕАЛИЗОВАН
   - Статус: PARTIAL_CALC — нормы есть, расчётная логика отсутствует
```

---

## 7. Верификация с каноном

Canon `TECHNADZOR_DOMAIN_LOGIC_CANON.md`, §22:
```
СП 16, СП 70, СП 28, ГОСТ 23118, СП 48, СП 13-102, ГОСТ 31937, СП 63, СП 22
```
Все 9 норм присутствуют в committed normative_engine.py. ✓

Canon `01_SYSTEM_LOGIC_FULL.md`:
```
topic_210: КЖ / КМ / КМД / АР / ОВ / ВК / ЭОМ / СС / ГП / ПЗ / СМ / ТХ
```
- ОВ / ВК / ЭОМ — committed нормы в project_engine.py NORMS_MAP. ✓
- СС / ГП / ПЗ / СМ / ТХ — в NORMS_MAP отсутствуют. NOT_PRESENT.

====================================================================================================
END_FILE: docs/TECHNADZOR/NORMATIVE_ENGINE_SHARED_CONTEXT.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/TOPIC5_DOCUMENT_OUTPUT_CONTRACT.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 557b97c8c932bb7c5228ff7049330426530dca78340f4cddab5435c59e290633
====================================================================================================
{
  "version": "TOPIC5_DOCUMENT_OUTPUT_CONTRACT_V1",
  "updated_at": "2026-05-05",
  "status": "CODE_AUDIT_DRAFT_NOT_LIVE_VERIFIED",
  "source": "technadzor_engine.py audit + owner addendum 2026-05-05",

  "output_types": [
    {"type": "TEXT_REPORT", "status": "ACTIVE", "note": "рабочий путь"},
    {"type": "PDF_ACT", "status": "NOT_IMPLEMENTED", "note": "local-check 2026-05-05: ModuleNotFoundError reportlab"},
    {"type": "DOCX", "status": "NOT_IMPLEMENTED", "note": "local-check 2026-05-05: ModuleNotFoundError python-docx"},
    {"type": "XLSX", "status": "UNVERIFIED"},
    {"type": "GOOGLE_DOC", "status": "FUTURE_OPTIONAL_NOT_VERIFIED"},
    {"type": "TELEGRAM_ONLY", "status": "ACTIVE", "note": "нет файла, только текст"}
  ],

  "document_statuses": [
    "TELEGRAM_TEXT_REPORT_SENT",
    "LOCAL_DRAFT_CREATED",
    "DOCX_DRAFT_CREATED",
    "PDF_GENERATION_NOT_IMPLEMENTED",
    "DRIVE_UPLOAD_PENDING",
    "DRIVE_UPLOAD_DONE",
    "DRIVE_UPLOAD_FAILED",
    "TELEGRAM_LINK_SENT",
    "FALLBACK_SENT",
    "CLIENT_DOCUMENT_DELIVERED"
  ],

  "done_rule": {
    "done": "CLIENT_DOCUMENT_DELIVERED",
    "not_done": [
      "LOCAL_DRAFT_CREATED",
      "DOCX_DRAFT_CREATED",
      "DRIVE_UPLOAD_DONE without TELEGRAM_LINK_SENT"
    ],
    "conditions": [
      "Document exists (PDF / DOCX / TEXT)",
      "Uploaded to Drive (PDF/DOCX) OR text sent to Telegram (TEXT)",
      "Owner/client received link or text in Telegram"
    ]
  },

  "forbidden_patterns": [
    "calling LOCAL_DRAFT_CREATED done",
    "calling DOCX_DRAFT_CREATED done without Drive upload and Telegram link",
    "claiming PDF generated without reportlab local-check",
    "Drive upload without Telegram confirmation",
    "sending /root/... path to client",
    "placing DOCX in client_facing without explicit owner command"
  ],

  "delivery_chain": {
    "entry": "task_worker._handle_in_progress",
    "process": "process_technadzor (wrapper chain, 8 definitions)",
    "build": "_p6h_build_* (text / docx / pdf)",
    "drive_upload_fn": "technadzor_drive_index.upload_client_pdf_to_folder",
    "drive_upload_fn_line": 383,
    "drive_upload_fn_verified": true,
    "fallback": "FALLBACK_SENT + error status in ObjectCard"
  },

  "packages_local_check_20260505": {
    "reportlab": "NOT_INSTALLED",
    "python_docx": "NOT_INSTALLED",
    "dejavu_fonts": "PRESENT"
  },

  "file_naming": {
    "docx_draft": "Черновик_акта_<объект>_<дата>.docx",
    "pdf_final": "Акт_осмотра_<объект>_<дата>.pdf",
    "xlsx_registry": "Реестр_замечаний_<объект>_<дата>.xlsx",
    "date_format": "YYYYMMDD",
    "object_name": "Russian name from ObjectCard"
  },

  "drive_placement": {
    "client_facing_folder": "финальный PDF; DOCX только по явной команде владельца",
    "topic5_system_folder": "служебные файлы, черновики, JSON манифесты",
    "forbidden": "путь /root/... клиенту"
  }
}

====================================================================================================
END_FILE: docs/TECHNADZOR/TOPIC5_DOCUMENT_OUTPUT_CONTRACT.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/TOPIC5_DOCUMENT_OUTPUT_CONTRACT.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: edff2931c8896b02651a0175466d81c5659f3ebc155ccfa5f9a60b6ddc44480d
====================================================================================================
# TOPIC5 DOCUMENT OUTPUT CONTRACT

version: TOPIC5_DOCUMENT_OUTPUT_CONTRACT_V1
updated_at: 2026-05-05
status: CODE_AUDIT_DRAFT_NOT_LIVE_VERIFIED
source: technadzor_engine.py audit + owner addendum 2026-05-05

---

## 1. Типы выходных документов

| Тип | Константа | Статус |
|---|---|---|
| Текстовый разбор | TEXT_REPORT | ACTIVE — рабочий путь |
| PDF акт | PDF_ACT | NOT_IMPLEMENTED — local-check 2026-05-05: ModuleNotFoundError |
| DOCX черновик | DOCX | NOT_IMPLEMENTED — local-check 2026-05-05: ModuleNotFoundError |
| XLSX реестр | XLSX | UNVERIFIED |
| Google Doc | GOOGLE_DOC | FUTURE_OPTIONAL_NOT_VERIFIED |
| Только Telegram | TELEGRAM_ONLY | ACTIVE — нет файла, только текст |

---

## 2. Статусы документа

```
TELEGRAM_TEXT_REPORT_SENT   — текстовый разбор отправлен в Telegram
LOCAL_DRAFT_CREATED         — черновик создан локально (НЕ ДОСТАВЛЕН клиенту)
DOCX_DRAFT_CREATED          — DOCX создан локально (НЕ ДОСТАВЛЕН клиенту)
PDF_GENERATION_NOT_IMPLEMENTED — reportlab не установлен: ModuleNotFoundError
DRIVE_UPLOAD_PENDING        — ожидает загрузки на Drive
DRIVE_UPLOAD_DONE           — загружен на Drive
DRIVE_UPLOAD_FAILED         — ошибка загрузки на Drive
TELEGRAM_LINK_SENT          — ссылка на Drive отправлена в Telegram
FALLBACK_SENT               — текстовый fallback вместо файла
CLIENT_DOCUMENT_DELIVERED   — документ доставлен: Drive + Telegram ссылка получена
```

---

## 3. Правило DONE

```
CLIENT_DOCUMENT_DELIVERED = задача выполнена
LOCAL_DRAFT_CREATED        ≠ задача выполнена
DOCX_DRAFT_CREATED         ≠ задача выполнена
DRIVE_UPLOAD_DONE без Telegram ссылки ≠ задача выполнена

Закрыто только когда:
  1. Документ существует (PDF / DOCX / TEXT)
  2. Загружен на Drive (PDF/DOCX) ИЛИ текст отправлен в Telegram (TEXT)
  3. Владелец/клиент получил ссылку или текст в Telegram
```

---

## 4. Запрещённые паттерны

- Называть LOCAL_DRAFT_CREATED «готово» или «документ создан»
- Называть DOCX_DRAFT_CREATED «акт готов» без Drive-загрузки и Telegram-ссылки
- Сообщать «PDF сгенерирован» без фактической проверки reportlab
- Загружать на Drive без подтверждения ссылки в Telegram
- Отправлять клиенту путь вида /root/...
- Помещать DOCX в client_facing папку без явной команды владельца

---

## 5. Цепочка доставки

```
Telegram (владелец)
  → task_worker._handle_in_progress
  → process_technadzor (wrapper chain, 8 definitions)
  → VisitPackage собран
  → _p6h_build_* (text / docx / pdf builder)
  → technadzor_drive_index.upload_client_pdf_to_folder (line 383, verified)
  → Telegram ответ со ссылкой
```

Если любой шаг падает → FALLBACK_SENT + статус ошибки в ObjectCard.

---

## 6. Статус пакетов (local-check 2026-05-05)

```
reportlab:    ModuleNotFoundError — не установлен
python-docx:  ModuleNotFoundError — не установлен
DejaVu fonts: присутствуют (/usr/share/fonts/truetype/dejavu/)

Код _p6h_build_pdf_act / _p6h_build_docx_act существует в technadzor_engine.py
но упадёт на import при вызове.

Текущий рабочий путь: TEXT_REPORT → Telegram text
```

---

## 7. Именование файлов

```
Черновик DOCX:  Черновик_акта_<объект>_<дата>.docx
Финальный PDF:  Акт_осмотра_<объект>_<дата>.pdf
Реестр XLSX:    Реестр_замечаний_<объект>_<дата>.xlsx
```

Дата формат: YYYYMMDD.
Объект: имя из ObjectCard на русском для клиентских файлов.

---

## 8. Drive placement

```
client_facing=True папка → финальный PDF акт
                           DOCX — только по явной команде владельца
topic_5 system folder    → служебные файлы, черновики, JSON манифесты
Путь /root/...           → НИКОГДА не отправлять клиенту
```

====================================================================================================
END_FILE: docs/TECHNADZOR/TOPIC5_DOCUMENT_OUTPUT_CONTRACT.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/TOPIC5_RUNTIME_USAGE_RULES.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 4093ded0ac87b42cc50beb5578095a4ae85e9bc4ec5ec7f5ddb5ead599618fa3
====================================================================================================
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

====================================================================================================
END_FILE: docs/TECHNADZOR/TOPIC5_RUNTIME_USAGE_RULES.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e3bf441983629d033eb5d781360ea364c905fd229134d0ec3f2ed943a9080fa4
====================================================================================================
{
  "version": "TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL_V1",
  "updated_at": "2026-05-05",
  "status": "FINAL_DOCUMENTED",
  "topic": "topic_5",
  "topic_name": "ТЕХНАДЗОР",
  "main_principle": "Drive folder = work container. Telegram = owner explanation + control. Files = materials (not tasks). 61 photos = one visit = one act.",
  "task_components": [
    "OwnerInstruction",
    "InputFiles",
    "ActiveFolder",
    "ObjectContext",
    "PreviousActs"
  ],
  "material_paths": {
    "PATH_A": "Drive folder → owner Telegram explanation → ActiveTechnadzorFolder → VisitPackage → one result",
    "PATH_B": "Telegram files + voice → VisitBuffer → owner explanation → VisitPackage → one result"
  },
  "task_lifecycle": [
    "owner creates/selects Drive folder",
    "Оркестр opens ActiveTechnadzorFolder",
    "owner uploads materials + explains via voice/text",
    "Оркестр collects VisitMaterials (COLLECTING_VISIT_MATERIALS)",
    "owner commands 'сделай разбор/акт/документ'",
    "Оркестр assembles VisitPackage",
    "ObjectContext loaded (history, previous acts)",
    "Norms matched via normative_engine",
    "One result output: text report / PDF / DOCX / XLSX",
    "ObjectCard updated",
    "Drive upload: final document only to topic folder"
  ],
  "drive_facts": {
    "технадзор_root_id": "1s2y5l2mJFTb7P90XVokErXYVzmoH-VtD",
    "технадзор_root_url": "https://drive.google.com/drive/folders/1s2y5l2mJFTb7P90XVokErXYVzmoH-VtD",
    "topic_5_folder_id": "1yWIJdSrypH3BbIozCz-OAw1R6hmnMRHK",
    "technadzor_system_id": "1vKQM0Z2qBmiKtgeyx95JaNEQAp5mJLOm",
    "known_user_folders": [
      "Сусанино. Технадзор",
      "КП _Новичково_ Александр",
      "Выезд ангар Киевское ш",
      "Документы личные работа НЕ ОРКЕСТР",
      "тест надзор"
    ]
  },
  "system_folder_blacklist": [
    "TECHNADZOR",
    "ТЕХНАДЗОР",
    "topic_5",
    "_system",
    "_tmp",
    "_archive",
    "_drafts",
    "_templates",
    "_manifests"
  ],
  "active_folder_state_file": "data/technadzor/active_folder_{chat_id}_{topic_id}.json",
  "visit_buffer_file": "data/technadzor/buf_{chat_id}_{topic_id}.json",
  "current_active_folder": {
    "folder_id": "1Jfw1VKgOi2GgdlimK-HCBw7mx9a_FbKG",
    "folder_name": "тест надзор",
    "status": "TEST_ACTIVE_FOLDER",
    "verified_task": "rowid_5276_DONE"
  },
  "remark_statuses": [
    "новое замечание",
    "подтверждено по фото",
    "частично видно по фото",
    "устранено",
    "устранено частично",
    "не устранено",
    "требует доведения",
    "не проверялось на текущем выезде",
    "требует уточнения"
  ],
  "base_sections": [
    "опорные узлы",
    "сварные соединения",
    "антикоррозионная защита",
    "основание и водоотведение",
    "крепления и узлы покрытия",
    "связи / укосины / элементы жёсткости",
    "бетонные и железобетонные конструкции",
    "кровля / фасад / ограждающие конструкции",
    "прочие замечания"
  ],
  "output_formats": ["PDF", "DOCX", "GoogleDocs", "TelegramText", "XLSX", "Appendix"],
  "language_rules": {
    "client_and_owner_output": "Russian only",
    "code_internal": "English"
  },
  "vision_status": {
    "EXTERNAL_PHOTO_ANALYSIS_ALLOWED": false,
    "status": "VISION_BLOCKED_OWNER_DECISION_REQUIRED",
    "reason": "OpenRouter Google 403 + no other Vision model authorized",
    "fallback": "owner voice/text + previous acts + filenames/metadata"
  },
  "code_status": {
    "visit_buffer": "VERIFIED",
    "active_folder": "VERIFIED",
    "folder_discovery": "LIVE_CLOSED_task5276",
    "drive_batch_trigger": "INSTALLED_P6H4TW_BATCH_TRIGGER_V1",
    "stt_hallucination_guard": "INSTALLED",
    "vision_guard": "INSTALLED_EXTERNAL_PHOTO_ANALYSIS_ALLOWED_FALSE"
  }
}

====================================================================================================
END_FILE: docs/TECHNADZOR/TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 59b575c0ccca40bac5fb41a2907fc7d2801f4032826805668f594db34284d49c
====================================================================================================
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

====================================================================================================
END_FILE: docs/TECHNADZOR/TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL_REPORT.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 3fa5aa20e7d214e993ed3cdd8e92f54c81539f60605513169901b9ace0eb726f
====================================================================================================
# TOPIC5 TECHNADZOR — ИТОГОВЫЙ ОТЧЁТ

version: TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL_REPORT_V1
date: 2026-05-05
status: FINAL

---

## 1. Что сделано

### Документы контекста (unified_context/)
- KIEVSKOE_95_OBJECT_CONTEXT.md — DRIVE_VERIFIED (3 акта прочитаны с Drive)
- NOVICHKOVO_OBJECT_CONTEXT.md — DRIVE_VERIFIED (акт Щеглово прочитан, source ref добавлен)
- SUSANINO_OBJECT_CONTEXT.md — DRIVE_VERIFIED (неподтверждённое авторство фото убрано → UNKNOWN)
- OWNER_ACT_STYLE_PROFILE.md — DRIVE_VERIFIED (профиль стиля из 3 реальных актов)
- OBJECT_CONTEXT_INDEX.json — VERIFIED (все folder_id подтверждены Drive API)
- OWNER_ACTS_INDEX.json — DRIVE_VERIFIED (5 актов, все прочитаны)
- NORMATIVE_CONTEXT_INDEX.json — VERIFIED_FROM_ACTS
- TNZ_MSK_SKILL_BINDING.json — VERIFIED
- CHAT_EXPORT_TECHNADZOR_BINDING.json — VERIFIED
- OWNER_ENGINEERING_LOAD_VALIDATION_PATTERN.md/.json — SOURCE_FROM_OWNER_CONVERSATION
- TOPIC5_UNIFIED_TECHNADZOR_CONTEXT.md/.json — VERIFIED

### Системные документы
- TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.md — CODE_AUDIT_VERIFIED (20 секций)
- TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.json — CODE_AUDIT_VERIFIED
- TOPIC5_DOCUMENT_OUTPUT_CONTRACT.md/.json — CODE_AUDIT_DRAFT_NOT_LIVE_VERIFIED
- TOPIC5_RUNTIME_USAGE_RULES.md — CODE_AUDIT_VERIFIED

---

## 2. Исправленные ошибки

| Файл | Ошибка | Исправление |
|---|---|---|
| SUSANINO_OBJECT_CONTEXT.md | Выдуманное авторство фото (Фото Илья + Фото от заказчиков) | Заменено на UNKNOWN / NOT_VERIFIED |
| NOVICHKOVO_OBJECT_CONTEXT.md | Нет ссылки на источник | Добавлен source_file (Drive id: 1mqE0G-U5mB889IQMlh5e02UFFSkoADW9) |
| OWNER_ACT_STYLE_PROFILE.md | Предыдущая версия создана до чтения Drive актов | Полностью переписан из 3 реальных актов |

---

## 3. Верифицированные факты системы

### Wrapper chains
- `process_technadzor`: 8 определений в technadzor_engine.py, `_p6h4tw_v1_wrapped=True`
- `_handle_in_progress`: 14 определений в task_worker.py
- `_handle_new`: 4 определения в task_worker.py

### Drive
- ТЕХНАДЗОР root: `1s2y5l2mJFTb7P90XVokErXYVzmoH-VtD`
- topic_5 system: `1yWIJdSrypH3BbIozCz-OAw1R6hmnMRHK`
- Active test folder: `тест надзор` (`1Jfw1VKgOi2GgdlimK-HCBw7mx9a_FbKG`) — task 5276 DONE

### Пакеты (local-check 2026-05-05)
- reportlab: NOT INSTALLED (ModuleNotFoundError)
- python-docx: NOT INSTALLED (ModuleNotFoundError)
- DejaVu fonts: PRESENT

### Vision
- `EXTERNAL_PHOTO_ANALYSIS_ALLOWED = False`
- OpenRouter Google: 403

### Search
- SearchMonolithV2 → perplexity/sonar via OpenRouter
- OPENROUTER_API_KEY подтверждён в .env

---

## 4. Открытые вопросы

| Вопрос | Статус |
|---|---|
| Vision для 3-го выезда Киевское (04.05.2026) | OWNER_DECISION_REQUIRED |
| reportlab/python-docx — установить? | OWNER_DECISION_REQUIRED |
| @tnz_msk карты (66 на review) — одобрить? | OWNER_DECISION_REQUIRED |
| ГОСТ 30971 — добавить в normative_engine? | OWNER_DECISION_REQUIRED |

---

## 5. Что НЕ делалось

- Runtime patches: нет
- Drive mutations: нет
- normative_engine.py: не staged, не committed
- Запрещённые файлы: не редактировались

====================================================================================================
END_FILE: docs/TECHNADZOR/TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL_REPORT.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/source_skills/tnz_msk/LINKED_DOCUMENTS_INDEX.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 5f685fff1da97501adca5e14d8c99bddcd01f846778f99d1485eae20baaaa6e4
====================================================================================================
{
  "schema": "TNZ_MSK_LINKED_DOCUMENTS_INDEX_V1",
  "source": "@tnz_msk",
  "scanned_at": "2026-05-05T07:49:28.093641+00:00",
  "downloaded_count": 6,
  "downloaded_paths": [
    "/root/.areal-neva-core/data/memory_files/TEHNADZOR/source_skills/tnz_msk/downloaded_docs/ГОСТ Р 72509-2026.pdf",
    "/root/.areal-neva-core/data/memory_files/TEHNADZOR/source_skills/tnz_msk/downloaded_docs/0001202512310019.pdf",
    "/root/.areal-neva-core/data/memory_files/TEHNADZOR/source_skills/tnz_msk/downloaded_docs/Чек-лист по окнам.pdf",
    "/root/.areal-neva-core/data/memory_files/TEHNADZOR/source_skills/tnz_msk/downloaded_docs/checklist_priemka_white_box.pdf",
    "/root/.areal-neva-core/data/memory_files/TEHNADZOR/source_skills/tnz_msk/downloaded_docs/cheklist_priemka_kvartiry_v_betone_kirillitsa.pdf",
    "/root/.areal-neva-core/data/memory_files/TEHNADZOR/source_skills/tnz_msk/downloaded_docs/ВСН 53-86 Утратил силу.pdf"
  ],
  "linked_urls": [
    "https://donstroy.moscow/owners/keys/",
    "https://ds-fest.ru/",
    "https://framerfest.ru/",
    "https://markets.house/",
    "https://max.ru/tnz_msk",
    "https://poly.cam/",
    "https://t.me/+26x9OiOEawphMDdi",
    "https://t.me/KarabanovPV",
    "https://t.me/developers_policy/8029",
    "https://t.me/glebgrinfeld/668",
    "https://t.me/neural_ntw",
    "https://t.me/neural_ntw/175",
    "https://t.me/parket_expert",
    "https://t.me/tnz_msk",
    "https://t.me/tnz_msk/116",
    "https://t.me/tnz_msk/2899",
    "https://t.me/tnz_msk/3290",
    "https://t.me/tnz_msk/3391",
    "https://t.me/tnz_msk/3436",
    "https://t.me/tnz_msk/3606",
    "https://t.me/tnz_msk/3635",
    "https://t.me/tnz_msk/3654",
    "https://t.me/tnz_msk/3785",
    "https://t.me/tnz_msk/4",
    "https://t.me/tnz_msk?livestream",
    "https://telegra.ph/Svetlyachkam-na-zavist-06-14",
    "https://telegra.ph/Svetlyachkam-na-zavist-part-2-08-05",
    "https://telegra.ph/U-nas-promerzanie--D-12-19",
    "https://vk.com/clip-216130923_456240215",
    "https://www.gosuslugi.ru/snet/6895ec2c06836073af0da543",
    "https://www.youtube.com/watch?v=7kZHpvqMqRM",
    "https://www.youtube.com/watch?v=A4sMjYyN7FM",
    "https://www.youtube.com/watch?v=HGQU1ZdylT0",
    "https://www.youtube.com/watch?v=LWE3TCS8njs",
    "https://www.youtube.com/watch?v=Vt7w9kjG460",
    "https://www.youtube.com/watch?v=i4yUN8YANJs",
    "https://www.youtube.com/watch?v=vhXxJp1MS6E",
    "https://yandex.ru/adv/edu/materials/registraciya-blogerov-ot-10000-podpischikov?ysclid=mdfrqderhy804916339",
    "https://yandex.ru/maps/?um=constructor%3Af35f7f3f5f880a78b46c473eca916075f563f6eaf036006f7519a3f3f3751e89&source=constructorLink",
    "https://yandex.ru/video/touch/preview/17284700974743076036"
  ],
  "document_messages": [
    {
      "message_id": 4059,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4059",
      "file_name": "IMG_5198.MOV"
    },
    {
      "message_id": 4058,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4058",
      "file_name": "IMG_5200.MOV"
    },
    {
      "message_id": 4036,
      "date": "2026-04-24T12:33:58+00:00",
      "source_ref": "https://t.me/tnz_msk/4036",
      "file_name": "IMG_4848.MOV"
    },
    {
      "message_id": 4023,
      "date": "2026-04-20T09:48:36+00:00",
      "source_ref": "https://t.me/tnz_msk/4023",
      "file_name": "IMG_4666.MOV"
    },
    {
      "message_id": 4021,
      "date": "2026-04-16T10:53:00+00:00",
      "source_ref": "https://t.me/tnz_msk/4021",
      "file_name": "IMG_4381.MOV"
    },
    {
      "message_id": 4005,
      "date": "2026-04-11T23:16:43+00:00",
      "source_ref": "https://t.me/tnz_msk/4005",
      "file_name": "IMG_5079.MP4"
    },
    {
      "message_id": 4004,
      "date": "2026-04-11T23:16:43+00:00",
      "source_ref": "https://t.me/tnz_msk/4004",
      "file_name": "IMG_5078.MOV"
    },
    {
      "message_id": 3998,
      "date": "2026-04-09T08:40:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3998",
      "file_name": "IMG_4172.MP4"
    },
    {
      "message_id": 3992,
      "date": "2026-04-05T10:04:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3992",
      "file_name": "IMG_1448.mp4"
    },
    {
      "message_id": 3988,
      "date": "2026-04-02T20:51:08+00:00",
      "source_ref": "https://t.me/tnz_msk/3988",
      "file_name": "IMG_1642.MP4"
    },
    {
      "message_id": 3978,
      "date": "2026-04-01T09:16:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3978",
      "file_name": "IMG_3415.MOV"
    },
    {
      "message_id": 3977,
      "date": "2026-04-01T09:16:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3977",
      "file_name": "IMG_3421.MOV"
    },
    {
      "message_id": 3971,
      "date": "2026-04-01T07:36:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3971",
      "file_name": "IMG_3860.MP4"
    },
    {
      "message_id": 3965,
      "date": "2026-03-31T21:05:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3965",
      "file_name": "IMG_1570.MP4"
    },
    {
      "message_id": 3943,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3943",
      "file_name": "IMG_3518.MOV"
    },
    {
      "message_id": 3929,
      "date": "2026-03-10T19:44:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3929",
      "file_name": "video_2026-03-10_22-40-41.mp4"
    },
    {
      "message_id": 3903,
      "date": "2026-02-21T10:11:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3903",
      "file_name": "IMG_2455.MP4"
    },
    {
      "message_id": 3901,
      "date": "2026-02-20T16:46:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3901",
      "file_name": "ГОСТ Р 72509-2026.pdf"
    },
    {
      "message_id": 3895,
      "date": "2026-02-18T04:05:04+00:00",
      "source_ref": "https://t.me/tnz_msk/3895",
      "file_name": "IMG_2370.MP4"
    },
    {
      "message_id": 3893,
      "date": "2026-02-17T15:11:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3893",
      "file_name": "IMG_2365.MP4"
    },
    {
      "message_id": 3892,
      "date": "2026-02-17T12:38:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3892",
      "file_name": "IMG_2355.MOV"
    },
    {
      "message_id": 3891,
      "date": "2026-02-17T04:57:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3891",
      "file_name": "Бот.mp4"
    },
    {
      "message_id": 3890,
      "date": "2026-02-13T13:26:36+00:00",
      "source_ref": "https://t.me/tnz_msk/3890",
      "file_name": "IMG_2239.MP4"
    },
    {
      "message_id": 3883,
      "date": "2026-02-08T15:44:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3883",
      "file_name": "IMG_2135.MP4"
    },
    {
      "message_id": 3865,
      "date": "2026-02-05T14:25:43+00:00",
      "source_ref": "https://t.me/tnz_msk/3865",
      "file_name": "IMG_2034.MP4"
    },
    {
      "message_id": 3864,
      "date": "2026-02-05T14:25:43+00:00",
      "source_ref": "https://t.me/tnz_msk/3864",
      "file_name": "IMG_2035.MP4"
    },
    {
      "message_id": 3844,
      "date": "2026-01-23T15:48:47+00:00",
      "source_ref": "https://t.me/tnz_msk/3844",
      "file_name": "IMG_1542.MP4"
    },
    {
      "message_id": 3840,
      "date": "2026-01-22T12:52:31+00:00",
      "source_ref": "https://t.me/tnz_msk/3840",
      "file_name": "IMG_1471.MP4"
    },
    {
      "message_id": 3836,
      "date": "2026-01-22T09:56:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3836",
      "file_name": "IMG_1454.MP4"
    },
    {
      "message_id": 3833,
      "date": "2026-01-20T07:49:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3833",
      "file_name": "1113 (1)(1).mp4"
    },
    {
      "message_id": 3817,
      "date": "2026-01-14T10:10:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3817",
      "file_name": "IMG_1195.MOV"
    },
    {
      "message_id": 3807,
      "date": "2026-01-05T09:30:54+00:00",
      "source_ref": "https://t.me/tnz_msk/3807",
      "file_name": "0001202512310019.pdf"
    },
    {
      "message_id": 3784,
      "date": "2025-12-23T15:12:48+00:00",
      "source_ref": "https://t.me/tnz_msk/3784",
      "file_name": "IMG_0527.MP4"
    },
    {
      "message_id": 3751,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3751",
      "file_name": "IMG_9952.MP4"
    },
    {
      "message_id": 3749,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3749",
      "file_name": "IMG_9949.MP4"
    },
    {
      "message_id": 3748,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3748",
      "file_name": "IMG_9948.MP4"
    },
    {
      "message_id": 3747,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3747",
      "file_name": "IMG_9944.MP4"
    },
    {
      "message_id": 3746,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3746",
      "file_name": "IMG_9947.MP4"
    },
    {
      "message_id": 3743,
      "date": "2025-12-07T08:10:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3743",
      "file_name": "IMG_9831.MP4"
    },
    {
      "message_id": 3740,
      "date": "2025-12-06T11:16:23+00:00",
      "source_ref": "https://t.me/tnz_msk/3740",
      "file_name": "IMG_9862.MP4"
    },
    {
      "message_id": 3735,
      "date": "2025-12-04T08:41:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3735",
      "file_name": "IMG_9750.MP4"
    },
    {
      "message_id": 3730,
      "date": "2025-11-29T15:29:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3730",
      "file_name": "IMG_9618.MOV"
    },
    {
      "message_id": 3729,
      "date": "2025-11-29T15:29:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3729",
      "file_name": "IMG_9617.MOV"
    },
    {
      "message_id": 3728,
      "date": "2025-11-29T15:29:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3728",
      "file_name": "IMG_9615.MOV"
    },
    {
      "message_id": 3714,
      "date": "2025-11-28T12:14:17+00:00",
      "source_ref": "https://t.me/tnz_msk/3714",
      "file_name": "IMG_9573.MP4"
    },
    {
      "message_id": 3710,
      "date": "2025-11-26T12:22:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3710",
      "file_name": "Чек-лист по окнам.pdf"
    },
    {
      "message_id": 3694,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3694",
      "file_name": "IMG_9373.MP4"
    },
    {
      "message_id": 3693,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3693",
      "file_name": "IMG_9374.MP4"
    },
    {
      "message_id": 3691,
      "date": "2025-11-24T16:58:33+00:00",
      "source_ref": "https://t.me/tnz_msk/3691",
      "file_name": "record.ogg"
    },
    {
      "message_id": 3690,
      "date": "2025-11-24T16:58:33+00:00",
      "source_ref": "https://t.me/tnz_msk/3690",
      "file_name": "record.mp4"
    },
    {
      "message_id": 3675,
      "date": "2025-11-20T16:47:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3675",
      "file_name": "IMG_9159.MP4"
    },
    {
      "message_id": 3657,
      "date": "2025-11-17T15:33:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3657",
      "file_name": "IMG_8898.MOV"
    },
    {
      "message_id": 3656,
      "date": "2025-11-17T15:33:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3656",
      "file_name": "IMG_8899.MOV"
    },
    {
      "message_id": 3630,
      "date": "2025-11-07T14:37:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3630",
      "file_name": "19700121_1234_690d225fb42481919d3aa09139f5e817.mp4"
    },
    {
      "message_id": 3629,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3629",
      "file_name": "IMG_8340.MOV"
    },
    {
      "message_id": 3628,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3628",
      "file_name": "IMG_8360.MOV"
    },
    {
      "message_id": 3625,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3625",
      "file_name": "IMG_8351.MOV"
    },
    {
      "message_id": 3623,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3623",
      "file_name": "IMG_8329.MOV"
    },
    {
      "message_id": 3622,
      "date": "2025-11-06T08:10:44+00:00",
      "source_ref": "https://t.me/tnz_msk/3622",
      "file_name": "IMG_8345.MOV"
    },
    {
      "message_id": 3621,
      "date": "2025-11-05T18:41:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3621",
      "file_name": "video_2025-11-05_21-40-44.mp4"
    },
    {
      "message_id": 3604,
      "date": "2025-11-03T09:45:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3604",
      "file_name": "IMG_8161.MP4"
    },
    {
      "message_id": 3589,
      "date": "2025-10-28T11:59:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3589",
      "file_name": "IMG_8035.MOV"
    },
    {
      "message_id": 3588,
      "date": "2025-10-28T11:59:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3588",
      "file_name": "IMG_8010.MOV"
    },
    {
      "message_id": 3587,
      "date": "2025-10-28T11:59:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3587",
      "file_name": "IMG_8037.MP4"
    },
    {
      "message_id": 3586,
      "date": "2025-10-28T11:59:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3586",
      "file_name": "IMG_8038.MP4"
    },
    {
      "message_id": 3585,
      "date": "2025-10-27T16:28:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3585",
      "file_name": "IMG_7990.MOV"
    },
    {
      "message_id": 3581,
      "date": "2025-10-26T04:45:04+00:00",
      "source_ref": "https://t.me/tnz_msk/3581",
      "file_name": "sora_video_1761427768738.mp4"
    },
    {
      "message_id": 3580,
      "date": "2025-10-25T04:16:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3580",
      "file_name": "ScreenRecorderProject96.mp4"
    },
    {
      "message_id": 3579,
      "date": "2025-10-24T16:00:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3579",
      "file_name": "IMG_7820.MP4"
    },
    {
      "message_id": 3576,
      "date": "2025-10-24T15:58:30+00:00",
      "source_ref": "https://t.me/tnz_msk/3576",
      "file_name": "IMG_7820.MP4"
    },
    {
      "message_id": 3571,
      "date": "2025-10-24T03:39:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3571",
      "file_name": "checklist_priemka_white_box.pdf"
    },
    {
      "message_id": 3563,
      "date": "2025-10-22T13:51:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3563",
      "file_name": "IMG_7621.MOV"
    },
    {
      "message_id": 3562,
      "date": "2025-10-22T13:51:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3562",
      "file_name": "IMG_7620.MOV"
    },
    {
      "message_id": 3561,
      "date": "2025-10-22T13:51:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3561",
      "file_name": "IMG_7646.MP4"
    },
    {
      "message_id": 3559,
      "date": "2025-10-22T04:06:58+00:00",
      "source_ref": "https://t.me/tnz_msk/3559",
      "file_name": "cheklist_priemka_kvartiry_v_betone_kirillitsa.pdf"
    },
    {
      "message_id": 3547,
      "date": "2025-10-20T16:58:36+00:00",
      "source_ref": "https://t.me/tnz_msk/3547",
      "file_name": "IMG_7494.MP4"
    },
    {
      "message_id": 3539,
      "date": "2025-10-20T10:15:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3539",
      "file_name": "IMG_7437.MOV"
    },
    {
      "message_id": 3537,
      "date": "2025-10-18T09:48:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3537",
      "file_name": "IMG_7318.MP4"
    },
    {
      "message_id": 3536,
      "date": "2025-10-17T14:52:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3536",
      "file_name": "IMG_7341.MP4"
    },
    {
      "message_id": 3521,
      "date": "2025-10-15T14:50:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3521",
      "file_name": "IMG_7247.MOV"
    },
    {
      "message_id": 3520,
      "date": "2025-10-15T14:50:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3520",
      "file_name": "IMG_7248.MOV"
    },
    {
      "message_id": 3519,
      "date": "2025-10-15T14:50:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3519",
      "file_name": "IMG_7246.MP4"
    },
    {
      "message_id": 3492,
      "date": "2025-10-08T13:35:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3492",
      "file_name": "IMG_4490.MOV"
    },
    {
      "message_id": 3491,
      "date": "2025-10-08T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3491",
      "file_name": "watermark-removed-20251008_0035_01k709amyafkka83bp7j708xxn.mp4"
    },
    {
      "message_id": 3487,
      "date": "2025-10-06T04:28:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3487",
      "file_name": "video_2025-10-06_00-15-54.mp4"
    },
    {
      "message_id": 3486,
      "date": "2025-10-05T17:29:36+00:00",
      "source_ref": "https://t.me/tnz_msk/3486",
      "file_name": "IMG_6893.MP4"
    },
    {
      "message_id": 3485,
      "date": "2025-10-05T14:08:47+00:00",
      "source_ref": "https://t.me/tnz_msk/3485",
      "file_name": "IMG_6882.MP4"
    },
    {
      "message_id": 3484,
      "date": "2025-10-05T09:13:04+00:00",
      "source_ref": "https://t.me/tnz_msk/3484",
      "file_name": "20251005_1211_01k6st6fgee749rtfghjefsra1.mp4"
    },
    {
      "message_id": 3483,
      "date": "2025-10-03T14:20:47+00:00",
      "source_ref": "https://t.me/tnz_msk/3483",
      "file_name": "IMG_6817.MP4"
    },
    {
      "message_id": 3482,
      "date": "2025-10-01T20:27:52+00:00",
      "source_ref": "https://t.me/tnz_msk/3482",
      "file_name": "20251001_2327_01k6gq89y0fpkamh6ycr0txqhs.mp4"
    },
    {
      "message_id": 3481,
      "date": "2025-10-01T19:47:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3481",
      "file_name": "20251001_2246_01k6gmxkw2f4fvn46zhbm80y56.mp4"
    },
    {
      "message_id": 3479,
      "date": "2025-09-30T21:58:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3479",
      "file_name": "IMG_7556.MP4"
    },
    {
      "message_id": 3475,
      "date": "2025-09-29T04:33:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3475",
      "file_name": "Новый проект.mp4"
    },
    {
      "message_id": 3471,
      "date": "2025-09-24T16:24:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3471",
      "file_name": "IMG_6579.MP4"
    },
    {
      "message_id": 3466,
      "date": "2025-09-19T09:23:17+00:00",
      "source_ref": "https://t.me/tnz_msk/3466",
      "file_name": "IMG_6370.MP4"
    },
    {
      "message_id": 3442,
      "date": "2025-09-13T08:53:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3442",
      "file_name": "IMG_6006.MP4"
    },
    {
      "message_id": 3441,
      "date": "2025-09-13T08:53:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3441",
      "file_name": "IMG_6005.MP4"
    },
    {
      "message_id": 3425,
      "date": "2025-08-29T09:02:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3425",
      "file_name": "IMG_5435.MOV"
    },
    {
      "message_id": 3424,
      "date": "2025-08-28T10:14:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3424",
      "file_name": "IMG_5368.MP4"
    },
    {
      "message_id": 3422,
      "date": "2025-08-27T13:19:15+00:00",
      "source_ref": "https://t.me/tnz_msk/3422",
      "file_name": "IMG_5337.MP4"
    },
    {
      "message_id": 3417,
      "date": "2025-08-27T13:19:15+00:00",
      "source_ref": "https://t.me/tnz_msk/3417",
      "file_name": "IMG_5329.MOV"
    },
    {
      "message_id": 3416,
      "date": "2025-08-27T09:01:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3416",
      "file_name": "IMG_5302.MP4"
    },
    {
      "message_id": 3401,
      "date": "2025-08-22T18:56:35+00:00",
      "source_ref": "https://t.me/tnz_msk/3401",
      "file_name": "IMG_5811.MP4"
    },
    {
      "message_id": 3398,
      "date": "2025-08-21T11:51:07+00:00",
      "source_ref": "https://t.me/tnz_msk/3398",
      "file_name": "IMG_4981.MOV"
    },
    {
      "message_id": 3387,
      "date": "2025-08-14T15:59:15+00:00",
      "source_ref": "https://t.me/tnz_msk/3387",
      "file_name": "IMG_4764.MP4"
    },
    {
      "message_id": 3377,
      "date": "2025-08-13T07:50:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3377",
      "file_name": "IMG_4715.MOV"
    },
    {
      "message_id": 3375,
      "date": "2025-08-12T20:21:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3375",
      "file_name": "IMG_6243.MOV"
    },
    {
      "message_id": 3367,
      "date": "2025-08-10T20:18:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3367",
      "file_name": "IMG_4661.MP4"
    },
    {
      "message_id": 3356,
      "date": "2025-08-08T12:49:54+00:00",
      "source_ref": "https://t.me/tnz_msk/3356",
      "file_name": "IMG_4469.MOV"
    },
    {
      "message_id": 3353,
      "date": "2025-08-07T20:00:39+00:00",
      "source_ref": "https://t.me/tnz_msk/3353",
      "file_name": "video_2025-08-07_21-50-56.mp4"
    },
    {
      "message_id": 3352,
      "date": "2025-08-07T17:35:18+00:00",
      "source_ref": "https://t.me/tnz_msk/3352",
      "file_name": "IMG_4386.MP4"
    },
    {
      "message_id": 3344,
      "date": "2025-08-07T17:35:18+00:00",
      "source_ref": "https://t.me/tnz_msk/3344",
      "file_name": "IMG_4365.MOV"
    },
    {
      "message_id": 3334,
      "date": "2025-08-07T06:49:54+00:00",
      "source_ref": "https://t.me/tnz_msk/3334",
      "file_name": "IMG_4386.MP4"
    },
    {
      "message_id": 3316,
      "date": "2025-08-03T12:35:23+00:00",
      "source_ref": "https://t.me/tnz_msk/3316",
      "file_name": "IMG_0125.MP4"
    },
    {
      "message_id": 3315,
      "date": "2025-08-02T12:55:18+00:00",
      "source_ref": "https://t.me/tnz_msk/3315",
      "file_name": "IMG_4218.MOV"
    },
    {
      "message_id": 3313,
      "date": "2025-08-02T12:55:18+00:00",
      "source_ref": "https://t.me/tnz_msk/3313",
      "file_name": "IMG_4213.MOV"
    },
    {
      "message_id": 3312,
      "date": "2025-08-02T12:55:18+00:00",
      "source_ref": "https://t.me/tnz_msk/3312",
      "file_name": "IMG_4210.MOV"
    },
    {
      "message_id": 3311,
      "date": "2025-08-02T12:55:18+00:00",
      "source_ref": "https://t.me/tnz_msk/3311",
      "file_name": "IMG_4209.MOV"
    },
    {
      "message_id": 3310,
      "date": "2025-08-02T12:55:18+00:00",
      "source_ref": "https://t.me/tnz_msk/3310",
      "file_name": "IMG_4205.MOV"
    },
    {
      "message_id": 3309,
      "date": "2025-08-01T19:48:54+00:00",
      "source_ref": "https://t.me/tnz_msk/3309",
      "file_name": "video_2025-08-01_22-47-43.mp4"
    },
    {
      "message_id": 3302,
      "date": "2025-08-01T08:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3302",
      "file_name": "polycam.mp4"
    },
    {
      "message_id": 3291,
      "date": "2025-07-26T21:10:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3291",
      "file_name": "IMG_2715.MP4"
    },
    {
      "message_id": 3282,
      "date": "2025-07-25T10:53:59+00:00",
      "source_ref": "https://t.me/tnz_msk/3282",
      "file_name": "IMG_3851.MP4"
    },
    {
      "message_id": 3271,
      "date": "2025-07-24T09:23:23+00:00",
      "source_ref": "https://t.me/tnz_msk/3271",
      "file_name": "IMG_3811.MOV"
    },
    {
      "message_id": 3258,
      "date": "2025-07-18T08:25:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3258",
      "file_name": "IMG_3419.MOV"
    },
    {
      "message_id": 3242,
      "date": "2025-07-15T07:43:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3242",
      "file_name": "IMG_3158.MP4"
    },
    {
      "message_id": 3231,
      "date": "2025-07-11T14:20:47+00:00",
      "source_ref": "https://t.me/tnz_msk/3231",
      "file_name": "IMG_2811.MP4"
    },
    {
      "message_id": 3227,
      "date": "2025-07-10T11:31:02+00:00",
      "source_ref": "https://t.me/tnz_msk/3227",
      "file_name": "IMG_2695.MOV"
    },
    {
      "message_id": 3202,
      "date": "2025-07-05T15:56:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3202",
      "file_name": "IMG_2463.MP4"
    },
    {
      "message_id": 3201,
      "date": "2025-07-05T15:56:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3201",
      "file_name": "IMG_2465.MP4"
    },
    {
      "message_id": 3200,
      "date": "2025-07-05T15:56:36+00:00",
      "source_ref": "https://t.me/tnz_msk/3200",
      "file_name": "IMG_2464.MP4"
    },
    {
      "message_id": 3199,
      "date": "2025-07-04T18:24:36+00:00",
      "source_ref": "https://t.me/tnz_msk/3199",
      "file_name": "IMG_2400.MP4"
    },
    {
      "message_id": 3198,
      "date": "2025-07-04T14:26:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3198",
      "file_name": "IMG_2406.MOV"
    },
    {
      "message_id": 3186,
      "date": "2025-07-02T15:22:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3186",
      "file_name": "IMG_2264.MOV"
    },
    {
      "message_id": 3184,
      "date": "2025-07-01T20:39:15+00:00",
      "source_ref": "https://t.me/tnz_msk/3184",
      "file_name": "Видео WhatsApp 2025-06-30 в 15.51.31_6dd6737c.mp4"
    },
    {
      "message_id": 3183,
      "date": "2025-06-30T10:53:23+00:00",
      "source_ref": "https://t.me/tnz_msk/3183",
      "file_name": "IMG_9935.MOV"
    },
    {
      "message_id": 3182,
      "date": "2025-06-30T10:00:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3182",
      "file_name": "IMG_1576.MP4"
    },
    {
      "message_id": 3180,
      "date": "2025-06-30T08:13:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3180",
      "file_name": "IMG_2110.MP4"
    },
    {
      "message_id": 3179,
      "date": "2025-06-30T07:16:23+00:00",
      "source_ref": "https://t.me/tnz_msk/3179",
      "file_name": "IMG_2107.MP4"
    },
    {
      "message_id": 3166,
      "date": "2025-06-27T14:03:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3166",
      "file_name": "IMG_2048.MP4"
    },
    {
      "message_id": 3136,
      "date": "2025-06-19T14:31:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3136",
      "file_name": "IMG_1460.MOV"
    },
    {
      "message_id": 3134,
      "date": "2025-06-19T10:15:20+00:00",
      "source_ref": "https://t.me/tnz_msk/3134",
      "file_name": "IMG_1598.MP4"
    },
    {
      "message_id": 3130,
      "date": "2025-06-19T10:15:20+00:00",
      "source_ref": "https://t.me/tnz_msk/3130",
      "file_name": "IMG_1440.MOV"
    },
    {
      "message_id": 3128,
      "date": "2025-06-18T08:03:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3128",
      "file_name": "IMG_1565.MP4"
    },
    {
      "message_id": 3117,
      "date": "2025-06-14T15:35:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3117",
      "file_name": "IMG_1406.MP4"
    },
    {
      "message_id": 3112,
      "date": "2025-06-10T08:20:34+00:00",
      "source_ref": "https://t.me/tnz_msk/3112",
      "file_name": "IMG_1191.MP4"
    },
    {
      "message_id": 3111,
      "date": "2025-06-08T07:42:30+00:00",
      "source_ref": "https://t.me/tnz_msk/3111",
      "file_name": "IMG_1130.MP4"
    },
    {
      "message_id": 3086,
      "date": "2025-05-30T11:10:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3086",
      "file_name": "AIIN.mp4"
    },
    {
      "message_id": 3084,
      "date": "2025-05-29T20:46:59+00:00",
      "source_ref": "https://t.me/tnz_msk/3084",
      "file_name": "record.ogg"
    },
    {
      "message_id": 3083,
      "date": "2025-05-29T16:17:46+00:00",
      "source_ref": "https://t.me/tnz_msk/3083",
      "file_name": "record.mp4"
    },
    {
      "message_id": 3077,
      "date": "2025-05-28T04:09:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3077",
      "file_name": "ВСН 53-86 Утратил силу.pdf"
    },
    {
      "message_id": 3072,
      "date": "2025-05-25T12:09:34+00:00",
      "source_ref": "https://t.me/tnz_msk/3072",
      "file_name": "IMG_0537.MOV"
    },
    {
      "message_id": 3070,
      "date": "2025-05-25T12:09:34+00:00",
      "source_ref": "https://t.me/tnz_msk/3070",
      "file_name": "IMG_0547.MOV"
    },
    {
      "message_id": 3067,
      "date": "2025-05-25T12:09:34+00:00",
      "source_ref": "https://t.me/tnz_msk/3067",
      "file_name": "IMG_0546.MOV"
    },
    {
      "message_id": 3063,
      "date": "2025-05-24T05:31:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3063",
      "file_name": "IMG_0477.MP4"
    },
    {
      "message_id": 3062,
      "date": "2025-05-24T05:31:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3062",
      "file_name": "IMG_0476.MP4"
    },
    {
      "message_id": 3050,
      "date": "2025-05-21T16:29:46+00:00",
      "source_ref": "https://t.me/tnz_msk/3050",
      "file_name": "IMG_3938.MOV"
    },
    {
      "message_id": 3037,
      "date": "2025-05-19T08:44:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3037",
      "file_name": "IMG_0223.MP4"
    },
    {
      "message_id": 3034,
      "date": "2025-05-14T17:17:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3034",
      "file_name": "video_2025-05-15_00-14-14.mp4"
    },
    {
      "message_id": 3033,
      "date": "2025-05-14T10:51:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3033",
      "file_name": "IMG_9931.MOV"
    },
    {
      "message_id": 3031,
      "date": "2025-05-13T07:07:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3031",
      "file_name": "IMG_9914.MOV"
    }
  ]
}
====================================================================================================
END_FILE: docs/TECHNADZOR/source_skills/tnz_msk/LINKED_DOCUMENTS_INDEX.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/source_skills/tnz_msk/SOURCE_INDEX.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 64adb6f42d95261884ffea8950affac4b4b134750a417e397449e804b004ca28
====================================================================================================
{
  "schema": "TNZ_MSK_SOURCE_INDEX_V1",
  "source": "@tnz_msk",
  "scanned_at": "2026-05-05T07:49:28.093445+00:00",
  "total_fetched": 1000,
  "records_count": 971,
  "records": [
    {
      "message_id": 4068,
      "date": "2026-05-04T11:17:38+00:00",
      "source_ref": "https://t.me/tnz_msk/4068",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4067,
      "date": "2026-05-04T04:50:05+00:00",
      "source_ref": "https://t.me/tnz_msk/4067",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4066,
      "date": "2026-05-02T13:49:44+00:00",
      "source_ref": "https://t.me/tnz_msk/4066",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4065,
      "date": "2026-05-02T13:49:43+00:00",
      "source_ref": "https://t.me/tnz_msk/4065",
      "has_links": true,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4064,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4064",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4063,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4063",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4062,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4062",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4061,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4061",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4060,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4060",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4059,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4059",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 4058,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4058",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 4057,
      "date": "2026-04-30T05:34:01+00:00",
      "source_ref": "https://t.me/tnz_msk/4057",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4056,
      "date": "2026-04-27T07:26:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4056",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 4055,
      "date": "2026-04-25T13:20:45+00:00",
      "source_ref": "https://t.me/tnz_msk/4055",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4054,
      "date": "2026-04-25T13:20:45+00:00",
      "source_ref": "https://t.me/tnz_msk/4054",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4053,
      "date": "2026-04-25T13:20:45+00:00",
      "source_ref": "https://t.me/tnz_msk/4053",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4052,
      "date": "2026-04-25T13:20:45+00:00",
      "source_ref": "https://t.me/tnz_msk/4052",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4051,
      "date": "2026-04-25T13:20:45+00:00",
      "source_ref": "https://t.me/tnz_msk/4051",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4050,
      "date": "2026-04-25T13:20:45+00:00",
      "source_ref": "https://t.me/tnz_msk/4050",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4049,
      "date": "2026-04-25T13:20:44+00:00",
      "source_ref": "https://t.me/tnz_msk/4049",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4048,
      "date": "2026-04-25T13:20:44+00:00",
      "source_ref": "https://t.me/tnz_msk/4048",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4047,
      "date": "2026-04-25T11:57:46+00:00",
      "source_ref": "https://t.me/tnz_msk/4047",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4046,
      "date": "2026-04-25T11:57:46+00:00",
      "source_ref": "https://t.me/tnz_msk/4046",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4045,
      "date": "2026-04-25T11:57:46+00:00",
      "source_ref": "https://t.me/tnz_msk/4045",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4044,
      "date": "2026-04-25T11:57:46+00:00",
      "source_ref": "https://t.me/tnz_msk/4044",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4043,
      "date": "2026-04-25T11:57:46+00:00",
      "source_ref": "https://t.me/tnz_msk/4043",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4042,
      "date": "2026-04-24T17:53:44+00:00",
      "source_ref": "https://t.me/tnz_msk/4042",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4041,
      "date": "2026-04-24T17:53:44+00:00",
      "source_ref": "https://t.me/tnz_msk/4041",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4040,
      "date": "2026-04-24T16:17:01+00:00",
      "source_ref": "https://t.me/tnz_msk/4040",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4039,
      "date": "2026-04-24T16:17:01+00:00",
      "source_ref": "https://t.me/tnz_msk/4039",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4038,
      "date": "2026-04-24T12:33:58+00:00",
      "source_ref": "https://t.me/tnz_msk/4038",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4037,
      "date": "2026-04-24T12:33:58+00:00",
      "source_ref": "https://t.me/tnz_msk/4037",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4036,
      "date": "2026-04-24T12:33:58+00:00",
      "source_ref": "https://t.me/tnz_msk/4036",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 4035,
      "date": "2026-04-24T12:33:58+00:00",
      "source_ref": "https://t.me/tnz_msk/4035",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4034,
      "date": "2026-04-24T12:33:58+00:00",
      "source_ref": "https://t.me/tnz_msk/4034",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4033,
      "date": "2026-04-23T17:28:13+00:00",
      "source_ref": "https://t.me/tnz_msk/4033",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4032,
      "date": "2026-04-23T16:07:07+00:00",
      "source_ref": "https://t.me/tnz_msk/4032",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4030,
      "date": "2026-04-23T05:47:53+00:00",
      "source_ref": "https://t.me/tnz_msk/4030",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4029,
      "date": "2026-04-23T05:47:53+00:00",
      "source_ref": "https://t.me/tnz_msk/4029",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4028,
      "date": "2026-04-23T05:47:53+00:00",
      "source_ref": "https://t.me/tnz_msk/4028",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4027,
      "date": "2026-04-21T15:15:31+00:00",
      "source_ref": "https://t.me/tnz_msk/4027",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4026,
      "date": "2026-04-21T15:15:31+00:00",
      "source_ref": "https://t.me/tnz_msk/4026",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4025,
      "date": "2026-04-21T15:15:31+00:00",
      "source_ref": "https://t.me/tnz_msk/4025",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4024,
      "date": "2026-04-21T15:15:31+00:00",
      "source_ref": "https://t.me/tnz_msk/4024",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4023,
      "date": "2026-04-20T09:48:36+00:00",
      "source_ref": "https://t.me/tnz_msk/4023",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 4022,
      "date": "2026-04-16T13:39:50+00:00",
      "source_ref": "https://t.me/tnz_msk/4022",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4021,
      "date": "2026-04-16T10:53:00+00:00",
      "source_ref": "https://t.me/tnz_msk/4021",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 4020,
      "date": "2026-04-16T10:53:00+00:00",
      "source_ref": "https://t.me/tnz_msk/4020",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4019,
      "date": "2026-04-16T10:53:00+00:00",
      "source_ref": "https://t.me/tnz_msk/4019",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4018,
      "date": "2026-04-15T16:44:14+00:00",
      "source_ref": "https://t.me/tnz_msk/4018",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4017,
      "date": "2026-04-15T16:44:14+00:00",
      "source_ref": "https://t.me/tnz_msk/4017",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4016,
      "date": "2026-04-14T17:08:33+00:00",
      "source_ref": "https://t.me/tnz_msk/4016",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4015,
      "date": "2026-04-14T17:08:33+00:00",
      "source_ref": "https://t.me/tnz_msk/4015",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4014,
      "date": "2026-04-14T17:08:33+00:00",
      "source_ref": "https://t.me/tnz_msk/4014",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4013,
      "date": "2026-04-14T17:08:33+00:00",
      "source_ref": "https://t.me/tnz_msk/4013",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4012,
      "date": "2026-04-14T17:08:33+00:00",
      "source_ref": "https://t.me/tnz_msk/4012",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4011,
      "date": "2026-04-14T17:08:33+00:00",
      "source_ref": "https://t.me/tnz_msk/4011",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4010,
      "date": "2026-04-14T16:59:12+00:00",
      "source_ref": "https://t.me/tnz_msk/4010",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 4009,
      "date": "2026-04-13T14:38:49+00:00",
      "source_ref": "https://t.me/tnz_msk/4009",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4008,
      "date": "2026-04-13T14:38:49+00:00",
      "source_ref": "https://t.me/tnz_msk/4008",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4007,
      "date": "2026-04-13T14:38:49+00:00",
      "source_ref": "https://t.me/tnz_msk/4007",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4006,
      "date": "2026-04-13T14:38:49+00:00",
      "source_ref": "https://t.me/tnz_msk/4006",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4005,
      "date": "2026-04-11T23:16:43+00:00",
      "source_ref": "https://t.me/tnz_msk/4005",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 4004,
      "date": "2026-04-11T23:16:43+00:00",
      "source_ref": "https://t.me/tnz_msk/4004",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 4003,
      "date": "2026-04-11T23:16:43+00:00",
      "source_ref": "https://t.me/tnz_msk/4003",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 4002,
      "date": "2026-04-10T16:32:18+00:00",
      "source_ref": "https://t.me/tnz_msk/4002",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4001,
      "date": "2026-04-10T12:44:04+00:00",
      "source_ref": "https://t.me/tnz_msk/4001",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 4000,
      "date": "2026-04-10T11:25:38+00:00",
      "source_ref": "https://t.me/tnz_msk/4000",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3999,
      "date": "2026-04-10T08:36:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3999",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3998,
      "date": "2026-04-09T08:40:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3998",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3997,
      "date": "2026-04-08T15:16:14+00:00",
      "source_ref": "https://t.me/tnz_msk/3997",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3996,
      "date": "2026-04-08T11:57:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3996",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3995,
      "date": "2026-04-08T11:57:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3995",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3994,
      "date": "2026-04-05T10:44:16+00:00",
      "source_ref": "https://t.me/tnz_msk/3994",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3993,
      "date": "2026-04-05T10:16:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3993",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3992,
      "date": "2026-04-05T10:04:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3992",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3991,
      "date": "2026-04-05T10:04:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3991",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3990,
      "date": "2026-04-05T09:09:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3990",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3989,
      "date": "2026-04-03T04:23:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3989",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3988,
      "date": "2026-04-02T20:51:08+00:00",
      "source_ref": "https://t.me/tnz_msk/3988",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3987,
      "date": "2026-04-02T14:42:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3987",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3986,
      "date": "2026-04-02T09:30:57+00:00",
      "source_ref": "https://t.me/tnz_msk/3986",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3985,
      "date": "2026-04-01T09:31:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3985",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3984,
      "date": "2026-04-01T09:25:02+00:00",
      "source_ref": "https://t.me/tnz_msk/3984",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3983,
      "date": "2026-04-01T09:25:02+00:00",
      "source_ref": "https://t.me/tnz_msk/3983",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3982,
      "date": "2026-04-01T09:25:02+00:00",
      "source_ref": "https://t.me/tnz_msk/3982",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3981,
      "date": "2026-04-01T09:16:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3981",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3980,
      "date": "2026-04-01T09:16:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3980",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3979,
      "date": "2026-04-01T09:16:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3979",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3978,
      "date": "2026-04-01T09:16:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3978",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3977,
      "date": "2026-04-01T09:16:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3977",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3976,
      "date": "2026-04-01T08:39:57+00:00",
      "source_ref": "https://t.me/tnz_msk/3976",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3975,
      "date": "2026-04-01T08:39:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3975",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3974,
      "date": "2026-04-01T08:39:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3974",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3973,
      "date": "2026-04-01T07:36:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3973",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3972,
      "date": "2026-04-01T07:36:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3972",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3971,
      "date": "2026-04-01T07:36:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3971",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3970,
      "date": "2026-04-01T06:06:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3970",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3969,
      "date": "2026-04-01T05:56:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3969",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3968,
      "date": "2026-04-01T05:42:15+00:00",
      "source_ref": "https://t.me/tnz_msk/3968",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3967,
      "date": "2026-04-01T05:42:15+00:00",
      "source_ref": "https://t.me/tnz_msk/3967",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3965,
      "date": "2026-03-31T21:05:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3965",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3964,
      "date": "2026-03-31T21:01:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3964",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3963,
      "date": "2026-03-30T10:05:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3963",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3962,
      "date": "2026-03-28T19:23:33+00:00",
      "source_ref": "https://t.me/tnz_msk/3962",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3960,
      "date": "2026-03-27T11:18:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3960",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3959,
      "date": "2026-03-27T11:01:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3959",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3958,
      "date": "2026-03-27T10:13:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3958",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3957,
      "date": "2026-03-27T07:18:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3957",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3956,
      "date": "2026-03-27T04:03:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3956",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3955,
      "date": "2026-03-26T19:36:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3955",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3954,
      "date": "2026-03-26T04:23:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3954",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3953,
      "date": "2026-03-26T04:23:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3953",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3952,
      "date": "2026-03-26T04:23:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3952",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3951,
      "date": "2026-03-26T04:23:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3951",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3950,
      "date": "2026-03-26T04:23:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3950",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3949,
      "date": "2026-03-25T03:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3949",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3948,
      "date": "2026-03-24T08:04:22+00:00",
      "source_ref": "https://t.me/tnz_msk/3948",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3947,
      "date": "2026-03-24T08:04:22+00:00",
      "source_ref": "https://t.me/tnz_msk/3947",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3945,
      "date": "2026-03-21T20:35:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3945",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3944,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3944",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3943,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3943",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3942,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3942",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3941,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3941",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3940,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3940",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3939,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3939",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3938,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3938",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3937,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3937",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3936,
      "date": "2026-03-18T16:20:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3936",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3935,
      "date": "2026-03-17T09:22:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3935",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3934,
      "date": "2026-03-17T09:22:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3934",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3933,
      "date": "2026-03-17T09:22:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3933",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3932,
      "date": "2026-03-12T21:51:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3932",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3931,
      "date": "2026-03-11T20:06:18+00:00",
      "source_ref": "https://t.me/tnz_msk/3931",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3929,
      "date": "2026-03-10T19:44:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3929",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3928,
      "date": "2026-03-09T20:52:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3928",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3927,
      "date": "2026-03-09T11:05:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3927",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3926,
      "date": "2026-03-09T11:05:02+00:00",
      "source_ref": "https://t.me/tnz_msk/3926",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3924,
      "date": "2026-03-08T08:03:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3924",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3923,
      "date": "2026-03-06T10:01:36+00:00",
      "source_ref": "https://t.me/tnz_msk/3923",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3922,
      "date": "2026-03-06T06:58:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3922",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3921,
      "date": "2026-03-06T03:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3921",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3920,
      "date": "2026-03-05T17:31:46+00:00",
      "source_ref": "https://t.me/tnz_msk/3920",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3918,
      "date": "2026-03-04T08:34:47+00:00",
      "source_ref": "https://t.me/tnz_msk/3918",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3917,
      "date": "2026-03-04T07:04:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3917",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3916,
      "date": "2026-03-03T12:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3916",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3915,
      "date": "2026-03-03T12:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3915",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3914,
      "date": "2026-03-03T12:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3914",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3913,
      "date": "2026-03-03T12:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3913",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3912,
      "date": "2026-03-03T12:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3912",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3911,
      "date": "2026-03-03T12:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3911",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3910,
      "date": "2026-03-03T12:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3910",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3909,
      "date": "2026-03-03T10:33:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3909",
      "has_links": true,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3908,
      "date": "2026-03-03T07:24:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3908",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3907,
      "date": "2026-03-03T03:13:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3907",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3906,
      "date": "2026-02-26T10:37:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3906",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3905,
      "date": "2026-02-26T10:37:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3905",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3903,
      "date": "2026-02-21T10:11:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3903",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3902,
      "date": "2026-02-21T10:01:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3902",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3901,
      "date": "2026-02-20T16:46:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3901",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3900,
      "date": "2026-02-18T04:05:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3900",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3899,
      "date": "2026-02-18T04:05:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3899",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3898,
      "date": "2026-02-18T04:05:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3898",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3897,
      "date": "2026-02-18T04:05:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3897",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3896,
      "date": "2026-02-18T04:05:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3896",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3895,
      "date": "2026-02-18T04:05:04+00:00",
      "source_ref": "https://t.me/tnz_msk/3895",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3894,
      "date": "2026-02-17T16:23:02+00:00",
      "source_ref": "https://t.me/tnz_msk/3894",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3893,
      "date": "2026-02-17T15:11:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3893",
      "has_links": true,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3892,
      "date": "2026-02-17T12:38:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3892",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3891,
      "date": "2026-02-17T04:57:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3891",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3890,
      "date": "2026-02-13T13:26:36+00:00",
      "source_ref": "https://t.me/tnz_msk/3890",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3889,
      "date": "2026-02-13T10:33:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3889",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3888,
      "date": "2026-02-13T10:33:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3888",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3886,
      "date": "2026-02-10T10:38:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3886",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3885,
      "date": "2026-02-10T04:24:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3885",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3884,
      "date": "2026-02-09T20:31:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3884",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3883,
      "date": "2026-02-08T15:44:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3883",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3882,
      "date": "2026-02-06T23:27:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3882",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3881,
      "date": "2026-02-06T21:34:59+00:00",
      "source_ref": "https://t.me/tnz_msk/3881",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3880,
      "date": "2026-02-06T21:34:59+00:00",
      "source_ref": "https://t.me/tnz_msk/3880",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3879,
      "date": "2026-02-06T13:21:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3879",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3878,
      "date": "2026-02-06T13:21:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3878",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3877,
      "date": "2026-02-06T13:21:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3877",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3876,
      "date": "2026-02-06T13:21:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3876",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3875,
      "date": "2026-02-06T13:21:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3875",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3874,
      "date": "2026-02-06T13:21:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3874",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3873,
      "date": "2026-02-06T13:21:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3873",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3872,
      "date": "2026-02-06T13:21:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3872",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3871,
      "date": "2026-02-06T07:32:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3871",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3870,
      "date": "2026-02-06T07:32:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3870",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3869,
      "date": "2026-02-06T07:32:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3869",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3868,
      "date": "2026-02-06T07:32:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3868",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3867,
      "date": "2026-02-06T03:02:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3867",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3866,
      "date": "2026-02-05T14:25:43+00:00",
      "source_ref": "https://t.me/tnz_msk/3866",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3865,
      "date": "2026-02-05T14:25:43+00:00",
      "source_ref": "https://t.me/tnz_msk/3865",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3864,
      "date": "2026-02-05T14:25:43+00:00",
      "source_ref": "https://t.me/tnz_msk/3864",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3863,
      "date": "2026-02-03T17:59:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3863",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3862,
      "date": "2026-02-03T06:54:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3862",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3861,
      "date": "2026-02-02T19:45:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3861",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3860,
      "date": "2026-02-02T19:45:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3860",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3859,
      "date": "2026-01-30T08:32:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3859",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3857,
      "date": "2026-01-29T08:43:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3857",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3856,
      "date": "2026-01-29T08:43:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3856",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3855,
      "date": "2026-01-29T05:10:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3855",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3854,
      "date": "2026-01-29T05:10:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3854",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3853,
      "date": "2026-01-29T05:10:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3853",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3852,
      "date": "2026-01-29T05:10:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3852",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3851,
      "date": "2026-01-29T05:10:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3851",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3850,
      "date": "2026-01-29T05:10:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3850",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3849,
      "date": "2026-01-28T15:06:30+00:00",
      "source_ref": "https://t.me/tnz_msk/3849",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3847,
      "date": "2026-01-24T09:29:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3847",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3846,
      "date": "2026-01-24T09:29:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3846",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3845,
      "date": "2026-01-24T07:33:31+00:00",
      "source_ref": "https://t.me/tnz_msk/3845",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3844,
      "date": "2026-01-23T15:48:47+00:00",
      "source_ref": "https://t.me/tnz_msk/3844",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3843,
      "date": "2026-01-23T14:48:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3843",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3842,
      "date": "2026-01-23T14:48:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3842",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3841,
      "date": "2026-01-23T14:48:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3841",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3840,
      "date": "2026-01-22T12:52:31+00:00",
      "source_ref": "https://t.me/tnz_msk/3840",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3839,
      "date": "2026-01-22T12:32:08+00:00",
      "source_ref": "https://t.me/tnz_msk/3839",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3838,
      "date": "2026-01-22T12:32:08+00:00",
      "source_ref": "https://t.me/tnz_msk/3838",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3837,
      "date": "2026-01-22T09:56:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3837",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3836,
      "date": "2026-01-22T09:56:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3836",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3834,
      "date": "2026-01-21T16:47:54+00:00",
      "source_ref": "https://t.me/tnz_msk/3834",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3833,
      "date": "2026-01-20T07:49:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3833",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3832,
      "date": "2026-01-19T18:20:15+00:00",
      "source_ref": "https://t.me/tnz_msk/3832",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3831,
      "date": "2026-01-17T06:41:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3831",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3830,
      "date": "2026-01-16T10:35:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3830",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3829,
      "date": "2026-01-16T10:35:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3829",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3828,
      "date": "2026-01-16T10:35:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3828",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3827,
      "date": "2026-01-16T10:35:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3827",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3826,
      "date": "2026-01-16T10:35:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3826",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3825,
      "date": "2026-01-16T10:35:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3825",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3824,
      "date": "2026-01-16T10:35:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3824",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3823,
      "date": "2026-01-14T21:06:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3823",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3822,
      "date": "2026-01-14T10:10:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3822",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3821,
      "date": "2026-01-14T10:10:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3821",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3820,
      "date": "2026-01-14T10:10:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3820",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3819,
      "date": "2026-01-14T10:10:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3819",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3818,
      "date": "2026-01-14T10:10:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3818",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3817,
      "date": "2026-01-14T10:10:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3817",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3816,
      "date": "2026-01-07T12:59:31+00:00",
      "source_ref": "https://t.me/tnz_msk/3816",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3815,
      "date": "2026-01-06T20:23:07+00:00",
      "source_ref": "https://t.me/tnz_msk/3815",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3814,
      "date": "2026-01-06T13:50:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3814",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3813,
      "date": "2026-01-06T13:38:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3813",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3812,
      "date": "2026-01-06T12:46:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3812",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3811,
      "date": "2026-01-06T12:46:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3811",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3810,
      "date": "2026-01-06T08:23:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3810",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3809,
      "date": "2026-01-05T19:08:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3809",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3808,
      "date": "2026-01-05T17:40:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3808",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3807,
      "date": "2026-01-05T09:30:54+00:00",
      "source_ref": "https://t.me/tnz_msk/3807",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3806,
      "date": "2026-01-05T09:30:54+00:00",
      "source_ref": "https://t.me/tnz_msk/3806",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3805,
      "date": "2026-01-02T11:01:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3805",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3804,
      "date": "2026-01-01T21:42:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3804",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3803,
      "date": "2025-12-31T21:18:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3803",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3802,
      "date": "2025-12-31T12:52:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3802",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3800,
      "date": "2025-12-30T14:59:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3800",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3799,
      "date": "2025-12-30T07:40:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3799",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3798,
      "date": "2025-12-29T22:11:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3798",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3797,
      "date": "2025-12-29T18:21:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3797",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3796,
      "date": "2025-12-29T17:00:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3796",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3795,
      "date": "2025-12-29T12:43:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3795",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3794,
      "date": "2025-12-26T06:34:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3794",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3793,
      "date": "2025-12-24T13:03:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3793",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3792,
      "date": "2025-12-24T13:03:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3792",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3791,
      "date": "2025-12-24T13:03:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3791",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3790,
      "date": "2025-12-24T13:03:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3790",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3789,
      "date": "2025-12-24T13:03:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3789",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3788,
      "date": "2025-12-24T13:03:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3788",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3787,
      "date": "2025-12-24T13:03:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3787",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3786,
      "date": "2025-12-24T13:03:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3786",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3784,
      "date": "2025-12-23T15:12:48+00:00",
      "source_ref": "https://t.me/tnz_msk/3784",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3783,
      "date": "2025-12-19T21:37:15+00:00",
      "source_ref": "https://t.me/tnz_msk/3783",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3782,
      "date": "2025-12-18T03:20:58+00:00",
      "source_ref": "https://t.me/tnz_msk/3782",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3781,
      "date": "2025-12-17T11:57:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3781",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3780,
      "date": "2025-12-17T11:57:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3780",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3779,
      "date": "2025-12-17T11:57:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3779",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3778,
      "date": "2025-12-17T11:57:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3778",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3777,
      "date": "2025-12-17T11:57:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3777",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3776,
      "date": "2025-12-17T11:57:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3776",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3775,
      "date": "2025-12-16T14:25:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3775",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3774,
      "date": "2025-12-16T14:25:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3774",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3773,
      "date": "2025-12-16T14:25:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3773",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3772,
      "date": "2025-12-16T14:25:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3772",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3771,
      "date": "2025-12-16T08:59:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3771",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3770,
      "date": "2025-12-16T08:59:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3770",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3769,
      "date": "2025-12-16T08:59:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3769",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3768,
      "date": "2025-12-16T07:22:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3768",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3767,
      "date": "2025-12-15T11:28:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3767",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3766,
      "date": "2025-12-15T11:28:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3766",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3765,
      "date": "2025-12-15T11:28:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3765",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3764,
      "date": "2025-12-15T11:28:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3764",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3763,
      "date": "2025-12-15T11:28:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3763",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3762,
      "date": "2025-12-15T11:28:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3762",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3761,
      "date": "2025-12-15T05:47:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3761",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3760,
      "date": "2025-12-13T06:14:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3760",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3759,
      "date": "2025-12-12T05:03:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3759",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3758,
      "date": "2025-12-11T09:11:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3758",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3757,
      "date": "2025-12-11T09:11:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3757",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3756,
      "date": "2025-12-11T09:11:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3756",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3755,
      "date": "2025-12-10T15:43:52+00:00",
      "source_ref": "https://t.me/tnz_msk/3755",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3754,
      "date": "2025-12-10T15:19:53+00:00",
      "source_ref": "https://t.me/tnz_msk/3754",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3753,
      "date": "2025-12-10T15:19:53+00:00",
      "source_ref": "https://t.me/tnz_msk/3753",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3752,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3752",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3751,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3751",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3750,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3750",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3749,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3749",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3748,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3748",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3747,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3747",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3746,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3746",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3745,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3745",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3744,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3744",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3743,
      "date": "2025-12-07T08:10:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3743",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3742,
      "date": "2025-12-07T06:32:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3742",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3741,
      "date": "2025-12-06T11:16:23+00:00",
      "source_ref": "https://t.me/tnz_msk/3741",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3740,
      "date": "2025-12-06T11:16:23+00:00",
      "source_ref": "https://t.me/tnz_msk/3740",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3739,
      "date": "2025-12-06T07:22:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3739",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3738,
      "date": "2025-12-06T07:22:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3738",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3737,
      "date": "2025-12-06T07:22:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3737",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3736,
      "date": "2025-12-04T12:57:11+00:00",
      "source_ref": "https://t.me/tnz_msk/3736",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3735,
      "date": "2025-12-04T08:41:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3735",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3734,
      "date": "2025-12-03T13:38:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3734",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3733,
      "date": "2025-12-03T13:38:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3733",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3732,
      "date": "2025-12-03T13:38:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3732",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3731,
      "date": "2025-12-02T04:11:58+00:00",
      "source_ref": "https://t.me/tnz_msk/3731",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3730,
      "date": "2025-11-29T15:29:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3730",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3729,
      "date": "2025-11-29T15:29:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3729",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3728,
      "date": "2025-11-29T15:29:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3728",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3727,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3727",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3726,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3726",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3725,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3725",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3724,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3724",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3723,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3723",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3722,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3722",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3721,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3721",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3720,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3720",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3719,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3719",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3717,
      "date": "2025-11-28T14:15:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3717",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3716,
      "date": "2025-11-28T14:03:07+00:00",
      "source_ref": "https://t.me/tnz_msk/3716",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3715,
      "date": "2025-11-28T14:03:07+00:00",
      "source_ref": "https://t.me/tnz_msk/3715",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3714,
      "date": "2025-11-28T12:14:17+00:00",
      "source_ref": "https://t.me/tnz_msk/3714",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3713,
      "date": "2025-11-28T04:45:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3713",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3711,
      "date": "2025-11-27T08:33:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3711",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3710,
      "date": "2025-11-26T12:22:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3710",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3709,
      "date": "2025-11-25T18:19:58+00:00",
      "source_ref": "https://t.me/tnz_msk/3709",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3708,
      "date": "2025-11-25T18:19:58+00:00",
      "source_ref": "https://t.me/tnz_msk/3708",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3707,
      "date": "2025-11-25T18:19:58+00:00",
      "source_ref": "https://t.me/tnz_msk/3707",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3706,
      "date": "2025-11-25T18:19:57+00:00",
      "source_ref": "https://t.me/tnz_msk/3706",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3701,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3701",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3700,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3700",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3699,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3699",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3698,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3698",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3697,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3697",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3696,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3696",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3695,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3695",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3694,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3694",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3693,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3693",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3692,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3692",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3691,
      "date": "2025-11-24T16:58:33+00:00",
      "source_ref": "https://t.me/tnz_msk/3691",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3690,
      "date": "2025-11-24T16:58:33+00:00",
      "source_ref": "https://t.me/tnz_msk/3690",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3681,
      "date": "2025-11-24T09:35:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3681",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3680,
      "date": "2025-11-23T06:59:46+00:00",
      "source_ref": "https://t.me/tnz_msk/3680",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3679,
      "date": "2025-11-23T06:59:46+00:00",
      "source_ref": "https://t.me/tnz_msk/3679",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3678,
      "date": "2025-11-21T09:54:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3678",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3677,
      "date": "2025-11-21T09:54:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3677",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3675,
      "date": "2025-11-20T16:47:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3675",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3674,
      "date": "2025-11-20T16:47:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3674",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3673,
      "date": "2025-11-20T16:47:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3673",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3672,
      "date": "2025-11-20T16:47:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3672",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3671,
      "date": "2025-11-20T16:29:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3671",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3670,
      "date": "2025-11-20T16:29:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3670",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3669,
      "date": "2025-11-20T08:24:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3669",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3668,
      "date": "2025-11-20T08:23:53+00:00",
      "source_ref": "https://t.me/tnz_msk/3668",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3667,
      "date": "2025-11-18T14:50:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3667",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3666,
      "date": "2025-11-18T14:50:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3666",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3665,
      "date": "2025-11-18T14:50:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3665",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3664,
      "date": "2025-11-18T14:50:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3664",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3663,
      "date": "2025-11-18T14:50:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3663",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3662,
      "date": "2025-11-18T14:50:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3662",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3661,
      "date": "2025-11-18T14:50:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3661",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3660,
      "date": "2025-11-18T14:50:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3660",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3659,
      "date": "2025-11-18T14:50:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3659",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3658,
      "date": "2025-11-18T14:50:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3658",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3657,
      "date": "2025-11-17T15:33:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3657",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3656,
      "date": "2025-11-17T15:33:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3656",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3655,
      "date": "2025-11-17T15:33:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3655",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3654,
      "date": "2025-11-17T15:33:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3654",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3653,
      "date": "2025-11-17T07:48:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3653",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3652,
      "date": "2025-11-17T07:48:28+00:00",
      "source_ref": "https://t.me/tnz_msk/3652",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3651,
      "date": "2025-11-13T16:14:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3651",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3650,
      "date": "2025-11-13T16:14:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3650",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3649,
      "date": "2025-11-12T18:37:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3649",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3648,
      "date": "2025-11-12T16:22:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3648",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3647,
      "date": "2025-11-11T07:19:54+00:00",
      "source_ref": "https://t.me/tnz_msk/3647",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3646,
      "date": "2025-11-11T06:38:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3646",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3645,
      "date": "2025-11-11T04:11:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3645",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3644,
      "date": "2025-11-10T16:11:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3644",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3643,
      "date": "2025-11-10T16:11:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3643",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3642,
      "date": "2025-11-10T13:38:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3642",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3641,
      "date": "2025-11-10T13:38:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3641",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3640,
      "date": "2025-11-10T13:38:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3640",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3639,
      "date": "2025-11-10T13:38:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3639",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3638,
      "date": "2025-11-10T13:38:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3638",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3637,
      "date": "2025-11-10T13:38:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3637",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3635,
      "date": "2025-11-09T04:38:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3635",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3634,
      "date": "2025-11-08T06:53:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3634",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3633,
      "date": "2025-11-08T06:53:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3633",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3632,
      "date": "2025-11-08T06:53:11+00:00",
      "source_ref": "https://t.me/tnz_msk/3632",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3631,
      "date": "2025-11-08T04:06:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3631",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3630,
      "date": "2025-11-07T14:37:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3630",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3629,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3629",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3628,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3628",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3627,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3627",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3626,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3626",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3625,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3625",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3624,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3624",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3623,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3623",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3622,
      "date": "2025-11-06T08:10:44+00:00",
      "source_ref": "https://t.me/tnz_msk/3622",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3621,
      "date": "2025-11-05T18:41:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3621",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3620,
      "date": "2025-11-05T17:40:07+00:00",
      "source_ref": "https://t.me/tnz_msk/3620",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3619,
      "date": "2025-11-05T14:24:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3619",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3618,
      "date": "2025-11-05T14:24:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3618",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3617,
      "date": "2025-11-05T12:27:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3617",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3616,
      "date": "2025-11-05T12:27:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3616",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3615,
      "date": "2025-11-05T12:27:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3615",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3614,
      "date": "2025-11-05T12:27:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3614",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3613,
      "date": "2025-11-05T12:27:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3613",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3612,
      "date": "2025-11-05T12:27:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3612",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3611,
      "date": "2025-11-05T10:44:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3611",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3610,
      "date": "2025-11-05T10:44:20+00:00",
      "source_ref": "https://t.me/tnz_msk/3610",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3609,
      "date": "2025-11-05T10:44:20+00:00",
      "source_ref": "https://t.me/tnz_msk/3609",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3608,
      "date": "2025-11-05T10:44:20+00:00",
      "source_ref": "https://t.me/tnz_msk/3608",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3607,
      "date": "2025-11-05T10:44:20+00:00",
      "source_ref": "https://t.me/tnz_msk/3607",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3606,
      "date": "2025-11-04T10:20:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3606",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3605,
      "date": "2025-11-04T09:39:08+00:00",
      "source_ref": "https://t.me/tnz_msk/3605",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3604,
      "date": "2025-11-03T09:45:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3604",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3602,
      "date": "2025-11-02T09:08:30+00:00",
      "source_ref": "https://t.me/tnz_msk/3602",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3601,
      "date": "2025-11-02T09:08:30+00:00",
      "source_ref": "https://t.me/tnz_msk/3601",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3600,
      "date": "2025-11-02T09:08:30+00:00",
      "source_ref": "https://t.me/tnz_msk/3600",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3599,
      "date": "2025-11-02T09:08:30+00:00",
      "source_ref": "https://t.me/tnz_msk/3599",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3598,
      "date": "2025-11-02T09:08:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3598",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3597,
      "date": "2025-10-31T06:12:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3597",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3596,
      "date": "2025-10-31T06:12:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3596",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3595,
      "date": "2025-10-31T06:12:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3595",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3594,
      "date": "2025-10-31T06:12:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3594",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3593,
      "date": "2025-10-31T06:12:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3593",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3592,
      "date": "2025-10-31T06:12:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3592",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3591,
      "date": "2025-10-31T06:12:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3591",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3590,
      "date": "2025-10-30T19:29:04+00:00",
      "source_ref": "https://t.me/tnz_msk/3590",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3589,
      "date": "2025-10-28T11:59:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3589",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3588,
      "date": "2025-10-28T11:59:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3588",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3587,
      "date": "2025-10-28T11:59:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3587",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3586,
      "date": "2025-10-28T11:59:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3586",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3585,
      "date": "2025-10-27T16:28:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3585",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3584,
      "date": "2025-10-27T11:40:46+00:00",
      "source_ref": "https://t.me/tnz_msk/3584",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3583,
      "date": "2025-10-26T04:45:04+00:00",
      "source_ref": "https://t.me/tnz_msk/3583",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3582,
      "date": "2025-10-26T04:45:04+00:00",
      "source_ref": "https://t.me/tnz_msk/3582",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3581,
      "date": "2025-10-26T04:45:04+00:00",
      "source_ref": "https://t.me/tnz_msk/3581",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3580,
      "date": "2025-10-25T04:16:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3580",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3579,
      "date": "2025-10-24T16:00:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3579",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3578,
      "date": "2025-10-24T16:00:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3578",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3577,
      "date": "2025-10-24T16:00:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3577",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3576,
      "date": "2025-10-24T15:58:30+00:00",
      "source_ref": "https://t.me/tnz_msk/3576",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3573,
      "date": "2025-10-24T12:58:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3573",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3572,
      "date": "2025-10-24T09:16:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3572",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3571,
      "date": "2025-10-24T03:39:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3571",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3569,
      "date": "2025-10-23T04:06:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3569",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3568,
      "date": "2025-10-22T16:59:48+00:00",
      "source_ref": "https://t.me/tnz_msk/3568",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3567,
      "date": "2025-10-22T16:59:48+00:00",
      "source_ref": "https://t.me/tnz_msk/3567",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3566,
      "date": "2025-10-22T16:59:48+00:00",
      "source_ref": "https://t.me/tnz_msk/3566",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3565,
      "date": "2025-10-22T16:59:48+00:00",
      "source_ref": "https://t.me/tnz_msk/3565",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3564,
      "date": "2025-10-22T16:59:48+00:00",
      "source_ref": "https://t.me/tnz_msk/3564",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3563,
      "date": "2025-10-22T13:51:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3563",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3562,
      "date": "2025-10-22T13:51:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3562",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3561,
      "date": "2025-10-22T13:51:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3561",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3560,
      "date": "2025-10-22T07:18:58+00:00",
      "source_ref": "https://t.me/tnz_msk/3560",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3559,
      "date": "2025-10-22T04:06:58+00:00",
      "source_ref": "https://t.me/tnz_msk/3559",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3558,
      "date": "2025-10-21T12:40:46+00:00",
      "source_ref": "https://t.me/tnz_msk/3558",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3557,
      "date": "2025-10-21T12:40:46+00:00",
      "source_ref": "https://t.me/tnz_msk/3557",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3556,
      "date": "2025-10-21T12:40:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3556",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3555,
      "date": "2025-10-21T12:40:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3555",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3554,
      "date": "2025-10-21T12:40:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3554",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3553,
      "date": "2025-10-21T12:40:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3553",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3551,
      "date": "2025-10-21T08:47:52+00:00",
      "source_ref": "https://t.me/tnz_msk/3551",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3550,
      "date": "2025-10-20T20:02:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3550",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3549,
      "date": "2025-10-20T20:02:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3549",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3548,
      "date": "2025-10-20T20:02:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3548",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3547,
      "date": "2025-10-20T16:58:36+00:00",
      "source_ref": "https://t.me/tnz_msk/3547",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3546,
      "date": "2025-10-20T13:39:22+00:00",
      "source_ref": "https://t.me/tnz_msk/3546",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3545,
      "date": "2025-10-20T13:39:22+00:00",
      "source_ref": "https://t.me/tnz_msk/3545",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3544,
      "date": "2025-10-20T13:39:22+00:00",
      "source_ref": "https://t.me/tnz_msk/3544",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3543,
      "date": "2025-10-20T13:39:22+00:00",
      "source_ref": "https://t.me/tnz_msk/3543",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3542,
      "date": "2025-10-20T13:39:22+00:00",
      "source_ref": "https://t.me/tnz_msk/3542",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3541,
      "date": "2025-10-20T10:15:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3541",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3540,
      "date": "2025-10-20T10:15:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3540",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3539,
      "date": "2025-10-20T10:15:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3539",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3538,
      "date": "2025-10-20T10:15:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3538",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3537,
      "date": "2025-10-18T09:48:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3537",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3536,
      "date": "2025-10-17T14:52:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3536",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3535,
      "date": "2025-10-17T09:09:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3535",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3534,
      "date": "2025-10-17T07:08:28+00:00",
      "source_ref": "https://t.me/tnz_msk/3534",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    }
  ]
}
====================================================================================================
END_FILE: docs/TECHNADZOR/source_skills/tnz_msk/SOURCE_INDEX.json
FILE_CHUNK: 1/1
====================================================================================================
