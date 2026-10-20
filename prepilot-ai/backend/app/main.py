from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import (
    ENVIRONMENT,
    HOST,
    PORT,
    DEBUG,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_API_URL,
    DATABASE_URL,
    FRONTEND_ORIGIN,
    ALLOWED_ORIGINS,
    UPLOAD_DIR,
    MAX_UPLOAD_SIZE,
    ALLOWED_EXTENSIONS,
)
from app.api.router_profile import router as profile_router
from app.api.router_resume import router as resume_router
from app.api.router_job import router as job_router
from app.api.router_interview import router as interview_router
from app.api.router_practice import router as practice_router
from app.api.router_coding import router as coding_router
from app.api.router_dashboard import router as dashboard_router
from app.api.router_reports import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Initialize database tables
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="PrepPilot AI API",
    description="AI-Powered Interview Preparation and Career Readiness Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(profile_router, prefix="/api/v1", tags=["v1"])
app.include_router(resume_router, prefix="/api/v1", tags=["v1"])
app.include_router(job_router, prefix="/api/v1", tags=["v1"])
app.include_router(interview_router, prefix="/api/v1", tags=["v1"])
app.include_router(practice_router, prefix="/api/v1", tags=["v1"])
app.include_router(coding_router, prefix="/api/v1", tags=["v1"])
app.include_router(dashboard_router, prefix="/api/v1", tags=["v1"])
app.include_router(reports_router, prefix="/api/v1", tags=["v1"])


@app.get("/health", tags=["general"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "prepilot-ai-backend"}


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {
        "message": "PrepPilot AI API is running",
        "docs": "/api/docs",
        "version": "1.0.0"
    }