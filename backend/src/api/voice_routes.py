"""Voice interaction API routes."""

import base64
from typing import Dict, Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse

from src.api.voice_models import (
    VoiceSessionStartRequest,
    VoiceSessionStartResponse,
    TranscribeRequest,
    TranscribeResponse,
    SynthesizeRequest,
    SynthesizeResponse,
    VoiceQueryRequest,
    VoiceQueryResponse,
)
from src.api.models import ErrorResponse
from src.services.voice_session_manager import VoiceSessionManager
from src.services.speech_to_text_service import SpeechToTextService
from src.services.text_to_speech_service import TextToSpeechService


router = APIRouter(prefix="/api/v1/voice", tags=["voice"])


def create_error_response(
    error_type: str,
    message: str,
    details: Dict[str, Any] = None,
    request_id: str = None,
) -> ErrorResponse:
    """Create a standardized error response."""
    return ErrorResponse(
        error=error_type,
        message=message,
        details=details,
        request_id=request_id,
    )


@router.post(
    "/session/start",
    response_model=VoiceSessionStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create voice session",
    description="Start a new voice interaction session",
    responses={
        201: {"description": "Session successfully created"},
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def start_voice_session(
    request: Request,
    session_data: VoiceSessionStartRequest,
) -> VoiceSessionStartResponse:
    """
    Create a new voice session.
    
    Initializes a voice session for the user with the specified language.
    The session maintains conversation context and has a 5-minute inactivity timeout.
    
    Args:
        request: FastAPI request object
        session_data: Session creation data
        
    Returns:
        Created session with session_id and token
        
    Raises:
        HTTPException: If session creation fails
    """
    request_id = str(uuid4())
    
    try:
        # Create voice session
        session_manager = VoiceSessionManager()
        session = session_manager.create_session(
            user_id=session_data.user_id,
            language_code=session_data.language_code
        )
        
        # Generate session token (for MVP, use session_id as token)
        # In production, this would be a JWT or similar
        session_token = session.session_id
        
        return VoiceSessionStartResponse(
            session_id=session.session_id,
            session_token=session_token,
            language_code=session.language_code.value,
            start_time=session.start_time,
        )
    except ValueError as e:
        # Validation error (e.g., unsupported language)
        error = create_error_response(
            error_type="VALIDATION_ERROR",
            message=str(e),
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.model_dump(),
        )
    except Exception as e:
        # Unexpected error
        error = create_error_response(
            error_type="INTERNAL_ERROR",
            message="Failed to create voice session",
            details={"error": str(e)},
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )


@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    summary="Transcribe audio",
    description="Convert Indic language audio to text",
    responses={
        200: {"description": "Audio successfully transcribed"},
        400: {"model": ErrorResponse, "description": "Invalid audio or session"},
        404: {"model": ErrorResponse, "description": "Session not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def transcribe_audio(
    request: Request,
    transcribe_data: TranscribeRequest,
) -> TranscribeResponse:
    """
    Transcribe audio to text.
    
    Converts Indic language speech to text using AI4Bharat models (mock for MVP).
    Validates the session exists and is active before processing.
    
    Args:
        request: FastAPI request object
        transcribe_data: Transcription request data
        
    Returns:
        Transcribed text with confidence score
        
    Raises:
        HTTPException: If transcription fails
    """
    request_id = str(uuid4())
    
    try:
        # Validate session exists and is active
        session_manager = VoiceSessionManager()
        session = session_manager.get_session(transcribe_data.session_id)
        
        if session is None:
            error = create_error_response(
                error_type="SESSION_NOT_FOUND",
                message=f"Session {transcribe_data.session_id} not found or expired",
                request_id=request_id,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error.model_dump(),
            )
        
        # Decode base64 audio data
        try:
            audio_bytes = base64.b64decode(transcribe_data.audio_data)
        except Exception as e:
            error = create_error_response(
                error_type="INVALID_AUDIO_DATA",
                message="Failed to decode audio data. Must be valid base64.",
                details={"error": str(e)},
                request_id=request_id,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error.model_dump(),
            )
        
        # Transcribe audio
        stt_service = SpeechToTextService()
        result = stt_service.transcribe(
            audio_data=audio_bytes,
            language_code=transcribe_data.language_code,
            session_id=transcribe_data.session_id
        )
        
        return TranscribeResponse(
            text=result.text,
            confidence=result.confidence,
            language=result.language.value,
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        # Validation error
        error = create_error_response(
            error_type="VALIDATION_ERROR",
            message=str(e),
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.model_dump(),
        )
    except Exception as e:
        # Unexpected error
        error = create_error_response(
            error_type="INTERNAL_ERROR",
            message="Failed to transcribe audio",
            details={"error": str(e)},
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )


@router.post(
    "/synthesize",
    response_model=SynthesizeResponse,
    summary="Generate speech",
    description="Convert text to Indic language speech",
    responses={
        200: {"description": "Speech successfully generated"},
        400: {"model": ErrorResponse, "description": "Invalid text or language"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def synthesize_speech(
    request: Request,
    synthesize_data: SynthesizeRequest,
) -> SynthesizeResponse:
    """
    Convert text to speech.
    
    Generates natural Indic language speech from text using AI4Bharat models (mock for MVP).
    
    Args:
        request: FastAPI request object
        synthesize_data: Synthesis request data
        
    Returns:
        Base64 encoded audio data with duration
        
    Raises:
        HTTPException: If synthesis fails
    """
    request_id = str(uuid4())
    
    try:
        # Synthesize speech
        tts_service = TextToSpeechService()
        result = tts_service.synthesize_with_result(
            text=synthesize_data.text,
            language_code=synthesize_data.language_code,
            voice_profile=synthesize_data.voice_profile
        )
        
        # Encode audio data as base64
        audio_base64 = base64.b64encode(result.audio_data).decode('utf-8')
        
        return SynthesizeResponse(
            audio_data=audio_base64,
            duration=result.duration,
            language=result.language.value,
        )
    except ValueError as e:
        # Validation error
        error = create_error_response(
            error_type="VALIDATION_ERROR",
            message=str(e),
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.model_dump(),
        )
    except Exception as e:
        # Unexpected error
        error = create_error_response(
            error_type="INTERNAL_ERROR",
            message="Failed to synthesize speech",
            details={"error": str(e)},
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )


@router.post(
    "/query",
    response_model=VoiceQueryResponse,
    summary="End-to-end voice query",
    description="Process complete voice query from audio input to audio response",
    responses={
        200: {"description": "Query successfully processed"},
        400: {"model": ErrorResponse, "description": "Invalid audio or session"},
        404: {"model": ErrorResponse, "description": "Session not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def process_voice_query(
    request: Request,
    query_data: VoiceQueryRequest,
) -> VoiceQueryResponse:
    """
    Process end-to-end voice query.
    
    Complete voice interaction flow:
    1. Validate session
    2. Transcribe audio to text (STT)
    3. Process query through orchestrator (placeholder for now)
    4. Generate speech response (TTS)
    5. Update session context
    
    Args:
        request: FastAPI request object
        query_data: Voice query request data
        
    Returns:
        Response text and audio with agent information
        
    Raises:
        HTTPException: If query processing fails
    """
    request_id = str(uuid4())
    
    try:
        # Validate session exists and is active
        session_manager = VoiceSessionManager()
        session = session_manager.get_session(query_data.session_id)
        
        if session is None:
            error = create_error_response(
                error_type="SESSION_NOT_FOUND",
                message=f"Session {query_data.session_id} not found or expired",
                request_id=request_id,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error.model_dump(),
            )
        
        # Decode base64 audio data
        try:
            audio_bytes = base64.b64decode(query_data.audio_data)
        except Exception as e:
            error = create_error_response(
                error_type="INVALID_AUDIO_DATA",
                message="Failed to decode audio data. Must be valid base64.",
                details={"error": str(e)},
                request_id=request_id,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error.model_dump(),
            )
        
        # Step 1: Transcribe audio to text
        stt_service = SpeechToTextService()
        transcription = stt_service.transcribe(
            audio_data=audio_bytes,
            language_code=session.language_code.value,
            session_id=query_data.session_id
        )
        
        # Step 2: Process query through orchestrator
        # TODO: Integrate with BedrockOrchestrator when available
        # For now, use a simple placeholder response
        response_text = _generate_placeholder_response(
            transcription.text,
            session.language_code.value
        )
        agent_used = "placeholder_agent"
        intent = "general_query"
        
        # Step 3: Generate speech response
        tts_service = TextToSpeechService()
        synthesis = tts_service.synthesize_with_result(
            text=response_text,
            language_code=session.language_code.value,
            voice_profile="female_default"
        )
        
        # Encode audio data as base64
        response_audio_base64 = base64.b64encode(synthesis.audio_data).decode('utf-8')
        
        # Step 4: Update session context
        from datetime import datetime
        from src.models.voice import ConversationTurn
        
        turn = ConversationTurn(
            turn_id=len(session.conversation_turns),
            timestamp=datetime.utcnow(),
            user_text=transcription.text,
            intent=intent,
            agent_used=agent_used,
            response_text=response_text,
        )
        
        session_manager.update_context(query_data.session_id, turn)
        
        return VoiceQueryResponse(
            response_text=response_text,
            response_audio=response_audio_base64,
            agent_used=agent_used,
            intent=intent,
            confidence=transcription.confidence,
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        # Validation error
        error = create_error_response(
            error_type="VALIDATION_ERROR",
            message=str(e),
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.model_dump(),
        )
    except Exception as e:
        # Unexpected error
        error = create_error_response(
            error_type="INTERNAL_ERROR",
            message="Failed to process voice query",
            details={"error": str(e)},
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )


@router.delete(
    "/session/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="Terminate voice session",
    description="End a voice session and cleanup resources",
    responses={
        200: {"description": "Session successfully terminated"},
        404: {"model": ErrorResponse, "description": "Session not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def terminate_voice_session(
    request: Request,
    session_id: str,
) -> Dict[str, str]:
    """
    Terminate a voice session.
    
    Ends the session and marks it as completed. The session will no longer
    accept new queries.
    
    Args:
        request: FastAPI request object
        session_id: Session identifier
        
    Returns:
        Termination confirmation
        
    Raises:
        HTTPException: If termination fails
    """
    request_id = str(uuid4())
    
    try:
        # Check if session exists
        session_manager = VoiceSessionManager()
        session = session_manager.get_session(session_id)
        
        if session is None:
            error = create_error_response(
                error_type="SESSION_NOT_FOUND",
                message=f"Session {session_id} not found",
                request_id=request_id,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error.model_dump(),
            )
        
        # Terminate session
        from src.models.voice import SessionStatus
        session_manager.terminate_session(session_id, SessionStatus.COMPLETED)
        
        return {
            "message": "Voice session terminated successfully",
            "session_id": session_id,
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Unexpected error
        error = create_error_response(
            error_type="INTERNAL_ERROR",
            message="Failed to terminate voice session",
            details={"error": str(e)},
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )


def _generate_placeholder_response(user_text: str, language_code: str) -> str:
    """
    Generate placeholder response for voice query.
    
    This is a temporary implementation until the orchestrator is integrated.
    
    Args:
        user_text: User's transcribed text
        language_code: Language code
        
    Returns:
        Response text in the appropriate language
    """
    # Simple keyword-based responses for demo
    user_text_lower = user_text.lower()
    
    if language_code == "hi":
        # Hindi responses
        if any(word in user_text for word in ["टमाटर", "प्याज", "आलू", "कीमत", "मंडी"]):
            return "आज टमाटर की कीमत 25 रुपये प्रति किलो है। दिल्ली मंडी में सबसे अच्छी कीमत मिल रही है।"
        elif any(word in user_text for word in ["लोन", "योजना", "सब्सिडी", "सरकार"]):
            return "आपके लिए 3 सरकारी योजनाएं उपलब्ध हैं। पहली है मुद्रा लोन योजना, जिसमें 10 लाख तक का लोन मिल सकता है।"
        elif any(word in user_text for word in ["वित्तीय", "रिपोर्ट", "क्रेडिट"]):
            return "मैं आपकी वित्तीय रिपोर्ट तैयार कर रहा हूं। आपका मासिक राजस्व और खर्च का विवरण जल्द ही तैयार हो जाएगा।"
        else:
            return "धन्यवाद। मैं आपकी मदद के लिए यहां हूं। कृपया अपना सवाल फिर से पूछें।"
    else:
        # English fallback
        return "Thank you for your query. I'm here to help you with market prices, government schemes, and financial guidance."
