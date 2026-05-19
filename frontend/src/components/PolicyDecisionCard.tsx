import React from 'react';
import { DecisionRecord, PolicyDecision, ReasonCode } from '../types';

interface Props {
    decision: DecisionRecord | null;
}

const decisionClassMap: Record<PolicyDecision, string> = {
    ALLOW: 'decision-allow',
    DELAY: 'decision-delay',
    FREEZE: 'decision-freeze',
    ESCALATE_TO_GUARDIANS: 'decision-escalate-to-guardians',
    REQUIRE_EXTRA_SIGNATURES: 'decision-require-extra-signatures',
};

const getRiskClass = (score: number) => {
    if (score <= 30) return 'risk-low';
    if (score <= 60) return 'risk-medium';
    if (score <= 84) return 'risk-high';
    return 'risk-critical';
};

const getReasonClass = (code: ReasonCode) => {
    if (['MINT_EXCEEDS_LOCKED', 'RELEASE_EXCEEDS_BURNED', 'REPLAY_OR_DUPLICATE_MESSAGE', 'EMERGENCY_MODE_ACTIVE'].includes(code)) {
        return 'reason-critical';
    }
    if (['CONFIG_CHANGE_UNCOOLED', 'UNKNOWN_OR_CHANGED_ROOT', 'VALIDATOR_SET_RISK', 'TVL_DIVERGENCE'].includes(code)) {
        return 'reason-high';
    }
    if (['SIGNER_THRESHOLD_WEAK', 'CHAIN_FINALITY_NOT_REACHED', 'ROUTE_CAP_EXCEEDED', 'ASSET_CAP_EXCEEDED'].includes(code)) {
        return 'reason-medium';
    }
    return 'reason-low';
};

const exportDecision = (decision: DecisionRecord) => {
    const blob = new Blob([JSON.stringify(decision, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `bridgeguard-decision-${decision.id}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
};

const PolicyDecisionCard: React.FC<Props> = ({ decision }) => {
    if (!decision) {
        return <p className="muted">No decision yet. Select an incident and run a defensive replay.</p>;
    }

    const riskClass = getRiskClass(decision.risk_score);
    const clampedRisk = Math.max(0, Math.min(decision.risk_score, 100));

    return (
        <section className={`card decision-card ${decisionClassMap[decision.decision]}`}>
            <div className="decision-header">
                <div>
                    <span className="decision-label">Policy decision</span>
                    <h3 className="decision-title">{decision.decision}</h3>
                </div>
                <button className="secondary-button" onClick={() => exportDecision(decision)}>
                    Export Decision (JSON)
                </button>
            </div>

            <div className="risk-gauge-row">
                <span className="decision-label">Risk score</span>
                <svg className={`risk-gauge ${riskClass}`} viewBox="0 0 120 120" role="img" aria-label={`Risk score ${decision.risk_score.toFixed(1)} out of 100`}>
                    <circle className="risk-gauge-track" cx="60" cy="60" r="48" pathLength="100" />
                    <circle className="risk-gauge-fill" cx="60" cy="60" r="48" pathLength="100" strokeDasharray="100" strokeDashoffset={100 - clampedRisk} />
                    <text className="risk-gauge-text" x="60" y="65">{decision.risk_score.toFixed(0)}</text>
                </svg>
                <strong>{decision.risk_score.toFixed(1)} / 100</strong>
            </div>

            <div>
                <span className="decision-label">Reason codes</span>
                <div className="badge-list">
                    {decision.reason_codes.length > 0
                        ? decision.reason_codes.map(code => <span className={`badge ${getReasonClass(code)}`} key={code}>{code}</span>)
                        : <span className="badge">NONE</span>}
                </div>
            </div>

            <div className="explanation-grid">
                <div className="text-panel">
                    <h4>Explanation</h4>
                    <p>{decision.explanation}</p>
                </div>
                <div className="text-panel">
                    <h4>Recommended action</h4>
                    <p>{decision.recommended_action}</p>
                </div>
            </div>
        </section>
    );
};

export default PolicyDecisionCard;
