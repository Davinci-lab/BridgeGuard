from abc import ABC, abstractmethod

from .connector_config import ConnectorConfig
from .models import TransferSimulation
from .policy_engine import decide


try:
    from web3 import Web3

    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    print("web3 not installed, EVM connector will use mock data")


class BaseConnector(ABC):
    connector_type: str = "base"

    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.warning: str | None = None

    @abstractmethod
    def evaluate(self) -> TransferSimulation:
        """Read the live or mocked connector state and build a simulation."""

    def mock_simulation(self, warning: str) -> TransferSimulation:
        self.warning = warning
        return TransferSimulation(
            source_chain=self.config.source_chain,
            dest_chain=self.config.dest_chain,
            asset=self.config.asset,
            amount=100.0,
            locked_collateral=10000.0,
            minted_supply=9000.0,
            burned_proven=1000.0,
            released_supply=1000.0,
            signer_count=10,
            required_signers=6,
            finality_blocks=self.config.finality_blocks,
            current_block=100,
            tx_block=90,
            is_duplicate=False,
            emergency_mode=False,
            daily_volume=5000.0,
            daily_cap=self.config.daily_cap,
            route_volume=2000.0,
            route_cap=self.config.route_cap,
            asset_cap=self.config.asset_cap,
            total_inflow=9000.0,
            total_outflow=8000.0,
            config_change_cooled=True,
        )


class EVMConnector(BaseConnector):
    connector_type = "evm"

    def evaluate(self) -> TransferSimulation:
        if not WEB3_AVAILABLE or self.config.rpc_url.startswith("mock://"):
            return self.mock_simulation("Using mock EVM connector data for local workflow testing")

        w3 = Web3(Web3.HTTPProvider(self.config.rpc_url))
        if not w3.is_connected():
            return self.mock_simulation(
                f"RPC unavailable ({self.config.rpc_url}); using local mock evaluation"
            )

        contract = w3.eth.contract(address=self.config.contract_address, abi=self.config.abi)
        warnings = []

        def call_method(method_name: str | None, default=None):
            if not method_name:
                return default
            try:
                func = getattr(contract.functions, method_name, None)
            except Exception:
                warnings.append(f"Method not available in ABI: {method_name}")
                return default
            if func is None:
                warnings.append(f"Method not available in ABI: {method_name}")
                return default
            try:
                return func().call()
            except Exception as exc:
                warnings.append(f"Method call failed for {method_name}: {exc}")
                return default

        mapping = self.config.method_mapping
        locked = call_method(mapping.locked_collateral, 0)
        minted = call_method(mapping.minted_supply, 0)
        burned = call_method(mapping.burned_proven, 0)
        released = call_method(mapping.released_supply, 0)
        signer_count = call_method(mapping.signer_count, 10)
        required_signers = call_method(mapping.required_signers, 6)
        emergency = call_method(mapping.emergency_mode, False)
        config_change_block = call_method(mapping.config_change_block, 0)
        current_block = call_method(mapping.current_block, w3.eth.block_number)
        self.warning = "; ".join(warnings) if warnings else None

        return TransferSimulation(
            source_chain=self.config.source_chain,
            dest_chain=self.config.dest_chain,
            asset=self.config.asset,
            amount=1.0,
            locked_collateral=float(locked),
            minted_supply=float(minted),
            burned_proven=float(burned),
            released_supply=float(released),
            signer_count=signer_count,
            required_signers=required_signers,
            finality_blocks=self.config.finality_blocks,
            current_block=current_block,
            tx_block=current_block - 1,
            is_duplicate=False,
            emergency_mode=bool(emergency),
            daily_volume=0,
            daily_cap=self.config.daily_cap,
            route_volume=0,
            route_cap=self.config.route_cap,
            asset_cap=self.config.asset_cap,
            total_inflow=float(locked) + float(released),
            total_outflow=float(minted) + float(burned),
            config_change_cooled=(current_block - config_change_block > 100),
        )


class SolanaConnector(BaseConnector):
    connector_type = "solana"

    def evaluate(self) -> TransferSimulation:
        return self.mock_simulation("Using mock Solana connector data")


class CosmosConnector(BaseConnector):
    connector_type = "cosmos"

    def evaluate(self) -> TransferSimulation:
        return self.mock_simulation("Using mock Cosmos connector data")


class ConnectorEngine:
    @staticmethod
    def evaluate(config: ConnectorConfig) -> dict:
        from .connector_registry import ConnectorRegistry

        connector = ConnectorRegistry.create(config)
        sim = connector.evaluate()
        decision, risk_score, violations, explanation, recommended = decide(sim)
        return {
            "simulation": sim.model_dump(),
            "decision": decision,
            "risk_score": risk_score,
            "reason_codes": [v.value for v in violations],
            "explanation": explanation,
            "recommended_action": recommended,
            "warning": connector.warning,
        }
