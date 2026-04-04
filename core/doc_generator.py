import datetime
def num_to_text(n):
    return f"{n:.2f} руб."
async def generate_google_doc(client, template_id, data):
    title = f"{datetime.date.today()}_Акт_{data.project_name}"
    doc_id = client.safe_copy(template_id, title, mode='doc')
    client.share(doc_id)
    return f"https://docs.google.com/document/d/{doc_id}/edit"
