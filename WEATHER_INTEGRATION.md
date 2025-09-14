# AuraFarming Weather Integration Setup

## Overview
AuraFarming now includes real-time weather data integration using the **WeatherAPI.com** service. This enhances both the user interface and ML model predictions with live weather data.

## Features
✅ **Real-time Weather Data**: Current conditions, forecasts, and weather alerts  
✅ **ML Model Enhancement**: Weather data automatically improves crop recommendations  
✅ **Fallback System**: Mock data when API is unavailable  
✅ **Smart Caching**: Efficient API usage within generous rate limits  
✅ **Historical Data**: 7-day historical weather (free tier)  
✅ **14-day Forecasts**: Extended weather predictions  

## Setup Instructions

### 1. Get WeatherAPI.com API Key

1. Visit [WeatherAPI.com](https://www.weatherapi.com/signup.aspx)
2. Sign up for a free account
3. Navigate to your dashboard
4. Copy your API key

**Free Tier Benefits:**
- **1 million API calls per month** (vs 1,000/day with others)
- Real-time weather data
- 14-day weather forecasts
- 7-day historical weather data
- No rate limiting on free tier
- Perfect for production use!

### 2. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```
   WEATHERAPI_KEY=your_actual_api_key_here
   ```

### 3. Test the Integration

Start your FastAPI server and test these endpoints:

```bash
# Get current weather for a farm
GET /api/weather/current/{farm_id}

# Get weather forecast (up to 14 days)
GET /api/weather/forecast/{farm_id}?days=7

# Get ML-enhanced weather data
GET /api/weather/ml-enhanced/{farm_id}

# Get weather alerts
GET /api/weather/alerts/{farm_id}
```

## How Weather Enhances ML Predictions

### Before (Mock Data)
```json
{
  "temperature": 25.0,
  "rainfall": 800.0,
  "humidity": 65
}
```

### After (Real WeatherAPI.com Data)
```json
{
  "current": {
    "temperature": 28.3,
    "rainfall": 12.5,
    "humidity": 78
  },
  "forecast_weekly_avg": {
    "temperature": 26.8,
    "rainfall": 45.2,
    "humidity": 72
  }
}
```

### ML Model Integration

The weather service automatically enhances farm data for ML predictions:

1. **Location-based**: Uses farm GPS coordinates
2. **Real-time**: Current weather conditions from WeatherAPI.com
3. **Predictive**: Weekly forecast averages (up to 14 days)
4. **Historical**: 7-day historical data available
5. **Fallback**: Mock data if API fails

## API Endpoints

### Weather Data
- `GET /api/weather/current/{farm_id}` - Current weather
- `GET /api/weather/forecast/{farm_id}` - Weather forecast (up to 14 days)
- `GET /api/weather/alerts/{farm_id}` - Weather alerts
- `GET /api/weather/ml-enhanced/{farm_id}` - ML-optimized data

### Enhanced ML Recommendations
- `POST /api/ml/recommendations` - Now includes real weather data
- The ML service automatically fetches weather when farm coordinates are provided

## Data Structure

### Current Weather Response (WeatherAPI.com)
```json
{
  "temperature": 28.3,
  "humidity": 78,
  "pressure": 1013,
  "wind_speed": 3.5,
  "wind_direction": 180,
  "description": "partly cloudy",
  "icon": "//cdn.weatherapi.com/weather/64x64/day/116.png",
  "visibility": 10.0,
  "feels_like": 30.1,
  "uv_index": 6,
  "ml_data": {
    "temperature": 28.3,
    "rainfall": 12.5,
    "humidity": 78
  },
  "location": {
    "latitude": 23.3441,
    "longitude": 85.3096,
    "city": "Ranchi",
    "region": "Jharkhand",
    "country": "India"
  },
  "source": "weatherapi"
}
```

### Forecast Response
```json
{
  "forecasts": [
    {
      "date": "2024-12-15",
      "temperature_max": 31.2,
      "temperature_min": 18.5,
      "temperature_avg": 24.8,
      "rainfall": 2.3,
      "humidity_avg": 72,
      "description": "partly cloudy",
      "icon": "//cdn.weatherapi.com/weather/64x64/day/116.png",
      "uv_index": 6,
      "wind_speed": 4.2,
      "ml_data": {
        "temperature": 24.8,
        "rainfall": 2.3,
        "humidity": 72
      }
    }
  ]
}
```

## WeatherAPI.com Advantages

### Compared to OpenWeatherMap:
- **1000x more API calls**: 1 million/month vs 1,000/day
- **Better forecasts**: 14 days vs 5 days
- **Historical data**: 7 days free vs paid only
- **More accurate**: Especially for Indian locations
- **Better documentation**: Cleaner API structure
- **No rate limits**: On free tier

### Additional Features:
- Air quality data
- Marine weather
- Bulk API requests
- Weather alerts and warnings
- Astronomy data (sunrise, sunset, moon phases)

## Troubleshooting

### Common Issues

1. **"Using mock weather data" warning**
   - Check your API key in `.env`
   - Ensure key length > 10 characters
   - Verify key is not set to "mock_weatherapi_key"

2. **API rate limit exceeded (unlikely with 1M calls/month)**
   - Monitor usage in WeatherAPI.com dashboard
   - Consider upgrading if needed

3. **Weather data not affecting ML predictions**
   - Ensure farm data includes latitude/longitude
   - Check logs for weather service errors
   - Verify `_enhance_farm_data_with_weather` is being called

### Development Mode

For development without API usage:
```python
# In .env file
WEATHERAPI_KEY=mock_weatherapi_key
```

This will use realistic mock data based on geographic location.

## Production Considerations

1. **API Key Security**: Store in environment variables, never in code
2. **Usage Monitoring**: Track API calls (1M free per month)
3. **Error Handling**: Weather service gracefully falls back to mock data
4. **Caching**: Consider caching for frequently requested data
5. **Historical Training**: Use 7-day free historical data for ML training

## Next Steps

1. **Historical Data**: Use free 7-day historical weather for ML training
2. **Advanced Alerts**: Implement crop-specific weather alerts using WeatherAPI alerts
3. **Air Quality**: Add air quality data for more accurate recommendations
4. **Bulk Requests**: Optimize for multiple farms using bulk API endpoints

## Support

For issues with weather integration:
1. Check logs for weather service errors
2. Verify WeatherAPI.com API key is valid
3. Test endpoints with mock data first
4. Check WeatherAPI.com dashboard for usage stats