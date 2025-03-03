import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ディレクトリの確認と作成
if not os.path.exists('pages'):
    os.makedirs('pages')

# # Chromeのオプション設定
# chrome_options = Options()
# chrome_options.add_argument('--headless')  # ヘッドレスモードで実行
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')

# WebDriverの初期化
driver = webdriver.Chrome()

# 初期URL
url = "https://job-medley.com/hh/search/?job_category_code=hh&prefecture_id=13&city_id%5B%5D=13101&city_id%5B%5D=13102&city_id%5B%5D=13103&city_id%5B%5D=13104&city_id%5B%5D=13105&city_id%5B%5D=13106&city_id%5B%5D=13107&city_id%5B%5D=13108&city_id%5B%5D=13109&city_id%5B%5D=13110&city_id%5B%5D=13111&city_id%5B%5D=13112&city_id%5B%5D=13113&city_id%5B%5D=13114&city_id%5B%5D=13115&city_id%5B%5D=13116&city_id%5B%5D=13117&city_id%5B%5D=13118&city_id%5B%5D=13119&city_id%5B%5D=13120&city_id%5B%5D=13121&city_id%5B%5D=13122&city_id%5B%5D=13123&designated_city_id=4&hw=1&order=2"

try:
    page_number = 1
    
    while True:
        print(f"ページ {page_number} を処理中...")
        
        # URLにアクセス
        driver.get(url)
        
        # ページが完全に読み込まれるまで待機
        time.sleep(3)
        
        # HTMLを取得
        html_content = driver.page_source
        
        # ファイル名を生成（日時とページ番号を含む）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_page{page_number:03d}.html"
        filepath = os.path.join('pages', filename)
        
        # HTMLをファイルに保存
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"ページ {page_number} を保存しました: {filepath}")
        
        # 「次へ」ボタンを探す
        try:
            # 「次へ」ボタンが無効になっているか確認
            disabled_next_button = driver.find_elements(By.XPATH, "//a[@aria-label='次のページへ' and @aria-disabled='true']")
            if disabled_next_button:
                print("「次へ」ボタンが無効です。全ページの取得が完了しました。")
                break
            
            # 有効な「次へ」ボタンを探してクリック
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='次のページへ' and @aria-disabled='false']"))
            )
            
            # 次のページのURLを取得
            url = next_button.get_attribute('href')
            
            # ページ番号をインクリメント
            page_number += 1
            
        except (TimeoutException, NoSuchElementException):
            print("「次へ」ボタンが見つからないか、クリックできません。全ページの取得が完了しました。")
            break

except Exception as e:
    print(f"エラーが発生しました: {e}")

finally:
    # WebDriverを終了
    driver.quit()
    print("処理が完了しました。")
