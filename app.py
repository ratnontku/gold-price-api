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
        
        # First, try to find the main gold price table (Thai domestic prices)
        # Look for the table that contains both "ทองคำแท่ง" and "ฐานภาษี"
        main_gold_table = None
        tables = soup.find_all("table")
        
        for table in tables:
            table_text = table.get_text()
            if "ทองคำแท่ง" in table_text and "ฐานภาษี" in table_text:
                main_gold_table = table
                break
        
        if main_gold_table:
            rows = main_gold_table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 3:  # Should have at least 3 columns
                    # Check if first cell contains "ฐานภาษี"
                    first_cell_text = cells[0].get_text().strip()
                    if "ฐานภาษี" in first_cell_text:
                        # The price should be in the last cell
                        price_cell = cells[-1]
                        raw_price = price_cell.get_text().strip()
                        # Clean the price: remove commas and any other non-numeric characters except decimal point
                        clean_price = ''.join(c for c in raw_price if c.isdigit() or c == '.')
                        if clean_price and float(clean_price) > 10000:  # Base price should be > 10,000
                            return jsonify({
                                "goldPrice": float(clean_price),
                                "rawPrice": raw_price,
                                "currency": "THB"
                            })
        
        # Alternative approach: look for elements with green styling or specific classes
        # The green highlighted price might have specific CSS classes
        green_elements = soup.find_all(attrs={"style": lambda x: x and "color" in x.lower() and "green" in x.lower()})
        for element in green_elements:
            text = element.get_text().strip()
            if "," in text and "." in text:
                clean_price = ''.join(c for c in text if c.isdigit() or c == '.')
                if clean_price and float(clean_price) > 10000:
                    return jsonify({
                        "goldPrice": float(clean_price),
                        "rawPrice": text,
                        "currency": "THB"
                    })
        
        # Try to find elements containing numbers around 50,000
        all_text_elements = soup.find_all(text=True)
        for text in all_text_elements:
            text = text.strip()
            if "50," in text and "." in text:
                # Check if this is likely the base price by checking surrounding context
                parent = text.parent if hasattr(text, 'parent') else None
                if parent:
                    context = str(parent.parent) if parent.parent else str(parent)
                    if "ฐานภาษี" in context or "base" in context.lower():
                        clean_price = ''.join(c for c in text if c.isdigit() or c == '.')
                        if clean_price:
                            return jsonify({
                                "goldPrice": float(clean_price),
                                "rawPrice": text,
                                "currency": "THB"
                            })
        
        return jsonify({"error": "Gold base price not found"}), 404
        
    except requests.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Parsing failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
