import pandas as pd
import os

# --- 設定 ---
# 檔案名稱
file_gpx = 'Taoshan_route_GPX_file_analysis_results.csv'
file_html = 'webscrapping4HTML_Taoshan.csv'
output_file = 'merged_taoshan_data.csv'

# --- 主程式 ---
def merge_taoshan_data():
    """
    使用 INNER JOIN 合併兩個 CSV 檔案，
    條件為 end_date 和 total_time 皆相同。
    """
    # 檢查檔案是否存在
    if not os.path.exists(file_gpx) or not os.path.exists(file_html):
        print(f"錯誤：請確認 '{file_gpx}' 和 '{file_html}' 都存在於同一個資料夾中。")
        return

    try:
        # --- 讀取檔案 (修正點) ---
        # 明確指定使用 'cp950' 編碼來讀取來源檔案
        print(f"正在嘗試使用 'cp950' 編碼讀取 '{file_gpx}'...")
        df_gpx = pd.read_csv(file_gpx, encoding='cp950')

        print(f"正在嘗試使用 'cp950' 編碼讀取 '{file_html}'...")
        # 檔案2: 網頁爬取結果 (從檔案內容看是 Tab 分隔的)
        df_html = pd.read_csv(file_html, sep='\t', encoding='cp950')

        print("\n成功讀取檔案。開始進行資料清理與合併...")
        print(f"'{file_gpx}' 原始筆數: {len(df_gpx)}")
        print(f"'{file_html}' 原始筆數: {len(df_html)}")

        # --- 資料清理與標準化 (合併前的關鍵步驟) ---

        # 1. 標準化 'end_date' 欄位格式，以便正確比對
        df_gpx['end_date'] = pd.to_datetime(df_gpx['end_date'], errors='coerce')
        df_html['end_date'] = pd.to_datetime(df_html['end_date'], errors='coerce')

        # 2. 確保 'total_time' 欄位為數值型態 (整數)
        df_gpx['total_time'] = pd.to_numeric(df_gpx['total_time'], errors='coerce').astype('Int64')
        df_html['total_time'] = pd.to_numeric(df_html['total_time'], errors='coerce').astype('Int64')
        
        # 移除因格式轉換錯誤而產生的空值列，避免合併失敗
        df_gpx.dropna(subset=['end_date', 'total_time'], inplace=True)
        df_html.dropna(subset=['end_date', 'total_time'], inplace=True)

        # --- 執行合併 ---
        # 使用 'inner' join 合併，條件為 end_date 和 total_time
        merged_df = pd.merge(
            df_gpx,
            df_html,
            how='inner',
            on=['end_date', 'total_time']
        )
        
        print(f"\n合併完成！共找到 {len(merged_df)} 筆符合條件的資料。")

        # --- 處理重複欄位並儲存 ---
        # Pandas 會自動為來源不同但名稱相同的欄位加上 _x 和 _y 後綴
        # 例如 file_name_x (來自df_gpx) 和 file_name_y (來自df_html)
        # 您可以視需求重新命名或刪除其中一個
        
        # 儲存合併後的檔案
        # 使用 utf-8-sig 編碼確保 Excel 開啟中文不會亂碼
        merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"成功！合併後的檔案已儲存為 '{output_file}'。")

    except FileNotFoundError:
        print(f"錯誤：找不到指定的檔案。請再次確認檔案名稱及路徑。")
    except Exception as e:
        print(f"處理過程中發生未預期的錯誤: {e}")


# --- 執行程式 ---
if __name__ == '__main__':
    merge_taoshan_data()
