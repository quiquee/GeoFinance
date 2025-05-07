/**
 * API Configuration Settings
 * Centralized configuration for backend API connections
 */

// Backend server configuration
const API_CONFIG = {
  baseURL: 'http://127.0.0.1:5000',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};

// Helper function to build API URLs
export const buildApiUrl = (endpoint) => {
  // Remove leading slash if present
  const path = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  return `${API_CONFIG.baseURL}/${path}`;
};

// Helper function to get default headers
export const getHeaders = () => {
  return { ...API_CONFIG.headers };
};

// Function to update API configuration (useful for environment-specific settings)
export const updateApiConfig = (newConfig) => {
  Object.assign(API_CONFIG, newConfig);
};

export default API_CONFIG;