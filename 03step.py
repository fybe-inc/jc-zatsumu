import json
import csv
import time
import requests
from bs4 import BeautifulSoup

# JSONL ファイルおよび出力 CSV のパス
jsonl_path = 'output.jsonl'
csv_path = 'output.csv'

# CSV に書き出すすべてのカラム（各セクションの項目）
csv_header = [
    # １．基本情報
    "求人番号", "受付年月日", "紹介期限日", "受理安定所", "求人区分", "オンライン自主応募の受付", "産業分類", "トライアル雇用併用の希望",
    # ２．求人事業所情報
    "事業所番号", "事業所名（カナ）", "事業所名", "所在地郵便番号", "所在地", "ホームページ",
    # ３．仕事内容・就業条件 (a) 職種・仕事内容
    "職種", "仕事内容", "雇用形態", "派遣・請負等", "雇用期間",
    # ３．仕事内容・就業条件 (b) 就業場所
    "就業場所表示", "就業場所郵便番号", "就業場所住所", "受動喫煙対策",
    # ３．仕事内容・就業条件 (c) その他
    "マイカー通勤可否", "駐車場の有無", "転勤の可能性",
    "年齢制限", "年齢制限範囲", "年齢制限該当事由", "年齢制限理由",
    "学歴", "必要な経験・知識・技能等", "必要なPCスキル", "必要な免許・資格",
    # ３．仕事内容・就業条件 (d) 試用期間
    "試用期間の有無", "試用期間", "試用期間中の労働条件", "試用期間条件詳細",
    # ４．賃金・手当
    "総支給額", "基本給", "定額手当", "固定残業代", "その他手当",
    "月平均労働日数", "賃金形態", "通勤手当", "通勤手当支給形態", "通勤手当金額",
    "賃金締切日", "賃金支払日", "昇給制度", "昇給実績", "昇給金額/率", "賞与制度", "賞与実績",
    # ５．労働時間・休日
    "就業時間形式", "変形労働時間単位", "就業時間1", "就業時間2", "又は就業時間", "就業時間特記事項",
    "時間外労働有無", "月平均時間外労働", "36協定特別条項", "特別な事情",
    "休憩時間", "年間休日数", "休日", "週休二日制", "その他休日", "年次有給休暇日数",
    # ６．その他の労働条件等
    "加入保険等", "退職金共済", "退職金制度", "定年制", "再雇用制度", "勤務延長", "入居可能住宅", "利用可能託児施設",
    # ７．会社の情報
    "従業員数（企業全体）", "従業員数（就業場所）", "うち女性", "うちパート", "設立年", "資本金",
    "労働組合", "事業内容", "会社の特長", "役職", "代表者名", "法人番号",
    "就業規則（フルタイム）", "就業規則（パートタイム）",
    "育児休業実績", "介護休業実績", "看護休暇実績", "外国人雇用実績",
    # ８．選考等
    "採用人数", "募集理由", "選考方法", "選考結果通知タイミング", "面接選考結果通知期間",
    "求職者への通知方法", "選考日時", "選考場所郵便番号", "選考場所住所",
    "応募書類", "応募書類送付方法", "応募書類返戻",
    "担当部署/役職", "担当者（カタカナ）", "担当者", "担当者電話", "担当者FAX",
    # ９．求人特記事項・PR情報
    "求人特記事項", "職務給制度", "復職制度",
    # リンク先（詳細表示URL）
    "詳細表示URL"
]

# 各項目の抽出に用いる CSS セレクタのマッピング
fields = {
    # １．基本情報
    "求人番号": "#ID_kjNo",
    "受付年月日": "#ID_uktkYmd",
    "紹介期限日": "#ID_shkiKigenHi",
    "受理安定所": "#ID_juriAtsh",
    "求人区分": "#ID_kjKbn",
    "オンライン自主応募の受付": "#ID_onlinJishuOboUktkKahi",
    "産業分類": "#ID_sngBrui",
    "トライアル雇用併用の希望": "#ID_tryKoyoKibo",
    # ２．求人事業所情報
    "事業所番号": "#ID_jgshNo",
    "事業所名（カナ）": "#ID_jgshMeiKana",
    "事業所名": "#ID_jgshMei",
    "所在地郵便番号": "#ID_szciYbn",
    "所在地": "#ID_szci",
    "ホームページ": "#ID_hp",
    # ３．仕事内容・就業条件 (a)
    "職種": "#ID_sksu",
    "仕事内容": "#ID_shigotoNy",
    "雇用形態": "#ID_koyoKeitai",
    "派遣・請負等": "#ID_hakenUkeoiToShgKeitai",
    "雇用期間": "#ID_koyoKikan",
    # ３．仕事内容・就業条件 (b)
    "就業場所表示": "#ID_shgBs",
    "就業場所郵便番号": "#ID_shgBsYubinNo",
    "就業場所住所": "#ID_shgBsJusho",
    "受動喫煙対策": "#ID_shgBsKitsuTsak",
    # ３．仕事内容・就業条件 (c)
    "マイカー通勤可否": "#ID_mycarTskn",
    "駐車場の有無": "#ID_mycarTsknChushaUmu",
    "転勤の可能性": "#ID_tenkinNoKnsi",
    "年齢制限": "#ID_nenreiSegn",
    "年齢制限範囲": "#ID_nenreiSegnHanni",
    "年齢制限該当事由": "#ID_nenreiSegnGaitoJiyu",
    "年齢制限理由": "#ID_nenreiSegnNoRy",
    "学歴": "#ID_grki",
    "必要な経験・知識・技能等": "#ID_hynaKiknt",
    "必要なPCスキル": "#ID_hynaPc",
    "必要な免許・資格": "#ID_hynaMenkyoSkku",
    # ３．仕事内容・就業条件 (d)
    "試用期間の有無": "#ID_trialKikan",
    "試用期間": "#ID_trialKikanKikan",
    "試用期間中の労働条件": "#ID_trialKikanChuuNoRodoJkn",
    "試用期間条件詳細": "#ID_trialKikanChuuNoRodoJknNoNy",
    # ４．賃金・手当
    "総支給額": "#ID_chgn",
    "基本給": "#ID_khky",
    "定額手当": "#ID_tgktNiShwrTat",
    "固定残業代": "#ID_koteiZngyKbn",
    "その他手当": "#ID_sntaTatFukiJk",
    "月平均労働日数": "#ID_thkinRodoNissu",
    "賃金形態": "#ID_chgnKeitaiToKbn",
    "通勤手当": "#ID_tsknTat",
    "通勤手当支給形態": "#ID_tsknTatTsuki",
    "通勤手当金額": "#ID_tsknTatKingaku",
    "賃金締切日": "#ID_chgnSkbi",
    "賃金支払日": "#ID_chgnSrbi",
    "昇給制度": "#ID_shokyuSd",
    "昇給実績": "#ID_shokyuMaeNendoJisseki",
    "昇給金額/率": "#ID_sokkgSkrt",
    "賞与制度": "#ID_shoyoSdNoUmu",
    "賞与実績": "#ID_shoyoMaeNendoUmu",
    # ５．労働時間・休日
    "就業時間形式": "#ID_shgJn",
    "変形労働時間単位": "#ID_henkeiRdTani",
    "就業時間1": "#ID_shgJn1",
    "就業時間2": "#ID_shgJn2",
    "又は就業時間": "#ID_shgJnOr",
    "就業時間特記事項": "#ID_shgJiknTkjk",
    "時間外労働有無": "#ID_jkgiRodoJn",
    "月平均時間外労働": "#ID_thkinJkgiRodoJn",
    "36協定特別条項": "#ID_sanrokuKyotei",
    "特別な事情": "#ID_tkbsNaJijo",
    "休憩時間": "#ID_kyukeiJn",
    "年間休日数": "#ID_nenkanKjsu",
    "休日": "#ID_kyjs",
    "週休二日制": "#ID_shukFtskSei",
    "その他休日": "#ID_kyjsSnta",
    "年次有給休暇日数": "#ID_nenjiYukyu",
    # ６．その他の労働条件等
    "加入保険等": "#ID_knyHoken",
    "退職金共済": "#ID_tskinKsi",
    "退職金制度": "#ID_tskinSd",
    "定年制": "#ID_tnsei",
    "再雇用制度": "#ID_saiKoyoSd",
    "勤務延長": "#ID_kmec",
    "入居可能住宅": "#ID_nkj",
    "利用可能託児施設": "#ID_riyoKanoTkjShst",
    # ７．会社の情報
    "従業員数（企業全体）": "#ID_jgisKigyoZentai",
    "従業員数（就業場所）": "#ID_jgisShgBs",
    "うち女性": "#ID_jgisUchiJosei",
    "うちパート": "#ID_jgisUchiPart",
    "設立年": "#ID_setsuritsuNen",
    "資本金": "#ID_shkn",
    "労働組合": "#ID_rodoKumiai",
    "事業内容": "#ID_jigyoNy",
    "会社の特長": "#ID_kaishaNoTokucho",
    "役職": "#ID_yshk",
    "代表者名": "#ID_dhshaMei",
    "法人番号": "#ID_hoNinNo",
    "就業規則（フルタイム）": "#ID_fltmShgKisoku",
    "就業規則（パートタイム）": "#ID_partShgKisoku",
    "育児休業実績": "#ID_ikujiKyugyoStkJisseki",
    "介護休業実績": "#ID_kaigoKyugyoStkJisseki",
    "看護休暇実績": "#ID_kangoKyukaStkJisseki",
    "外国人雇用実績": "#ID_gkjnKoyoJisseki",
    # ８．選考等
    "採用人数": "#ID_saiyoNinsu",
    "募集理由": "#ID_boshuRy",
    "選考方法": "#ID_selectHoho",
    "選考結果通知タイミング": "#ID_selectKekkaTsuch",
    "面接選考結果通知期間": "#ID_mensetsuSelectKekka",
    "求職者への通知方法": "#ID_ksshEnoTsuchiHoho",
    "選考日時": "#ID_selectNichijiTo",
    "選考場所郵便番号": "#ID_selectBsYubinNo",
    "選考場所住所": "#ID_selectBsJusho",
    "応募書類": "#ID_oboShoruitou",
    "応募書類送付方法": "#ID_oboShoruiNoSofuHoho",
    "応募書類返戻": "#ID_obohen",
    "担当部署/役職": "#ID_ttsYkm",
    "担当者（カタカナ）": "#ID_ttsTtsKana",
    "担当者": "#ID_ttsTts",
    "担当者電話": "#ID_ttsTel",
    "担当者FAX": "#ID_ttsFax",
    # ９．求人特記事項・PR情報
    "求人特記事項": "#ID_kjTkjk",
    "職務給制度": "#ID_shokumuKyuSd",
    "復職制度": "#ID_fukushokuSd"
}

# CSV ヘッダーを書き出す（最初に一度だけ）
with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_header)
    writer.writeheader()

def get_text(soup, selector):
    """
    指定の CSS セレクタからテキストを取得します。
    存在しない場合やエラーが発生した場合は空文字を返します。
    """
    try:
        el = soup.select_one(selector)
        if el is not None:
            return el.get_text(strip=True)
    except Exception as e:
        # エラー発生時は空文字を返す
        pass
    return ""

line_count = 0
# JSONL ファイルを 1 行ずつ処理
with open(jsonl_path, 'r', encoding='utf-8') as f:
    for line in f:
        line_count += 1
        try:
            data = json.loads(line)
        except Exception as e:
            print(f"{line_count}: JSON 読み込みエラー")
            continue

        # リンク情報の「詳細を表示」の URL を取得し、先頭の「.」を補完する
        rel_url = data.get("リンク情報", {}).get("詳細を表示", "")
        if rel_url.startswith("."):
            detail_url = "https://www.hellowork.mhlw.go.jp/kensaku" + rel_url[1:]
        else:
            detail_url = rel_url

        # 詳細表示ページの HTML を取得
        try:
            resp = requests.get(detail_url)
            resp.raise_for_status()
        except Exception as e:
            print(f"{line_count}: URL取得エラー")
            continue

        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')

        # 各項目を抽出（セレクタに存在しない場合は get_text() が空文字を返す）
        extracted = {}
        for key, selector in fields.items():
            extracted[key] = get_text(soup, selector)

        # 詳細表示 URL 自体も保存
        extracted["詳細表示URL"] = detail_url

        # CSV に追記する（各求人ごとに書き出す）
        try:
            with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_header)
                writer.writerow(extracted)
        except Exception as e:
            print(f"{line_count}: CSV 書き出しエラー")
            continue

        # 各行の処理が成功した場合、行番号:success を表示（1行につき1回）
        print(f"{line_count}: success")
        time.sleep(1)
