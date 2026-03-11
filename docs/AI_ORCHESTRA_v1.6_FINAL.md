# AI ORCHESTRA SYSTEM — FINAL ARCHITECTURE v1.5 (PATCHED)

This document represents the final architecture of the AI Orchestra system after all audit corrections.  
Purpose: confirm final structure before implementation.

---

## 1. CORE PRINCIPLE

Python is the real orchestrator.  
AI models are used only as specialized processors.  
All routing logic is handled by the Python orchestration layer.

---

## 2. TASK QUEUE

- Queue system: **Redis ONLY**
- SQLite is completely forbidden due to multi-worker database locking problems.
- All workers communicate exclusively through Redis.

---

## 3. WORKERS

- Workers are isolated processes.
- Default worker count: `CPU cores × 2` (baseline for I/O-bound tasks; adjust upward for LLM-heavy workloads due to high network latency).
- Workers never communicate with each other directly.
- All communication goes through Redis and the orchestrator.

---

## 4. SYNC WORKER (CRITICAL COMPONENT)

- Workers write runtime state to Redis.
- A separate daemon process called `sync_worker` reads updates from Redis.
- Redis reads must be atomic using `GETDEL`.
- **Redis key pattern:** workers write to `sheet_batch_queue` (list). Each entry is a JSON object with `job_id`, `sheet_tab`, and `row_data`.
- `sync_worker` sends batch updates to Google Sheets every 30 seconds.

**Rules:**
- Workers NEVER write directly to Google Sheets.
- Only `sync_worker` writes to Google Sheets.

**Failure handling:**
- If the Google Sheets API is unavailable, updates remain buffered in Redis.
- `sync_worker` retries with exponential backoff until the API recovers.
- Persistent failures trigger a Telegram alert after 3 consecutive failures.

**Purpose:**  
Avoid Google Sheets API rate limits (60 requests per minute).

---

## 5. STATE MANAGER

- Each job receives a unique identifier.
- Example: `20260310_223455_ESTIMATE_8f23a`
- **Redis TTL:** Job state records expire after **7 days** by default.  
  Completed jobs are explicitly deleted upon successful result delivery.  
  Failed jobs (status `error`) are retained for 30 days for audit purposes.

---

## 6. LOGGING

Logs are stored in:
- `logs/task_log.json`
- `logs/error_log.json`
- `logs/executor_log.json`

Log rotation: 10 MB per file, maximum 10 files.

---

## 7. TIMEOUTS

| Task type   | Soft timeout | Hard timeout |
|-------------|-------------|--------------|
| LLM tasks   | 300 seconds | 600 seconds  |
| API tasks   | 60 seconds  | 120 seconds  |
| Web fetch   | 30 seconds  | 60 seconds   |

---

## 8. APPROVAL SYSTEM

Critical operations require manual approval.

- Implementation: Telegram Bot API
- Interface: Inline buttons — **Approve** / **Reject**

**Flow:**
1. Executor triggers `pending_approval`
2. Telegram bot sends message
3. User presses Approve or Reject
4. Status becomes `approved` or `rejected`

Used primarily for: `devops_executor`

---

## 9. AI ROLES

| Model | Responsibilities |
|-------|-----------------|
| **ChatGPT** | Task packaging, user interaction, final formatting |
| **Claude** | Code generation, architecture logic, document processing |
| **Gemini (Jimmy)** | Web search, Google ecosystem, YouTube analysis, visual generation, Veo video generation (BETA) |
| **DeepSeek** | Mathematics, cost calculations, estimates, fast numeric processing |
| **Grok** | Marketing ideas, hooks, short-form concepts, creative prompts |

---

## 10. EXECUTOR RULES

- Executors never call each other directly.
- Executors communicate only through the orchestrator.
- Each executor runs in a separate process.
- Communication between modules occurs only through Redis.

---

## 11. EXECUTORS

**Implemented executors:**
`pdf_executor`, `cad_executor`, `tech_executor`, `web_executor`, `sport_executor`, `estimate_executor`, `excel_executor`, `google_sheets_executor`, `google_drive_executor`, `content_executor`, `photo_executor`, `video_executor`, `video_prompt_executor`, `amocrm_executor`, `devops_executor`

**Planned executors (NOT production-ready, do not implement without explicit task):**
- `tourism_executor` *(PLANNED — requires API integration)*
- `audio_executor` *(PLANNED — GPU REQUIRED, requires CUDA node)*

---

## 12. PDF PROCESSING

- Unified executor: `pdf_executor`
- Library: **PyMuPDF**
- Supported operations: `extract_pages`, `merge_pdfs`, `reorder_pages`, `number_pages`, `validate_output`
- Removed modules: `pdf_merge_executor`, `pdf_extract_executor`

---

## 13. CRM SYSTEM

- Executor: `amocrm_executor`
- Functions: `create_lead`, `create_contact`, `create_deal`, `update_deal`, `change_status`, `add_note`, `attach_file`, `find_duplicate`, `get_contact`, `get_deal`

---

## 14. TOKEN MANAGER

- Stores: `access_token`, `refresh_token`, `expires_at`
- Token refresh occurs automatically when `expires_at - now < 300 seconds`.
- Locking must use **Redis distributed locks (Redlock)**.
- `threading.Lock` is **forbidden** in multi-worker mode.
- `refresh_token` is stored in Redis with **AES-256 encryption at rest**.  
  Encryption key is loaded from environment variable `TOKEN_ENCRYPTION_KEY` at startup.

---

## 15. WEBHOOK LISTENER

- FastAPI endpoint receives amoCRM webhooks.
- Webhook events are pushed into Redis task queue.

---

## 16. DEVOPS MODULE

- Executor: `devops_executor`

**Restrictions:**
- No blind bash execution.
- SSH must use **`asyncssh`** library.
- Docker must use **Docker SDK for Python** (`docker` package).
- All `sudo` operations require `approval_gate`.
- **Allowed hosts:** defined in `config/devops_allowlist.yaml`. Connections to unlisted hosts are rejected.
- **Allowed operation classes:** `deploy`, `restart`, `logs`, `status`, `backup`. Any operation outside this list requires explicit approval regardless of host.

---

## 17. TECH MODULE

- Executor: `tech_executor`
- Parsers: `ifcopenshell`, `ezdxf`, PDF parsing tools
- **Rule:** AI never processes raw BIM or CAD binary files. AI receives extracted metadata only.

---

## 18. ESTIMATE SYSTEM

**Pipeline:** `estimate_executor` → `excel_executor` → `google_drive_executor`

**Output schema:**

```json
{ "category": "", "item": "", "unit": "", "quantity": 0, "price": 0, "total": 0, "note": "" }
```

All executors in this pipeline must use these exact key names. `excel_executor` will reject payloads with missing or renamed keys.

DeepSeek performs all calculation logic.

---

## 19. WEB PIPELINE

**Stages:** `TASK` → `SEARCH` → `SOURCE_CHECK` → `FETCH` → `EXTRACT` → `STRUCTURE` → `VALIDATE` → `ANALYSIS` → `REPORT`

**Retry policy:**
- `SEARCH`: retry 2 times with exponential backoff (base 2s)
- `FETCH`: retry 3 times with exponential backoff (base 5s)

**Source limits:**
- Maximum **10 sources per task**.
- Trusted/whitelisted domains are prioritized first.
- Sources exceeding the limit are discarded before `EXTRACT` stage.

---

## 20. CONTENT PIPELINE

**Stages:** `TASK` → `DRAFT` → `FILTER` → `VALIDATE` → `FINAL`

Content filter includes stop-word dictionary, anti-AI phrase detection, regex validation, and auto rewrite if forbidden phrases are detected.

---

## 21. VIDEO STACK

**Tools:** Runway, Kling, Luma Dream Machine, Pika, Veo *(BETA / WAITLIST)*  
**Editing:** CapCut (manual). Topaz — removed completely from architecture.

---

## 22. PHOTO STACK

Midjourney, DALL-E, Stable Diffusion, Flux, Canva AI, Gemini visual tools.

---

## 23. AUDIO STACK

- Executor: `audio_executor` — **PLANNED / GPU REQUIRED**
- Status: Not in current architecture. Will be added when CUDA GPU node is available.
- Tools (planned): MusicGen, Spleeter, librosa, ffmpeg
- Requires CUDA GPU node.

---

## 24. TOURISM MODULE

- Executor: `tourism_executor` — **PLANNED**
- Possible providers: Amadeus, Aviasales, Booking API, Playwright scraping

---

## 25. SPORT ANALYTICS

- Executor: `sport_executor`
- Functions: team statistics, match comparison, player analytics, betting analysis

---

## 26. GOOGLE INTEGRATION

- APIs used: Google Drive, Google Sheets, YouTube
- Access method: **Python service account only**
- AI models never call Google APIs directly.

---

## 27. FILE STORAGE STRUCTURE

```
/orchestra
  /pdf
  /cad
  /estimates
  /video
  /reports
  /photo
  /audio
  /tourism
```

---

## 28. SYSTEM STATE (SSOT)

| Storage | Purpose |
|---------|---------|
| GitHub | System code and architecture |
| Google Sheets | Task status |
| Google Drive | Generated files |
| Redis | Runtime state |

---

## 29. JOB INPUT SCHEMA (CRITICAL)

```json
{
  "job_id": "string",
  "command_prefix": "string",
  "payload": "object",
  "attempt_count": "integer",
  "max_retries": "integer"
}
```

**Purpose:** Prevent infinite retry loops. Workers increment `attempt_count` after each failure.

---

## 30. RETRY EXECUTION RULE

```
if job fails:
    if attempt_count < max_retries:
        attempt_count += 1
        return job to queue (with exponential backoff delay)
    else:
        status = "error"
        write to error_log
        move job to dead letter queue
        send Telegram alert
```

---

## 31. JOB RESULT STRUCTURE

```json
{
  "job_id": "string",
  "executor": "string",
  "status": "string",
  "payload": "object",
  "output_path": "string",
  "error_message": "string",
  "attempt_count": "integer"
}
```

> `attempt_count` added to result structure for full audit trail on failures.

---

## 32. DEAD LETTER QUEUE (NEW)

- Jobs that exhaust all retries are moved to a dedicated Redis key: `dlq:{executor}`.
- A Telegram alert is sent immediately with `job_id`, `executor`, and final `error_message`.
- DLQ jobs are retained for **30 days**.
- Manual requeue is supported via orchestrator CLI: `orchestra requeue <job_id>`.

---

## FINAL STATUS — APPLIED CORRECTIONS

| Fix | Status |
|-----|--------|
| Redis-only queue | ✅ |
| `sync_worker` with Google Sheets fallback | ✅ |
| Telegram approval gate | ✅ |
| Unified `pdf_executor` | ✅ |
| SQLite removed completely | ✅ |
| `tourism_executor` marked PLANNED | ✅ |
| `audio_executor` marked PLANNED / GPU REQUIRED | ✅ |
| Veo marked BETA | ✅ |
| `JOB INPUT SCHEMA` (infinite retry protection) | ✅ |
| Redis TTL for state records defined | ✅ |
| `refresh_token` encryption specified (AES-256) | ✅ |
| SSH library fixed to `asyncssh` | ✅ |
| Exponential backoff added to retry logic | ✅ |
| `attempt_count` added to `JOB RESULT STRUCTURE` | ✅ |
| Dead letter queue + Telegram alerts defined | ✅ |
| Google Sheets API failure fallback defined | ✅ |
| Executors split into implemented / planned | ✅ |
| Estimate output schema formalized as JSON | ✅ |
| Web pipeline max source count defined (10) | ✅ |
| `sync_worker` Redis key pattern defined (`sheet_batch_queue`) | ✅ |
| Token refresh threshold defined (`expires_at - now < 300s`) | ✅ |
| `devops_executor` allowlist added (hosts + operation classes) | ✅ |

---
