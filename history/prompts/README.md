# Prompt History

This directory contains all prompts used during the development of Physical AI Book project, organized by component area and following SpecKit format.

## Structure

```
history/prompts/
├── backend/          # Backend API endpoints and services
├── frontend/         # Frontend React components and pages
├── general/          # General bug fixes and integrations
└── README.md         # This file
```

## Prompt File Format

All prompts follow the SpecKit format with frontmatter metadata:

```yaml
---
id: 001
title: Feature Name
stage: green
date: 2025-12-12
surface: agent
model: gemini-2.5-flash
feature: feature-name
branch: main
user: user
command: /sp.implement description of what to implement
labels: ["tag1", "tag2"]
links:
  spec: specs/xxx/spec.md (or null)
  plan: specs/xxx/plan.md (or null)
  tasks: specs/xxx/tasks.md (or null)
  adr: null
  pr: null
files:
  - path/to/file1
  - path/to/file2
tests: []
---
```

## Command Format

All prompts use SpecKit commands:
- `/sp.specify` - Create feature specification
- `/sp.plan` - Create implementation plan
- `/sp.tasks` - Generate task list
- `/sp.implement` - Execute implementation
- `/sp.checklist` - Create checklists
- `/sp.analyze` - Analyze artifacts

## Categories

### Backend Prompts
- Authentication system
- Content personalization
- Translation endpoint
- Quiz generation
- Content evaluation
- Database connection fixes
- Error handling improvements

### Frontend Prompts
- Personalize button component
- Chapter integration
- Authentication pages
- UI fixes and styling
- Mobile responsiveness

### General Prompts
- Bug fixes
- Skill integrations
- Cross-cutting concerns

## Development Approach

All development was done through iterative prompts and collaborative coding sessions using SpecKit workflow:
1. Specification (if needed)
2. Planning (if needed)
3. Task generation (if needed)
4. Implementation
5. Testing and refinement

Each prompt documents:
- Original command
- Implementation response
- Outcome and impact
- Files modified
- Next steps
- Reflection and learnings

