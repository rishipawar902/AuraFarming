/**
 * API Service for handling HTTP requests to the backend
 */

import axios from 'axios';
import toast from 'react-hot-toast';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle different error scenarios
    if (error.response) {
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user_data');
          window.location.href = '/login';
          toast.error('Session expired. Please login again.');
          break;
          
        case 403:
          toast.error('Access forbidden');
          break;
          
        case 404:
          // Don't show toast for expected 404s like missing farm profile
          const url = error.config?.url || '';
          if (!url.includes('/farms/profile') && !url.includes('/farms/crop-history')) {
            toast.error('Resource not found');
          }
          break;
          
        case 500:
          toast.error('Server error. Please try again later.');
          break;
          
        default:
          toast.error(data?.error || 'An error occurred');
      }
    } else if (error.request) {
      // Network error
      toast.error('Network error. Please check your connection.');
    } else {
      // Other error
      toast.error('An unexpected error occurred');
    }
    
    return Promise.reject(error);
  }
);

export class ApiService {
  // Authentication endpoints
  static async login(credentials) {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data;
  }
  
  static async register(userData) {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  }
  
  static async logout() {
    const response = await apiClient.post('/auth/logout');
    return response.data;
  }
  
  static async getCurrentUser() {
    const response = await apiClient.get('/auth/me');
    return response.data;
  }
  
  // Farm management endpoints
  static async createFarmProfile(farmData) {
    const response = await apiClient.post('/farms/profile', farmData);
    return response.data;
  }
  
  static async getFarmProfile() {
    const response = await apiClient.get('/farms/profile');
    return response.data;
  }
  
  static async addCropHistory(cropData) {
    const response = await apiClient.post('/farms/crop-history', cropData);
    return response.data;
  }
  
  static async getCropHistory() {
    const response = await apiClient.get('/farms/crop-history');
    return response.data;
  }
  
  // Crop recommendations endpoints
  static async getCropRecommendations(requestData) {
    const response = await apiClient.post('/crops/recommend', requestData);
    return response.data;
  }
  
  // ML-powered crop recommendations
  static async getMLCropRecommendations(requestData) {
    const response = await apiClient.post('/crops/ml/recommend', requestData);
    return response.data;
  }
  
  // ML yield prediction
  static async predictYield(requestData) {
    const response = await apiClient.post('/crops/ml/yield-prediction', requestData);
    return response.data;
  }
  
  // ML model information
  static async getMLModelInfo() {
    const response = await apiClient.get('/crops/ml/model-info');
    return response.data;
  }
  
  // Crop insights
  static async getCropInsights(cropName) {
    const response = await apiClient.get(`/crops/ml/crop-insights/${cropName}`);
    return response.data;
  }
  
  static async getCropRotation(requestData) {
    const response = await apiClient.post('/crops/rotation', requestData);
    return response.data;
  }
  
  static async getPopularCrops() {
    const response = await apiClient.get('/crops/popular');
    return response.data;
  }
  
  static async getSuitableCrops(district) {
    const response = await apiClient.get(`/crops/suitable/${district}`);
    return response.data;
  }
  
  // Weather endpoints - EMERGENCY DISABLED
  static async getCurrentWeather(farmId) {
    const response = await apiClient.get(`/weather/current/${farmId}`, {
      headers: {
        'Cache-Control': 'max-age=1800' // 30 minutes cache
      }
    });
    return response.data;
  }
  
  static async getWeatherForecast(farmId, days = 7) {
    // Validate and clamp days to supported range
    const validDays = Math.max(1, Math.min(14, days));
    
    const response = await apiClient.get(`/weather/forecast/${farmId}?days=${validDays}`, {
      headers: {
        'Cache-Control': 'max-age=3600' // 1 hour cache
      }
    });
    return response.data;
  }
  
  static async getWeatherAlerts(farmId) {
    const response = await apiClient.get(`/weather/alerts/${farmId}`);
    return response.data;
  }
  
  static async getMLEnhancedWeather(farmId) {
    const response = await apiClient.get(`/weather/ml-enhanced/${farmId}`);
    return response.data;
  }
  
  static async getSeasonalPatterns(district) {
    const response = await apiClient.get(`/weather/seasonal/${district}`);
    return response.data;
  }
  
  // Direct weather API for coordinates (when farm location is available)
  static async getWeatherByCoordinates(latitude, longitude) {
    const response = await apiClient.get(`/weather/current?lat=${latitude}&lng=${longitude}`);
    return response.data;
  }
  
  static async getForecastByCoordinates(latitude, longitude, days = 7) {
    // Validate and clamp days to supported range
    const validDays = Math.max(1, Math.min(14, days));
    
    const response = await apiClient.get(`/weather/forecast?lat=${latitude}&lng=${longitude}&days=${validDays}`);
    return response.data;
  }
  
  // Market endpoints
  static async getMandiPrices(district, crop = null) {
    const url = crop 
      ? `/market/prices/${district}?crop=${crop}`
      : `/market/prices/${district}`;
    const response = await apiClient.get(url);
    return response.data;
  }
  
  static async getPriceTrends(crop, days = 30) {
    const response = await apiClient.get(`/market/trends/${crop}?days=${days}`);
    return response.data;
  }
  
  static async getPriceForecast(crop) {
    const response = await apiClient.get(`/market/forecast/${crop}`);
    return response.data;
  }
  
  static async getBestMarkets(crop, originDistrict) {
    const response = await apiClient.get(`/market/best-markets/${crop}?origin_district=${originDistrict}`);
    return response.data;
  }
  
  static async getMarketDemand(district) {
    const response = await apiClient.get(`/market/demand/${district}`);
    return response.data;
  }

  // Analytics endpoints
  static async getPriceTrends(crop, days = 30) {
    const response = await apiClient.get(`/market/trends/${crop}?days=${days}`);
    return response.data;
  }

  static async getMarketAnalytics(district, timeframe = 30) {
    const response = await apiClient.get(`/market/analytics/${district}?timeframe=${timeframe}`);
    return response.data;
  }

  // Finance endpoints
  static async getFinancialRecommendations() {
    const response = await apiClient.get('/finance/recommendations');
    return response.data;
  }
  
  static async getPmKisanStatus() {
    const response = await apiClient.get('/finance/pm-kisan/status');
    return response.data;
  }
  
  static async getAgricultureLoans() {
    const response = await apiClient.get('/finance/loans/agriculture');
    return response.data;
  }
  
  static async getCropInsurance() {
    const response = await apiClient.get('/finance/insurance/crop');
    return response.data;
  }
  
  static async getSubsidies() {
    const response = await apiClient.get('/finance/subsidies');
    return response.data;
  }
  
  static async calculateProjectedIncome(crop, area) {
    const response = await apiClient.post('/finance/calculate-income', { crop, area });
    return response.data;
  }
  
  // Sustainability endpoints
  static async getSustainabilityScore(farmId) {
    const response = await apiClient.get(`/sustainability/score/${farmId}`);
    return response.data;
  }
  
  static async getCarbonFootprint(farmId) {
    const response = await apiClient.get(`/sustainability/carbon-footprint/${farmId}`);
    return response.data;
  }
  
  static async getWaterEfficiency(farmId) {
    const response = await apiClient.get(`/sustainability/water-efficiency/${farmId}`);
    return response.data;
  }
  
  static async getSoilHealth(farmId) {
    const response = await apiClient.get(`/sustainability/soil-health/${farmId}`);
    return response.data;
  }
  
  static async getSustainabilityRecommendations(farmId) {
    const response = await apiClient.get(`/sustainability/recommendations/${farmId}`);
    return response.data;
  }
  
  // Market endpoints
  static async getMandiPrices(district, crop = null) {
    const url = crop 
      ? `/market/prices/${district}?crop=${encodeURIComponent(crop)}`
      : `/market/prices/${district}`;
    const response = await apiClient.get(url);
    return response.data;
  }
  
  static async getPriceTrends(crop, days = 30) {
    const response = await apiClient.get(`/market/trends/${crop}?days=${days}`);
    return response.data;
  }
  
  static async getPriceForecast(crop) {
    const response = await apiClient.get(`/market/forecast/${crop}`);
    return response.data;
  }
  
  static async getBestMarkets(crop, originDistrict) {
    const response = await apiClient.get(`/market/best-markets/${crop}?origin_district=${originDistrict}`);
    return response.data;
  }
  
  static async getMarketDemand(district) {
    const response = await apiClient.get(`/market/demand/${district}`);
    return response.data;
  }
  
  static async getPotentialBuyers(crop, district = null) {
    const url = district 
      ? `/market/buyers/${crop}?district=${district}`
      : `/market/buyers/${crop}`;
    const response = await apiClient.get(url);
    return response.data;
  }
  
  // Admin endpoints
  static async getAdminStats() {
    const response = await apiClient.get('/admin/stats');
    return response.data;
  }
  
  static async getCropAdoptionData() {
    const response = await apiClient.get('/admin/crop-adoption');
    return response.data;
  }
  
  static async getDistrictWiseData() {
    const response = await apiClient.get('/admin/district-wise');
    return response.data;
  }
  
  static async getMLPerformanceMetrics() {
    const response = await apiClient.get('/admin/ml-performance');
    return response.data;
  }
}

export default ApiService;