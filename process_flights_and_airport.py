import json
import gpxpy
import gpxpy.gpx
from datetime import datetime
import os
import glob

import pandas as pd

# ==== config ====
input_csv_folder = "./flights/csv"
output_gpx_folder = "./flights/gpx"

airport_csv_path = "flights/airport.csv"
airport_json_path = "./flights/airport.json"

flights_csv_path = "./flights/flights.csv"
flights_json_path = "./flights/flights.json"


def csv_to_gpx(csv_path, gpx_path, force = False):
    if not force and os.path.exists(gpx_path):
        print(f"\033[34mSkip file that already exists: {gpx_path}\033[34m")
        return
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack(name=os.path.basename(csv_path))
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    import csv

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

    print(f"\033[32m{csv_path} -> {gpx_path} succeed with {len(gpx_segment.points)} points.\033[32m")

def bind_airport_and_flights(airport_json, flights_csv_path):

    if os.path.exists(flights_csv_path):

        flights_csv = pd.read_csv(flights_csv_path, encoding="utf-8", keep_default_na=False, dtype={
            "flight_id": str,
            "gpx_filename": str,
            "flight_no": str,
            "date": str,
            "dpt": str,
            "arr": str,
            "via": str
        })

    flights_json = []
    existing_filenames = set()
    max_id = 0

    for r in range(flights_csv.shape[0]):
        filename = flights_csv.at[r, "gpx_filename"]
        flight_id = flights_csv.at[r, "flight_id"]
        flight_no = flights_csv.at[r, "flight_no"]
        date = flights_csv.at[r, "date"]
        dpt = flights_csv.at[r, "dpt"]
        arr = flights_csv.at[r, "arr"]
        via = flights_csv.at[r, "via"]

        flights_json.append({
            "flight_id": flight_id,
            "gpx_filename": filename,
            "flight_no": flight_no,
            "date": date,
            "departure": dpt,
            "arrival" : arr,
            "via": via
        })

        if dpt not in airport_json:
            airport_json[dpt] = {
                "name_zh": "", "name_en": "",
                "lat": 0.0, "lon": 0.0,
                "iata": dpt,
                "departure":[], "arrival":[],
                "via":[], "cnt": 0
            }
            print(f"\033[33mWarning: Airport {dpt} of flight {date}-{flight_no} not found in airport.csv. Added with empty info.\033[0m")
        if arr not in airport_json:
            airport_json[arr] = {
                "name_zh": "", "name_en": "",
                "lat": 0.0, "lon": 0.0,
                "iata": arr,
                "departure":[], "arrival":[],
                "via":[],  "cnt": 0
            }
            print(f"\033[33mWarning: Airport {arr} of flight {date}-{flight_no} not found in airport.csv. Added with empty info.\033[0m")
        if via != "" and via not in airport_json:
            airport_json[via] = {
                "name_zh": "", "name_en": "",
                "lat": 0.0, "lon": 0.0,
                "iata": via,
                "departure":[], "arrival":[],
                "via":[], "cnt": 0
            }
            print(f"\033[33mWarning: Airport {via} of flight {date}-{flight_no} not found in airport.csv. Added with empty info.\033[0m")

        airport_json[dpt]["departure"].append(flight_id)
        airport_json[dpt]["cnt"] += 1
        airport_json[arr]["arrival"].append(flight_id)
        airport_json[arr]["cnt"] += 1
        if via != "":
            airport_json[via]["via"].append(flight_id)
            airport_json[via]["cnt"] += 1

        if filename:
            existing_filenames.add(filename)
        try:
            max_id = max(max_id, int(flight_id))
        except ValueError:
            pass


    idx = max_id + 1

    for csv_file in glob.glob(os.path.join(input_csv_folder, "*.csv")):
        filename = os.path.splitext(os.path.basename(csv_file))[0]
        _, flight_no, date = filename.split('_')

        gpx_file = f"{date}_{flight_no}.gpx"

        if gpx_file in existing_filenames:
            continue
        else:
            flights_csv = pd.concat([flights_csv, pd.DataFrame([{
                "flight_id": idx,
                "gpx_filename": gpx_file,
                "flight_no": flight_no,
                "date": date,
                "dpt": "",
                "arr": "",
                "via": ""
            }])], ignore_index=True)

            csv_to_gpx(csv_file, os.path.join(output_gpx_folder, gpx_file), force =True)

            idx+=1

    flights_csv.to_csv(flights_csv_path, index=False, encoding="utf-8")

    return airport_json, flights_json

if __name__ == "__main__":

    airport_csv = pd.read_csv(airport_csv_path, encoding="utf-8", keep_default_na=False, dtype={
        "name_zh": str,
        "name_en": str,
        "lat": float,
        "lon": float
    })
    airport_csv = airport_csv[airport_csv["name_zh"] != ""]

    airport_json = {}
    for r in range(airport_csv.shape[0]):
        iata = airport_csv.at[r, "iata"]
        icao = airport_csv.at[r, "icao"]
        airport_json[iata] = {
            "name_zh": airport_csv.at[r, "name_zh"],
            "name_en": airport_csv.at[r, "name_en"],
            "lat": airport_csv.at[r, "lat"],
            "lon": airport_csv.at[r, "lon"],
            "iata": iata,
            "icao": icao,
            "departure": [],
            "arrival": [],
            "via": [],
            "cnt": 0
        }

    os.makedirs(output_gpx_folder, exist_ok=True)

    airport_json, flights_json = bind_airport_and_flights(airport_json, flights_csv_path)

    with open(airport_json_path, "w", encoding="utf-8") as f:
        json.dump(airport_json, f, ensure_ascii=False, indent=2)

    print(f"\033[32m已将 flights/airport.csv 转换为 flights/airport.json\033[0m")

    with open(flights_json_path, "w", encoding="utf-8") as f:
        json.dump(flights_json, f, ensure_ascii=False, indent=2)
    print(f"\033[32m已将 flights/flights.csv 转换为 flights/flights.json\033[0m")