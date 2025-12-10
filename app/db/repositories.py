from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.models import Job, JobArtifact, JobStatus
from app.api.schemas.jobs import CreateJobRequest
import uuid


class JobRepository:
    """Repository for job-related database operations"""
    def __init__(self, db: Session):
        self.db = db
    
    def create_job(self, job_request: CreateJobRequest) -> Job:
        """Create a new job"""
        job = Job(
            github_username=job_request.github_username,
            skills=job_request.skills,
            repo_limit=job_request.repo_limit,
            max_files_per_repo=job_request.max_files_per_repo,
            languages=job_request.languages,
            notes_for_ai=job_request.notes_for_ai,
            status=JobStatus.QUEUED
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def get_job_by_id(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        try:
            job_uuid = uuid.UUID(job_id)
            return self.db.query(Job).filter(Job.id == job_uuid).first()
        except ValueError:
            return None
    
    def update_job_status(self, job_id: str, status: JobStatus, 
                         error_code: Optional[str] = None, 
                         error_message: Optional[str] = None) -> bool:
        """Update job status"""
        try:
            job_uuid = uuid.UUID(job_id)
            job = self.db.query(Job).filter(Job.id == job_uuid).first()
            if job:
                job.status = status
                if error_code:
                    job.error_code = error_code
                if error_message:
                    job.error_message = error_message
                self.db.commit()
                return True
            return False
        except ValueError:
            return False
    
    def get_recent_jobs(self, limit: int = 10) -> List[Job]:
        """Get recent jobs"""
        return self.db.query(Job).order_by(desc(Job.created_at)).limit(limit).all()


class JobArtifactRepository:
    """Repository for job artifact operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_artifact(self, job_id: str, raw_sources: dict = None, 
                        report: dict = None) -> JobArtifact:
        """Create job artifact"""
        try:
            job_uuid = uuid.UUID(job_id)
            artifact = JobArtifact(
                job_id=job_uuid,
                raw_sources=raw_sources,
                report=report
            )
            self.db.add(artifact)
            self.db.commit()
            self.db.refresh(artifact)
            return artifact
        except ValueError:
            raise ValueError("Invalid job ID format")
    
    def get_artifact_by_job_id(self, job_id: str) -> Optional[JobArtifact]:
        """Get artifact by job ID"""
        try:
            job_uuid = uuid.UUID(job_id)
            return self.db.query(JobArtifact).filter(JobArtifact.job_id == job_uuid).first()
        except ValueError:
            return None
    
    def update_artifact(self, job_id: str, raw_sources: dict = None, 
                      report: dict = None) -> bool:
        """Update job artifact"""
        try:
            job_uuid = uuid.UUID(job_id)
            artifact = self.db.query(JobArtifact).filter(JobArtifact.job_id == job_uuid).first()
            if artifact:
                if raw_sources is not None:
                    artifact.raw_sources = raw_sources
                if report is not None:
                    artifact.report = report
                self.db.commit()
                return True
            return False
        except ValueError:
            return False
