import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import cv2

class VisionEngine:

    def _ocr_image(self, path):
        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        text = pytesseract.image_to_string(thresh, lang='rus+eng')
        return text.strip()

    def _ocr_pdf(self, path):
        pages = convert_from_path(path, dpi=300)
        texts = []
        for i, page in enumerate(pages[:10]):
            tmp = f"/tmp/page_{i}.jpg"
            page.save(tmp, "JPEG")
            texts.append(self._ocr_image(tmp))
            os.remove(tmp)
        return "\n\n".join(texts)

    def process(self, path, text=""):
        if not os.path.exists(path):
            return {"status":"error","engine":"vision","data":"file_not_found"}

        ext = path.lower().split(".")[-1]

        try:
            if ext in ["jpg","jpeg","png"]:
                text_res = self._ocr_image(path)

            elif ext == "pdf":
                text_res = self._ocr_pdf(path)

            else:
                return {"status":"error","engine":"vision","data":"unsupported_format"}

            prefix = "[DRAFT - Требует проверки специалистом]\n[OCR]\n\n"

            if not text_res.strip():
                return {"status":"done","engine":"vision","data": prefix + "ТЕКСТ НЕ ОБНАРУЖЕН"}

            return {
                "status":"done",
                "engine":"vision",
                "data": prefix + text_res[:4000]
            }

        except Exception as e:
            return {"status":"error","engine":"vision","data":str(e)}
