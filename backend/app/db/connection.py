"""Database connection management and transaction helpers."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.logging import get_logger
from app.db.engine import get_async_engine

logger = get_logger(__name__)


@asynccontextmanager
async def get_db_connection() -> AsyncGenerator[AsyncConnection, None]:
    """Get an async database connection with automatic transaction management.

    Yields:
        AsyncConnection: Database connection within a transaction

    Example:
        async with get_db_connection() as conn:
            result = await conn.execute(text("SELECT * FROM users"))
            rows = result.fetchall()

    Note:
        - Transaction is automatically committed on success
        - Transaction is automatically rolled back on exception
        - Connection is returned to pool after use
    """
    engine = get_async_engine()

    async with engine.begin() as conn:
        try:
            logger.debug("Database connection acquired")
            yield conn
            # Commit happens automatically on context exit if no exception
        except Exception as e:
            logger.error(f"Transaction error, rolling back: {e}")
            # Rollback happens automatically on exception
            raise


@asynccontextmanager
async def get_db_connection_no_transaction() -> AsyncGenerator[AsyncConnection, None]:
    """Get an async database connection WITHOUT automatic transaction.

    Use this for read-only operations or when you need manual transaction control.

    Yields:
        AsyncConnection: Database connection without transaction

    Example:
        async with get_db_connection_no_transaction() as conn:
            result = await conn.execute(text("SELECT * FROM users"))
            rows = result.fetchall()
    """
    engine = get_async_engine()

    async with engine.connect() as conn:
        try:
            logger.debug("Database connection acquired (no transaction)")
            yield conn
        finally:
            await conn.close()


async def execute_query(query: str, params: dict[str, Any] | None = None) -> Any:
    """Execute a raw SQL query and return results.

    Args:
        query: SQL query string
        params: Query parameters (optional)

    Returns:
        Query result

    Example:
        result = await execute_query(
            "SELECT * FROM users WHERE email = :email",
            {"email": "user@example.com"}
        )
    """
    async with get_db_connection() as conn:
        result = await conn.execute(text(query), params or {})
        return result


async def execute_insert(
    query: str, params: dict[str, Any] | None = None
) -> Any:
    """Execute an INSERT query and return the inserted row.

    Args:
        query: SQL INSERT query with RETURNING clause
        params: Query parameters (optional)

    Returns:
        Inserted row

    Example:
        row = await execute_insert(
            "INSERT INTO users (email, role) VALUES (:email, :role) RETURNING *",
            {"email": "user@example.com", "role": "writer"}
        )
    """
    async with get_db_connection() as conn:
        result = await conn.execute(text(query), params or {})
        return result.fetchone()


async def execute_update(
    query: str, params: dict[str, Any] | None = None
) -> int:
    """Execute an UPDATE query and return number of affected rows.

    Args:
        query: SQL UPDATE query
        params: Query parameters (optional)

    Returns:
        Number of rows affected

    Example:
        affected = await execute_update(
            "UPDATE evaluation_runs SET status = :status WHERE id = :id",
            {"status": "completed", "id": run_id}
        )
    """
    async with get_db_connection() as conn:
        result = await conn.execute(text(query), params or {})
        return result.rowcount


async def health_check() -> bool:
    """Check database connectivity.

    Returns:
        True if database is accessible, False otherwise
    """
    try:
        async with get_db_connection_no_transaction() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
