from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .models import TransferSimulation, DecisionRecord, Attack, Metrics
from .policy_engine import decide
from .attack_replay import load_attacks, load_normal_flows, attack_to_simulation
from .storage import save_decision, load_all_decisions, clear_storage
from .reason_codes import REASON_DESCRIPTIONS, ReasonCode
from datetime import datetime
from .api.auth import router as auth_router
from .api.v2 import router as bridgeguard_v2_router
from .database import get_db, init_db
from .dependencies import validate_api_key
from .routes_connectors import router as connectors_router
import uuid
import os

app = FastAPI(title="BridgeGuard", version="0.1.0")

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


PREMIUM_API_KEY_PATHS = {
    "/api/v2/connectors/discover",
}


def is_premium_api_key_path(path: str) -> bool:
    return (
        path in PREMIUM_API_KEY_PATHS
        or (path.startswith("/api/v2/connectors/") and path.endswith("/evaluate"))
    )


def extract_project_id(request) -> int | None:
    raw_project_id = request.headers.get("X-Project-ID") or request.query_params.get("project_id")
    if raw_project_id is None:
        return None
    try:
        return int(raw_project_id)
    except ValueError:
        return None


def open_request_db(request):
    db_provider = request.app.dependency_overrides.get(get_db, get_db)
    db_generator = db_provider()
    return next(db_generator), db_generator


@app.middleware("http")
async def premium_api_key_middleware(request, call_next):
    if not is_premium_api_key_path(request.url.path):
        return await call_next(request)

    db, db_generator = open_request_db(request)
    try:
        key_record = validate_api_key(
            request.headers.get("X-API-Key"),
            db,
            extract_project_id(request),
        )
    finally:
        db_generator.close()

    if key_record is None:
        return JSONResponse(
            status_code=403,
            content={"detail": "Valid X-API-Key header required for this premium endpoint"},
        )

    return await call_next(request)

attacks = load_attacks()
normal_flows = load_normal_flows()
v1_router = APIRouter(tags=["v1"])
v1_router.include_router(connectors_router)
v2_router = APIRouter()
v2_router.include_router(auth_router)
v2_router.include_router(bridgeguard_v2_router)


@app.on_event("startup")
def startup():
    init_db()


@v1_router.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


@v1_router.get("/attacks")
def get_attacks():
    return attacks


@v1_router.get("/normal-flows")
def get_normal_flows():
    return normal_flows


@v1_router.post("/simulate")
def simulate_transfer(sim: TransferSimulation):
    try:
        decision, risk_score, violations, explanation, recommended = decide(sim)
        record = DecisionRecord(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            simulation=sim,
            decision=decision,
            risk_score=risk_score,
            reason_codes=violations,
            explanation=explanation,
            recommended_action=recommended
        )
        save_decision(record)
        return record
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@v1_router.post("/simulate-attack/{attack_name:path}")
def simulate_by_attack_name(attack_name: str):
    attack = next((a for a in attacks if a.name == attack_name), None)
    if not attack:
        raise HTTPException(status_code=404, detail="Attack not found")
    sim = attack_to_simulation(attack)
    return simulate_transfer(sim)


@v1_router.get("/decisions")
def get_decisions():
    return load_all_decisions()


@v1_router.get("/reason-codes")
def get_reason_codes():
    return {code.value: desc for code, desc in REASON_DESCRIPTIONS.items()}


@v1_router.get("/metrics")
def get_metrics():
    decisions = load_all_decisions()
    total = len(decisions)
    risk_dist = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    dec_dist = {}
    reason_counter = {}
    for d in decisions:
        if d.risk_score < 30:
            risk_dist["low"] += 1
        elif d.risk_score < 60:
            risk_dist["medium"] += 1
        elif d.risk_score < 85:
            risk_dist["high"] += 1
        else:
            risk_dist["critical"] += 1
        dec_dist[d.decision] = dec_dist.get(d.decision, 0) + 1
        for rc in d.reason_codes:
            reason_counter[rc] = reason_counter.get(rc, 0) + 1
    top_reasons = sorted(reason_counter.items(), key=lambda x: x[1], reverse=True)[:5]
    return Metrics(
        total_simulations=total,
        risk_score_distribution=risk_dist,
        decisions_distribution=dec_dist,
        top_reason_codes=[{"code": k, "count": v} for k, v in top_reasons]
    )


@v1_router.delete("/decisions")
def clear_decisions():
    clear_storage()
    return {"status": "cleared"}


app.include_router(v1_router)
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")
