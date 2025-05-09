import { buildApiUrl } from '../config/api';
import { getAuthHeaders } from './authService';
import { triggerFinancialDataRefresh } from './financialDataService';

/**
 * Handles API requests with consistent error handling and authentication
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {object} options - Fetch options
 * @returns {Promise} - Response promise
 */
const apiFetch = async (endpoint, options = {}) => {
  const url = buildApiUrl(endpoint);
  
  // Add auth headers to all requests
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeaders(),
    ...options.headers
  };
  
  const fetchOptions = {
    ...options,
    headers,
    credentials: 'include'
  };
  
  try {
    const response = await fetch(url, fetchOptions);
    
    // If this was a data-modifying request and it was successful, trigger a refresh
    const method = options.method?.toUpperCase() || 'GET';
    const isDataModifying = ['POST', 'PUT', 'DELETE'].includes(method);
    
    if (isDataModifying && response.ok) {
      triggerFinancialDataRefresh();
    }
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `API request failed with status ${response.status}`);
    }
    
    // For empty responses (like some DELETE operations)
    if (response.status === 204) {
      return { data: null };
    }
    
    const data = await response.json();
    return { data, status: response.status };
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

/**
 * Make a GET request to the API
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {object} params - URL parameters
 * @returns {Promise} - Response promise with data
 */
export const get = async (endpoint, params = {}) => {
  // Convert params to URL search params if provided
  let url = endpoint;
  if (Object.keys(params).length) {
    const searchParams = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value);
      }
    }
    url = `${endpoint}?${searchParams.toString()}`;
  }
  
  return apiFetch(url);
};

/**
 * Make a POST request to the API
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {object} data - Request body data
 * @returns {Promise} - Response promise with data
 */
export const post = (endpoint, data = {}) => {
  return apiFetch(endpoint, {
    method: 'POST',
    body: JSON.stringify(data)
  });
};

/**
 * Make a PUT request to the API
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {object} data - Request body data
 * @returns {Promise} - Response promise with data
 */
export const put = (endpoint, data = {}) => {
  return apiFetch(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
};

/**
 * Make a DELETE request to the API
 * @param {string} endpoint - API endpoint (without base URL)
 * @returns {Promise} - Response promise with data
 */
export const del = (endpoint) => {
  return apiFetch(endpoint, {
    method: 'DELETE'
  });
};

export default {
  get,
  post,
  put,
  delete: del
};