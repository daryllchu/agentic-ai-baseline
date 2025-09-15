import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models import ETLJob, DataSource, Employee
import psutil
import redis

logger = logging.getLogger(__name__)

class MonitoringService:
    def __init__(self, db: Session, redis_client: Optional[redis.Redis] = None):
        self.db = db
        self.redis = redis_client or redis.Redis(host='redis', port=6379, decode_responses=True)
    
    def get_system_metrics(self) -> Dict:
        """Get system performance metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_etl_metrics(self) -> Dict:
        """Get ETL job performance metrics"""
        # Jobs in last 24 hours
        from datetime import timedelta
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        
        recent_jobs = self.db.query(ETLJob).filter(ETLJob.created_at >= yesterday).all()
        
        metrics = {
            "total_jobs_24h": len(recent_jobs),
            "completed_jobs": len([j for j in recent_jobs if j.status == "completed"]),
            "failed_jobs": len([j for j in recent_jobs if j.status == "failed"]),
            "processing_jobs": len([j for j in recent_jobs if j.status == "processing"]),
            "avg_processing_time": self._calculate_avg_processing_time(recent_jobs),
            "total_records_processed": sum(j.records_processed or 0 for j in recent_jobs)
        }
        
        # Store in Redis for caching
        self.redis.setex("etl_metrics", 300, str(metrics))  # 5 min cache
        return metrics
    
    def _calculate_avg_processing_time(self, jobs: List[ETLJob]) -> float:
        """Calculate average processing time for completed jobs"""
        completed = [j for j in jobs if j.status == "completed" and j.started_at and j.completed_at]
        if not completed:
            return 0.0
        
        total_time = sum((j.completed_at - j.started_at).total_seconds() for j in completed)
        return total_time / len(completed)
    
    def check_alerts(self) -> List[Dict]:
        """Check for system alerts"""
        alerts = []
        
        # System resource alerts
        metrics = self.get_system_metrics()
        if metrics["cpu_percent"] > 80:
            alerts.append({
                "type": "system",
                "severity": "warning",
                "message": f"High CPU usage: {metrics['cpu_percent']:.1f}%",
                "timestamp": metrics["timestamp"]
            })
        
        if metrics["memory_percent"] > 85:
            alerts.append({
                "type": "system", 
                "severity": "critical",
                "message": f"High memory usage: {metrics['memory_percent']:.1f}%",
                "timestamp": metrics["timestamp"]
            })
        
        # ETL job alerts
        failed_jobs = self.db.query(ETLJob).filter(ETLJob.status == "failed").count()
        if failed_jobs > 5:
            alerts.append({
                "type": "etl",
                "severity": "warning", 
                "message": f"{failed_jobs} failed ETL jobs require attention",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return alerts
    
    def log_performance_metric(self, metric_name: str, value: float, tags: Dict = None):
        """Log custom performance metric"""
        metric_data = {
            "name": metric_name,
            "value": value,
            "tags": tags or {},
            "timestamp": time.time()
        }
        
        # Store in Redis time series
        key = f"metrics:{metric_name}"
        self.redis.zadd(key, {str(metric_data): time.time()})
        
        # Keep only last 1000 entries
        self.redis.zremrangebyrank(key, 0, -1001)
        
        logger.info(f"Metric logged: {metric_name}={value}")