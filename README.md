# GitGauge 🎯
### [Live Link](https://gitgauge.onrender.com/)

**AI-Powered GitHub Candidate Screening Platform**

GitGauge is a comprehensive technical recruitment tool that analyzes GitHub profiles to provide detailed candidate assessments using AI. It combines GitHub API data with advanced AI analysis to generate professional hiring recommendations.

## 🚀 Features

### Core Capabilities
- **GitHub Integration**: Fetches and analyzes user repositories
- **AI-Powered Analysis**: Uses Groq/Gemini for intelligent candidate assessment
- **Skills Matching**: Evaluates technical skills with evidence-based scoring
- **Code Quality Assessment**: Analyzes code style, documentation, and practices
- **Interview Questions**: Generates relevant technical interview questions
- **Risk Assessment**: Identifies potential red flags and concerns
- **Hiring Recommendations**: Provides data-driven hiring decisions

### Technical Features
- **RESTful API**: FastAPI-based with comprehensive documentation
- **Background Processing**: Asynchronous job processing with Redis
- **Database Persistence**: PostgreSQL with SQLAlchemy ORM
- **Comprehensive Logging**: Detailed logging and error handling
- **Rate Limiting**: GitHub API rate limit management
- **CORS Support**: Cross-origin resource sharing enabled

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  GitHub Client  │    │   AI Client     │
│                 │    │                 │    │                 │
│ • Job Creation  │───▶│ • Repo Fetching │───▶│ • Groq/Gemini   │
│ • Status Check  │    │ • Skills Filter │    │ • Analysis      │
│ • Results API   │    │ • Rate Limiting │    │ • Report Gen    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │  Background     │
│                 │    │                 │    │  Workers        │
│ • Job Storage   │    │ • Job Queue     │    │                 │
│ • Artifacts     │    │ • Status Cache  │    │ • Job Processing│
│ • Reports       │    │ • Rate Limiting │    │ • Error Handling│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- GitHub API Token (optional, for higher rate limits)
- Groq API Key (for AI analysis)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GitGauge
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   # Ensure PostgreSQL is running
   # The app will create tables automatically on startup
   ```

6. **Start Redis**
   ```bash
   redis-server
   ```

7. **Run the application**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/gitgauge

# GitHub API
GITHUB_TOKEN=your_github_token_here  # Optional but recommended

# AI Configuration
AI_API_KEY=your_groq_api_key_here

# Redis
REDIS_URL=redis://localhost:6379/0

# Application
APP_NAME=GitGauge
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### API Keys Setup

1. **GitHub Token** (Optional)
   - Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
   - Generate a token with `public_repo` scope
   - Add to `.env` file

2. **Groq API Key** (Required for AI features)
   - Sign up at [Groq Console](https://console.groq.com/)
   - Generate an API key
   - Add to `.env` file

## 📚 API Usage

### Create Analysis Job

```bash
curl -X POST "http://localhost:8000/api/jobs/" \
  -H "Content-Type: application/json" \
  -d '{
    "github_username": "torvalds",
    "skills": ["C", "Linux", "kernel"],
    "repo_limit": 10,
    "max_files_per_repo": 5,
    "languages": ["C", "Python"],
    "notes_for_ai": "Looking for kernel development expertise"
  }'
```

**Response:**
```json
{
  "job_id": "uuid-here",
  "status": "queued",
  "estimated_wait_seconds": 300
}
```

### Check Job Status

```bash
curl "http://localhost:8000/api/jobs/{job_id}"
```

**Response:**
```json
{
  "job_id": "uuid-here",
  "status": "completed",
  "created_at": "2025-10-12T18:02:09.666813+05:30",
  "updated_at": "2025-10-12T18:02:26.006046+05:30",
  "report": {
    "candidate": {
      "github_username": "torvalds",
      "summary_of_work": "Active developer with 5 relevant repositories...",
      "notable_repos": ["torvalds/linux", "torvalds/subsurface-for-dirk"]
    },
    "skills_match": [
      {
        "skill": "C",
        "strength": 5,
        "evidence_snippets": ["Found C code in linux", "..."],
        "repos_referenced": ["torvalds/linux", "..."]
      }
    ],
    "code_quality": {
      "style": "Excellent",
      "readability": "Excellent",
      "testing": "Good",
      "documentation": "Good",
      "security": "Good"
    },
    "commit_habits": {
      "frequency": "Frequent",
      "message_quality": "Excellent",
      "collaboration_signals": "Very Active"
    },
    "interview_questions": [
      {
        "question": "Can you explain the Linux kernel's memory management subsystem?",
        "rationale": "Assesses understanding of kernel-level memory management",
        "difficulty": "advanced"
      }
    ],
    "risk_flags": [
      {
        "flag": "Lack of diversity in project types",
        "description": "Most projects are related to Linux kernel development...",
        "severity": "medium"
      }
    ],
    "overall_assessment": {
      "decision_hint": "strong_yes",
      "justification": "Linus Torvalds' GitHub profile showcases exceptional expertise..."
    }
  },
  "generated_at": "2025-10-12T18:02:26.055519+05:30"
}
```

### List Recent Jobs

```bash
curl "http://localhost:8000/api/jobs/?limit=10"
```

## 🎯 Analysis Components

### Skills Assessment
- **Strength Rating**: 1-5 scale based on evidence
- **Evidence Snippets**: Specific examples from repositories
- **Repository References**: Links to relevant projects

### Code Quality Analysis
- **Style**: Code organization and consistency
- **Readability**: Code clarity and documentation
- **Testing**: Test coverage and quality indicators
- **Documentation**: README and code documentation
- **Security**: Security best practices

### Interview Questions
- **Technical Depth**: Questions based on actual projects
- **Difficulty Levels**: Beginner, intermediate, advanced
- **Rationale**: Why each question is relevant

### Risk Assessment
- **Red Flags**: Potential concerns identified
- **Severity Levels**: Low, medium, high
- **Descriptions**: Detailed explanations

## 🔍 Development

### Project Structure

```
GitGauge/
├── app/
│   ├── api/
│   │   ├── routers/
│   │   │   └── jobs.py          # Job API endpoints
│   │   └── schemas/
│   │       └── jobs.py          # Pydantic models
│   ├── db/
│   │   ├── base.py              # Database configuration
│   │   ├── models.py            # SQLAlchemy models
│   │   └── repositories.py      # Data access layer
│   ├── integrations/
│   │   ├── github_client.py     # GitHub API client
│   │   └── ai_client.py         # AI analysis client
│   ├── services/
│   │   └── analysis_service.py  # Business logic
│   ├── utils/
│   │   ├── logging.py           # Logging utilities
│   │   └── id_gen.py            # ID generation
│   ├── workers/
│   │   ├── tasks.py             # Background job processing
│   │   ├── queue.py             # Job queue management
│   │   └── redis_manager.py     # Redis operations
│   ├── static/                  # Static files
│   ├── templates/               # HTML templates
│   ├── config.py                # Configuration
│   └── main.py                  # FastAPI application
├── requirements.txt             # Python dependencies
├── env.example                  # Environment template
└── README.md                    # This file
```

### Running Tests

```bash
# Run the application
python -m uvicorn app.main:app --reload

# Test API endpoints
curl -X POST "http://localhost:8000/api/jobs/" \
  -H "Content-Type: application/json" \
  -d '{"github_username": "torvalds", "skills": ["C", "Linux"]}'
```

### Logging

The application includes comprehensive logging:

- **Request Logging**: All HTTP requests and responses
- **Job Progress**: Detailed job processing steps
- **Error Handling**: Contextual error logging
- **Performance**: Timing and resource usage

Logs are output to console with color coding and can be configured for file output.

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Set all required environment variables
2. **Database**: Use production PostgreSQL instance
3. **Redis**: Use production Redis instance
4. **API Keys**: Ensure all API keys are properly configured
5. **Logging**: Configure file-based logging for production
6. **Monitoring**: Set up application monitoring
7. **Rate Limiting**: Configure appropriate rate limits

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs` when running the application
- Review the logs for debugging information

## 🎉 Acknowledgments

- FastAPI for the excellent web framework
- Groq for AI model access
- GitHub for the comprehensive API
- PostgreSQL and Redis for data storage
- The open-source community for inspiration and tools
