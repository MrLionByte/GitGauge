from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.db.repositories import JobRepository, JobArtifactRepository
from app.api.schemas.jobs import (
    CreateJobRequest, JobResponse, JobStatusResponse, 
    JobStatus as SchemaJobStatus, ErrorResponse
)
from app.db.models import JobStatus as ModelJobStatus
from app.services.analysis_service import analysis_service
import uuid

router = APIRouter(prefix='/jobs')


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_request: CreateJobRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new analysis job"""
    try:
        # Create job repository
        job_repo = JobRepository(db)
        
        # Create the job in database
        job = job_repo.create_job(job_request)
        
        # Start background analysis using Redis queue
        from app.workers.tasks import process_analysis_job
        background_tasks.add_task(
            process_analysis_job,
            str(job.id),
            job_request.github_username,
            job_request.skills
        )
        
        # Return response
        return JobResponse(
            job_id=str(job.id),
            status=SchemaJobStatus.QUEUED,
            estimated_wait_seconds=300  # 5 minutes estimate
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Get job status and results"""
    try:
        # Validate UUID format
        try:
            uuid.UUID(job_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid job ID format"
            )
        
        # Get job repository
        job_repo = JobRepository(db)
        artifact_repo = JobArtifactRepository(db)
        
        # Get job
        job = job_repo.get_job_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Get artifact if job is completed
        artifact = None
        if job.status == ModelJobStatus.COMPLETED:
            artifact = artifact_repo.get_artifact_by_job_id(job_id)
        
        # Build response
        response_data = {
            "job_id": str(job.id),
            "status": SchemaJobStatus(job.status.value),
            "created_at": job.created_at,
            "updated_at": job.updated_at
        }
        
        # Add optional fields based on status
        if job.status == ModelJobStatus.COMPLETED and artifact and artifact.report:
            response_data["report"] = artifact.report
            response_data["generated_at"] = artifact.generated_at
        elif job.status == ModelJobStatus.FAILED:
            response_data["error_code"] = job.error_code
            response_data["error_message"] = job.error_message
        
        return JobStatusResponse(**response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.get("/", response_model=List[JobStatusResponse])
async def list_jobs(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List recent jobs"""
    try:
        job_repo = JobRepository(db)
        jobs = job_repo.get_recent_jobs(limit)
        
        return [
            JobStatusResponse(
                job_id=str(job.id),
                status=SchemaJobStatus(job.status.value),
                created_at=job.created_at,
                updated_at=job.updated_at,
                error_code=job.error_code if job.status == ModelJobStatus.FAILED else None,
                error_message=job.error_message if job.status == ModelJobStatus.FAILED else None
            )
            for job in jobs
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list jobs: {str(e)}"
        )