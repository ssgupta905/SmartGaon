"""Text-to-speech service for Indic languages.

This is a mock implementation for hackathon demo purposes.
In production, this would integrate with AI4Bharat IndicTTS models.
"""

import hashlib
import struct
from typing import Dict, List

from src.models.voice import LanguageCode, SynthesisResult


class TextToSpeechService:
    """Mock text-to-speech service for hackathon demonstration.
    
    This service simulates speech synthesis using pre-generated audio files.
    For the MVP, it supports Hindi language code ('hi').
    
    In production, this would integrate with AI4Bharat IndicTTS models
    for real-time Indic language speech synthesis.
    """
    
    # Mock text to audio mappings for demo
    # In a real implementation, these would be actual audio files
    MOCK_AUDIO_RESPONSES: Dict[str, Dict[str, any]] = {
        # Market intelligence responses
        "market_price_response_hi": {
            "text_pattern": "टमाटर|प्याज|आलू|कीमत|मंडी",
            "duration": 8.5,
            "language": LanguageCode.HINDI
        },
        "market_recommendation_hi": {
            "text_pattern": "सिफारिश|बाजार|बेचना",
            "duration": 12.3,
            "language": LanguageCode.HINDI
        },
        
        # Scheme responses
        "scheme_list_hi": {
            "text_pattern": "योजना|लोन|सब्सिडी",
            "duration": 15.7,
            "language": LanguageCode.HINDI
        },
        "scheme_details_hi": {
            "text_pattern": "आवेदन|दस्तावेज|पात्रता",
            "duration": 20.4,
            "language": LanguageCode.HINDI
        },
        
        # Financial responses
        "financial_summary_hi": {
            "text_pattern": "वित्तीय|रिपोर्ट|लाभ|राजस्व",
            "duration": 18.2,
            "language": LanguageCode.HINDI
        },
        "credit_report_hi": {
            "text_pattern": "क्रेडिट|ऋण|साख",
            "duration": 14.6,
            "language": LanguageCode.HINDI
        },
        
        # General responses
        "greeting_hi": {
            "text_pattern": "नमस्ते|स्वागत",
            "duration": 3.5,
            "language": LanguageCode.HINDI
        },
        "confirmation_hi": {
            "text_pattern": "धन्यवाद|ठीक है|हो गया",
            "duration": 2.8,
            "language": LanguageCode.HINDI
        },
        "help_hi": {
            "text_pattern": "मदद|सहायता|कैसे",
            "duration": 10.5,
            "language": LanguageCode.HINDI
        },
        
        # Default fallback
        "default_hi": {
            "text_pattern": "",
            "duration": 5.0,
            "language": LanguageCode.HINDI
        }
    }
    
    # Voice profiles available for each language
    VOICE_PROFILES: Dict[str, List[str]] = {
        "hi": ["female_default", "male_default", "female_formal", "male_formal"],
        "ta": ["female_default", "male_default"],
        "te": ["female_default", "male_default"]
    }
    
    def __init__(self):
        """Initialize the text-to-speech service."""
        self._supported_languages = [LanguageCode.HINDI]
    
    def synthesize(
        self,
        text: str,
        language_code: str,
        voice_profile: str = "female_default"
    ) -> bytes:
        """Generate speech audio from text.
        
        This is a mock implementation that generates synthetic WAV audio
        for demo purposes. The audio is deterministic based on text content.
        
        Args:
            text: Text to convert to speech
            language_code: Language code ('hi', 'ta', 'te')
            voice_profile: Voice profile to use (default: 'female_default')
        
        Returns:
            Audio bytes in WAV format
        
        Raises:
            ValueError: If language is not supported or text is invalid
        """
        # Validate inputs
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
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
        
        # Validate voice profile
        if voice_profile not in self.VOICE_PROFILES.get(language_code, []):
            raise ValueError(
                f"Voice profile '{voice_profile}' not available for language {language_code}. "
                f"Available profiles: {self.VOICE_PROFILES.get(language_code, [])}"
            )
        
        # Generate mock audio based on text
        # In a real implementation, this would call AI4Bharat API
        audio_data = self._generate_mock_audio(text, lang, voice_profile)
        
        return audio_data
    
    def synthesize_with_result(
        self,
        text: str,
        language_code: str,
        voice_profile: str = "female_default"
    ) -> SynthesisResult:
        """Generate speech audio and return detailed result.
        
        Args:
            text: Text to convert to speech
            language_code: Language code ('hi', 'ta', 'te')
            voice_profile: Voice profile to use
        
        Returns:
            SynthesisResult with audio data, duration, and language
        
        Raises:
            ValueError: If language is not supported or text is invalid
        """
        # Validate language code
        try:
            lang = LanguageCode(language_code)
        except ValueError:
            raise ValueError(
                f"Unsupported language code: {language_code}. "
                f"Supported languages: {[l.value for l in self._supported_languages]}"
            )
        
        # Generate audio
        audio_data = self.synthesize(text, language_code, voice_profile)
        
        # Estimate duration based on text length and audio response type
        duration = self._estimate_duration(text, lang)
        
        return SynthesisResult(
            audio_data=audio_data,
            duration=duration,
            language=lang
        )
    
    def _generate_mock_audio(
        self,
        text: str,
        language: LanguageCode,
        voice_profile: str
    ) -> bytes:
        """Generate mock WAV audio data.
        
        This creates a simple WAV file with synthetic audio data.
        In production, this would call AI4Bharat TTS API.
        
        Args:
            text: Text to synthesize
            language: Target language
            voice_profile: Voice profile to use
        
        Returns:
            WAV audio bytes
        """
        # Determine audio response type based on text content
        response_type = self._classify_response_type(text)
        response_data = self.MOCK_AUDIO_RESPONSES.get(
            response_type,
            self.MOCK_AUDIO_RESPONSES["default_hi"]
        )
        
        # Calculate audio duration based on text length
        # Rough estimate: 150 words per minute for Hindi
        word_count = len(text.split())
        estimated_duration = max(response_data["duration"], word_count / 2.5)
        
        # Generate deterministic audio based on text hash
        text_hash = hashlib.md5(text.encode('utf-8')).digest()
        
        # WAV file parameters
        sample_rate = 16000  # 16 kHz
        num_channels = 1  # Mono
        bits_per_sample = 16
        
        # Calculate number of samples
        num_samples = int(sample_rate * estimated_duration)
        
        # Generate simple audio data (sine wave based on text hash)
        # In production, this would be actual speech audio
        audio_samples = []
        frequency = 200 + (text_hash[0] % 100)  # Base frequency 200-300 Hz
        
        for i in range(num_samples):
            # Create a simple varying tone
            t = i / sample_rate
            # Mix multiple frequencies for more natural sound
            sample = 0
            for j in range(3):
                freq = frequency * (j + 1) + (text_hash[j] % 50)
                amplitude = 8000 / (j + 1)  # Decreasing amplitude for harmonics
                sample += amplitude * (1 + (i % 1000) / 1000) * \
                         ((i % (sample_rate // 10)) / (sample_rate // 10))
            
            # Add some variation based on text content
            if i % (sample_rate // 4) < sample_rate // 8:
                sample *= 0.7  # Simulate pauses
            
            audio_samples.append(int(sample) % 32767)
        
        # Create WAV file header
        wav_data = self._create_wav_header(
            num_samples,
            sample_rate,
            num_channels,
            bits_per_sample
        )
        
        # Add audio samples
        for sample in audio_samples:
            wav_data += struct.pack('<h', sample)
        
        return wav_data
    
    def _create_wav_header(
        self,
        num_samples: int,
        sample_rate: int,
        num_channels: int,
        bits_per_sample: int
    ) -> bytes:
        """Create WAV file header.
        
        Args:
            num_samples: Number of audio samples
            sample_rate: Sample rate in Hz
            num_channels: Number of audio channels
            bits_per_sample: Bits per sample
        
        Returns:
            WAV header bytes
        """
        byte_rate = sample_rate * num_channels * bits_per_sample // 8
        block_align = num_channels * bits_per_sample // 8
        data_size = num_samples * num_channels * bits_per_sample // 8
        
        # RIFF header
        header = b'RIFF'
        header += struct.pack('<I', 36 + data_size)  # File size - 8
        header += b'WAVE'
        
        # fmt subchunk
        header += b'fmt '
        header += struct.pack('<I', 16)  # Subchunk size
        header += struct.pack('<H', 1)  # Audio format (1 = PCM)
        header += struct.pack('<H', num_channels)
        header += struct.pack('<I', sample_rate)
        header += struct.pack('<I', byte_rate)
        header += struct.pack('<H', block_align)
        header += struct.pack('<H', bits_per_sample)
        
        # data subchunk
        header += b'data'
        header += struct.pack('<I', data_size)
        
        return header
    
    def _classify_response_type(self, text: str) -> str:
        """Classify text to determine appropriate audio response type.
        
        Args:
            text: Text to classify
        
        Returns:
            Response type key
        """
        text_lower = text.lower()
        
        # Check each response type pattern
        for response_type, data in self.MOCK_AUDIO_RESPONSES.items():
            pattern = data.get("text_pattern", "")
            if pattern:
                keywords = pattern.split("|")
                if any(keyword in text for keyword in keywords):
                    return response_type
        
        return "default_hi"
    
    def _estimate_duration(self, text: str, language: LanguageCode) -> float:
        """Estimate audio duration based on text length.
        
        Args:
            text: Text to synthesize
            language: Target language
        
        Returns:
            Estimated duration in seconds
        """
        # Rough estimate: 150 words per minute for Hindi
        # Adjust for other languages as needed
        word_count = len(text.split())
        words_per_second = 2.5  # 150 words per minute
        
        # Add base duration for very short texts
        base_duration = 1.0
        estimated_duration = base_duration + (word_count / words_per_second)
        
        return round(estimated_duration, 1)
    
    def get_supported_voices(self, language_code: str) -> List[str]:
        """Get available voice profiles for language.
        
        Args:
            language_code: Language code
        
        Returns:
            List of available voice profile names
        
        Raises:
            ValueError: If language is not supported
        """
        if language_code not in self.VOICE_PROFILES:
            raise ValueError(
                f"Language {language_code} not supported. "
                f"Supported languages: {list(self.VOICE_PROFILES.keys())}"
            )
        
        return self.VOICE_PROFILES[language_code]
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes.
        
        Returns:
            List of supported language codes
        """
        return [lang.value for lang in self._supported_languages]
