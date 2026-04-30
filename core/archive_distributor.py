# === ARCHIVE_DISTRIBUTOR_V1 ===
# Читает timeline.jsonl → определяет топик → раскладывает в memory.db
import json, os, re, logging, sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

BASE = Path("/root/.areal-neva-core")
MEM_DB = str(BASE / "data/memory.db")
CHAT_ID = "-1003725299009"

# Сигнатуры топиков по контенту
_TOPIC_SIGNATURES = {
    2:    ["стройк", "смет", "кровл", "фасад", "фундамент", "металлочерепиц", "профнастил",
           "ангар", "бетон", "арматур", "утеплитель", "монтаж", "кж", "ар ", "кд "],
    5:    ["технадзор", "дефект", "акт осмотр", "нарушени", "предписани", "сп ", "гост", "снип",
           "инспекц", "фото дефект"],
    500:  ["найди", "поищи", "цена", "стоимость", "avito", "ozon", "wildberries", "поставщик",
           "купить", "маркет", "ral", "профлист"],
    961:  ["toyota", "hiace", "запчаст", "brembo", "авто", "машин", "vin", "oem", "разборк",
           "двигател", "подвеск"],
    3008: ["код", "python", "патч", "функци", "верификац", "архитектур", "task_worker",
           "telegram_daemon", "оркестр"],
}

def _detect_topic(text: str) -> int:
    low = text.lower()
    scores = {}
    for topic_id, keywords in _TOPIC_SIGNATURES.items():
        scores[topic_id] = sum(1 for kw in keywords if kw in low)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else 0  # 0 = общий

def _ensure_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory
        (chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)
    """)

def distribute_timeline(timeline_path: str, chat_id: str = CHAT_ID, dry_run: bool = False) -> dict:
    """
    Читает timeline.jsonl → раскладывает записи в memory.db по топикам.
    Возвращает статистику.
    """
    p = Path(timeline_path)
    if not p.exists():
        return {"ok": False, "reason": "FILE_NOT_FOUND"}

    conn = sqlite3.connect(MEM_DB)
    conn.row_factory = sqlite3.Row
    _ensure_table(conn)

    stats = {"total": 0, "distributed": 0, "skipped": 0, "by_topic": {}}
    seen_keys = set()

    with open(p, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue

            stats["total"] += 1

            # Собираем текст для классификации
            text_parts = []
            for field in ["text", "message", "content", "result", "raw_input", "value"]:
                v = entry.get(field)
                if v and isinstance(v, str):
                    text_parts.append(v)
            text = " ".join(text_parts)[:2000]

            if not text or len(text) < 20:
                stats["skipped"] += 1
                continue

            # Определяем топик
            topic_id = _detect_topic(text)

            # Формируем ключ
            ts = entry.get("timestamp") or entry.get("ts") or entry.get("created_at") or "2026"
            ts_short = str(ts)[:10].replace("-", "")
            dedup_key = f"topic_{topic_id}_archive_{ts_short}_{hash(text) % 100000}"

            if dedup_key in seen_keys:
                stats["skipped"] += 1
                continue
            seen_keys.add(dedup_key)

            value = text[:5000]

            if not dry_run:
                # Проверяем нет ли уже такой записи
                existing = conn.execute(
                    "SELECT 1 FROM memory WHERE chat_id=? AND key=?",
                    (chat_id, dedup_key)
                ).fetchone()
                if not existing:
                    conn.execute(
                        "INSERT INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, ?)",
                        (chat_id, dedup_key, value, str(ts)[:19])
                    )

            stats["distributed"] += 1
            stats["by_topic"][topic_id] = stats["by_topic"].get(topic_id, 0) + 1

    if not dry_run:
        conn.commit()
    conn.close()

    return {"ok": True, **stats}

def run_distribution(chat_id: str = CHAT_ID) -> dict:
    """Запустить распределение для всех timeline.jsonl чата"""
    results = {}
    chats_dir = BASE / "data/memory_files/CHATS"
    if not chats_dir.exists():
        return {"ok": False, "reason": "NO_CHATS_DIR"}

    for chat_dir in chats_dir.iterdir():
        if not chat_dir.is_dir():
            continue
        timeline = chat_dir / "timeline.jsonl"
        if timeline.exists():
            r = distribute_timeline(str(timeline), chat_id=chat_id)
            results[str(timeline)] = r
            logger.info("ARCHIVE_DISTRIBUTED file=%s stats=%s", timeline, r)

    return {"ok": True, "files": results}

def _load_archive_for_topic(chat_id: str, topic_id: int, user_text: str = "", limit: int = 5) -> str:
    """
    Загрузить архивный контекст для топика из memory.db.
    Используется в _load_archive_context.
    """
    if not os.path.exists(MEM_DB):
        return ""
    conn = sqlite3.connect(MEM_DB)
    conn.row_factory = sqlite3.Row
    try:
        _ensure_table(conn)
        key_pattern = f"topic_{topic_id}_archive_%"
        rows = conn.execute(
            """SELECT key, value FROM memory
               WHERE chat_id=? AND key GLOB ?
               ORDER BY timestamp DESC LIMIT ?""",
            (str(chat_id), key_pattern, limit * 3)
        ).fetchall()

        if not rows:
            return ""

        # Фильтрация по релевантности если есть запрос
        if user_text:
            query_words = set(w for w in user_text.lower().split() if len(w) > 3)
            scored = []
            for row in rows:
                val = str(row["value"]).lower()
                score = sum(1 for w in query_words if w in val)
                scored.append((score, str(row["value"])[:500]))
            scored.sort(reverse=True)
            relevant = [v for s, v in scored if s > 0][:limit]
        else:
            relevant = [str(r["value"])[:500] for r in rows[:limit]]

        return "\n---\n".join(relevant) if relevant else ""
    except Exception as e:
        logger.warning("ARCHIVE_LOAD_ERR topic=%s err=%s", topic_id, e)
        return ""
    finally:
        conn.close()

if __name__ == "__main__":
    print("Running archive distribution...")
    result = run_distribution()
    print(json.dumps(result, ensure_ascii=False, indent=2))
# === END ARCHIVE_DISTRIBUTOR_V1 ===
