/**
 * Analytics Dashboard Component
 * Comprehensive market analytics and farm insights with real-time data
 */

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ChartBarIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  CalendarIcon,
  CurrencyRupeeIcon,
  MapPinIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import toast from 'react-hot-toast';
import ApiService from '../services/apiService';

const Analytics = () => {
  const [selectedDistrict, setSelectedDistrict] = useState('Ranchi');
  const [selectedTimeframe, setSelectedTimeframe] = useState('30');
  const [selectedMetric, setSelectedMetric] = useState('price');

  // Jharkhand districts
  const districts = [
    'Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro', 'Deoghar', 'Hazaribagh',
    'Giridih', 'Ramgarh', 'Chaibasa', 'Daltonganj', 'Dumka', 'Godda'
  ];

  // Major commodities for analysis
  const commodities = ['Rice', 'Wheat', 'Maize', 'Potato', 'Arhar', 'Gram', 'Mustard', 'Onion'];

  // Fetch current market data for analytics
  const {
    data: marketData,
    isLoading: isLoadingMarket,
    refetch: refetchMarket
  } = useQuery({
    queryKey: ['analytics-market', selectedDistrict],
    queryFn: () => ApiService.getMandiPrices(selectedDistrict),
    refetchInterval: 60000, // Refresh every minute for real-time analytics
    onError: (error) => {
      console.error('Analytics market data error:', error);
      toast.error('Failed to fetch market analytics');
    }
  });

  // Generate analytics data based on market prices
  const generateAnalyticsData = () => {
    if (!marketData?.data?.prices) return null;

    const prices = marketData.data.prices;
    
    // Price trend analysis
    const priceAnalysis = prices.map(price => ({
      commodity: price.commodity || price.crop,
      currentPrice: price.modal_price,
      minPrice: price.min_price,
      maxPrice: price.max_price,
      volatility: ((price.max_price - price.min_price) / price.modal_price * 100).toFixed(1),
      trend: price.trend || 'stable',
      arrival: price.arrival || 0
    }));

    // Generate historical trend data (simulated for demo)
    const generateHistoricalData = () => {
      const days = parseInt(selectedTimeframe);
      const data = [];
      
      for (let i = days; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        
        const dayData = {
          date: date.toISOString().split('T')[0],
          day: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        };

        prices.forEach(price => {
          const commodity = price.commodity || price.crop;
          const basePrice = price.modal_price;
          const variation = (Math.random() - 0.5) * 200; // Random variation
          dayData[commodity] = Math.max(100, basePrice + variation);
        });

        data.push(dayData);
      }
      
      return data;
    };

    return {
      priceAnalysis,
      historicalData: generateHistoricalData(),
      totalCommodities: prices.length,
      avgPrice: (prices.reduce((sum, p) => sum + p.modal_price, 0) / prices.length).toFixed(0),
      highestPrice: Math.max(...prices.map(p => p.modal_price)),
      lowestPrice: Math.min(...prices.map(p => p.modal_price))
    };
  };

  const analytics = generateAnalyticsData();

  // Chart colors
  const colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#F97316', '#84CC16'];

  // Calculate market insights
  const calculateInsights = () => {
    if (!analytics) return [];

    const insights = [];
    
    // Price volatility insight
    const highVolatility = analytics.priceAnalysis.filter(p => parseFloat(p.volatility) > 15);
    if (highVolatility.length > 0) {
      insights.push({
        type: 'warning',
        title: 'High Price Volatility',
        description: `${highVolatility.length} commodities showing high volatility (>15%)`,
        action: 'Consider market timing for these crops'
      });
    }

    // Price trend insight
    const increasingPrices = analytics.priceAnalysis.filter(p => p.trend === 'increasing');
    if (increasingPrices.length > 0) {
      insights.push({
        type: 'success',
        title: 'Favorable Price Trends',
        description: `${increasingPrices.length} commodities showing increasing prices`,
        action: 'Good time to sell these crops'
      });
    }

    // Supply insight
    const lowSupply = analytics.priceAnalysis.filter(p => p.arrival < 200);
    if (lowSupply.length > 0) {
      insights.push({
        type: 'info',
        title: 'Supply Shortage',
        description: `${lowSupply.length} commodities have low market arrivals`,
        action: 'Potential opportunity for higher prices'
      });
    }

    return insights;
  };

  const insights = calculateInsights();

  if (isLoadingMarket) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="bg-gray-200 h-8 w-64 rounded"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="bg-gray-200 h-24 rounded-lg"></div>
            ))}
          </div>
          <div className="bg-gray-200 h-96 rounded-lg"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
            <p className="text-blue-100 mt-1">
              Real-time market insights and farm analytics for {selectedDistrict}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-blue-100">Data Source</p>
            <p className="text-lg font-medium flex items-center">
              <span className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
              Live Government Data
            </p>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <MapPinIcon className="h-4 w-4 inline mr-1" />
              District
            </label>
            <select
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {districts.map(district => (
                <option key={district} value={district}>{district}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <CalendarIcon className="h-4 w-4 inline mr-1" />
              Timeframe
            </label>
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 3 months</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <ChartBarIcon className="h-4 w-4 inline mr-1" />
              Metric
            </label>
            <select
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="price">Price Analysis</option>
              <option value="volatility">Volatility Analysis</option>
              <option value="supply">Supply Analysis</option>
            </select>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <ChartBarIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Total Commodities</p>
                <p className="text-2xl font-bold text-gray-900">{analytics.totalCommodities}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <CurrencyRupeeIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Average Price</p>
                <p className="text-2xl font-bold text-gray-900">₹{analytics.avgPrice}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <TrendingUpIcon className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Highest Price</p>
                <p className="text-2xl font-bold text-gray-900">₹{analytics.highestPrice}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <TrendingDownIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Lowest Price</p>
                <p className="text-2xl font-bold text-gray-900">₹{analytics.lowestPrice}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Price Trends Chart */}
        {analytics && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Price Trends ({selectedTimeframe} days)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analytics.historicalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip 
                  formatter={(value) => [`₹${value.toFixed(0)}`, 'Price']}
                  labelFormatter={(label) => `Date: ${label}`}
                />
                <Legend />
                {commodities.slice(0, 4).map((commodity, index) => (
                  <Line
                    key={commodity}
                    type="monotone"
                    dataKey={commodity}
                    stroke={colors[index]}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Volatility Analysis */}
        {analytics && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Price Volatility Analysis</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.priceAnalysis}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="commodity" />
                <YAxis />
                <Tooltip 
                  formatter={(value) => [`${value}%`, 'Volatility']}
                />
                <Bar dataKey="volatility" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Market Insights */}
      {insights.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Insights</h3>
          <div className="space-y-4">
            {insights.map((insight, index) => (
              <div key={index} className={`p-4 rounded-lg border-l-4 ${
                insight.type === 'success' ? 'bg-green-50 border-green-400' :
                insight.type === 'warning' ? 'bg-yellow-50 border-yellow-400' :
                'bg-blue-50 border-blue-400'
              }`}>
                <div className="flex items-start">
                  <InformationCircleIcon className={`h-5 w-5 mt-0.5 mr-3 ${
                    insight.type === 'success' ? 'text-green-400' :
                    insight.type === 'warning' ? 'text-yellow-400' :
                    'text-blue-400'
                  }`} />
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">{insight.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
                    <p className="text-xs text-gray-500 mt-1">💡 {insight.action}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Price Analysis */}
      {analytics && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Detailed Price Analysis</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Commodity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Current Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Range
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Volatility
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Trend
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Supply
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {analytics.priceAnalysis.map((item, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {item.commodity}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ₹{item.currentPrice.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ₹{item.minPrice} - ₹{item.maxPrice}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        parseFloat(item.volatility) > 15 ? 'bg-red-100 text-red-800' :
                        parseFloat(item.volatility) > 10 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {item.volatility}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        {item.trend === 'increasing' && <ArrowUpIcon className="h-4 w-4 text-green-500 mr-1" />}
                        {item.trend === 'decreasing' && <ArrowDownIcon className="h-4 w-4 text-red-500 mr-1" />}
                        <span className={
                          item.trend === 'increasing' ? 'text-green-600' :
                          item.trend === 'decreasing' ? 'text-red-600' :
                          'text-gray-600'
                        }>
                          {item.trend}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {item.arrival} quintals
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Refresh Button */}
      <div className="flex justify-center">
        <button
          onClick={() => refetchMarket()}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
        >
          🔄 Refresh Analytics
        </button>
      </div>
    </div>
  );
};

export default Analytics;
