import csv

input_file = 'jobs_deduplicated.csv'
output_file = 'output.csv'

# facilityNameの重複を避けるためのセット
seen_facilities = set()

with open(input_file, mode='r', encoding='utf-8') as infile, \
     open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    
    # ヘッダーを書き込む
    writer.writeheader()
    
    for row in reader:
        facility_name = row['facilityName']
        if facility_name not in seen_facilities:
            writer.writerow(row)
            seen_facilities.add(facility_name)
