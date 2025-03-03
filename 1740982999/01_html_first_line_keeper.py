import os
import glob
from datetime import datetime

def main():
    # 処理開始メッセージ
    print("HTMLファイルの1行目以外を削除する処理を開始します...")
    
    # 開始時間を記録
    start_time = datetime.now()
    
    # tmpディレクトリ内のすべてのHTMLファイルを取得
    html_files = glob.glob(os.path.join('tmp', '*.html'))
    
    # ファイル数を表示
    total_files = len(html_files)
    print(f"処理対象ファイル数: {total_files}")
    
    # 処理したファイル数をカウント
    processed_files = 0
    total_size_before = 0
    total_size_after = 0
    
    # 各HTMLファイルを処理
    for html_file in html_files:
        try:
            # 処理前のファイルサイズを取得
            file_size_before = os.path.getsize(html_file)
            total_size_before += file_size_before
            
            # ファイルを開いて1行目だけを読み取る
            with open(html_file, 'r', encoding='utf-8') as f:
                first_line = f.readline()
            
            # 同じファイルに1行目だけを書き込み直す
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(first_line)
            
            # 処理後のファイルサイズを取得
            file_size_after = os.path.getsize(html_file)
            total_size_after += file_size_after
            
            # 処理したファイル数をインクリメント
            processed_files += 1
            
            # 詳細なログを出力（最初の5ファイルと、その後は10ファイルごと）
            if processed_files <= 5 or processed_files % 10 == 0 or processed_files == total_files:
                print(f"進捗: {processed_files}/{total_files} - {html_file}")
                print(f"  サイズ変更: {file_size_before} バイト → {file_size_after} バイト")
                
        except Exception as e:
            print(f"エラー: {html_file} の処理中に問題が発生しました - {e}")
    
    # 終了時間を記録
    end_time = datetime.now()
    
    # 処理時間を計算
    processing_time = end_time - start_time
    
    # 結果を表示
    print(f"\n処理が完了しました。")
    print(f"処理ファイル数: {processed_files}/{total_files}")
    print(f"処理前の合計サイズ: {total_size_before} バイト")
    print(f"処理後の合計サイズ: {total_size_after} バイト")
    print(f"削減されたサイズ: {total_size_before - total_size_after} バイト")
    print(f"処理時間: {processing_time}")

if __name__ == "__main__":
    main()