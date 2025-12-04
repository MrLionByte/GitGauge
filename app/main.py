from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routers import jobs
from contextlib import asynccontextmanager
from app.db.base import create_tables
from app.workers.tasks import start_background_processor
from app.utils.logging import setup_logging, log_api_request
import asyncio, time, uuid

# Setup logging
logger = setup_logging(
    level="INFO" if not settings.DEBUG else "DEBUG",
)

# Create database tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting GitGauge application...")
    
    try:
        await create_tables()
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise
    
    try:
        # Start background processor
        asyncio.create_task(start_background_processor())
        logger.info("✅ Background job processor started")
    except Exception as e:
        logger.error(f"❌ Failed to start background processor: {e}")
        raise
    
    logger.info("🎉 Application startup completed successfully")
    yield
    
    logger.info("🛑 Shutting down GitGauge application...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Tech candidate screening API that analyzes GitHub profiles",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    # Log request
    logger.info(f"📥 {request.method} {request.url.path} [ID: {request_id}]")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    log_api_request(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=duration
    )
    
    return response

# Include routers
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with API documentation"""
    logger.info("🏠 Home page accessed")
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/test-api", response_class=HTMLResponse)
async def home(request: Request):
    """Test Api page with API interaction"""
    logger.info("📝 Api test accessed")
    return templates.TemplateResponse("test_api.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.debug("🏥 Health check requested")
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
