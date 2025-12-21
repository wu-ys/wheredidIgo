import csv
import json
import gpxpy
import gpxpy.gpx
from datetime import datetime
import os
import glob

# ==== 配置 ====
input_folder = "./flights/csv"      # 存放 CSV 的文件夹
output_folder = "./flights/gpx"     # 输出 GPX 的文件夹
output_csv = "./flights/flights.csv"
output_flights_json = "./flights/flights.json"
output_airport_flights_json = "./flights/airport_flights.json"

def csv_to_gpx(csv_path, gpx_path, force = False):
    if not force and os.path.exists(gpx_path):
        print(f"跳过已存在的文件: {gpx_path}")
        return
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack(name=os.path.basename(csv_path))
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lat = float(row["Latitude"])
                lon = float(row["Longitude"])
                ele = float(row.get("Height", 0.0))
            except (ValueError, KeyError):
                continue

            time_str = row.get("UTC TIME")
            time_obj = None
            if time_str:
                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                    try:
                        time_obj = datetime.strptime(time_str.strip(), fmt)
                        break
                    except Exception:
                        continue
            
            try:
                speed = float(row.get("Speed", 0.0))
            except ValueError:
                speed = 0.0

            try:
                course = float(row.get("Angle", 0.0))
            except ValueError:
                course = 0.0

            point = gpxpy.gpx.GPXTrackPoint(
                latitude=lat,
                longitude=lon,
                elevation=ele,
                time=time_obj
            )

            # point.extensions = [speed, course]
            gpx_segment.points.append(point)

    with open(gpx_path, "w", encoding="utf-8") as f:
        f.write(gpx.to_xml())

    print(f"已生成: {gpx_path} ({len(gpx_segment.points)} 个点)")


if __name__ == "__main__":
    os.makedirs(output_folder, exist_ok=True)

    gpx_flies = []

    flights_data = {}
    airport_flights_data = {}

    existing_filenames = set()
    max_id = 0

    if os.path.exists(output_csv):
        with open(output_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                filename = row.get("gpx_filename")

                group = row.get("group", "flights")
                if group not in flights_data:
                    flights_data[group] = []

                flights_data[group].append({
                    "flight_id": row["flight_id"],
                    "gpx_filename": filename,
                    "flight_no": row["flight_no"],
                    "date": row["date"],
                    "departure": row["dpt"],
                    "arrival" : row["arr"],
                    "via": row["via"]
                })

                if row["dpt"] not in airport_flights_data:
                    airport_flights_data[row["dpt"]] = {"departure":[], "arrival":[], "via":[], "cnt": 0}
                if row["arr"] not in airport_flights_data:
                    airport_flights_data[row["arr"]] = {"departure":[], "arrival":[], "via":[], "cnt": 0}
                if row["via"] != "" and row["via"] not in airport_flights_data:
                    airport_flights_data[row["via"]] = {"departure":[], "arrival":[], "via":[], "cnt": 0}

                airport_flights_data[row["dpt"]]["departure"].append(row["flight_id"])
                airport_flights_data[row["dpt"]]["cnt"] += 1
                airport_flights_data[row["arr"]]["arrival"].append(row["flight_id"])
                airport_flights_data[row["arr"]]["cnt"] += 1
                if row["via"] != "":
                    airport_flights_data[row["via"]]["via"].append(row["flight_id"])
                    airport_flights_data[row["via"]]["cnt"] += 1

                if filename:
                    existing_filenames.add(filename)
                try:
                    max_id = max(max_id, int(row.get("flight_id", 0)))
                except ValueError:
                    pass

        write_header = False
    else:
        write_header = True

    with open(output_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["flight_id", "gpx_filename", "flight_no", "date", "dpt", "arr", "via"])

        idx = max_id+1

        for csv_file in glob.glob(os.path.join(input_folder, "*.csv")):
            filename = os.path.splitext(os.path.basename(csv_file))[0]

            _, flight_no, date = filename.split('_')

            gpx_file = f"{date}_{flight_no}.gpx"

            if gpx_file in existing_filenames:
                continue
            else:
                writer.writerow([idx, gpx_file, flight_no, date])

                flights_data["flights"].append({
                    "flight_id": idx,
                    "gpx_filename": gpx_file,
                    "flight_no": flight_no,
                    "date": date,
                    "departure": "",
                    "arrival" : "",
                    "via": ""
                })

                csv_to_gpx(csv_file, os.path.join(output_folder, gpx_file), force =True)
                idx+=1

                print(f"已在 {output_csv} 中添加记录: {date}_{flight_no}")
        
    with open(output_flights_json, "w", newline="", encoding="utf-8") as f:
        json.dump(flights_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已将 flights/flights.csv 转换为 flights/flights.json")
    
    with open(output_airport_flights_json, "w", encoding="utf-8") as f:
        json.dump(airport_flights_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已将 flights/flights.csv 转换为 flights/airport_flights.json")

