# BridgeGuard

**Defensive runtime security kernel for cross-chain bridge systems.**

BridgeGuard is a local-first research MVP that simulates bridge events, checks runtime invariants, computes risk scores, and returns explainable policy decisions. It is designed for bridge operators, guardians, auditors, insurers, and security researchers who need a clear demo of runtime verification beyond static audits.

## Current MVP

- FastAPI backend with deterministic policy, invariant, and risk engines.
- Dark dashboard UI for incident replay, decision explanations, reason codes, history, and connector testing.
- 19 historical bridge incident scenarios with public references.
- Plug-and-play local connector configuration for read-only EVM bridge evaluation.
- Local `start-dev.bat` launcher for backend, frontend, tests, and health checks.

## What It Is

- A defensive monitoring and decision-support prototype.
- A runtime invariant-checking layer for mint-lock, burn-release, flow, cap, finality, signer, governance, replay, TVL divergence, and emergency-state risks.
- A historical incident replay system for client demos and regression tests.
- A local connector manager that can store read-only bridge configurations in `connectors.json`.

## What It Is Not

- Not a bridge, relayer, wallet, or transaction execution system.
- Not an exploit toolkit.
- Not an audited production security control.
- Not a guarantee of bridge safety.
- Not a private-key manager and not a transaction signer.

## Policy Decisions

BridgeGuard maps detected runtime conditions to:

- `ALLOW`
- `DELAY`
- `FREEZE`
- `ESCALATE_TO_GUARDIANS`
- `REQUIRE_EXTRA_SIGNATURES`

Each decision includes a risk score, reason codes, explanation, and recommended defensive action.

## Quick Start

From the repository root:

```powershell
start-dev.bat
```

The launcher verifies dependencies, optionally runs backend tests, builds the lightweight frontend bundle, starts the backend, starts the frontend server, and performs health checks.

Open:

- Frontend dashboard: `http://localhost:3000`
- Backend health: `http://127.0.0.1:8000/health`
- API docs: `http://127.0.0.1:8000/docs`

## Backend

```powershell
cd backend
python -m pip install -r requirements.txt
python -m pytest tests
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Expected current test result:

```text
18 passed
```

By default, CORS allows browser requests only from:

- `http://localhost:3000`
- `http://127.0.0.1:3000`

Override for local experiments:

```powershell
set ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Frontend

```powershell
cd frontend
npm.cmd run build
```

The current demo build uses `scripts/build-frontend.js`, a lightweight local bundle generator used to avoid `react-scripts` instability under newer Node versions. The source React/TypeScript UI remains in `frontend/src`.

Optional TypeScript check:

```powershell
npm.cmd exec tsc -- --noEmit --skipLibCheck
```

## Example API Calls

Health:

```powershell
curl http://127.0.0.1:8000/health
```

Historical incidents:

```powershell
curl http://127.0.0.1:8000/attacks
```

Replay Ronin:

```powershell
curl -X POST "http://127.0.0.1:8000/simulate-attack/Ronin%20Bridge"
```

Replay Socket/Bungee:

```powershell
curl -X POST "http://127.0.0.1:8000/simulate-attack/Socket%2FBungee"
```

## Plug-and-Play Connectors

The Connectors panel lets users create local read-only EVM connector configurations and evaluate them through the same policy engine.

Connector data is stored locally in:

```text
backend/connectors.json
```

This file is intentionally ignored by Git.

Two demo presets are shipped in `backend/app/sample_data/default_connectors.json` and can be loaded from the dashboard with **Load preset connectors**:

- Wormhole Sepolia (ETH)
- Axelar Gateway (Sepolia)

For local demos, use:

```json
{
  "name": "Demo EVM Bridge",
  "type": "evm",
  "enabled": true,
  "rpc_url": "mock://local",
  "chain_id": 1,
  "contract_address": "0x0000000000000000000000000000000000000000",
  "abi": [],
  "method_mapping": {
    "locked_collateral": "totalLocked",
    "minted_supply": "totalMinted",
    "burned_proven": "totalBurned",
    "released_supply": "totalReleased"
  },
  "daily_cap": 1000000,
  "route_cap": 500000,
  "asset_cap": 2000000,
  "source_chain": "Ethereum",
  "dest_chain": "Arbitrum",
  "asset": "ETH",
  "finality_blocks": 10
}
```

If `web3` is installed and a real RPC is configured, BridgeGuard attempts read-only method calls. If the RPC is unavailable, it returns a safe mock evaluation with a warning instead of crashing.

## Defensive Boundaries

BridgeGuard must remain defensive-only:

- no private keys;
- no transaction signing;
- no exploit payloads;
- no live fund movement;
- no guarantee of absolute security;
- no proprietary internal bridge logic exposed.

See [SECURITY.md](SECURITY.md) for reporting guidance and safe-use notice.

## Risk Model

The current risk model is heuristic and deterministic. Weights are fixed for demo and testing purposes, and must be calibrated with real operational data before any production deployment.

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

## Repository Hygiene

Ignored local artifacts include:

- Python caches and `.pytest_cache`
- `frontend/node_modules`
- `frontend/build`
- `backend/decisions.json`
- `backend/connectors.json`
- logs and local environment files

## License / Status

BridgeGuard v1.0 is a defensive research MVP. It is suitable for local demonstrations, internal review, and investor/prospect discussions, but it is not production-grade bridge security.
