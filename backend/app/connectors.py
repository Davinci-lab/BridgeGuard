from .connector_config import ConnectorConfig
from .models import TransferSimulation
from .policy_engine import decide

# Try to import web3, if not available, mock it for demo
try:
    from web3 import Web3
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    print("web3 not installed, EVM connector will use mock data")

class ConnectorEngine:
    @staticmethod
    def evaluate(config: ConnectorConfig) -> dict:
        if config.type == "evm":
            return ConnectorEngine._eval_evm(config)
        else:
            raise ValueError(f"Unsupported connector type: {config.type}")

    @staticmethod
    def _eval_evm(config: ConnectorConfig) -> dict:
        if not WEB3_AVAILABLE or config.rpc_url.startswith("mock://"):
            return ConnectorEngine._mock_result(config, "Using mock connector data for local workflow testing")

        # Real on-chain evaluation
        w3 = Web3(Web3.HTTPProvider(config.rpc_url))
        if not w3.is_connected():
            return ConnectorEngine._mock_result(config, f"RPC unavailable ({config.rpc_url}); using local mock evaluation")

        contract = w3.eth.contract(address=config.contract_address, abi=config.abi)

        # Read on-chain state based on method mapping
        warnings = []

        def call_method(method_name: str, default=None):
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

        locked = call_method(config.method_mapping.locked_collateral, 0)
        minted = call_method(config.method_mapping.minted_supply, 0)
        burned = call_method(config.method_mapping.burned_proven, 0)
        released = call_method(config.method_mapping.released_supply, 0)
        signer_count = call_method(config.method_mapping.signer_count, 10)
        required_signers = call_method(config.method_mapping.required_signers, 6)
        emergency = call_method(config.method_mapping.emergency_mode, False)
        config_change_block = call_method(config.method_mapping.config_change_block, 0)
        current_block = call_method(config.method_mapping.current_block, w3.eth.block_number)

        # Simplified transfer: we need a recent deposit event to simulate
        # In a full version, we'd listen to events. Here we just use a placeholder amount = 1 unit.
        amount = 1.0  # could be extracted from an event

        # Build simulation
        sim = TransferSimulation(
            source_chain=config.source_chain,
            dest_chain=config.dest_chain,
            asset=config.asset,
            amount=amount,
            locked_collateral=float(locked),
            minted_supply=float(minted),
            burned_proven=float(burned),
            released_supply=float(released),
            signer_count=signer_count,
            required_signers=required_signers,
            finality_blocks=config.finality_blocks,
            current_block=current_block,
            tx_block=current_block - 1,  # assume just mined
            is_duplicate=False,
            emergency_mode=bool(emergency),
            daily_volume=0,  # would need off-chain tracking
            daily_cap=config.daily_cap,
            route_volume=0,
            route_cap=config.route_cap,
            asset_cap=config.asset_cap,
            total_inflow=float(locked) + float(released),  # simplistic
            total_outflow=float(minted) + float(burned),
            config_change_cooled=(current_block - config_change_block > 100)  # arbitrary cooldown
        )

        decision, risk_score, violations, explanation, recommended = decide(sim)
        return {
            "simulation": sim.model_dump(),
            "decision": decision,
            "risk_score": risk_score,
            "reason_codes": [v.value for v in violations],
            "explanation": explanation,
            "recommended_action": recommended,
            "warning": "; ".join(warnings) if warnings else None
        }

    @staticmethod
    def _mock_result(config: ConnectorConfig, warning: str) -> dict:
        sim = TransferSimulation(
            source_chain=config.source_chain,
            dest_chain=config.dest_chain,
            asset=config.asset,
            amount=100.0,
            locked_collateral=10000.0,
            minted_supply=9000.0,
            burned_proven=1000.0,
            released_supply=1000.0,
            signer_count=10,
            required_signers=6,
            finality_blocks=config.finality_blocks,
            current_block=100,
            tx_block=90,
            is_duplicate=False,
            emergency_mode=False,
            daily_volume=5000.0,
            daily_cap=config.daily_cap,
            route_volume=2000.0,
            route_cap=config.route_cap,
            asset_cap=config.asset_cap,
            total_inflow=9000.0,
            total_outflow=8000.0,
            config_change_cooled=True
        )
        decision, risk_score, violations, explanation, recommended = decide(sim)
        return {
            "simulation": sim.model_dump(),
            "decision": decision,
            "risk_score": risk_score,
            "reason_codes": [v.value for v in violations],
            "explanation": explanation,
            "recommended_action": recommended,
            "warning": warning
        }
