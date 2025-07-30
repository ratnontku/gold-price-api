from flask import Flask, jsonify
import requests
from lxml import html

app = Flask(__name__)

@app.route("/gold-price")
def get_gold_price():
    try:
        url = "https://www.goldtraders.or.th/default.aspx"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers)
        tree = html.fromstring(response.content)
         # XPath for date and gold price table rows
        gold_price_xpath = '//*[@id="DetailPlace_uc_goldprices1_lblOMBuy"]/b/font'

        gold_price = tree.xpath(gold_price_xpath)
        print(gold_price[0].text_content().strip() if gold_price else "No buy price found")

        return jsonify({"goldPrice": gold_price[0].text_content().strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
