# Root-level app.py wrapper for Render deployment
# This file imports the Flask app from the backend directory
# so gunicorn can find it when running from the root directory

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the Flask app from the backend
from backend.app import app

# This allows gunicorn to find the app with: gunicorn app:app
if __name__ == '__main__':
    app.run()
