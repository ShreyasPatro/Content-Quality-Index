"""Database engine configuration for SQLAlchemy Core 2.0 async."""

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Global async engine instance
_async_engine: AsyncEngine | None = None


def get_async_engine() -> AsyncEngine:
    """Get or create the async database engine.

    Returns:
        AsyncEngine: Configured async database engine

    Note:
        Engine is created once and reused for the application lifetime.
        Call close_async_engine() on shutdown to dispose of connections.
    """
    global _async_engine

    if _async_engine is None:
        logger.info("Creating async database engine")
        _async_engine = create_async_engine(
            str(settings.database_url),
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,  # Verify connections before using
            echo=settings.is_development,  # Log SQL in development
            future=True,  # Use SQLAlchemy 2.0 style
        )
        logger.info(
            f"Engine created with pool_size={settings.database_pool_size}, "
            f"max_overflow={settings.database_max_overflow}"
        )

    return _async_engine


async def close_async_engine() -> None:
    """Close and dispose of the async database engine.

    Call this during application shutdown to cleanly close all connections.
    """
    global _async_engine

    if _async_engine is not None:
        logger.info("Closing async database engine")
        await _async_engine.dispose()
        _async_engine = None
        logger.info("Database engine closed")
