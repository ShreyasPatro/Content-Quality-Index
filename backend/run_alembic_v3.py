import sys
import traceback
from alembic.config import Config
from alembic import command

def main():
    try:
        print("Starting Alembic upgrade...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Upgrade successful!")
    except Exception:
        print("Upgrade failed! Writing traceback to traceback_v3.log")
        with open("traceback_v3.log", "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)

if __name__ == "__main__":
    main()
