import os
import csv

# 设置路径
folder_path = "./"  # GPX文件所在文件夹路径
csv_file_path = 'lang_gpx.csv'  # 已有CSV文件路径

# 读取已存在的文件名
existing_names = set()
records = {}
if os.path.exists(csv_file_path):
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row.get('name')
            name_en = row.get('name_en', "")
            existing_names.add(name)  # 取首列内容
            records[name] = {"zh": name, "en": name_en}

# 获取所有GPX文件名（不带扩展名）
new_names = []

for root, dirs, files in os.walk(folder_path):
    for f in files:
        if f.lower().endswith('.gpx'):
            filename_without_ext = os.path.splitext(f)[0]
            if filename_without_ext not in existing_names:
                new_names.append([filename_without_ext])
                existing_names.add(filename_without_ext)
                records[filename_without_ext] = {"zh": filename_without_ext, "en": ""}

# 将新文件名追加到CSV文件（如果有新内容）
if new_names:
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(new_names)

print("操作完成！")

import json
with open('./lang_gpx.json', 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)
