import React, { useEffect, useState } from 'react';
import { fetchMetrics, getApiErrorMessage } from '../api';
import { Metrics, RiskScoreDistribution } from '../types';

const riskBands: Array<{ key: keyof RiskScoreDistribution; label: string; className: string }> = [
    { key: 'low', label: 'Low', className: 'bg-emerald-500' },
    { key: 'medium', label: 'Medium', className: 'bg-amber-500' },
    { key: 'high', label: 'High', className: 'bg-orange-500' },
    { key: 'critical', label: 'Critical', className: 'bg-red-500' },
];

const getWidth = (value: number, max: number) => `${Math.max(0, Math.min(max > 0 ? (value / max) * 100 : 0, 100))}%`;

const RiskPanel: React.FC = () => {
    const [metrics, setMetrics] = useState<Metrics | null>(null);
    const [error, setError] = useState<string>('');

    useEffect(() => {
        fetchMetrics()
            .then(res => {
                setMetrics(res.data);
                setError('');
            })
            .catch(err => setError(getApiErrorMessage(err)));
    }, []);

    if (error) return <section className="rounded-lg border bg-card p-5"><p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p></section>;
    if (!metrics) return <section className="rounded-lg border bg-card p-5"><p className="text-sm text-muted-foreground">Loading risk metrics...</p></section>;

    const maxBandCount = Math.max(...riskBands.map(band => metrics.risk_score_distribution[band.key]), 1);

    return (
        <section className="space-y-4 rounded-lg border bg-card p-5">
            <h2 className="text-lg font-semibold">Risk Metrics</h2>
            <div className="rounded-md border bg-white p-3">
                <span className="block text-xs font-semibold uppercase text-muted-foreground">Total simulations</span>
                <strong className="text-2xl">{metrics.total_simulations}</strong>
            </div>

            <h3 className="text-base font-semibold">Risk distribution</h3>
            <div className="space-y-3">
                {riskBands.map(band => {
                    const value = metrics.risk_score_distribution[band.key];
                    return (
                        <div className="grid grid-cols-[80px_1fr_40px] items-center gap-3 text-sm" key={band.key}>
                            <span>{band.label}</span>
                            <div className="h-2 overflow-hidden rounded-full bg-muted">
                                <div className={`h-full rounded-full ${band.className}`} style={{ width: getWidth(value, maxBandCount) }} />
                            </div>
                            <strong>{value}</strong>
                        </div>
                    );
                })}
            </div>

            <h3 className="text-base font-semibold">Top reason codes</h3>
            {metrics.top_reason_codes.length > 0 ? (
                <ul className="space-y-2 text-sm">
                    {metrics.top_reason_codes.map(reason => (
                        <li key={reason.code}>
                            <strong>{reason.code}</strong> <span className="text-muted-foreground">({reason.count})</span>
                        </li>
                    ))}
                </ul>
            ) : (
                <p className="text-sm text-muted-foreground">No reason codes have been recorded yet.</p>
            )}
        </section>
    );
};

export default RiskPanel;
