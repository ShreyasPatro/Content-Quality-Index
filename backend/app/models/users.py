"""User table definitions."""

from sqlalchemy import Boolean, CheckConstraint, Column, Index, String, Table, text
from sqlalchemy.dialects.postgresql import TIMESTAMPTZ, UUID

from app.models.base import metadata

users = Table(
    "users",
    metadata,
    Column("id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")),
    Column("email", String(255), nullable=False, unique=True),
    Column(
        "role",
        String(50),
        nullable=False,
        server_default=text("'writer'"),
    ),
    Column("is_human", Boolean, nullable=False, server_default=text("false")),
    Column("created_at", TIMESTAMPTZ, nullable=False, server_default=text("NOW()")),
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
Index("idx_users_is_human", users.c.is_human, postgresql_where=users.c.is_human == True)
