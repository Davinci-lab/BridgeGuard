"""seed demo project

Revision ID: 20260520_0007
Revises: 20260520_0006
Create Date: 2026-05-20 00:00:00.000000
"""
from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260520_0007"
down_revision: Union[str, None] = "20260520_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEMO_EMAIL = "demo@bridgeguard.local"
DEMO_PASSWORD_HASH = "$2b$12$aQIQ11Gy8/E9cxP142pHq.BgaLYYhXvp8zr.YSU6NLlX1VH46Z466"
DEMO_PROJECT_NAME = "Demo Bridge Operations"

DEFAULT_RISK_WEIGHTS = {
    "MINT_EXCEEDS_LOCKED": 35,
    "RELEASE_EXCEEDS_BURNED": 35,
    "OUTFLOW_EXCEEDS_INFLOW": 30,
    "EMERGENCY_MODE_ACTIVE": 100,
    "REPLAY_OR_DUPLICATE_MESSAGE": 90,
    "UNKNOWN_OR_CHANGED_ROOT": 80,
    "CONFIG_CHANGE_UNCOOLED": 70,
    "SIGNER_THRESHOLD_WEAK": 50,
    "VALIDATOR_SET_RISK": 60,
    "CHAIN_FINALITY_NOT_REACHED": 20,
    "ABNORMAL_VOLUME_SPIKE": 20,
    "ASSET_CAP_EXCEEDED": 25,
    "ROUTE_CAP_EXCEEDED": 25,
    "TVL_DIVERGENCE": 40,
    "CUSTOM": 30,
}

DEFAULT_CONNECTORS = [
    {
        "id": "demo-wormhole-sepolia",
        "name": "Wormhole Sepolia (ETH)",
        "type": "evm",
        "enabled": True,
        "rpc_url": "https://rpc.sepolia.org",
        "chain_id": 11155111,
        "contract_address": "0x4a8bc80Ed5a4067f1CCf107057b8270E0cC11A78",
        "abi": [
            {
                "inputs": [],
                "name": "numGuardians",
                "outputs": [{"internalType": "uint32", "name": "", "type": "uint32"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [],
                "name": "outstandingBridged",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [],
                "name": "emergencyShutdown",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "view",
                "type": "function",
            },
        ],
        "method_mapping": {
            "locked_collateral": "outstandingBridged",
            "minted_supply": "totalSupply",
            "burned_proven": "",
            "released_supply": "",
            "signer_count": "numGuardians",
            "required_signers": None,
            "emergency_mode": "emergencyShutdown",
            "config_change_block": None,
            "current_block": None,
        },
        "daily_cap": 1000000,
        "route_cap": 500000,
        "asset_cap": 5000000,
        "source_chain": "Sepolia",
        "dest_chain": "Wormhole Testnet",
        "asset": "ETH",
        "finality_blocks": 15,
    },
    {
        "id": "demo-axelar-sepolia",
        "name": "Axelar Gateway (Sepolia)",
        "type": "evm",
        "enabled": True,
        "rpc_url": "https://rpc.sepolia.org",
        "chain_id": 11155111,
        "contract_address": "0xe432150cce91c13a887f7D836923d5597adD8E31",
        "abi": [
            {
                "inputs": [],
                "name": "operator",
                "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [],
                "name": "emergencyShutdown",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "view",
                "type": "function",
            },
        ],
        "method_mapping": {
            "locked_collateral": "totalSupply",
            "minted_supply": "",
            "burned_proven": "",
            "released_supply": "",
            "signer_count": "",
            "required_signers": None,
            "emergency_mode": "emergencyShutdown",
            "config_change_block": None,
            "current_block": None,
        },
        "daily_cap": 1000000,
        "route_cap": 500000,
        "asset_cap": 5000000,
        "source_chain": "Sepolia",
        "dest_chain": "Axelar Testnet",
        "asset": "ETH",
        "finality_blocks": 15,
    },
]


users = sa.table(
    "users",
    sa.column("id", sa.Integer),
    sa.column("email", sa.String),
    sa.column("hashed_password", sa.String),
    sa.column("is_active", sa.Boolean),
)

projects = sa.table(
    "projects",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
    sa.column("owner_id", sa.Integer),
)

policy_configs = sa.table(
    "policy_configs",
    sa.column("project_id", sa.Integer),
    sa.column("risk_weights", sa.JSON),
    sa.column("custom_rules", sa.JSON),
    sa.column("created_at", sa.DateTime(timezone=True)),
    sa.column("updated_at", sa.DateTime(timezone=True)),
)

listeners = sa.table(
    "listeners",
    sa.column("project_id", sa.Integer),
    sa.column("connector_id", sa.String),
    sa.column("status", sa.String),
    sa.column("mode", sa.String),
    sa.column("task_id", sa.String),
    sa.column("connector_config", sa.JSON),
    sa.column("last_error", sa.Text),
    sa.column("created_at", sa.DateTime(timezone=True)),
    sa.column("updated_at", sa.DateTime(timezone=True)),
)


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)

    user_id = conn.execute(
        sa.select(users.c.id).where(users.c.email == DEMO_EMAIL)
    ).scalar_one_or_none()
    if user_id is None:
        op.bulk_insert(
            users,
            [
                {
                    "email": DEMO_EMAIL,
                    "hashed_password": DEMO_PASSWORD_HASH,
                    "is_active": True,
                }
            ],
        )
        user_id = conn.execute(
            sa.select(users.c.id).where(users.c.email == DEMO_EMAIL)
        ).scalar_one()

    project_id = conn.execute(
        sa.select(projects.c.id).where(
            projects.c.owner_id == user_id,
            projects.c.name == DEMO_PROJECT_NAME,
        )
    ).scalar_one_or_none()
    if project_id is None:
        op.bulk_insert(
            projects,
            [
                {
                    "name": DEMO_PROJECT_NAME,
                    "owner_id": user_id,
                }
            ],
        )
        project_id = conn.execute(
            sa.select(projects.c.id).where(
                projects.c.owner_id == user_id,
                projects.c.name == DEMO_PROJECT_NAME,
            )
        ).scalar_one()

    existing_policy = conn.execute(
        sa.select(policy_configs.c.project_id).where(policy_configs.c.project_id == project_id)
    ).scalar_one_or_none()
    if existing_policy is None:
        op.bulk_insert(
            policy_configs,
            [
                {
                    "project_id": project_id,
                    "risk_weights": DEFAULT_RISK_WEIGHTS,
                    "custom_rules": [],
                    "created_at": now,
                    "updated_at": now,
                }
            ],
        )

    for connector in DEFAULT_CONNECTORS:
        existing_listener = conn.execute(
            sa.select(listeners.c.connector_id).where(
                listeners.c.project_id == project_id,
                listeners.c.connector_id == connector["id"],
            )
        ).scalar_one_or_none()
        if existing_listener is not None:
            continue
        op.bulk_insert(
            listeners,
            [
                {
                    "project_id": project_id,
                    "connector_id": connector["id"],
                    "status": "stopped",
                    "mode": "polling",
                    "task_id": None,
                    "connector_config": connector,
                    "last_error": None,
                    "created_at": now,
                    "updated_at": now,
                }
            ],
        )


def downgrade() -> None:
    conn = op.get_bind()
    user_id = conn.execute(
        sa.select(users.c.id).where(users.c.email == DEMO_EMAIL)
    ).scalar_one_or_none()
    if user_id is None:
        return

    project_id = conn.execute(
        sa.select(projects.c.id).where(
            projects.c.owner_id == user_id,
            projects.c.name == DEMO_PROJECT_NAME,
        )
    ).scalar_one_or_none()
    if project_id is not None:
        connector_ids = [connector["id"] for connector in DEFAULT_CONNECTORS]
        op.execute(
            listeners.delete().where(
                listeners.c.project_id == project_id,
                listeners.c.connector_id.in_(connector_ids),
            )
        )
        op.execute(policy_configs.delete().where(policy_configs.c.project_id == project_id))
        op.execute(projects.delete().where(projects.c.id == project_id))

    remaining_projects = conn.execute(
        sa.select(projects.c.id).where(projects.c.owner_id == user_id)
    ).first()
    if remaining_projects is None:
        op.execute(users.delete().where(users.c.id == user_id))
