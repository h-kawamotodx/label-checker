from flask import Flask, request, jsonify
import re

app = Flask(__name__)

shipping_case = None

@app.route("/shipping", methods=["POST"])
def shipping():
    global shipping_case
    text = request.json.get("text", "")

    nums = re.findall(r"\d{3}", text)
    shipping_case = nums[0] if nums else None

    return jsonify({"shipping": shipping_case})


@app.route("/case", methods=["POST"])
def case():
    global shipping_case
    text = request.json.get("text", "")

    match = re.search(r"(\d{3})$", text)
    case_no = match.group(1) if match else None

    if shipping_case and case_no:
        if shipping_case == case_no:
            result = "✅ OK"
        else:
            result = "❌ NG"
    else:
        result = "⚠️ 読み取り失敗"

    return jsonify({
        "shipping": shipping_case,
        "case": case_no,
        "result": result
    })


@app.route("/")
def home():
    return "Server is running"
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
