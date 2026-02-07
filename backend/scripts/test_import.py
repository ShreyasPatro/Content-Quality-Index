import sys
import os
import traceback

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    print("Attempting to import app.models.scores...")
    import app.models.scores
    print("Import successful!")
except Exception:
    traceback.print_exc()
