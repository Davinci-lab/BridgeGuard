import React from 'react';
import { DecisionRecord, PolicyDecision, ReasonCode } from '../types';

interface Props {
    decision: DecisionRecord | null;
}

const decisionClassMap: Record<PolicyDecision, string> = {
    ALLOW: 'border-emerald-200 bg-emerald-50',
    DELAY: 'border-amber-200 bg-amber-50',
    FREEZE: 'border-red-200 bg-red-50',
    ESCALATE_TO_GUARDIANS: 'border-red-200 bg-red-50',
    REQUIRE_EXTRA_SIGNATURES: 'border-amber-200 bg-amber-50',
};

const getRiskClass = (score: number) => {
    if (score <= 30) return 'text-emerald-700';
    if (score <= 60) return 'text-amber-700';
    if (score <= 84) return 'text-orange-700';
    return 'text-red-700';
};

const getReasonClass = (code: ReasonCode) => {
    if (['MINT_EXCEEDS_LOCKED', 'RELEASE_EXCEEDS_BURNED', 'REPLAY_OR_DUPLICATE_MESSAGE', 'EMERGENCY_MODE_ACTIVE'].includes(code)) {
        return 'bg-red-100 text-red-800';
    }
    if (['CONFIG_CHANGE_UNCOOLED', 'UNKNOWN_OR_CHANGED_ROOT', 'VALIDATOR_SET_RISK', 'TVL_DIVERGENCE'].includes(code)) {
        return 'bg-orange-100 text-orange-800';
    }
    if (['SIGNER_THRESHOLD_WEAK', 'CHAIN_FINALITY_NOT_REACHED', 'ROUTE_CAP_EXCEEDED', 'ASSET_CAP_EXCEEDED'].includes(code)) {
        return 'bg-amber-100 text-amber-900';
    }
    return 'bg-emerald-100 text-emerald-800';
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
        return <p className="text-sm text-muted-foreground">No decision yet. Select an incident and run a defensive replay.</p>;
    }

    const riskClass = getRiskClass(decision.risk_score);
    const clampedRisk = Math.max(0, Math.min(decision.risk_score, 100));
    const primaryReason = decision.reason_codes[0] ?? 'NO_REASON';

    return (
        <section className={`space-y-5 rounded-lg border p-5 ${decisionClassMap[decision.decision]}`}>
            <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div>
                    <span className="text-xs font-semibold uppercase text-muted-foreground">Policy decision</span>
                    <h3 className="mt-1 text-2xl font-semibold">{decision.decision}</h3>
                    <p className="text-sm text-muted-foreground">Primary signal: <strong>{primaryReason}</strong></p>
                </div>
                <button className="rounded-md border bg-white px-4 py-2 text-sm font-medium" onClick={() => exportDecision(decision)}>
                    Export Decision (JSON)
                </button>
            </div>

            <div className="flex flex-col gap-4 md:flex-row md:items-center">
                <svg className={`h-28 w-28 ${riskClass}`} viewBox="0 0 120 120" role="img" aria-label={`Risk score ${decision.risk_score.toFixed(1)} out of 100`}>
                    <defs>
                        <linearGradient id="risk-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#22c55e" />
                            <stop offset="50%" stopColor="#f59e0b" />
                            <stop offset="100%" stopColor="#ef4444" />
                        </linearGradient>
                    </defs>
                    <circle className="stroke-white/80" cx="60" cy="60" r="48" pathLength="100" fill="none" strokeWidth="12" />
                    <circle className="stroke-current" cx="60" cy="60" r="48" pathLength="100" fill="none" strokeWidth="12" strokeLinecap="round" strokeDasharray="100" strokeDashoffset={100 - clampedRisk} transform="rotate(-90 60 60)" />
                    <text className="fill-current text-2xl font-semibold" x="60" y="67" textAnchor="middle">{decision.risk_score.toFixed(0)}</text>
                </svg>
                <div>
                    <span className="text-xs font-semibold uppercase text-muted-foreground">Risk score</span>
                    <strong className="block text-2xl">{decision.risk_score.toFixed(1)} / 100</strong>
                    <p className="text-sm text-muted-foreground">The score summarizes invariant violations, governance signals, finality, caps, and replay risk.</p>
                </div>
            </div>

            <div>
                <span className="text-xs font-semibold uppercase text-muted-foreground">Reason codes</span>
                <div className="mt-2 flex flex-wrap gap-2">
                    {decision.reason_codes.length > 0
                        ? decision.reason_codes.map(code => <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${getReasonClass(code)}`} key={code}>{code}</span>)
                        : <span className="rounded-full bg-muted px-2.5 py-1 text-xs font-semibold">NONE</span>}
                </div>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
                <div className="rounded-md bg-white/80 p-3">
                    <h4 className="text-sm font-semibold">Explanation</h4>
                    <p className="mt-1 text-sm text-muted-foreground">{decision.explanation}</p>
                </div>
                <div className="rounded-md bg-white/80 p-3">
                    <h4 className="text-sm font-semibold">Recommended action</h4>
                    <p className="mt-1 text-sm text-muted-foreground">{decision.recommended_action}</p>
                </div>
            </div>
        </section>
    );
};

export default PolicyDecisionCard;
