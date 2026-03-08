"""Orchestration data models for multi-agent coordination."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Types of specialized agents."""
    
    MARKET_INTELLIGENCE = "market_intelligence"
    SCHEME_EXECUTION = "scheme_execution"
    FINANCIAL = "financial"
    OPERATIONS = "operations"
    GENERAL = "general"


class AgentResponse(BaseModel):
    """Response from a specialized agent."""
    
    agent_type: AgentType = Field(..., description="Type of agent that generated response")
    response_text: str = Field(..., description="Agent response text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Response confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    execution_time_ms: float = Field(..., description="Agent execution time in milliseconds")
    success: bool = Field(default=True, description="Whether agent execution succeeded")
    error_message: Optional[str] = Field(None, description="Error message if execution failed")


class OrchestrationResult(BaseModel):
    """Result of multi-agent orchestration."""
    
    query: str = Field(..., description="Original user query")
    intent: str = Field(..., description="Classified intent")
    agents_invoked: List[AgentType] = Field(..., description="List of agents invoked")
    agent_responses: Dict[AgentType, AgentResponse] = Field(..., description="Responses from each agent")
    synthesized_response: str = Field(..., description="Final synthesized response")
    total_execution_time_ms: float = Field(..., description="Total orchestration time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Orchestration timestamp")
    success: bool = Field(default=True, description="Whether orchestration succeeded")
    error_message: Optional[str] = Field(None, description="Error message if orchestration failed")


class UserContext(BaseModel):
    """User context for agent processing."""
    
    enterprise_id: str = Field(..., description="Enterprise identifier")
    session_id: str = Field(..., description="Voice session identifier")
    language_code: str = Field(..., description="User's language code")
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list, description="Previous conversation turns")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities from current and past queries")
    enterprise_profile: Optional[Dict[str, Any]] = Field(None, description="Enterprise profile data")
