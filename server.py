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


# ✅ ラベル種類判定
def detect_label_type(text):
    text = normalize_text(text)

    if "SHIPPING" in text:
        return "SHIPPING"

    if "CASE MARK" in text:
        return "CASE"

    return "UNKNOWN"


# ✅ SHIPPING用（CASE-NOの下の3桁）
def extract_shipping_code(text):
    text = normalize_text(text)

    # CASE-NO の近くから3桁取得
    match = re.search(r"CASE[- ]?NO\.?\s*(\d{3})", text)
    if match:
        return match.group(1)

    return None


# ✅ CASE用（バーコード末尾3桁）
def extract_case_code(text):
    text = normalize_text(text)

    match = re.search(r"\d{3}$", text)
    if match:
        return match.group()

    return None


@app.route("/check", methods=["POST"])
def check():
    data = request.json

    text1 = normalize_text(data.get("text1", ""))
    text2 = normalize_text(data.get("text2", ""))

    type1 = detect_label_type(text1)
    type2 = detect_label_type(text2)

    # ✅ ラベル判定できない
    if type1 == "UNKNOWN" or type2 == "UNKNOWN":
        return jsonify({"result": "⚠️ ラベル識別できません"})

    # ✅ 同じ種類（同ラベル対策）
    if type1 == type2:
        return jsonify({
            "result": f"⚠️ 同じ{type1}ラベルを読み取っています"
        })

    # ✅ 種類ごとに正しい方法で抽出
    if type1 == "SHIPPING":
        ship_code = extract_shipping_code(text1)
        case_code = extract_case_code(text2)
    else:
        ship_code = extract_shipping_code(text2)
        case_code = extract_case_code(text1)

    # ✅ 抽出失敗
    if not ship_code or not case_code:
        return jsonify({"result": "⚠️ 読み取り失敗"})

    # ✅ 判定
    if ship_code == case_code:
        return jsonify({"result": "✅ OK"})
    else:
        return jsonify({"result": "❌ NG"})


@app.route("/")
def home():
    return "Server is running ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
