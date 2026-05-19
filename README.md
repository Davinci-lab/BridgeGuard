# CarthEdge BridgeGuard

**Runtime security kernel for cross-chain bridge systems.**

BridgeGuard is a defensive, local-first research MVP that simulates cross-chain bridge events, checks runtime invariants, computes risk scores, and recommends explainable policy decisions without moving real funds.

## What It Is

- A local monitoring and decision-support prototype for bridge operators, guardians, auditors, and insurers.
- A runtime invariant-checking layer for mint-lock, burn-release, flow, cap, finality, signer, governance, replay, and emergency-state risks.
- A defensive replay tool for historical bridge incidents.

## What It Is Not

- Not a bridge, relayer, wallet, or transaction execution system.
- Not an exploit toolkit.
- Not connected to live chains in this MVP.
- Not production-grade security and not a guarantee of safety.

## Core Policy Decisions

BridgeGuard maps detected runtime conditions to:

- `ALLOW`
- `DELAY`
- `FREEZE`
- `ESCALATE_TO_GUARDIANS`
- `REQUIRE_EXTRA_SIGNATURES`

Each response includes a risk score, reason codes, explanation, and recommended defensive action.

## Run Backend

```bash
cd backend
pip install -r requirements.txt
python -m pytest tests
python -m uvicorn app.main:app --reload
```

By default, the API allows browser requests only from `http://localhost:3000` and `http://127.0.0.1:3000`. Override this for local experiments with:

```bash
set ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Health check:

```bash
curl http://localhost:8000/health
```

## Run Frontend

```bash
cd frontend
npm install
npm start
```

The frontend runs on `http://localhost:3000` and proxies API calls to `http://localhost:8000`.

## Example Defensive Replay

```bash
curl -X POST "http://localhost:8000/simulate-attack/Ronin%20Bridge"
```

Expected shape:

```json
{
  "decision": "FREEZE",
  "risk_score": 100.0,
  "reason_codes": ["MINT_EXCEEDS_LOCKED"],
  "explanation": "Violations detected: ...",
  "recommended_action": "Pause bridge route, require guardian review, rotate signers if needed."
}
```

## Security Limitations

- Uses simplified deterministic models and sample data.
- Does not perform cryptographic verification.
- Does not ingest live on-chain data.
- Risk weights are heuristic and require calibration before commercial deployment.
- Must not be used as the sole decision maker for real assets.

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
