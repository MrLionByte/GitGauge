from fastapi import BackgroundTasks
from typing import Callable, Any
import asyncio
from app.workers.redis_manager import redis_manager
import json
import uuid
from datetime import datetime


class JobQueue:
    """Queue abstraction for background job processing"""
    
    def __init__(self):
        self.redis = redis_manager
    
    async def enqueue_job(self, job_id: str, task_func: Callable, *args, **kwargs):
        """Enqueue a job for background processing"""
        # Store job metadata in Redis
        job_data = {
            "job_id": job_id,
            "status": "queued",
            "enqueued_at": datetime.utcnow().isoformat(),
            "task": task_func.__name__,
            "args": args,
            "kwargs": kwargs
        }
        
        await self.redis.set(f"job:{job_id}", json.dumps(job_data), expire_seconds=3600)
        await self.redis.set(f"job_status:{job_id}", "queued", expire_seconds=3600)
        
        # Add to processing queue
        await self.redis.set(f"queue:processing", job_id, expire_seconds=3600)
    
    async def get_job_status(self, job_id: str) -> str:
        """Get the current status of a job"""
        status = await self.redis.get(f"job_status:{job_id}")
        return status or "unknown"
    
    async def update_job_status(self, job_id: str, status: str, result: dict = None, error: str = None):
        """Update job status and store result/error"""
        await self.redis.set(f"job_status:{job_id}", status, expire_seconds=3600)
        
        if result:
            await self.redis.set(f"job_result:{job_id}", json.dumps(result), expire_seconds=3600)
        
        if error:
            await self.redis.set(f"job_error:{job_id}", error, expire_seconds=3600)
    
    async def get_job_result(self, job_id: str) -> dict:
        """Get job result if available"""
        result_str = await self.redis.get(f"job_result:{job_id}")
        if result_str:
            return json.loads(result_str)
        return None
    
    async def get_job_error(self, job_id: str) -> str:
        """Get job error if available"""
        return await self.redis.get(f"job_error:{job_id}")


# Global queue instance
job_queue = JobQueue()
