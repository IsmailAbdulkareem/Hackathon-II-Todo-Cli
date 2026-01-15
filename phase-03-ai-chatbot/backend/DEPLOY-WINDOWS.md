# Quick Deployment Guide for Windows

## Prerequisites Check
- [ ] Neon PostgreSQL database created
- [ ] DATABASE_URL copied
- [ ] Hugging Face account created
- [ ] Hugging Face Space created (todo-backend-api)
- [ ] Environment secrets added to Space
- [ ] Git installed on your computer

## Deployment Steps

### Option 1: Using PowerShell Script (Easiest)

1. Open PowerShell in the backend directory:
   ```powershell
   cd "D:\Projects\spec-driven-development-hacathon\Hackathon II - Todo Spec-Driven Development\phase-02-fullstack-web\backend"
   ```

2. Run the deployment script:
   ```powershell
   .\deploy-hf.ps1
   ```

3. Follow the prompts:
   - Enter your Hugging Face username
   - Enter your Hugging Face Access Token (get from https://huggingface.co/settings/tokens)

4. Wait for deployment to complete (2-5 minutes)

### Option 2: Manual Deployment

1. Navigate to backend directory:
   ```powershell
   cd "D:\Projects\spec-driven-development-hacathon\Hackathon II - Todo Spec-Driven Development\phase-02-fullstack-web\backend"
   ```

2. Copy README for Hugging Face:
   ```powershell
   Copy-Item README_HF.md README.md
   ```

3. Initialize Git (if not already done):
   ```powershell
   git init
   ```

4. Add Hugging Face remote (replace YOUR_USERNAME):
   ```powershell
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/todo-backend-api
   ```

5. Add and commit files:
   ```powershell
   git add Dockerfile requirements.txt main.py src/ README.md .dockerignore
   git commit -m "Deploy Todo Backend API to Hugging Face Spaces"
   ```

6. Push to Hugging Face:
   ```powershell
   git push hf main
   ```

   When prompted:
   - Username: Your Hugging Face username
   - Password: Your Hugging Face Access Token (NOT your password!)

## After Deployment

### 1. Check Build Status

1. Go to your Space: https://huggingface.co/spaces/YOUR_USERNAME/todo-backend-api
2. Click "Logs" tab
3. Wait for build to complete (2-5 minutes)
4. Look for: "Application startup complete"

### 2. Test Your API

Once deployed, your API will be at:
```
https://YOUR_USERNAME-todo-backend-api.hf.space
```

Test it:
```powershell
# Health check
curl https://YOUR_USERNAME-todo-backend-api.hf.space/

# API documentation
# Open in browser: https://YOUR_USERNAME-todo-backend-api.hf.space/docs

# Get tasks
curl https://YOUR_USERNAME-todo-backend-api.hf.space/api/user123/tasks
```

### 3. Update Frontend

Update `phase-02-fullstack-web/frontend/.env.local`:

```bash
# Replace with your deployed API URL
NEXT_PUBLIC_API_URL=https://YOUR_USERNAME-todo-backend-api.hf.space
```

Restart your frontend:
```powershell
cd ..\frontend
npm run dev
```

## Troubleshooting

### Build Failed

**Check Logs**: Go to Space → Logs tab

**Common Issues**:
- Missing environment secrets (DATABASE_URL, CORS_ORIGINS)
- Wrong DATABASE_URL format (must include ?sslmode=require)
- Port mismatch (must be 7860 for Hugging Face)

**Solution**: Fix the issue, then push again:
```powershell
git add .
git commit -m "Fix deployment issue"
git push hf main
```

### Database Connection Error

**Check**:
- DATABASE_URL secret is set correctly in Space settings
- Neon database is active (check https://console.neon.tech)
- Connection string includes `?sslmode=require`

### CORS Errors

**Solution**:
- Add your frontend URL to CORS_ORIGINS secret
- Format: `http://localhost:3000,https://your-frontend.vercel.app`
- Restart Space: Settings → Factory reboot

### Authentication Failed (git push)

**Solution**:
- Use Access Token, NOT your password
- Get token: https://huggingface.co/settings/tokens
- Create new token with "write" access
- Use token as password when prompted

## Success Checklist

- [ ] Backend deployed to Hugging Face
- [ ] Build completed successfully
- [ ] Health check returns 200 OK
- [ ] API documentation accessible at /docs
- [ ] Can create tasks via API
- [ ] Frontend updated with new API URL
- [ ] Frontend can communicate with deployed backend
- [ ] Tasks persist in Neon database

## Cost Summary

| Service | Cost | What You Get |
|---------|------|--------------|
| Hugging Face Spaces | **FREE** | CPU basic, 16GB RAM, 50GB storage |
| Neon PostgreSQL | **FREE** | 0.5GB storage, unlimited queries |
| **Total** | **$0/month** | Full production backend! |

## Next Steps

1. ✅ Test all API endpoints in Swagger UI
2. ✅ Verify frontend works with deployed backend
3. ✅ Deploy frontend to Vercel (also free!)
4. ✅ Share your app with the world!

## Support

- **Hugging Face Docs**: https://huggingface.co/docs/hub/spaces
- **Neon Docs**: https://neon.tech/docs
- **Deployment Guide**: See HUGGINGFACE-DEPLOYMENT.md
