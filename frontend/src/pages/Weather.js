/**
 * Weather Page Component
 * Dedicated page for detailed weather information and forecast
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  ArrowLeftIcon,
  MapPinIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { useQuery } from '@tanstack/react-query';
import ApiService from '../services/apiService';
import AuthService from '../services/authService';
import WeatherWidget from '../components/WeatherWidget';
import WeatherForecast from '../components/WeatherForecast';
import WeatherService from '../services/weatherService';

const WeatherPage = () => {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const userData = AuthService.getUser();
    setUser(userData);
  }, []);

  // Fetch farm profile
  const { data: farmProfileResponse, isLoading: farmLoading } = useQuery({
    queryKey: ['farmProfile'],
    queryFn: async () => {
      try {
        return await ApiService.getFarmProfile();
      } catch (error) {
        if (error.response?.status === 404) {
          return null;
        }
        throw error;
      }
    },
    enabled: !!user,
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });

  // Extract the actual farm profile from the API response
  const farmProfile = farmProfileResponse?.data || farmProfileResponse;

  // Fetch weather alerts - TEMPORARILY DISABLED
  const weatherAlerts = null;
  /*
  const { data: weatherAlerts } = useQuery({
    queryKey: ['weatherAlerts', farmProfile?.id],
    queryFn: async () => {
      if (farmProfile?.id) {
        try {
          return await WeatherService.getWeatherAlerts(farmProfile.id);
        } catch (error) {
          console.error('Error fetching weather alerts:', error);
          return [];
        }
      }
      return [];
    },
    enabled: !!farmProfile?.id,
    staleTime: 15 * 60 * 1000, // 15 minutes
    refetchOnWindowFocus: false,
  });
  */

  if (farmLoading) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="h-64 bg-gray-200 rounded"></div>
            <div className="lg:col-span-2 h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!farmProfile) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="text-center py-12">
          <MapPinIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No Farm Profile</h3>
          <p className="mt-1 text-sm text-gray-500">
            You need to set up your farm profile to view weather information.
          </p>
          <div className="mt-6">
            <Link
              to="/farm/setup"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              Set up farm profile
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate(-1)}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <ArrowLeftIcon className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Weather Forecast</h1>
            <p className="text-gray-600 mt-1">
              Real-time weather conditions for {farmProfile.location?.district}, {farmProfile.location?.state}
            </p>
          </div>
        </div>
        
        {/* Last Updated */}
        <div className="flex items-center text-sm text-gray-500">
          <ClockIcon className="w-4 h-4 mr-1" />
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* Weather Alerts */}
      {weatherAlerts && weatherAlerts.length > 0 && (
        <div className="mb-6">
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-md">
            <div className="flex">
              <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">
                  Weather Alerts
                </h3>
                <div className="mt-2 text-sm text-yellow-700">
                  {weatherAlerts.map((alert, index) => (
                    <p key={index} className="mb-1">• {alert.message || alert.description}</p>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Weather Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Current Weather */}
        <div className="lg:col-span-1">
          {farmProfile?.id ? (
            <WeatherWidget farmId={farmProfile.id} />
          ) : (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Current Weather</h3>
              <p className="text-gray-500">Please create a farm profile to view weather data.</p>
            </div>
          )}
        </div>

        {/* Extended Forecast */}
        <div className="lg:col-span-2">
          {farmProfile?.id ? (
            <WeatherForecast farmId={farmProfile.id} days={7} />
          ) : (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Weather Forecast</h3>
              <p className="text-gray-500">Please create a farm profile to view forecast data.</p>
            </div>
          )}
        </div>
      </div>

      {/* Weather Information Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {/* Farming Recommendations */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            📋 Farming Recommendations
          </h3>
          <div className="space-y-3 text-sm">
            <div className="p-3 bg-green-50 rounded-md">
              <p className="text-green-800">
                <span className="font-medium">Irrigation:</span> Check soil moisture levels before watering
              </p>
            </div>
            <div className="p-3 bg-blue-50 rounded-md">
              <p className="text-blue-800">
                <span className="font-medium">Spraying:</span> Early morning hours are ideal for pesticide application
              </p>
            </div>
            <div className="p-3 bg-yellow-50 rounded-md">
              <p className="text-yellow-800">
                <span className="font-medium">Harvesting:</span> Avoid harvesting during high humidity periods
              </p>
            </div>
          </div>
        </div>

        {/* Seasonal Information */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            🌱 Seasonal Guide
          </h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Current Season:</span>
              <span className="font-medium">Kharif</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Recommended Crops:</span>
              <span className="font-medium">Rice, Cotton</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Planting Window:</span>
              <span className="font-medium">June - July</span>
            </div>
            <div className="pt-2 border-t border-gray-200">
              <p className="text-gray-600">
                Monitor weather patterns for optimal planting and harvesting timing.
              </p>
            </div>
          </div>
        </div>

        {/* Weather Data Sources */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            📡 Data Sources
          </h3>
          <div className="space-y-3 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>WeatherAPI.com - Real-time data</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>Satellite imagery integration</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span>ML-enhanced predictions</span>
            </div>
            <div className="pt-2 border-t border-gray-200">
              <div className="flex items-start space-x-2">
                <InformationCircleIcon className="w-4 h-4 text-blue-500 mt-0.5" />
                <p className="text-gray-600">
                  Weather data is updated every 30 minutes for accuracy.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <Link
          to="/crops"
          className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
        >
          Get Crop Recommendations
        </Link>
        <Link
          to="/dashboard"
          className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
        >
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
};

export default WeatherPage;