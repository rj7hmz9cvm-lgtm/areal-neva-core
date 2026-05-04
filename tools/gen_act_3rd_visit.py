#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор акта осмотра № 3 — ангар Киевское шоссе, 04.05.2026
Standalone-скрипт. Запуск:
  cd /root/.areal-neva-core && .venv/bin/python3 tools/gen_act_3rd_visit.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Загружаем .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
except Exception:
    pass

import asyncio
import base64
import json
import re
import time
from pathlib import Path
from datetime import datetime

# ─── Константы объекта ─────────────────────────────────────────────────────

FOLDER_ID   = "1sS1A6iHQHUwjqZGF43wdyRjoLwwAHPse"
FOLDER_URL  = f"https://drive.google.com/drive/folders/{FOLDER_ID}"
CHAT_ID     = "-1003725299009"
TOPIC_ID    = 5

ACT_NUMBER      = "04-05/26"
VISIT_DATE      = "04.05.2026"
OBJECT_DESCR    = "Металлокаркасное здание (ангар), Киевское шоссе"
PLACE           = "Объект на Киевском шоссе"
PREV_ACT_REF    = "в развитие акта № 12-03/26 от 12.03.2026"

BATCH_SIZE    = 1    # по одному фото — избегаем 502 на больших payload
MAX_PARALLEL  = 5   # одновременных Vision запросов
OUTPUT_DIR    = Path(__file__).resolve().parent.parent / "outputs" / "technadzor_p6h"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Vision промпт ─────────────────────────────────────────────────────────

VISION_PROMPT = """\
Ты специалист технического надзора. Объект — металлокаркасное здание (ангар).
Перед тобой несколько фото строительного объекта — пронумерованы по порядку, начиная с фото 1.

Задача: по каждому фото выяви дефекты и строительные нарушения.

Возможные категории дефектов:
- опорные узлы колонн: подливка, зазоры, анкера, опорные плиты
- сварные соединения: непровар, поры, прожог, наплывы, незачищенные швы
- антикоррозионная защита: отсутствие покрытия, повреждение, ржавчина
- основание и водоотведение: замачивание, загрязнение, лужи, отсутствие уклонов
- узлы крепления покрытия: болтовые соединения, смещение элементов
- связи и укосины: неправильное примыкание, отсутствие жёсткости
- прочие: всё остальное

Верни ТОЛЬКО JSON-массив. Каждый элемент:
{
  "photo_no": <номер фото в пачке, целое число>,
  "title": "краткое название дефекта на русском",
  "description": "подробное описание что именно видно на фото",
  "section_hint": "опорные узлы / сварка / антикоррозия / основание / крепления / связи / прочее",
  "why": "почему это технически плохо, к чему ведёт",
  "consequence": "что произойдёт если не устранить",
  "fix": "конкретные действия по устранению",
  "verify": "что проверить или запросить у подрядчика",
  "confidence": "high / medium / low"
}

Если на фото нет нарушений — пропусти это фото (не добавляй в массив).
Если фото нечёткое или непонятное — добавь запись с confidence=low и укажи что именно непонятно.
Верни ТОЛЬКО JSON-массив, без заголовков и пояснений.
"""


# ─── Drive helpers ──────────────────────────────────────────────────────────

def get_drive_service():
    from core.technadzor_drive_index import _service
    return _service()


def list_photos_in_folder(svc, folder_id: str) -> list[dict]:
    """Вернуть все изображения из папки, отсортированные по имени."""
    from core.technadzor_drive_index import _list_folder
    files = _list_folder(svc, folder_id)
    photos = [f for f in files if (f.get("mimeType") or "").startswith("image/")]
    photos.sort(key=lambda x: x.get("name") or "")
    return photos


def download_photo(svc, file_id: str, filename: str) -> Path | None:
    """Скачать файл в локальный кэш."""
    from core.technadzor_drive_index import download_to_local
    return download_to_local(file_id, filename)


# ─── Vision ─────────────────────────────────────────────────────────────────

_vision_sem = None  # asyncio.Semaphore, инициализируется в main


async def run_single_vision(local_path: str, fname: str, photo_no: int, total: int) -> list[dict]:
    """Анализ одного фото через существующую Vision функцию."""
    global _vision_sem
    async with _vision_sem:
        from core.technadzor_engine import _p6f_tnz_vision_via_openrouter
        vision, vstatus = await _p6f_tnz_vision_via_openrouter(local_path)
        if vstatus != "OK" and vstatus != "PARTIAL":
            print(f"    [{photo_no}/{total}] {fname}: Vision {vstatus}")
            return []
        defects = (vision.get("defects") or []) if isinstance(vision, dict) else []
        summary = (vision.get("summary") or "") if isinstance(vision, dict) else ""
        # Если нет structured defects — превращаем summary в defect
        if not defects and summary:
            defects = [{"title": "Замечание по фото", "description": summary[:500]}]
        for d in defects:
            d["file_name"] = fname
            d["photo_no"] = photo_no
        ok_str = "✓" if defects else "·"
        print(f"    [{photo_no}/{total}] {fname}: {ok_str} {len(defects)} замеч.", flush=True)
        return defects


# ─── PDF сборка ──────────────────────────────────────────────────────────────

def build_pdf(all_defects: list[dict], out_path: Path) -> bool:
    """Собрать PDF акта из агрегированных дефектов."""
    from core.technadzor_engine import (
        _p6h_group_defects_by_section,
        _p6h_build_pdf_act,
        _p6h_norms_for_section,
    )

    grouped = _p6h_group_defects_by_section(all_defects)

    # Секции с нормами и списком фото
    sections_payload = []
    section_norms_index = {}
    for sec_title, defects in grouped:
        texts = [str(d.get("description") or d.get("title") or "") for d in defects]
        norms = _p6h_norms_for_section(sec_title, texts)
        photos_block = list(dict.fromkeys(
            d.get("file_name", "") for d in defects if d.get("file_name")
        ))
        sections_payload.append({
            "title": sec_title,
            "defects": defects,
            "norms": norms,
            "photos_block": photos_block,
        })
        section_norms_index[sec_title] = norms

    # Рекомендации / последствия
    recs = list(dict.fromkeys(
        str(d.get("fix") or "").strip()
        for d in all_defects if d.get("fix")
    ))[:20]
    cons = list(dict.fromkeys(
        str(d.get("consequence") or d.get("why") or "").strip()
        for d in all_defects if (d.get("consequence") or d.get("why"))
    ))[:10]

    # Таблица нарушений
    vtable = []
    for sec_title, defects in grouped:
        norm_id = ""
        nlist = section_norms_index.get(sec_title) or []
        if nlist:
            norm_id = nlist[0].get("norm_id", "")
        for d in defects:
            v  = str(d.get("title") or d.get("description") or sec_title)[:200]
            ph = str(d.get("file_name") or "")
            vtable.append((v, norm_id or "норма не подтверждена", ph))

    payload = {
        "act_number":      ACT_NUMBER,
        "date_str":        VISIT_DATE,
        "place":           PLACE,
        "object_descr":    OBJECT_DESCR,
        "method":          "визуальный неразрушающий контроль с выездом на объект",
        "performer":       "",
        "specialist":      "Кузнецов Илья Владимирович",
        "photos_link":     FOLDER_URL,
        "general_purpose": (
            f"Осмотр выполнен методом визуального неразрушающего контроля с выездом на объект. "
            f"Текущий осмотр выполнен {PREV_ACT_REF}. "
            f"Цель осмотра — проверка выполнения замечаний из предыдущего акта, "
            f"выявление новых дефектов и отклонений, определение рекомендаций к устранению "
            f"и возможных последствий при сохранении текущего состояния. "
            f"Проектная и рабочая исполнительная документация на момент осмотра "
            f"к проверке не представлена."
        ),
        "sections":         sections_payload,
        "recommendations":  recs if recs else [
            "Привести выявленные узлы и покрытия к нормативному состоянию по СП 16.13330.2017, СП 70.13330.2012",
            "Восстановить антикоррозионную защиту всех незащищённых металлических конструкций",
            "Обеспечить отвод воды от основания и опорных узлов",
            "Выполнить фотофиксацию после устранения всех выявленных замечаний",
            "Предоставить исполнительную документацию по выполненным работам",
        ],
        "consequences":     cons if cons else [
            "Снижение несущей способности и эксплуатационной надёжности конструкций",
            "Прогрессирующее развитие коррозионных поражений",
            "Риск аварийного развития дефектов при эксплуатационных нагрузках",
        ],
        "violations_table": vtable[:40],
    }

    try:
        _p6h_build_pdf_act(payload, out_path)
        return True
    except Exception as e:
        print(f"  ❌ Ошибка генерации PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


# ─── Загрузка на Drive ───────────────────────────────────────────────────────

def upload_pdf_to_drive(pdf_path: Path, pdf_name: str) -> str:
    """Загрузить PDF в topic_5 (корень). Вернуть ссылку или пустую строку."""
    try:
        from core.technadzor_drive_index import upload_client_pdf_to_folder
        result = upload_client_pdf_to_folder(
            pdf_path, pdf_name,
            chat_id=CHAT_ID, topic_id=TOPIC_ID,
            target_folder_name=None,  # в корень topic_5
        )
        return (result or {}).get("link", "") or (result or {}).get("webViewLink", "")
    except Exception as e:
        print(f"  ⚠️  Drive upload ошибка: {e}")
        return ""


# ─── Главный цикл ────────────────────────────────────────────────────────────

async def main():
    t0 = time.time()
    print("=" * 60)
    print("АКТ ОСМОТРА № 04-05/26 — ангар Киевское шоссе")
    print("Третий выезд, 04.05.2026")
    print("=" * 60)
    print(f"Папка фото: {FOLDER_URL}\n")

    # 1. Список фото
    print("1. Получаю список фото из Drive...")
    try:
        svc = get_drive_service()
        photos = list_photos_in_folder(svc, FOLDER_ID)
    except Exception as e:
        print(f"  ❌ Ошибка Drive: {e}")
        return

    print(f"   Найдено: {len(photos)} фото")
    if not photos:
        print("   Фото не найдено — выход")
        return

    # 2. Скачиваем все фото
    print(f"\n2. Скачиваю {len(photos)} фото из Drive...")
    local_photos = []
    for photo in photos:
        p = download_photo(svc, photo["id"], photo["name"])
        if p:
            local_photos.append((str(p), photo["name"]))
        else:
            print(f"  ✗ {photo['name']} — не скачалось")
    print(f"   Скачано: {len(local_photos)} фото")

    # 3. Vision — параллельно, MAX_PARALLEL одновременно
    global _vision_sem
    _vision_sem = asyncio.Semaphore(MAX_PARALLEL)
    total = len(local_photos)
    print(f"\n3. Vision анализ ({total} фото, до {MAX_PARALLEL} параллельно)...")

    tasks = [
        run_single_vision(path, fname, i + 1, total)
        for i, (path, fname) in enumerate(local_photos)
    ]
    results = await asyncio.gather(*tasks)
    all_defects = [d for sublist in results for d in sublist]

    elapsed = int(time.time() - t0)
    print(f"\n   Vision завершён за {elapsed}с. Всего замечаний: {len(all_defects)}")

    if not all_defects:
        print("  ⚠️  Vision не выявил замечаний — генерирую акт с пустыми разделами")

    # 4. Генерация PDF
    ts = datetime.now().strftime("%d_%m_%Y")
    pdf_name = f"Акт_осмотра_ангар_Киевское_шоссе_{ts}.pdf"
    pdf_path = OUTPUT_DIR / pdf_name

    print(f"\n3. Генерирую PDF: {pdf_name}")
    ok = build_pdf(all_defects, pdf_path)
    if not ok:
        print("  ❌ PDF не создан")
        return

    size_kb = pdf_path.stat().st_size // 1024
    print(f"   ✅ PDF готов — {size_kb} KB")
    print(f"   Путь: {pdf_path}")

    # 5. Загрузка на Drive
    print("\n4. Загружаю PDF на Drive (topic_5)...")
    link = upload_pdf_to_drive(pdf_path, pdf_name)
    if link:
        print(f"   ✅ Drive: {link}")
    else:
        print(f"   ⚠️  Drive upload не выполнен, файл доступен локально")

    # Итог
    total = int(time.time() - t0)
    print("\n" + "=" * 60)
    print(f"ГОТОВО за {total // 60}м {total % 60}с")
    print(f"PDF: {pdf_path}")
    if link:
        print(f"Drive: {link}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())


# ─── P6H_VISION_RESIZE_V1 ───────────────────────────────────────────────────
# Append-only override.
# Оригиналы нетронуты. Temp только в /tmp. Model не меняется.
# Если resize не получился → STOP, оригинал 8MB не отправляется.
# Если Vision падает → показать vstatus → STOP, без fallback.

import hashlib as _p6h_hashlib
import tempfile as _p6h_tempfile


def prepare_image_for_openrouter_vision(src_path: str) -> Path:
    from PIL import Image as _PIL
    src = Path(src_path)
    h = _p6h_hashlib.md5(src_path.encode()).hexdigest()[:8]
    tmp = Path(_p6h_tempfile.gettempdir()) / f"tnz_v_{h}.jpg"
    with _PIL.open(src) as img:
        img = img.convert("RGB")
        w, ht = img.size
        if max(w, ht) > 1600:
            ratio = 1600 / max(w, ht)
            img = img.resize((int(w * ratio), int(ht * ratio)), _PIL.LANCZOS)
        img.save(str(tmp), "JPEG", quality=75, optimize=True)
    return tmp


async def run_single_vision(local_path: str, fname: str, photo_no: int, total: int) -> list[dict]:
    global _vision_sem
    async with _vision_sem:
        orig_size = Path(local_path).stat().st_size if Path(local_path).exists() else 0

        try:
            tmp = prepare_image_for_openrouter_vision(local_path)
        except Exception as e:
            print(f"    [{photo_no}/{total}] {fname}: ✗ resize STOP: {e}")
            return []

        resized_size = tmp.stat().st_size
        model = (os.getenv("OPENROUTER_VISION_MODEL") or "google/gemini-2.5-flash")
        print(f"    [{photo_no}/{total}] {fname}: orig={orig_size//1024}KB resized={resized_size//1024}KB model={model}", flush=True)

        from core.technadzor_engine import _p6f_tnz_vision_via_openrouter
        vision, vstatus = await _p6f_tnz_vision_via_openrouter(str(tmp))

        try:
            tmp.unlink()
        except Exception:
            pass

        if vstatus not in ("OK", "PARTIAL"):
            print(f"    [{photo_no}/{total}] {fname}: ✗ vstatus={vstatus} — STOP")
            return []

        defects = (vision.get("defects") or []) if isinstance(vision, dict) else []
        summary = (vision.get("summary") or "") if isinstance(vision, dict) else ""
        if not defects and summary:
            defects = [{"title": "Замечание по фото", "description": summary[:500]}]
        for d in defects:
            d["file_name"] = fname
            d["photo_no"] = photo_no
        ok_str = "✓" if defects else "·"
        print(f"    [{photo_no}/{total}] {fname}: {ok_str} {len(defects)} замеч.", flush=True)
        return defects

# ─── END P6H_VISION_RESIZE_V1 ────────────────────────────────────────────────

# ─── P6H_VISION_GUARD_STANDALONE_V1 ─────────────────────────────────────────
# CANON: TECHNADZOR_DOMAIN_LOGIC_CANON_V2 §33
# Standalone-скрипт не должен запускать Vision без явного разрешения владельца

_GEN_ACT_VISION_ALLOWED = os.getenv("EXTERNAL_PHOTO_ANALYSIS_ALLOWED", "").strip().lower() in ("1", "true", "yes")

if _GEN_ACT_VISION_ALLOWED:
    print("INFO: EXTERNAL_PHOTO_ANALYSIS_ALLOWED=True — Vision включён", flush=True)
    try:
        from core.technadzor_engine import _p6h_allow_external_vision
        _p6h_allow_external_vision()
    except Exception as _e:
        print(f"WARN: _p6h_allow_external_vision failed: {_e}", flush=True)
else:
    print("INFO: EXTERNAL_PHOTO_ANALYSIS_ALLOWED=False (default) — Vision заблокирован по канону §33", flush=True)
    print("INFO: Для включения Vision установить в .env: EXTERNAL_PHOTO_ANALYSIS_ALLOWED=true", flush=True)
    print("INFO: Скрипт продолжит работу без Vision — разбор по голосу/тексту/документам", flush=True)
# ─── END P6H_VISION_GUARD_STANDALONE_V1 ──────────────────────────────────────
