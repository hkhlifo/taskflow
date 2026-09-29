# TaskFlow

TaskFlow is a collaborative task management platform built as a production-style internship assignment.

## Tech Stack

- Next.js
- TypeScript
- Flask
- Supabase PostgreSQL
- Supabase Auth
- Google OAuth 2.0
- Gmail
- Vercel
- Render

## Architecture

The application follows a frontend/backend architecture:

```text
Next.js + TypeScript
        |
        | REST API
        v
      Flask
        |
        +------> Supabase PostgreSQL
        |
        +------> Gmail


Project Structure
taskflow/
├── frontend/
├── backend/
├── migrations/
├── docs/
├── .env.example
└── README.md
