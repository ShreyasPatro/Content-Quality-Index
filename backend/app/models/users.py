"""User table definitions."""

from sqlalchemy import Boolean, CheckConstraint, Column, Index, String, Table, text
import uuid

from app.models.base import metadata

users = Table(
    "users",
    metadata,
    Column("id", String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("email", String(255), nullable=False, unique=True),
    Column(
        "role",
        String(50),
        nullable=False,
        server_default=text("'writer'"),
    ),
    Column("is_human", Boolean, nullable=False, server_default=text("false")),
    Column("hashed_password", String(255), nullable=False, server_default=text("''")),
    Column("created_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    # Prevent service accounts from being marked as human
    CheckConstraint(
        "role != 'system' OR is_human = false",
        name="chk_system_not_human",
    ),
    CheckConstraint(
        "role IN ('writer', 'reviewer', 'admin', 'system')",
        name="chk_users_role",
    ),
)

# Indexes
Index("idx_users_role", users.c.role)
Index("idx_users_is_human", users.c.is_human, sqlite_where=users.c.is_human == True)
