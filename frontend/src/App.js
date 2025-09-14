import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Components
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import FarmProfile from './pages/FarmProfile';
import AdminDashboard from './pages/AdminDashboard';
import CropRecommendation from './pages/CropRecommendation';

// Services
import OfflineService from './services/offlineService';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: (failureCount, error) => {
        // Don't retry on 4xx errors except 408, 429
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          if (error.response.status === 408 || error.response.status === 429) {
            return failureCount < 2;
          }
          return false;
        }
        return failureCount < 3;
      },
    },
  },
});

function App() {
  useEffect(() => {
    // Initialize offline service
    OfflineService.initDB();
    OfflineService.setupNetworkListeners();
    
    // Clean up old data periodically
    const cleanup = () => {
      OfflineService.cleanupOldData();
    };
    
    // Run cleanup once on app start
    cleanup();
    
    // Set up periodic cleanup (every 24 hours)
    const cleanupInterval = setInterval(cleanup, 24 * 60 * 60 * 1000);
    
    return () => {
      clearInterval(cleanupInterval);
    };
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            {/* Protected Routes with Layout */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/farm/*" element={
              <ProtectedRoute>
                <Layout>
                  <FarmProfile />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/crops/*" element={
              <ProtectedRoute>
                <Layout>
                  <CropRecommendation />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/weather" element={
              <ProtectedRoute>
                <Layout>
                  <div className="p-6">
                    <h1 className="text-2xl font-bold text-gray-900 mb-6">Weather Information</h1>
                    <div className="bg-white rounded-lg shadow p-6">
                      <p className="text-gray-600">Weather forecasts and alerts coming soon...</p>
                    </div>
                  </div>
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/market" element={
              <ProtectedRoute>
                <Layout>
                  <div className="p-6">
                    <h1 className="text-2xl font-bold text-gray-900 mb-6">Market Prices</h1>
                    <div className="bg-white rounded-lg shadow p-6">
                      <p className="text-gray-600">Live mandi prices coming soon...</p>
                    </div>
                  </div>
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/analytics" element={
              <ProtectedRoute>
                <Layout>
                  <div className="p-6">
                    <h1 className="text-2xl font-bold text-gray-900 mb-6">Analytics Dashboard</h1>
                    <div className="bg-white rounded-lg shadow p-6">
                      <p className="text-gray-600">Farm analytics and insights coming soon...</p>
                    </div>
                  </div>
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/admin" element={
              <ProtectedRoute>
                <Layout>
                  <AdminDashboard />
                </Layout>
              </ProtectedRoute>
            } />
            
            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;