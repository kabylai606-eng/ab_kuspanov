import re
import json
from pathlib import Path


def read_text(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8", errors="ignore")


def normalize(text: str) -> str:
    # normalize line endings and remove weird spaces
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return text


def extract_date_time(text: str):
    """
    Tries to find date and time in common formats:
    - 2026-02-26 14:25
    - 26.02.2026 14:25
    - 26/02/2026 14:25
    - 26-02-2026 14:25
    """
    # date patterns
    dt_patterns = [
        r"(?P<date>\d{4}[-/.]\d{2}[-/.]\d{2})[ T,]*(?P<time>\d{2}:\d{2}(?::\d{2})?)",
        r"(?P<date>\d{2}[-/.]\d{2}[-/.]\d{4})[ T,]*(?P<time>\d{2}:\d{2}(?::\d{2})?)",
        r"(?P<date>\d{4}[-/.]\d{2}[-/.]\d{2})",
        r"(?P<date>\d{2}[-/.]\d{2}[-/.]\d{4})",
    ]
    for pat in dt_patterns:
        m = re.search(pat, text)
        if m:
            return m.groupdict().get("date"), m.groupdict().get("time")
    return None, None


def extract_payment_method(text: str):
    """
    Searches for keywords in English/Russian.
    """
    patterns = [
        (r"\b(CASH)\b|\bНАЛИЧНЫМИ\b|\bНАЛИЧНЫЕ\b", "CASH"),
        (r"\b(CARD)\b|\bКАРТА\b|\bБАНКОВСКАЯ КАРТА\b|\bVISA\b|\bMASTERCARD\b", "CARD"),
        (r"\b(QR)\b|\bQR[- ]?PAY\b|\bKASPI\b|\bKASPI QR\b", "QR"),
        (r"\b(APPLE PAY)\b|\bGOOGLE PAY\b", "MOBILE_PAY"),
    ]
    for pat, name in patterns:
        if re.search(pat, text, flags=re.IGNORECASE):
            return name
    return None


def extract_total(text: str):
    """
    Tries to find total amount lines:
    TOTAL, SUM, ИТОГО, К ОПЛАТЕ
    """
    total_patterns = [
        r"(?:TOTAL|AMOUNT DUE|SUM|ИТОГО|К ОПЛАТЕ)\s*[:\-]?\s*(\d+[.,]\d{2})",
        r"(?:TOTAL|AMOUNT DUE|SUM|ИТОГО|К ОПЛАТЕ)\s*[:\-]?\s*(\d+)",
    ]
    for pat in total_patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return float(m.group(1).replace(",", "."))
    return None


def extract_prices(text: str):
    """
    Extract all prices like:
    123.45, 123,45, 123.00
    We ignore very long numbers (like phone numbers) by requiring decimals OR being near currency.
    """
    # Prices with decimals
    prices_dec = re.findall(r"(?<!\d)(\d{1,6}[.,]\d{2})(?!\d)", text)
    prices = [float(p.replace(",", ".")) for p in prices_dec]

    # Also catch integers near currency words/symbols
    currency_int = re.findall(
        r"(?:(?:KZT|₸|тг|тенге|USD|\$|EUR|€)\s*)?(\d{1,6})(?:\s*(?:KZT|₸|тг|тенге))",
        text,
        flags=re.IGNORECASE
    )
    prices += [float(p) for p in currency_int]

    return prices


def extract_items(text: str):
    """
    Tries to extract product lines:
    Common patterns:
      NAME ... 2 x 150.00 = 300.00
      NAME ....... 300.00
      NAME 300,00
    We'll search per-line with heuristics.
    """
    items = []
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

    # candidate: line has letters and ends with a price
    end_price_pat = re.compile(r"^(?P<name>.*?[A-Za-zА-Яа-я].*?)\s+(?P<price>\d{1,6}[.,]\d{2})\s*$")
    qty_pat = re.compile(
        r"^(?P<name>.*?[A-Za-zА-Яа-я].*?)\s+(?P<qty>\d+)\s*[xX\*]\s*(?P<unit>\d{1,6}[.,]\d{2})\s*(?:=\s*)?(?P<sum>\d{1,6}[.,]\d{2})?\s*$"
    )

    for ln in lines:
        # skip obvious headers
        if re.search(r"(TOTAL|ИТОГО|К ОПЛАТЕ|CASH|CARD|QR|THANK YOU|СПАСИБО)", ln, re.IGNORECASE):
            continue

        m_qty = qty_pat.match(ln)
        if m_qty:
            name = m_qty.group("name").strip(" .:-")
            qty = int(m_qty.group("qty"))
            unit = float(m_qty.group("unit").replace(",", "."))
            s = m_qty.group("sum")
            line_sum = float(s.replace(",", ".")) if s else qty * unit
            items.append({
                "name": name,
                "qty": qty,
                "unit_price": unit,
                "line_total": line_sum
            })
            continue

        m_end = end_price_pat.match(ln)
        if m_end:
            name = m_end.group("name").strip(" .:-")
            price = float(m_end.group("price").replace(",", "."))
            items.append({
                "name": name,
                "qty": 1,
                "unit_price": price,
                "line_total": price
            })

    return items


def main():
    # expects Practice5/raw.txt
    file_path = Path(__file__).with_name("raw.txt")
    text = read_text(str(file_path))
    text = normalize(text)

    date, time = extract_date_time(text)
    payment = extract_payment_method(text)

    items = extract_items(text)
    prices = extract_prices(text)

    total_found = extract_total(text)

    # If total not found, try to compute
    computed_total = None
    if items:
        computed_total = round(sum(i["line_total"] for i in items), 2)

    # If total not found & no items, try fallback using max price as total (weak heuristic)
    if total_found is None and computed_total is None and prices:
        total_found = max(prices)

    result = {
        "date": date,
        "time": time,
        "payment_method": payment,
        "items": items,
        "all_prices_found": prices,
        "total_found_in_text": total_found,
        "total_computed_from_items": computed_total,
    }

    # --- Output JSON (structured output requirement) ---
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # --- Human readable output ---
    print("\n--- Parsed Summary ---")
    print(f"Date: {date or 'Not found'}")
    print(f"Time: {time or 'Not found'}")
    print(f"Payment: {payment or 'Not found'}")

    if items:
        print("\nItems:")
        for it in items:
            print(f"- {it['name']} | qty={it['qty']} | unit={it['unit_price']:.2f} | sum={it['line_total']:.2f}")
    else:
        print("\nItems: Not found (try adjusting regex to your raw.txt)")

    final_total = total_found if total_found is not None else computed_total
    if final_total is not None:
        print(f"\nTotal: {final_total:.2f}")
    else:
        print("\nTotal: Not found")


if __name__ == "__main__":
    main()