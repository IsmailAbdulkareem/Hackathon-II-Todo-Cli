import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

from src.api.tasks import router as tasks_router
from src.core.config import settings
from src.core.database import engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Create database tables
    - Shutdown: Cleanup resources
    """
    # Startup: Create all database tables
    SQLModel.metadata.create_all(engine)
    yield
    # Shutdown: Cleanup (if needed)


# Initialize FastAPI application
app = FastAPI(
    title="Todo Backend API",
    description="FastAPI backend for Todo application with PostgreSQL persistence",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests with timestamp, endpoint, and response status.
    """
    start_time = time.time()

    # Extract user_id from path if present
    user_id = request.path_params.get("user_id", "N/A")

    # Log request
    logger.info(f"Request: {request.method} {request.url.path} | User: {user_id}")

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log response
    logger.info(
        f"Response: {request.method} {request.url.path} | "
        f"Status: {response.status_code} | Duration: {duration:.3f}s"
    )

    return response


# Global exception handler for database errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Returns a generic 500 error to avoid leaking implementation details.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Register API routers
app.include_router(tasks_router)


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Todo Backend API is running",
        "docs": "/docs"
    }
