# Speech-to-Text Service Implementation

## Overview

This document describes the implementation of the Speech-to-Text (STT) service for the GramSaarthi AI platform. This is a **mock implementation** designed for hackathon demonstration purposes.

## Implementation Details

### Components

#### 1. Voice Models (`src/models/voice.py`)

**LanguageCode Enum**
- Defines supported Indic language codes
- MVP supports: Hindi (`hi`)
- Future support: Tamil (`ta`), Telugu (`te`)

**TranscriptionResult Model**
- `text`: Transcribed text (non-empty, stripped)
- `confidence`: Confidence score (0.0 to 1.0)
- `language`: Detected language code
- Includes validation for all fields

**SynthesisResult Model**
- `audio_data`: Audio bytes in WAV format
- `duration`: Audio duration in seconds (positive)
- `language`: Language code
- Prepared for TTS service implementation

#### 2. SpeechToTextService (`src/services/speech_to_text_service.py`)

**Purpose**
Mock STT service that simulates AI4Bharat IndicWav2Vec integration for demo purposes.

**Key Features**
- Pre-defined transcription mappings for common queries
- Hash-based audio-to-text mapping for deterministic demo behavior
- Support for Hindi language (MVP requirement)
- Comprehensive error handling and validation

**Mock Transcriptions**
The service includes 12 pre-defined transcriptions covering:
- Market intelligence queries (tomato, onion, potato prices)
- Scheme discovery queries (loans, subsidies, government help)
- Financial queries (reports, credit)
- Profile updates
- General help queries

**Methods**

1. `transcribe(audio_data, language_code, session_id) -> TranscriptionResult`
   - Main transcription method
   - Validates inputs (audio data, language, session ID)
   - Returns TranscriptionResult with text, confidence, language
   - Raises ValueError for invalid inputs

2. `get_supported_languages() -> list[str]`
   - Returns list of supported language codes
   - Currently returns `['hi']` for MVP

3. `detect_language(audio_data) -> str`
   - Auto-detects language from audio
   - Currently returns `'hi'` for MVP
   - Prepared for future multi-language support

**Hash-Based Mapping**
- Uses MD5 hash of audio data to deterministically map to transcriptions
- First character of hash determines which transcription to return
- Allows different audio samples to produce different transcriptions
- Ensures consistent behavior for demo scenarios

### Requirements Validation

✅ **Requirement 1.1**: Voice_Interface SHALL convert Indic language speech to text
- Implemented via `transcribe()` method
- Returns non-empty transcription for valid audio

✅ **Requirement 1.3**: Support at least 3 Indic languages (Hindi for MVP)
- Hindi (`hi`) fully supported
- Architecture ready for Tamil and Telugu

## Usage Examples

### Basic Transcription

```python
from src.services.speech_to_text_service import SpeechToTextService

# Initialize service
stt = SpeechToTextService()

# Transcribe audio
audio_data = b"sample_audio_bytes"
result = stt.transcribe(
    audio_data=audio_data,
    language_code="hi",
    session_id="session_123"
)

print(f"Text: {result.text}")
print(f"Confidence: {result.confidence}")
print(f"Language: {result.language}")
```

### Language Detection

```python
# Detect language from audio
detected_lang = stt.detect_language(audio_data)
print(f"Detected: {detected_lang}")  # Output: "hi"
```

### Get Supported Languages

```python
# Check supported languages
languages = stt.get_supported_languages()
print(f"Supported: {languages}")  # Output: ['hi']
```

### Error Handling

```python
# Handle errors gracefully
try:
    result = stt.transcribe(b"", "hi", "session_1")
except ValueError as e:
    print(f"Error: {e}")  # "Audio data cannot be empty"

try:
    result = stt.transcribe(b"audio", "ta", "session_2")
except ValueError as e:
    print(f"Error: {e}")  # "Language ta not yet supported in MVP"
```

## Demo Script

Run the demo script to see the STT service in action:

```bash
python examples/stt_demo.py
```

The demo showcases:
- Different query types (market, scheme, financial, general)
- Transcription results with confidence scores
- Language detection
- Supported languages

## Testing

### Manual Testing

```bash
# Test basic functionality
python -c "from src.services.speech_to_text_service import SpeechToTextService; \
stt = SpeechToTextService(); \
result = stt.transcribe(b'test', 'hi', 'session_1'); \
print(f'Text: {result.text}')"
```

### Error Cases Tested

1. ✅ Empty audio data → ValueError
2. ✅ Invalid language code → ValueError
3. ✅ Unsupported language (ta, te) → ValueError
4. ✅ Empty session ID → ValueError
5. ✅ Valid inputs → TranscriptionResult

## Production Considerations

This is a **mock implementation** for hackathon demo. For production deployment:

### Required Changes

1. **AI4Bharat Integration**
   - Replace mock mappings with actual AI4Bharat IndicWav2Vec API calls
   - Implement real-time audio streaming
   - Handle API authentication and rate limiting

2. **Audio Processing**
   - Add audio format validation (WAV, MP3, etc.)
   - Implement audio preprocessing (noise reduction, normalization)
   - Support various sample rates and bit depths

3. **Language Support**
   - Enable Tamil and Telugu language models
   - Implement robust language detection
   - Support code-switching between languages

4. **Performance Optimization**
   - Implement caching for repeated audio samples
   - Add connection pooling for API calls
   - Optimize for low-latency transcription (<3 seconds)

5. **Error Handling**
   - Implement retry logic with exponential backoff
   - Add fallback mechanisms for API failures
   - Provide user-friendly error messages in Indic languages

6. **Monitoring**
   - Track transcription accuracy metrics
   - Monitor API latency and availability
   - Log failed transcriptions for model improvement

### Architecture for Production

```
User Audio Input
    ↓
Audio Validation & Preprocessing
    ↓
AI4Bharat IndicWav2Vec API
    ↓
Post-processing & Confidence Scoring
    ↓
TranscriptionResult
```

## File Structure

```
src/
├── models/
│   └── voice.py                    # Voice data models
└── services/
    └── speech_to_text_service.py   # STT service implementation

examples/
└── stt_demo.py                     # Demo script

docs/
└── STT_SERVICE_IMPLEMENTATION.md   # This document
```

## Related Components

- **Text-to-Speech Service** (Task 3.2): Converts text responses to Indic speech
- **Voice Session Manager** (Task 3.4): Manages conversation context
- **Intent Classifier** (Task 5.1): Classifies transcribed text into intents
- **Orchestrator** (Task 5.3): Routes queries to appropriate agents

## Next Steps

1. ✅ Task 3.1: Implement mock STT service (COMPLETED)
2. ⏭️ Task 3.2: Implement mock TTS service
3. ⏭️ Task 3.4: Implement voice session management
4. ⏭️ Task 3.6: Create voice interaction API endpoints

## References

- Design Document: `.kiro/specs/gramsaarthi-ai/design.md`
- Requirements: `.kiro/specs/gramsaarthi-ai/requirements.md` (Requirements 1.1, 1.3)
- Tasks: `.kiro/specs/gramsaarthi-ai/tasks.md` (Task 3.1)
- AI4Bharat: https://ai4bharat.org/ (for production integration)
