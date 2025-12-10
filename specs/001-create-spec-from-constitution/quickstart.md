# Quickstart Guide: Constitution-Driven Specification Workflow

This guide provides a quick overview of how to initiate and manage a feature development lifecycle using the SpecKit CLI, following the Constitution-Driven Specification Process.

## Prerequisites
- Git installed and configured.
- PowerShell (for Windows environments) or Bash (for Linux/macOS environments) with required scripts in `.specify/scripts/`.
- Access to an AI agent (e.g., Gemini) for content generation (`/sp.implement` phase).
- A project adhering to the Constitution (`.specify/memory/constitution.md`).

## Workflow Steps

### 1. Initiate a New Feature (Specify)
Start every new feature by creating its formal specification.

```bash
/sp.specify "Your natural language description of the feature."
```
- This command will:
    - Create a new Git branch for your feature.
    - Generate `specs/[###-your-feature]/spec.md` with detailed requirements.
    - Generate a `checklists/requirements.md` to validate your spec.

### 2. Plan the Implementation
Once your specification is approved, create a technical plan for its implementation.

```bash
/sp.plan
```
- This command will:
    - Generate `specs/[###-your-feature]/plan.md` outlining the technical context and project structure.
    - Generate a `data-model.md` and `contracts/cli-commands.md` (if applicable).
    - Generate a `quickstart.md` (this file).

### 3. Break Down into Tasks
Translate your plan into a granular, executable task list.

```bash
/sp.tasks
```
- This command will:
    - Generate `specs/[###-your-feature]/tasks.md` with a dependency-ordered list of implementation steps.

### 4. Implement the Feature
Execute the tasks, typically leveraging an AI agent for content or code generation.

```bash
/sp.implement
```
- This command will:
    - Run through the tasks in `tasks.md`.
    - Generate required files (e.g., textbook chapters, code components).
    - Mark tasks as complete.

### 5. Analyze and Validate
Periodically (or after each major phase), analyze your artifacts for consistency and adherence to the constitution.

```bash
/sp.analyze
```
- This command will:
    - Provide a report on inconsistencies, ambiguities, or constitutional violations across your `spec.md`, `plan.md`, and `tasks.md`.

## Important Notes
- Always follow the `specify -> plan -> tasks -> implement` sequence.
- Leverage version control (`git`) for all changes.
- Review generated content and make manual refinements as needed.
