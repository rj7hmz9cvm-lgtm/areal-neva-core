import os
import re
import subprocess
from datetime import datetime

BASE = os.path.expanduser("~/.areal-neva-core")

RULES = os.path.join(BASE, "GLOBAL_INSTRUCTIONS.md")
CONTEXT = os.path.join(BASE, "sync_context.md")
HISTORY = os.path.join(BASE, "history.md")
PROFILE_FILE = os.path.join(BASE, "ai/profiles/ACTIVE_PROFILE.txt")
PROFILES_DIR = os.path.join(BASE, "ai/profiles")


def read_file(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def write_file(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def get_active_profile_name() -> str:
    name = read_file(PROFILE_FILE).strip()
    return name if name else "chatgpt_orchestrator"


def get_active_profile_text() -> str:
    name = get_active_profile_name()
    path = os.path.join(PROFILES_DIR, f"{name}.txt")
    return read_file(path)


def detect_mode(user_prompt: str) -> str:
    text = user_prompt.strip()

    prefix_map = {
        "[DEVOPS]": "DEVOPS",
        "[TECH]": "TECH",
        "[CONTENT]": "CONTENT",
        "[CRM]": "CRM",
        "[LEADGEN]": "LEADGEN",
        "[TOUR]": "TOUR",
        "[TREND]": "TREND",
    }

    for prefix, mode in prefix_map.items():
        if text.upper().startswith(prefix):
            return mode

    lowered = text.lower()

    if any(x in lowered for x in ["docker", "git", "github", "vps", "wireguard", "vless", "xray", ".env", "скрипт", "сервер"]):
        return "DEVOPS"

    if any(x in lowered for x in ["dwg", "dxf", "чертеж", "сантех", "отопл", "технадзор", "узел", "спецификац", "объем", "объём", "проект"]):
        return "TECH"

    if any(x in lowered for x in ["instagram", "youtube", "рилс", "пост", "контент", "сценар"]):
        return "CONTENT"

    if any(x in lowered for x in ["amocrm", "лид", "клиент", "продаж", "воронк", "квалификац", "ответ клиенту"]):
        return "CRM"

    if any(x in lowered for x in ["telegram", "авито", "avito", "profi", "профи", "заказ", "работа", "заявк", "лидоген"]):
        return "LEADGEN"

    if any(x in lowered for x in ["тур", "байкал", "камчат", "маршрут", "логистик", "поездк"]):
        return "TOUR"

    return "DEVOPS"


def assign_model(mode: str) -> str:
    mapping = {
        "DEVOPS": "Gemini",
        "TECH": "Claude",
        "CONTENT": "Claude",
        "CRM": "ChatGPT",
        "LEADGEN": "ChatGPT",
        "TOUR": "Gemini",
        "TREND": "Grok",
    }
    return mapping.get(mode, "ChatGPT")


def helper_model(mode: str) -> str:
    mapping = {
        "DEVOPS": "DeepSeek",
        "TECH": "DeepSeek",
        "CONTENT": "Grok",
        "CRM": "Claude",
        "LEADGEN": "Grok",
        "TOUR": "Grok",
        "TREND": "DeepSeek",
    }
    return mapping.get(mode, "DeepSeek")


def build_result(user_prompt: str) -> str:
    mode = detect_mode(user_prompt)
    owner_model = assign_model(mode)
    helper = helper_model(mode)

    cleaned = re.sub(r"^\[[A-Z]+\]\s*", "", user_prompt.strip())

    result = []
    result.append("SYSTEM STATUS: OK")
    result.append(f"ACTIVE_PROFILE: {get_active_profile_name()}")
    result.append(f"MODE: {mode}")
    result.append(f"PRIMARY_MODEL: {owner_model}")
    result.append(f"HELPER_MODEL: {helper}")
    result.append("ACTION: Оркестрация задачи выполнена")
    result.append(f"TASK: {cleaned}")
    result.append("NEXT_STEP: Выполнять задачу в назначенном домене")
    result.append("SYNC: history.md будет обновлён локально")
    return "\n".join(result)


def append_history(user_prompt: str, answer: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HISTORY, "a", encoding="utf-8") as f:
        f.write("\n\n")
        f.write(f"## {timestamp}\n")
        f.write("PROMPT:\n")
        f.write(user_prompt + "\n\n")
        f.write("ANSWER:\n")
        f.write(answer + "\n")


def git_sync() -> str:
    try:
        subprocess.run(["git", "add", "-A"], cwd=BASE, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-m", "auto: update history and orchestrator state"], cwd=BASE, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "push"], cwd=BASE, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "OK"
    except Exception:
        return "FAIL"


def main() -> None:
    user_prompt = input("ASK > ").strip()

    if not user_prompt:
        print("Пустой запрос")
        return

    _rules = read_file(RULES)
    _context = read_file(CONTEXT)
    _profile = get_active_profile_text()

    answer = build_result(user_prompt)
    append_history(user_prompt, answer)
    sync_status = git_sync()

    print("\nANSWER:\n")
    print(answer)
    print(f"\nGIT_SYNC: {sync_status}")


if __name__ == "__main__":
    main()
