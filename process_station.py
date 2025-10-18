import pandas as pd
import json

from utils.project import gcj02towgs84

# === 1. 读取 JSON 文件 ===
with open('assets/station_lnglat_20250217.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# 构造 name → (lat, lng) 的字典
coord_dict = {item["name"]: (item["lat"], item["lng"]) for item in json_data}

# === 2. 读取 CSV 文件 ===
df = pd.read_csv('railway/station.csv', encoding='utf-8')

# # === 3. 匹配经纬度 ===
# df['lat'] = df['name'].map(lambda x: coord_dict.get(x, (None, None))[0])
# df['lon'] = df['name'].map(lambda x: coord_dict.get(x, (None, None))[1])

# === 3. 匹配经纬度，并记录未匹配项 ===
missing_names = []
records = []

for _, row in df.iterrows():
    name = row['name']
    lat, lon = row['lat'], row['lon']
    # 如果CSV中已有坐标，直接用
    if pd.notna(lat) and pd.notna(lon):
        lon, lat = gcj02towgs84(lon, lat)
        records.append({"name": name, "lat": lat, "lon": lon})

    # 如果json中可以找到坐标
    elif name in coord_dict:
        lat, lon = coord_dict[name][0], coord_dict[name][1]
        lon, lat = gcj02towgs84(lon, lat)
        records.append({"name": name, "lat": lat, "lon": lon})
    else:
        # records.append({"name": name, "lat": None, "lon": None})
        missing_names.append(name)

# === 4. 转换为 JSON 格式并保存 ===
wrapped = {"railway": records}

with open('railway/station.json', 'w', encoding='utf-8') as f:
    json.dump(wrapped, f, ensure_ascii=False, indent=2)

print("缺失的车站：", missing_names)
print("✅ 已生成 station.json 文件！")
