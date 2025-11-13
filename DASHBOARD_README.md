# S&P 500 AI Prediction Dashboard

## Beautiful, Professional Web Dashboard for Your Prediction System

A modern, responsive web dashboard to visualize and interact with your S&P 500 prediction model. Features real-time predictions, performance metrics, interactive charts, and more!

---

## Features

### Real-Time Data
- Live market status (S&P 500 current price)
- Latest prediction with confidence levels
- One-click prediction generation

### Interactive Visualizations
- **Prediction History Chart** - Last 30 predictions with confidence levels
- **Confidence Distribution** - Pie chart showing high/medium/low confidence predictions
- **Sentiment Timeline** - News sentiment trends over time
- **Performance Metrics** - Accuracy, win rate, and more

### Professional Design
- Modern gradient UI with smooth animations
- Fully responsive (works on desktop, tablet, mobile)
- Clean, intuitive interface
- Real-time updates every 30 seconds

### Data Tables
- Recent predictions history
- Sortable and filterable tables
- Signal strength indicators

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_dashboard.txt
```

This installs:
- Flask (web framework)
- pandas (data handling)
- numpy (calculations)

### 2. Run the Dashboard

```bash
python app.py
```

You'll see:
```
======================================================================
S&P 500 PREDICTION DASHBOARD
======================================================================

Starting server...
Dashboard will be available at: http://localhost:5000

Press Ctrl+C to stop the server
======================================================================
```

### 3. Open in Browser

Navigate to: **http://localhost:5000**

That's it! Your dashboard is now running.

---

## Dashboard Features Explained

### Top Bar - Market Status
- Current S&P 500 price
- Daily change percentage
- "Get Prediction" button (click to generate new prediction)

### Latest Prediction Card
- Direction (UP/DOWN) with animated icon
- Confidence gauge (HIGH/MEDIUM/LOW)
- Up/Down probabilities
- Last updated timestamp

### Performance Metrics Card
- Model accuracy (from backtest: 63.64%)
- Edge over random guessing
- Total predictions made
- Average confidence level
- Up/Down prediction ratio

### Confidence Distribution Chart
- Pie chart showing distribution of high/medium/low confidence predictions
- Interactive hover tooltips

### Prediction History Chart
- Bar chart of last 30 predictions
- Color-coded by direction (green=UP, red=DOWN)
- Shows confidence level for each prediction

### Sentiment Timeline Chart
- Line chart of news sentiment over time
- Shows positive/negative/neutral sentiment trends

### Recent Predictions Table
- Last 10 predictions in table format
- Date, direction, confidence, probabilities
- Signal strength indicator (bars)

---

## How to Use

### Daily Workflow:

1. **Start Dashboard** (if not already running):
   ```bash
   python app.py
   ```

2. **Generate Prediction**:
   - Click "Get Prediction" button
   - Wait for processing (2-3 seconds)
   - View results in "Latest Prediction" card

3. **Review Performance**:
   - Check accuracy metrics
   - Review confidence distribution
   - Analyze sentiment trends

4. **Track History**:
   - Scroll to "Recent Predictions" table
   - See all past predictions
   - Compare predictions over time

### Tips:
- Dashboard auto-refreshes data every 30 seconds
- Leave it open on a second monitor for live tracking
- High confidence predictions (>70%) are most reliable
- Use sentiment chart to gauge market mood

---

## Embedding in Your Website

### Option 1: Run on Same Server
If your website is Python-based, integrate Flask directly.

### Option 2: Deploy Separately
Deploy dashboard to a free hosting service:

#### **Render.com (Recommended - FREE)**
1. Create account at render.com
2. Connect your GitHub repo
3. Create new "Web Service"
4. Set build command: `pip install -r requirements_dashboard.txt`
5. Set start command: `python app.py`
6. Deploy!

Your dashboard will be live at: `https://your-app.onrender.com`

#### **Vercel (FREE)**
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel` in your project folder
3. Follow prompts
4. Get live URL!

### Option 3: Embed as iFrame
Once deployed, embed in any website:

```html
<iframe
  src="https://your-dashboard-url.com"
  width="100%"
  height="800px"
  frameborder="0"
></iframe>
```

---

## API Endpoints

The dashboard provides several API endpoints you can use:

### GET `/api/latest_prediction`
Returns the most recent prediction.

**Response:**
```json
{
  "success": true,
  "prediction": {
    "date": "2025-11-13 22:01:37",
    "direction": "UP",
    "confidence": 0.5910,
    "prob_up": 0.5910,
    "prob_down": 0.4090
  }
}
```

### GET `/api/performance_metrics`
Returns model performance statistics.

### GET `/api/prediction_history`
Returns last 30 predictions for charting.

### POST `/api/run_prediction`
Triggers a new prediction.

### GET `/api/sentiment_data`
Returns sentiment timeline data.

### GET `/api/market_status`
Returns current S&P 500 price and change.

---

## Customization

### Change Colors
Edit `static/css/style.css`, lines 9-15:
```css
:root {
    --primary-color: #4f46e5;     /* Main color */
    --secondary-color: #10b981;   /* Success/Up color */
    --danger-color: #ef4444;      /* Danger/Down color */
    /* ... */
}
```

### Change Port
Edit `app.py`, last line:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change 5000 to 8080
```

### Add Your Logo
1. Place logo image in `static/images/logo.png`
2. Edit `templates/dashboard.html`, line 56:
```html
<a class="navbar-brand fw-bold" href="#">
    <img src="{{ url_for('static', filename='images/logo.png') }}" height="30">
    S&P 500 AI Prediction
</a>
```

### Modify Refresh Rate
Edit `static/js/dashboard.js`, line 23:
```javascript
setInterval(loadAllData, 60000);  // Change 30000 (30s) to 60000 (60s)
```

---

## Troubleshooting

### Dashboard won't start
**Error:** `ModuleNotFoundError: No module named 'flask'`
**Solution:** Install dependencies:
```bash
pip install -r requirements_dashboard.txt
```

### "No predictions yet" message
**Solution:** Generate your first prediction:
```bash
python predict.py
```
or click "Get Prediction" button in dashboard.

### Charts not showing
**Solution:** Make sure you have prediction history:
```bash
python predict.py
```
Run this a few times to generate history data.

### Port already in use
**Error:** `Address already in use`
**Solution:** Change port in app.py or kill the process:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

---

## File Structure

```
S&P USA/
├── app.py                      # Flask backend
├── templates/
│   └── dashboard.html          # Dashboard HTML
├── static/
│   ├── css/
│   │   └── style.css          # Custom styling
│   ├── js/
│   │   └── dashboard.js       # Interactive functionality
│   └── images/                # (optional) Your images
├── requirements_dashboard.txt  # Dashboard dependencies
└── DASHBOARD_README.md        # This file
```

---

## Performance Notes

- Dashboard is lightweight (loads in <1 second)
- Uses minimal server resources
- Can handle multiple concurrent users
- Auto-refreshes without page reload
- Optimized for both desktop and mobile

---

## Security Notes

### For Production Deployment:

1. **Disable Debug Mode**
   Edit `app.py`, last line:
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

2. **Use HTTPS**
   Most hosting providers (Render, Vercel) provide HTTPS automatically.

3. **Add Authentication** (Optional)
   If you want to password-protect your dashboard:
   ```bash
   pip install flask-httpauth
   ```
   Then add basic authentication to `app.py`.

4. **Set SECRET_KEY**
   Add to `app.py`:
   ```python
   app.secret_key = 'your-secret-key-here-change-this'
   ```

---

## Browser Compatibility

Tested and works on:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Android)

---

## Technology Stack

### Backend:
- **Flask** - Python web framework
- **pandas** - Data manipulation
- **numpy** - Numerical calculations

### Frontend:
- **Bootstrap 5** - Responsive design framework
- **Chart.js** - Interactive charts
- **Font Awesome** - Icons
- **Custom CSS/JS** - Animations and interactions

---

## Next Steps

### Enhancements You Can Add:

1. **Email Alerts**
   - Send email when high-confidence prediction is made
   - Daily summary emails

2. **Telegram Bot**
   - Get predictions via Telegram
   - Real-time alerts

3. **Historical Backtest View**
   - Interactive backtest results
   - Profit/loss calculator

4. **Multi-Model Comparison**
   - Compare all 4 model versions
   - Ensemble voting system

5. **User Authentication**
   - Multiple users with different accounts
   - Save personal settings

6. **Export Reports**
   - PDF report generation
   - Excel export of predictions

---

## Support

For issues or questions:
1. Check the main README.md
2. Review TROUBLESHOOTING section above
3. Check console logs in browser (F12 > Console)
4. Check Flask terminal output for errors

---

## License

This dashboard is part of your S&P 500 Prediction System.
Free to use and modify for personal/educational purposes.

---

**Enjoy your professional dashboard!**

For daily predictions without the dashboard, you can still use:
```bash
python predict.py
```
