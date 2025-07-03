import gpxpy
import gpxpy.gpx
from datetime import datetime
import os
import csv

def analyze_gpx(file_path):
    """
    分析單個 GPX 檔案以提取所需資訊：
    1. GPX 結束日期
    2. 到達最高點的時間
    3. 開始到最高點的時間
    4. 最高點到結束的時間
    5. 總共花費時間（分鐘）
    """
    try:
        # 讀取 GPX 檔案
        with open(file_path, 'r', encoding='utf-8') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        # 初始化變數
        max_elevation = float('-inf')
        max_elevation_time = None
        start_time = None
        end_time = None
        
        # 提取所有點的資訊
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append(point)

        # 確保有足夠的點進行計算
        if len(points) < 2:
            raise ValueError(f"GPX 文件 {file_path} 的點數不足，無法進行分析。")

        # 設定起始時間和結束時間
        start_time = points[0].time
        end_time = points[-1].time

        # 找到最高點
        for point in points:
            if point.elevation > max_elevation:
                max_elevation = point.elevation
                max_elevation_time = point.time

        # 計算總花費時間（分鐘）
        total_time_minutes = (end_time - start_time).total_seconds() / 60

        # 計算從開始到最高點的時間（分鐘）
        time_to_max_elevation_minutes = (max_elevation_time - start_time).total_seconds() / 60

        # 計算從最高點到結束的時間（分鐘）
        time_from_max_elevation_to_end_minutes = (end_time - max_elevation_time).total_seconds() / 60

        # 返回分析結果
        return {
            "file_name": os.path.basename(file_path),
            "end_date": end_time.strftime("%Y/%m/%d"),  # 格式化日期
            "max_elevation_time": max_elevation_time,
            "time_to_max_elevation_min": int(time_to_max_elevation_minutes),
            "time_from_max_to_end_min": int(time_from_max_elevation_to_end_minutes),
            "total_time": int(total_time_minutes)
        }
    except Exception as e:
        # 捕獲分析單一檔案時的錯誤
        print(f"分析 GPX 文件 {file_path} 時發生錯誤：{e}")
        return None

def analyze_gpx_folder(folder_path, output_csv):
    """
    分析資料夾內的所有 GPX 檔案，並將結果輸出為 CSV 檔案。
    """
    # 檢查資料夾是否存在
    if not os.path.isdir(folder_path):
        raise ValueError(f"資料夾 {folder_path} 不存在。")

    # 初始化結果列表
    results = []

    # 遍歷資料夾內的所有 GPX 檔案
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith('.gpx'):
            file_path = os.path.join(folder_path, file_name)
            result = analyze_gpx(file_path)
            if result:  # 確保只有成功分析的結果才被加入
                results.append(result)

    # 將結果寫入 CSV 檔案
    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ["file_name", "end_date", "max_elevation_time", "time_to_max_elevation_min", "time_from_max_to_end_min", "total_time"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"分析結果已輸出至 {output_csv}")

# 使用範例
folder_path = input("請輸入 GPX 檔案所在的資料夾路徑：")
folder_name = os.path.basename(os.path.normpath(folder_path))
output_csv = f"{folder_name}_analysis_results.csv"
analyze_gpx_folder(folder_path, output_csv)
