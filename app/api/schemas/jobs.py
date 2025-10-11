from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CreateJobRequest(BaseModel):
    """Request model for creating a new job"""
    github_username: str = Field(..., description="GitHub username to analyze")
    skills: List[str] = Field(..., description="List of skills to evaluate")
    repo_limit: Optional[int] = Field(10, description="Maximum number of repos to analyze")
    max_files_per_repo: Optional[int] = Field(5, description="Maximum files per repository")
    languages: Optional[List[str]] = Field(None, description="Preferred programming languages")
    notes_for_ai: Optional[str] = Field(None, description="Additional notes for AI analysis")


class JobResponse(BaseModel):
    """Response model for job creation"""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    estimated_wait_seconds: int = Field(..., description="Estimated processing time")


class SkillsMatch(BaseModel):
    """Skills match analysis"""
    skill: str
    strength: int = Field(..., ge=1, le=5, description="Skill strength rating (1-5)")
    evidence_snippets: List[str]
    repos_referenced: List[str]


class CodeQuality(BaseModel):
    """Code quality assessment"""
    style: str
    readability: str
    testing: str
    documentation: str
    security: str


class CommitHabits(BaseModel):
    """Commit habits analysis"""
    frequency: str
    message_quality: str
    collaboration_signals: str


class InterviewQuestion(BaseModel):
    """Interview question suggestion"""
    question: str
    rationale: str
    difficulty: str = Field(..., pattern="^(beginner|intermediate|advanced)$")


class RiskFlag(BaseModel):
    """Risk flag identification"""
    flag: str
    description: str
    severity: str


class OverallAssessment(BaseModel):
    """Overall candidate assessment"""
    decision_hint: str = Field(..., pattern="^(strong_yes|yes|maybe|no)$")
    justification: str


class CandidateInfo(BaseModel):
    """Candidate information"""
    github_username: str
    summary_of_work: str
    notable_repos: List[str]


class AnalysisReport(BaseModel):
    """Complete analysis report"""
    candidate: CandidateInfo
    skills_match: List[SkillsMatch]
    code_quality: CodeQuality
    commit_habits: CommitHabits
    interview_questions: List[InterviewQuestion]
    risk_flags: List[RiskFlag]
    overall_assessment: OverallAssessment


class JobStatusResponse(BaseModel):
    """Response model for job status check"""
    job_id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    
    # Optional fields based on status
    report: Optional[AnalysisReport] = None
    generated_at: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None