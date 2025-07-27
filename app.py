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
         # XPath for date and gold price table rows
        gold_price_xpath = '//*[@id="DetailPlace_uc_goldprices1_lblOMBuy"]/b/font'

        gold_price = tree.xpath(gold_price_xpath)
        print(buy_x[0].text_content().strip() if buy_x else "No buy price found")

        return jsonify({"goldPrice": float(gold_price)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

