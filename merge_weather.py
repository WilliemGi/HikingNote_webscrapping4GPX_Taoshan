import pandas as pd
import os

# --- 設定 ---
# 檔案名稱
file_hike = 'merged_taoshan_data.csv'
file_weather = 'weather.csv'
output_file = 'final_data_with_weather.csv'

# --- 主程式 ---
def merge_with_weather_data():
    """
    使用 LEFT JOIN 合併登山資料與天氣資料，
    條件為登山資料的 'end_date' 與天氣資料的 'date' 相同。
    """
    # 檢查檔案是否存在
    if not os.path.exists(file_hike) or not os.path.exists(file_weather):
        print(f"錯誤：請確認 '{file_hike}' 和 '{file_weather}' 都存在於同一個資料夾中。")
        return

    try:
        # --- 讀取檔案 ---
        # 根據上一步的輸出，merged_taoshan_data.csv 應為 'utf-8-sig'
        # weather.csv 從內容預覽也應為 'utf-8-sig'
        print(f"正在讀取 '{file_hike}'...")
        df_hike = pd.read_csv(file_hike, encoding='utf-8-sig')

        print(f"正在讀取 '{file_weather}'...")
        df_weather = pd.read_csv(file_weather, encoding='utf-8-sig')

        print("\n成功讀取檔案。開始進行資料清理與合併...")
        print(f"'{file_hike}' 原始筆數: {len(df_hike)}")
        print(f"'{file_weather}' 原始筆數: {len(df_weather)}")

        # --- 資料清理與標準化 ---
        # 為了確保合併的鍵 (key) 格式一致，將兩個檔案的日期欄位都轉換為 pandas 的 datetime 物件
        # errors='coerce' 會讓無法轉換的格式變成空值(NaT)，增加程式的穩定性
        df_hike['end_date'] = pd.to_datetime(df_hike['end_date'], errors='coerce')
        df_weather['date'] = pd.to_datetime(df_weather['date'], errors='coerce')

        # 移除日期轉換失敗的列
        df_hike.dropna(subset=['end_date'], inplace=True)
        df_weather.dropna(subset=['date'], inplace=True)

        # --- 執行合併 ---
        # 使用 'left' join，以 df_hike (左表) 為主進行合併
        final_df = pd.merge(
            left=df_hike,
            right=df_weather,
            how='left',
            left_on='end_date',
            right_on='date'
        )
        
        print(f"\n合併完成！最終資料共有 {len(final_df)} 筆。")

        # --- 整理欄位 ---
        # 合併後會同時存在 'end_date' 和 'date' 兩個欄位，我們可以移除多餘的 'date' 欄位
        # axis=1 代表要刪除的是欄(column)
        # inplace=True 代表直接在 final_df 上進行修改
        final_df.drop('date', axis=1, inplace=True)
        print("已移除重複的日期欄位 'date'。")
        
        # --- 儲存檔案 ---
        # 使用 utf-8-sig 編碼確保 Excel 開啟中文不會亂碼
        final_df.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"成功！合併後的檔案已儲存為 '{output_file}'。")

    except FileNotFoundError:
        print(f"錯誤：找不到指定的檔案。請再次確認檔案名稱及路徑。")
    except Exception as e:
        print(f"處理過程中發生未預期的錯誤: {e}")


# --- 執行程式 ---
if __name__ == '__main__':
    merge_with_weather_data()
