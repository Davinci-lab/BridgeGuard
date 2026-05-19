import json
from pathlib import Path
from typing import List
from .models import Attack, TransferSimulation

DATA_DIR = Path(__file__).parent / "sample_data"

def load_attacks() -> List[Attack]:
    with open(DATA_DIR / "attacks.json") as f:
        data = json.load(f)
    return [Attack(**item) for item in data]

def load_normal_flows() -> List[TransferSimulation]:
    with open(DATA_DIR / "normal_flows.json") as f:
        data = json.load(f)
    return [TransferSimulation(**item) for item in data]

def attack_to_simulation(attack: Attack) -> TransferSimulation:
    """Convert a historical attack pattern into a simulation input (defensive only)."""
    # Representative defensive mapping only; this is not an exploit reproduction.
    mapping = {
        "Ronin Bridge": TransferSimulation(
            source_chain="Ronin", dest_chain="Ethereum", asset="ETH", amount=173600,
            signer_count=9, required_signers=5, finality_blocks=10,
            current_block=100, tx_block=100,
            is_duplicate=False, emergency_mode=False,
            locked_collateral=0, minted_supply=173600,
            burned_proven=0, released_supply=0,
            daily_volume=173600, daily_cap=10000,
            route_volume=173600, route_cap=50000,
            asset_cap=500000, total_inflow=0, total_outflow=173600
        ),
        "Wormhole": TransferSimulation(
            source_chain="Solana", dest_chain="Ethereum", asset="ETH", amount=120000,
            signer_count=19, required_signers=13, finality_blocks=32,
            current_block=50, tx_block=50,
            is_duplicate=False, emergency_mode=False,
            locked_collateral=50000, minted_supply=120000,
            burned_proven=0, released_supply=0,
            daily_volume=120000, daily_cap=50000,
            route_volume=120000, route_cap=100000,
            asset_cap=500000, total_inflow=50000, total_outflow=120000
        ),
        "Nomad": TransferSimulation(
            source_chain="Moonbeam", dest_chain="Ethereum", asset="USDC", amount=190000000,
            signer_count=1, required_signers=1, finality_blocks=5,
            current_block=30, tx_block=30,
            is_duplicate=True, emergency_mode=False,
            locked_collateral=200000000, minted_supply=200000000,
            burned_proven=10000000, released_supply=190000000,
            daily_volume=190000000, daily_cap=10000000,
            route_volume=190000000, route_cap=20000000,
            asset_cap=500000000, total_inflow=200000000, total_outflow=190000000
        ),
        "Harmony Horizon": TransferSimulation(
            source_chain="Harmony", dest_chain="Ethereum", asset="ETH", amount=85000,
            signer_count=4, required_signers=2, finality_blocks=5,
            current_block=20, tx_block=20,
            is_duplicate=False, emergency_mode=False,
            locked_collateral=10000, minted_supply=85000,
            burned_proven=0, released_supply=0,
            daily_volume=85000, daily_cap=5000,
            route_volume=85000, route_cap=20000,
            asset_cap=200000, total_inflow=10000, total_outflow=85000
        ),
        "BNB Token Hub": TransferSimulation(
            source_chain="BSC", dest_chain="BSC", asset="BNB", amount=2000000,
            signer_count=21, required_signers=11, finality_blocks=10,
            current_block=150, tx_block=150,
            is_duplicate=True, emergency_mode=False,
            locked_collateral=0, minted_supply=2000000,
            burned_proven=0, released_supply=0,
            daily_volume=2000000, daily_cap=100000,
            route_volume=2000000, route_cap=500000,
            asset_cap=5000000, total_inflow=0, total_outflow=2000000
        ),
        "Poly Network": TransferSimulation(
            source_chain="Polygon", dest_chain="Ethereum", asset="USDC", amount=600000000,
            signer_count=3, required_signers=2, finality_blocks=10,
            current_block=200, tx_block=200,
            is_duplicate=False, emergency_mode=False,
            locked_collateral=1000000000, minted_supply=1000000000,
            burned_proven=400000000, released_supply=600000000,
            daily_volume=600000000, daily_cap=50000000,
            route_volume=600000000, route_cap=100000000,
            asset_cap=2000000000, total_inflow=1000000000, total_outflow=600000000,
            config_change_cooled=False
        ),
        "Multichain": TransferSimulation(
            source_chain="Fantom", dest_chain="Ethereum", asset="USDC", amount=130000000,
            signer_count=5, required_signers=3, finality_blocks=10,
            current_block=80, tx_block=80,
            is_duplicate=False, emergency_mode=False,
            locked_collateral=50000000, minted_supply=130000000,
            burned_proven=50000000, released_supply=130000000,
            daily_volume=130000000, daily_cap=20000000,
            route_volume=130000000, route_cap=50000000,
            asset_cap=300000000, total_inflow=50000000, total_outflow=130000000
        ),
        "THORChain recent incident": TransferSimulation(
            source_chain="THORChain", dest_chain="Bitcoin", asset="BTC", amount=4000,
            signer_count=10, required_signers=7, finality_blocks=6,
            current_block=60, tx_block=60,
            is_duplicate=False, emergency_mode=True,
            locked_collateral=2000, minted_supply=2000,
            burned_proven=0, released_supply=4000,
            daily_volume=4000, daily_cap=100,
            route_volume=4000, route_cap=500,
            asset_cap=1000, total_inflow=2000, total_outflow=4000
        ),
        "Orbit Chain": TransferSimulation(
            source_chain="Orbit", dest_chain="Ethereum", asset="USDT", amount=81000000,
            signer_count=5, required_signers=3, finality_blocks=5,
            current_block=90, tx_block=90,
            is_duplicate=False, emergency_mode=False,
            locked_collateral=200000000, minted_supply=200000000,
            burned_proven=119000000, released_supply=200000000,
            daily_volume=81000000, daily_cap=50000000,
            route_volume=81000000, route_cap=50000000,
            asset_cap=200000000, total_inflow=200000000, total_outflow=200000000
        ),
        "Socket/Bungee": TransferSimulation(
            source_chain="Ethereum", dest_chain="Polygon", asset="USDC", amount=3300000,
            signer_count=10, required_signers=5, finality_blocks=12,
            current_block=145, tx_block=140,
            is_duplicate=False, emergency_mode=False,
            locked_collateral=50000000, minted_supply=50000000,
            burned_proven=3300000, released_supply=3300000,
            daily_volume=3300000, daily_cap=5000000,
            route_volume=3300000, route_cap=1000000,
            asset_cap=10000000, total_inflow=50000000, total_outflow=3300000,
            config_change_cooled=True
        ),
        "Heco Bridge (HTX)": TransferSimulation(
            source_chain="Ethereum", dest_chain="Heco", asset="ETH", amount=86600000,
            signer_count=4, required_signers=2, finality_blocks=10,
            current_block=200, tx_block=200,
            is_duplicate=False, emergency_mode=False,
            locked_collateral=50000000, minted_supply=86600000,
            burned_proven=0, released_supply=0,
            daily_volume=86600000, daily_cap=20000000,
            route_volume=86600000, route_cap=50000000,
            asset_cap=100000000, total_inflow=50000000, total_outflow=86600000
        ),
        "Mixin Network": TransferSimulation(
            source_chain="Bitcoin", dest_chain="Ethereum", asset="BTC", amount=200000000,
            signer_count=8, required_signers=4, finality_blocks=6,
            current_block=36, tx_block=30,
            is_duplicate=False, emergency_mode=False,
            locked_collateral=500000000, minted_supply=490000000,
            burned_proven=10000000, released_supply=200000000,
            daily_volume=200000000, daily_cap=50000000,
            route_volume=200000000, route_cap=100000000,
            asset_cap=500000000, total_inflow=500000000, total_outflow=500000000
        ),
        "LI.FI protocol": TransferSimulation(
            source_chain="Arbitrum", dest_chain="Optimism", asset="USDC", amount=11600000,
            signer_count=8, required_signers=5, finality_blocks=10,
            current_block=80, tx_block=80,
            is_duplicate=True, emergency_mode=False,
            locked_collateral=50000000, minted_supply=50000000,
            burned_proven=0, released_supply=11600000,
            daily_volume=11600000, daily_cap=5000000,
            route_volume=11600000, route_cap=2000000,
            asset_cap=20000000, total_inflow=50000000, total_outflow=11600000
        ),
        "Celer cBridge DNS hijack": TransferSimulation(
            source_chain="Ethereum", dest_chain="BSC", asset="USDC", amount=0,
            signer_count=12, required_signers=8, finality_blocks=10,
            current_block=120, tx_block=120,
            is_duplicate=False, emergency_mode=False,
            locked_collateral=100000000, minted_supply=100000000,
            burned_proven=0, released_supply=0,
            daily_volume=0, daily_cap=50000000,
            route_volume=0, route_cap=20000000,
            asset_cap=200000000, total_inflow=100000000, total_outflow=0,
            config_change_cooled=False
        ),
        "Kelp DAO rsETH Bridge": TransferSimulation(
            source_chain="Ethereum", dest_chain="Arbitrum", asset="rsETH", amount=292000000,
            signer_count=5, required_signers=3, finality_blocks=15,
            current_block=150, tx_block=150,
            is_duplicate=False, emergency_mode=False,
            locked_collateral=500000000, minted_supply=792000000,
            burned_proven=0, released_supply=292000000,
            daily_volume=292000000, daily_cap=50000000,
            route_volume=292000000, route_cap=100000000,
            asset_cap=500000000, total_inflow=500000000, total_outflow=292000000,
            config_change_cooled=False
        ),
        "Shibarium Bridge": TransferSimulation(
            source_chain="Ethereum", dest_chain="Shibarium", asset="BONE", amount=2400000,
            signer_count=3, required_signers=2, finality_blocks=10,
            current_block=100, tx_block=100,
            is_duplicate=False, emergency_mode=False,
            locked_collateral=5000000, minted_supply=5000000,
            burned_proven=2600000, released_supply=5000000,
            daily_volume=2400000, daily_cap=1000000,
            route_volume=2400000, route_cap=2000000,
            asset_cap=5000000, total_inflow=5000000, total_outflow=5000000
        ),
        "Nervos Force Bridge": TransferSimulation(
            source_chain="Ethereum", dest_chain="Nervos", asset="USDC", amount=3900000,
            signer_count=5, required_signers=3, finality_blocks=12,
            current_block=80, tx_block=80,
            is_duplicate=False, emergency_mode=False,
            locked_collateral=10000000, minted_supply=13900000,
            burned_proven=0, released_supply=3900000,
            daily_volume=3900000, daily_cap=2000000,
            route_volume=3900000, route_cap=3000000,
            asset_cap=10000000, total_inflow=10000000, total_outflow=3900000
        ),
        "Verus Ethereum Bridge": TransferSimulation(
            source_chain="Verus", dest_chain="Ethereum", asset="ETH", amount=11580000,
            signer_count=3, required_signers=2, finality_blocks=6,
            current_block=50, tx_block=50,
            is_duplicate=False, emergency_mode=False,
            locked_collateral=20000000, minted_supply=20000000,
            burned_proven=8420000, released_supply=20000000,
            daily_volume=11580000, daily_cap=5000000,
            route_volume=11580000, route_cap=10000000,
            asset_cap=20000000, total_inflow=20000000, total_outflow=20000000
        ),
        "NoOnes Solana Bridge": TransferSimulation(
            source_chain="Solana", dest_chain="Ethereum", asset="USDT", amount=8000000,
            signer_count=5, required_signers=3, finality_blocks=20,
            current_block=120, tx_block=120,
            is_duplicate=False, emergency_mode=False,
            locked_collateral=50000000, minted_supply=50000000,
            burned_proven=42000000, released_supply=50000000,
            daily_volume=8000000, daily_cap=5000000,
            route_volume=8000000, route_cap=10000000,
            asset_cap=5000000, total_inflow=50000000, total_outflow=50000000
        ),
    }
    return mapping.get(attack.name, TransferSimulation(
        source_chain="unknown", dest_chain="unknown", asset="ETH", amount=100,
        locked_collateral=0, minted_supply=100
    ))
