# AREAL-NEVA CORE — LIVE STATE

## TELEGRAM AGENT
- group_bot.py: ACTIVE (long polling)
- Voice: ENABLED (Groq Whisper)
- Text: ENABLED
- Logging: ENABLED → /root/AI_ORCHESTRA/telegram

## MODELS
- DeepSeek: MAIN (OpenRouter)
- Claude: AVAILABLE
- Gemini: AVAILABLE
- Grok: AVAILABLE
- OpenAI: AVAILABLE

## VOICE PIPELINE
Telegram → Whisper (Groq) → text → DeepSeek → response

## STORAGE PIPELINE
Telegram → /root/AI_ORCHESTRA/telegram → rclone → Google Drive → Mac

## STATUS
- Voice: OK
- Text: OK
- Logging: OK
- Sync: OK

## NOTES
- webhook DISABLED
- group_bot is single active entrypoint
- system stable
