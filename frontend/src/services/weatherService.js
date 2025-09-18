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
      throw error; // Throw error instead of falling back to mock data
    }
  }

  /**
   * Get weather forecast for a farm
   */
  static async getForecastForFarm(farmId, days = 7) {
    try {
      // Ensure days is within valid range (1-14)
      const validDays = Math.max(1, Math.min(14, days));
      if (validDays !== days) {
        console.warn(`WeatherService: Requested ${days} days, clamped to ${validDays} days`);
      }
      
      const response = await ApiService.getWeatherForecast(farmId, validDays);
      // The response structure is: { success, message, data: { forecasts, location, ... } }
      // So we need to access response.data.data for the actual forecast data
      const forecastData = response.data?.data || response.data;
      return this.formatForecastData(forecastData);
    } catch (error) {
      console.error('Error fetching weather forecast:', error);
      throw error; // Throw error instead of falling back to mock data
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

    // Handle the nested structure from enhanced weather service
    const current = data.current || data;
    
    return {
      temperature: Math.round(current.temperature || 0),
      feelsLike: Math.round(current.feels_like || current.temperature || 0),
      humidity: Math.round(current.humidity || 0),
      pressure: Math.round(current.pressure || 0),
      windSpeed: Math.round((current.wind_speed || 0) * 3.6), // Convert m/s to km/h
      windDirection: current.wind_direction || 0,
      description: current.description || 'Unknown',
      icon: current.icon || this.getDefaultIcon(current.description),
      visibility: Math.round(current.visibility || 0),
      uvIndex: current.uv_index || 0,
      location: data.location || {},
      timestamp: data.last_updated || new Date().toISOString(),
      source: data.data_source || 'unknown'
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