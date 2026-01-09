# Hugging Face Deployment Guide

## Step 1: Create Free PostgreSQL Database on Neon

1. Go to https://neon.tech
2. Click "Sign Up" (free, no credit card required)
3. Create a new project:
   - Name: `todo-backend`
   - Region: Choose closest to you
4. Copy the connection string (looks like):
   ```
   postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```
5. Save this connection string - you'll need it for Hugging Face

**Neon Free Tier:**
- 0.5 GB storage
- 1 project
- Unlimited queries
- Perfect for this app!

---

## Step 2: Prepare Backend for Deployment

### 2.1: Create Dockerfile

Create `phase-02-fullstack-web/backend/Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir fastapi sqlmodel psycopg2-binary uvicorn python-dotenv pydantic-settings

# Copy application code
COPY . .

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```

### 2.2: Create requirements.txt (alternative to pyproject.toml)

Create `phase-02-fullstack-web/backend/requirements.txt`:

```
fastapi>=0.109.0
sqlmodel>=0.0.14
psycopg2-binary>=2.9.9
uvicorn[standard]>=0.27.0
python-dotenv>=1.0.0
pydantic-settings>=2.1.0
```

### 2.3: Create README for Hugging Face

Create `phase-02-fullstack-web/backend/README_HF.md`:

```markdown
---
title: Todo Backend API
emoji: ✅
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Todo Backend API

FastAPI backend for Todo application with PostgreSQL persistence.

## API Documentation

Once deployed, visit `/docs` for interactive API documentation.

## Endpoints

- `GET /` - Health check
- `GET /docs` - API documentation
- `GET /api/{user_id}/tasks` - Get all tasks
- `POST /api/{user_id}/tasks` - Create task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
```

---

## Step 3: Deploy to Hugging Face Spaces

### 3.1: Create Hugging Face Account

1. Go to https://huggingface.co
2. Click "Sign Up" (free)
3. Verify your email

### 3.2: Create a New Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in:
   - **Space name**: `todo-backend-api`
   - **License**: MIT
   - **Select SDK**: Docker
   - **Space hardware**: CPU basic (free)
   - **Visibility**: Public (or Private if you prefer)
4. Click "Create Space"

### 3.3: Add Environment Variables

In your Space settings:

1. Click "Settings" tab
2. Scroll to "Repository secrets"
3. Add these secrets:
   - **Name**: `DATABASE_URL`
   - **Value**: Your Neon PostgreSQL connection string
   ```
   postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```

4. Add CORS origins:
   - **Name**: `CORS_ORIGINS`
   - **Value**: `http://localhost:3000,https://your-frontend-url.vercel.app`

### 3.4: Upload Files to Hugging Face

**Option A: Using Git (Recommended)**

```bash
# Navigate to backend directory
cd phase-02-fullstack-web/backend

# Initialize git if not already done
git init

# Add Hugging Face remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/todo-backend-api

# Add files
git add Dockerfile requirements.txt main.py src/ README_HF.md

# Commit
git commit -m "Initial deployment"

# Push to Hugging Face
git push hf main
```

**Option B: Using Web Interface**

1. In your Space, click "Files and versions"
2. Click "Add file" → "Upload files"
3. Upload these files:
   - `Dockerfile`
   - `requirements.txt`
   - `main.py`
   - `src/` folder (all files)
   - `README_HF.md` (rename to `README.md`)
4. Click "Commit changes to main"

### 3.5: Wait for Build

- Hugging Face will automatically build your Docker container
- This takes 2-5 minutes
- You'll see build logs in the "Logs" tab
- Once complete, your API will be live!

---

## Step 4: Update Frontend to Use Deployed Backend

### 4.1: Get Your Hugging Face Space URL

Your API will be available at:
```
https://YOUR_USERNAME-todo-backend-api.hf.space
```

### 4.2: Update Frontend Environment

Update `phase-02-fullstack-web/frontend/.env.local`:

```bash
# For local development
NEXT_PUBLIC_API_URL=http://localhost:8001

# For production (uncomment when ready)
# NEXT_PUBLIC_API_URL=https://YOUR_USERNAME-todo-backend-api.hf.space
```

### 4.3: Test the Deployed API

Open in browser:
```
https://YOUR_USERNAME-todo-backend-api.hf.space/docs
```

You should see the Swagger UI with all your endpoints!

---

## Step 5: Update CORS in Backend

Make sure your backend allows requests from your frontend URL.

Update `phase-02-fullstack-web/backend/.env.example`:

```bash
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app,https://YOUR_USERNAME-todo-backend-api.hf.space
```

---

## Troubleshooting

### Issue 1: Space Not Building

**Solution**: Check build logs in "Logs" tab. Common issues:
- Missing Dockerfile
- Wrong port (must be 7860 for Hugging Face)
- Missing dependencies in requirements.txt

### Issue 2: Database Connection Error

**Solution**:
- Verify DATABASE_URL secret is set correctly
- Ensure connection string includes `?sslmode=require`
- Check Neon database is active

### Issue 3: CORS Errors

**Solution**:
- Add your frontend URL to CORS_ORIGINS
- Restart the Space after updating secrets

---

## Cost Breakdown (All FREE!)

| Service | Free Tier | What You Get |
|---------|-----------|--------------|
| **Hugging Face Spaces** | Free forever | CPU basic, 16GB RAM, 50GB storage |
| **Neon PostgreSQL** | Free forever | 0.5GB storage, unlimited queries |
| **Total Cost** | **$0/month** | Full production backend! |

---

## Alternative Free Options

If Hugging Face doesn't work for you:

### Option 1: Railway (Recommended)
- **Free Tier**: $5 credit/month (enough for small apps)
- **Pros**: Easier setup, built-in PostgreSQL
- **Cons**: Credit runs out after ~1 month of heavy use

### Option 2: Render
- **Free Tier**: Free forever (with limitations)
- **Pros**: Easy deployment, free PostgreSQL
- **Cons**: Spins down after 15 min inactivity (cold starts)

### Option 3: Fly.io
- **Free Tier**: 3 VMs free
- **Pros**: Fast, global edge network
- **Cons**: More complex setup

---

## Next Steps After Deployment

1. ✅ Test all API endpoints in Swagger UI
2. ✅ Update frontend to use deployed backend URL
3. ✅ Deploy frontend to Vercel (also free!)
4. ✅ Test full application end-to-end
5. ✅ Share your app with the world!

---

## Monitoring Your Deployment

### Hugging Face Spaces Dashboard
- View logs: Click "Logs" tab
- View metrics: Click "Settings" → "Analytics"
- Restart space: Click "Settings" → "Factory reboot"

### Neon Dashboard
- View database size: https://console.neon.tech
- Monitor queries: Check "Monitoring" tab
- View connection info: Click your project

---

## Security Best Practices

1. ✅ Use environment variables for secrets (never commit DATABASE_URL)
2. ✅ Enable HTTPS (automatic on Hugging Face)
3. ✅ Set specific CORS origins (not wildcard `*`)
4. ✅ Keep dependencies updated
5. ✅ Monitor logs for suspicious activity

---

## Support

- **Hugging Face Docs**: https://huggingface.co/docs/hub/spaces
- **Neon Docs**: https://neon.tech/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
