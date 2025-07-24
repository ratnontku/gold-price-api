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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Get the HTML content
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Debug: Search for all text containing numbers with commas and decimals
        # This will help us find where the price 50,316.04 is located
        price_pattern = re.compile(r'\d{1,3}(?:,\d{3})*\.\d{2}')
        all_prices = price_pattern.findall(html_content)
        
        # Look for the specific price we want (around 50,000)
        target_price = None
        for price in all_prices:
            clean_price = float(price.replace(',', ''))
            if 50000 <= clean_price <= 60000:  # Range where the base price should be
                target_price = price
                break
        
        if target_price:
            return jsonify({
                "goldPrice": float(target_price.replace(',', '')),
                "rawPrice": target_price,
                "currency": "THB",
                "debug": f"Found {len(all_prices)} prices on page"
            })
        
        # Alternative: Search in the raw HTML for the pattern around the base price
        # Look for text patterns that contain both Thai text and the price
        base_price_patterns = [
            r'ฐานภาษี[^0-9]*(\d{1,3}(?:,\d{3})*\.\d{2})',
            r'(\d{1,3}(?:,\d{3})*\.\d{2})[^0-9]*ฐานภาษี',
            r'50,\d{3}\.\d{2}'  # Specific pattern for prices starting with 50,
        ]
        
        for pattern in base_price_patterns:
            matches = re.search(pattern, html_content)
            if matches:
                if pattern == r'50,\d{3}\.\d{2}':
                    price = matches.group(0)
                else:
                    price = matches.group(1)
                return jsonify({
                    "goldPrice": float(price.replace(',', '')),
                    "rawPrice": price,
                    "currency": "THB",
                    "method": "regex"
                })
        
        # Last resort: return all prices found for debugging
        return jsonify({
            "error": "Gold base price not found",
            "debug": {
                "all_prices_found": all_prices[:10],  # First 10 prices found
                "total_prices": len(all_prices),
                "html_sample": html_content[:1000] if len(html_content) > 1000 else html_content
            }
        }), 404
        
    except requests.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Parsing failed: {str(e)}"}), 500

@app.route("/debug-page")
def debug_page():
    """Debug endpoint to see the raw HTML structure"""
    try:
        url = "https://www.goldtraders.or.th/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all elements containing "ฐานภาษี"
        base_tax_elements = soup.find_all(text=lambda text: text and "ฐานภาษี" in text)
        
        debug_info = {
            "base_tax_elements_found": len(base_tax_elements),
            "elements_content": []
        }
        
        for i, element in enumerate(base_tax_elements[:5]):  # First 5 elements
            parent = element.parent if hasattr(element, 'parent') else None
            if parent:
                debug_info["elements_content"].append({
                    "index": i,
                    "text": element.strip(),
                    "parent_tag": parent.name,
                    "parent_text": parent.get_text().strip()[:200],  # First 200 chars
                    "parent_html": str(parent)[:500]  # First 500 chars of HTML
                })
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
