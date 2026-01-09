# 🚀 Study Pilot AI - Deployment Guide

This guide provides step-by-step instructions for deploying Study Pilot AI to **Vercel** (Frontend) and **Render** (Backend).

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Backend Deployment (Render)](#backend-deployment-render)
   - [Option A: Blueprint Deployment (Recommended)](#option-a-blueprint-deployment-recommended)
   - [Option B: Manual Deployment](#option-b-manual-deployment)
4. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
5. [Environment Variables](#environment-variables)
6. [Post-Deployment Configuration](#post-deployment-configuration)
7. [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STUDY PILOT AI ARCHITECTURE                     │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────────────────┐
                    │           USER BROWSER           │
                    │     (Chrome, Firefox, Safari)    │
                    └──────────────────┬───────────────┘
                                       │
                                       │ HTTPS
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                              VERCEL (Frontend)                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                     React + Vite Application                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │  │
│  │  │   Static     │  │   SPA        │  │   Environment Config     │  │  │
│  │  │   Assets     │  │   Router     │  │   VITE_API_BASE_URL      │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                     URL: https://your-app.vercel.app                      │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │
                                   │ REST API Calls (HTTPS)
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                              RENDER (Backend)                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    Flask + Gunicorn Application                    │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │  │
│  │  │  REST API    │  │   RAG        │  │   Bayesian Knowledge     │  │  │
│  │  │  Endpoints   │  │   Pipeline   │  │   Tracing (BKT)          │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │  │
│  │  │  SQLite      │  │  FAISS       │  │   Quiz & Roadmap         │  │  │
│  │  │  Database    │  │  Vector DB   │  │   Generators             │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                  URL: https://study-pilot-backend.onrender.com            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## ✅ Prerequisites

Before deploying, ensure you have:

- [ ] **GitHub Account** - Your code must be pushed to a GitHub repository
- [ ] **Render Account** - Sign up at [render.com](https://render.com)
- [ ] **Vercel Account** - Sign up at [vercel.com](https://vercel.com)
- [ ] **(Optional) OpenAI API Key** - For enhanced AI responses

---

## 🔧 Backend Deployment (Render)

### Option A: Blueprint Deployment (Recommended)

The **Blueprint** method uses the `render.yaml` file to automatically configure your service.

#### Step 1: Push Code to GitHub

```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

#### Step 2: Create Blueprint in Render

1. **Login** to [Render Dashboard](https://dashboard.render.com)

2. Click **"New"** → **"Blueprint"**

   ![New Blueprint](https://render.com/docs/images/blueprint-new.png)

3. **Connect your GitHub repository:**
   - Select `study-pilot-AI` repository
   - Click **"Connect"**

4. **Render will detect `render.yaml`** and show the configured services:
   ```
   ┌─────────────────────────────────────────┐
   │  🔍 Blueprint Preview                   │
   ├─────────────────────────────────────────┤
   │  Service: study-pilot-backend           │
   │  Type: Web Service                      │
   │  Runtime: Python 3.10                   │
   │  Plan: Free                             │
   └─────────────────────────────────────────┘
   ```

5. Click **"Apply"** to deploy

#### Step 3: Wait for Deployment

- Build typically takes **5-10 minutes** (initial deployment)
- Render will:
  - Install Python dependencies
  - Start the Gunicorn server
  - Run health checks

#### Step 4: Verify Deployment

Once deployed, test the health endpoint:

```bash
curl https://study-pilot-backend.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "retriever_size": 0,
  "courses_available": 4
}
```

---

### Option B: Manual Deployment

Use this method if you need more control over the configuration.

#### Step 1: Create New Web Service

1. **Login** to [Render Dashboard](https://dashboard.render.com)

2. Click **"New"** → **"Web Service"**

3. **Connect your repository:**
   - Select `study-pilot-AI`
   - Click **"Connect"**

#### Step 2: Configure Service Settings

Fill in the following settings:

| Setting | Value |
|---------|-------|
| **Name** | `study-pilot-backend` |
| **Region** | Oregon (US West) or your preferred region |
| **Branch** | `main` |
| **Root Directory** | *(leave empty)* |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --chdir backend --workers 2 --threads 4 --bind 0.0.0.0:$PORT app:app` |
| **Plan** | Free (or higher for production) |

#### Step 3: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.10.0` |
| `FLASK_ENV` | `production` |
| `OPENAI_API_KEY` | *(your key, optional)* |

#### Step 4: Deploy

Click **"Create Web Service"** and wait for the build to complete.

---

### 📊 Render Dashboard Overview

After deployment, your Render dashboard will show:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RENDER DASHBOARD                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─ study-pilot-backend ──────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │  Status:     🟢 Live                                                │ │
│  │  URL:        https://study-pilot-backend.onrender.com               │ │
│  │  Region:     Oregon (US West)                                       │ │
│  │  Plan:       Free                                                   │ │
│  │  Last Deploy: 2 minutes ago                                         │ │
│  │                                                                     │ │
│  │  ┌─────────────────────────────────────────────────────────────┐   │ │
│  │  │  📈 Metrics                                                 │   │ │
│  │  │  Memory: 256MB / 512MB                                      │   │ │
│  │  │  CPU: 0.1 / 0.5                                             │   │ │
│  │  │  Requests: 150/hour                                         │   │ │
│  │  └─────────────────────────────────────────────────────────────┘   │ │
│  │                                                                     │ │
│  │  [Logs]  [Shell]  [Environment]  [Settings]                        │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Frontend Deployment (Vercel)

### Step 1: Push Code to GitHub

Ensure your latest code is pushed:

```bash
git add .
git commit -m "Add Vercel deployment configuration"
git push origin main
```

### Step 2: Import Project in Vercel

1. **Login** to [Vercel Dashboard](https://vercel.com/dashboard)

2. Click **"Add New..."** → **"Project"**

3. **Import your GitHub repository:**
   - Find and select `study-pilot-AI`
   - Click **"Import"**

### Step 3: Configure Project Settings

Vercel will auto-detect the configuration from `vercel.json`, but verify:

| Setting | Value |
|---------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` (Click "Edit" to change) |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

### Step 4: Add Environment Variables

Click **"Environment Variables"** and add:

| Name | Value | Environment |
|------|-------|-------------|
| `VITE_API_BASE_URL` | `https://study-pilot-backend.onrender.com` | Production |

> ⚠️ **Important:** Replace with your actual Render backend URL!

### Step 5: Deploy

Click **"Deploy"** and wait for the build to complete (usually 1-2 minutes).

---

## 🔐 Environment Variables

### Backend (Render)

| Variable | Required | Description |
|----------|----------|-------------|
| `PYTHON_VERSION` | ✅ | Python version (recommended: `3.10.0`) |
| `FLASK_ENV` | ✅ | Environment: `production` or `development` |
| `OPENAI_API_KEY` | ❌ | OpenAI API key for enhanced AI features |

### Frontend (Vercel)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_BASE_URL` | ✅ | Full URL to your Render backend |

---

## ⚙️ Post-Deployment Configuration

### Step 1: Update CORS Settings

After deploying both services, update the CORS configuration in `backend/app.py`:

```python
CORS(app, origins=[
    "http://localhost:5173",
    "http://localhost:3000",
    "https://your-app.vercel.app",  # Add your Vercel URL
])
```

### Step 2: Update Frontend Environment

Update `frontend/.env.production`:

```env
VITE_API_BASE_URL=https://study-pilot-backend.onrender.com
```

### Step 3: Redeploy

Commit and push changes to trigger a new deployment:

```bash
git add .
git commit -m "Update CORS and environment configuration"
git push origin main
```

---

## 🔍 Troubleshooting

### Common Issues & Solutions

#### ❌ Build Failed on Render

**Symptom:** `ERROR: Could not find a version that satisfies the requirement`

**Solution:** Update package versions in `requirements.txt` to use flexible constraints:
```
faiss-cpu>=1.9.0  # Instead of faiss-cpu==1.7.4
```

#### ❌ CORS Error in Browser

**Symptom:** `Access to fetch blocked by CORS policy`

**Solution:** Add your Vercel URL to CORS origins in `backend/app.py`

#### ❌ API Connection Failed

**Symptom:** Frontend can't reach backend

**Solution:** 
1. Verify `VITE_API_BASE_URL` is set correctly in Vercel
2. Check backend is running: `curl https://your-backend.onrender.com/api/health`

#### ❌ Render Service Sleeps (Free Tier)

**Symptom:** First request takes 30+ seconds

**This is normal behavior for free tier.** Solutions:
1. Upgrade to paid plan
2. Use a service like [UptimeRobot](https://uptimerobot.com) to ping your service every 14 minutes

---

## 📁 Deployment Files Reference

```
study-pilot-AI/
├── render.yaml           # Render Blueprint configuration
├── vercel.json           # Vercel configuration (root level)
├── Procfile              # Heroku-style process file
├── runtime.txt           # Python version specification
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
│
├── frontend/
│   ├── vercel.json       # Frontend-specific Vercel config
│   └── .env.production   # Production environment variables
│
└── backend/
    └── app.py            # Flask application
```

---

## 🎉 Deployment Checklist

Use this checklist to verify your deployment:

- [ ] Backend deployed on Render
- [ ] Health check returns `{"status": "healthy"}`
- [ ] Frontend deployed on Vercel
- [ ] Frontend can communicate with backend
- [ ] User registration/login works
- [ ] Courses load correctly
- [ ] Quiz generation works
- [ ] AI query responses work

---

## 📞 Support

If you encounter issues:

1. **Check Render Logs:** Dashboard → Your Service → Logs
2. **Check Vercel Logs:** Dashboard → Your Project → Functions/Build Logs
3. **Review this guide's troubleshooting section**

---

*Last Updated: January 2026*
