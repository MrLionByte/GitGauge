import json
import asyncio
from typing import Dict, Any, List, Optional
from groq import Groq
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class AIClient:
    """AI client for analyzing GitHub data using Groq/Gemini"""
    
    def __init__(self):
        self.client = None
        if settings.AI_API_KEY:
            try:
                self.client = Groq(api_key=settings.AI_API_KEY)
                logger.info("AI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize AI client: {e}")
                self.client = None
        else:
            logger.warning("No AI API key provided, AI features will be disabled")
    
    def is_available(self) -> bool:
        """Check if AI client is available"""
        return self.client is not None
    
    async def analyze_candidate(self, github_data: Dict[str, Any], skills: List[str], username: str) -> Dict[str, Any]:
        """
        Analyze GitHub data using AI to generate comprehensive candidate assessment
        """
        if not self.is_available():
            logger.warning("AI client not available, returning basic analysis")
            return self._generate_basic_analysis(github_data, skills, username)
        
        try:
            # Prepare the prompt for AI analysis
            prompt = self._create_analysis_prompt(github_data, skills, username)
            
            # Call the AI API
            response = await self._call_ai_api(prompt)
            
            # Parse and validate the response
            analysis = self._parse_ai_response(response)
            
            # Ensure the response matches our schema
            return self._validate_and_format_response(analysis, github_data, skills, username)
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._generate_basic_analysis(github_data, skills, username)
    
    def _create_analysis_prompt(self, github_data: Dict[str, Any], skills: List[str], username: str) -> str:
        """Create a comprehensive prompt for AI analysis"""
        
        # Extract repository information
        repos = github_data.get("repos", [])
        repo_summaries = []
        
        for repo in repos[:5]:  # Limit to top 5 repos
            repo_info = f"""
                    Repository: {repo.get('full_name', 'Unknown')}
                    Description: {repo.get('description', 'No description')}
                    Languages: {', '.join(repo.get('languages', {}).keys())}
                    Stars: {repo.get('stars', 0)}
                    Size: {repo.get('size', 0)} KB
                    Updated: {repo.get('updated_at', 'Unknown')}
                    Matched Skills: {', '.join(repo.get('matched_skills', []))}
                """
            repo_summaries.append(repo_info)
        
        prompt = f"""
You are an expert technical recruiter and software engineer analyzing a GitHub candidate profile. 

CANDIDATE: {username}
SKILLS TO EVALUATE: {', '.join(skills)}

REPOSITORY DATA:
{chr(10).join(repo_summaries)}

Please provide a comprehensive analysis in the following JSON format:

{{
    "candidate": {{
        "github_username": "{username}",
        "summary_of_work": "Brief 2-3 sentence summary of their work and expertise",
        "notable_repos": ["list", "of", "top", "3", "repos"]
    }},
    "skills_match": [
        {{
            "skill": "skill_name",
            "strength": 1-5,
            "evidence_snippets": ["specific evidence 1", "specific evidence 2"],
            "repos_referenced": ["repo1", "repo2"]
        }}
    ],
    "code_quality": {{
        "style": "Poor|Adequate|Good|Excellent",
        "readability": "Low|Medium|High|Excellent", 
        "testing": "Poor|Adequate|Good|Excellent",
        "documentation": "Poor|Adequate|Good|Excellent",
        "security": "Poor|Adequate|Good|Excellent"
    }},
    "commit_habits": {{
        "frequency": "Rare|Occasional|Regular|Frequent",
        "message_quality": "Poor|Adequate|Good|Excellent",
        "collaboration_signals": "Limited|Moderate|Active|Very Active"
    }},
    "interview_questions": [
        {{
            "question": "Specific technical question",
            "rationale": "Why this question is relevant",
            "difficulty": "beginner|intermediate|advanced"
        }}
    ],
    "risk_flags": [
        {{
            "flag": "Flag name",
            "description": "Description of the concern",
            "severity": "low|medium|high"
        }}
    ],
    "overall_assessment": {{
        "decision_hint": "strong_yes|yes|maybe|no",
        "justification": "Detailed reasoning for the decision"
    }}
}}

IMPORTANT GUIDELINES:
1. Be objective and evidence-based
2. Rate skills 1-5 based on concrete evidence
3. Generate 2-3 relevant interview questions
4. Identify any red flags or concerns
5. Provide specific evidence for all assessments
6. Consider both technical depth and breadth
7. Look for patterns in code quality and practices
8. Assess collaboration and communication skills
9. Be fair but thorough in evaluation

Respond ONLY with valid JSON, no additional text.
"""
        return prompt
    
    async def _call_ai_api(self, prompt: str) -> str:
        """Call the AI API with the prompt"""
        try:
            # Use Groq with a current model
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Current Groq model
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical recruiter and software engineer. Provide detailed, objective analysis of GitHub profiles for hiring decisions."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=settings.AI_MAX_TOKENS,
                temperature=0.3,  # Lower temperature for more consistent analysis
                timeout=settings.AI_TIMEOUT
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI API call failed: {e}")
            raise Exception(f"AI analysis failed: {str(e)}")
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response and extract JSON"""
        try:
            # Clean the response to extract JSON
            response = response.strip()
            
            # Find JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in AI response")
            
            json_str = response[start_idx:end_idx]
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            raise Exception(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            raise Exception(f"Failed to parse AI response: {str(e)}")
    
    def _validate_and_format_response(self, analysis: Dict[str, Any], github_data: Dict[str, Any], skills: List[str], username: str) -> Dict[str, Any]:
        """Validate and format the AI response to match our schema"""
        
        # Ensure all required fields are present
        validated = {
            "candidate": analysis.get("candidate", {
                "github_username": username,
                "summary_of_work": f"Developer with {len(github_data.get('repos', []))} repositories",
                "notable_repos": [repo.get('full_name', '') for repo in github_data.get('repos', [])[:3]]
            }),
            "skills_match": analysis.get("skills_match", []),
            "code_quality": analysis.get("code_quality", {
                "style": "Adequate",
                "readability": "Medium", 
                "testing": "Adequate",
                "documentation": "Adequate",
                "security": "Adequate"
            }),
            "commit_habits": analysis.get("commit_habits", {
                "frequency": "Regular",
                "message_quality": "Adequate",
                "collaboration_signals": "Moderate"
            }),
            "interview_questions": analysis.get("interview_questions", []),
            "risk_flags": analysis.get("risk_flags", []),
            "overall_assessment": analysis.get("overall_assessment", {
                "decision_hint": "maybe",
                "justification": "Insufficient data for assessment"
            })
        }
        
        # Validate skills_match has all requested skills
        existing_skills = {skill["skill"] for skill in validated["skills_match"]}
        for skill in skills:
            if skill not in existing_skills:
                validated["skills_match"].append({
                    "skill": skill,
                    "strength": 1,
                    "evidence_snippets": ["No evidence found"],
                    "repos_referenced": []
                })
        
        # Ensure interview questions are properly formatted
        if not validated["interview_questions"]:
            validated["interview_questions"] = [
                {
                    "question": f"Can you walk me through your experience with {skills[0] if skills else 'programming'}?",
                    "rationale": "Assess technical experience",
                    "difficulty": "intermediate"
                }
            ]
        
        return validated
    
    def _generate_basic_analysis(self, github_data: Dict[str, Any], skills: List[str], username: str) -> Dict[str, Any]:
        """Generate basic analysis when AI is not available"""
        repos = github_data.get("repos", [])
        
        # Basic skills analysis
        skills_match = []
        for skill in skills:
            strength = 0
            evidence = []
            repos_ref = []
            
            for repo in repos:
                if skill.lower() in [lang.lower() for lang in repo.get("languages", {}).keys()]:
                    strength += 2
                    evidence.append(f"Found {skill} code in {repo.get('name', '')}")
                    repos_ref.append(repo.get("full_name", ""))
                elif skill.lower() in repo.get("name", "").lower():
                    strength += 1
                    evidence.append(f"Repository name suggests {skill} expertise")
                    if repo.get("full_name", "") not in repos_ref:
                        repos_ref.append(repo.get("full_name", ""))
            
            skills_match.append({
                "skill": skill,
                "strength": min(5, max(1, strength)),
                "evidence_snippets": evidence[:3],
                "repos_referenced": repos_ref[:3]
            })
        
        return {
            "candidate": {
                "github_username": username,
                "summary_of_work": f"Developer with {len(repos)} repositories",
                "notable_repos": [repo.get("full_name", "") for repo in repos[:3]]
            },
            "skills_match": skills_match,
            "code_quality": {
                "style": "Adequate",
                "readability": "Medium",
                "testing": "Adequate", 
                "documentation": "Adequate",
                "security": "Adequate"
            },
            "commit_habits": {
                "frequency": "Regular",
                "message_quality": "Adequate",
                "collaboration_signals": "Moderate"
            },
            "interview_questions": [
                {
                    "question": f"Can you explain your experience with {skills[0] if skills else 'programming'}?",
                    "rationale": "Assess technical background",
                    "difficulty": "intermediate"
                }
            ],
            "risk_flags": [],
            "overall_assessment": {
                "decision_hint": "maybe",
                "justification": "Basic analysis completed, AI analysis recommended for detailed assessment"
            }
        }


# Global AI client instance
ai_client = AIClient()
