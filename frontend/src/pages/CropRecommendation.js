/**
 * ML-Powered Crop Recommendation Page with Market Intelligence
 */

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  BeakerIcon, 
  InformationCircleIcon,
  SparklesIcon,
  TrophyIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon
} from '@heroicons/react/24/outline';
import apiService from '../services/apiService';
import AuthService from '../services/authService';
import { useMarket } from '../contexts/MarketContext';
import useMarketAwareCropRecommendations from '../hooks/useMarketAwareCropRecommendations';

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
    phosphorus: 50,
    potassium: 50,
    humidity: 70
  });

  // Market context and hooks
  const { getMarketData } = useMarket();
  const {
    useMarketData,
    data: recommendations,
    loading,
    getRecommendations,
    processRecommendationData,
    toggleRecommendationType,
    hasData
  } = useMarketAwareCropRecommendations();

  useEffect(() => {
    const userData = AuthService.getUser();
    
    // Set district from user data if available
    if (userData?.district) {
      setFormData(prev => ({ ...prev, district: userData.district }));
    }
  }, []);

  // Preload market data when district changes
  useEffect(() => {
    if (formData.district && useMarketData) {
      getMarketData(formData.district);
    }
  }, [formData.district, useMarketData, getMarketData]);

  // Get ML model info
  const { data: modelInfo } = useQuery({
    queryKey: ['mlModelInfo'],
    queryFn: apiService.getMLModelInfo,
    staleTime: 60 * 60 * 1000, // 1 hour
  });

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value
    }));
  };

  // Handle recommendation submission
  const handleGetRecommendations = async () => {
    try {
      await getRecommendations(formData);
    } catch (error) {
      console.error('Error getting recommendations:', error);
    }
  };

  // Process recommendations for display
  const processedRecommendations = recommendations ? 
    processRecommendationData(recommendations, formData.district) : [];

  // Utility functions for styling
  const getConfidenceColor = (score) => {
    const percentage = score * 100;
    if (percentage >= 80) return 'text-green-600 bg-green-100';
    if (percentage >= 60) return 'text-yellow-600 bg-yellow-100';
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

                {/* Market Data Toggle */}
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-blue-900">Market Intelligence</h3>
                      <p className="text-xs text-blue-700 mt-1">
                        {useMarketData 
                          ? "Get profit-optimized recommendations with real-time market data" 
                          : "Get basic ML recommendations without market analysis"
                        }
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={useMarketData}
                        onChange={(e) => toggleRecommendationType()}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>

                {/* Submit Buttons */}
                <div className="space-y-3">
                  <button
                    onClick={handleGetRecommendations}
                    disabled={loading}
                    className="w-full bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <SparklesIcon className="h-5 w-5" />
                        {useMarketData ? 'Get Market-Enhanced Recommendations' : 'Get AI Recommendations'}
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="lg:col-span-2">
            {hasData && (
              <div className="space-y-6">
                
                {/* Recommendations Header */}
                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <TrophyIcon className="h-6 w-6 text-green-600" />
                    <h2 className="text-xl font-semibold text-gray-900">
                      {useMarketData ? 'Market-Enhanced Crop Recommendations' : 'Top Crop Recommendations'}
                    </h2>
                  </div>
                  <p className="text-gray-600">
                    {useMarketData 
                      ? 'Based on your farm conditions, ML analysis, and real-time market intelligence'
                      : 'Based on your farm conditions and ML analysis'
                    }
                  </p>
                </div>

                {/* Recommendation Cards */}
                {processedRecommendations.map((rec, index) => (
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
                              {rec.cropName || rec.crop}
                            </h3>
                            <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getConfidenceColor(rec.displayScore)}`}>
                              {(rec.displayScore * 100).toFixed(1)}% {rec.scoreLabel || 'Score'}
                            </div>
                            {rec.isMarketEnhanced && (
                              <div className="mt-1">
                                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                  <CurrencyDollarIcon className="h-3 w-3 mr-1" />
                                  Market Enhanced
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                        
                        <div className="flex gap-2">
                          {rec.showMarketData && (
                            <div className="flex items-center gap-2 text-sm text-gray-600">
                              <ArrowTrendingUpIcon className="h-4 w-4" />
                              <span>Real Market Data</span>
                            </div>
                          )}
                          <div className="text-sm text-gray-500">
                            {rec.reliability === 'high' ? '🟢' : '🟡'} {rec.dataSource}
                          </div>
                        </div>
                      </div>

                      <div className={`grid grid-cols-1 ${useMarketData ? 'md:grid-cols-4' : 'md:grid-cols-3'} gap-4 mb-4`}>
                        <div className="bg-gray-50 p-3 rounded-md">
                          <div className="text-sm text-gray-600">Expected Yield</div>
                          <div className="text-lg font-semibold text-gray-900">
                            {rec.expectedYield} tonnes/ha
                          </div>
                        </div>
                        
                        <div className="bg-gray-50 p-3 rounded-md">
                          <div className="text-sm text-gray-600">Suitability Score</div>
                          <div className="text-lg font-semibold text-gray-900">
                            {(rec.confidenceScore * 100).toFixed(0)}%
                          </div>
                        </div>
                        
                        <div className="bg-gray-50 p-3 rounded-md">
                          <div className="text-sm text-gray-600">Est. Profit</div>
                          <div className={`text-lg font-semibold ${getProfitColor(rec.profitEstimate)}`}>
                            ₹{rec.profitEstimate?.toLocaleString() || 'N/A'}
                          </div>
                        </div>

                        {rec.isMarketEnhanced && rec.marketScore !== undefined && (
                          <div className="bg-blue-50 p-3 rounded-md">
                            <div className="text-sm text-blue-600">Market Score</div>
                            <div className="text-lg font-semibold text-blue-900">
                              {(rec.marketScore * 100).toFixed(0)}%
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Market Intelligence Section */}
                      {rec.isMarketEnhanced && rec.combinedScore !== undefined && (
                        <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg border mb-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="text-sm font-medium text-gray-900">Market Intelligence</h4>
                            <div className="bg-white px-2 py-1 rounded-full">
                              <span className="text-sm font-semibold text-green-600">
                                {(rec.combinedScore * 100).toFixed(1)}% Overall Score
                              </span>
                            </div>
                          </div>
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            {rec.currentMarketPrice && (
                              <div>
                                <span className="text-gray-600">Current Price:</span>
                                <span className="ml-1 font-medium">₹{rec.currentMarketPrice}/quintal</span>
                              </div>
                            )}
                            {rec.priceTrend && (
                              <div>
                                <span className="text-gray-600">Price Trend:</span>
                                <span className={`ml-1 font-medium ${
                                  rec.priceTrend === 'Rising' ? 'text-green-600' : 
                                  rec.priceTrend === 'Falling' ? 'text-red-600' : 'text-gray-600'
                                }`}>
                                  {rec.priceTrend}
                                </span>
                              </div>
                            )}
                            {rec.roiPercentage && (
                              <div>
                                <span className="text-gray-600">Expected ROI:</span>
                                <span className="ml-1 font-medium text-green-600">{rec.roiPercentage.toFixed(1)}%</span>
                              </div>
                            )}
                            {rec.profitPerAcre && (
                              <div>
                                <span className="text-gray-600">Profit/Acre:</span>
                                <span className="ml-1 font-medium text-green-600">₹{rec.profitPerAcre.toLocaleString()}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

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
              </div>
            )}

            {/* Empty State */}
            {!hasData && !loading && (
              <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
                <InformationCircleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Ready for AI Analysis
                </h3>
                <p className="text-gray-600 mb-6">
                  Fill in your farm conditions and click "{useMarketData ? 'Get Market-Enhanced' : 'Get AI'} Recommendations" 
                  to receive personalized crop suggestions {useMarketData ? 'with real-time market intelligence' : 'powered by machine learning'}.
                </p>
                <div className="text-sm text-gray-500">
                  Our AI model analyzes {modelInfo?.total_features ? (modelInfo.total_features + ' features and ') : ''}2000+ agricultural data points{useMarketData ? ' plus live market data' : ''} to provide accurate recommendations.
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