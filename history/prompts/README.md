# Prompt History - SpecKit Plus Workflow

This directory contains all prompts used during the development of Physical AI Book project, following **SpecKit Plus** format and workflow.

## SpecKit Plus Workflow

SpecKit Plus follows a structured **Spec-Driven Development** methodology:

```
/sp.constitution → /sp.specify → /sp.plan → /sp.tasks → /sp.implement
```

### Optional Commands
- `/sp.clarify` - Clarify underspecified areas (before /sp.plan)
- `/sp.analyze` - Cross-artifact consistency analysis (after /sp.tasks)
- `/sp.checklist` - Generate quality checklists

## Structure

```
history/prompts/
├── backend/          # Backend implementation prompts (stage: green)
├── frontend/         # Frontend implementation prompts (stage: green)
├── general/          # General implementation prompts (stage: green)
├── 001-textbook-qa/  # Complete workflow: spec → plan → tasks → implement
├── physical-ai-book/ # Docusaurus setup implementation prompts
└── README.md
```

## Prompt Stages

Prompts are organized by **stage** (not just implementation):

| Stage | Command | Purpose | Example |
|-------|---------|---------|---------|
| `constitution` | `/sp.constitution` | Create project principles | Project governance rules |
| `spec` | `/sp.specify` | Define requirements | User stories, functional requirements |
| `plan` | `/sp.plan` | Technical implementation plan | Tech stack, architecture |
| `tasks` | `/sp.tasks` | Generate task breakdown | Actionable task list |
| `green` | `/sp.implement` | Execute implementation | Code implementation |
| `clarify` | `/sp.clarify` | Clarify requirements | Questions and answers |
| `analyze` | `/sp.analyze` | Analyze artifacts | Consistency checks |
| `checklist` | `/sp.checklist` | Generate checklists | Quality validation |

## Prompt File Format

All prompts follow SpecKit Plus format with frontmatter metadata:

```yaml
---
id: 001
title: Feature Name
stage: green  # or: spec, plan, tasks, clarify, analyze, checklist
date: 2025-12-12
surface: agent
model: gemini-2.5-flash
feature: feature-name
branch: main
user: user
command: /sp.implement description
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

## File Naming Convention

Format: `{sequence}-{description}.{stage}.prompt.md`

Examples:
- `001-create-textbook-qa-spec.spec.prompt.md` - Specification stage
- `002-create-textbook-qa-plan.plan.prompt.md` - Planning stage
- `003-create-textbook-qa-tasks.tasks.prompt.md` - Tasks stage
- `004-implement-textbook-qa-bot.green.prompt.md` - Implementation stage (green)

## Categories

### Backend Prompts (7 implementation)
- User authentication system
- Content personalization endpoint
- Translation endpoint
- Quiz generation endpoint
- Content evaluation endpoint
- Database connection fixes
- Gemini API error handling

### Frontend Prompts (5 implementation)
- Personalize button component
- Chapter personalization integration
- Authentication pages
- Mobile sidebar fixes
- UI theme matching

### General Prompts (5 implementation)
- Profile navigation and token fixes
- Gemini skills integration
- Content truncation optimization
- Retry logic implementation
- localStorage content caching

### Complete Workflows
- `001-textbook-qa/` - Full SpecKit Plus workflow:
  - `001-create-textbook-qa-spec.spec.prompt.md` - Specification
  - `002-create-textbook-qa-plan.plan.prompt.md` - Implementation plan
  - `003-create-textbook-qa-tasks.tasks.prompt.md` - Task breakdown
  - `004-implement-textbook-qa-bot.green.prompt.md` - Implementation

## SpecKit Plus Philosophy

**Spec-Driven Development** emphasizes:
- **Intent-driven**: Specifications define "what" before "how"
- **Rich specifications**: Guardrails and organizational principles
- **Multi-step refinement**: Not one-shot code generation
- **AI-native**: Leverage advanced AI model capabilities

## Development Approach

All development follows **SpecKit Plus workflow**:

1. **Constitution** (`/sp.constitution`) - Establish principles
2. **Specify** (`/sp.specify`) - Define requirements
3. **Plan** (`/sp.plan`) - Technical architecture
4. **Tasks** (`/sp.tasks`) - Task breakdown
5. **Implement** (`/sp.implement`) - Execute code

Each prompt documents:
- Original SpecKit Plus command
- Implementation/response
- Outcome and impact
- Files modified
- Next steps
- Reflection and learnings

## References

- [SpecKit Plus Repository](https://github.com/panaversity/spec-kit-plus)
- [Spec-Driven Development Guide](https://github.com/panaversity/spec-kit-plus#-what-is-spec-driven-development)
- [SpecifyPlus CLI Documentation](https://github.com/panaversity/spec-kit-plus#-specify-cli-reference)
