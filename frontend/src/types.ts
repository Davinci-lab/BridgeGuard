export type PolicyDecision =
    | 'ALLOW'
    | 'DELAY'
    | 'FREEZE'
    | 'ESCALATE_TO_GUARDIANS'
    | 'REQUIRE_EXTRA_SIGNATURES';

export type ReasonCode =
    | 'OUTFLOW_EXCEEDS_INFLOW'
    | 'MINT_EXCEEDS_LOCKED'
    | 'RELEASE_EXCEEDS_BURNED'
    | 'UNKNOWN_OR_CHANGED_ROOT'
    | 'SIGNER_THRESHOLD_WEAK'
    | 'ABNORMAL_VOLUME_SPIKE'
    | 'CONFIG_CHANGE_UNCOOLED'
    | 'CHAIN_FINALITY_NOT_REACHED'
    | 'REPLAY_OR_DUPLICATE_MESSAGE'
    | 'VALIDATOR_SET_RISK'
    | 'ASSET_CAP_EXCEEDED'
    | 'ROUTE_CAP_EXCEEDED'
    | 'TVL_DIVERGENCE'
    | 'EMERGENCY_MODE_ACTIVE';

export interface TransferSimulation {
    source_chain: string;
    dest_chain: string;
    asset: string;
    amount: number;
    signer_count: number;
    required_signers: number;
    finality_blocks: number;
    current_block: number;
    tx_block: number;
    is_duplicate: boolean;
    emergency_mode: boolean;
    config_change_cooled: boolean;
    locked_collateral: number;
    minted_supply: number;
    burned_proven: number;
    released_supply: number;
    daily_volume: number;
    daily_cap: number;
    route_volume: number;
    route_cap: number;
    asset_cap: number;
    total_inflow: number;
    total_outflow: number;
    known_message_hash?: string | null;
}

export interface Attack {
    name: string;
    date: string;
    loss: string;
    bridge_type: string;
    root_cause_category: string;
    violated_invariant: string;
    defensive_control: string;
    expected_decision: PolicyDecision;
    reason_codes: ReasonCode[];
    summary: string;
    source?: string | null;
}

export interface DecisionRecord {
    id: string;
    timestamp: string;
    decision: PolicyDecision;
    risk_score: number;
    reason_codes: ReasonCode[];
    explanation: string;
    recommended_action: string;
    simulation: TransferSimulation;
}

export interface RiskScoreDistribution {
    low: number;
    medium: number;
    high: number;
    critical: number;
}

export type DecisionsDistribution = Partial<Record<PolicyDecision, number>>;

export interface TopReasonCode {
    code: ReasonCode;
    count: number;
}

export interface Metrics {
    total_simulations: number;
    risk_score_distribution: RiskScoreDistribution;
    decisions_distribution: DecisionsDistribution;
    top_reason_codes: TopReasonCode[];
}

export interface EVMMethodMapping {
  locked_collateral: string;
  minted_supply: string;
  burned_proven: string;
  released_supply: string;
  signer_count?: string | null;
  required_signers?: string | null;
  emergency_mode?: string | null;
  config_change_block?: string | null;
  current_block?: string | null;
}

export interface AbiInput {
  name: string;
  type: string;
  indexed?: boolean;
}

export interface AbiOutput {
  name: string;
  type: string;
}

export interface AbiItem {
  type: 'function' | 'event' | 'constructor' | 'fallback' | 'receive';
  name?: string;
  stateMutability?: 'pure' | 'view' | 'nonpayable' | 'payable';
  inputs?: AbiInput[];
  outputs?: AbiOutput[];
  anonymous?: boolean;
}

export interface ConnectorConfig {
  id: string;
  name: string;
  type: 'evm';
  enabled: boolean;
  rpc_url: string;
  chain_id: number;
  contract_address: string;
  abi: AbiItem[];
  method_mapping: EVMMethodMapping;
  daily_cap: number;
  route_cap: number;
  asset_cap: number;
  source_chain: string;
  dest_chain: string;
  asset: string;
  finality_blocks: number;
}

export interface ConnectorEvaluationResult {
    simulation: TransferSimulation;
    decision: PolicyDecision;
    risk_score: number;
    reason_codes: ReasonCode[];
    explanation: string;
    recommended_action: string;
    warning?: string;
}
