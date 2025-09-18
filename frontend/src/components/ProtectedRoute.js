/**
 * Protected Route Component
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import AuthService from '../services/authService';

const ProtectedRoute = ({ children }) => {
  const location = useLocation();
  const isAuthenticated = AuthService.isAuthenticated();
  
  console.log('🛡️  ProtectedRoute: Checking authentication...');
  console.log('📍 ProtectedRoute: Current location:', location.pathname);
  console.log('🔐 ProtectedRoute: Is authenticated:', isAuthenticated);
  console.log('🎫 ProtectedRoute: Token exists:', !!AuthService.getToken());
  console.log('👤 ProtectedRoute: User data:', AuthService.getUser());

  if (!isAuthenticated) {
    console.log('🚫 ProtectedRoute: Not authenticated, redirecting to login');
    // Redirect to login page with return url
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  console.log('✅ ProtectedRoute: Authenticated, rendering children');
  return children;
};

export default ProtectedRoute;