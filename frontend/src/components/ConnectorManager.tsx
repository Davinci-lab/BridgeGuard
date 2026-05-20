import React, { useEffect, useState } from 'react';
import {
    createConnector,
    deleteConnector,
    discoverConnector,
    evaluateConnector,
    fetchConnectorPresets,
    fetchConnectors,
    getApiErrorMessage,
} from '../api';
import { ConnectorConfig, ConnectorEvaluationResult } from '../types';

const emptyConnector: ConnectorConfig = {
    id: '',
    name: 'Demo EVM Bridge',
    type: 'evm',
    enabled: true,
    rpc_url: 'mock://local',
    chain_id: 1,
    contract_address: '0x0000000000000000000000000000000000000000',
    abi: [],
    method_mapping: {
        locked_collateral: 'totalLocked',
        minted_supply: 'totalMinted',
        burned_proven: 'totalBurned',
        released_supply: 'totalReleased',
    },
    daily_cap: 1000000,
    route_cap: 500000,
    asset_cap: 2000000,
    source_chain: 'Ethereum',
    dest_chain: 'Arbitrum',
    asset: 'ETH',
    finality_blocks: 10,
};

const ConnectorManager: React.FC = () => {
    const [connectors, setConnectors] = useState<ConnectorConfig[]>([]);
    const [form, setForm] = useState<ConnectorConfig>(emptyConnector);
    const [abiText, setAbiText] = useState<string>('[]');
    const [configText, setConfigText] = useState<string>('');
    const [discoveryKey, setDiscoveryKey] = useState<string>('');
    const [result, setResult] = useState<ConnectorEvaluationResult | null>(null);
    const [error, setError] = useState<string>('');
    const [status, setStatus] = useState<string>('');

    const loadConnectors = () => {
        fetchConnectors()
            .then(res => {
                setConnectors(res.data);
                setError('');
            })
            .catch(err => setError(getApiErrorMessage(err)));
    };

    useEffect(() => {
        loadConnectors();
    }, []);

    const updateField = (key: keyof ConnectorConfig, value: string | number | boolean) => {
        setForm(prev => ({ ...prev, [key]: value }));
    };

    const handleCreate = async () => {
        try {
            const connector = configText.trim()
                ? JSON.parse(configText)
                : { ...form, id: '', abi: JSON.parse(abiText) };
            await createConnector({ ...connector, id: connector.id ?? '' });
            setResult(null);
            setError('');
            setStatus('Connector stored locally.');
            loadConnectors();
        } catch (err) {
            setError(err instanceof Error ? err.message : getApiErrorMessage(err));
        }
    };

    const handleDiscover = async () => {
        try {
            const res = await discoverConnector({
                chain_id: form.chain_id,
                contract_address: form.contract_address,
                api_key: discoveryKey.trim() || null,
            });
            setForm(prev => ({
                ...prev,
                abi: res.data.abi,
                method_mapping: res.data.method_mapping,
            }));
            setAbiText(JSON.stringify(res.data.abi, null, 2));
            setStatus(res.data.verified ? 'Discovery loaded verified ABI mapping.' : res.data.warning || 'No verified ABI found.');
            setError('');
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    const connectorKey = (connector: ConnectorConfig) =>
        `${connector.name.toLowerCase()}|${connector.chain_id}|${connector.contract_address.toLowerCase()}`;

    const handleLoadPresets = async () => {
        try {
            const [existingRes, presetsRes] = await Promise.all([fetchConnectors(), fetchConnectorPresets()]);
            const existingKeys = new Set(existingRes.data.map(connectorKey));
            const missing = presetsRes.data.filter(preset => !existingKeys.has(connectorKey(preset)));

            for (const preset of missing) {
                await createConnector({ ...preset, id: '' });
            }

            setResult(null);
            setError('');
            setStatus(missing.length === 0 ? 'Preset connectors are already loaded.' : `Loaded ${missing.length} preset connector(s).`);
            loadConnectors();
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    const handleEvaluate = async (id: string) => {
        try {
            const res = await evaluateConnector(id);
            setResult(res.data);
            setError('');
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    const handleDelete = async (id: string) => {
        try {
            await deleteConnector(id);
            setResult(null);
            setStatus('Connector deleted.');
            loadConnectors();
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    return (
        <section className="card connector-manager">
            <h2 className="section-title">Plug-and-Play Connectors</h2>
            <p className="section-subtitle">
                Configure local EVM bridge read-only connectors and evaluate them through the same defensive policy engine.
            </p>
            <div className="controls-row connector-toolbar">
                <button className="secondary-button" onClick={handleLoadPresets}>Load preset connectors</button>
                <button className="secondary-button" onClick={loadConnectors}>Refresh</button>
            </div>

            {error && <p className="error">{error}</p>}
            {status && <p className="status-message">{status}</p>}

            <div className="connector-grid">
                <div className="connector-form">
                    <textarea
                        className="text-area"
                        value={configText}
                        onChange={e => setConfigText(e.target.value)}
                        rows={8}
                        placeholder="Paste a full ConnectorConfig JSON here, or use the fields below."
                    />
                    <input className="text-input" value={form.name} onChange={e => updateField('name', e.target.value)} placeholder="Connector name" />
                    <input className="text-input" value={form.rpc_url} onChange={e => updateField('rpc_url', e.target.value)} placeholder="RPC URL" />
                    <input className="text-input" value={form.contract_address} onChange={e => updateField('contract_address', e.target.value)} placeholder="Contract address" />
                    <div className="compact-grid">
                        <input className="text-input" type="number" value={form.chain_id} onChange={e => updateField('chain_id', Number(e.target.value))} placeholder="Chain ID" />
                        <input className="text-input" value={form.asset} onChange={e => updateField('asset', e.target.value)} placeholder="Asset" />
                        <input className="text-input" value={form.source_chain} onChange={e => updateField('source_chain', e.target.value)} placeholder="Source chain" />
                        <input className="text-input" value={form.dest_chain} onChange={e => updateField('dest_chain', e.target.value)} placeholder="Destination chain" />
                    </div>
                    <textarea className="text-area" value={abiText} onChange={e => setAbiText(e.target.value)} rows={5} placeholder="Simplified ABI JSON" />
                    <div className="controls-row">
                        <input
                            className="text-input"
                            value={discoveryKey}
                            onChange={e => setDiscoveryKey(e.target.value)}
                            placeholder="Etherscan API key (optional)"
                        />
                        <button className="secondary-button" onClick={handleDiscover}>Auto-discover</button>
                    </div>
                    <button className="primary-button" onClick={handleCreate}>{configText.trim() ? 'Import Connector JSON' : 'Create Connector'}</button>
                </div>

                <div className="connector-list">
                    {connectors.length === 0 ? (
                        <p className="muted">No connectors configured yet. Create a mock connector to test the workflow.</p>
                    ) : connectors.map(connector => (
                        <article className="history-card" key={connector.id}>
                            <strong>{connector.name}</strong>
                            <p>{connector.source_chain} to {connector.dest_chain} | {connector.asset}</p>
                            <p>Chain ID: {connector.chain_id}</p>
                            <p className="connector-address">{connector.contract_address}</p>
                            <div className="controls-row">
                                <button className="secondary-button" onClick={() => handleEvaluate(connector.id)}>Evaluate</button>
                                <button className="secondary-button danger-button" onClick={() => handleDelete(connector.id)}>Delete</button>
                            </div>
                        </article>
                    ))}
                </div>
            </div>

            {result && (
                <article className="text-panel connector-result">
                    <h4>Connector Evaluation Result</h4>
                    <p><strong>Decision:</strong> {result.decision}</p>
                    <p><strong>Risk score:</strong> {result.risk_score.toFixed(1)}</p>
                    <div className="badge-list">
                        {result.reason_codes.map(code => <span className="badge" key={code}>{code}</span>)}
                    </div>
                    {result.warning && <p className="muted">{result.warning}</p>}
                </article>
            )}
        </section>
    );
};

export default ConnectorManager;
