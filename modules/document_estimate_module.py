from modules.document_module import run as d_run
from modules.estimate_module import run as e_run

def run(ctx):
    return e_run({"text": d_run(ctx).get("text", "")})
