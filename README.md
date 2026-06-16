# AI Email Generator

A production-style FastAPI application that generates professional emails using AI. It includes login/signup, JWT authentication, saved email history, AI-generated subject lines, tone control, email scoring, Docker, and a clean browser UI.

## Features

- User registration and login
- JWT-based authentication
- AI email generation using OpenAI or local Ollama models
- Email tone, purpose, recipient type, language, and length options
- Generated subject line, email body, CTA, and quality score
- Save generated emails in database
- View and delete email history
- Rate limiting on AI generation endpoint
- SQLite for local development
- PostgreSQL-ready Docker Compose setup
- Environment-based configuration
- Health check endpoint

## Tech Stack

- Backend: FastAPI
- Database: SQLAlchemy with SQLite/PostgreSQL
- Authentication: JWT + bcrypt password hashing
- AI: OpenAI API or Ollama with local Llama models
- Frontend: HTML, CSS, JavaScript
- Deployment: Docker / Render / Railway / VPS

## Project Structure

```text
ai-email-generator/
├── app/
│   ├── api/routes/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── static/
│   ├── tests/
│   └── main.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Local Setup

### 1. Create virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `.env`

```bash
copy .env.example .env
```

For Mac/Linux:

```bash
cp .env.example .env
```

Update this in `.env`.

For OpenAI:

```env
SECRET_KEY="use-a-long-random-secret"
AI_PROVIDER="openai"
OPENAI_API_KEY="your-openai-api-key"
```

For Ollama with a local Llama model:

```env
SECRET_KEY="use-a-long-random-secret"
AI_PROVIDER="ollama"
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="llama3.2"
```

Install Ollama from:

```text
https://ollama.com
```

Then pull a model:

```bash
ollama pull llama3.2
```

Make sure Ollama is running before generating emails:

```bash
ollama serve
```

### 4. Run the application

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Run with Docker Compose and PostgreSQL

Change your `.env` database URL to:

```env
DATABASE_URL="postgresql+psycopg2://postgres:postgres@db:5432/ai_email_generator"
```

If you run the FastAPI app in Docker and Ollama on your host machine, `localhost`
inside the container does not point to your host. Use a reachable Ollama URL for
`OLLAMA_BASE_URL`, or add Ollama as a Docker Compose service and set:

```env
OLLAMA_BASE_URL="http://ollama:11434"
```

Then run:

```bash
docker compose up --build
```

Open:

```text
http://localhost:8000
```

## Main API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check server status |
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Current user |
| POST | `/api/emails/generate` | Generate AI email |
| GET | `/api/emails/history` | View saved email history |
| DELETE | `/api/emails/{email_id}` | Delete saved email |

## Production Deployment Checklist

Before deploying publicly:

- Set a strong `SECRET_KEY`
- Use PostgreSQL, not SQLite
- Set `ENVIRONMENT=production`
- Restrict `ALLOWED_ORIGINS` to your real frontend domain
- If using Ollama, keep the Ollama server private and do not expose it publicly
- Use HTTPS
- Store environment variables in your hosting dashboard
- Add database migrations with Alembic for large production use
- Add monitoring/logging such as Sentry or Grafana
- Add billing if you turn it into SaaS

## Portfolio Improvements

You can add these later:

- Gmail API integration to send emails directly
- Resume + job description upload for job application emails
- Client proposal generator
- WhatsApp/LinkedIn message generator
- Team workspace and usage limits
- Stripe subscription plans
