# Deployment Guide - Secondary Research Workflow System

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Production Configuration](#production-configuration)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Security Configuration](#security-configuration)
8. [Backup and Recovery](#backup-and-recovery)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 2 cores, 2.0 GHz
- **RAM**: 4 GB
- **Storage**: 20 GB available space
- **Network**: Stable internet connection for data collection

#### Recommended Requirements
- **CPU**: 4+ cores, 2.5+ GHz
- **RAM**: 8+ GB
- **Storage**: 50+ GB SSD
- **Network**: High-speed internet with low latency

#### Software Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10+
- **Python**: 3.11 or higher
- **Docker**: 20.10+ (for containerized deployment)
- **Git**: 2.30+ (for source code management)

### External Dependencies

#### Database (Optional)
- **PostgreSQL**: 13+ (recommended for production)
- **Redis**: 6+ (for caching and session management)

#### External APIs
- **Yahoo Finance API**: Free tier available
- **Google News API**: Free tier available
- **PubMed API**: Free access
- **ArXiv API**: Free access
- **SEC EDGAR API**: Free access

## Local Development Setup

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/alejandromichell/Secondary-Research-Workflow_V1.git
cd Secondary-Research-Workflow_V1

# Verify Python version
python --version  # Should be 3.11+
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

### Step 4: Configure Environment

```bash
# Create environment file
cp .env.example .env

# Edit environment variables
nano .env
```

#### Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1
LOG_LEVEL=DEBUG

# Database Configuration (Optional)
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=research_workflow
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# Redis Configuration (Optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Security
SECRET_KEY=your_very_long_secret_key_here_at_least_32_characters

# Data Collection
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30

# Environment
ENVIRONMENT=development
```

### Step 5: Start the Application

```bash
# Start development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Verify startup
curl http://localhost:8000/api/status
```

### Step 6: Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/status

## Docker Deployment

### Step 1: Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs cache data

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/status || exit 1

# Start application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Step 2: Create Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_HOST=postgres
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
      - ./cache:/app/cache
      - ./data:/app/data
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=research_workflow
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass your_redis_password
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Step 3: Deploy with Docker

```bash
# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Step 4: Configure Nginx (Optional)

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## Cloud Deployment

### AWS Deployment

#### Option 1: AWS ECS (Elastic Container Service)

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name research-workflow

# Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
    --cluster research-workflow \
    --service-name research-workflow-service \
    --task-definition research-workflow:1 \
    --desired-count 2 \
    --launch-type FARGATE
```

#### Option 2: AWS EC2

```bash
# Launch EC2 instance
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --instance-type t3.medium \
    --key-name your-key-pair \
    --security-group-ids sg-12345678

# Connect to instance
ssh -i your-key-pair.pem ec2-user@your-instance-ip

# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Deploy application
git clone https://github.com/alejandromichell/Secondary-Research-Workflow_V1.git
cd Secondary-Research-Workflow_V1
docker-compose up -d
```

### Google Cloud Deployment

#### Option 1: Google Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/your-project/research-workflow

# Deploy to Cloud Run
gcloud run deploy research-workflow \
    --image gcr.io/your-project/research-workflow \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

#### Option 2: Google Compute Engine

```bash
# Create VM instance
gcloud compute instances create research-workflow \
    --image-family ubuntu-2004-lts \
    --image-project ubuntu-os-cloud \
    --machine-type e2-medium \
    --zone us-central1-a

# Connect to instance
gcloud compute ssh research-workflow --zone us-central1-a

# Install and deploy
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker

git clone https://github.com/alejandromichell/Secondary-Research-Workflow_V1.git
cd Secondary-Research-Workflow_V1
sudo docker-compose up -d
```

### Azure Deployment

#### Option 1: Azure Container Instances

```bash
# Create resource group
az group create --name research-workflow-rg --location eastus

# Deploy container
az container create \
    --resource-group research-workflow-rg \
    --name research-workflow \
    --image your-registry/research-workflow:latest \
    --ports 8000 \
    --dns-name-label research-workflow \
    --environment-variables ENVIRONMENT=production
```

#### Option 2: Azure App Service

```bash
# Create App Service plan
az appservice plan create \
    --name research-workflow-plan \
    --resource-group research-workflow-rg \
    --sku B1 \
    --is-linux

# Create web app
az webapp create \
    --resource-group research-workflow-rg \
    --plan research-workflow-plan \
    --name research-workflow-app \
    --deployment-container-image-name your-registry/research-workflow:latest
```

## Production Configuration

### Environment Configuration

#### Production Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
LOG_LEVEL=WARNING
CORS_ORIGINS=["https://your-domain.com"]

# Database Configuration
DATABASE_HOST=your-db-host
DATABASE_PORT=5432
DATABASE_NAME=research_workflow_prod
DATABASE_USER=research_user
DATABASE_PASSWORD=strong_password_here

# Redis Configuration
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=strong_redis_password

# Security
SECRET_KEY=very_long_random_secret_key_at_least_32_characters
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENABLE_2FA=true

# Data Collection
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30
RATE_LIMIT_PER_HOUR=1000

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30
ENABLE_ALERTING=true
ALERT_WEBHOOK=https://your-monitoring-system.com/webhook

# Environment
ENVIRONMENT=production
DEBUG=false
```

### Database Setup

#### PostgreSQL Configuration

```sql
-- Create database
CREATE DATABASE research_workflow_prod;

-- Create user
CREATE USER research_user WITH PASSWORD 'strong_password_here';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE research_workflow_prod TO research_user;

-- Create tables (if needed)
\c research_workflow_prod;
-- Add your table creation scripts here
```

#### Redis Configuration

```bash
# Redis configuration file
# /etc/redis/redis.conf

# Security
requirepass strong_redis_password

# Memory management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log
```

### SSL/TLS Configuration

#### Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## Monitoring and Logging

### Application Monitoring

#### Health Checks

```bash
# Basic health check
curl -f http://localhost:8000/api/status

# Detailed health check
curl http://localhost:8000/api/health/detailed

# Data collection status
curl http://localhost:8000/data-collection/status/plan_id
```

#### Metrics Collection

```python
# Prometheus metrics endpoint
# Available at http://localhost:9090/metrics

# Key metrics to monitor:
# - HTTP request duration
# - Data collection success rate
# - Cache hit/miss ratio
# - System resource usage
# - Error rates by endpoint
```

### Log Management

#### Log Configuration

```python
# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
```

#### Log Rotation

```bash
# Configure logrotate
# /etc/logrotate.d/research-workflow

/var/log/research-workflow/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 app app
    postrotate
        systemctl reload research-workflow
    endscript
}
```

### Alerting Setup

#### Prometheus + Grafana

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'research-workflow'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: /metrics
    scrape_interval: 30s
```

#### Alert Rules

```yaml
# alert_rules.yml
groups:
  - name: research-workflow
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          
      - alert: DataCollectionFailure
        expr: data_collection_success_rate < 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Data collection success rate below 80%"
```

## Security Configuration

### Authentication and Authorization

#### JWT Configuration

```python
# JWT settings
SECRET_KEY = "your-very-long-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

#### User Management

```python
# User roles and permissions
ROLES = {
    "admin": ["read", "write", "delete", "manage_users"],
    "researcher": ["read", "write", "create_plans"],
    "viewer": ["read"]
}
```

### Network Security

#### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # Application (if direct access needed)
```

#### Security Headers

```python
# Security middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["your-domain.com", "*.your-domain.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Data Protection

#### Encryption at Rest

```bash
# Encrypt sensitive data
# Use environment variables for secrets
# Encrypt database connections
# Use encrypted volumes for data storage
```

#### API Rate Limiting

```python
# Rate limiting configuration
RATE_LIMITS = {
    "default": "1000/hour",
    "data_collection": "100/hour",
    "report_generation": "10/hour"
}
```

## Backup and Recovery

### Database Backup

#### Automated Backups

```bash
#!/bin/bash
# backup_database.sh

BACKUP_DIR="/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="research_workflow_prod"

# Create backup
pg_dump -h localhost -U postgres $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Remove old backups (keep 30 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Upload to cloud storage (optional)
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://your-backup-bucket/
```

#### Backup Schedule

```bash
# Crontab entry
# Daily backup at 2 AM
0 2 * * * /path/to/backup_database.sh
```

### Application Data Backup

#### File System Backup

```bash
#!/bin/bash
# backup_application.sh

BACKUP_DIR="/backups/application"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/app"

# Create backup
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz \
    $APP_DIR/logs \
    $APP_DIR/cache \
    $APP_DIR/data \
    $APP_DIR/config

# Upload to cloud storage
aws s3 cp $BACKUP_DIR/app_backup_$DATE.tar.gz s3://your-backup-bucket/
```

### Recovery Procedures

#### Database Recovery

```bash
# Restore from backup
gunzip backup_20240101_020000.sql.gz
psql -h localhost -U postgres research_workflow_prod < backup_20240101_020000.sql
```

#### Application Recovery

```bash
# Restore application data
tar -xzf app_backup_20240101_020000.tar.gz -C /
systemctl restart research-workflow
```

## Troubleshooting

### Common Issues

#### Application Won't Start

**Symptoms**: Service fails to start or crashes immediately
**Solutions**:
1. Check logs: `journalctl -u research-workflow -f`
2. Verify configuration: `python -c "from src.config import get_config; print(get_config())"`
3. Check dependencies: `pip list`
4. Verify environment variables: `env | grep API_`

#### Database Connection Issues

**Symptoms**: Database connection errors in logs
**Solutions**:
1. Check database status: `systemctl status postgresql`
2. Verify connection: `psql -h localhost -U postgres -d research_workflow`
3. Check firewall: `sudo ufw status`
4. Verify credentials in environment variables

#### Data Collection Failures

**Symptoms**: Low success rates or missing data
**Solutions**:
1. Check network connectivity: `ping google.com`
2. Test individual sources: Use the test endpoint
3. Review rate limiting settings
4. Check API key requirements
5. Monitor system resources: `htop`

#### Performance Issues

**Symptoms**: Slow response times or high resource usage
**Solutions**:
1. Monitor system resources: `htop`, `iostat`
2. Check application logs for errors
3. Review database performance: `pg_stat_activity`
4. Optimize configuration settings
5. Scale horizontally if needed

### Diagnostic Commands

#### System Health Check

```bash
# Check system resources
free -h
df -h
top

# Check network connectivity
ping -c 4 google.com
curl -I https://api.example.com

# Check service status
systemctl status research-workflow
docker ps
```

#### Application Health Check

```bash
# Check application status
curl http://localhost:8000/api/status

# Check health endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/data-collection/sources

# Check logs
tail -f logs/app.log
journalctl -u research-workflow -f
```

#### Database Health Check

```bash
# Check database status
systemctl status postgresql
sudo -u postgres psql -c "SELECT version();"

# Check database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('research_workflow'));"

# Check active connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

### Support and Escalation

#### Log Collection

```bash
# Collect diagnostic information
mkdir -p diagnostics
cd diagnostics

# System information
uname -a > system_info.txt
free -h >> system_info.txt
df -h >> system_info.txt

# Application logs
cp /var/log/research-workflow/*.log .
cp /app/logs/*.log .

# Configuration
cp /app/.env .
cp /app/config/*.json .

# Create archive
tar -czf diagnostics_$(date +%Y%m%d_%H%M%S).tar.gz *
```

#### Contact Support

When contacting support, please include:
1. **System information**: OS, Python version, Docker version
2. **Error messages**: Complete error logs and stack traces
3. **Configuration**: Environment variables and config files
4. **Steps to reproduce**: Detailed steps that led to the issue
5. **Expected vs actual behavior**: What should happen vs what actually happens

---

**Need more help?** Check out our [FAQ](faq.md) or [contact support](support.md) for additional assistance.
