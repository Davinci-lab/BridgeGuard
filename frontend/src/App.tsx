import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
    Bell,
    ChevronDown,
    Gauge,
    History,
    LogOut,
    Play,
    Plus,
    RefreshCcw,
    ShieldCheck,
    SlidersHorizontal,
    Trash2,
    Wand2,
} from 'lucide-react';
import {
    createAlertRule,
    createProject,
    createV2Connector,
    deleteAlertRule,
    deleteProject,
    deleteV2Connector,
    discoverConnector,
    fetchAlertRules,
    fetchMe,
    fetchPolicy,
    fetchProjects,
    fetchV2Connectors,
    fetchV2Decisions,
    getApiErrorMessage,
    getStoredToken,
    loginUser,
    registerUser,
    setStoredToken,
    simulateTransferV2,
    startListener,
    stopListener,
    testAlertRule,
    updatePolicy,
} from './api';
import Dashboard from './components/Dashboard';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from './components/ui/dialog';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from './components/ui/dropdown-menu';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './components/ui/table';
import {
    AlertChannel,
    AlertCondition,
    AlertRule,
    ConnectorConfig,
    CustomRule,
    DecisionRecord,
    ListenerRecord,
    PolicyConfig,
    Project,
    TransferSimulation,
    User,
} from './types';

type View = 'overview' | 'simulate' | 'connectors' | 'alerts' | 'policy' | 'legacy';
type AuthMode = 'login' | 'register';

const inputClass =
    'h-10 w-full rounded-md border border-input bg-white px-3 text-sm outline-none transition focus:ring-2 focus:ring-ring';
const textareaClass =
    'min-h-24 w-full rounded-md border border-input bg-white px-3 py-2 text-sm outline-none transition focus:ring-2 focus:ring-ring';
const labelClass = 'text-xs font-semibold uppercase text-muted-foreground';

const defaultSimulation: TransferSimulation = {
    source_chain: 'Ethereum',
    dest_chain: 'Arbitrum',
    asset: 'ETH',
    amount: 1250,
    signer_count: 3,
    required_signers: 5,
    finality_blocks: 12,
    current_block: 120,
    tx_block: 114,
    is_duplicate: false,
    emergency_mode: false,
    config_change_cooled: true,
    locked_collateral: 1000000,
    minted_supply: 980000,
    burned_proven: 12000,
    released_supply: 11000,
    daily_volume: 450000,
    daily_cap: 1000000,
    route_volume: 125000,
    route_cap: 500000,
    asset_cap: 2000000,
    total_inflow: 1025000,
    total_outflow: 1012000,
    known_message_hash: null,
};

const emptyConnector: ConnectorConfig = {
    id: '',
    name: 'Production Bridge Watcher',
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
    finality_blocks: 12,
};

const emptyPolicy: PolicyConfig = {
    project_id: 0,
    risk_weights: {
        collateralization: 1,
        caps: 1,
        finality: 1,
        replay: 1,
        governance: 1,
    },
    custom_rules: [],
};

const navItems: Array<{ id: View; label: string; icon: React.ComponentType<{ className?: string }> }> = [
    { id: 'overview', label: 'Overview', icon: Gauge },
    { id: 'simulate', label: 'Simulate', icon: Play },
    { id: 'connectors', label: 'Connectors', icon: Wand2 },
    { id: 'alerts', label: 'Alerts', icon: Bell },
    { id: 'policy', label: 'Policy', icon: SlidersHorizontal },
    { id: 'legacy', label: 'v1 Tools', icon: History },
];

const badgeClass = (decision: string) => {
    if (decision === 'ALLOW') return 'bg-emerald-100 text-emerald-800';
    if (decision === 'DELAY' || decision === 'REQUIRE_EXTRA_SIGNATURES') return 'bg-amber-100 text-amber-900';
    return 'bg-red-100 text-red-800';
};

const formatNumber = (value: number | undefined | null) =>
    typeof value === 'number' ? value.toLocaleString(undefined, { maximumFractionDigits: 1 }) : '0';

const parseJsonObject = (text: string): Record<string, unknown> => {
    const parsed = JSON.parse(text);
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
        throw new Error('Configuration must be a JSON object.');
    }
    return parsed as Record<string, unknown>;
};

const AuthScreen: React.FC<{ onAuthenticated: (token: string) => void }> = ({ onAuthenticated }) => {
    const [mode, setMode] = useState<AuthMode>('login');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [projectName, setProjectName] = useState('Default Project');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const submit = async (event: React.FormEvent) => {
        event.preventDefault();
        setLoading(true);
        setError('');
        try {
            if (mode === 'register') {
                await registerUser(email, password, projectName);
            }
            const res = await loginUser(email, password);
            setStoredToken(res.data.access_token);
            onAuthenticated(res.data.access_token);
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="flex min-h-screen items-center justify-center bg-background px-4 py-8">
            <Card className="w-full max-w-md">
                <CardHeader>
                    <div className="mb-2 flex h-11 w-11 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                        <ShieldCheck className="h-6 w-6" />
                    </div>
                    <CardTitle>BridgeGuard operator console</CardTitle>
                    <CardDescription>Sign in to manage v2 projects, policies, connectors, and alerts.</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="mb-5 grid grid-cols-2 rounded-md border bg-muted p-1">
                        <button
                            className={`rounded px-3 py-2 text-sm font-medium ${mode === 'login' ? 'bg-white shadow-sm' : 'text-muted-foreground'}`}
                            onClick={() => setMode('login')}
                            type="button"
                        >
                            Login
                        </button>
                        <button
                            className={`rounded px-3 py-2 text-sm font-medium ${mode === 'register' ? 'bg-white shadow-sm' : 'text-muted-foreground'}`}
                            onClick={() => setMode('register')}
                            type="button"
                        >
                            Register
                        </button>
                    </div>
                    <form className="space-y-4" onSubmit={submit}>
                        <label className="block space-y-1.5">
                            <span className={labelClass}>Email</span>
                            <input className={inputClass} value={email} onChange={e => setEmail(e.target.value)} type="email" required />
                        </label>
                        <label className="block space-y-1.5">
                            <span className={labelClass}>Password</span>
                            <input className={inputClass} value={password} onChange={e => setPassword(e.target.value)} type="password" required minLength={8} />
                        </label>
                        {mode === 'register' && (
                            <label className="block space-y-1.5">
                                <span className={labelClass}>Initial project</span>
                                <input className={inputClass} value={projectName} onChange={e => setProjectName(e.target.value)} required />
                            </label>
                        )}
                        {error && <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
                        <Button className="w-full" disabled={loading} type="submit">
                            {loading ? 'Working...' : mode === 'login' ? 'Login' : 'Create account'}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </main>
    );
};

const DecisionTable: React.FC<{ decisions: DecisionRecord[] }> = ({ decisions }) => (
    <Table>
        <TableHeader>
            <TableRow>
                <TableHead>Decision</TableHead>
                <TableHead>Risk</TableHead>
                <TableHead>Route</TableHead>
                <TableHead>When</TableHead>
            </TableRow>
        </TableHeader>
        <TableBody>
            {decisions.map(decision => (
                <TableRow key={decision.id}>
                    <TableCell>
                        <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${badgeClass(decision.decision)}`}>
                            {decision.decision}
                        </span>
                    </TableCell>
                    <TableCell>{formatNumber(decision.risk_score)}</TableCell>
                    <TableCell>
                        {decision.simulation.source_chain} to {decision.simulation.dest_chain}
                    </TableCell>
                    <TableCell>{new Date(decision.timestamp).toLocaleString()}</TableCell>
                </TableRow>
            ))}
        </TableBody>
    </Table>
);

const OverviewPanel: React.FC<{
    decisions: DecisionRecord[];
    alerts: AlertRule[];
    listeners: ListenerRecord[];
    onRefresh: () => void;
}> = ({ decisions, alerts, listeners, onRefresh }) => {
    const lastDecision = decisions[0];
    const activeAlerts = alerts.filter(alert => alert.is_active).length;
    const activeListeners = listeners.filter(listener => listener.status !== 'stopped').length;

    return (
        <div className="space-y-5">
            <div className="grid gap-4 md:grid-cols-3">
                <Card>
                    <CardHeader>
                        <CardDescription>Latest decision</CardDescription>
                        <CardTitle>{lastDecision?.decision ?? 'No decisions'}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">Risk score {formatNumber(lastDecision?.risk_score)} / 100</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader>
                        <CardDescription>Active alert rules</CardDescription>
                        <CardTitle>{activeAlerts}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">{alerts.length} configured notification path(s)</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader>
                        <CardDescription>Listener status</CardDescription>
                        <CardTitle>{activeListeners}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">{listeners.length} listener update(s) in this session</p>
                    </CardContent>
                </Card>
            </div>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between gap-3">
                    <div>
                        <CardTitle>Recent project decisions</CardTitle>
                        <CardDescription>Project-scoped v2 decisions from the backend.</CardDescription>
                    </div>
                    <Button variant="outline" size="icon" onClick={onRefresh} title="Refresh">
                        <RefreshCcw className="h-4 w-4" />
                    </Button>
                </CardHeader>
                <CardContent>
                    {decisions.length ? <DecisionTable decisions={decisions.slice(0, 8)} /> : <p className="text-sm text-muted-foreground">No decisions have been saved for this project yet.</p>}
                </CardContent>
            </Card>
        </div>
    );
};

const SimulationPanel: React.FC<{
    token: string;
    project: Project;
    onDecision: (decision: DecisionRecord) => void;
}> = ({ token, project, onDecision }) => {
    const [simulation, setSimulation] = useState<TransferSimulation>(defaultSimulation);
    const [result, setResult] = useState<DecisionRecord | null>(null);
    const [error, setError] = useState('');

    const updateField = (key: keyof TransferSimulation, value: string | number | boolean | null) => {
        setSimulation(prev => ({ ...prev, [key]: value }));
    };

    const submit = async () => {
        try {
            const res = await simulateTransferV2(token, project.id, simulation);
            setResult(res.data);
            onDecision(res.data);
            setError('');
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    const numericFields: Array<[keyof TransferSimulation, string]> = [
        ['amount', 'Amount'],
        ['signer_count', 'Signer count'],
        ['required_signers', 'Required signers'],
        ['finality_blocks', 'Finality blocks'],
        ['locked_collateral', 'Locked collateral'],
        ['minted_supply', 'Minted supply'],
        ['daily_volume', 'Daily volume'],
        ['daily_cap', 'Daily cap'],
        ['route_volume', 'Route volume'],
        ['route_cap', 'Route cap'],
        ['asset_cap', 'Asset cap'],
        ['total_inflow', 'Total inflow'],
        ['total_outflow', 'Total outflow'],
    ];

    return (
        <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
            <Card>
                <CardHeader>
                    <CardTitle>Project-scoped simulation</CardTitle>
                    <CardDescription>Runs the v2 invariant and policy engines, then stores the result under {project.name}.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-5">
                    <div className="grid gap-4 md:grid-cols-3">
                        {(['source_chain', 'dest_chain', 'asset'] as Array<keyof TransferSimulation>).map(field => (
                            <label className="space-y-1.5" key={field}>
                                <span className={labelClass}>{String(field).replace(/_/g, ' ')}</span>
                                <input className={inputClass} value={String(simulation[field] ?? '')} onChange={e => updateField(field, e.target.value)} />
                            </label>
                        ))}
                    </div>
                    <div className="grid gap-4 md:grid-cols-4">
                        {numericFields.map(([field, label]) => (
                            <label className="space-y-1.5" key={field}>
                                <span className={labelClass}>{label}</span>
                                <input
                                    className={inputClass}
                                    type="number"
                                    value={Number(simulation[field] ?? 0)}
                                    onChange={e => updateField(field, Number(e.target.value))}
                                />
                            </label>
                        ))}
                    </div>
                    <div className="grid gap-3 md:grid-cols-3">
                        {(['is_duplicate', 'emergency_mode', 'config_change_cooled'] as Array<keyof TransferSimulation>).map(field => (
                            <label className="flex items-center gap-2 rounded-md border bg-white px-3 py-2 text-sm" key={field}>
                                <input
                                    type="checkbox"
                                    checked={Boolean(simulation[field])}
                                    onChange={e => updateField(field, e.target.checked)}
                                />
                                {String(field).replace(/_/g, ' ')}
                            </label>
                        ))}
                    </div>
                    {error && <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
                    <Button onClick={submit}>
                        <Play className="h-4 w-4" />
                        Run simulation
                    </Button>
                </CardContent>
            </Card>
            <Card>
                <CardHeader>
                    <CardTitle>Decision result</CardTitle>
                    <CardDescription>Stored results appear in the project overview.</CardDescription>
                </CardHeader>
                <CardContent>
                    {result ? (
                        <div className="space-y-4">
                            <span className={`inline-flex rounded-full px-3 py-1 text-sm font-semibold ${badgeClass(result.decision)}`}>
                                {result.decision}
                            </span>
                            <div>
                                <p className={labelClass}>Risk score</p>
                                <p className="text-3xl font-semibold">{result.risk_score.toFixed(1)}</p>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {result.reason_codes.map(code => (
                                    <span className="rounded-full bg-muted px-2.5 py-1 text-xs font-medium" key={code}>{code}</span>
                                ))}
                            </div>
                            <p className="text-sm text-muted-foreground">{result.explanation}</p>
                        </div>
                    ) : (
                        <p className="text-sm text-muted-foreground">Run a simulation to see the policy decision.</p>
                    )}
                </CardContent>
            </Card>
        </div>
    );
};

const ConnectorWizard: React.FC<{
    token: string;
    project: Project;
    onListener: (listener: ListenerRecord) => void;
}> = ({ token, project, onListener }) => {
    const [connectors, setConnectors] = useState<ConnectorConfig[]>([]);
    const [form, setForm] = useState<ConnectorConfig>(emptyConnector);
    const [apiKey, setApiKey] = useState('');
    const [status, setStatus] = useState('');
    const [error, setError] = useState('');

    const load = useCallback(async () => {
        try {
            const res = await fetchV2Connectors();
            setConnectors(res.data);
            setError('');
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    }, []);

    useEffect(() => {
        load();
    }, [load]);

    const updateField = (key: keyof ConnectorConfig, value: string | number | boolean) => {
        setForm(prev => ({ ...prev, [key]: value }));
    };

    const discover = async () => {
        try {
            const res = await discoverConnector({
                chain_id: form.chain_id,
                contract_address: form.contract_address,
                api_key: apiKey.trim() || null,
            });
            setForm(prev => ({ ...prev, abi: res.data.abi, method_mapping: res.data.method_mapping }));
            setStatus(res.data.verified ? 'Verified ABI discovered and mapped.' : res.data.warning || 'Discovery completed without a verified ABI.');
            setError('');
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    const saveConnector = async () => {
        try {
            await createV2Connector({ ...form, id: '' });
            setStatus('Connector saved.');
            setError('');
            load();
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    const start = async (connector: ConnectorConfig) => {
        try {
            const res = await startListener(token, project.id, connector, 'polling');
            onListener(res.data);
            setStatus(`Listener started for ${connector.name}.`);
            setError('');
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    const stop = async (connector: ConnectorConfig) => {
        try {
            const res = await stopListener(token, project.id, connector.id);
            res.data.forEach(onListener);
            setStatus(`Listener stopped for ${connector.name}.`);
            setError('');
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    const remove = async (connector: ConnectorConfig) => {
        try {
            await deleteV2Connector(connector.id);
            setStatus('Connector deleted.');
            load();
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    return (
        <div className="grid gap-5 xl:grid-cols-[minmax(0,430px)_1fr]">
            <Card>
                <CardHeader>
                    <CardTitle>Connector wizard</CardTitle>
                    <CardDescription>Configure EVM, Solana, or Cosmos connectors and auto-discover EVM method mappings.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid gap-4 sm:grid-cols-2">
                        <label className="space-y-1.5">
                            <span className={labelClass}>Name</span>
                            <input className={inputClass} value={form.name} onChange={e => updateField('name', e.target.value)} />
                        </label>
                        <label className="space-y-1.5">
                            <span className={labelClass}>Type</span>
                            <select className={inputClass} value={form.type} onChange={e => updateField('type', e.target.value)}>
                                <option value="evm">EVM</option>
                                <option value="solana">Solana</option>
                                <option value="cosmos">Cosmos</option>
                            </select>
                        </label>
                    </div>
                    <label className="space-y-1.5">
                        <span className={labelClass}>RPC URL</span>
                        <input className={inputClass} value={form.rpc_url} onChange={e => updateField('rpc_url', e.target.value)} />
                    </label>
                    <label className="space-y-1.5">
                        <span className={labelClass}>Contract address</span>
                        <input className={inputClass} value={form.contract_address} onChange={e => updateField('contract_address', e.target.value)} />
                    </label>
                    <div className="grid gap-4 sm:grid-cols-3">
                        <label className="space-y-1.5">
                            <span className={labelClass}>Chain ID</span>
                            <input className={inputClass} type="number" value={form.chain_id} onChange={e => updateField('chain_id', Number(e.target.value))} />
                        </label>
                        <label className="space-y-1.5">
                            <span className={labelClass}>Source</span>
                            <input className={inputClass} value={form.source_chain} onChange={e => updateField('source_chain', e.target.value)} />
                        </label>
                        <label className="space-y-1.5">
                            <span className={labelClass}>Destination</span>
                            <input className={inputClass} value={form.dest_chain} onChange={e => updateField('dest_chain', e.target.value)} />
                        </label>
                    </div>
                    <Dialog>
                        <DialogTrigger asChild>
                            <Button variant="outline" className="w-full">
                                <Wand2 className="h-4 w-4" />
                                Auto-discover methods
                            </Button>
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Etherscan method discovery</DialogTitle>
                                <DialogDescription>Uses the configured chain ID and contract address to suggest method mappings when the ABI is verified.</DialogDescription>
                            </DialogHeader>
                            <label className="space-y-1.5">
                                <span className={labelClass}>Etherscan API key</span>
                                <input className={inputClass} value={apiKey} onChange={e => setApiKey(e.target.value)} placeholder="Optional for free tier" />
                            </label>
                            <Button onClick={discover}>
                                <Wand2 className="h-4 w-4" />
                                Discover mapping
                            </Button>
                        </DialogContent>
                    </Dialog>
                    <Button className="w-full" onClick={saveConnector}>
                        <Plus className="h-4 w-4" />
                        Save connector
                    </Button>
                    {status && <p className="rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-800">{status}</p>}
                    {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between gap-3">
                    <div>
                        <CardTitle>Configured connectors</CardTitle>
                        <CardDescription>Start polling listeners without changing old connector storage.</CardDescription>
                    </div>
                    <Button variant="outline" size="icon" onClick={load} title="Refresh connectors">
                        <RefreshCcw className="h-4 w-4" />
                    </Button>
                </CardHeader>
                <CardContent>
                    <div className="grid gap-3">
                        {connectors.map(connector => (
                            <div className="rounded-lg border bg-white p-4" key={connector.id || connector.name}>
                                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                                    <div>
                                        <p className="font-semibold">{connector.name}</p>
                                        <p className="text-sm text-muted-foreground">{connector.type.toUpperCase()} | {connector.source_chain} to {connector.dest_chain} | {connector.asset}</p>
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        <Button variant="outline" size="sm" onClick={() => start(connector)}>Start</Button>
                                        <Button variant="outline" size="sm" onClick={() => stop(connector)}>Stop</Button>
                                        <Button variant="destructive" size="sm" onClick={() => remove(connector)}>
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        ))}
                        {!connectors.length && <p className="text-sm text-muted-foreground">No connectors configured yet.</p>}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

const AlertRulesPanel: React.FC<{
    token: string;
    project: Project;
    alerts: AlertRule[];
    onReload: () => void;
}> = ({ token, project, alerts, onReload }) => {
    const [condition, setCondition] = useState<AlertCondition>('decision_not_allow');
    const [threshold, setThreshold] = useState(70);
    const [channel, setChannel] = useState<AlertChannel>('webhook');
    const [config, setConfig] = useState('{"url":"https://example.com/bridgeguard"}');
    const [error, setError] = useState('');
    const [status, setStatus] = useState('');

    const save = async () => {
        try {
            await createAlertRule(token, project.id, {
                condition,
                threshold: condition === 'risk_score_gt' ? threshold : null,
                channel_type: channel,
                config: parseJsonObject(config),
                is_active: true,
            });
            setStatus('Alert rule saved.');
            setError('');
            onReload();
        } catch (err) {
            setError(err instanceof Error ? err.message : getApiErrorMessage(err));
        }
    };

    const remove = async (alert: AlertRule) => {
        try {
            await deleteAlertRule(token, project.id, alert.id);
            onReload();
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    const test = async (alert: AlertRule) => {
        try {
            const res = await testAlertRule(token, project.id, alert.id);
            setStatus(res.data.sent ? `Test ${res.data.channel_type} notification sent.` : 'Notifier returned false.');
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    return (
        <div className="grid gap-5 xl:grid-cols-[390px_1fr]">
            <Card>
                <CardHeader>
                    <CardTitle>Alert rule</CardTitle>
                    <CardDescription>Send Slack, email, or webhook notifications for risky decisions.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <label className="space-y-1.5">
                        <span className={labelClass}>Condition</span>
                        <select className={inputClass} value={condition} onChange={e => setCondition(e.target.value as AlertCondition)}>
                            <option value="decision_not_allow">Decision is not ALLOW</option>
                            <option value="risk_score_gt">Risk score exceeds threshold</option>
                        </select>
                    </label>
                    {condition === 'risk_score_gt' && (
                        <label className="space-y-1.5">
                            <span className={labelClass}>Threshold {threshold}</span>
                            <input className="w-full accent-primary" type="range" min={0} max={100} value={threshold} onChange={e => setThreshold(Number(e.target.value))} />
                        </label>
                    )}
                    <label className="space-y-1.5">
                        <span className={labelClass}>Channel</span>
                        <select className={inputClass} value={channel} onChange={e => setChannel(e.target.value as AlertChannel)}>
                            <option value="webhook">Webhook</option>
                            <option value="slack">Slack</option>
                            <option value="email">Email</option>
                        </select>
                    </label>
                    <label className="space-y-1.5">
                        <span className={labelClass}>Config JSON</span>
                        <textarea className={textareaClass} value={config} onChange={e => setConfig(e.target.value)} />
                    </label>
                    <Button onClick={save} className="w-full">
                        <Bell className="h-4 w-4" />
                        Save rule
                    </Button>
                    {status && <p className="rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-800">{status}</p>}
                    {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
                </CardContent>
            </Card>
            <Card>
                <CardHeader>
                    <CardTitle>Configured alerts</CardTitle>
                    <CardDescription>Rules are scoped to {project.name}.</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid gap-3">
                        {alerts.map(alert => (
                            <div className="rounded-lg border bg-white p-4" key={alert.id}>
                                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                                    <div>
                                        <p className="font-semibold">{alert.condition}{alert.threshold ? ` > ${alert.threshold}` : ''}</p>
                                        <p className="text-sm text-muted-foreground">{alert.channel_type} | {alert.is_active ? 'active' : 'paused'}</p>
                                    </div>
                                    <div className="flex gap-2">
                                        <Button variant="outline" size="sm" onClick={() => test(alert)}>Test</Button>
                                        <Button variant="destructive" size="sm" onClick={() => remove(alert)}>
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        ))}
                        {!alerts.length && <p className="text-sm text-muted-foreground">No alert rules configured yet.</p>}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

const PolicyPanel: React.FC<{ token: string; project: Project }> = ({ token, project }) => {
    const [policy, setPolicy] = useState<PolicyConfig>(emptyPolicy);
    const [error, setError] = useState('');
    const [status, setStatus] = useState('');

    const load = useCallback(async () => {
        try {
            const res = await fetchPolicy(token, project.id);
            setPolicy(res.data);
            setError('');
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    }, [project.id, token]);

    useEffect(() => {
        load();
    }, [load]);

    const updateWeight = (key: string, value: number) => {
        setPolicy(prev => ({ ...prev, risk_weights: { ...prev.risk_weights, [key]: value } }));
    };

    const updateRule = (index: number, key: keyof CustomRule, value: string) => {
        setPolicy(prev => ({
            ...prev,
            custom_rules: prev.custom_rules.map((rule, i) => (i === index ? { ...rule, [key]: value } : rule)),
        }));
    };

    const save = async () => {
        try {
            const res = await updatePolicy(token, project.id, {
                risk_weights: policy.risk_weights,
                custom_rules: policy.custom_rules,
            });
            setPolicy(res.data);
            setStatus('Policy saved.');
            setError('');
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    return (
        <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_430px]">
            <Card>
                <CardHeader>
                    <CardTitle>Risk weights</CardTitle>
                    <CardDescription>Tune how strongly policy signals contribute to the final risk score.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {Object.entries(policy.risk_weights).map(([key, value]) => (
                        <label className="block space-y-2" key={key}>
                            <div className="flex items-center justify-between gap-3">
                                <span className="text-sm font-medium capitalize">{key.replace(/_/g, ' ')}</span>
                                <span className="text-sm text-muted-foreground">{value.toFixed(2)}</span>
                            </div>
                            <input
                                className="w-full accent-primary"
                                type="range"
                                min={0}
                                max={3}
                                step={0.05}
                                value={value}
                                onChange={e => updateWeight(key, Number(e.target.value))}
                            />
                        </label>
                    ))}
                    <Button onClick={save}>
                        <SlidersHorizontal className="h-4 w-4" />
                        Save policy
                    </Button>
                    {status && <p className="rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-800">{status}</p>}
                    {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between gap-3">
                    <div>
                        <CardTitle>Custom rules</CardTitle>
                        <CardDescription>Expression rules evaluate alongside built-in invariants.</CardDescription>
                    </div>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPolicy(prev => ({
                            ...prev,
                            custom_rules: [...prev.custom_rules, { name: 'Supply drift', condition: 'minted_supply > locked_collateral * 1.1', reason_code: 'CUSTOM' }],
                        }))}
                    >
                        <Plus className="h-4 w-4" />
                    </Button>
                </CardHeader>
                <CardContent className="space-y-4">
                    {policy.custom_rules.map((rule, index) => (
                        <div className="space-y-3 rounded-lg border bg-white p-3" key={`${rule.name}-${index}`}>
                            <input className={inputClass} value={rule.name} onChange={e => updateRule(index, 'name', e.target.value)} placeholder="Rule name" />
                            <textarea className={textareaClass} value={rule.condition} onChange={e => updateRule(index, 'condition', e.target.value)} placeholder="minted_supply > locked_collateral * 1.1" />
                            <input className={inputClass} value={rule.reason_code} onChange={e => updateRule(index, 'reason_code', e.target.value)} placeholder="Reason code" />
                        </div>
                    ))}
                    {!policy.custom_rules.length && <p className="text-sm text-muted-foreground">No custom rules yet.</p>}
                </CardContent>
            </Card>
        </div>
    );
};

const LegacyPanel: React.FC = () => (
    <Card>
        <CardHeader>
            <CardTitle>v1 simulation tools</CardTitle>
            <CardDescription>The original replay, metrics, connector, and reason-code panels remain available under their existing endpoints.</CardDescription>
        </CardHeader>
        <CardContent>
            <div className="rounded-lg border bg-white p-4">
                <Dashboard />
            </div>
        </CardContent>
    </Card>
);

const App: React.FC = () => {
    const [token, setToken] = useState<string | null>(() => getStoredToken());
    const [user, setUser] = useState<User | null>(null);
    const [projects, setProjects] = useState<Project[]>([]);
    const [activeProjectId, setActiveProjectId] = useState<number | null>(null);
    const [view, setView] = useState<View>('overview');
    const [decisions, setDecisions] = useState<DecisionRecord[]>([]);
    const [alerts, setAlerts] = useState<AlertRule[]>([]);
    const [listeners, setListeners] = useState<ListenerRecord[]>([]);
    const [newProjectName, setNewProjectName] = useState('');
    const [error, setError] = useState('');

    const activeProject = useMemo(
        () => projects.find(project => project.id === activeProjectId) ?? projects[0] ?? null,
        [activeProjectId, projects],
    );

    const loadProjects = useCallback(async (authToken: string) => {
        const res = await fetchProjects(authToken);
        setProjects(res.data);
        setActiveProjectId(current => current ?? res.data[0]?.id ?? null);
    }, []);

    const loadProjectData = useCallback(async () => {
        if (!token || !activeProject) return;
        try {
            const [decisionRes, alertRes] = await Promise.all([
                fetchV2Decisions(token, activeProject.id, 20),
                fetchAlertRules(token, activeProject.id),
            ]);
            setDecisions(decisionRes.data.items);
            setAlerts(alertRes.data);
            setError('');
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    }, [activeProject, token]);

    useEffect(() => {
        if (!token) return;
        Promise.all([fetchMe(token), loadProjects(token)])
            .then(([me]) => {
                setUser(me.data);
                setError('');
            })
            .catch(err => {
                setStoredToken(null);
                setToken(null);
                setError(getApiErrorMessage(err));
            });
    }, [loadProjects, token]);

    useEffect(() => {
        loadProjectData();
    }, [loadProjectData]);

    const logout = () => {
        setStoredToken(null);
        setToken(null);
        setUser(null);
        setProjects([]);
        setActiveProjectId(null);
    };

    const addProject = async () => {
        if (!token || !newProjectName.trim()) return;
        try {
            const res = await createProject(token, newProjectName.trim());
            setProjects(prev => [...prev, res.data]);
            setActiveProjectId(res.data.id);
            setNewProjectName('');
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    const removeActiveProject = async () => {
        if (!token || !activeProject || projects.length <= 1) return;
        try {
            await deleteProject(token, activeProject.id);
            setProjects(prev => prev.filter(project => project.id !== activeProject.id));
            setActiveProjectId(projects.find(project => project.id !== activeProject.id)?.id ?? null);
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    const recordListener = (listener: ListenerRecord) => {
        setListeners(prev => [listener, ...prev.filter(item => item.id !== listener.id)].slice(0, 8));
    };

    if (!token) {
        return <AuthScreen onAuthenticated={setToken} />;
    }

    return (
        <main className="min-h-screen bg-background">
            <div className="flex min-h-screen">
                <aside className="hidden w-72 border-r bg-white px-4 py-5 lg:block">
                    <div className="mb-6 flex items-center gap-3 px-2">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                            <ShieldCheck className="h-5 w-5" />
                        </div>
                        <div>
                            <p className="font-semibold">BridgeGuard</p>
                            <p className="text-xs text-muted-foreground">v2 operator console</p>
                        </div>
                    </div>
                    <nav className="space-y-1">
                        {navItems.map(item => {
                            const Icon = item.icon;
                            return (
                                <button
                                    className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm font-medium transition ${view === item.id ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`}
                                    key={item.id}
                                    onClick={() => setView(item.id)}
                                >
                                    <Icon className="h-4 w-4" />
                                    {item.label}
                                </button>
                            );
                        })}
                    </nav>
                </aside>
                <section className="flex min-w-0 flex-1 flex-col">
                    <header className="sticky top-0 z-20 border-b bg-white/95 px-4 py-3 backdrop-blur">
                        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                            <div>
                                <p className="text-xs font-semibold uppercase text-muted-foreground">Authenticated as {user?.email ?? 'operator'}</p>
                                <h1 className="text-2xl font-semibold tracking-normal">{activeProject?.name ?? 'No project selected'}</h1>
                            </div>
                            <div className="flex flex-wrap items-center gap-2">
                                <DropdownMenu>
                                    <DropdownMenuTrigger asChild>
                                        <Button variant="outline">
                                            {activeProject?.name ?? 'Projects'}
                                            <ChevronDown className="h-4 w-4" />
                                        </Button>
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent align="end">
                                        {projects.map(project => (
                                            <DropdownMenuItem key={project.id} onClick={() => setActiveProjectId(project.id)}>
                                                {project.name}
                                            </DropdownMenuItem>
                                        ))}
                                    </DropdownMenuContent>
                                </DropdownMenu>
                                <Dialog>
                                    <DialogTrigger asChild>
                                        <Button variant="outline">
                                            <Plus className="h-4 w-4" />
                                            Project
                                        </Button>
                                    </DialogTrigger>
                                    <DialogContent>
                                        <DialogHeader>
                                            <DialogTitle>Create project</DialogTitle>
                                            <DialogDescription>Projects isolate decisions, alerts, policies, and listeners.</DialogDescription>
                                        </DialogHeader>
                                        <input className={inputClass} value={newProjectName} onChange={e => setNewProjectName(e.target.value)} placeholder="Bridge operations" />
                                        <Button onClick={addProject}>Create project</Button>
                                    </DialogContent>
                                </Dialog>
                                <Button variant="outline" size="icon" onClick={loadProjectData} title="Refresh project data">
                                    <RefreshCcw className="h-4 w-4" />
                                </Button>
                                <Button variant="ghost" size="icon" onClick={logout} title="Log out">
                                    <LogOut className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                        <div className="mt-3 flex gap-2 overflow-x-auto lg:hidden">
                            {navItems.map(item => {
                                const Icon = item.icon;
                                return (
                                    <Button key={item.id} size="sm" variant={view === item.id ? 'default' : 'outline'} onClick={() => setView(item.id)}>
                                        <Icon className="h-4 w-4" />
                                        {item.label}
                                    </Button>
                                );
                            })}
                        </div>
                    </header>
                    <div className="flex-1 px-4 py-5 md:px-6">
                        {error && <p className="mb-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
                        {!activeProject ? (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Create your first project</CardTitle>
                                    <CardDescription>The v2 API requires a project before simulations can be saved.</CardDescription>
                                </CardHeader>
                                <CardContent className="flex max-w-lg gap-2">
                                    <input className={inputClass} value={newProjectName} onChange={e => setNewProjectName(e.target.value)} placeholder="Bridge operations" />
                                    <Button onClick={addProject}>Create</Button>
                                </CardContent>
                            </Card>
                        ) : (
                            <>
                                {view === 'overview' && (
                                    <OverviewPanel decisions={decisions} alerts={alerts} listeners={listeners} onRefresh={loadProjectData} />
                                )}
                                {view === 'simulate' && (
                                    <SimulationPanel
                                        token={token}
                                        project={activeProject}
                                        onDecision={decision => {
                                            setDecisions(prev => [decision, ...prev.filter(item => item.id !== decision.id)]);
                                            setView('overview');
                                        }}
                                    />
                                )}
                                {view === 'connectors' && <ConnectorWizard token={token} project={activeProject} onListener={recordListener} />}
                                {view === 'alerts' && <AlertRulesPanel token={token} project={activeProject} alerts={alerts} onReload={loadProjectData} />}
                                {view === 'policy' && <PolicyPanel token={token} project={activeProject} />}
                                {view === 'legacy' && <LegacyPanel />}
                                <div className="mt-8 flex justify-end">
                                    <Button variant="outline" size="sm" onClick={removeActiveProject} disabled={projects.length <= 1}>
                                        <Trash2 className="h-4 w-4" />
                                        Delete project
                                    </Button>
                                </div>
                            </>
                        )}
                    </div>
                </section>
            </div>
        </main>
    );
};

export default App;
