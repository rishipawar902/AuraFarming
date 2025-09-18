# 🌾 AuraFarming - Smart Agriculture Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-009688.svg)](https://fastapi.tiangolo.com/)

> **AI-Powered Crop Recommendation System for Smart Agriculture in Jharkhand**
> 
> Built for Smart India Hackathon (SIH) 2025 - Empowering farmers with data-driven agricultural insights and sustainable farming practices.

## 🚀 Overview

AuraFarming is an innovative agricultural technology platform that leverages artificial intelligence and machine learning to provide farmers with intelligent crop recommendations, weather forecasting, market insights, and comprehensive farm management tools. Designed specifically for the agricultural landscape of Jharkhand, India, this platform aims to maximize crop yields while promoting sustainable farming practices.

### 🎯 Key Features

- **🤖 AI-Powered Crop Recommendations** - Machine learning models trained on soil, climate, and regional data
- **🌡️ Real-time Weather Monitoring** - Integrated weather forecasting with agricultural insights
- **🧠 Smart Advisory System** - Seasonal agricultural guidance and risk assessment
- **📈 Market Intelligence** - Real-time price tracking and market trends
- **💰 Financial Planning Tools** - Crop cost analysis and profit optimization
- **🌱 Sustainability Metrics** - Environmental impact tracking and eco-friendly practices
- **📱 Progressive Web App** - Offline capabilities for remote farming areas
- **🏢 Admin Dashboard** - Comprehensive farm management and analytics

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React PWA)   │◄──►│   (FastAPI)     │◄──►│   (Supabase)    │
│                 │    │                 │    │                 │
│ • React 18      │    │ • Python 3.9+  │    │ • PostgreSQL    │
│ • TailwindCSS   │    │ • FastAPI       │    │ • Real-time     │
│ • React Query   │    │ • ML Models     │    │ • Row Level     │
│ • PWA Features  │    │ • XGBoost       │    │   Security      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Frontend
- **Framework**: React 18 with modern hooks
- **Styling**: TailwindCSS for responsive design
- **State Management**: TanStack Query (React Query)
- **Routing**: React Router v6
- **Icons**: Heroicons v2
- **PWA**: Service Workers with Workbox
- **Notifications**: React Hot Toast

### Backend
- **Framework**: FastAPI 0.116+
- **Language**: Python 3.9+
- **Authentication**: JWT with python-jose
- **Database ORM**: Supabase Python Client
- **ML Framework**: XGBoost, Scikit-learn
- **Data Processing**: Pandas, NumPy
- **API Documentation**: Automatic OpenAPI/Swagger

### Database & Infrastructure
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **Real-time**: Supabase Realtime
- **Storage**: Supabase Storage
- **Deployment**: Docker-ready configuration

### Machine Learning
- **Crop Recommendation**: XGBoost ensemble models
- **Soil Analysis**: Advanced feature engineering
- **Weather Integration**: Historical and forecast data analysis
- **Market Prediction**: Time-series analysis

## � Quick Start

### Prerequisites
- **Node.js** 16+ and npm
- **Python** 3.9+
- **Git**
- **Supabase Account** (for database)

### 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rishipawar902/AuraFarming.git
   cd AuraFarming
   ```

2. **Backend Setup**
   ```bash
   cd backend
   
   # Create virtual environment
   python -m venv .venv
   
   # Activate virtual environment
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Setup environment variables
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   
   # Install dependencies
   npm install
   
   # Setup environment variables
   cp .env .env.local
   # Edit .env.local with your configuration
   ```

4. **Database Setup**
   ```bash
   # Run the Supabase schema
   # Execute the SQL files in backend/ directory:
   # - supabase_schema.sql (complete schema)
   # - supabase_tables_only.sql (tables only)
   ```

### 🚀 Running the Application

1. **Start the Backend**
   ```bash
   cd backend
   python main.py
   # API will be available at http://localhost:8000
   # API Documentation: http://localhost:8000/docs
   ```

2. **Start the Frontend**
   ```bash
   cd frontend
   npm start
   # Application will be available at http://localhost:3000
   ```

## � Features Overview

### 🌾 Crop Recommendation System
- **AI-driven recommendations** based on soil parameters, climate data, and regional patterns
- **Multi-model ensemble** using XGBoost and advanced feature engineering
- **Seasonal optimization** for maximum yield and profitability
- **Soil health analysis** with actionable insights

### 🌤️ Weather Intelligence
- **Real-time weather data** integration
- **7-day forecasting** with agricultural focus
- **Weather-based advisories** for farming activities
- **Climate risk assessment** for crop planning

### 🧠 Smart Advisory System
- **Seasonal guidance** for crop management
- **Pest and disease alerts** based on weather patterns
- **Irrigation recommendations** based on soil moisture and weather
- **Harvest timing optimization**

### 📈 Market Intelligence
- **Real-time price tracking** for major crops
- **Market trend analysis** and forecasting
- **Profit optimization** recommendations
- **Supply chain insights**

### 💰 Financial Management
- **Cost-benefit analysis** for different crops
- **Budget planning tools** for farming seasons
- **ROI calculations** and profit projections
- **Government scheme information** and eligibility

### 🌱 Sustainability Tracking
- **Carbon footprint calculation** for farming practices
- **Sustainable farming recommendations**
- **Water usage optimization**
- **Soil health monitoring**

## 📊 API Documentation

The backend provides a comprehensive REST API with the following endpoints:

### Core Services
- **Authentication**: `/api/v1/auth/*` - User registration, login, JWT management
- **Farm Management**: `/api/v1/farms/*` - Farm profiles and management
- **Crop Services**: `/api/v1/crops/*` - Crop recommendations and analysis
- **Weather Services**: `/api/v1/weather/*` - Weather data and forecasting
- **Market Data**: `/api/v1/market/*` - Price tracking and market insights
- **Financial Services**: `/api/v1/finance/*` - Cost analysis and financial planning
- **Smart Advisory**: `/api/v1/smart-advisory/*` - AI-powered farming guidance
- **Sustainability**: `/api/v1/sustainability/*` - Environmental impact tracking
- **Admin Dashboard**: `/api/v1/admin/*` - Administrative tools and analytics

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🔒 Security Features

- **JWT Authentication** with secure token management
- **Row Level Security** in Supabase for data protection
- **CORS Configuration** for secure cross-origin requests
- **Input Validation** with Pydantic models
- **Error Handling** with comprehensive logging
- **Rate Limiting** to prevent API abuse

## 📱 Progressive Web App Features

- **Offline Functionality** for remote farming areas
- **Push Notifications** for important alerts
- **Background Sync** for data synchronization
- **Responsive Design** for mobile and desktop
- **Fast Loading** with service worker caching
- **Installable** on mobile devices

## 🧪 Testing & Development

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Development Tools
- **Backend**: FastAPI automatic reload with `uvicorn --reload`
- **Frontend**: React hot reload with Create React App
- **API Testing**: Swagger UI for interactive testing
- **Database**: Supabase dashboard for data management

## 📈 Performance Optimization

- **Query Optimization** with TanStack Query caching
- **Image Optimization** with lazy loading
- **Code Splitting** for faster initial load
- **Service Worker** for offline performance
- **Database Indexing** for fast data retrieval
- **API Response Caching** to reduce server load

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Manual Deployment
1. **Backend**: Deploy to cloud platforms like Heroku, AWS, or DigitalOcean
2. **Frontend**: Deploy to Vercel, Netlify, or AWS S3
3. **Database**: Supabase provides hosted PostgreSQL

## 🤝 Contributing

We welcome contributions to AuraFarming! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and test thoroughly
4. Commit with descriptive messages
5. Push to your fork and submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- **Smart India Hackathon 2025** for the opportunity to solve real-world agricultural challenges
- **Jharkhand Agriculture Department** for domain expertise and requirements
- **Open Source Community** for the amazing tools and libraries used in this project

## 📞 Contact & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/rishipawar902/AuraFarming/issues)
- **Documentation**: [Project Wiki](https://github.com/rishipawar902/AuraFarming/wiki)
- **Team**: SIH 2025 Team - AuraFarming

---

<div align="center">

**🌾 Built with ❤️ for farmers and sustainable agriculture 🌱**

[⭐ Star this repository](https://github.com/rishipawar902/AuraFarming) | [🐛 Report Bug](https://github.com/rishipawar902/AuraFarming/issues) | [✨ Request Feature](https://github.com/rishipawar902/AuraFarming/issues)

</div>

---

**Built with ❤️ for farmers in Jharkhand**