import sqlalchemy
import sqlalchemy.types
import sys

print("SQLAlchemy version:", sqlalchemy.__version__)
print("JSON in sqlalchemy?", 'JSON' in dir(sqlalchemy))
print("JSON in sqlalchemy.types?", 'JSON' in dir(sqlalchemy.types))

try:
    from sqlalchemy.types import JSON
    print("Import from sqlalchemy.types: SUCCESS")
except ImportError as e:
    print("Import from sqlalchemy.types: FAILED", e)

try:
    from sqlalchemy import JSON
    print("Import from sqlalchemy: SUCCESS")
except ImportError as e:
    print("Import from sqlalchemy: FAILED", e)
