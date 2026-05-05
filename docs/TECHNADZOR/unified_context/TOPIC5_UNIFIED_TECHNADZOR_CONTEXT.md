# TOPIC5 UNIFIED TECHNADZOR CONTEXT

version: TOPIC5_UNIFIED_TECHNADZOR_CONTEXT_V1
updated_at: 2026-05-05
status: VERIFIED
note: Сводный контекст topic_5 (ТЕХНАДЗОР). Все ссылки верифицированы.

---

## 1. Файлы системного контекста

| Файл | Назначение | Статус |
|---|---|---|
| OBJECT_CONTEXT_INDEX.json | Индекс всех объектов | VERIFIED |
| KIEVSKOE_95_OBJECT_CONTEXT.md | Ангар Киевское 95 (3 выезда) | DRIVE_VERIFIED |
| NOVICHKOVO_OBJECT_CONTEXT.md | КП Новичково / Щеглово | DRIVE_VERIFIED |
| SUSANINO_OBJECT_CONTEXT.md | Сусанино | DRIVE_VERIFIED |
| OWNER_ACT_STYLE_PROFILE.md | Стиль актов владельца | DRIVE_VERIFIED |
| OWNER_ACTS_INDEX.json | Индекс всех актов | DRIVE_VERIFIED |
| NORMATIVE_CONTEXT_INDEX.json | Нормативная база | VERIFIED_FROM_ACTS |
| TNZ_MSK_SKILL_BINDING.json | @tnz_msk как скилл оформления | VERIFIED |
| CHAT_EXPORT_TECHNADZOR_BINDING.json | Привязка экспортов чатов | VERIFIED |
| OWNER_ENGINEERING_LOAD_VALIDATION_PATTERN.md | 600/1500 кг/м² паттерн | SOURCE_FROM_OWNER_CONVERSATION |
| OWNER_ENGINEERING_LOAD_VALIDATION_PATTERN.json | То же, JSON | SOURCE_FROM_OWNER_CONVERSATION |

---

## 2. Системная документация

| Файл | Назначение | Статус |
|---|---|---|
| ../TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.md | Полная логика системы | CODE_AUDIT_VERIFIED |
| ../TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.json | То же, JSON | CODE_AUDIT_VERIFIED |
| ../TOPIC5_DOCUMENT_OUTPUT_CONTRACT.md | Контракт вывода документов | CODE_AUDIT_DRAFT_NOT_LIVE_VERIFIED |
| ../TOPIC5_DOCUMENT_OUTPUT_CONTRACT.json | То же, JSON | CODE_AUDIT_DRAFT_NOT_LIVE_VERIFIED |
| ../TOPIC5_RUNTIME_USAGE_RULES.md | Правила работы с системой | CODE_AUDIT_VERIFIED |

---

## 3. Источники скиллов

| Папка | Источник | Роль |
|---|---|---|
| source_skills/tnz_msk/ | @tnz_msk (Карабанов) | DOCUMENT_COMPOSITION_SKILL |

---

## 4. Объекты (краткий индекс)

| ID | Название | Профиль | Статус |
|---|---|---|---|
| KIEVSKOE_95 | Ангар Киевское 95 | METAL_FRAME | ACTIVE_OBJECT |
| NOVICHKOVO | КП Новичково / Щеглово | FRAME_HOUSE | ACTIVE_OBJECT |
| SUSANINO | Сусанино | GENERAL | PROBLEM_OBJECT_CASE |

---

## 5. Ключевые правила

- Факты только из верифицированных источников (Drive актов, прямых измерений)
- Не изобретать пункты нормативов
- Не переносить дефекты между объектами
- @tnz_msk = скилл оформления, не нормативная база, не история объектов
- Vision заблокирован по умолчанию (EXTERNAL_PHOTO_ANALYSIS_ALLOWED=False)
- LOCAL_DRAFT_CREATED ≠ задача выполнена
- CLIENT_DOCUMENT_DELIVERED = задача выполнена

---

## 6. Canon

Основной канонический документ домена:
`docs/CANON_FINAL/TECHNADZOR_DOMAIN_LOGIC_CANON.md`
