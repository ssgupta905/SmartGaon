"""Voice API request and response models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VoiceSessionStartRequest(BaseModel):
    """Request model for starting a voice session."""
    
    user_id: str = Field(..., min_length=1, description="Enterprise/user identifier")
    language_code: str = Field(..., description="Language code (hi, ta, te)")


class VoiceSessionStartResponse(BaseModel):
    """Response model for voice session creation."""
    
    session_id: str = Field(..., description="Unique session identifier")
    session_token: str = Field(..., description="Session authentication token")
    language_code: str = Field(..., description="Session language code")
    start_time: datetime = Field(..., description="Session start timestamp")


class TranscribeRequest(BaseModel):
    """Request model for audio transcription."""
    
    session_id: str = Field(..., min_length=1, description="Session identifier")
    audio_data: str = Field(..., description="Base64 encoded audio data")
    language_code: str = Field(..., description="Language code (hi, ta, te)")


class TranscribeResponse(BaseModel):
    """Response model for transcription."""
    
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    language: str = Field(..., description="Detected language code")


class SynthesizeRequest(BaseModel):
    """Request model for speech synthesis."""
    
    text: str = Field(..., min_length=1, description="Text to synthesize")
    language_code: str = Field(..., description="Language code (hi, ta, te)")
    voice_profile: str = Field(
        default="female_default",
        description="Voice profile to use"
    )


class SynthesizeResponse(BaseModel):
    """Response model for speech synthesis."""
    
    audio_data: str = Field(..., description="Base64 encoded audio data")
    duration: float = Field(..., gt=0, description="Audio duration in seconds")
    language: str = Field(..., description="Language code")


class VoiceQueryRequest(BaseModel):
    """Request model for end-to-end voice query."""
    
    session_id: str = Field(..., min_length=1, description="Session identifier")
    audio_data: str = Field(..., description="Base64 encoded audio data")


class VoiceQueryResponse(BaseModel):
    """Response model for voice query."""
    
    response_text: str = Field(..., description="Agent response text")
    response_audio: str = Field(..., description="Base64 encoded response audio")
    agent_used: Optional[str] = Field(None, description="Agent that handled the query")
    intent: Optional[str] = Field(None, description="Classified intent")
    confidence: float = Field(..., description="Transcription confidence")
