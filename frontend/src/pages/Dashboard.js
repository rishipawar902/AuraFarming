/**
 * Dashboard Page Component
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  BuildingOfficeIcon, 
  CloudIcon, 
  CurrencyRupeeIcon,
  MapIcon,
  PlusIcon,
  ExclamationTriangleIcon,
  SunIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { useQuery } from '@tanstack/react-query';
import ApiService from '../services/apiService';
import AuthService from '../services/authService';
import OfflineService from '../services/offlineService';
import WeatherWidget from '../components/WeatherWidget';
import WeatherForecast from '../components/WeatherForecast';

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const [isOnline] = useState(navigator.onLine);

  useEffect(() => {
    const userData = AuthService.getUser();
    setUser(userData);
  }, []);

  // Fetch farm profile
  const { data: farmProfileResponse, isLoading: farmLoading, error: farmError } = useQuery({
    queryKey: ['farmProfile'],
    queryFn: async () => {
      try {
        if (isOnline) {
          return await ApiService.getFarmProfile();
        } else {
          return await OfflineService.getFarmProfile(user?.id);
        }
      } catch (error) {
        // Handle 404 - no farm profile exists yet
        if (error.response?.status === 404) {
          return null;
        }
        throw error;
      }
    },
    enabled: !!user,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    retry: (failureCount, error) => {
      // Don't retry on 404 errors
      if (error.response?.status === 404) {
        return false;
      }
      return failureCount < 2;
    }
  });

  // Extract the actual farm profile from the API response
  const farmProfile = farmProfileResponse?.data || farmProfileResponse;

  // Fetch recent crop recommendations
  const { data: recommendations } = useQuery({
    queryKey: ['recentRecommendations'],
    queryFn: async () => {
      try {
        if (isOnline) {
          // This would be a new endpoint for recent recommendations
          return []; // Mock empty for now
        } else {
          return await OfflineService.getRecommendations(user?.id);
        }
      } catch (error) {
        console.log('Recommendations not available:', error.message);
        return [];
      }
    },
    enabled: false, // DISABLED to prevent background calls
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });

  // Quick action cards
  const quickActions = [
    {
      title: 'Setup Farm Profile',
      description: 'Add your farm details to get personalized recommendations',
      icon: BuildingOfficeIcon,
      href: '/farm/setup',
      color: 'bg-blue-500',
      available: !farmProfile,
    },
    {
      title: 'Get AI Crop Recommendations',
      description: 'ML-powered suggestions based on soil & weather',
      icon: MapIcon,
      href: '/crops',
      color: 'bg-green-500',
      available: true,
      badge: 'NEW',
    },
    {
      title: 'Check Weather',
      description: 'Weather forecast and farming alerts',
      icon: CloudIcon,
      href: '/weather',
      color: 'bg-blue-400',
      available: true,
    },
    {
      title: 'Market Prices',
      description: 'Current mandi prices in your area',
      icon: CurrencyRupeeIcon,
      href: '/market',
      color: 'bg-yellow-500',
      available: true,
    },
  ];

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          {getGreeting()}, {user?.name || 'Farmer'}!
        </h1>
        <p className="text-gray-600 mt-2">
          Here's what's happening with your farm today
        </p>
      </div>

      {/* Farm Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Farm Profile Status */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <BuildingOfficeIcon className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Farm Profile</p>
              <p className="text-2xl font-bold text-gray-900">
                {farmLoading ? '...' : farmProfile ? 'Active' : 'Pending'}
              </p>
            </div>
          </div>
          {farmProfile && (
            <div className="mt-4 text-sm text-gray-600">
              <p>Area: {farmProfile.total_area} acres</p>
              <p>Location: {farmProfile.village}, {farmProfile.district}</p>
            </div>
          )}
        </div>

        {/* Weather Status */}
        {farmProfile?.id ? (
          <WeatherWidget 
            farmId={farmProfile.id} 
            className="bg-white rounded-lg shadow p-6"
          />
        ) : (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Weather</h3>
            <p className="text-gray-500">Create a farm profile to view weather data.</p>
          </div>
        )}

        {/* Recommendations */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <MapIcon className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Recommendations</p>
              <p className="text-2xl font-bold text-gray-900">
                {recommendations?.length || 0}
              </p>
            </div>
          </div>
          <div className="mt-4">
            <Link 
              to="/crops" 
              className="text-sm text-blue-600 hover:text-blue-500 font-medium"
            >
              View all →
            </Link>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Season</p>
              <p className="text-2xl font-bold text-gray-900">
                {new Date().getMonth() >= 5 && new Date().getMonth() <= 9 ? 'Kharif' : 'Rabi'}
              </p>
            </div>
          </div>
          <div className="mt-4 text-sm text-gray-600">
            <p>Current farming season</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {quickActions.filter(action => action.available).map((action) => {
            const Icon = action.icon;
            return (
              <Link
                key={action.title}
                to={action.href}
                className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6 block"
              >
                <div className="flex items-start">
                  <div className={`flex-shrink-0 ${action.color} rounded-lg p-3`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      {action.title}
                    </h3>
                    <p className="text-gray-600 mt-2">
                      {action.description}
                    </p>
                  </div>
                  <PlusIcon className="h-5 w-5 text-gray-400 ml-auto" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Weather Forecast & Tips */}
      {farmProfile && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Weather Forecast */}
          <WeatherForecast 
            farmId={farmProfile.id} 
            days={5}
            className="lg:col-span-1"
          />

          {/* Farming Tips */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Today's Farming Tips
            </h3>
            <div className="space-y-3">
              <div className="p-3 bg-green-50 rounded-md">
                <p className="text-sm text-green-800">
                  💡 Check soil moisture before irrigation to conserve water
                </p>
              </div>
              <div className="p-3 bg-blue-50 rounded-md">
                <p className="text-sm text-blue-800">
                  🌱 Monitor crop growth stage for optimal fertilizer application
                </p>
              </div>
              <div className="p-3 bg-purple-50 rounded-md">
                <p className="text-sm text-purple-800">
                  📊 Record daily observations for better crop management
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* No Farm Profile CTA */}
      {!farmProfile && !farmLoading && (
        <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-8 text-white">
          <div className="max-w-2xl">
            <h3 className="text-2xl font-bold mb-4">
              Complete Your Farm Setup
            </h3>
            <p className="text-green-100 mb-6">
              To get personalized crop recommendations and maximize your yield potential, 
              please complete your farm profile setup.
            </p>
            <Link
              to="/farm/setup"
              className="inline-flex items-center px-6 py-3 bg-white text-green-600 font-medium rounded-lg hover:bg-green-50 transition-colors"
            >
              <BuildingOfficeIcon className="h-5 w-5 mr-2" />
              Setup Farm Profile
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;