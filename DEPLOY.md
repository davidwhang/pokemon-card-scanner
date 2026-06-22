# 🚀 Deployment Guide - Railway

This will be live in 5 minutes.

## Step 1: Push to GitHub

```bash
cd /Users/whang/pokemon_card_scanner

# Initialize git if not already done
git init
git add .
git commit -m "Initial Pokemon Card Scanner commit"

# Create a new repo on GitHub (https://github.com/new)
# Then push:
git remote add origin https://github.com/YOUR-USERNAME/pokemon-card-scanner.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Railway

1. **Go to** → https://railway.app
2. **Sign up** (free account)
3. **Click "Create New Project"**
4. **Choose "Deploy from GitHub repo"**
5. **Select your pokemon-card-scanner repo**
6. **Railway auto-detects Python** ✅
7. **Wait for build** (~2 min)

## Step 3: Add Environment Variable

1. **Go to Project Settings**
2. **Click "Variables"**
3. **Add new variable:**
   - Key: `ANTHROPIC_API_KEY`
   - Value: (get from https://console.anthropic.com/api-keys)
4. **Save** → Railway auto-redeploys

## Step 4: Get Your Live URL

1. **Go to "Deployments"** tab
2. **Find the ✅ successful deployment**
3. **Click the URL** at the top
4. **Your app is LIVE!** 🎉

Example: `https://pokemon-card-scanner-production.railway.app`

## Step 5: Share with Your Friend

Send them:
```
🎴 Scan cards here: https://your-url.railway.app
```

That's it! They can start scanning immediately from Japan.

---

## Troubleshooting

**"Build failed"**
- Check Railway logs - usually missing API key
- Make sure requirements.txt is in root folder

**"Cannot access camera"**
- Mobile browser needs HTTPS (Railway provides this automatically ✅)
- Desktop browser may need to allow camera permissions

**"Cards not saving"**
- Railway has a read-only file system by default
- We can add a PostgreSQL database (see below)

---

## Optional: Add Database (For Long-Term)

Railway's file system resets. To keep cards permanently:

1. **In Railway Dashboard:**
   - Click "Add Service"
   - Choose "PostgreSQL"
2. **Get connection string** from PostgreSQL service
3. **Update app.py** to use PostgreSQL instead of SQLite
4. **Redeploy**

For now, SQLite works fine - cards persist until Railway restarts (weekly).

---

## Done! 🎉

Your friend can now:
1. Visit the URL on their phone
2. Take photos of cards
3. Get instant USD prices
4. Download CSV when done

Total cost: **$0** (Railway free tier) + ~$6 in Claude API credits for 427 cards
