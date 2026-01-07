# Deployment Guide

## 1. Backend Deployment (Render)

This project is configured for easy deployment on [Render](https://render.com/).

### Option A: Blueprints (Recommended)
1. Push your code to GitHub.
2. Go to Render Dashboard -> **Blueprints**.
3. Click **New Blueprint Instance**.
4. Connect the repository `study-pilot-AI`.
5. Render will automatically detect `render.yaml` and configure the service.
6. Click **Apply**.

### Option B: Manual Setup
1. Create a new **Web Service**.
2. Connect your GitHub repository.
3. Settings:
   - **Name**: `study-pilot-backend`
   - **Root Directory**: `.` (leave empty)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --chdir backend app:app`

## 2. Frontend Deployment (Vercel)

1. Push your code to GitHub.
2. Go to [Vercel](https://vercel.com/) -> **Add New...** -> **Project**.
3. Import `study-pilot-AI`.
4. **Project Settings**:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend` (Click Edit and select the `frontend` folder).
5. **Environment Variables**:
   - If your backend is deployed, you'll need to update the frontend to point to it.
   - Creating a `.env.production` file in `frontend` or setting Environment Variables in Vercel:
     - `VITE_API_BASE_URL`: `https://your-render-backend-url.onrender.com`
6. Click **Deploy**.

## Notes
- The `frontend/vercel.json` ensures that page refreshing works correctly (SPA routing).
- `requirements.txt` is updated to include `gunicorn` for the production server.
