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
        <section className="space-y-4 rounded-lg border bg-card p-5">
            <h2 className="text-lg font-semibold">Recent Decision History</h2>
            <p className="text-sm text-muted-foreground">The five most recent local policy decisions recorded by the backend.</p>
            {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
            {decisions.length === 0 ? (
                <p className="text-sm text-muted-foreground">No decisions recorded yet. Run an incident replay to populate this section.</p>
            ) : (
                <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
                    {decisions.map(decision => (
                        <article className="rounded-lg border bg-white p-3" key={decision.id}>
                            <strong>{decision.decision}</strong>
                            <p className="text-xs text-muted-foreground">{new Date(decision.timestamp).toLocaleString()}</p>
                            <p className="text-sm">Score: {decision.risk_score.toFixed(1)}</p>
                            <span className="mt-2 inline-flex rounded-full bg-muted px-2.5 py-1 text-xs font-medium">{decision.reason_codes[0] ?? 'None'}</span>
                        </article>
                    ))}
                </div>
            )}
        </section>
    );
};

export default DecisionHistory;
