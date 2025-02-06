import os
import glob
import json
import re
from bs4 import BeautifulSoup

def parse_job_table(table):
    """
    １つの求人情報テーブルから情報を抽出して辞書にまとめる関数です。
    例外が発生しても None 等を返すようにし、処理が止まらないようにしています。
    """
    job = {}

    try:
        # 職種（タイトル）は td クラス "m13 fs1" 内のテキスト
        title_tag = table.find("td", class_="m13 fs1")
        job["職種"] = title_tag.get_text(strip=True) if title_tag else None
    except Exception as e:
        job["職種"] = None

    try:
        # 「新着」ラベルの有無（spanクラス "nes_label nes" が存在すれば True）
        job["新着"] = bool(table.find("span", class_="nes_label nes"))
    except Exception as e:
        job["新着"] = False

    try:
        # 受付年月日・紹介期限日の抽出
        date_div = table.find("div", class_="flex fs13")
        if date_div:
            text = date_div.get_text(separator=" ", strip=True)
            m = re.search(r"受付年月日：(\S+).*紹介期限日：(\S+)", text)
            if m:
                job["受付年月日"] = m.group(1)
                job["紹介期限日"] = m.group(2)
            else:
                job["受付年月日"] = None
                job["紹介期限日"] = None
        else:
            job["受付年月日"] = None
            job["紹介期限日"] = None
    except Exception as e:
        job["受付年月日"] = None
        job["紹介期限日"] = None

    # 基本情報（左側）
    basic = {}
    try:
        left_div = table.find("div", class_="left-side")
        if left_div:
            rows = left_div.find_all("tr", class_="border_new")
            for row in rows:
                tds = row.find_all("td")
                if len(tds) >= 2:
                    field = tds[0].get_text(strip=True)
                    value = tds[1].get_text(separator="\n", strip=True)
                    basic[field] = value
    except Exception as e:
        pass
    job["基本情報"] = basic

    # 勤務条件（右側）
    work_cond = {}
    try:
        right_div = table.find("div", class_="right-side")
        if right_div:
            rows = right_div.find_all("tr", class_="border_new")
            for row in rows:
                tds = row.find_all("td")
                if len(tds) >= 2:
                    field = tds[0].get_text(strip=True)
                    value = tds[1].get_text(separator="\n", strip=True)
                    work_cond[field] = value
    except Exception as e:
        pass
    job["勤務条件"] = work_cond

    try:
        # 求人数を正規表現で抽出
        num_text = table.get_text(separator=" ", strip=True)
        m_num = re.search(r"求人数：\s*(\d+)", num_text)
        job["求人数"] = int(m_num.group(1)) if m_num else None
    except Exception as e:
        job["求人数"] = None

    # リンク情報
    links = {}
    try:
        link1 = table.find("a", id="ID_kyujinhyoBtn")
        if link1 and link1.has_attr("href"):
            links["求人票を表示"] = link1["href"]
        else:
            links["求人票を表示"] = None
    except Exception as e:
        links["求人票を表示"] = None

    try:
        link2 = table.find("a", id="ID_dispDetailBtn")
        if link2 and link2.has_attr("href"):
            links["詳細を表示"] = link2["href"]
        else:
            links["詳細を表示"] = None
    except Exception as e:
        links["詳細を表示"] = None

    job["リンク情報"] = links

    return job

def main():
    # 処理対象の HTML ファイルが格納されたディレクトリ（適宜変更してください）
    html_dir = "./"
    # 拡張子 .html のファイル一覧
    file_list = glob.glob(os.path.join(html_dir, "*.html"))

    # 出力先（JSON Lines形式：1行に1件の JSON オブジェクト）
    output_file = "output.jsonl"
    with open(output_file, "w", encoding="utf-8") as out_f:
        # 各ファイルを順番に処理
        for file_path in file_list:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f, "html.parser")
            except Exception as e:
                print(f"ファイル {file_path} の読み込みでエラー: {e}")
                continue

            try:
                # 求人情報は <table class="kyujin mt1 noborder"> 内にあるとする
                tables = soup.find_all("table", class_="kyujin mt1 noborder")
            except Exception as e:
                print(f"ファイル {file_path} からテーブルが取得できませんでした: {e}")
                continue

            for table in tables:
                try:
                    job_info = parse_job_table(table)
                    # 各求人情報を JSON 形式にして1行ずつ出力
                    out_f.write(json.dumps(job_info, ensure_ascii=False) + "\n")
                except Exception as e:
                    print(f"求人情報の解析に失敗: {e}")
                    continue

if __name__ == "__main__":
    main()
