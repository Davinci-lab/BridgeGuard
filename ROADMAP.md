
### `ARCHITECTURE.md`
```markdown
# Architecture

BridgeGuard follows a **local‑first, event‑driven architecture** with four core engines:

1. **Invariant Engine** – pure functions checking 14 invariant rules.
2. **Risk Engine** – converts violation set into a 0‑100 score.
3. **Policy Engine** – maps risk + reason codes to actionable decisions.
4. **Attack Replay Service** – loads defensive pattern libraries.

All storage is JSON file‑based, making the system zero‑dependency for persistence.

## Data Flow
Simulation → InvariantEngine → RiskEngine → PolicyEngine → DecisionRecord → Storage
              ↑
              └── AttackReplay (historical mapping)

## API Layer
FastAPI serves:
- `/simulate` – custom simulation
- `/simulate-attack/{name}` – replay known incidents
- `/metrics` – aggregate analytics
- `/decisions` – audit trail

## Frontend
React dashboard visualises historical attacks, replays them, and shows real‑time policy decisions.