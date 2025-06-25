"""
Task Delegation Manager for CrewAI Implementation.
Maps LangGraph agent handoff patterns to CrewAI task delegation.
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from crewai import Task, Agent
import structlog
from datetime import datetime

logger = structlog.get_logger()


class DelegationReason(Enum):
    """Reasons for task delegation (mapped from LangGraph HandoffReason)."""
    EXPERTISE_NEEDED = "expertise_needed"
    TASK_COMPLETE = "task_complete"
    COLLABORATION_REQUIRED = "collaboration_required"
    USER_REQUEST = "user_request"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    PARALLEL_WORK = "parallel_work"
    PHASE_TRANSITION = "phase_transition"


class DelegationUrgency(Enum):
    """Urgency levels for task delegation."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TaskDelegationContext:
    """Context for task delegation decisions."""
    source_agent: str
    target_agent: str
    reason: DelegationReason
    urgency: DelegationUrgency
    context_summary: str
    specific_request: str
    expected_deliverables: List[str]
    collaboration_mode: bool = False
    dependencies: List[str] = None
    deadline: Optional[datetime] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class AgentCapability:
    """Agent capability mapping (from LangGraph agent capabilities)."""
    agent_type: str
    capabilities: List[str]
    specializations: List[str]
    collaboration_partners: List[str]


class TaskDelegationManager:
    """
    Manages task delegation using CrewAI patterns.
    Converts LangGraph handoff logic to intelligent task routing.
    """
    
    def __init__(self):
        self.agent_capabilities = self._initialize_agent_capabilities()
        self.delegation_history: List[TaskDelegationContext] = []
        self.active_delegations: Dict[str, TaskDelegationContext] = {}
        
    def _initialize_agent_capabilities(self) -> Dict[str, AgentCapability]:
        """Initialize agent capabilities mapping."""
        return {
            "orchestrator": AgentCapability(
                agent_type="orchestrator",
                capabilities=[
                    "workflow_management", "routing", "coordination", "overview",
                    "project_analysis", "intent_classification", "phase_management"
                ],
                specializations=["project_coordination", "agent_routing", "workflow_optimization"],
                collaboration_partners=["all_agents"]
            ),
            "product_manager": AgentCapability(
                agent_type="product_manager",
                capabilities=[
                    "business_requirements", "stakeholder_analysis", "product_vision",
                    "feature_prioritization", "market_analysis", "user_stories",
                    "prd_generation", "brd_generation", "product_strategy"
                ],
                specializations=["product_strategy", "business_requirements", "market_analysis"],
                collaboration_partners=["user_researcher", "business_analyst", "designer"]
            ),
            "designer": AgentCapability(
                agent_type="designer",
                capabilities=[
                    "user_experience", "interface_design", "wireframes", "prototyping",
                    "design_systems", "accessibility", "user_flows", "uxdd_generation",
                    "information_architecture", "visual_design"
                ],
                specializations=["ux_design", "ui_design", "design_systems"],
                collaboration_partners=["user_researcher", "product_manager", "engineer"]
            ),
            "engineer": AgentCapability(
                agent_type="engineer",
                capabilities=[
                    "technical_architecture", "system_design", "api_design",
                    "performance_requirements", "scalability", "security",
                    "srs_generation", "technical_specifications", "code_architecture"
                ],
                specializations=["system_architecture", "technical_design", "performance_optimization"],
                collaboration_partners=["solution_architect", "database", "designer"]
            ),
            "database": AgentCapability(
                agent_type="database",
                capabilities=[
                    "data_modeling", "database_design", "data_relationships",
                    "data_integrity", "performance_optimization", "data_governance",
                    "erd_generation", "dbrd_generation", "schema_design"
                ],
                specializations=["data_modeling", "database_optimization", "data_architecture"],
                collaboration_partners=["engineer", "solution_architect", "business_analyst"]
            ),
            "user_researcher": AgentCapability(
                agent_type="user_researcher",
                capabilities=[
                    "user_personas", "user_journey_mapping", "usability_testing",
                    "user_interviews", "behavioral_analysis", "user_story_creation",
                    "persona_generation", "journey_mapping"
                ],
                specializations=["user_research", "persona_development", "journey_mapping"],
                collaboration_partners=["designer", "product_manager", "business_analyst"]
            ),
            "business_analyst": AgentCapability(
                agent_type="business_analyst",
                capabilities=[
                    "business_process_analysis", "requirements_gathering",
                    "gap_analysis", "business_rules", "compliance",
                    "srs_generation", "process_optimization", "stakeholder_mapping"
                ],
                specializations=["requirements_analysis", "process_optimization", "compliance"],
                collaboration_partners=["product_manager", "solution_architect", "user_researcher"]
            ),
            "solution_architect": AgentCapability(
                agent_type="solution_architect",
                capabilities=[
                    "system_architecture", "integration_design", "technology_selection",
                    "deployment_strategy", "infrastructure_design", "architecture_patterns",
                    "scalability_planning", "technology_assessment"
                ],
                specializations=["system_architecture", "integration_design", "scalability"],
                collaboration_partners=["engineer", "database", "business_analyst"]
            ),
            "review": AgentCapability(
                agent_type="review",
                capabilities=[
                    "quality_assurance", "completeness_review", "consistency_check",
                    "final_validation", "documentation_review", "quality_scoring",
                    "compliance_validation", "risk_assessment"
                ],
                specializations=["quality_assurance", "documentation_review", "compliance"],
                collaboration_partners=["all_agents"]
            )
        }
    
    def create_delegated_task(
        self,
        delegation_context: TaskDelegationContext,
        base_description: str,
        conversation_context: Dict[str, Any] = None
    ) -> Task:
        """Create a CrewAI task based on delegation context."""
        
        # Get target agent capabilities
        target_capabilities = self.agent_capabilities.get(delegation_context.target_agent)
        if not target_capabilities:
            raise ValueError(f"Unknown agent type: {delegation_context.target_agent}")
        
        # Build enhanced task description
        enhanced_description = self._build_enhanced_description(
            delegation_context, base_description, conversation_context
        )
        
        # Build expected output based on agent specializations
        expected_output = self._build_expected_output(delegation_context, target_capabilities)
        
        # Create task (agent will be assigned by crew)
        task = Task(
            description=enhanced_description,
            expected_output=expected_output
        )
        
        # Store delegation context
        delegation_id = f"{delegation_context.source_agent}_to_{delegation_context.target_agent}_{len(self.delegation_history)}"
        self.active_delegations[delegation_id] = delegation_context
        self.delegation_history.append(delegation_context)
        
        logger.info(
            "Task delegation created",
            source_agent=delegation_context.source_agent,
            target_agent=delegation_context.target_agent,
            reason=delegation_context.reason.value
        )
        
        return task
    
    def _build_enhanced_description(
        self,
        delegation_context: TaskDelegationContext,
        base_description: str,
        conversation_context: Dict[str, Any] = None
    ) -> str:
        """Build enhanced task description with delegation context."""
        
        context_info = ""
        if conversation_context:
            context_info = f"""
            
Conversation Context:
- Project Type: {conversation_context.get('conversation_type', 'Unknown')}
- Phase: {conversation_context.get('phase', 'Unknown')}
- Previous Work: {conversation_context.get('previous_deliverables', [])}
- Key Requirements: {conversation_context.get('key_requirements', [])}
"""
        
        handoff_info = f"""

Delegation Details:
- From: {delegation_context.source_agent}
- Reason: {delegation_context.reason.value}
- Priority: {delegation_context.urgency.value}
- Specific Request: {delegation_context.specific_request}
- Context: {delegation_context.context_summary}
"""
        
        collaboration_info = ""
        if delegation_context.collaboration_mode:
            partners = self.agent_capabilities[delegation_context.target_agent].collaboration_partners
            collaboration_info = f"""

Collaboration Mode: Active
- Consider insights from: {', '.join(partners)}
- Build upon previous agent work
- Ensure consistency with existing deliverables
"""
        
        dependencies_info = ""
        if delegation_context.dependencies:
            dependencies_info = f"""

Dependencies:
- Must complete after: {', '.join(delegation_context.dependencies)}
- Consider outputs from dependent tasks
"""
        
        return f"""{base_description}{context_info}{handoff_info}{collaboration_info}{dependencies_info}

Expected Deliverables: {', '.join(delegation_context.expected_deliverables)}
"""
    
    def _build_expected_output(
        self,
        delegation_context: TaskDelegationContext,
        target_capabilities: AgentCapability
    ) -> str:
        """Build expected output based on agent capabilities and delegation context."""
        
        base_outputs = {
            "orchestrator": "Project analysis, coordination plan, and agent routing recommendations",
            "product_manager": "Product Requirements Document (PRD) or Business Requirements Document (BRD)",
            "designer": "User Experience Design Document (UXDD) with wireframes and design specifications",
            "engineer": "Software Requirements Specification (SRS) with technical architecture",
            "database": "Entity Relationship Diagram (ERD) and Database Requirements Document (DBRD)",
            "user_researcher": "User personas, journey maps, and research insights",
            "business_analyst": "Business process analysis and requirements specification",
            "solution_architect": "System architecture design and integration patterns",
            "review": "Quality review report with recommendations and validation results"
        }
        
        base_output = base_outputs.get(delegation_context.target_agent, "Analysis and recommendations")
        
        # Add specific deliverables from delegation context
        if delegation_context.expected_deliverables:
            specific_outputs = ", ".join(delegation_context.expected_deliverables)
            return f"{base_output}\n\nSpecific Deliverables: {specific_outputs}"
        
        return base_output
    
    def suggest_next_delegation(
        self,
        current_agent: str,
        conversation_context: Dict[str, Any],
        completed_tasks: List[str] = None
    ) -> Optional[TaskDelegationContext]:
        """Suggest next delegation based on conversation state (replaces LangGraph routing logic)."""
        
        if completed_tasks is None:
            completed_tasks = []
        
        phase = conversation_context.get('phase', 'discovery')
        conversation_type = conversation_context.get('conversation_type', 'feature')
        agents_consulted = conversation_context.get('agents_consulted', [])
        documents_generated = conversation_context.get('documents_generated', [])
        
        # Discovery phase routing
        if phase == 'discovery':
            return self._suggest_discovery_delegation(
                current_agent, conversation_type, agents_consulted
            )
        
        # Definition phase routing
        elif phase == 'definition':
            return self._suggest_definition_delegation(
                current_agent, conversation_type, agents_consulted, documents_generated
            )
        
        # Review phase routing
        elif phase == 'review':
            return self._suggest_review_delegation(current_agent, documents_generated)
        
        return None
    
    def _suggest_discovery_delegation(
        self,
        current_agent: str,
        conversation_type: str,
        agents_consulted: List[str]
    ) -> Optional[TaskDelegationContext]:
        """Suggest delegation for discovery phase."""
        
        # Priority agents by conversation type
        priority_maps = {
            "idea": ["product_manager", "user_researcher", "business_analyst"],
            "feature": ["product_manager", "designer", "user_researcher"],
            "tool": ["product_manager", "engineer", "solution_architect"]
        }
        
        priority_agents = priority_maps.get(conversation_type, ["product_manager", "business_analyst"])
        
        # Find next unconsulted agent
        for agent in priority_agents:
            if agent not in agents_consulted and agent != current_agent:
                return TaskDelegationContext(
                    source_agent=current_agent,
                    target_agent=agent,
                    reason=DelegationReason.EXPERTISE_NEEDED,
                    urgency=DelegationUrgency.MEDIUM,
                    context_summary=f"Discovery phase requires {agent} expertise",
                    specific_request=f"Provide {agent} perspective on requirements",
                    expected_deliverables=[f"{agent}_analysis"],
                    collaboration_mode=True
                )
        
        return None
    
    def _suggest_definition_delegation(
        self,
        current_agent: str,
        conversation_type: str,
        agents_consulted: List[str],
        documents_generated: List[str]
    ) -> Optional[TaskDelegationContext]:
        """Suggest delegation for definition phase."""
        
        # Required documents by conversation type
        doc_requirements = {
            "idea": ["prd", "uxdd", "srs", "erd"],
            "feature": ["prd", "uxdd", "srs"],
            "tool": ["srs", "architecture", "erd"]
        }
        
        # Agent to document mapping
        doc_to_agent = {
            "prd": "product_manager",
            "uxdd": "designer", 
            "srs": "engineer",
            "erd": "database",
            "architecture": "solution_architect"
        }
        
        required_docs = doc_requirements.get(conversation_type, ["prd", "srs"])
        
        # Find missing document that needs generation
        for doc in required_docs:
            if doc not in documents_generated:
                target_agent = doc_to_agent.get(doc)
                if target_agent and target_agent != current_agent:
                    return TaskDelegationContext(
                        source_agent=current_agent,
                        target_agent=target_agent,
                        reason=DelegationReason.EXPERTISE_NEEDED,
                        urgency=DelegationUrgency.HIGH,
                        context_summary=f"Need {doc.upper()} document generation",
                        specific_request=f"Generate comprehensive {doc.upper()} document",
                        expected_deliverables=[doc],
                        collaboration_mode=True
                    )
        
        return None
    
    def _suggest_review_delegation(
        self,
        current_agent: str,
        documents_generated: List[str]
    ) -> Optional[TaskDelegationContext]:
        """Suggest delegation for review phase."""
        
        if current_agent != "review" and documents_generated:
            return TaskDelegationContext(
                source_agent=current_agent,
                target_agent="review",
                reason=DelegationReason.TASK_COMPLETE,
                urgency=DelegationUrgency.HIGH,
                context_summary="All documents generated, need quality review",
                specific_request="Perform comprehensive quality review",
                expected_deliverables=["quality_report"],
                collaboration_mode=False
            )
        
        return None
    
    def validate_delegation(self, delegation_context: TaskDelegationContext) -> Tuple[bool, str]:
        """Validate if delegation is appropriate (replaces LangGraph handoff validation)."""
        
        # Check for self-delegation
        if delegation_context.source_agent == delegation_context.target_agent:
            return False, "Cannot delegate to self"
        
        # Check if target agent has relevant capabilities
        target_capabilities = self.agent_capabilities.get(delegation_context.target_agent)
        if not target_capabilities:
            return False, f"Unknown agent type: {delegation_context.target_agent}"
        
        # Check for capability match
        if not self._has_relevant_capability(delegation_context, target_capabilities):
            return False, f"Agent {delegation_context.target_agent} may not have relevant capabilities"
        
        # Check for delegation cycles (simplified)
        if self._would_create_cycle(delegation_context):
            return False, "Delegation would create a cycle"
        
        return True, "Delegation validated successfully"
    
    def _has_relevant_capability(
        self,
        delegation_context: TaskDelegationContext,
        target_capabilities: AgentCapability
    ) -> bool:
        """Check if target agent has relevant capabilities."""
        
        request_keywords = delegation_context.specific_request.lower().split()
        
        # Check capabilities
        for capability in target_capabilities.capabilities:
            capability_keywords = capability.replace("_", " ").split()
            if any(keyword in request_keywords for keyword in capability_keywords):
                return True
        
        # Check expected deliverables
        for deliverable in delegation_context.expected_deliverables:
            if any(deliverable.lower() in cap for cap in target_capabilities.capabilities):
                return True
        
        return True  # Default to allow delegation (more permissive than LangGraph)
    
    def _would_create_cycle(self, delegation_context: TaskDelegationContext) -> bool:
        """Check for delegation cycles (simplified version of LangGraph cycle detection)."""
        
        # Check last few delegations for immediate back-and-forth
        recent_delegations = self.delegation_history[-5:] if self.delegation_history else []
        
        for recent in recent_delegations:
            if (recent.source_agent == delegation_context.target_agent and 
                recent.target_agent == delegation_context.source_agent):
                return True
        
        return False
    
    def get_collaboration_partners(self, agent_type: str) -> List[str]:
        """Get collaboration partners for an agent."""
        
        capabilities = self.agent_capabilities.get(agent_type)
        if not capabilities:
            return []
        
        partners = capabilities.collaboration_partners
        if "all_agents" in partners:
            return list(self.agent_capabilities.keys())
        
        return partners
    
    def get_delegation_history(self, agent_type: Optional[str] = None) -> List[TaskDelegationContext]:
        """Get delegation history, optionally filtered by agent."""
        
        if not agent_type:
            return self.delegation_history
        
        return [
            delegation for delegation in self.delegation_history
            if delegation.source_agent == agent_type or delegation.target_agent == agent_type
        ]


# Global task delegation manager
task_delegation_manager = TaskDelegationManager()