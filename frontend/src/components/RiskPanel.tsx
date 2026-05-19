import React, { useEffect, useState } from 'react';
import { fetchMetrics, getApiErrorMessage } from '../api';
import { Metrics, RiskScoreDistribution } from '../types';

const riskBands: Array<{ key: keyof RiskScoreDistribution; label: string; className: string }> = [
    { key: 'low', label: 'Low', className: 'risk-low' },
    { key: 'medium', label: 'Medium', className: 'risk-medium' },
    { key: 'high', label: 'High', className: 'risk-high' },
    { key: 'critical', label: 'Critical', className: 'risk-critical' },
];

const getWidthClass = (value: number, max: number) => {
    const percent = max > 0 ? Math.round((value / max) * 20) * 5 : 0;
    return `bar-width-${Math.max(0, Math.min(percent, 100))}`;
};

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

    if (error) return <section className="card"><p className="error">{error}</p></section>;
    if (!metrics) return <section className="card"><p className="muted">Loading risk metrics...</p></section>;

    const maxBandCount = Math.max(...riskBands.map(band => metrics.risk_score_distribution[band.key]), 1);

    return (
        <section className="card">
            <h2 className="section-title">Risk Metrics</h2>
            <div className="metric-summary">
                <div className="metric-pill">
                    <span className="detail-label">Total simulations</span>
                    <strong>{metrics.total_simulations}</strong>
                </div>
            </div>

            <h3 className="section-title">Risk distribution</h3>
            <div className="distribution-list">
                {riskBands.map(band => {
                    const value = metrics.risk_score_distribution[band.key];
                    return (
                        <div className="distribution-row" key={band.key}>
                            <span>{band.label}</span>
                            <div className="distribution-track">
                                <div className={`distribution-fill ${band.className} ${getWidthClass(value, maxBandCount)}`} />
                            </div>
                            <strong>{value}</strong>
                        </div>
                    );
                })}
            </div>

            <h3 className="section-title section-title-spaced">Top reason codes</h3>
            {metrics.top_reason_codes.length > 0 ? (
                <ul className="reason-list">
                    {metrics.top_reason_codes.map(reason => (
                        <li key={reason.code}>
                            <strong>{reason.code}</strong> <span className="muted">({reason.count})</span>
                        </li>
                    ))}
                </ul>
            ) : (
                <p className="muted">No reason codes have been recorded yet.</p>
            )}
        </section>
    );
};

export default RiskPanel;
