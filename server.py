from flask import Flask, request
import re
import os

app = Flask(__name__)


# ✅ OCR補正（誤認識対策）
def normalize_text(text):
    text = str(text).upper()
    text = text.replace("O", "0")  # O → 0
    text = text.replace("I", "1")  # I → 1
    text = text.replace("S", "5")  # S → 5（必要に応じて）
    return text


# ✅ CASE NO抽出（3桁限定）
def extract_case_no(text):
    patterns = [
        r"CASE[- ]?NO\.?\s*(\d{3})",
        r"C/NO\.?\s*(\d{3})"
    ]

    for p in patterns:
        match = re.search(p, text)
        if match:
            return match.group(1)

    return "なし"


@app.route("/check", methods=["POST"])
def check():
    data = request.json or {}

    # ✅ OCR入力
    text1 = normalize_text(data.get("text1", ""))
    text2 = normalize_text(data.get("text2", ""))

    # ✅ CASE NO抽出
    case1 = extract_case_no(text1)
    case2 = extract_case_no(text2)

    # ✅ 判定
    if case1 == case2 and case1 != "なし":
        result = "✅✅ 完全一致"
    elif case1 == "なし" or case2 == "なし":
        result = "⚠️ CASE NO 読み取り失敗"
    else:
        result = "🔥❌ NG（不一致）🔥"

    # ✅ 表示
    output = f"""\
========================
📦 判定結果
========================
{result}

🧾 CASE NO
{case1} / {case2}

------------------------

🔵 SHIPPING LABEL
{text1}

------------------------

🟢 CASE MARK LABEL
{text2}
"""

    return output, 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/")
def home():
    return "Server is running ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
