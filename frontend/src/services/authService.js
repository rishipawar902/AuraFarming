/**
 * Authentication Service
 */

import ApiService from './apiService';

export class AuthService {
  static TOKEN_KEY = 'auth_token';
  static USER_KEY = 'user_data';
  
  // Get stored token
  static getToken() {
    return localStorage.getItem(this.TOKEN_KEY);
  }
  
  // Get stored user data
  static getUser() {
    const userData = localStorage.getItem(this.USER_KEY);
    return userData ? JSON.parse(userData) : null;
  }
  
  // Check if user is authenticated
  static isAuthenticated() {
    return !!this.getToken();
  }
  
  // Store authentication data
  static setAuthData(token, user) {
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }
  
  // Clear authentication data
  static clearAuthData() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }
  
  // Login user
  static async login(phoneNumber, password) {
    try {
      console.log('🔐 AuthService: Starting login for', phoneNumber);
      
      const response = await ApiService.login({ 
        phone: phoneNumber,
        password: password 
      });
      
      console.log('📡 AuthService: Login API response:', response);
      
      if (response.access_token) {
        console.log('🎫 AuthService: Token received, getting user data...');
        
        // Get user data from the backend
        const userData = await this.getCurrentUser(response.access_token);
        
        console.log('👤 AuthService: User data:', userData);
        
        this.setAuthData(response.access_token, userData);
        
        console.log('💾 AuthService: Data stored in localStorage');
        console.log('🔍 AuthService: Authentication check:', this.isAuthenticated());
        
        return { success: true, user: userData };
      }
      
      console.log('❌ AuthService: No access token in response');
      return { success: false, error: 'Invalid credentials' };
    } catch (error) {
      console.error('❌ AuthService: Login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || error.response?.data?.error || 'Login failed' 
      };
    }
  }
  
  // Register new user
  static async register(userData) {
    try {
      const response = await ApiService.register(userData);
      
      if (response.access_token) {
        // Get user data from the backend after registration
        const userProfile = await this.getCurrentUser(response.access_token);
        
        this.setAuthData(response.access_token, userProfile);
        return { success: true, user: userProfile };
      }
      
      return { success: false, error: 'Registration failed' };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.response?.data?.error || 'Registration failed' 
      };
    }
  }
  
  // Logout user
  static async logout() {
    try {
      await ApiService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.clearAuthData();
    }
  }
  
  // Get current user data from backend
  static async getCurrentUser(token = null) {
    try {
      // Temporarily set the token for this request if provided
      const oldToken = this.getToken();
      if (token) {
        localStorage.setItem(this.TOKEN_KEY, token);
      }
      
      const response = await ApiService.getCurrentUser();
      
      // Restore old token if we temporarily set one
      if (token && oldToken) {
        localStorage.setItem(this.TOKEN_KEY, oldToken);
      }
      
      // The API response structure is { success: true, message: "...", data: { user_info } }
      // ApiService.getCurrentUser() returns response.data (the parsed JSON)
      // So the user data is in response.data (the user_object from API's data field)
      if (response && response.data) {
        return response.data;
      }
      throw new Error('No user data received');
    } catch (error) {
      console.error('Failed to get current user:', error);
      throw error;
    }
  }
  
  // Refresh user data
  static async refreshUser() {
    try {
      const userData = await this.getCurrentUser();
      localStorage.setItem(this.USER_KEY, JSON.stringify(userData));
      return userData;
    } catch (error) {
      console.error('Failed to refresh user data:', error);
      // If refresh fails, clear auth data
      this.clearAuthData();
      throw error;
    }
  }
}

export default AuthService;