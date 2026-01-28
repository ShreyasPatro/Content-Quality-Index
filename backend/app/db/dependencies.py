"""FastAPI dependency for database connections."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncConnection

from app.db.connection import get_db_connection


async def get_db() -> AsyncGenerator[AsyncConnection, None]:
    """FastAPI dependency for database connections.

    Provides an async database connection with automatic transaction management.

    Yields:
        AsyncConnection: Database connection within a transaction

    Example:
        @app.post("/blogs")
        async def create_blog(
            data: BlogCreate,
            db: AsyncConnection = Depends(get_db)
        ):
            result = await db.execute(
                text("INSERT INTO blogs (title_slug) VALUES (:slug) RETURNING *"),
                {"slug": data.title_slug}
            )
            return result.fetchone()

    Note:
        - Transaction is committed automatically on successful response
        - Transaction is rolled back automatically on exception
        - Use this for all endpoints that modify data
    """
    async with get_db_connection() as conn:
        yield conn


# Type alias for dependency injection
DBConnection = AsyncConnection
