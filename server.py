from flask import Flask, request
import re
import os

app = Flask(__name__)


# ✅ OCR補正
def normalize_text(text):
    return str(text).upper()


# ✅ CASE NO抽出（両対応）
def extract_case_no(text):
    patterns = [
        r"CASE[- ]?NO\.?\s*(\d+)",
        r"C/NO\.?\s*(\d+)"
    ]

    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)

    return "なし"


@app.route("/check", methods=["POST"])
def check():
    data = request.json or {}

    # ✅ 入力
    text1 = normalize_text(data.get("text1", ""))
    text2 = normalize_text(data.get("text2", ""))

    barcode1 = data.get("barcode1", "")
    barcode2 = data.get("barcode2", "")

    # ✅ バーコード：左から11桁
    barcode1_11 = barcode1[:11]
    barcode2_11 = barcode2[:11]

    # ✅ CASE NO抽出
    case1 = extract_case_no(text1)
    case2 = extract_case_no(text2)

    # ✅ 判定
    barcode_match = (barcode1_11 == barcode2_11)
    case_match = (case1 == case2)

    if barcode_match and case_match:
        final = "✅✅ 完全一致（安全）"
    elif barcode_match:
        final = "⚠️ バーコード一致（CASE要確認）"
    elif case_match:
        final = "⚠️ CASE一致（バーコード不一致）"
    else:
        final = "❌ NG（不一致）"

    # ✅ 表示
    output = f"""\
========================
📦 総合判定
========================
{final}

🏷 バーコード（11桁）
{barcode1_11} / {barcode2_11}

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
