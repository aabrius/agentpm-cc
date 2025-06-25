"""
Langfuse Observability Configuration for CrewAI Implementation.
Preserves all LangGraph functionality while adapting to CrewAI patterns.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import structlog
from contextlib import contextmanager

try:
    from langfuse import Langfuse
    from langfuse.decorators import observe, langfuse_context
    from langfuse.openai import openai as langfuse_openai
    from langfuse.anthropic import anthropic as langfuse_anthropic
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    # Mock classes for graceful degradation
    class MockLangfuse:
        def __init__(self, *args, **kwargs): pass
        def trace(self, *args, **kwargs): return MockTrace()
        def span(self, *args, **kwargs): return MockSpan()
        def generation(self, *args, **kwargs): return MockGeneration()
        def flush(self): pass
        def auth_check(self): return True
    
    class MockTrace:
        def __init__(self, *args, **kwargs): pass
        def span(self, *args, **kwargs): return MockSpan()
        def generation(self, *args, **kwargs): return MockGeneration()
        def update(self, *args, **kwargs): pass
        def end(self, *args, **kwargs): pass
    
    class MockSpan:
        def __init__(self, *args, **kwargs): pass
        def generation(self, *args, **kwargs): return MockGeneration()
        def update(self, *args, **kwargs): pass
        def end(self, *args, **kwargs): pass
    
    class MockGeneration:
        def __init__(self, *args, **kwargs): pass
        def update(self, *args, **kwargs): pass
        def end(self, *args, **kwargs): pass
    
    def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    langfuse_context = type('MockContext', (), {
        'update_current_trace': lambda *args, **kwargs: None,
        'update_current_span': lambda *args, **kwargs: None
    })()

logger = structlog.get_logger()


@dataclass
class ConversationMetrics:
    """Conversation-level metrics for analytics."""
    conversation_id: str
    conversation_type: str
    total_messages: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    duration_seconds: float = 0.0
    agent_interactions: List[Dict[str, Any]] = None
    document_generations: List[Dict[str, Any]] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.agent_interactions is None:
            self.agent_interactions = []
        if self.document_generations is None:
            self.document_generations = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class AgentMetrics:
    """Agent-specific performance metrics."""
    agent_id: str
    total_executions: int = 0
    success_rate: float = 0.0
    average_duration: float = 0.0
    token_usage: Dict[str, int] = None
    cost_breakdown: Dict[str, float] = None
    error_count: int = 0
    
    def __post_init__(self):
        if self.token_usage is None:
            self.token_usage = {"input": 0, "output": 0, "total": 0}
        if self.cost_breakdown is None:
            self.cost_breakdown = {}


class LangfuseManager:
    """
    Centralized Langfuse observability manager for CrewAI implementation.
    Maintains compatibility with LangGraph tracking while adapting to CrewAI patterns.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self.client: Optional[Langfuse] = None
        self.enabled = False
        self.active_traces: Dict[str, Any] = {}
        self.active_spans: Dict[str, Any] = {}
        self.conversation_metrics: Dict[str, ConversationMetrics] = {}
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        
        # Model cost mapping (per 1K tokens)
        self.model_costs = {
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
            "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
        }
        
        self._initialize_client()
        self._initialized = True
    
    def _initialize_client(self):
        """Initialize Langfuse client with environment configuration."""
        
        if not LANGFUSE_AVAILABLE:
            logger.warning("Langfuse not available - using mock implementation")
            self.client = MockLangfuse()
            return
        
        try:
            # Get configuration from environment
            secret_key = os.getenv("LANGFUSE_SECRET_KEY")
            public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
            host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
            
            if not secret_key or not public_key:
                logger.warning("Langfuse credentials not found - observability disabled")
                self.client = MockLangfuse()
                return
            
            # Initialize client
            self.client = Langfuse(
                secret_key=secret_key,
                public_key=public_key,
                host=host
            )
            
            # Test authentication
            auth_check = self.client.auth_check()
            if auth_check:
                self.enabled = True
                logger.info("Langfuse observability enabled")
            else:
                logger.error("Langfuse authentication failed")
                self.client = MockLangfuse()
                
        except Exception as e:
            logger.error(f"Failed to initialize Langfuse: {e}")
            self.client = MockLangfuse()
    
    def start_conversation_trace(
        self,
        conversation_id: str,
        conversation_type: str,
        user_input: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Start a new conversation trace."""
        
        if conversation_id in self.conversation_metrics:
            logger.warning(f"Conversation {conversation_id} already exists in metrics")
        
        # Create conversation metrics
        self.conversation_metrics[conversation_id] = ConversationMetrics(
            conversation_id=conversation_id,
            conversation_type=conversation_type
        )
        
        if not self.enabled:
            return None
        
        try:
            trace = self.client.trace(
                name=f"conversation_{conversation_type}",
                id=conversation_id,
                input=user_input,
                metadata={
                    "conversation_type": conversation_type,
                    "conversation_id": conversation_id,
                    "start_time": datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
            )
            
            self.active_traces[conversation_id] = trace
            logger.debug(f"Started conversation trace: {conversation_id}")
            return trace
            
        except Exception as e:
            logger.error(f"Failed to start conversation trace: {e}")
            return None
    
    def create_crew_span(
        self,
        conversation_id: str,
        crew_name: str,
        agents: List[str],
        tasks: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Create span for CrewAI crew execution."""
        
        if not self.enabled or conversation_id not in self.active_traces:
            return None
        
        try:
            trace = self.active_traces[conversation_id]
            span = trace.span(
                name=f"crew_{crew_name}",
                input={
                    "agents": agents,
                    "tasks": tasks,
                    "crew_type": crew_name
                },
                metadata={
                    "crew_name": crew_name,
                    "agent_count": len(agents),
                    "task_count": len(tasks),
                    "start_time": datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
            )
            
            span_key = f"{conversation_id}:{crew_name}"
            self.active_spans[span_key] = span
            logger.debug(f"Created crew span: {crew_name}")
            return span
            
        except Exception as e:
            logger.error(f"Failed to create crew span: {e}")
            return None
    
    def create_agent_span(
        self,
        conversation_id: str,
        agent_id: str,
        task_description: str,
        parent_span_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Create span for individual agent execution."""
        
        if not self.enabled:
            return None
        
        try:
            # Get parent (trace or span)
            parent = None
            if parent_span_name:
                parent_key = f"{conversation_id}:{parent_span_name}"
                parent = self.active_spans.get(parent_key)
            
            if not parent and conversation_id in self.active_traces:
                parent = self.active_traces[conversation_id]
            
            if not parent:
                logger.warning(f"No parent found for agent span: {agent_id}")
                return None
            
            span = parent.span(
                name=f"agent_{agent_id}",
                input=task_description,
                metadata={
                    "agent_id": agent_id,
                    "task_type": task_description[:100],
                    "start_time": datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
            )
            
            span_key = f"{conversation_id}:{agent_id}"
            self.active_spans[span_key] = span
            
            # Initialize agent metrics if needed
            if agent_id not in self.agent_metrics:
                self.agent_metrics[agent_id] = AgentMetrics(agent_id=agent_id)
            
            logger.debug(f"Created agent span: {agent_id}")
            return span
            
        except Exception as e:
            logger.error(f"Failed to create agent span: {e}")
            return None
    
    def track_llm_generation(
        self,
        conversation_id: str,
        agent_id: str,
        model: str,
        prompt: str,
        response: str,
        input_tokens: int,
        output_tokens: int,
        duration_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track LLM generation with comprehensive metrics."""
        
        # Calculate cost
        total_tokens = input_tokens + output_tokens
        cost = self._calculate_cost(model, input_tokens, output_tokens)
        
        # Update conversation metrics
        if conversation_id in self.conversation_metrics:
            conv_metrics = self.conversation_metrics[conversation_id]
            conv_metrics.total_tokens += total_tokens
            conv_metrics.total_cost += cost
        
        # Update agent metrics
        if agent_id in self.agent_metrics:
            agent_metrics = self.agent_metrics[agent_id]
            agent_metrics.total_executions += 1
            agent_metrics.token_usage["input"] += input_tokens
            agent_metrics.token_usage["output"] += output_tokens
            agent_metrics.token_usage["total"] += total_tokens
            agent_metrics.cost_breakdown[model] = agent_metrics.cost_breakdown.get(model, 0) + cost
        
        if not self.enabled:
            return
        
        try:
            # Get parent span
            span_key = f"{conversation_id}:{agent_id}"
            parent_span = self.active_spans.get(span_key)
            
            if not parent_span and conversation_id in self.active_traces:
                parent_span = self.active_traces[conversation_id]
            
            if not parent_span:
                logger.warning(f"No parent span found for LLM generation: {agent_id}")
                return
            
            generation = parent_span.generation(
                name=f"{agent_id}_llm_call",
                model=model,
                input=prompt[:2000],  # Truncate for readability
                output=response[:2000],
                usage={
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": total_tokens,
                    "unit": "TOKENS"
                },
                metadata={
                    "agent_id": agent_id,
                    "model": model,
                    "cost_usd": cost,
                    "duration_ms": duration_ms,
                    "conversation_id": conversation_id,
                    **(metadata or {})
                }
            )
            
            logger.debug(f"Tracked LLM generation: {agent_id} using {model}")
            
        except Exception as e:
            logger.error(f"Failed to track LLM generation: {e}")
    
    def track_document_generation(
        self,
        conversation_id: str,
        document_type: str,
        success: bool,
        generation_time: float,
        word_count: Optional[int] = None,
        quality_score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track document generation events."""
        
        # Update conversation metrics
        if conversation_id in self.conversation_metrics:
            conv_metrics = self.conversation_metrics[conversation_id]
            doc_info = {
                "document_type": document_type,
                "success": success,
                "generation_time": generation_time,
                "word_count": word_count,
                "quality_score": quality_score,
                "timestamp": datetime.utcnow().isoformat()
            }
            conv_metrics.document_generations.append(doc_info)
        
        if not self.enabled or conversation_id not in self.active_traces:
            return
        
        try:
            trace = self.active_traces[conversation_id]
            span = trace.span(
                name=f"document_generation_{document_type}",
                input=f"Generate {document_type}",
                output="Document generated" if success else "Generation failed",
                metadata={
                    "document_type": document_type,
                    "success": success,
                    "generation_time": generation_time,
                    "word_count": word_count,
                    "quality_score": quality_score,
                    "conversation_id": conversation_id,
                    **(metadata or {})
                }
            )
            
            span.end()
            logger.debug(f"Tracked document generation: {document_type}")
            
        except Exception as e:
            logger.error(f"Failed to track document generation: {e}")
    
    def update_agent_span(
        self,
        conversation_id: str,
        agent_id: str,
        output: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Update and end agent span."""
        
        span_key = f"{conversation_id}:{agent_id}"
        
        # Update agent metrics
        if agent_id in self.agent_metrics:
            agent_metrics = self.agent_metrics[agent_id]
            if not success:
                agent_metrics.error_count += 1
            # Recalculate success rate
            total_ops = agent_metrics.total_executions + agent_metrics.error_count
            if total_ops > 0:
                agent_metrics.success_rate = agent_metrics.total_executions / total_ops
        
        if not self.enabled or span_key not in self.active_spans:
            return
        
        try:
            span = self.active_spans[span_key]
            
            update_data = {
                "end_time": datetime.utcnow().isoformat(),
                "success": success,
                **(metadata or {})
            }
            
            if output:
                update_data["output"] = output[:1000]  # Truncate
            
            if error:
                update_data["error"] = error
                update_data["level"] = "ERROR"
            
            span.update(**update_data)
            span.end()
            
            # Remove from active spans
            del self.active_spans[span_key]
            logger.debug(f"Updated agent span: {agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to update agent span: {e}")
    
    def complete_conversation_trace(
        self,
        conversation_id: str,
        final_output: Optional[str] = None,
        success: bool = True,
        documents_generated: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Complete conversation trace with final metrics."""
        
        # Update conversation metrics
        if conversation_id in self.conversation_metrics:
            conv_metrics = self.conversation_metrics[conversation_id]
            conv_metrics.completed_at = datetime.utcnow()
            if conv_metrics.created_at:
                conv_metrics.duration_seconds = (
                    conv_metrics.completed_at - conv_metrics.created_at
                ).total_seconds()
        
        if not self.enabled or conversation_id not in self.active_traces:
            return
        
        try:
            trace = self.active_traces[conversation_id]
            
            update_data = {
                "output": final_output or "Conversation completed",
                "end_time": datetime.utcnow().isoformat(),
                "success": success,
                "documents_generated": documents_generated or [],
                **(metadata or {})
            }
            
            # Add final metrics
            if conversation_id in self.conversation_metrics:
                conv_metrics = self.conversation_metrics[conversation_id]
                update_data.update({
                    "total_tokens": conv_metrics.total_tokens,
                    "total_cost": conv_metrics.total_cost,
                    "duration_seconds": conv_metrics.duration_seconds,
                    "document_count": len(conv_metrics.document_generations)
                })
            
            trace.update(**update_data)
            
            # Clean up
            del self.active_traces[conversation_id]
            
            # End any remaining spans
            remaining_spans = [
                key for key in self.active_spans.keys() 
                if key.startswith(f"{conversation_id}:")
            ]
            for span_key in remaining_spans:
                try:
                    self.active_spans[span_key].end()
                    del self.active_spans[span_key]
                except Exception:
                    pass
            
            logger.info(f"Completed conversation trace: {conversation_id}")
            
        except Exception as e:
            logger.error(f"Failed to complete conversation trace: {e}")
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for LLM usage."""
        
        if model not in self.model_costs:
            logger.warning(f"Cost data not available for model: {model}")
            return 0.0
        
        costs = self.model_costs[model]
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        
        return input_cost + output_cost
    
    def get_conversation_metrics(self, conversation_id: str) -> Optional[ConversationMetrics]:
        """Get metrics for a specific conversation."""
        return self.conversation_metrics.get(conversation_id)
    
    def get_agent_metrics(self, agent_id: str) -> Optional[AgentMetrics]:
        """Get metrics for a specific agent."""
        return self.agent_metrics.get(agent_id)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics."""
        
        total_conversations = len(self.conversation_metrics)
        total_tokens = sum(m.total_tokens for m in self.conversation_metrics.values())
        total_cost = sum(m.total_cost for m in self.conversation_metrics.values())
        
        # Agent performance summary
        agent_summary = {}
        for agent_id, metrics in self.agent_metrics.items():
            agent_summary[agent_id] = {
                "total_executions": metrics.total_executions,
                "success_rate": metrics.success_rate,
                "total_tokens": metrics.token_usage["total"],
                "total_cost": sum(metrics.cost_breakdown.values())
            }
        
        return {
            "total_conversations": total_conversations,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "agent_metrics": agent_summary,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def export_conversation_data(self, conversation_id: str) -> Dict[str, Any]:
        """Export complete conversation data for analysis."""
        
        if conversation_id not in self.conversation_metrics:
            return {"error": "Conversation not found"}
        
        conv_metrics = self.conversation_metrics[conversation_id]
        
        # Get related agent data
        agent_data = {}
        for agent_id, metrics in self.agent_metrics.items():
            agent_data[agent_id] = asdict(metrics)
        
        return {
            "conversation_metrics": asdict(conv_metrics),
            "agent_metrics": agent_data,
            "export_timestamp": datetime.utcnow().isoformat()
        }
    
    def flush_data(self):
        """Flush all pending data to Langfuse."""
        if self.enabled:
            try:
                self.client.flush()
                logger.debug("Flushed data to Langfuse")
            except Exception as e:
                logger.error(f"Failed to flush Langfuse data: {e}")
    
    @contextmanager
    def observe_agent_execution(self, conversation_id: str, agent_id: str, task_description: str):
        """Context manager for agent execution tracking."""
        
        span = self.create_agent_span(conversation_id, agent_id, task_description)
        start_time = datetime.utcnow()
        
        try:
            yield span
            # Success case
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.update_agent_span(
                conversation_id, agent_id, 
                success=True, 
                metadata={"duration_seconds": duration}
            )
        except Exception as e:
            # Error case
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.update_agent_span(
                conversation_id, agent_id, 
                success=False, 
                error=str(e),
                metadata={"duration_seconds": duration}
            )
            raise


# Global manager instance
langfuse_manager = LangfuseManager()


# Helper functions for backward compatibility
def get_langfuse_anthropic():
    """Get Anthropic client with Langfuse instrumentation."""
    if LANGFUSE_AVAILABLE and langfuse_manager.enabled:
        return langfuse_anthropic
    else:
        # Return regular anthropic client
        import anthropic
        return anthropic


def get_langfuse_openai():
    """Get OpenAI client with Langfuse instrumentation."""
    if LANGFUSE_AVAILABLE and langfuse_manager.enabled:
        return langfuse_openai
    else:
        # Return regular openai client
        import openai
        return openai


# Decorator for automatic LLM call tracking
def track_llm_call(agent_id: str, conversation_id: str):
    """Decorator for automatic LLM call tracking."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Extract metrics if available
                if hasattr(result, 'usage'):
                    langfuse_manager.track_llm_generation(
                        conversation_id=conversation_id,
                        agent_id=agent_id,
                        model=getattr(result, 'model', 'unknown'),
                        prompt=str(args[0]) if args else "",
                        response=str(result),
                        input_tokens=getattr(result.usage, 'input_tokens', 0),
                        output_tokens=getattr(result.usage, 'output_tokens', 0),
                        duration_ms=duration
                    )
                
                return result
            except Exception as e:
                # Track error
                if agent_id in langfuse_manager.agent_metrics:
                    langfuse_manager.agent_metrics[agent_id].error_count += 1
                raise
        return wrapper
    return decorator