#!/usr/bin/env python3
import os
import sys

BASE = os.path.expanduser("~/.areal-neva-core")
if os.path.exists("/app"):
    BASE = "/app"

if BASE not in sys.path:
    sys.path.insert(0, BASE)

LIB = os.path.join(BASE, "lib")
if os.path.isdir(LIB) and LIB not in sys.path:
    sys.path.insert(0, LIB)

def read_prompt() -> str:
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    return ""

def main() -> int:
    prompt = read_prompt()
    if not prompt:
        print("ERROR: empty prompt")
        return 1

    force_direct = os.getenv("ORCHESTRA_INTERNAL_DIRECT", "0") == "1" or os.path.exists("/.dockerenv")

    if force_direct:
        try:
            from orchestrator import execute
            result = execute(prompt)
            if result is None:
                print("ERROR: empty execute result")
                return 1
            print(str(result).strip())
            return 0
        except Exception as e:
            print(f"ERROR: direct execute failed: {e}")
            return 1

    try:
        import orchestra_runtime as rt
    except Exception as e:
        print(f"ERROR: import orchestra_runtime failed: {e} | BASE={BASE} | LIB={LIB} | PYTHONPATH={os.environ.get('PYTHONPATH','')}")
        return 1

    try:
        payload = rt.call_orchestrator(prompt)
        answer = rt.extract_answer(payload)
        if answer:
            print(str(answer).strip())
            return 0
        print("SKIP")
        return 1
    except Exception as e:
        print(f"ERROR: runtime orchestrator failed: {e}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
