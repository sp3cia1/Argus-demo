"""
Application settings using Pydantic for type safety and validation.
"""

import os
from typing import Optional, List
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()

class ArgusSettings(BaseSettings):
    """Main application settings."""
    
    # OpenRouter Configuration
    openrouter_api_key: Optional[str] = Field(None, env="OPENROUTER_API_KEY")
    guard_llm_model: str = Field(
        "deepseek/deepseek-r1-distill-qwen-32b:free", 
        env="GUARD_LLM_MODEL"
    )
    
    # Site Configuration
    site_url: str = Field("http://localhost:8000", env="YOUR_SITE_URL")
    site_name: str = Field("Argus AI Gateway MVP", env="YOUR_SITE_NAME")
    
    # Timeouts and Performance
    guard_llm_timeout: float = Field(20.0, env="GUARD_LLM_TIMEOUT")
    max_tokens: int = Field(6000, env="MAX_TOKENS")
    temperature: float = Field(0.1, env="TEMPERATURE")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field(
        "%(asctime)s - %(levelname)s - [%(name)s.%(funcName)s] - %(message)s",
        env="LOG_FORMAT"
    )
    
    # Performance Simulation
    simulated_unprotected_delay: float = Field(0.25, env="SIMULATED_UNPROTECTED_DELAY")
    streaming_delay_no_argus: float = Field(0.025, env="STREAMING_DELAY_NO_ARGUS")
    streaming_delay_with_argus: float = Field(0.010, env="STREAMING_DELAY_WITH_ARGUS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = ArgusSettings()
