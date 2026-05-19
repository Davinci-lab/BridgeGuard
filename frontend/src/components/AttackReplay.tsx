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
        <section className="card">
            <h2 className="section-title">Historical Incident Replay</h2>
            <p className="section-subtitle">
                Select a public bridge incident and replay it as a defensive simulation.
            </p>

            <div className="controls-row">
                <select className="select-input" value={selected} onChange={e => setSelected(e.target.value)}>
                    <option value="">Select historical incident</option>
                    {attacks.map(a => <option key={a.name} value={a.name}>{a.name}</option>)}
                </select>
                <button className="primary-button" onClick={handleReplay} disabled={!selected}>
                    Replay and Evaluate
                </button>
            </div>

            {error && <p className="error">{error}</p>}

            {selectedAttack && (
                <article className="card incident-card">
                    <div className="incident-title-row">
                        <h3 className="section-title">{selectedAttack.name}</h3>
                        <span className="badge reason-medium">Expected: {selectedAttack.expected_decision}</span>
                    </div>
                    <div className="incident-grid">
                        <div>
                            <span className="detail-label">Date</span>
                            <span className="detail-value">{selectedAttack.date}</span>
                        </div>
                        <div>
                            <span className="detail-label">Estimated loss</span>
                            <span className="detail-value">{selectedAttack.loss}</span>
                        </div>
                        <div>
                            <span className="detail-label">Bridge type</span>
                            <span className="detail-value">{selectedAttack.bridge_type}</span>
                        </div>
                        <div>
                            <span className="detail-label">Root cause category</span>
                            <span className="detail-value">{selectedAttack.root_cause_category}</span>
                        </div>
                    </div>
                    <p>{selectedAttack.summary}</p>
                    <div className="text-panel">
                        <h4>Defensive control under test</h4>
                        <p>{selectedAttack.defensive_control}</p>
                    </div>
                    {selectedAttack.source && (
                        <a href={selectedAttack.source} target="_blank" rel="noreferrer">
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
