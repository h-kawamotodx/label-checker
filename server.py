from flask import Flask, request, jsonify
import re
import os

app = Flask(__name__)


# ✅ OCR補正
def normalize_text(text):
    text = text.upper()
    text = text.replace("O", "0")
    text = text.replace("B", "8")
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


@app.route("/check", methods=["POST"])
def check():
    data = request.json

    text1 = data.get("text1", "")
    text2 = data.get("text2", "")

    code1 = extract_code(text1)
    code2 = extract_code(text2)

    # ✅ デバッグ用（確認したいとき用）
    # return jsonify({"text1": text1, "text2": text2})

    # ✅ 読み取り失敗
    if not code1 or not code2:
        return jsonify({
            "result": "⚠️ 読み取り失敗",
            "code1": code1,
            "code2": code2
        })

    # ✅ 判定
    if code1 == code2:
        result = "✅ OK"
    else:
        result = "❌ NG"

    return jsonify({
        "code1": code1,
        "code2": code2,
        "result": result
    })


@app.route("/")
def home():
    return "Server is running ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
