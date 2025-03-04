#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
APIサーバーを叩く最も簡単なアプリ
"""

import requests
import json

def main():
    """メイン関数"""
    try:
        # JSONPlaceholderの公開APIにGETリクエストを送信
        url = "https://www.yolo-japan.com/ja/recruit/job/ajax/list/73?order=new"
        response = requests.get(url)
        
        # HTTPステータスコードをチェック
        response.raise_for_status()
        
        # JSONレスポンスを取得
        data = response.json()
        
        # 結果を整形して表示
        print("APIリクエスト成功！")
        print("レスポンスデータ:")
        print(json.dumps(data, indent=4, ensure_ascii=False))
        
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"APIリクエストエラー: {e}")
        return None

if __name__ == "__main__":
    main()