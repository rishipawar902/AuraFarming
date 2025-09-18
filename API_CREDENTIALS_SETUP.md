# API Credentials Setup Guide

## Overview
Your AuraFarming platform now has **REAL API integration** capabilities for all three government data sources. Follow this guide to enable live data scraping.

## 🚀 Current Status

### ✅ Implemented Real API Integration
- **AGMARKNET**: Enhanced web scraper with ASP.NET session handling *(No API key needed)*
- **Government Portal**: Real data.gov.in API integration
- **eNAM**: Real National Agriculture Market API integration

### 🔧 API Credentials Required

#### 1. Data.gov.in API Key (Government Portal)
**Step 1**: Visit [data.gov.in](https://data.gov.in/)
**Step 2**: Create free account and request API access
**Step 3**: Navigate to "Developer" section
**Step 4**: Generate API key for agricultural datasets

**Environment Variable**:
```bash
DATA_GOV_IN_API_KEY=your_api_key_here
```

**Available Datasets**:
- Agricultural Marketing Division prices
- Market arrival data
- State-wise commodity prices
- Daily market reports

#### 2. eNAM API Credentials
**Step 1**: Visit [eNAM Portal](https://enam.gov.in/)
**Step 2**: Register as a business/developer
**Step 3**: Apply for API access through developer portal
**Step 4**: Obtain API Key and Secret

**Environment Variables**:
```bash
ENAM_API_KEY=your_enam_api_key
ENAM_API_SECRET=your_enam_api_secret
```

**Available APIs**:
- Market prices by commodity
- Daily arrival data
- Trade transactions
- Market-wise data for Jharkhand

#### 3. AGMARKNET (No Credentials Needed)
- ✅ **Already Active**: Uses enhanced web scraping
- Real-time data from [agmarknet.gov.in](https://agmarknet.gov.in/)
- ASP.NET session handling with ViewState management
- No API key required

## 🔧 Environment Setup

### Add to `.env` file:
```bash
# Existing variables
WEATHER_API_KEY=your_weather_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# New API credentials for real data
DATA_GOV_IN_API_KEY=your_data_gov_key
ENAM_API_KEY=your_enam_key
ENAM_API_SECRET=your_enam_secret
```

### Backend Configuration:
Add to `backend/app/core/config.py`:
```python
# API Credentials
DATA_GOV_IN_API_KEY: Optional[str] = None
ENAM_API_KEY: Optional[str] = None  
ENAM_API_SECRET: Optional[str] = None
```

## 🧪 Testing Real Data Integration

### 1. Test Without Credentials (Fallback Mode)
```bash
cd backend
python -m pytest tests/test_real_api_integration.py
```

### 2. Test With Real Credentials
```bash
# After adding API keys to .env
python -c "
from app.services.multi_source_market_service import MultiSourceMarketService
import asyncio

async def test():
    service = MultiSourceMarketService()
    data = await service.get_market_data('Ranchi', 'Rice')
    print(data)

asyncio.run(test())
"
```

## 📊 Real Data Flow

### With API Credentials:
```
Request → Real Government API → Live Data → Response
```

### Without API Credentials:
```  
Request → Fallback System → Professional Simulation → Response
```

## 🎯 Expected Benefits

### Real Data Integration:
- **Live market prices** from 3 government sources
- **Cross-source validation** for accuracy
- **Confidence scoring** based on data agreement
- **Automatic fallback** when APIs are unavailable

### Data Sources Coverage:
- **24 Jharkhand districts** mapped to government systems
- **Major agricultural commodities** (Rice, Wheat, Maize, etc.)
- **Daily price updates** from official sources
- **Historical data trends** where available

## 🚨 Important Notes

1. **Gradual Rollout**: Start with one API at a time
2. **Rate Limiting**: Government APIs have usage limits
3. **Fallback Ready**: System works without credentials
4. **Data Quality**: Real APIs provide verified government data

## 📞 Support Contacts

### Government Portal API:
- **Support**: data.gov.in support portal
- **Documentation**: [API docs](https://data.gov.in/help/api)

### eNAM API:
- **Support**: eNAM developer portal
- **Registration**: Business verification required

### AGMARKNET:
- **Status**: ✅ No registration needed
- **Method**: Web scraping (already active)

---

## 🔄 Next Steps

1. **Obtain API credentials** from government portals
2. **Add credentials** to environment variables  
3. **Test integration** with real data
4. **Monitor data quality** and API performance
5. **Deploy** with full real data capabilities

Your system is now **production-ready** with comprehensive real API integration! 🚀
