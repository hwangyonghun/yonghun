import os
import sys

# -------------------------------------------------
# Base directory (absolute path, safer for Render)
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure base directory is in sys.path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# -------------------------------------------------
# DEBUG: Environment inspection (Render deployment)
# -------------------------------------------------
print("DEBUG: BASE_DIR =", BASE_DIR)

try:
    print("DEBUG: BASE_DIR files =", os.listdir(BASE_DIR))

    app_dir = os.path.join(BASE_DIR, "app")
    if os.path.exists(app_dir):
        print("DEBUG: 'app' directory found")
        print("DEBUG: app contents =", os.listdir(app_dir))
    else:
        print("DEBUG ERROR: 'app' directory NOT FOUND")
except Exception as e:
    print("DEBUG ERROR while listing files:", e)

# -------------------------------------------------
# Flask application factory import
# -------------------------------------------------
try:
    from app import create_app
except ImportError as e:
    print("CRITICAL IMPORT ERROR:", e)
    raise

# -------------------------------------------------
# Create Flask app (Gunicorn entry point)
# -------------------------------------------------
app = create_app()

# -------------------------------------------------
# Local development only
# -------------------------------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        debug=True
    )
