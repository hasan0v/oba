# OBA Smart Assistant

🛒 AI-Powered Retail Shopping Platform for Azerbaijan Market

<p align="center">
  <img src="docs/images/logo.png" alt="OBA Logo" width="200"/>
</p>

## 📋 Overview

OBA Smart Assistant is a comprehensive retail shopping platform that combines mobile commerce with artificial intelligence to deliver personalized shopping experiences. Built specifically for the Azerbaijan market with full Azerbaijani language support.

### 🌟 Key Features

| Feature | Description |
|---------|-------------|
| 🔐 **JWT Authentication** | Secure user registration and login with token-based auth |
| 📦 **Product Catalog** | Full-featured catalog with categories, search, and filters |
| 🤖 **AI Recommendations** | SVD-based collaborative filtering for personalized suggestions |
| 🎤 **Voice Search** | Azerbaijani voice search support via speech-to-text |
| 🛒 **Smart Cart** | Intelligent cart with savings calculation and free delivery tracking |
| 🏆 **Gamification** | Points system with Bronze/Silver/Gold/Platinum tiers and badges |
| ⚠️ **Complaint Classification** | AI-powered automatic complaint categorization |
| 📈 **Demand Forecasting** | Prophet-based time series prediction for inventory management |
| 📊 **Analytics Dashboard** | Real-time Streamlit dashboard for business insights |
| 🔔 **Push Notifications** | Firebase-based push notifications for orders and promotions |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Mobile App (Flutter)                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Provider State │ Voice Search │ Firebase Messaging  │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Auth API    │  │ Product API │  │ ML Engines          │  │
│  │ Orders API  │  │ Cart API    │  │ - Recommendations   │  │
│  │ Complaints  │  │ Analytics   │  │ - Sentiment         │  │
│  │ Users API   │  │ Gamification│  │ - Forecasting       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
┌────────────▼────────────┐    ┌──────────────▼───────────────┐
│     PostgreSQL          │    │           Redis              │
│  - Users, Products      │    │  - Session Cache             │
│  - Orders, Reviews      │    │  - Rate Limiting             │
│  - Complaints           │    │  - Temporary Data            │
└─────────────────────────┘    └──────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Flutter 3.0+
- Node.js 18+ (optional, for tooling)

### 1. Clone & Setup Environment

```bash
git clone https://github.com/your-org/oba-smart-assistant.git
cd oba-smart-assistant

# Copy environment file
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start Services with Docker

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 3. Generate Sample Data & Train Models

```bash
# Enter backend container
docker-compose exec backend bash

# Generate synthetic data
python scripts/generate_data.py

# Seed database
python scripts/seed_database.py

# Train ML models
python scripts/train_models.py
```

### 4. Access Services

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:8000 | FastAPI backend |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Dashboard | http://localhost:8501 | Streamlit analytics |

### 5. Run Mobile App

```bash
cd mobile
flutter pub get
flutter run
```

## 📁 Project Structure

```
oba-smart-assistant/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core config & security
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── utils/          # Utility functions
│   ├── ml/                 # Machine learning
│   │   ├── models/         # Trained models
│   │   ├── recommendation.py
│   │   ├── sentiment.py
│   │   ├── complaint.py
│   │   └── forecast.py
│   ├── scripts/            # Data & training scripts
│   └── requirements.txt
├── mobile/                  # Flutter mobile app
│   ├── lib/
│   │   ├── config/         # App configuration
│   │   ├── models/         # Data models
│   │   ├── providers/      # State management
│   │   ├── screens/        # UI screens
│   │   ├── services/       # API & auth services
│   │   └── widgets/        # Reusable widgets
│   └── pubspec.yaml
├── dashboard/               # Streamlit dashboard
│   └── app.py
├── data/                    # Generated data files
├── docs/                    # Documentation
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | - |
| `SECRET_KEY` | JWT signing key | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | 30 |
| `ENVIRONMENT` | development/staging/production | development |

### Mobile App Configuration

Edit `mobile/lib/config/app_config.dart`:

```dart
static const String apiBaseUrl = 'http://your-api-url';
static const bool enableVoiceSearch = true;
static const bool enablePushNotifications = true;
```

## 🧪 API Documentation

### Authentication

```bash
# Register
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "Test User"
}

# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Products

```bash
# Get products
GET /api/v1/products?page=1&limit=20&category_id=1

# Search products
GET /api/v1/products/search?q=telefon

# Get recommendations
GET /api/v1/products/recommendations
```

### Orders

```bash
# Create order
POST /api/v1/orders
{
  "items": [{"product_id": 1, "quantity": 2}],
  "shipping_address_id": 1
}

# Get user orders
GET /api/v1/orders
```

Full API documentation available at `/docs` when running the backend.

## 🤖 Machine Learning Models

### 1. Recommendation Engine (SVD)
- **Algorithm**: Singular Value Decomposition
- **Library**: scikit-surprise
- **Training**: User-product interaction matrix
- **Fallback**: Popular products by category

### 2. Sentiment Analyzer
- **Model**: BERT multilingual
- **Library**: transformers (HuggingFace)
- **Languages**: Azerbaijani, English, Russian
- **Output**: Positive/Neutral/Negative + confidence

### 3. Complaint Classifier
- **Algorithm**: TF-IDF + Logistic Regression
- **Categories**: Product, Service, Delivery, Pricing, Other
- **Priority**: Auto-detection based on keywords

### 4. Demand Forecaster
- **Algorithm**: Prophet time series
- **Features**: Trend, weekly/yearly seasonality
- **Output**: 30-day demand forecast with intervals

## 📊 Dashboard Features

- **KPI Overview**: Sales, orders, users, average order value
- **Sales Analytics**: Trends, top products, category distribution
- **User Analytics**: Registration trends, tier distribution
- **Product Management**: Stock alerts, ratings analysis
- **Complaint Management**: Status tracking, priority filtering
- **Demand Forecast**: Product-level predictions, stock recommendations
- **Sentiment Analysis**: Review sentiment distribution, live testing

## 🛠️ Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

### Mobile Development

```bash
cd mobile

# Get dependencies
flutter pub get

# Run tests
flutter test

# Build APK
flutter build apk --release

# Build iOS
flutter build ios --release
```

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Mobile tests
cd mobile
flutter test
```

## 📱 Mobile App Screenshots

<p align="center">
  <img src="docs/images/home.png" width="200"/>
  <img src="docs/images/products.png" width="200"/>
  <img src="docs/images/cart.png" width="200"/>
  <img src="docs/images/profile.png" width="200"/>
</p>

## 🚢 Deployment

### Production with Docker

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment Options

- **AWS**: ECS/EKS + RDS + ElastiCache
- **GCP**: Cloud Run + Cloud SQL + Memorystore
- **Azure**: AKS + Azure Database + Azure Cache

## 📈 Roadmap

### Phase 1 (MVP) ✅
- [x] User authentication
- [x] Product catalog
- [x] Shopping cart
- [x] Order management
- [x] Basic recommendations
- [x] Admin dashboard

### Phase 2
- [ ] Payment integration (MilliÖn, PAŞA Pay)
- [ ] Real-time order tracking
- [ ] Multi-language support
- [ ] Social login (Google, Facebook)
- [ ] Store locator with maps

### Phase 3
- [ ] AR product preview
- [ ] Chatbot integration
- [ ] Loyalty program expansion
- [ ] Marketplace features
- [ ] Advanced analytics

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 📞 Support

- **Email**: support@oba.az
- **Documentation**: [docs.oba.az](https://docs.oba.az)
- **Issues**: [GitHub Issues](https://github.com/your-org/oba-smart-assistant/issues)

---

<p align="center">
  Made with ❤️ in Azerbaijan
</p>
