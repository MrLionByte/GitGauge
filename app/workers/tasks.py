import asyncio
from typing import Dict, Any
from app.workers.queue import job_queue
from app.workers.redis_manager import redis_manager
from app.db.base import get_db_session
from app.db.repositories import JobRepository, JobArtifactRepository
from app.db.models import JobStatus
from app.integrations.github_client import github_client
from app.integrations.ai_client import ai_client
import json
from datetime import datetime


async def analyze_repositories(repos: list, skills: list, username: str) -> Dict[str, Any]:
    """
    Analyze GitHub repositories using AI for comprehensive candidate assessment
    Phase 5: Enhanced AI-powered analysis
    """
    if not repos:
        return {
            "summary": f"No relevant repositories found for {username}",
            "skills_match": [],
            "code_quality": {"style": "Unknown", "readability": "Unknown", "testing": "Unknown", "documentation": "Unknown", "security": "Unknown"},
            "commit_habits": {"frequency": "Unknown", "message_quality": "Unknown", "collaboration_signals": "Unknown"},
            "interview_questions": [],
            "risk_flags": [],
            "overall_assessment": {"decision_hint": "no", "justification": "No relevant repositories found"}
        }
    
    print(f"🤖 Using AI analysis for {len(repos)} repositories")
    
    # Prepare GitHub data for AI analysis
    github_data = {
        "repos": repos,
        "username": username,
        "total_repos": len(repos),
        "total_stars": sum(repo.get("stars", 0) for repo in repos),
        "languages": list(set([lang for repo in repos for lang in repo.get("languages", {}).keys()]))
    }
    
    try:
        # Use AI client for enhanced analysis
        ai_analysis = await ai_client.analyze_candidate(github_data, skills, username)
        
        # Generate summary from AI analysis
        top_skills = [skill["skill"] for skill in ai_analysis.get("skills_match", []) if skill.get("strength", 0) >= 3]
        summary = f"Active developer with {len(repos)} relevant repositories"
        if top_skills:
            summary += f" showing expertise in {', '.join(top_skills)}"
        if github_data["total_stars"] > 0:
            summary += f" with {github_data['total_stars']} total stars"
        
        # Add summary to the analysis
        ai_analysis["summary"] = summary
        
        print(f"✅ AI analysis completed successfully")
        return ai_analysis
        
    except Exception as e:
        print(f"⚠️ AI analysis failed, falling back to basic analysis: {str(e)}")
        
        # Fallback to basic analysis if AI fails
        return await _basic_analysis_fallback(repos, skills, username)


async def _basic_analysis_fallback(repos: list, skills: list, username: str) -> Dict[str, Any]:
    """
    Fallback basic analysis when AI is not available
    """
    # Analyze skills match
    skills_match = []
    for skill in skills:
        skill_lower = skill.lower()
        strength = 0
        evidence_snippets = []
        repos_referenced = []
        
        for repo in repos:
            if skill_lower in [lang.lower() for lang in repo.get("languages", {}).keys()]:
                strength += 2
                evidence_snippets.append(f"Found {skill} code in {repo['name']}")
                repos_referenced.append(repo["full_name"])
            
            if skill_lower in repo.get("name", "").lower():
                strength += 1
                evidence_snippets.append(f"Repository name suggests {skill} expertise: {repo['name']}")
                if repo["full_name"] not in repos_referenced:
                    repos_referenced.append(repo["full_name"])
            
            if skill_lower in repo.get("description", "").lower():
                strength += 1
                evidence_snippets.append(f"Repository description mentions {skill}: {repo['description']}")
                if repo["full_name"] not in repos_referenced:
                    repos_referenced.append(repo["full_name"])
        
        # Normalize strength to 1-5 scale
        normalized_strength = min(5, max(1, strength))
        
        skills_match.append({
            "skill": skill,
            "strength": normalized_strength,
            "evidence_snippets": evidence_snippets[:3],  # Limit to top 3
            "repos_referenced": repos_referenced[:3]  # Limit to top 3
        })
    
    # Analyze code quality based on repository characteristics
    total_stars = sum(repo.get("stars", 0) for repo in repos)
    avg_stars = total_stars / len(repos) if repos else 0
    
    # Check for testing indicators
    testing_indicators = 0
    for repo in repos:
        if any(keyword in repo.get("description", "").lower() for keyword in ["test", "testing", "spec", "unit"]):
            testing_indicators += 1
        if any(keyword in repo.get("name", "").lower() for keyword in ["test", "spec"]):
            testing_indicators += 1
    
    # Check for documentation indicators
    doc_indicators = 0
    for repo in repos:
        if repo.get("readme_preview"):
            doc_indicators += 1
        if any(keyword in repo.get("description", "").lower() for keyword in ["doc", "documentation", "guide", "tutorial"]):
            doc_indicators += 1
    
    code_quality = {
        "style": "Good" if avg_stars > 10 else "Adequate",
        "readability": "High" if any(len(repo.get("description", "")) > 50 for repo in repos) else "Medium",
        "testing": "Good" if testing_indicators > len(repos) / 2 else "Adequate",
        "documentation": "Good" if doc_indicators > len(repos) / 2 else "Adequate",
        "security": "Good" if any("security" in repo.get("description", "").lower() for repo in repos) else "Adequate"
    }
    
    # Analyze commit habits (simplified based on repository activity)
    recent_repos = [repo for repo in repos if repo.get("updated_at")]
    commit_habits = {
        "frequency": "Regular" if len(recent_repos) > 2 else "Occasional",
        "message_quality": "Good" if any(len(repo.get("description", "")) > 20 for repo in repos) else "Adequate",
        "collaboration_signals": "Active" if total_stars > 5 else "Limited"
    }
    
    # Generate interview questions based on skills and repositories
    interview_questions = []
    for skill in skills[:2]:  # Top 2 skills
        interview_questions.append({
            "question": f"Can you walk me through your experience with {skill} based on your GitHub projects?",
            "rationale": f"Assess practical {skill} experience through real projects",
            "difficulty": "intermediate"
        })
    
    if len(repos) > 3:
        interview_questions.append({
            "question": "I see you have multiple repositories. How do you organize and maintain your projects?",
            "rationale": "Assess project management and organization skills",
            "difficulty": "intermediate"
        })
    
    # Identify risk flags
    risk_flags = []
    if avg_stars < 1 and len(repos) > 5:
        risk_flags.append({
            "flag": "Low Engagement",
            "description": "Many repositories but low community engagement",
            "severity": "medium"
        })
    
    if not any(repo.get("readme_preview") for repo in repos):
        risk_flags.append({
            "flag": "Poor Documentation",
            "description": "Lack of README files in repositories",
            "severity": "low"
        })
    
    # Overall assessment
    avg_skill_strength = sum(skill["strength"] for skill in skills_match) / len(skills_match) if skills_match else 0
    
    if avg_skill_strength >= 4 and len(repos) >= 2:
        decision_hint = "strong_yes"
        justification = f"Strong evidence of {', '.join(skills[:2])} expertise with multiple relevant projects"
    elif avg_skill_strength >= 3 and len(repos) >= 1:
        decision_hint = "yes"
        justification = f"Good evidence of {', '.join(skills[:2])} skills with relevant projects"
    elif avg_skill_strength >= 2:
        decision_hint = "maybe"
        justification = f"Some evidence of {', '.join(skills[:2])} skills but limited project depth"
    else:
        decision_hint = "no"
        justification = f"Insufficient evidence of {', '.join(skills[:2])} expertise"
    
    overall_assessment = {
        "decision_hint": decision_hint,
        "justification": justification
    }
    
    # Generate summary
    top_skills = [skill["skill"] for skill in skills_match if skill["strength"] >= 3]
    summary = f"Active developer with {len(repos)} relevant repositories"
    if top_skills:
        summary += f" showing expertise in {', '.join(top_skills)}"
    if total_stars > 0:
        summary += f" with {total_stars} total stars"
    
    return {
        "summary": summary,
        "skills_match": skills_match,
        "code_quality": code_quality,
        "commit_habits": commit_habits,
        "interview_questions": interview_questions,
        "risk_flags": risk_flags,
        "overall_assessment": overall_assessment
    }


async def process_analysis_job(job_id: str, github_username: str, skills: list):
    """
    Background task to process GitHub analysis job
    Phase 4: Real GitHub integration
    """
    try:
        # Update status to running
        await job_queue.update_job_status(job_id, "running")
        
        print(f"🔍 Starting GitHub analysis for {github_username} with skills: {skills}")
        
        # Fetch repositories matching the skills
        try:
            relevant_repos = await github_client.search_repositories_by_skills(
                username=github_username,
                skills=skills,
                limit=5  # Top 5 most relevant repos
            )
        except Exception as e:
            print(f"❌ GitHub API error: {str(e)}")
            raise Exception(f"Failed to fetch GitHub data: {str(e)}")
        
        if not relevant_repos:
            raise Exception(f"No repositories found matching skills: {', '.join(skills)}")
        
        print(f"📊 Found {len(relevant_repos)} relevant repositories")
        
        # Analyze the repositories
        analysis_data = await analyze_repositories(relevant_repos, skills, github_username)
        
        # Create analysis report
        analysis_report = {
            "candidate": {
                "github_username": github_username,
                "summary_of_work": analysis_data["summary"],
                "notable_repos": [repo["full_name"] for repo in relevant_repos[:3]]
            },
            "skills_match": analysis_data["skills_match"],
            "code_quality": analysis_data["code_quality"],
            "commit_habits": analysis_data["commit_habits"],
            "interview_questions": analysis_data["interview_questions"],
            "risk_flags": analysis_data["risk_flags"],
            "overall_assessment": analysis_data["overall_assessment"]
        }
        
        # Store result in database
        from app.db.base import get_db_session
        db = get_db_session()
        try:
            job_repo = JobRepository(db)
            artifact_repo = JobArtifactRepository(db)
            
            # Update job status
            job = job_repo.get_job_by_id(job_id)
            if job:
                job_repo.update_job_status(job_id, JobStatus.COMPLETED)
                
                # Create artifact with real GitHub data
                artifact_repo.create_artifact(
                    job_id=job_id,
                    raw_sources={"github_repos": relevant_repos},
                    report=analysis_report
                )
        finally:
            db.close()
        
        # Update Redis status
        await job_queue.update_job_status(job_id, "completed", result=analysis_report)
        
        print(f"✅ Job {job_id} completed successfully")
        
    except Exception as e:
        # Handle errors
        print(f"❌ Job {job_id} failed: {str(e)}")
        
        # Update database with error
        try:
            from app.db.base import get_db_session
            db = get_db_session()
            try:
                job_repo = JobRepository(db)
                job_repo.update_job_status(
                    job_id, 
                    JobStatus.FAILED, 
                    error_code="PROCESSING_ERROR",
                    error_message=str(e)
                )
            finally:
                db.close()
        except Exception as db_error:
            print(f"Failed to update job status in DB: {db_error}")
        
        # Update Redis status
        await job_queue.update_job_status(job_id, "failed", error=str(e))


async def start_background_processor():
    """
    Start the background job processor
    This runs continuously to process jobs from the queue
    """
    print("🚀 Starting background job processor...")
    
    while True:
        try:
            # Check for jobs in queue
            job_id = await redis_manager.get("queue:processing")
            
            if job_id:
                # Get job data
                job_data_str = await redis_manager.get(f"job:{job_id}")
                if job_data_str:
                    job_data = json.loads(job_data_str)
                    
                    # Process the job
                    await process_analysis_job(
                        job_id=job_id,
                        github_username=job_data.get("github_username", ""),
                        skills=job_data.get("skills", [])
                    )
                    
                    # Remove from queue
                    await redis_manager.delete("queue:processing")
                    await redis_manager.delete(f"job:{job_id}")
            
            # Wait before checking again
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"Error in background processor: {e}")
            await asyncio.sleep(5)  # Wait longer on error
