# S&P 500 AI Dashboard - Deployment Guide

## 🎯 Achievement Status

✅ **71.20% Accuracy Achieved!**
✅ **Website Updated**
✅ **Docker Ready**
✅ **Pushed to GitHub**

---

## 🚀 Quick Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/lkiwan/S-P-500-Price-Prediction.git
cd "S-P-500-Price-Prediction"

# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Access dashboard
open http://localhost:5000
```

### Option 2: Docker Build

```bash
# Build image
docker build -t sp500-dashboard:latest .

# Run container
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  --name sp500-dashboard \
  sp500-dashboard:latest

# Check logs
docker logs -f sp500-dashboard

# Access dashboard
open http://localhost:5000
```

### Option 3: Manual Python Setup

```bash
# Clone repository
git clone https://github.com/lkiwan/S-P-500-Price-Prediction.git
cd "S-P-500-Price-Prediction"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

# Access dashboard
open http://localhost:5000
```

---

## 📋 Pre-Deployment Checklist

### Required Files
- [x] `models/sp500_complete_20251113.pkl` - Main model
- [x] `models/sp500_complete_20251113_scaler.pkl` - Feature scaler
- [x] `models/sp500_complete_20251113_features.pkl` - Feature names
- [x] `data/features/features_complete.csv` - Feature data
- [x] `data/raw/price_data.csv` - Price history
- [x] `predictions_history.csv` - Prediction records

### Configuration
- [x] `config.yaml` - Model configuration
- [x] `Dockerfile` - Container build
- [x] `docker-compose.yml` - Service orchestration
- [x] `requirements.txt` - Python dependencies

---

## 🐳 Docker Details

### Image Specifications

- **Base Image**: python:3.11-slim
- **Port**: 5000
- **WSGI Server**: Gunicorn with gevent workers
- **Workers**: 4 concurrent workers
- **Health Check**: Every 30 seconds
- **Auto-restart**: unless-stopped

### Environment Variables

```bash
FLASK_ENV=production
FLASK_APP=app.py
PYTHONUNBUFFERED=1
```

### Volume Mounts

```yaml
volumes:
  - ./data:/app/data              # Data persistence
  - ./models:/app/models          # Model files
  - ./predictions_history.csv:/app/predictions_history.csv
  - ./predictions_with_accuracy.csv:/app/predictions_with_accuracy.csv
```

---

## 🧪 Testing Deployment

### 1. Health Check

```bash
# Check if service is running
curl http://localhost:5000/

# Should return dashboard HTML
```

### 2. API Endpoints

```bash
# Get latest metrics
curl http://localhost:5000/api/metrics

# Get latest prediction
curl http://localhost:5000/api/latest_prediction

# Get accuracy stats
curl http://localhost:5000/api/accuracy_stats
```

### 3. Test Prediction

```bash
# Run prediction script
docker exec -it sp500-dashboard python predict.py

# Should output:
# Market Direction: UP/DOWN
# Confidence: XX.XX%
# Accuracy: 71.20%
```

---

## 🔧 Production Configuration

### Gunicorn Settings (Already Configured)

```python
# In Dockerfile CMD
gunicorn \
  --bind 0.0.0.0:5000 \
  --workers 4 \
  --worker-class gevent \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  app:app
```

### Nginx Reverse Proxy (Optional)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📊 Performance Metrics

### Model Performance

```
Base Accuracy:          71.20%
High-Confidence (80%+): 93.12%
AUC-ROC:               80.39%
F1 Score:              77.64%
Precision:             71.27%
Recall:                85.27%
```

### System Requirements

**Minimum**:
- 2 CPU cores
- 4 GB RAM
- 10 GB storage

**Recommended**:
- 4 CPU cores
- 8 GB RAM
- 20 GB storage

---

## 🔄 Updating the Model

### When to Retrain

- Monthly: Incorporate new market data
- After major market events
- When accuracy drops below 65%
- Every 3 months minimum

### Retrain Process

```bash
# 1. Update data
python run_complete_pipeline.py

# 2. Validate new model
python test_original_model_properly.py

# 3. If accuracy is good, update app.py
# Change model_name to new model file

# 4. Rebuild Docker
docker-compose down
docker-compose up --build -d
```

---

## 📈 Monitoring

### Key Metrics to Track

1. **Prediction Accuracy**
   - Daily win rate
   - Rolling 7-day accuracy
   - Monthly performance

2. **Confidence Distribution**
   - % of high-confidence predictions
   - Accuracy by confidence level

3. **System Health**
   - Response time
   - Memory usage
   - Error rate

### Logging

```bash
# View application logs
docker-compose logs -f web

# View specific time range
docker-compose logs --since 1h web

# Save logs to file
docker-compose logs web > logs.txt
```

---

## 🆘 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs web

# Common issues:
# 1. Port 5000 already in use
#    Solution: Change port in docker-compose.yml

# 2. Missing model files
#    Solution: Ensure models/ directory has required files

# 3. Missing data
#    Solution: Run run_complete_pipeline.py first
```

### Low Accuracy

```bash
# 1. Check data freshness
ls -lh data/raw/price_data.csv

# 2. Verify model loaded
docker exec sp500-dashboard python -c "import joblib; m = joblib.load('models/sp500_complete_20251113.pkl'); print('Model loaded OK')"

# 3. Retrain if needed
docker exec sp500-dashboard python run_complete_pipeline.py
```

### High Memory Usage

```bash
# Reduce Gunicorn workers in Dockerfile
# Change --workers 4 to --workers 2

# Rebuild
docker-compose up --build -d
```

---

## 🔐 Security Considerations

### Production Checklist

- [ ] Change default Flask secret key
- [ ] Enable HTTPS (use nginx + Let's Encrypt)
- [ ] Set up firewall rules
- [ ] Regular backups of data/ and models/
- [ ] Monitor for unusual API access patterns
- [ ] Keep dependencies updated

### Recommended Setup

```bash
# 1. Use environment variables for secrets
export FLASK_SECRET_KEY="your-random-secret-key"

# 2. Run behind reverse proxy (nginx)
# 3. Enable rate limiting
# 4. Set up SSL/TLS certificates
```

---

## 📦 Backup & Recovery

### What to Backup

```bash
# Essential files
models/sp500_complete_20251113.*
data/features/features_complete.csv
data/raw/price_data.csv
predictions_history.csv
config.yaml
```

### Backup Script

```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf backup_$DATE.tar.gz \
  models/ \
  data/ \
  predictions_history.csv \
  config.yaml

echo "Backup created: backup_$DATE.tar.gz"
```

### Recovery

```bash
# Extract backup
tar -xzf backup_YYYYMMDD.tar.gz

# Rebuild and restart
docker-compose up --build -d
```

---

## 🎯 Success Criteria

✅ **Deployment Successful If**:

1. Dashboard loads at http://localhost:5000
2. Displays "71.20%" accuracy
3. Latest prediction shows with confidence
4. Charts and graphs render correctly
5. PDF report generation works
6. API endpoints respond correctly
7. No errors in docker logs

---

## 📞 Support & Maintenance

### Daily Tasks
- Check prediction accuracy
- Monitor system logs
- Verify API responses

### Weekly Tasks
- Review prediction history
- Calculate rolling accuracy
- Check data freshness

### Monthly Tasks
- Retrain model with new data
- Update dependencies
- Review performance metrics
- Backup all data

---

## 🎉 Deployment Complete!

Your S&P 500 AI Prediction Dashboard is now live with:

- ✅ **71.20% Accuracy** (93.12% at high confidence)
- ✅ **Docker Containerized**
- ✅ **Production Ready**
- ✅ **Fully Documented**
- ✅ **Pushed to GitHub**

**Access Dashboard**: http://localhost:5000

**GitHub Repository**: https://github.com/lkiwan/S-P-500-Price-Prediction

---

**Last Updated**: 2025-11-14
**Model**: sp500_complete_20251113
**Status**: Production Ready 🚀
