# Manufacturing Workload Management App - Production Deployment Guide

## Overview

This guide covers deploying the optimized Flask Manufacturing Workload Management App to production with all performance, security, and scalability enhancements.

## 🚀 Production Requirements

### System Requirements
- **Python**: 3.9+
- **Database**: PostgreSQL 12+
- **Cache**: Redis 6+
- **Web Server**: Nginx + Gunicorn
- **OS**: Ubuntu 20.04 LTS or CentOS 8+

### Dependencies
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib redis-server nginx

# Create application user
sudo useradd -m -s /bin/bash manufacturing
sudo usermod -a -G sudo manufacturing
```

## 🔧 Environment Setup

### 1. Clone and Setup Application
```bash
# Switch to application user
sudo su - manufacturing

# Clone repository
git clone <repository-url> /opt/manufacturing-app
cd /opt/manufacturing-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 2. Database Configuration
```bash
# Switch to postgres user
sudo su - postgres

# Create database and user
createdb manufacturing_prod
createuser -P manufacturing_user
# Enter password when prompted

# Grant privileges
psql -c "GRANT ALL PRIVILEGES ON DATABASE manufacturing_prod TO manufacturing_user;"
psql -c "ALTER USER manufacturing_user CREATEDB;"
```

### 3. Redis Configuration
```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Add these settings:
maxmemory 256mb
maxmemory-policy allkeys-lru
bind 127.0.0.1
port 6379

# Restart Redis
sudo systemctl restart redis
sudo systemctl enable redis
```

## 🔐 Environment Variables

Create `/opt/manufacturing-app/.env`:
```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this
SECURITY_PASSWORD_SALT=your-security-salt-change-this

# Database
DATABASE_URL=postgresql://manufacturing_user:password@localhost/manufacturing_prod

# Redis
REDIS_URL=redis://localhost:6379/0
CACHE_REDIS_URL=redis://localhost:6379/0
RATELIMIT_STORAGE_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/2
CELERY_RESULT_BACKEND=redis://localhost:6379/3

# Security
SESSION_COOKIE_SECURE=true
WTF_CSRF_SSL_STRICT=true
TALISMAN_FORCE_HTTPS=true

# Email (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-app-password

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/manufacturing-app/app.log
```

## 🎯 Database Migration

```bash
# Switch to app directory
cd /opt/manufacturing-app
source venv/bin/activate

# Initialize database
flask db upgrade

# Seed with initial data
python seed_data.py
```

## 🌐 Gunicorn Configuration

Create `/opt/manufacturing-app/gunicorn.conf.py`:
```python
# Gunicorn configuration
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
user = "manufacturing"
group = "manufacturing"
tmp_upload_dir = None
errorlog = "/var/log/manufacturing-app/gunicorn_error.log"
accesslog = "/var/log/manufacturing-app/gunicorn_access.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
loglevel = "info"
capture_output = True
enable_stdio_inheritance = True
```

## 📊 Systemd Service

Create `/etc/systemd/system/manufacturing-app.service`:
```ini
[Unit]
Description=Manufacturing Workload Management App
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=manufacturing
Group=manufacturing
WorkingDirectory=/opt/manufacturing-app
Environment=PATH=/opt/manufacturing-app/venv/bin
EnvironmentFile=/opt/manufacturing-app/.env
ExecStart=/opt/manufacturing-app/venv/bin/gunicorn --config gunicorn.conf.py run:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🔄 Celery Background Tasks

Create `/etc/systemd/system/manufacturing-celery.service`:
```ini
[Unit]
Description=Manufacturing App Celery Worker
After=network.target redis.service

[Service]
Type=exec
User=manufacturing
Group=manufacturing
WorkingDirectory=/opt/manufacturing-app
Environment=PATH=/opt/manufacturing-app/venv/bin
EnvironmentFile=/opt/manufacturing-app/.env
ExecStart=/opt/manufacturing-app/venv/bin/celery -A app.celery worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🌍 Nginx Configuration

Create `/etc/nginx/sites-available/manufacturing-app`:
```nginx
upstream manufacturing_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    # Logging
    access_log /var/log/nginx/manufacturing-app.access.log;
    error_log /var/log/nginx/manufacturing-app.error.log;

    # Static Files
    location /static/ {
        alias /opt/manufacturing-app/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API Rate Limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://manufacturing_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Login Rate Limiting
    location /auth/login {
        limit_req zone=login burst=10 nodelay;
        proxy_pass http://manufacturing_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # General Application
    location / {
        proxy_pass http://manufacturing_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        application/atom+xml
        application/javascript
        application/json
        application/rss+xml
        application/vnd.ms-fontobject
        application/x-font-ttf
        application/x-web-app-manifest+json
        application/xhtml+xml
        application/xml
        font/opentype
        image/svg+xml
        image/x-icon
        text/css
        text/plain
        text/x-component;
}
```

## 🔄 Deployment Steps

### 1. Setup Services
```bash
# Create log directory
sudo mkdir -p /var/log/manufacturing-app
sudo chown manufacturing:manufacturing /var/log/manufacturing-app

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable manufacturing-app
sudo systemctl enable manufacturing-celery
sudo systemctl start manufacturing-app
sudo systemctl start manufacturing-celery

# Enable and configure Nginx
sudo ln -s /etc/nginx/sites-available/manufacturing-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 2. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### 3. Monitoring Setup
```bash
# Install monitoring tools
sudo apt-get install htop iotop nethogs

# Setup log rotation
sudo nano /etc/logrotate.d/manufacturing-app
```

Add to logrotate config:
```
/var/log/manufacturing-app/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 manufacturing manufacturing
    postrotate
        systemctl reload manufacturing-app
    endscript
}
```

## 🔍 Health Checks

Create `/opt/manufacturing-app/health_check.py`:
```python
#!/usr/bin/env python3
import requests
import sys
import redis
import psycopg2
from urllib.parse import urlparse

def check_app():
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        return response.status_code == 200
    except:
        return False

def check_redis():
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        return True
    except:
        return False

def check_database():
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='manufacturing_prod',
            user='manufacturing_user',
            password='password'
        )
        conn.close()
        return True
    except:
        return False

if __name__ == '__main__':
    checks = {
        'app': check_app(),
        'redis': check_redis(),
        'database': check_database()
    }
    
    all_healthy = all(checks.values())
    
    for service, healthy in checks.items():
        status = "✅ HEALTHY" if healthy else "❌ UNHEALTHY"
        print(f"{service}: {status}")
    
    sys.exit(0 if all_healthy else 1)
```

## 📊 Performance Monitoring

### Application Metrics
- **Response Time**: Monitor with Nginx logs
- **Database Queries**: Use SQLAlchemy query logging
- **Cache Hit Rate**: Monitor Redis metrics
- **Error Rate**: Track application logs

### System Metrics
- **CPU Usage**: Monitor with htop
- **Memory Usage**: Track with free -h
- **Disk I/O**: Monitor with iotop
- **Network**: Track with nethogs

## 🔧 Maintenance Tasks

### Daily Tasks
```bash
# Check system health
./health_check.py

# Monitor logs
sudo journalctl -u manufacturing-app --since "1 hour ago"

# Check database performance
psql -d manufacturing_prod -c "SELECT * FROM pg_stat_activity;"
```

### Weekly Tasks
```bash
# Update dependencies
pip list --outdated

# Database maintenance
psql -d manufacturing_prod -c "VACUUM ANALYZE;"

# Clean old logs
sudo logrotate -f /etc/logrotate.d/manufacturing-app
```

## 🔐 Security Checklist

- [ ] SSL/TLS certificate configured
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] Database connections encrypted
- [ ] Regular security updates applied
- [ ] Log monitoring configured
- [ ] Firewall rules configured
- [ ] User access controls implemented

## 📚 Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   sudo systemctl status manufacturing-app
   sudo journalctl -u manufacturing-app -f
   ```

2. **Database Connection Issues**
   ```bash
   sudo -u postgres psql
   \l  # List databases
   \du # List users
   ```

3. **Redis Connection Issues**
   ```bash
   redis-cli ping
   redis-cli info
   ```

4. **High Memory Usage**
   ```bash
   free -h
   ps aux --sort=-%mem | head
   ```

### Performance Optimization

1. **Database Query Optimization**
   - Use database indexes
   - Optimize N+1 queries
   - Use query result caching

2. **Redis Optimization**
   - Set appropriate memory limits
   - Use efficient data structures
   - Monitor key expiration

3. **Application Optimization**
   - Enable gzip compression
   - Use CDN for static assets
   - Implement connection pooling

## 🎯 Success Metrics

- **Uptime**: > 99.9%
- **Response Time**: < 200ms (95th percentile)
- **Error Rate**: < 0.1%
- **Database Query Time**: < 50ms average
- **Cache Hit Rate**: > 90%
- **Memory Usage**: < 80% of available
- **CPU Usage**: < 70% average

---

This deployment guide ensures your Manufacturing Workload Management App runs efficiently, securely, and scales properly in production. 