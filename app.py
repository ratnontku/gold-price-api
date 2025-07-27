from flask import Flask, jsonify
import requests
from lxml import html

app = Flask(__name__)

@app.route("/gold-price")
def get_gold_price():
    try:
        url = "https://www.goldtraders.or.th/"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers)
        tree = html.fromstring(response.content)

        xpath = '/html/body/form/div/div/div[2]/div[2]/div[1]/table/tbody/tr/td[1]/div[1]/table/tbody/tr[1]/td[2]/div[1]/div/table/tbody/tr[4]/td[3]/span/b/font'
        result = tree.xpath(xpath)

        if result and result[0].text:
            raw_price = result[0].text.strip().replace(",", "")
            return jsonify({"goldPrice": float(raw_price)})

        return jsonify({"error": "Gold base price not found +++"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
