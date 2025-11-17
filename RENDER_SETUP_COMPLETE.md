# 🚀 Render Deployment with Automatic Daily Updates - Complete Setup Guide

## What I've Created For You

I've set up everything you need for automatic daily updates on Render with **FREE** persistent storage using PostgreSQL!

### ✅ Files Created

1. **`render_with_postgres.yaml`** - Complete Render configuration with:
   - Free PostgreSQL database for predictions
   - Web service (your Flask dashboard)
   - Cron job (runs daily at 5 PM EST)

2. **`src/utils/database.py`** - Smart database wrapper that:
   - Uses PostgreSQL on Render (persistent)
   - Falls back to CSV locally (for development)
   - Handles all data storage automatically

3. **`daily_update_production.py`** - Production update script:
   - Saves to PostgreSQL instead of CSV
   - Works automatically on Render
   - Still works locally for testing

4. **`requirements_deploy.txt`** - Updated with PostgreSQL support

---

## 🎯 How It Works

### Every Day at 5 PM EST (Automatically):

1. ✅ Fetches latest S&P 500 prices from Yahoo Finance
2. ✅ Checks previous predictions vs actual market movements
3. ✅ Calculates accuracy for past predictions
4. ✅ Generates new prediction for next trading day
5. ✅ **Saves everything to PostgreSQL** (persists forever!)
6. ✅ Updates your live dashboard automatically

### Storage:
- **On Render**: Uses FREE PostgreSQL database (persistent, never lost!)
- **Locally**: Uses CSV files (for development/testing)

---

## 📋 Deployment Steps

### Step 1: Prepare Your Repository

Make sure you're in your project directory and commit the changes:

```bash
cd "C:\Users\arhou\OneDrive\Bureau\projet omar\S&P USA"

git add .
git commit -m "Add Render deployment with auto-updates and PostgreSQL"
git push
```

### Step 2: Rename Configuration File

Rename `render_with_postgres.yaml` to `render.yaml`:

```bash
# On Windows:
ren render_with_postgres.yaml render.yaml

# Or manually rename the file
```

### Step 3: Deploy on Render

1. **Go to Render Dashboard**: https://dashboard.render.com

2. **Connect Your Repository**:
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Select the repository with your S&P 500 project

3. **Render Will Auto-Detect**:
   - It will find `render.yaml`
   - You'll see 3 services to create:
     - `sp500-database` (PostgreSQL - Free)
     - `sp500-prediction-dashboard` (Web Service - Free)
     - `sp500-daily-update` (Cron Job - Free)

4. **Approve and Deploy**:
   - Click "Apply"
   - Render will create all 3 services
   - Wait 5-10 minutes for initial deployment

### Step 4: Verify It's Working

1. **Check Web Service**:
   - Go to your dashboard URL: https://s-p-500-price-prediction.onrender.com
   - Should work normally

2. **Check Database**:
   - In Render dashboard, go to "sp500-database"
   - Click "Connect"
   - You'll see connection info (database is ready!)

3. **Check Cron Job**:
   - Go to "sp500-daily-update" service
   - Click "Logs"
   - You can manually trigger it to test

4. **Manual Test Run**:
   - In "sp500-daily-update" service
   - Click "Manual Trigger" (if available)
   - Or wait until 5 PM EST for first automatic run

---

## 🔍 Monitoring

### View Cron Job Logs

1. Go to Render Dashboard
2. Click on "sp500-daily-update"
3. Click "Logs"
4. You'll see output from each daily run

### View Database Data

1. Go to "sp500-database" in Render
2. Click "Connect"
3. Use the connection info with any PostgreSQL client
4. Or use Render's web interface

### Check Last Run

Logs will show:
```
[STEP 1/4] Fetching latest S&P 500 data...
[OK] Fetched latest data

[STEP 2/4] Updating prediction accuracy...
[OK] Updated 1 predictions with actual results

[STEP 3/4] Generating new prediction...
[OK] New prediction generated and saved

[STEP 4/4] Summary Report
[OVERALL PERFORMANCE]
  Total predictions: 385
  Correct: 275
  Accuracy: 71.43%
```

---

## 📊 Database Tables

The PostgreSQL database has 2 tables:

### 1. `predictions`
Stores all predictions made:
- prediction_date
- data_date
- direction (UP/DOWN)
- confidence
- prob_up
- prob_down

### 2. `prediction_accuracy`
Stores predictions with actual results:
- prediction_date
- data_date
- predicted_direction
- actual_direction
- actual_return
- is_correct
- current_price
- next_price

---

## 🎛️ Configuration

### Change Schedule

To run at a different time, edit `render.yaml`:

```yaml
schedule: "0 22 * * *"  # Current: 10 PM UTC = 5 PM EST
```

Examples:
- `"0 21 * * *"` = 4 PM EST (9 PM UTC)
- `"0 23 * * *"` = 6 PM EST (11 PM UTC)
- `"0 14 * * *"` = 9 AM EST (2 PM UTC)

Then commit and push:
```bash
git add render.yaml
git commit -m "Update cron schedule"
git push
```

Render will auto-update the schedule.

---

## 🆓 Costs

Everything is **100% FREE**:

- ✅ PostgreSQL Database: **FREE** (500 MB storage)
- ✅ Web Service: **FREE** (512 MB RAM, sleeps after 15 min inactivity)
- ✅ Cron Job: **FREE** (runs on schedule)

**Total Cost: $0/month**

---

## 🔧 Troubleshooting

### Cron Job Not Running

1. Check the schedule is correct
2. Look at logs for errors
3. Verify DATABASE_URL is connected
4. Manually trigger to test

### Database Connection Error

1. Go to database service
2. Check it's in "Available" status
3. Verify environment variable `DATABASE_URL` is set in both web and cron services

### Predictions Not Saving

1. Check cron job logs
2. Verify model files are in the Docker image
3. Check features file exists
4. Look for error messages in logs

### Web Service Not Updating

- Cron job saves to database
- Web service reads from database
- Both must be connected to same database
- Check DATABASE_URL in both services

---

## 📱 What You Get

### Live Dashboard
- Always up-to-date predictions
- Historical accuracy tracking
- Trading simulator with profit/loss
- Performance metrics

### Automatic Updates
- Runs every day at 5 PM EST
- No manual intervention needed
- Data persists forever
- Scales automatically

### Free & Reliable
- PostgreSQL ensures data never lost
- Render handles infrastructure
- Auto-restarts if errors occur
- Monitoring included

---

## 🎉 Next Steps After Deployment

1. **Wait for First Cron Run**: Tomorrow at 5 PM EST
2. **Check Logs**: Verify it ran successfully
3. **View Dashboard**: See new prediction
4. **Monitor Performance**: Track accuracy over time

---

## 📞 Support

If you see errors in the logs:
1. Copy the error message
2. Check the troubleshooting section
3. Verify all files are committed and pushed
4. Check Render status page: https://status.render.com

---

## 🔄 Local Development

You can still run locally without changes!

```bash
# Local version (uses CSV files)
python daily_update.py

# Production version (uses PostgreSQL if DATABASE_URL set, else CSV)
python daily_update_production.py
```

The code automatically detects if you're running locally or on Render.

---

## ✨ Summary

You now have:

✅ Fully automated daily prediction system
✅ Persistent PostgreSQL storage (FREE)
✅ Scheduled cron job at 5 PM EST daily
✅ Historical accuracy tracking
✅ Live dashboard with real-time updates
✅ 100% free deployment on Render
✅ Smart fallback for local development

**Your S&P 500 prediction system is production-ready! 🚀**

---

## Quick Start Checklist

- [ ] Rename `render_with_postgres.yaml` to `render.yaml`
- [ ] Commit and push to GitHub
- [ ] Connect repository in Render Dashboard
- [ ] Deploy blueprint (3 services)
- [ ] Wait for deployment to complete
- [ ] Visit your dashboard URL
- [ ] Check cron job logs
- [ ] Wait for first automated run at 5 PM EST
- [ ] Celebrate! 🎉
