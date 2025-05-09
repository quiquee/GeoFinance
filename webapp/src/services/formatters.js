/**
 * Utility functions for formatting values in the GeoFinance application
 */

/**
 * Formats a numeric value as currency (USD)
 * @param {number} value - The numeric value to format
 * @returns {string} - Formatted currency string
 */
export function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value || 0);
}

/**
 * Formats a date string into a readable format
 * @param {string} dateString - ISO date string
 * @returns {string} - Formatted date string
 */
export function formatDate(dateString) {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date);
}

/**
 * Formats a date string into a shorter format (MM/DD/YYYY)
 * @param {string} dateString - ISO date string
 * @returns {string} - Formatted short date string
 */
export function formatShortDate(dateString) {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric'
  }).format(date);
}

/**
 * Formats a number with the specified number of decimal places
 * @param {number} value - The numeric value to format
 * @param {number} decimals - Number of decimal places (default: 2)
 * @returns {string} - Formatted number string
 */
export function formatNumber(value, decimals = 2) {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value || 0);
}

/**
 * Formats a percentage value
 * @param {number} value - The numeric value to format (e.g., 0.25 for 25%)
 * @param {number} decimals - Number of decimal places (default: 2)
 * @returns {string} - Formatted percentage string
 */
export function formatPercent(value, decimals = 2) {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value || 0);
}