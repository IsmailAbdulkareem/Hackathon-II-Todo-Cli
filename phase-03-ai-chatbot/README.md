# Phase III: AI-Powered Todo Chatbot

**Status:** ✅ Complete
**Points:** 200
**Tech Stack:** Next.js 16, FastAPI, OpenAI GPT-4o-mini, SQLModel, Neon DB
**Completion Date:** January 16, 2026

## Overview

Phase III transforms the full-stack web application into an AI-powered chatbot that allows users to manage their todos through natural language conversations.

## What's New in Phase 3

### AI Chatbot Features
- **Natural Language Task Management**: Create, view, update, complete, and delete tasks using conversational commands
- **Fuzzy Matching**: AI can find tasks by partial title match (e.g., "I finished buying groceries" → finds "Buy groceries")
- **Conversation History**: Multi-turn conversations with context awareness
- **Smart Interpretation**: AI understands various phrasings and intents
- **Ambiguous Command Resolution**: Presents numbered lists when multiple tasks match

### Backend Enhancements
- **OpenAI Integration**: GPT-4o-mini with function calling for task operations
- **MCP Server**: 6 tools for task management (add, list, complete, delete, update, find_by_title)
- **Chat API**: RESTful endpoints for conversations and messages
- **Rate Limiting**: 10 requests per minute per user to prevent abuse
- **Comprehensive Logging**: INFO/WARNING/ERROR levels for debugging

### Frontend Enhancements
- **Chat Interface**: Modern conversational UI with message bubbles
- **Conversation List**: View and switch between past conversations
- **Message History**: Paginated message loading with "Load older messages"
- **Floating Chat Button**: Quick access from anywhere in the app
- **Real-time Updates**: Instant message display with optimistic UI

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 20+
- PostgreSQL database (Neon recommended)
- OpenAI API key

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd phase-03-ai-chatbot/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create `.env` file:
   ```bash
   # Database
   DATABASE_URL=postgresql://user:pass@host/db

   # CORS
   CORS_ORIGINS=http://localhost:3000,https://your-vercel-app.vercel.app

   # JWT Authentication
   BETTER_AUTH_SECRET=your-jwt-secret-here

   # OpenAI Configuration
   OPENAI_API_KEY=sk-proj-your-openai-api-key
   OPENAI_MODEL=gpt-4o-mini
   ```

5. **Run database migrations:**
   ```bash
   python run_migrations.py
   ```

6. **Start the server:**
   ```bash
   uvicorn main:app --reload
   ```

   **API will run on:** `http://localhost:8000`
   **API Docs:** `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd phase-03-ai-chatbot/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   Create `.env.local` file:
   ```bash
   # Backend API URL
   NEXT_PUBLIC_API_URL=http://localhost:8000

   # OpenAI ChatKit Domain Key (for production)
   NEXT_PUBLIC_OPENAI_DOMAIN_KEY=domain_pk_your-domain-key
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

   **Frontend will run on:** `http://localhost:3000`

## Deployment

### Backend to Hugging Face

**Deployed at:** https://huggingface.co/spaces/ismail233290/TODO_APP

1. **Push to Hugging Face repository:**
   ```bash
   cd TODO_APP
   git add .
   git commit -m "Deploy Phase 3 backend"
   git push origin main
   ```

2. **Set environment variables in Hugging Face:**
   - Go to: Settings → Repository secrets
   - Add: `DATABASE_URL`, `BETTER_AUTH_SECRET`, `OPENAI_API_KEY`, `CORS_ORIGINS`

3. **Hugging Face will automatically:**
   - Build Docker container
   - Run migrations
   - Start the FastAPI server

### Frontend to Vercel

**Deployed at:** https://hackathon-ii-todo-cli.vercel.app

1. **Configure OpenAI Domain Allowlist:**
   - Go to: https://platform.openai.com/settings/organization/domains
   - Add domain: `hackathon-ii-todo-cli.vercel.app`
   - Save configuration

2. **Set Vercel environment variables:**
   - Go to: Vercel Dashboard → Settings → Environment Variables
   - Add:
     - `NEXT_PUBLIC_API_URL=https://ismail233290-todo-app.hf.space`
     - `NEXT_PUBLIC_OPENAI_DOMAIN_KEY=domain_pk_your-domain-key`

3. **Deploy:**
   ```bash
   git push origin main
   ```
   Vercel will automatically deploy on push.

## Project Structure

```
phase-03-ai-chatbot/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── chat/              # Chat page
│   │   │   └── layout.tsx         # Root layout with nav
│   │   ├── components/
│   │   │   └── chat/              # Chat components
│   │   │       ├── chat-interface.tsx
│   │   │       ├── conversation-list.tsx
│   │   │       ├── message-list.tsx
│   │   │       └── floating-chat-button.tsx
│   │   └── lib/
│   │       └── chat-service.ts    # Chat API client
│   ├── package.json
│   └── next.config.js
└── backend/
    ├── src/
    │   ├── api/
    │   │   ├── auth.py            # Authentication endpoints
    │   │   ├── tasks.py           # Task CRUD endpoints
    │   │   └── chat.py            # Chat endpoints (NEW)
    │   ├── core/
    │   │   ├── config.py          # Settings with OpenAI config
    │   │   ├── database.py        # Database connection
    │   │   ├── auth.py            # JWT utilities
    │   │   └── rate_limiter.py    # Rate limiting (NEW)
    │   ├── models/
    │   │   ├── task.py            # Task model
    │   │   ├── user.py            # User model
    │   │   ├── conversation.py    # Conversation model (NEW)
    │   │   └── message.py         # Message model (NEW)
    │   ├── services/
    │   │   ├── mcp_server.py      # MCP tools (NEW)
    │   │   └── chat_service.py    # OpenAI integration (NEW)
    │   └── migrations/
    │       ├── add_conversations.sql  # Conversation table (NEW)
    │       └── add_messages.sql       # Message table (NEW)
    ├── main.py
    ├── requirements.txt
    └── run_migrations.py
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register new user |
| POST | `/api/login` | Login user |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/tasks` | Get all tasks |
| POST | `/api/{user_id}/tasks` | Create a new task |
| GET | `/api/{user_id}/tasks/{task_id}` | Get task by ID |
| PUT | `/api/{user_id}/tasks/{task_id}` | Update task |
| DELETE | `/api/{user_id}/tasks/{task_id}` | Delete task |
| PATCH | `/api/{user_id}/tasks/{task_id}/complete` | Toggle completion |

### Chat (NEW)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/{user_id}/chat` | Send message and get AI response |
| GET | `/api/{user_id}/conversations` | Get conversation list |
| GET | `/api/{user_id}/conversations/{id}/messages` | Get messages |

## MCP Tools

The AI agent has access to 6 tools for task management:

1. **add_task**: Create a new task
2. **list_tasks**: Retrieve tasks (all, pending, or completed)
3. **complete_task**: Mark a task as complete
4. **delete_task**: Remove a task
5. **update_task**: Modify task title or description
6. **find_task_by_title**: Search tasks by partial title match (fuzzy matching)

## Example Conversations

### Creating Tasks
```
User: Add a task to buy groceries
AI: ✓ I've created a new task: "Buy groceries"

User: Remind me to call mom tonight
AI: ✓ I've added "Call mom tonight" to your tasks
```

### Viewing Tasks
```
User: Show me all my tasks
AI: You have 3 tasks:
    1. Buy groceries (pending)
    2. Call mom tonight (pending)
    3. Finish project report (completed)

User: What tasks are still pending?
AI: You have 2 pending tasks:
    1. Buy groceries
    2. Call mom tonight
```

### Completing Tasks (with Fuzzy Matching)
```
User: I finished buying groceries
AI: ✓ Great! I've marked "Buy groceries" as complete

User: Mark task 2 as done
AI: ✓ "Call mom tonight" is now complete
```

### Updating Tasks
```
User: Change task 1 to "Buy groceries and cook dinner"
AI: ✓ I've updated the task title

User: Add a description to task 2: "Call at 7pm"
AI: ✓ I've added the description to "Call mom tonight"
```

### Deleting Tasks
```
User: Delete task 3
AI: ✓ I've removed "Finish project report" from your tasks
```

## Environment Variables

### Backend (.env)
```bash
# Database Configuration
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,https://your-vercel-app.vercel.app,https://your-hf-space.hf.space

# JWT Authentication Secret
BETTER_AUTH_SECRET=your-secret-key-min-32-chars

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
```

### Frontend (.env.local)
```bash
# Backend API URL
# Development: http://localhost:8000
# Production: Your deployed backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# OpenAI ChatKit Domain Key
# Get from: https://platform.openai.com/settings/organization/security/domain-allowlist
# Required for production, optional for localhost
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=domain_pk_your-domain-key
```

## Testing

### Manual Testing

1. **Start both backend and frontend locally**

2. **Register/Login:**
   - Go to: http://localhost:3000
   - Register a new account or login

3. **Test Chat Interface:**
   - Click "Chat Assistant" in navigation or floating chat button
   - Try these commands:
     - "Add a task to buy groceries"
     - "Show me all my tasks"
     - "I finished buying groceries"
     - "Delete task 1"

4. **Test Conversation History:**
   - Close and reopen chat
   - Verify conversation history is preserved
   - Switch between conversations

### API Testing

Use the interactive API docs at `http://localhost:8000/docs`:

1. **Authenticate:**
   - POST `/api/register` or `/api/login`
   - Copy the JWT token

2. **Test Chat Endpoint:**
   - POST `/api/{user_id}/chat`
   - Add Authorization header: `Bearer {token}`
   - Send: `{"message": "Add a task to test the API"}`

3. **Verify Database:**
   - Check conversations table
   - Check messages table
   - Verify tasks were created

## Architecture Decisions

### Phase 3 Additions

1. **OpenAI Function Calling**: Enables AI to invoke task management tools based on natural language
2. **MCP Server Pattern**: Modular tool registration for easy extension
3. **Conversation Persistence**: Full chat history stored in database for context awareness
4. **Rate Limiting**: In-memory rate limiter (10 req/min) prevents API abuse
5. **Fuzzy Matching**: Case-insensitive partial title search for natural language completion
6. **Optimistic UI**: Immediate message display before API response for better UX

## Performance Considerations

- **Rate Limiting**: 10 requests per minute per user
- **Message Pagination**: Load 50 messages at a time
- **Conversation Pagination**: Load 20 conversations at a time
- **Database Indexing**: Indexed on user_id, conversation_id, created_at
- **Connection Pooling**: Neon PostgreSQL with connection pooling enabled

## Security Features

- **JWT Authentication**: All endpoints require valid JWT token
- **User Ownership Validation**: Users can only access their own data
- **Rate Limiting**: Prevents API abuse and DoS attacks
- **Input Validation**: Character limits (200 for title, 2000 for description, 5000 for messages)
- **SQL Injection Prevention**: SQLModel ORM with parameterized queries
- **CORS Configuration**: Whitelist of allowed origins

## Troubleshooting

### Backend Issues

**Issue: ModuleNotFoundError**
- Solution: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Issue: Database connection failed**
- Solution: Verify DATABASE_URL in .env file
- Check Neon database is running and accessible

**Issue: OpenAI API error**
- Solution: Verify OPENAI_API_KEY is valid
- Check API quota and billing status

### Frontend Issues

**Issue: API connection refused**
- Solution: Ensure backend is running on correct port
- Verify NEXT_PUBLIC_API_URL in .env.local

**Issue: Chat not working**
- Solution: Check NEXT_PUBLIC_OPENAI_DOMAIN_KEY is set
- Verify domain is allowlisted in OpenAI dashboard

**Issue: Authentication errors**
- Solution: Clear localStorage and re-login
- Verify JWT token is not expired

## Task Completion Status

**Overall: 67/71 tasks (94%) complete**

### Completed Features
- ✅ Phase 1: Setup (5/5 tasks)
- ✅ Phase 2: Foundational (14/14 tasks)
- ✅ User Story 1: Natural Language Task Creation (16/16 tasks)
- ✅ User Story 2: View and Filter Tasks (4/4 tasks)
- ✅ User Story 3: Mark Tasks Complete (5/5 tasks) - Including fuzzy matching
- ✅ User Story 4: Conversation Continuity (9/9 tasks)
- ✅ User Story 5: Update Task Details (4/4 tasks)
- ✅ User Story 6: Delete Tasks (4/4 tasks)
- ✅ Phase 9: Polish & Cross-Cutting (5/10 tasks)

### Remaining Tasks (Optional)
- ⏳ T067: Deploy frontend to Vercel (Already deployed)
- ⏳ T068: Configure OpenAI domain allowlist (Instructions provided)
- ⏳ T069: Set Vercel environment variables (Instructions provided)
- ⏳ T070: Update README.md (This document)
- ⏳ T071: Run quickstart validation (Next step)

## Next Steps

Phase IV could add:
- Voice input/output for hands-free task management
- Smart scheduling with calendar integration
- Task prioritization based on deadlines and importance
- Collaborative task lists with team members
- Mobile app with push notifications

## Support

For issues or questions:
- Check API docs: http://localhost:8000/docs
- Review logs: Backend console output
- Debug endpoint: http://localhost:8000/debug/config

## License

MIT License - See LICENSE file for details

---

**Built with ❤️ using OpenAI GPT-4o-mini, Next.js 16, and FastAPI**
