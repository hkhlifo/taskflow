# TaskFlow

TaskFlow is a collaborative task management platform built as a production-style internship assignment.

It allows authenticated users to create tasks, assign them to other users, track task status, and receive email notifications when tasks are assigned and completed.

## Features

- Google OAuth 2.0 authentication
- Secure authenticated REST API
- Create and manage tasks
- Assign tasks to other registered users
- Task priorities and statuses
- Task completion tracking
- Gmail notification when a task is assigned
- Gmail notification when a task is completed
- Supabase PostgreSQL database
- Profile creation through Supabase Auth
- Protected backend API endpoints
- Production-ready frontend/backend architecture

## Tech Stack

### Frontend
- Next.js
- TypeScript
- Tailwind CSS
- Supabase Auth

### Backend
- Python
- Flask
- Flask-CORS
- Supabase Python client

### Database & Authentication
- Supabase PostgreSQL
- Supabase Auth
- Google OAuth 2.0

### Email
- Gmail SMTP
- Gmail App Password

### Deployment
- Vercel
- Render

## Architecture

The application follows a frontend/backend architecture:

```text
                    ┌─────────────────────┐
                    │       Browser       │
                    └──────────┬──────────┘
                               │
                               │
                    ┌──────────▼──────────┐
                    │ Next.js + TypeScript│
                    │      Frontend       │
                    └──────────┬──────────┘
                               │
                         REST API + JWT
                               │
                    ┌──────────▼──────────┐
                    │       Flask         │
                    │       Backend       │
                    └──────┬───────┬──────┘
                           │       │
                  ┌────────▼───┐   │
                  │  Supabase  │   │
                  │ PostgreSQL │   │
                  └────────────┘   │
                                   │
                              ┌────▼────┐
                              │  Gmail  │
                              │  SMTP   │
                              └─────────┘
````

## Authentication Flow

1. User selects **Continue with Google**.
2. Supabase Auth handles Google OAuth.
3. Supabase creates an authenticated session.
4. The frontend obtains the user's access token.
5. The access token is sent to the Flask API using the `Authorization: Bearer <token>` header.
6. Flask validates the token through Supabase.
7. Authenticated API operations are then performed for the current user.

## Task Flow

1. An authenticated user creates a task.
2. The task is stored in Supabase PostgreSQL.
3. The creator can assign the task to another registered user.
4. The assigned user receives a Gmail notification.
5. The assigned user can update the task status.
6. When the task is completed, the task creator receives a Gmail notification.

## Database

The database is organized into the following tables:

### `profiles`

Stores application user profile information linked to Supabase Auth users.

### `tasks`

Stores task information including:

* Title
* Description
* Status
* Priority
* Creator
* Assignee
* Due date
* Completion timestamp
* Created/updated timestamps

### `task_activity`

Stores task-related activity records.

### `email_notifications`

Stores email notification records and their delivery status.

Database migrations are maintained in:

```text
/migrations
```

## API Overview

### Authentication

```text
GET /api/auth/me
```

Returns the currently authenticated user's profile.

### Users

```text
GET /api/users
GET /api/users/search?q=<query>
```

Retrieves registered users for task assignment.

### Tasks

```text
GET    /api/tasks
POST   /api/tasks
PATCH  /api/tasks/:id
DELETE /api/tasks/:id
```

These endpoints allow authenticated users to retrieve, create, update, and delete tasks according to the application's authorization rules.

## Project Structure

```text
taskflow/
├── frontend/
│   ├── src/
│   └── ...
├── backend/
│   ├── app/
│   └── ...
├── migrations/
│   ├── 001_create_profiles.sql
│   ├── 002_create_tasks.sql
│   ├── 003_create_task_activity.sql
│   ├── 004_create_email_notifications.sql
│   ├── 005_create_indexes.sql
│   └── 006_create_profile_trigger.sql
├── docs/
├── .env.example
├── .gitignore
└── README.md
```

## Environment Variables

Create the required environment variables locally.

### Frontend

```env
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=
```

### Backend

```env
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=

GMAIL_USER=
GMAIL_APP_PASSWORD=

FRONTEND_URL=
```

Never commit real credentials or secret keys to GitHub.

Use `.env.example` as a reference for the required configuration.

## Local Development

### 1. Clone the repository

```bash
git clone <repository-url>
cd taskflow
```

### 2. Start the backend

```bash
cd backend

python -m venv venv
```

Activate the virtual environment.

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the backend environment variables and start Flask:

```bash
python run.py
```

The backend runs locally on:

```text
http://localhost:5000
```

### 3. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs locally on:

```text
http://localhost:3000
```

## Google OAuth Configuration

Google OAuth is configured through Supabase Auth.

The OAuth redirect URL must be configured in the Supabase project and Google Cloud OAuth configuration for the relevant environment.

For local development:

```text
http://localhost:3000/auth/callback
```

Production deployments should use the deployed frontend callback URL.

## Email Notifications

TaskFlow uses Gmail SMTP to send notification emails.

A Gmail App Password is used instead of storing a regular Gmail account password.

Emails are triggered for:

* New task assignment
* Task completion

The Gmail credentials are kept exclusively on the backend and are never exposed to the frontend.

## Security Considerations

* Authentication is handled through Supabase Auth and Google OAuth.
* Backend endpoints require a valid Supabase access token.
* Server-side Supabase credentials are never exposed to the frontend.
* Gmail credentials are stored only in backend environment variables.
* Environment files containing secrets are excluded from Git.
* Task operations enforce authorization based on the authenticated user.

## Deployment

The intended production architecture is:

```text
Frontend → Vercel
Backend  → Render
Database → Supabase
Email    → Gmail SMTP
```

Environment variables must be configured separately in the respective deployment platforms.

## Future Improvements

Possible production improvements include:

* Background job processing for email delivery
* Retry handling for failed emails
* Real-time task updates
* Rich task activity timeline
* Pagination and filtering
* Automated testing
* CI/CD pipeline
* More granular role-based permissions

---
