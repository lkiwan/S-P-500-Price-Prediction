# Render Deployment Guide - Automatic Daily Updates

## ⚠️ Important: Data Persistence Issue

**Problem**: Render's free tier has **ephemeral storage** - any files written (CSV files) are deleted when the container restarts.

**Impact**:
- `predictions_history.csv` will be lost on restart
- `predictions_with_accuracy.csv` will be lost on restart
- Your prediction history won't persist

## Solutions

### Option 1: Use Render PostgreSQL (Recommended - Free)

Add a free PostgreSQL database to store predictions instead of CSV files.

**Steps:**

1. **Add PostgreSQL to render.yaml**:
   - Free PostgreSQL database available on Render
   - Persistent storage included

2. **Modify app to use database**:
   - Store predictions in PostgreSQL instead of CSV
   - I can help you convert the CSV logic to database logic

### Option 2: Use Render Disk (Paid - $7/month)

Add persistent disk storage to your service.

**Pros**:
- No code changes needed
- CSV files persist

**Cons**:
- Costs $7/month for 1GB disk

### Option 3: External Storage (Free with limits)

Use external services:
- **Supabase** (free PostgreSQL)
- **PlanetScale** (free MySQL)
- **AWS S3** (free tier for storage)

## Current Setup (render.yaml)

I've created a `render.yaml` with:

1. **Web Service**: Your Flask dashboard
2. **Cron Job**: Runs `daily_update.py` at 5 PM EST daily

**Schedule**: `0 22 * * *` (10 PM UTC = 5 PM EST)

## How to Deploy with Automatic Updates

### Step 1: Choose Data Persistence Method

Pick one of the options above. **I recommend Option 1 (PostgreSQL)** because it's free and reliable.

### Step 2: Update render.yaml (if using PostgreSQL)

If you choose PostgreSQL, I'll update the configuration.

### Step 3: Push to GitHub and Deploy

```bash
git add render.yaml
git commit -m "Add Render deployment config with daily cron job"
git push
```

### Step 4: Configure in Render Dashboard

1. Go to https://dashboard.render.com
2. Your service should auto-detect `render.yaml`
3. Approve the configuration
4. Both services will deploy:
   - Web service (your dashboard)
   - Cron job (daily updates)

## What the Cron Job Does

Every day at 5 PM EST (after market close), it automatically:

1. ✅ Fetches latest S&P 500 prices from Yahoo Finance
2. ✅ Updates accuracy for previous predictions
3. ✅ Generates new prediction for next day
4. ✅ Saves everything to CSV (or database if configured)

## Monitoring

### View Cron Job Logs

In Render Dashboard:
1. Go to "sp500-daily-update" service
2. Click "Logs"
3. See output from each daily run

### Manual Trigger

You can manually trigger the cron job in Render dashboard for testing.

## Current Limitation (Without Database)

⚠️ **If you deploy without database/persistent storage:**
- Cron job will run successfully
- But data will be lost on container restart
- Predictions won't accumulate over time

## Next Steps

**Tell me which option you prefer:**

1. **PostgreSQL** (I'll update the code to use database) - FREE
2. **Render Disk** (no code changes, but $7/month) - PAID
3. **Keep CSV** (data lost on restart, but free) - LIMITED

I recommend Option 1 (PostgreSQL) for a production system.
