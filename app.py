# Root-level app.py wrapper for Render deployment
# This file imports the Flask app from the backend directory

import sys
import os
import importlib.util

# Get the absolute path to the backend directory
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')

# Add the backend directory to sys.path FIRST
sys.path.insert(0, backend_path)

# Change working directory to backend for relative imports within backend
os.chdir(backend_path)

# Load backend/app.py using importlib to avoid circular import
spec = importlib.util.spec_from_file_location("backend_app", os.path.join(backend_path, "app.py"))
backend_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend_module)

# Get the Flask app from the loaded module
app = backend_module.app

# This allows gunicorn to find the app with: gunicorn app:app
if __name__ == '__main__':
    app.run()
