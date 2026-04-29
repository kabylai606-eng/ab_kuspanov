import json

# Read JSON file
with open("sample-data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Prepare rows: (dn, descr, speed, mtu)
rows = []
for item in data.get("imdata", []):
    attrs = item.get("l1PhysIf", {}).get("attributes", {})
    dn = attrs.get("dn", "")
    descr = attrs.get("descr", "")
    speed = attrs.get("speed", "")
    mtu = attrs.get("mtu", "")
    rows.append((dn, descr, speed, mtu))

# Column widths (match the “look” of the example)
dn_w = 50
desc_w = 20
speed_w = 6
mtu_w = 6

# Print header
print("Interface Status")
print("=" * 80)
print(f"{'DN':<{dn_w}} {'Description':<{desc_w}} {'Speed':<{speed_w}} {'MTU':<{mtu_w}}")
print(f"{'-'*dn_w} {'-'*desc_w}  {'-'*speed_w}  {'-'*mtu_w}")

# Print rows (truncate if too long)
for dn, descr, speed, mtu in rows:
    dn_out = dn[:dn_w]
    descr_out = descr[:desc_w]
    speed_out = str(speed)[:speed_w]
    mtu_out = str(mtu)[:mtu_w]
    print(f"{dn_out:<{dn_w}} {descr_out:<{desc_w}}  {speed_out:<{speed_w}}  {mtu_out:<{mtu_w}}")