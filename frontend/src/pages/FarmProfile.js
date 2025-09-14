/**
 * Farm Profile Setup Page Component
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapIcon, BuildingOfficeIcon, PlusIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import ApiService from '../services/apiService';
import AuthService from '../services/authService';
import OfflineService from '../services/offlineService';

// Jharkhand districts and common crops
const JHARKHAND_DISTRICTS = [
  'Bokaro', 'Chatra', 'Deoghar', 'Dhanbad', 'Dumka', 'East Singhbhum',
  'Garhwa', 'Giridih', 'Godda', 'Gumla', 'Hazaribagh', 'Jamtara',
  'Khunti', 'Koderma', 'Latehar', 'Lohardaga', 'Pakur', 'Palamu',
  'Ramgarh', 'Ranchi', 'Sahebganj', 'Seraikela Kharsawan', 'Simdega', 'West Singhbhum'
];

const SOIL_TYPES = [
  'Red Soil', 'Black Soil', 'Alluvial Soil', 'Laterite Soil', 'Sandy Soil', 'Clay Soil'
];

const IRRIGATION_SOURCES = [
  'Rain Fed', 'Bore Well', 'Open Well', 'Canal', 'Pond', 'River', 'Tube Well'
];

const COMMON_CROPS = [
  'Rice', 'Wheat', 'Maize', 'Sugarcane', 'Potato', 'Onion', 'Tomato', 
  'Mustard', 'Gram', 'Arhar', 'Moong', 'Urad', 'Groundnut', 'Soybean'
];

const FarmProfile = () => {
  const [user, setUser] = useState(null);
  const [formData, setFormData] = useState({
    totalArea: '',
    district: '',
    village: '',
    soilType: '',
    irrigationSource: '',
    latitude: '',
    longitude: '',
    previousCrops: []
  });
  const [currentCrop, setCurrentCrop] = useState({ 
    name: '', 
    area: '', 
    season: '', 
    year: new Date().getFullYear() 
  });
  const [isAddingCrop, setIsAddingCrop] = useState(false);
  const [isOnline] = useState(navigator.onLine);
  
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  useEffect(() => {
    const userData = AuthService.getUser();
    setUser(userData);
  }, []);

  // Fetch existing farm profile
  const { data: existingProfile, isLoading } = useQuery({
    queryKey: ['farmProfile'],
    queryFn: async () => {
      if (isOnline) {
        return await ApiService.getFarmProfile();
      } else {
        return await OfflineService.getFarmProfile(user?.id);
      }
    },
    enabled: !!user,
    onSuccess: (data) => {
      if (data) {
        setFormData({
          totalArea: data.total_area || '',
          district: data.district || '',
          village: data.village || '',
          soilType: data.soil_type || '',
          irrigationSource: data.irrigation_source || '',
          latitude: data.latitude || '',
          longitude: data.longitude || '',
          previousCrops: data.previous_crops || []
        });
      }
    }
  });

  // Create/Update farm profile mutation
  const farmMutation = useMutation({
    mutationFn: async (farmData) => {
      if (isOnline) {
        return await ApiService.createFarmProfile(farmData);
      } else {
        // Save offline and add to sync queue
        await OfflineService.saveFarmProfile({ ...farmData, farmer_id: user.id });
        await OfflineService.addToSyncQueue('CREATE_FARM', farmData);
        return { success: true, offline: true };
      }
    },
    onSuccess: (data) => {
      if (data.offline) {
        toast.success('Farm profile saved offline. Will sync when online.');
      } else {
        toast.success('Farm profile created successfully!');
      }
      queryClient.invalidateQueries(['farmProfile']);
      navigate('/dashboard');
    },
    onError: (error) => {
      toast.error('Failed to save farm profile');
      console.error('Farm profile error:', error);
    }
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCropInputChange = (e) => {
    const { name, value } = e.target;
    setCurrentCrop(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const addCrop = () => {
    if (!currentCrop.name || !currentCrop.area || !currentCrop.season) {
      toast.error('Please fill in all crop details');
      return;
    }

    const crop = {
      ...currentCrop,
      area: parseFloat(currentCrop.area),
      year: parseInt(currentCrop.year)
    };

    setFormData(prev => ({
      ...prev,
      previousCrops: [...prev.previousCrops, crop]
    }));

    setCurrentCrop({ name: '', area: '', season: '', year: new Date().getFullYear() });
    setIsAddingCrop(false);
    toast.success('Crop added successfully!');
  };

  const removeCrop = (index) => {
    setFormData(prev => ({
      ...prev,
      previousCrops: prev.previousCrops.filter((_, i) => i !== index)
    }));
    toast.success('Crop removed');
  };

  const getLocation = () => {
    if (navigator.geolocation) {
      toast.loading('Getting your location...');
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData(prev => ({
            ...prev,
            latitude: position.coords.latitude.toFixed(6),
            longitude: position.coords.longitude.toFixed(6)
          }));
          toast.dismiss();
          toast.success('Location updated!');
        },
        (error) => {
          toast.dismiss();
          toast.error('Unable to get location. Please enter manually.');
          console.error('Location error:', error);
        }
      );
    } else {
      toast.error('Geolocation is not supported by this browser');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Validation
    if (!formData.totalArea || !formData.district || !formData.village || !formData.soilType) {
      toast.error('Please fill in all required fields');
      return;
    }

    if (parseFloat(formData.totalArea) <= 0) {
      toast.error('Total area must be greater than 0');
      return;
    }

    const profileData = {
      total_area: parseFloat(formData.totalArea),
      district: formData.district,
      village: formData.village,
      soil_type: formData.soilType,
      irrigation_source: formData.irrigationSource,
      latitude: formData.latitude ? parseFloat(formData.latitude) : null,
      longitude: formData.longitude ? parseFloat(formData.longitude) : null,
      previous_crops: formData.previousCrops
    };

    farmMutation.mutate(profileData);
  };

  if (isLoading) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="animate-pulse">
            <div className="h-6 bg-gray-300 rounded w-1/3 mb-4"></div>
            <div className="space-y-4">
              <div className="h-4 bg-gray-300 rounded w-full"></div>
              <div className="h-4 bg-gray-300 rounded w-2/3"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <BuildingOfficeIcon className="h-8 w-8 mr-3 text-green-600" />
          {existingProfile ? 'Update Farm Profile' : 'Setup Your Farm Profile'}
        </h1>
        <p className="text-gray-600 mt-2">
          {existingProfile 
            ? 'Update your farm information to get better recommendations'
            : 'Please provide your farm details to get personalized crop recommendations'
          }
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Farm Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="totalArea" className="block text-sm font-medium text-gray-700">
                Total Farm Area (in acres) *
              </label>
              <input
                id="totalArea"
                name="totalArea"
                type="number"
                step="0.1"
                min="0.1"
                required
                value={formData.totalArea}
                onChange={handleInputChange}
                placeholder="e.g., 2.5"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500"
              />
            </div>

            <div>
              <label htmlFor="district" className="block text-sm font-medium text-gray-700">
                District *
              </label>
              <select
                id="district"
                name="district"
                required
                value={formData.district}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
              >
                <option value="">Select District</option>
                {JHARKHAND_DISTRICTS.map(district => (
                  <option key={district} value={district}>{district}</option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="village" className="block text-sm font-medium text-gray-700">
                Village/Block *
              </label>
              <input
                id="village"
                name="village"
                type="text"
                required
                value={formData.village}
                onChange={handleInputChange}
                placeholder="Enter village or block name"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500"
              />
            </div>

            <div>
              <label htmlFor="soilType" className="block text-sm font-medium text-gray-700">
                Soil Type *
              </label>
              <select
                id="soilType"
                name="soilType"
                required
                value={formData.soilType}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
              >
                <option value="">Select Soil Type</option>
                {SOIL_TYPES.map(soil => (
                  <option key={soil} value={soil}>{soil}</option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="irrigationSource" className="block text-sm font-medium text-gray-700">
                Main Irrigation Source
              </label>
              <select
                id="irrigationSource"
                name="irrigationSource"
                value={formData.irrigationSource}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
              >
                <option value="">Select Irrigation Source</option>
                {IRRIGATION_SOURCES.map(source => (
                  <option key={source} value={source}>{source}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Location Information */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <MapIcon className="h-5 w-5 mr-2 text-green-600" />
              Location (Optional)
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label htmlFor="latitude" className="block text-sm font-medium text-gray-700">
                  Latitude
                </label>
                <input
                  id="latitude"
                  name="latitude"
                  type="number"
                  step="0.000001"
                  value={formData.latitude}
                  onChange={handleInputChange}
                  placeholder="e.g., 23.3441"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500"
                />
              </div>

              <div>
                <label htmlFor="longitude" className="block text-sm font-medium text-gray-700">
                  Longitude
                </label>
                <input
                  id="longitude"
                  name="longitude"
                  type="number"
                  step="0.000001"
                  value={formData.longitude}
                  onChange={handleInputChange}
                  placeholder="e.g., 85.3096"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500"
                />
              </div>

              <div className="flex items-end">
                <button
                  type="button"
                  onClick={getLocation}
                  className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  Get Current Location
                </button>
              </div>
            </div>
          </div>

          {/* Previous Crops */}
          <div className="border-t pt-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Previous Crops (Optional)
              </h3>
              <button
                type="button"
                onClick={() => setIsAddingCrop(true)}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-green-700 bg-green-100 hover:bg-green-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <PlusIcon className="h-4 w-4 mr-1" />
                Add Crop
              </button>
            </div>

            {/* Add Crop Form */}
            {isAddingCrop && (
              <div className="bg-gray-50 p-4 rounded-lg mb-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Crop Name
                    </label>
                    <select
                      name="name"
                      value={currentCrop.name}
                      onChange={handleCropInputChange}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
                    >
                      <option value="">Select Crop</option>
                      {COMMON_CROPS.map(crop => (
                        <option key={crop} value={crop}>{crop}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Area (acres)
                    </label>
                    <input
                      name="area"
                      type="number"
                      step="0.1"
                      min="0.1"
                      value={currentCrop.area}
                      onChange={handleCropInputChange}
                      placeholder="e.g., 1.5"
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Season
                    </label>
                    <select
                      name="season"
                      value={currentCrop.season}
                      onChange={handleCropInputChange}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
                    >
                      <option value="">Select Season</option>
                      <option value="Kharif">Kharif (Monsoon)</option>
                      <option value="Rabi">Rabi (Winter)</option>
                      <option value="Zaid">Zaid (Summer)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Year
                    </label>
                    <input
                      name="year"
                      type="number"
                      min="2020"
                      max={new Date().getFullYear()}
                      value={currentCrop.year}
                      onChange={handleCropInputChange}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
                    />
                  </div>
                </div>

                <div className="flex space-x-3 mt-4">
                  <button
                    type="button"
                    onClick={addCrop}
                    className="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700"
                  >
                    Add Crop
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsAddingCrop(false)}
                    className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Existing Crops */}
            {formData.previousCrops.length > 0 && (
              <div className="space-y-3">
                {formData.previousCrops.map((crop, index) => (
                  <div key={index} className="flex items-center justify-between bg-white border border-gray-200 rounded-lg p-4">
                    <div>
                      <h4 className="font-medium text-gray-900">{crop.name}</h4>
                      <p className="text-sm text-gray-600">
                        {crop.area} acres • {crop.season} {crop.year}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeCrop(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <XMarkIcon className="h-5 w-5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Submit Button */}
          <div className="flex justify-end pt-6 border-t">
            <button
              type="submit"
              disabled={farmMutation.isLoading}
              className={`inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 ${
                farmMutation.isLoading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {farmMutation.isLoading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Saving...
                </div>
              ) : (
                existingProfile ? 'Update Farm Profile' : 'Create Farm Profile'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FarmProfile;