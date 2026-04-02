import json
import os
import sys
import sqlite3
import logging

sys.path.append("/root/.areal-neva-core")

AUDIO_EXTS = (".ogg", ".mp3", ".wav", ".m4a")
VISION_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".pdf")
DWG_EXTS = (".dxf", ".dwg")
DB_PATH = "/root/.areal-neva-core/orchestra.db"

class Router:

    def _get_context_file(self, chat_id):
        if not chat_id: return None
        try:
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("""
                SELECT path 
                FROM tasks 
                WHERE chat_id = ? AND path IS NOT NULL AND status != 'error'
                ORDER BY id DESC 
                LIMIT 1
            """, (str(chat_id),)).fetchone()
            conn.close()
            if row and row[0]:
                path = row[0]
                if path.lower().endswith(VISION_EXTS):
                    return path
            return None
        except Exception as e:
            logging.error(f"Context lookup error: {e}")
            return None

    def _normalize_payload(self, task):
        payload = task.get("payload") or {}
        if isinstance(payload, str):
            try: payload = json.loads(payload)
            except: payload = {"text": payload}
        if not isinstance(payload, dict):
            payload = {"text": str(payload)}
        return payload

    def _route_text(self, text):
        t = (text or "").lower().strip()

        # 1. НОРМАТИВКА
        if any(x in t for x in ["сп", "гост", "снип", "норматив", "допуск"]):
            from normative_engine import NormativeEngine
            return NormativeEngine().process(text)

        # 2. ЛИДЫ / БРИГАДЫ
        if any(x in t for x in ["бригада", "монолит", "бетон", "куб", "работа"]):
            from lead_engine import LeadEngine
            return LeadEngine().process(text)

        # 3. ПОИСК ЦЕН
        if any(x in t for x in ["цена", "стоимость", "сколько"]):
            from web_engine import WebEngine
            return WebEngine().search(text)

        # 4. ФОЛЛБЭК
        return {
            "status": "done",
            "engine": "core",
            "data": "[DRAFT - Требует проверки специалистом]\nЗадача не распознана. Уточни запрос."
        }

    def route_and_execute(self, task):
        payload = self._normalize_payload(task)
        text = str(payload.get("text", "")).strip()
        path = str(payload.get("path", "")).strip().lower()
        chat_id = task.get("chat_id")

        # ===== 1. VOICE PROCESSING =====
        if path.endswith(AUDIO_EXTS):
            from voice_engine import VoiceEngine
            vr = VoiceEngine().transcribe(payload.get("path")) 
            transcript = str(vr.get("text", "")).strip()
            
            if not transcript:
                return {"status": "error", "engine": "voice", "data": "Ошибка: Голос не распознан"}
            
            t_lower = transcript.lower()

            # --- CONTEXT LOOKUP FOR VOLUMES/OCR FROM VOICE ---
            if any(x in t_lower for x in ["объем", "распозна", "вытащи", "таблиц", "ocr", "картинк", "файл"]):
                context_file = self._get_context_file(chat_id)
                if context_file:
                    from vision_engine import VisionEngine
                    res = VisionEngine().process(context_file, transcript)
                    res["data"] = f"🎤 Распознано: {transcript}\n\n📄 Взят файл из истории: {os.path.basename(context_file)}\n\n{res.get('data', '')}"
                    return res

            # Если контекст не нужен - обычный рутинг текста
            routed = self._route_text(transcript)
            routed["data"] = f"🎤 Распознано: {transcript}\n\n{routed.get('data', '')}"
            return routed

        # ===== 2. VISION PRIORITY (Фото + PDF) =====
        if path.endswith(VISION_EXTS):
            from vision_engine import VisionEngine
            return VisionEngine().process(payload.get("path"), text)

        # ===== 3. DWG PRIORITY (Чертежи) =====
        if path.endswith(DWG_EXTS):
            from dwg_engine import DWGEngine
            return DWGEngine().process(payload.get("path"))

        # ===== 4. TEXT ROUTING =====
        return self._route_text(text)
