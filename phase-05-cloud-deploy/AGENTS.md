# AGENTS.md

## Purpose

This project uses **Spec-Driven Development (SDD)** — a workflow where **no agent is allowed to write code until the specification is complete and approved**.

All AI agents (Claude, Copilot, Gemini, local LLMs, etc.) must follow the **Spec-Kit lifecycle** and adhere to the guidelines defined in this document.

---

## 1. The Mental Model: Who Does What?

| Component | Role | Responsibility |
|-----------|------|----------------|
| **AGENTS.md** | The Brain | Cross-agent truth. Defines how agents should behave, what tools to use, and coding standards. |
| **Spec-KitPlus** | The Architect | Manages spec artifacts (`.specify`, `.plan`, `.tasks`). Ensures technical rigor before coding starts. |
| **Claude Code** | The Executor | The agentic environment. Reads the project memory and executes Spec-Kit tools via MCP. |

**Key Idea:** Claude reads AGENTS.md via a tiny CLAUDE.md shim and interacts with Spec-KitPlus. For development, set up an MCP Server and upgrade SpecifyPlus commands to be available as Prompts in MCP. SpecKitPlus MCP server ensures every line of code maps back to a validated task.

---

## 2. Spec-Driven Development Lifecycle

**STRICT RULE:** No code may be written until all specification artifacts are complete and approved.

### Phase 1: Specification (sp.specify)
- **Input:** Natural language feature description
- **Output:** `specs/<feature>/spec.md`
- **Approval Required:** Yes (user must approve before proceeding)
- **Agent Behavior:** Ask clarifying questions, document requirements, define acceptance criteria

### Phase 2: Planning (sp.plan)
- **Input:** Approved spec.md
- **Output:** `specs/<feature>/plan.md`
- **Approval Required:** Yes (user must approve architecture)
- **Agent Behavior:** Design architecture, identify dependencies, document decisions, suggest ADRs

### Phase 3: Task Breakdown (sp.tasks)
- **Input:** Approved plan.md
- **Output:** `specs/<feature>/tasks.md`
- **Approval Required:** Yes (user must approve task list)
- **Agent Behavior:** Break down into testable tasks, define test cases, establish dependencies

### Phase 4: Implementation (sp.implement)
- **Input:** Approved tasks.md
- **Output:** Working code + tests
- **Approval Required:** Per-task (user can monitor progress)
- **Agent Behavior:** Execute tasks in order, write tests first (TDD), commit frequently

---

## 3. Core Agent Guarantees

All agents MUST adhere to these guarantees:

### 3.1 Prompt History Records (PHR)
- **Record every user input** verbatim in a Prompt History Record after every user message
- **Never truncate** - preserve full multiline input
- **Routing:**
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`

### 3.2 Architectural Decision Records (ADR)
- When architecturally significant decisions are detected, suggest:
  ```
  📋 Architectural decision detected: <brief>
  Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`
  ```
- **Never auto-create ADRs** - require user consent
- **Significance test:** Impact + Alternatives + Scope (all must be true)

### 3.3 Small, Testable Changes
- All outputs strictly follow user intent
- Changes are small, testable, and reference code precisely
- No unrelated refactoring or "improvements"
- Cite existing code with references (file:line)

---

## 4. Development Guidelines

### 4.1 Authoritative Source Mandate
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. **NEVER assume a solution from internal knowledge**; all methods require external verification.

### 4.2 Execution Flow
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. **PREFER CLI interactions** (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 4.3 Human as Tool Strategy
You are not expected to solve every problem autonomously. **MUST invoke the user** for input when you encounter situations that require human judgment.

**Invocation Triggers:**
1. **Ambiguous Requirements:** Ask 2-3 targeted clarifying questions before proceeding
2. **Unforeseen Dependencies:** Surface them and ask for prioritization
3. **Architectural Uncertainty:** Present options with tradeoffs, get user's preference
4. **Completion Checkpoint:** After major milestones, summarize and confirm next steps

---

## 5. Default Policies (MUST FOLLOW)

- **Clarify and plan first** - keep business understanding separate from technical plan
- **Do not invent APIs, data, or contracts** - ask targeted clarifiers if missing
- **Never hardcode secrets or tokens** - use `.env` and documentation
- **Prefer the smallest viable diff** - do not refactor unrelated code
- **Cite existing code** with code references (start:end:path)
- **Keep reasoning private** - output only decisions, artifacts, and justifications

---

## 6. Execution Contract for Every Request

1. **Confirm surface and success criteria** (one sentence)
2. **List constraints, invariants, non-goals**
3. **Produce the artifact** with acceptance checks inlined (checkboxes or tests)
4. **Add follow-ups and risks** (max 3 bullets)
5. **Create PHR** in appropriate subdirectory under `history/prompts/`
6. **If plan/tasks identified decisions** that meet significance, surface ADR suggestion

---

## 7. Minimum Acceptance Criteria

Every deliverable must include:
- Clear, testable acceptance criteria
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

---

## 8. Architect Guidelines (for Planning)

When generating architectural plans, address each of the following thoroughly:

### 8.1 Scope and Dependencies
- **In Scope:** boundaries and key features
- **Out of Scope:** explicitly excluded items
- **External Dependencies:** systems/services/teams and ownership

### 8.2 Key Decisions and Rationale
- Options Considered, Trade-offs, Rationale
- Principles: measurable, reversible where possible, smallest viable change

### 8.3 Interfaces and API Contracts
- Public APIs: Inputs, Outputs, Errors
- Versioning Strategy
- Idempotency, Timeouts, Retries
- Error Taxonomy with status codes

### 8.4 Non-Functional Requirements (NFRs) and Budgets
- **Performance:** p95 latency, throughput, resource caps
- **Reliability:** SLOs, error budgets, degradation strategy
- **Security:** AuthN/AuthZ, data handling, secrets, auditing
- **Cost:** unit economics

### 8.5 Data Management and Migration
- Source of Truth, Schema Evolution, Migration and Rollback, Data Retention

### 8.6 Operational Readiness
- **Observability:** logs, metrics, traces
- **Alerting:** thresholds and on-call owners
- **Runbooks** for common tasks
- **Deployment and Rollback** strategies
- **Feature Flags** and compatibility

### 8.7 Risk Analysis and Mitigation
- Top 3 Risks, blast radius, kill switches/guardrails

### 8.8 Evaluation and Validation
- Definition of Done (tests, scans)
- Output Validation for format/requirements/safety

### 8.9 Architectural Decision Record (ADR)
- For each significant decision, create an ADR and link it

---

## 9. Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- **Impact:** long-term consequences? (e.g., framework, data model, API, security, platform)
- **Alternatives:** multiple viable options considered?
- **Scope:** cross-cutting and influences system design?

**If ALL true, suggest:**
```
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`
```

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

---

## 10. Project Structure

```
.
├── .specify/
│   ├── memory/
│   │   └── constitution.md          # Project principles
│   ├── templates/                   # PHR and other templates
│   └── scripts/                     # Automation scripts
├── specs/
│   └── <feature>/
│       ├── spec.md                  # Feature requirements
│       ├── plan.md                  # Architecture decisions
│       └── tasks.md                 # Testable tasks with cases
├── history/
│   ├── prompts/                     # Prompt History Records
│   │   ├── constitution/
│   │   ├── <feature-name>/
│   │   └── general/
│   └── adr/                         # Architecture Decision Records
├── AGENTS.md                        # This file (agent behavior rules)
├── CLAUDE.md                        # Lightweight shim for Claude Code
└── README.md                        # Project documentation
```

---

## 11. Code Standards

See `.specify/memory/constitution.md` for detailed code quality, testing, performance, security, and architecture principles.

**Key Standards:**
- **Test-Driven Development (TDD):** Write tests before implementation
- **Type Safety:** Use type annotations (Python, TypeScript)
- **Error Handling:** Explicit error paths, no silent failures
- **Security:** Input validation, no SQL injection, XSS, CSRF
- **Performance:** Measure before optimizing, document trade-offs
- **Documentation:** Self-documenting code, comments only for "why" not "what"

---

## 12. Git Workflow

### Committing Changes
- **Only create commits when requested by the user**
- **Never run destructive git commands** unless explicitly requested
- **Never skip hooks** (--no-verify, --no-gpg-sign)
- **Never force push to main/master**
- **Always create NEW commits** rather than amending (unless explicitly requested)
- **Prefer staging specific files** rather than `git add -A` or `git add .`

### Commit Message Format
```
<type>: <brief summary>

<detailed description if needed>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types:** feat, fix, docs, style, refactor, test, chore

### Pull Requests
- **Title:** Short (under 70 characters)
- **Body:** Summary (1-3 bullets), Test plan (checklist)
- **Footer:** `🤖 Generated with [Claude Code](https://claude.com/claude-code)`

---

## 13. MCP Server Integration

### SpecKitPlus MCP Server
The SpecKitPlus MCP server provides the following commands as MCP prompts:

- `/sp.specify` - Create or update feature specification
- `/sp.plan` - Execute implementation planning workflow
- `/sp.tasks` - Generate actionable, dependency-ordered tasks
- `/sp.implement` - Execute implementation plan
- `/sp.adr` - Create Architectural Decision Records
- `/sp.phr` - Record Prompt History Records
- `/sp.constitution` - Create or update project constitution
- `/sp.clarify` - Identify underspecified areas in spec
- `/sp.analyze` - Cross-artifact consistency analysis
- `/sp.checklist` - Generate custom feature checklist
- `/sp.taskstoissues` - Convert tasks to GitHub issues
- `/sp.git.commit_pr` - Autonomous git workflow execution
- `/sp.reverse-engineer` - Reverse engineer codebase into SDD artifacts

### Usage
Agents should invoke these commands via the MCP interface to ensure all work is tracked and validated against specifications.

---

## 14. Active Technologies

Current project stack (see constitution.md for updates):

- **Backend:** Python 3.13+, FastAPI (planned)
- **Frontend:** TypeScript, Node.js 20+, Next.js 16+, React 19, Tailwind CSS
- **Infrastructure:** Docker, Kubernetes (Minikube), Helm 3+
- **Storage:** In-memory (development), PostgreSQL (planned)
- **Testing:** pytest (Python), Jest/Vitest (TypeScript)
- **CI/CD:** GitHub Actions (planned)

---

## 15. Submission Requirements (Hackathon Context)

This project is being developed for a hackathon with the following submission requirements:

### Required Submissions
1. **Public GitHub Repository** containing:
   - All source code for all completed phases
   - `/specs` folder with all specification files
   - `CLAUDE.md` with Claude Code instructions
   - `AGENTS.md` with agent behavior rules (this file)
   - `README.md` with comprehensive documentation
   - Clear folder structure for each phase

2. **Deployed Application Links:**
   - Phase II: Vercel/frontend URL + Backend API URL
   - Phase III-V: Chatbot URL
   - Phase IV: Instructions for local Minikube setup
   - Phase V: DigitalOcean deployment URL

3. **Demo Video** (maximum 90 seconds):
   - Demonstrate all implemented features
   - Show spec-driven development workflow
   - Judges will only watch the first 90 seconds

4. **WhatsApp Number** for presentation invitation

---

## 16. Agent-Specific Instructions

### For Claude Code
- Read this file (AGENTS.md) via CLAUDE.md shim
- Use MCP tools for all Spec-Kit operations
- Create PHRs after every user interaction
- Suggest ADRs for significant decisions
- Follow TDD: write tests before implementation
- Commit frequently with descriptive messages

### For GitHub Copilot
- Respect existing code patterns and conventions
- Do not suggest code changes outside approved tasks
- Use inline comments to explain complex logic
- Follow type safety and error handling standards

### For Cursor/Other IDEs
- Integrate with SpecKitPlus MCP server if available
- Respect the Spec-Driven Development lifecycle
- Do not bypass specification approval gates
- Use constitution.md for coding standards

---

## 17. Troubleshooting

### Common Issues

**Issue:** Agent wants to write code before spec is approved
**Solution:** Remind agent of SDD lifecycle, require spec approval first

**Issue:** PHR not created after user interaction
**Solution:** Check PHR template exists, verify routing logic, ensure no placeholders remain

**Issue:** ADR auto-created without user consent
**Solution:** Agents must only suggest ADRs, never create them automatically

**Issue:** Code changes unrelated to current task
**Solution:** Enforce "smallest viable diff" policy, reject unrelated refactoring

---

## 18. Version History

- **v1.0.0** (2026-02-06): Initial version with mental model, SDD lifecycle, and MCP integration

---

## 19. Contributing

When updating this file:
1. Maintain backward compatibility with existing agents
2. Update version history with date and changes
3. Test changes with at least one agent (Claude Code recommended)
4. Ensure CLAUDE.md shim still references this file correctly
5. Update constitution.md if coding standards change

---

**Last Updated:** 2026-02-06
**Maintained By:** Project Team
**License:** MIT (or as specified in repository)
