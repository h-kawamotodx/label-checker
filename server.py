from flask import Flask, request
import re
import os

app = Flask(__name__)


def normalize_text(text):
    text = str(text)
    text = text.upper()
    return text


def extract_code(text):
    nums = re.findall(r"\d{3}", text)
    if nums:
        return nums[-1]
    return "なし"


@app.route("/check", methods=["POST"])
def check():
    data = request.json or {}

    text1 = normalize_text(data.get("text1", ""))
    text2 = normalize_text(data.get("text2", ""))

    code1 = extract_code(text1)
    code2 = extract_code(text2)

    if code1 == "なし" or code2 == "なし":
        result = "⚠️ 読み取り失敗"
    elif code1 == code2:
        result = "✅ OK"
    else:
        result = "❌ NG"

    output = f"""\
========================
✅ 判定結果
========================
{result}

🔢 コード
------------------------
{code1} / {code2}

🔵 LABEL 1
------------------------
{text1}

🟢 LABEL 2
------------------------
{text2}
"""

    return output, 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/")
def home():
    return "Server is running ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
