# Quickstart Guide - AI-Powered Todo Chatbot

**Feature**: 001-ai-chatbot
**Date**: 2026-01-15
**Prerequisites**: Phase 2 infrastructure (FastAPI backend, PostgreSQL, Next.js frontend, JWT auth)

## Overview

This guide walks through setting up and running the AI-powered todo chatbot feature. The system extends Phase 2 with conversational task management using OpenAI Agents SDK and MCP server.

## Architecture Overview

```
┌─────────────────┐
│  Hosted ChatKit │ (OpenAI)
│   (Frontend UI) │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│   Next.js App   │
│  (phase-03-ai-  │
│   chatbot/      │
│   frontend)     │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐      ┌──────────────┐
│  FastAPI Backend│◄────►│  PostgreSQL  │
│  Chat Endpoint  │      │  Database    │
│  /api/{user}/   │      │  - tasks     │
│  chat           │      │  - users     │
└────────┬────────┘      │  - convs     │
         │               │  - messages  │
         ▼               └──────────────┘
┌─────────────────┐
│  OpenAI Agents  │
│      SDK        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   MCP Server    │
│   (5 tools)     │
│  - add_task     │
│  - list_tasks   │
│  - complete_task│
│  - delete_task  │
│  - update_task  │
└─────────────────┘
```

## Prerequisites

### Required Software
- Python 3.13+
- Node.js 20+
- PostgreSQL 14+
- Git

### Required Accounts
- OpenAI API account (for Agents SDK)
- Vercel account (for frontend deployment)
- OpenAI Platform access (for ChatKit domain allowlisting)

### Phase 2 Setup
Ensure Phase 2 is working:
```bash
# Backend should be running
cd phase-02-fullstack-web/backend
python main.py

# Frontend should be running
cd phase-02-fullstack-web/frontend
npm run dev

# Database should have users and tasks tables
psql $DATABASE_URL -c "\dt"
```

## Setup Instructions

### Step 1: Copy Phase 2 to Phase 3

```bash
# From project root
cp -r phase-02-fullstack-web phase-03-ai-chatbot

# Exclude large directories
rm -rf phase-03-ai-chatbot/backend/venv
rm -rf phase-03-ai-chatbot/frontend/node_modules
rm -rf phase-03-ai-chatbot/frontend/.next
```

### Step 2: Backend Setup

#### 2.1 Install Dependencies

```bash
cd phase-03-ai-chatbot/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install existing dependencies
pip install -r requirements.txt

# Install new dependencies
pip install openai mcp-sdk
```

#### 2.2 Update requirements.txt

Add to `requirements.txt`:
```
openai>=1.0.0
mcp-sdk>=0.1.0
```

#### 2.3 Configure Environment Variables

Update `.env`:
```bash
# Existing from Phase 2
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db
BETTER_AUTH_SECRET=your-secret-key
CORS_ORIGINS=http://localhost:3000

# New for Phase 3
OPENAI_API_KEY=sk-...your-openai-api-key
OPENAI_MODEL=gpt-4
MCP_SERVER_PORT=8001
```

#### 2.4 Run Database Migrations

```bash
# Create migration script
cat > migrations/add_chat_tables.sql << 'EOF'
-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL CHECK (LENGTH(content) <= 5000 AND LENGTH(TRIM(content)) > 0),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created ON messages(conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
EOF

# Run migration
psql $DATABASE_URL -f migrations/add_chat_tables.sql
```

#### 2.5 Start Backend

```bash
# From phase-03-ai-chatbot/backend
uvicorn main:app --reload --port 8000
```

Verify backend is running:
```bash
curl http://localhost:8000/
# Should return: {"status": "healthy", ...}
```

### Step 3: Frontend Setup

#### 3.1 Install Dependencies

```bash
cd phase-03-ai-chatbot/frontend

# Install existing dependencies
npm install

# Install ChatKit (if available as npm package)
# Note: Hosted ChatKit may not require npm package
# Check OpenAI documentation for latest integration method
```

#### 3.2 Configure Environment Variables

Update `.env.local`:
```bash
# Existing from Phase 2
NEXT_PUBLIC_API_URL=http://localhost:8000

# New for Phase 3 (will be set after deployment)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=
```

#### 3.3 Start Frontend (Local Development)

```bash
# From phase-03-ai-chatbot/frontend
npm run dev
```

Visit http://localhost:3000 to verify frontend is running.

### Step 4: Deploy Frontend to Vercel

#### 4.1 Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from frontend directory
cd phase-03-ai-chatbot/frontend
vercel --prod
```

Note your production URL (e.g., `https://todo-chatbot-xyz.vercel.app`)

#### 4.2 Configure Domain Allowlist

1. Go to https://platform.openai.com/settings/organization/security/domain-allowlist
2. Click "Add domain"
3. Enter your Vercel URL (without trailing slash): `https://todo-chatbot-xyz.vercel.app`
4. Save configuration
5. Copy the provided domain key

#### 4.3 Update Environment Variables

```bash
# Set domain key in Vercel
vercel env add NEXT_PUBLIC_OPENAI_DOMAIN_KEY production
# Paste the domain key when prompted

# Redeploy to apply environment variable
vercel --prod
```

### Step 5: Verify Installation

#### 5.1 Test Backend Chat Endpoint

```bash
# Get JWT token (login via Phase 2 auth)
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.access_token')

# Test chat endpoint
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Add a task to buy groceries"}'

# Expected response:
# {
#   "conversation_id": 1,
#   "response": "I've created a task 'Buy groceries' for you.",
#   "tool_calls": [...]
# }
```

#### 5.2 Test Frontend Chat Interface

1. Visit your Vercel URL
2. Login with Phase 2 credentials
3. Navigate to `/chat` page
4. Type: "Add a task to buy groceries"
5. Verify task is created and chatbot responds

#### 5.3 Verify Database

```bash
# Check conversations table
psql $DATABASE_URL -c "SELECT * FROM conversations LIMIT 5;"

# Check messages table
psql $DATABASE_URL -c "SELECT * FROM messages LIMIT 10;"

# Check tasks were created via chat
psql $DATABASE_URL -c "SELECT * FROM tasks ORDER BY created_at DESC LIMIT 5;"
```

## Common Issues & Troubleshooting

### Issue: ChatKit not loading

**Symptoms**: Blank chat interface or "Domain not allowlisted" error

**Solutions**:
1. Verify domain is added to OpenAI allowlist (exact URL match)
2. Check `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` is set correctly
3. Redeploy frontend after setting environment variable
4. Clear browser cache and reload

### Issue: Chat endpoint returns 500 error

**Symptoms**: "Internal server error" when sending messages

**Solutions**:
1. Check `OPENAI_API_KEY` is set in backend `.env`
2. Verify OpenAI API key has sufficient credits
3. Check backend logs for detailed error messages
4. Ensure MCP server is initialized correctly

### Issue: Tasks not being created

**Symptoms**: Chatbot responds but tasks don't appear in database

**Solutions**:
1. Verify MCP tools are registered correctly
2. Check backend logs for tool invocation errors
3. Test task creation via Phase 2 UI to verify backend works
4. Ensure user_id is passed correctly to MCP tools

### Issue: Conversation history not loading

**Symptoms**: Previous messages don't appear when reopening chat

**Solutions**:
1. Verify conversations and messages tables exist
2. Check database indexes are created
3. Verify conversation_id is persisted in frontend state
4. Check backend logs for database query errors

## Development Workflow

### Running Locally

```bash
# Terminal 1: Backend
cd phase-03-ai-chatbot/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd phase-03-ai-chatbot/frontend
npm run dev

# Terminal 3: Database (if needed)
psql $DATABASE_URL
```

### Testing Changes

```bash
# Backend: Run tests (if implemented)
cd phase-03-ai-chatbot/backend
pytest

# Frontend: Run tests (if implemented)
cd phase-03-ai-chatbot/frontend
npm test

# Manual testing via curl
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Show me all my tasks"}'
```

### Deploying Updates

```bash
# Backend: Deploy to your hosting provider
# (Deployment method depends on hosting choice)

# Frontend: Deploy to Vercel
cd phase-03-ai-chatbot/frontend
vercel --prod
```

## Next Steps

After completing setup:

1. **Test all user stories** from spec.md
2. **Monitor OpenAI API usage** and costs
3. **Implement error handling** improvements
4. **Add conversation management UI** (list, switch, delete conversations)
5. **Optimize message loading** (implement pagination UI)
6. **Add analytics** (track tool usage, conversation metrics)

## Resources

- **Specification**: `specs/001-ai-chatbot/spec.md`
- **Data Model**: `specs/001-ai-chatbot/data-model.md`
- **API Contracts**: `specs/001-ai-chatbot/contracts/`
- **OpenAI Agents SDK**: https://platform.openai.com/docs/agents
- **MCP Documentation**: https://modelcontextprotocol.io/
- **Phase 2 Documentation**: `phase-02-fullstack-web/README.md`
