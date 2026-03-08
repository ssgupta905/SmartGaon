"""Demo script for Speech-to-Text service.

This script demonstrates the mock STT service functionality for the hackathon demo.
"""

from src.services.speech_to_text_service import SpeechToTextService
from src.models.voice import LanguageCode


def main():
    """Run STT service demo."""
    print("=" * 60)
    print("GramSaarthi AI - Speech-to-Text Service Demo")
    print("=" * 60)
    print()
    
    # Initialize service
    stt_service = SpeechToTextService()
    
    # Display supported languages
    print(f"Supported Languages: {stt_service.get_supported_languages()}")
    print()
    
    # Demo different types of queries
    demo_queries = [
        ("Market Intelligence Query", b"market_query_tomato_price"),
        ("Scheme Discovery Query", b"scheme_query_loan_help"),
        ("Financial Summary Query", b"financial_query_report"),
        ("General Help Query", b"general_query_help"),
        ("Profile Update Query", b"profile_query_update"),
    ]
    
    print("Demo Transcriptions:")
    print("-" * 60)
    
    for i, (query_type, audio_data) in enumerate(demo_queries, 1):
        session_id = f"demo_session_{i}"
        
        # Transcribe audio
        result = stt_service.transcribe(
            audio_data=audio_data,
            language_code="hi",
            session_id=session_id
        )
        
        print(f"\n{i}. {query_type}")
        print(f"   Session ID: {session_id}")
        print(f"   Transcribed Text: {result.text}")
        print(f"   Confidence: {result.confidence:.2%}")
        print(f"   Language: {result.language.value}")
    
    print()
    print("-" * 60)
    
    # Demo language detection
    print("\nLanguage Detection Demo:")
    test_audio = b"test_audio_sample"
    detected_lang = stt_service.detect_language(test_audio)
    print(f"Detected Language: {detected_lang}")
    
    print()
    print("=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
