BridgeGuard/
├── README.md
├── ARCHITECTURE.md
├── THREAT_MODEL.md
├── ROADMAP.md
├── SECURITY_NOTES.md
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── reason_codes.py
│   │   ├── invariant_engine.py
│   │   ├── policy_engine.py
│   │   ├── risk_engine.py
│   │   ├── attack_replay.py
│   │   ├── storage.py
│   │   └── sample_data/
│   │       ├── attacks.json
│   │       └── normal_flows.json
│   └── tests/
│       ├── test_invariant_engine.py
│       ├── test_policy_engine.py
│       ├── test_attack_replay.py
│       └── test_risk_engine.py
└── frontend/
    ├── package.json
    ├── tsconfig.json
    └── src/
        ├── App.tsx
        ├── api.ts
        ├── index.tsx
        └── components/
            ├── Dashboard.tsx
            ├── AttackReplay.tsx
            ├── PolicyDecisionCard.tsx
            ├── RiskPanel.tsx
            └── ReasonCodesTable.tsx