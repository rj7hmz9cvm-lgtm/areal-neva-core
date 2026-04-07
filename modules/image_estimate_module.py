from modules.image_ocr_module import run as i_run
from modules.estimate_module import run as e_run

def run(ctx):
    return e_run({"text": i_run(ctx).get("text", "")})
