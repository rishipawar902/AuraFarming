/**
 * Weather Service for handling weather-related data and formatting
 */

import ApiService from './apiService';

export class WeatherService {
  /**
   * Get current weather for a farm
   */
  static async getCurrentWeatherForFarm(farmId) {
    try {
      console.log('WeatherService: Requesting current weather for farmId:', farmId);
      const response = await ApiService.getCurrentWeather(farmId);
      console.log('WeatherService: Raw API response:', response);
      
      // The response structure is: { success, message, data: { weather data } }
      const weatherData = response.data?.data || response.data;
      console.log('WeatherService: Parsed weather data:', weatherData);
      
      return this.formatWeatherData(weatherData);
    } catch (error) {
      console.error('WeatherService: Error fetching current weather:', error);
      console.log('WeatherService: Falling back to mock data');
      return this.getMockWeatherData();
    }
  }

  /**
   * Get weather forecast for a farm
   */
  static async getForecastForFarm(farmId, days = 7) {
    try {
      const response = await ApiService.getWeatherForecast(farmId, days);
      // The response structure is: { success, message, data: { forecasts, location, ... } }
      // So we need to access response.data.data for the actual forecast data
      const forecastData = response.data?.data || response.data;
      return this.formatForecastData(forecastData);
    } catch (error) {
      console.error('Error fetching weather forecast:', error);
      return this.getMockForecastData(days);
    }
  }

  /**
   * Get ML-enhanced weather data for farming recommendations
   */
  static async getMLEnhancedWeather(farmId) {
    try {
      const response = await ApiService.getMLEnhancedWeather(farmId);
      // The response structure is: { success, message, data: { ml data } }
      return response.data?.data || response.data;
    } catch (error) {
      console.error('Error fetching ML-enhanced weather:', error);
      return null;
    }
  }

  /**
   * Get weather alerts for a farm
   */
  static async getWeatherAlerts(farmId) {
    try {
      const response = await ApiService.getWeatherAlerts(farmId);
      // The response structure is: { success, message, data: [ alerts ] }
      return response.data?.data || response.data;
    } catch (error) {
      console.error('Error fetching weather alerts:', error);
      return [];
    }
  }

  /**
   * Format weather data for consistent UI display
   */
  static formatWeatherData(data) {
    if (!data) return null;

    return {
      temperature: Math.round(data.temperature || 0),
      feelsLike: Math.round(data.feels_like || data.temperature || 0),
      humidity: Math.round(data.humidity || 0),
      pressure: Math.round(data.pressure || 0),
      windSpeed: Math.round((data.wind_speed || 0) * 3.6), // Convert m/s to km/h
      windDirection: data.wind_direction || 0,
      description: data.description || 'Unknown',
      icon: data.icon || this.getDefaultIcon(data.description),
      visibility: Math.round(data.visibility || 0),
      uvIndex: data.uv_index || 0,
      location: data.location || {},
      timestamp: data.timestamp || new Date().toISOString(),
      source: data.source || 'unknown'
    };
  }

  /**
   * Format forecast data for UI display
   */
  static formatForecastData(data) {
    if (!data || !data.forecasts) return [];

    return data.forecasts.map(day => ({
      date: day.date,
      dateFormatted: this.formatDate(day.date),
      temperatureMax: Math.round(day.temperature_max || 0),
      temperatureMin: Math.round(day.temperature_min || 0),
      temperatureAvg: Math.round(day.temperature_avg || 0),
      rainfall: Math.round((day.rainfall || 0) * 10) / 10, // Round to 1 decimal
      humidity: Math.round(day.humidity_avg || 0),
      description: day.description || 'Unknown',
      icon: day.icon || this.getDefaultIcon(day.description),
      uvIndex: day.uv_index || 0,
      windSpeed: Math.round((day.wind_speed || 0) * 3.6), // Convert m/s to km/h
    }));
  }

  /**
   * Get appropriate weather icon based on description
   */
  static getDefaultIcon(description) {
    if (!description) return '☁️';
    
    const desc = description.toLowerCase();
    if (desc.includes('sunny') || desc.includes('clear')) return '☀️';
    if (desc.includes('partly') || desc.includes('partial')) return '⛅';
    if (desc.includes('cloudy') || desc.includes('overcast')) return '☁️';
    if (desc.includes('rain') || desc.includes('shower')) return '🌧️';
    if (desc.includes('storm') || desc.includes('thunder')) return '⛈️';
    if (desc.includes('snow')) return '❄️';
    if (desc.includes('mist') || desc.includes('fog')) return '🌫️';
    
    return '☁️'; // Default
  }

  /**
   * Format date for display
   */
  static formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    });
  }

  /**
   * Get temperature color class based on value
   */
  static getTemperatureColor(temp) {
    if (temp >= 35) return 'text-red-600';
    if (temp >= 25) return 'text-orange-500';
    if (temp >= 15) return 'text-green-600';
    if (temp >= 5) return 'text-blue-500';
    return 'text-blue-700';
  }

  /**
   * Get humidity color class based on value
   */
  static getHumidityColor(humidity) {
    if (humidity >= 80) return 'text-blue-600';
    if (humidity >= 60) return 'text-green-600';
    if (humidity >= 40) return 'text-yellow-600';
    return 'text-red-600';
  }

  /**
   * Get weather condition for farming activities
   */
  static getFarmingCondition(weatherData) {
    if (!weatherData) return { status: 'unknown', message: 'Weather data unavailable' };

    const { temperature, humidity, windSpeed, description } = weatherData;
    const desc = description.toLowerCase();

    // Check for adverse conditions
    if (desc.includes('storm') || desc.includes('thunder')) {
      return { status: 'danger', message: 'Severe weather - avoid outdoor farming activities' };
    }

    if (desc.includes('heavy rain') || windSpeed > 25) {
      return { status: 'warning', message: 'Avoid spraying and harvesting activities' };
    }

    if (temperature > 40) {
      return { status: 'warning', message: 'Very hot - provide extra irrigation and avoid midday work' };
    }

    if (temperature < 5) {
      return { status: 'warning', message: 'Cold weather - protect sensitive crops' };
    }

    // Good conditions
    if (temperature >= 20 && temperature <= 30 && humidity >= 40 && humidity <= 70) {
      return { status: 'good', message: 'Excellent conditions for most farming activities' };
    }

    return { status: 'moderate', message: 'Suitable for farming with normal precautions' };
  }

  /**
   * Generate mock weather data for testing
   */
  static getMockWeatherData() {
    return {
      temperature: 28,
      feelsLike: 31,
      humidity: 65,
      pressure: 1013,
      windSpeed: 12,
      windDirection: 180,
      description: 'Partly cloudy',
      icon: '⛅',
      visibility: 10,
      uvIndex: 6,
      location: {
        city: 'Ranchi',
        region: 'Jharkhand',
        country: 'India'
      },
      timestamp: new Date().toISOString(),
      source: 'mock'
    };
  }

  /**
   * Generate mock forecast data for testing
   */
  static getMockForecastData(days = 7) {
    const forecasts = [];
    const baseTemp = 28;
    
    for (let i = 0; i < days; i++) {
      const date = new Date();
      date.setDate(date.getDate() + i + 1);
      
      const dayTemp = baseTemp + (Math.random() - 0.5) * 6; // ±3°C variation
      
      forecasts.push({
        date: date.toISOString().split('T')[0],
        dateFormatted: this.formatDate(date.toISOString()),
        temperatureMax: Math.round(dayTemp + 5),
        temperatureMin: Math.round(dayTemp - 5),
        temperatureAvg: Math.round(dayTemp),
        rainfall: Math.round(Math.random() * 10 * 10) / 10, // 0-10mm
        humidity: Math.round(60 + Math.random() * 20), // 60-80%
        description: ['Sunny', 'Partly cloudy', 'Cloudy', 'Light rain'][Math.floor(Math.random() * 4)],
        icon: ['☀️', '⛅', '☁️', '🌧️'][Math.floor(Math.random() * 4)],
        uvIndex: Math.round(3 + Math.random() * 5), // 3-8
        windSpeed: Math.round(5 + Math.random() * 15), // 5-20 km/h
      });
    }
    
    return forecasts;
  }

  /**
   * Get weather icon URL from WeatherAPI.com
   */
  static getIconUrl(iconPath) {
    if (!iconPath) return null;
    if (iconPath.startsWith('//')) {
      return `https:${iconPath}`;
    }
    return iconPath;
  }

  /**
   * Check if weather data is fresh (less than 30 minutes old)
   */
  static isDataFresh(timestamp) {
    if (!timestamp) return false;
    const dataTime = new Date(timestamp);
    const now = new Date();
    const diffMinutes = (now - dataTime) / (1000 * 60);
    return diffMinutes < 30;
  }
}

export default WeatherService;