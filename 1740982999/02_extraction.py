import re
import json
import csv

def extract_job_data_from_html(html_text):
    """
    HTML 内の「window['__RQ:Rakq:']」に push されている JSON オブジェクト群を
    複数回 .push(...) している場合も含め、すべて取得し、
    その中から 'jmJobOffers' (求人リスト) を収集して返す。
    """

    # 1) 正規表現で .push({...}) の JSON 部分をすべて抜き出す
    #
    #   - "window\["__RQ:Rakq:"\].push\((" の直後から対応する「}）;」までを取得
    #   - DOTALL フラグで改行を跨いでもマッチ可能に
    #   - 最初の行にある「= window['__RQ:Rakq:'] || []」の有無は必須にしない(柔軟に)
    #
    pattern = r'window\["__RQ:Rakq:"\]\.push\(\s*(\{.*?\})\s*\)\s*;'
    snippets = re.findall(pattern, html_text, flags=re.DOTALL)

    job_data_list = []
    
    # 2) 見つかったすべての JSON スニペットをパースし、jmJobOffers を取得
    for json_str in snippets:
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            # JSON の構造が壊れている場合など（環境によっては不要なら無視してもOK）
            continue

        queries = data.get("queries", [])
        for q in queries:
            state = q.get("state")
            if not state or "data" not in state:
                continue
            sub_data = state["data"]
            # "jmJobOffers" キーを持つものは求人情報とみなす
            if "jmJobOffers" in sub_data:
                job_data_list.extend(sub_data["jmJobOffers"])
            # 必要に応じて "hwJobOffers" 等も集約したい場合は追加

    return job_data_list


def main():
    # 入出力ファイルパス
    input_html = "./tmp/20250303_153843_page001.html"
    output_csv = "jobs.csv"

    # 1) HTML を全部読み込み
    with open(input_html, "r", encoding="utf-8") as f:
        html_text = f.read()

    # 2) 求人データを抽出
    jobs = extract_job_data_from_html(html_text)

    if not jobs:
        print("求人データが見つかりませんでした。")
        return

    # 3) CSV のカラムを定義
    columns = [
        "id",
        "updatedAt",
        "jobTitle",
        "jobOfferCardTitle",
        "jobOfferCardSalaryList",
        "appealTitle",
        "requiredText",
        "facilityName",
        "facilityAddress",
        "facilityAccess"
    ]

    # 4) CSV 書き出し
    #    改行を含むセルを正しく扱うため quoting=csv.QUOTE_ALL を使用
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=columns,
            quoting=csv.QUOTE_ALL,  # 全フィールドをダブルクォート
            quotechar='"',
            escapechar='\\'         # 万が一ダブルクォートが混入していてもエスケープできるように
        )
        writer.writeheader()

        count = 0
        for j in jobs:
            row = {}
            row["id"]                   = j.get("id")
            row["updatedAt"]            = j.get("updatedAt")
            row["jobTitle"]             = j.get("jobTitle")
            row["jobOfferCardTitle"]    = j.get("jobOfferCardTitle")

            # 給与リストは配列になっているので結合しておく
            salary_list = j.get("jobOfferCardSalaryList", [])
            row["jobOfferCardSalaryList"] = " / ".join(salary_list) if salary_list else ""

            row["appealTitle"]          = j.get("appealTitle")
            row["requiredText"]         = j.get("requiredText")

            facility = j.get("facility", {})
            row["facilityName"]         = facility.get("name")
            row["facilityAddress"]      = facility.get("addressEtc")
            row["facilityAccess"]       = facility.get("access")

            writer.writerow(row)
            count += 1

    print(f"合計 {count} 件の求人を '{output_csv}' に書き出しました。")


if __name__ == "__main__":
    main()
