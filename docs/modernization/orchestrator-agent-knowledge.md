# Orchestrator Agent Knowledge Documentation

## Agent Overview

**Agent ID**: `orchestrator_01`  
**Agent Type**: `orchestrator`  
**Primary Role**: Central coordination and routing hub for the multi-agent system

## Core Responsibilities

1. **Conversation Flow Management**: Orchestrates the entire conversation lifecycle
2. **Agent Routing**: Intelligently routes questions to appropriate specialist agents
3. **Phase Management**: Manages conversation phases (discovery → definition → review)
4. **Coverage Assurance**: Ensures comprehensive coverage across all documentation aspects
5. **Context Preservation**: Maintains conversation coherence and context

## Routing Logic & Decision Patterns

### Available Specialist Agents
The orchestrator has knowledge of 8 specialist agents:

- **Product Manager**: Business value, stakeholder needs, market analysis, PRDs, FRDs, product vision, epics
- **Designer**: User experience, information architecture, visual design, wireframes, UX site maps
- **Database Engineer**: Data modeling, relationships, performance, ERDs, database schemas, data catalogs
- **Backend Engineer**: Technical specifications, backend requirements, system architecture
- **User Researcher**: User personas, journey maps, user stories
- **Business Analyst**: Business requirements, system requirements specifications
- **Solution Architect**: Design requirements, architectural patterns, integration design
- **Review Agent**: Quality assurance, completeness check

### Routing Decision Algorithm

#### Initial Routing (Based on Conversation Type)
```python
# Discovery phase - first 3 questions
if conversation_type == "idea":
    return "product_manager"
elif conversation_type == "feature":
    return "designer"  
else:  # tool
    return "engineer"
```

#### Advanced Routing (After 3+ Questions)
```python
# Rotate through specialists based on conversation type and history
if conversation_type == "idea":
    priority_order = ["user_researcher", "business_analyst", "database", "engineer", "solution_architect", "designer"]
elif conversation_type == "feature":
    priority_order = ["database", "engineer", "solution_architect", "designer"]
else:  # tool
    priority_order = ["database", "engineer", "solution_architect", "designer"]

# Route to first agent not yet consulted
```

#### Phase-Based Routing
- **Discovery Phase**: Business-focused agents (PM, User Researcher, Business Analyst)
- **Definition Phase**: Technical agents (Engineer, Database, Designer, Solution Architect)
- **Review Phase**: Review agent exclusively

### Context-Aware Question Generation

#### Initial Questions by Type
- **Idea**: "What's your idea about? Please describe it in a few sentences."
- **Feature**: "What feature would you like to build? Please provide a brief description."
- **Tool**: "What kind of tool are you looking to create? What problem will it solve?"

#### Phase Transition Questions
- After 5+ answered questions in discovery: "We've gathered initial information. Would you like to proceed to defining detailed requirements?"

## LLM Integration

### Model Configuration
- **Model**: Claude 3 Opus (`claude-3-opus-20240229`)
- **Temperature**: 0.3 (balanced creativity/consistency)
- **Max Tokens**: 2000
- **Langfuse Integration**: Full observability tracking

### System Prompt
```
You are the Orchestrator Agent for AgentPM, responsible for managing the conversation flow and routing to appropriate specialist agents.

Your responsibilities:
1. Understand the user's intent and conversation type (idea/feature/tool)
2. Route questions to the appropriate specialist agents
3. Ensure comprehensive coverage across all aspects
4. Maintain conversation coherence and context
5. Identify when sufficient information has been gathered

Current conversation type: {conversation_type}
Current phase: {phase}
Answered questions: {answered_count}

[Available specialist agents list...]

Guide the conversation naturally while ensuring all critical aspects are covered.
```

## Agent Communication Patterns

### Message Types Handled
- **question_request**: Routes to appropriate specialist
- **state_update**: Acknowledges state changes from other agents
- **orchestrator_response**: Standard response format

### Response Format
```python
{
    "action": "route_to_agent" | "acknowledge" | "error",
    "target_agent": "agent_name",
    "reason": "Routing justification",
    "status": "state_updated" (for acknowledgments)
}
```

## Integration with LangGraph State Machine

### State Management
The orchestrator works within the LangGraph `AgentState` structure:

```python
class AgentState(TypedDict):
    conversation_id: str
    conversation_type: Literal["idea", "feature", "tool"]
    phase: Literal["discovery", "definition", "review"]
    messages: List[Dict[str, Any]]
    current_question: Question | None
    answered_questions: List[QuestionResponse]
    pending_questions: List[Question]
    current_agent: str
    agent_history: List[str]
    document_drafts: Dict[str, str]
    # ... additional state fields
```

### Advanced Orchestration Features

#### Smart Transition Logic
```python
def _smart_transition(state: AgentState) -> str:
    """Intelligent routing when no explicit agent decision"""
    - Early stage (< 3 answers): Route by conversation type
    - Discovery phase: Ensure key discovery agents involved
    - Definition phase: Ensure technical agents involved
    - Review phase: Route to review agent
```

#### Agent Completion Handling
```python
def _handle_agent_completion(state: AgentState) -> str:
    """Handle when agents signal task completion"""
    - Check if other agents still need to contribute
    - Transition between phases when appropriate
    - End conversation when all phases complete
```

## Progress Summarization

The orchestrator can generate conversation progress summaries:

```python
async def summarize_progress(self, state: ConversationState) -> str:
    """Generate 2-3 sentence summary of discussion and remaining tasks"""
```

## Migration Considerations for CrewAI

### Current Strengths to Preserve
1. **Intelligent Routing Logic**: The conversation-type and phase-based routing algorithm
2. **Agent Awareness**: Deep knowledge of each specialist agent's capabilities
3. **Phase Management**: Structured progression through discovery → definition → review
4. **Context Preservation**: Systematic tracking of conversation history and agent involvement

### Recommended CrewAI Mapping
```python
# Convert to CrewAI Manager Agent
orchestrator_agent = Agent(
    role='Project Coordinator',
    goal='Orchestrate document generation through specialized agent collaboration',
    backstory='Expert project manager with deep knowledge of documentation workflows',
    tools=[agent_routing_tool, progress_tracking_tool],
    process=Process.hierarchical,  # Maintains orchestrator control
    delegation=True  # Can delegate to specialists
)
```

### Key Intelligence to Transfer
- Conversation type classification logic
- Phase transition criteria
- Agent selection algorithms
- Context summarization capabilities
- Coverage verification patterns

## Current Implementation Files
- `/backend/agents/orchestrator.py` - Main orchestrator implementation
- `/backend/agents/graph.py` - LangGraph integration and routing logic
- `/backend/agents/base.py` - Common agent functionality and communication patterns

---

*This documentation captures the orchestrator's current intelligence for preservation during the CrewAI migration.*