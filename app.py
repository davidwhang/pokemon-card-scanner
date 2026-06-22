from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import anthropic
import base64
import json
import os
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from apify_client import ApifyClient
from ddgs import DDGS

app = Flask(__name__)
CORS(app)

# In-memory card storage (persists during app runtime)
cards_storage = []

def get_client():
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    return anthropic.Anthropic(api_key=api_key)

def analyze_card_image(image_base64):
    """Use Claude to analyze card image and extract details"""
    try:
        client = get_client()
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": """Analyze this Pokemon trading card image and extract the following information in JSON format:
{
    "card_name": "the pokemon name",
    "card_number": "the card number if visible (e.g., 123/102), or null if not visible",
    "set_name": "the set this card is from (e.g., Base Set, EX Era, Vivid Voltage, etc.)",
    "variant": "any special variant like Holo, Shadowless, ex, VMAX, Full Art, etc.",
    "psa_grade": "the PSA grade if visible (1-10), or null if not graded",
    "price_jpy": "the price in Japanese Yen if visible, or null if not visible",
    "confidence": "high/medium/low - how confident you are in the extraction"
}

Be precise and only include information you can clearly see. For price_jpy, only include if you can clearly read the price on the card."""
                        }
                    ],
                }
            ],
        )

        response_text = message.content[0].text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            card_data = json.loads(json_match.group())
            return card_data
        return None
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return None

def get_pricecharting_price(card_name, set_name, psa_grade, variant=None):
    """Search DuckDuckGo for card on PriceCharting, then scrape the page. Returns (price, url) tuple."""
    try:
        # Build search query with card name, set, and variant for specificity
        search_parts = [card_name, set_name]
        if variant:
            search_parts.append(variant)
        search_parts.append("pricecharting")
        search_query = " ".join(search_parts)
        print(f"Searching DuckDuckGo for: {search_query}")

        ddgs = DDGS()
        results = ddgs.text(search_query, max_results=10)

        pricecharting_url = None
        for result in results:
            url = result.get("link") or result.get("href") or result.get("url")
            if url and "pricecharting.com" in url and "pokemon" in url.lower():
                # Prefer links that look like specific card pages (have /product/ or long paths)
                if "/product/" in url or url.count("/") > 4:
                    pricecharting_url = url
                    print(f"  Found PriceCharting card link: {pricecharting_url}")
                    break
                elif not pricecharting_url:
                    # Keep as fallback if no better link found
                    pricecharting_url = url

        if not pricecharting_url:
            print("  No PriceCharting link found")
            return None

        print(f"  Using PriceCharting link: {pricecharting_url}")

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(pricecharting_url, headers=headers, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        page_text = soup.get_text()

        if psa_grade:
            # Look for PSA grade and nearby prices more carefully
            grade_patterns = [
                f"PSA\\s*{psa_grade}[^$]*\\$(\\d{{1,4}}(?:,\\d{{3}})*(?:\\.\\d{{2}})?)",  # PSA X $price
                f"PSA\\s{psa_grade}[^$]*\\$(\\d{{1,4}}(?:,\\d{{3}})*(?:\\.\\d{{2}})?)",   # PSA X $price (less space)
                f"{psa_grade}\\/10[^$]*\\$(\\d{{1,4}}(?:,\\d{{3}})*(?:\\.\\d{{2}})?)",    # X/10 format
            ]
            for pattern in grade_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                if matches:
                    for price_str in matches:
                        try:
                            price = float(price_str.replace(',', ''))
                            if 5 < price < 5000:
                                print(f"  ✓ Found PSA {psa_grade} price: ${price}")
                                return (price, pricecharting_url)
                        except ValueError:
                            pass

        prices = re.findall(r'\$([\\d,]+\\.?\\d+)', page_text)
        if prices:
            valid_prices = []
            for price_str in prices:
                try:
                    price = float(price_str.replace(',', ''))
                    if 5 < price < 5000:
                        valid_prices.append(price)
                except ValueError:
                    pass
            if valid_prices:
                highest_price = max(valid_prices)
                print(f"  ✓ Found price (highest): ${highest_price}")
                return (highest_price, pricecharting_url)

        return None

    except Exception as e:
        print(f"PriceCharting lookup error: {type(e).__name__}: {e}")
        return None

def get_ebay_price(card_name, set_name, psa_grade):
    """Get eBay price estimate"""
    try:
        search_query = f"Pokemon {card_name} {set_name} PSA {psa_grade}"
        url = f"https://www.ebay.com/sch/i.html?_nkw={quote(search_query)}&_sacat=213&rt=nc&LH_Sold=1"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=3)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        prices = []
        for price_elem in soup.find_all('span', class_='BOLD'):
            price_text = price_elem.get_text(strip=True)
            price_match = re.search(r'\$(\d+\.?\d*)', price_text)
            if price_match:
                prices.append(float(price_match.group(1)))
        if prices:
            return sum(prices) / len(prices)
    except Exception as e:
        print(f"eBay lookup skipped: {e}")
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Pokemon Card Scanner is running!'}), 200

@app.route('/api/analyze-card', methods=['POST'])
def analyze_card():
    """Analyze card image using Claude vision"""
    try:
        data = request.get_json()
        image_base64 = data.get('image')
        manual_price = data.get('manual_price_jpy')

        card_data = analyze_card_image(image_base64)

        if not card_data:
            return jsonify({'error': 'Failed to analyze image'}), 400

        if manual_price:
            card_data['price_jpy'] = float(manual_price)

        if card_data.get('price_jpy'):
            card_data['price_usd'] = round(card_data['price_jpy'] / 150, 2)
            card_data['discount_price'] = round(card_data['price_usd'] * 0.9, 2)

        if card_data.get('psa_grade') and card_data.get('card_name'):
            # Get PriceCharting price and URL
            pricecharting_result = get_pricecharting_price(
                card_data['card_name'],
                card_data.get('set_name', ''),
                card_data['psa_grade'],
                card_data.get('variant', '')
            )
            if isinstance(pricecharting_result, tuple):
                card_data['pricecharting_price'], card_data['pricecharting_url'] = pricecharting_result
            else:
                card_data['pricecharting_price'] = pricecharting_result

            ebay = get_ebay_price(
                card_data['card_name'],
                card_data.get('set_name', ''),
                card_data['psa_grade']
            )
            card_data['ebay_price'] = ebay

        return jsonify(card_data)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-card', methods=['POST'])
def save_card():
    """Save card to in-memory storage"""
    try:
        data = request.get_json()
        data['id'] = len(cards_storage) + 1
        data['created_at'] = datetime.now().isoformat()
        cards_storage.append(data)
        return jsonify({'id': data['id'], 'message': 'Card saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-cards', methods=['GET'])
def get_cards():
    """Retrieve all saved cards"""
    try:
        return jsonify(cards_storage)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-csv', methods=['GET'])
def export_csv():
    """Export cards as CSV"""
    try:
        import csv
        from io import StringIO

        output = StringIO()
        if cards_storage:
            writer = csv.DictWriter(output, fieldnames=cards_storage[0].keys())
            writer.writeheader()
            writer.writerows(cards_storage)

        return output.getvalue(), 200, {
            'Content-Disposition': 'attachment; filename=pokemon_cards.csv',
            'Content-Type': 'text/csv'
        }

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
