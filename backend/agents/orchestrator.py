"""
Orchestrator Agent for CrewAI implementation.
Manages project intent analysis and agent coordination.
"""

from crewai import Agent
from typing import Dict, Any, List
from ..tools.intent_analyzer import IntentAnalyzerTool
from ..tools.project_classifier import ProjectClassifierTool
from ..tools.requirements_mapper import RequirementsMapperTool
from ..tools.rag_search import RAGSearchTool
from ..tools.document_indexer import DocumentIndexerTool
from ..tools.knowledge_synthesizer import KnowledgeSynthesizerTool
from ..config import get_llm_model
from .base_observability import ObservableAgentMixin
from ..prompts.enhanced_orchestrator_prompt import ENHANCED_ORCHESTRATOR_PROMPT, ENHANCED_ANALYSIS_TASK_PROMPT


class OrchestratorAgent(ObservableAgentMixin):
    """Creates and configures the Orchestrator agent with observability."""
    
    @staticmethod
    def create(model_override: str = None) -> Agent:
        """Create the Orchestrator agent with full capabilities."""
        base_agent = Agent(
            role='Senior Project Orchestration Manager',
            goal='''Conduct exhaustive, quality-first analysis of every project request. 
            Analyze from multiple perspectives, identify hidden requirements, and ensure 
            comprehensive documentation coverage. Leave no stone unturned in understanding 
            the full scope and implications of each project.''',
            backstory=ENHANCED_ORCHESTRATOR_PROMPT,
            tools=[
                IntentAnalyzerTool(),
                ProjectClassifierTool(),
                RequirementsMapperTool(),
                RAGSearchTool(),
                KnowledgeSynthesizerTool(),
                DocumentIndexerTool()
            ],
            llm=get_llm_model('orchestrator', override_model=model_override),
            verbose=True,
            allow_delegation=True,
            max_iter=15,  # Increased for quality
            memory=False  # Disabled for quality focus
        )
        
        # Create observable wrapper
        class ObservableOrchestratorAgent(ObservableAgentMixin):
            def __init__(self, base_agent: Agent):
                super().__init__()
                self.base_agent = base_agent
                self.role = base_agent.role
                self.agent_id = 'orchestrator'
            
            def __getattr__(self, name):
                return getattr(self.base_agent, name)
        
        return ObservableOrchestratorAgent(base_agent)
    
    @staticmethod
    def create_analysis_task(user_input: str) -> Dict[str, Any]:
        """Create the initial analysis task for the orchestrator."""
        return {
            "description": ENHANCED_ANALYSIS_TASK_PROMPT.format(user_input=user_input),
            "expected_output": """A comprehensive, multi-iteration analysis containing:
            - Executive Summary comparing request vs actual needs
            - Comprehensive Requirements Matrix with functional/non-functional/hidden requirements
            - Multi-perspective analysis (business, technical, user, risk, future)
            - Risk Assessment with detailed mitigation strategies
            - Documentation Roadmap with depth recommendations and priorities
            - Critical Success Factors and failure modes
            - Open Questions requiring user clarification
            - Stakeholder impact analysis
            - Long-term implications and evolution paths
            - Edge cases and corner scenarios
            
            Each section should reflect deep, iterative thinking with evidence of multiple analysis passes."""
        }
    
    @staticmethod
    def create_coordination_task(project_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create the coordination task for managing other agents."""
        return {
            "description": f"""Based on the project analysis, coordinate the documentation 
            generation process:
            
            Project Analysis: {project_analysis}
            
            Manage the flow of information between agents, ensuring each receives the 
            necessary context and their outputs build upon each other effectively. 
            Monitor progress and quality throughout the process.""",
            "expected_output": """A coordination plan including:
            - Agent activation sequence
            - Information flow between agents
            - Quality checkpoints
            - Timeline estimates
            - Success criteria for each phase"""
        }
    
    @staticmethod
    def determine_required_agents(project_type: str) -> List[str]:
        """Determine which agents are needed based on project type."""
        agent_requirements = {
            "full_product": [
                "product_manager",
                "designer", 
                "database_engineer",
                "software_engineer",
                "user_researcher",
                "business_analyst",
                "solution_architect",
                "quality_reviewer"
            ],
            "feature": [
                "product_manager",
                "designer",
                "software_engineer",
                "quality_reviewer"
            ],
            "tool": [
                "product_manager",
                "software_engineer",
                "quality_reviewer"
            ],
            "api": [
                "product_manager",
                "software_engineer",
                "solution_architect",
                "quality_reviewer"
            ],
            "database": [
                "database_engineer",
                "solution_architect",
                "quality_reviewer"
            ]
        }
        
        return agent_requirements.get(project_type, ["product_manager", "quality_reviewer"])
    
    @staticmethod
    def create_phase_transition_task(current_phase: str, next_phase: str) -> Dict[str, Any]:
        """Create a task for transitioning between project phases."""
        return {
            "description": f"""Manage the transition from {current_phase} to {next_phase}:
            
            1. Validate all deliverables from {current_phase} are complete
            2. Prepare context and requirements for {next_phase}
            3. Identify any gaps or issues that need resolution
            4. Set clear objectives for {next_phase}
            
            Ensure smooth handoff between phases with no loss of information or context.""",
            "expected_output": f"""Phase transition report including:
            - {current_phase} completion status and deliverables
            - {next_phase} readiness assessment
            - Context package for {next_phase} agents
            - Identified risks or blockers
            - Success criteria for {next_phase}"""
        }