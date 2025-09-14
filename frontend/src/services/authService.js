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
      const response = await ApiService.login({ phone_number: phoneNumber, password });
      
      if (response.access_token && response.user) {
        this.setAuthData(response.access_token, response.user);
        return { success: true, user: response.user };
      }
      
      return { success: false, error: 'Invalid credentials' };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      };
    }
  }
  
  // Register new user
  static async register(userData) {
    try {
      const response = await ApiService.register(userData);
      
      if (response.access_token && response.user) {
        this.setAuthData(response.access_token, response.user);
        return { success: true, user: response.user };
      }
      
      return { success: false, error: 'Registration failed' };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Registration failed' 
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
  
  // Refresh user data
  static async refreshUser() {
    try {
      const response = await ApiService.getCurrentUser();
      if (response.user) {
        localStorage.setItem(this.USER_KEY, JSON.stringify(response.user));
        return response.user;
      }
    } catch (error) {
      console.error('Failed to refresh user data:', error);
      // If refresh fails, clear auth data
      this.clearAuthData();
      throw error;
    }
  }
}

export default AuthService;