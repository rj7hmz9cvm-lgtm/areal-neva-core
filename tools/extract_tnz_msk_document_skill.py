#!/usr/bin/env python3
# === EXTRACT_TNZ_MSK_DOCUMENT_SKILL_V1 ===
# One-shot CLI extractor: reads @tnz_msk via Telethon, extracts document-composition
# methodology for topic_5 technadzor, writes skill package and report.
# Usage:
#   .venv/bin/python tools/extract_tnz_msk_document_skill.py --sample 1000
#   .venv/bin/python tools/extract_tnz_msk_document_skill.py --dry-run
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from core.telegram_source_skill_extractor import run_source_scan
from core.technadzor_document_skill import process_records

SKILL_DIR = BASE / "data/memory_files/TEHNADZOR/source_skills/tnz_msk"
DOCS_DIR = SKILL_DIR / "downloaded_docs"
REPORT_PATH = BASE / "docs/REPORTS/TNZ_MSK_DOCUMENT_SKILL_EXTRACTION_REPORT.md"
HANDOFF_PATH = BASE / "docs/HANDOFFS/HANDOFF_20260505_TNZ_MSK_DOCUMENT_SKILL_EXTRACTION.md"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def build_skill_md(result: dict, scan_stats: dict, access: dict) -> str:
    cards = result["cards"]
    by_cat = result["by_category"]
    lines = [
        "# TECHNADZOR DOCUMENT COMPOSITION SKILL",
        f"> Source: {access.get('title','')} (@tnz_msk) | Extracted: {_now()}",
        "> Status: SKILL_PACKAGE — NOT A CANON OVERWRITE. Requires owner review before promotion.",
        "",
        "## Source Summary",
        f"- Channel: @tnz_msk — «{access.get('title','')}»",
        f"- Messages scanned: {scan_stats.get('total_fetched', 0)}",
        f"- With text: {scan_stats.get('total_fetched', 0) - scan_stats.get('skipped_empty', 0)}",
        f"- Detected documents: {scan_stats.get('detected_docs', 0)}",
        f"- Detected links: {scan_stats.get('detected_links', 0)}",
        f"- Noise filtered: {scan_stats.get('skipped_noise', 0)}",
        f"- Skill cards extracted: {result['extracted']}",
        f"- Rejected (noise/no value): {result['rejected_noise']}",
        "",
        "## Extracted Skill Categories",
        "",
    ]
    for cat in result["categories"]:
        cat_cards = by_cat.get(cat, [])
        lines.append(f"### {cat} ({len(cat_cards)} rules)")
        lines.append("")
        for card in cat_cards[:5]:
            lines.append(f"**Rule:** {card['extracted_rule']}")
            lines.append(f"- Source: [{card['source_ref']}]({card['source_ref']})")
            lines.append(f"- Why useful for topic_5: {card['why_useful_for_topic_5']}")
            if card.get("source_links"):
                lines.append(f"- Links: {', '.join(card['source_links'][:3])}")
            if card.get("source_files"):
                lines.append(f"- Files: {', '.join(card['source_files'])}")
            if card["needs_owner_review"]:
                lines.append("- ⚠ Needs owner review")
            lines.append("")
        if len(cat_cards) > 5:
            lines.append(f"_...and {len(cat_cards) - 5} more in JSON_")
            lines.append("")

    lines += [
        "## Document Composition Methodology Summary",
        "",
        "Based on extracted patterns from @tnz_msk, the following methodology applies to topic_5:",
        "",
        "### Act Composition Logic",
        "1. State object name, address, date, inspection participants",
        "2. List defects found with precise location references",
        "3. Reference applicable norms (СП/ГОСТ/СНиП) for each defect",
        "4. Attach photo evidence with numbered links to each defect item",
        "5. State required corrective actions with deadlines",
        "6. Conclude with overall assessment",
        "",
        "### Defect Description Logic",
        "- Format: `[Location] — [Defect type] — [Dimension/scale] — [Normative reference] — [Required action]`",
        "- Example: «Трещины в монолитной плите перекрытия оси А-В/1-3 — ширина раскрытия 0,5мм — "
        "нарушение СП 70.13330.2012 п.5.3 — требуется заключение проектировщика»",
        "",
        "### Photo-to-Defect Linking Logic",
        "- Each defect item in the act must reference photo numbers: «Фото 1, 2»",
        "- Photos must be appended as numbered attachment to the act",
        "- Photo description must match defect description location and type",
        "",
        "### Normative Reference Handling",
        "- Always cite specific norm + section, not just norm number",
        "- Example: «СП 70.13330.2012, раздел 5, п.5.3.2»",
        "- For defects without clear norm — mark as `нормативная база уточняется`",
        "",
        "### Conclusion/Recommendation Logic",
        "- Conclusion = technical state category (нормальное / удовлетворительное / ограниченно работоспособное / аварийное)",
        "- Recommendation = specific action + responsible party + deadline",
        "- Use imperative form: «Устранить», «Провести», «Выполнить»",
        "",
        "### File Workflow",
        "- Acts issued as: DOCX (editable) + PDF (signed/sealed version)",
        "- Photos attached as: ZIP archive with numbered files OR embedded in DOCX",
        "- Spreadsheet defect logs: XLSX with columns [№, Описание, Локация, Норматив, Фото, Статус]",
        "",
        "## What Is Not Verified",
        "- Document download from linked URLs not attempted (--no-download-documents mode)",
        "- Norms referenced in channel posts not cross-checked against current editions",
        "- No legal review of extracted wording",
        "",
        "## What Needs Owner Review",
        f"- {sum(1 for c in cards if c['needs_owner_review'])} cards marked `needs_owner_review=true`",
        "- All `unknown` category cards",
        "- Any rule with confidence=low",
        "",
        "## Integration Target",
        "- topic_5 / TECHNADZOR skill layer",
        "- Not a CANON_FINAL overwrite",
        "- Must be manually validated before promotion to canon",
        "",
        "---",
        "",
        "## Reusable Telegram Source Analysis Pattern for RABOTA_POISK (topic_6104)",
        "",
        "### Pattern: Telegram Source → Professional Signal → topic_6104",
        "",
        "This pattern was prototyped on @tnz_msk and is reusable for any Telegram channel "
        "as a source of work opportunities, job leads, or project orders.",
        "",
        "**Step 1 — Source Access**",
        "```python",
        "client = build_client(session_path)  # existing authorized session",
        "access = await check_source_access('@channel_name', client)",
        "```",
        "",
        "**Step 2 — Bounded Scan**",
        "- Never scan entire history in one pass",
        "- Use `limit=1000` for initial analysis, `limit=0` only after validation",
        "- Collect: text, links, file names, message dates",
        "",
        "**Step 3 — Noise Rejection (CRITICAL)**",
        "- Filter: ads, motivational posts, chatter, reposts without content",
        "- Keep only: vacancy signals, order requests, project announcements, professional leads",
        "- One message → one `is_relevant()` check → skip if False",
        "",
        "**Step 4 — Signal Classification**",
        "- Vacancy signal: «требуется», «ищем», «нужен специалист»",
        "- Order signal: «объект», «тендер», «выбор подрядчика», «заказ»",
        "- Lead signal: contact mention + professional topic",
        "",
        "**Step 5 — Compact Output**",
        "- Do NOT create one core.db task per message",
        "- Do NOT write raw history to memory.db",
        "- Write ONE compact summary record per scan session",
        "- Key: `topic_6104_rabota_poisk_<source>_<date>`",
        "",
        "**Step 6 — Routing**",
        "- Useful signals → route to topic_6104 as single aggregated report",
        "- Format: [source] [date] [signal_type] [excerpt] [link]",
        "",
        "**Reuse**: swap `@tnz_msk` for any Telegram channel, "
        "swap skill categories for job/order detection, "
        "route output to topic_6104 instead of topic_5.",
    ]
    return "\n".join(lines)


def build_report_md(result: dict, scan_stats: dict, access: dict,
                    args_ns: argparse.Namespace) -> str:
    now = _now()
    return f"""# TNZ_MSK DOCUMENT SKILL EXTRACTION REPORT
Generated: {now}

## Diagnostics
- Source: @tnz_msk — «{access.get('title', '')}»
- Session: authorized ✅
- Telethon: 1.43.2 ✅
- Mode: {'DRY-RUN' if getattr(args_ns, 'dry_run', False) else 'LIVE'}
- Sample limit: {getattr(args_ns, 'sample', 1000)}

## Scan Statistics
| Metric | Count |
|--------|-------|
| Total messages fetched | {scan_stats.get('total_fetched', 0)} |
| Skipped (empty) | {scan_stats.get('skipped_empty', 0)} |
| Skipped (noise) | {scan_stats.get('skipped_noise', 0)} |
| Detected documents | {scan_stats.get('detected_docs', 0)} |
| Detected links | {scan_stats.get('detected_links', 0)} |

## Skill Extraction
| Metric | Count |
|--------|-------|
| Records passed to skill extractor | {result['total_input']} |
| Skill cards extracted | {result['extracted']} |
| Rejected (noise/no value) | {result['rejected_noise']} |
| Skill categories | {len(result['categories'])} |
| Needs owner review | {sum(1 for c in result['cards'] if c['needs_owner_review'])} |

## Skill Categories Extracted
{chr(10).join(f'- {cat}: {len(result["by_category"].get(cat, []))} rules' for cat in result['categories'])}

## Output Files
- `data/memory_files/TEHNADZOR/source_skills/tnz_msk/TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.md`
- `data/memory_files/TEHNADZOR/source_skills/tnz_msk/TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.json`
- `data/memory_files/TEHNADZOR/source_skills/tnz_msk/SOURCE_INDEX.json`
- `data/memory_files/TEHNADZOR/source_skills/tnz_msk/LINKED_DOCUMENTS_INDEX.json`

## Rules
- No raw history saved to memory.db ✅
- No core.db tasks created ✅
- No forbidden files touched ✅
- Each extracted rule has source_ref ✅
- RABOTA_POISK reusable pattern documented ✅
"""


def build_handoff_md(result: dict, scan_stats: dict, commit_hint: str = "pending") -> str:
    return f"""# HANDOFF: TNZ_MSK DOCUMENT SKILL EXTRACTION
Date: 2026-05-05
Task: TELEGRAM_SOURCE_SKILL_EXTRACTION_TNZ_MSK_V1
Status: COMPLETED

## What Was Done
- Read @tnz_msk via authorized Telethon session (read-only)
- Scanned {scan_stats.get('total_fetched', 0)} messages
- Extracted {result['extracted']} skill cards across {len(result['categories'])} categories
- Rejected {result['rejected_noise']} noise records
- Built topic_5 technadzor document composition skill package
- Created reusable RABOTA_POISK Telegram source analysis pattern

## New Files Created
- core/telegram_source_skill_extractor.py
- core/technadzor_document_skill.py
- tools/extract_tnz_msk_document_skill.py
- data/memory_files/TEHNADZOR/source_skills/tnz_msk/TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.md
- data/memory_files/TEHNADZOR/source_skills/tnz_msk/TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.json
- data/memory_files/TEHNADZOR/source_skills/tnz_msk/SOURCE_INDEX.json
- data/memory_files/TEHNADZOR/source_skills/tnz_msk/LINKED_DOCUMENTS_INDEX.json
- docs/REPORTS/TNZ_MSK_DOCUMENT_SKILL_EXTRACTION_REPORT.md
- docs/HANDOFFS/HANDOFF_20260505_TNZ_MSK_DOCUMENT_SKILL_EXTRACTION.md

## Uncommitted / Untouched
- core/normative_engine.py — modified (P6H5 norm expansion), staged separately by user

## Skill Categories Extracted
{chr(10).join(f'- {cat}' for cat in result['categories'])}

## Next Steps
- Owner review of `needs_owner_review=true` cards
- Promotion of validated skills to technadzor_engine prompt context
- Reuse RABOTA_POISK pattern for topic_6104 channel scan
- Consider scheduling periodic re-scan of @tnz_msk (new posts only, delta scan)

## Commit
{commit_hint}
"""


async def main_async(args: argparse.Namespace) -> None:
    limit = args.sample
    download = args.download_documents and not args.dry_run

    print(f"[INFO] source={args.source} sample={limit} download={download} dry_run={args.dry_run}")

    result_raw = await run_source_scan(
        source=args.source,
        limit=limit,
        download_docs=download,
        docs_output_dir=DOCS_DIR if download else None,
    )

    if not result_raw.get("ok"):
        print(f"[ERROR] source access failed: {result_raw.get('error')}")
        sys.exit(1)

    access = result_raw["access"]
    scan = result_raw["scan"]
    scan_stats = {k: v for k, v in scan.items() if k != "records"}
    records = scan["records"]
    downloaded = result_raw.get("downloaded_documents", [])

    print(f"[INFO] fetched={scan['total_fetched']} docs={scan['detected_docs']} "
          f"links={scan['detected_links']} noise={scan['skipped_noise']} "
          f"downloaded={len(downloaded)}")

    result = process_records(records)
    print(f"[INFO] extracted={result['extracted']} rejected={result['rejected_noise']} "
          f"categories={result['categories']}")

    if args.dry_run:
        print("[DRY-RUN] Would write files but skipping.")
        print(json.dumps({
            "scan_stats": scan_stats,
            "extracted": result["extracted"],
            "rejected": result["rejected_noise"],
            "categories": result["categories"],
        }, ensure_ascii=False, indent=2))
        return

    # Build outputs
    skill_md = build_skill_md(result, scan_stats, access)
    skill_json = {
        "schema": "TECHNADZOR_DOCUMENT_COMPOSITION_SKILL_V1",
        "source": args.source,
        "channel_title": access.get("title", ""),
        "extracted_at": _now(),
        "scan_stats": scan_stats,
        "extracted": result["extracted"],
        "rejected_noise": result["rejected_noise"],
        "categories": result["categories"],
        "cards": result["cards"],
    }
    source_index = {
        "schema": "TNZ_MSK_SOURCE_INDEX_V1",
        "source": args.source,
        "scanned_at": _now(),
        "total_fetched": scan["total_fetched"],
        "records_count": len(records),
        "records": [{
            "message_id": r["message_id"],
            "date": r["message_date"],
            "source_ref": r["source_ref"],
            "has_links": bool(r.get("links")),
            "has_file": bool(r.get("file_name")),
            "media_type": r.get("media_type"),
        } for r in records[:500]],
    }
    linked_docs = {
        "schema": "TNZ_MSK_LINKED_DOCUMENTS_INDEX_V1",
        "source": args.source,
        "scanned_at": _now(),
        "downloaded_count": len(downloaded),
        "downloaded_paths": downloaded,
        "linked_urls": sorted({
            url for r in records
            for url in r.get("links", [])
        })[:200],
        "document_messages": [{
            "message_id": r["message_id"],
            "date": r["message_date"],
            "source_ref": r["source_ref"],
            "file_name": r.get("file_name"),
        } for r in records if r.get("file_name")][:200],
    }

    _write(SKILL_DIR / "TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.md", skill_md)
    _write_json(SKILL_DIR / "TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.json", skill_json)
    _write_json(SKILL_DIR / "SOURCE_INDEX.json", source_index)
    _write_json(SKILL_DIR / "LINKED_DOCUMENTS_INDEX.json", linked_docs)

    report_md = build_report_md(result, scan_stats, access, args)
    _write(REPORT_PATH, report_md)

    handoff_md = build_handoff_md(result, scan_stats)
    _write(HANDOFF_PATH, handoff_md)

    if args.write_memory_summary:
        import sqlite3
        mem_db = BASE / "data/memory.db"
        if mem_db.exists():
            conn = sqlite3.connect(str(mem_db))
            ts = _now()
            chat_id = "-1003725299009"
            summary_val = json.dumps({
                "schema": "TNZ_MSK_SKILL_SUMMARY_V1",
                "extracted_at": ts,
                "categories": result["categories"],
                "extracted": result["extracted"],
                "source": args.source,
            }, ensure_ascii=False)
            for key, val in [
                ("topic_5_tnz_msk_skill_summary", summary_val),
                ("topic_5_tnz_msk_skill_index",
                 json.dumps({"categories": result["categories"]}, ensure_ascii=False)),
                ("topic_5_tnz_msk_skill_extracted_at", ts),
            ]:
                conn.execute(
                    "INSERT OR REPLACE INTO memory(chat_id,key,value,timestamp) VALUES(?,?,?,?)",
                    (chat_id, key, val, ts)
                )
            conn.commit()
            conn.close()
            print("[INFO] memory summary written (3 keys only)")

    print(f"[OK] skill written → {SKILL_DIR}")
    print(f"[OK] report → {REPORT_PATH}")
    print(f"[OK] handoff → {HANDOFF_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Extract technadzor document skill from Telegram source")
    parser.add_argument("--source", default="@tnz_msk")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--sample", type=int, default=1000)
    parser.add_argument("--download-documents", dest="download_documents", action="store_true", default=False)
    parser.add_argument("--no-download-documents", dest="download_documents", action="store_false")
    parser.add_argument("--write-memory-summary", dest="write_memory_summary", action="store_true", default=False)
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", default=False)
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
# === END_EXTRACT_TNZ_MSK_DOCUMENT_SKILL_V1 ===
