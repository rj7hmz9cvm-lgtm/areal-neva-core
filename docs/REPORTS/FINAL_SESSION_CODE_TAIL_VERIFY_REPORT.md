# FINAL_SESSION_CODE_TAIL_VERIFY_REPORT

generated_at: 2026-05-02T10:15:27.257895+00:00
status: OK
markers_ok: True
hook_order_ok: True
counts_ok: True
forbidden_ok: True
smoke_ok: True

## RAW_JSON
```json
{
  "generated_at": "2026-05-02T10:15:27.257895+00:00",
  "git": {
    "head": "34aaae5",
    "origin": "597c1f1",
    "ahead_behind": "0\t1",
    "status": "M core/file_context_intake.py\n M core/file_memory_bridge.py\n M core/final_closure_engine.py\n M core/output_sanitizer.py\n M docs/REPORTS/CLAUDE_BOOTSTRAP_PENDING_PUSH.md\n?? data/telegram_file_catalog/\n?? data/templates/estimate_batch/\n?? docs/REPORTS/areal-claude-bootstrap-aggregator.service.before.20260502_121121.txt\n?? outputs/\n?? tools/telegram_file_memory_backfill.py"
  },
  "markers": {
    "task_worker.py": {
      "exists": true,
      "missing": [],
      "ok": true
    },
    "core/price_enrichment.py": {
      "exists": true,
      "missing": [],
      "ok": true
    },
    "core/file_context_intake.py": {
      "exists": true,
      "missing": [],
      "ok": true
    },
    "core/final_closure_engine.py": {
      "exists": true,
      "missing": [],
      "ok": true
    },
    "core/model_router.py": {
      "exists": true,
      "missing": [],
      "ok": true
    },
    "core/runtime_file_catalog.py": {
      "exists": true,
      "missing": [],
      "ok": true
    },
    "core/archive_guard.py": {
      "exists": true,
      "missing": [],
      "ok": true
    },
    "core/technadzor_engine.py": {
      "exists": true,
      "missing": [],
      "ok": true
    },
    "core/ocr_engine.py": {
      "exists": true,
      "missing": [],
      "ok": true
    },
    "core/estimate_engine.py": {
      "exists": true,
      "missing": [],
      "ok": true
    }
  },
  "hook_order": {
    "full_end": 1373,
    "final_hook": 1375,
    "active_dialog": 1796
  },
  "counts": {
    "public_prehandle_price_task_v1": 1,
    "base_prehandle_price_task_v1": 1,
    "create_estimate_xlsx_from_rows": 1
  },
  "forbidden": {
    "telegram_daemon_dirty": false,
    "final_closure_has_voice_handler_def": false,
    "wrong_route_import": false,
    "wrong_final_closure_import": false,
    "wrong_price_symbol": false
  },
  "smoke": {
    "router_cases": {
      "estimate": "estimate",
      "estimate_inflected": "estimate",
      "technadzor": "technadzor",
      "memory": "memory",
      "project": "project"
    },
    "router_ok": true,
    "price_function_exists": true,
    "price_function_result_type_ok": true,
    "final_closure_memory_ok": true,
    "estimate_xlsx_function_ok": true
  },
  "markers_ok": true,
  "hook_order_ok": true,
  "counts_ok": true,
  "forbidden_ok": true,
  "smoke_ok": true,
  "status": "OK"
}
```
