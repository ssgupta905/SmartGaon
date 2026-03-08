"""DynamoDB table schema definitions for GramSaarthi AI."""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class TableSchema:
    """Schema definition for a DynamoDB table."""
    
    table_name: str
    key_schema: List[Dict[str, str]]
    attribute_definitions: List[Dict[str, str]]
    global_secondary_indexes: List[Dict[str, Any]] = None
    billing_mode: str = "PAY_PER_REQUEST"
    ttl_attribute: str = None


# EnterpriseProfiles Table
ENTERPRISE_PROFILES_SCHEMA = TableSchema(
    table_name="EnterpriseProfiles",
    key_schema=[
        {"AttributeName": "PK", "KeyType": "HASH"},
        {"AttributeName": "SK", "KeyType": "RANGE"}
    ],
    attribute_definitions=[
        {"AttributeName": "PK", "AttributeType": "S"},
        {"AttributeName": "SK", "AttributeType": "S"}
    ]
)

# VoiceSessions Table
VOICE_SESSIONS_SCHEMA = TableSchema(
    table_name="VoiceSessions",
    key_schema=[
        {"AttributeName": "PK", "KeyType": "HASH"},
        {"AttributeName": "SK", "KeyType": "RANGE"}
    ],
    attribute_definitions=[
        {"AttributeName": "PK", "AttributeType": "S"},
        {"AttributeName": "SK", "AttributeType": "S"},
        {"AttributeName": "enterprise_id", "AttributeType": "S"},
        {"AttributeName": "start_time", "AttributeType": "S"}
    ],
    global_secondary_indexes=[
        {
            "IndexName": "GSI2-SessionsByEnterprise",
            "KeySchema": [
                {"AttributeName": "enterprise_id", "KeyType": "HASH"},
                {"AttributeName": "start_time", "KeyType": "RANGE"}
            ],
            "Projection": {"ProjectionType": "ALL"}
        }
    ],
    ttl_attribute="ttl"
)

# ActionPlans Table
ACTION_PLANS_SCHEMA = TableSchema(
    table_name="ActionPlans",
    key_schema=[
        {"AttributeName": "PK", "KeyType": "HASH"},
        {"AttributeName": "SK", "KeyType": "RANGE"}
    ],
    attribute_definitions=[
        {"AttributeName": "PK", "AttributeType": "S"},
        {"AttributeName": "SK", "AttributeType": "S"}
    ]
)

# FinancialData Table
FINANCIAL_DATA_SCHEMA = TableSchema(
    table_name="FinancialData",
    key_schema=[
        {"AttributeName": "PK", "KeyType": "HASH"},
        {"AttributeName": "SK", "KeyType": "RANGE"}
    ],
    attribute_definitions=[
        {"AttributeName": "PK", "AttributeType": "S"},
        {"AttributeName": "SK", "AttributeType": "S"}
    ]
)

# OperationalData Table
OPERATIONAL_DATA_SCHEMA = TableSchema(
    table_name="OperationalData",
    key_schema=[
        {"AttributeName": "PK", "KeyType": "HASH"},
        {"AttributeName": "SK", "KeyType": "RANGE"}
    ],
    attribute_definitions=[
        {"AttributeName": "PK", "AttributeType": "S"},
        {"AttributeName": "SK", "AttributeType": "S"}
    ]
)

# Schemes Table
SCHEMES_SCHEMA = TableSchema(
    table_name="Schemes",
    key_schema=[
        {"AttributeName": "PK", "KeyType": "HASH"},
        {"AttributeName": "SK", "KeyType": "RANGE"}
    ],
    attribute_definitions=[
        {"AttributeName": "PK", "AttributeType": "S"},
        {"AttributeName": "SK", "AttributeType": "S"},
        {"AttributeName": "scheme_type", "AttributeType": "S"},
        {"AttributeName": "last_updated", "AttributeType": "S"}
    ],
    global_secondary_indexes=[
        {
            "IndexName": "GSI3-SchemesByType",
            "KeySchema": [
                {"AttributeName": "scheme_type", "KeyType": "HASH"},
                {"AttributeName": "last_updated", "KeyType": "RANGE"}
            ],
            "Projection": {"ProjectionType": "ALL"}
        }
    ]
)

# MandiPrices Table
MANDI_PRICES_SCHEMA = TableSchema(
    table_name="MandiPrices",
    key_schema=[
        {"AttributeName": "PK", "KeyType": "HASH"},
        {"AttributeName": "SK", "KeyType": "RANGE"}
    ],
    attribute_definitions=[
        {"AttributeName": "PK", "AttributeType": "S"},
        {"AttributeName": "SK", "AttributeType": "S"}
    ],
    ttl_attribute="ttl"
)

# Alerts Table
ALERTS_SCHEMA = TableSchema(
    table_name="Alerts",
    key_schema=[
        {"AttributeName": "PK", "KeyType": "HASH"},
        {"AttributeName": "SK", "KeyType": "RANGE"}
    ],
    attribute_definitions=[
        {"AttributeName": "PK", "AttributeType": "S"},
        {"AttributeName": "SK", "AttributeType": "S"},
        {"AttributeName": "alert_status", "AttributeType": "S"},
        {"AttributeName": "created_date", "AttributeType": "S"}
    ],
    global_secondary_indexes=[
        {
            "IndexName": "GSI1-AlertsByStatus",
            "KeySchema": [
                {"AttributeName": "alert_status", "KeyType": "HASH"},
                {"AttributeName": "created_date", "KeyType": "RANGE"}
            ],
            "Projection": {"ProjectionType": "ALL"}
        }
    ],
    ttl_attribute="ttl"
)

# AnalyticsEvents Table
ANALYTICS_EVENTS_SCHEMA = TableSchema(
    table_name="AnalyticsEvents",
    key_schema=[
        {"AttributeName": "PK", "KeyType": "HASH"},
        {"AttributeName": "SK", "KeyType": "RANGE"}
    ],
    attribute_definitions=[
        {"AttributeName": "PK", "AttributeType": "S"},
        {"AttributeName": "SK", "AttributeType": "S"}
    ],
    ttl_attribute="ttl"
)

# All table schemas
ALL_TABLE_SCHEMAS = [
    ENTERPRISE_PROFILES_SCHEMA,
    VOICE_SESSIONS_SCHEMA,
    ACTION_PLANS_SCHEMA,
    FINANCIAL_DATA_SCHEMA,
    OPERATIONAL_DATA_SCHEMA,
    SCHEMES_SCHEMA,
    MANDI_PRICES_SCHEMA,
    ALERTS_SCHEMA,
    ANALYTICS_EVENTS_SCHEMA
]


# Helper function to get table name
def get_table_name(table_name: str) -> str:
    """
    Get the full table name for a given table.
    
    Args:
        table_name: Base table name (e.g., "EnterpriseProfiles", "OperationalData")
        
    Returns:
        Full table name (same as input for now, can be prefixed in production)
    """
    # In production, this could add environment prefixes like "dev-", "prod-"
    return table_name
