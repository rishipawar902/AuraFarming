import React from 'react';
import { ArrowPathIcon } from '@heroicons/react/24/outline';
import { useQuery } from '@tanstack/react-query';
import WeatherService from '../services/weatherService';

const WeatherForecast = ({ farmId, days = 5, className = '' }) => {
  // Re-enabled with safe caching
  const { 
    data: forecastData, 
    isLoading: loading, 
    error,
    refetch
  } = useQuery({
    queryKey: ['weatherForecast', farmId, days],
    queryFn: async () => {
      if (!farmId) return [];
      const data = await WeatherService.getForecastForFarm(farmId, days);
      return data || [];
    },
    enabled: !!farmId,
    staleTime: 5 * 60 * 1000, // 5 minutes cache for forecasts (updated for freshness)
    cacheTime: 30 * 60 * 1000, // 30 minutes (reduced from 2 hours)
    refetchOnMount: true, // Enable fresh data on mount
    refetchOnWindowFocus: false,
    refetchOnReconnect: true, // Refetch when reconnecting
    retry: 1
  });

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Weather Forecast</h3>
        <p className="text-gray-500">Loading forecast...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Weather Forecast</h3>
        <p className="text-gray-500 text-sm mb-2">Unable to load forecast</p>
        <button onClick={() => refetch()} className="text-blue-600 text-sm">
          Refresh
        </button>
      </div>
    );
  }

  const displayData = forecastData || [];

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">{days}-Day Forecast</h3>
        <button onClick={() => refetch()} className="p-1 text-gray-400 hover:text-gray-600">
          <ArrowPathIcon className="w-4 h-4" />
        </button>
      </div>
      <div className="space-y-3">
        {displayData.map((day, index) => (
          <div key={day.date || index} className="flex items-center justify-between py-2">
            <div className="flex items-center space-x-3">
              <span className="text-xl">{day.icon || ''}</span>
              <div>
                <p className="font-medium">{index === 0 ? 'Today' : day.dateFormatted}</p>
                <p className="text-sm text-gray-500">{day.description}</p>
              </div>
            </div>
            <div className="text-right">
              <span className="font-bold">{day.temperatureMax}</span>
              <span className="text-gray-500 ml-2">{day.temperatureMin}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WeatherForecast;
