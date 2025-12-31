# Phase II: Full-Stack Web Application

**Status:** ⏳ In Progress
**Points:** 150
**Tech Stack:** Next.js, FastAPI, SQLModel, Neon DB
**Due Date:** Dec 14, 2025

## Overview

Phase II transforms the in-memory console app into a full-stack web application with database persistence and REST API.

## What's New

### Backend (FastAPI)
- RESTful API endpoints for all CRUD operations
- SQLModel for database ORM
- Neon PostgreSQL for cloud database
- CORS support for frontend integration

### Frontend (Next.js 15)
- Modern React UI with TypeScript
- Real-time todo management
- Responsive design
- State management with React hooks

## Quick Start

### Backend Setup

```bash
cd backend
uv venv
uv sync
uvicorn main:app --reload
```

**API will run on:** `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

**Frontend will run on:** `http://localhost:3000`

## Deployment

### Frontend to Vercel

**Option 1: Vercel Dashboard**
1. Link GitHub repository
2. Set **Root Directory** to: `phase-02-fullstack-web/frontend`
3. Deploy

**Option 2: vercel.json** (at project root)
```json
{
  "buildCommand": "cd phase-02-fullstack-web/frontend && npm run build",
  "outputDirectory": "phase-02-fullstack-web/frontend/.next",
  "installCommand": "cd phase-02-fullstack-web/frontend && npm install"
}
```

### Backend to Cloud

Recommended platforms:
- **Railway**: Auto-deploys from GitHub
- **Render**: Fast and simple
- **Fly.io**: Edge deployment

## Project Structure

```
phase-02-fullstack-web/
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js App Router
│   │   ├── components/       # React components
│   │   └── lib/              # API clients
│   ├── package.json
│   └── next.config.js
└── backend/
    ├── src/
    │   ├── domain/           # Domain models (same as Phase I)
    │   ├── service/          # Business logic
    │   ├── repository/        # Database operations
    │   └── api/              # FastAPI routes
    ├── main.py
    └── pyproject.toml
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/todos` | Get all todos |
| POST | `/api/todos` | Create a new todo |
| GET | `/api/todos/{id}` | Get todo by ID |
| PUT | `/api/todos/{id}` | Update todo |
| DELETE | `/api/todos/{id}` | Delete todo |
| PATCH | `/api/todos/{id}/complete` | Toggle completion status |

## Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql://user:pass@host/db
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Architecture Decisions

- **Domain Model Preservation**: The Todo entity remains unchanged from Phase I
- **Repository Pattern**: New repository layer separates persistence from business logic
- **API Versioning**: `/api/v1/` prefix for future compatibility
- **Type Safety**: Full TypeScript coverage (frontend + SQLModel backend)

## Next Steps

Phase III will add:
- AI-powered chatbot interface
- Natural language todo creation
- Smart scheduling and prioritization
- OpenAI ChatKit integration
