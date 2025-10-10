"""Main FastAPI application for GitGauge."""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from datetime import datetime

from app.core.config import settings
from api.routers import jobs
from app.api.schemas.jobs import HealthResponse

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="GitGauge - Automated GitHub Profile Analysis for Technical Recruiting",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Static & templates setup
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(jobs.router, prefix="/api/v1")

# Routes
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request):
    """Serve main landing page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.app_version,
        database_status="connected"
    )


@app.get("/api/v1/", include_in_schema=False)
async def api_info():
    """API information endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "GitGauge - Automated GitHub Profile Analysis for Technical Recruiting",
        "endpoints": {
            "create_job": "POST /api/v1/jobs/",
            "get_job": "GET /api/v1/jobs/{job_id}",
            "list_jobs": "GET /api/v1/jobs/",
            "health": "GET /health"
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
