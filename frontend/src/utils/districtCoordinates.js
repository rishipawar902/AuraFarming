/**
 * Jharkhand Districts Coordinate Mapping
 * Central coordinates for each district in Jharkhand state
 */

// Central coordinates for all Jharkhand districts
export const JHARKHAND_DISTRICT_COORDINATES = {
  'Bokaro': { latitude: 23.7869, longitude: 85.9568 },
  'Chatra': { latitude: 24.2092, longitude: 84.8722 },
  'Deoghar': { latitude: 24.4823, longitude: 86.6968 },
  'Dhanbad': { latitude: 23.7957, longitude: 86.4304 },
  'Dumka': { latitude: 24.2676, longitude: 87.2498 },
  'East Singhbhum': { latitude: 22.8046, longitude: 86.2029 }, // Jamshedpur
  'Garhwa': { latitude: 24.1542, longitude: 83.8147 },
  'Giridih': { latitude: 24.1912, longitude: 86.3022 },
  'Godda': { latitude: 24.8333, longitude: 87.2167 },
  'Gumla': { latitude: 23.0435, longitude: 84.5420 },
  'Hazaribagh': { latitude: 23.9929, longitude: 85.3647 },
  'Jamtara': { latitude: 23.9628, longitude: 86.8083 },
  'Khunti': { latitude: 23.0817, longitude: 85.2784 },
  'Koderma': { latitude: 24.4681, longitude: 85.5947 },
  'Latehar': { latitude: 23.7448, longitude: 84.5022 },
  'Lohardaga': { latitude: 23.4322, longitude: 84.6819 },
  'Pakur': { latitude: 24.6333, longitude: 87.8500 },
  'Palamu': { latitude: 24.0358, longitude: 83.9795 }, // Daltonganj
  'Ramgarh': { latitude: 23.6309, longitude: 85.5155 },
  'Ranchi': { latitude: 23.3441, longitude: 85.3096 },
  'Sahibganj': { latitude: 25.2500, longitude: 87.6500 },
  'Seraikela Kharsawan': { latitude: 22.6890, longitude: 85.9400 },
  'Simdega': { latitude: 22.6158, longitude: 84.5142 },
  'West Singhbhum': { latitude: 22.5579, longitude: 85.0178 } // Chaibasa
};

/**
 * Get coordinates for a given district name
 * @param {string} districtName - Name of the district
 * @returns {object} Object with latitude and longitude, or null if not found
 */
export const getDistrictCoordinates = (districtName) => {
  return JHARKHAND_DISTRICT_COORDINATES[districtName] || null;
};

/**
 * Get list of all available districts
 * @returns {array} Array of district names
 */
export const getAllDistricts = () => {
  return Object.keys(JHARKHAND_DISTRICT_COORDINATES);
};

/**
 * Check if a district name is valid
 * @param {string} districtName - Name of the district
 * @returns {boolean} True if valid district
 */
export const isValidDistrict = (districtName) => {
  return districtName in JHARKHAND_DISTRICT_COORDINATES;
};

/**
 * Auto-populate coordinates based on district selection
 * @param {string} district - Selected district name
 * @param {object} currentLocation - Current location data
 * @returns {object} Updated location with coordinates
 */
export const autoPopulateCoordinates = (district, currentLocation = {}) => {
  const districtCoords = getDistrictCoordinates(district);
  
  if (!districtCoords) {
    console.warn(`No coordinates found for district: ${district}`);
    return currentLocation;
  }
  
  // Only auto-populate if coordinates are empty or are default Ranchi coordinates
  const shouldAutoPopulate = 
    !currentLocation.latitude || 
    !currentLocation.longitude ||
    (currentLocation.latitude === '23.3441' && currentLocation.longitude === '85.3096' && district !== 'Ranchi');
  
  if (shouldAutoPopulate) {
    console.log(`Auto-populating coordinates for ${district}:`, districtCoords);
    return {
      ...currentLocation,
      latitude: districtCoords.latitude.toFixed(6),
      longitude: districtCoords.longitude.toFixed(6)
    };
  }
  
  return currentLocation;
};