/**
 * Main Layout Component with Navigation
 */

import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  HomeIcon, 
  BuildingOfficeIcon, 
  MapIcon, 
  CloudIcon, 
  CurrencyRupeeIcon,
  ChartBarIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  WifiIcon,
  SignalSlashIcon
} from '@heroicons/react/24/outline';
import { Toaster } from 'react-hot-toast';
import AuthService from '../services/authService';

const Layout = ({ children }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [user, setUser] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Get user data
    const userData = AuthService.getUser();
    setUser(userData);

    // Network status listeners
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleLogout = async () => {
    try {
      await AuthService.logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const navigation = [
    { 
      name: 'Dashboard', 
      href: '/dashboard', 
      icon: HomeIcon,
      description: 'Overview and quick actions'
    },
    { 
      name: 'My Farm', 
      href: '/farm', 
      icon: BuildingOfficeIcon,
      description: 'Farm profile and management'
    },
    { 
      name: 'Crop Recommendations', 
      href: '/crops', 
      icon: MapIcon,
      description: 'AI-powered crop suggestions'
    },
    { 
      name: 'Weather', 
      href: '/weather', 
      icon: CloudIcon,
      description: 'Weather forecast and alerts'
    },
    { 
      name: 'Market Prices', 
      href: '/market', 
      icon: CurrencyRupeeIcon,
      description: 'Mandi prices and trends'
    },
    { 
      name: 'Analytics', 
      href: '/analytics', 
      icon: ChartBarIcon,
      description: 'Farm performance metrics'
    }
  ];

  const isCurrentPage = (href) => {
    return location.pathname === href || location.pathname.startsWith(href + '/');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation Bar */}
      <nav className="bg-green-600 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Logo and Brand */}
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <img 
                  src="/logo192.png" 
                  alt="SmartKhet" 
                  className="h-8 w-8"
                />
                <span className="ml-2 text-xl font-bold text-white">
                  SmartKhet
                </span>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-4">
              {/* Online/Offline Indicator */}
              <div className={`flex items-center space-x-1 px-2 py-1 rounded text-sm ${
                isOnline 
                  ? 'bg-green-500 text-white' 
                  : 'bg-red-500 text-white'
              }`}>
                {isOnline ? (
                  <>
                    <WifiIcon className="h-4 w-4" />
                    <span>Online</span>
                  </>
                ) : (
                  <>
                    <SignalSlashIcon className="h-4 w-4" />
                    <span>Offline</span>
                  </>
                )}
              </div>

              {/* User Menu */}
              <div className="flex items-center space-x-3">
                <span className="text-white text-sm">
                  {user?.name || 'User'}
                </span>
                <UserCircleIcon className="h-8 w-8 text-white" />
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 text-white hover:text-green-200 transition-colors"
                >
                  <ArrowRightOnRectangleIcon className="h-5 w-5" />
                  <span className="text-sm">Logout</span>
                </button>
              </div>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden flex items-center">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="text-white hover:text-green-200 transition-colors"
              >
                {isMenuOpen ? (
                  <XMarkIcon className="h-6 w-6" />
                ) : (
                  <Bars3Icon className="h-6 w-6" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 bg-green-700">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setIsMenuOpen(false)}
                    className={`flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isCurrentPage(item.href)
                        ? 'bg-green-800 text-white'
                        : 'text-green-100 hover:bg-green-600'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
              
              {/* Mobile User Actions */}
              <div className="border-t border-green-600 mt-3 pt-3">
                <div className="flex items-center px-3 py-2">
                  <UserCircleIcon className="h-6 w-6 text-green-100" />
                  <span className="ml-3 text-green-100">{user?.name || 'User'}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-3 px-3 py-2 text-green-100 hover:bg-green-600 w-full text-left"
                >
                  <ArrowRightOnRectangleIcon className="h-5 w-5" />
                  <span>Logout</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Main Content Area */}
      <div className="flex">
        {/* Desktop Sidebar */}
        <aside className="hidden md:flex md:flex-shrink-0">
          <div className="flex flex-col w-64">
            <div className="flex flex-col h-0 flex-1 bg-white shadow">
              <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
                <nav className="mt-5 flex-1 px-2 space-y-1">
                  {navigation.map((item) => {
                    const Icon = item.icon;
                    return (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={`group flex flex-col items-start px-3 py-3 text-sm font-medium rounded-md transition-colors ${
                          isCurrentPage(item.href)
                            ? 'bg-green-100 text-green-900 border-r-2 border-green-600'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                        }`}
                      >
                        <div className="flex items-center w-full">
                          <Icon className={`mr-3 flex-shrink-0 h-5 w-5 ${
                            isCurrentPage(item.href) ? 'text-green-600' : 'text-gray-400'
                          }`} />
                          {item.name}
                        </div>
                        <span className="mt-1 text-xs text-gray-500 ml-8">
                          {item.description}
                        </span>
                      </Link>
                    );
                  })}
                </nav>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 relative overflow-hidden">
          <div className="h-full">
            {children}
          </div>
        </main>
      </div>

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            style: {
              background: '#059669',
            },
          },
          error: {
            style: {
              background: '#DC2626',
            },
          },
        }}
      />

      {/* Offline Banner */}
      {!isOnline && (
        <div className="fixed bottom-0 left-0 right-0 bg-yellow-500 text-black p-3 text-center z-50">
          <div className="flex items-center justify-center space-x-2">
            <SignalSlashIcon className="h-5 w-5" />
            <span className="font-medium">
              You're offline. Some features may not be available.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default Layout;