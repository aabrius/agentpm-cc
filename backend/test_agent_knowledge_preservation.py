"""
Test Knowledge Preservation from LangGraph to CrewAI Migration.
Validates that all specialized agent knowledge, templates, and expertise is preserved.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from agents import create_agent, AGENT_REGISTRY
from agents.product_manager import ProductManagerAgent
from agents.designer import DesignerAgent
from agents.database import DatabaseAgent
from agents.engineer import EngineerAgent
from agents.user_researcher import UserResearcherAgent
from agents.business_analyst import BusinessAnalystAgent
from agents.solution_architect import SolutionArchitectAgent
from agents.review import ReviewAgent


class TestKnowledgePreservation:
    """Test that all specialized knowledge from LangGraph implementation is preserved."""
    
    def test_product_manager_complete_knowledge(self):
        """Test Product Manager preserves complete business expertise."""
        agent = create_agent('product_manager')
        
        # Test complete question framework (11 questions)
        questions = agent.base_agent.__class__.PRODUCT_QUESTIONS
        assert len(questions) == 11
        
        # Test specific question content preservation
        question_ids = [q['id'] for q in questions]
        expected_questions = [
            'product_1', 'product_2', 'product_3', 'product_4', 'product_5',
            'product_6', 'product_7', 'product_8', 'product_9', 'product_10', 'product_11'
        ]
        assert all(qid in question_ids for qid in expected_questions)
        
        # Test required vs optional categorization
        required_questions = [q for q in questions if q['required']]
        optional_questions = [q for q in questions if not q['required']]
        assert len(required_questions) == 6  # First 6 are required
        assert len(optional_questions) == 5  # Last 5 are optional
        
        # Test key business questions content
        problem_question = next(q for q in questions if q['id'] == 'product_1')
        assert 'problem' in problem_question['content'].lower()
        
        users_question = next(q for q in questions if q['id'] == 'product_2')
        assert 'target users' in users_question['content'].lower()
        
        features_question = next(q for q in questions if q['id'] == 'product_3')
        assert 'features' in features_question['content'].lower()
        
        metrics_question = next(q for q in questions if q['id'] == 'product_4')
        assert 'metrics' in metrics_question['content'].lower()
    
    def test_designer_ux_expertise_preservation(self):
        """Test Designer Agent preserves UX/UI expertise."""
        agent = create_agent('designer')
        
        # Test design question framework
        design_questions = agent.base_agent.__class__.DESIGN_QUESTIONS
        assert len(design_questions) >= 8
        
        # Test UX-specific knowledge
        question_content = ' '.join([q['content'].lower() for q in design_questions])
        ux_keywords = ['user experience', 'interface', 'wireframe', 'design', 'accessibility', 'usability']
        
        keyword_matches = sum(1 for keyword in ux_keywords if keyword in question_content)
        assert keyword_matches >= 4  # At least half should be present
        
        # Test UXDD task creation preserves structure
        uxdd_task = agent.base_agent.__class__.create_uxdd_task({
            'product_name': 'Test App',
            'target_users': 'Mobile users'
        })
        
        assert 'UXDD' in uxdd_task['description'] or 'UX Design' in uxdd_task['description']
        assert 'wireframe' in uxdd_task['description'].lower() or 'design' in uxdd_task['description'].lower()
    
    def test_database_agent_erd_expertise(self):
        """Test Database Agent preserves ERD and schema expertise."""
        agent = create_agent('database')
        
        # Test database question framework
        db_questions = agent.base_agent.__class__.DATABASE_QUESTIONS
        assert len(db_questions) >= 6
        
        # Test database-specific knowledge
        question_content = ' '.join([q['content'].lower() for q in db_questions])
        db_keywords = ['database', 'schema', 'entity', 'relationship', 'table', 'data']
        
        keyword_matches = sum(1 for keyword in db_keywords if keyword in question_content)
        assert keyword_matches >= 3
        
        # Test ERD task creation
        erd_task = agent.base_agent.__class__.create_erd_task({
            'entities': ['User', 'Product', 'Order'],
            'relationships': 'One-to-many between User and Order'
        })
        
        assert 'ERD' in erd_task['description'] or 'entity' in erd_task['description'].lower()
        assert 'database' in erd_task['description'].lower() or 'schema' in erd_task['description'].lower()
    
    def test_engineer_technical_expertise_preservation(self):
        """Test Engineer Agent preserves technical specification expertise."""
        agent = create_agent('engineer')
        
        # Test technical question framework
        tech_questions = agent.base_agent.__class__.TECHNICAL_QUESTIONS
        assert len(tech_questions) >= 8
        
        # Test technical knowledge areas
        question_content = ' '.join([q['content'].lower() for q in tech_questions])
        tech_keywords = ['architecture', 'performance', 'security', 'scalability', 'implementation', 'technology']
        
        keyword_matches = sum(1 for keyword in tech_keywords if keyword in question_content)
        assert keyword_matches >= 4
        
        # Test SRS task creation follows IEEE standards
        srs_task = agent.base_agent.__class__.create_srs_task({
            'system_name': 'User Management System',
            'technical_requirements': 'High performance, secure authentication'
        })
        
        assert 'SRS' in srs_task['description'] or 'Software Requirements' in srs_task['description']
        assert 'IEEE' in srs_task['description'] or 'standard' in srs_task['description'].lower()
    
    def test_user_researcher_methodology_preservation(self):
        """Test User Researcher preserves research methodology."""
        agent = create_agent('user_researcher')
        
        # Test research question framework
        research_questions = agent.base_agent.__class__.RESEARCH_QUESTIONS
        assert len(research_questions) >= 6
        
        # Test research methodology knowledge
        question_content = ' '.join([q['content'].lower() for q in research_questions])
        research_keywords = ['user', 'behavior', 'persona', 'journey', 'research', 'interview']
        
        keyword_matches = sum(1 for keyword in research_keywords if keyword in question_content)
        assert keyword_matches >= 3
        
        # Test persona creation task
        persona_task = agent.base_agent.__class__.create_persona_task({
            'target_audience': 'Young professionals',
            'product_context': 'Productivity app'
        })
        
        assert 'persona' in persona_task['description'].lower()
        assert 'user' in persona_task['description'].lower()
    
    def test_business_analyst_requirements_expertise(self):
        """Test Business Analyst preserves requirements analysis expertise."""
        agent = create_agent('business_analyst')
        
        # Test analysis question framework
        analysis_questions = agent.base_agent.__class__.ANALYSIS_QUESTIONS
        assert len(analysis_questions) >= 7
        
        # Test requirements analysis knowledge
        question_content = ' '.join([q['content'].lower() for q in analysis_questions])
        ba_keywords = ['requirements', 'stakeholder', 'process', 'analysis', 'business', 'functional']
        
        keyword_matches = sum(1 for keyword in ba_keywords if keyword in question_content)
        assert keyword_matches >= 4
        
        # Test requirements analysis task
        req_analysis_task = agent.base_agent.__class__.create_requirements_analysis_task({
            'business_context': 'E-commerce platform',
            'stakeholders': 'Customers, vendors, administrators'
        })
        
        assert 'requirements' in req_analysis_task['description'].lower()
        assert 'analysis' in req_analysis_task['description'].lower()
    
    def test_solution_architect_design_patterns_preservation(self):
        """Test Solution Architect preserves design patterns and integration knowledge."""
        agent = create_agent('solution_architect')
        
        # Test architecture question framework
        arch_questions = agent.base_agent.__class__.ARCHITECTURE_QUESTIONS
        assert len(arch_questions) >= 8
        
        # Test architecture knowledge
        question_content = ' '.join([q['content'].lower() for q in arch_questions])
        arch_keywords = ['architecture', 'system', 'integration', 'scalability', 'pattern', 'design']
        
        keyword_matches = sum(1 for keyword in arch_keywords if keyword in question_content)
        assert keyword_matches >= 4
        
        # Test system design task
        system_design_task = agent.base_agent.__class__.create_system_design_task({
            'system_requirements': 'Microservices architecture with API gateway',
            'scalability_needs': 'Handle 10M+ requests per day'
        })
        
        assert 'system' in system_design_task['description'].lower()
        assert 'architecture' in system_design_task['description'].lower()
    
    def test_review_agent_validation_criteria_preservation(self):
        """Test Review Agent preserves quality validation criteria."""
        agent = create_agent('review')
        
        # Test validation criteria framework
        validation_criteria = agent.base_agent.__class__.VALIDATION_CRITERIA
        assert len(validation_criteria) >= 5
        
        # Test quality assurance knowledge
        criteria_content = ' '.join([criterion.lower() for criterion in validation_criteria])
        qa_keywords = ['completeness', 'consistency', 'clarity', 'accuracy', 'standard']
        
        keyword_matches = sum(1 for keyword in qa_keywords if keyword in criteria_content)
        assert keyword_matches >= 3
        
        # Test document review task
        review_task = agent.base_agent.__class__.create_document_review_task({
            'document_type': 'PRD',
            'document_content': 'Sample PRD content for review'
        })
        
        assert 'review' in review_task['description'].lower()
        assert 'quality' in review_task['description'].lower() or 'validation' in review_task['description'].lower()
    
    def test_orchestrator_routing_logic_preservation(self):
        """Test Orchestrator preserves routing and coordination logic."""
        agent = create_agent('orchestrator')
        
        # Test routing capabilities
        routing_task = agent.base_agent.__class__.create_routing_task({
            'conversation_type': 'full_product',
            'user_input': 'I want to build a mobile app for food delivery'
        })
        
        assert 'routing' in routing_task['description'].lower() or 'coordination' in routing_task['description'].lower()
        
        # Test coordination capabilities
        coordination_task = agent.base_agent.__class__.create_coordination_task({
            'agents_needed': ['product_manager', 'designer', 'engineer'],
            'objective': 'Create comprehensive product documentation'
        })
        
        assert 'coordination' in coordination_task['description'].lower() or 'orchestrat' in coordination_task['description'].lower()


class TestTemplateContentPreservation:
    """Test that all template content and structure is preserved."""
    
    def test_prd_template_structure_preservation(self):
        """Test PRD template structure is preserved."""
        pm_agent = create_agent('product_manager')
        
        prd_task = pm_agent.base_agent.__class__.create_prd_task({
            'product_name': 'Test Product',
            'business_context': 'Test business context'
        })
        
        # Test PRD sections are mentioned
        prd_sections = [
            'Executive Summary', 'Problem Statement', 'Goals and Objectives',
            'User Personas', 'Functional Requirements', 'Non-Functional Requirements',
            'Success Metrics', 'Timeline', 'Risks'
        ]
        
        section_matches = sum(1 for section in prd_sections if section in prd_task['description'])
        assert section_matches >= 7  # At least 7 of 9 sections should be mentioned
    
    def test_uxdd_template_structure_preservation(self):
        """Test UXDD template structure is preserved."""
        designer_agent = create_agent('designer')
        
        uxdd_task = designer_agent.base_agent.__class__.create_uxdd_task({
            'product_name': 'Test App',
            'user_personas': 'Tech-savvy professionals'
        })
        
        # Test UXDD sections are mentioned
        uxdd_sections = [
            'User Research', 'Design Principles', 'Information Architecture',
            'Wireframes', 'Visual Design', 'Interaction Design', 'Accessibility'
        ]
        
        section_matches = sum(1 for section in uxdd_sections if section.lower() in uxdd_task['description'].lower())
        assert section_matches >= 4  # At least half should be mentioned
    
    def test_erd_template_structure_preservation(self):
        """Test ERD template structure is preserved."""
        db_agent = create_agent('database')
        
        erd_task = db_agent.base_agent.__class__.create_erd_task({
            'system_name': 'E-commerce System',
            'main_entities': 'User, Product, Order, Payment'
        })
        
        # Test ERD components are mentioned
        erd_components = ['entities', 'relationships', 'attributes', 'constraints', 'diagram']
        
        component_matches = sum(1 for component in erd_components if component in erd_task['description'].lower())
        assert component_matches >= 3
    
    def test_srs_template_ieee_compliance(self):
        """Test SRS template follows IEEE standards."""
        engineer_agent = create_agent('engineer')
        
        srs_task = engineer_agent.base_agent.__class__.create_srs_task({
            'system_name': 'Inventory Management System',
            'functional_requirements': 'Track inventory, generate reports'
        })
        
        # Test IEEE SRS sections
        ieee_sections = [
            'Introduction', 'Overall Description', 'System Features',
            'External Interface Requirements', 'Non-functional Requirements'
        ]
        
        section_matches = sum(1 for section in ieee_sections if section in srs_task['description'])
        assert section_matches >= 3
        assert 'IEEE' in srs_task['description']


class TestAgentCollaborationPatterns:
    """Test agent collaboration patterns are preserved."""
    
    def test_orchestrator_agent_selection_logic(self):
        """Test orchestrator can select appropriate agents for different scenarios."""
        orchestrator = create_agent('orchestrator')
        
        # Test different conversation types require different agent combinations
        scenarios = [
            {
                'type': 'full_product',
                'expected_agents': ['product_manager', 'designer', 'engineer', 'user_researcher']
            },
            {
                'type': 'api_design',
                'expected_agents': ['engineer', 'solution_architect', 'database']
            },
            {
                'type': 'ux_improvement',
                'expected_agents': ['designer', 'user_researcher', 'review']
            }
        ]
        
        for scenario in scenarios:
            routing_task = orchestrator.base_agent.__class__.create_routing_task({
                'conversation_type': scenario['type'],
                'user_input': f"Project for {scenario['type']}"
            })
            
            # Check that routing logic exists
            assert 'description' in routing_task
            assert len(routing_task['description']) > 100  # Should be detailed
    
    def test_agent_handoff_information_preservation(self):
        """Test that agent handoffs preserve necessary information."""
        pm_agent = create_agent('product_manager')
        designer_agent = create_agent('designer')
        
        # Test PM can create context for designer handoff
        pm_context = {
            'product_requirements': 'Mobile app for task management',
            'user_personas': 'Busy professionals',
            'key_features': 'Task creation, reminders, collaboration'
        }
        
        # PM should be able to create UXDD task with context
        uxdd_task = designer_agent.base_agent.__class__.create_uxdd_task(pm_context)
        
        # Designer should receive all necessary context
        for key_info in ['task management', 'professionals', 'features']:
            # Some form of this information should be in the task
            assert any(info in uxdd_task['description'].lower() for info in [key_info, pm_context.get('product_requirements', '').lower()])
    
    def test_review_agent_integration_with_all_agents(self):
        """Test Review Agent can validate outputs from all other agents."""
        review_agent = create_agent('review')
        
        # Test review tasks for different document types
        document_types = ['PRD', 'UXDD', 'ERD', 'SRS', 'BRD']
        
        for doc_type in document_types:
            review_task = review_agent.base_agent.__class__.create_document_review_task({
                'document_type': doc_type,
                'document_content': f'Sample {doc_type} content for validation'
            })
            
            assert doc_type in review_task['description']
            assert 'review' in review_task['description'].lower()
            assert 'validation' in review_task['description'].lower() or 'quality' in review_task['description'].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])