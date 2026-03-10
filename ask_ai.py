import os
import subprocess
from datetime import datetime
from orchestrator import execute

BASE = os.path.expanduser("~/.areal-neva-core")
HISTORY = os.path.join(BASE, "history.md")

def log_history(prompt, answer):
    with open(HISTORY, "a", encoding="utf-8") as f:
        f.write("\n\n")
        f.write("## " + str(datetime.now()) + "\n")
        f.write("TASK:\n")
        f.write(prompt + "\n\n")
        f.write("RESULT:\n")
        f.write(answer + "\n")

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

    try:
        git_sync()
        print("\nGIT_SYNC: OK")
    except Exception:
        print("\nGIT_SYNC: FAIL")

if __name__ == "__main__":
    main()
