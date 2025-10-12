import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class GitHubClient:
    """GitHub API client for fetching user repositories and analyzing code"""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": f"{settings.APP_NAME}/{settings.APP_VERSION}"
        }
        
        # Add authentication if token is provided and valid
        if settings.GITHUB_TOKEN:
            print("Github Auth token is =>", settings.GITHUB_TOKEN)
            self.headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"
        
        self.timeout = httpx.Timeout(settings.GITHUB_TIMEOUT)
        self.rate_limit_remaining = settings.GITHUB_RATE_LIMIT
        self.rate_limit_reset = None
    
    async def _make_request(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to GitHub API with rate limiting and error handling"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers, params=params)
                
                # Update rate limit info
                self.rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
                reset_timestamp = response.headers.get("X-RateLimit-Reset")
                if reset_timestamp:
                    self.rate_limit_reset = datetime.fromtimestamp(int(reset_timestamp))
                
                # Check rate limit
                if response.status_code == 403 and "rate limit" in response.text.lower():
                    reset_time = self.rate_limit_reset or datetime.now() + timedelta(hours=1)
                    wait_seconds = (reset_time - datetime.now()).total_seconds()
                    logger.warning(f"Rate limit exceeded. Resets at {reset_time}. Waiting {wait_seconds}s")
                    raise Exception(f"GitHub API rate limit exceeded. Resets at {reset_time}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            logger.error(f"Timeout while fetching {url}")
            raise Exception("GitHub API request timed out")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise Exception("GitHub user not found")
            elif e.response.status_code == 403:
                raise Exception("GitHub API access forbidden. Check token permissions.")
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                raise Exception(f"GitHub API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            raise
    
    async def get_user_repositories(self, username: str, per_page: int = 100, sort: str = "updated") -> List[Dict[str, Any]]:
        """Fetch all repositories for a user"""
        url = f"{self.base_url}/users/{username}/repos"
        params = {
            "per_page": per_page,
            "sort": sort,
            "type": "owner"  # Only get repos owned by the user
        }
        
        all_repos = []
        page = 1
        
        while True:
            params["page"] = page
            repos = await self._make_request(url, params)
            
            if not repos:
                break
                
            all_repos.extend(repos)
            
            # If we got fewer repos than requested, we've reached the end
            if len(repos) < per_page:
                break
                
            page += 1
            
            # Safety limit to prevent infinite loops
            if page > 20:  # Max 2000 repos
                break
        
        logger.info(f"Fetched {len(all_repos)} repositories for user {username}")
        return all_repos
    
    async def get_repository_languages(self, owner: str, repo_name: str) -> Dict[str, int]:
        """Get programming languages used in a repository"""
        url = f"{self.base_url}/repos/{owner}/{repo_name}/languages"
        try:
            languages = await self._make_request(url)
            return languages
        except Exception as e:
            logger.warning(f"Could not fetch languages for {owner}/{repo_name}: {str(e)}")
            return {}
    
    async def get_repository_readme(self, owner: str, repo_name: str) -> Optional[str]:
        """Get repository README content"""
        url = f"{self.base_url}/repos/{owner}/{repo_name}/readme"
        try:
            readme_data = await self._make_request(url)
            # The content is base64 encoded
            import base64
            content = base64.b64decode(readme_data["content"]).decode("utf-8")
            return content
        except Exception as e:
            logger.warning(f"Could not fetch README for {owner}/{repo_name}: {str(e)}")
            return None
    
    async def search_repositories_by_skills(self, username: str, skills: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find repositories that match the given skills
        Returns top repositories sorted by relevance
        """
        all_repos = await self.get_user_repositories(username)
        
        if not all_repos:
            return []
        
        # Score repositories based on skill matches
        scored_repos = []
        
        for repo in all_repos:
            score = 0
            matched_skills = []
            
            # Get repository languages
            languages = await self.get_repository_languages(repo["owner"]["login"], repo["name"])
            
            # Get README content for additional context
            readme = await self.get_repository_readme(repo["owner"]["login"], repo["name"])
            readme_text = readme.lower() if readme else ""
            
            # Check language matches
            for skill in skills:
                skill_lower = skill.lower()
                
                # Direct language match
                if skill_lower in [lang.lower() for lang in languages.keys()]:
                    score += 3
                    matched_skills.append(skill)
                
                # Check in repository name
                if skill_lower in repo["name"].lower():
                    score += 2
                    if skill not in matched_skills:
                        matched_skills.append(skill)
                
                # Check in description
                if repo.get("description") and skill_lower in repo["description"].lower():
                    score += 1
                    if skill not in matched_skills:
                        matched_skills.append(skill)
                
                # Check in README
                if readme_text and skill_lower in readme_text:
                    score += 1
                    if skill not in matched_skills:
                        matched_skills.append(skill)
            
            # Add repository metadata
            repo_data = {
                "id": repo["id"],
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo.get("description", ""),
                "html_url": repo["html_url"],
                "clone_url": repo["clone_url"],
                "languages": languages,
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "size": repo["size"],
                "updated_at": repo["updated_at"],
                "created_at": repo["created_at"],
                "score": score,
                "matched_skills": matched_skills,
                "readme_preview": readme[:500] if readme else ""  # First 500 chars
            }
            
            scored_repos.append(repo_data)
        
        # Sort by score (descending) and return top results
        scored_repos.sort(key=lambda x: x["score"], reverse=True)
        
        # Filter out repos with no skill matches
        relevant_repos = [repo for repo in scored_repos if repo["score"] > 0]
        
        logger.info(f"Found {len(relevant_repos)} repositories matching skills {skills}")
        return relevant_repos[:limit]
    
    async def get_repository_content(self, owner: str, repo_name: str, path: str = "") -> List[Dict[str, Any]]:
        """Get repository file contents (limited to avoid large responses)"""
        url = f"{self.base_url}/repos/{owner}/{repo_name}/contents/{path}"
        try:
            contents = await self._make_request(url)
            
            # Filter for code files only
            code_files = []
            for item in contents:
                if item["type"] == "file":
                    # Check if it's a code file
                    file_name = item["name"].lower()
                    if any(file_name.endswith(ext) for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb', '.swift', '.kt']):
                        code_files.append({
                            "name": item["name"],
                            "path": item["path"],
                            "size": item["size"],
                            "download_url": item["download_url"],
                            "html_url": item["html_url"]
                        })
            
            return code_files[:10]  # Limit to 10 files
            
        except Exception as e:
            logger.warning(f"Could not fetch content for {owner}/{repo_name}/{path}: {str(e)}")
            return []
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get current rate limit information"""
        has_valid_token = bool(settings.GITHUB_TOKEN and settings.GITHUB_TOKEN != "your_github_token_here")
        return {
            "remaining": self.rate_limit_remaining,
            "reset_at": self.rate_limit_reset.isoformat() if self.rate_limit_reset else None,
            "has_token": has_valid_token,
            "note": "Using unauthenticated API (60 requests/hour)" if not has_valid_token else "Using authenticated API (5000 requests/hour)"
        }


# Global GitHub client instance
github_client = GitHubClient()
