# Tasks: AI-Powered Todo Chatbot

**Input**: Design documents from `/specs/001-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL per constitution - not included unless explicitly requested in specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `phase-03-ai-chatbot/backend/src/`, `phase-03-ai-chatbot/frontend/src/`
- Backend: Python 3.13+, FastAPI, SQLModel, PostgreSQL, OpenAI Agents SDK, MCP SDK
- Frontend: TypeScript/Node.js 20+, Next.js 16+, React 19, Hosted ChatKit

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Copy Phase 2 codebase to phase-03-ai-chatbot/ directory (excluding node_modules, venv, .next)
- [X] T002 Update backend requirements.txt with openai>=1.0.0 and mcp-sdk>=0.1.0
- [X] T003 [P] Update backend .env.example with OPENAI_API_KEY, OPENAI_MODEL, MCP_SERVER_PORT
- [X] T004 [P] Update frontend package.json with ChatKit dependencies (if npm package available)
- [X] T005 [P] Update frontend .env.local.example with NEXT_PUBLIC_OPENAI_DOMAIN_KEY

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create database migration script for Conversation table in phase-03-ai-chatbot/backend/migrations/add_conversations.sql
- [X] T007 Create database migration script for Message table in phase-03-ai-chatbot/backend/migrations/add_messages.sql
- [X] T008 Run database migrations to create conversations and messages tables
- [X] T009 [P] Create Conversation model in phase-03-ai-chatbot/backend/src/models/conversation.py
- [X] T010 [P] Create Message model in phase-03-ai-chatbot/backend/src/models/message.py
- [X] T011 Update backend config.py to include OpenAI configuration (API key, model) in phase-03-ai-chatbot/backend/src/core/config.py
- [X] T012 Initialize MCP server in phase-03-ai-chatbot/backend/src/services/mcp_server.py
- [X] T013 Register add_task MCP tool in phase-03-ai-chatbot/backend/src/services/mcp_server.py
- [X] T014 [P] Register list_tasks MCP tool in phase-03-ai-chatbot/backend/src/services/mcp_server.py
- [X] T015 [P] Register complete_task MCP tool in phase-03-ai-chatbot/backend/src/services/mcp_server.py
- [X] T016 [P] Register delete_task MCP tool in phase-03-ai-chatbot/backend/src/services/mcp_server.py
- [X] T017 [P] Register update_task MCP tool in phase-03-ai-chatbot/backend/src/services/mcp_server.py
- [X] T018 Create ChatService for conversation and message management in phase-03-ai-chatbot/backend/src/services/chat_service.py
- [X] T019 Initialize OpenAI Agents SDK with MCP tools in phase-03-ai-chatbot/backend/src/services/chat_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks by typing natural language commands in chat interface

**Independent Test**: Send message "Add a task to buy groceries" and verify task is created in database with correct title

### Implementation for User Story 1

- [X] T020 [US1] Implement POST /api/{user_id}/chat endpoint in phase-03-ai-chatbot/backend/src/api/chat.py
- [X] T021 [US1] Add conversation retrieval or creation logic in chat endpoint (phase-03-ai-chatbot/backend/src/api/chat.py)
- [X] T022 [US1] Add message history loading (last 50 messages) in chat endpoint (phase-03-ai-chatbot/backend/src/api/chat.py)
- [X] T023 [US1] Integrate OpenAI agent execution with conversation context in chat endpoint (phase-03-ai-chatbot/backend/src/api/chat.py)
- [X] T024 [US1] Add user and assistant message persistence in chat endpoint (phase-03-ai-chatbot/backend/src/api/chat.py)
- [X] T025 [US1] Add character limit validation (5000 chars) for incoming messages in chat endpoint (phase-03-ai-chatbot/backend/src/api/chat.py)
- [X] T026 [US1] Register chat router in main.py (phase-03-ai-chatbot/backend/main.py)
- [X] T027 [P] [US1] Create chat page route in phase-03-ai-chatbot/frontend/src/app/chat/page.tsx
- [X] T028 [P] [US1] Implement ChatInterface component with hosted ChatKit integration in phase-03-ai-chatbot/frontend/src/components/chat/chat-interface.tsx
- [X] T029 [P] [US1] Create chat API service client in phase-03-ai-chatbot/frontend/src/lib/chat-service.ts
- [X] T030 [US1] Connect ChatInterface to backend chat endpoint using chat-service.ts
- [X] T031 [US1] Add error handling for chat endpoint failures (task not created, API errors)
- [X] T032 [US1] Add "Chat Assistant" navigation link with message bubble icon to main layout in phase-03-ai-chatbot/frontend/src/app/layout.tsx
- [X] T033 [P] [US1] Create FloatingChatButton component (message bubble icon, bottom-right) in phase-03-ai-chatbot/frontend/src/components/chat/floating-chat-button.tsx
- [X] T034 [US1] Add FloatingChatButton to root layout, positioned fixed bottom-right corner
- [X] T035 [US1] Implement navigation to /chat page on button/link click

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via natural language and access chat from anywhere

---

## Phase 4: User Story 2 - View and Filter Tasks (Priority: P1)

**Goal**: Users can ask chatbot to show tasks with natural language queries, including filtering by completion status

**Independent Test**: Create sample tasks, then ask "Show me all my tasks" and verify chatbot lists them correctly

### Implementation for User Story 2

- [X] T036 [US2] Enhance list_tasks MCP tool to support status filtering (all, pending, completed) in phase-03-ai-chatbot/backend/src/services/mcp_server.py
- [X] T037 [US2] Add natural language interpretation for task listing commands in OpenAI agent instructions (phase-03-ai-chatbot/backend/src/services/chat_service.py)
- [X] T038 [US2] Format task list responses for user-friendly display in chat (phase-03-ai-chatbot/backend/src/services/chat_service.py)
- [X] T039 [US2] Handle empty task list scenario with friendly message

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can create and view tasks

---

## Phase 5: User Story 3 - Mark Tasks Complete (Priority: P2)

**Goal**: Users can mark tasks as complete through natural language commands

**Independent Test**: Create a task, then say "Mark task 3 as complete" and verify task status changes

### Implementation for User Story 3

- [X] T040 [US3] Enhance complete_task MCP tool to toggle completion status in phase-03-ai-chatbot/backend/src/services/mcp_server.py
- [X] T041 [US3] Add natural language interpretation for task completion commands (phase-03-ai-chatbot/backend/src/services/chat_service.py)
- [ ] T042 [US3] Add fuzzy matching for task titles (e.g., "I finished buying groceries" → find "Buy groceries" task)
- [X] T043 [US3] Implement ambiguous command resolution (numbered list when multiple matches) per FR-007
- [X] T044 [US3] Add confirmation messages for task completion

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Conversation Continuity (Priority: P2)

**Goal**: Users can resume previous conversations with chatbot remembering context

**Independent Test**: Create a task, close chat, reopen it, and verify conversation history is preserved

### Implementation for User Story 4

- [X] T045 [P] [US4] Create GET /api/{user_id}/conversations endpoint in phase-03-ai-chatbot/backend/src/api/chat.py
- [X] T046 [P] [US4] Create GET /api/{user_id}/conversations/{conversation_id}/messages endpoint in phase-03-ai-chatbot/backend/src/api/chat.py
- [X] T047 [US4] Implement conversation list retrieval with pagination (limit, offset) in ChatService
- [X] T048 [US4] Implement message history loading with pagination (limit, before timestamp) in ChatService
- [X] T049 [P] [US4] Create ConversationList component in phase-03-ai-chatbot/frontend/src/components/chat/conversation-list.tsx
- [X] T050 [P] [US4] Create MessageList component with pagination in phase-03-ai-chatbot/frontend/src/components/chat/message-list.tsx
- [X] T051 [US4] Add conversation switching functionality in ChatInterface component
- [X] T052 [US4] Persist active conversation_id in frontend state (localStorage or session)
- [X] T053 [US4] Load conversation history on chat page mount

**Checkpoint**: At this point, all P1 and P2 user stories should work independently

---

## Phase 7: User Story 5 - Update Task Details (Priority: P3)

**Goal**: Users can modify task titles and descriptions through conversational commands

**Independent Test**: Create a task, then say "Change task 1 to 'Call mom tonight'" and verify title updates

### Implementation for User Story 5

- [X] T054 [US5] Enhance update_task MCP tool to support title and description updates in phase-03-ai-chatbot/backend/src/services/mcp_server.py
- [X] T055 [US5] Add natural language interpretation for task update commands (phase-03-ai-chatbot/backend/src/services/chat_service.py)
- [X] T056 [US5] Add character limit validation (200 for title, 2000 for description) in update_task tool
- [X] T057 [US5] Add confirmation messages for task updates

**Checkpoint**: User Story 5 complete and independently testable

---

## Phase 8: User Story 6 - Delete Tasks (Priority: P3)

**Goal**: Users can remove tasks through natural language commands

**Independent Test**: Create a task, then say "Delete task 4" and verify it's removed from database

### Implementation for User Story 6

- [X] T058 [US6] Enhance delete_task MCP tool with proper authorization checks in phase-03-ai-chatbot/backend/src/services/mcp_server.py
- [X] T059 [US6] Add natural language interpretation for task deletion commands (phase-03-ai-chatbot/backend/src/services/chat_service.py)
- [X] T060 [US6] Add confirmation messages for task deletion
- [X] T061 [US6] Handle task not found errors gracefully

**Checkpoint**: All user stories (P1, P2, P3) should now be independently functional

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T062 [P] Add comprehensive error handling for database connection failures across all endpoints
- [X] T063 [P] Add logging for all MCP tool invocations in phase-03-ai-chatbot/backend/src/services/mcp_server.py
- [X] T064 [P] Add logging for chat endpoint operations in phase-03-ai-chatbot/backend/src/api/chat.py
- [X] T065 [P] Implement rate limiting for chat endpoint to prevent abuse
- [X] T066 [P] Add user-friendly error messages for all edge cases (gibberish input, very long messages, etc.)
- [ ] T067 Deploy frontend to Vercel and obtain production URL
- [ ] T068 Configure OpenAI domain allowlist with Vercel URL
- [ ] T069 Set NEXT_PUBLIC_OPENAI_DOMAIN_KEY in Vercel environment variables
- [ ] T070 Update README.md with Phase 3 setup instructions
- [ ] T071 Run quickstart.md validation to verify all setup steps work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent of US1 but builds on same infrastructure
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent of US1/US2
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Independent of US1/US2/US3
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 6 (P3)**: Can start after Foundational (Phase 2) - Independent of other stories

### Within Each User Story

- Backend implementation before frontend integration
- MCP tools before chat endpoint logic
- Core functionality before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005)
- All Foundational model tasks marked [P] can run in parallel (T009, T010)
- All MCP tool registration tasks marked [P] can run in parallel (T014, T015, T016, T017)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Frontend components within a story marked [P] can run in parallel (T027, T028, T029, T033)
- Polish tasks marked [P] can run in parallel (T062, T063, T064, T065, T066)

---

## Parallel Example: User Story 1

```bash
# Launch frontend components for User Story 1 together:
Task: "Create chat page route in phase-03-ai-chatbot/frontend/src/app/chat/page.tsx"
Task: "Implement ChatInterface component with hosted ChatKit integration in phase-03-ai-chatbot/frontend/src/components/chat/chat-interface.tsx"
Task: "Create chat API service client in phase-03-ai-chatbot/frontend/src/lib/chat-service.ts"
Task: "Create FloatingChatButton component (message bubble icon, bottom-right) in phase-03-ai-chatbot/frontend/src/components/chat/floating-chat-button.tsx"
```

---

## Parallel Example: User Story 4

```bash
# Launch API endpoints for User Story 4 together:
Task: "Create GET /api/{user_id}/conversations endpoint in phase-03-ai-chatbot/backend/src/api/chat.py"
Task: "Create GET /api/{user_id}/conversations/{conversation_id}/messages endpoint in phase-03-ai-chatbot/backend/src/api/chat.py"

# Launch frontend components for User Story 4 together:
Task: "Create ConversationList component in phase-03-ai-chatbot/frontend/src/components/chat/conversation-list.tsx"
Task: "Create MessageList component with pagination in phase-03-ai-chatbot/frontend/src/components/chat/message-list.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only - Both P1)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Natural Language Task Creation) - 16 tasks including chat accessibility
4. Complete Phase 4: User Story 2 (View and Filter Tasks) - 4 tasks
5. **STOP and VALIDATE**: Test User Stories 1 & 2 independently
6. Deploy/demo if ready

**Rationale**: Both US1 and US2 are P1 (highest priority) and together form a minimal viable chatbot - users can create and view tasks through natural language. Chat is accessible via navigation link and floating button.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (includes chat accessibility)
3. Add User Story 2 → Test independently → Deploy/Demo (MVP with create + view!)
4. Add User Story 3 → Test independently → Deploy/Demo (add task completion)
5. Add User Story 4 → Test independently → Deploy/Demo (add conversation continuity)
6. Add User Stories 5 & 6 → Test independently → Deploy/Demo (full feature set)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Natural Language Task Creation)
   - Developer B: User Story 2 (View and Filter Tasks)
   - Developer C: User Story 3 (Mark Tasks Complete)
   - Developer D: User Story 4 (Conversation Continuity)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are OPTIONAL per constitution - not included unless explicitly requested
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Character limits enforced: 200 (task title), 2000 (task description), 5000 (message content)
- Conversation pagination: Load last 50 messages by default
- Ambiguous commands resolved via numbered list selection (FR-007)
