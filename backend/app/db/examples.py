"""Example usage of SQLAlchemy Core database operations.

This file demonstrates how to use the database layer for common operations.
"""

from uuid import UUID

from sqlalchemy import text

from app.db import DBConnection, get_db


# Example 1: Using get_db dependency in FastAPI endpoint
async def create_blog_example(title_slug: str, db: DBConnection) -> dict:
    """Example: Create a blog using FastAPI dependency injection.

    Args:
        title_slug: Blog title slug
        db: Database connection from Depends(get_db)

    Returns:
        Created blog data
    """
    result = await db.execute(
        text(
            """
            INSERT INTO blogs (title_slug, created_at)
            VALUES (:slug, NOW())
            RETURNING id, title_slug, created_at
            """
        ),
        {"slug": title_slug},
    )
    row = result.fetchone()
    return {"id": str(row.id), "title_slug": row.title_slug, "created_at": row.created_at}


# Example 2: Using connection context manager directly
async def get_blog_by_id_example(blog_id: UUID) -> dict | None:
    """Example: Fetch a blog using connection context manager.

    Args:
        blog_id: Blog UUID

    Returns:
        Blog data or None if not found
    """
    from app.db import get_db_connection

    async with get_db_connection() as conn:
        result = await conn.execute(
            text("SELECT * FROM blogs WHERE id = :id"), {"id": blog_id}
        )
        row = result.fetchone()
        if row:
            return {"id": str(row.id), "title_slug": row.title_slug}
        return None


# Example 3: Using helper functions
async def update_evaluation_status_example(run_id: UUID, status: str) -> int:
    """Example: Update evaluation run status using helper function.

    Args:
        run_id: Evaluation run UUID
        status: New status

    Returns:
        Number of rows affected
    """
    from app.db import execute_update

    affected = await execute_update(
        """
        UPDATE evaluation_runs
        SET status = :status, completed_at = NOW()
        WHERE id = :id
        """,
        {"status": status, "id": run_id},
    )
    return affected


# Example 4: Complex query with joins
async def get_blog_with_latest_version_example(blog_id: UUID) -> dict | None:
    """Example: Fetch blog with its latest version.

    Args:
        blog_id: Blog UUID

    Returns:
        Blog with latest version data
    """
    from app.db import get_db_connection

    async with get_db_connection() as conn:
        result = await conn.execute(
            text(
                """
                SELECT
                    b.id as blog_id,
                    b.title_slug,
                    v.id as version_id,
                    v.version_number,
                    v.content,
                    v.created_at
                FROM blogs b
                LEFT JOIN LATERAL (
                    SELECT * FROM blog_versions
                    WHERE blog_id = b.id
                    ORDER BY version_number DESC
                    LIMIT 1
                ) v ON true
                WHERE b.id = :blog_id
                """
            ),
            {"blog_id": blog_id},
        )
        row = result.fetchone()
        if row:
            return {
                "blog_id": str(row.blog_id),
                "title_slug": row.title_slug,
                "latest_version": {
                    "id": str(row.version_id) if row.version_id else None,
                    "version_number": row.version_number,
                    "content": row.content,
                },
            }
        return None


# Example 5: Batch insert
async def insert_detector_scores_example(run_id: UUID, scores: list[dict]) -> None:
    """Example: Batch insert AI detector scores.

    Args:
        run_id: Evaluation run UUID
        scores: List of score dictionaries
    """
    from app.db import get_db_connection

    async with get_db_connection() as conn:
        for score in scores:
            await conn.execute(
                text(
                    """
                    INSERT INTO ai_detector_scores (run_id, provider, score, details)
                    VALUES (:run_id, :provider, :score, :details)
                    """
                ),
                {
                    "run_id": run_id,
                    "provider": score["provider"],
                    "score": score["score"],
                    "details": score["details"],
                },
            )


# Example 6: Read-only query (no transaction)
async def count_blogs_example() -> int:
    """Example: Count total blogs using read-only connection.

    Returns:
        Total number of blogs
    """
    from app.db import get_db_connection_no_transaction

    async with get_db_connection_no_transaction() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM blogs"))
        row = result.fetchone()
        return row[0]
