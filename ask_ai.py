import os, requests, subprocess, sys, json
from datetime import datetime

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
user_input = " ".join(sys.argv[1:])

def ask_gemini(text):
    # Список всех возможных имен моделей на 2026 год
    models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": text}]}]}
    
    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_KEY}"
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                res = r.json()
                return res['candidates'][0]['content']['parts'][0]['text']
        except:
            continue
            
    return "Ошибка: Не удалось подобрать рабочую модель. Проверь баланс или лимиты ключа"

if not user_input:
    print("Ошибка: Введи вопрос")
    sys.exit()

print("Пробую разные модели...")
answer = ask_gemini(user_input)
print(f"\n--- ОТВЕТ ---\n{answer}")

log_file = "history.md"
with open(log_file, "a", encoding="utf-8") as f:
    f.write(f"\n\n## {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    f.write(f"**Вопрос:** {user_input}\n")
    f.write(f"### Ответ:\n{answer}\n---\n")

print("\n[Синхронизирую с GitHub...]")
subprocess.run(["git", "add", log_file], check=False)
subprocess.run(["git", "commit", "-m", "update history"], check=False)
subprocess.run(["git", "push"], check=False)
print("Готово")
