---
title: Physical AI Book Backend API
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Physical AI Book Backend API

FastAPI backend for the Physical AI & Humanoid Robotics book.

## Features

- 🔐 Authentication (Sign up, Sign in, Password reset)
- 🎯 Content Personalization
- 🌐 Translation (English to Urdu)
- 💬 RAG-based Chatbot

## API Endpoints

- `POST /auth/sign-up` - User registration
- `POST /auth/sign-in` - User login
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password
- `POST /personalize` - Personalize content
- `POST /translate` - Translate content
- `POST /query` - Chatbot query
- `GET /health` - Health check

## Environment Variables

Set these in Hugging Face Space Settings → Variables:

- `GROQ_API_KEY`: Your Groq API key
- `AUTH_SECRET_KEY`: Secret key for JWT tokens
- `CORS_ORIGINS`: Comma-separated list of allowed origins (e.g., `https://yourusername.github.io`)

## Local Development

```bash
pip install -r requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```
