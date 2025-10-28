# AI4D — Backend for Adaptive AI Learning Platform

This repository contains the backend code for AI4D, a personalized, gamified learning platform focused on AI and data engineering. It provides question generation, user profiling, assessment handling, and profile generation using LLMs and fallback logic. This project is intended as part of a memory/thesis project and is structured for local development and deployment.

## Table of contents

- Project overview
- Key features
- Architecture overview
- Requirements
- Environment variables
- Quickstart (development)
- Running services and workers
- Streamlit frontend (local)
- Running tests
- Security and best practices
- How profiling and LLM calls work
- Recommendations and TODOs
- Contributing
- License
- Contact


## Project overview

AI4D backend implements APIs and background tasks to:

- Generate quizzes and personalized questions for users (via LLM or fallback).
- Collect user answers and compute scores.
- Analyze quiz results to generate a learning profile (profile analysis task).
- Persist profiles and activity history (MongoDB + PostgreSQL usage in project).
- Run asynchronous tasks using Celery (Redis broker and backend).
- Expose an authenticated API for the Streamlit frontend and other clients.

The repository contains code in `src/`, Celery tasks in `src/celery_tasks.py`, profile logic in `src/profile/`, and a Streamlit demo app in `streamlit_app/`.


## Key features

- Question generation pipeline using an LLM with robust fallback when the LLM or its credentials are unavailable.
- Celery-based asynchronous tasks for long-running operations (question generation, profile analysis).
- MongoDB for profile and activity storage and Redis for Celery broker/results.
- Email utilities for account verification and notifications.
- Streamlit-based demo frontend (for rapid testing and demos).
- Config-driven environment management via a `.env` file and `pydantic-settings`.


## Architecture overview

- API server (FastAPI or equivalent) — exposes `/api/profile/v1` and `/api/auth/v1` endpoints.
- Background workers (Celery) — run `generate_profile_question_task` and `profile_analysis_task`.
- LLM integration — calls to an LLM endpoint (local or OpenAI) with fallback profile logic.
- Datastores — Redis (broker/results) and MongoDB (profiles), PostgreSQL for core app data.
- Frontend — a Streamlit app under `streamlit_app/` used for manual testing and demos.


## Requirements

- Python 3.11+ (project used Python 3.12 in development; use compatible Python in your environment)
- Redis (local or Docker)
- MongoDB (local or Docker)
- PostgreSQL (if you use DB features; migrations present under `migrations/`)
- Optional: an LLM endpoint (OpenAI or local LLM) and an API key if using OpenAI


## Environment variables

Create a `.env` file at the project root (the `Settings` class loads it). At minimum provide the following:

- DATABASE_URL - your PostgreSQL URL (if used)
- JWT_SECRET - secret used for JWT token signing
- JWT_ALGORITHM - (optional) default HS256
- REDIS_HOST, REDIS_PORT, REDIS_DB or REDIS_URL
- MONGO_ROOT_USERNAME, MONGO_ROOT_PASSWORD
- MONGO_APP_USERNAME, MONGO_APP_PASSWORD
- MONGO_DATABASE, MONGO_HOST, MONGO_PORT
- DOMAIN - public domain or localhost used for email links
- MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_PORT, MAIL_SERVER, MAIL_FROM_NAME
- MAIL_STARTTLS, MAIL_SSL_TLS, USE_CREDENTIALS, VALIDATE_CERTS
- OPENAI_API_KEY - required if you call OpenAI; otherwise ensure your local LLM endpoint is reachable

Example (.env):

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/ai4d
JWT_SECRET=replace-with-secure-secret
REDIS_URL=redis://localhost:6379/0
MONGO_ROOT_USERNAME=root
MONGO_ROOT_PASSWORD=change-me
MONGO_APP_USERNAME=ai4d
MONGO_APP_PASSWORD=change-me
MONGO_DATABASE=ai4d_db
MONGO_HOST=localhost
MONGO_PORT=27017
DOMAIN=http://localhost:8000
MAIL_USERNAME=your@email
MAIL_PASSWORD=your-email-password
MAIL_FROM=your@email
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME="AI4D Support"
MAIL_STARTTLS=true
MAIL_SSL_TLS=false
USE_CREDENTIALS=true
VALIDATE_CERTS=true
OPENAI_API_KEY=sk-...
```

Security note: Never commit your `.env` or secrets into source control.


## Quickstart (development)

1. Clone and enter the repository

```bash
cd /Users/smallziz/Documents/project\ ai4d/backend_ai4_d
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Ensure Redis and MongoDB are running. You may use Docker or your local installs. Example using Docker Compose (if you have `docker-compose.yml` configured):

```bash
docker-compose up -d redis mongo postgres
```

3. Create `.env` with the required variables.

4. Run database migrations (if you use PostgreSQL migrations present in `migrations/`):

```bash
alembic upgrade head
```

5. Start the API server (example using uvicorn):

```bash
uvicorn src.main:app --reload --port 8000
```

6. Start a Celery worker (important for long tasks):

```bash
celery -A src.celery_tasks worker --loglevel=info
```

7. Run the Streamlit frontend for local UI testing (optional):

```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run main.py
```


## Running services and workers

- Celery worker: `celery -A src.celery_tasks worker --loglevel=info`
- To monitor task events: enable `-E` flag or use Flower if configured.
- Make sure Celery uses the same Redis URL as in `Config.REDIS_URL`.

Notes:
- Avoid opening MongoClient before forking workers in production. See PyMongo docs regarding fork safety. In development this warning is shown when creating a client at module import time.
- Long-running LLM generation can take minutes; Celery tasks are used to avoid request timeouts. Configure task time limits carefully if you want no timeout.


## Streamlit frontend (local)

The demo Streamlit app under `streamlit_app/` is intended for manual testing and demonstration. It reads API endpoints from configuration and requires an authenticated user token to access protected endpoints.

Important Streamlit notes you encountered in development:
- Forms must use unique `key` values for each `st.form` instance. If you see `StreamlitAPIException: There are multiple identical forms with key='login_form'`, ensure forms use unique keys or conditional rendering.
- Keep the UI simple: fetch the JSON `question` payload from the `/api/profile/v1/question` API, parse it, and dynamically render the appropriate input widgets per question type.


## Running tests

Run unit tests with pytest:

```bash
pytest -q
```


## Security and best practices

- Protect APIs: all endpoints that return user-specific data should require authentication. Do not expose internal endpoints or secrets.
- Token handling: JWT token expiration and refresh flow must be implemented. Ensure tokens used for email verification have a limited TTL.
- Email verification: verification links should contain short-lived signed tokens and should not expose sensitive data.
- User isolation: one user must never access another user's private data. Enforce checks on each API handler (ownership and authorization checks).
- Secrets: use environment variables or secret management systems (Vault, cloud KMS) in production. Do not store secrets in the repository.


## How profiling and LLM calls work

Profile generation flow in this project:

1. The user completes the generated questionnaire. The frontend composes a response JSON that includes each original question object plus a `user_answer` field. An example structure is included below.
2. The backend receives the completed questionnaire and enqueues a `profile_analysis_task` Celery job.
3. The task calls an LLM (configured either via `OPENAI_API_KEY` for OpenAI or a local LLM endpoint). If the LLM call fails (no API key, model unavailable, or network errors), the task must fall back to deterministic logic and a fallback profile.
4. The resulting profile is persisted to MongoDB and returned as the task result.

Example of the completed questionnaire JSON that your front-end should send (backend expects to copy original question metadata and add user answers):

```json
{
  "score": "6/6",
  "questions_data": [
    {
      "numero": 1,
      "question": "...",
      "type": "ChoixMultiple",
      "options": [],
      "user_answer": "A",
      "correct_answer": "A",
      "is_correct": true
    }
  ]
}
```

Requirements for the front-end payload sent to `profile_analysis_task`:
- Keep the original questions' metadata (numero, question, type, options).
- Add `user_answer` for each question.
- Include any client-side computed score if available.


## Recommendations and TODOs

- Improve LLM usage: allow configurable model names and endpoints; add retries and exponential backoff.
- Make the profile generation output richer: include concrete learning paths, suggested resources, timeline, and next steps derived from answers.
- Add an admin interface to review fallback profiles and re-run analyses when a better LLM endpoint is available.
- Secure Celery/worker environment: avoid opening DB clients at import time (defer client creation to task runtime), or use `forksafe` patterns.
- Add integration tests for the full quiz -> analysis -> profile persistence flow.


## Contributing

1. Fork the repository and create a feature branch.
2. Run tests locally and ensure new code includes tests where appropriate.
3. Create a pull request with a clear description of changes.


