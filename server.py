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


# ✅ CASE判定（KMX + 構造 + 末尾3桁）
def is_case_label(text):
    text = normalize_text(text)

    # ✅ KMX行で最後に3桁がある構造だけを採用
    match = re.search(r"KMX[-A-Z0-9/\.]*?(\d{3})$", text)
    return bool(match)


# ✅ CASE：KMX行から末尾3桁を抽出
def extract_case_code(text):
    text = normalize_text(text)

    match = re.search(r"KMX[-A-Z0-9/\.]*?(\d{3})$", text)
    if match:
        return match.group(1)

    return None


# ✅ SHIPPING：単純な3桁（Case側除外後に使う）
def extract_shipping_code(text):
    text = normalize_text(text)

    nums = re.findall(r"\b\d{3}\b", text)
    if nums:
        return nums[0]

    return None


@app.route("/check", methods=["POST"])
def check():
    data = request.json

    text1 = normalize_text(data.get("text1", ""))
    text2 = normalize_text(data.get("text2", ""))

    # ✅ CASE判定（片方だけ採用🔥）
    case1 = is_case_label(text1)
    case2 = is_case_label(text2)

    # ✅ 両方CASE → 同じラベル
    if case1 and case2:
        return jsonify({
            "result": "⚠️ 同じCASEラベルの可能性"
        })

    # ✅ CASEがどちらにも無い → エラー
    if not case1 and not case2:
        return jsonify({
            "result": "⚠️ CASEラベルを認識できません"
        })

    # ✅ CASEとSHIPPINGを分ける
    if case1:
        case_text = text1
        ship_text = text2
    else:
        case_text = text2
        ship_text = text1

    # ✅ 抽出
    case_code = extract_case_code(case_text)
    ship_code = extract_shipping_code(ship_text)

    # ✅ 読み取り失敗
    if not case_code or not ship_code:
        return jsonify({
            "result": "⚠️ 読み取り失敗"
        })

    # ✅ 判定
    if case_code == ship_code:
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
