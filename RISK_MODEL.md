# Risk Model

BridgeGuard's current risk model is deterministic and heuristic. It is intended for local demonstration of explainable runtime policy decisions, not production-grade risk pricing or automated control of real assets.

## Scoring Formula

The backend computes risk from the set of violated reason codes:

```text
risk_score = min(max_violation_weight + combination_penalty, 100)
combination_penalty = min(number_of_violations * 5, 40)
```

If there are no violations, the score is `0`.

## Risk Bands

The `/metrics` endpoint groups scores into bands:

| Band | Score range |
| --- | --- |
| Low | `< 30` |
| Medium | `30-59.9` |
| High | `60-84.9` |
| Critical | `>= 85` |

The policy engine separately maps scores and selected hard-stop reason codes to policy decisions.

## Current Weights

| Reason code | Weight | Rationale |
| --- | ---: | --- |
| `EMERGENCY_MODE_ACTIVE` | 100 | Emergency mode is treated as an immediate stop condition. |
| `REPLAY_OR_DUPLICATE_MESSAGE` | 90 | Duplicate messages can indicate replay risk and should freeze the route. |
| `UNKNOWN_OR_CHANGED_ROOT` | 80 | Unknown or changed trust roots can invalidate message verification assumptions. |
| `CONFIG_CHANGE_UNCOOLED` | 70 | Recent configuration changes require guardian-level caution. |
| `VALIDATOR_SET_RISK` | 60 | A small or risky validator set materially weakens governance safety. |
| `SIGNER_THRESHOLD_WEAK` | 50 | Signer participation too close to threshold increases compromise risk. |
| `TVL_DIVERGENCE` | 40 | Accounting divergence can indicate missing collateral or state mismatch. |
| `MINT_EXCEEDS_LOCKED` | 35 | Minted assets exceeding locked collateral violates core bridge accounting. |
| `RELEASE_EXCEEDS_BURNED` | 35 | Released assets exceeding burned/proven assets violates release accounting. |
| `OUTFLOW_EXCEEDS_INFLOW` | 30 | Excess outflow indicates imbalance beyond the allowed buffer. |
| `ASSET_CAP_EXCEEDED` | 25 | Per-asset limits are exceeded. |
| `ROUTE_CAP_EXCEEDED` | 25 | Per-route limits are exceeded. |
| `CHAIN_FINALITY_NOT_REACHED` | 20 | Source-chain finality is incomplete. |
| `ABNORMAL_VOLUME_SPIKE` | 20 | Volume exceeds configured daily thresholds. |

## Calibration Status

These weights are not statistically calibrated. They should be treated as transparent placeholders for the MVP.

Before production use, the model needs:

- historical labeled datasets;
- per-bridge policy profiles;
- invariant-specific tolerances;
- magnitude-aware scoring;
- false-positive and false-negative analysis;
- formal review by bridge security engineers;
- independent external validation.

## Proprietary Boundary

The public MVP can disclose the existence of invariant categories, reason codes, and this simple heuristic scoring model. Production calibration logic, customer-specific policies, and insurer or enterprise pricing models should remain private.
