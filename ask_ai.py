import os
import subprocess
from datetime import datetime
from orchestrator import execute

BASE = os.path.expanduser("~/.areal-neva-core")
HISTORY = os.path.join(BASE, "history.md")
OUTPUTS = os.path.join(BASE, "outputs")

def log_history(prompt, answer):
    os.makedirs(BASE, exist_ok=True)
    with open(HISTORY, "a", encoding="utf-8") as f:
        f.write("\n\n")
        f.write("## " + str(datetime.now()) + "\n")
        f.write("TASK:\n")
        f.write(prompt + "\n\n")
        f.write("RESULT:\n")
        f.write(answer + "\n")

def save_result_file(prompt, answer):
    os.makedirs(OUTPUTS, exist_ok=True)

    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    mode = "general"
    if prompt.strip().startswith("["):
        try:
            mode = prompt.strip().split("]")[0].replace("[", "").lower()
        except Exception:
            pass

    filename = os.path.join(OUTPUTS, f"{stamp}_{mode}_result.txt")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("TASK:\n")
        f.write(prompt + "\n\n")
        f.write("RESULT:\n")
        f.write(answer + "\n")

    return filename

def git_sync():
    subprocess.run(["git", "add", "-A"], cwd=BASE, check=False)
    subprocess.run(["git", "commit", "-m", "auto: orchestra task result"], cwd=BASE, check=False)
    subprocess.run(["git", "push"], cwd=BASE, check=False)

def main():
    prompt = input("TASK > ").strip()

    if not prompt:
        print("Пустая задача")
        return

    result = execute(prompt)

    print("")
    print(result)

    log_history(prompt, result)
    file_path = save_result_file(prompt, result)

    print("\nRESULT_FILE:")
    print(file_path)

    try:
        git_sync()
        print("\nGIT_SYNC: OK")
    except Exception:
        print("\nGIT_SYNC: FAIL")

    os.system("open ~/.areal-neva-core/outputs")

if __name__ == "__main__":
    main()
