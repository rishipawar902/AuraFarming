/**
 * Market Data Caching Service
 * 
 * This service manages client-side caching of market price data using localStorage.
 * It fetches data once per session/day and serves it from cache for better performance.
 */

import apiService from './apiService';

class MarketCacheService {
    constructor() {
        this.cacheKey = 'aura_farming_market_data';
        this.metadataKey = 'aura_farming_market_metadata';
        this.cacheExpiryHours = 6; // Cache expires after 6 hours
        this.retryAttempts = 3;
        this.retryDelay = 1000; // 1 second
    }

    /**
     * Get market data for a district with caching
     */
    async getMarketData(district) {
        try {
            // Check if we have cached data
            const cachedData = this.getCachedData(district);
            if (cachedData && !this.isCacheExpired(district)) {
                console.log(`Using cached market data for ${district}`);
                return {
                    ...cachedData,
                    source: 'cache',
                    cached: true
                };
            }

            // Fetch fresh data
            console.log(`Fetching fresh market data for ${district}`);
            const freshData = await this.fetchWithRetry(district);
            
            // Cache the fresh data
            this.setCachedData(district, freshData);
            
            return {
                ...freshData,
                source: 'api',
                cached: false
            };

        } catch (error) {
            console.error(`Error getting market data for ${district}:`, error);
            
            // Return cached data even if expired as fallback
            const staleData = this.getCachedData(district);
            if (staleData) {
                console.log(`Using stale cached data for ${district} as fallback`);
                return {
                    ...staleData,
                    source: 'stale_cache',
                    cached: true,
                    stale: true
                };
            }
            
            // Final fallback to basic structure
            return this.getDefaultMarketData(district);
        }
    }

    /**
     * Fetch data with retry logic
     */
    async fetchWithRetry(district, attempt = 1) {
        try {
            const response = await apiService.getLiveMarketPrices(district);
            return response;
        } catch (error) {
            if (attempt < this.retryAttempts) {
                console.log(`Retry ${attempt}/${this.retryAttempts} for ${district} in ${this.retryDelay}ms`);
                await this.delay(this.retryDelay);
                return this.fetchWithRetry(district, attempt + 1);
            }
            throw error;
        }
    }

    /**
     * Get multiple districts data efficiently
     */
    async getMultipleDistrictsData(districts) {
        const results = {};
        
        // Check cache first for all districts
        const cachedResults = [];
        const districtsToFetch = [];

        for (const district of districts) {
            const cachedData = this.getCachedData(district);
            if (cachedData && !this.isCacheExpired(district)) {
                results[district] = { ...cachedData, source: 'cache', cached: true };
            } else {
                districtsToFetch.push(district);
            }
        }

        // Fetch missing districts in parallel
        if (districtsToFetch.length > 0) {
            const fetchPromises = districtsToFetch.map(async (district) => {
                try {
                    const data = await this.fetchWithRetry(district);
                    this.setCachedData(district, data);
                    return { district, data: { ...data, source: 'api', cached: false } };
                } catch (error) {
                    console.error(`Failed to fetch data for ${district}:`, error);
                    const staleData = this.getCachedData(district);
                    return { 
                        district, 
                        data: staleData ? 
                            { ...staleData, source: 'stale_cache', cached: true, stale: true } :
                            this.getDefaultMarketData(district)
                    };
                }
            });

            const fetchedResults = await Promise.allSettled(fetchPromises);
            fetchedResults.forEach((result) => {
                if (result.status === 'fulfilled') {
                    results[result.value.district] = result.value.data;
                }
            });
        }

        return results;
    }

    /**
     * Preload market data for common districts
     */
    async preloadCommonDistricts() {
        const commonDistricts = [
            'Ranchi', 'Delhi', 'Mumbai', 'Bangalore', 'Hyderabad',
            'Chennai', 'Kolkata', 'Pune', 'Ahmedabad', 'Jaipur'
        ];

        console.log('Preloading market data for common districts...');
        
        try {
            await this.getMultipleDistrictsData(commonDistricts);
            console.log('Market data preloading completed');
        } catch (error) {
            console.error('Market data preloading failed:', error);
        }
    }

    /**
     * Check if cached data exists and is valid
     */
    getCachedData(district) {
        try {
            const data = localStorage.getItem(`${this.cacheKey}_${district}`);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error(`Error reading cached data for ${district}:`, error);
            return null;
        }
    }

    /**
     * Store data in cache with timestamp
     */
    setCachedData(district, data) {
        try {
            const cacheEntry = {
                data,
                timestamp: Date.now(),
                district,
                expires: Date.now() + (this.cacheExpiryHours * 60 * 60 * 1000)
            };

            localStorage.setItem(`${this.cacheKey}_${district}`, JSON.stringify(cacheEntry));
            
            // Update metadata
            this.updateCacheMetadata(district);
            
            console.log(`Cached market data for ${district}`);
        } catch (error) {
            console.error(`Error caching data for ${district}:`, error);
        }
    }

    /**
     * Check if cache is expired
     */
    isCacheExpired(district) {
        try {
            const cached = this.getCachedData(district);
            if (!cached) return true;
            
            return Date.now() > cached.expires;
        } catch (error) {
            return true;
        }
    }

    /**
     * Update cache metadata for management
     */
    updateCacheMetadata(district) {
        try {
            const metadata = this.getCacheMetadata();
            metadata.districts = metadata.districts || {};
            metadata.districts[district] = {
                lastUpdated: Date.now(),
                updateCount: (metadata.districts[district]?.updateCount || 0) + 1
            };
            metadata.lastUpdate = Date.now();
            
            localStorage.setItem(this.metadataKey, JSON.stringify(metadata));
        } catch (error) {
            console.error('Error updating cache metadata:', error);
        }
    }

    /**
     * Get cache metadata
     */
    getCacheMetadata() {
        try {
            const metadata = localStorage.getItem(this.metadataKey);
            return metadata ? JSON.parse(metadata) : { districts: {}, lastUpdate: null };
        } catch (error) {
            return { districts: {}, lastUpdate: null };
        }
    }

    /**
     * Clear cache for a specific district
     */
    clearDistrictCache(district) {
        try {
            localStorage.removeItem(`${this.cacheKey}_${district}`);
            console.log(`Cleared cache for ${district}`);
        } catch (error) {
            console.error(`Error clearing cache for ${district}:`, error);
        }
    }

    /**
     * Clear all market cache
     */
    clearAllCache() {
        try {
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith(this.cacheKey) || key === this.metadataKey) {
                    localStorage.removeItem(key);
                }
            });
            console.log('Cleared all market cache');
        } catch (error) {
            console.error('Error clearing all cache:', error);
        }
    }

    /**
     * Get cache statistics
     */
    getCacheStats() {
        const metadata = this.getCacheMetadata();
        const keys = Object.keys(localStorage).filter(key => key.startsWith(this.cacheKey));
        
        return {
            totalDistricts: keys.length,
            districts: Object.keys(metadata.districts || {}),
            lastUpdate: metadata.lastUpdate,
            cacheSize: this.calculateCacheSize(),
            expiryTime: this.cacheExpiryHours
        };
    }

    /**
     * Calculate cache size
     */
    calculateCacheSize() {
        let size = 0;
        const keys = Object.keys(localStorage);
        keys.forEach(key => {
            if (key.startsWith(this.cacheKey) || key === this.metadataKey) {
                size += localStorage.getItem(key).length;
            }
        });
        return `${(size / 1024).toFixed(2)} KB`;
    }

    /**
     * Get default market data structure
     */
    getDefaultMarketData(district) {
        return {
            success: true,
            district,
            data: {
                prices: [],
                summary: {
                    total_markets: 0,
                    average_price: 0,
                    last_updated: new Date().toISOString()
                },
                trends: {
                    direction: 'stable',
                    percentage_change: 0
                }
            },
            metadata: {
                source: 'fallback',
                reliability: 'low',
                last_updated: new Date().toISOString()
            },
            source: 'fallback',
            cached: false,
            fallback: true
        };
    }

    /**
     * Utility delay function
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Force refresh data for a district
     */
    async forceRefresh(district) {
        this.clearDistrictCache(district);
        return await this.getMarketData(district);
    }

    /**
     * Refresh expired cache entries
     */
    async refreshExpiredCache() {
        const metadata = this.getCacheMetadata();
        const expiredDistricts = [];

        Object.keys(metadata.districts || {}).forEach(district => {
            if (this.isCacheExpired(district)) {
                expiredDistricts.push(district);
            }
        });

        if (expiredDistricts.length > 0) {
            console.log(`Refreshing expired cache for ${expiredDistricts.length} districts`);
            await this.getMultipleDistrictsData(expiredDistricts);
        }
    }
}

// Create and export a singleton instance
const marketCacheService = new MarketCacheService();

export default marketCacheService;