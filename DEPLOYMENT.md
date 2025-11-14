# S&P 500 AI Prediction Dashboard - Deployment Guide

## Table of Contents
1. [Docker Deployment (Recommended)](#docker-deployment)
2. [Cloud Deployment Options](#cloud-deployment)
3. [Traditional VPS Deployment](#vps-deployment)
4. [Local Production Setup](#local-production)

---

## 🐳 Docker Deployment (Recommended)

### Prerequisites
- Docker installed ([Download Docker](https://www.docker.com/products/docker-desktop))
- Docker Compose installed (included with Docker Desktop)

### Quick Start

#### Option 1: Using Docker Compose (Easiest)
```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The dashboard will be available at: **http://localhost:5000**

#### Option 2: Using Docker CLI
```bash
# Build the image
docker build -t sp500-dashboard .

# Run the container
docker run -d \
  --name sp500-dashboard \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/predictions_history.csv:/app/predictions_history.csv \
  sp500-dashboard

# View logs
docker logs -f sp500-dashboard

# Stop the container
docker stop sp500-dashboard
```

---

## ☁️ Cloud Deployment Options

### 1. **Heroku** (Free Tier Available)

#### Setup Steps:
1. Install Heroku CLI:
```bash
# Windows (using Chocolatey)
choco install heroku-cli

# Or download from: https://devcenter.heroku.com/articles/heroku-cli
```

2. Create a `Procfile`:
```bash
echo "web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app" > Procfile
```

3. Deploy:
```bash
# Login to Heroku
heroku login

# Create app
heroku create sp500-prediction-dashboard

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Open app
heroku open
```

**Cost:** Free tier available, then $7/month for basic dyno

---

### 2. **Railway.app** (Modern & Easy)

1. Visit [Railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub repository
5. Railway will auto-detect the Dockerfile and deploy

**Cost:** $5/month for starter plan with generous free tier

---

### 3. **Render.com** (Free Tier Available)

1. Visit [Render.com](https://render.com)
2. Click "New Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Build Command:** `pip install -r requirements_dashboard.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 4 app:app`
5. Click "Create Web Service"

**Cost:** Free tier available, then $7/month

---

### 4. **Google Cloud Run** (Serverless)

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud run deploy sp500-dashboard \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Cost:** Pay per use, very affordable for low traffic (~$5-20/month)

---

### 5. **AWS Elastic Beanstalk**

```bash
# Install AWS EB CLI
pip install awsebcli

# Initialize
eb init -p docker sp500-dashboard

# Create environment and deploy
eb create sp500-env

# Open app
eb open
```

**Cost:** ~$15-30/month for t2.micro instance

---

### 6. **DigitalOcean App Platform**

1. Visit [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Connect GitHub repository
4. Select "Dockerfile" as build method
5. Deploy

**Cost:** $5/month for basic app

---

## 🖥️ VPS Deployment (Ubuntu/Debian)

### Prerequisites
- Ubuntu 20.04+ or Debian 11+ server
- SSH access
- Domain name (optional but recommended)

### Step 1: Server Setup
```bash
# SSH into your server
ssh user@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Add user to docker group
sudo usermod -aG docker $USER
```

### Step 2: Clone & Deploy
```bash
# Clone repository
git clone https://github.com/yourusername/sp500-dashboard.git
cd sp500-dashboard

# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
```

### Step 3: Setup Nginx Reverse Proxy (Optional)
```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/sp500-dashboard
```

Add this configuration:
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

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/sp500-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 4: Setup SSL with Let's Encrypt
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
```

**Cost:** $5-10/month for VPS (DigitalOcean, Linode, Vultr)

---

## 💻 Local Production Setup (Windows)

### Using Gunicorn Alternative for Windows (Waitress)

1. Install waitress:
```bash
pip install waitress
```

2. Create `run_production.py`:
```python
from waitress import serve
from app import app

if __name__ == '__main__':
    print("Starting S&P 500 Dashboard on http://localhost:5000")
    serve(app, host='0.0.0.0', port=5000, threads=4)
```

3. Run:
```bash
python run_production.py
```

---

## 🔧 Environment Variables

For production deployment, set these environment variables:

```bash
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=your-secret-key-here
PORT=5000
```

---

## 📊 Monitoring & Maintenance

### Health Check Endpoint
The app includes a health check at `/` that Docker uses automatically.

### View Logs
```bash
# Docker Compose
docker-compose logs -f

# Docker
docker logs -f sp500-dashboard

# VPS (systemd service)
sudo journalctl -u sp500-dashboard -f
```

### Update Deployment
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

---

## 🚀 Recommended Deployment

**For Beginners:** Use **Railway.app** or **Render.com** - easiest setup with free tier

**For Production:** Use **DigitalOcean** or **Linode** VPS with Docker - best price/performance

**For Scale:** Use **Google Cloud Run** or **AWS ECS** - serverless, auto-scaling

---

## 💡 Tips

1. **Always use HTTPS in production** - Use Let's Encrypt for free SSL
2. **Set up monitoring** - Use UptimeRobot or Pingdom for uptime monitoring
3. **Enable backups** - Backup your data and models folders regularly
4. **Use environment variables** - Never commit secrets to git
5. **Monitor resources** - Track CPU, memory, and disk usage

---

## 🆘 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Port already in use
```bash
# Find what's using port 5000
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000

# Change port in docker-compose.yml
ports:
  - "8080:5000"  # Access via port 8080
```

### Out of memory
- Reduce worker count in Gunicorn
- Increase VPS/container memory
- Enable swap on VPS

---

## 📞 Support

For issues or questions:
- Check logs first
- Review this deployment guide
- Contact: your-email@example.com

---

**Last Updated:** November 2025
