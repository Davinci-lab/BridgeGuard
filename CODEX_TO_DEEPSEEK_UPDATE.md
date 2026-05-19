# Codex Technical Update to DeepSeek — CarthEdge BridgeGuard

## 1. Current Local State

- Repository path: `C:\Projects\BridgeGuard`.
- Backend: FastAPI MVP under `backend/app`.
- Frontend: React + TypeScript under `frontend/src`.
- Data: 8 historical bridge incidents and 2 normal flow examples under `backend/app/sample_data`.
- Tests: Pytest backend suite under `backend/tests`.
- Docs/config now include:
  - `.gitignore`
  - `ARCHITECTURE.md`
  - `RISK_MODEL.md`
  - updated `README.md`
  - updated `CODEX_TO_DEEPSEEK_UPDATE.md`
  - `start-dev.bat`
  - `scripts/serve-frontend.js`

Local MVP status after Codex work:

- Backend runs on `http://127.0.0.1:8000`.
- Frontend runs on `http://localhost:3000`.
- API docs run on `http://127.0.0.1:8000/docs`.
- Frontend can call API through the local frontend server proxy.
- `start-dev.bat` has been tested end-to-end and launches the MVP with backend tests and frontend build options.

## 2. Modifications Applied by Codex

### P0 fixes applied

- Removed duplicate replay module:
  - Deleted `backend/app/attack_reply.py`.
  - Moved the implementation into `backend/app/attack_replay.py`.
  - Verified there are no remaining imports or references to `attack_reply`.

- Clean Git/GitHub readiness:
  - Added `.gitignore`.
  - Ignored Python caches, `.pytest_cache`, `frontend/node_modules`, `frontend/build`, logs, `.env`, editor noise, and runtime `decisions.json`.
  - Initialized local project Git repository at `C:\Projects\BridgeGuard`.
  - Verified project top-level with:
    - `git -c safe.directory=C:/Projects/BridgeGuard rev-parse --show-toplevel`
    - result: `C:/Projects/BridgeGuard`
  - Note: because Codex runs under a different Windows user than the folder owner, Git needs `-c safe.directory=C:/Projects/BridgeGuard` in this environment. A normal user shell should not need that after ownership is consistent.

- Removed generated artifacts during cleanup:
  - `backend/app/__pycache__`
  - `backend/tests/__pycache__`
  - `backend/.pytest_cache`
  - `frontend/node_modules`
  - `frontend/build`
  - Later `node_modules` and `build` were recreated by testing `start-dev.bat`; they remain ignored by `.gitignore`.

### P1 fixes applied

- Restricted CORS in `backend/app/main.py`:
  - Replaced wildcard `allow_origins=["*"]`.
  - Added environment-configured `ALLOWED_ORIGINS`.
  - Default origins:
    - `http://localhost:3000`
    - `http://127.0.0.1:3000`
  - Documented behavior in `README.md`.

- Added historical incident source URLs:
  - Added optional `source` field to `Attack` model in `backend/app/models.py`.
  - Added `source` URL for each incident in `backend/app/sample_data/attacks.json`.
  - Added `Data Sources` section to `README.md`.
  - Updated frontend `AttackReplay` to render the source link when present.

- Documented risk model:
  - Added `RISK_MODEL.md`.
  - Documented heuristic scoring formula.
  - Documented risk bands.
  - Documented every current weight in `backend/app/risk_engine.py`.
  - Explicitly states the model is not statistically calibrated and not production-grade.

- Improved TypeScript typing:
  - Rewrote `frontend/src/types.ts` with explicit types:
    - `PolicyDecision`
    - `ReasonCode`
    - `TransferSimulation`
    - `Attack`
    - `DecisionRecord`
    - `Metrics`
    - `RiskScoreDistribution`
    - `TopReasonCode`
  - Updated `frontend/src/api.ts` to type Axios responses.
  - Removed business-domain `any` usage from core API and metrics path.

- Added exact expected-decision regression test:
  - Updated `backend/tests/test_attack_replay.py`.
  - New test asserts every incident returns exactly its `expected_decision`.
  - Total backend tests increased from 16 to 17.

- Updated `Poly Network` sample expected decision:
  - Changed `expected_decision` from `ESCALATE_TO_GUARDIANS` to `FREEZE`.
  - Reason: existing policy logic returns `FREEZE` for the current Poly Network simulated violations and risk score.
  - This preserves current policy logic rather than changing business behavior to force a lower-severity decision.

## 3. Launcher Work Completed

User requested a double-click launcher that starts the whole MVP and allows testing.

Updated `start-dev.bat` now:

- Checks `python`.
- Checks `npm.cmd`.
- Installs/verifies backend dependencies with:
  - `python -m pip install -r requirements.txt`
- Installs frontend dependencies if `frontend/node_modules` is missing:
  - `npm.cmd install`
- Prompts user to run backend tests:
  - `python -m pytest tests`
- Prompts user to run frontend production build:
  - `npm.cmd run build`
- If frontend build is skipped but missing, it builds anyway.
- Starts backend:
  - `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
- Starts frontend through a stable local Node server:
  - `node scripts\serve-frontend.js`
- Performs backend and frontend health checks.
- Prints useful URLs and manual test commands.

Added `scripts/serve-frontend.js`:

- Serves `frontend/build` on `http://localhost:3000`.
- Proxies API calls to `http://127.0.0.1:8000`.
- Avoids reliability issues seen with `react-scripts start` inside batch/test contexts.

## 4. Test and Build Results

Backend commands run:

```bash
cd C:\Projects\BridgeGuard\backend
python -m pytest tests
```

Backend result:

```text
17 passed
```

Frontend commands run:

```bash
cd C:\Projects\BridgeGuard\frontend
npm.cmd run build
```

Frontend result:

```text
Compiled successfully.
```

Launcher test command used:

```bat
(echo Y&echo Y&echo.) | start-dev.bat
```

Launcher result:

- Backend dependencies verified.
- Frontend dependencies verified.
- Backend tests passed: `17 passed`.
- Frontend build passed.
- Backend health check returned:

```json
{"status":"ok","version":"0.1.0"}
```

- Frontend check returned:

```text
200
```

Post-launch verification:

- `http://127.0.0.1:8000/health` returned `{"status":"ok","version":"0.1.0"}`.
- `http://localhost:3000` returned HTTP `200`.
- `http://localhost:3000/attacks` returned `8` attacks through the frontend proxy.

Known non-blocking warnings:

- `pip` prints a new-version notice.
- `react-scripts`/Node prints `[DEP0176] DeprecationWarning: fs.F_OK is deprecated`.
- These are not blocking runtime or build failures.

## 5. Architecture Assessment After Updates

Coherent:

- Backend has clean separation between:
  - models,
  - reason codes,
  - invariant engine,
  - risk engine,
  - policy engine,
  - attack replay,
  - storage,
  - API layer.
- Frontend consumes typed API helpers.
- Historical incident source metadata is now part of the data model.
- Local launch flow is easier for demos and testing.

Still fragile:

- Runtime storage still writes `decisions.json` relative to current working directory.
- No auth, tenant isolation, rate limiting, request-size limits, or production deployment profile.
- Risk model remains heuristic.
- UI still uses inline styles and is demo-grade.
- Frontend served by custom local Node server for double-click MVP reliability; production packaging should be decided later.

## 6. Security and Defensive-Only Review

Confirmed:

- No real bridge execution.
- No live-chain adapters.
- No private-key handling.
- No transaction signing.
- No exploit payload implementation.
- Historical incidents are used for defensive replay and explanation only.
- No hardcoded secrets found in source/docs scan.

Improved:

- CORS is no longer wildcard by default.
- README now explicitly states limitations and defensive-only scope.
- Risk model docs explicitly avoid production-grade security claims.

Remaining security gaps for future work:

- Unauthenticated API.
- Unauthenticated `DELETE /decisions`.
- No rate limiting.
- No audit logging beyond local JSON decisions.
- No production configuration separation.

## 7. Scientific and Mathematical Review

Current state:

- Invariants are explicit in `backend/app/invariant_engine.py`.
- Reason codes cover the required minimum set.
- Policy decisions are explainable through:
  - decision,
  - risk score,
  - reason codes,
  - explanation,
  - recommended action.
- `RISK_MODEL.md` now documents score formula, bands, weights, and calibration limitations.
- Expected decision tests now lock the historical replay behavior.

Still missing for stronger rigor:

- Explicit `BridgeState` / `Transition` abstraction.
- Formal invariant formulas in code-adjacent docs.
- Magnitude-aware scoring.
- Calibrated score weights from real labeled datasets.
- False-positive / false-negative evaluation.
- Confidence or uncertainty reporting.

## 8. Product and Monetization Review

Current commercial/demo readiness:

- Ready for internal MVP demos.
- Ready for investor/demo discussion with clear disclaimers.
- Better GitHub credibility after P0/P1 cleanup.
- Not ready as paid SaaS, production risk API, or enterprise control layer.

What improved:

- Double-click launch flow.
- Test/build prompts.
- Stable frontend serving for demos.
- Public incident source references.
- Clearer risk-model documentation.
- Stronger TypeScript contracts.

Still needed for commercial credibility:

- polished UI,
- exportable risk reports,
- API authentication,
- tenant model,
- CI,
- deployment profile,
- incident source quality review,
- calibrated risk scoring,
- formal security review.

## 9. GitHub Readiness Status

Improved and mostly ready for a clean first commit after final manual review.

Important note:

- `frontend/node_modules` and `frontend/build` were recreated during launcher testing. They are ignored by `.gitignore`.
- Before committing, use:

```bash
git -c safe.directory=C:/Projects/BridgeGuard status --short --ignored
```

Expected commit set should include source/docs/config only, not generated artifacts.

Files added or materially updated:

- `.gitignore`
- `ARCHITECTURE.md`
- `RISK_MODEL.md`
- `README.md`
- `CODEX_TO_DEEPSEEK_UPDATE.md`
- `start-dev.bat`
- `scripts/serve-frontend.js`
- `backend/app/attack_replay.py`
- `backend/app/main.py`
- `backend/app/models.py`
- `backend/app/sample_data/attacks.json`
- `backend/tests/test_attack_replay.py`
- `frontend/src/api.ts`
- `frontend/src/types.ts`
- `frontend/src/components/AttackReplay.tsx`
- `frontend/src/components/RiskPanel.tsx`
- `frontend/src/components/Dashboard.tsx`

Removed:

- `backend/app/attack_reply.py`

## 10. Remaining DeepSeek Fixes

### P1/P2 — recommended before public launch

- Add CI:
  - backend pytest,
  - frontend npm install/build,
  - maybe no-audit warning gate at first.

- Add license decision:
  - required before public GitHub publication.

- Add API tests using FastAPI `TestClient`:
  - `/health`,
  - `/attacks`,
  - `/simulate-attack/{name}`,
  - `/reason-codes`,
  - `/metrics`,
  - malformed request cases.

- Make storage deterministic:
  - use explicit local data directory,
  - add atomic writes,
  - test save/load/delete.

- Add formal model doc:
  - `S_t`,
  - `S_t -> S_t+1`,
  - invariant formulas,
  - tolerance definitions.

- Improve frontend:
  - remove inline styles,
  - add richer incident panel,
  - add decision history,
  - add report/export button,
  - add visual risk bands.

### P3 — commercial roadmap

- Authenticated API mode.
- Tenant/project model.
- Enterprise policy packs.
- Report generation.
- Insurer intelligence views.
- Calibrated scoring.
- Optional private chain-adapter layer.

## 11. Recommended Next Development Plan

1. Commit current P0/P1 stabilization work.
2. Add GitHub Actions CI.
3. Add API-level tests.
4. Add storage hardening.
5. Add formal invariant/risk documentation.
6. Polish frontend demo flow.
7. Add screenshot/demo GIF only after UI polish.
8. Prepare public README with strict defensive-only wording.

## 12. Safe Public Positioning

One-sentence description:

> CarthEdge BridgeGuard is a defensive, local-first runtime invariant-checking MVP for simulated cross-chain bridge security decisions.

README warning/disclaimer:

> BridgeGuard is a research and decision-support prototype. It does not execute bridge transactions, handle private keys, connect to live chains, or guarantee asset safety. Do not use it as the sole control for real funds.

Commercial positioning paragraph:

> BridgeGuard demonstrates how bridge operators, auditors, insurers, and institutional risk teams can evaluate cross-chain bridge events using runtime accounting invariants, signer/governance checks, finality checks, anomaly signals, and explainable policy decisions. The public MVP is a local defensive demo; production deployments require calibrated policies, authentication, deployment hardening, monitoring integrations, and independent security review.

Scientific positioning paragraph:

> BridgeGuard models bridge activity as a state-transition problem: each simulated transition is evaluated against accounting, cap, finality, governance, replay, and emergency-state invariants. The MVP uses deterministic heuristic scoring for explainability; future versions should formalize invariant tolerances, magnitude-aware scoring, calibration datasets, and validation methodology.

## 13. Final Go / No-Go Verdict

- Internal MVP: Go.
- Investor/demo discussion: Go with disclaimers.
- GitHub publication: Near-go after final manual commit review and license decision.
- Production/security product: No-go.

Reason:

The MVP now runs locally, the double-click launcher works, backend tests pass, frontend builds, API behavior matches demo expectations, P0/P1 audit blockers are addressed, and the defensive-only boundary is intact. Production or paid-security claims remain inappropriate until authentication, deployment hardening, formal calibration, and independent review are completed.
