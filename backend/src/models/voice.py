"""Voice processing data models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class LanguageCode(str, Enum):
    """Supported Indic language codes."""
    
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"


class SessionStatus(str, Enum):
    """Voice session status."""
    
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    TIMEOUT = "TIMEOUT"


class TranscriptionResult(BaseModel):
    """Result of speech-to-text transcription."""
    
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    language: LanguageCode = Field(..., description="Detected language code")
    
    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate transcribed text is non-empty."""
        if not v or not v.strip():
            raise ValueError("Transcribed text cannot be empty")
        return v.strip()
    
    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Validate confidence is in valid range."""
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class SynthesisResult(BaseModel):
    """Result of text-to-speech synthesis."""
    
    audio_data: bytes = Field(..., description="Audio data in WAV format")
    duration: float = Field(..., gt=0, description="Audio duration in seconds")
    language: LanguageCode = Field(..., description="Language code")
    
    @field_validator("audio_data")
    @classmethod
    def validate_audio_data(cls, v: bytes) -> bytes:
        """Validate audio data is non-empty."""
        if not v:
            raise ValueError("Audio data cannot be empty")
        return v
    
    @field_validator("duration")
    @classmethod
    def validate_duration(cls, v: float) -> float:
        """Validate duration is positive."""
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v



class ConversationTurn(BaseModel):
    """A single turn in a voice conversation."""
    
    turn_id: int = Field(..., ge=0, description="Turn number in conversation")
    timestamp: datetime = Field(..., description="Turn timestamp")
    user_audio_s3_key: Optional[str] = Field(None, description="S3 key for user audio")
    user_text: str = Field(..., description="Transcribed user text")
    intent: Optional[str] = Field(None, description="Classified intent")
    agent_used: Optional[str] = Field(None, description="Agent that handled the query")
    response_text: str = Field(..., description="Agent response text")
    response_audio_s3_key: Optional[str] = Field(None, description="S3 key for response audio")
    
    @field_validator("user_text", "response_text")
    @classmethod
    def validate_text_not_empty(cls, v: str) -> str:
        """Validate text is non-empty."""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()


class SessionContext(BaseModel):
    """Context information for a voice session."""
    
    current_topic: Optional[str] = Field(None, description="Current conversation topic")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities")
    pending_questions: List[str] = Field(default_factory=list, description="Questions awaiting response")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "current_topic": "market_pricing",
                "entities": {"commodity": "tomato", "location": "Delhi"},
                "pending_questions": []
            }
        }


class VoiceSession(BaseModel):
    """Voice session data model."""
    
    session_id: str = Field(..., description="Unique session identifier")
    enterprise_id: str = Field(..., description="Enterprise identifier")
    language_code: LanguageCode = Field(..., description="Session language")
    start_time: datetime = Field(..., description="Session start time")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    status: SessionStatus = Field(default=SessionStatus.ACTIVE, description="Session status")
    conversation_turns: List[ConversationTurn] = Field(default_factory=list, description="Conversation history")
    context: SessionContext = Field(default_factory=SessionContext, description="Session context")
    ttl: Optional[int] = Field(None, description="TTL for auto-deletion (Unix timestamp)")
    
    @field_validator("session_id", "enterprise_id")
    @classmethod
    def validate_id_not_empty(cls, v: str) -> str:
        """Validate ID is non-empty."""
        if not v or not v.strip():
            raise ValueError("ID cannot be empty")
        return v.strip()
    
    def add_turn(self, turn: ConversationTurn) -> None:
        """
        Add a conversation turn to the session.
        
        Args:
            turn: Conversation turn to add
        """
        self.conversation_turns.append(turn)
        self.last_activity = turn.timestamp
    
    def update_context(self, **kwargs) -> None:
        """
        Update session context.
        
        Args:
            **kwargs: Context fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self.context, key):
                setattr(self.context, key, value)
    
    def is_active(self, timeout_minutes: int = 5) -> bool:
        """
        Check if session is still active based on timeout.
        
        Args:
            timeout_minutes: Inactivity timeout in minutes
            
        Returns:
            True if session is active, False if timed out
        """
        if self.status != SessionStatus.ACTIVE:
            return False
        
        from datetime import timedelta
        timeout_threshold = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        return self.last_activity > timeout_threshold
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "enterprise_id": "ent_123",
                "language_code": "hi",
                "start_time": "2024-01-15T10:30:00Z",
                "last_activity": "2024-01-15T10:35:00Z",
                "status": "ACTIVE",
                "conversation_turns": [],
                "context": {
                    "current_topic": None,
                    "entities": {},
                    "pending_questions": []
                }
            }
        }
