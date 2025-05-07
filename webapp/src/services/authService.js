/**
 * Authentication Service for GeoFinance
 * Handles login, logout, and session management
 */
import { buildApiUrl } from '../config/api';

// Check if user is logged in
export const isAuthenticated = () => {
  const user = localStorage.getItem('user');
  return !!user; // Convert to boolean
};

// Get current user information
export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  if (!userStr) return null;
  
  try {
    return JSON.parse(userStr);
  } catch (e) {
    console.error('Error parsing user data:', e);
    return null;
  }
};

// Login user and store credentials
export const login = async (username, password, remember = false) => {
  try {
    console.log(`Attempting to login at: ${buildApiUrl('api/login')}`);
    
    // Make sure we're using the correct headers for CORS
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
    
    console.log('Headers:', headers);
    
    const body = JSON.stringify({
      username,
      password,
      remember
    });
    console.log('Request body:', body);

    const response = await fetch(buildApiUrl('api/login'), {
      method: 'POST',
      headers: headers,
      body: body,
      credentials: 'include',  // Important for cookies/session
      mode: 'cors'  // Explicitly set mode to cors
    });
    
    console.log('Response status:', response.status);
    
    const data = await response.json();
    console.log('Response data:', data);
    
    if (!response.ok) {
      throw new Error(data.message || 'Authentication failed');
    }
    
    // Store user data in localStorage (no token needed with sessions)
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

// Logout user
export const logout = async () => {
  try {
    // Call the logout endpoint to clear the session
    await fetch(buildApiUrl('api/logout'), {
      method: 'POST',
      credentials: 'include',  // Important for cookies/session
      mode: 'cors'
    });
  } catch (err) {
    console.error('Logout API error:', err);
  } finally {
    // Clear local storage regardless of API call success
    localStorage.removeItem('user');
  }
};

// Add authentication headers to requests (not needed with session auth)
export const getAuthHeaders = () => {
  return {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };
};

// For demonstration/development purposes only
// Provides a fake login when backend is not available
export const fakeDemoLogin = (username, password) => {
  if (username === 'admin' && password === 'admin') {
    const fakeUser = {
      id: 1,
      username: 'admin',
      name: 'Administrator',
      role: 'admin'
    };
    
    localStorage.setItem('user', JSON.stringify(fakeUser));
    
    return Promise.resolve({
      user: fakeUser
    });
  }
  
  return Promise.reject(new Error('Invalid credentials'));
};