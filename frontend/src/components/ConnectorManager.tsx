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
        <section className="space-y-4 rounded-lg border bg-card p-5">
            <h2 className="text-lg font-semibold">Plug-and-Play Connectors</h2>
            <p className="text-sm text-muted-foreground">
                Configure local EVM bridge read-only connectors and evaluate them through the same defensive policy engine.
            </p>
            <div className="flex flex-wrap gap-3">
                <button className="rounded-md border bg-white px-4 py-2 text-sm font-medium" onClick={handleLoadPresets}>Load preset connectors</button>
                <button className="rounded-md border bg-white px-4 py-2 text-sm font-medium" onClick={loadConnectors}>Refresh</button>
            </div>

            {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
            {status && <p className="rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-800">{status}</p>}

            <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_390px]">
                <div className="space-y-3">
                    <textarea
                        className="min-h-32 w-full rounded-md border border-input bg-white px-3 py-2 text-sm"
                        value={configText}
                        onChange={e => setConfigText(e.target.value)}
                        rows={8}
                        placeholder="Paste a full ConnectorConfig JSON here, or use the fields below."
                    />
                    <input className="h-10 w-full rounded-md border border-input bg-white px-3 text-sm" value={form.name} onChange={e => updateField('name', e.target.value)} placeholder="Connector name" />
                    <input className="h-10 w-full rounded-md border border-input bg-white px-3 text-sm" value={form.rpc_url} onChange={e => updateField('rpc_url', e.target.value)} placeholder="RPC URL" />
                    <input className="h-10 w-full rounded-md border border-input bg-white px-3 text-sm" value={form.contract_address} onChange={e => updateField('contract_address', e.target.value)} placeholder="Contract address" />
                    <div className="grid gap-3 md:grid-cols-4">
                        <input className="h-10 w-full rounded-md border border-input bg-white px-3 text-sm" type="number" value={form.chain_id} onChange={e => updateField('chain_id', Number(e.target.value))} placeholder="Chain ID" />
                        <input className="h-10 w-full rounded-md border border-input bg-white px-3 text-sm" value={form.asset} onChange={e => updateField('asset', e.target.value)} placeholder="Asset" />
                        <input className="h-10 w-full rounded-md border border-input bg-white px-3 text-sm" value={form.source_chain} onChange={e => updateField('source_chain', e.target.value)} placeholder="Source chain" />
                        <input className="h-10 w-full rounded-md border border-input bg-white px-3 text-sm" value={form.dest_chain} onChange={e => updateField('dest_chain', e.target.value)} placeholder="Destination chain" />
                    </div>
                    <textarea className="min-h-28 w-full rounded-md border border-input bg-white px-3 py-2 text-sm" value={abiText} onChange={e => setAbiText(e.target.value)} rows={5} placeholder="Simplified ABI JSON" />
                    <div className="flex flex-wrap gap-3">
                        <input
                            className="h-10 min-w-64 flex-1 rounded-md border border-input bg-white px-3 text-sm"
                            value={discoveryKey}
                            onChange={e => setDiscoveryKey(e.target.value)}
                            placeholder="Etherscan API key (optional)"
                        />
                        <button className="rounded-md border bg-white px-4 py-2 text-sm font-medium" onClick={handleDiscover}>Auto-discover</button>
                    </div>
                    <button className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground" onClick={handleCreate}>{configText.trim() ? 'Import Connector JSON' : 'Create Connector'}</button>
                </div>

                <div className="space-y-3">
                    {connectors.length === 0 ? (
                        <p className="text-sm text-muted-foreground">No connectors configured yet. Create a mock connector to test the workflow.</p>
                    ) : connectors.map(connector => (
                        <article className="space-y-2 rounded-lg border bg-white p-4" key={connector.id}>
                            <strong>{connector.name}</strong>
                            <p className="text-sm text-muted-foreground">{connector.source_chain} to {connector.dest_chain} | {connector.asset}</p>
                            <p className="text-sm">Chain ID: {connector.chain_id}</p>
                            <p className="break-all text-xs text-muted-foreground">{connector.contract_address}</p>
                            <div className="flex flex-wrap gap-2">
                                <button className="rounded-md border bg-white px-3 py-2 text-sm font-medium" onClick={() => handleEvaluate(connector.id)}>Evaluate</button>
                                <button className="rounded-md bg-destructive px-3 py-2 text-sm font-medium text-destructive-foreground" onClick={() => handleDelete(connector.id)}>Delete</button>
                            </div>
                        </article>
                    ))}
                </div>
            </div>

            {result && (
                <article className="space-y-3 rounded-lg border bg-muted/50 p-4">
                    <h4 className="font-semibold">Connector Evaluation Result</h4>
                    <p className="text-sm"><strong>Decision:</strong> {result.decision}</p>
                    <p className="text-sm"><strong>Risk score:</strong> {result.risk_score.toFixed(1)}</p>
                    <div className="flex flex-wrap gap-2">
                        {result.reason_codes.map(code => <span className="rounded-full bg-white px-2.5 py-1 text-xs font-medium" key={code}>{code}</span>)}
                    </div>
                    {result.warning && <p className="text-sm text-muted-foreground">{result.warning}</p>}
                </article>
            )}
        </section>
    );
};

export default ConnectorManager;
