"""Blog and blog version table definitions."""

from sqlalchemy import (
    CheckConstraint,
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
import sqlalchemy
import uuid

from app.models.base import metadata

blogs = Table(
    "blogs",
    metadata,
    Column("id", String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("name", Text, nullable=False),
    Column("created_by", String(36), ForeignKey("users.id"), nullable=False),
    Column("created_at", Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
)

Index("idx_blogs_created_at", blogs.c.created_at)
Index("idx_blogs_created_by", blogs.c.created_by)

blog_versions = Table(
    "blog_versions",
    metadata,
    Column("id", String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("blog_id", String(36), ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False),
    Column("parent_version_id", String(36), ForeignKey("blog_versions.id"), nullable=True),
    Column("content", Text, nullable=False),
    Column(
        "content_hash",
        String(64),
        nullable=False,
    ),
    Column("source", String(20), nullable=False, server_default=text("'human_paste'")),
    Column("version_number", Integer, nullable=False),
    Column("created_by", String(36), ForeignKey("users.id"), nullable=False),
    Column("created_at", Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    UniqueConstraint("blog_id", "version_number", name="uq_blog_version"),
    CheckConstraint("source IN ('human_paste', 'ai_rewrite', 'human_edit')", name="chk_version_source"),
)

Index("idx_blog_versions_blog_id", blog_versions.c.blog_id)
Index("idx_blog_versions_parent", blog_versions.c.parent_version_id)
Index("idx_blog_versions_created_at", blog_versions.c.created_at)
Index("idx_blog_versions_created_by", blog_versions.c.created_by)
Index("idx_blog_versions_source", blog_versions.c.source)
