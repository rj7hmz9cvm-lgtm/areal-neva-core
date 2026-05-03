# ORCHESTRA_FULL_CONTEXT

generated_at_utc: 2026-05-03T10:06:29.924640+00:00
git_sha_before_commit: a57325c6341abf3a627bed7ecf628fd7b89310ad
parts_count: 7
included_full_files: 268
excluded_records: 29

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

## FULL_CONTEXT_PARTS
- PART_001: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_001.md
- PART_002: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_002.md
- PART_003: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_003.md
- PART_004: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_004.md
- PART_005: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_005.md
- PART_006: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_006.md
- PART_007: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_007.md

## MANIFEST
https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json

## RUNTIME
https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md
