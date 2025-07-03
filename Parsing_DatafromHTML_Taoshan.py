import json
import csv
import os
import re

# --- 設定 ---
# 原始 JSON 檔案名稱
json_filename = 'data_from_HTML_Taoshan.json'
# 輸出 CSV 檔案名稱
csv_filename = 'webscrapping4HTML_Taoshan_en.csv'
# 您指定的 CSV 英文欄位標頭
csv_headers = ["file_name", "distance", "total_time", "total_ascent", "total_descent", "end_date", "user"]
# JSON 中文鍵值與英文標頭的對應
json_to_csv_map = {
    "標題": "file_name",
    "總距離": "distance",
    "花費時間": "total_time",
    "總爬升高度": "total_ascent",
    "總下降高度": "total_descent",
    "日期": "end_date",
    "紀錄者": "user"
}


# --- 輔助函式 ---
def parse_time_to_minutes(time_str):
    """
    將 "X 天 Y 小時 Z 分鐘" 格式的時間字串轉換為總分鐘數。
    """
    if not isinstance(time_str, str):
        return 0

    days = re.search(r'(\d+)\s*天', time_str)
    hours = re.search(r'(\d+)\s*小時', time_str)
    minutes = re.search(r'(\d+)\s*分鐘', time_str)

    total_minutes = 0
    if days:
        total_minutes += int(days.group(1)) * 24 * 60
    if hours:
        total_minutes += int(hours.group(1)) * 60
    if minutes:
        total_minutes += int(minutes.group(1))
        
    # 處理類似 "13 小時" 這樣沒有分鐘數的格式
    if not days and not hours and not minutes and '小時' in time_str:
        try:
            # 嘗試直接將字串中的數字部分作為小時來解析
            cleaned_str = time_str.replace('小時', '').strip()
            total_minutes = int(float(cleaned_str)) * 60
        except ValueError:
            pass # 如果轉換失敗，則保持為0
            
    return total_minutes

def clean_numeric_value(value_str):
    """
    移除數值字串中的逗號和前後空白。
    """
    if isinstance(value_str, str):
        return value_str.replace(',', '').strip()
    return value_str


# --- 主程式 ---
def convert_json_to_csv():
    """
    讀取指定的 JSON 檔案，並將其內容轉換為使用英文欄位的 CSV 檔案。
    """
    if not os.path.exists(json_filename):
        print(f"錯誤：找不到檔案 '{json_filename}'。請確認檔案名稱是否正確，且與此程式檔位於相同目錄。")
        return

    try:
        with open(json_filename, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
    except json.JSONDecodeError as e:
        print(f"錯誤：無法解析 '{json_filename}'。")
        print(f"JSON 格式有誤，錯誤發生在第 {e.lineno} 行，第 {e.colno} 欄: {e.msg}")
        print("請檢查檔案結尾是否缺少 '}' 或其他語法錯誤。")
        return
    except Exception as e:
        print(f"讀取檔案時發生未預期的錯誤: {e}")
        return

    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
            writer.writeheader()

            if not isinstance(data, dict):
                print("錯誤：JSON 檔案的頂層結構不是一個字典（物件）。")
                return

            for record_key, record_value in data.items():
                if not isinstance(record_value, dict):
                    print(f"警告：紀錄 '{record_key}' 的格式不正確，將略過此筆資料。")
                    continue

                # 建立一個新的字典來存放處理過的資料
                processed_row = {}
                for json_key, csv_key in json_to_csv_map.items():
                    raw_value = record_value.get(json_key)

                    if csv_key == 'total_time':
                        processed_row[csv_key] = parse_time_to_minutes(raw_value)
                    elif csv_key in ['distance', 'total_ascent', 'total_descent']:
                        processed_row[csv_key] = clean_numeric_value(raw_value)
                    else:
                        processed_row[csv_key] = raw_value

                writer.writerow(processed_row)

        print(f"成功！已將資料從 '{json_filename}' 轉換並儲存至 '{csv_filename}'。")
        print(f"其中 '花費時間' 已被轉換為 'total_time' (總分鐘數)。")

    except IOError as e:
        print(f"寫入 CSV 檔案時發生錯誤: {e}")
    except Exception as e:
        print(f"處理過程中發生未預期的錯誤: {e}")


# --- 執行程式 ---
if __name__ == '__main__':
    convert_json_to_csv()
