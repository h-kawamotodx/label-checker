from flask import Flask, request, jsonify
import re
import os
import requests
from datetime import datetime

app = Flask(__name__)

# ✅ Notion設定
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID = "37f25b7b2a81800996b5d9f3a04f7f1f"


# ✅ OCR補正
def normalize_text(text):
    text = text.upper()
    text = text.replace("O", "0")
    text = text.replace("I", "1")
    text = text.replace("S", "5")
    return text


# ✅ 3桁抽出
def extract_code(text):
    text = normalize_text(text)

    nums = re.findall(r"\d{3}", text)
    if nums:
        return nums[-1]

    return None


# ✅ Notion保存
def save_to_notion(text1, text2, code1, code2, result):
    try:
        url = "https://api.notion.com/v1/pages"

        headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        data = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "タイトル": {
                    "title": [
                        {"text": {"content": datetime.now().strftime("%H:%M:%S")}}
                    ]
                },
                "result": {
                    "rich_text": [{"text": {"content": result}}]
                },
                "code1": {
                    "rich_text": [{"text": {"content": str(code1)}}]
                },
                "code2": {
                    "rich_text": [{"text": {"content": str(code2)}}]
                },
                "text1": {
                    "rich_text": [{"text": {"content": text1[:100]}}]
                },
                "text2": {
                    "rich_text": [{"text": {"content": text2[:100]}}]
                }
            }
        }

        response = requests.post(url, headers=headers, json=data)

        print("Notion status:", response.status_code)
        print("Response:", response.text)

    except Exception as e:
        print("Notion error:", e)


@app.route("/check", methods=["POST"])
def check():
    data = request.json

    text1 = normalize_text(data.get("text1", ""))
    text2 = normalize_text(data.get("text2", ""))

    # ✅ 改行修正（ここが超重要🔥）
    text1 = text1.replace("\\n", "\n")
    text2 = text2.replace("\\n", "\n")

    code1 = extract_code(text1)
    code2 = extract_code(text2)

    # ✅ 判定
    if not code1 or not code2:
        result = "⚠️ 読み取り失敗"
    elif code1 == code2:
        result = "✅ OK"
    else:
        result = "❌ NG"

    # ✅ Notion保存
    if NOTION_API_KEY:
        save_to_notion(text1, text2, code1, code2, result)

    # ✅ 表示（見やすく最適化🔥）
    display_text = f"""
====================
判定結果: {result}
====================

🔵 ラベル①（抜粋）
{text1[:80]}

🟢 ラベル②（抜粋）
{text2[:80]}

--------------------
🔢 抽出コード
{code1} / {code2}
--------------------
"""

    return jsonify({
        "result": result,
        "display": display_text
    })


@app.route("/")
def home():
    return "Server is running ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
