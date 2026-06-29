# ai-backend

A production-ready, highly modular FastAPI backend template built with PostgreSQL, Redis, Alembic, Docker, and NGINX. Designed as a template for building robust AI application backends, it includes structured JSON logging, dynamic rate limiting, JWT session token management, and containerized deployment configuration.

---

## Project Architecture

This application employs a layered clean architecture pattern to segregate concerns:

```text
                       +-----------------------+
                       |   NGINX Reverse Proxy |
                       +-----------+-----------+
                                   |
                       +-----------v-----------+
                       |  FastAPI Application  |
                       +-----------+-----------+
                                   |
      +----------------------------+----------------------------+
      |                            |                            |
+-----v-----+                +-----v-----+                +-----v-----+
| Security  |                | Cache/Limit|                | DB Session|
| (JWT/Hash)|                |  (Redis)  |                | (Asyncpg) |
+-----------+                +-----+-----+                +-----+-----+
                                   |                            |
                             +-----v-----+                +-----v-----+
                             |RedisService|                |UserService|
                             +-----------+                +-----v-----+
                                                                |
                                                          +-----v-----+
                                                          |User Model |
                                                          +-----------+
```

1. **Reverse Proxy (NGINX)**: Acts as the gateway entry point. Terminates connection parameters, implements standard security headers, limits file uploads to 20MB, enables gzip compression, and proxies application requests to the FastAPI ASGI servers.
2. **FastAPI Application (lifespan)**: Coordinates boot/teardown events, manages global middlewares (Structured Request Logger, Redis Rate Limiter, CORS, and Trusted Hosts), and registers unified Exception Handlers.
3. **Services Layer**: Encapsulates connections and CRUD methods for external engines (SQLAlchemy + asyncpg for Postgres database; redis.asyncio for caching and rate limiting).
4. **API Router**: Mounts API routes with clean prefixes, utilizing dependencies to enforce access limits and JWT authentication validation.

---

## Folder Structure

```text
ai-backend/
├── .env.example            # Template for environment settings
├── .env                    # Active local environment variables
├── .gitignore              # Files ignored by git version control
├── Dockerfile              # Multi-stage production build configuration
├── docker-compose.yml      # Containerized database, cache, proxy, and app runner
├── requirements.txt        # Python package dependencies
├── start.sh                # Script to poll Postgres, run Alembic, and start Uvicorn
├── alembic.ini             # Alembic configuration metadata
├── alembic/                # Database migrations directory
│   ├── env.py              # Async migration runner environment hook
│   ├── script.py.mako      # Template for new database revisions
│   └── versions/           # Ordered list of schema changes
│       └── 001_initial_migration.py  # Created users table schema
├── nginx/
│   └── nginx.conf          # NGINX reverse-proxy, security, and gzip config
├── static/
│   └── placeholder.txt     # Placeholder for static assets directory
└── app/
    ├── main.py             # App initiator and middleware registration
    ├── api/
    │   ├── deps.py         # DB session, Redis, and Current User dependencies
    │   └── routes/
    │       ├── api.py      # Combines all routers
    │       ├── auth.py     # Endpoints for registering, login, and auth token
    │       ├── health.py   # System database and redis connection health probing
    │       ├── root.py     # Base landing router
    │       └── users.py    # Active session user details router
    ├── core/
    │   ├── config.py       # Configuration settings loader (Pydantic Settings)
    │   ├── exceptions.py   # Global custom exception wrappers and handler bindings
    │   ├── logging_config.py # Structured JSON console and rotating file logger setup
    │   ├── middleware.py   # Access tracker and Redis-based rate limiter middleware
    │   └── security.py     # bcrypt password hasher and jwt token encoders/decoders
    ├── database/
    │   ├── base.py         # SQLAlchemy Base model definition
    │   └── session.py      # Async db engine and session dependencies
    ├── models/
    │   └── user.py         # SQLAlchemy 'users' table model
    ├── schemas/
    │   ├── token.py        # Token response and payload structures
    │   └── user.py         # Registration, login, and query validation definitions
    ├── services/
    │   ├── redis_service.py # Redis client caching and rate-limiting service
    │   └── user_service.py # Database user registrations and login credentials resolver
    └── utils/              # Helper utility packages
```

---

## API Endpoints

All endpoints are fully documented interactively on Swagger UI when running.

| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| **GET** | `/` | No | Base endpoint returning API specifications and details. |
| **GET** | `/health` | No | Verifies PostgreSQL and Redis health status and connection responses. |
| **GET** | `/version` | No | Returns the application's active build version. |
| **POST**| `/auth/register` | No | Registers a new user. Expects JSON body with email, name, and password. |
| **POST**| `/auth/login` | No | Authenticates user credentials. Expects JSON body and returns JWT. |
| **POST**| `/auth/token` | No | Authenticates user credentials. Expects form-data (compatible with Swagger Authorize). |
| **GET** | `/users/me` | **Yes (Bearer JWT)** | Returns the logged-in user's details. |

---

## Setup & Running Guide

### Prerequisite

Make sure you have [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed on your machine.

---

### Running using Docker Compose (Recommended)

To run the entire stack including database, cache, backend app, and reverse proxy:

1. Clone or navigate to the workspace directory.
2. Build and start all services in detached mode:
   ```bash
   docker compose up --build -d
   ```
3. Docker Compose will automatically boot:
   - `postgres_db` (PostgreSQL 16)
   - `redis_cache` (Redis 7)
   - `fastapi_server` (FastAPI backend - wait until postgres and redis pass health checks, then runs database migrations and starts uvicorn)
   - `nginx_proxy` (NGINX proxy serving at port `80`)

4. Open your browser and navigate to:
   - **Main App Landing**: `http://localhost`
   - **Interactive API Docs (Swagger UI)**: `http://localhost/docs`
   - **Alternative API Docs (ReDoc)**: `http://localhost/redoc`

5. View real-time logs from the docker stack:
   ```bash
   docker compose logs -f
   ```

6. Stop all services and tear down containers:
   ```bash
   docker compose down -v
   ```

---

### Running Locally (Development Mode)

If you wish to run the backend application locally outside of Docker (using a local Python environment):

1. **Configure Environment Variables**:
   Create a local `.env` file by copying the template:
   ```bash
   cp .env.example .env
   ```
   Modify `DATABASE_URL` and `REDIS_URL` in `.env` to point to your local instances (e.g., `localhost` instead of `postgres` and `redis` hosts):
   ```text
   DATABASE_URL="postgresql+asyncpg://postgres:securepassword@localhost:5432/aibackend"
   REDIS_URL="redis://localhost:6379/0"
   ```

2. **Set up Virtual Environment**:
   Create and activate a Python virtual env (requires Python 3.12):
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # Linux/macOS
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Run Database Migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Start Development Server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   Interact with the API directly at `http://localhost:8000/docs`.

---

## Alembic Migration Commands

Alembic keeps track of database changes. Here are the core command lines used to manage migrations:

- **Create a new migration script manually**:
  ```bash
  alembic revision -m "description of migration"
  ```
- **Auto-generate a migration based on SQLAlchemy model changes**:
  (Requires a running local database with configuration in `.env` matching active database state)
  ```bash
  alembic revision --autogenerate -m "add new field to users"
  ```
- **Apply all pending migrations to the database**:
  ```bash
  alembic upgrade head
  ```
- **Revert the last database migration**:
  ```bash
  alembic downgrade -1
  ```
- **Check current database migration state**:
  ```bash
  alembic current
  ```

---

## Logging Configuration

Logs are written in structured JSON to facilitate ingestion in production environments (like ELK stacks, Datadog, or CloudWatch):
- **Console Log (stdout)**: JSON logs printed directly to the system console.
- **Log Files**: Logs are continuously written to the `logs/app.log` file.
- **Log Rotation**: The file logger automatically rotates files when the log size reaches 10MB, maintaining up to 5 history backups.
