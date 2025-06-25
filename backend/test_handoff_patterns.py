#!/usr/bin/env python3
"""
Integration tests for LangGraph to CrewAI handoff pattern conversion.
Tests conversation flow, task delegation, and agent collaboration patterns.
"""

import asyncio
import pytest
from typing import Dict, Any
from unittest.mock import Mock, patch

from conversation_flow import (
    conversation_flow, 
    ConversationPhase, 
    ConversationContext,
    CrewAIConversationFlow
)
from task_delegation import (
    task_delegation_manager,
    TaskDelegationManager,
    TaskDelegationContext,
    DelegationReason,
    DelegationUrgency
)
from crews.project_crew import ProjectCrew
from agents import OrchestratorAgent, ProductManagerAgent


class TestConversationFlowIntegration:
    """Test conversation flow integration patterns."""
    
    def setup_method(self):
        """Setup test environment."""
        self.flow = CrewAIConversationFlow()
        self.test_conversation_id = "test_conv_123"
        
    async def test_conversation_type_detection(self):
        """Test automatic conversation type detection."""
        
        test_cases = [
            ("I want to build a task management application", "idea"),
            ("Add a new feature to export data", "feature"), 
            ("Create a utility script for automation", "tool"),
            ("Enhance the existing dashboard", "feature")
        ]
        
        for user_input, expected_type in test_cases:
            detected_type = await self.flow._detect_conversation_type(user_input)
            assert detected_type == expected_type, f"Failed for: {user_input}"
    
    def test_discovery_agent_selection(self):
        """Test agent selection for discovery phase."""
        
        # Test idea conversation
        agents = self.flow._get_discovery_agents("idea")
        expected = ["orchestrator", "product_manager", "user_researcher", "business_analyst"]
        assert agents == expected
        
        # Test feature conversation
        agents = self.flow._get_discovery_agents("feature")
        expected = ["orchestrator", "product_manager", "designer", "user_researcher"]
        assert agents == expected
        
        # Test tool conversation  
        agents = self.flow._get_discovery_agents("tool")
        expected = ["orchestrator", "product_manager", "engineer", "solution_architect"]
        assert agents == expected
    
    def test_definition_agent_selection(self):
        """Test agent selection for definition phase."""
        
        # Test idea conversation
        agents = self.flow._get_definition_agents("idea")
        expected = ["orchestrator", "designer", "database", "engineer", "solution_architect"]
        assert agents == expected
        
        # Test feature conversation
        agents = self.flow._get_definition_agents("feature") 
        expected = ["orchestrator", "designer", "engineer", "database"]
        assert agents == expected
    
    def test_phase_transition_logic(self):
        """Test phase transition conditions."""
        
        # Test discovery to definition transition
        context = ConversationContext(
            conversation_id="test",
            conversation_type="feature",
            phase=ConversationPhase.DISCOVERY,
            agents_consulted=["orchestrator", "product_manager", "designer"],
            questions_answered=4,
            documents_generated=[]
        )
        
        assert self.flow._should_transition_to_definition(context) == True
        
        # Test definition to review transition
        context.phase = ConversationPhase.DEFINITION
        context.documents_generated = ["prd", "srs", "uxdd"]
        
        assert self.flow._should_transition_to_review(context) == True


class TestTaskDelegationIntegration:
    """Test task delegation pattern integration."""
    
    def setup_method(self):
        """Setup test environment."""
        self.delegation_manager = TaskDelegationManager()
        
    def test_agent_capability_mapping(self):
        """Test agent capability mappings from LangGraph."""
        
        # Test product manager capabilities
        pm_caps = self.delegation_manager.agent_capabilities["product_manager"]
        assert "business_requirements" in pm_caps.capabilities
        assert "prd_generation" in pm_caps.capabilities
        assert "user_researcher" in pm_caps.collaboration_partners
        
        # Test designer capabilities
        designer_caps = self.delegation_manager.agent_capabilities["designer"]
        assert "user_experience" in designer_caps.capabilities
        assert "uxdd_generation" in designer_caps.capabilities
        assert "product_manager" in designer_caps.collaboration_partners
    
    def test_delegation_suggestion_discovery_phase(self):
        """Test delegation suggestions for discovery phase."""
        
        conversation_context = {
            "phase": "discovery",
            "conversation_type": "feature",
            "agents_consulted": ["orchestrator"],
            "documents_generated": []
        }
        
        suggestion = self.delegation_manager.suggest_next_delegation(
            current_agent="orchestrator",
            conversation_context=conversation_context
        )
        
        assert suggestion is not None
        assert suggestion.target_agent == "product_manager"
        assert suggestion.reason == DelegationReason.EXPERTISE_NEEDED
        assert suggestion.collaboration_mode == True
    
    def test_delegation_suggestion_definition_phase(self):
        """Test delegation suggestions for definition phase."""
        
        conversation_context = {
            "phase": "definition", 
            "conversation_type": "feature",
            "agents_consulted": ["orchestrator", "product_manager"],
            "documents_generated": []
        }
        
        suggestion = self.delegation_manager.suggest_next_delegation(
            current_agent="product_manager",
            conversation_context=conversation_context
        )
        
        assert suggestion is not None
        assert suggestion.target_agent in ["designer", "engineer"]
        assert suggestion.reason == DelegationReason.EXPERTISE_NEEDED
        assert "prd" in suggestion.expected_deliverables or "uxdd" in suggestion.expected_deliverables
    
    def test_delegation_validation(self):
        """Test delegation validation logic."""
        
        # Valid delegation
        valid_delegation = TaskDelegationContext(
            source_agent="product_manager",
            target_agent="designer",
            reason=DelegationReason.EXPERTISE_NEEDED,
            urgency=DelegationUrgency.MEDIUM,
            context_summary="Need UX design",
            specific_request="Create wireframes",
            expected_deliverables=["wireframes"]
        )
        
        is_valid, message = self.delegation_manager.validate_delegation(valid_delegation)
        assert is_valid == True
        
        # Invalid self-delegation
        invalid_delegation = TaskDelegationContext(
            source_agent="product_manager",
            target_agent="product_manager",
            reason=DelegationReason.EXPERTISE_NEEDED,
            urgency=DelegationUrgency.MEDIUM,
            context_summary="Self delegation",
            specific_request="Do something",
            expected_deliverables=["something"]
        )
        
        is_valid, message = self.delegation_manager.validate_delegation(invalid_delegation)
        assert is_valid == False
        assert "Cannot delegate to self" in message
    
    def test_task_creation_with_delegation_context(self):
        """Test CrewAI task creation with delegation context."""
        
        delegation_context = TaskDelegationContext(
            source_agent="orchestrator",
            target_agent="product_manager",
            reason=DelegationReason.EXPERTISE_NEEDED,
            urgency=DelegationUrgency.HIGH,
            context_summary="Need business requirements analysis",
            specific_request="Define product requirements",
            expected_deliverables=["prd"]
        )
        
        conversation_context = {
            "conversation_type": "feature",
            "phase": "discovery",
            "key_requirements": ["user management", "data export"]
        }
        
        task = self.delegation_manager.create_delegated_task(
            delegation_context,
            "Define business requirements for new feature",
            conversation_context
        )
        
        assert task is not None
        assert "product requirements" in task.description.lower()
        assert "prd" in task.expected_output.lower()
        assert "orchestrator" in task.description
        assert "expertise_needed" in task.description


class TestCrewIntegration:
    """Test CrewAI crew integration patterns."""
    
    def setup_method(self):
        """Setup test environment."""
        self.project_crew = ProjectCrew()
        
    def test_crew_composition_for_conversation_types(self):
        """Test crew composition matches conversation requirements."""
        
        # Test feature crew
        feature_crew = self.project_crew.get_crew_for_project_type("feature")
        agent_types = [agent.role for agent in feature_crew.agents]
        
        expected_roles = [
            "Senior Project Orchestrator",
            "Senior Product Manager", 
            "Senior UX/UI Designer",
            "Senior Software Engineer",
            "Senior Quality Reviewer"
        ]
        
        for role in expected_roles:
            assert role in agent_types, f"Missing role: {role}"
    
    def test_custom_crew_creation(self):
        """Test custom crew creation for conversation flow."""
        
        # Test discovery crew creation
        agent_names = ["orchestrator", "product_manager", "user_researcher"]
        crew = self.project_crew.create_custom_crew(agent_names)
        
        assert len(crew.agents) == 3
        assert crew.process.name == "hierarchical"
        assert crew.manager_llm is not None
    
    def test_crew_agent_availability(self):
        """Test all required agents are available."""
        
        required_agents = [
            "orchestrator", "product_manager", "designer", "engineer",
            "database", "user_researcher", "business_analyst", 
            "solution_architect", "review"
        ]
        
        for agent_name in required_agents:
            assert agent_name in self.project_crew.agents
            assert self.project_crew.agents[agent_name] is not None


class TestEndToEndIntegration:
    """Test end-to-end conversation flow integration."""
    
    @pytest.mark.asyncio
    async def test_conversation_flow_mock_execution(self):
        """Test full conversation flow with mocked execution."""
        
        flow = CrewAIConversationFlow()
        
        # Mock crew execution to avoid actual LLM calls
        async def mock_crew_execution(crew, tasks, conversation_id):
            return {
                "analysis": "Project analysis completed",
                "requirements": "Business requirements defined",
                "prd": "Product Requirements Document generated"
            }
        
        with patch.object(flow, '_run_crew_with_flow_control', side_effect=mock_crew_execution):
            
            result = await flow.start_conversation(
                conversation_id="test_integration",
                user_input="Build a task management feature for teams",
                conversation_type="feature"
            )
            
            assert result["status"] in ["discovery_completed", "definition_completed", "completed"]
            assert "conversation_id" in result
            assert result["conversation_id"] == "test_integration"
    
    def test_handoff_pattern_preservation(self):
        """Test that LangGraph handoff patterns are preserved in CrewAI."""
        
        # Test that all handoff reasons are mapped
        langraph_reasons = [
            "expertise_needed", "task_complete", "collaboration_required",
            "user_request", "workflow_optimization", "parallel_work", "phase_transition"
        ]
        
        crewai_reasons = [reason.value for reason in DelegationReason]
        
        for reason in langraph_reasons:
            assert reason in crewai_reasons, f"Missing delegation reason: {reason}"
        
        # Test that agent capabilities cover LangGraph agent types
        langraph_agents = [
            "orchestrator", "product_manager", "designer", "engineer",
            "database", "user_researcher", "business_analyst", 
            "solution_architect", "review"
        ]
        
        crewai_agents = list(task_delegation_manager.agent_capabilities.keys())
        
        for agent in langraph_agents:
            assert agent in crewai_agents, f"Missing agent type: {agent}"


if __name__ == "__main__":
    """Run integration tests."""
    
    async def run_async_tests():
        """Run async tests."""
        
        print("🧪 Testing Conversation Flow Integration...")
        flow_test = TestConversationFlowIntegration()
        flow_test.setup_method()
        
        await flow_test.test_conversation_type_detection()
        print("✅ Conversation type detection works")
        
        flow_test.test_discovery_agent_selection()
        print("✅ Discovery agent selection works")
        
        flow_test.test_definition_agent_selection()
        print("✅ Definition agent selection works")
        
        flow_test.test_phase_transition_logic()
        print("✅ Phase transition logic works")
        
        print("\n🔧 Testing Task Delegation Integration...")
        delegation_test = TestTaskDelegationIntegration()
        delegation_test.setup_method()
        
        delegation_test.test_agent_capability_mapping()
        print("✅ Agent capability mapping works")
        
        delegation_test.test_delegation_suggestion_discovery_phase()
        print("✅ Discovery phase delegation works")
        
        delegation_test.test_delegation_suggestion_definition_phase()
        print("✅ Definition phase delegation works")
        
        delegation_test.test_delegation_validation()
        print("✅ Delegation validation works")
        
        delegation_test.test_task_creation_with_delegation_context()
        print("✅ Task creation with context works")
        
        print("\n⚙️ Testing Crew Integration...")
        crew_test = TestCrewIntegration()
        crew_test.setup_method()
        
        crew_test.test_crew_composition_for_conversation_types()
        print("✅ Crew composition works")
        
        crew_test.test_custom_crew_creation()
        print("✅ Custom crew creation works")
        
        crew_test.test_crew_agent_availability()
        print("✅ All agents available")
        
        print("\n🎯 Testing End-to-End Integration...")
        e2e_test = TestEndToEndIntegration()
        
        await e2e_test.test_conversation_flow_mock_execution()
        print("✅ End-to-end conversation flow works")
        
        e2e_test.test_handoff_pattern_preservation()
        print("✅ LangGraph handoff patterns preserved")
        
        print("\n🎉 All handoff pattern conversion tests passed!")
        print("✨ LangGraph to CrewAI conversion is working correctly")
    
    def run_sync_tests():
        """Run synchronous tests."""
        pass
    
    # Run tests
    asyncio.run(run_async_tests())
    run_sync_tests()