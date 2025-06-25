"""
Conversation Flow Management for CrewAI Implementation.
Converts LangGraph handoff patterns to CrewAI task delegation.
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from crewai import Task, Crew, Process
import structlog
import asyncio
from datetime import datetime

from agents import (
    OrchestratorAgent, ProductManagerAgent, DesignerAgent,
    DatabaseAgent, EngineerAgent, UserResearcherAgent,
    BusinessAnalystAgent, SolutionArchitectAgent, ReviewAgent
)
from crews.project_crew import ProjectCrew
from core.document_pipeline import (
    document_pipeline, 
    DocumentGenerationRequest, 
    DocumentGenerationStatus
)
from core.state_manager import (
    state_manager,
    ConversationState,
    ConversationPhase as StatePhase,
    ConversationStatus
)

logger = structlog.get_logger()


class ConversationPhase(Enum):
    """Phases of conversation matching LangGraph phases."""
    DISCOVERY = "discovery"
    DEFINITION = "definition"
    REVIEW = "review"
    COMPLETED = "completed"


class AgentDecision(Enum):
    """Agent decision types converted from LangGraph."""
    CONTINUE = "continue"
    HANDOFF = "handoff"
    COLLABORATE = "collaborate"
    COMPLETE = "complete"
    REQUEST_INPUT = "request_input"


@dataclass
class ConversationContext:
    """Context tracking for conversation flow."""
    conversation_id: str
    conversation_type: str  # idea, feature, tool
    phase: ConversationPhase
    agents_consulted: List[str]
    questions_answered: int
    documents_generated: List[str]
    current_agent: Optional[str] = None
    pending_tasks: List[str] = None
    collaboration_active: bool = False
    context_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.pending_tasks is None:
            self.pending_tasks = []
        if self.context_data is None:
            self.context_data = {}


class CrewAIConversationFlow:
    """
    Manages conversation flow using CrewAI task delegation patterns.
    Converts LangGraph handoff logic to CrewAI collaboration.
    Integrates with persistent state management.
    """
    
    def __init__(self):
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.task_history: Dict[str, List[Dict[str, Any]]] = {}
        self.document_pipeline = document_pipeline
        self.state_manager = state_manager
        self.project_crews: Dict[str, ProjectCrew] = {}  # Per-conversation crews
        
    async def start_conversation(
        self,
        conversation_id: str,
        user_input: str,
        conversation_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a new conversation with intelligent routing and state persistence."""
        
        logger.info(f"Starting conversation flow: {conversation_id}")
        
        # Initialize state manager
        await self.state_manager.initialize()
        
        # Detect conversation type if not provided
        if not conversation_type:
            conversation_type = await self._detect_conversation_type(user_input)
        
        # Create persistent conversation state
        persistent_state = await self.state_manager.create_conversation(
            conversation_id=conversation_id,
            conversation_type=conversation_type,
            initial_context={"user_input": user_input}
        )
        
        # Initialize local conversation context (for backward compatibility)
        context = ConversationContext(
            conversation_id=conversation_id,
            conversation_type=conversation_type,
            phase=ConversationPhase.DISCOVERY,
            agents_consulted=[],
            questions_answered=0,
            documents_generated=[],
            context_data={"user_input": user_input}
        )
        
        self.active_conversations[conversation_id] = context
        self.task_history[conversation_id] = []
        
        # Add initial user message to persistent state
        await self.state_manager.add_message(
            conversation_id=conversation_id,
            role="user",
            content=user_input,
            metadata={"conversation_type": conversation_type}
        )
        
        # Start with orchestrator analysis
        return await self._execute_conversation_phase(conversation_id)
        
    async def _execute_conversation_phase(self, conversation_id: str) -> Dict[str, Any]:
        """Execute current conversation phase with appropriate agents."""
        
        context = self.active_conversations[conversation_id]
        
        logger.info(f"Executing phase {context.phase.value} for conversation {conversation_id}")
        
        if context.phase == ConversationPhase.DISCOVERY:
            return await self._execute_discovery_phase(conversation_id)
        elif context.phase == ConversationPhase.DEFINITION:
            return await self._execute_definition_phase(conversation_id)
        elif context.phase == ConversationPhase.REVIEW:
            return await self._execute_review_phase(conversation_id)
        else:
            return {"status": "completed", "conversation_id": conversation_id}
    
    async def _execute_discovery_phase(self, conversation_id: str) -> Dict[str, Any]:
        """Execute discovery phase with appropriate agent sequence."""
        
        context = self.active_conversations[conversation_id]
        
        # Get or create project crew for this conversation
        if conversation_id not in self.project_crews:
            self.project_crews[conversation_id] = ProjectCrew(conversation_id)
        
        project_crew = self.project_crews[conversation_id]
        
        # Create discovery crew based on conversation type
        discovery_agents = self._get_discovery_agents(context.conversation_type)
        discovery_crew = project_crew.create_custom_crew(
            discovery_agents, 
            Process.hierarchical
        )
        
        # Create discovery tasks
        tasks = self._create_discovery_tasks(context)
        
        # Execute discovery crew
        results = await self._run_crew_with_flow_control(
            discovery_crew, tasks, conversation_id
        )
        
        # Process results and determine next phase
        await self._process_phase_results(conversation_id, results)
        
        # Check if ready for next phase
        if self._should_transition_to_definition(context):
            context.phase = ConversationPhase.DEFINITION
            # Update persistent state
            await self.state_manager.update_phase(conversation_id, StatePhase.DEFINITION)
            return await self._execute_conversation_phase(conversation_id)
        
        return {
            "status": "discovery_completed",
            "results": results,
            "next_phase": context.phase.value,
            "conversation_id": conversation_id
        }
    
    async def _execute_definition_phase(self, conversation_id: str) -> Dict[str, Any]:
        """Execute definition phase with technical agents."""
        
        context = self.active_conversations[conversation_id]
        
        # Get or create project crew for this conversation
        if conversation_id not in self.project_crews:
            self.project_crews[conversation_id] = ProjectCrew(conversation_id)
        
        project_crew = self.project_crews[conversation_id]
        
        # Create definition crew
        definition_agents = self._get_definition_agents(context.conversation_type)
        definition_crew = project_crew.create_custom_crew(
            definition_agents,
            Process.hierarchical
        )
        
        # Create definition tasks with parallel document generation
        tasks = self._create_definition_tasks(context)
        
        # Execute definition crew
        results = await self._run_crew_with_flow_control(
            definition_crew, tasks, conversation_id
        )
        
        # Process results
        await self._process_phase_results(conversation_id, results)
        
        # Generate documents using the new pipeline
        await self._generate_documents_for_phase(conversation_id, results)
        
        # Check if ready for review
        if self._should_transition_to_review(context):
            context.phase = ConversationPhase.REVIEW
            # Update persistent state
            await self.state_manager.update_phase(conversation_id, StatePhase.REVIEW)
            return await self._execute_conversation_phase(conversation_id)
        
        return {
            "status": "definition_completed",
            "results": results,
            "next_phase": context.phase.value,
            "conversation_id": conversation_id
        }
    
    async def _execute_review_phase(self, conversation_id: str) -> Dict[str, Any]:
        """Execute review phase with quality assurance."""
        
        context = self.active_conversations[conversation_id]
        
        # Get or create project crew for this conversation
        if conversation_id not in self.project_crews:
            self.project_crews[conversation_id] = ProjectCrew(conversation_id)
        
        project_crew = self.project_crews[conversation_id]
        
        # Create review crew
        review_crew = project_crew.create_custom_crew(
            ["review", "orchestrator"],
            Process.hierarchical
        )
        
        # Create review tasks
        tasks = self._create_review_tasks(context)
        
        # Execute review crew
        results = await self._run_crew_with_flow_control(
            review_crew, tasks, conversation_id
        )
        
        # Mark conversation as completed
        context.phase = ConversationPhase.COMPLETED
        await self.state_manager.complete_conversation(conversation_id)
        
        return {
            "status": "completed",
            "results": results,
            "final_documents": context.documents_generated,
            "conversation_id": conversation_id
        }
    
    def _get_discovery_agents(self, conversation_type: str) -> List[str]:
        """Get agents for discovery phase based on conversation type."""
        
        base_agents = ["orchestrator"]
        
        if conversation_type == "idea":
            return base_agents + ["product_manager", "user_researcher", "business_analyst"]
        elif conversation_type == "feature":
            return base_agents + ["product_manager", "designer", "user_researcher"]
        elif conversation_type == "tool":
            return base_agents + ["product_manager", "engineer", "solution_architect"]
        else:
            return base_agents + ["product_manager", "business_analyst"]
    
    def _get_definition_agents(self, conversation_type: str) -> List[str]:
        """Get agents for definition phase based on conversation type."""
        
        base_agents = ["orchestrator"]
        
        if conversation_type == "idea":
            return base_agents + ["designer", "database", "engineer", "solution_architect"]
        elif conversation_type == "feature":
            return base_agents + ["designer", "engineer", "database"]
        elif conversation_type == "tool":
            return base_agents + ["engineer", "solution_architect", "database"]
        else:
            return base_agents + ["engineer", "designer"]
    
    def _create_discovery_tasks(self, context: ConversationContext) -> List[Task]:
        """Create tasks for discovery phase with intelligent sequencing."""
        
        tasks = []
        user_input = context.context_data.get("user_input", "")
        
        # Get or create project crew for this conversation
        if context.conversation_id not in self.project_crews:
            self.project_crews[context.conversation_id] = ProjectCrew(context.conversation_id)
        
        project_crew = self.project_crews[context.conversation_id]
        
        # Orchestrator analysis task
        orchestrator = project_crew.agents['orchestrator']
        tasks.append(Task(
            description=f"""Analyze user request for {context.conversation_type} project:
            
            User Input: {user_input}
            
            Determine:
            1. Project scope and complexity
            2. Key stakeholders and requirements
            3. Required documentation types
            4. Potential risks and constraints
            5. Agent collaboration strategy
            
            Search knowledge base for similar projects and synthesize insights.""",
            expected_output="Comprehensive project analysis with recommendations",
            agent=orchestrator
        ))
        
        # Business requirements task
        if "product_manager" in self._get_discovery_agents(context.conversation_type):
            pm_agent = project_crew.agents['product_manager']
            tasks.append(Task(
                description=f"""Define business requirements for: {user_input}
                
                Focus on:
                1. Business value and objectives
                2. Target user segments
                3. Success metrics and KPIs
                4. Competitive landscape
                5. Business constraints and assumptions
                
                Generate preliminary PRD sections.""",
                expected_output="Business requirements document with PRD foundations",
                agent=pm_agent
            ))
        
        # User research task
        if "user_researcher" in self._get_discovery_agents(context.conversation_type):
            ur_agent = project_crew.agents['user_researcher']
            tasks.append(Task(
                description=f"""Conduct user research for: {user_input}
                
                Develop:
                1. User personas and segments
                2. User journey maps
                3. Pain points and opportunities
                4. User story prioritization
                5. Usability considerations
                
                Provide user-centered insights.""",
                expected_output="User research findings with personas and journeys",
                agent=ur_agent
            ))
        
        return tasks
    
    def _create_definition_tasks(self, context: ConversationContext) -> List[Task]:
        """Create tasks for definition phase with document generation."""
        
        tasks = []
        user_input = context.context_data.get("user_input", "")
        
        # Get or create project crew for this conversation
        if context.conversation_id not in self.project_crews:
            self.project_crews[context.conversation_id] = ProjectCrew(context.conversation_id)
        
        project_crew = self.project_crews[context.conversation_id]
        
        # Technical specification task
        if "engineer" in self._get_definition_agents(context.conversation_type):
            engineer = project_crew.agents['engineer']
            tasks.append(Task(
                description=f"""Create technical specifications for: {user_input}
                
                Based on discovery findings, define:
                1. System architecture and components
                2. Technical requirements and constraints
                3. API design and integration points
                4. Performance and scalability requirements
                5. Security and compliance considerations
                
                Generate comprehensive SRS document.""",
                expected_output="Software Requirements Specification (SRS)",
                agent=engineer
            ))
        
        # Design specification task
        if "designer" in self._get_definition_agents(context.conversation_type):
            designer = project_crew.agents['designer']
            tasks.append(Task(
                description=f"""Create UX design specifications for: {user_input}
                
                Based on user research, design:
                1. Information architecture
                2. User interface wireframes
                3. Design system principles
                4. Accessibility guidelines
                5. Responsive design patterns
                
                Generate complete UXDD document.""",
                expected_output="User Experience Design Document (UXDD)",
                agent=designer
            ))
        
        # Database design task
        if "database" in self._get_definition_agents(context.conversation_type):
            db_agent = project_crew.agents['database']
            tasks.append(Task(
                description=f"""Design database schema for: {user_input}
                
                Create:
                1. Entity relationship diagram (ERD)
                2. Data model with relationships
                3. Database performance optimization
                4. Data governance and security
                5. Migration and backup strategies
                
                Generate ERD and DBRD documents.""",
                expected_output="Entity Relationship Diagram and Database Requirements",
                agent=db_agent
            ))
        
        return tasks
    
    def _create_review_tasks(self, context: ConversationContext) -> List[Task]:
        """Create tasks for review phase."""
        
        tasks = []
        
        # Get or create project crew for this conversation
        if context.conversation_id not in self.project_crews:
            self.project_crews[context.conversation_id] = ProjectCrew(context.conversation_id)
        
        project_crew = self.project_crews[context.conversation_id]
        
        # Quality review task
        reviewer = project_crew.agents['review']
        tasks.append(Task(
            description=f"""Review all generated documentation for consistency and quality:
            
            Generated Documents: {', '.join(context.documents_generated)}
            
            Validate:
            1. Completeness and accuracy
            2. Consistency across documents
            3. Technical feasibility
            4. Business alignment
            5. Quality standards compliance
            
            Provide final recommendations.""",
            expected_output="Quality review report with recommendations",
            agent=reviewer
        ))
        
        return tasks
    
    async def _run_crew_with_flow_control(
        self, 
        crew: Crew, 
        tasks: List[Task], 
        conversation_id: str
    ) -> Dict[str, Any]:
        """Run crew with flow control and progress tracking."""
        
        logger.info(f"Running crew with {len(tasks)} tasks for conversation {conversation_id}")
        
        # Track task execution
        task_results = {}
        
        try:
            # Execute crew
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, crew.kickoff, {"tasks": tasks})
            
            # Process results
            if isinstance(result, dict):
                task_results.update(result)
            else:
                task_results["crew_output"] = str(result)
            
            # Log task completion
            task_info = {
                "timestamp": datetime.utcnow().isoformat(),
                "crew_size": len(crew.agents),
                "task_count": len(tasks),
                "results": list(task_results.keys())
            }
            self.task_history[conversation_id].append(task_info)
            
            # Update persistent state with crew results
            await self.state_manager.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=f"Crew execution completed with {len(task_results)} results",
                metadata=task_info
            )
            
            return task_results
            
        except Exception as e:
            logger.error(f"Crew execution failed for conversation {conversation_id}: {e}")
            raise
    
    async def _process_phase_results(
        self, 
        conversation_id: str, 
        results: Dict[str, Any]
    ):
        """Process phase results and update conversation context."""
        
        context = self.active_conversations[conversation_id]
        
        # Update documents generated
        for key, value in results.items():
            if isinstance(value, str) and len(value) > 100:
                if key not in context.documents_generated:
                    context.documents_generated.append(key)
                    # Update persistent state
                    await self.state_manager.add_document(
                        conversation_id=conversation_id,
                        document_type=key,
                        document_content=value,
                        is_draft=True
                    )
        
        # Update questions answered count (mock implementation)
        context.questions_answered += len(results)
        
        # Log progress
        logger.info(f"Phase {context.phase.value} results processed for {conversation_id}")
    
    async def _generate_documents_for_phase(
        self, 
        conversation_id: str, 
        phase_results: Dict[str, Any]
    ):
        """Generate documents using the new document pipeline."""
        
        context = self.active_conversations[conversation_id]
        
        # Determine which documents to generate based on conversation type and phase
        document_types = self._get_document_types_for_conversation(context.conversation_type)
        
        if not document_types:
            return
        
        logger.info(f"Generating documents for conversation {conversation_id}: {document_types}")
        
        # Extract Q&A pairs from phase results
        qa_pairs = self._extract_qa_pairs_from_results(phase_results)
        
        # Create document generation request
        request = DocumentGenerationRequest(
            conversation_id=conversation_id,
            document_types=document_types,
            conversation_type=context.conversation_type,
            context=context.context_data,
            qa_pairs=qa_pairs,
            enhancement_level="standard",
            parallel_generation=True
        )
        
        try:
            # Generate documents
            results = await self.document_pipeline.generate_documents(request)
            
            # Update conversation context with generated documents
            for result in results:
                if result.status == DocumentGenerationStatus.COMPLETED:
                    context.documents_generated.append(result.document_type)
                    # Update persistent state with final document
                    await self.state_manager.add_document(
                        conversation_id=conversation_id,
                        document_type=result.document_type,
                        is_draft=False
                    )
                    logger.info(f"Generated {result.document_type} for conversation {conversation_id}")
                else:
                    logger.error(f"Failed to generate {result.document_type}: {result.error_message}")
            
        except Exception as e:
            logger.error(f"Document generation failed for conversation {conversation_id}: {e}")
    
    def _get_document_types_for_conversation(self, conversation_type: str) -> List[str]:
        """Get document types to generate based on conversation type."""
        return self.document_pipeline.get_default_document_types_for_conversation(conversation_type)
    
    def _extract_qa_pairs_from_results(self, results: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """Extract Q&A pairs from phase results for document generation."""
        
        qa_pairs = {}
        
        # Extract meaningful information from crew results
        for key, value in results.items():
            if isinstance(value, str) and value:
                # Create pseudo Q&A pairs from results
                qa_pairs[f"result_{key}"] = {
                    "question": f"What are the {key.replace('_', ' ')} for this project?",
                    "answer": value
                }
        
        return qa_pairs
    
    def _should_transition_to_definition(self, context: ConversationContext) -> bool:
        """Determine if ready to transition to definition phase."""
        
        # Check if we have sufficient discovery information
        min_agents_consulted = 2 if context.conversation_type == "tool" else 3
        min_questions_answered = 3
        
        return (
            len(context.agents_consulted) >= min_agents_consulted and
            context.questions_answered >= min_questions_answered
        )
    
    def _should_transition_to_review(self, context: ConversationContext) -> bool:
        """Determine if ready to transition to review phase."""
        
        # Check if we have core documents generated
        required_docs = 2 if context.conversation_type == "tool" else 3
        
        return len(context.documents_generated) >= required_docs
    
    async def _detect_conversation_type(self, user_input: str) -> str:
        """Detect conversation type from user input."""
        
        input_lower = user_input.lower()
        
        # Simple keyword-based detection (could be enhanced with LLM)
        if any(word in input_lower for word in ["application", "product", "platform", "system"]):
            return "idea"
        elif any(word in input_lower for word in ["feature", "functionality", "enhancement"]):
            return "feature"
        elif any(word in input_lower for word in ["tool", "utility", "script", "automation"]):
            return "tool"
        else:
            return "feature"  # Default
    
    async def continue_conversation(
        self,
        conversation_id: str,
        user_response: str
    ) -> Dict[str, Any]:
        """Continue existing conversation with user response and state recovery."""
        
        # Try to recover conversation from persistent state if not in memory
        if conversation_id not in self.active_conversations:
            await self._recover_conversation_state(conversation_id)
        
        if conversation_id not in self.active_conversations:
            raise ValueError(f"Conversation {conversation_id} not found and could not be recovered")
        
        context = self.active_conversations[conversation_id]
        
        # Add user response to persistent state
        await self.state_manager.add_message(
            conversation_id=conversation_id,
            role="user",
            content=user_response
        )
        
        # Update context with user response
        context.context_data["last_user_response"] = user_response
        context.questions_answered += 1
        
        # Continue current phase or transition
        return await self._execute_conversation_phase(conversation_id)
    
    async def _recover_conversation_state(self, conversation_id: str):
        """Recover conversation state from persistent storage."""
        
        logger.info(f"Attempting to recover conversation state: {conversation_id}")
        
        # Initialize state manager if needed
        await self.state_manager.initialize()
        
        # Try to get persistent state
        persistent_state = await self.state_manager.get_conversation_state(conversation_id)
        
        if persistent_state:
            # Recreate local conversation context from persistent state
            context = ConversationContext(
                conversation_id=persistent_state.conversation_id,
                conversation_type=persistent_state.conversation_type,
                phase=ConversationPhase(persistent_state.phase.value),
                agents_consulted=persistent_state.agents_consulted[:],
                questions_answered=len(persistent_state.messages),
                documents_generated=persistent_state.documents_generated[:],
                context_data=persistent_state.context_data.copy()
            )
            
            self.active_conversations[conversation_id] = context
            self.task_history[conversation_id] = []
            
            logger.info(f"Successfully recovered conversation {conversation_id}")
        else:
            # Try checkpoint recovery
            recovered_state = await self.state_manager.restore_from_checkpoint(conversation_id)
            if recovered_state:
                await self._recover_conversation_state(conversation_id)  # Retry after checkpoint recovery
    
    def get_conversation_status(self, conversation_id: str) -> Dict[str, Any]:
        """Get current status of conversation with persistent state fallback."""
        
        # Check local context first
        if conversation_id in self.active_conversations:
            context = self.active_conversations[conversation_id]
            return {
                "conversation_id": conversation_id,
                "conversation_type": context.conversation_type,
                "phase": context.phase.value,
                "agents_consulted": context.agents_consulted,
                "questions_answered": context.questions_answered,
                "documents_generated": context.documents_generated,
                "collaboration_active": context.collaboration_active,
                "source": "active_memory"
            }
        
        # Try to get from persistent state (synchronous fallback)
        return {
            "conversation_id": conversation_id,
            "status": "not_in_memory",
            "message": "Conversation may exist in persistent storage - use continue_conversation to recover",
            "source": "persistent_storage"
        }
    
    async def create_checkpoint(self, conversation_id: str) -> Dict[str, Any]:
        """Create manual checkpoint for conversation."""
        return await self.state_manager.create_checkpoint(conversation_id)
    
    async def restore_from_checkpoint(
        self,
        conversation_id: str,
        checkpoint_time: Optional[str] = None
    ) -> bool:
        """Restore conversation from checkpoint."""
        
        recovered_state = await self.state_manager.restore_from_checkpoint(
            conversation_id, checkpoint_time
        )
        
        if recovered_state:
            await self._recover_conversation_state(conversation_id)
            return True
        
        return False


# Global conversation flow manager
conversation_flow = CrewAIConversationFlow()