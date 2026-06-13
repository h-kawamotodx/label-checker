from flask import Flask, request, jsonify
import re
import os

app = Flask(__name__)

# ✅ OCR誤認識補正
def normalize_text(text):
    text = text.upper()
    text = text.replace("O", "0")
    text = text.replace("B", "8")
    text = text.replace("I", "1")
    text = text.replace("S", "5")
    return text


# ✅ 3桁コード抽出（最後を優先）
def extract_code(text):
    text = normalize_text(text)

    nums = re.findall(r"\d{3}", text)
    if nums:
        return nums[-1]

    return None


# ✅ ラベル種類判定（安定版）
def detect_type(text):
    text = normalize_text(text)

    # 🔥 Shipping判定（重要：柔軟に対応）
    # CASE と NO が両方含まれていればOK
    if "CASE" in text and "NO" in text:
        return "SHIPPING"

    # ✅ Caseラベル（末尾3桁）
    if re.search(r"\d{3}$", text):
        return "CASE"

    return "UNKNOWN"


@app.route("/check", methods=["POST"])
def check():
    data = request.json

    text1 = data.get("text1", "")
    text2 = data.get("text2", "")

    # ✅ 種類判定（順不同OK）
    type1 = detect_type(text1)
    type2 = detect_type(text2)

    # ✅ コード抽出
    code1 = extract_code(text1)
    code2 = extract_code(text2)

    # 🔴 同じ種類チェック（これがメイン）
    if type1 == type2:
        return jsonify({
            "result": "⚠️ 同じ種類のラベルです",
            "type1": type1,
            "type2": type2
        })

    # 🔴 OCR失敗チェック
    if not code1 or not code2:
        return jsonify({
            "result": "⚠️ 読み取り失敗",
            "type1": type1,
            "type2": type2
        })

    # ✅ 最終判定
    if code1 == code2:
        result = "✅ OK"
    else:
        result = "❌ NG"

    return jsonify({
        "raw_text1": text1,
        "raw_text2": text2,
        "type1": type1,
        "type2": type2,
        "code1": code1,
        "code2": code2,
        "result": result
    })


@app.route("/")
def home():
    return "Server is running"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
