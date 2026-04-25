# OBA Smart Assistant - Deployment Guide

This guide covers deploying OBA Smart Assistant to production environments.

## Deployment Options

| Option | Best For | Complexity |
|--------|----------|------------|
| Docker Compose | Single server, small scale | Low |
| Kubernetes | Multi-server, auto-scaling | High |
| AWS ECS | AWS ecosystem | Medium |
| GCP Cloud Run | GCP ecosystem, serverless | Medium |
| Azure Container Apps | Azure ecosystem | Medium |

---

## Pre-Deployment Checklist

- [ ] Update all secrets in `.env`
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS for production domains
- [ ] Set `ENVIRONMENT=production`
- [ ] Enable rate limiting
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Configure backup strategy
- [ ] Review security settings
- [ ] Test with production data volume

---

## Option 1: Docker Compose (Single Server)

### Requirements
- Ubuntu 22.04+ server
- 4GB+ RAM
- 50GB+ storage
- Docker & Docker Compose installed

### Setup

```bash
# 1. Clone repository
git clone https://github.com/your-org/oba-smart-assistant.git
cd oba-smart-assistant

# 2. Create production environment file
cp .env.example .env.production
nano .env.production
```

### Production Environment File

```bash
# .env.production
POSTGRES_USER=oba_prod_user
POSTGRES_PASSWORD=<strong-random-password>
POSTGRES_DB=oba_production

REDIS_PASSWORD=<strong-random-password>

SECRET_KEY=<64-character-random-string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://app.oba.az,https://admin.oba.az
```

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - oba_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - oba_network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    restart: always
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - oba_network

  dashboard:
    build:
      context: ./dashboard
      dockerfile: Dockerfile
    restart: always
    environment:
      - API_BASE_URL=http://backend:8000/api/v1
    depends_on:
      - backend
    networks:
      - oba_network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/certbot:/var/www/certbot
    depends_on:
      - backend
      - dashboard
    networks:
      - oba_network

volumes:
  postgres_data:
  redis_data:

networks:
  oba_network:
    driver: bridge
```

### Production Backend Dockerfile

Create `backend/Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY . .

RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

### Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream dashboard {
        server dashboard:8501;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general:10m rate=30r/s;

    # API Server
    server {
        listen 80;
        server_name api.oba.az;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.oba.az;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;

        location / {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # Dashboard Server
    server {
        listen 80;
        server_name admin.oba.az;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name admin.oba.az;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        location / {
            limit_req zone=general burst=50;
            proxy_pass http://dashboard;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
    }
}
```

### Deploy

```bash
# Build and start
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# Initialize database
docker-compose -f docker-compose.prod.yml exec backend python scripts/seed_database.py

# Train models
docker-compose -f docker-compose.prod.yml exec backend python scripts/train_models.py

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## Option 2: Kubernetes (GKE/EKS/AKS)

### Kubernetes Manifests

Create `k8s/` directory with manifests:

#### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: oba-production
```

#### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: oba-secrets
  namespace: oba-production
type: Opaque
stringData:
  POSTGRES_PASSWORD: <password>
  REDIS_PASSWORD: <password>
  SECRET_KEY: <secret-key>
```

#### Backend Deployment

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oba-backend
  namespace: oba-production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: oba-backend
  template:
    metadata:
      labels:
        app: oba-backend
    spec:
      containers:
      - name: backend
        image: gcr.io/your-project/oba-backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: oba-secrets
        - configMapRef:
            name: oba-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Service & Ingress

```yaml
# k8s/backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: oba-backend
  namespace: oba-production
spec:
  selector:
    app: oba-backend
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: oba-ingress
  namespace: oba-production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.oba.az
    secretName: oba-tls
  rules:
  - host: api.oba.az
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: oba-backend
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n oba-production
kubectl get services -n oba-production

# View logs
kubectl logs -f deployment/oba-backend -n oba-production
```

---

## Mobile App Deployment

### Android (Google Play)

```bash
cd mobile

# Build release APK
flutter build apk --release

# Build App Bundle (recommended)
flutter build appbundle --release

# Output: build/app/outputs/bundle/release/app-release.aab
```

Upload to Google Play Console.

### iOS (App Store)

```bash
cd mobile

# Build iOS release
flutter build ios --release

# Open Xcode
open ios/Runner.xcworkspace
```

Archive and upload via Xcode.

---

## Database Backups

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups/postgres
S3_BUCKET=s3://oba-backups/postgres

# Create backup
docker exec oba_postgres pg_dump -U oba_user oba_db | gzip > $BACKUP_DIR/oba_$DATE.sql.gz

# Upload to S3
aws s3 cp $BACKUP_DIR/oba_$DATE.sql.gz $S3_BUCKET/

# Keep only last 7 days locally
find $BACKUP_DIR -mtime +7 -delete
```

Add to crontab:
```bash
0 2 * * * /path/to/backup.sh
```

---

## Monitoring

### Health Endpoints

```python
# Backend provides:
GET /health        # Basic health check
GET /health/ready  # Readiness (DB + Redis)
GET /health/live   # Liveness
```

### Prometheus Metrics

Add to backend for metrics collection:

```python
# requirements.txt
prometheus-fastapi-instrumentator==6.1.0

# main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### Logging

Configure structured logging:

```python
# app/core/logging.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        })
```

---

## Security Checklist

- [ ] Use HTTPS everywhere
- [ ] Strong passwords (32+ characters)
- [ ] Rate limiting enabled
- [ ] CORS configured for specific domains
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (input sanitization)
- [ ] JWT tokens with short expiry
- [ ] Database access restricted
- [ ] Secrets in environment variables
- [ ] Regular security updates

---

## Scaling Considerations

### Horizontal Scaling

- Backend: Stateless, scale horizontally
- Dashboard: Single instance usually sufficient
- Database: Consider read replicas
- Redis: Cluster mode for high availability

### Performance Optimization

1. **Database**
   - Add indexes for common queries
   - Connection pooling (SQLAlchemy pool)
   - Query optimization

2. **Caching**
   - Redis for session/API cache
   - CDN for static assets

3. **Backend**
   - Async endpoints
   - Background tasks for ML inference
   - Gunicorn with multiple workers

---

## Rollback Procedure

```bash
# List previous deployments
docker-compose -f docker-compose.prod.yml ps

# Rollback to previous image
docker-compose -f docker-compose.prod.yml down
docker tag oba-backend:latest oba-backend:rollback
docker tag oba-backend:previous oba-backend:latest
docker-compose -f docker-compose.prod.yml up -d

# Kubernetes rollback
kubectl rollout undo deployment/oba-backend -n oba-production
```

---

## Support

For deployment issues:
- Email: devops@oba.az
- Documentation: https://docs.oba.az/deployment
