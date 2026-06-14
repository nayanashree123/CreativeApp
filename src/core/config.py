"""
Application configuration loaded from environment variables.
Uses pydantic for validation.
"""

import os
import logging
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from .env file or environment variables.
    """
    
    # LLM Configuration - Default to Copilot, fallback to OpenAI
    llm_provider: str = "copilot"  # "copilot" or "openai"
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.7
    
    # Copilot Configuration
    github_token: Optional[str] = None
    alternate_github_token: Optional[str] = None
    copilot_model: str = "gpt-5-mini"  # "auto", "gpt-5-mini", "claude-haiku-4.5"
    copilot_timeout: int = 200
    copilot_retries: int = 3
    copilot_temperature: float = 0.2
    
    # Application
    app_name: str = "Dream to Reality AI"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Gradio UI
    gradio_share: bool = False
    gradio_debug: bool = False
    gradio_server_name: str = "127.0.0.1"
    gradio_server_port: int = 7860
    
    # Timeouts (seconds)
    agent_timeout: int = 60
    orchestrator_timeout: int = 300
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # RAG Configuration
    knowledge_base_path: str = "knowledge"
    embedding_model: str = "text-embedding-3-small"
    max_retrieved_docs: int = 5
    
    # Async Configuration
    max_concurrent_agents: int = 6
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields


def get_settings() -> Settings:
    """Load and validate settings from environment."""
    try:
        settings = Settings()
        return settings
    except Exception as e:
        print(f"ERROR loading settings: {e}")
        raise


def setup_logging(settings: Settings) -> logging.Logger:
    """Configure logging based on settings."""
    
    # Get log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            *([logging.FileHandler(settings.log_file)] if settings.log_file else [])
        ]
    )
    
    # Suppress verbose logging from third-party libraries
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("faiss").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at level: {settings.log_level}")
    
    return logger


# Initialize settings at module level
settings = get_settings()
logger = setup_logging(settings)


if __name__ == "__main__":
    # Test settings loading
    settings = get_settings()
    print(f"App: {settings.app_name} v{settings.app_version}")
    print(f"Model: {settings.openai_model}")
    print(f"Debug: {settings.debug}")
    print(f"Gradio: {settings.gradio_server_name}:{settings.gradio_server_port}")
    print("\n✓ Settings loaded successfully")
