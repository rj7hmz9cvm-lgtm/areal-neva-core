from executors.pdf_executor import create_pdf

def run_pdf(query):
    q = query.replace("[PDF]", "").strip()
    filename = create_pdf("PDF REPORT\n\n" + q, "outputs/result.pdf")
    return "PDF создан\n\n" + filename
