"""
Comprehensive test suite for all 9 specialized agents in CrewAI framework.
Tests agent behaviors, knowledge preservation, and document generation capabilities.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List

from agents import (
    OrchestratorAgent, ProductManagerAgent, DesignerAgent, 
    DatabaseAgent, EngineerAgent, UserResearcherAgent,
    BusinessAnalystAgent, SolutionArchitectAgent, ReviewAgent,
    create_agent, get_agent
)
from agents.base_observability import ObservableAgentMixin
from tools.prd_generator import PRDGeneratorTool
from tools.rag_search import RAGSearchTool
from config import get_llm_model


class TestSpecializedAgentBehaviors:
    """Test all 9 specialized agents in the CrewAI framework."""
    
    def test_agent_registry_completeness(self):
        """Test that all 9 agents are properly registered."""
        from agents import AGENT_REGISTRY
        
        expected_agents = [
            'orchestrator', 'product_manager', 'designer', 'database',
            'engineer', 'user_researcher', 'business_analyst', 
            'solution_architect', 'review'
        ]
        
        assert len(AGENT_REGISTRY) == 9
        for agent_type in expected_agents:
            assert agent_type in AGENT_REGISTRY
            assert AGENT_REGISTRY[agent_type] is not None
    
    def test_agent_creation_with_observability(self):
        """Test that all agents can be created with observability."""
        agent_types = [
            'orchestrator', 'product_manager', 'designer', 'database',
            'engineer', 'user_researcher', 'business_analyst', 
            'solution_architect', 'review'
        ]
        
        for agent_type in agent_types:
            agent = create_agent(agent_type, with_observability=True)
            assert agent is not None
            assert isinstance(agent, ObservableAgentMixin)
            assert hasattr(agent, 'agent_id')
            assert hasattr(agent, 'set_observability_context')
    
    def test_orchestrator_agent_creation(self):
        """Test Orchestrator Agent creation and properties."""
        agent = create_agent('orchestrator')
        
        assert agent is not None
        assert agent.agent_id == 'orchestrator'
        assert hasattr(agent, 'role')
        assert 'orchestrator' in agent.role.lower() or 'manager' in agent.role.lower()
        
        # Test task creation methods
        assert hasattr(agent.base_agent.__class__, 'create_routing_task')
        assert hasattr(agent.base_agent.__class__, 'create_coordination_task')
    
    def test_product_manager_agent_knowledge_preservation(self):
        """Test Product Manager Agent preserves original knowledge."""
        agent = create_agent('product_manager')
        
        # Test preserved question framework
        assert hasattr(agent.base_agent.__class__, 'PRODUCT_QUESTIONS')
        questions = agent.base_agent.__class__.PRODUCT_QUESTIONS
        assert len(questions) == 11
        assert all('id' in q and 'content' in q and 'required' in q for q in questions)
        
        # Test required questions
        required_questions = [q for q in questions if q['required']]
        assert len(required_questions) >= 5
        
        # Test specific preserved capabilities
        assert hasattr(agent.base_agent.__class__, 'create_prd_task')
        assert hasattr(agent.base_agent.__class__, 'create_brd_task')
        assert hasattr(agent.base_agent.__class__, 'validate_requirements_completeness')
    
    def test_designer_agent_capabilities(self):
        """Test Designer Agent UX/UI capabilities."""
        agent = create_agent('designer')
        
        assert agent.agent_id == 'designer'
        assert 'ux' in agent.role.lower() or 'design' in agent.role.lower()
        
        # Test preserved design knowledge
        assert hasattr(agent.base_agent.__class__, 'DESIGN_QUESTIONS')
        design_questions = agent.base_agent.__class__.DESIGN_QUESTIONS
        assert len(design_questions) >= 8
        
        # Test design task creation
        assert hasattr(agent.base_agent.__class__, 'create_uxdd_task')
        assert hasattr(agent.base_agent.__class__, 'create_wireframe_task')
    
    def test_database_agent_erd_capabilities(self):
        """Test Database Agent ERD generation capabilities."""
        agent = create_agent('database')
        
        assert agent.agent_id == 'database'
        assert 'database' in agent.role.lower() or 'data' in agent.role.lower()
        
        # Test preserved database expertise
        assert hasattr(agent.base_agent.__class__, 'DATABASE_QUESTIONS')
        db_questions = agent.base_agent.__class__.DATABASE_QUESTIONS
        assert len(db_questions) >= 6
        
        # Test ERD task creation
        assert hasattr(agent.base_agent.__class__, 'create_erd_task')
        assert hasattr(agent.base_agent.__class__, 'create_dbrd_task')
    
    def test_engineer_agent_technical_expertise(self):
        """Test Engineer Agent technical specification capabilities."""
        agent = create_agent('engineer')
        
        assert agent.agent_id == 'engineer'
        assert 'engineer' in agent.role.lower() or 'technical' in agent.role.lower()
        
        # Test preserved engineering knowledge
        assert hasattr(agent.base_agent.__class__, 'TECHNICAL_QUESTIONS')
        tech_questions = agent.base_agent.__class__.TECHNICAL_QUESTIONS
        assert len(tech_questions) >= 8
        
        # Test SRS task creation
        assert hasattr(agent.base_agent.__class__, 'create_srs_task')
        assert hasattr(agent.base_agent.__class__, 'create_architecture_task')
    
    def test_user_researcher_persona_expertise(self):
        """Test User Researcher Agent persona and journey mapping."""
        agent = create_agent('user_researcher')
        
        assert agent.agent_id == 'user_researcher'
        assert 'research' in agent.role.lower() or 'user' in agent.role.lower()
        
        # Test preserved research methodology
        assert hasattr(agent.base_agent.__class__, 'RESEARCH_QUESTIONS')
        research_questions = agent.base_agent.__class__.RESEARCH_QUESTIONS
        assert len(research_questions) >= 6
        
        # Test persona and journey mapping
        assert hasattr(agent.base_agent.__class__, 'create_persona_task')
        assert hasattr(agent.base_agent.__class__, 'create_journey_mapping_task')
    
    def test_business_analyst_srs_capabilities(self):
        """Test Business Analyst Agent SRS and requirements expertise."""
        agent = create_agent('business_analyst')
        
        assert agent.agent_id == 'business_analyst'
        assert 'analyst' in agent.role.lower() or 'business' in agent.role.lower()
        
        # Test preserved analysis framework
        assert hasattr(agent.base_agent.__class__, 'ANALYSIS_QUESTIONS')
        analysis_questions = agent.base_agent.__class__.ANALYSIS_QUESTIONS
        assert len(analysis_questions) >= 7
        
        # Test requirements analysis
        assert hasattr(agent.base_agent.__class__, 'create_requirements_analysis_task')
        assert hasattr(agent.base_agent.__class__, 'create_stakeholder_analysis_task')
    
    def test_solution_architect_design_patterns(self):
        """Test Solution Architect Agent design patterns and integration."""
        agent = create_agent('solution_architect')
        
        assert agent.agent_id == 'solution_architect'
        assert 'architect' in agent.role.lower() or 'solution' in agent.role.lower()
        
        # Test preserved architecture knowledge
        assert hasattr(agent.base_agent.__class__, 'ARCHITECTURE_QUESTIONS')
        arch_questions = agent.base_agent.__class__.ARCHITECTURE_QUESTIONS
        assert len(arch_questions) >= 8
        
        # Test architecture design tasks
        assert hasattr(agent.base_agent.__class__, 'create_system_design_task')
        assert hasattr(agent.base_agent.__class__, 'create_integration_task')
    
    def test_review_agent_validation_criteria(self):
        """Test Review Agent quality assurance and validation."""
        agent = create_agent('review')
        
        assert agent.agent_id == 'review'
        assert 'review' in agent.role.lower() or 'quality' in agent.role.lower()
        
        # Test preserved validation framework
        assert hasattr(agent.base_agent.__class__, 'VALIDATION_CRITERIA')
        validation_criteria = agent.base_agent.__class__.VALIDATION_CRITERIA
        assert len(validation_criteria) >= 5
        
        # Test quality assurance methods
        assert hasattr(agent.base_agent.__class__, 'create_document_review_task')
        assert hasattr(agent.base_agent.__class__, 'validate_completeness')
    
    def test_agent_tool_integration(self):
        """Test that agents have proper tool integration."""
        # Product Manager should have PRD and BRD tools
        pm_agent = create_agent('product_manager')
        pm_tools = pm_agent.base_agent.tools
        tool_names = [tool.__class__.__name__ for tool in pm_tools]
        
        assert 'PRDGeneratorTool' in tool_names
        assert 'BRDGeneratorTool' in tool_names
        assert 'RAGSearchTool' in tool_names
        
        # Designer should have UXDD and wireframe tools
        designer_agent = create_agent('designer')
        designer_tools = designer_agent.base_agent.tools
        designer_tool_names = [tool.__class__.__name__ for tool in designer_tools]
        
        assert 'UXDDGeneratorTool' in designer_tool_names
        assert 'WireframeGeneratorTool' in designer_tool_names
    
    def test_agent_llm_configuration(self):
        """Test that agents have proper LLM configuration."""
        test_agents = ['orchestrator', 'product_manager', 'designer']
        
        for agent_type in test_agents:
            agent = create_agent(agent_type)
            assert hasattr(agent.base_agent, 'llm')
            assert agent.base_agent.llm is not None
    
    @patch('tools.prd_generator.PRDGeneratorTool.generate_prd')
    def test_document_generation_integration(self, mock_prd_gen):
        """Test document generation through agents."""
        mock_prd_gen.return_value = {
            'content': 'Mock PRD content',
            'metadata': {'word_count': 2500, 'quality_score': 0.85}
        }
        
        agent = create_agent('product_manager')
        
        # Test PRD task creation
        project_context = {
            'product_name': 'Test Product',
            'problem_statement': 'Test problem',
            'target_users': 'Test users'
        }
        
        prd_task = agent.base_agent.__class__.create_prd_task(project_context)
        
        assert 'description' in prd_task
        assert 'expected_output' in prd_task
        assert 'PRD' in prd_task['description']
        assert 'Executive Summary' in prd_task['description']
    
    def test_question_framework_completeness(self):
        """Test that all agents have complete question frameworks."""
        question_frameworks = [
            ('product_manager', 'PRODUCT_QUESTIONS', 11),
            ('designer', 'DESIGN_QUESTIONS', 8),
            ('database', 'DATABASE_QUESTIONS', 6),
            ('engineer', 'TECHNICAL_QUESTIONS', 8),
            ('user_researcher', 'RESEARCH_QUESTIONS', 6),
            ('business_analyst', 'ANALYSIS_QUESTIONS', 7),
            ('solution_architect', 'ARCHITECTURE_QUESTIONS', 8)
        ]
        
        for agent_type, attr_name, expected_count in question_frameworks:
            agent = create_agent(agent_type)
            assert hasattr(agent.base_agent.__class__, attr_name)
            
            questions = getattr(agent.base_agent.__class__, attr_name)
            assert len(questions) >= expected_count
            
            # Validate question structure
            for question in questions:
                assert 'id' in question
                assert 'content' in question
                assert 'required' in question
                assert isinstance(question['required'], bool)
    
    def test_agent_memory_and_iteration_settings(self):
        """Test that agents have proper memory and iteration configuration."""
        test_agents = ['product_manager', 'designer', 'engineer']
        
        for agent_type in test_agents:
            agent = create_agent(agent_type)
            
            # Test memory is enabled
            assert hasattr(agent.base_agent, 'memory')
            assert agent.base_agent.memory == True
            
            # Test iteration limits
            assert hasattr(agent.base_agent, 'max_iter')
            assert agent.base_agent.max_iter >= 3
    
    def test_agent_collaboration_capabilities(self):
        """Test agent collaboration and handoff capabilities."""
        orchestrator = create_agent('orchestrator')
        product_manager = create_agent('product_manager')
        
        # Test orchestrator can create coordination tasks
        coordination_task = orchestrator.base_agent.__class__.create_coordination_task({
            'agents': ['product_manager', 'designer'],
            'objective': 'Create comprehensive product documentation'
        })
        
        assert 'description' in coordination_task
        assert 'expected_output' in coordination_task
        
        # Test product manager can create collaborative tasks
        pm_stakeholder_task = product_manager.base_agent.__class__.create_stakeholder_analysis_task({
            'project_name': 'Test Project',
            'business_context': 'Test business context'
        })
        
        assert 'description' in pm_stakeholder_task
        assert 'stakeholder' in pm_stakeholder_task['description'].lower()
    
    def test_error_handling_in_agent_creation(self):
        """Test error handling for invalid agent types."""
        with pytest.raises(ValueError):
            create_agent('invalid_agent_type')
        
        # Test graceful handling of missing tools
        with patch('agents.product_manager.PRDGeneratorTool', side_effect=ImportError):
            # Should still create agent but with reduced functionality
            try:
                agent = create_agent('product_manager')
                assert agent is not None
            except ImportError:
                # Expected if tool initialization fails
                pass
    
    def test_agent_backstory_preservation(self):
        """Test that agent backstories preserve original expertise."""
        expertise_keywords = {
            'product_manager': ['product', 'business', 'stakeholder', 'requirements'],
            'designer': ['design', 'user experience', 'wireframe', 'accessibility'],
            'database': ['database', 'schema', 'entity', 'normalization'],
            'engineer': ['technical', 'architecture', 'software', 'implementation'],
            'user_researcher': ['research', 'persona', 'journey', 'behavior'],
            'business_analyst': ['analysis', 'requirements', 'process', 'stakeholder'],
            'solution_architect': ['architecture', 'system', 'integration', 'scalability'],
            'review': ['quality', 'validation', 'review', 'standards']
        }
        
        for agent_type, keywords in expertise_keywords.items():
            agent = create_agent(agent_type)
            backstory = agent.base_agent.backstory.lower()
            
            # At least half of the keywords should be present
            keyword_matches = sum(1 for keyword in keywords if keyword in backstory)
            assert keyword_matches >= len(keywords) // 2, f"Agent {agent_type} missing key expertise keywords"
    
    def test_agent_goal_clarity(self):
        """Test that agent goals are clear and specific."""
        test_agents = ['product_manager', 'designer', 'engineer', 'review']
        
        for agent_type in test_agents:
            agent = create_agent(agent_type)
            goal = agent.base_agent.goal.lower()
            
            # Goals should mention specific deliverables
            assert len(goal) > 50, f"Agent {agent_type} goal too brief"
            assert any(word in goal for word in ['create', 'generate', 'develop', 'analyze']), \
                f"Agent {agent_type} goal lacks action words"
    
    def test_requirements_validation_methods(self):
        """Test requirements validation across agents."""
        # Test Product Manager validation
        pm_agent = create_agent('product_manager')
        
        # Mock requirements data
        complete_requirements = {f"product_{i}": f"Answer {i}" for i in range(1, 12)}
        incomplete_requirements = {f"product_{i}": f"Answer {i}" for i in range(1, 4)}
        
        # Test complete requirements
        validation_result = pm_agent.base_agent.__class__.validate_requirements_completeness(complete_requirements)
        assert validation_result['is_complete'] == True
        assert validation_result['completeness_percentage'] == 100
        
        # Test incomplete requirements
        validation_result = pm_agent.base_agent.__class__.validate_requirements_completeness(incomplete_requirements)
        assert validation_result['is_complete'] == False
        assert validation_result['completeness_percentage'] < 100
        assert len(validation_result['missing_required']) > 0


class TestAgentIntegrationScenarios:
    """Test realistic agent integration scenarios."""
    
    def test_full_product_development_scenario(self):
        """Test a complete product development workflow."""
        # Create all agents
        orchestrator = create_agent('orchestrator')
        pm = create_agent('product_manager')
        designer = create_agent('designer')
        engineer = create_agent('engineer')
        
        # Test workflow creation
        project_context = {
            'product_name': 'AI-Powered Task Manager',
            'target_users': 'Knowledge workers and teams',
            'business_objective': 'Increase productivity by 30%'
        }
        
        # Test orchestrator can create coordination tasks
        coordination_task = orchestrator.base_agent.__class__.create_coordination_task(project_context)
        assert 'description' in coordination_task
        
        # Test each agent can create relevant tasks
        prd_task = pm.base_agent.__class__.create_prd_task(project_context)
        uxdd_task = designer.base_agent.__class__.create_uxdd_task(project_context)
        srs_task = engineer.base_agent.__class__.create_srs_task(project_context)
        
        assert all('description' in task for task in [prd_task, uxdd_task, srs_task])
    
    def test_api_development_scenario(self):
        """Test API development specific workflow."""
        engineer = create_agent('engineer')
        db_agent = create_agent('database')
        architect = create_agent('solution_architect')
        
        api_context = {
            'api_type': 'REST API for user management',
            'endpoints': ['users', 'authentication', 'profiles'],
            'data_requirements': 'User data, sessions, preferences'
        }
        
        # Test API-specific task creation
        api_task = engineer.base_agent.__class__.create_api_specification_task(api_context)
        erd_task = db_agent.base_agent.__class__.create_erd_task(api_context)
        integration_task = architect.base_agent.__class__.create_integration_task(api_context)
        
        assert 'api' in api_task['description'].lower()
        assert 'database' in erd_task['description'].lower() or 'erd' in erd_task['description'].lower()
        assert 'integration' in integration_task['description'].lower()
    
    def test_mobile_app_scenario(self):
        """Test mobile app development workflow."""
        designer = create_agent('designer')
        researcher = create_agent('user_researcher')
        pm = create_agent('product_manager')
        
        mobile_context = {
            'platform': 'iOS and Android',
            'app_type': 'Social networking app',
            'target_audience': 'Young professionals aged 25-35'
        }
        
        # Test mobile-specific tasks
        wireframe_task = designer.base_agent.__class__.create_wireframe_task(mobile_context)
        persona_task = researcher.base_agent.__class__.create_persona_task(mobile_context)
        brd_task = pm.base_agent.__class__.create_brd_task(mobile_context)
        
        assert any(word in wireframe_task['description'].lower() for word in ['wireframe', 'mockup', 'interface'])
        assert 'persona' in persona_task['description'].lower()
        assert 'business' in brd_task['description'].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])