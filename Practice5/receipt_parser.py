import re
import json

with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Цены
price_pattern = r"\d+[.,]\d{2}"
prices = re.findall(price_pattern, text)
prices_float = [float(p.replace(",", ".")) for p in prices]

# Товары
item_pattern = r"(.+?)\s+\d+[.,]\d{2}"
items = re.findall(item_pattern, text)

# Общая сумма
total_pattern = r"(ИТОГО|TOTAL|СУММА).*?(\d+[.,]\d{2})"
total_match = re.search(total_pattern, text, re.IGNORECASE)

if total_match:
    total = float(total_match.group(2).replace(",", "."))
else:
    total = sum(prices_float)

# Дата и время
datetime_pattern = r"\d{2}[./-]\d{2}[./-]\d{4}\s+\d{2}:\d{2}(?::\d{2})?"
datetime_match = re.search(datetime_pattern, text)
date_time = datetime_match.group() if datetime_match else None

# Способ оплаты
payment_pattern = r"(НАЛИЧНЫМИ|КАРТА|CARD|CASH)"
payment_match = re.search(payment_pattern, text, re.IGNORECASE)
payment_method = payment_match.group() if payment_match else None

# Результат
result = {
    "items": items,
    "prices": prices_float,
    "total": total,
    "datetime": date_time,
    "payment_method": payment_method
}

print(json.dumps(result, ensure_ascii=False, indent=4))