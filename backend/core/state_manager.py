"""
CrewAI State Management System.
Simplified conversation state management preserving LangGraph functionality.
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, TypedDict
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import structlog
import redis.asyncio as redis
from pathlib import Path

logger = structlog.get_logger()


class ConversationStatus(Enum):
    """Conversation status states."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


class ConversationPhase(Enum):
    """Conversation flow phases."""
    DISCOVERY = "discovery"
    DEFINITION = "definition"
    REVIEW = "review"
    COMPLETED = "completed"


@dataclass
class ConversationMetadata:
    """Metadata about conversation execution."""
    token_usage: int = 0
    agent_calls: int = 0
    document_count: int = 0
    error_count: int = 0
    start_time: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    total_duration: Optional[float] = None


@dataclass
class ConversationState:
    """
    Simplified conversation state for CrewAI.
    Preserves essential state while removing LangGraph complexity.
    """
    # Core identification
    conversation_id: str
    conversation_type: str  # idea, feature, tool, api
    
    # Flow management
    phase: ConversationPhase
    status: ConversationStatus
    
    # Agent tracking
    current_agent: Optional[str] = None
    agents_consulted: List[str] = None
    
    # Content tracking
    messages: List[Dict[str, Any]] = None
    context_data: Dict[str, Any] = None
    qa_pairs: Dict[str, Dict[str, str]] = None
    
    # Document management
    documents_generated: List[str] = None
    document_drafts: Dict[str, str] = None
    
    # Task tracking
    pending_tasks: List[str] = None
    completed_tasks: List[str] = None
    
    # Metadata
    metadata: ConversationMetadata = None
    
    # Timestamps
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.agents_consulted is None:
            self.agents_consulted = []
        if self.messages is None:
            self.messages = []
        if self.context_data is None:
            self.context_data = {}
        if self.qa_pairs is None:
            self.qa_pairs = {}
        if self.documents_generated is None:
            self.documents_generated = []
        if self.document_drafts is None:
            self.document_drafts = {}
        if self.pending_tasks is None:
            self.pending_tasks = []
        if self.completed_tasks is None:
            self.completed_tasks = []
        if self.metadata is None:
            self.metadata = ConversationMetadata()
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class ConversationStateManager:
    """
    Manages conversation state with Redis caching and database persistence.
    Simplified from LangGraph's complex state management.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis_client: Optional[redis.Redis] = None
        self.state_ttl = 24 * 60 * 60  # 24 hours
        self.checkpoint_interval = 5 * 60  # 5 minutes
        
        # In-memory cache for active conversations
        self._active_states: Dict[str, ConversationState] = {}
        self._checkpoint_tasks: Dict[str, asyncio.Task] = {}
    
    async def initialize(self):
        """Initialize Redis connection."""
        try:
            self._redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self._redis_client.ping()
            logger.info("State manager initialized with Redis connection")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Continue without Redis for testing
            self._redis_client = None
    
    async def create_conversation(
        self,
        conversation_id: str,
        conversation_type: str,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> ConversationState:
        """Create new conversation state."""
        
        logger.info(f"Creating new conversation: {conversation_id}")
        
        state = ConversationState(
            conversation_id=conversation_id,
            conversation_type=conversation_type,
            phase=ConversationPhase.DISCOVERY,
            status=ConversationStatus.ACTIVE,
            context_data=initial_context or {}
        )
        
        # Store in memory and Redis
        self._active_states[conversation_id] = state
        await self._store_state_in_redis(state)
        
        # Start periodic checkpointing
        await self._start_checkpoint_task(conversation_id)
        
        logger.info(f"Conversation {conversation_id} created and cached")
        return state
    
    async def get_conversation_state(self, conversation_id: str) -> Optional[ConversationState]:
        """Get conversation state from cache or Redis."""
        
        # Check in-memory cache first
        if conversation_id in self._active_states:
            return self._active_states[conversation_id]
        
        # Try to load from Redis
        state = await self._load_state_from_redis(conversation_id)
        if state:
            self._active_states[conversation_id] = state
            logger.info(f"Loaded conversation {conversation_id} from Redis")
            return state
        
        logger.warning(f"Conversation {conversation_id} not found")
        return None
    
    async def update_conversation_state(
        self,
        conversation_id: str,
        updates: Dict[str, Any]
    ) -> Optional[ConversationState]:
        """Update conversation state with partial updates."""
        
        state = await self.get_conversation_state(conversation_id)
        if not state:
            logger.error(f"Cannot update non-existent conversation: {conversation_id}")
            return None
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(state, key):
                setattr(state, key, value)
        
        # Update timestamp
        state.updated_at = datetime.utcnow()
        
        # Store updated state
        self._active_states[conversation_id] = state
        await self._store_state_in_redis(state)
        
        logger.debug(f"Updated conversation {conversation_id} state")
        return state
    
    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add message to conversation state."""
        
        state = await self.get_conversation_state(conversation_id)
        if not state:
            return
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "metadata": metadata or {}
        }
        
        state.messages.append(message)
        state.updated_at = datetime.utcnow()
        
        # Update agent tracking
        if agent_id and agent_id not in state.agents_consulted:
            state.agents_consulted.append(agent_id)
        
        await self._store_state_in_redis(state)
        logger.debug(f"Added message to conversation {conversation_id}")
    
    async def update_phase(
        self,
        conversation_id: str,
        new_phase: ConversationPhase
    ):
        """Update conversation phase."""
        
        await self.update_conversation_state(conversation_id, {
            "phase": new_phase,
            "updated_at": datetime.utcnow()
        })
        
        logger.info(f"Conversation {conversation_id} transitioned to phase: {new_phase.value}")
    
    async def add_document(
        self,
        conversation_id: str,
        document_type: str,
        document_content: Optional[str] = None,
        is_draft: bool = False
    ):
        """Add generated document to conversation state."""
        
        state = await self.get_conversation_state(conversation_id)
        if not state:
            return
        
        if is_draft and document_content:
            state.document_drafts[document_type] = document_content
        elif document_type not in state.documents_generated:
            state.documents_generated.append(document_type)
            state.metadata.document_count += 1
        
        state.updated_at = datetime.utcnow()
        await self._store_state_in_redis(state)
        
        logger.info(f"Added document {document_type} to conversation {conversation_id}")
    
    async def create_checkpoint(self, conversation_id: str) -> Dict[str, Any]:
        """Create manual checkpoint of conversation state."""
        
        state = await self.get_conversation_state(conversation_id)
        if not state:
            return {"error": "Conversation not found"}
        
        checkpoint_data = {
            "conversation_id": conversation_id,
            "checkpoint_time": datetime.utcnow().isoformat(),
            "state": asdict(state)
        }
        
        # Store checkpoint in Redis with extended TTL
        checkpoint_key = f"checkpoint:{conversation_id}:{int(datetime.utcnow().timestamp())}"
        if self._redis_client:
            await self._redis_client.setex(
                checkpoint_key,
                7 * 24 * 60 * 60,  # 7 days
                json.dumps(checkpoint_data, default=str)
            )
        
        # Also save to filesystem for recovery
        await self._save_checkpoint_to_file(checkpoint_data)
        
        logger.info(f"Created checkpoint for conversation {conversation_id}")
        return checkpoint_data
    
    async def restore_from_checkpoint(
        self,
        conversation_id: str,
        checkpoint_time: Optional[str] = None
    ) -> Optional[ConversationState]:
        """Restore conversation state from checkpoint."""
        
        try:
            # Find latest checkpoint if time not specified
            if not checkpoint_time:
                checkpoint_time = await self._find_latest_checkpoint(conversation_id)
            
            if not checkpoint_time:
                logger.error(f"No checkpoint found for conversation {conversation_id}")
                return None
            
            # Load checkpoint data
            checkpoint_key = f"checkpoint:{conversation_id}:{checkpoint_time}"
            if self._redis_client:
                checkpoint_data = await self._redis_client.get(checkpoint_key)
                if checkpoint_data:
                    data = json.loads(checkpoint_data)
                    state_dict = data["state"]
                    
                    # Reconstruct state object
                    state = self._dict_to_state(state_dict)
                    
                    # Restore to active cache
                    self._active_states[conversation_id] = state
                    await self._store_state_in_redis(state)
                    
                    logger.info(f"Restored conversation {conversation_id} from checkpoint")
                    return state
            
            # Try filesystem backup
            return await self._restore_from_file_checkpoint(conversation_id)
            
        except Exception as e:
            logger.error(f"Failed to restore checkpoint for {conversation_id}: {e}")
            return None
    
    async def complete_conversation(self, conversation_id: str):
        """Mark conversation as completed and cleanup."""
        
        await self.update_conversation_state(conversation_id, {
            "status": ConversationStatus.COMPLETED,
            "phase": ConversationPhase.COMPLETED,
            "updated_at": datetime.utcnow()
        })
        
        # Stop checkpoint task
        if conversation_id in self._checkpoint_tasks:
            self._checkpoint_tasks[conversation_id].cancel()
            del self._checkpoint_tasks[conversation_id]
        
        # Create final checkpoint
        await self.create_checkpoint(conversation_id)
        
        logger.info(f"Conversation {conversation_id} marked as completed")
    
    async def cleanup_expired_conversations(self):
        """Clean up expired conversations from memory."""
        
        current_time = datetime.utcnow()
        expired_conversations = []
        
        for conversation_id, state in self._active_states.items():
            if state.updated_at < current_time - timedelta(hours=24):
                expired_conversations.append(conversation_id)
        
        for conversation_id in expired_conversations:
            await self._cleanup_conversation(conversation_id)
        
        if expired_conversations:
            logger.info(f"Cleaned up {len(expired_conversations)} expired conversations")
    
    async def _store_state_in_redis(self, state: ConversationState):
        """Store conversation state in Redis."""
        
        if not self._redis_client:
            return
        
        try:
            state_key = f"conversation:{state.conversation_id}"
            state_data = json.dumps(asdict(state), default=str)
            
            await self._redis_client.setex(state_key, self.state_ttl, state_data)
            
        except Exception as e:
            logger.error(f"Failed to store state in Redis: {e}")
    
    async def _load_state_from_redis(self, conversation_id: str) -> Optional[ConversationState]:
        """Load conversation state from Redis."""
        
        if not self._redis_client:
            return None
        
        try:
            state_key = f"conversation:{conversation_id}"
            state_data = await self._redis_client.get(state_key)
            
            if state_data:
                state_dict = json.loads(state_data)
                return self._dict_to_state(state_dict)
            
        except Exception as e:
            logger.error(f"Failed to load state from Redis: {e}")
        
        return None
    
    def _dict_to_state(self, state_dict: Dict[str, Any]) -> ConversationState:
        """Convert dictionary to ConversationState object."""
        
        # Handle enum conversions
        if "phase" in state_dict:
            state_dict["phase"] = ConversationPhase(state_dict["phase"])
        if "status" in state_dict:
            state_dict["status"] = ConversationStatus(state_dict["status"])
        
        # Handle datetime conversions
        for time_field in ["created_at", "updated_at"]:
            if time_field in state_dict and isinstance(state_dict[time_field], str):
                state_dict[time_field] = datetime.fromisoformat(state_dict[time_field])
        
        # Handle metadata
        if "metadata" in state_dict and isinstance(state_dict["metadata"], dict):
            metadata_dict = state_dict["metadata"]
            for time_field in ["start_time", "last_activity"]:
                if time_field in metadata_dict and isinstance(metadata_dict[time_field], str):
                    metadata_dict[time_field] = datetime.fromisoformat(metadata_dict[time_field])
            state_dict["metadata"] = ConversationMetadata(**metadata_dict)
        
        return ConversationState(**state_dict)
    
    async def _start_checkpoint_task(self, conversation_id: str):
        """Start periodic checkpointing for conversation."""
        
        async def checkpoint_loop():
            try:
                while True:
                    await asyncio.sleep(self.checkpoint_interval)
                    await self.create_checkpoint(conversation_id)
            except asyncio.CancelledError:
                logger.debug(f"Checkpoint task cancelled for conversation {conversation_id}")
            except Exception as e:
                logger.error(f"Checkpoint task error for {conversation_id}: {e}")
        
        task = asyncio.create_task(checkpoint_loop())
        self._checkpoint_tasks[conversation_id] = task
    
    async def _save_checkpoint_to_file(self, checkpoint_data: Dict[str, Any]):
        """Save checkpoint to filesystem as backup."""
        
        try:
            checkpoint_dir = Path("checkpoints")
            checkpoint_dir.mkdir(exist_ok=True)
            
            checkpoint_file = checkpoint_dir / f"{checkpoint_data['conversation_id']}_latest.json"
            
            with open(checkpoint_file, "w") as f:
                json.dump(checkpoint_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save checkpoint to file: {e}")
    
    async def _restore_from_file_checkpoint(self, conversation_id: str) -> Optional[ConversationState]:
        """Restore from filesystem checkpoint backup."""
        
        try:
            checkpoint_file = Path("checkpoints") / f"{conversation_id}_latest.json"
            
            if checkpoint_file.exists():
                with open(checkpoint_file, "r") as f:
                    data = json.load(f)
                
                state_dict = data["state"]
                state = self._dict_to_state(state_dict)
                
                self._active_states[conversation_id] = state
                await self._store_state_in_redis(state)
                
                logger.info(f"Restored conversation {conversation_id} from file checkpoint")
                return state
                
        except Exception as e:
            logger.error(f"Failed to restore from file checkpoint: {e}")
        
        return None
    
    async def _find_latest_checkpoint(self, conversation_id: str) -> Optional[str]:
        """Find latest checkpoint timestamp for conversation."""
        
        if not self._redis_client:
            return None
        
        try:
            pattern = f"checkpoint:{conversation_id}:*"
            keys = await self._redis_client.keys(pattern)
            
            if keys:
                # Extract timestamps and find latest
                timestamps = [key.split(":")[-1] for key in keys]
                return max(timestamps)
                
        except Exception as e:
            logger.error(f"Failed to find latest checkpoint: {e}")
        
        return None
    
    async def _cleanup_conversation(self, conversation_id: str):
        """Clean up conversation from memory and cancel tasks."""
        
        # Remove from active cache
        if conversation_id in self._active_states:
            del self._active_states[conversation_id]
        
        # Cancel checkpoint task
        if conversation_id in self._checkpoint_tasks:
            self._checkpoint_tasks[conversation_id].cancel()
            del self._checkpoint_tasks[conversation_id]
        
        logger.debug(f"Cleaned up conversation {conversation_id}")


# Global state manager instance
state_manager = ConversationStateManager()