import os
import re
import json
import csv

def extract_job_data_from_html(html_text):
    """
    HTML 内の「window['__RQ:Rakq:']」に push されている JSON オブジェクト群を
    複数回 .push(...) している場合も含め、すべて取得し、
    その中から 'jmJobOffers' (求人リスト) を収集して返す。
    """

    # 正規表現パターン:
    #   window["__RQ:Rakq:"].push( {...} );
    pattern = r'window\["__RQ:Rakq:"\]\.push\(\s*(\{.*?\})\s*\)\s*;'
    snippets = re.findall(pattern, html_text, flags=re.DOTALL)

    job_data_list = []
    
    for json_str in snippets:
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            # 破損した JSON などがあればスキップ
            continue

        # "queries" に含まれるデータを探す
        queries = data.get("queries", [])
        for q in queries:
            state = q.get("state")
            if not state or "data" not in state:
                continue
            sub_data = state["data"]

            # "jmJobOffers" キーがあれば求人情報配列とみなし、リストに追加
            if "jmJobOffers" in sub_data:
                job_data_list.extend(sub_data["jmJobOffers"])
            # 必要に応じて他のキーも探す場合はここで追加

    return job_data_list


def main():
    # 入出力設定
    input_dir = "./tmp"
    output_csv = "jobs.csv"

    # 書き出す項目（ヘッダ）
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

    # CSV を "w" モードで開き、ヘッダを書き込む
    # → 各ファイルを順番に処理して1つのCSVにまとめる
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=columns,
            quoting=csv.QUOTE_ALL,
            quotechar='"',
            escapechar='\\'
        )
        writer.writeheader()

        total_jobs_count = 0

        # tmpディレクトリ内のファイルを走査
        for filename in sorted(os.listdir(input_dir)):
            if not filename.endswith(".html"):
                # HTML以外はスキップ
                continue

            filepath = os.path.join(input_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                html_text = f.read()

            # 抽出
            jobs = extract_job_data_from_html(html_text)
            if not jobs:
                print(f"  {filename} からは求人が見つかりませんでした。")
                continue

            # CSV に書き出す
            for j in jobs:
                row = {}
                row["id"] = j.get("id")
                row["updatedAt"] = j.get("updatedAt")
                row["jobTitle"] = j.get("jobTitle")
                row["jobOfferCardTitle"] = j.get("jobOfferCardTitle")

                salary_list = j.get("jobOfferCardSalaryList", [])
                row["jobOfferCardSalaryList"] = " / ".join(salary_list) if salary_list else ""

                row["appealTitle"] = j.get("appealTitle")
                row["requiredText"] = j.get("requiredText")

                facility = j.get("facility", {})
                row["facilityName"] = facility.get("name")
                row["facilityAddress"] = facility.get("addressEtc")
                row["facilityAccess"] = facility.get("access")

                writer.writerow(row)
            total_jobs_count += len(jobs)
            print(f"  {filename} から {len(jobs)} 件を追加しました。")

    print(f"\n合計 {total_jobs_count} 件の求人を '{output_csv}' に書き出しました。")

if __name__ == "__main__":
    main()
