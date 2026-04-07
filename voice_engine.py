import os
import httpx
import logging

logger = logging.getLogger("voice_engine")

async def transcribe_voice(task_id, file_path):
    api_key = os.getenv("GROQ_API_KEY")
    url = os.getenv("AUDIO_API_BASE_URL")
    model = os.getenv("AUDIO_API_MODEL", "whisper-large-v3-turbo")

    if not api_key:
        logger.error("GROQ_API_KEY missing in .env")
        return "ERROR: No Groq API Key"

    async with httpx.AsyncClient() as client:
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f)}
                data = {"model": model, "response_format": "text"}
                headers = {"Authorization": f"Bearer {api_key}"}
                
                response = await client.post(url, headers=headers, files=files, data=data, timeout=60.0)
                
                if response.status_code == 200:
                    text = response.text.strip()
                    logger.info(f"Transcription success for {task_id}")
                    return text
                else:
                    logger.error(f"STT Error {response.status_code}: {response.text}")
                    return f"ERROR: STT failed ({response.status_code})"
        except Exception as e:
            logger.error(f"Voice engine crash: {str(e)}")
            return f"ERROR: {str(e)}"
