/**
 * Market Data Context Provider
 * 
 * Provides global market data state management with automatic caching and preloading
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import marketCacheService from '../services/MarketCacheService';

const MarketContext = createContext();

export const useMarket = () => {
    const context = useContext(MarketContext);
    if (!context) {
        throw new Error('useMarket must be used within a MarketProvider');
    }
    return context;
};

export const MarketProvider = ({ children }) => {
    const [marketData, setMarketData] = useState({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [cacheStats, setCacheStats] = useState(null);
    const [preloadComplete, setPreloadComplete] = useState(false);

    // Get market data for a specific district
    const getMarketData = useCallback(async (district) => {
        if (!district) return null;
        
        try {
            setLoading(true);
            setError(null);
            
            const data = await marketCacheService.getMarketData(district);
            
            // Update local state
            setMarketData(prev => ({
                ...prev,
                [district]: data
            }));
            
            return data;
        } catch (err) {
            console.error(`Error fetching market data for ${district}:`, err);
            setError(err.message);
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    // Get market data for multiple districts
    const getMultipleDistrictsData = useCallback(async (districts) => {
        if (!districts || districts.length === 0) return {};
        
        try {
            setLoading(true);
            setError(null);
            
            const data = await marketCacheService.getMultipleDistrictsData(districts);
            
            // Update local state
            setMarketData(prev => ({
                ...prev,
                ...data
            }));
            
            return data;
        } catch (err) {
            console.error('Error fetching multiple districts data:', err);
            setError(err.message);
            return {};
        } finally {
            setLoading(false);
        }
    }, []);

    // Force refresh data for a district
    const refreshMarketData = useCallback(async (district) => {
        try {
            setLoading(true);
            setError(null);
            
            const data = await marketCacheService.forceRefresh(district);
            
            setMarketData(prev => ({
                ...prev,
                [district]: data
            }));
            
            return data;
        } catch (err) {
            console.error(`Error refreshing market data for ${district}:`, err);
            setError(err.message);
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    // Clear cache for a district
    const clearDistrictCache = useCallback((district) => {
        marketCacheService.clearDistrictCache(district);
        setMarketData(prev => {
            const newData = { ...prev };
            delete newData[district];
            return newData;
        });
    }, []);

    // Clear all cache
    const clearAllCache = useCallback(() => {
        marketCacheService.clearAllCache();
        setMarketData({});
    }, []);

    // Get cache statistics
    const updateCacheStats = useCallback(() => {
        const stats = marketCacheService.getCacheStats();
        setCacheStats(stats);
        return stats;
    }, []);

    // Check if data is available for a district
    const hasMarketData = useCallback((district) => {
        return marketData[district] && !marketData[district].fallback;
    }, [marketData]);

    // Get market price for a specific crop in a district
    const getCropPrice = useCallback((district, cropName) => {
        const districtData = marketData[district];
        if (!districtData || !districtData.data || !districtData.data.prices) {
            return null;
        }

        // Find crop in market data
        const cropPrice = districtData.data.prices.find(price => 
            price.commodity && 
            price.commodity.toLowerCase().includes(cropName.toLowerCase())
        );

        return cropPrice ? {
            price: cropPrice.modal_price || cropPrice.max_price || cropPrice.min_price,
            unit: cropPrice.unit || 'per quintal',
            market: cropPrice.market,
            date: cropPrice.arrival_date
        } : null;
    }, [marketData]);

    // Get market trend for a district
    const getMarketTrend = useCallback((district) => {
        const districtData = marketData[district];
        if (!districtData || !districtData.data) {
            return { direction: 'stable', percentage: 0 };
        }

        return districtData.data.trends || { direction: 'stable', percentage: 0 };
    }, [marketData]);

    // Initialize market data on app start
    useEffect(() => {
        const initializeMarketData = async () => {
            try {
                console.log('Initializing market data...');
                
                // Update cache stats
                updateCacheStats();
                
                // Preload common districts
                await marketCacheService.preloadCommonDistricts();
                
                // Refresh expired cache
                await marketCacheService.refreshExpiredCache();
                
                setPreloadComplete(true);
                console.log('Market data initialization complete');
            } catch (err) {
                console.error('Market data initialization failed:', err);
                setError('Failed to initialize market data');
                setPreloadComplete(true); // Still set to true to not block the app
            }
        };

        initializeMarketData();
    }, [updateCacheStats]);

    // Periodically refresh cache stats
    useEffect(() => {
        const interval = setInterval(() => {
            updateCacheStats();
        }, 30000); // Update every 30 seconds

        return () => clearInterval(interval);
    }, [updateCacheStats]);

    const value = {
        // Data
        marketData,
        loading,
        error,
        cacheStats,
        preloadComplete,

        // Methods
        getMarketData,
        getMultipleDistrictsData,
        refreshMarketData,
        clearDistrictCache,
        clearAllCache,
        updateCacheStats,
        hasMarketData,
        getCropPrice,
        getMarketTrend,

        // Utility
        isDataCached: (district) => marketData[district]?.cached || false,
        isDataStale: (district) => marketData[district]?.stale || false,
        getDataSource: (district) => marketData[district]?.source || 'unknown',
        getLastUpdated: (district) => marketData[district]?.data?.summary?.last_updated,
    };

    return (
        <MarketContext.Provider value={value}>
            {children}
        </MarketContext.Provider>
    );
};