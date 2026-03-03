# HireSense

**AI-Powered Resume Intelligence & Career Path Recommendation System**

HireSense is a semantic AI-driven resume analysis platform that goes beyond traditional Applicant Tracking Systems (ATS). Instead of relying on keyword matching, HireSense uses transformer-based language models to deeply understand resumes — extracting skills, technologies, and project experience while generating personalised learning and career transition paths.

Built for campus placement drives, HR teams, and working professionals, HireSense enables smarter hiring, skill gap analysis, and long-term career development.

---

## Key Features

- Semantic resume parsing using transformer models
- Context-aware skill extraction from projects & tech stack
- Automatic structuring of unstructured resume data
- Role-based benchmarking and profile comparison
- Personalised learning paths for upskilling & career switching
- Skill gap detection with recommendations
- Support for multiple resume formats (PDF, DOCX, TXT)

---

## How HireSense Works

1. Resume ingestion and preprocessing
2. Semantic embedding generation
3. Skill & technology extraction using NLP models
4. Role similarity scoring & benchmarking
5. Learning path generation based on industry profiles

---

## Use Cases

- Campus placement shortlisting
- Intelligent HR screening
- Career transition planning
- Promotion readiness analysis
- Skill gap analytics
- Personalised upskilling guidance

---

## Tech Stack

- Python 3.11+
- Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate
- PostgreSQL 15
- Docker & Docker Compose
- Transformer models (BERT), spaCy, HuggingFace, NLTK
- Pgvector (planned)

---


## RBAC & Sessions

Three roles: **admin**, **manager**, **employee**.

- `admin` is created automatically on first startup. Cannot register via UI.
- `manager` and `employee` register via `/auth/register`.
- Any user with any role can log in on any port.
- Sessions are isolated per port using separate cookies:

| Port | URL                   | Session Cookie    |
|------|-----------------------|-------------------|
| 5010 | http://localhost:5010 | `hs_session_5010` |
| 5011 | http://localhost:5011 | `hs_session_5011` |
| 5012 | http://localhost:5012 | `hs_session_5012` |

Logging in on port 5010 does not affect sessions on 5011 or 5012.

---

## First-Time Setup

### Prerequisites

- Python 3.11+
- Docker Desktop with Compose v2
- Git

---

### Option A — Docker (recommended)

**1. Clone and enter the repository**

```bash
git clone https://github.com/paarthsiloiya/HireSense.git
cd HireSense
```

**2. Create your environment file**

```bash
cp .env.example .env
```

Set `SECRET_KEY` and `ADMIN_PASSWORD` in `.env` before any non-local deployment.

**3. Build and start all services**

```bash
docker compose up --build
```

This starts PostgreSQL 15 on host port `5434` (container port `5432`) and three Flask instances on ports `5010`, `5011`, `5012`. The admin user is created automatically on first boot — no manual seeding required.

**4. Open a portal and log in**

| Port | URL                   |
|------|-----------------------|
| 5010 | http://localhost:5010 |
| 5011 | http://localhost:5011 |
| 5012 | http://localhost:5012 |

Username: `admin` — Password: value of `ADMIN_PASSWORD` (default: `Admin@1234`).

**5. Common Docker commands**

```bash
# Stop (data kept)
docker compose down

# Stop and delete all data
docker compose down -v

# Rebuild after code changes
docker compose up --build

# Tail logs for one service
docker compose logs -f app_5010
```

---

### Option B — Local Virtual Environment

**1. Clone and enter the repository**

```bash
git clone https://github.com/paarthsiloiya/HireSense.git
cd HireSense
```

**2. Create and activate a virtual environment**

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

```bash
cp .env.example .env
# Edit .env — set DATABASE_URL to your local PostgreSQL connection string
```

**5. Start a portal**

```bash
# macOS / Linux
PORT=5010 python run.py
```

```powershell
# Windows (PowerShell)
$env:PORT=5010; python run.py
```

Tables are created and the admin user is seeded automatically on first run. Register manager or employee accounts at `/auth/register`.

---

## Default Admin Credentials

| Username | Password     |
|----------|--------------|
| `admin`  | `Admin@1234` |

Change `ADMIN_PASSWORD` in `.env` before any non-local deployment.

---

## License

This project is licensed under the GNU General Public License v3.0.

