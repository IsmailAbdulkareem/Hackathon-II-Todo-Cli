#!/bin/bash

# Hugging Face Deployment Script for Todo Backend API
# This script helps you deploy your FastAPI backend to Hugging Face Spaces

set -e

echo "🚀 Todo Backend API - Hugging Face Deployment"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}Error: Please run this script from the backend directory${NC}"
    echo "cd phase-02-fullstack-web/backend"
    exit 1
fi

echo -e "${YELLOW}Step 1: Checking required files...${NC}"
required_files=("Dockerfile" "requirements.txt" "main.py" "src/core/config.py" "src/core/database.py" "src/models/task.py" "src/api/tasks.py")

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (missing)"
        exit 1
    fi
done

echo ""
echo -e "${YELLOW}Step 2: Testing Docker build locally...${NC}"
echo "Building Docker image..."

if docker build -t todo-backend-test . > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker build successful"
else
    echo -e "${RED}✗${NC} Docker build failed"
    echo "Run 'docker build -t todo-backend-test .' to see detailed errors"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 3: Deployment checklist${NC}"
echo ""
echo "Before deploying to Hugging Face, make sure you have:"
echo ""
echo "1. ✓ Hugging Face account (https://huggingface.co/join)"
echo "2. ✓ Neon PostgreSQL database (https://neon.tech)"
echo "3. ✓ DATABASE_URL connection string"
echo "4. ✓ Git installed and configured"
echo ""

read -p "Have you completed all the above? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Please complete the checklist first:"
    echo ""
    echo "→ Create Neon account: https://neon.tech"
    echo "→ Create Hugging Face account: https://huggingface.co/join"
    echo "→ Get your DATABASE_URL from Neon dashboard"
    echo ""
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 4: Hugging Face Space setup${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Go to https://huggingface.co/spaces"
echo "2. Click 'Create new Space'"
echo "3. Fill in:"
echo "   - Space name: todo-backend-api"
echo "   - License: MIT"
echo "   - SDK: Docker"
echo "   - Hardware: CPU basic (free)"
echo ""
echo "4. After creating the Space, add secrets:"
echo "   - Go to Settings → Repository secrets"
echo "   - Add DATABASE_URL (your Neon connection string)"
echo "   - Add CORS_ORIGINS (http://localhost:3000)"
echo ""

read -p "Have you created your Hugging Face Space? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Create your Space first, then run this script again."
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 5: Enter your Hugging Face username${NC}"
read -p "Hugging Face username: " HF_USERNAME

if [ -z "$HF_USERNAME" ]; then
    echo -e "${RED}Error: Username cannot be empty${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 6: Preparing files for deployment...${NC}"

# Copy README_HF.md to README.md for Hugging Face
if [ -f "README_HF.md" ]; then
    cp README_HF.md README.md
    echo -e "${GREEN}✓${NC} README.md prepared"
fi

echo ""
echo -e "${YELLOW}Step 7: Git setup${NC}"

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
    echo -e "${GREEN}✓${NC} Git initialized"
fi

# Add Hugging Face remote
HF_SPACE_URL="https://huggingface.co/spaces/$HF_USERNAME/todo-backend-api"
if git remote | grep -q "hf"; then
    git remote remove hf
fi
git remote add hf $HF_SPACE_URL
echo -e "${GREEN}✓${NC} Hugging Face remote added"

echo ""
echo -e "${YELLOW}Step 8: Committing files...${NC}"

# Add files
git add Dockerfile requirements.txt main.py src/ README.md .dockerignore

# Commit
git commit -m "Deploy Todo Backend API to Hugging Face Spaces" || echo "No changes to commit"

echo ""
echo -e "${YELLOW}Step 9: Pushing to Hugging Face...${NC}"
echo ""
echo "You will be prompted for your Hugging Face credentials:"
echo "- Username: $HF_USERNAME"
echo "- Password: Use your Hugging Face Access Token"
echo "  (Get it from: https://huggingface.co/settings/tokens)"
echo ""

read -p "Ready to push? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if git push hf main; then
        echo ""
        echo -e "${GREEN}✓ Deployment successful!${NC}"
        echo ""
        echo "Your API will be available at:"
        echo "https://$HF_USERNAME-todo-backend-api.hf.space"
        echo ""
        echo "API Documentation:"
        echo "https://$HF_USERNAME-todo-backend-api.hf.space/docs"
        echo ""
        echo "Next steps:"
        echo "1. Wait 2-5 minutes for the build to complete"
        echo "2. Check build logs in your Space's 'Logs' tab"
        echo "3. Test the API at the URL above"
        echo "4. Update your frontend .env.local with the new API URL"
        echo ""
    else
        echo ""
        echo -e "${RED}✗ Push failed${NC}"
        echo ""
        echo "Common issues:"
        echo "- Wrong credentials (use Access Token, not password)"
        echo "- Space doesn't exist (create it first)"
        echo "- Network issues (check your connection)"
        echo ""
    fi
fi

echo ""
echo "Deployment script completed!"
