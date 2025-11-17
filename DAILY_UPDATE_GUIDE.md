# S&P 500 Daily Update System - User Guide

## Overview

This system now automatically updates predictions and tracks accuracy daily. The simulator has also been improved to show clear profit/loss tracking based on prediction accuracy.

---

## What's New

### 1. Automated Daily Updates
- Fetches latest S&P 500 prices
- Generates new predictions automatically
- Updates accuracy for previous predictions
- Tracks everything in history files

### 2. Improved Trading Simulator
The simulator now shows:
- **Correct Wins**: Predicted UP correctly and made money
- **Correct Saves**: Predicted DOWN correctly and avoided losses
- **Wrong Losses**: Predicted UP but market went DOWN (lost money)
- **Wrong Misses**: Predicted DOWN but market went UP (missed opportunity)
- Clear profit/loss on each trade
- Prediction accuracy percentage

---

## Setup Instructions

### Option 1: Automatic Setup (Recommended)

1. **Open PowerShell as Administrator**
   - Press `Win + X`
   - Select "Windows PowerShell (Admin)"

2. **Navigate to project directory**
   ```powershell
   cd "C:\Users\arhou\OneDrive\Bureau\projet omar\S&P USA"
   ```

3. **Run the setup script**
   ```powershell
   .\setup_daily_task.ps1
   ```

4. **Done!**
   - The task will run daily at 5:00 PM (after market close)
   - You can test it immediately when prompted

### Option 2: Manual Run

If you don't want to schedule it, you can run manually:

```batch
DAILY_AUTO_UPDATE.bat
```

Or directly:
```bash
python daily_update.py
```

---

## How It Works

### Daily Update Process

1. **Fetch Latest Prices** (5d data from Yahoo Finance)
   - Updates `data/raw/price_data.csv`

2. **Update Previous Predictions**
   - Checks predictions from `predictions_history.csv`
   - Compares with actual market movements
   - Saves results to `predictions_with_accuracy.csv`

3. **Generate New Prediction**
   - Uses latest model to predict next day
   - Saves to `predictions_history.csv`
   - Won't duplicate if already predicted today

4. **Summary Report**
   - Shows overall accuracy
   - Recent performance (last 30 days)
   - Latest prediction details

### Trading Simulator Logic

The simulator operates with these rules:

**When Predicting UP (BUY):**
- Invests 50% of capital
- If market goes UP: Makes profit ✓ (Correct Win)
- If market goes DOWN: Loses money ✗ (Wrong Loss)

**When Predicting DOWN (HOLD):**
- Keeps capital safe
- If market goes DOWN: Avoided loss ✓ (Correct Save)
- If market goes UP: Missed opportunity ✗ (Wrong Miss)

**Results:**
- Capital changes based on actual returns
- Win/Loss clearly tracked
- Compared against buy-and-hold strategy

---

## Files Created

### New Files
- `daily_update.py` - Main automated update script
- `DAILY_AUTO_UPDATE.bat` - Batch file to run updates
- `setup_daily_task.ps1` - PowerShell script to setup scheduled task
- `daily_update.log` - Log file (created after first run)

### Updated Files
- `app.py` - Enhanced trading simulator with better tracking

### Data Files
- `predictions_history.csv` - All predictions made
- `predictions_with_accuracy.csv` - Predictions with actual results
- `data/raw/price_data.csv` - S&P 500 price data

---

## Managing the Scheduled Task

### View Task Status
```powershell
Get-ScheduledTask -TaskName "SP500_Daily_Update"
```

### Run Task Manually
```powershell
Start-ScheduledTask -TaskName "SP500_Daily_Update"
```

### View Task History
```powershell
Get-ScheduledTaskInfo -TaskName "SP500_Daily_Update"
```

### Remove Task
```powershell
Unregister-ScheduledTask -TaskName "SP500_Daily_Update" -Confirm:$false
```

### Open Task Scheduler GUI
```
Win + R → taskschd.msc → Enter
```
Look for "SP500_Daily_Update" in Task Scheduler Library

---

## Monitoring

### Check Logs
```bash
type daily_update.log
```

Or open in text editor:
```bash
notepad daily_update.log
```

### View Latest Results
The web dashboard automatically shows:
- Latest predictions
- Updated accuracy statistics
- Enhanced trading simulation with win/loss breakdown

---

## Schedule

The default schedule is:
- **Time**: 5:00 PM daily (17:00)
- **Reason**: After US market close (4:00 PM EST)
- **Frequency**: Every day

To change the time, edit `setup_daily_task.ps1`:
```powershell
$TriggerTime = "17:00"  # Change this to desired time
```
Then re-run the setup script.

---

## Troubleshooting

### Task Not Running
1. Check Task Scheduler for errors
2. Ensure computer is awake at scheduled time
3. Check `daily_update.log` for errors

### No Predictions Saving
1. Ensure model file exists: `models/sp500_complete_20251113.pkl`
2. Check features file exists: `data/features/features_complete.csv`
3. Run manually to see errors: `python daily_update.py`

### Accuracy Not Updating
- Accuracy updates require next day's price data
- Predictions made today won't have accuracy until tomorrow
- This is normal and expected

### Network Errors
- Ensure internet connection for Yahoo Finance
- Script will retry on next scheduled run
- Check firewall/antivirus settings

---

## Dashboard Features

### Prediction History Page
- Monthly aggregated predictions
- Confidence trends
- UP vs DOWN prediction distribution

### Trading Simulator
- Initial capital: $10,000
- Position size: 50% per trade
- Shows detailed win/loss breakdown
- Compares to buy-and-hold strategy

### Performance Metrics
- **Prediction Accuracy**: % of correct predictions
- **Correct Wins**: Profitable trades from correct UP predictions
- **Correct Saves**: Avoided losses from correct DOWN predictions
- **Wrong Losses**: Lost money from incorrect UP predictions
- **Wrong Misses**: Missed gains from incorrect DOWN predictions

---

## Best Practices

1. **Run Initial Update**
   - Before scheduling, run once manually to ensure it works
   - Check for any errors

2. **Monitor First Week**
   - Check logs daily for first week
   - Ensure predictions are being saved
   - Verify accuracy updates are working

3. **Keep Computer On**
   - For scheduled task to run, computer must be on
   - Or configure to run at startup if missed

4. **Regular Maintenance**
   - Check logs weekly
   - Monitor accuracy trends
   - Update model when needed

5. **Backup Data**
   - Periodically backup CSV files
   - Keep prediction history safe

---

## Support

If you encounter issues:
1. Check `daily_update.log` for error messages
2. Run manually: `python daily_update.py`
3. Verify all dependencies are installed
4. Check model and data files exist

For model updates or feature requests, modify the scripts as needed.

---

## Summary

You now have:
✅ Automated daily price updates
✅ Automatic prediction generation
✅ Accuracy tracking over time
✅ Enhanced trading simulator
✅ Clear win/loss breakdown
✅ Scheduled task running daily
✅ Logging for monitoring

Your S&P 500 prediction system is now fully automated!
