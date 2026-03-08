"""Voice session management service."""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal

from botocore.exceptions import ClientError

from src.aws_client import aws_client
from src.config import settings
from src.models.voice import (
    ConversationTurn,
    LanguageCode,
    SessionStatus,
    VoiceSession,
)


class VoiceSessionManager:
    """
    Manages voice session state and context in DynamoDB.
    
    Implements:
    - Session creation with TTL (7 days)
    - Session retrieval and validation
    - Conversation turn tracking with context preservation
    - 5-minute inactivity timeout logic
    """
    
    def __init__(self):
        """Initialize voice session manager."""
        self.table = aws_client.get_table("VoiceSessions")
        self.session_timeout_minutes = settings.session_timeout_minutes
        self.session_ttl_days = 7
    
    def create_session(
        self,
        user_id: str,
        language_code: str
    ) -> VoiceSession:
        """
        Create a new voice session.
        
        Args:
            user_id: Enterprise/user identifier
            language_code: Language code for the session (hi, ta, te)
            
        Returns:
            Created VoiceSession object
            
        Raises:
            ValueError: If language_code is not supported
        """
        # Validate language code
        try:
            lang = LanguageCode(language_code)
        except ValueError:
            raise ValueError(
                f"Unsupported language code: {language_code}. "
                f"Supported: {', '.join([l.value for l in LanguageCode])}"
            )
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create session object
        now = datetime.utcnow()
        ttl_timestamp = int((now + timedelta(days=self.session_ttl_days)).timestamp())
        
        session = VoiceSession(
            session_id=session_id,
            enterprise_id=user_id,
            language_code=lang,
            start_time=now,
            last_activity=now,
            status=SessionStatus.ACTIVE,
            conversation_turns=[],
            context={
                "current_topic": None,
                "entities": {},
                "pending_questions": []
            },
            ttl=ttl_timestamp
        )
        
        # Store in DynamoDB
        self._store_session(session)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[VoiceSession]:
        """
        Retrieve an active voice session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            VoiceSession object if found and active, None otherwise
        """
        try:
            response = self.table.get_item(
                Key={
                    "PK": f"SESSION#{session_id}",
                    "SK": "METADATA"
                }
            )
            
            if "Item" not in response:
                return None
            
            item = response["Item"]
            
            # Convert DynamoDB item to VoiceSession
            session = self._item_to_session(item)
            
            # Check if session is still active based on timeout
            if not session.is_active(self.session_timeout_minutes):
                # Auto-terminate timed out session
                self.terminate_session(session_id, SessionStatus.TIMEOUT)
                return None
            
            return session
            
        except ClientError as e:
            print(f"Error retrieving session {session_id}: {e}")
            return None
    
    def update_context(
        self,
        session_id: str,
        turn_data: ConversationTurn
    ) -> None:
        """
        Add a conversation turn to session context.
        
        Args:
            session_id: Session identifier
            turn_data: Conversation turn to add
            
        Raises:
            ValueError: If session not found or inactive
        """
        session = self.get_session(session_id)
        
        if session is None:
            raise ValueError(f"Session {session_id} not found or inactive")
        
        # Add turn to session
        session.add_turn(turn_data)
        
        # Update context based on turn data
        if turn_data.intent:
            session.update_context(current_topic=turn_data.intent)
        
        # Store updated session
        self._store_session(session)
    
    def terminate_session(
        self,
        session_id: str,
        status: SessionStatus = SessionStatus.COMPLETED
    ) -> None:
        """
        End a session and update its status.
        
        Args:
            session_id: Session identifier
            status: Final session status (COMPLETED or TIMEOUT)
        """
        try:
            # Update session status
            self.table.update_item(
                Key={
                    "PK": f"SESSION#{session_id}",
                    "SK": "METADATA"
                },
                UpdateExpression="SET #status = :status",
                ExpressionAttributeNames={
                    "#status": "status"
                },
                ExpressionAttributeValues={
                    ":status": status.value
                }
            )
        except ClientError as e:
            print(f"Error terminating session {session_id}: {e}")
    
    def _store_session(self, session: VoiceSession) -> None:
        """
        Store session in DynamoDB.
        
        Args:
            session: VoiceSession to store
        """
        item = {
            "PK": f"SESSION#{session.session_id}",
            "SK": "METADATA",
            "session_id": session.session_id,
            "enterprise_id": session.enterprise_id,
            "language_code": session.language_code.value,
            "start_time": session.start_time.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "status": session.status.value,
            "conversation_turns": [
                {
                    "turn_id": turn.turn_id,
                    "timestamp": turn.timestamp.isoformat(),
                    "user_audio_s3_key": turn.user_audio_s3_key,
                    "user_text": turn.user_text,
                    "intent": turn.intent,
                    "agent_used": turn.agent_used,
                    "response_text": turn.response_text,
                    "response_audio_s3_key": turn.response_audio_s3_key
                }
                for turn in session.conversation_turns
            ],
            "context": {
                "current_topic": session.context.current_topic,
                "entities": session.context.entities,
                "pending_questions": session.context.pending_questions
            },
            "ttl": session.ttl
        }
        
        try:
            self.table.put_item(Item=item)
        except ClientError as e:
            print(f"Error storing session {session.session_id}: {e}")
            raise
    
    def _item_to_session(self, item: dict) -> VoiceSession:
        """
        Convert DynamoDB item to VoiceSession object.
        
        Args:
            item: DynamoDB item
            
        Returns:
            VoiceSession object
        """
        # Convert conversation turns
        turns = []
        for turn_data in item.get("conversation_turns", []):
            turn = ConversationTurn(
                turn_id=int(turn_data["turn_id"]),
                timestamp=datetime.fromisoformat(turn_data["timestamp"]),
                user_audio_s3_key=turn_data.get("user_audio_s3_key"),
                user_text=turn_data["user_text"],
                intent=turn_data.get("intent"),
                agent_used=turn_data.get("agent_used"),
                response_text=turn_data["response_text"],
                response_audio_s3_key=turn_data.get("response_audio_s3_key")
            )
            turns.append(turn)
        
        # Convert context
        context_data = item.get("context", {})
        
        # Create session
        session = VoiceSession(
            session_id=item["session_id"],
            enterprise_id=item["enterprise_id"],
            language_code=LanguageCode(item["language_code"]),
            start_time=datetime.fromisoformat(item["start_time"]),
            last_activity=datetime.fromisoformat(item["last_activity"]),
            status=SessionStatus(item["status"]),
            conversation_turns=turns,
            context={
                "current_topic": context_data.get("current_topic"),
                "entities": context_data.get("entities", {}),
                "pending_questions": context_data.get("pending_questions", [])
            },
            ttl=int(item.get("ttl", 0)) if item.get("ttl") else None
        )
        
        return session
