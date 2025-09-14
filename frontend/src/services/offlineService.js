/**
 * Offline Service for PWA functionality
 */

import { openDB } from 'idb';

const DB_NAME = 'SmartKhetDB';
const DB_VERSION = 1;

// Database store names
const STORES = {
  FARMS: 'farms',
  CROPS: 'crops',
  WEATHER: 'weather',
  MARKET: 'market',
  RECOMMENDATIONS: 'recommendations',
  SYNC_QUEUE: 'sync_queue'
};

export class OfflineService {
  static db = null;
  
  // Initialize IndexedDB
  static async initDB() {
    if (this.db) return this.db;
    
    this.db = await openDB(DB_NAME, DB_VERSION, {
      upgrade(db) {
        // Farms store
        if (!db.objectStoreNames.contains(STORES.FARMS)) {
          const farmStore = db.createObjectStore(STORES.FARMS, { 
            keyPath: 'id', 
            autoIncrement: true 
          });
          farmStore.createIndex('farmer_id', 'farmer_id');
        }
        
        // Crops store
        if (!db.objectStoreNames.contains(STORES.CROPS)) {
          const cropStore = db.createObjectStore(STORES.CROPS, { 
            keyPath: 'id', 
            autoIncrement: true 
          });
          cropStore.createIndex('farm_id', 'farm_id');
          cropStore.createIndex('season', 'season');
        }
        
        // Weather store
        if (!db.objectStoreNames.contains(STORES.WEATHER)) {
          const weatherStore = db.createObjectStore(STORES.WEATHER, { 
            keyPath: 'id', 
            autoIncrement: true 
          });
          weatherStore.createIndex('farm_id', 'farm_id');
          weatherStore.createIndex('date', 'date');
        }
        
        // Market store
        if (!db.objectStoreNames.contains(STORES.MARKET)) {
          const marketStore = db.createObjectStore(STORES.MARKET, { 
            keyPath: 'id', 
            autoIncrement: true 
          });
          marketStore.createIndex('district', 'district');
          marketStore.createIndex('crop', 'crop');
          marketStore.createIndex('date', 'date');
        }
        
        // Recommendations store
        if (!db.objectStoreNames.contains(STORES.RECOMMENDATIONS)) {
          const recStore = db.createObjectStore(STORES.RECOMMENDATIONS, { 
            keyPath: 'id', 
            autoIncrement: true 
          });
          recStore.createIndex('farmer_id', 'farmer_id');
          recStore.createIndex('season', 'season');
        }
        
        // Sync queue store
        if (!db.objectStoreNames.contains(STORES.SYNC_QUEUE)) {
          const syncStore = db.createObjectStore(STORES.SYNC_QUEUE, { 
            keyPath: 'id', 
            autoIncrement: true 
          });
          syncStore.createIndex('timestamp', 'timestamp');
          syncStore.createIndex('type', 'type');
        }
      },
    });
    
    return this.db;
  }
  
  // Save data to IndexedDB
  static async saveToStore(storeName, data) {
    const db = await this.initDB();
    const tx = db.transaction(storeName, 'readwrite');
    await tx.store.put({ ...data, cached_at: new Date().toISOString() });
    await tx.done;
  }
  
  // Get data from IndexedDB
  static async getFromStore(storeName, key = null) {
    const db = await this.initDB();
    const tx = db.transaction(storeName, 'readonly');
    
    if (key) {
      return await tx.store.get(key);
    } else {
      return await tx.store.getAll();
    }
  }
  
  // Get data by index
  static async getByIndex(storeName, indexName, value) {
    const db = await this.initDB();
    const tx = db.transaction(storeName, 'readonly');
    return await tx.store.index(indexName).getAll(value);
  }
  
  // Delete from store
  static async deleteFromStore(storeName, key) {
    const db = await this.initDB();
    const tx = db.transaction(storeName, 'readwrite');
    await tx.store.delete(key);
    await tx.done;
  }
  
  // Clear store
  static async clearStore(storeName) {
    const db = await this.initDB();
    const tx = db.transaction(storeName, 'readwrite');
    await tx.store.clear();
    await tx.done;
  }
  
  // Farm data methods
  static async saveFarmProfile(farmData) {
    return await this.saveToStore(STORES.FARMS, farmData);
  }
  
  static async getFarmProfile(farmerId) {
    const farms = await this.getByIndex(STORES.FARMS, 'farmer_id', farmerId);
    return farms[0] || null;
  }
  
  // Crop history methods
  static async saveCropHistory(cropData) {
    return await this.saveToStore(STORES.CROPS, cropData);
  }
  
  static async getCropHistory(farmId) {
    return await this.getByIndex(STORES.CROPS, 'farm_id', farmId);
  }
  
  // Weather data methods
  static async saveWeatherData(weatherData) {
    return await this.saveToStore(STORES.WEATHER, weatherData);
  }
  
  static async getWeatherData(farmId, days = 7) {
    const allWeather = await this.getByIndex(STORES.WEATHER, 'farm_id', farmId);
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    return allWeather.filter(w => new Date(w.date) >= cutoffDate);
  }
  
  // Market data methods
  static async saveMarketData(marketData) {
    return await this.saveToStore(STORES.MARKET, marketData);
  }
  
  static async getMarketData(district, crop = null) {
    let marketData = await this.getByIndex(STORES.MARKET, 'district', district);
    
    if (crop) {
      marketData = marketData.filter(m => m.crop === crop);
    }
    
    // Return recent data (last 7 days)
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - 7);
    
    return marketData.filter(m => new Date(m.date) >= cutoffDate);
  }
  
  // Recommendations methods
  static async saveRecommendations(recommendations) {
    return await this.saveToStore(STORES.RECOMMENDATIONS, recommendations);
  }
  
  static async getRecommendations(farmerId, season = null) {
    let recommendations = await this.getByIndex(STORES.RECOMMENDATIONS, 'farmer_id', farmerId);
    
    if (season) {
      recommendations = recommendations.filter(r => r.season === season);
    }
    
    return recommendations;
  }
  
  // Sync queue methods
  static async addToSyncQueue(action, data) {
    const queueItem = {
      type: action,
      data: data,
      timestamp: new Date().toISOString(),
      synced: false
    };
    
    return await this.saveToStore(STORES.SYNC_QUEUE, queueItem);
  }
  
  static async getSyncQueue() {
    const queue = await this.getFromStore(STORES.SYNC_QUEUE);
    return queue.filter(item => !item.synced);
  }
  
  static async markSynced(queueItemId) {
    const db = await this.initDB();
    const tx = db.transaction(STORES.SYNC_QUEUE, 'readwrite');
    const item = await tx.store.get(queueItemId);
    
    if (item) {
      item.synced = true;
      item.synced_at = new Date().toISOString();
      await tx.store.put(item);
    }
    
    await tx.done;
  }
  
  // Data freshness check
  static isDataFresh(cachedAt, maxAgeMinutes = 60) {
    if (!cachedAt) return false;
    
    const cached = new Date(cachedAt);
    const now = new Date();
    const diffMinutes = (now - cached) / (1000 * 60);
    
    return diffMinutes < maxAgeMinutes;
  }
  
  // Cleanup old data
  static async cleanupOldData() {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - 30); // Keep 30 days of data
    
    const stores = [STORES.WEATHER, STORES.MARKET];
    
    for (const storeName of stores) {
      const db = await this.initDB();
      const tx = db.transaction(storeName, 'readwrite');
      const allData = await tx.store.getAll();
      
      for (const item of allData) {
        if (new Date(item.cached_at) < cutoffDate) {
          await tx.store.delete(item.id);
        }
      }
      
      await tx.done;
    }
  }
  
  // Check if app is online
  static isOnline() {
    return navigator.onLine;
  }
  
  // Setup online/offline event listeners
  static setupNetworkListeners() {
    window.addEventListener('online', () => {
      console.log('App is back online');
      this.syncPendingData();
    });
    
    window.addEventListener('offline', () => {
      console.log('App is offline');
    });
  }
  
  // Sync pending data when back online
  static async syncPendingData() {
    if (!this.isOnline()) return;
    
    try {
      const queue = await this.getSyncQueue();
      console.log(`Syncing ${queue.length} pending items`);
      
      for (const item of queue) {
        try {
          // Process sync item based on type
          await this.processSyncItem(item);
          await this.markSynced(item.id);
        } catch (error) {
          console.error('Failed to sync item:', item.id, error);
        }
      }
    } catch (error) {
      console.error('Sync failed:', error);
    }
  }
  
  // Process individual sync item
  static async processSyncItem(item) {
    // Import ApiService dynamically to avoid circular dependency
    const { ApiService } = await import('./apiService');
    
    switch (item.type) {
      case 'CREATE_FARM':
        await ApiService.createFarmProfile(item.data);
        break;
        
      case 'ADD_CROP_HISTORY':
        await ApiService.addCropHistory(item.data);
        break;
        
      default:
        console.warn('Unknown sync item type:', item.type);
    }
  }
}

export default OfflineService;