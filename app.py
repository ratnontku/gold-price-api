from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/gold-price")
def get_gold_price():
    try:
        url = "https://www.goldtraders.or.th/"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the row containing the word "ฐานภาษี"
        rows = soup.find_all("tr")
        for row in rows:
            if "ฐานภาษี" in row.get_text():
                columns = row.find_all("td")
                if columns:
                    price_text = columns[-1].get_text().replace(",", "").strip()
                    return jsonify({"goldPrice": float(price_text)})

        return jsonify({"error": "Gold price not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500