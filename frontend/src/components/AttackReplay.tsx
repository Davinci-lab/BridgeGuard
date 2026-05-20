import React, { useState, useEffect } from 'react';
import { fetchAttacks, getApiErrorMessage, simulateAttack } from '../api';
import { Attack, DecisionRecord } from '../types';
import PolicyDecisionCard from './PolicyDecisionCard';

const AttackReplay: React.FC = () => {
    const [attacks, setAttacks] = useState<Attack[]>([]);
    const [selected, setSelected] = useState<string>('');
    const [result, setResult] = useState<DecisionRecord | null>(null);
    const [error, setError] = useState<string>('');
    const selectedAttack = attacks.find(a => a.name === selected);

    useEffect(() => {
        fetchAttacks()
            .then(res => {
                setAttacks(res.data);
                setError('');
            })
            .catch(err => setError(getApiErrorMessage(err)));
    }, []);

    const handleReplay = async () => {
        if (!selected) return;
        try {
            const res = await simulateAttack(selected);
            setResult(res.data);
            setError('');
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    return (
        <section className="space-y-4 rounded-lg border bg-card p-5">
            <h2 className="text-lg font-semibold">Historical Incident Replay</h2>
            <p className="text-sm text-muted-foreground">
                Select a public bridge incident and replay it as a defensive simulation.
            </p>

            <div className="flex flex-wrap gap-3">
                <select className="h-10 min-w-64 rounded-md border border-input bg-white px-3 text-sm" value={selected} onChange={e => setSelected(e.target.value)}>
                    <option value="">Select historical incident</option>
                    {attacks.map(a => <option key={a.name} value={a.name}>{a.name}</option>)}
                </select>
                <button className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:opacity-50" onClick={handleReplay} disabled={!selected}>
                    Replay and Evaluate
                </button>
            </div>

            {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}

            {selectedAttack && (
                <article className="space-y-4 rounded-lg border bg-white p-4">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                        <h3 className="text-base font-semibold">{selectedAttack.name}</h3>
                        <span className="rounded-full bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-900">Expected: {selectedAttack.expected_decision}</span>
                    </div>
                    <div className="grid gap-3 md:grid-cols-4">
                        <div>
                            <span className="block text-xs font-semibold uppercase text-muted-foreground">Date</span>
                            <span className="text-sm">{selectedAttack.date}</span>
                        </div>
                        <div>
                            <span className="block text-xs font-semibold uppercase text-muted-foreground">Estimated loss</span>
                            <span className="text-sm">{selectedAttack.loss}</span>
                        </div>
                        <div>
                            <span className="block text-xs font-semibold uppercase text-muted-foreground">Bridge type</span>
                            <span className="text-sm">{selectedAttack.bridge_type}</span>
                        </div>
                        <div>
                            <span className="block text-xs font-semibold uppercase text-muted-foreground">Root cause category</span>
                            <span className="text-sm">{selectedAttack.root_cause_category}</span>
                        </div>
                    </div>
                    <p className="text-sm text-muted-foreground">{selectedAttack.summary}</p>
                    <div className="rounded-md bg-muted p-3">
                        <h4 className="text-sm font-semibold">Defensive control under test</h4>
                        <p className="mt-1 text-sm text-muted-foreground">{selectedAttack.defensive_control}</p>
                    </div>
                    {selectedAttack.source && (
                        <a className="text-sm font-medium text-primary underline-offset-4 hover:underline" href={selectedAttack.source} target="_blank" rel="noreferrer">
                            Open public incident source
                        </a>
                    )}
                </article>
            )}

            <PolicyDecisionCard decision={result} />
        </section>
    );
};

export default AttackReplay;
