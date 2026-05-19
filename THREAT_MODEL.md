# Threat Model

**Scope**: Cross‑chain bridge accounting, governance, and message validation.

**Assumptions**:
- Underlying blockchains are secure (no 51% attacks).
- The bridge’s smart contracts may have bugs, but BridgeGuard focuses on **detection**, not prevention.

**Threats Considered**:
1. **Insider/compromised signers** → Detected via signer health checks.
2. **Replay attacks** → Detected via duplicate message filter.
3. **Infinite mint** → Detected via mint‑lock imbalance.
4. **Configuration tampering** → Detected via cooldown violation.
5. **Emergency bypass** → Detected via emergency flag enforcement.
6. **Abnormal volume** → Detected via caps.

**Mitigations**:
- Runtime invariant monitoring.
- Policy engine with escalating responses.
- Full reason‑code transparency.