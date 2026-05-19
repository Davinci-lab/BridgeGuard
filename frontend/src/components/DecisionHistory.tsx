import React, { useEffect, useState } from 'react';
import { fetchDecisions, getApiErrorMessage } from '../api';
import { DecisionRecord } from '../types';

const DecisionHistory: React.FC = () => {
    const [decisions, setDecisions] = useState<DecisionRecord[]>([]);
    const [error, setError] = useState<string>('');

    useEffect(() => {
        fetchDecisions()
            .then(res => {
                setDecisions(res.data.slice(-5).reverse());
                setError('');
            })
            .catch(err => setError(getApiErrorMessage(err)));
    }, []);

    return (
        <section className="card">
            <h2 className="section-title">Recent Decision History</h2>
            <p className="section-subtitle">The five most recent local policy decisions recorded by the backend.</p>
            {error && <p className="error">{error}</p>}
            {decisions.length === 0 ? (
                <p className="muted">No decisions recorded yet. Run an incident replay to populate this section.</p>
            ) : (
                <div className="history-grid">
                    {decisions.map(decision => (
                        <article className="history-card" key={decision.id}>
                            <strong>{decision.decision}</strong>
                            <p>{new Date(decision.timestamp).toLocaleString()}</p>
                            <p>Score: {decision.risk_score.toFixed(1)}</p>
                            <span className="badge">{decision.reason_codes[0] ?? 'None'}</span>
                        </article>
                    ))}
                </div>
            )}
        </section>
    );
};

export default DecisionHistory;
