# 🎴 Pokemon Card Scanner - Japan Edition

A web app for scanning Pokemon trading cards in Japan. Take a photo or manually enter card details to get:
- Card information (name, set, variant, PSA grade)
- JPY → USD conversion
- 10% passport discount calculation
- PriceCharting & eBay market prices
- Save & export your collection

## Setup (Local Development)

### 1. Install Python dependencies
```bash
cd pokemon_card_scanner
pip install -r requirements.txt
```

### 2. Set your Anthropic API key
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 3. Run the app
```bash
python app.py
```

Visit: **http://localhost:5000**

---

## Deployment to Production (For Your Friend in Japan)

### Option A: Deploy to Railway (Easiest)

1. **Create a Railway account** at railway.app
2. **Connect your GitHub repo** or upload the code
3. **Set environment variable:**
   - Go to Variables → Add `ANTHROPIC_API_KEY`
4. **Deploy** - Railway handles everything!

### Option B: Deploy to Heroku (Still Easy)

1. **Create a Heroku account** at heroku.com
2. Create `Procfile` in root:
   ```
   web: python app.py
   ```
3. **Deploy:**
   ```bash
   heroku login
   heroku create your-app-name
   heroku config:set ANTHROPIC_API_KEY="your-key"
   git push heroku main
   ```

### Option C: Use ngrok for Remote Access (Quickest)

If you want to share with your friend RIGHT NOW:

```bash
# Install ngrok
brew install ngrok

# Run the Flask app
python app.py

# In another terminal, expose it
ngrok http 5000

# Share the URL with your friend (e.g., https://abc123.ngrok.io)
```

---

## Features

### 📷 Camera Tab
- Point at card, capture photo
- Claude AI analyzes card automatically
- Extracts: name, set, variant, PSA grade, JPY price
- Optionally enter JPY price manually if not visible
- Shows USD price & 10% discount
- Fetches PriceCharting & eBay comparisons

### ✏️ Manual Tab
- Type card details directly
- No camera needed
- Useful for entering data later or batch input

### 📋 History Tab
- View all scanned cards
- Running totals (JPY, USD, with discount)
- Export to CSV for spreadsheet

---

## How to Use

1. **Open the app** on your phone (or computer)
2. **Go to Camera tab**
3. **Point at the card** - make sure price is visible
4. **Tap Capture** - takes photo
5. **Tap Analyze Card** - Claude reads it
6. **Review the results:**
   - Original JPY price (from photo)
   - USD conversion (÷150)
   - 10% passport discount price
   - PriceCharting & eBay market prices for comparison
7. **Tap Save Card** - stores in database
8. **Go to History tab** - see all your cards & totals

---

## Tips for Best Results

✅ **Good lighting** - Make sure card is well-lit
✅ **Clear price** - Make sure the JPY price is visible in photo
✅ **Steady hand** - Hold camera still for 1-2 seconds
✅ **Card details** - Top/bottom of card visible for set info

---

## Cost

- **Anthropic API**: ~$0.001-0.002 per card analysis
- **PriceCharting/eBay scraping**: Free
- **Hosting**: ~$5-10/month (Railway/Heroku free tier available)

For 427 cards = ~$0.50 in API costs

---

## Database

Cards are stored in `pokemon_cards.db` (SQLite) with:
- Card name, set, variant, PSA grade
- JPY price, USD price, discount price
- PriceCharting & eBay prices
- Timestamp & source (camera vs manual)

Export to CSV anytime from History tab.

---

## Troubleshooting

**"Camera access denied"**
- Grant camera permission in browser settings

**"API key error"**
- Make sure `ANTHROPIC_API_KEY` environment variable is set

**"No prices found"**
- PriceCharting/eBay scraping might timeout
- Prices are optional - app still works without them

**"Claude didn't read the card correctly"**
- Try different angle or lighting
- Or use Manual tab to enter details

---

## Next Steps

1. **Deploy the app** (Railway is easiest - 2 min setup)
2. **Share URL with your friend**
3. **Your friend scans cards in Japan**
4. **Download CSV when done**
5. **Merge with your master spreadsheet**

Enjoy! 🎴✨
