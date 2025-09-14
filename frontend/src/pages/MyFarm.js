/**
 * My Farm Page - Display current farm information from Supabase
 */

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  MapPinIcon, 
  BuildingOfficeIcon, 
  GlobeAltIcon,
  WrenchScrewdriverIcon,
  BeakerIcon,
  ScaleIcon,
  PencilIcon
} from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';
import ApiService from '../services/apiService';
import WeatherWidget from '../components/WeatherWidget';

const MyFarm = () => {
  // Fetch farm profile data
  const { 
    data: farmResponse, 
    isLoading, 
    error,
    refetch 
  } = useQuery({
    queryKey: ['farmProfile'],
    queryFn: ApiService.getFarmProfile,
    retry: 1,
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    onError: (error) => {
      console.error('Farm profile fetch error:', error);
    }
  });

  const farm = farmResponse?.data;

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !farm) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <BuildingOfficeIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No Farm Profile Found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating your farm profile to track your farming activities.
          </p>
          <div className="mt-6">
            <Link
              to="/farm/setup"
              className="inline-flex items-center rounded-md bg-green-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500"
            >
              <PencilIcon className="-ml-0.5 mr-1.5 h-5 w-5" />
              Create Farm Profile
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Farm</h1>
          <p className="mt-2 text-sm text-gray-600">
            Current farm information from Supabase database
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => refetch()}
            className="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
          >
            Refresh Data
          </button>
          <Link
            to="/farm/setup"
            className="inline-flex items-center rounded-md bg-green-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500"
          >
            <PencilIcon className="-ml-0.5 mr-1.5 h-5 w-5" />
            Edit Profile
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Farm Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Information */}
          <div className="bg-white shadow-md rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Farm Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex items-start space-x-3">
                <ScaleIcon className="w-5 h-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Total Area</p>
                  <p className="text-lg text-gray-700">{farm.field_size} acres</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <BeakerIcon className="w-5 h-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Soil Type</p>
                  <p className="text-lg text-gray-700">{farm.soil_type || 'Not specified'}</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <WrenchScrewdriverIcon className="w-5 h-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Irrigation Method</p>
                  <p className="text-lg text-gray-700">{farm.irrigation_method || 'Not specified'}</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <BuildingOfficeIcon className="w-5 h-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Farm ID</p>
                  <p className="text-sm font-mono text-gray-600">{farm.id}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Location Information */}
          <div className="bg-white shadow-md rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Location Details</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex items-start space-x-3">
                <MapPinIcon className="w-5 h-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm font-medium text-gray-900">District</p>
                  <p className="text-lg text-gray-700">{farm.location?.district || 'Not specified'}</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <BuildingOfficeIcon className="w-5 h-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Village</p>
                  <p className="text-lg text-gray-700">{farm.location?.village || 'Not specified'}</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <GlobeAltIcon className="w-5 h-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Coordinates</p>
                  <p className="text-sm text-gray-600">
                    {farm.location?.latitude && farm.location?.longitude 
                      ? `${parseFloat(farm.location.latitude).toFixed(4)}, ${parseFloat(farm.location.longitude).toFixed(4)}`
                      : 'Not specified'
                    }
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Database Status */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-3 h-3 bg-green-400 rounded-full"></div>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-green-800">
                  Supabase Connection Active
                </h3>
                <p className="text-sm text-green-700 mt-1">
                  Data is being successfully retrieved from the Supabase database. 
                  Farm ID: <span className="font-mono">{farm.id}</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Weather Widget */}
        <div className="lg:col-span-1">
          <WeatherWidget farmId={farm.id} className="mb-6" />
          
          {/* Quick Stats */}
          <div className="bg-white shadow-md rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Stats</h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Created</span>
                <span className="text-sm font-medium text-gray-900">
                  {farm.created_at ? new Date(farm.created_at).toLocaleDateString() : 'Unknown'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Last Updated</span>
                <span className="text-sm font-medium text-gray-900">
                  {farm.updated_at ? new Date(farm.updated_at).toLocaleDateString() : 'Never'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Farmer ID</span>
                <span className="text-sm font-mono text-gray-600">{farm.farmer_id}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyFarm;