import re
import json
from pathlib import Path

# --- helpers ---
def parse_money(s: str) -> float:
    """
    Converts money like '1 200,00' or '308,00' to float: 1200.00 / 308.00
    """
    s = s.strip().replace(" ", "").replace("\xa0", "")
    s = s.replace(",", ".")
    return float(s)

def find_first(pattern: str, text: str, flags=0):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else None

# --- main parsing ---
def parse_receipt(text: str) -> dict:
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Header fields
    branch = find_first(r"^Филиал\s+(.+)$", text, flags=re.MULTILINE)
    bin_num = find_first(r"^БИН\s+(\d+)$", text, flags=re.MULTILINE)
    receipt_no = find_first(r"^Чек\s+№(\d+)$", text, flags=re.MULTILINE)
    cashier = find_first(r"^Кассир\s+(.+)$", text, flags=re.MULTILINE)

    # Date-time
    dt = find_first(r"^Время:\s*([0-9]{2}\.[0-9]{2}\.[0-9]{4}\s+[0-9]{2}:[0-9]{2}:[0-9]{2})$",
                    text, flags=re.MULTILINE)

    # Address (in your чек it is one line)
    address = find_first(r"^(г\.\s*Нур\-султан.+)$", text, flags=re.MULTILINE)

    # Payment method + paid amount
    # In your чек: 'Банковская карта:\n18 009,00'
    payment_method = None
    payment_amount = None
    m_pay = re.search(r"^(Банковская карта):\s*\n([\d \xa0]+,\d{2})$",
                      text, flags=re.MULTILINE)
    if m_pay:
        payment_method = m_pay.group(1)
        payment_amount = parse_money(m_pay.group(2))

    # Total
    total = None
    m_total = re.search(r"^ИТОГО:\s*\n([\d \xa0]+,\d{2})$",
                        text, flags=re.MULTILINE)
    if m_total:
        total = parse_money(m_total.group(1))

    # VAT (optional)
    vat = None
    m_vat = re.search(r"^в т\.ч\.\s+НДС\s+\d+%:\s*\n([\d \xa0]+,\d{2})$",
                      text, flags=re.MULTILINE)
    if m_vat:
        vat = parse_money(m_vat.group(1))

    # ---- Items parsing (your чек имеет стабильный блок) ----
    # Structure per item in your raw.txt:
    # 1.
    # <NAME>
    # 2,000 x 154,00
    # 308,00
    # Стоимость
    # 308,00
    item_pattern = re.compile(
        r"(?m)^\s*(\d+)\.\s*\n"                 # item number
        r"(.+?)\n"                              # name (one line)
        r"([\d \xa0]+,\d{3})\s*x\s*([\d \xa0]+,\d{2})\n"  # qty x unit
        r"([\d \xa0]+,\d{2})\n"                 # line total
        r"Стоимость\n"
        r"([\d \xa0]+,\d{2})",                  # repeated cost
        flags=re.MULTILINE
    )

    items = []
    for m in item_pattern.finditer(text):
        idx = int(m.group(1))
        name = m.group(2).strip()
        qty = parse_money(m.group(3))           # qty looks like 2,000
        unit_price = parse_money(m.group(4))
        line_total = parse_money(m.group(5))
        cost = parse_money(m.group(6))

        items.append({
            "pos": idx,
            "name": name,
            "qty": qty,
            "unit_price": unit_price,
            "line_total": line_total,
            "cost": cost
        })

    # Task 1: Extract all prices (we’ll collect money-like values with ,dd)
    all_prices_raw = re.findall(r"(?<!\d)(\d[\d \xa0]*,\d{2})(?!\d)", text)
    all_prices = [parse_money(x) for x in all_prices_raw]

    # Task 3: Calculate total amount (from items)
    computed_total = round(sum(i["line_total"] for i in items), 2) if items else None

    result = {
        "branch": branch,
        "bin": bin_num,
        "receipt_number": receipt_no,
        "cashier": cashier,
        "datetime": dt,
        "address": address,

        "payment_method": payment_method,
        "payment_amount": payment_amount,

        "total": total,
        "vat": vat,

        "items": items,

        # for the assignment tasks:
        "all_prices_found": all_prices,
        "computed_total_from_items": computed_total
    }
    return result


def main():
    file_path = Path(__file__).with_name("raw.txt")
    text = file_path.read_text(encoding="utf-8", errors="ignore")

    data = parse_receipt(text)

    # --- JSON output (structured) ---
    print(json.dumps(data, ensure_ascii=False, indent=2))

    # --- readable output ---
    print("\n--- SUMMARY ---")
    print("Branch:", data["branch"])
    print("BIN:", data["bin"])
    print("Receipt #:", data["receipt_number"])
    print("DateTime:", data["datetime"])
    print("Payment:", data["payment_method"], "| Amount:", data["payment_amount"])
    print("Total:", data["total"])
    print("Computed total from items:", data["computed_total_from_items"])
    print("Items count:", len(data["items"]))

if __name__ == "__main__":
    main()