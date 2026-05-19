from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import TransferSimulation, DecisionRecord, Attack, Metrics
from .policy_engine import decide
from .attack_replay import load_attacks, load_normal_flows, attack_to_simulation
from .storage import save_decision, load_all_decisions, clear_storage
from .reason_codes import REASON_DESCRIPTIONS, ReasonCode
from datetime import datetime
from .routes_connectors import router as connectors_router
import uuid
import os

app = FastAPI(title="CarthEdge BridgeGuard", version="0.1.0")
app.include_router(connectors_router)

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

attacks = load_attacks()
normal_flows = load_normal_flows()

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}

@app.get("/attacks")
def get_attacks():
    return attacks

@app.get("/normal-flows")
def get_normal_flows():
    return normal_flows

@app.post("/simulate")
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

@app.post("/simulate-attack/{attack_name:path}")
def simulate_by_attack_name(attack_name: str):
    attack = next((a for a in attacks if a.name == attack_name), None)
    if not attack:
        raise HTTPException(status_code=404, detail="Attack not found")
    sim = attack_to_simulation(attack)
    return simulate_transfer(sim)

@app.get("/decisions")
def get_decisions():
    return load_all_decisions()

@app.get("/reason-codes")
def get_reason_codes():
    return {code.value: desc for code, desc in REASON_DESCRIPTIONS.items()}

@app.get("/metrics")
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

@app.delete("/decisions")
def clear_decisions():
    clear_storage()
    return {"status": "cleared"}
