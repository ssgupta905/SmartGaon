"""Configuration management for GramSaarthi AI platform."""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # AWS Configuration
    aws_region: str = "ap-south-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    
    # AWS Service Configuration
    dynamodb_table_prefix: str = "gramsaarthi"
    s3_bucket_name: str = "gramsaarthi-data"
    
    # Bedrock Configuration
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    bedrock_agent_id: str = ""
    bedrock_agent_alias_id: str = ""
    
    # API Configuration
    api_base_url: str = "http://localhost:8000"
    api_gateway_stage: str = "dev"
    
    # Voice Processing Configuration
    supported_languages: str = "hi,ta,te"
    default_language: str = "hi"
    session_timeout_minutes: int = 5
    
    # External API Configuration
    agmarknet_api_url: str = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    agmarknet_api_key: str = ""
    
    # Application Settings
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = True
    
    # Demo Mode
    demo_mode: bool = True
    use_mock_voice: bool = True
    use_cached_data: bool = True
    
    @property
    def supported_languages_list(self) -> List[str]:
        """Get supported languages as a list."""
        return [lang.strip() for lang in self.supported_languages.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"


# Global settings instance
settings = Settings()
