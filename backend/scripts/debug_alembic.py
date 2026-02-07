import subprocess
import sys

def run_alembic():
    try:
        # Run alembic upgrade head
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=r"c:\Users\Shrey\OneDrive\Desktop\SEO_AEO_CQI\backend",
            capture_output=True,
            text=True
        )
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        if result.returncode != 0:
            print("Migration failed with code", result.returncode)
    except Exception as e:
        print(f"Error running alembic: {e}")

if __name__ == "__main__":
    run_alembic()
