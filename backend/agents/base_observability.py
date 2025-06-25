"""
Base Observability Mixin for CrewAI Agents.
Adds comprehensive Langfuse tracking to all agent interactions.
"""

import time
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from functools import wraps
from crewai import Agent, Task
import structlog

from core.langfuse_config import langfuse_manager, track_llm_call

logger = structlog.get_logger()


class ObservableAgentMixin:
    """
    Mixin to add comprehensive observability to CrewAI agents.
    Tracks agent execution, LLM calls, task completion, and performance metrics.
    """
    
    def __init__(self):
        # Observability state
        self.conversation_id: Optional[str] = None
        self.agent_id: str = getattr(self, 'role', self.__class__.__name__).lower().replace(' ', '_')
        self.execution_context: Dict[str, Any] = {}
        self.start_time: Optional[datetime] = None
        self.task_history: List[Dict[str, Any]] = []
        
    def set_observability_context(
        self, 
        conversation_id: str, 
        context: Optional[Dict[str, Any]] = None
    ):
        """Set observability context for tracking."""
        self.conversation_id = conversation_id
        self.execution_context = context or {}
        
        logger.info(
            f"Observability context set for agent {self.agent_id}",
            conversation_id=conversation_id,
            agent_id=self.agent_id
        )
    
    def track_task_execution(self, task: Task, **kwargs):
        """Decorator-style method to track task execution."""
        
        def decorator(execution_func):
            @wraps(execution_func)
            def wrapper(*args, **kwargs):
                return self._execute_with_tracking(
                    execution_func, task, *args, **kwargs
                )
            return wrapper
        
        return decorator
    
    def _execute_with_tracking(self, execution_func, task: Task, *args, **kwargs):
        """Execute task with comprehensive tracking."""
        
        if not self.conversation_id:
            logger.warning(f"No conversation ID set for agent {self.agent_id}")
            return execution_func(*args, **kwargs)
        
        task_description = getattr(task, 'description', str(task))[:200]
        execution_start = datetime.utcnow()
        
        # Create agent span
        with langfuse_manager.observe_agent_execution(
            conversation_id=self.conversation_id,
            agent_id=self.agent_id,
            task_description=task_description
        ) as span:
            
            try:
                # Track task start
                self._track_task_start(task, execution_start)
                
                # Execute the actual task
                result = execution_func(*args, **kwargs)
                
                # Track successful completion
                execution_time = (datetime.utcnow() - execution_start).total_seconds()
                self._track_task_completion(
                    task, result, execution_time, success=True
                )
                
                return result
                
            except Exception as e:
                # Track error
                execution_time = (datetime.utcnow() - execution_start).total_seconds()
                self._track_task_completion(
                    task, None, execution_time, success=False, error=str(e)
                )
                
                # Re-raise the exception
                raise
    
    def _track_task_start(self, task: Task, start_time: datetime):
        """Track the start of task execution."""
        
        task_info = {
            "task_id": getattr(task, 'id', 'unknown'),
            "task_description": getattr(task, 'description', str(task))[:200],
            "agent_id": self.agent_id,
            "start_time": start_time.isoformat(),
            "status": "started"
        }
        
        self.task_history.append(task_info)
        
        logger.info(
            f"Task started by agent {self.agent_id}",
            conversation_id=self.conversation_id,
            task_info=task_info
        )
    
    def _track_task_completion(
        self, 
        task: Task, 
        result: Any, 
        execution_time: float,
        success: bool = True,
        error: Optional[str] = None
    ):
        """Track task completion with results and metrics."""
        
        # Update task history
        task_info = {
            "task_id": getattr(task, 'id', 'unknown'),
            "agent_id": self.agent_id,
            "execution_time": execution_time,
            "success": success,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        if error:
            task_info["error"] = error
        
        if result and success:
            # Extract key information from result
            result_summary = self._summarize_result(result)
            task_info["result_summary"] = result_summary
        
        self.task_history.append(task_info)
        
        # Log completion
        if success:
            logger.info(
                f"Task completed successfully by agent {self.agent_id}",
                conversation_id=self.conversation_id,
                execution_time=execution_time,
                task_info=task_info
            )
        else:
            logger.error(
                f"Task failed for agent {self.agent_id}",
                conversation_id=self.conversation_id,
                error=error,
                execution_time=execution_time
            )
    
    def track_llm_interaction(
        self,
        prompt: str,
        response: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        duration_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track LLM interaction with comprehensive metrics."""
        
        if not self.conversation_id:
            return
        
        langfuse_manager.track_llm_generation(
            conversation_id=self.conversation_id,
            agent_id=self.agent_id,
            model=model,
            prompt=prompt,
            response=response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
            metadata={
                "agent_context": self.execution_context,
                **(metadata or {})
            }
        )
        
        logger.debug(
            f"LLM interaction tracked for agent {self.agent_id}",
            conversation_id=self.conversation_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
    
    def track_tool_usage(
        self,
        tool_name: str,
        tool_input: Any,
        tool_output: Any,
        execution_time: float,
        success: bool = True,
        error: Optional[str] = None
    ):
        """Track tool usage within agent execution."""
        
        tool_info = {
            "tool_name": tool_name,
            "agent_id": self.agent_id,
            "execution_time": execution_time,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if error:
            tool_info["error"] = error
        
        # Add to execution context
        if "tool_usage" not in self.execution_context:
            self.execution_context["tool_usage"] = []
        
        self.execution_context["tool_usage"].append(tool_info)
        
        logger.debug(
            f"Tool usage tracked for agent {self.agent_id}",
            conversation_id=self.conversation_id,
            tool_name=tool_name,
            success=success
        )
    
    def track_agent_collaboration(
        self,
        target_agent: str,
        collaboration_type: str,
        context: Dict[str, Any],
        success: bool = True
    ):
        """Track collaboration between agents."""
        
        collaboration_info = {
            "source_agent": self.agent_id,
            "target_agent": target_agent,
            "collaboration_type": collaboration_type,
            "context": context,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add to execution context
        if "collaborations" not in self.execution_context:
            self.execution_context["collaborations"] = []
        
        self.execution_context["collaborations"].append(collaboration_info)
        
        logger.info(
            f"Agent collaboration tracked: {self.agent_id} -> {target_agent}",
            conversation_id=self.conversation_id,
            collaboration_type=collaboration_type
        )
    
    def _summarize_result(self, result: Any) -> Dict[str, Any]:
        """Create a summary of task result for tracking."""
        
        summary = {
            "result_type": type(result).__name__,
            "result_length": len(str(result)) if result else 0
        }
        
        # Extract specific information based on result type
        if isinstance(result, str):
            summary.update({
                "word_count": len(result.split()),
                "character_count": len(result),
                "has_content": bool(result.strip())
            })
        
        elif isinstance(result, dict):
            summary.update({
                "key_count": len(result),
                "keys": list(result.keys())[:10]  # First 10 keys
            })
        
        elif isinstance(result, list):
            summary.update({
                "item_count": len(result),
                "item_types": list(set(type(item).__name__ for item in result[:5]))
            })
        
        return summary
    
    def get_execution_metrics(self) -> Dict[str, Any]:
        """Get execution metrics for this agent."""
        
        if not self.task_history:
            return {"status": "no_tasks_executed"}
        
        successful_tasks = [t for t in self.task_history if t.get("success", False)]
        failed_tasks = [t for t in self.task_history if not t.get("success", True)]
        
        execution_times = [
            t["execution_time"] for t in self.task_history 
            if "execution_time" in t
        ]
        
        metrics = {
            "agent_id": self.agent_id,
            "conversation_id": self.conversation_id,
            "total_tasks": len(self.task_history),
            "successful_tasks": len(successful_tasks),
            "failed_tasks": len(failed_tasks),
            "success_rate": len(successful_tasks) / len(self.task_history) if self.task_history else 0,
            "average_execution_time": sum(execution_times) / len(execution_times) if execution_times else 0,
            "total_execution_time": sum(execution_times),
            "tool_usage_count": len(self.execution_context.get("tool_usage", [])),
            "collaboration_count": len(self.execution_context.get("collaborations", [])),
            "execution_context": self.execution_context
        }
        
        return metrics
    
    def export_execution_data(self) -> Dict[str, Any]:
        """Export complete execution data for analysis."""
        
        return {
            "agent_metadata": {
                "agent_id": self.agent_id,
                "conversation_id": self.conversation_id,
                "agent_class": self.__class__.__name__
            },
            "execution_metrics": self.get_execution_metrics(),
            "task_history": self.task_history,
            "execution_context": self.execution_context,
            "export_timestamp": datetime.utcnow().isoformat()
        }


def create_observable_agent(agent_class, **kwargs) -> Agent:
    """
    Factory function to create an observable CrewAI agent.
    Wraps the standard agent with observability capabilities.
    """
    
    # Create the base agent
    base_agent = agent_class.create(**kwargs)
    
    # Create observable wrapper
    class ObservableAgent(ObservableAgentMixin):
        def __init__(self, base_agent: Agent):
            super().__init__()
            self.base_agent = base_agent
            self.role = base_agent.role
            self.goal = base_agent.goal
            self.backstory = base_agent.backstory
            self.tools = base_agent.tools
            self.llm = base_agent.llm
            self.verbose = base_agent.verbose
            self.allow_delegation = base_agent.allow_delegation
            self.max_iter = base_agent.max_iter
            self.memory = base_agent.memory
            
            # Set agent_id from role
            self.agent_id = self.role.lower().replace(' ', '_').replace('-', '_')
        
        def execute_task(self, task: Task, **kwargs):
            """Execute task with full observability tracking."""
            
            @self.track_task_execution(task, **kwargs)
            def _execute():
                # In a real implementation, this would call the actual CrewAI execution
                # For now, we'll simulate the execution
                start_time = time.time()
                
                try:
                    # This would be the actual agent execution
                    result = f"Task completed by {self.agent_id}: {getattr(task, 'description', str(task))[:100]}"
                    
                    # Simulate LLM interaction tracking
                    if hasattr(self, 'conversation_id') and self.conversation_id:
                        self.track_llm_interaction(
                            prompt=getattr(task, 'description', str(task)),
                            response=result,
                            model="claude-3-sonnet-20240229",
                            input_tokens=len(str(task).split()) * 2,  # Rough estimate
                            output_tokens=len(result.split()) * 2,    # Rough estimate
                            duration_ms=(time.time() - start_time) * 1000
                        )
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Task execution failed for {self.agent_id}: {e}")
                    raise
            
            return _execute()
        
        def __getattr__(self, name):
            """Delegate unknown attributes to base agent."""
            return getattr(self.base_agent, name)
    
    return ObservableAgent(base_agent)


def track_crew_execution(
    conversation_id: str,
    crew_name: str,
    agents: List[str],
    tasks: List[str]
):
    """Decorator to track complete crew execution."""
    
    def decorator(execution_func):
        @wraps(execution_func)
        def wrapper(*args, **kwargs):
            
            # Create crew span
            crew_span = langfuse_manager.create_crew_span(
                conversation_id=conversation_id,
                crew_name=crew_name,
                agents=agents,
                tasks=tasks
            )
            
            start_time = datetime.utcnow()
            
            try:
                # Execute crew
                result = execution_func(*args, **kwargs)
                
                # Track successful completion
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                if crew_span:
                    crew_span.update(
                        output=f"Crew execution completed successfully",
                        end_time=datetime.utcnow().isoformat(),
                        success=True,
                        execution_time=execution_time
                    )
                    crew_span.end()
                
                logger.info(
                    f"Crew execution completed: {crew_name}",
                    conversation_id=conversation_id,
                    execution_time=execution_time
                )
                
                return result
                
            except Exception as e:
                # Track error
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                if crew_span:
                    crew_span.update(
                        output=f"Crew execution failed: {str(e)}",
                        end_time=datetime.utcnow().isoformat(),
                        success=False,
                        error=str(e),
                        execution_time=execution_time
                    )
                    crew_span.end()
                
                logger.error(
                    f"Crew execution failed: {crew_name}",
                    conversation_id=conversation_id,
                    error=str(e)
                )
                
                raise
        
        return wrapper
    return decorator


# Utility functions for agent observability
def get_agent_performance_summary(agent_id: str) -> Dict[str, Any]:
    """Get performance summary for an agent."""
    
    agent_metrics = langfuse_manager.get_agent_metrics(agent_id)
    
    if not agent_metrics:
        return {"error": f"No metrics found for agent {agent_id}"}
    
    return {
        "agent_id": agent_id,
        "total_executions": agent_metrics.total_executions,
        "success_rate": agent_metrics.success_rate,
        "average_duration": agent_metrics.average_duration,
        "token_usage": agent_metrics.token_usage,
        "cost_breakdown": agent_metrics.cost_breakdown,
        "error_count": agent_metrics.error_count,
        "efficiency_score": agent_metrics.total_executions / max(sum(agent_metrics.cost_breakdown.values()), 0.01)
    }


def track_document_generation_by_agent(
    conversation_id: str,
    agent_id: str,
    document_type: str,
    generation_time: float,
    success: bool,
    word_count: Optional[int] = None,
    quality_score: Optional[float] = None
):
    """Track document generation by specific agent."""
    
    langfuse_manager.track_document_generation(
        conversation_id=conversation_id,
        document_type=document_type,
        success=success,
        generation_time=generation_time,
        word_count=word_count,
        quality_score=quality_score,
        metadata={
            "generating_agent": agent_id,
            "generation_method": "agent_driven"
        }
    )
    
    logger.info(
        f"Document generation tracked: {document_type} by {agent_id}",
        conversation_id=conversation_id,
        success=success,
        generation_time=generation_time
    )