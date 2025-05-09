/**
 * Financial Data Service
 * Provides utility functions to trigger financial data refresh events
 */

/**
 * Triggers a financial data updated event that will cause the FinancialBanner
 * to refresh its data
 */
export const triggerFinancialDataRefresh = () => {
  // Create and dispatch custom event that FinancialBanner listens for
  const event = new CustomEvent('financial-data-updated');
  window.dispatchEvent(event);
};

/**
 * Wraps a fetch operation for POST/PUT/DELETE requests and automatically
 * triggers a financial data refresh when the operation is complete
 * @param {string} url - The URL to fetch
 * @param {object} options - Fetch options (method, body, headers, etc.)
 * @returns {Promise} - The fetch promise
 */
export const fetchWithRefresh = async (url, options = {}) => {
  try {
    const response = await fetch(url, options);
    
    // If this was a data-modifying operation (POST, PUT, DELETE) and it was successful,
    // trigger a refresh of financial data
    const isDataModifying = ['POST', 'PUT', 'DELETE'].includes(options.method?.toUpperCase());
    if (isDataModifying && response.ok) {
      triggerFinancialDataRefresh();
    }
    
    return response;
  } catch (error) {
    console.error('Fetch operation failed:', error);
    throw error;
  }
};