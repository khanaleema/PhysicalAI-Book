# Prompt History

This directory contains all prompts used during the development of Physical AI Book project.

## Structure

Each prompt is organized by feature/component area:

- `001-textbook-qa/` - Initial RAG chatbot implementation
- `002-backend-auth/` - User authentication system
- `003-backend-personalization/` - Content personalization endpoint
- `004-backend-translation/` - Translation endpoint
- `005-backend-quiz/` - Quiz generation endpoint
- `006-backend-evaluation/` - Content evaluation endpoint
- `007-backend-database/` - Database connection fixes
- `008-backend-errors/` - Error handling improvements
- `009-frontend-personalize/` - Personalize button component
- `010-frontend-chapter/` - Chapter page integration
- `011-frontend-auth/` - Authentication pages
- `012-frontend-ui/` - UI styling and fixes
- `013-frontend-ui/` - UI theme matching
- `014-general/` - General bug fixes
- `015-general/` - Skill integrations

## Prompt File Naming

Format: `{sequence}-{description}.{stage}.prompt.md`

- `sequence`: 3-digit sequential number
- `description`: Brief description in kebab-case
- `stage`: implementation, spec, plan, tasks, green, etc.

## Metadata Format

Each prompt file includes frontmatter with:
- `id`: Unique identifier
- `title`: Human-readable title
- `stage`: Development stage
- `date_iso`: ISO date (YYYY-MM-DD)
- `model`: AI model used
- `feature`: Feature identifier
- `branch`: Git branch
- `command`: Original user command
- `labels`: Tags for categorization
- `files_yaml`: List of files modified/created
- `tests_yaml`: List of tests

## Development Approach

All development was done through iterative prompts and collaborative coding sessions, documenting each significant change and feature implementation.

