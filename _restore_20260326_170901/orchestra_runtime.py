import sys,traceback
sys.path.insert(0,"/root/.areal-neva-core")

def execute(task):
    try:
        from router import route_and_execute
        return route_and_execute(task)
    except Exception as e:
        return "failed", f"RUNTIME_ERROR:{e}\n{traceback.format_exc()}"
