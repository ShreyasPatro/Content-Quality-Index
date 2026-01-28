"""FastAPI application initialization."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core import get_logger, settings, setup_logging
from app.db import close_async_engine, health_check

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Content Quality Engine API")
    logger.info(f"Environment: {settings.environment}")

    yield

    # Shutdown
    logger.info("Shutting down Content Quality Engine API")
    await close_async_engine()


# Create FastAPI app
app = FastAPI(
    title="Content Quality Engine",
    description="Internal Content Quality Engine with Human-in-the-Loop",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check_endpoint() -> dict[str, str | bool]:
    """Health check endpoint.

    Returns:
        Health status including database connectivity
    """
    db_healthy = await health_check()
    return {
        "status": "healthy" if db_healthy else "degraded",
        "environment": settings.environment,
        "database": db_healthy,
    }


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        API information
    """
    return {
        "name": "Content Quality Engine API",
        "version": "0.1.0",
        "docs": "/docs" if not settings.is_production else "disabled",
    }


# Include API router
app.include_router(api_router, prefix="/api/v1")
