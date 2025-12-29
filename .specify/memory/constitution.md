<!--
Sync Impact Report:
- Version change: Initial creation → 1.0.0
- Modified principles: N/A (initial version)
- Added sections: All sections are newly created
- Removed sections: N/A
- Templates requiring updates:
  ✅ .specify/templates/plan-template.md - Constitution Check section verified
  ✅ .specify/templates/spec-template.md - Requirements alignment verified
  ✅ .specify/templates/tasks-template.md - Task categorization verified
  ⚠ README.md - Not yet created (TODO: Create README explaining spec-driven workflow)
- Follow-up TODOs:
  - Create README.md documenting the spec-driven workflow and AI usage
  - Establish initial git repository if not already done
-->

# The Evolution of Todo — Spec-Driven, Cloud-Native AI Application Constitution

## Core Principles

### I. Spec-Driven Development First

Specifications govern all implementation. No code may be written or modified manually without a corresponding specification. Every feature MUST have:
- A written specification in Markdown format stored in `/specs`
- Clearly defined scope and acceptance criteria
- Explicit boundaries between what is in scope and out of scope

**Rationale**: Specifications serve as the source of truth, ensuring that all stakeholders understand what is being built before implementation begins. This prevents scope creep, reduces rework, and enables AI agents to implement features deterministically.

### II. AI as Implementer, Human as Architect

Claude Code is the primary implementation agent. Humans define requirements, make architectural decisions, and review outputs. AI agents operate under explicit, constrained instructions and MUST NOT invent features outside the active specification.

**Rationale**: This division of labor leverages AI's strength in code generation while preserving human judgment for critical architectural decisions. Ambiguous specifications MUST result in clarification requests, not assumptions.

### III. Deterministic Behavior Across Non-LLM Components

All non-LLM system components MUST exhibit deterministic, predictable behavior. State mutations MUST be explicit, traceable, and reversible where applicable. Side effects (I/O, database operations, events, LLM calls) MUST be isolated from core domain logic.

**Rationale**: Determinism enables reliable testing, debugging, and reasoning about system behavior. Isolating side effects ensures the domain model remains testable and maintainable.

### IV. Evolvability Across Phases Without Breaking Domain Contracts

The domain model MUST remain stable across all project phases (Phases I–V). Domain logic MUST remain independent of:
- UI framework choices
- Transport layer implementations (CLI, HTTP, Chat, Events)
- Deployment environment specifics

**Rationale**: Decoupling domain logic from infrastructure concerns enables the system to evolve without requiring rewrites. Interfaces can change, but core domain contracts must remain stable.

### V. Clear Separation of Domain Logic, Interfaces, and Infrastructure

Architecture MUST maintain strict boundaries between:
- **Domain Logic**: Business rules, entities, and workflows
- **Interfaces**: User-facing or API endpoints (CLI, HTTP, GraphQL, etc.)
- **Infrastructure**: Databases, message queues, external services, cloud resources

**Rationale**: Separation of concerns reduces coupling, improves testability, and enables independent evolution of each layer.

### VI. Reusable Intelligence Over One-Off Solutions

AI-powered features MUST be designed for reusability and explainability. Every AI feature MUST:
- Be explainable (clear inputs, outputs, and reasoning)
- Have predictable tool usage patterns
- Fail safely without corrupting system state
- Operate under explicit constraints defined in specifications

**Rationale**: Reusable AI components reduce development time and increase consistency. Explainability and safe failure modes are critical for production systems where AI behavior must be understood and trusted.

### VII. Infrastructure as Declarative and Reproducible

All infrastructure definitions MUST be declarative, version-controlled, and reproducible. Infrastructure changes MUST be reviewable and auditable.

**Rationale**: Declarative infrastructure (e.g., Terraform, CloudFormation, Kubernetes manifests) ensures environments can be recreated consistently, supports disaster recovery, and enables code review of infrastructure changes.

## Specification Standards

### Specification Requirements

All features MUST have specifications created BEFORE implementation begins. Each specification MUST include:
- **User Scenarios**: Prioritized user journeys with acceptance criteria (Given-When-Then format)
- **Functional Requirements**: Explicit, testable requirements with clear identifiers (FR-001, FR-002, etc.)
- **Key Entities**: Data models and their relationships (when applicable)
- **Success Criteria**: Measurable outcomes that define feature completion
- **Edge Cases**: Boundary conditions and error scenarios

### Specification Versioning

Specifications MUST be versioned and stored in `/specs/<feature-name>/`. Each phase MUST have its own spec folder structure:
- `spec.md` — Feature requirements and user scenarios
- `plan.md` — Architecture decisions and technical approach
- `tasks.md` — Testable implementation tasks
- `research.md` — Phase 0 research outputs (optional)
- `data-model.md` — Entity definitions (optional)
- `contracts/` — API contracts and interfaces (optional)

### Specification Compliance

Incorrect behavior MUST be fixed by refining the specification, not by directly editing code. If implementation deviates from spec, the spec takes precedence unless the spec itself is found to be incorrect.

## Repository Standards

### Repository Structure

The repository MUST clearly reflect:
- **Constitution**: `.specify/memory/constitution.md`
- **Specifications History**: `/specs/<feature>/`
- **Generated Source Code**: `/src/` or language-specific convention
- **Deployment Artifacts**: Infrastructure definitions, CI/CD configs
- **Prompt History Records**: `history/prompts/` (constitution, feature-specific, general)
- **Architecture Decision Records**: `history/adr/`

### Documentation Requirements

The README MUST explain:
- The spec-driven development workflow used in this project
- How AI (Claude Code) was used for implementation
- How the system evolved across phases
- How to contribute following the spec-driven process

## AI Usage Standards

### AI Agent Constraints

- **Primary Agent**: Claude Code is the primary implementation agent
- **Specialized Agents**: OpenAI Agents SDK and MCP SDK are used only where explicitly specified in feature specs
- **No Feature Invention**: AI agents MUST NOT invent features, APIs, or data models outside the active specification
- **Clarification Requirement**: Ambiguous specifications MUST result in clarification requests to the human architect

### AI Feature Requirements

AI-powered features MUST:
- **Be Explainable**: Clear documentation of inputs, outputs, and decision logic
- **Have Predictable Tool Usage**: Defined set of tools/APIs the AI can invoke
- **Fail Safely**: Graceful degradation without corrupting application state
- **Operate Under Constraints**: Explicit guardrails defined in feature specifications

## Architecture Standards

### State Management

State mutations MUST be:
- **Explicit**: No hidden side effects
- **Traceable**: Auditable through logs or event sourcing
- **Reversible**: Support undo/rollback where applicable

### Error Handling

The system MUST define:
- **Error Taxonomy**: Categorized error types with status codes
- **Error Boundaries**: Clear failure isolation points
- **Degradation Strategy**: Graceful handling when dependencies fail

### Testing Requirements

While Test-Driven Development (TDD) is encouraged, tests are OPTIONAL unless explicitly requested in the feature specification. When tests are required:
- Tests MUST be written BEFORE implementation
- Tests MUST fail initially (Red-Green-Refactor cycle)
- Test types include: contract tests, integration tests, unit tests

### Performance and Scalability

Non-functional requirements (NFRs) MUST be defined in specifications:
- **Performance**: p95 latency targets, throughput requirements
- **Reliability**: SLOs, error budgets, degradation strategies
- **Security**: AuthN/AuthZ mechanisms, data handling, secrets management
- **Cost**: Unit economics and resource budgets

## Governance

### Amendment Procedure

This Constitution MUST be amended through the `/sp.constitution` command. All amendments MUST:
- Document the rationale for changes
- Update the version number according to semantic versioning
- Include a Sync Impact Report listing affected templates and documents
- Receive approval from the project architect before finalization

### Versioning Policy

Constitution versions follow semantic versioning:
- **MAJOR**: Backward-incompatible governance changes or principle removals/redefinitions
- **MINOR**: New principles/sections added or materially expanded guidance
- **PATCH**: Clarifications, wording improvements, non-semantic refinements

### Compliance Review

All implementations MUST verify compliance with this Constitution. Pull requests and code reviews MUST check:
- Specification exists and is complete before implementation
- Domain logic is independent of infrastructure
- AI features operate within defined constraints
- Infrastructure changes are declarative and reproducible

### Complexity Justification

Any violation of constitutional principles (e.g., adding complexity beyond simplicity guidelines) MUST be explicitly justified in the implementation plan with documentation of:
- Why the violation is necessary
- What simpler alternatives were considered and rejected
- What the long-term maintenance implications are

### Runtime Development Guidance

Developers and AI agents MUST refer to `CLAUDE.md` for runtime development guidance, including:
- Prompt History Record (PHR) creation workflows
- Architecture Decision Record (ADR) suggestion criteria
- Execution contracts and acceptance criteria
- Human-as-tool invocation triggers

**Version**: 1.0.0 | **Ratified**: 2025-12-28 | **Last Amended**: 2025-12-28
