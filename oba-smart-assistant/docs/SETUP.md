# OBA Smart Assistant - Setup Guide

This guide walks you through setting up the OBA Smart Assistant development environment.

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Docker | 20.10+ | Container runtime |
| Docker Compose | 2.0+ | Multi-container orchestration |
| Python | 3.11+ | Backend development |
| Flutter | 3.0+ | Mobile app development |
| Git | 2.30+ | Version control |

### Optional Software

| Software | Purpose |
|----------|---------|
| VS Code | Recommended IDE |
| Android Studio | Android development & emulator |
| Xcode | iOS development (macOS only) |
| Postman | API testing |
| DBeaver | Database management |

---

## Quick Setup (Docker)

The fastest way to get started:

```bash
# 1. Clone repository
git clone https://github.com/your-org/oba-smart-assistant.git
cd oba-smart-assistant

# 2. Copy environment file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Generate sample data
docker-compose exec backend python scripts/generate_data.py

# 5. Seed database
docker-compose exec backend python scripts/seed_database.py

# 6. Train ML models
docker-compose exec backend python scripts/train_models.py
```

Services will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Dashboard: http://localhost:8501

---

## Manual Setup

### 1. Database Setup

#### PostgreSQL

```bash
# Using Docker
docker run -d \
  --name oba_postgres \
  -e POSTGRES_USER=oba_user \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=oba_db \
  -p 5432:5432 \
  postgres:15-alpine

# Or install locally (Ubuntu)
sudo apt install postgresql postgresql-contrib
sudo -u postgres createuser oba_user
sudo -u postgres createdb oba_db -O oba_user
```

#### Redis

```bash
# Using Docker
docker run -d \
  --name oba_redis \
  -p 6379:6379 \
  redis:7-alpine redis-server --requirepass your_redis_password

# Or install locally (Ubuntu)
sudo apt install redis-server
sudo systemctl enable redis-server
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://oba_user:your_password@localhost:5432/oba_db"
export REDIS_URL="redis://:your_redis_password@localhost:6379/0"
export SECRET_KEY="your-secret-key-at-least-32-characters"

# Run migrations (if using Alembic)
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### 3. Generate Data & Train Models

```bash
# Make sure virtual environment is activated
cd backend

# Generate synthetic data
python scripts/generate_data.py
# Creates CSV files in ../data/ directory

# Seed database with generated data
python scripts/seed_database.py
# Populates PostgreSQL tables

# Train ML models
python scripts/train_models.py
# Creates model files in ml/models/
```

### 4. Dashboard Setup

```bash
cd dashboard

# Create virtual environment (optional, can use backend's)
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit dashboard
streamlit run app.py --server.port 8501
```

### 5. Mobile App Setup

```bash
cd mobile

# Get Flutter dependencies
flutter pub get

# Check Flutter setup
flutter doctor

# Run on connected device/emulator
flutter run

# Or specify device
flutter run -d chrome  # Web
flutter run -d android # Android emulator
flutter run -d ios     # iOS simulator
```

---

## Environment Configuration

### Required Environment Variables

Create `.env` file in project root:

```bash
# Database
POSTGRES_USER=oba_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=oba_db
DATABASE_URL=postgresql://oba_user:secure_password_here@localhost:5432/oba_db

# Redis
REDIS_PASSWORD=redis_password_here
REDIS_URL=redis://:redis_password_here@localhost:6379/0

# JWT
SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8501
```

### Mobile App Configuration

Edit `mobile/lib/config/app_config.dart`:

```dart
class AppConfig {
  static const String apiBaseUrl = 'http://10.0.2.2:8000'; // Android emulator
  // static const String apiBaseUrl = 'http://localhost:8000'; // iOS simulator
  // static const String apiBaseUrl = 'https://api.oba.az'; // Production
  
  static const bool enableVoiceSearch = true;
  static const bool enablePushNotifications = false; // Set true with Firebase
}
```

---

## IDE Setup

### VS Code Extensions

Recommended extensions:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "Dart-Code.dart-code",
    "Dart-Code.flutter",
    "ms-azuretools.vscode-docker",
    "mtxr.sqltools",
    "mtxr.sqltools-driver-pg"
  ]
}
```

### VS Code Settings

```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "[dart]": {
    "editor.formatOnSave": true,
    "editor.selectionHighlight": false,
    "editor.suggest.snippetsPreventQuickSuggestions": false,
    "editor.suggestSelection": "first",
    "editor.tabCompletion": "onlySnippets",
    "editor.wordBasedSuggestions": "off"
  }
}
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker ps | grep postgres
# or
systemctl status postgresql

# Test connection
psql -h localhost -U oba_user -d oba_db

# Check logs
docker logs oba_postgres
```

### Backend Won't Start

```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check for port conflicts
lsof -i :8000
# Kill conflicting process
kill -9 <PID>
```

### Flutter Build Errors

```bash
# Clean build
flutter clean
flutter pub get

# Check Flutter installation
flutter doctor -v

# Update Flutter
flutter upgrade
```

### ML Model Training Fails

```bash
# Check memory (Prophet needs ~2GB)
free -h

# Install specific versions
pip install prophet==1.1.4
pip install scikit-surprise==1.1.3

# Run with verbose output
python scripts/train_models.py --verbose
```

### Redis Connection Issues

```bash
# Test Redis connection
redis-cli -a your_redis_password ping
# Should return: PONG

# Check Redis logs
docker logs oba_redis
```

---

## Verification

### 1. API Health Check

```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "database": "connected", "redis": "connected"}
```

### 2. API Documentation

Open http://localhost:8000/docs in browser

### 3. Dashboard

Open http://localhost:8501 in browser

### 4. Mobile App

```bash
cd mobile
flutter test
flutter run
```

---

## Next Steps

After setup:

1. **Explore API**: Visit http://localhost:8000/docs
2. **Login to Dashboard**: http://localhost:8501
3. **Run Mobile App**: `flutter run`
4. **Default Admin**: admin@oba.az / admin123

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).
