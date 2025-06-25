"""
Product Manager Agent for CrewAI implementation.
Creates comprehensive PRD and BRD documents with business focus.
"""

from crewai import Agent
from typing import Dict, Any, List
from ..tools.prd_generator import PRDGeneratorTool
from ..tools.brd_generator import BRDGeneratorTool
from ..tools.market_analyzer import MarketAnalyzerTool
from ..tools.stakeholder_mapper import StakeholderMapperTool
from ..tools.requirements_gatherer import RequirementsGathererTool
from ..tools.rag_search import RAGSearchTool
from ..tools.document_indexer import DocumentIndexerTool
from ..config import get_llm_model
from .base_observability import ObservableAgentMixin
from ..prompts.enhanced_product_manager_prompt import ENHANCED_PRODUCT_MANAGER_PROMPT, ENHANCED_PRD_GENERATION_PROMPT


class ProductManagerAgent:
    """Creates and configures the Product Manager agent for requirements documentation."""
    
    # Preserved question framework from original implementation
    PRODUCT_QUESTIONS = [
        {
            "id": "product_1",
            "content": "What problem does this product solve?",
            "required": True
        },
        {
            "id": "product_2",
            "content": "Who are the target users?",
            "required": True
        },
        {
            "id": "product_3",
            "content": "What are the key features and functionalities?",
            "required": True
        },
        {
            "id": "product_4",
            "content": "What are the success metrics?",
            "required": True
        },
        {
            "id": "product_5",
            "content": "What is the business model or value proposition?",
            "required": True
        },
        {
            "id": "product_6",
            "content": "What are the main user journeys?",
            "required": True
        },
        {
            "id": "product_7",
            "content": "What are the technical constraints or requirements?",
            "required": False
        },
        {
            "id": "product_8",
            "content": "What is the project timeline?",
            "required": False
        },
        {
            "id": "product_9",
            "content": "What are the budget constraints?",
            "required": False
        },
        {
            "id": "product_10",
            "content": "Who are the key stakeholders?",
            "required": False
        },
        {
            "id": "product_11",
            "content": "What are the main risks and mitigation strategies?",
            "required": False
        }
    ]
    
    @staticmethod
    def create(model_override: str = None) -> Agent:
        """Create the Product Manager agent with full capabilities."""
        base_agent = Agent(
            role='Senior Principal Product Manager',
            goal='''Create investor-grade PRD and BRD documents that not only capture 
            requirements but provide strategic blueprints for market dominance. Conduct 
            exhaustive analysis of problems, markets, users, and business models. Ensure 
            documents can guide product development for 6+ months without clarification.''',
            backstory=ENHANCED_PRODUCT_MANAGER_PROMPT,
            tools=[
                PRDGeneratorTool(),
                BRDGeneratorTool(),
                MarketAnalyzerTool(),
                StakeholderMapperTool(),
                RequirementsGathererTool(),
                RAGSearchTool(),
                DocumentIndexerTool()
            ],
            llm=get_llm_model('product_manager', override_model=model_override),
            verbose=True,
            max_iter=15,
            memory=False
        )
        
        # Create observable wrapper
        class ObservableProductManagerAgent(ObservableAgentMixin):
            def __init__(self, base_agent: Agent):
                super().__init__()
                self.base_agent = base_agent
                self.role = base_agent.role
                self.agent_id = 'product_manager'
            
            def __getattr__(self, name):
                return getattr(self.base_agent, name)
        
        return ObservableProductManagerAgent(base_agent)
    
    @staticmethod
    def create_prd_task(project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for generating a Product Requirements Document."""
        return {
            "description": ENHANCED_PRD_GENERATION_PROMPT.format(
                project_context=project_context
            ),
            "expected_output": """An investor-grade PRD document (4000-6000 words) that:
            - Tells a compelling product story from problem to solution to impact
            - Includes comprehensive market analysis with TAM/SAM/SOM
            - Details 3-5 user personas with deep behavioral insights
            - Provides exhaustive functional requirements with edge cases
            - Specifies non-functional requirements with measurable criteria
            - Includes detailed success metrics with leading/lagging indicators
            - Contains risk analysis with mitigation strategies
            - Provides phased implementation roadmap
            - Includes competitive analysis and differentiation strategy
            - Contains API specifications and integration requirements
            - Addresses security, compliance, and data requirements
            
            The document should be sufficient to guide engineering for 6+ months
            without requiring clarification meetings."""
        }
    
    @staticmethod
    def create_brd_task(project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for generating a Business Requirements Document."""
        return {
            "description": f"""Create a comprehensive Business Requirements Document (BRD) 
            based on the following project context:
            
            {project_context}
            
            The BRD should include:
            1. Executive Summary
            2. Business Objectives and Success Criteria
            3. Stakeholder Analysis
            4. Current State Analysis
            5. Future State Vision
            6. Gap Analysis
            7. Business Requirements (Functional and Non-Functional)
            8. Constraints and Assumptions
            9. Risk Analysis
            10. Cost-Benefit Analysis
            11. Implementation Roadmap
            
            Focus on the business perspective, ensuring alignment with organizational 
            goals and stakeholder needs.""",
            "expected_output": """A complete BRD document (2500-3500 words) that clearly 
            articulates the business need, objectives, and requirements. The document 
            should facilitate decision-making and provide a clear business case for 
            the project."""
        }
    
    @staticmethod
    def create_requirements_gathering_task(user_input: str) -> Dict[str, Any]:
        """Create a task for gathering requirements through structured questions."""
        return {
            "description": f"""Analyze the user input and gather comprehensive product 
            requirements using our structured question framework:
            
            User Input: {user_input}
            
            Extract or infer answers to our 11 product questions, identifying any gaps 
            that need clarification. For missing information, provide reasonable 
            assumptions based on industry best practices and the context provided.""",
            "expected_output": """A structured requirements analysis containing:
            - Answers to all 11 product questions (with confidence levels)
            - Identified gaps and assumptions made
            - Additional requirements discovered
            - Recommendations for further clarification"""
        }
    
    @staticmethod
    def create_stakeholder_analysis_task(project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for comprehensive stakeholder analysis."""
        return {
            "description": f"""Conduct a thorough stakeholder analysis for the project:
            
            {project_context}
            
            Identify all stakeholders, their roles, interests, influence levels, and 
            communication needs. Consider both internal and external stakeholders.""",
            "expected_output": """A detailed stakeholder analysis including:
            - Stakeholder identification and categorization
            - Influence/Interest matrix
            - Communication plan for each stakeholder group
            - Potential conflicts and resolution strategies
            - Engagement timeline and touchpoints"""
        }
    
    @staticmethod
    def validate_requirements_completeness(requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all required questions have been answered."""
        missing_required = []
        completeness_score = 0
        total_required = 0
        
        for question in ProductManagerAgent.PRODUCT_QUESTIONS:
            if question["required"]:
                total_required += 1
                if question["id"] not in requirements or not requirements[question["id"]]:
                    missing_required.append(question["content"])
                else:
                    completeness_score += 1
        
        return {
            "is_complete": len(missing_required) == 0,
            "completeness_percentage": (completeness_score / total_required) * 100 if total_required > 0 else 0,
            "missing_required": missing_required,
            "total_required": total_required,
            "total_answered": completeness_score
        }