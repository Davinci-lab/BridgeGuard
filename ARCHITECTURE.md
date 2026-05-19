# Architecture

BridgeGuard is a local-first defensive runtime security MVP for simulated cross-chain bridge events. It does not execute bridge transactions, connect to live chains, or handle private keys.

## Backend

The FastAPI backend exposes simulated bridge security workflows:

- `InvariantEngine`: evaluates accounting, signer, finality, replay, cap, configuration, and emergency-state invariants.
- `RiskEngine`: maps reason-code violations to a deterministic 0-100 heuristic score.
- `PolicyEngine`: converts violations and risk score into `ALLOW`, `DELAY`, `FREEZE`, `ESCALATE_TO_GUARDIANS`, or `REQUIRE_EXTRA_SIGNATURES`.
- Attack replay helpers: load historical incident metadata and convert each incident into defensive simulation inputs.
- JSON storage: keeps local decision records for demo metrics.

## Frontend

The React frontend is a local dashboard for:

- viewing aggregate risk metrics,
- replaying historical incidents defensively,
- displaying policy decisions, risk scores, reason codes, explanations, and recommended actions,
- showing reason-code descriptions.

## Data Flow

```text
Simulation input
  -> InvariantEngine
  -> RiskEngine
  -> PolicyEngine
  -> DecisionRecord
  -> Local JSON storage / API response
```

Historical incidents follow the same path after being mapped to simulated transfer state.

## Boundaries

BridgeGuard is intentionally not a bridge, relayer, wallet, exploit toolkit, or live-chain monitoring agent in this MVP. Production versions would require chain adapters, formalized calibration, authentication, tenant isolation, external audits, and deployment hardening.
