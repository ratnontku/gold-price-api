from flask import Flask, jsonify
from flask_cors import CORS
import requests
from lxml import html

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
        goldBar_buy_price_xpath = '//*[@id="DetailPlace_uc_goldprices1_lblOMBuy"]/b/font'
        goldJew_buy_price_xpath = '//*[@id="DetailPlace_uc_goldprices1_lblBLBuy"]/b/font'
        goldJew_sell_price_xpath = '//*[@id="DetailPlace_uc_goldprices1_lblBLSell"]/b/font'

        goldBar_buy_price = tree.xpath(goldBar_buy_price_xpath)
        print(goldBar_buy_price[0].text_content().strip() if goldBar_buy_price else "No gold bar buy price found")
		
        goldJew_buy_price = tree.xpath(goldJew_buy_price_xpath)
        print(goldJew_buy_price[0].text_content().strip() if goldJew_buy_price else "No gold jew buy price found")
		
        goldJew_sell_price = tree.xpath(goldJew_sell_price_xpath)
        print(goldJew_sell_price[0].text_content().strip() if goldJew_sell_price else "No gold jew sell price found")

        return jsonify({
            "goldBarBuyPrice": float(goldBar_buy_price[0].text_content().strip().replace(",", "")),
            "goldJewBuyPrice": float(goldJew_buy_price[0].text_content().strip().replace(",", "")),
            "goldJewSellPrice": float(goldJew_sell_price[0].text_content().strip().replace(",", ""))
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
