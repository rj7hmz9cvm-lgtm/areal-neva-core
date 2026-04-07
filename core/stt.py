import whisper, os
model = whisper.load_model("base")
def transcribe(path):
    res = model.transcribe(path, fp16=False, language='ru')
    return res.get("text", "").strip()
