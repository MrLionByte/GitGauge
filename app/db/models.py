from sqlalchemy import Column, String, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from enum import Enum as PyEnum


class JobStatus(PyEnum):
    """Job status enumeration for database"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


Base = declarative_base()


class Job(Base):
    """Job model for tracking analysis jobs"""
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    github_username = Column(String(255), nullable=False, index=True)
    skills = Column(JSON, nullable=False)  # List of skills
    status = Column(SQLEnum(JobStatus), nullable=False, default=JobStatus.QUEUED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Additional job parameters
    repo_limit = Column(JSON, nullable=True)
    max_files_per_repo = Column(JSON, nullable=True)
    languages = Column(JSON, nullable=True)
    notes_for_ai = Column(Text, nullable=True)


class JobArtifact(Base):
    """Job artifacts model for storing analysis results"""
    __tablename__ = "job_artifacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    raw_sources = Column(JSON, nullable=True)  # GitHub data, repos, files, snippets
    report = Column(JSON, nullable=True)  # Final LLM analysis report
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Optional caching fields
    github_repo_cache = Column(JSON, nullable=True)
    file_snippet_cache = Column(JSON, nullable=True)
