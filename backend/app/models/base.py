"""Central metadata registry for SQLAlchemy Core table definitions."""

from sqlalchemy import MetaData

# Central metadata object for all table definitions
# This is used by Alembic for migrations and by the application for queries
metadata = MetaData()
