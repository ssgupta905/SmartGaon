# DynamoDB Table Reference

Complete reference for all GramSaarthi AI DynamoDB tables.

## Table Schemas

### 1. EnterpriseProfiles

**Purpose**: Store enterprise registration and profile data

**Keys**:
- PK: `ENTERPRISE#{enterprise_id}`
- SK: `PROFILE`

**Attributes**:
```json
{
  "PK": "ENTERPRISE#ent-001",
  "SK": "PROFILE",
  "enterprise_id": "string (UUID)",
  "type": "SHG|FPO|COOPERATIVE|MSME",
  "name": "string",
  "products": ["string"],
  "location": {
    "state": "string",
    "district": "string",
    "block": "string",
    "village": "string",
    "coordinates": {"lat": "number", "lon": "number"}
  },
  "contact": {
    "phone": "string",
    "alternate_phone": "string",
    "preferred_language": "hi|ta|te"
  },
  "registration_date": "ISO 8601",
  "last_updated": "ISO 8601",
  "metadata": {
    "member_count": "number",
    "annual_turnover": "number",
    "primary_market": "string"
  }
}
```

**Access Patterns**:
- Get profile: `PK = ENTERPRISE#{id} AND SK = PROFILE`
- List all profiles: Scan (use sparingly)

---

### 2. VoiceSessions

**Purpose**: Track voice interaction sessions and conversation history

**Keys**:
- PK: `SESSION#{session_id}`
- SK: `METADATA`

**GSI2 - SessionsByEnterprise**:
- PK: `enterprise_id`
- SK: `start_time`

**Attributes**:
```json
{
  "PK": "SESSION#sess-001",
  "SK": "METADATA",
  "session_id": "string (UUID)",
  "enterprise_id": "string",
  "language_code": "hi|ta|te",
  "start_time": "ISO 8601",
  "last_activity": "ISO 8601",
  "status": "ACTIVE|COMPLETED|TIMEOUT",
  "conversation_turns": [
    {
      "turn_id": "number",
      "timestamp": "ISO 8601",
      "user_audio_s3_key": "string",
      "user_text": "string",
      "intent": "string",
      "agent_used": "string",
      "response_text": "string",
      "response_audio_s3_key": "string"
    }
  ],
  "context": {
    "current_topic": "string",
    "entities": "map",
    "pending_questions": ["string"]
  },
  "ttl": "number (Unix timestamp)"
}
```

**Access Patterns**:
- Get session: `PK = SESSION#{id} AND SK = METADATA`
- Get enterprise sessions: GSI2 query on `enterprise_id`

**TTL**: 7 days (auto-delete old sessions)

---

### 3. ActionPlans

**Purpose**: Store scheme application action plans and progress

**Keys**:
- PK: `ENTERPRISE#{enterprise_id}`
- SK: `PLAN#{plan_id}`

**Attributes**:
```json
{
  "PK": "ENTERPRISE#ent-001",
  "SK": "PLAN#plan-001",
  "plan_id": "string (UUID)",
  "enterprise_id": "string",
  "scheme_id": "string",
  "scheme_name": "string",
  "created_date": "ISO 8601",
  "status": "IN_PROGRESS|COMPLETED|ABANDONED",
  "steps": [
    {
      "step_id": "string",
      "step_number": "number",
      "description": "string",
      "required_documents": ["string"],
      "deadline": "ISO 8601",
      "status": "PENDING|IN_PROGRESS|COMPLETED",
      "completed_date": "ISO 8601",
      "notes": "string"
    }
  ],
  "progress_percentage": "number",
  "next_reminder_date": "ISO 8601",
  "contact_info": {
    "office_name": "string",
    "phone": "string",
    "address": "string"
  }
}
```

**Access Patterns**:
- Get plan: `PK = ENTERPRISE#{id} AND SK = PLAN#{plan_id}`
- Get all plans for enterprise: Query with `begins_with(SK, 'PLAN#')`

---

### 4. FinancialData

**Purpose**: Store monthly financial data for enterprises

**Keys**:
- PK: `ENTERPRISE#{enterprise_id}`
- SK: `FINANCIAL#{period}` (period: YYYY-MM)

**Attributes**:
```json
{
  "PK": "ENTERPRISE#ent-001",
  "SK": "FINANCIAL#2024-01",
  "enterprise_id": "string",
  "period": "YYYY-MM",
  "recorded_date": "ISO 8601",
  "sales": {
    "total_revenue": "number",
    "product_breakdown": [
      {"product": "string", "quantity": "number", "revenue": "number"}
    ]
  },
  "expenses": {
    "total_expenses": "number",
    "categories": {
      "raw_materials": "number",
      "labor": "number",
      "transport": "number",
      "utilities": "number",
      "other": "number"
    }
  },
  "inventory": {
    "products": [
      {"product": "string", "quantity": "number", "value": "number"}
    ],
    "total_value": "number"
  },
  "cash_flow": {
    "opening_balance": "number",
    "closing_balance": "number",
    "receivables": "number",
    "payables": "number"
  },
  "calculated_metrics": {
    "profit_margin": "number",
    "net_profit": "number",
    "cash_flow_change": "number"
  }
}
```

**Access Patterns**:
- Get period data: `PK = ENTERPRISE#{id} AND SK = FINANCIAL#{period}`
- Get financial history: Query with `begins_with(SK, 'FINANCIAL#')`

---

### 5. OperationalData

**Purpose**: Track daily operational metrics

**Keys**:
- PK: `ENTERPRISE#{enterprise_id}`
- SK: `OPS#{date}` (date: YYYY-MM-DD)

**Attributes**:
```json
{
  "PK": "ENTERPRISE#ent-001",
  "SK": "OPS#2024-01-15",
  "enterprise_id": "string",
  "date": "YYYY-MM-DD",
  "recorded_timestamp": "ISO 8601",
  "daily_sales": {
    "total": "number",
    "transactions": "number",
    "products_sold": [
      {"product": "string", "quantity": "number", "revenue": "number"}
    ]
  },
  "inventory_snapshot": {
    "products": [
      {
        "product": "string",
        "quantity": "number",
        "reorder_level": "number",
        "alert_triggered": "boolean"
      }
    ]
  },
  "cash_position": "number",
  "notes": "string"
}
```

**Access Patterns**:
- Get daily data: `PK = ENTERPRISE#{id} AND SK = OPS#{date}`
- Get date range: Query with `SK BETWEEN OPS#{start} AND OPS#{end}`

---

### 6. Schemes

**Purpose**: Government scheme database with eligibility criteria

**Keys**:
- PK: `SCHEME#{scheme_id}`
- SK: `METADATA`

**GSI3 - SchemesByType**:
- PK: `scheme_type`
- SK: `last_updated`

**Attributes**:
```json
{
  "PK": "SCHEME#scheme-001",
  "SK": "METADATA",
  "scheme_id": "string (UUID)",
  "name": "string",
  "name_local": {"hi": "string", "ta": "string"},
  "description": "string",
  "description_local": {"hi": "string", "ta": "string"},
  "scheme_type": "LOAN|SUBSIDY|GRANT|TRAINING",
  "authority": "CENTRAL|STATE",
  "state": "string (optional)",
  "eligibility_criteria": {
    "enterprise_types": ["SHG", "FPO"],
    "min_turnover": "number (optional)",
    "max_turnover": "number (optional)",
    "sectors": ["string"],
    "other_requirements": ["string"]
  },
  "benefits": {
    "financial_benefit": "string",
    "benefit_amount": "number (optional)",
    "other_benefits": ["string"]
  },
  "application_process": {
    "required_documents": ["string"],
    "application_url": "string",
    "contact_info": {
      "office": "string",
      "phone": "string",
      "email": "string"
    }
  },
  "deadlines": {
    "application_deadline": "ISO 8601 (optional)",
    "is_ongoing": "boolean"
  },
  "last_updated": "ISO 8601",
  "source_url": "string"
}
```

**Access Patterns**:
- Get scheme: `PK = SCHEME#{id} AND SK = METADATA`
- Browse by type: GSI3 query on `scheme_type`
- List all schemes: Scan

---

### 7. MandiPrices

**Purpose**: Agricultural commodity market prices

**Keys**:
- PK: `COMMODITY#{commodity_name}`
- SK: `PRICE#{state}#{market}#{date}`

**Attributes**:
```json
{
  "PK": "COMMODITY#tomato",
  "SK": "PRICE#Maharashtra#Pune Mandi#2024-01-15",
  "commodity_name": "string",
  "state": "string",
  "district": "string",
  "market_name": "string",
  "date": "YYYY-MM-DD",
  "price_min": "number",
  "price_max": "number",
  "price_modal": "number",
  "unit": "quintal|kg",
  "arrivals": "number",
  "source": "agmarknet",
  "fetched_timestamp": "ISO 8601",
  "ttl": "number (Unix timestamp)"
}
```

**Access Patterns**:
- Get commodity prices: Query with `PK = COMMODITY#{name}`
- Get market prices: Query with `PK = COMMODITY#{name} AND begins_with(SK, 'PRICE#{state}#{market}#')`
- Get date range: Query with `SK BETWEEN ... AND ...`

**TTL**: 90 days (auto-delete old prices)

---

### 8. Alerts

**Purpose**: Proactive alerts and notifications

**Keys**:
- PK: `ENTERPRISE#{enterprise_id}`
- SK: `ALERT#{alert_id}`

**GSI1 - AlertsByStatus**:
- PK: `alert_status`
- SK: `created_date`

**Attributes**:
```json
{
  "PK": "ENTERPRISE#ent-001",
  "SK": "ALERT#alert-001",
  "alert_id": "string (UUID)",
  "enterprise_id": "string",
  "alert_type": "PRICE|INVENTORY|DEADLINE|CASH_FLOW|SCHEME",
  "severity": "INFO|WARNING|CRITICAL",
  "title": "string",
  "message": "string",
  "created_date": "ISO 8601",
  "status": "PENDING|SENT|ACKNOWLEDGED|DISMISSED",
  "delivery_method": "VOICE_CALL|SMS|IN_APP",
  "delivery_timestamp": "ISO 8601 (optional)",
  "related_entity_id": "string (optional)",
  "action_required": "boolean",
  "ttl": "number (Unix timestamp)"
}
```

**Access Patterns**:
- Get enterprise alerts: Query with `PK = ENTERPRISE#{id} AND begins_with(SK, 'ALERT#')`
- Get pending alerts: GSI1 query on `alert_status = PENDING`

**TTL**: 30 days (auto-delete old alerts)

---

### 9. AnalyticsEvents

**Purpose**: Platform usage analytics and events

**Keys**:
- PK: `EVENT#{date}` (date: YYYY-MM-DD)
- SK: `#{timestamp}#{event_id}`

**Attributes**:
```json
{
  "PK": "EVENT#2024-01-15",
  "SK": "#2024-01-15T10:30:00Z#evt-001",
  "event_id": "string (UUID)",
  "timestamp": "ISO 8601",
  "event_type": "QUERY|REGISTRATION|ALERT|PLAN_CREATED",
  "enterprise_id": "string (optional)",
  "session_id": "string (optional)",
  "agent_used": "string (optional)",
  "intent": "string (optional)",
  "latency_ms": "number",
  "success": "boolean",
  "error_message": "string (optional)",
  "metadata": "map",
  "ttl": "number (Unix timestamp)"
}
```

**Access Patterns**:
- Get daily events: Query with `PK = EVENT#{date}`
- Get date range: Multiple queries or scan with filter

**TTL**: 90 days (auto-delete old events)

---

## Index Summary

| Index | Table | Purpose | Keys |
|-------|-------|---------|------|
| GSI1-AlertsByStatus | Alerts | Query pending alerts | alert_status (H), created_date (R) |
| GSI2-SessionsByEnterprise | VoiceSessions | Get enterprise sessions | enterprise_id (H), start_time (R) |
| GSI3-SchemesByType | Schemes | Browse schemes by type | scheme_type (H), last_updated (R) |

## Key Patterns

### Single-Table Design
All tables use composite keys (PK/SK) for flexible access patterns:
- **PK**: Entity identifier (e.g., `ENTERPRISE#id`, `COMMODITY#name`)
- **SK**: Sub-entity or metadata (e.g., `PROFILE`, `PLAN#id`, `PRICE#...`)

### Benefits
- Efficient queries with `begins_with()` on SK
- Related data co-located for fast access
- Flexible schema evolution
- Cost-effective (fewer tables = fewer requests)

### Query Examples

```python
# Get all plans for enterprise
response = table.query(
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
    ExpressionAttributeValues={
        ':pk': 'ENTERPRISE#ent-001',
        ':sk': 'PLAN#'
    }
)

# Get financial history (last 6 months)
response = table.query(
    KeyConditionExpression='PK = :pk AND SK BETWEEN :start AND :end',
    ExpressionAttributeValues={
        ':pk': 'ENTERPRISE#ent-001',
        ':start': 'FINANCIAL#2023-07',
        ':end': 'FINANCIAL#2024-01'
    }
)

# Get pending alerts (using GSI)
response = table.query(
    IndexName='GSI1-AlertsByStatus',
    KeyConditionExpression='alert_status = :status',
    ExpressionAttributeValues={
        ':status': 'PENDING'
    }
)
```

## Best Practices

1. **Always use KeyConditionExpression**: More efficient than FilterExpression
2. **Limit scan operations**: Use queries with indexes instead
3. **Batch operations**: Use batch_get_item and batch_write_item for multiple items
4. **Consistent reads**: Use ConsistentRead=True only when necessary
5. **Projection expressions**: Fetch only needed attributes to reduce costs
6. **TTL for cleanup**: Let DynamoDB auto-delete expired items
7. **Exponential backoff**: Implement retry logic for throttling

## Cost Optimization

- **PAY_PER_REQUEST**: Best for unpredictable traffic (hackathon/MVP)
- **PROVISIONED**: Better for predictable traffic (production)
- **Auto-scaling**: Enable for provisioned mode
- **Reserved capacity**: 1-year commitment for 50% savings
- **On-demand backups**: Free, use for critical data
- **PITR**: $0.20 per GB-month, enable for production

## Migration Path

For production deployment:
1. Enable PITR on all tables
2. Set up CloudWatch alarms
3. Consider switching to provisioned mode with auto-scaling
4. Enable DynamoDB Streams for change data capture
5. Set up cross-region replication for disaster recovery
