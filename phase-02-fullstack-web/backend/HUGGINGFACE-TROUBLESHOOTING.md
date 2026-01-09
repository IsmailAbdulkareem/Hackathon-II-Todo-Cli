# Hugging Face Space Troubleshooting Guide

## Your Space URL
https://huggingface.co/spaces/ismail233290/TODO_APP

## Current Status: ERROR (Missing Environment Secrets)

## How to Fix:

### Step 1: Add Environment Secrets

1. Go to: https://huggingface.co/spaces/ismail233290/TODO_APP
2. Click "Settings" tab
3. Scroll to "Repository secrets"
4. Add these two secrets:

**Secret 1:**
- Name: `DATABASE_URL`
- Value: `postgresql://neondb_owner:npg_No4mB3EezhxH@ep-still-rain-ahk6e0c4-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require`

**Secret 2:**
- Name: `CORS_ORIGINS`
- Value: `http://localhost:3000,https://ismail233290-todo-app.hf.space`

### Step 2: Reboot Space

1. In Settings, scroll to "Factory reboot"
2. Click "Reboot Space"
3. Wait 2-3 minutes

### Step 3: Check Build Logs

1. Go to your Space: https://huggingface.co/spaces/ismail233290/TODO_APP
2. Click "Logs" tab
3. Look for these success messages:
   - "Application startup complete"
   - "Uvicorn running on http://0.0.0.0:7860"

### Step 4: Test Your API

Once the build succeeds, test these URLs:

**Health Check:**
```
https://ismail233290-todo-app.hf.space/
```

**API Documentation:**
```
https://ismail233290-todo-app.hf.space/docs
```

**Get Tasks:**
```
https://ismail233290-todo-app.hf.space/api/user123/tasks
```

## Common Build Errors and Solutions

### Error: "DATABASE_URL not found"
**Solution**: Add DATABASE_URL secret in Settings → Repository secrets

### Error: "Can't connect to database"
**Solution**:
- Check DATABASE_URL format (must start with `postgresql://`)
- Ensure it includes `?sslmode=require` at the end
- Verify Neon database is active

### Error: "Port 7860 already in use"
**Solution**: This shouldn't happen on Hugging Face. Reboot the Space.

### Error: "Module not found"
**Solution**: Check requirements.txt includes all dependencies

## Expected Build Output

When successful, you should see:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7860 (Press CTRL+C to quit)
```

## After Successful Deployment

### Update Frontend

Edit `phase-02-fullstack-web/frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://ismail233290-todo.hf.space
```

Restart frontend:
```bash
cd phase-02-fullstack-web/frontend
npm run dev
```

### Test Full Integration

1. Open frontend: http://localhost:3000
2. Create a task
3. Verify it appears in the list
4. Check it persists after page refresh
5. Toggle completion
6. Delete task

## Success Checklist

- [ ] DATABASE_URL secret added
- [ ] CORS_ORIGINS secret added
- [ ] Space rebooted
- [ ] Build logs show "Application startup complete"
- [ ] Health check returns 200 OK
- [ ] API docs accessible at /docs
- [ ] Can create tasks via API
- [ ] Frontend updated with new API URL
- [ ] Frontend can communicate with deployed backend

## Your Deployed API URLs

**Base URL**: https://ismail233290-todo.hf.space

**Endpoints**:
- GET `/` - Health check
- GET `/docs` - API documentation
- GET `/api/{user_id}/tasks` - Get all tasks
- POST `/api/{user_id}/tasks` - Create task
- GET `/api/{user_id}/tasks/{id}` - Get single task
- PUT `/api/{user_id}/tasks/{id}` - Update task
- DELETE `/api/{user_id}/tasks/{id}` - Delete task
- PATCH `/api/{user_id}/tasks/{id}/complete` - Toggle completion

## Need Help?

If you're still having issues after adding secrets and rebooting:

1. Check the "Logs" tab for specific error messages
2. Verify both secrets are added correctly (no extra spaces)
3. Make sure DATABASE_URL starts with `postgresql://` (not `postgres://`)
4. Confirm Neon database is active at https://console.neon.tech
