import sys
import os
import uuid

# Add backend directory to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, insert, text
from app.models.users import users
from app.core.security import get_password_hash

def seed():
    print("Seeding user...")
    engine = create_engine('sqlite:///seo_aeo.db')
    
    with engine.connect() as conn:
        # Check if user exists
        result = conn.execute(text("SELECT id FROM users WHERE email = 'admin@example.com'")).fetchone()
        if result:
            print("User admin@example.com already exists.")
            return

        stmt = insert(users).values(
            email='admin@example.com',
            role='admin',
            is_human=True,
            hashed_password=get_password_hash('password')
        )
        conn.execute(stmt)
        conn.commit()
        print("User admin@example.com created with password 'password'.")

if __name__ == '__main__':
    seed()
