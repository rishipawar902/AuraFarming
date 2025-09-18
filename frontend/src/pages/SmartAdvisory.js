import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import ApiService from '../services/apiService';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  ExclamationTriangleIcon,
  LightBulbIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

const getCurrentSeason = () => {
  const month = new Date().getMonth() + 1; // 1-12
  if (month >= 6 && month <= 11) return 'Kharif';
  if (month >= 11 || month <= 4) return 'Rabi';
  return 'Zaid';
};

const SmartAdvisory = () => {
  const [inputData, setInputData] = useState({
    location: 'Ranchi',
    soil_type: 'loamy',
    current_crop: '',
    farm_size: 2.5,
    irrigation_available: true,
    N: 90,
    P: 40,
    K: 40,
    temperature: 25,
    humidity: 80,
    ph: 6.5,
    rainfall: 200,
    organic_matter: 3.0,
    soil_moisture: 60
  });

  // Helper function to safely render any value, handling objects
  const safeRender = (value, fallback = 'N/A') => {
    if (value === null || value === undefined) return fallback;
    if (typeof value === 'object') {
      // If it's an object with risk assessment data, render as string
      if (value.market_risk !== undefined) {
        return `Market Risk: ${value.market_risk} | Climate Risk: ${value.climate_risk} | Pest Disease Risk: ${value.pest_disease_risk}`;
      }
      // For other objects, convert to JSON string
      return JSON.stringify(value);
    }
    return String(value);
  };

  // Seasonal advisory mutation
  const seasonalMutation = useMutation({
    mutationFn: async (requestData) => {
      console.log('Seasonal advisory request:', requestData);
      const result = await ApiService.getSeasonalAdvisory(requestData);
      console.log('Seasonal advisory response:', result);
      return result;
    },
    onSuccess: (data) => {
      console.log('Seasonal advisory success:', data);
      toast.success('Seasonal advisory generated successfully!');
    },
    onError: (error) => {
      console.error('Seasonal advisory error:', error);
      toast.error('Failed to get seasonal advisory');
    }
  });

  const handleInputChange = (field, value) => {
    setInputData(prev => ({
      ...prev,
      [field]: field.includes('available') ? value === 'true' : (parseFloat(value) || value)
    }));
  };

  const getAdvisory = async () => {
    console.log('Getting seasonal advisory');
    console.log('Input data:', inputData);
    
    try {
      // Transform input data for seasonal advisory
      const requestData = {
        location: inputData.location,
        soil_type: inputData.soil_type,
        current_season: getCurrentSeason(),
        climate_conditions: {
          temperature: inputData.temperature,
          humidity: inputData.humidity,
          rainfall: inputData.rainfall
        }
      };
      seasonalMutation.mutate(requestData);
    } catch (error) {
      console.error('Error in getAdvisory:', error);
      toast.error('Something went wrong. Please try again.');
    }
  };

  const renderInputForm = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        Farm Information
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Location
          </label>
          <select
            value={inputData.location}
            onChange={(e) => handleInputChange('location', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="Ranchi">Ranchi</option>
            <option value="Dhanbad">Dhanbad</option>
            <option value="Jamshedpur">Jamshedpur</option>
            <option value="Bokaro">Bokaro</option>
            <option value="Deoghar">Deoghar</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Soil Type
          </label>
          <select
            value={inputData.soil_type}
            onChange={(e) => handleInputChange('soil_type', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="loamy">Loamy Soil</option>
            <option value="clay">Clay Soil</option>
            <option value="sandy">Sandy Soil</option>
            <option value="red">Red Soil</option>
            <option value="black">Black Soil</option>
          </select>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Farm Size (acres)
          </label>
          <input
            type="number"
            step="0.1"
            value={inputData.farm_size}
            onChange={(e) => handleInputChange('farm_size', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Current Crop (Optional)
          </label>
          <input
            type="text"
            value={inputData.current_crop}
            onChange={(e) => handleInputChange('current_crop', e.target.value)}
            placeholder="e.g. Rice, Wheat"
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Irrigation Available
          </label>
          <select
            value={inputData.irrigation_available.toString()}
            onChange={(e) => handleInputChange('irrigation_available', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="true">Yes</option>
            <option value="false">No</option>
          </select>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nitrogen (N)
          </label>
          <input
            type="number"
            value={inputData.N}
            onChange={(e) => handleInputChange('N', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Phosphorus (P)
          </label>
          <input
            type="number"
            value={inputData.P}
            onChange={(e) => handleInputChange('P', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Potassium (K)
          </label>
          <input
            type="number"
            value={inputData.K}
            onChange={(e) => handleInputChange('K', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            pH Level
          </label>
          <input
            type="number"
            step="0.1"
            value={inputData.ph}
            onChange={(e) => handleInputChange('ph', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
      
      <div className="mt-6">
        <button
          onClick={getAdvisory}
          disabled={seasonalMutation.isPending}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center"
        >
          {seasonalMutation.isPending ? (
            <ClockIcon className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <LightBulbIcon className="h-4 w-4 mr-2" />
          )}
          Get Seasonal Advisory
        </button>
      </div>
    </div>
  );

  const renderAdvisoryResults = (mutation) => {
    const { data, isPending, error } = mutation;
    
    if (isPending) return <LoadingSpinner message="Getting your personalized farming advice..." />;
    
    if (error) {
      console.error('Advisory error details:', error);
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-2" />
            <span className="text-red-800">
              Failed to load advisory data: {error?.message || 'Unknown error'}
            </span>
          </div>
          <button 
            onClick={() => mutation.reset()}
            className="mt-3 text-sm bg-red-100 hover:bg-red-200 px-3 py-1 rounded"
          >
            Try Again
          </button>
        </div>
      );
    }

    if (!data) {
      return (
        <div className="text-center text-gray-500 py-8">
          Click "Get Seasonal Advisory" to get personalized seasonal farming recommendations
        </div>
      );
    }

    // Debug: Log the data structure
    console.log('Advisory data structure:', data);
    console.log('Data keys:', Object.keys(data));

    return (
      <div className="space-y-6">
        {/* Seasonal Practices */}
        {data.seasonal_practices && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Seasonal Practices</h3>
            <ul className="space-y-2">
              {Array.isArray(data.seasonal_practices) ? data.seasonal_practices.map((practice, index) => (
                <li key={index} className="flex items-start">
                  <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  <span className="text-gray-600">
                    {safeRender(practice)}
                  </span>
                </li>
              )) : (
                <li className="text-center text-gray-500">No seasonal practices available</li>
              )}
            </ul>
          </div>
        )}

        {/* Precautions */}
        {data.precautions && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <ExclamationTriangleIcon className="h-5 w-5 mr-2 text-red-600" />
              Precautions
            </h3>
            <ul className="space-y-2">
              {Array.isArray(data.precautions) ? data.precautions.map((precaution, index) => (
                <li key={index} className="flex items-start">
                  <span className="inline-block w-2 h-2 bg-red-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  <span className="text-gray-600">
                    {safeRender(precaution)}
                  </span>
                </li>
              )) : (
                <li className="text-center text-gray-500">No precautions available</li>
              )}
            </ul>
          </div>
        )}

        {/* Suitable crops for seasonal advisory */}
        {data.suitable_crops && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Suitable Crops for This Season</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {Array.isArray(data.suitable_crops) ? data.suitable_crops.map((crop, index) => (
                <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
                  <span className="font-medium text-green-800 capitalize">
                    {safeRender(crop)}
                  </span>
                </div>
              )) : (
                <div className="col-span-full text-center text-gray-500">
                  No suitable crops available
                </div>
              )}
            </div>
          </div>
        )}

        {/* Market timing for seasonal advisory */}
        {data.market_timing && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Market Timing</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-1">Best Sowing Time</h4>
                <p className="text-gray-600">
                  {safeRender(data.market_timing.best_sowing_time)}
                </p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-1">Expected Harvest</h4>
                <p className="text-gray-600">
                  {safeRender(data.market_timing.expected_harvest)}
                </p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-1">Market Outlook</h4>
                <p className="text-gray-600">
                  {safeRender(data.market_timing.market_outlook)}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Seasonal Agricultural Advisory</h1>
          <p className="text-gray-600">Get personalized seasonal farming recommendations based on your specific conditions</p>
        </div>

        {/* Input Form */}
        <div className="mb-8">
          {renderInputForm()}
        </div>

        {/* Results */}
        <div className="mt-8">
          {renderAdvisoryResults(seasonalMutation)}
        </div>
      </div>
    </div>
  );
};

export default SmartAdvisory;