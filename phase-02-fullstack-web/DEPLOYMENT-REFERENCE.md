# Quick Reference: Your Deployed Backend

## 🌐 Your API URLs

**Base URL**: https://ismail233290-todo-app.hf.space

**Health Check**: https://ismail233290-todo-app.hf.space/
**API Docs**: https://ismail233290-todo-app.hf.space/docs

## 📋 Environment Secrets (Add in Settings)

### Secret 1: DATABASE_URL
```
postgresql://neondb_owner:npg_No4mB3EezhxH@ep-still-rain-ahk6e0c4-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### Secret 2: CORS_ORIGINS
```
http://localhost:3000,https://ismail233290-todo-app.hf.space,https://hackathon-ii-todo-cli.vercel.app
```

## 🧪 Test Commands (After Deployment)

### Health Check
```bash
curl https://ismail233290-todo-app.hf.space/
```

### Get All Tasks
```bash
curl https://ismail233290-todo-app.hf.space/api/user123/tasks
```

### Create a Task
```bash
curl -X POST https://ismail233290-todo-app.hf.space/api/user123/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "description": "Testing deployed API"}'
```

## 🔄 Update Frontend

Edit: `phase-02-fullstack-web/frontend/.env.local`

```bash
NEXT_PUBLIC_API_URL=https://ismail233290-todo-app.hf.space
```

Then restart frontend:
```bash
cd phase-02-fullstack-web/frontend
npm run dev
```

## ✅ Success Indicators

When deployment is successful, you should see:

1. **In Hugging Face Logs tab**:
   - "Application startup complete"
   - "Uvicorn running on http://0.0.0.0:7860"

2. **Health Check Response**:
   ```json
   {
     "status": "healthy",
     "message": "Todo Backend API is running",
     "docs": "/docs"
   }
   ```

3. **API Docs**: Interactive Swagger UI at /docs

## 💰 Cost Summary

| Service | Cost |
|---------|------|
| Hugging Face Spaces | **FREE** |
| Neon PostgreSQL | **FREE** |
| **Total** | **$0/month** |

## 📞 Support

- **Space URL**: https://huggingface.co/spaces/ismail233290/TODO_APP
- **Neon Console**: https://console.neon.tech
- **Troubleshooting**: See HUGGINGFACE-TROUBLESHOOTING.md
