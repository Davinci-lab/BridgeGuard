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
                <h1>CarthEdge BridgeGuard</h1>
                <p>Runtime security kernel for simulated cross-chain bridge decisions.</p>
            </header>
            <div className="dashboard-grid">
                <RiskPanel />
                <AttackReplay />
                <ReasonCodesTable />
                <DecisionHistory />
                <ConnectorManager />
            </div>
        </main>
    );
};

export default Dashboard;
