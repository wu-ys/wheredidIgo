import json
import csv

data = {}

# 读取 CSV 文件
with open("flights/airport.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        group = row.get("group", "flights")  # 按 group 分类
        if group not in data:
            data[group] = []
        data[group].append({
            "name_zh": row["name_zh"],
            "name_en": row["name_en"],
            "lat": float(row["lat"]),
            "lon": float(row["lon"])
        })

# 写出 JSON 文件
with open("flights/airport.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 已将 flights/airport.csv 转换为 flights/airport.json")