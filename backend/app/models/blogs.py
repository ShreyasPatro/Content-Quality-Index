"""Blog and blog version table definitions."""

from sqlalchemy import (
    Column,
    Computed,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMPTZ, UUID

from app.models.base import metadata

blogs = Table(
    "blogs",
    metadata,
    Column("id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")),
    Column("title_slug", Text, nullable=False),
    Column("created_at", TIMESTAMPTZ, nullable=False, server_default=text("NOW()")),
    Column("project_id", UUID, nullable=True),
)

Index("idx_blogs_created_at", blogs.c.created_at)

blog_versions = Table(
    "blog_versions",
    metadata,
    Column("id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")),
    Column("blog_id", UUID, ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False),
    Column("parent_version_id", UUID, ForeignKey("blog_versions.id"), nullable=True),
    Column("source_rewrite_cycle_id", UUID, nullable=True),  # FK added later
    Column("content", JSONB, nullable=False),
    Column(
        "content_hash",
        String(64),
        Computed("encode(digest(content::text, 'sha256'), 'hex')"),
        nullable=False,
    ),
    Column("version_number", Integer, nullable=False),
    Column("created_by", UUID, ForeignKey("users.id"), nullable=False),
    Column("created_at", TIMESTAMPTZ, nullable=False, server_default=text("NOW()")),
    Column("change_reason", Text, nullable=True),
    UniqueConstraint("blog_id", "version_number", name="uq_blog_version"),
)

Index("idx_blog_versions_blog_id", blog_versions.c.blog_id)
Index("idx_blog_versions_parent", blog_versions.c.parent_version_id)
Index("idx_blog_versions_created_at", blog_versions.c.created_at)
Index("idx_blog_versions_created_by", blog_versions.c.created_by)
