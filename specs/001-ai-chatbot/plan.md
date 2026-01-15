# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `001-ai-chatbot` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create an AI-powered chatbot interface that enables users to man/age todo tasks through natural language conversations. The system extends Phase 2 infrastructure (FastAPI backend, PostgreSQL database, Next.js frontend, JWT authentication) with:
- Hosted OpenAI ChatKit for conversational UI
- OpenAI Agents SDK for natural language interpretation
- MCP (Model Context Protocol) server exposing task operations as tools
- Stateless chat endpoint with database-persisted conversation state
- Support for multiple conversations per user with automatic creation
- Character limits: 200 (task title), 2000 (task description), 5000 (message content)
- Pagination: Load last 50 messages per conversation with on-demand loading

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Node.js 20+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, PostgreSQL, OpenAI Agents SDK, MCP SDK (Python), python-dotenv
- Frontend: Next.js 16+, React 19, Hosted OpenAI ChatKit, Tailwind CSS
**Storage**: PostgreSQL (existing Phase 2 database, extended with Conversation and Message tables)
**Testing**: pytest (backend), Jest/React Testing Library (frontend) - OPTIONAL per constitution unless explicitly requested
**Target Platform**: Web application - Vercel (frontend), cloud hosting for backend (TBD)
**Project Type**: Web (frontend + backend extending Phase 2)
**Performance Goals**:
- 2 second response time for chat messages under normal load
- Support 50 concurrent chat sessions without degradation
- Task creation <10 seconds, task viewing <5 seconds
**Constraints**:
- Character limits: 200 (task title), 2000 (task description), 5000 (message content)
- Pagination: Load last 50 messages per conversation
- Must use hosted ChatKit (not self-hosted)
- Domain allowlisting required before production
**Scale/Scope**:
- 1-5 active conversations per user (typical)
- 10-20 messages per conversation (average)
- Extends existing Phase 2 task management system

**Research Needed**:
- MCP SDK Python implementation patterns and best practices
- OpenAI Agents SDK integration with FastAPI
- Hosted ChatKit domain allowlisting and configuration workflow
- Stateless chat endpoint architecture with conversation state persistence
- MCP tool definition patterns for task operations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development First
✅ **PASS** - Complete specification exists at `specs/001-ai-chatbot/spec.md` with:
- 6 prioritized user stories with acceptance criteria
- 15 functional requirements (FR-001 through FR-015)
- 8 measurable success criteria
- Clarifications session completed (5 questions resolved)

### Principle II: AI as Implementer, Human as Architect
✅ **PASS** - Following spec-driven workflow:
- Human architect defined requirements and clarified ambiguities
- Claude Code executing planning phase per `/sp.plan` command
- AI chatbot feature operates under explicit constraints (FR-007, FR-008a, FR-008b)

### Principle III: Deterministic Behavior Across Non-LLM Components
✅ **PASS** - Architecture maintains determinism:
- Database operations (Conversation, Message, Task) are deterministic
- MCP tools have predictable inputs/outputs
- Only AI agent (OpenAI Agents SDK) is non-deterministic, isolated to natural language interpretation
- State mutations explicit (conversation creation, message persistence, task operations)

### Principle IV: Evolvability Across Phases
✅ **PASS** - Extends Phase 2 without breaking contracts:
- Reuses existing Task entity and APIs
- Adds new entities (Conversation, Message) without modifying existing schema
- Domain logic (task management) remains independent of chat interface
- Can evolve chat UI without affecting task operations

### Principle V: Clear Separation of Domain Logic, Interfaces, and Infrastructure
✅ **PASS** - Maintains architectural boundaries:
- **Domain**: Task management logic (existing from Phase 2)
- **Interfaces**: Chat endpoint (`/api/{user_id}/chat`), MCP tools, hosted ChatKit UI
- **Infrastructure**: PostgreSQL (conversations, messages), OpenAI Agents SDK, MCP server

### Principle VI: Reusable Intelligence Over One-Off Solutions
✅ **PASS** - AI feature designed for reusability:
- MCP tools are reusable (add_task, list_tasks, complete_task, delete_task, update_task)
- Explicit constraints: character limits, ambiguity resolution (numbered list), error handling
- Predictable tool usage patterns defined in spec
- Fails safely: errors return user-friendly messages without corrupting state

### Principle VII: Infrastructure as Declarative and Reproducible
✅ **PASS** - Infrastructure will be declarative:
- Environment variables for configuration (DATABASE_URL, OPENAI_API_KEY, NEXT_PUBLIC_OPENAI_DOMAIN_KEY)
- Database migrations for schema changes (Conversation, Message tables)
- Deployment configs for Vercel (frontend) and backend hosting

**Overall Status**: ✅ **ALL GATES PASSED** - No constitutional violations. Proceed to Phase 0 research.

---

## Phase 0: Research (Completed)

**Output**: `research.md`

All technical unknowns resolved:
- ✅ MCP SDK Python implementation patterns
- ✅ OpenAI Agents SDK integration with FastAPI
- ✅ Hosted ChatKit domain allowlisting workflow
- ✅ Stateless chat endpoint architecture
- ✅ MCP tool definition patterns

---

## Phase 1: Design & Contracts (Completed)

**Outputs**:
- ✅ `data-model.md` - Database entities (Conversation, Message, Task)
- ✅ `contracts/chat-api.yaml` - OpenAPI specification for chat endpoint
- ✅ `contracts/mcp-tools.json` - MCP tool definitions (5 tools)
- ✅ `quickstart.md` - Setup and deployment guide

---

## Constitution Check (Post-Design Re-evaluation)

*Re-check after Phase 1 design completed.*

### Principle I: Spec-Driven Development First
✅ **PASS** - Design artifacts created from specification:
- Data model derived from Key Entities in spec
- API contracts derived from Functional Requirements
- All design decisions traceable to spec requirements

### Principle II: AI as Implementer, Human as Architect
✅ **PASS** - Planning phase completed by Claude Code following `/sp.plan` workflow:
- Research decisions documented with rationale
- Design choices explicit and justified
- No feature invention beyond spec

### Principle III: Deterministic Behavior Across Non-LLM Components
✅ **PASS** - Design maintains determinism:
- Database schema is deterministic (PostgreSQL)
- MCP tools have predictable inputs/outputs
- Stateless endpoint design ensures reproducibility
- Only OpenAI Agents SDK is non-deterministic (isolated)

### Principle IV: Evolvability Across Phases
✅ **PASS** - Design supports evolution:
- New entities (Conversation, Message) don't modify existing schema
- Task entity reused without changes
- Chat interface decoupled from task domain logic
- Can add new MCP tools without breaking existing ones

### Principle V: Clear Separation of Domain Logic, Interfaces, and Infrastructure
✅ **PASS** - Architecture maintains boundaries:
- **Domain**: Task management (unchanged from Phase 2)
- **Interfaces**: Chat endpoint, MCP tools, ChatKit UI
- **Infrastructure**: PostgreSQL, OpenAI Agents SDK, MCP server
- Clear separation documented in data-model.md and contracts

### Principle VI: Reusable Intelligence Over One-Off Solutions
✅ **PASS** - AI components designed for reusability:
- MCP tools are reusable across different AI agents
- Tool definitions follow standard MCP schema
- Error handling patterns consistent across tools
- Conversation management reusable for future features

### Principle VII: Infrastructure as Declarative and Reproducible
✅ **PASS** - Infrastructure is declarative:
- Database migrations in SQL (declarative schema)
- Environment variables for configuration
- Deployment documented in quickstart.md
- Vercel deployment is declarative (vercel.json)

**Post-Design Status**: ✅ **ALL GATES PASSED** - Design maintains constitutional compliance.

---

## Next Phase

**Phase 2**: Task Generation (`/sp.tasks` command)
- Break down implementation into testable tasks
- Define acceptance criteria for each task
- Prioritize tasks by dependency order

**Note**: Planning phase (`/sp.plan`) ends here. Task generation is a separate command.

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-chatbot/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoint
│   └── mcp-tools.json   # MCP tool definitions
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (extends Phase 2)
phase-03-ai-chatbot/
├── backend/
│   ├── src/
│   │   ├── models/
│   │   │   ├── conversation.py    # New: Conversation entity
│   │   │   ├── message.py         # New: Message entity
│   │   │   ├── task.py            # Existing from Phase 2
│   │   │   └── user.py            # Existing from Phase 2
│   │   ├── services/
│   │   │   ├── chat_service.py    # New: Chat endpoint logic
│   │   │   └── mcp_server.py      # New: MCP server implementation
│   │   ├── api/
│   │   │   ├── chat.py            # New: /api/{user_id}/chat endpoint
│   │   │   ├── tasks.py           # Existing from Phase 2
│   │   │   └── auth.py            # Existing from Phase 2
│   │   └── core/
│   │       ├── database.py        # Existing from Phase 2
│   │       ├── config.py          # Existing from Phase 2 (extend with OpenAI config)
│   │       └── auth.py            # Existing from Phase 2
│   ├── tests/                     # Optional per constitution
│   ├── requirements.txt           # Extended with OpenAI SDK, MCP SDK
│   └── main.py                    # Existing from Phase 2
│
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── chat/
    │   │   │   └── page.tsx       # New: Chat interface page
    │   │   ├── page.tsx           # Existing from Phase 2
    │   │   ├── login/             # Existing from Phase 2
    │   │   └── register/          # Existing from Phase 2
    │   ├── components/
    │   │   ├── chat/
    │   │   │   ├── chat-interface.tsx      # New: ChatKit integration
    │   │   │   ├── conversation-list.tsx   # New: Conversation switcher
    │   │   │   └── message-list.tsx        # New: Message display
    │   │   ├── todo/              # Existing from Phase 2
    │   │   └── ui/                # Existing from Phase 2
    │   ├── lib/
    │   │   ├── chat-service.ts    # New: Chat API client
    │   │   ├── api-service.ts     # Existing from Phase 2
    │   │   └── auth-service.ts    # Existing from Phase 2
    │   └── types/
    │       ├── chat.ts            # New: Conversation, Message types
    │       └── task.ts            # Existing from Phase 2
    ├── package.json               # Extended with ChatKit dependencies
    └── .env.local                 # Extended with NEXT_PUBLIC_OPENAI_DOMAIN_KEY
```

**Structure Decision**: Web application structure extending Phase 2. Backend adds chat endpoint, MCP server, and new database models. Frontend adds chat interface using hosted ChatKit. Maintains separation between task management domain logic and chat interface.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations detected. This section is not applicable.
