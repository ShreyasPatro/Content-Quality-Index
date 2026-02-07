import asyncio
import os
import sys

# Add backend directory to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import asyncpg

async def create_db():
    # Default credentials usually used in dev
    # We try to read from .env if possible, but for initial setup we might need fallback
    
    # Read .env file manually to avoid pydantic validation errors if DB doesn't exist
    env_vars = {}
    try:
        with open(os.path.join(os.path.dirname(__file__), '../.env'), 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    env_vars[key] = val
    except Exception:
        pass

    db_url = env_vars.get('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/seo_aeo_db')
    
    # Parse standard URL: postgresql+asyncpg://user:pass@host:port/dbname
    try:
        # Very basic parsing
        prefix, rest = db_url.split('://', 1)
        creds, loc = rest.split('@', 1)
        user, password = creds.split(':', 1)
        host_port, dbname = loc.split('/', 1)
        host = host_port.split(':')[0]
    except Exception as e:
        print(f"Error parsing connection string: {e}")
        return

    print(f"Attempting to connect to PostgreSQL as user '{user}' to create database '{dbname}'...")

    try:
        # Connect to 'postgres' system database
        sys_conn = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            database='postgres'
        )
        
        # Check existence
        exists = await sys_conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", 
            dbname
        )
        
        if not exists:
            await sys_conn.execute(f'CREATE DATABASE "{dbname}"')
            print(f"DATABASECREATED: Database '{dbname}' created successfully!")
        else:
            print(f"DATABASEEXISTS: Database '{dbname}' already exists.")
            
        await sys_conn.close()
        
    except Exception as e:
        print(f"ERROR: Failed to create database: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL service is running.")
        print("2. Check if your password in 'backend/.env' matches what you set during installation.")
        print("   Current value in .env uses password: " + ('*' * len(password)))
        print("3. You can manually create the database using pgAdmin: CREATE DATABASE seo_aeo_db;")

if __name__ == "__main__":
    try:
        asyncio.run(create_db())
    except ImportError:
        print("need asyncpg installed: pip install asyncpg")
