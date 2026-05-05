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
