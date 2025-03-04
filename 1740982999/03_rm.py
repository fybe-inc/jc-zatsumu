import csv

def remove_duplicates(input_csv, output_csv):
    """
    jobs.csv を読み込み、同じ id を持つ行が重複していたら片方をスキップして
    重複のない形で output_csv に書き出す。
    """
    seen_ids = set()
    rows_no_dup = []

    with open(input_csv, "r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        # CSV の列名（fieldnames）を確保しておく
        fieldnames = reader.fieldnames

        for row in reader:
            row_id = row.get("id")
            if row_id not in seen_ids:
                # まだ見ていない id なら、出力用に確保して set に追加
                rows_no_dup.append(row)
                seen_ids.add(row_id)
            else:
                # すでに id が存在する行はスキップ
                pass

    # 重複除去済みリストを新しい CSV に書き出す
    with open(output_csv, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in rows_no_dup:
            writer.writerow(row)

    print(f"Duplicates removed. Wrote {len(rows_no_dup)} unique rows to '{output_csv}'.")


def main():
    input_csv = "jobs.csv"
    output_csv = "jobs_deduplicated.csv"
    remove_duplicates(input_csv, output_csv)


if __name__ == "__main__":
    main()
