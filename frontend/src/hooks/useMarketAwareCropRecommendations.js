/**
 * Market-Aware Crop Recommendation Hook
 * 
 * Custom hook that provides market-enhanced crop recommendations with caching
 */

import { useState, useCallback } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useMarket } from '../contexts/MarketContext';
import apiService from '../services/apiService';
import { toast } from 'react-hot-toast';

export const useMarketAwareCropRecommendations = () => {
    const [useMarketData, setUseMarketData] = useState(true);
    const [recommendationType, setRecommendationType] = useState('market-enhanced'); // 'regular' or 'market-enhanced'
    const { getMarketData, hasMarketData, getCropPrice } = useMarket();

    // Regular ML recommendations
    const regularRecommendationsMutation = useMutation({
        mutationFn: async (formData) => {
            return await apiService.getMLCropRecommendations(formData);
        },
        onSuccess: () => {
            toast.success('Regular crop recommendations generated!');
        },
        onError: (error) => {
            console.error('Regular recommendations error:', error);
            toast.error('Failed to get crop recommendations');
        }
    });

    // Market-enhanced ML recommendations
    const marketEnhancedMutation = useMutation({
        mutationFn: async (formData) => {
            // Ensure we have market data for the district
            if (formData.district) {
                await getMarketData(formData.district);
            }
            return await apiService.getMarketEnhancedRecommendations(formData);
        },
        onSuccess: () => {
            toast.success('Market-enhanced recommendations generated!');
        },
        onError: (error) => {
            console.error('Market-enhanced recommendations error:', error);
            toast.error('Failed to get market-enhanced recommendations');
        }
    });

    // Get recommendations based on current settings
    const getRecommendations = useCallback(async (formData) => {
        if (useMarketData && recommendationType === 'market-enhanced') {
            return marketEnhancedMutation.mutateAsync(formData);
        } else {
            return regularRecommendationsMutation.mutateAsync(formData);
        }
    }, [useMarketData, recommendationType, marketEnhancedMutation, regularRecommendationsMutation]);

    // Enhanced data processing
    const processRecommendationData = useCallback((recommendations, district) => {
        if (!recommendations || !Array.isArray(recommendations)) {
            return [];
        }

        return recommendations.map(rec => {
            // Get market price for this crop
            const marketPrice = getCropPrice(district, rec.crop);
            
            // Determine data source and reliability
            const isMarketEnhanced = rec.hasOwnProperty('market_score');
            const hasRealMarketData = hasMarketData(district);
            
            return {
                ...rec,
                // Standardize property names
                cropName: rec.crop,
                confidenceScore: rec.confidence || rec.suitability_score,
                expectedYield: rec.expected_yield,
                profitEstimate: rec.profit_estimate,
                
                // Market-specific data
                marketScore: rec.market_score || null,
                combinedScore: rec.combined_score || rec.suitability_score || rec.confidence,
                currentMarketPrice: rec.current_market_price || marketPrice?.price || null,
                priceTrend: rec.price_trend || 'stable',
                profitPerAcre: rec.profit_per_acre || null,
                roiPercentage: rec.roi_percentage || null,
                
                // Data quality indicators
                isMarketEnhanced,
                hasRealMarketData,
                dataSource: isMarketEnhanced ? 'market-enhanced' : 'regular-ml',
                reliability: hasRealMarketData ? 'high' : 'medium',
                
                // Display helpers
                displayScore: isMarketEnhanced ? rec.combined_score : (rec.confidence || rec.suitability_score),
                scoreLabel: isMarketEnhanced ? 'Combined Score' : 'Suitability Score',
                showMarketData: isMarketEnhanced && hasRealMarketData,
            };
        });
    }, [getCropPrice, hasMarketData]);

    // Toggle between recommendation types
    const toggleRecommendationType = useCallback(() => {
        const newType = recommendationType === 'market-enhanced' ? 'regular' : 'market-enhanced';
        setRecommendationType(newType);
        
        // Also update useMarketData state
        setUseMarketData(newType === 'market-enhanced');
        
        toast.success(`Switched to ${newType.replace('-', ' ')} recommendations`);
    }, [recommendationType]);

    // Get current mutation based on type
    const currentMutation = recommendationType === 'market-enhanced' 
        ? marketEnhancedMutation 
        : regularRecommendationsMutation;

    return {
        // State
        useMarketData,
        recommendationType,
        
        // Data
        data: currentMutation.data,
        loading: currentMutation.isPending,
        error: currentMutation.error,
        
        // Methods
        getRecommendations,
        processRecommendationData,
        toggleRecommendationType,
        setUseMarketData,
        setRecommendationType,
        
        // Mutations (for direct access if needed)
        regularMutation: regularRecommendationsMutation,
        marketEnhancedMutation,
        
        // Status helpers
        isLoading: currentMutation.isPending,
        isError: currentMutation.isError,
        isSuccess: currentMutation.isSuccess,
        
        // Data quality helpers
        hasData: !!currentMutation.data?.length,
        isMarketEnhanced: recommendationType === 'market-enhanced',
        canUseMarketData: true, // Always available due to fallback
    };
};

export default useMarketAwareCropRecommendations;