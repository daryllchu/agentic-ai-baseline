from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.monitoring_service import MonitoringService
from services.cache_service import cache
from typing import Dict, List
import redis

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])

@router.get("/metrics")
def get_system_metrics(db: Session = Depends(get_db)):
    """Get comprehensive system metrics"""
    
    # Try cache first
    cached_metrics = cache.get("system_metrics")
    if cached_metrics:
        return cached_metrics
    
    monitoring = MonitoringService(db)
    
    metrics = {
        "system": monitoring.get_system_metrics(),
        "etl": monitoring.get_etl_metrics(),
        "alerts": monitoring.check_alerts()
    }
    
    # Cache for 1 minute
    cache.set("system_metrics", metrics, 60)
    
    return metrics

@router.get("/health/detailed")
def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check for all services"""
    
    health_status = {
        "status": "healthy",
        "timestamp": cache.get("health_timestamp") or "unknown",
        "services": {}
    }
    
    # Database health
    try:
        db.execute("SELECT 1")
        health_status["services"]["database"] = {"status": "healthy", "response_time_ms": 0}
    except Exception as e:
        health_status["services"]["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Redis health
    try:
        redis_client = redis.Redis(host='redis', port=6379)
        redis_client.ping()
        health_status["services"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health_status["services"]["redis"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # ETL processing health
    try:
        from models import ETLJob
        processing_jobs = db.query(ETLJob).filter(ETLJob.status == "processing").count()
        health_status["services"]["etl"] = {
            "status": "healthy",
            "processing_jobs": processing_jobs
        }
    except Exception as e:
        health_status["services"]["etl"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    return health_status

@router.get("/alerts")
def get_active_alerts(db: Session = Depends(get_db)):
    """Get all active system alerts"""
    
    monitoring = MonitoringService(db)
    alerts = monitoring.check_alerts()
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "critical_count": len([a for a in alerts if a.get("severity") == "critical"]),
        "warning_count": len([a for a in alerts if a.get("severity") == "warning"])
    }

@router.post("/metrics/custom")
def log_custom_metric(
    metric_name: str,
    value: float,
    tags: Dict = None,
    db: Session = Depends(get_db)
):
    """Log custom application metric"""
    
    monitoring = MonitoringService(db)
    monitoring.log_performance_metric(metric_name, value, tags)
    
    return {"message": f"Metric {metric_name} logged successfully"}

@router.get("/performance/summary")
def get_performance_summary(db: Session = Depends(get_db)):
    """Get performance summary for dashboard"""
    
    # Try cache first
    cached_summary = cache.get("performance_summary")
    if cached_summary:
        return cached_summary
    
    monitoring = MonitoringService(db)
    
    summary = {
        "system_health": "healthy",
        "etl_jobs_24h": monitoring.get_etl_metrics(),
        "resource_usage": monitoring.get_system_metrics(),
        "active_alerts": len(monitoring.check_alerts()),
        "uptime_hours": 24  # Mock uptime
    }
    
    # Cache for 5 minutes
    cache.set("performance_summary", summary, 300)
    
    return summary