import os
import re
import glob
import json
import numpy as np
import pandas as pd

from dataclasses import dataclass

@dataclass
class Vec2:
    lon: float #longitude
    lat: float #latitude

    def __add__(self, other):
        return Vec2(self.lon + other.lon, self.lat + other.lat)

    def __sub__(self, other):
        return Vec2(self.lon - other.lon, self.lat - other.lat)
    
    def norm(self):
        return np.sqrt(self.lon * self.lon + self.lat * self.lat)


def remove_parentheses_from_filenames(folder_path):

    files = glob.glob(os.path.join(folder_path, '**/*.gpx'))

    for file_path in files:
        if os.path.isfile(file_path):
            dir_name = os.path.dirname(file_path)
            old_filename = os.path.basename(file_path)

            # 删除括号及括号内容
            new_filename = re.sub(r'\([^)]*\)', '', old_filename)
            # 删除所有空格
            new_filename = new_filename.replace(' ', '')

            if new_filename != old_filename:
                new_file_path = os.path.join(dir_name, new_filename)

                # 处理文件名冲突
                counter = 1
                temp_new_file_path = new_file_path
                while os.path.exists(temp_new_file_path):
                    name, ext = os.path.splitext(new_file_path)
                    temp_new_file_path = f"{name}_{counter}{ext}"
                    counter += 1

                try:
                    os.rename(file_path, temp_new_file_path)
                    print(f"重命名: {old_filename} -> {os.path.basename(temp_new_file_path)}")
                except Exception as e:
                    print(f"重命名 {old_filename} 时出错: {e}")

def export_railway_gpx_to_csv(folder_path, csv_file_path, json_file_path):

    records = {}
    extra_records = {}

    for gpx_file in glob.glob(os.path.join(folder_path, "*.gpx")):

        filename_without_ext = os.path.splitext(os.path.basename(gpx_file))[0] 
        records[filename_without_ext] = {"zh": filename_without_ext, "en": "", "country": "CN", 'type': "main", 'speed': 160, "line_ref": "", "start": "", "end": "", "vias": []}

    if os.path.exists(csv_file_path):

        csv = pd.read_csv(csv_file_path, encoding='utf-8', keep_default_na=False, dtype={
            "line_ref": str,
            "name_zh": str,
            "name_en": str,
            "country": str,
            "type": str,
            "speed": int,
            "start": str,
            "end": str,
            "vias": str
        })

        for row in range(csv.shape[0]):
            line_ref = csv.at[row,"line_ref"]
            name_zh = csv.at[row,"name_zh"]
            name_en = csv.at[row,"name_en"]
            country = csv.at[row,"country"]
            type_ = csv.at[row,"type"]
            speed = int(csv.at[row,"speed"])
            start = csv.at[row,"start"]
            end = csv.at[row,"end"]
            vias = csv.at[row,"vias"].split()

            if name_zh in records:

                new_name_zh = re.sub(r'\([^)]*\)', '', name_zh).replace(' ', '')
                if not line_ref[0].isdigit() or line_ref[-1].isdigit():
                    new_name_zh = re.sub(r'（[^)]*）', '', new_name_zh)
                    if new_name_zh != name_zh:
                        os.rename(
                            os.path.join(folder_path, f"{name_zh}.gpx"),
                            os.path.join(folder_path, f"{new_name_zh}.gpx"))
                        csv.at[row,"name_zh"] = new_name_zh
                        print(f"重命名: {name_zh} -> {new_name_zh}")
                else:
                    print(f"{name_zh} 的 line_ref 不合法，无法重命名！")

                records[name_zh]["line_ref"] = line_ref
                records[name_zh]["zh"] = new_name_zh
                records[name_zh]["en"] = name_en
                records[name_zh]["country"] = country
                records[name_zh]["type"] = type_
                records[name_zh]["speed"] = speed
                records[name_zh]["start"] = start
                records[name_zh]["end"] = end
                records[name_zh]["vias"] = vias

            else:
                extra_records[name_zh] = {"zh": name_zh, "en": name_en, "country": country, 'type': type_, 'speed': speed, "line_ref": line_ref, "start": start, "end": end, "vias": vias}

                print(f"{name_zh}.gpx 文件不存在，但在 CSV 中有记录！")

        csv.to_csv(csv_file_path, index=False, encoding='utf-8')

    for record in records:
        if records[record]["line_ref"] == '':
            print(f"{record}.gpx 文件存在，但在 CSV 中没有记录！")
    
    print("导出完成！")

    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def fill_station_lonlat(reference_path, station_csv : pd.DataFrame, unused_station_csv : pd.DataFrame, loadJSON = True):

    # === 1. 读取 JSON 文件 ===
    coord_dict = {}
    if loadJSON:
        with open('assets/station_lnglat_20250217.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # 构造 name → (lat, lon) 的字典
        coord_dict = {item["name"]: (item["lat"], item["lng"]) for item in json_data}

    # === 2. 读取 CSV 文件 ===
    station_dict = {}
    unusedstation_dict = {}
    missing_names = []

    from utils.project import gcj02towgs84

    for row in range(station_csv.shape[0]):
        code = station_csv.at[row,'code']
        name = station_csv.at[row,'name']
        name_en = station_csv.at[row,"name_en"]
        lat_str = station_csv.at[row,'lat']
        lon_str = station_csv.at[row,'lon']
        country = station_csv.at[row,'country']

        lat = float(lat_str) if lat_str else None
        lon = float(lon_str) if lon_str else None

        # 如果CSV中已有坐标
        if lat is not None and lon is not None:
            station_dict[name] = {"name_zh": name, "name_en": name_en, "lat": lat, "lon": lon, "country": country, "code": code}

        # 如果JSON中存在该车站
        elif name in coord_dict and loadJSON:
            lat, lon = coord_dict[name]
            lon, lat = gcj02towgs84(lon, lat)
            station_csv.at[row, 'lat'] = lat
            station_csv.at[row, 'lon'] = lon
            print(f"已从 JSON 中填充 {name} 的坐标：({lat}, {lon})")
            station_dict[name] = {"name_zh": name, "name_en": name_en, "lat": lat, "lon": lon, "country": country, "code": code}
        else:
            missing_names.append(name)

    for row in range(unused_station_csv.shape[0]):
        code = unused_station_csv.at[row,'code']
        name = unused_station_csv.at[row,'name']
        name_en = unused_station_csv.at[row,"name_en"]
        lat_str = unused_station_csv.at[row,'lat']
        lon_str = unused_station_csv.at[row,'lon']
        country = unused_station_csv.at[row,'country']

        lat = float(lat_str) if lat_str else None
        lon = float(lon_str) if lon_str else None

        # 如果CSV中已有坐标
        if lat is not None and lon is not None:
            unusedstation_dict[name] = {"name_zh": name, "name_en": name_en, "lat": lat, "lon": lon, "country": country, "code": code}

        # 如果JSON中存在该车站
        elif name in coord_dict and loadJSON:
            lat, lon = coord_dict[name]
            unused_station_csv.at[row, 'lat'] = lat
            unused_station_csv.at[row, 'lon'] = lon
            unusedstation_dict[name] = {"name_zh": name, "name_en": name_en, "lat": lat, "lon": lon, "country": country, "code": code}
        else:
            missing_names.append(name)

    return missing_names, station_dict, unusedstation_dict

def update_waypoints_in_gpx(gpx_folder_path, railway_csv, railway_json_path, usedstation_dict, unused_station_dict, overwrite = True):

    import gpxpy
    import gpxpy.gpx

    station_dict = {**usedstation_dict, **unused_station_dict}
    for s in station_dict:
        station_dict[s]["lines"] = [] 

    railway_json = {}
    missing_stations = set()

    for r in range(railway_csv.shape[0]):
        r_name = railway_csv.at[r, "name_zh"]
        r_name_en = railway_csv.at[r,"name_en"]
        r_country = railway_csv.at[r,"country"]
        r_type = railway_csv.at[r,"type"]
        r_speed = int(railway_csv.at[r, "speed"])
        r_line_ref = railway_csv.at[r,"line_ref"]
        r_start = railway_csv.at[r, "start"]
        r_end = railway_csv.at[r, "end"]
        r_vias = railway_csv.at[r, "vias"].split()

        r_name_suffix = railway_csv.at[r, "name_suffix"]

        g = gpxpy.gpx.GPX()

        try:
            with open(os.path.join(gpx_folder_path, f"{r_name + r_name_suffix}.gpx"), 'r', encoding='utf-8') as f:
            # Parse the file object
                g = gpxpy.parse(f)
        except FileNotFoundError:
            print(f"\033[31mError: The file '{r_name + r_name_suffix}.gpx' was not found.\033[0m")
        except Exception as e:
            print(f"\033[31mError parsing GPX file: {r_name}.gpx\033[0m")

        gpx_changed = False

        railway_json[r_name + r_name_suffix] = {
            "line_ref": r_line_ref,
            "name_zh": r_name,
            "name_en": r_name_en,
            "country": r_country,
            "type": r_type,
            "speed": r_speed,
            "start": r_start,
            "end": r_end,
            "vias": r_vias
        }

        if r_start not in station_dict:
            print(f"\033[33mWarning: Start station {r_start} of railway {r_name + r_name_suffix} has no coordinate, skipped.\033[0m")
        
        elif r_end not in station_dict:
            print(f"\033[33mWarning: End station {r_end} of railway {r_name} has no coordinate, skipped.\033[0m")
        
        else:
            # determine whether the gpx should be reversed
            # by the information of starting/ending points
            # and coordinates of start/end stations in station_dict
            c_start = Vec2( station_dict[r_start]["lon"], station_dict[r_start]["lat"] )
            c_end = Vec2( station_dict[r_end]["lon"], station_dict[r_end]["lat"] )

            # assert that g has only one trk and one trkseg
            if len(g.tracks) > 1:
                print(f"\033[33mWarning: {r_name + r_name_suffix}.gpx has more than one track, only the first one will be processed.\033[0m")
            if len(g.tracks[0].segments) > 1:
                print(f"\033[33mWarning: {r_name + r_name_suffix}.gpx has more than one segment, only the first one will be processed.\033[0m")

            points = g.tracks[0].segments[0].points
            
            g_start = Vec2(points[0].longitude, points[0].latitude)
            g_end = Vec2(points[-1].longitude, points[-1].latitude)

            if (c_start - g_start).norm() > (c_start - g_end).norm() and (c_end - g_start).norm() < (c_end - g_end).norm():
                print(f"\033[34mReversing {r_name + r_name_suffix} because start point is closer to end station.\033[0m")
                points.reverse()
                gpx_changed = True
            elif (c_start - g_start).norm() < (c_start - g_end).norm() and (c_end - g_start).norm() > (c_end - g_end).norm():
                pass
                # print(f"\033[32m{r_name + r_name_suffix} is in correct direction.\033[0m")
            else:
                print(f"\033[33mWarning: Cannot determine the direction of {r_name + r_name_suffix}, please check manually.\033[0m")

        r_stations = [r_start, *r_vias, r_end]

        r_waypoints = []
        g_waypoints = g.waypoints

        if len(g_waypoints) < len(r_stations) or overwrite:
            gpx_changed = True
            for s in r_stations:
                if s in station_dict:
                    lon, lat = station_dict[s]["lon"], station_dict[s]["lat"]
                    r_waypoints.append(gpxpy.gpx.GPXWaypoint(
                        latitude=lat,
                        longitude=lon,
                        name=station_dict[s]["name_zh"],
                        description=station_dict[s]["country"] + station_dict[s]["code"]
                    ))
                    station_dict[s]["lines"].append(r_name + r_name_suffix)

                else:
                    print(f"\033[33mWarning: Station {s} of railway {r_name + r_name_suffix} has no coordinate, skipped.\033[0m")
                    gpx_changed = False
                    missing_stations.add(s)
            
            g.waypoints = r_waypoints
        
        # 写入文件
        if gpx_changed:
            print(f"\033[32mUpdated waypoints in {r_name + r_name_suffix}.gpx and saved.\033[0m")
            with open(os.path.join(gpx_folder_path, f"{r_name + r_name_suffix}.gpx"), 'w', encoding='utf-8') as f:
                f.write(g.to_xml())
        
    with open(railway_json_path, 'w', encoding='utf-8') as f:
        json.dump(railway_json, f, ensure_ascii=False, indent=2)

    return missing_stations, station_dict



if __name__ == "__main__":
    gpx_folder_path = "./railway/gpx"
    railway_csv_file_path = "./railway/railway.csv"
    railway_json_file_path = "./railway/railway.json"
    station_csv_file_path = "./railway/station.csv"
    station_json_file_path = "./railway/station.json"
    unusedstation_csv_file_path = "./railway/unusedstation.csv"
    station_reference_path = "./assets/station_lnglat_20250217.json"

    station_csv = pd.read_csv(station_csv_file_path, encoding='utf-8', keep_default_na=False, dtype=str)

    unusedstation_csv = pd.read_csv(unusedstation_csv_file_path, encoding='utf-8', keep_default_na=False, dtype=str)
        
    # station names that have no coordinates in csv and json
    cmd = input("是否从 JSON 文件加载车站坐标信息？\n输入 Y+Enter 加载，否则不加载: ").strip().lower()
    missing_names, usedstation_dict, unusedstation_dict = fill_station_lonlat(station_reference_path, station_csv, unusedstation_csv, loadJSON=(cmd == "y"))

    station_csv.to_csv(station_csv_file_path, index=False, encoding='utf-8')
    # unusedstation_csv.to_csv(unusedstation_csv_file_path, index=False, encoding='utf-8')

    if len(missing_names) == 0:
        print("所有车站的坐标信息都已补充完整！")
    else:
        print("以下车站在 CSV 和 JSON 中都没有坐标信息，请手动补充：")
        print(missing_names)
        cmd = input("输入 C+Enter 继续，否则程序退出: ").strip().lower()

        if cmd != "c":
            print("Terminating")
            exit()

    # process gpx file names
    remove_parentheses_from_filenames(gpx_folder_path)

    # export_railway_gpx_to_csv(gpx_folder_path, csv_file_path='./railway/railway.csv', json_file_path='./railway/railway.json')

    railway_csv = pd.read_csv(railway_csv_file_path, encoding='utf-8', keep_default_na=False, dtype=str)

    missing_stations, station_dict = update_waypoints_in_gpx(gpx_folder_path, railway_csv, railway_json_file_path, usedstation_dict, unusedstation_dict, overwrite=True)

    for m in missing_stations:
        if m not in station_dict and m not in unusedstation_dict:
            unusedstation_csv = pd.concat([unusedstation_csv, pd.DataFrame([{
                "code": "",
                "name": m,
                "name_en": "",
                "lat": "",
                "lon": "",
                "country": ""
            }])], ignore_index=True)

    if len(missing_stations) > 0:
        print("以下车站在铁路数据中出现，但在车站数据中没有坐标信息：")
        print(missing_stations)
        cmd = input("是否将这些车站添加到 unusedstation.csv 中？\n输入 Y+Enter 添加，否则不添加: ").strip().lower()

        if cmd == "y":
            unusedstation_csv.to_csv(unusedstation_csv_file_path, index=False, encoding='utf-8')
            print("已将缺失车站添加到 unusedstation.csv 中。")

    station_json = {"railway": []}

    for s in usedstation_dict:
        station_json["railway"].append({
            "name_zh": station_dict[s]["name_zh"],
            "name_en": station_dict[s]["name_en"],
            "lat": station_dict[s]["lat"],
            "lon": station_dict[s]["lon"],
            "country": station_dict[s]["country"],
            "code": station_dict[s]["code"],
            "lines": station_dict[s]["lines"]
        })

    with open(station_json_file_path, 'w', encoding='utf-8') as f:    
        json.dump(station_json, f, ensure_ascii=False, indent=2)
        print(f"已生成 station.json 文件，包含 {len(usedstation_dict)} 个车站。")