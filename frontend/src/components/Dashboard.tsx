import React from 'react';
import AttackReplay from './AttackReplay';
import RiskPanel from './RiskPanel';
import ReasonCodesTable from './ReasonCodesTable';
import DecisionHistory from './DecisionHistory';
import ConnectorManager from './ConnectorManager';

const Dashboard: React.FC = () => {
    return (
        <main className="space-y-5">
            <header className="space-y-2">
                <p className="text-xs font-semibold uppercase text-muted-foreground">Defensive bridge runtime monitoring</p>
                <h1 className="text-2xl font-semibold tracking-normal">BridgeGuard</h1>
                <p className="text-sm text-muted-foreground">Runtime Security Kernel for Cross-Chain Bridges</p>
            </header>
            <div className="grid gap-5">
                <section className="grid gap-4 rounded-lg border bg-muted/50 p-4 md:grid-cols-2">
                    <div>
                        <span className="text-xs font-semibold uppercase text-muted-foreground">Client demo focus</span>
                        <strong className="mt-1 block text-sm">Replay public bridge incidents, inspect policy decisions, and test read-only connector configurations.</strong>
                    </div>
                    <div>
                        <span className="text-xs font-semibold uppercase text-muted-foreground">Safety boundary</span>
                        <strong className="mt-1 block text-sm">No private keys, no transaction signing, no exploit payloads.</strong>
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
