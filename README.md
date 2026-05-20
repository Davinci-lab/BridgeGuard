# BridgeGuard

**Defensive runtime security kernel for cross-chain bridge systems.**

BridgeGuard v2 is a local-first operator console and API for simulating bridge events, checking runtime invariants, scoring risk, and producing explainable decisions. It keeps the original v1 simulation endpoints intact while adding authentication, project isolation, event listeners, alerts, policy calibration, connector discovery, and signed compliance reports.

## v2 Feature Set

- Authenticated FastAPI v2 API with JWT login/register and `/api/v2/auth/me`.
- Project-scoped multi-tenancy for simulations, decisions, alerts, listeners, policy configs, and reports.
- Project dashboard with recent decisions, alert status, listener status, and v2 simulation flow.
- Multi-chain connector framework with EVM, Solana, and Cosmos connector types.
- EVM auto-discovery endpoint for verified ABI method mapping suggestions.
- Celery/Redis listener foundation for polling or websocket connector events.
- Slack, email, and webhook alert rules for risky decisions.
- Policy calibration with risk weights and custom expression rules.
- PDF decision reports with digital signature verification.
- TailwindCSS/shadcn-style frontend components.
- Docker Compose stack for PostgreSQL, Redis, backend, Celery worker, and Nginx frontend.
- GitHub Actions workflow for backend pytest and frontend type-check/build.

## Backward Compatibility

The original v1 API is intentionally preserved:

- Root v1 endpoints still work, including `/health`, `/simulate`, `/simulate-attack/{name}`, `/decisions`, `/metrics`, `/reason-codes`, and `/connectors`.
- The same v1 routes are also available under `/api/v1`.
- v2 routes live under `/api/v2` and require auth for project-scoped operations.
- The frontend keeps a **v1 Tools** section for historical replay, risk metrics, old connector storage, recent v1 decisions, and reason-code reference.
- Existing local `backend/connectors.json` files continue to work with old connector endpoints.

## Quick Start

The fastest path is Docker:

```powershell
docker compose up --build
```

Open:

- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

The Alembic seed migration creates a demo account:

```text
Email: demo@bridgeguard.local
Password: bridgeguard-demo
Project: Demo Bridge Operations
```

For a guided walkthrough, see [QUICKSTART.md](QUICKSTART.md).

## Docker Setup

The Compose stack includes:

- `db`: PostgreSQL 16
- `redis`: Redis 7
- `backend`: FastAPI with Alembic migrations on startup
- `celery`: BridgeGuard worker for listener and alert tasks
- `frontend`: Nginx serving the production React build and proxying API routes

Useful commands:

```powershell
docker compose up --build
docker compose ps
docker compose logs -f backend
docker compose down
```

To reset the database volume:

```powershell
docker compose down -v
docker compose up --build
```

## Manual Setup

Backend:

```powershell
cd backend
python -m pip install -r requirements.txt
alembic upgrade head
python -m pytest tests
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm.cmd exec tsc -- --noEmit
npm.cmd run build
npm start
```

Optional local services for v2 listener/alert workflows:

```powershell
redis-server
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

Environment variables:

```text
DATABASE_URL=sqlite:///./bridgeguard.db
DATABASE_URL=postgresql://bridgeguard:bridgeguard@localhost:5432/bridgeguard
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
SECRET_KEY=change-this-in-real-deployments
```

## API Overview

v1 examples:

```powershell
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/attacks
curl -X POST "http://127.0.0.1:8000/simulate-attack/Ronin%20Bridge"
```

v2 auth:

```powershell
curl -X POST http://127.0.0.1:8000/api/v2/auth/register `
  -H "Content-Type: application/json" `
  -d "{\"email\":\"operator@example.com\",\"password\":\"bridgeguard-demo\",\"project_name\":\"Ops\"}"

curl -X POST http://127.0.0.1:8000/api/v2/auth/login `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=operator@example.com&password=bridgeguard-demo"
```

v2 project-scoped requests use:

```text
Authorization: Bearer <token>
X-Project-ID: <project_id>
```

## Connectors

BridgeGuard supports a connector registry with:

- EVM connector
- Solana connector mock
- Cosmos connector mock
- Config-file discovery
- Etherscan ABI discovery through `POST /api/v2/connectors/discover`

Default demo connector configs are stored in:

```text
backend/app/sample_data/default_connectors.json
```

User-created legacy connectors are stored in:

```text
backend/connectors.json
```

## Testing

Backend:

```powershell
cd backend
python -m pytest tests
```

Frontend:

```powershell
cd frontend
npm.cmd exec tsc -- --noEmit
npm.cmd run build
```

CI runs the same backend and frontend checks on push and pull request.

## Defensive Boundaries

BridgeGuard is defensive-only:

- no private keys
- no transaction signing
- no exploit payloads
- no live fund movement
- no guarantee of absolute security
- no proprietary internal bridge logic exposed

See [SECURITY.md](SECURITY.md) for reporting guidance and safe-use notice.

## Risk Model

The risk model is deterministic and explainable. v2 adds project-level weight calibration and custom expression rules, but operators must calibrate with real operational data before any production use.

See [RISK_MODEL.md](RISK_MODEL.md).

## Data Sources

The historical incident library is used only for defensive simulation and product demonstration.

| Incident | Reference |
| --- | --- |
| Ronin Bridge | https://nomoslabs.io/archive/ronin-bridge-2022 |
| Wormhole | https://www.halborn.com/blog/post/explained-the-wormhole-hack-february-2022 |
| Nomad | https://nomoslabs.io/archive/nomad-bridge-2022 |
| Harmony Horizon | https://techcrunch.com/2022/06/24/harmony-blockchain-crypto-hack/ |
| BNB Token Hub | https://www.nansen.ai/research/bnb-chains-cross-chain-bridge-exploit-explained |
| Poly Network | https://www.cnbc.com/2021/08/11/cryptocurrency-theft-hackers-steal-600-million-in-poly-network-hack.html |
| Multichain | https://www.coindesk.com/tech/2023/07/07/multichain-team-confirms-exploit-across-fantom-moonriver-and-dogechain-bridges |
| THORChain recent incident | https://blog.thorchain.org/post-mortem-eth-router-exploits-1-2-and-premature-return-to-trading-incident/ |
| Orbit Chain | https://rekt.news/orbit-chain-rekt/ |
| Socket/Bungee | https://rekt.news/socket-rekt/ |
| Heco Bridge (HTX) | https://rekt.news/htx-heco-bridge-rekt/ |
| Mixin Network | https://rekt.news/mixin-network-rekt/ |
| LI.FI protocol | https://rekt.news/lifi-rekt/ |
| Celer cBridge DNS hijack | https://blog.celer.network/2023/08/18/celer-cbridge-dns-hijack-incident/ |
| Kelp DAO rsETH Bridge | https://rekt.news/kelp-dao-rekt/ |
| Shibarium Bridge | https://rekt.news/shibarium-bridge-rekt/ |
| Nervos Force Bridge | https://rekt.news/nervos-force-bridge-rekt/ |
| Verus Ethereum Bridge | https://blockchain.news/verus-ethereum-bridge-exploited |
| NoOnes Solana Bridge | https://www.gate.com/news/noones-8m-cross-chain-bridge-exploit |

## Status

BridgeGuard v2.0.0 is a defensive research MVP. It is suitable for local demonstrations, internal review, and prototype operator workflows, but it is not an audited production security control.
