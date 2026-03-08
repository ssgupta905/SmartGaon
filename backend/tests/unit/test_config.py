"""Unit tests for configuration management."""

import pytest
from src.config import Settings


def test_settings_defaults():
    """Test that settings have sensible defaults."""
    settings = Settings()
    
    assert settings.aws_region == "ap-south-1"
    assert settings.dynamodb_table_prefix == "gramsaarthi"
    assert settings.s3_bucket_name == "gramsaarthi-data"
    assert settings.default_language == "hi"
    assert settings.session_timeout_minutes == 5


def test_supported_languages_list():
    """Test that supported languages are parsed correctly."""
    settings = Settings()
    
    languages = settings.supported_languages_list
    assert isinstance(languages, list)
    assert len(languages) >= 3
    assert "hi" in languages
    assert "ta" in languages
    assert "te" in languages


def test_is_production_flag():
    """Test production environment detection."""
    settings = Settings(environment="development")
    assert not settings.is_production
    
    settings = Settings(environment="production")
    assert settings.is_production
    
    settings = Settings(environment="PRODUCTION")
    assert settings.is_production


def test_demo_mode_defaults():
    """Test demo mode configuration defaults."""
    settings = Settings()
    
    assert settings.demo_mode is True
    assert settings.use_mock_voice is True
    assert settings.use_cached_data is True
