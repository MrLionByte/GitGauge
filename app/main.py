from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import settings
from app.api.routers import jobs
from contextlib import asynccontextmanager
from app.db.base import create_tables
from app.workers.tasks import start_background_processor
import asyncio

# Create database tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    print("✅ Tables created at startup")
    
    # Start background processor
    asyncio.create_task(start_background_processor())
    print("✅ Background processor started")
    
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Tech candidate screening API that analyzes GitHub profiles",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Include routers
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")


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
