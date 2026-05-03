# CLAUDE_SESSION_START_PROMPT

GENERATED_AT_UTC: 2026-05-03T06:15:08.337990+00:00

MANDATORY FIRST STEP:
Read the full file below before answering any technical question:

https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md

If the file is unavailable, answer only:
CLAUDE_BOOTSTRAP_CONTEXT_UNAVAILABLE

OPERATING MODE:
FACT_ONLY
ZERO_ASSUMPTIONS
GITHUB_SSOT_ONLY
NO_MEMORY_GUESSING
NO_SELF_INITIATED_ARCHITECTURE_CHANGES
NO_PATCH_WITHOUT_DIAGNOSTICS
NO_ENV_TOUCH
NO_SECRET_TOUCH
NO_SESSION_TOUCH
NO_CREDENTIALS_TOUCH

PRIMARY PROJECT:
AREAL-NEVA ORCHESTRA

SERVER:
89.22.225.136

BASE_PATH:
/root/.areal-neva-core

GITHUB_SSOT:
https://github.com/rj7hmz9cvm-lgtm/areal-neva-core

RAW_BOOTSTRAP:
https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md

MANDATORY ANSWER RULES:
1. State facts only from bootstrap, logs, code, or user-provided command output
2. If a fact is missing, write UNKNOWN
3. Never invent service state, file content, DB state, Git state, or runtime result
4. For patches: diagnostics first, backup second, patch third, compile fourth, restart fifth, logs sixth
5. Every patch must be named
6. Use only allowed files from canon unless user explicitly allows more
7. Do not modify .env, tokens, credentials, sessions, Google OAuth files, or DB schema unless the task explicitly requires it
8. Do not use memory from another topic
9. Do not treat topic_id=0 as a specific topic
10. Do not call a task closed until syntax, service, log, DB, Git, and runtime checks pass

WHEN ASKED "WHAT DO YOU KNOW":
Answer using only this bootstrap file and cite the section names from it

WHEN ASKED TO PATCH:
First verify live files and logs, then produce one monolithic SSH block

WHEN ASKED TO CLOSE A CANON:
Verify:
- code markers
- syntax
- services active
- runtime smoke
- DB open task count
- memory writes
- Git commit and push
- fatal logs
- canon docs updated

END
