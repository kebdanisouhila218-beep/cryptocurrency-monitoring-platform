# api/health.py - Enhanced Health Check Endpoints

from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone
import psutil
import time
import asyncio
from pymongo import MongoClient
import redis
from prometheus_client import Counter, Gauge, Histogram
import os

router = APIRouter(prefix="/health", tags=["Health"])

# Prometheus metrics for health checks
HEALTH_CHECK_TOTAL = Counter('health_checks_total', 'Total health checks', ['status'])
HEALTH_CHECK_DURATION = Histogram('health_check_duration_seconds', 'Health check duration')
SYSTEM_RESOURCES = Gauge('system_resources_bytes', 'System resources', ['resource'])

# Global health status
last_health_check = {}
HEALTH_CHECK_TIMEOUT = 30  # seconds

def update_health_check(component: str, status: str, details: dict = None):
    """Update the last health check status"""
    global last_health_check
    last_health_check[component] = {
        'status': status,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'details': details or {}
    }
    HEALTH_CHECK_TOTAL.labels(status=status).inc()

@router.get("/")
async def health_check():
    """
    Basic health check endpoint
    """
    Basic health check - returns 200 if service is running
    """
    start_time = time.time()
    
    try:
        # Check basic connectivity
        status = "healthy"
        update_health_check("basic", status)
        
        duration = time.time() - start_time
        HEALTH_CHECK_DURATION.observe(duration)
        
        return {
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "crypto-api",
            "version": "2.0.0",
            "checks": last_health_check
        }
    except Exception as e:
        update_health_check("basic", "unhealthy", {"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )

@router.get("/detailed")
async def detailed_health_check():
    """
    Detailed health check with all components
    """
    Detailed health check - checks all system components
    """
    start_time = time.time()
    
    checks = {}
    overall_status = "healthy"
    
    # Database connectivity check
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        checks["mongodb"] = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {"database": "crypto_db"}
        }
        update_health_check("mongodb", "healthy")
    except Exception as e:
        checks["mongodb"] = {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {"error": str(e)}
        }
        update_health_check("mongodb", "unhealthy")
        overall_status = "degraded"
    
    # Redis connectivity check
    try:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_client = redis.Redis(host=redis_host, port=redis_port, socket_connect_timeout=5)
        redis_client.ping()
        checks["redis"] = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {"host": redis_host, "port": redis_port}
        }
        update_health_check("redis", "healthy")
    except Exception as e:
        checks["redis"] = {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {"error": str(e)}
        }
        update_health_check("redis", "unhealthy")
        overall_status = "degraded"
    
    # System resources check
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        checks["system"] = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "percent": disk.percent
                }
            }
        }
        
        # Update Prometheus metrics
        SYSTEM_RESOURCES.labels(resource="memory_used").set(memory.used)
        SYSTEM_RESOURCES.labels(resource="memory_available").set(memory.available)
        SYSTEM_RESOURCES.labels(resource="disk_used").set(disk.used)
        SYSTEM_RESOURCES.labels(resource="disk_free").set(disk.free)
        
        # Check thresholds
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            checks["system"]["status"] = "degraded"
            overall_status = "degraded"
            
        update_health_check("system", checks["system"]["status"])
        
    except Exception as e:
        checks["system"] = {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {"error": str(e)}
        }
        update_health_check("system", "unhealthy")
        overall_status = "degraded"
    
    # Database collections check
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client["crypto_db"]
        
        collections = {
            "prices": db["prices"].count_documents({}),
            "users": db["users"].count_documents({}),
            "alerts": db["alerts"].count_documents({})
        }
        
        checks["collections"] = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": collections
        }
        update_health_check("collections", "healthy")
        
    except Exception as e:
        checks["collections"] = {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {"error": str(e)}
        }
        update_health_check("collections", "unhealthy")
        overall_status = "degraded"
    
    duration = time.time() - start_time
    HEALTH_CHECK_DURATION.observe(duration)
    
    # Determine HTTP status code
    status_code = status.HTTP_200_OK if overall_status == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "crypto-api",
        "version": "2.0.0",
        "duration_seconds": round(duration, 2),
        "checks": checks
    }, status_code

@router.get("/readiness")
async def readiness_check():
    """
    Readiness check - checks if the service is ready to serve traffic
    """
    try:
        # Check if database connections are ready
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_client = redis.Redis(host=redis_host, port=redis_port, socket_connect_timeout=2)
        redis_client.ping()
        
        return {
            "status": "ready",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {
                "database": "ready",
                "cache": "ready"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )

@router.get("/liveness")
async def liveness_check():
    """
    Liveness check - checks if the service is alive
    """
    try:
        # Simple check to see if the service is responding
        return {
            "status": "alive",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {
                "service": "alive"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not alive: {str(e)}"
        )

@router.get("/metrics")
async def metrics_endpoint():
    """
    Prometheus metrics endpoint
    """
    Prometheus metrics for health checks
    """
    from metrics import get_metrics
    return get_metrics()
