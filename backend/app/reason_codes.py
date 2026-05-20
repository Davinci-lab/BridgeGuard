from enum import Enum

class ReasonCode(str, Enum):
    OUTFLOW_EXCEEDS_INFLOW = "OUTFLOW_EXCEEDS_INFLOW"
    MINT_EXCEEDS_LOCKED = "MINT_EXCEEDS_LOCKED"
    RELEASE_EXCEEDS_BURNED = "RELEASE_EXCEEDS_BURNED"
    UNKNOWN_OR_CHANGED_ROOT = "UNKNOWN_OR_CHANGED_ROOT"
    SIGNER_THRESHOLD_WEAK = "SIGNER_THRESHOLD_WEAK"
    ABNORMAL_VOLUME_SPIKE = "ABNORMAL_VOLUME_SPIKE"
    CONFIG_CHANGE_UNCOOLED = "CONFIG_CHANGE_UNCOOLED"
    CHAIN_FINALITY_NOT_REACHED = "CHAIN_FINALITY_NOT_REACHED"
    REPLAY_OR_DUPLICATE_MESSAGE = "REPLAY_OR_DUPLICATE_MESSAGE"
    VALIDATOR_SET_RISK = "VALIDATOR_SET_RISK"
    ASSET_CAP_EXCEEDED = "ASSET_CAP_EXCEEDED"
    ROUTE_CAP_EXCEEDED = "ROUTE_CAP_EXCEEDED"
    TVL_DIVERGENCE = "TVL_DIVERGENCE"
    EMERGENCY_MODE_ACTIVE = "EMERGENCY_MODE_ACTIVE"
    CUSTOM = "CUSTOM"

REASON_DESCRIPTIONS = {
    ReasonCode.OUTFLOW_EXCEEDS_INFLOW: "Total outflow exceeds inflow plus allowed buffer",
    ReasonCode.MINT_EXCEEDS_LOCKED: "Minted tokens exceed locked collateral",
    ReasonCode.RELEASE_EXCEEDS_BURNED: "Released tokens exceed burned/proven amount",
    ReasonCode.UNKNOWN_OR_CHANGED_ROOT: "Trusted root (validator set / merkle root) changed without cooldown",
    ReasonCode.SIGNER_THRESHOLD_WEAK: "Signer participation below safety threshold",
    ReasonCode.ABNORMAL_VOLUME_SPIKE: "Transfer volume exceeds statistical anomaly threshold",
    ReasonCode.CONFIG_CHANGE_UNCOOLED: "Bridge configuration changed within cooldown period",
    ReasonCode.CHAIN_FINALITY_NOT_REACHED: "Source chain finality not achieved for this transaction",
    ReasonCode.REPLAY_OR_DUPLICATE_MESSAGE: "Duplicate transfer message detected (possible replay)",
    ReasonCode.VALIDATOR_SET_RISK: "Validator set governance appears compromised or too small",
    ReasonCode.ASSET_CAP_EXCEEDED: "Per-asset transfer cap exceeded",
    ReasonCode.ROUTE_CAP_EXCEEDED: "Per-route transfer cap exceeded",
    ReasonCode.TVL_DIVERGENCE: "On‑chain TVL diverges from expected accounting",
    ReasonCode.EMERGENCY_MODE_ACTIVE: "Emergency pause mode is active on the bridge",
    ReasonCode.CUSTOM: "Project-defined custom policy rule matched",
}
