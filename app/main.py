from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import settings
from app.api.routers import jobs
from app.db.base import create_tables

app = FastAPI(
    title=settings.APP_NAME,
    description="Tech candidate screening API that analyzes GitHub profiles",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include routers
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with API documentation"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "GitGauge",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
