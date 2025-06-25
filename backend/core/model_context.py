"""
Model Context Manager for Dynamic Model Selection.
Manages user-selected models throughout conversation flow.
"""

from typing import Optional, Dict, Any
import contextvars
import structlog

logger = structlog.get_logger()

# Context variable for storing current model selection
_current_model: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'current_model',
    default=None
)

# Store model selections per conversation
_conversation_models: Dict[str, str] = {}


class ModelContext:
    """Manages model selection context for conversations."""
    
    @staticmethod
    def set_model_for_conversation(conversation_id: str, model: str):
        """Set the model for a specific conversation."""
        _conversation_models[conversation_id] = model
        logger.info(f"Set model for conversation", 
                   conversation_id=conversation_id,
                   model=model)
    
    @staticmethod
    def get_model_for_conversation(conversation_id: str) -> Optional[str]:
        """Get the model for a specific conversation."""
        return _conversation_models.get(conversation_id)
    
    @staticmethod
    def set_current_model(model: str):
        """Set the model for the current context."""
        _current_model.set(model)
    
    @staticmethod
    def get_current_model() -> Optional[str]:
        """Get the model for the current context."""
        return _current_model.get()
    
    @staticmethod
    def clear_conversation_model(conversation_id: str):
        """Clear the model selection for a conversation."""
        if conversation_id in _conversation_models:
            del _conversation_models[conversation_id]
            logger.info(f"Cleared model for conversation", conversation_id=conversation_id)


# Global instance
model_context = ModelContext()