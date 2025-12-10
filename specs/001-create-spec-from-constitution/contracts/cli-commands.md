# CLI Command Contracts: SpecKit Workflow

This document defines the functional contracts for the core SpecKit CLI commands (`/sp.*`) that orchestrate the Constitution-Driven Specification Process. Each command serves as an endpoint in the development workflow, taking specific inputs and producing defined outputs.

## 1. `/sp.specify`
- **Description**: Creates or updates a feature specification (`spec.md`) from a natural language description.
- **Method**: CLI Command
- **Inputs**:
    - `ARGUMENTS (string)`: Natural language feature description.
- **Outputs**:
    - `feature_branch (string)`: New Git branch name (`[###-feature-name]`).
    - `spec_file_path (string)`: Absolute path to the generated `spec.md`.
    - `checklist_file_path (string)`: Absolute path to the generated `requirements.md` checklist.
    - `status (enum)`: Success | Failure.
- **Preconditions**:
    - Must be executed in a Git repository.
    - User must provide a feature description.
- **Postconditions**:
    - A new Git branch for the feature is created and checked out.
    - A `specs/[###-feature-name]/` directory is created.
    - A `spec.md` and `checklists/requirements.md` are created within the feature directory.

## 2. `/sp.plan`
- **Description**: Generates an implementation plan (`plan.md`) based on an existing feature specification.
- **Method**: CLI Command
- **Inputs**:
    - None (operates on the current feature's `spec.md`).
- **Outputs**:
    - `plan_file_path (string)`: Absolute path to the generated `plan.md`.
    - `data_model_file_path (string)`: Absolute path to `data-model.md` (if generated).
    - `contracts_dir (string)`: Path to the `contracts/` directory (if generated).
    - `quickstart_file_path (string)`: Absolute path to `quickstart.md` (if generated).
    - `status (enum)`: Success | Failure.
- **Preconditions**:
    - A valid `spec.md` must exist for the current feature.
    - Must be executed on the feature branch.
- **Postconditions**:
    - `plan.md` is created/updated in the feature directory.
    - `data-model.md`, `contracts/cli-commands.md`, `quickstart.md` are created/updated (if applicable).

## 3. `/sp.tasks`
- **Description**: Generates an actionable, dependency-ordered task list (`tasks.md`) from an implementation plan.
- **Method**: CLI Command
- **Inputs**:
    - None (operates on the current feature's `plan.md`).
- **Outputs**:
    - `tasks_file_path (string)`: Absolute path to the generated `tasks.md`.
    - `status (enum)`: Success | Failure.
- **Preconditions**:
    - A valid `plan.md` must exist for the current feature.
    - Must be executed on the feature branch.
- **Postconditions**:
    - `tasks.md` is created/updated in the feature directory.

## 4. `/sp.implement`
- **Description**: Executes implementation tasks, typically using an AI agent to generate code or content, based on the `tasks.md`.
- **Method**: CLI Command
- **Inputs**:
    - None (operates on the current feature's `tasks.md`).
- **Outputs**:
    - `implemented_files (array of string)`: List of paths to files created/modified during implementation.
    - `status (enum)`: Success | Failure.
- **Preconditions**:
    - A valid `tasks.md` must exist for the current feature.
    - AI agent configuration must be available.
- **Postconditions**:
    - Files are created/modified on the filesystem as per the tasks.
    - Tasks in `tasks.md` are marked as complete.
