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


# ✅ Case用（バーコード末尾3桁）
def extract_case_code(text):
    text = normalize_text(text)

    match = re.search(r"\d{3}$", text)
    if match:
        return match.group()

    return None


# ✅ Shipping用（CASE-NO付近の3桁）
def extract_shipping_code(text):
    text = normalize_text(text)

    # CASE-NO周辺を優先して探す
    match = re.search(r"CASE.*?(\d{3})", text)
    if match:
        return match.group(1)

    # fallback（単独3桁）
    nums = re.findall(r"\b\d{3}\b", text)
    if nums:
        return nums[0]

    return None


@app.route("/check", methods=["POST"])
def check():
    data = request.json

    text1 = data.get("text1", "")
    text2 = data.get("text2", "")

    # ✅ 両方から「Case」「Shipping」両方抽出してみる
    case1 = extract_case_code(text1)
    case2 = extract_case_code(text2)

    ship1 = extract_shipping_code(text1)
    ship2 = extract_shipping_code(text2)

    # ✅ 正しい組み合わせはこれだけ
    # Case側の数字 = Shipping側の数字

    pairs = [
        (case1, ship2),
        (case2, ship1)
    ]

    # ✅ 同じラベル防止
    if case1 and case2:
        return jsonify({
            "result": "⚠️ 同じCaseラベルの可能性"
        })

    if ship1 and ship2:
        return jsonify({
            "result": "⚠️ 同じShippingラベルの可能性"
        })

    # ✅ 判定
    for c, s in pairs:
        if c and s:
            if c == s:
                return jsonify({"result": "✅ OK"})
            else:
                return jsonify({"result": "❌ NG"})

    return jsonify({"result": "⚠️ 読み取り失敗"})


@app.route("/")
def home():
    return "Server is running ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
