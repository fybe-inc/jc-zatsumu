import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def main():
    # ChromeDriverなどを使用する場合の例
    driver = webdriver.Chrome()

    # 1. 指定ページへ遷移
    driver.get("https://www.hellowork.mhlw.go.jp/kensaku/GECA110010.do?action=initDisp&screenId=GECA110010")
    time.sleep(1)

    # 2. フルタイム, パートのチェックボックスにチェックを付ける
    driver.find_element(By.ID, "ID_ippanCKBox1").click()
    driver.find_element(By.ID, "ID_ippanCKBox2").click()
    time.sleep(1)

    # 3. OR検索ラジオボタンにチェックを付ける
    driver.find_element(By.ID, "ID_freeWordRadioBtn0").click()
    time.sleep(1)

    # 4. フリーワード入力
    keyword = "外国人歓迎　Ｎ１　Ｎ２　Ｎ３　Ｎ４　Ｎ５　日本語不問　日本語レベル不問"
    driver.find_element(By.ID, "ID_freeWordInput").send_keys(keyword)
    time.sleep(1)

    # 5. 検索ボタンクリック
    driver.find_element(By.ID, "ID_searchBtn").click()
    time.sleep(1)

    while True:
        # 1秒待機
        time.sleep(1)

        # HTMLを取得して保存
        html_source = driver.page_source
        unix_time = int(time.time())
        file_name = f"{unix_time}.html"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(html_source)

        try:
            # 次へ＞ボタンを取得
            next_button = driver.find_element(By.NAME, "fwListNaviBtnNext")

            # ボタンが disable ならループ終了
            if next_button.get_attribute("disabled"):
                print("次へ＞ ボタンが無効になったため終了します。")
                break

            # ボタンが有効ならクリックして次のページへ
            next_button.click()

        except Exception as e:
            # 次へ＞ボタンが見つからない場合などはループ終了
            print(f"次へ＞ ボタンが見つからないかエラーが発生したため終了します: {e}")
            break

    # ブラウザを閉じる
    driver.quit()

if __name__ == "__main__":
    main()