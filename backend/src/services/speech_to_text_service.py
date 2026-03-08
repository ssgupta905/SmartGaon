"""Speech-to-text service for Indic languages.

This is a mock implementation for hackathon demo purposes.
In production, this would integrate with AI4Bharat IndicWav2Vec models.
"""

import hashlib
from typing import Dict

from src.models.voice import LanguageCode, TranscriptionResult


class SpeechToTextService:
    """Mock speech-to-text service for hackathon demonstration.
    
    This service simulates transcription using pre-recorded audio mappings.
    For the MVP, it supports Hindi language code ('hi').
    
    In production, this would integrate with AI4Bharat IndicWav2Vec models
    for real-time Indic language speech recognition.
    """
    
    # Mock audio hash to transcription mappings for demo
    # In a real implementation, these would be actual audio files
    MOCK_TRANSCRIPTIONS: Dict[str, Dict[str, any]] = {
        # Market intelligence queries
        "market_tomato_hi": {
            "text": "मुझे टमाटर की कीमत बताओ",
            "confidence": 0.95,
            "language": LanguageCode.HINDI
        },
        "market_onion_hi": {
            "text": "प्याज की मंडी भाव क्या है",
            "confidence": 0.92,
            "language": LanguageCode.HINDI
        },
        "market_potato_hi": {
            "text": "आलू की कीमत कितनी है",
            "confidence": 0.94,
            "language": LanguageCode.HINDI
        },
        
        # Scheme discovery queries
        "scheme_loan_hi": {
            "text": "मुझे लोन चाहिए",
            "confidence": 0.96,
            "language": LanguageCode.HINDI
        },
        "scheme_subsidy_hi": {
            "text": "सरकारी योजनाएं बताओ",
            "confidence": 0.93,
            "language": LanguageCode.HINDI
        },
        "scheme_help_hi": {
            "text": "सरकार से मदद कैसे मिलेगी",
            "confidence": 0.91,
            "language": LanguageCode.HINDI
        },
        
        # Financial queries
        "financial_summary_hi": {
            "text": "मेरी वित्तीय रिपोर्ट बनाओ",
            "confidence": 0.94,
            "language": LanguageCode.HINDI
        },
        "financial_credit_hi": {
            "text": "क्रेडिट रिपोर्ट चाहिए",
            "confidence": 0.93,
            "language": LanguageCode.HINDI
        },
        
        # Profile updates
        "profile_update_hi": {
            "text": "मेरी जानकारी बदलनी है",
            "confidence": 0.92,
            "language": LanguageCode.HINDI
        },
        
        # General queries
        "general_help_hi": {
            "text": "मुझे मदद चाहिए",
            "confidence": 0.95,
            "language": LanguageCode.HINDI
        },
        "general_status_hi": {
            "text": "मेरा स्टेटस क्या है",
            "confidence": 0.94,
            "language": LanguageCode.HINDI
        },
        
        # Default fallback
        "default_hi": {
            "text": "नमस्ते, मैं आपकी कैसे मदद कर सकता हूं",
            "confidence": 0.85,
            "language": LanguageCode.HINDI
        }
    }
    
    def __init__(self):
        """Initialize the speech-to-text service."""
        self._supported_languages = [LanguageCode.HINDI]
    
    def transcribe(
        self,
        audio_data: bytes,
        language_code: str,
        session_id: str
    ) -> TranscriptionResult:
        """Transcribe Indic language audio to text.
        
        This is a mock implementation that uses audio data hash to look up
        pre-defined transcriptions for demo purposes.
        
        Args:
            audio_data: Audio data in bytes (WAV format expected)
            language_code: Language code ('hi', 'ta', 'te')
            session_id: Session identifier for tracking
        
        Returns:
            TranscriptionResult with text, confidence, and language
        
        Raises:
            ValueError: If language is not supported or audio data is invalid
        """
        # Validate inputs
        if not audio_data:
            raise ValueError("Audio data cannot be empty")
        
        if not session_id:
            raise ValueError("Session ID is required")
        
        # Validate language code
        try:
            lang = LanguageCode(language_code)
        except ValueError:
            raise ValueError(
                f"Unsupported language code: {language_code}. "
                f"Supported languages: {[l.value for l in self._supported_languages]}"
            )
        
        # For MVP, only Hindi is supported
        if lang not in self._supported_languages:
            raise ValueError(
                f"Language {language_code} not yet supported in MVP. "
                f"Supported languages: {[l.value for l in self._supported_languages]}"
            )
        
        # Generate hash of audio data to look up mock transcription
        audio_hash = hashlib.md5(audio_data).hexdigest()[:16]
        
        # Try to find matching mock transcription
        # In a real implementation, this would call AI4Bharat API
        transcription_data = self._get_mock_transcription(audio_hash, lang)
        
        # Create and return transcription result
        return TranscriptionResult(
            text=transcription_data["text"],
            confidence=transcription_data["confidence"],
            language=transcription_data["language"]
        )
    
    def _get_mock_transcription(
        self,
        audio_hash: str,
        language: LanguageCode
    ) -> Dict[str, any]:
        """Get mock transcription based on audio hash.
        
        This simulates the AI4Bharat transcription service.
        In production, this would make an actual API call.
        
        Args:
            audio_hash: Hash of audio data
            language: Target language
        
        Returns:
            Dictionary with text, confidence, and language
        """
        # Try to find exact match by hash
        # In demo, we'll use a simple mapping based on hash prefix
        hash_prefix = audio_hash[:4]
        
        # Map hash prefixes to demo transcriptions
        # This allows different audio samples to map to different queries
        hash_to_key = {
            "0": "market_tomato_hi",
            "1": "market_onion_hi",
            "2": "market_potato_hi",
            "3": "scheme_loan_hi",
            "4": "scheme_subsidy_hi",
            "5": "scheme_help_hi",
            "6": "financial_summary_hi",
            "7": "financial_credit_hi",
            "8": "profile_update_hi",
            "9": "general_help_hi",
            "a": "general_status_hi",
            "b": "market_tomato_hi",
            "c": "scheme_loan_hi",
            "d": "financial_summary_hi",
            "e": "general_help_hi",
            "f": "default_hi",
        }
        
        # Get first character of hash prefix
        first_char = hash_prefix[0].lower()
        transcription_key = hash_to_key.get(first_char, "default_hi")
        
        # Return the mock transcription
        return self.MOCK_TRANSCRIPTIONS[transcription_key]
    
    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes.
        
        Returns:
            List of supported language codes
        """
        return [lang.value for lang in self._supported_languages]
    
    def detect_language(self, audio_data: bytes) -> str:
        """Auto-detect Indic language from audio.
        
        This is a mock implementation that returns Hindi for MVP.
        In production, this would use AI4Bharat language detection.
        
        Args:
            audio_data: Audio data in bytes
        
        Returns:
            Detected language code
        
        Raises:
            ValueError: If audio data is invalid
        """
        if not audio_data:
            raise ValueError("Audio data cannot be empty")
        
        # For MVP, always return Hindi
        # In production, this would analyze audio to detect language
        return LanguageCode.HINDI.value
