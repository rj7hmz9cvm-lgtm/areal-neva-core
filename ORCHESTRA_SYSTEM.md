# AI ORCHESTRA — CONTEXT UPDATE

## 1. Цель проекта
Мы создаём AI-оркестр, который автоматически выполняет задачи и возвращает готовые результаты:
- файлы
- таблицы
- документы
- расчёты
- анализ

Система уже запущена на Python

## 2. Архитектура
Реальный оркестратор — код (Python orchestration layer)

AI-модели используются как специализированные исполнители

## 3. Роли AI
ChatGPT
- формулирование задач
- контент

Claude
- код
- логика
- структурирование данных
- обработка документов

Gemini
- web-поиск
- анализ данных
- YouTube

DeepSeek
- математика
- сметные расчёты
- конвертации

Grok
- идеи
- короткие формулировки

## 4. Основные модули системы
Система должна поддерживать задачи:
- PDF
- CAD / DWG
- WEB SEARCH
- SPORT ANALYTICS
- CRM / LEADS
- CONTENT
- PHOTO
- VIDEO
- ESTIMATE
- GOOGLE DOCS
- GOOGLE SHEETS
- GOOGLE DRIVE
- YOUTUBE

## 5. Командные режимы
Оркестр должен распознавать команды:
- [PDF]
- [CAD]
- [SEARCH]
- [SPORT]
- [ESTIMATE]
- [VIDEO]
- [CONTENT]

## 6. Executor-архитектура
Каждая задача выполняется отдельным модулем:
- pdf_executor
- cad_executor
- web_executor
- sport_executor
- estimate_executor
- excel_executor
- google_sheets_executor
- google_drive_executor
- video_executor
- video_prompt_executor
- video_enhance_executor

## 7. Web pipeline
Интернет-анализ выполняется так:
TASK
SEARCH
FETCH
EXTRACT
STRUCTURE
ANALYSIS
REPORT

Система должна возвращать данные, а не ссылки

## 8. Модуль смет (ESTIMATE)
Оркестр должен уметь:
- делать сметы
- делать калькуляции
- считать объёмы
- считать бюджеты

Форматы:
- Excel
- Google Sheets

DeepSeek — расчёты
Claude / Python — генерация таблиц

## 9. Google интеграции
Подключены API:
- Google Drive
- Google Sheets
- YouTube

LLM напрямую к Google не подключаются
Работа идёт через Python-код и service account

## 10. Видео стек
Генерация видео:
- Runway
- Kling
- Luma
- Pika

Монтаж:
- CapCut

Улучшение:
- Topaz Video AI
  через локальный CLI wrapper

## 11. Fault tolerance
Каждый шаг должен иметь fallback:
- SEARCH -> fallback provider
- FETCH -> retry
- EXTRACT -> alternate parser

## 12. State management (SSOT)
GitHub
- код и архитектура

Google Sheets
- статусы задач
- pending
- processing
- done
- error

Google Drive
- хранение файлов и результатов

## 13. Текущий статус
Сегодня:
- установлен Python
- запущен оркестр
- определена архитектура
- добавлен модуль смет
- подключены Google API
- добавлен видео стек
- определены роли AI

Следующая задача:
сделать стабильную работу оркестра особенно для:
- смет
- таблиц
- анализа данных

## 14. Инструкция для Claude / Gemini
Store this architecture as persistent project context
Use it for all tasks related to the AI orchestration system
