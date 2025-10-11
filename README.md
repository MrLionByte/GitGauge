# 🔍 GitGauge

**Tech Candidate Screening API** - Automated GitHub profile analysis for intelligent hiring decisions.

GitGauge simplifies tech candidate screening into a non-blocking, two-step flow:
- Recruiter submits `github_username` and required `skills` → API returns `job_id` immediately
- Recruiter later polls `job_id` to retrieve a structured, actionable analysis report

## 🚀 Features

- **🎯 Skills Analysis**: Comprehensive evaluation of technical skills with evidence-based scoring
- **📊 Code Quality Assessment**: Analysis of coding style, readability, testing, and documentation
- **📈 Commit Pattern Analysis**: Evaluation of commit frequency, message quality, and collaboration
- **❓ Interview Questions**: AI-generated, tailored interview questions based on code
- **⚠️ Risk Assessment**: Identification of potential red flags and areas of concern
- **🎯 Overall Recommendation**: Clear hiring recommendation with detailed justification

## 🏗️ Architecture

- **FastAPI monolith** with clean internal boundaries
- **Async background processing** using FastAPI BackgroundTasks
- **PostgreSQL with JSONB** for flexible LLM output storage
- **GitHub API integration** with web scraping fallback
- **AI/LLM integration** for generating structured analysis reports

## 📋 API Endpoints

### POST `/api/jobs`
Create a new analysis job.

**Request:**
```json
{
  "github_username": "octocat",
  "skills": ["Python", "JavaScript", "React"],
  "repo_limit": 10,
  "max_files_per_repo": 5,
  "languages": ["Python", "JavaScript"],
  "notes_for_ai": "Focus on backend development skills"
}
```

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "queued",
  "estimated_wait_seconds": 300
}
```

### GET `/api/jobs/{job_id}`
Get job status and results.

**Response (Completed):**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z",
  "report": {
    "candidate": {
      "github_username": "octocat",
      "summary_of_work": "Full-stack developer with 5+ years experience...",
      "notable_repos": ["awesome-project", "cool-library"]
    },
    "skills_match": [
      {
        "skill": "Python",
        "strength": 4,
        "evidence_snippets": ["def calculate_score():", "import pandas as pd"],
        "repos_referenced": ["data-analysis", "ml-project"]
      }
    ],
    "code_quality": {
      "style": "Good",
      "readability": "Excellent",
      "testing": "Good",
      "documentation": "Excellent",
      "security": "Good"
    },
    "commit_habits": {
      "frequency": "Regular",
      "message_quality": "Good",
      "collaboration_signals": "Active in team projects"
    },
    "interview_questions": [
      {
        "question": "How do you handle error handling in Python?",
        "rationale": "Based on your Python code patterns",
        "difficulty": "intermediate"
      }
    ],
    "risk_flags": [],
    "overall_assessment": {
      "decision_hint": "yes",
      "justification": "Strong technical skills with good code quality"
    }
  },
  "generated_at": "2024-01-15T10:35:00Z"
}
```

### GET `/api/jobs`
List recent jobs.

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (or SQLite for development)
- GitHub API token
- AI API key (OpenAI, Groq, etc.)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GitGauge
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .gitgauge-venv
   source .gitgauge-venv/bin/activate  # On Windows: .gitgauge-venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

### Environment Variables

```env
# Database Configuration
DATABASE_URL=sqlite:///./gitgauge.db

# GitHub Configuration
GITHUB_TOKEN=your_github_token_here

# AI Configuration
AI_API_KEY=your_ai_api_key_here
AI_MODEL=gpt-3.5-turbo

# Application Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

## 🧪 Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Create a job
curl -X POST "http://localhost:8000/api/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "github_username": "octocat",
    "skills": ["Python", "Django", "PostgreSQL"]
  }'

# Check job status
curl "http://localhost:8000/api/jobs/{job_id}"
```

## 📊 Job Status

- **`queued`**: Job is waiting to be processed
- **`running`**: Analysis is currently in progress
- **`completed`**: Analysis completed successfully
- **`failed`**: Analysis failed with error details

## 🏗️ Development

### Project Structure
```
GitGauge/
├── app/
│   ├── main.py                # FastAPI entrypoint
│   ├── config.py              # Environment settings
│   ├── api/
│   │   ├── routers/
│   │   │   └── jobs.py        # Job endpoints
│   │   └── schemas/
│   │       └── jobs.py         # Request/Response models
│   ├── services/
│   │   ├── job_service.py     # Job business logic
│   │   └── analysis_service.py# Analysis workflow
│   ├── integrations/
│   │   ├── github_client.py   # GitHub API wrapper
│   │   └── ai_client.py       # AI API wrapper
│   ├── workers/
│   │   ├── tasks.py           # Background tasks
│   │   └── queue.py           # Queue abstraction
│   ├── db/
│   │   ├── base.py            # Database connection
│   │   ├── models.py          # SQLAlchemy models
│   │   └── repositories.py    # Database operations
│   ├── templates/
│   │   └── index.html         # Home page
│   └── static/
│       └── style.css          # Home page styles
├── requirements.txt
├── .env.example
└── README.md
```

### Phase Development

- **Phase 1**: ✅ Project scaffolding and basic setup
- **Phase 2**: ✅ API + DB setup with home page
- **Phase 3**: Background task + mock analysis
- **Phase 4**: GitHub integration
- **Phase 5**: AI/LLM integration
- **Phase 6**: Final report persistence

## 🔗 Links

- **Home Page**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions or support, please open an issue in the repository.