# Data Model: Constitution-Driven Specification Process

This document defines the key entities (artifacts) that are managed by the SpecKit workflow for a Constitution-Driven Specification Process.

## Entities

### 1. Specification (spec.md)
- **Description**: A markdown document that formally defines a feature's user stories, functional and non-functional requirements, edge cases, and success criteria. It is the primary input for the planning phase.
- **Attributes**:
    - `Feature Name (string)`: Unique identifier and title for the feature.
    - `Feature Branch (string)`: Git branch associated with the feature.
    - `User Stories (array of objects)`: Prioritized user journeys with acceptance criteria.
    - `Requirements (array of objects)`: Functional and non-functional requirements.
    - `Success Criteria (array of objects)`: Measurable outcomes for the feature.
    - `Status (enum)`: Draft, Approved, Rejected.
- **Relationships**:
    - `One-to-One` with `Plan`: A specification directly informs a single plan.
    - `One-to-Many` with `Tasks`: A specification, via its plan, leads to multiple tasks.

### 2. Plan (plan.md)
- **Description**: A markdown document detailing the technical approach, architecture, technology stack, and project structure required to implement a feature defined by a `spec.md`. It translates abstract requirements into concrete design decisions.
- **Attributes**:
    - `Feature Name (string)`: Matches the associated Specification.
    - `Branch (string)`: Git branch associated with the feature.
    - `Technical Context (object)`: Language, dependencies, storage, testing, platform.
    - `Constitution Check (array of objects)`: Validation gates against project principles.
    - `Project Structure (text)`: Defined file and directory layout.
- **Relationships**:
    - `One-to-One` with `Specification`: Derived from a single specification.
    - `One-to-Many` with `Tasks`: A plan directly informs multiple tasks.

### 3. Tasks (tasks.md)
- **Description**: A markdown document listing granular, executable steps required to implement a feature, organized by user story and with explicit dependencies. It guides the implementation phase.
- **Attributes**:
    - `Feature Name (string)`: Matches the associated Specification and Plan.
    - `Phases (array of objects)`: Setup, Foundational, User Stories (P1, P2, P3...), Polish.
    - `Task Items (array of objects)`: Individual tasks with ID, description, status (checkbox), and file paths.
    - `Dependencies (text)`: Order of execution and parallel opportunities.
- **Relationships**:
    - `Many-to-One` with `Plan`: Multiple tasks are derived from a single plan.
    - `Many-to-One` with `Specification`: Multiple tasks fulfill a single specification.

### 4. Constitution (constitution.md)
- **Description**: A markdown document defining the overarching guiding principles, standards, and governance for the entire project. It acts as the ultimate source of truth for project quality and process.
- **Attributes**:
    - `Project Name (string)`: Overall project identifier.
    - `Constitution Version (string)`: Semantic version of the constitution.
    - `Ratification Date (date)`: Date the constitution was adopted.
    - `Last Amended Date (date)`: Last date of modification.
    - `Principles (array of objects)`: Core rules and their rationale.
    - `Amendment Process (text)`: Guidelines for modifying the constitution.
    - `Compliance (text)`: Rules for validating project artifacts against the constitution.
- **Relationships**:
    - `One-to-Many` with `Specification`, `Plan`, `Tasks`: All project artifacts must adhere to the principles defined in the Constitution.
