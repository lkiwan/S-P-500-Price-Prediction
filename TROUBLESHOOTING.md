# Troubleshooting Guide - Website Not Showing

## ✅ Current Status

The website IS running successfully:
- Container: `sp500-dashboard` is UP and HEALTHY
- Port: 5000 is exposed and working
- Logs show: "Listening at: http://0.0.0.0:5000"
- Test connection: Successful (returns HTML)

## 🌐 How to Access

### Method 1: Direct Browser Access

1. Open your web browser (Chrome, Firefox, Edge)
2. Type one of these URLs:
   ```
   http://localhost:5000
   http://127.0.0.1:5000
   http://192.168.0.107:5000
   ```
3. Press Enter

### Method 2: Use the Batch File

Double-click: `QUICK_START.bat`

This will:
- Start the Docker container
- Wait for it to be ready
- Open your browser automatically

### Method 3: Manual Check

1. Open Command Prompt
2. Run: `curl http://localhost:5000`
3. You should see HTML output

---

## ❌ Common Issues & Solutions

### Issue 1: "This site can't be reached"

**Cause**: Browser can't connect to localhost:5000

**Solutions**:

A. Try different URL format:
```
http://localhost:5000      (try this first)
http://127.0.0.1:5000      (if localhost fails)
http://0.0.0.0:5000        (alternative)
```

B. Check Docker is running:
```bash
docker ps
# Should show: sp500-dashboard with status "Up"
```

C. Restart Docker container:
```bash
docker-compose down
docker-compose up -d
```

### Issue 2: Port 5000 Already in Use

**Check what's using port 5000**:
```bash
netstat -ano | findstr :5000
```

**Solution A - Kill the process**:
```bash
# Find the PID from netstat output
taskkill /F /PID <PID_NUMBER>
```

**Solution B - Use different port**:

Edit `docker-compose.yml`:
```yaml
ports:
  - "5001:5000"  # Change 5000 to 5001
```

Then access: `http://localhost:5001`

### Issue 3: Windows Firewall Blocking

**Solution**:

1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules"
4. Click "New Rule..."
5. Select "Port" → Next
6. Enter "5000" → Next
7. "Allow the connection" → Next
8. Check all boxes → Next
9. Name: "S&P500 Dashboard" → Finish

### Issue 4: Browser Cache

**Solution**:

1. Press `Ctrl + Shift + Delete` in browser
2. Select "Cached images and files"
3. Click "Clear data"
4. Try accessing again

OR

- Try in Incognito/Private mode (`Ctrl + Shift + N` in Chrome)

### Issue 5: Docker Desktop Not Running

**Check Docker**:
```bash
docker --version
docker-compose --version
```

**If Docker not found**:
1. Open Docker Desktop application
2. Wait for it to fully start (whale icon in system tray)
3. Try again

---

## 🔍 Diagnostic Commands

### Check Container Status
```bash
docker-compose ps
# Should show: Up (healthy)
```

### View Container Logs
```bash
docker-compose logs -f
# Should show: "Listening at: http://0.0.0.0:5000"
```

### Test Connection
```bash
curl http://localhost:5000
# Should return HTML
```

### Check Port Availability
```bash
netstat -ano | findstr :5000
# Should show Docker process
```

### Restart Everything
```bash
docker-compose down
docker-compose up --build -d
docker-compose logs -f
```

---

## 🚀 Alternative: Run Without Docker

If Docker continues to have issues, run directly with Python:

### Step 1: Stop Docker
```bash
docker-compose down
```

### Step 2: Install Python Requirements
```bash
pip install -r requirements.txt
```

### Step 3: Run Application
```bash
python app.py
```

### Step 4: Access
```
http://localhost:5000
```

---

## 📱 Verify Website is Working

Once you can access the site, you should see:

✅ **Homepage displays**:
- "S&P 500 AI Prediction Dashboard" title
- Model Accuracy: **71.20%**
- Latest prediction card
- Charts and graphs

✅ **Features working**:
- Prediction updates
- Charts render
- PDF report download
- API endpoints respond

---

## 🆘 Still Not Working?

### Quick Reset Everything

```bash
# Stop everything
docker-compose down

# Remove old containers
docker rm -f sp500-dashboard

# Rebuild fresh
docker-compose up --build -d

# Wait 30 seconds
timeout /t 30

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Check System Requirements

**Minimum**:
- Docker Desktop installed and running
- 4 GB RAM available
- Port 5000 free
- Windows 10/11

**Browser**:
- Chrome 90+
- Firefox 88+
- Edge 90+
- (Do NOT use Internet Explorer)

---

## 📊 Expected Output

When working correctly, you should see in logs:

```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:5000
[INFO] Using worker: gevent
[INFO] Booting worker with pid: 7
[INFO] Booting worker with pid: 8
[INFO] Booting worker with pid: 9
[INFO] Booting worker with pid: 10
```

And in browser:
```
✅ Dashboard loads with charts
✅ Shows "71.20%" accuracy
✅ Latest prediction visible
✅ No error messages
```

---

## 💡 Quick Tips

1. **Always use `http://` not `https://`**
   - ✅ `http://localhost:5000`
   - ❌ `https://localhost:5000`

2. **Check Docker Desktop is green/running**
   - Look for whale icon in system tray
   - Should NOT be red/orange

3. **Wait 10-15 seconds after starting**
   - Container needs time to initialize
   - Check logs for "Booting worker" messages

4. **Try different browsers**
   - Chrome usually works best
   - Avoid Internet Explorer

5. **Disable VPN if using one**
   - VPNs can block localhost connections

---

## ✅ Success Checklist

- [ ] Docker Desktop is running (green whale icon)
- [ ] Container shows "Up (healthy)" status
- [ ] Port 5000 is not used by other apps
- [ ] Firewall allows port 5000
- [ ] Browser is up to date
- [ ] Using `http://` not `https://`
- [ ] Waited at least 30 seconds after starting
- [ ] Tried multiple URL formats
- [ ] Cleared browser cache

---

## 📞 Last Resort

If nothing works:

1. Take a screenshot of:
   - `docker-compose ps` output
   - `docker logs sp500-dashboard` output
   - Browser error message

2. Check these URLs work:
   - `http://localhost:5000` (main)
   - `http://localhost:5000/api/metrics` (API)
   - `http://127.0.0.1:5000` (alternative)

3. Try the Python method (without Docker) as shown above

---

**Your website IS running successfully!**

**Container Status**: ✅ UP and HEALTHY
**Port**: 5000
**URL**: http://localhost:5000

The issue is likely browser/network related, not the application itself.
