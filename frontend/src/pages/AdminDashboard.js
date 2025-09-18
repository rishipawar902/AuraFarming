/**
 * Admin Dashboard Page Component
 */

import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  UserGroupIcon, 
  MapIcon,
  TruckIcon,
  CurrencyRupeeIcon,
  ClockIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  DocumentArrowDownIcon
} from '@heroicons/react/24/outline';
import { useQuery } from '@tanstack/react-query';
import ApiService from '../services/apiService';

const AdminDashboard = () => {
  const [dateRange, setDateRange] = useState('7d');
  const [selectedDistrict, setSelectedDistrict] = useState('all');

  // Fetch admin statistics
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['adminStats', dateRange],
    queryFn: () => ApiService.getAdminStats(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Fetch crop adoption data
  const { data: cropAdoption } = useQuery({
    queryKey: ['cropAdoption', selectedDistrict],
    queryFn: () => ApiService.getCropAdoptionData(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });

  // Fetch district-wise data
  const { data: districtData } = useQuery({
    queryKey: ['districtData'],
    queryFn: () => ApiService.getDistrictWiseData(),
    staleTime: 15 * 60 * 1000, // 15 minutes
  });

  // Fetch ML performance metrics
  const { data: mlMetrics } = useQuery({
    queryKey: ['mlMetrics'],
    queryFn: () => ApiService.getMLPerformanceMetrics(),
    staleTime: 30 * 60 * 1000, // 30 minutes
  });

  const handleExportData = (type) => {
    // Export real data from APIs
    const data = JSON.stringify(
      type === 'farmers' 
        ? districtData?.data || [] 
        : cropAdoption?.data || [], 
      null, 
      2
    );
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${type}-data-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const StatCard = ({ title, value, icon: Icon, growth, color = 'blue' }) => (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {growth !== undefined && (
            <div className={`flex items-center mt-2 text-sm ${
              growth >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {growth >= 0 ? (
                <ArrowUpIcon className="h-4 w-4 mr-1" />
              ) : (
                <ArrowDownIcon className="h-4 w-4 mr-1" />
              )}
              <span>{Math.abs(growth)}% from last month</span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-full bg-${color}-100`}>
          <Icon className={`h-8 w-8 text-${color}-600`} />
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Monitor and analyze SmartKhet platform performance
          </p>
        </div>
        
        {/* Date Range Selector */}
        <div className="flex items-center space-x-4">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          
          <button
            onClick={() => handleExportData('summary')}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
            Export Data
          </button>
        </div>
      </div>

      {/* Key Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Farmers"
          value={stats?.data?.total_farmers?.toLocaleString() || '0'}
          icon={UserGroupIcon}
          growth={12.5}
          color="blue"
        />
        <StatCard
          title="Active Farms"
          value={stats?.data?.total_farms?.toLocaleString() || '0'}
          icon={MapIcon}
          growth={5.2}
          color="green"
        />
        <StatCard
          title="Recommendations"
          value={stats?.data?.total_recommendations?.toLocaleString() || '0'}
          icon={ChartBarIcon}
          growth={8.3}
          color="purple"
        />
        <StatCard
          title="Popular Crops"
          value={stats?.data?.popular_crops?.length?.toString() || '0'}
          icon={TruckIcon}
          growth={2.1}
          color="yellow"
        />
      </div>

      {/* Crop Adoption Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900">Crop Adoption Rates</h2>
            <button
              onClick={() => handleExportData('crops')}
              className="text-sm text-green-600 hover:text-green-500 font-medium"
            >
              Export →
            </button>
          </div>
          
          <div className="space-y-4">
            {cropAdoption?.data?.map((crop, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-medium text-gray-900">{crop.crop_name || crop.crop}</h3>
                  <span className="text-sm text-gray-600">{crop.farmers || crop.farmer_count || 0} farmers</span>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                  <div
                    className="bg-green-600 h-2 rounded-full"
                    style={{ width: `${crop.adoption_rate || crop.adoption || 0}%` }}
                  ></div>
                </div>
                
                <div className="flex justify-between text-sm text-gray-600">
                  <span>{crop.adoption_rate || crop.adoption || 0}% adoption rate</span>
                  <span>{crop.avg_yield || crop.yield || 0} tons/acre avg yield</span>
                </div>
              </div>
            )) || []}
            
            {(!cropAdoption?.data || cropAdoption.data.length === 0) && (
              <div className="text-center py-8 text-gray-500">
                No crop adoption data available
              </div>
            )}
          </div>
        </div>

        {/* District Performance */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900">District Performance</h2>
            <button
              onClick={() => handleExportData('farmers')}
              className="text-sm text-green-600 hover:text-green-500 font-medium"
            >
              Export →
            </button>
          </div>
          
          <div className="space-y-4">
            {districtData?.data?.map((district, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-medium text-gray-900">{district.district_name || district.name}</h3>
                    <p className="text-sm text-gray-600">
                      {district.farmer_count || district.farmers || 0} farmers • {district.recommendation_count || district.recommendations || 0} recommendations
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-gray-900">
                      {district.avg_yield || district.avgYield || 0} T/A
                    </div>
                    <div className="text-sm text-gray-600">avg yield</div>
                  </div>
                </div>
              </div>
            )) || []}
            
            {(!districtData?.data || districtData.data.length === 0) && (
              <div className="text-center py-8 text-gray-500">
                No district data available
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ML Performance Metrics */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">ML Model Performance</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-3xl font-bold text-blue-600">92.3%</div>
            <div className="text-sm text-blue-800 mt-1">Prediction Accuracy</div>
            <div className="text-xs text-blue-600 mt-1">↑ 2.1% from last month</div>
          </div>
          
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-3xl font-bold text-green-600">1.2s</div>
            <div className="text-sm text-green-800 mt-1">Avg Response Time</div>
            <div className="text-xs text-green-600 mt-1">↓ 0.3s from last month</div>
          </div>
          
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-3xl font-bold text-purple-600">847</div>
            <div className="text-sm text-purple-800 mt-1">Models Trained</div>
            <div className="text-xs text-purple-600 mt-1">↑ 15% from last month</div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Recent Activity</h2>
        
        <div className="space-y-4">
          {[
            { time: '2 hours ago', action: 'New farmer registration', details: 'Ramesh Kumar from Ranchi district', type: 'user' },
            { time: '4 hours ago', action: 'Crop recommendation generated', details: '145 recommendations for Kharif season', type: 'system' },
            { time: '6 hours ago', action: 'Weather alert sent', details: 'Heavy rainfall warning for 12 districts', type: 'alert' },
            { time: '1 day ago', action: 'Market price update', details: 'Rice prices updated for all mandis', type: 'data' },
            { time: '2 days ago', action: 'ML model retrained', details: 'Crop recommendation model v2.1 deployed', type: 'system' }
          ].map((activity, index) => (
            <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className={`flex-shrink-0 w-2 h-2 mt-2 rounded-full ${
                activity.type === 'user' ? 'bg-blue-500' :
                activity.type === 'system' ? 'bg-green-500' :
                activity.type === 'alert' ? 'bg-red-500' : 'bg-gray-500'
              }`}></div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-gray-900">{activity.action}</span>
                  <span className="text-xs text-gray-500">{activity.time}</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{activity.details}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;