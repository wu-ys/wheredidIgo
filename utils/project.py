import math
 
PI = 3.1415926535897932384626
a = 6378245.0
ee = 0.00669342162296594323
 
def gcj02towgs84(lng, lat):
    lat = float(lat)
    lng = float(lng)
    if out_of_china(lng, lat):
        return [lng, lat]
    else:
        dlat = transformlat(lng - 105.0, lat - 35.0)
        dlng = transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * PI
        magic = math.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
        dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * PI)
        mglat = lat + dlat
        mglng = lng + dlng
        return [lng * 2 - mglng, lat * 2 - mglat]
 
def out_of_china(lng, lat):
    lat = float(lat)
    lng = float(lng)
    return not (73.66 < lng < 135.05 and 3.86 < lat < 53.55)
 
def transformlat(lng, lat):
    lat = float(lat)
    lng = float(lng)
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * PI) + 40.0 * math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * PI) + 320 * math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret
 
def transformlng(lng, lat):
    lat = float(lat)
    lng = float(lng)
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * PI) + 40.0 * math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * PI) + 300.0 * math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret
 
if __name__ == '__main__':
    lng = input("请输入经度: ")
    lat = input("请输入纬度: ")
    result = gcj02towgs84(lng, lat)
    print(f"转换后的经纬度为: 经度 {result[0]}, 纬度 {result[1]}")