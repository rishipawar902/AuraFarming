# AuraFarming - SIH 2025: AI-Based Crop Recommendation System for Jharkhand

## 🌾 Project Overview

AuraFarming is a production-quality prototype for SIH-2025 that combines **SmartKhet (holistic farm management)** and **KisanMitra (privacy-preserving federated learning)** to provide intelligent crop recommendations for farmers in Jharkhand.

## 🏗️ Architecture

```
AuraFarming/
├── frontend/           # React PWA (Farmer App + Admin Dashboard) ✅ COMPLETED
├── backend/           # FastAPI Backend Services ✅ COMPLETED
├── federated-learning/ # TensorFlow Federated Simulation 🚧 PLANNED
├── docs/              # Documentation & API Specs ✅ COMPLETED
└── deployment/        # Docker & Deployment Configs 🚧 PLANNED
```

## 🔹 Implementation Status

### ✅ COMPLETED - Farmer Progressive Web App
- ✅ React 18 + TypeScript + PWA manifest
- ✅ Offline-first with IndexedDB caching (idb)
- ✅ Authentication (Login/Register pages)
- ✅ Responsive design with Tailwind CSS
- ✅ Farm profile setup with location services
- ✅ Dashboard with weather integration
- ✅ Navigation with React Router
- ✅ Service worker for offline functionality

### ✅ COMPLETED - Admin Dashboard
- ✅ Comprehensive statistics overview
- ✅ Crop adoption rate analysis
- ✅ District-wise performance metrics
- ✅ ML model performance tracking
- ✅ Data export functionality
- ✅ Real-time activity monitoring

### ✅ COMPLETED - Backend Services
- ✅ FastAPI with modular architecture
- ✅ Complete API routes for all features:
  - Authentication (register, login, JWT)
  - Farm management (profiles, crop history)
  - Crop recommendations with ML integration
  - Weather services (current, forecast, alerts)
  - Market prices (mandi data, trends)
  - Financial services (PM-KISAN integration)
  - Sustainability scoring
  - Admin analytics
- ✅ Supabase database integration
- ✅ Mock ML service for recommendations
- ✅ Clean architecture with services layer
- ✅ Error handling and validation

### 🚧 IN PROGRESS - External API Integrations
- 🔄 OpenWeatherMap API integration
- 🔄 Agmarknet mandi price API
- 🔄 Caching and error handling

### 🚧 PLANNED - Federated Learning (KisanMitra)
- ⏳ TensorFlow Federated setup
- ⏳ Differential privacy implementation
- ⏳ Blockchain audit trail
- ⏳ Privacy-preserving ML models

### 🚧 PLANNED - Deployment
- ⏳ Netlify/Vercel frontend deployment
- ⏳ Render backend deployment
- ⏳ Environment configuration
- ⏳ Production optimizations

## 🚀 Tech Stack

- **Frontend**: React + PWA + IndexedDB + Leaflet.js
- **Backend**: FastAPI (Python 3.11) + Pydantic
- **Database**: Supabase (PostgreSQL)
- **ML**: TensorFlow Federated / Flower
- **APIs**: Agmarknet, OpenWeatherMap
- **Deployment**: Netlify/Vercel + Render (Free tier)

## 📊 Database Schema

### Core Tables
- `farmers` - User profiles and authentication
- `farms` - Farm metadata and location data
- `crops_history` - Historical crop and yield data
- `recommendations` - AI-generated crop suggestions
- `audit_logs` - Federated learning audit trail

## 🛠️ Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase account
- OpenWeatherMap API key

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Federated Learning
```bash
cd federated-learning
pip install -r requirements.txt
python federated_simulation.py
```

## 🌍 API Endpoints

- `POST /register` - Farmer registration
- `GET /farm-profile` - Farm data management
- `POST /recommend-crop` - AI crop recommendations
- `GET /crop-rotation` - Rotation optimization
- `GET /mandi-prices` - Market price data
- `GET /weather` - Weather forecasting
- `GET /finance` - Financial recommendations
- `GET /sustainability` - Environmental scoring
- `GET /admin/aggregates` - Dashboard analytics

## 🔐 Security & Privacy

- JWT-based authentication
- Differential privacy for federated learning
- CORS protection
- Environment-based secrets management
- Blockchain-inspired audit logging

## 📈 Sustainability Focus

- Carbon footprint calculation
- Fertilizer efficiency scoring
- Environmental impact assessment
- Sustainable farming recommendations

## 🎯 Demo Flow

1. **Farmer Registration** → Create account with Supabase Auth
2. **Farm Profile Setup** → Add soil type, location, field size
3. **Crop Recommendation** → Get AI-powered suggestions
4. **Market Analysis** → View real-time mandi prices
5. **Weather Planning** → Access 7-day forecasts
6. **Rotation Planning** → Get 2-3 year crop sequences
7. **Admin Insights** → Aggregated analytics dashboard

## 📝 License

Open source - Built for SIH 2025

## 🤝 Contributing

This is a prototype for SIH 2025. For production deployment, ensure proper security audits and compliance with agricultural data regulations.

---

**Built with ❤️ for farmers in Jharkhand**