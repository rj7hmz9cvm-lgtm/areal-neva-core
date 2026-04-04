import re, datetime
from core.price_manager import get_price
class EstimateData:
    def __init__(self, text, vat_enabled=True, overhead_rate=1.0):
        self.project_name = "Проект"
        self.sections = {"Материалы": [], "Оборудование": [], "Монтажные работы": [], "Транспортные расходы": [], "Прочее": []}
        self.missing_prices, self.vat_enabled, self.vat_rate, self.overhead_rate = [], vat_enabled, 0.22, overhead_rate
        self.subtotal = 0.0
        self._parse(text)
    def _parse(self, text):
        lines = text.split('\n')
        units = r'(м2|м3|пог\.\s*м|п\.м|шт|кг|т|м|компл|лист|рул|гкал|квт)'
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3: continue
            match = re.search(r'(\d+[.,]?\d*)\s*' + units, line, re.I)
            if match:
                qty, unit = float(match.group(1).replace(',', '.')), match.group(2)
                name = line[:match.start()].strip(" -:")
                p_match = re.search(r'(?:по|цена|—|-)\s*(\d+[.,]?\d*)', line)
                price, src = (float(p_match.group(1).replace(',', '.')), "input") if p_match else get_price(name)
                item = {"name": name, "unit": unit, "qty": qty, "price": price, "total": qty * price, "price_source": src}
                if price == 0: self.missing_prices.append(name)
                self.subtotal += item["total"]
                low = name.lower()
                if any(x in low for x in ['доставка', 'транспорт']): s = "Транспортные расходы"
                elif any(x in low for x in ['монтаж', 'работа']): s = "Монтажные работы"
                elif any(x in low for x in ['котел', 'насос']): s = "Оборудование"
                else: s = "Материалы"
                self.sections[s].append(item)
async def create_estimate_sheet(client, data, template_id=None):
    title = f"{datetime.date.today()}_Смета_{data.project_name}"
    sheet_id = client.safe_copy(template_id, title, mode='sheet')
    rows = [["№", "Раздел", "Наименование", "Ед", "Кол-во", "Цена", "Сумма"]]
    for s_name, items in data.sections.items():
        if not items: continue
        rows.append(["", s_name, "", "", "", "", ""])
        for it in items: rows.append(["", "", it["name"], it["unit"], it["qty"], it["price"], it["total"]])
    rows.append(["", "", "ИТОГО", "", "", "", data.subtotal])
    if data.vat_enabled: rows.append(["", "", "ВСЕГО (НДС 22%)", "", "", "", data.subtotal * 1.22])
    client.sheets.values().update(spreadsheetId=sheet_id, range="A1", valueInputOption="USER_ENTERED", body={"values": rows}).execute()
    client.share(sheet_id)
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}"
