## 🛡️ BridgeGuard v2.0.0 – Commercial Stable Release

**The first open-source, explainable, plug-and-play runtime security kernel for cross-chain bridges is now production-ready.**

### What's New in v2.0.0

- **Multi-Tenant Authentication** – JWT-based auth with project isolation. Each team manages its own bridges securely.
- **Real-Time Event Listener** – Subscribe to bridge contract events via WebSocket/polling and evaluate every transfer as it happens.
- **Smart Alerting** – Get instant notifications via Slack, email, or custom webhooks when a transfer is flagged (FREEZE, ESCALATE).
- **Multi-Chain Connector Framework** – Pre-built connectors for EVM (Wormhole, Axelar), Solana, Cosmos IBC. Add a new bridge in minutes with a JSON config.
- **Auto-Discovery Wizard** – Paste a contract address; BridgeGuard suggests the correct invariant mappings using verified ABIs.
- **Custom Policy & DSL** – Calibrate risk weights or define your own invariants with a simple expression language.
- **Audit-Ready Reports** – Generate PDF decision reports with digital signatures for compliance and insurance.
- **Professional UI** – Redesigned dashboard with Tailwind CSS and shadcn/ui components.
- **Docker Deployment** – One-command setup with `docker-compose up`.
- **38 Passing Tests** – Zero critical issues, deterministic performance.

### Quick Start
```bash
git clone https://github.com/Davinci-lab/BridgeGuard.git
cd BridgeGuard
docker-compose up
```

Or run locally: .\start-dev.bat (Windows) – see README.md.

Why BridgeGuard?
Bridge-Native: Checks 14 accounting, governance, finality, and anomaly invariants specific to cross-chain bridges.

Explainable: Every decision (ALLOW, DELAY, FREEZE, ESCALATE, REQUIRE_EXTRA_SIGNATURES) comes with a reason code and human-readable explanation.

Plug-and-Play: Connect to any EVM bridge by providing an ABI and contract address – no custom code.

Open Source & Auditable: MIT licensed. All detection logic is transparent and testable.

Who Is It For?
Bridge operators who want continuous runtime protection without slowing down transfers.

Auditors (Trail of Bits, OpenZeppelin) needing a post-audit monitoring tool.

Insurers (Nexus Mutual, InsurAce) looking for real-time risk data feeds.

DeFi security researchers studying bridge attack patterns.

Resources
Documentation

Architecture & Invariants

Risk Model

Contributing

Twitter @BridgeGuard_io

BridgeGuard is defensive only. It never executes transactions or holds private keys.
