"""
CrewAI Agents for AgentPM 2.0
All specialized agents for the multi-agent system.
"""

from .orchestrator import OrchestratorAgent
from .product_manager import ProductManagerAgent
from .designer import DesignerAgent
from .database import DatabaseAgent
from .engineer import EngineerAgent
from .user_researcher import UserResearcherAgent
from .business_analyst import BusinessAnalystAgent
from .solution_architect import SolutionArchitectAgent
from .review import ReviewAgent
from .base_observability import ObservableAgentMixin, create_observable_agent

__all__ = [
    'OrchestratorAgent',
    'ProductManagerAgent',
    'DesignerAgent',
    'DatabaseAgent',
    'EngineerAgent',
    'UserResearcherAgent',
    'BusinessAnalystAgent',
    'SolutionArchitectAgent',
    'ReviewAgent',
    'ObservableAgentMixin',
    'create_observable_agent'
]

# Agent registry for easy access
AGENT_REGISTRY = {
    'orchestrator': OrchestratorAgent,
    'product_manager': ProductManagerAgent,
    'designer': DesignerAgent,
    'database': DatabaseAgent,
    'engineer': EngineerAgent,
    'user_researcher': UserResearcherAgent,
    'business_analyst': BusinessAnalystAgent,
    'solution_architect': SolutionArchitectAgent,
    'review': ReviewAgent
}

def get_agent(agent_type: str):
    """Get agent class by type."""
    return AGENT_REGISTRY.get(agent_type)

def create_agent(agent_type: str, with_observability: bool = True):
    """Create agent instance by type with optional observability."""
    agent_class = get_agent(agent_type)
    if agent_class:
        agent = agent_class.create()
        if with_observability and not isinstance(agent, ObservableAgentMixin):
            # If not already observable, wrap it
            return create_observable_agent(agent_class)
        return agent
    raise ValueError(f"Unknown agent type: {agent_type}")