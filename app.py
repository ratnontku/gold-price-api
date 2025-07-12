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

        # Match only the keyword "ฐานภาษี"
        rows = soup.find_all("tr")
        for row in rows:
            if "ฐานภาษี" in row.get_text():
                columns = row.find_all("td")
                if columns:
                    raw_price = columns[-1].get_text().strip().replace(",", "")
                    if raw_price:
                        return jsonify({"goldPrice": float(raw_price)})

        return jsonify({"error": "Gold base price not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500