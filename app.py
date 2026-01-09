# Root-level app.py wrapper for Render deployment
# This file imports the Flask app from the backend directory
# so gunicorn can find it when running from the root directory

import sys
import os

# Get the absolute path to the backend directory
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')

# Add the backend directory to sys.path so all imports work correctly
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Change the current working directory to backend for relative path imports
os.chdir(backend_path)

# Now import the Flask app
# We need to import after changing the path and cwd
from app import app as flask_app

# Export as 'app' for gunicorn
app = flask_app

# This allows gunicorn to find the app with: gunicorn app:app
if __name__ == '__main__':
    app.run()
