from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/gold-price")
def get_gold_price():
    try:
        url = "https://www.goldtraders.or.th/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Look for the table containing gold prices
        tables = soup.find_all("table")
        
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                # Check if this row contains "ฐานภาษี" (base tax/base price)
                for i, cell in enumerate(cells):
                    if "ฐานภาษี" in cell.get_text():
                        # The price should be in the last cell of this row
                        if len(cells) > i:
                            price_cell = cells[-1]  # Get the last cell
                            raw_price = price_cell.get_text().strip()
                            # Clean the price: remove commas and any other non-numeric characters except decimal point
                            clean_price = ''.join(c for c in raw_price if c.isdigit() or c == '.')
                            if clean_price:
                                return jsonify({
                                    "goldPrice": float(clean_price),
                                    "rawPrice": raw_price,
                                    "currency": "THB"
                                })
        
        # Alternative approach: look for specific patterns or classes
        # Sometimes the price might be in a span or div with specific styling
        price_elements = soup.find_all(text=lambda text: text and "50," in text and "." in text)
        for element in price_elements:
            parent = element.parent
            if parent and ("ฐานภาษี" in str(parent.parent) or "base" in str(parent.get('class', [])).lower()):
                clean_price = ''.join(c for c in element.strip() if c.isdigit() or c == '.')
                if clean_price:
                    return jsonify({
                        "goldPrice": float(clean_price),
                        "rawPrice": element.strip(),
                        "currency": "THB"
                    })
        
        return jsonify({"error": "Gold base price not found"}), 404
        
    except requests.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Parsing failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
