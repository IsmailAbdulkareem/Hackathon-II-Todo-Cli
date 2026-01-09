# Hugging Face Deployment Script for Todo Backend API (Windows)
# Run this in PowerShell from the backend directory

Write-Host "🚀 Todo Backend API - Hugging Face Deployment" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the backend directory
if (-not (Test-Path "main.py")) {
    Write-Host "Error: Please run this script from the backend directory" -ForegroundColor Red
    Write-Host "cd phase-02-fullstack-web\backend"
    exit 1
}

Write-Host "Step 1: Checking required files..." -ForegroundColor Yellow
$requiredFiles = @("Dockerfile", "requirements.txt", "main.py", "src\core\config.py", "src\core\database.py", "src\models\task.py", "src\api\tasks.py")

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file" -ForegroundColor Green
    } else {
        Write-Host "✗ $file (missing)" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Step 2: Deployment checklist" -ForegroundColor Yellow
Write-Host ""
Write-Host "Before deploying to Hugging Face, make sure you have:"
Write-Host ""
Write-Host "1. ✓ Hugging Face account (https://huggingface.co/join)"
Write-Host "2. ✓ Neon PostgreSQL database (https://neon.tech)"
Write-Host "3. ✓ DATABASE_URL connection string"
Write-Host "4. ✓ Git installed and configured"
Write-Host ""

$response = Read-Host "Have you completed all the above? (y/n)"
if ($response -ne "y" -and $response -ne "Y") {
    Write-Host ""
    Write-Host "Please complete the checklist first:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "→ Create Neon account: https://neon.tech"
    Write-Host "→ Create Hugging Face account: https://huggingface.co/join"
    Write-Host "→ Get your DATABASE_URL from Neon dashboard"
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Step 3: Hugging Face Space setup" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:"
Write-Host ""
Write-Host "1. Go to https://huggingface.co/spaces"
Write-Host "2. Click 'Create new Space'"
Write-Host "3. Fill in:"
Write-Host "   - Space name: todo-backend-api"
Write-Host "   - License: MIT"
Write-Host "   - SDK: Docker"
Write-Host "   - Hardware: CPU basic (free)"
Write-Host ""
Write-Host "4. After creating the Space, add secrets:"
Write-Host "   - Go to Settings → Repository secrets"
Write-Host "   - Add DATABASE_URL (your Neon connection string)"
Write-Host "   - Add CORS_ORIGINS (http://localhost:3000)"
Write-Host ""

$response = Read-Host "Have you created your Hugging Face Space? (y/n)"
if ($response -ne "y" -and $response -ne "Y") {
    Write-Host ""
    Write-Host "Create your Space first, then run this script again."
    exit 1
}

Write-Host ""
Write-Host "Step 4: Enter your Hugging Face username" -ForegroundColor Yellow
$HF_USERNAME = Read-Host "Hugging Face username"

if ([string]::IsNullOrWhiteSpace($HF_USERNAME)) {
    Write-Host "Error: Username cannot be empty" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 5: Preparing files for deployment..." -ForegroundColor Yellow

# Copy README_HF.md to README.md for Hugging Face
if (Test-Path "README_HF.md") {
    Copy-Item "README_HF.md" "README.md" -Force
    Write-Host "✓ README.md prepared" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 6: Git setup" -ForegroundColor Yellow

# Initialize git if not already done
if (-not (Test-Path ".git")) {
    git init
    Write-Host "✓ Git initialized" -ForegroundColor Green
}

# Add Hugging Face remote
$HF_SPACE_URL = "https://huggingface.co/spaces/$HF_USERNAME/todo-backend-api"
$remotes = git remote
if ($remotes -contains "hf") {
    git remote remove hf
}
git remote add hf $HF_SPACE_URL
Write-Host "✓ Hugging Face remote added" -ForegroundColor Green

Write-Host ""
Write-Host "Step 7: Committing files..." -ForegroundColor Yellow

# Add files
git add Dockerfile requirements.txt main.py src/ README.md .dockerignore

# Commit
git commit -m "Deploy Todo Backend API to Hugging Face Spaces"

Write-Host ""
Write-Host "Step 8: Pushing to Hugging Face..." -ForegroundColor Yellow
Write-Host ""
Write-Host "You will be prompted for your Hugging Face credentials:"
Write-Host "- Username: $HF_USERNAME"
Write-Host "- Password: Use your Hugging Face Access Token"
Write-Host "  (Get it from: https://huggingface.co/settings/tokens)"
Write-Host ""

$response = Read-Host "Ready to push? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    git push hf main

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ Deployment successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your API will be available at:"
        Write-Host "https://$HF_USERNAME-todo-backend-api.hf.space" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "API Documentation:"
        Write-Host "https://$HF_USERNAME-todo-backend-api.hf.space/docs" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Next steps:"
        Write-Host "1. Wait 2-5 minutes for the build to complete"
        Write-Host "2. Check build logs in your Space's 'Logs' tab"
        Write-Host "3. Test the API at the URL above"
        Write-Host "4. Update your frontend .env.local with the new API URL"
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "✗ Push failed" -ForegroundColor Red
        Write-Host ""
        Write-Host "Common issues:"
        Write-Host "- Wrong credentials (use Access Token, not password)"
        Write-Host "- Space doesn't exist (create it first)"
        Write-Host "- Network issues (check your connection)"
        Write-Host ""
    }
}

Write-Host ""
Write-Host "Deployment script completed!"
