import axios from 'axios';
import {
    Attack,
    ConnectorConfig,
    ConnectorDiscoveryRequest,
    ConnectorDiscoveryResponse,
    ConnectorEvaluationResult,
    DecisionRecord,
    Metrics,
    ReasonCode,
    TransferSimulation,
} from './types';

const API = axios.create({ baseURL: '' });

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
