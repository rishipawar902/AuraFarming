/**
 * Weather Widget Component for Dashboard
 * Displays current weather conditions in   if (error && !weatherData) {
    return <WeatherErrorFallback error={error} retry={() => refetch()} />;
  }
 */

import React from 'react';
import { 
  CloudIcon, 
  SunIcon,
  EyeIcon,
  ArrowRightIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { useQuery } from '@tanstack/react-query';
import WeatherService from '../services/weatherService';
import { WeatherErrorFallback } from './ErrorBoundary';

const WeatherWidget = ({ farmId, className = '' }) => {
  console.log('WeatherWidget: farmId received:', farmId);
  
  // Optimized caching with fresh data capability
  const { 
    data: weatherData, 
    isLoading: loading, 
    error,
    refetch
  } = useQuery({
    queryKey: ['currentWeather', farmId],
    queryFn: async () => {
      console.log('WeatherWidget: Fetching weather data for farmId:', farmId);
      if (!farmId) {
        throw new Error('No farm ID provided');
      }
      const data = await WeatherService.getCurrentWeatherForFarm(farmId);
      console.log('WeatherWidget: Received weather data:', data);
      return data;
    },
    enabled: !!farmId,
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes (reduced from 30)
    cacheTime: 30 * 60 * 1000, // Keep in cache for 30 minutes (reduced from 1 hour)
    refetchOnWindowFocus: false, // Don't refetch on window focus
    refetchOnMount: true, // Enable fresh data on component mount
    refetchOnReconnect: true, // Refetch when reconnecting to get latest data
    retry: 1, // Only retry once on failure
    onError: (error) => {
      // Log error for debugging but don't show console.error to users
      if (process.env.NODE_ENV === 'development') {
        console.error('WeatherWidget: Error fetching weather:', error);
      }
      // Error boundary will handle user-facing error display
    }
  });

  const getConditionIcon = (description) => {
    if (!description) return <CloudIcon className="w-8 h-8" />;
    
    const desc = description.toLowerCase();
    if (desc.includes('sunny') || desc.includes('clear')) {
      return <SunIcon className="w-8 h-8 text-yellow-500" />;
    }
    if (desc.includes('rain')) {
      return <CloudIcon className="w-8 h-8 text-blue-500" />;
    }
    return <CloudIcon className="w-8 h-8 text-gray-500" />;
  };

  const getFarmingCondition = () => {
    if (!weatherData) return null;
    return WeatherService.getFarmingCondition(weatherData);
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Current Weather</h3>
          <div className="animate-spin">
            <ArrowPathIcon className="w-5 h-5 text-gray-400" />
          </div>
        </div>
        <div className="space-y-2">
          <p className="text-gray-500">Loading fresh weather data...</p>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (error && !weatherData) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="text-center">
          <CloudIcon className="w-12 h-12 text-gray-400 mx-auto mb-2" />
          <p className="text-gray-500 text-sm">Unable to load weather data</p>
          <button
            onClick={() => refetch()}
            className="mt-2 text-blue-600 hover:text-blue-800 text-sm flex items-center justify-center gap-1"
          >
            <ArrowPathIcon className="w-4 h-4" />
            Refresh Data
          </button>
        </div>
      </div>
    );
  }

  const condition = getFarmingCondition();

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">Current Weather</h3>
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              console.log('Manual weather refresh triggered');
              refetch();
            }}
            className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
            title="Refresh weather data"
          >
            <ArrowPathIcon className="w-4 h-4" />
          </button>
          {weatherData?.icon && weatherData.icon.startsWith('http') ? (
            <img 
              src={WeatherService.getIconUrl(weatherData.icon)} 
              alt={weatherData.description}
              className="w-8 h-8"
            />
          ) : (
            getConditionIcon(weatherData?.description)
          )}
        </div>
      </div>

      <div className="space-y-3">
        {/* Temperature */}
        <div className="flex items-center justify-between">
          <span className="text-gray-600">Temperature</span>
          <span className={`text-2xl font-bold ${WeatherService.getTemperatureColor(weatherData?.temperature)}`}>
            {weatherData?.temperature}°C
          </span>
        </div>

        {/* Feels Like */}
        {weatherData?.feelsLike && weatherData.feelsLike !== weatherData.temperature && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500">Feels like</span>
            <span className="text-gray-700">{weatherData.feelsLike}°C</span>
          </div>
        )}

        {/* Humidity */}
        <div className="flex items-center justify-between">
          <span className="text-gray-600">Humidity</span>
          <span className={`font-medium ${WeatherService.getHumidityColor(weatherData?.humidity)}`}>
            {weatherData?.humidity}%
          </span>
        </div>

        {/* Wind */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1">
            <ArrowRightIcon className="w-4 h-4 text-gray-500" />
            <span className="text-gray-600">Wind</span>
          </div>
          <span className="text-gray-700">{weatherData?.windSpeed} km/h</span>
        </div>

        {/* Visibility */}
        {weatherData?.visibility && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-1">
              <EyeIcon className="w-4 h-4 text-gray-500" />
              <span className="text-gray-600">Visibility</span>
            </div>
            <span className="text-gray-700">{weatherData.visibility} km</span>
          </div>
        )}

        {/* Condition */}
        <div className="pt-2 border-t border-gray-200">
          <p className="text-sm text-gray-600 mb-1">{weatherData?.description}</p>
          {condition && (
            <div className={`text-sm px-2 py-1 rounded-full inline-block ${
              condition.status === 'good' ? 'bg-green-100 text-green-700' :
              condition.status === 'warning' ? 'bg-yellow-100 text-yellow-700' :
              condition.status === 'danger' ? 'bg-red-100 text-red-700' :
              'bg-gray-100 text-gray-700'
            }`}>
              {condition.message}
            </div>
          )}
        </div>

        {/* Location & Data Source */}
        {weatherData?.location && (
          <div className="pt-2 border-t border-gray-200 text-xs text-gray-500">
            <p>{weatherData.location.city}, {weatherData.location.region}</p>
            <p className="flex items-center justify-between">
              <span>Source: {weatherData.source}</span>
              {weatherData.timestamp && (
                <span>
                  {WeatherService.isDataFresh(weatherData.timestamp) ? '🟢 Fresh' : '🟡 Cached'}
                </span>
              )}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default WeatherWidget;