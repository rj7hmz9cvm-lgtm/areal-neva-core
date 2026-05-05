#!/usr/bin/env python3
# === TECHNADZOR_DOCUMENT_SKILL_V1 ===
# Converts source records from telegram_source_skill_extractor into skill cards.
# Rejects noise. Classifies useful document-composition logic.
# All extracted rules must keep source reference.
from __future__ import annotations

import hashlib
import logging
import re
from typing import Any

logger = logging.getLogger("technadzor_document_skill")

SKILL_CATEGORIES = (
    "act_structure",
    "report_structure",
    "defect_description_logic",
    "photo_to_defect_linking",
    "evidence_handling",
    "normative_reference_handling",
    "recommendation_logic",
    "conclusion_logic",
    "file_workflow",
    "document_workflow",
    "client_facing_language",
    "contractor_statement_handling",
    "owner_statement_handling",
    "telegram_source_work_signal",
    "rabota_poisk_reusable_pattern",
    "unknown",
)

# Patterns → category
_CATEGORY_PATTERNS: list[tuple[str, list[str]]] = [
    ("act_structure", [
        "акт", "форма акта", "состав акта", "разделы акта", "приложение к акту",
        "акт освидетельствования", "акт скрытых", "акт приёмки", "акт проверки",
    ]),
    ("report_structure", [
        "отчёт", "отчет", "заключение", "техническое заключение", "разделы отчёта",
        "структура отчёта", "состав отчёта",
    ]),
    ("defect_description_logic", [
        "дефект", "нарушение", "замечание", "несоответствие", "отклонение",
        "трещин", "скол", "раковин", "расслоен", "коррозия",
        "как описать", "формулировка дефекта", "описание дефекта",
    ]),
    ("photo_to_defect_linking", [
        "фото", "фотофиксация", "привязка фото", "фото к дефекту",
        "фото к акту", "фотоматериал", "приложение фото",
    ]),
    ("evidence_handling", [
        "доказательство", "факт", "подтверждение", "доказательная база",
        "источник данных", "обоснование", "исполнительная документация",
    ]),
    ("normative_reference_handling", [
        "снип", "гост", "сп ", "нормати", "требования нормативов",
        "ссылка на норму", "нормативный документ", "регламент",
    ]),
    ("recommendation_logic", [
        "рекомендация", "предписание", "устранить", "необходимо устранить",
        "рекомендуется", "следует", "требуется", "провести работы",
    ]),
    ("conclusion_logic", [
        "вывод", "заключение", "итог", "резюме", "категория состояния",
        "техническое состояние", "ограниченно работоспособ", "аварийн",
    ]),
    ("file_workflow", [
        "pdf", "docx", "xlsx", "dwg", "файл", "загрузка файла",
        "прикрепить файл", "скачать", "отправить файл", "формат файла",
    ]),
    ("document_workflow", [
        "документооборот", "пакет документов", "комплект",
        "исполнительная документация", "журнал работ", "акт скрытых",
        "приёмка документов",
    ]),
    ("client_facing_language", [
        "заказчик", "собственник", "владелец", "клиент", "застройщик",
        "как написать заказчику", "для заказчика", "язык документа",
    ]),
    ("contractor_statement_handling", [
        "подрядчик", "генподрядчик", "субподрядчик", "исполнитель",
        "ответ подрядчика", "позиция подрядчика",
    ]),
    ("owner_statement_handling", [
        "застройщик", "инвестор", "позиция застройщика",
        "ответ застройщика", "письмо застройщика",
    ]),
    ("telegram_source_work_signal", [
        "вакансия", "требуется", "нужен специалист", "ищем технадзор",
        "ищем инженера", "найдём", "предложение работы",
    ]),
    ("rabota_poisk_reusable_pattern", [
        "заказ", "тендер", "объявление", "контракт", "выбор подрядчика",
        "объект ищет", "нужен технадзор", "проведём отбор",
    ]),
]

TOPIC5_VALUE_KEYWORDS = [
    "акт", "дефект", "технадзор", "заключение", "предписание",
    "приёмка", "отчёт", "фото", "норматив", "документ",
    "рекомендация", "вывод", "замечание",
]

NOISE_MARKERS = [
    "реклама", "продам", "куплю", "скидка", "акция",
    "заработок", "кредит без отказа", "займ", "только сегодня",
    "подпишись", "переходи по ссылке", "выиграли",
]


def _card_id(source_ref: str, message_id: int | str) -> str:
    raw = f"{source_ref}::{message_id}"
    return "SK_" + hashlib.md5(raw.encode()).hexdigest()[:12].upper()


def classify_category(text: str) -> str:
    low = text.lower()
    for category, patterns in _CATEGORY_PATTERNS:
        if any(p in low for p in patterns):
            return category
    return "unknown"


def extract_rule_from_text(text: str, category: str) -> str:
    sentences = re.split(r"[.\n!?]+", text)
    useful = []
    for sent in sentences:
        s = sent.strip()
        if len(s) < 20:
            continue
        low = s.lower()
        if any(kw in low for kw in TOPIC5_VALUE_KEYWORDS):
            useful.append(s)
        if len(useful) >= 3:
            break
    if useful:
        return ". ".join(useful[:3])
    # fallback: first substantial sentence
    for sent in sentences:
        s = sent.strip()
        if len(s) >= 30:
            return s[:300]
    return text[:300].strip()


def why_useful(category: str) -> str:
    mapping = {
        "act_structure": "Позволяет выстраивать структуру акта технадзора: разделы, приложения, обязательные поля",
        "report_structure": "Определяет состав технического отчёта/заключения по объекту",
        "defect_description_logic": "Формирует навык точной формулировки дефектов для актов и предписаний",
        "photo_to_defect_linking": "Описывает правило привязки фотоматериалов к конкретным дефектам в документе",
        "evidence_handling": "Показывает как формировать доказательную базу — факты, источники, исполнительная документация",
        "normative_reference_handling": "Обучает правильному указанию нормативных ссылок (СП/ГОСТ/СНиП) в актах",
        "recommendation_logic": "Задаёт логику формулировки предписаний и рекомендаций по устранению",
        "conclusion_logic": "Показывает структуру вывода/заключения о техническом состоянии",
        "file_workflow": "Описывает правила работы с файлами (PDF/DOCX/XLSX) при формировании пакета документов",
        "document_workflow": "Определяет порядок формирования и передачи комплекта исполнительной документации",
        "client_facing_language": "Задаёт профессиональный язык документов, обращённых к заказчику/собственнику",
        "contractor_statement_handling": "Показывает как фиксировать позицию подрядчика в документах",
        "owner_statement_handling": "Показывает как фиксировать позицию застройщика/инвестора",
        "telegram_source_work_signal": "Сигнал о возможной работе/заказе — полезен для маршрутизации в topic_6104",
        "rabota_poisk_reusable_pattern": "Паттерн для поиска заказов/вакансий через Telegram-источник (тема RABOTA_POISK)",
        "unknown": "Категория не определена — требует ручной проверки владельца",
    }
    return mapping.get(category, "")


def is_noise(text: str) -> bool:
    low = (text or "").lower()
    if any(n in low for n in NOISE_MARKERS):
        return True
    if len(text.strip()) < 20:
        return True
    return False


def has_practical_value(text: str) -> bool:
    low = text.lower()
    return any(kw in low for kw in TOPIC5_VALUE_KEYWORDS)


def build_skill_card(record: dict) -> dict | None:
    text = record.get("text", "")
    source_ref = record.get("source_ref", "")
    message_id = record.get("message_id", "")

    if not source_ref:
        logger.debug("rejected: no source_ref msg=%s", message_id)
        return None

    if is_noise(text):
        logger.debug("rejected: noise msg=%s", message_id)
        return None

    if not has_practical_value(text) and not record.get("file_name") and not record.get("links"):
        logger.debug("rejected: no practical value msg=%s", message_id)
        return None

    category = classify_category(text)
    extracted_rule = extract_rule_from_text(text, category)

    needs_review = (
        category == "unknown"
        or len(extracted_rule) < 30
        or not has_practical_value(text)
    )

    tags = [category]
    if record.get("file_name"):
        tags.append("has_document")
    if record.get("links"):
        tags.append("has_links")
    if record.get("media_type") == "photo":
        tags.append("has_photo")

    return {
        "id": _card_id(source_ref, message_id),
        "source": record.get("source", "@tnz_msk"),
        "source_ref": source_ref,
        "message_id": message_id,
        "message_date": record.get("message_date", ""),
        "category": category,
        "title": f"{category}: {extracted_rule[:60]}",
        "source_excerpt": text[:400],
        "extracted_rule": extracted_rule,
        "why_useful_for_topic_5": why_useful(category),
        "source_links": record.get("links", []),
        "source_files": ([record["file_name"]] if record.get("file_name") else []),
        "confidence": "low" if needs_review else "medium",
        "needs_owner_review": needs_review,
        "tags": tags,
    }


def process_records(records: list[dict]) -> dict:
    cards: list[dict] = []
    rejected = 0
    for rec in records:
        card = build_skill_card(rec)
        if card:
            cards.append(card)
        else:
            rejected += 1

    by_category: dict[str, list] = {}
    for card in cards:
        by_category.setdefault(card["category"], []).append(card)

    return {
        "total_input": len(records),
        "extracted": len(cards),
        "rejected_noise": rejected,
        "categories": list(by_category.keys()),
        "cards": cards,
        "by_category": by_category,
    }
# === END_TECHNADZOR_DOCUMENT_SKILL_V1 ===
