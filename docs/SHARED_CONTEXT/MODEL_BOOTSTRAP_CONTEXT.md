# MODEL_BOOTSTRAP_CONTEXT

SYSTEM: AREAL-NEVA ORCHESTRA
GENERATED_AT_UTC: 2026-05-08T06:05:01.741238+00:00
GIT_SHA_BEFORE_COMMIT: b236f02ce3ca63701b23e2185620504fab02ba28
MODE: FACT_ONLY / ZERO_ASSUMPTIONS / GITHUB_SSOT / CANON_LOCK
NO_TRUNCATION: TRUE
TEXT_FILES_INCLUDED_FULLY: TRUE
BIG_FILES_SPLIT_TO_PARTS: TRUE
MANIFEST_SHA256: f383a24a32457d2eb5c66ec6724ddf76c989e212d6829b07f352f9f1a5a148d9

RAW_THIS_FILE:
https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md

CLAUDE_ALIAS:
https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md

IF_UNAVAILABLE:
MODEL_BOOTSTRAP_CONTEXT_UNAVAILABLE

OPERATING_PROTOCOL:
MODE: FACT_ONLY / ZERO_ASSUMPTIONS / GITHUB_SSOT / CANON_LOCK
ONE_LINK_GOAL: модель читает MODEL_BOOTSTRAP_CONTEXT.md и сразу получает всю картину
PATCH_ORDER: DIAGNOSTICS → BAK → PATCH → PY_COMPILE → RESTART → LOGS → DB_VERIFY → GIT_PUSH → FINAL_VERIFY
FORBIDDEN: .env, credentials, token, sessions, raw DB dumps, rm -rf project/canon dirs
CONTEXT_RULE: разрешённые текстовые файлы включаются полностью без обрезки
BIG_TEXT_RULE: большие текстовые файлы дробятся по PART-файлам, не режутся
SECRET_RULE: секретные значения редактируются как <REDACTED_SECRET>
STATUS_RULE: INSTALLED != VERIFIED; VERIFIED только после live-test

TOPIC_REGISTRY:
topic_0=CHAT_ZADACH: общий чат
topic_2=STROYKA: estimate_engine, Excel =C*D =SUM, Python считает, LLM не считает
topic_5=TEKHNADZOR: technadzor_engine, Gemini vision, нормы СП/ГОСТ без выдумывания
topic_11=VIDEOKONTENT
topic_210=PROEKTIROVANIE: project_engine, PROJECT_TEMPLATE_MODEL, не OCR текст
topic_500=VEB_POISK: только Perplexity, 14 этапов, file-context/file-menu запрещены
topic_794=NEJRONKI_SOFT_VPN_VPS
topic_961=AVTO_ZAPCHASTI: OEM, Exist/Drom/Emex
topic_3008=KODY_MOZGOV: верификация кода, No Auto-Patch
topic_4569=LIDY_REKLAMA_AMO
topic_6104=RABOTA_POISK

## READ_ORDER
1. This MODEL_BOOTSTRAP_CONTEXT
2. SINGLE_MODEL_CURRENT_CONTEXT — quick start
3. SINGLE_MODEL_SOURCE — operational index
4. TOPIC_STATUS_INDEX
5. DIRECTION_STATUS_INDEX
6. Required topic/direction file from TOPICS/ or DIRECTIONS/
7. SAFE_RUNTIME_SNAPSHOT
8. SINGLE_MODEL_FULL_CONTEXT — audit only
9. ORCHESTRA_FULL_CONTEXT_MANIFEST
10. ORCHESTRA_FULL_CONTEXT_PART_XXX only if dispute/raw dump needed

## RAW_LINKS
SINGLE_MODEL_CURRENT_CONTEXT:
https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md

SINGLE_MODEL_SOURCE:
https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md

TOPIC_STATUS_INDEX:
https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md

DIRECTION_STATUS_INDEX:
https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md

SAFE_RUNTIME_SNAPSHOT:
https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md

ORCHESTRA_FULL_CONTEXT_INDEX:
https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md

ORCHESTRA_FULL_CONTEXT_MANIFEST:
https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json

## FULL_CONTEXT_PARTS
- PART_001: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_001.md
- PART_002: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_002.md
- PART_003: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_003.md
- PART_004: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_004.md
- PART_005: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_005.md
- PART_006: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_006.md
- PART_007: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_007.md
- PART_008: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_008.md
- PART_009: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_009.md
- PART_010: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_010.md
- PART_011: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_011.md
- PART_012: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_012.md
- PART_013: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_013.md
- PART_014: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_014.md
- PART_015: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_015.md
- PART_016: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_016.md
- PART_017: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_017.md

## PRIORITY_OF_TRUTH
1. Live user output + terminal
2. SAFE_RUNTIME_SNAPSHOT
3. LATEST_HANDOFF
4. NOT_CLOSED
5. CANON_FINAL
6. ARCHITECTURE
7. FULL_CONTEXT_PARTS
8. chat_exports
9. UNKNOWN

## CURRENT_OPEN_STATUS
CANON_ROUTE_FIX_V2: INSTALLED, live-test required
FULL_CONTEXT_AGGREGATOR_V1: this file is generated by full_context_aggregator.py
