from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/gold-price")
def get_gold_price():
    try:
        url = "https://www.goldtraders.or.th/DailyPrices.aspx"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        # Look for the row that contains "ทองรูปพรรณ 96.5%"
        rows = soup.find_all("tr")
        for row in rows:
            if "ทองรูปพรรณ 96.5%" in row.get_text():
                columns = row.find_all("td")
                if len(columns) >= 5:
                    raw_price = columns[4].get_text().strip().replace(",", "")
                    if raw_price.lower() != "n/a" and raw_price:
                        return jsonify({"goldPrice": float(raw_price)})
                    else:
                        return jsonify({"error": f"Invalid price: {raw_price}"}), 500

        return jsonify({"error": "Gold base price row not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
