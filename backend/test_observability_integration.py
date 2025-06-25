"""
Test Observability Integration with CrewAI Agents.
Validates Langfuse tracking and analytics capabilities.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch

from agents import create_agent, OrchestratorAgent, ProductManagerAgent
from agents.base_observability import ObservableAgentMixin, track_crew_execution
from core.langfuse_config import langfuse_manager
from core.analytics import analytics_engine


class TestObservabilityIntegration:
    """Test observability integration with CrewAI agents."""
    
    def test_agent_creation_with_observability(self):
        """Test that agents are created with observability capabilities."""
        
        # Create agent with observability
        orchestrator = create_agent('orchestrator', with_observability=True)
        
        # Verify it has observability capabilities
        assert isinstance(orchestrator, ObservableAgentMixin)
        assert hasattr(orchestrator, 'set_observability_context')
        assert hasattr(orchestrator, 'track_task_execution')
        assert hasattr(orchestrator, 'track_llm_interaction')
        assert orchestrator.agent_id == 'orchestrator'
    
    def test_product_manager_observability(self):
        """Test Product Manager agent with observability."""
        
        pm_agent = create_agent('product_manager', with_observability=True)
        
        assert isinstance(pm_agent, ObservableAgentMixin)
        assert pm_agent.agent_id == 'product_manager'
        assert hasattr(pm_agent, 'PRODUCT_QUESTIONS')  # Preserved functionality
    
    def test_observability_context_setting(self):
        """Test setting observability context on agents."""
        
        agent = create_agent('orchestrator')
        conversation_id = "test_conv_123"
        context = {"project_type": "full_product"}
        
        # Set observability context
        agent.set_observability_context(conversation_id, context)
        
        assert agent.conversation_id == conversation_id
        assert agent.execution_context == context
    
    @patch('agents.base_observability.langfuse_manager')
    def test_task_execution_tracking(self, mock_langfuse):
        """Test task execution tracking with observability."""
        
        agent = create_agent('orchestrator')
        agent.set_observability_context("test_conv", {"test": "data"})
        
        # Mock task
        mock_task = Mock()
        mock_task.description = "Test task description"
        mock_task.id = "task_123"
        
        # Mock Langfuse manager methods
        mock_span = Mock()
        mock_langfuse.observe_agent_execution.return_value.__enter__.return_value = mock_span
        mock_langfuse.observe_agent_execution.return_value.__exit__.return_value = None
        
        # Execute task with tracking
        @agent.track_task_execution(mock_task)
        def test_execution():
            return "Task completed successfully"
        
        result = test_execution()
        
        assert result == "Task completed successfully"
        assert len(agent.task_history) > 0
        assert agent.task_history[-1]["task_id"] == "task_123"
        assert agent.task_history[-1]["status"] == "started"
    
    def test_llm_interaction_tracking(self):
        """Test LLM interaction tracking."""
        
        agent = create_agent('product_manager')
        agent.set_observability_context("test_conv", {})
        
        # Track LLM interaction
        agent.track_llm_interaction(
            prompt="What is the product vision?",
            response="The product vision is to...",
            model="claude-3-sonnet-20240229",
            input_tokens=10,
            output_tokens=25,
            duration_ms=1500
        )
        
        # Verify tracking was called (would verify with Langfuse in real test)
        assert agent.conversation_id == "test_conv"
    
    def test_agent_collaboration_tracking(self):
        """Test agent collaboration tracking."""
        
        orchestrator = create_agent('orchestrator')
        orchestrator.set_observability_context("test_conv", {})
        
        # Track collaboration
        orchestrator.track_agent_collaboration(
            target_agent="product_manager",
            collaboration_type="handoff",
            context={"task": "requirements_gathering"},
            success=True
        )
        
        assert "collaborations" in orchestrator.execution_context
        assert len(orchestrator.execution_context["collaborations"]) == 1
        
        collab = orchestrator.execution_context["collaborations"][0]
        assert collab["source_agent"] == "orchestrator"
        assert collab["target_agent"] == "product_manager"
        assert collab["collaboration_type"] == "handoff"
    
    def test_execution_metrics_generation(self):
        """Test generation of execution metrics."""
        
        agent = create_agent('orchestrator')
        agent.set_observability_context("test_conv", {})
        
        # Add some mock task history
        agent.task_history = [
            {
                "task_id": "task_1",
                "success": True,
                "execution_time": 2.5
            },
            {
                "task_id": "task_2", 
                "success": False,
                "execution_time": 1.0
            },
            {
                "task_id": "task_3",
                "success": True,
                "execution_time": 3.0
            }
        ]
        
        metrics = agent.get_execution_metrics()
        
        assert metrics["agent_id"] == "orchestrator"
        assert metrics["total_tasks"] == 3
        assert metrics["successful_tasks"] == 2
        assert metrics["failed_tasks"] == 1
        assert metrics["success_rate"] == 2/3
        assert metrics["average_execution_time"] == 2.17  # Approximately
    
    def test_crew_execution_tracking_decorator(self):
        """Test crew execution tracking decorator."""
        
        @track_crew_execution(
            conversation_id="test_conv",
            crew_name="document_generation_crew",
            agents=["orchestrator", "product_manager"],
            tasks=["analysis", "prd_generation"]
        )
        def mock_crew_execution():
            return "Crew execution completed"
        
        # This would normally create spans in Langfuse
        result = mock_crew_execution()
        assert result == "Crew execution completed"
    
    @pytest.mark.asyncio
    async def test_analytics_engine_integration(self):
        """Test integration with analytics engine."""
        
        # Mock conversation metrics in langfuse manager
        langfuse_manager.conversation_metrics["test_conv"] = Mock(
            conversation_id="test_conv",
            total_tokens=1000,
            total_cost=5.0,
            total_messages=10,
            duration_seconds=300,
            document_generations=[
                {"success": True, "document_type": "PRD", "quality_score": 0.85}
            ]
        )
        
        # Get conversation metrics
        metrics = await analytics_engine.get_conversation_metrics("test_conv")
        
        assert "messages_per_minute" in metrics
        assert "cost_per_message" in metrics
        assert "tokens_per_message" in metrics
    
    def test_observable_agent_factory(self):
        """Test the observable agent factory function."""
        
        from agents.base_observability import create_observable_agent
        
        # This would normally create an observable wrapper
        # For this test, we'll verify the function exists and can be called
        assert callable(create_observable_agent)
    
    def test_agent_performance_summary(self):
        """Test agent performance summary generation."""
        
        from agents.base_observability import get_agent_performance_summary
        
        # Mock agent metrics in langfuse manager
        mock_metrics = Mock()
        mock_metrics.total_executions = 10
        mock_metrics.success_rate = 0.9
        mock_metrics.average_duration = 25.0
        mock_metrics.token_usage = {"total": 5000}
        mock_metrics.cost_breakdown = {"claude-3-sonnet": 10.0}
        mock_metrics.error_count = 1
        
        with patch.object(langfuse_manager, 'get_agent_metrics', return_value=mock_metrics):
            summary = get_agent_performance_summary("orchestrator")
            
            assert summary["agent_id"] == "orchestrator"
            assert summary["total_executions"] == 10
            assert summary["success_rate"] == 0.9
            assert "efficiency_score" in summary
    
    def test_document_generation_tracking(self):
        """Test document generation tracking by agents."""
        
        from agents.base_observability import track_document_generation_by_agent
        
        # Track document generation
        track_document_generation_by_agent(
            conversation_id="test_conv",
            agent_id="product_manager",
            document_type="PRD",
            generation_time=45.0,
            success=True,
            word_count=2500,
            quality_score=0.88
        )
        
        # This would normally send data to Langfuse
        # For now, just verify the function can be called without error
        assert True
    
    def test_error_handling_in_observability(self):
        """Test error handling in observability components."""
        
        agent = create_agent('orchestrator')
        
        # Test with no conversation ID set
        agent.track_llm_interaction(
            prompt="test",
            response="test",
            model="test",
            input_tokens=10,
            output_tokens=10
        )
        
        # Should not raise an error, just skip tracking
        assert agent.conversation_id is None
    
    def test_observability_data_export(self):
        """Test export of observability data."""
        
        agent = create_agent('product_manager')
        agent.set_observability_context("test_conv", {"project": "test"})
        
        # Add some execution data
        agent.task_history = [{"task_id": "test", "success": True}]
        agent.execution_context["tool_usage"] = [{"tool_name": "prd_generator"}]
        
        export_data = agent.export_execution_data()
        
        assert "agent_metadata" in export_data
        assert "execution_metrics" in export_data
        assert "task_history" in export_data
        assert "execution_context" in export_data
        assert export_data["agent_metadata"]["agent_id"] == "product_manager"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])