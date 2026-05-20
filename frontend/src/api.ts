import axios from 'axios';
import {
    AlertRule,
    AlertRulePayload,
    Attack,
    AuthToken,
    ConnectorConfig,
    ConnectorDiscoveryRequest,
    ConnectorDiscoveryResponse,
    ConnectorEvaluationResult,
    DecisionRecord,
    ListenerRecord,
    Metrics,
    PaginatedDecisions,
    PolicyConfig,
    Project,
    ReasonCode,
    TransferSimulation,
    User,
} from './types';

const API = axios.create({ baseURL: '' });
const TOKEN_KEY = 'bridgeguard.v2.token';

export const getStoredToken = () => localStorage.getItem(TOKEN_KEY);

export const setStoredToken = (token: string | null) => {
    if (token) {
        localStorage.setItem(TOKEN_KEY, token);
    } else {
        localStorage.removeItem(TOKEN_KEY);
    }
};

const authHeaders = (token: string) => ({
    Authorization: `Bearer ${token}`,
});

const projectHeaders = (token: string, projectId: number) => ({
    ...authHeaders(token),
    'X-Project-ID': String(projectId),
});

export const getApiErrorMessage = (error: unknown) => {
    if (axios.isAxiosError(error)) {
        const detail = error.response?.data?.detail;
        if (typeof detail === 'string') {
            return detail;
        }
        return 'Backend unavailable. Start the BridgeGuard API on port 8000 and retry.';
    }
    return 'Unexpected error while contacting the backend.';
};

export const fetchAttacks = () => API.get<Attack[]>('/attacks');
export const simulateTransfer = (data: TransferSimulation) => API.post<DecisionRecord>('/simulate', data);
export const simulateAttack = (name: string) => API.post<DecisionRecord>(`/simulate-attack/${encodeURIComponent(name)}`);
export const fetchDecisions = () => API.get<DecisionRecord[]>('/decisions');
export const fetchReasonCodes = () => API.get<Record<ReasonCode, string>>('/reason-codes');
export const fetchMetrics = () => API.get<Metrics>('/metrics');

export const fetchConnectors = () => API.get<ConnectorConfig[]>('/connectors/');
export const fetchConnectorPresets = () => API.get<ConnectorConfig[]>('/connectors/presets');
export const createConnector = (data: ConnectorConfig) => API.post<ConnectorConfig>('/connectors/', data);
export const updateConnector = (id: string, data: ConnectorConfig) => API.put<ConnectorConfig>(`/connectors/${id}`, data);
export const deleteConnector = (id: string) => API.delete(`/connectors/${id}`);
export const evaluateConnector = (id: string) => API.post<ConnectorEvaluationResult>(`/connectors/${id}/evaluate`);
export const discoverConnector = (data: ConnectorDiscoveryRequest) =>
    API.post<ConnectorDiscoveryResponse>('/api/v2/connectors/discover', data);

export const registerUser = (email: string, password: string, projectName: string) =>
    API.post<User>('/api/v2/auth/register', { email, password, project_name: projectName });

export const loginUser = (email: string, password: string) => {
    const body = new URLSearchParams();
    body.set('username', email);
    body.set('password', password);
    return API.post<AuthToken>('/api/v2/auth/login', body, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
};

export const fetchMe = (token: string) =>
    API.get<User>('/api/v2/auth/me', { headers: authHeaders(token) });

export const fetchProjects = (token: string) =>
    API.get<Project[]>('/api/v2/projects', { headers: authHeaders(token) });

export const createProject = (token: string, name: string) =>
    API.post<Project>('/api/v2/projects', { name }, { headers: authHeaders(token) });

export const deleteProject = (token: string, projectId: number) =>
    API.delete(`/api/v2/projects/${projectId}`, { headers: authHeaders(token) });

export const simulateTransferV2 = (token: string, projectId: number, data: TransferSimulation) =>
    API.post<DecisionRecord>('/api/v2/simulate', data, { headers: projectHeaders(token, projectId) });

export const fetchV2Decisions = (token: string, projectId: number, limit = 20, offset = 0) =>
    API.get<PaginatedDecisions>('/api/v2/decisions', {
        headers: projectHeaders(token, projectId),
        params: { project_id: projectId, limit, offset },
    });

export const fetchV2Connectors = () => API.get<ConnectorConfig[]>('/api/v2/connectors');

export const createV2Connector = (data: ConnectorConfig) => API.post<ConnectorConfig>('/api/v2/connectors', data);

export const deleteV2Connector = (id: string) => API.delete(`/api/v2/connectors/${id}`);

export const evaluateV2Connector = (id: string) => API.post<ConnectorEvaluationResult>(`/api/v2/connectors/${id}/evaluate`);

export const fetchAlertRules = (token: string, projectId: number) =>
    API.get<AlertRule[]>(`/api/v2/projects/${projectId}/alerts`, { headers: authHeaders(token) });

export const createAlertRule = (token: string, projectId: number, data: AlertRulePayload) =>
    API.post<AlertRule>(`/api/v2/projects/${projectId}/alerts`, data, { headers: authHeaders(token) });

export const updateAlertRule = (token: string, projectId: number, alertId: number, data: Partial<AlertRulePayload>) =>
    API.put<AlertRule>(`/api/v2/projects/${projectId}/alerts/${alertId}`, data, { headers: authHeaders(token) });

export const deleteAlertRule = (token: string, projectId: number, alertId: number) =>
    API.delete(`/api/v2/projects/${projectId}/alerts/${alertId}`, { headers: authHeaders(token) });

export const testAlertRule = (token: string, projectId: number, alertId: number) =>
    API.post<{ sent: boolean; channel_type: string }>(`/api/v2/projects/${projectId}/alerts/${alertId}/test`, null, {
        headers: authHeaders(token),
    });

export const fetchPolicy = (token: string, projectId: number) =>
    API.get<PolicyConfig>(`/api/v2/projects/${projectId}/policy`, { headers: authHeaders(token) });

export const updatePolicy = (token: string, projectId: number, data: Pick<PolicyConfig, 'risk_weights' | 'custom_rules'>) =>
    API.put<PolicyConfig>(`/api/v2/projects/${projectId}/policy`, data, { headers: authHeaders(token) });

export const startListener = (token: string, projectId: number, connector: ConnectorConfig, mode: 'polling' | 'websocket') =>
    API.post<ListenerRecord>(
        `/api/v2/projects/${projectId}/listeners/start`,
        { connector, mode },
        { headers: authHeaders(token) },
    );

export const stopListener = (token: string, projectId: number, connectorId?: string) =>
    API.post<ListenerRecord[]>(
        `/api/v2/projects/${projectId}/listeners/stop`,
        { connector_id: connectorId || null },
        { headers: authHeaders(token) },
    );
