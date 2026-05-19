import React from 'react';
import AttackReplay from './AttackReplay';
import RiskPanel from './RiskPanel';
import ReasonCodesTable from './ReasonCodesTable';
import DecisionHistory from './DecisionHistory';
import ConnectorManager from './ConnectorManager';

const Dashboard: React.FC = () => {
    return (
        <main className="dashboard">
            <header className="dashboard-header">
                <p className="eyebrow">Defensive bridge runtime monitoring</p>
                <h1>BridgeGuard</h1>
                <p>Runtime Security Kernel for Cross-Chain Bridges</p>
            </header>
            <div className="dashboard-grid">
                <section className="hero-strip">
                    <div>
                        <span className="detail-label">Client demo focus</span>
                        <strong>Replay public bridge incidents, inspect policy decisions, and test read-only connector configurations.</strong>
                    </div>
                    <div>
                        <span className="detail-label">Safety boundary</span>
                        <strong>No private keys, no transaction signing, no exploit payloads.</strong>
                    </div>
                </section>
                <AttackReplay />
                <RiskPanel />
                <ConnectorManager />
                <DecisionHistory />
                <ReasonCodesTable />
            </div>
        </main>
    );
};

export default Dashboard;
