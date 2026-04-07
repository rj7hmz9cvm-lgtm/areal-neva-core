#!/root/.areal-neva-core/.venv/bin/python3
import sys, json, multiprocessing, queue
def normalize_result(x):
    try:
        for _ in range(3):
            if isinstance(x, str):
                s = x.strip()
                if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
                    try: x = json.loads(s)
                    except: break
            if isinstance(x, dict): x = x.get("data", x); continue
            break
        if x is None or isinstance(x, (dict, list, tuple, set)): return "ERROR"
        s = str(x).strip()
        return s.replace("\n", " ").replace("\r", " ")[:1000] if s and "Traceback" not in s else "ERROR"
    except: return "ERROR"
def worker_func(p, q):
    try:
        from lib.orchestra_runtime import execute
        q.put(execute(p))
    except: q.put("ERROR")
def main():
    raw_in = sys.stdin.read(); prompt = raw_in.strip() if raw_in else ""
    if not prompt: print("ERROR", flush=True); return 0
    q = multiprocessing.Queue(); p = multiprocessing.Process(target=worker_func, args=(prompt, q))
    p.start()
    try:
        res = q.get(timeout=8.0); print(normalize_result(res), flush=True)
    except: print("ERROR", flush=True)
    finally:
        if p.is_alive(): p.terminate(); p.join(1.0)
    return 0
if __name__ == "__main__": sys.exit(main())
