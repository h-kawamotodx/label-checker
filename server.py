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


# ✅ ラベル種類判定（見出しは使わない）
def detect_type(text):
    text = normalize_text(text)

    # KMXがあればCASE
    if "KMX" in text:
        return "CASE"

    # CASE-NOがあればSHIPPING
    if "CASE" in text and "NO" in text:
        return "SHIPPING"

    return "UNKNOWN"


# ✅ SHIPPING：CASE-NOの下3桁
def extract_shipping(text):
    text = normalize_text(text)

    # CASE-NO周辺の3桁
    match = re.search(r"CASE.*?NO.*?(\d{3})", text)
    if match:
        return match.group(1)

    return None


# ✅ CASE：KMX行の末尾3桁
def extract_case(text):
    text = normalize_text(text)

    # KMXの行の末尾3桁
    match = re.search(r"KMX[^\n]*?(\d{3})", text)
    if match:
        return match.group(1)

    return None


@app.route("/check", methods=["POST"])
def check():
    data = request.json

    text1 = normalize_text(data.get("text1", ""))
    text2 = normalize_text(data.get("text2", ""))

    type1 = detect_type(text1)
    type2 = detect_type(text2)

    # ✅ 種類判定できない
    if type1 == "UNKNOWN" or type2 == "UNKNOWN":
        return jsonify({"result": "⚠️ ラベル識別失敗"})

    # ✅ 同じ種類（同ラベル対策）
    if type1 == type2:
        return jsonify({
            "result": f"⚠️ 同じ{type1}ラベルの可能性"
        })

    # ✅ 正しく抽出
    if type1 == "SHIPPING":
        ship = extract_shipping(text1)
        case = extract_case(text2)
    else:
        ship = extract_shipping(text2)
        case = extract_case(text1)

    # ✅ 抽出失敗
    if not ship or not case:
        return jsonify({"result": "⚠️ 読み取り失敗"})

    # ✅ 判定
    if ship == case:
        return jsonify({"result": "✅ OK"})
    else:
        return jsonify({"result": "❌ NG"})


@app.route("/")
def home():
    return "Server is running ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
