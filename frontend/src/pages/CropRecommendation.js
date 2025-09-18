/**
 * ML-Powered Crop Recommendation Page
 */

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { 
  BeakerIcon, 
  ChartBarIcon, 
  InformationCircleIcon,
  SparklesIcon,
  TrophyIcon
} from '@heroicons/react/24/outline';
import ApiService from '../services/apiService';
import AuthService from '../services/authService';
import toast from 'react-hot-toast';

const CropRecommendation = () => {
  const [formData, setFormData] = useState({
    district: 'Ranchi',
    season: 'Kharif',
    soil_type: 'Loamy Soil',
    soil_ph: 6.5,
    irrigation_type: 'Drip irrigation',
    field_size: 2.0,
    rainfall: 1200,
    temperature: 28,
    nitrogen: 300,
    phosphorus: 50,  // Added P parameter
    potassium: 50,   // Added K parameter
    humidity: 70
  });

  useEffect(() => {
    const userData = AuthService.getUser();
    
    // Set district from user data if available
    if (userData?.district) {
      setFormData(prev => ({ ...prev, district: userData.district }));
    }
  }, []);

  // Get ML model info
  const { data: modelInfo } = useQuery({
    queryKey: ['mlModelInfo'],
    queryFn: ApiService.getMLModelInfo,
    staleTime: 60 * 60 * 1000, // 1 hour
  });

  // Get crop recommendations mutation
  const recommendationMutation = useMutation({
    mutationFn: ApiService.getMLCropRecommendations,
    onSuccess: (data) => {
      // ML API returns array directly, not wrapped in success object
      if (Array.isArray(data) && data.length > 0) {
        toast.success('Recommendations generated successfully!');
      } else if (data.success) {
        toast.success('Recommendations generated successfully!');
      } else {
        toast.error(data.error || 'No recommendations found');
      }
    },
    onError: (error) => {
      console.error('ML Recommendation error:', error);
      toast.error('Failed to get recommendations. Please try again.');
    }
  });

  // Get yield prediction mutation
  const yieldMutation = useMutation({
    mutationFn: ApiService.predictYield,
    onSuccess: (data) => {
      if (data.success) {
        toast.success('Yield prediction calculated!');
      }
    },
    onError: () => {
      toast.error('Failed to predict yield.');
    }
  });

  // Advanced ML predictions mutation
  const advancedMLMutation = useMutation({
    mutationFn: ApiService.getAdvancedMLPredictions,
    onSuccess: (data) => {
      if (data.success) {
        toast.success('Advanced ML analysis completed!');
      }
    },
    onError: () => {
      toast.error('Failed to get advanced predictions.');
    }
  });

  // Crop price prediction mutation
  const priceMutation = useMutation({
    mutationFn: ApiService.predictCropPrice,
    onSuccess: (data) => {
      if (data.success) {
        toast.success('Price prediction generated!');
      }
    },
    onError: () => {
      toast.error('Failed to predict crop price.');
    }
  });

  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value
    }));
  };

  const handleGetRecommendations = async () => {
    await recommendationMutation.mutateAsync(formData);
  };

  const handlePredictYield = async (crop) => {
    const yieldData = {
      crop: crop,
      district: formData.district,
      soil_ph: formData.soil_ph,
      rainfall: formData.rainfall,
      temperature: formData.temperature,
      nitrogen: formData.nitrogen,
      phosphorus: formData.phosphorus,
      potassium: formData.potassium,
      field_size: formData.field_size
    };
    
    await yieldMutation.mutateAsync(yieldData);
  };

  const handleAdvancedMLPrediction = async () => {
    const mlData = {
      ...formData,
      features: {
        soil_ph: formData.soil_ph,
        rainfall: formData.rainfall,
        temperature: formData.temperature,
        nitrogen: formData.nitrogen,
        phosphorus: formData.phosphorus,
        potassium: formData.potassium,
        humidity: formData.humidity
      }
    };
    
    await advancedMLMutation.mutateAsync(mlData);
  };

  const handlePredictPrice = async (crop) => {
    const priceData = {
      crop: crop,
      district: formData.district,
      season: formData.season,
      market_factors: {
        rainfall: formData.rainfall,
        temperature: formData.temperature
      }
    };
    
    await priceMutation.mutateAsync(priceData);
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'text-green-600 bg-green-100';
    if (confidence >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getProfitColor = (profit) => {
    if (profit > 0) return 'text-green-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <SparklesIcon className="h-8 w-8 text-green-600" />
            <h1 className="text-3xl font-bold text-gray-900">
              AI-Powered Crop Recommendations
            </h1>
          </div>
          <p className="text-gray-600 max-w-3xl">
            Get intelligent crop recommendations powered by machine learning. 
            Our AI analyzes soil conditions, weather patterns, and agricultural data 
            to suggest the best crops for your farm in Jharkhand.
          </p>
        </div>

        {/* ML Model Info Card */}
        {modelInfo && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
            <div className="flex items-center gap-3 mb-4">
              <BeakerIcon className="h-6 w-6 text-blue-600" />
              <h3 className="text-lg font-semibold text-blue-900">
                ML Model Information
              </h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="font-medium text-blue-800">Model Type:</span>
                <span className="ml-2 text-blue-700">
                  {modelInfo?.model_type || 'N/A'}
                </span>
              </div>
              <div>
                <span className="font-medium text-blue-800">Accuracy:</span>
                <span className="ml-2 text-blue-700">
                  {modelInfo?.accuracy ? (modelInfo.accuracy * 100).toFixed(1) : 'N/A'}%
                </span>
              </div>
              <div>
                <span className="font-medium text-blue-800">Training Samples:</span>
                <span className="ml-2 text-blue-700">
                  2000
                </span>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Input Form */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">
                Farm Conditions
              </h2>
              
              <div className="space-y-4">
                {/* Location */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    District
                  </label>
                  <select
                    name="district"
                    value={formData.district}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    <option value="Ranchi">Ranchi</option>
                    <option value="Jamshedpur">Jamshedpur</option>
                    <option value="Dhanbad">Dhanbad</option>
                    <option value="Bokaro">Bokaro</option>
                    <option value="Deoghar">Deoghar</option>
                    <option value="Hazaribagh">Hazaribagh</option>
                  </select>
                </div>

                {/* Season */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Season
                  </label>
                  <select
                    name="season"
                    value={formData.season}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    <option value="Kharif">Kharif (June-November)</option>
                    <option value="Rabi">Rabi (November-April)</option>
                    <option value="Summer">Summer (February-May)</option>
                  </select>
                </div>

                {/* Soil Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Soil Type
                  </label>
                  <select
                    name="soil_type"
                    value={formData.soil_type}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    <option value="Loamy Soil">Loamy Soil</option>
                    <option value="Clay Soil">Clay Soil</option>
                    <option value="Sandy Soil">Sandy Soil</option>
                    <option value="Red Soil">Red Soil</option>
                    <option value="Alluvial Soil">Alluvial Soil</option>
                    <option value="Black Soil">Black Soil</option>
                  </select>
                </div>

                {/* Soil pH */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Soil pH
                  </label>
                  <input
                    type="number"
                    name="soil_ph"
                    value={formData.soil_ph}
                    onChange={handleInputChange}
                    min="4"
                    max="9"
                    step="0.1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>

                {/* Irrigation Method */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Irrigation Method
                  </label>
                  <select
                    name="irrigation_type"
                    value={formData.irrigation_type}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    <option value="Drip irrigation">Drip Irrigation</option>
                    <option value="Sprinkler irrigation">Sprinkler Irrigation</option>
                    <option value="Tube well">Tube Well</option>
                    <option value="Canal">Canal</option>
                    <option value="Rain-fed">Rain-fed</option>
                    <option value="Dug well">Dug Well</option>
                  </select>
                </div>

                {/* Field Size */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Field Size (hectares)
                  </label>
                  <input
                    type="number"
                    name="field_size"
                    value={formData.field_size}
                    onChange={handleInputChange}
                    min="0.1"
                    step="0.1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>

                {/* Environmental Conditions */}
                <div className="pt-4 border-t border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Environmental Conditions
                  </h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Expected Rainfall (mm/year)
                      </label>
                      <input
                        type="number"
                        name="rainfall"
                        value={formData.rainfall}
                        onChange={handleInputChange}
                        min="200"
                        max="3000"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Average Temperature (°C)
                      </label>
                      <input
                        type="number"
                        name="temperature"
                        value={formData.temperature}
                        onChange={handleInputChange}
                        min="15"
                        max="40"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nitrogen Content (kg/ha)
                      </label>
                      <input
                        type="number"
                        name="nitrogen"
                        value={formData.nitrogen}
                        onChange={handleInputChange}
                        min="50"
                        max="500"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Phosphorus Content (kg/ha)
                      </label>
                      <input
                        type="number"
                        name="phosphorus"
                        value={formData.phosphorus}
                        onChange={handleInputChange}
                        min="20"
                        max="150"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Potassium Content (kg/ha)
                      </label>
                      <input
                        type="number"
                        name="potassium"
                        value={formData.potassium}
                        onChange={handleInputChange}
                        min="20"
                        max="150"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Humidity (%)
                      </label>
                      <input
                        type="number"
                        name="humidity"
                        value={formData.humidity}
                        onChange={handleInputChange}
                        min="30"
                        max="100"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                  </div>
                </div>

                {/* Submit Buttons */}
                <div className="space-y-3">
                  <button
                    onClick={handleGetRecommendations}
                    disabled={recommendationMutation.isPending}
                    className="w-full bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {recommendationMutation.isPending ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <SparklesIcon className="h-5 w-5" />
                        Get AI Recommendations
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleAdvancedMLPrediction}
                    disabled={advancedMLMutation.isPending}
                    className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {advancedMLMutation.isPending ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Running Advanced Analysis...
                      </>
                    ) : (
                      <>
                        <BeakerIcon className="h-5 w-5" />
                        Advanced ML Analysis
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="lg:col-span-2">
            {(Array.isArray(recommendationMutation.data) || recommendationMutation.data?.success) && (
              <div className="space-y-6">
                
                {/* Recommendations Header */}
                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <TrophyIcon className="h-6 w-6 text-green-600" />
                    <h2 className="text-xl font-semibold text-gray-900">
                      Top Crop Recommendations
                    </h2>
                  </div>
                  <p className="text-gray-600">
                    Based on your farm conditions and ML analysis
                  </p>
                </div>

                {/* Recommendation Cards */}
                {(Array.isArray(recommendationMutation.data) 
                  ? recommendationMutation.data 
                  : recommendationMutation.data?.recommendations || []
                ).map((rec, index) => (
                  <div
                    key={index}
                    className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow"
                  >
                    <div className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                            <span className="text-xl font-bold text-green-600">
                              #{index + 1}
                            </span>
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900">
                              {rec.crop}
                            </h3>
                            <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getConfidenceColor(rec.confidence * 100)}`}>
                              {(rec.confidence * 100).toFixed(1)}% Confidence
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex gap-2">
                          <button
                            onClick={() => handlePredictYield(rec.crop)}
                            disabled={yieldMutation.isPending}
                            className="px-4 py-2 text-sm bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 transition-colors disabled:opacity-50"
                          >
                            {yieldMutation.isPending ? 'Predicting...' : 'Predict Yield'}
                          </button>
                          
                          <button
                            onClick={() => handlePredictPrice(rec.crop)}
                            disabled={priceMutation.isPending}
                            className="px-4 py-2 text-sm bg-purple-50 text-purple-600 rounded-md hover:bg-purple-100 transition-colors disabled:opacity-50"
                          >
                            {priceMutation.isPending ? 'Analyzing...' : 'Market Price'}
                          </button>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div className="bg-gray-50 p-3 rounded-md">
                          <div className="text-sm text-gray-600">Expected Yield</div>
                          <div className="text-lg font-semibold text-gray-900">
                            {rec.expected_yield} tonnes/ha
                          </div>
                        </div>
                        
                        <div className="bg-gray-50 p-3 rounded-md">
                          <div className="text-sm text-gray-600">Suitability Score</div>
                          <div className="text-lg font-semibold text-gray-900">
                            {(rec.suitability_score * 100).toFixed(0)}%
                          </div>
                        </div>
                        
                        <div className="bg-gray-50 p-3 rounded-md">
                          <div className="text-sm text-gray-600">Est. Profit</div>
                          <div className={`text-lg font-semibold ${getProfitColor(rec.profit_estimate)}`}>
                            ₹{rec.profit_estimate.toLocaleString()}
                          </div>
                        </div>
                      </div>

                      <div className="mb-4">
                        <h4 className="text-sm font-medium text-gray-700 mb-2">
                          Why this crop is recommended:
                        </h4>
                        <ul className="space-y-1">
                          <li className="text-sm text-gray-600 flex items-start gap-2">
                            <span className="text-green-500 mt-1">•</span>
                            High suitability for your soil and climate conditions
                          </li>
                          <li className="text-sm text-gray-600 flex items-start gap-2">
                            <span className="text-green-500 mt-1">•</span>
                            Good profit potential with current market rates
                          </li>
                          <li className="text-sm text-gray-600 flex items-start gap-2">
                            <span className="text-green-500 mt-1">•</span>
                            ML model confidence: {(rec.confidence * 100).toFixed(1)}%
                          </li>
                        </ul>
                      </div>

                      <div className="flex flex-wrap gap-2">
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          ML Recommended
                        </span>
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                          Yield: {rec.expected_yield.toFixed(1)} tonnes/ha
                        </span>
                        <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                          Harvest: {rec.harvest_month}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Yield Prediction Results */}
                {yieldMutation.data?.success && (
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <ChartBarIcon className="h-6 w-6 text-blue-600" />
                      <h3 className="text-lg font-semibold text-blue-900">
                        Yield Prediction for {yieldMutation.data.crop}
                      </h3>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <div className="text-sm text-blue-700 mb-1">Predicted Yield</div>
                        <div className="text-2xl font-bold text-blue-900">
                          {yieldMutation.data.predicted_yield} {yieldMutation.data.unit}
                        </div>
                        <div className="text-sm text-blue-600 mt-1">
                          Range: {yieldMutation.data.confidence_interval.lower} - {yieldMutation.data.confidence_interval.upper} {yieldMutation.data.unit}
                        </div>
                      </div>
                      
                      <div>
                        <div className="text-sm text-blue-700 mb-2">Contributing Factors</div>
                        <div className="space-y-1 text-sm">
                          <div className="flex justify-between">
                            <span>Soil pH Factor:</span>
                            <span className="font-medium">{(yieldMutation.data.factors.soil_ph_factor * 100).toFixed(0)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Rainfall Factor:</span>
                            <span className="font-medium">{(yieldMutation.data.factors.rainfall_factor * 100).toFixed(0)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Temperature Factor:</span>
                            <span className="font-medium">{(yieldMutation.data.factors.temp_factor * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Advanced ML Results */}
                {advancedMLMutation.data?.success && (
                  <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <BeakerIcon className="h-6 w-6 text-purple-600" />
                      <h3 className="text-lg font-semibold text-purple-900">
                        Advanced ML Analysis Results
                      </h3>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      <div>
                        <div className="text-sm text-purple-700 mb-1">Model Confidence</div>
                        <div className="text-2xl font-bold text-purple-900">
                          {(advancedMLMutation.data.confidence * 100).toFixed(1)}%
                        </div>
                      </div>
                      
                      <div>
                        <div className="text-sm text-purple-700 mb-1">Feature Importance</div>
                        <div className="space-y-1 text-sm">
                          {Object.entries(advancedMLMutation.data.feature_importance || {}).slice(0, 3).map(([feature, importance]) => (
                            <div key={feature} className="flex justify-between">
                              <span className="capitalize">{feature.replace('_', ' ')}:</span>
                              <span className="font-medium">{(importance * 100).toFixed(1)}%</span>
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      <div>
                        <div className="text-sm text-purple-700 mb-1">Risk Factors</div>
                        <div className="space-y-1 text-sm">
                          {advancedMLMutation.data.risk_analysis?.factors?.slice(0, 3).map((factor, idx) => (
                            <div key={idx} className="text-purple-600">
                              • {factor}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Price Prediction Results */}
                {priceMutation.data?.success && (
                  <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <InformationCircleIcon className="h-6 w-6 text-green-600" />
                      <h3 className="text-lg font-semibold text-green-900">
                        Market Price Prediction for {priceMutation.data.crop}
                      </h3>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div>
                        <div className="text-sm text-green-700 mb-1">Current Price</div>
                        <div className="text-2xl font-bold text-green-900">
                          ₹{priceMutation.data.current_price.toLocaleString()}/quintal
                        </div>
                      </div>
                      
                      <div>
                        <div className="text-sm text-green-700 mb-1">Predicted Price</div>
                        <div className="text-2xl font-bold text-green-900">
                          ₹{priceMutation.data.predicted_price.toLocaleString()}/quintal
                        </div>
                        <div className={`text-sm mt-1 ${priceMutation.data.price_trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                          {priceMutation.data.price_change > 0 ? '+' : ''}{priceMutation.data.price_change.toFixed(1)}% trend
                        </div>
                      </div>
                      
                      <div>
                        <div className="text-sm text-green-700 mb-1">Market Factors</div>
                        <div className="space-y-1 text-sm text-green-600">
                          {priceMutation.data.market_factors?.slice(0, 3).map((factor, idx) => (
                            <div key={idx}>• {factor}</div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

              </div>
            )}

            {/* Empty State */}
            {!recommendationMutation.data && !recommendationMutation.isPending && (
              <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
                <InformationCircleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Ready for AI Analysis
                </h3>
                <p className="text-gray-600 mb-6">
                  Fill in your farm conditions and click "Get AI Recommendations" 
                  to receive personalized crop suggestions powered by machine learning.
                </p>
                <div className="text-sm text-gray-500">
                  Our AI model analyzes {modelInfo?.total_features ? `${modelInfo.total_features} features and ` : ''}2000+ 
                  agricultural data points to provide accurate recommendations.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CropRecommendation;