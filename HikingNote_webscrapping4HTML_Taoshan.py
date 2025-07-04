'''
匯入套件
'''
# 操作 browser 的 API
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# 處理逾時例外的工具
from selenium.common.exceptions import TimeoutException
# 面對動態網頁，等待某個元素出現的工具，通常與 exptected_conditions 搭配
from selenium.webdriver.support.ui import WebDriverWait
# 搭配 WebDriverWait 使用，對元素狀態的一種期待條件，若條件發生，則等待結束，往下一行執行
from selenium.webdriver.support import expected_conditions as EC
# 期待元素出現要透過什麼方式指定，通常與 EC、WebDriverWait 一起使用
from selenium.webdriver.common.by import By
# 強制等待 (執行期間休息一下)
from time import sleep
import time
# 加入行為鍊 ActionChain (在 WebDriver 中模擬滑鼠移動、點擊、拖曳、按右鍵出現選單，以及鍵盤輸入文字、按下鍵盤上的按鈕等)
from selenium.webdriver.common.action_chains import ActionChains
# 啟動瀏覽器工具的選項
my_options = webdriver.ChromeOptions()
# my_options.add_argument("--headless")                #不開啟實體瀏覽器背景執行
my_options.add_argument("--start-maximized")         #最大化視窗
my_options.add_argument("--incognito")               #開啟無痕模式
my_options.add_argument("--disable-popup-blocking") #禁用彈出攔截
my_options.add_argument("--disable-notifications")  #取消 chrome 推播通知
my_options.add_argument("--lang=zh-TW")  #設定為正體中文
# 使用 Chrome 的 WebDriver
# my_service = Service(executable_path="./chromedriver.exe")
# 啟動 driver
driver = webdriver.Chrome(options=my_options)
# 開啟網頁
driver.get("https://hiking.biji.co/index.php?q=trail&act=detail&id=429")
sleep(3)

# 點擊 cookie 同意按鈕
dragger1 = driver.find_element(By.CSS_SELECTOR, "button.bg-primary.text-white.px-4.py-2.rounded")
ActionChains(driver).click(dragger1).perform()
sleep(1)

# 點擊 相關GPX tab
dragger = driver.find_element(By.CSS_SELECTOR, "div.tab-item[data-type='gpx']")
ActionChains(driver).click(dragger).perform()
sleep(2)


# 滾動頁面並點擊「載入更多」
def scroll():
    innerHeight = 0
    offset = 0
    count = 0
    limit = 3
    
    while count <= limit:
        offset = driver.execute_script('return document.documentElement.scrollHeight;')
        
        # 捲動到底
        driver.execute_script(f'window.scrollTo({{top: {offset}, behavior:"smooth"}})')
        sleep(3)
        
        # 點擊「載入更多」按鈕（如果有的話）
        try:
            load_more_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-rect--m.btn--secondary")
            load_more_button.click()  # ActionChains 這裡其實不用，用 click() 就好
            print("已點擊載入更多")
            sleep(2)
        except Exception:
            print("沒有更多內容可以載入了。")
            count += 1  # 無法再載入就計入無效滾動次數
        
        innerHeight = driver.execute_script('return document.documentElement.scrollHeight;')
        
        if offset == innerHeight:
            count += 1
        else:
            count = 0  # 如果有新的內容就重置計數器

# ✅ 呼叫滾動函式
scroll()
# 等待頁面載入完成

from selenium import webdriver
# 確保滾動完、載入更多完成，再抓取 HTML
from bs4 import BeautifulSoup
import json

# 取得網頁原始碼
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# 找出所有記錄區塊
cards = soup.find_all("div", class_="flex-1 p-5 space-y-2.5")

# 建立空字典
records = {}

# 逐一處理每一筆資料
for i, card in enumerate(cards):
    try:
        title = card.find("h3", class_="text-xl truncate").a.text.strip()
    except:
        title = "無標題"

    try:
        info_list = card.find("ul", class_="grid").find_all("li")
        distance = info_list[0].find("span").text.strip()
        duration = info_list[1].find("span").text.strip()
        ascent = info_list[2].find("span").text.strip()
        descent = info_list[3].find("span").text.strip()
        date = info_list[4].find("span").text.strip()
    except:
        distance = duration = ascent = descent = date = "無資料"

    try:
        member_href = card.find("a", href=True, class_="flex items-center space-x-1.5")["href"]
        member_link = "https://hiking.biji.co/" + member_href
    except:
        member_link = "無紀錄者"

    # 整理成字典，紀錄名稱自動編號
    records[f"紀錄{i+1}"] = {
        "file_name": title,
        "distance": distance,
        "total_time_hrs_mins": duration,
        "total_ascent": ascent,
        "total_descent": descent,
        "end_date": date,
        "user": member_link
    }

# 輸出成 JSON 檔
with open("record.json", "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=4)

# 關閉 driver
driver.quit()