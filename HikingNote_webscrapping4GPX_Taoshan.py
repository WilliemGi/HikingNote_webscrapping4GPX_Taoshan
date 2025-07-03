import os
import time
import pathlib
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 從環境變數中讀取帳號與密碼
load_dotenv()
USERNAME = os.getenv("MY_USERNAME")
PASSWORD = os.getenv("MY_PASSWORD")

# 設定下載目錄，建立新資料夾「桃山GPX檔」
current_dir = pathlib.Path(os.getcwd()).resolve()  # 獲取當前工作目錄
download_dir = current_dir / "桃山GPX檔"  # 建立「桃山GPX檔」資料夾
if not download_dir.exists():
    download_dir.mkdir()  # 如果資料夾不存在，則建立
DOWNLOAD_DIR = download_dir.as_posix()

# 設定瀏覽器選項
opts = webdriver.ChromeOptions()
opts.add_argument("--start-maximized")
opts.add_argument("--disable-popup-blocking")
opts.add_argument("--disable-notifications")
opts.add_argument("--lang=zh-TW")


# 啟動 driver
driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 10)

# 開啟目標網站
url = "https://hiking.biji.co/index.php?q=trail&act=detail&id=429"
driver.get(url)
time.sleep(1)

# 點擊 cookie 同意按鈕
try:
    cookie_btn = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button[class*='bg-primary']")))
    cookie_btn.click()
except Exception:
    pass  # 如果沒出現 cookie banner，直接跳過


# 等頁面載完後再點 GPX 分頁
wait.until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, "div.tab-item[data-type='gpx']"))).click()

# 點擊 GPX 下載按鈕
try:
    gpx_download_button = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "a.w-14.space-y-1.text-current>div")))

    # 滾動到目標元素
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", gpx_download_button)

    # 使用 JavaScript 強制點擊
    driver.execute_script("arguments[0].click();", gpx_download_button)
    print("成功點擊 GPX 下載按鈕")
except Exception as e:
    print(f"點擊 GPX 下載按鈕失敗: {e}")

# 輸入帳號與密碼進行登入
try:
    inputs = wait.until(EC.visibility_of_all_elements_located(
        (By.CSS_SELECTOR, "input.el-input__inner")))
    inputs[0].send_keys(USERNAME)
    inputs[1].send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button#normalLogin").click()
    print("登入成功！")
except Exception:
    print("登入頁面未顯示")

# 等第一個載完
time.sleep(2)
# 返回首頁
driver.back()
time.sleep(1)
# 點擊 GPX 分頁
wait.until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, "div.tab-item[data-type='gpx']"))).click()
time.sleep(2)


# 等頁面載完後再點 GPX 分頁
wait.until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, "div.tab-item[data-type='gpx']"))).click()

# 滾動並載入更多內容
def scroll():
    innerHeight = 0
    offset = 0
    count = 0
    limit = 3

    while count <= limit:
        offset = driver.execute_script(
            "return document.documentElement.scrollHeight;")
        driver.execute_script(f"window.scrollTo({{top: {offset}, behavior:'smooth'}})")
        time.sleep(1)

        try:
            load_more = driver.find_element(By.CSS_SELECTOR,
                                            "button.btn.btn-rect--m.btn--secondary")
            load_more.click()
            print("已點擊載入更多")
            time.sleep(1)
            count = 0
        except Exception:
            count += 1

scroll()

# 依序從第一個點到最後一個
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

hrefs = [a['href'] for a in soup.select('a.w-14.space-y-1.text-current')]

for href in hrefs:
    try:
        link = driver.find_element(By.CSS_SELECTOR, f"a[href='{href}']")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
        driver.execute_script("arguments[0].click();", link)
        time.sleep(1)
    except Exception:
        continue



print("已依序點完全部下載連結！")
driver.quit()
