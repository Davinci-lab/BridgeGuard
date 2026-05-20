# BridgeGuard v2 Quickstart

This guide gets BridgeGuard running and walks through the core v2 flow while keeping the v1 tools available.

## Option A: Docker

From the repository root:

```powershell
docker compose up --build
```

Open:

- `http://localhost:3000` for the frontend
- `http://localhost:8000/docs` for API docs
- `http://localhost:8000/health` for backend health

Demo login after migrations finish:

```text
Email: demo@bridgeguard.local
Password: bridgeguard-demo
```

Stop the stack:

```powershell
docker compose down
```

Reset demo data:

```powershell
docker compose down -v
docker compose up --build
```

## Option B: Manual

Start the backend:

```powershell
cd backend
python -m pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start the frontend in another terminal:

```powershell
cd frontend
npm install
npm start
```

For listener and alert task execution, also run Redis and a Celery worker:

```powershell
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

## First Five Minutes

1. Sign in with the demo account or register a new operator account.
2. Select `Demo Bridge Operations` or create a new project.
3. Open **Simulate**, run the default transfer simulation, and confirm a project-scoped decision appears in **Overview**.
4. Open **Alerts**, create a webhook/email/Slack rule, and use **Test** when the configured target is reachable.
5. Open **Policy**, adjust risk weights, add a custom rule such as:

```text
minted_supply > locked_collateral * 1.1
```

6. Open **Connectors**, save a connector or use the Etherscan discovery dialog for a verified EVM contract.
7. Open **v1 Tools** to replay historical incidents and confirm the old `/simulate`, `/simulate-attack`, `/metrics`, and connector flows still work.

## Health Checks

Backend:

```powershell
curl http://127.0.0.1:8000/health
```

Frontend build:

```powershell
cd frontend
npm.cmd exec tsc -- --noEmit
npm.cmd run build
```

Backend tests:

```powershell
cd backend
python -m pytest tests
```

## Notes

- Docker uses PostgreSQL and Redis.
- Manual setup defaults to SQLite unless `DATABASE_URL` is set.
- v1 endpoints remain available at the root and under `/api/v1`.
- v2 project-scoped endpoints require `Authorization: Bearer <token>` and either `X-Project-ID` or a `project_id` query parameter.
