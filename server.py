from flask import Flask, request
import re
import os

app = Flask(__name__)


# ✅ OCR補正
def normalize_text(text):
    text = str(text)
    text = text.upper()
    text = text.replace("O", "0")
    text = text.replace("I", "1")
    text = text.replace("S", "5")
    return text


# ✅ 3桁抽出
def extract_code(text):
    nums = re.findall(r"\d{3}", text)
    if nums:
        return nums[-1]
    return "なし"


# ✅ 見やすく整形（ここが今回のキモ🔥）
def format_text(text):
    # キーワードごとに改行
    text = text.replace("CASE", "\nCASE")
    text = text.replace("NO.", "\nNO.")
    text = text.replace("NO ", "\nNO ")
    text = text.replace("LOT", "\nLOT")
    text = text.replace("CONTROL", "\nCONTROL")
    text = text.replace("PART", "\nPART")
    text = text.replace("QTY", "\nQTY")

    return text.strip()


@app.route("/check", methods=["POST"])
def check():
    data = request.json or {}

    text1 = normalize_text(data.get("text1", ""))
    text2 = normalize_text(data.get("text2", ""))

    text1 = text1.replace("\\n", "\n")
    text2 = text2.replace("\\n", "\n")

    # ✅ 整形
    text1 = format_text(text1)
    text2 = format_text(text2)

    code1 = extract_code(text1)
    code2 = extract_code(text2)

    # ✅ 判定
    if code1 == "なし" or code2 == "なし":
        result = "⚠️ 読み取り失敗"
    elif code1 == code2:
        result = "✅ OK"
    else:
        result = "❌ NG"

    display_text = f"""
====================
判定結果: {result}
====================

🔢 コード
{code1} / {code2}

--------------------

🔵 ラベル①
{text1}

--------------------

🟢 ラベル②
{text2}
"""

    return display_text


@app.route("/")
def home():
    return "Server is running ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
