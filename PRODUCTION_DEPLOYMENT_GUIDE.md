# 🚀 PRODUCTION DEPLOYMENT GUIDE

## Current Setup

Your API is running locally on **`http://127.0.0.1:8001`** with the 15-disease retrained model.

For production, you need to:
1. Deploy the API to a cloud server
2. Update your app to use the production URL
3. Set up monitoring and logging
4. Configure SSL/HTTPS

---

## Option 1: Deploy to AWS (Recommended)

### Prerequisites
- AWS Account
- AWS CLI installed: `pip install awscli`

### Step 1: Create EC2 Instance

```bash
# Create security group
aws ec2 create-security-group \
  --group-name symptom-checker \
  --description "Symptom Checker API"

# Allow HTTP/HTTPS
aws ec2 authorize-security-group-ingress \
  --group-name symptom-checker \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name symptom-checker \
  --protocol tcp --port 443 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name symptom-checker \
  --protocol tcp --port 8001 --cidr 0.0.0.0/0
```

### Step 2: Launch Instance

```bash
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --security-groups symptom-checker \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=SymptomCheckerAPI}]'
```

### Step 3: Connect and Setup

```bash
# SSH into instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Update system
sudo yum update -y
sudo yum install python3 python3-pip -y

# Clone your code (or upload manually)
git clone <your-repo>
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start API
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Step 4: Setup Systemd Service

Create `/etc/systemd/system/symptom-checker.service`:

```ini
[Unit]
Description=Symptom Checker API
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/backend
Environment="PATH=/home/ec2-user/backend/venv/bin"
ExecStart=/home/ec2-user/backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable symptom-checker
sudo systemctl start symptom-checker
sudo systemctl status symptom-checker
```

### Step 5: Setup HTTPS with Let's Encrypt

```bash
sudo yum install certbot python3-certbot-nginx -y

sudo certbot certonly --standalone \
  -d your-domain.com \
  -d www.your-domain.com

# Configure Nginx as reverse proxy
sudo yum install nginx -y

# Edit /etc/nginx/nginx.conf
upstream backend {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Restart Nginx
sudo systemctl restart nginx
```

---

## Option 2: Deploy to Google Cloud Platform (GCP)

### Using Cloud Run (Easiest)

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash

# Authenticate
gcloud auth login

# Create project
gcloud projects create symptom-checker --name="Symptom Checker"

# Set project
gcloud config set project symptom-checker

# Create dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Build and deploy
gcloud builds submit --tag gcr.io/symptom-checker/api
gcloud run deploy symptom-checker-api \
  --image gcr.io/symptom-checker/api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2
```

Your API will be at: `https://symptom-checker-api-xxxxx.a.run.app`

---

## Option 3: Deploy to Azure

### Using App Service

```bash
# Install Azure CLI
pip install azure-cli

# Login
az login

# Create resource group
az group create --name symptom-checker --location eastus

# Create App Service Plan
az appservice plan create \
  --name symptom-checker-plan \
  --resource-group symptom-checker \
  --sku B2 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group symptom-checker \
  --plan symptom-checker-plan \
  --name symptom-checker-api \
  --runtime "PYTHON|3.12"

# Deploy code
git clone <your-repo>
cd backend
az webapp deployment source config-zip \
  --resource-group symptom-checker \
  --name symptom-checker-api \
  --src backend.zip
```

Your API will be at: `https://symptom-checker-api.azurewebsites.net`

---

## Option 4: Docker Deployment (Any Cloud)

### Create Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 8000

# Start server
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run Locally

```bash
# Build image
docker build -t symptom-checker:latest .

# Run container
docker run -p 8001:8000 \
  -e LOG_LEVEL=info \
  symptom-checker:latest

# Test
curl http://localhost:8001/health
```

### Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag symptom-checker:latest yourusername/symptom-checker:latest

# Push
docker push yourusername/symptom-checker:latest

# Others can now run:
docker run -p 8001:8000 yourusername/symptom-checker:latest
```

---

## Monitoring & Logging

### CloudWatch (AWS)

```bash
# Install CloudWatch agent
sudo yum install amazon-cloudwatch-agent -y

# Configure logs
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:config.json
```

### Application Logging

```python
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# In your FastAPI app
@app.post("/predict")
async def predict(payload: PredictRequest):
    logger.info(f"Prediction request: {payload.text[:50]}")
    result = model_service.predict(...)
    logger.info(f"Prediction result: {result['predicted_disease']}")
    return result
```

### Monitoring with Prometheus

Add to your app:

```python
from prometheus_client import Counter, Histogram, start_http_server

prediction_counter = Counter('predictions_total', 'Total predictions')
response_time = Histogram('prediction_response_time_seconds', 'Response time')

@app.post("/predict")
async def predict(payload: PredictRequest):
    with response_time.time():
        prediction_counter.inc()
        result = model_service.predict(...)
    return result

# Metrics available at /metrics
if __name__ == "__main__":
    start_http_server(8002)  # Metrics on separate port
```

---

## Update App Configuration

### Update Mobile App

In `mobile/lib/app/config/environment.dart`:

```dart
// DEVELOPMENT
static const String apiBaseUrl = 'http://127.0.0.1:8001';

// PRODUCTION
// static const String apiBaseUrl = 'https://api.symptom-checker.com';
// static const String apiBaseUrl = 'https://symptom-checker-api.azurewebsites.net';
// static const String apiBaseUrl = 'https://symptom-checker-api-xxxxx.a.run.app';
// static const String apiBaseUrl = 'https://your-ec2-instance.com';
```

Create environment-specific configs:

```dart
enum Environment {
  development,
  staging,
  production,
}

class Config {
  static Environment environment = Environment.development;
  
  static String get apiBaseUrl {
    switch (environment) {
      case Environment.development:
        return 'http://127.0.0.1:8001';
      case Environment.staging:
        return 'https://staging-api.symptom-checker.com';
      case Environment.production:
        return 'https://api.symptom-checker.com';
    }
  }
}
```

---

## Performance Tuning

### Increase Worker Count

```bash
# Use gunicorn instead of uvicorn for better performance
pip install gunicorn

gunicorn --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001 \
  app.main:app
```

### Enable Caching

```python
from fastapi import FastAPI
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

redis_backend = RedisBackend(Redis())
FastAPICache2.init(redis_backend, prefix="fastapi-cache")

@app.post("/predict")
@cached(namespace="predictions", expire=3600)
async def predict(payload: PredictRequest):
    # Cached for 1 hour
    return model_service.predict(...)
```

### Database Connection Pool

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40
)
```

---

## Monitoring Checklist

- [ ] Health check endpoint responding
- [ ] Prediction latency < 200ms
- [ ] Error rate < 1%
- [ ] Database connections stable
- [ ] SSL/HTTPS working
- [ ] Logs being collected
- [ ] Metrics being tracked
- [ ] Alerts configured
- [ ] Backup strategy in place
- [ ] Disaster recovery plan ready

---

## Cost Estimation

| Platform | Service | Monthly Cost |
|----------|---------|--------------|
| AWS | EC2 t3.medium + RDS | $30-50 |
| GCP | Cloud Run + Cloud SQL | $20-40 |
| Azure | App Service B2 + Database | $40-60 |
| Docker | Any VPS | $5-20 |

---

## Next Steps

1. Choose your hosting platform
2. Follow the deployment guide for your platform
3. Update your mobile app with new API URL
4. Set up monitoring and alerts
5. Configure SSL/HTTPS
6. Test thoroughly before going live
7. Monitor performance metrics
8. Plan for scaling if needed

---

## Support Resources

- AWS Documentation: https://docs.aws.amazon.com
- GCP Documentation: https://cloud.google.com/docs
- Azure Documentation: https://docs.microsoft.com/azure
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment
- Docker Documentation: https://docs.docker.com

