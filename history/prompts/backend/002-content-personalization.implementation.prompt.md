---
id: 002
title: Implement Content Personalization Endpoint
stage: green
date: 2025-12-12
surface: agent
model: gemini-2.5-flash
feature: content-personalization
branch: main
user: user
command: /sp.implement create content personalization endpoint that adapts textbook content based on user learning level (Beginner/Intermediate/Advanced) using Gemini API
labels: ["implementation", "backend", "ai", "personalization", "gemini-api"]
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

/sp.implement create content personalization endpoint that adapts textbook content based on user learning level (Beginner/Intermediate/Advanced) using Gemini API. Truncate content to 4000 characters at paragraph boundaries to avoid timeouts. Implement retry logic with exponential backoff for quota errors (429) and timeout errors (504). Use temperature 0.3 and max_output_tokens 6000 for faster, consistent generation.

## Response snapshot

Implemented POST /personalize endpoint that:
- Accepts content, chapterPath, and userLevel (Beginner/Intermediate/Advanced)
- Uses Gemini 2.5-flash model for content adaptation
- Truncates content to 4000 characters at paragraph boundaries to prevent timeouts
- Implements retry logic with exponential backoff for 429 (quota) and 504 (timeout) errors
- Extracts retry_delay from error messages for accurate backoff timing
- Uses temperature 0.3 and max_output_tokens 6000 for faster generation
- Returns personalized content optimized for user's learning level

## Outcome

- ✅ Impact: Enables personalized learning experience by adapting content complexity based on user level. Content truncation prevents timeouts, retry logic handles quota limits gracefully.
- 🧪 Tests: Endpoint tested with various content lengths and user levels. Retry logic validated with simulated quota errors.
- 📁 Files: Added /personalize endpoint to src/api/main.py with PersonalizeRequest model and comprehensive error handling.
- 🔁 Next prompts: Add content caching for personalized content, implement user preference persistence, add content revert functionality.
- 🧠 Reflection: Content truncation to 4000 characters significantly reduces timeout errors. Retry logic with extracted delay times provides better user experience during quota limits.

## Evaluation notes (flywheel)

- Failure modes observed: Initial timeout errors (504) due to large content sizes. Resolved by implementing smart truncation at paragraph boundaries and reducing max_output_tokens.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Implement content chunking for very long chapters, allowing progressive personalization.

