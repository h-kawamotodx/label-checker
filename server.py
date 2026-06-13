from flask import Flask, request, jsonify
import re
import os

app = Flask(__name__)


# ✅ OCR補正
def normalize_text(text):
    text = text.upper()
    text = text.replace("O", "0")
    text = text.replace("I", "1")
    text = text.replace("S", "5")
    return text


# ✅ 3桁抽出（どこでもOK・最後を採用）
def extract_code(text):
    text = normalize_text(text)

    nums = re.findall(r"\d{3}", text)
    if nums:
        return nums[-1]

    return None


@app.route("/check", methods=["POST"])
def check():
    data = request.json

    text1 = normalize_text(data.get("text1", ""))
    text2 = normalize_text(data.get("text2", ""))

    code1 = extract_code(text1)
    code2 = extract_code(text2)

    # ✅ 読み取り失敗
    if not code1 or not code2:
        return jsonify({
            "result": "⚠️ 読み取り失敗"
        })

    # ✅ 判定（シンプル）
    if code1 == code2:
        return jsonify({
            "result": "✅ OK"
        })
    else:
        return jsonify({
            "result": "❌ NG"
        })


@app.route("/")
def home():
    return "Server is running ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
