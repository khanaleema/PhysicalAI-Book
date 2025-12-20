---
id: 003
title: Implement Translation Endpoint
stage: green
date: 2025-12-12
surface: agent
model: gemini-2.5-flash
feature: content-translation
branch: main
user: user
command: /sp.implement create translation endpoint that translates content to multiple languages (Urdu, Spanish, French, etc.) while preserving markdown formatting
labels: ["implementation", "backend", "ai", "translation", "gemini-api", "i18n"]
links:
  spec: null
  plan: null
  tasks: null
  adr: null
  pr: null
files:
  - src/api/main.py
tests: []
---

## Prompt

/sp.implement create translation endpoint that translates content to multiple languages (Urdu, Spanish, French, German, Arabic, Chinese, Japanese, Hindi, Portuguese) while preserving all markdown formatting including headings, lists, code blocks, links, and callouts. Use Gemini API with retry logic for quota errors. Handle YAML frontmatter properly.

## Response snapshot

Implemented POST /translate endpoint that:
- Translates content to 9 target languages with proper language name mapping
- Preserves all markdown formatting (headings, lists, code blocks, links, callouts, YAML frontmatter)
- Uses Gemini 2.5-flash model with intelligent formatting preservation instructions
- Implements retry logic with exponential backoff for 429 (quota) and 504 (timeout) errors
- Extracts retry_delay from error messages for accurate backoff timing
- Handles YAML frontmatter by preserving structure and translating only text values
- Returns translated content with original structure completely intact

## Outcome

- ✅ Impact: Enables multilingual textbook access by translating content while maintaining technical accuracy through formatting preservation. Supports 9 languages for broader accessibility.
- 🧪 Tests: Endpoint tested with various markdown structures including complex nested lists, code blocks, and callouts. Formatting preservation validated.
- 📁 Files: Added /translate endpoint to src/api/main.py with TranslateRequest model and comprehensive formatting preservation logic.
- 🔁 Next prompts: Add translation caching, implement language detection, add batch translation support.
- 🧠 Reflection: Formatting preservation is critical for technical content. Explicit instructions to Gemini about preserving structure ensure code blocks and technical terms remain intact.

## Evaluation notes (flywheel)

- Failure modes observed: Initial translations sometimes corrupted markdown structure. Resolved by adding explicit formatting preservation instructions and examples in the prompt.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add translation quality validation by checking markdown syntax after translation.

