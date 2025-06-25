"""
Configuration for CrewAI implementation.
Handles LLM models, API keys, and system settings.
"""

import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
import structlog

logger = structlog.get_logger()


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Keys
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_host: str = "https://cloud.langfuse.com"
    
    # Model Configuration
    orchestrator_model: str = "claude-3-5-sonnet-20241022"
    agent_model: str = "claude-3-5-sonnet-20241022"
    fallback_model: str = "gpt-4o"
    
    # CrewAI Settings
    crew_verbose: bool = True
    crew_max_rpm: int = 10
    crew_memory: bool = True
    crew_cache: bool = False  # Disable caching for quality focus
    crew_max_iter: int = 15  # Increased from 5 for thorough analysis
    crew_max_execution_time: Optional[int] = None  # No time limits for quality
    
    # Application Settings
    environment: str = "development"
    log_level: str = "INFO"
    
    # Database
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    
    # Vector Store
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: str = "agentpm-docs"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_llm_model(agent_type: str = "default", override_model: Optional[str] = None) -> Any:
    """Get configured LLM model for specific agent type with optional override."""
    
    # Use override model if provided (for user-selected models)
    if override_model:
        model_name = override_model
    # Otherwise use configured models
    elif agent_type == "orchestrator":
        model_name = settings.orchestrator_model
    else:
        model_name = settings.agent_model
    
    # Configure callbacks
    callbacks = []
    if settings.langfuse_public_key and settings.langfuse_secret_key:
        try:
            from langfuse.callback import CallbackHandler
            langfuse_handler = CallbackHandler(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                host=settings.langfuse_host
            )
            callbacks.append(langfuse_handler)
        except Exception as e:
            logger.warning(f"Failed to initialize Langfuse callback", error=str(e))
    
    # Create model instance
    try:
        if "claude" in model_name and settings.anthropic_api_key:
            return ChatAnthropic(
                model=model_name,
                anthropic_api_key=settings.anthropic_api_key,
                max_tokens=8192,  # Increased for comprehensive outputs
                temperature=0.7,  # Optimal for quality and creativity
                callbacks=callbacks
            )
        elif "gpt" in model_name and settings.openai_api_key:
            return ChatOpenAI(
                model=model_name,
                openai_api_key=settings.openai_api_key,
                max_tokens=8192,  # Increased for comprehensive outputs
                temperature=0.7,  # Optimal for quality and creativity
                callbacks=callbacks
            )
        else:
            # Fallback model
            if settings.openai_api_key:
                logger.warning(f"Model {model_name} not available, using fallback")
                return ChatOpenAI(
                    model=settings.fallback_model,
                    openai_api_key=settings.openai_api_key,
                    temperature=0.7,
                    callbacks=callbacks
                )
            else:
                raise ValueError("No API keys configured for LLM models")
    except Exception as e:
        logger.error(f"Failed to create LLM model", agent_type=agent_type, error=str(e))
        raise


def get_crew_config(quality_level: str = "premium") -> Dict[str, Any]:
    """Get CrewAI configuration optimized for different quality levels."""
    
    base_config = {
        "verbose": settings.crew_verbose,
        "max_rpm": settings.crew_max_rpm,
        "memory": settings.crew_memory,
        "cache": settings.crew_cache,
    }
    
    # Quality-specific configurations
    quality_configs = {
        "draft": {
            "max_iter": 5,
            "max_execution_time": 300,  # 5 minutes
            "step_callback": None
        },
        "standard": {
            "max_iter": 10,
            "max_execution_time": 600,  # 10 minutes
            "step_callback": None
        },
        "premium": {
            "max_iter": 15,
            "max_execution_time": None,  # No time limits
            "step_callback": None
        },
        "excellence": {
            "max_iter": 25,  # Extended for multi-pass refinement
            "max_execution_time": None,  # No time limits
            "step_callback": None,
            "planning_llm": True,  # Use enhanced planning
            "task_callback": None
        }
    }
    
    config = base_config.copy()
    config.update(quality_configs.get(quality_level, quality_configs["premium"]))
    
    return config


def get_sequential_crew_config(quality_level: str = "premium") -> Dict[str, Any]:
    """Get crew configuration optimized for sequential deep processing."""
    
    config = get_crew_config(quality_level)
    
    # Sequential processing optimizations
    sequential_enhancements = {
        "process_timeout": None,  # No timeout for deep processing
        "agent_timeout": None,    # No individual agent timeouts
        "enable_delegation": False,  # Prevent delegation for quality control
        "memory_optimization": True,  # Enhanced memory management
        "quality_gates": True,    # Enable quality checkpoints
        "iterative_refinement": True,  # Enable iteration support
    }
    
    config.update(sequential_enhancements)
    
    return config


def get_multipass_crew_config(
    passes: int = 3,
    iterations_per_pass: int = 2,
    quality_threshold: float = 85.0
) -> Dict[str, Any]:
    """Get crew configuration for multi-pass document generation."""
    
    return {
        "verbose": True,
        "max_rpm": 5,  # Reduced for quality focus
        "memory": True,
        "cache": False,  # Always fresh analysis
        "max_iter": passes * iterations_per_pass * 3,  # Comprehensive iteration budget
        "max_execution_time": None,  # No time constraints
        "quality_threshold": quality_threshold,
        "pass_configuration": {
            "total_passes": passes,
            "iterations_per_pass": iterations_per_pass,
            "quality_gates_enabled": True,
            "review_between_passes": True,
            "improvement_tracking": True
        },
        "optimization_settings": {
            "token_management": "quality_focused",
            "response_processing": "comprehensive",
            "error_handling": "retry_with_improvement",
            "progress_tracking": "detailed"
        }
    }


def get_database_config() -> Dict[str, Any]:
    """Get database configuration."""
    return {
        "database_url": settings.database_url or "postgresql://postgres:postgres@localhost:5432/agentpm",
        "redis_url": settings.redis_url or "redis://localhost:6379",
        "pool_size": 10,
        "max_overflow": 20
    }


def get_vector_store_config() -> Dict[str, Any]:
    """Get vector store configuration."""
    return {
        "api_key": settings.pinecone_api_key,
        "environment": settings.pinecone_environment,
        "index_name": settings.pinecone_index_name,
        "dimension": 1536,  # Default for OpenAI embeddings
        "metric": "cosine"
    }


# Logging configuration
def setup_logging():
    """Configure structured logging."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.environment == "production" 
            else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )