import os
import glob

# === 配置要扫描的文件夹路径 ===
folder = "./railway"   # 当前文件夹

railway_gpx_files = sorted(glob.glob(os.path.join("./railway", "**", "*.gpx"), recursive=True))
flights_gpx_files = sorted(glob.glob(os.path.join("./flights", "**", "*.gpx"), recursive=True))


with open("index_template.html", 'r', encoding='utf-8') as file:
    template = file.read()

template = template.replace(f"{{railway}}", str(railway_gpx_files))
template = template.replace(f"{{flights}}", str(flights_gpx_files))
template = template.replace(f"\\\\", "/")

# 写入输出文件
with open("index.html", 'w', encoding='utf-8') as file:
    file.write(template)