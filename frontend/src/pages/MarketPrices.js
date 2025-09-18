/**
 * Market Prices Page Component
 * Displays live mandi prices, trends, and market insights
 */

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  CurrencyRupeeIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  MapPinIcon,
  ClockIcon,
  ChartBarIcon,
  InformationCircleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import ApiService from '../services/apiService';
import AuthService from '../services/authService';
import OfflineService from '../services/offlineService';
import toast from 'react-hot-toast';

const MarketPrices = () => {
  const [selectedDistrict, setSelectedDistrict] = useState('Ranchi');
  const [selectedCrop, setSelectedCrop] = useState('');
  const [showTrends, setShowTrends] = useState(false);
  const [trendsCrop, setTrendsCrop] = useState('');
  
  // Get user data to default to their district
  useEffect(() => {
    const user = AuthService.getUser();
    if (user?.farm?.location?.district) {
      setSelectedDistrict(user.farm.location.district);
    }
  }, []);

  // Jharkhand districts
  const districts = [
    'Ranchi', 'Dhanbad', 'Jamshedpur', 'Bokaro', 'Deoghar',
    'Hazaribagh', 'Giridih', 'Ramgarh', 'Medininagar', 'Chaibasa'
  ];

  // Major crops
  const crops = [
    'Rice', 'Wheat', 'Maize', 'Potato', 'Arhar (Tur)', 'Groundnut',
    'Mustard', 'Gram', 'Soybean', 'Sugarcane', 'Cotton', 'Onion',
    'Tomato', 'Cabbage', 'Cauliflower'
  ];

  // Fetch market prices
  const {
    data: marketData,
    isLoading: isLoadingPrices,
    error: pricesError,
    refetch: refetchPrices
  } = useQuery({
    queryKey: ['market-prices', selectedDistrict, selectedCrop],
    queryFn: () => ApiService.getMandiPrices(selectedDistrict, selectedCrop),
    staleTime: 5 * 60 * 1000, // 5 minutes
    onError: (error) => {
      console.error('Market prices error:', error);
      toast.error('Failed to fetch market prices');
    }
  });

  // Fetch price trends when requested
  const {
    data: trendsData,
    isLoading: isLoadingTrends,
    error: trendsError,
  } = useQuery({
    queryKey: ['price-trends', trendsCrop],
    queryFn: () => ApiService.getPriceTrends(trendsCrop, 30),
    enabled: showTrends && !!trendsCrop,
    staleTime: 10 * 60 * 1000, // 10 minutes
    onError: (error) => {
      console.error('Price trends error:', error);
      toast.error('Failed to fetch price trends');
    }
  });

  const handleShowTrends = (crop) => {
    setTrendsCrop(crop);
    setShowTrends(true);
  };

  const handleRefresh = () => {
    refetchPrices();
    toast.success('Market data refreshed');
  };

  const getTrendIcon = (trend) => {
    switch (trend?.toLowerCase()) {
      case 'rising':
        return <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />;
      case 'falling':
        return <ArrowTrendingDownIcon className="h-4 w-4 text-red-500" />;
      default:
        return <ArrowUpIcon className="h-4 w-4 text-gray-500" />;
    }
  };

  const getTrendColor = (trend) => {
    switch (trend?.toLowerCase()) {
      case 'rising':
        return 'text-green-600 bg-green-50';
      case 'falling':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(price);
  };

  const formatTime = (dateTime) => {
    return new Date(dateTime).toLocaleString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
      day: '2-digit',
      month: 'short'
    });
  };

  if (pricesError) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <InformationCircleIcon className="mx-auto h-12 w-12 text-red-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading market data</h3>
          <p className="mt-1 text-sm text-gray-500">
            {pricesError.message || 'Please try again later'}
          </p>
          <div className="mt-6">
            <button
              onClick={handleRefresh}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              <ArrowPathIcon className="h-4 w-4 mr-2" />
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Market Prices</h1>
            <p className="text-green-100 mt-1">
              Live mandi prices and market trends for Jharkhand
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-green-100">Last Updated</p>
            <p className="text-lg font-medium">
              {marketData?.data?.freshness === 'real_time' 
                ? '🔴 Real-time' 
                : marketData?.data?.last_updated 
                ? formatTime(marketData.data.last_updated)
                : 'Loading...'
              }
            </p>
            {marketData?.data?.scraping_method === 'aggressive_real_time' && (
              <p className="text-xs text-green-200 mt-1">
                ⚡ Live Government Data
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <MapPinIcon className="h-4 w-4 inline mr-1" />
              Select District
            </label>
            <select
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {districts.map(district => (
                <option key={district} value={district}>{district}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Crop (Optional)
            </label>
            <select
              value={selectedCrop}
              onChange={(e) => setSelectedCrop(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">All Crops</option>
              {crops.map(crop => (
                <option key={crop} value={crop}>{crop}</option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={handleRefresh}
              disabled={isLoadingPrices}
              className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
            >
              <ArrowPathIcon className={`h-4 w-4 mr-2 ${isLoadingPrices ? 'animate-spin' : ''}`} />
              Refresh Data
            </button>
          </div>
        </div>
      </div>

      {/* Market Status */}
      {marketData?.data && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {marketData.data.market_status}
              </div>
              <div className="text-sm text-gray-500">Market Status</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {marketData.data.total_crops}
              </div>
              <div className="text-sm text-gray-500">Crops Listed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {marketData.data.active_traders}
              </div>
              <div className="text-sm text-gray-500">Active Traders</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {selectedDistrict}
              </div>
              <div className="text-sm text-gray-500">Market Location</div>
            </div>
          </div>
        </div>
      )}

      {/* Price Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoadingPrices ? (
          // Loading skeleton
          Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="bg-white rounded-lg shadow p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/3"></div>
            </div>
          ))
        ) : (marketData?.data?.prices?.length > 0 || marketData?.prices?.length > 0) ? (
          (marketData.data?.prices || marketData.prices || []).map((price, index) => (
            <div key={index} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6">
              {/* Crop Header */}
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{price.crop}</h3>
                <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getTrendColor(price.trend)}`}>
                  {getTrendIcon(price.trend)}
                  <span className="ml-1">{price.trend}</span>
                </div>
              </div>

              {/* Price Information */}
              <div className="space-y-3">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Modal Price</span>
                    <span className="text-xl font-bold text-green-600">
                      {formatPrice(price.modal_price)}
                    </span>
                  </div>
                  <div className="text-xs text-gray-400">per quintal</div>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Range</span>
                  <span className="text-gray-900">
                    {formatPrice(price.min_price)} - {formatPrice(price.max_price)}
                  </span>
                </div>

                {price.effective_price && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">After Deductions</span>
                    <span className="text-green-600 font-medium">
                      {formatPrice(price.effective_price)}
                    </span>
                  </div>
                )}

                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Demand</span>
                  <span className={`font-medium ${
                    price.demand === 'High' ? 'text-green-600' :
                    price.demand === 'Medium' ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {price.demand}
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Volume Traded</span>
                  <span className="text-gray-900">{price.volume_traded} qtl</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-4 flex space-x-2">
                <button
                  onClick={() => handleShowTrends(price.crop)}
                  className="flex-1 text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 px-3 rounded-md transition-colors"
                >
                  <ChartBarIcon className="h-3 w-3 inline mr-1" />
                  View Trends
                </button>
                {price.storage_available && (
                  <div className="text-xs text-green-600 py-2 px-3 bg-green-50 rounded-md">
                    Storage Available
                  </div>
                )}
              </div>

              {/* Market Details */}
              <div className="mt-3 pt-3 border-t border-gray-200">
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span className="flex items-center">
                    <ClockIcon className="h-3 w-3 mr-1" />
                    {formatTime(price.date)}
                  </span>
                  <span>{price.market}</span>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full text-center py-12">
            <InformationCircleIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No price data available</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try selecting a different district or crop filter.
            </p>
          </div>
        )}
      </div>

      {/* Price Trends Modal */}
      {showTrends && trendsCrop && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Price Trends - {trendsCrop}
              </h3>
              <button
                onClick={() => setShowTrends(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <span className="sr-only">Close</span>
                ✕
              </button>
            </div>

            {isLoadingTrends ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto"></div>
                <p className="mt-2 text-sm text-gray-500">Loading trends...</p>
              </div>
            ) : trendsError ? (
              <div className="text-center py-8">
                <p className="text-red-600">Failed to load trends data</p>
              </div>
            ) : trendsData?.data ? (
              <div className="space-y-4">
                {/* Trend Summary */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <div>
                      <div className="text-lg font-bold text-gray-900">
                        {formatPrice(trendsData.data.trend_analysis.current_price)}
                      </div>
                      <div className="text-xs text-gray-500">Current Price</div>
                    </div>
                    <div>
                      <div className={`text-lg font-bold ${
                        trendsData.data.trend_analysis.direction === 'Rising' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {trendsData.data.trend_analysis.direction}
                      </div>
                      <div className="text-xs text-gray-500">
                        {trendsData.data.trend_analysis.percentage_change}%
                      </div>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-blue-600">
                        {formatPrice(trendsData.data.trend_analysis.highest_price)}
                      </div>
                      <div className="text-xs text-gray-500">30-Day High</div>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-orange-600">
                        {formatPrice(trendsData.data.trend_analysis.lowest_price)}
                      </div>
                      <div className="text-xs text-gray-500">30-Day Low</div>
                    </div>
                  </div>
                </div>

                {/* Recent Price History */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Recent Prices (Last 7 Days)</h4>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {trendsData.data.price_history.slice(-7).reverse().map((record, index) => (
                      <div key={index} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded">
                        <span className="text-sm text-gray-600">
                          {new Date(record.date).toLocaleDateString('en-IN')}
                        </span>
                        <span className="text-sm font-medium text-gray-900">
                          {formatPrice(record.price)}
                        </span>
                        <span className="text-xs text-gray-500">
                          {record.volume} qtl
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketPrices;
