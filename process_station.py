import csv
import json
from utils.project import gcj02towgs84

# === 1. 读取 JSON 文件 ===
with open('assets/station_lnglat_20250217.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# 构造 name → (lat, lon) 的字典
coord_dict = {item["name"]: (item["lat"], item["lng"]) for item in json_data}

# === 2. 读取 CSV 文件 ===
records = []
missing_names = []

with open('railway/station.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get('name')
        lat_str = row.get('lat', '').strip()
        lon_str = row.get('lon', '').strip()

        lat = float(lat_str) if lat_str else None
        lon = float(lon_str) if lon_str else None

        # 如果CSV中已有坐标
        if lat is not None and lon is not None:
            lon, lat = gcj02towgs84(lon, lat)
            records.append({"name": name, "lat": lat, "lon": lon})
            continue

        # 如果JSON中存在该车站
        if name in coord_dict:
            lat, lon = coord_dict[name]
            lon, lat = gcj02towgs84(lon, lat)
            records.append({"name": name, "lat": lat, "lon": lon})
        else:
            missing_names.append(name)

# === 3. 保存 JSON 文件 ===
wrapped = {"railway": records}

with open('railway/station.json', 'w', encoding='utf-8') as f:
    json.dump(wrapped, f, ensure_ascii=False, indent=2)

# === 4. 控制台输出 ===
if missing_names:
    print("⚠️ 缺失的车站：")
    for name in missing_names:
        print("  -", name)
else:
    print("✅ 所有车站都已匹配成功！")

print(f"✅ 已生成 railway/station.json 文件，共导出 {len(records)} 个车站。")
