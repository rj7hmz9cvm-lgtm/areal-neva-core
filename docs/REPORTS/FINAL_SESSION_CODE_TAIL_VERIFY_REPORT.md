# FINAL_SESSION_CODE_TAIL_VERIFY_REPORT

generated_at: 2026-05-02T10:48:46.722641+00:00
status: OK
markers_ok: True
hook_order_ok: True
counts_ok: True
forbidden_ok: True
smoke_ok: True

## RAW_JSON
```json
{
  "generated_at": "2026-05-02T10:48:46.722641+00:00",
  "git": {
    "head": "f767180",
    "origin": "db602f4",
    "ahead_behind": "0\t1",
    "status": "M core/file_memory_bridge.py\n M core/final_closure_engine.py\n M docs/REPORTS/CLAUDE_BOOTSTRAP_PENDING_PUSH.md\n M docs/REPORTS/FINAL_SESSION_CODE_TAIL_VERIFY_REPORT.md\n?? docs/REPORTS/areal-claude-bootstrap-aggregator.service.before.20260502_121121.txt"
  },
  "markers": {
    "task_worker.py": {
      "exists": true,
      "missing": [],
      "ok": true
    },
    "core/file_memory_bridge.py": {
      "exists": true,
      "missing": [],
      "ok": true
    },
    "core/output_sanitizer.py": {
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
    },
    "core/sheets_generator.py": {
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
    "create_estimate_xlsx_from_rows": 1,
    "prehandle_task_context_v1": 2
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
    "file_memory_domain_project_ok": true,
    "file_memory_title_ok": true,
    "file_memory_links_only_item_ok": true,
    "file_memory_no_blob_link_ok": true,
    "sanitizer_public_ok": true,
    "price_function_exists": true,
    "price_function_result_type_ok": true,
    "final_closure_memory_ok": true,
    "final_closure_public_ok": true,
    "estimate_xlsx_function_ok": true,
    "technadzor_public_message_ok": true,
    "google_sheets_user_entered_ok": true,
    "ocr_real_not_closed_fact": true,
    "dwg_converter_present": false
  },
  "markers_ok": true,
  "hook_order_ok": true,
  "counts_ok": true,
  "forbidden_ok": true,
  "smoke_ok": true,
  "status": "OK"
}
```
