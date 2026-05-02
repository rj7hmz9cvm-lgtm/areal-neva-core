# === WEB_SEARCH_PRICE_ENRICHMENT_V1 ===
# === PRICE_CONFIRMATION_BEFORE_ESTIMATE_V1 ===
from __future__ import annotations

import os
import re
import json
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

BASE = Path("/root/.areal-neva-core")
PRICE_DIR = BASE / "data" / "price_quotes"
PRICE_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v).strip()


def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")


def _task_field(task: Any, field: str, default: Any = "") -> Any:
    try:
        if hasattr(task, "keys") and field in task.keys():
            return task[field]
    except Exception:
        pass
    if isinstance(task, dict):
        return task.get(field, default)
    try:
        return getattr(task, field)
    except Exception:
        return default


def _safe_key(v: Any, limit: int = 80) -> str:
    return re.sub(r"[^0-9A-Za-z_-]+", "_", _s(v))[:limit] or "unknown"


def _cache_path(chat_id: str, topic_id: int) -> Path:
    return PRICE_DIR / f"PENDING__chat_{_safe_key(chat_id)}__topic_{int(topic_id or 0)}.json"


def _is_web_price_request(text: str) -> bool:
    low = _low(text)
    return any(x in low for x in (
        "цены из интернета", "цена из интернета", "актуальные цены", "актуальная цена",
        "цены материалов", "стоимость материалов", "брать из интернета", "искать в интернете",
        "найти цены", "проверить цены", "рыночные цены", "поставщиков", "поставщик"
    ))


def _detect_price_choice(text: str) -> str:
    low = _low(text)
    if any(x in low for x in ("дешев", "минималь", "самые низкие", "вариант а", "а —", "а-")):
        return "cheapest"
    if any(x in low for x in ("средн", "рынок", "вариант б", "б —", "б-")):
        return "average"
    if any(x in low for x in ("надеж", "надёж", "проверенн", "вариант в", "в —", "в-")):
        return "reliable"
    if any(x in low for x in ("вручную", "сам укажу", "мои цены", "вариант г", "г —", "г-")):
        return "manual"
    return ""


def _load_price_mode_from_memory(chat_id: str, topic_id: int) -> str:
    try:
        mem = BASE / "data" / "memory.db"
        if not mem.exists():
            return ""
        conn = sqlite3.connect(str(mem))
        try:
            key = f"topic_{int(topic_id or 0)}_price_mode"
            row = conn.execute(
                "SELECT value FROM memory WHERE chat_id=? AND key=? ORDER BY rowid DESC LIMIT 1",
                (str(chat_id), key),
            ).fetchone()
            return _s(row[0]) if row else ""
        finally:
            conn.close()
    except Exception:
        return ""


def _parse_json_from_text(text: str) -> Any:
    src = _s(text)
    if not src:
        return None
    m = re.search(r"```(?:json)?\s*(.*?)```", src, re.S | re.I)
    if m:
        src = m.group(1)
    else:
        a = src.find("{")
        b = src.rfind("}")
        if a >= 0 and b > a:
            src = src[a:b+1]
    try:
        return json.loads(src)
    except Exception:
        return None


async def _openrouter_price_search(item_name: str, unit: str = "", region: str = "Санкт-Петербург") -> List[Dict[str, Any]]:
    api_key = (os.getenv("OPENROUTER_API_KEY") or "").strip()
    if not api_key:
        return []

    model = (os.getenv("OPENROUTER_MODEL_ONLINE") or "perplexity/sonar").strip()
    base_url = (os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1").strip().rstrip("/")

    prompt = (
        "Найди актуальные цены на строительный материал для сметы\n"
        f"Материал: {item_name}\n"
        f"Единица: {unit or 'UNKNOWN'}\n"
        f"Регион: {region}\n\n"
        "Верни только JSON object:\n"
        "{\n"
        '  "offers": [\n'
        '    {"name":"...", "price":123.45, "unit":"м3/м2/т/шт/кг/п.м", "supplier":"...", "url":"https://...", "checked_at":"ISO_DATE", "status":"CONFIRMED|PARTIAL|UNVERIFIED", "risk":"low|medium|high"}\n'
        "  ]\n"
        "}\n"
        "Не выдумывай URL. Если цена не подтверждена — status=UNVERIFIED"
    )

    try:
        import httpx
        body = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=20.0)) as client:
            r = await client.post(f"{base_url}/chat/completions", headers=headers, json=body)
            r.raise_for_status()
            data = r.json()
        content = data["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "\n".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in content)
        parsed = _parse_json_from_text(content)
        offers = parsed.get("offers") if isinstance(parsed, dict) else []
        clean = []
        for o in offers or []:
            if not isinstance(o, dict):
                continue
            try:
                price = float(str(o.get("price") or "0").replace(" ", "").replace(",", "."))
            except Exception:
                price = 0.0
            if price <= 0:
                continue
            clean.append({
                "name": _s(o.get("name"))[:160] or item_name,
                "price": price,
                "unit": _s(o.get("unit"))[:30] or unit,
                "supplier": _s(o.get("supplier"))[:160],
                "url": _s(o.get("url"))[:500],
                "checked_at": _s(o.get("checked_at"))[:80] or _now(),
                "status": _s(o.get("status"))[:30] or "UNVERIFIED",
                "risk": _s(o.get("risk"))[:30] or "medium",
            })
        return clean[:5]
    except Exception:
        return []


def _fallback_offer(item_name: str, unit: str = "") -> List[Dict[str, Any]]:
    return [{
        "name": item_name,
        "price": 0.0,
        "unit": unit,
        "supplier": "NOT_FOUND",
        "url": "",
        "checked_at": _now(),
        "status": "UNVERIFIED",
        "risk": "high",
    }]


def _price_prompt(cache: Dict[str, Any]) -> str:
    lines = ["Нашёл актуальные цены для сметы", ""]
    for idx, item in enumerate(cache.get("items") or [], 1):
        lines.append(f"{idx}. {item.get('name')}")
        offers = item.get("offers") or []
        if not offers:
            lines.append("   цены не найдены")
            continue
        for j, o in enumerate(offers[:3], 1):
            price = float(o.get("price") or 0)
            unit = o.get("unit") or item.get("unit") or ""
            supplier = o.get("supplier") or "поставщик не указан"
            status = o.get("status") or "UNVERIFIED"
            url = o.get("url") or ""
            if price > 0:
                lines.append(f"   {j}) {price:g} руб/{unit} — {supplier} — {status}")
            else:
                lines.append(f"   {j}) цена не подтверждена — {supplier} — {status}")
            if url:
                lines.append(f"      {url}")
        lines.append("")
    lines.append("Какие цены поставить?")
    lines.append("А — самые дешёвые")
    lines.append("Б — средние")
    lines.append("В — надёжный поставщик")
    lines.append("Г — укажу вручную")
    return "\n".join(lines).strip()


def _select_price(offers: List[Dict[str, Any]], mode: str) -> float:
    valid = [o for o in offers if float(o.get("price") or 0) > 0]
    if not valid:
        return 0.0
    if mode == "cheapest":
        return min(float(o.get("price") or 0) for o in valid)
    if mode == "average":
        vals = [float(o.get("price") or 0) for o in valid]
        return round(sum(vals) / len(vals), 2)
    if mode == "reliable":
        confirmed = [o for o in valid if _low(o.get("status")) == "confirmed" and _low(o.get("risk")) != "high"]
        src = confirmed or valid
        return sorted(src, key=lambda x: float(x.get("price") or 0))[0]["price"]
    return 0.0


def _apply_selected_prices(cache: Dict[str, Any], mode: str) -> List[Dict[str, Any]]:
    items = []
    for item in cache.get("items") or []:
        qty = float(item.get("qty") or 0)
        unit = item.get("unit") or ""
        price = _select_price(item.get("offers") or [], mode)
        items.append({
            "name": item.get("name") or "Позиция",
            "unit": unit,
            "qty": qty,
            "material_price": price,
            "material_sum": round(qty * price, 2),
            "work_price": float(item.get("work_price") or 0),
            "work_sum": round(qty * float(item.get("work_price") or 0), 2),
            "price": price + float(item.get("work_price") or 0),
            "total": round(qty * (price + float(item.get("work_price") or 0)), 2),
        })
    return items


def _send_update_payload(conn: sqlite3.Connection, task_id: str, state: str, result: str, error_message: str = "") -> Dict[str, Any]:
    return {
        "handled": True,
        "state": state,
        "message": result,
        "error_message": error_message,
        "kind": "price_enrichment",
        "history": "WEB_SEARCH_PRICE_ENRICHMENT_V1:HANDLED",
    }


async def _build_estimate_from_cache(conn: sqlite3.Connection, task: Any, cache: Dict[str, Any], mode: str) -> Dict[str, Any]:
    from core import sample_template_engine as ste

    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)

    if mode == "manual":
        return _send_update_payload(
            conn,
            task_id,
            "WAITING_CLARIFICATION",
            "Пришли цены вручную одним сообщением: материал — цена за единицу",
            "",
        )

    template = ste._load_active_template("estimate", chat_id, topic_id)
    if not template:
        return _send_update_payload(conn, task_id, "FAILED", "Не найден активный шаблон сметы в этом топике", "ACTIVE_ESTIMATE_TEMPLATE_NOT_FOUND")

    items = _apply_selected_prices(cache, mode)
    total = round(sum(float(x.get("total") or 0) for x in items), 2)
    if total <= 0:
        return _send_update_payload(conn, task_id, "WAITING_CLARIFICATION", "Не смог подтвердить цены. Укажи цены вручную или выбери другой режим", "PRICE_TOTAL_ZERO")

    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id))[:30]
    out_dir = Path(tempfile.gettempdir()) / f"areal_price_estimate_{safe}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    xlsx_path = str(out_dir / f"estimate_{safe}.xlsx")
    pdf_path = str(out_dir / f"estimate_{safe}.pdf")
    manifest_path = str(out_dir / f"estimate_{safe}.price_sources.json")

    ste._write_estimate_xlsx(xlsx_path, items, template, cache.get("raw_input") or "")
    ste._write_estimate_pdf(pdf_path, items, template, cache.get("raw_input") or "")

    manifest = {
        "engine": "WEB_SEARCH_PRICE_ENRICHMENT_V1",
        "task_id": task_id,
        "chat_id": chat_id,
        "topic_id": topic_id,
        "selected_mode": mode,
        "items": items,
        "price_cache": cache,
        "total": total,
        "created_at": _now(),
    }
    Path(manifest_path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    pdf_link = ste._upload(pdf_path, task_id, topic_id)
    xlsx_link = ste._upload(xlsx_path, task_id, topic_id)
    manifest_link = ste._upload(manifest_path, task_id, topic_id)

    if not pdf_link or not xlsx_link:
        return _send_update_payload(
            conn,
            task_id,
            "FAILED",
            "Смета создана локально, но не выгрузилась в Google Drive",
            "ESTIMATE_UPLOAD_FAILED",
        )

    msg = (
        "Смета создана по выбранным актуальным ценам\n"
        f"Режим цен: {mode}\n"
        f"Позиций: {len(items)} | Итого: {total:.2f} руб\n\n"
        f"PDF: {pdf_link}\n"
        f"XLSX: {xlsx_link}\n"
    )
    if manifest_link:
        msg += f"\nИсточники цен: {manifest_link}\n"
    msg += "\nДоволен результатом? Да / Уточни / Правки"

    return _send_update_payload(conn, task_id, "AWAITING_CONFIRMATION", msg, "")


async def prehandle_price_task_v1(conn: sqlite3.Connection, task: Any) -> Optional[Dict[str, Any]]:
    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    input_type = _s(_task_field(task, "input_type"))
    raw_input = _s(_task_field(task, "raw_input"))

    if input_type not in ("text", "voice"):
        return None

    choice = _detect_price_choice(raw_input)
    cache_file = _cache_path(chat_id, topic_id)
    if choice and cache_file.exists():
        try:
            cache = json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            cache = {}
        if cache:
            return await _build_estimate_from_cache(conn, task, cache, choice)

    price_mode = _load_price_mode_from_memory(chat_id, topic_id)
    if not (_is_web_price_request(raw_input) or price_mode == "web_confirm"):
        return None

    from core import sample_template_engine as ste

    template = ste._load_active_template("estimate", chat_id, topic_id)
    if not template:
        return None

    items = ste._parse_estimate_items(raw_input)
    if not items:
        return None

    enriched = []
    for item in items[:30]:
        name = item.get("name") or "Позиция"
        unit = item.get("unit") or ""
        qty = float(item.get("qty") or 0)
        offers = await _openrouter_price_search(name, unit)
        if not offers:
            offers = _fallback_offer(name, unit)
        item2 = dict(item)
        item2["qty"] = qty
        item2["offers"] = offers
        enriched.append(item2)

    cache = {
        "engine": "WEB_SEARCH_PRICE_ENRICHMENT_V1",
        "chat_id": chat_id,
        "topic_id": topic_id,
        "task_id": task_id,
        "raw_input": raw_input,
        "template_file": template.get("source_file_name"),
        "items": enriched,
        "created_at": _now(),
    }
    cache_file.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    msg = _price_prompt(cache)

    return _send_update_payload(conn, task_id, "WAITING_CLARIFICATION", msg, "")


async def maybe_handle_price_enrichment_from_template_engine(conn, task_id: str, chat_id: str, topic_id: int, raw_input: Any, input_type: str, reply_to_message_id=None) -> bool:
    fake = {
        "id": task_id,
        "chat_id": chat_id,
        "topic_id": topic_id,
        "input_type": input_type,
        "raw_input": _s(raw_input),
        "reply_to_message_id": reply_to_message_id,
    }
    res = await prehandle_price_task_v1(conn, fake)
    if not res or not res.get("handled"):
        return False
    try:
        from core.reply_sender import send_reply_ex
        bot = send_reply_ex(chat_id=str(chat_id), text=res.get("message") or "", reply_to_message_id=reply_to_message_id)
        bot_id = bot.get("bot_message_id") if isinstance(bot, dict) else None
    except Exception:
        bot_id = None

    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
        sets = ["state=?", "result=?", "error_message=?", "updated_at=datetime('now')"]
        vals = [res.get("state") or "WAITING_CLARIFICATION", res.get("message") or "", res.get("error_message") or ""]
        if bot_id and "bot_message_id" in cols:
            sets.append("bot_message_id=?")
            vals.append(bot_id)
        vals.append(task_id)
        conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
        conn.execute("INSERT INTO task_history (task_id,action,created_at) VALUES (?,?,datetime('now'))", (task_id, res.get("history") or "WEB_SEARCH_PRICE_ENRICHMENT_V1:HANDLED"))
        conn.commit()
    except Exception:
        pass
    return True


# === END_WEB_SEARCH_PRICE_ENRICHMENT_V1 ===
# === END_PRICE_CONFIRMATION_BEFORE_ESTIMATE_V1 ===
