"""
Project Crew configuration for CrewAI implementation.
Defines crew compositions for different project types.
"""

from crewai import Crew, Process
from typing import List, Dict, Any, Optional
from ..agents import (
    OrchestratorAgent,
    ProductManagerAgent,
    DesignerAgent,
    DatabaseAgent,
    EngineerAgent,
    UserResearcherAgent,
    BusinessAnalystAgent,
    SolutionArchitectAgent,
    ReviewAgent
)
from ..core.model_context import model_context
from ..config import get_crew_config, get_sequential_crew_config, get_multipass_crew_config
import structlog

logger = structlog.get_logger()


class ProjectCrew:
    """Manages crew composition and task assignment for projects."""
    
    def __init__(self, conversation_id: Optional[str] = None, quality_level: str = "premium"):
        self.conversation_id = conversation_id
        self.quality_level = quality_level
        self._agents = None
        
    @property
    def agents(self) -> Dict[str, Any]:
        """Lazy load agents with dynamic model selection."""
        if self._agents is None:
            # Get model override if set for this conversation
            override_model = None
            if self.conversation_id:
                override_model = model_context.get_model_for_conversation(self.conversation_id)
                
            # Initialize all agents with potential model override
            self._agents = {
                'orchestrator': OrchestratorAgent.create(model_override=override_model),
                'product_manager': ProductManagerAgent.create(model_override=override_model),
                'designer': DesignerAgent.create(model_override=override_model),
                'database': DatabaseAgent.create(model_override=override_model),
                'engineer': EngineerAgent.create(model_override=override_model),
                'user_researcher': UserResearcherAgent.create(model_override=override_model),
                'business_analyst': BusinessAnalystAgent.create(model_override=override_model),
                'solution_architect': SolutionArchitectAgent.create(model_override=override_model),
                'review': ReviewAgent.create(model_override=override_model)
            }
            
            if override_model:
                logger.info(f"Created agents with model override: {override_model}")
                
        return self._agents
        
    def create_full_product_crew(self) -> Crew:
        """Create crew for full product development."""
        return Crew(
            agents=[
                self.agents['orchestrator'],
                self.agents['user_researcher'],
                self.agents['product_manager'],
                self.agents['business_analyst'],
                self.agents['designer'],
                self.agents['solution_architect'],
                self.agents['database'],
                self.agents['engineer'],
                self.agents['review']
            ],
            process=Process.sequential,  # Sequential for quality focus
            verbose=True,
            **get_sequential_crew_config(self.quality_level)
        )
        
    def create_feature_crew(self) -> Crew:
        """Create crew for feature development."""
        return Crew(
            agents=[
                self.agents['orchestrator'],
                self.agents['product_manager'],
                self.agents['designer'],
                self.agents['engineer'],
                self.agents['review']
            ],
            process=Process.sequential,  # Sequential for quality focus
            verbose=True,
            **get_sequential_crew_config(self.quality_level)
        )
        
    def create_api_crew(self) -> Crew:
        """Create crew for API development."""
        return Crew(
            agents=[
                self.agents['orchestrator'],
                self.agents['product_manager'],
                self.agents['solution_architect'],
                self.agents['engineer'],
                self.agents['review']
            ],
            process=Process.sequential,  # Sequential for quality focus
            verbose=True,
            **get_sequential_crew_config(self.quality_level)
        )
        
    def create_database_crew(self) -> Crew:
        """Create crew for database design."""
        return Crew(
            agents=[
                self.agents['orchestrator'],
                self.agents['business_analyst'],
                self.agents['database'],
                self.agents['solution_architect'],
                self.agents['review']
            ],
            process=Process.sequential,  # Sequential for quality focus
            verbose=True,
            **get_sequential_crew_config(self.quality_level)
        )
        
    def create_mvp_crew(self) -> Crew:
        """Create crew for MVP development."""
        return Crew(
            agents=[
                self.agents['orchestrator'],
                self.agents['product_manager'],
                self.agents['engineer'],
                self.agents['review']
            ],
            process=Process.sequential,
            verbose=True,
            **get_sequential_crew_config(self.quality_level)
        )
        
    def get_crew_for_project_type(self, project_type: str) -> Crew:
        """Get appropriate crew based on project type."""
        crew_mapping = {
            'full_product': self.create_full_product_crew,
            'feature': self.create_feature_crew,
            'api': self.create_api_crew,
            'database': self.create_database_crew,
            'mvp': self.create_mvp_crew,
            'tool': self.create_feature_crew
        }
        
        crew_creator = crew_mapping.get(project_type, self.create_feature_crew)
        logger.info(f"Creating crew for project type: {project_type}")
        return crew_creator()
        
    def create_custom_crew(self, agent_names: List[str], process: Process = Process.hierarchical) -> Crew:
        """Create custom crew with specified agents."""
        selected_agents = []
        
        for name in agent_names:
            if name in self.agents:
                selected_agents.append(self.agents[name])
            else:
                logger.warning(f"Unknown agent: {name}")
                
        if not selected_agents:
            # Fallback to minimal crew
            selected_agents = [self.agents['orchestrator'], self.agents['product_manager']]
            
        return Crew(
            agents=selected_agents,
            process=Process.sequential if process == Process.hierarchical else process,  # Force sequential for quality
            verbose=True,
            **get_sequential_crew_config(self.quality_level)
        )
    
    def create_excellence_crew(self) -> Crew:
        """Create crew optimized for excellence-level quality (5-pass generation)."""
        return Crew(
            agents=[
                self.agents['orchestrator'],
                self.agents['user_researcher'],
                self.agents['product_manager'],
                self.agents['business_analyst'],
                self.agents['designer'],
                self.agents['solution_architect'],
                self.agents['database'],
                self.agents['engineer'],
                self.agents['review']  # Enhanced review agent for multi-pass
            ],
            process=Process.sequential,
            verbose=True,
            **get_multipass_crew_config(passes=5, iterations_per_pass=3, quality_threshold=95.0)
        )
    
    def create_multipass_crew(
        self, 
        agent_names: List[str], 
        passes: int = 3,
        quality_threshold: float = 85.0
    ) -> Crew:
        """Create crew specifically for multi-pass document generation."""
        
        # Ensure review agent is always included for multi-pass
        if 'review' not in agent_names:
            agent_names.append('review')
        
        selected_agents = []
        for name in agent_names:
            if name in self.agents:
                selected_agents.append(self.agents[name])
            else:
                logger.warning(f"Unknown agent: {name}")
        
        return Crew(
            agents=selected_agents,
            process=Process.sequential,  # Always sequential for multi-pass
            verbose=True,
            **get_multipass_crew_config(
                passes=passes, 
                iterations_per_pass=2, 
                quality_threshold=quality_threshold
            )
        )
    
    def create_quality_focused_crew(self, project_type: str, quality_level: str = "excellence") -> Crew:
        """Create quality-focused crew with enhanced configurations."""
        
        # Set quality level for this crew
        original_quality = self.quality_level
        self.quality_level = quality_level
        
        try:
            # Create crew based on project type with quality focus
            if quality_level == "excellence":
                return self.create_excellence_crew()
            else:
                return self.get_crew_for_project_type(project_type)
        finally:
            # Restore original quality level
            self.quality_level = original_quality
    
    def create_review_focused_crew(self) -> Crew:
        """Create crew focused on review and quality assurance."""
        return Crew(
            agents=[
                self.agents['orchestrator'],
                self.agents['review']
            ],
            process=Process.sequential,
            verbose=True,
            **get_multipass_crew_config(passes=5, iterations_per_pass=1, quality_threshold=95.0)
        )