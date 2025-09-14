"""
Admin dashboard API routes.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.schemas import AdminStats, APIResponse
from app.services.database import DatabaseService
from app.services.admin_service import AdminService
from typing import Optional

admin_router = APIRouter()


@admin_router.get("/stats", response_model=APIResponse)
async def get_admin_statistics():
    """
    Get aggregated statistics for admin dashboard.
    
    Returns:
        Aggregated farm and farmer statistics (no personal data)
    """
    admin_service = AdminService()
    stats = await admin_service.get_aggregated_statistics()
    
    return APIResponse(
        success=True,
        message="Admin statistics retrieved successfully",
        data=stats
    )


@admin_router.get("/crop-adoption", response_model=APIResponse)
async def get_crop_adoption_data():
    """
    Get crop adoption vs recommendation analysis.
    
    Returns:
        Crop adoption statistics and recommendation effectiveness
    """
    admin_service = AdminService()
    adoption_data = await admin_service.get_crop_adoption_analysis()
    
    return APIResponse(
        success=True,
        message="Crop adoption data retrieved successfully",
        data=adoption_data
    )


@admin_router.get("/district-wise", response_model=APIResponse)
async def get_district_wise_data():
    """
    Get district-wise aggregated data for map visualization.
    
    Returns:
        District-wise statistics for Jharkhand
    """
    admin_service = AdminService()
    district_data = await admin_service.get_district_wise_data()
    
    return APIResponse(
        success=True,
        message="District-wise data retrieved successfully",
        data=district_data
    )


@admin_router.get("/popular-crops", response_model=APIResponse)
async def get_popular_crops_analysis():
    """
    Get analysis of most popular and recommended crops.
    
    Returns:
        Popular crops with adoption rates and success metrics
    """
    admin_service = AdminService()
    popular_crops = await admin_service.get_popular_crops_analysis()
    
    return APIResponse(
        success=True,
        message="Popular crops analysis retrieved successfully",
        data=popular_crops
    )


@admin_router.get("/financial-adoption", response_model=APIResponse)
async def get_financial_adoption():
    """
    Get financial services adoption statistics.
    
    Returns:
        Financial services usage and adoption rates
    """
    admin_service = AdminService()
    financial_data = await admin_service.get_financial_adoption_data()
    
    return APIResponse(
        success=True,
        message="Financial adoption data retrieved successfully",
        data=financial_data
    )


@admin_router.get("/sustainability-trends", response_model=APIResponse)
async def get_sustainability_trends():
    """
    Get sustainability trends and environmental impact.
    
    Returns:
        Sustainability metrics trends over time
    """
    admin_service = AdminService()
    sustainability_data = await admin_service.get_sustainability_trends()
    
    return APIResponse(
        success=True,
        message="Sustainability trends retrieved successfully",
        data=sustainability_data
    )


@admin_router.get("/export/farms", response_model=APIResponse)
async def export_farm_data(format: str = "csv"):
    """
    Export aggregated farm data.
    
    Args:
        format: Export format (csv, json)
        
    Returns:
        Download link for aggregated farm data
    """
    if format not in ["csv", "json"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'csv' or 'json'"
        )
    
    admin_service = AdminService()
    export_data = await admin_service.export_farm_data(format)
    
    return APIResponse(
        success=True,
        message=f"Farm data exported in {format} format successfully",
        data=export_data
    )


@admin_router.get("/export/recommendations", response_model=APIResponse)
async def export_recommendation_data(format: str = "csv"):
    """
    Export aggregated recommendation data.
    
    Args:
        format: Export format (csv, json)
        
    Returns:
        Download link for aggregated recommendation data
    """
    if format not in ["csv", "json"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'csv' or 'json'"
        )
    
    admin_service = AdminService()
    export_data = await admin_service.export_recommendation_data(format)
    
    return APIResponse(
        success=True,
        message=f"Recommendation data exported in {format} format successfully",
        data=export_data
    )


@admin_router.get("/ml-performance", response_model=APIResponse)
async def get_ml_performance_metrics():
    """
    Get ML model performance metrics.
    
    Returns:
        Model accuracy, precision, recall, and other performance metrics
    """
    admin_service = AdminService()
    ml_metrics = await admin_service.get_ml_performance_metrics()
    
    return APIResponse(
        success=True,
        message="ML performance metrics retrieved successfully",
        data=ml_metrics
    )


@admin_router.get("/federated-learning/status", response_model=APIResponse)
async def get_federated_learning_status():
    """
    Get federated learning system status.
    
    Returns:
        FL system status, last update, participating clients
    """
    admin_service = AdminService()
    fl_status = await admin_service.get_federated_learning_status()
    
    return APIResponse(
        success=True,
        message="Federated learning status retrieved successfully",
        data=fl_status
    )


@admin_router.get("/audit-logs", response_model=APIResponse)
async def get_audit_logs(limit: int = 100, offset: int = 0):
    """
    Get audit logs for federated learning updates.
    
    Args:
        limit: Number of logs to retrieve
        offset: Number of logs to skip
        
    Returns:
        Audit logs with hash chain verification
    """
    if limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit cannot exceed 1000"
        )
    
    admin_service = AdminService()
    audit_logs = await admin_service.get_audit_logs(limit, offset)
    
    return APIResponse(
        success=True,
        message="Audit logs retrieved successfully",
        data=audit_logs
    )