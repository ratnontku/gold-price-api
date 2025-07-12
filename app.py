from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/gold-price")
def get_gold_price():
    url = "https://www.goldtraders.or.th/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        table = soup.find("table", {"class": "table-price"})
        target_text = "ฐานภาษีทองรูปพรรณ 96.5%"

        for row in table.find_all("tr"):
            if target_text in row.get_text():
                columns = row.find_all("td")
                if columns:
                    raw_price = columns[-1].text.strip().replace(",", "")
                    gold_price = float(raw_price)
                    return jsonify({"goldPrice": gold_price})

        return jsonify({"error": "Gold price not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
