---

description: "Task list for Constitution-Driven Specification Process"
---

# Tasks: Constitution-Driven Specification Process

**Input**: Design documents from `specs/001-create-spec-from-constitution/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/cli-commands.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume CLI tool - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initial project setup and task file creation

- [X] T001 Create initial `tasks.md` file in `specs/001-create-spec-from-constitution/tasks.md`
- [X] T002 (P) Ensure base project structure for the feature is in place (`specs/001-create-spec-from-constitution/`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented, focusing on robust workflow control and validation.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Implement `check_spec_exists(feature_dir)` utility function for `spec.md` existence and validity checks.
- [X] T004 Implement `check_plan_exists(feature_dir)` utility function for `plan.md` existence and validity checks.
- [X] T005 Implement `check_tasks_exists(feature_dir)` utility function for `tasks.md` existence and validity checks.
- [X] T006 Integrate `constitution.md` loading and parsing into a `get_constitution()` utility function.
- [X] T007 Develop a `validate_against_constitution(artifact_path)` utility function that applies constitutional rules to an artifact.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Enforce Spec-Driven Development (P1) 🎯 MVP

**Goal**: Ensure commands (`/sp.plan`, `/sp.tasks`, `/sp.implement`) warn or error if prerequisite `spec.md`, `plan.md`, or `tasks.md` are missing/invalid.

**Independent Test**:
- Running `/sp.plan` without a valid `spec.md` results in an error.
- Running `/sp.tasks` without a valid `plan.md` results in an error.
- Running `/sp.implement` without a valid `tasks.md` results in an error.

### Implementation for User Story 1

- [X] T008 [US1] Modify `.gemini/commands/sp.plan.toml` to call `check_spec_exists()` before execution and return error if it fails.
- [X] T009 [US1] Modify `.gemini/commands/sp.tasks.toml` to call `check_plan_exists()` before execution and return error if it fails.
- [X] T010 [US1] Modify `.gemini/commands/sp.implement.toml` to call `check_tasks_exists()` before execution and return error if it fails.
- [X] T011 [US1] Update `setup-plan.ps1` to include checks for `spec.md` before copying template.
- [X] T012 [US1] Implement clear, actionable error messages for prerequisite failures in `sp.*` commands.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Ensure AI-Native Workflow (P2)

**Goal**: Extend `/sp.implement` to parse tasks and orchestrate AI-driven content generation.

**Independent Test**: `/sp.implement` successfully uses an AI agent to generate content based on tasks.

### Implementation for User Story 2

- [X] T013 [US2] Modify `.gemini/commands/sp.implement.toml` to include logic for parsing `tasks.md`.
- [X] T014 [US2] Develop an `invoke_ai_agent(task_description)` function in a new PowerShell module `.\.specify\scripts\powershell\ai_agent_utils.psm1`.
- [X] T015 [US2] Implement logic in `/sp.implement` to iterate over AI-generative tasks and call `invoke_ai_agent()`.
- [X] T016 [P] [US2] Define structured JSON input/output schemas for `invoke_ai_agent()` in `specs/001-create-spec-from-constitution/contracts/ai_agent_interface.json`.
- [X] T017 [US2] Implement robust error handling and retry mechanisms for AI agent communication in `ai_agent_utils.psm1`.
- [X] T018 [US2] Implement logic to mark tasks as complete in `tasks.md` after successful AI generation.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Validate Artifact Quality (P2)

**Goal**: Implement `/sp.analyze` to verify artifacts against defined criteria, including constitutional principles and measurable metrics.

**Independent Test**: `/sp.analyze` identifies vague success criteria in `spec.md` or constitutional violations in `plan.md`.

### Implementation for User Story 3

- [X] T019 [US3] Create new command definition file: `.gemini/commands/sp.analyze.toml`.
- [X] T020 [US3] Develop a new PowerShell script `.\.specify\scripts\powershell\analyze_artifacts.ps1` to be called by `/sp.analyze`.
- [X] T021 [US3] Implement logic in `analyze_artifacts.ps1` to load `spec.md`, `plan.md`, `tasks.md`, and `constitution.md`.
- [X] T022 [US3] Integrate `validate_against_constitution()` from Foundational phase into `analyze_artifacts.ps1`.
- [X] T023 [P] [US3] Implement detection of vague success criteria (e.g., "fast", "scalable") in `spec.md` and report them.
- [X] T024 [P] [US3] Implement detection of constitutional principle violations in `plan.md` and report them.
- [X] T025 [US3] Generate a structured markdown analysis report in `specs/001-create-spec-from-constitution/analysis_report.md`.

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and overall system quality.

- [X] T026 Update `GEMINI.md` to reflect new capabilities and recommended workflow (including `/sp.analyze`).
- [X] T027 Refactor common functions (`check_spec_exists`, `check_plan_exists`, `check_tasks_exists`, `get_constitution`, `validate_against_constitution`) into a shared PowerShell module (e.g., `.\.specify\scripts\powershell\spec_kit_utils.psm1`).
- [X] T028 Ensure all error messages are consistent, clear, and actionable.
- [X] T029 Add basic logging to `sp.*` commands for traceability and debugging.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phases 3-5)**: All depend on Foundational phase completion.
  - US1 (P1) is MVP and can proceed first.
  - US2 (P2) and US3 (P2) can proceed in parallel after US1, or sequentially by priority.
- **Polish (Phase 6)**: Depends on all desired user stories being functionally complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independent of US2 and US3 implementation, but US2 and US3 will rely on its established checks.
- **User Story 2 (P2)**: Relies on US1's command validity checks.
- **User Story 3 (P2)**: Relies on US1's command validity checks.

### Within Each User Story

- Utility functions should be implemented before their integration into commands.
- Command definitions (`.toml` files) should be updated after the underlying script logic is ready.

### Parallel Opportunities

- Tasks marked with `[P]` can be executed in parallel.
- Phases 3, 4, and 5 can be worked on by different developers once Phase 2 is complete.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1.  Complete Phase 1: Setup
2.  Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3.  Complete Phase 3: User Story 1
4.  **STOP and VALIDATE**: Test User Story 1 independently by trying to run `/sp.plan`, `/sp.tasks`, `/sp.implement` with missing prerequisite files.

### Incremental Delivery

1.  Complete Setup + Foundational → Foundation ready.
2.  Add User Story 1 → Test independently → Deploy/Demo (MVP for workflow enforcement!).
3.  Add User Story 2 → Test independently → Deploy/Demo.
4.  Add User Story 3 → Test independently → Deploy/Demo.
5.  Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1.  Team completes Setup + Foundational together.
2.  Once Foundational is done:
    - Developer A: User Story 1
    - Developer B: User Story 2
    - Developer C: User Story 3
3.  Stories complete and integrate independently.

---

## Notes

- `[P]` tasks = different files, no dependencies
- `[Story]` label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (where applicable)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
