"""
Enhanced Error Handling and Logging Configuration for AuraFarming
Provides better error management and fallback data generation.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import random

# Configure logging for better error tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('aurafarming.log')
    ]
)

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Enhanced error handling for market and weather services."""
    
    @staticmethod
    def handle_api_error(service_name: str, error: Exception, fallback_data: Any = None):
        """Handle API errors gracefully with fallback options."""
        error_msg = f"{service_name} error: {str(error)}"
        logger.warning(error_msg)
        
        if fallback_data:
            logger.info(f"Using fallback data for {service_name}")
            return fallback_data
        
        return ErrorHandler.generate_fallback_response(service_name)
    
    @staticmethod
    def handle_network_error(url: str, error: Exception):
        """Handle network-related errors."""
        logger.warning(f"Network error accessing {url}: {str(error)}")
        return {"error": "network_unavailable", "url": url, "message": str(error)}
    
    @staticmethod
    def generate_fallback_response(service_name: str) -> Dict[str, Any]:
        """Generate realistic fallback data when services are unavailable."""
        
        if "weather" in service_name.lower():
            return ErrorHandler._generate_weather_fallback()
        elif "market" in service_name.lower():
            return ErrorHandler._generate_market_fallback()
        else:
            return {"status": "service_unavailable", "fallback": True}
    
    @staticmethod
    def _generate_weather_fallback() -> Dict[str, Any]:
        """Generate realistic weather fallback data for Jharkhand."""
        return {
            "temperature": round(random.uniform(22, 35), 1),
            "humidity": random.randint(45, 85),
            "description": random.choice(["Partly cloudy", "Clear sky", "Light rain expected"]),
            "wind_speed": round(random.uniform(5, 15), 1),
            "source": "fallback_realistic",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def _generate_market_fallback() -> Dict[str, Any]:
        """Generate realistic market price fallback data."""
        crops = ["Rice", "Wheat", "Maize", "Paddy", "Sugarcane"]
        return {
            "prices": [
                {
                    "commodity": crop,
                    "min_price": round(random.uniform(1500, 2500), 2),
                    "max_price": round(random.uniform(2500, 3500), 2),
                    "modal_price": round(random.uniform(2000, 3000), 2),
                    "source": "fallback_realistic",
                    "timestamp": datetime.now().isoformat()
                }
                for crop in crops
            ],
            "status": "fallback_data",
            "message": "Government portals temporarily unavailable, showing realistic estimates"
        }


class ServiceHealthMonitor:
    """Monitor service health and provide status updates."""
    
    def __init__(self):
        self.service_status = {}
    
    def update_service_status(self, service_name: str, status: str, error_msg: str = None):
        """Update service status for monitoring."""
        self.service_status[service_name] = {
            "status": status,
            "last_checked": datetime.now().isoformat(),
            "error": error_msg
        }
        
        if status == "error":
            logger.warning(f"Service {service_name} is experiencing issues: {error_msg}")
        elif status == "recovered":
            logger.info(f"Service {service_name} has recovered")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        total_services = len(self.service_status)
        healthy_services = sum(1 for s in self.service_status.values() if s["status"] == "healthy")
        
        return {
            "overall_health": "healthy" if healthy_services == total_services else "degraded",
            "healthy_services": healthy_services,
            "total_services": total_services,
            "services": self.service_status,
            "timestamp": datetime.now().isoformat()
        }


# Global instances
error_handler = ErrorHandler()
health_monitor = ServiceHealthMonitor()
