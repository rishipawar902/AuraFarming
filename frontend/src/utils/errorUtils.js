/**
 * Utility function to safely convert error objects to displayable strings
 */

/**
 * Convert various error formats to user-friendly strings
 * @param {any} error - Error object, string, or array
 * @returns {string} - User-friendly error message
 */
export const formatErrorMessage = (error) => {
  // If it's already a string, return it
  if (typeof error === 'string') {
    return error;
  }
  
  // If it's null or undefined, return default message
  if (!error) {
    return 'An error occurred';
  }
  
  // Handle Pydantic validation errors (array of error objects)
  if (Array.isArray(error)) {
    if (error.length === 0) {
      return 'Validation error occurred';
    }
    
    // Extract messages from validation errors
    const messages = error.map(err => {
      if (typeof err === 'string') {
        return err;
      }
      if (err.msg) {
        return err.msg;
      }
      if (err.message) {
        return err.message;
      }
      if (err.type && err.loc) {
        const field = Array.isArray(err.loc) ? err.loc.join('.') : err.loc;
        return `${field}: ${err.type}`;
      }
      return 'Validation error';
    });
    
    return messages.join('; ');
  }
  
  // Handle error objects
  if (typeof error === 'object') {
    // Standard error object with message
    if (error.message) {
      return error.message;
    }
    
    // API error response with detail
    if (error.detail) {
      return error.detail;
    }
    
    // Pydantic validation error object
    if (error.msg) {
      return error.msg;
    }
    
    // Error with type and location info
    if (error.type && error.loc) {
      const field = Array.isArray(error.loc) ? error.loc.join('.') : error.loc;
      return `${field}: ${error.type}`;
    }
    
    // Try to stringify if it's a simple object
    try {
      const keys = Object.keys(error);
      if (keys.length === 1 && typeof error[keys[0]] === 'string') {
        return error[keys[0]];
      }
      
      // If it has multiple properties, try to find a readable one
      for (const key of ['error', 'message', 'detail', 'msg', 'description']) {
        if (error[key] && typeof error[key] === 'string') {
          return error[key];
        }
      }
      
      return 'An error occurred with the submitted data';
    } catch (e) {
      return 'An error occurred';
    }
  }
  
  // Fallback for other types
  return String(error);
};

/**
 * Safe error renderer component to prevent React rendering errors
 * @param {any} error - Error to display
 * @returns {string} - Safe string to render
 */
export const safeErrorRender = (error) => {
  try {
    return formatErrorMessage(error);
  } catch (e) {
    console.error('Error formatting error message:', e);
    return 'An error occurred';
  }
};

/**
 * Extract error message from axios error response
 * @param {object} error - Axios error object
 * @returns {string} - User-friendly error message
 */
export const extractApiErrorMessage = (error) => {
  if (!error) {
    return 'An unknown error occurred';
  }
  
  // Check for response data first
  if (error.response?.data) {
    return formatErrorMessage(error.response.data);
  }
  
  // Check for direct error message
  if (error.message) {
    return error.message;
  }
  
  // Fallback
  return 'An error occurred while processing your request';
};

export default {
  formatErrorMessage,
  safeErrorRender,
  extractApiErrorMessage
};