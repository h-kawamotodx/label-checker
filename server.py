from flask import Flask, request, jsonify
import re
import os

app = Flask(__name__)

@app.route("/check", methods=["POST"])
def check():
    data = request.json

    text1 = data.get("text1", "")
    text2 = data.get("text2", "")

    # 3桁抽出
    nums1 = re.findall(r"\d{3}", text1)
    nums2 = re.findall(r"\d{3}", text2)

    code1 = nums1[-1] if nums1 else None
    code2 = nums2[-1] if nums2 else None

    if not code1 or not code2:
        return jsonify({"result": "⚠️ 読み取り失敗"})

    if code1 == code2:
        result = "✅ OK"
    else:
        result = "❌ NG"

    return jsonify({
        "shipping": code1,
        "case": code2,
        "result": result
    })

@app.route("/")
def home():
    return "Server is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
