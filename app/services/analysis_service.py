from typing import Dict, Any, List
from app.workers.queue import job_queue
from app.workers.tasks import process_analysis_job
import asyncio


class AnalysisService:
    """Service for managing GitHub analysis jobs"""
    
    def __init__(self):
        self.queue = job_queue
    
    async def start_analysis_job(self, job_id: str, github_username: str, skills: List[str]) -> Dict[str, Any]:
        """
        Start a new analysis job
        Returns job metadata for immediate response
        """
        # Store job data in Redis for background processing
        job_data = {
            "job_id": job_id,
            "github_username": github_username,
            "skills": skills,
            "status": "queued",
            "created_at": asyncio.get_event_loop().time()
        }
        
        # Enqueue the job
        await self.queue.enqueue_job(
            job_id=job_id,
            task_func=process_analysis_job,
            github_username=github_username,
            skills=skills
        )
        
        return {
            "job_id": job_id,
            "status": "queued",
            "estimated_wait_seconds": 300  # 5 minutes estimate
        }
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the current status of a job
        Checks both Redis cache and database
        """
        # First check Redis for quick status
        redis_status = await self.queue.get_job_status(job_id)
        
        if redis_status in ["completed", "failed"]:
            # Get result from Redis if available
            result = await self.queue.get_job_result(job_id)
            error = await self.queue.get_job_error(job_id)
            
            return {
                "job_id": job_id,
                "status": redis_status,
                "result": result,
                "error": error
            }
        
        return {
            "job_id": job_id,
            "status": redis_status or "unknown"
        }
    
    async def get_job_result(self, job_id: str) -> Dict[str, Any]:
        """Get the final result of a completed job"""
        return await self.queue.get_job_result(job_id)


# Global service instance
analysis_service = AnalysisService()
