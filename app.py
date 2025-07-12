from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re

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

        # Look for the row containing "ฐานภาษี"
        rows = soup.find_all("tr")
        for row in rows:
            if "ฐานภาษี" in row.get_text():
                columns = row.find_all("td")
                if columns:
                    # Try to find the first column that looks like a number
                    for col in reversed(columns):
                        text = col.get_text().strip().replace(",", "")
                        if re.match(r"^\d+(\.\d+)?$", text):  # matches number with or without decimals
                            gold_price = float(text)
                            return jsonify({"goldPrice": gold_price})
                    return jsonify({"error": "No numeric value found in row"}), 500

        return jsonify({"error": "Gold price row not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500