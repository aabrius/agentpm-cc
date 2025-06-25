# LangGraph to CrewAI Migration Guide

## Overview

This guide provides detailed, step-by-step instructions for migrating each AgentPM agent from LangGraph to CrewAI. It includes code mappings, pattern translations, and practical examples to ensure a smooth transition while preserving all agent functionality.

## Core Concept Mappings

### 1. StateGraph → Crew

**LangGraph Pattern:**
```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("product_manager", product_manager_node)
workflow.add_edge("orchestrator", "product_manager")
workflow.add_conditional_edges(
    "orchestrator",
    route_to_next_agent,
    {
        "product_manager": "product_manager",
        "designer": "designer",
        END: END
    }
)
app = workflow.compile()
```

**CrewAI Equivalent:**
```python
from crewai import Crew, Process, Agent, Task

crew = Crew(
    agents=[orchestrator, product_manager, designer],
    tasks=[analyze_task, create_prd_task, design_task],
    process=Process.hierarchical,  # Orchestrator manages flow
    manager_llm=claude_opus_4,
    verbose=True
)
result = crew.kickoff(inputs={"user_input": message})
```

### 2. Agent Node → CrewAI Agent

**LangGraph Pattern:**
```python
class ProductManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="product_manager",
            agent_type="product_manager",
            description="Creates PRD and BRD documents"
        )
        self.llm = get_llm()
        self.supported_documents = ["prd", "brd"]
    
    async def process(self, state: AgentState) -> AgentState:
        # Complex state manipulation
        questions = await self._generate_product_questions(state)
        state["pending_questions"].extend(questions)
        
        if self._has_enough_info(state):
            document = await self._generate_document(state, doc_type)
            state["documents"][doc_type] = document
            
        return state
```

**CrewAI Equivalent:**
```python
from crewai import Agent
from crewai_tools import BaseTool

class PRDGeneratorTool(BaseTool):
    name: str = "PRD Generator"
    description: str = "Generates Product Requirements Documents"
    
    def _run(self, requirements: dict) -> str:
        template = load_template("prd")
        return generate_document(template, requirements)

product_manager = Agent(
    role='Senior Product Manager',
    goal='Create comprehensive PRD and BRD documents',
    backstory='Expert product strategist with 10+ years experience...',
    tools=[PRDGeneratorTool(), BRDGeneratorTool()],
    llm=claude_35_sonnet,
    max_iter=5,
    verbose=True
)
```

### 3. State Management → Task Context

**LangGraph Pattern:**
```python
class AgentState(TypedDict):
    conversation_id: str
    messages: List[Message]
    current_agent: str
    pending_questions: List[Question]
    answered_questions: List[Question]
    documents: Dict[str, str]
    phase: str
    metadata: Dict[str, Any]
    
# Complex state passing
state["handoff_context"] = {
    "from_agent": "product_manager",
    "to_agent": "designer",
    "shared_data": {...}
}
```

**CrewAI Equivalent:**
```python
# Automatic context passing through tasks
prd_task = Task(
    description="Create PRD based on requirements",
    agent=product_manager,
    expected_output="Complete PRD document"
)

design_task = Task(
    description="Create UXDD based on PRD",
    agent=designer,
    expected_output="UXDD with wireframes",
    context=[prd_task]  # Automatically receives PRD output
)

# Simplified state through task results
class TaskResult:
    raw: str  # Raw output
    pydantic: BaseModel  # Structured output
    json_dict: dict  # JSON representation
```

### 4. Routing Logic → Hierarchical Process

**LangGraph Pattern:**
```python
def route_to_next_agent(state: AgentState) -> str:
    if state["phase"] == "definition":
        if "product_manager" not in state["completed_agents"]:
            return "product_manager"
        elif "designer" not in state["completed_agents"]:
            return "designer"
    elif state["phase"] == "execution":
        if "engineer" not in state["completed_agents"]:
            return "engineer"
    return END
```

**CrewAI Equivalent:**
```python
# Orchestrator agent handles routing through delegation
orchestrator = Agent(
    role='Project Orchestration Manager',
    goal='Coordinate agents based on project needs',
    allow_delegation=True,  # Can delegate to other agents
    verbose=True
)

# Dynamic task creation based on project type
def create_tasks_for_project(project_type: str) -> List[Task]:
    if project_type == "full_product":
        return [prd_task, brd_task, uxdd_task, srs_task, erd_task]
    elif project_type == "feature":
        return [prd_task, uxdd_task, srs_task]
    else:
        return [prd_task, srs_task]
```

## Agent-Specific Migration Patterns

### 1. Orchestrator Agent Migration

**LangGraph Implementation:**
```python
async def orchestrator_node(state: AgentState) -> AgentState:
    orchestrator = OrchestratorAgent()
    
    # Analyze intent
    intent = await orchestrator.analyze_intent(state["messages"])
    state["intent"] = intent
    
    # Determine next agent
    next_agent = orchestrator.determine_next_agent(state)
    state["next_agent"] = next_agent
    
    # Update phase
    if all_requirements_gathered(state):
        state["phase"] = "execution"
    
    return state
```

**CrewAI Implementation:**
```python
class IntentAnalysisTool(BaseTool):
    name = "Intent Analyzer"
    description = "Analyzes user intent and project requirements"
    
    def _run(self, user_input: str) -> dict:
        # LLM-based intent analysis
        prompt = f"Analyze this request and categorize: {user_input}"
        response = llm.invoke(prompt)
        return parse_intent(response)

orchestrator = Agent(
    role='Project Orchestration Manager',
    goal='Analyze intent and coordinate documentation generation',
    tools=[IntentAnalysisTool(), ProjectClassifierTool()],
    allow_delegation=True
)

orchestration_task = Task(
    description="Analyze user request and plan documentation approach",
    agent=orchestrator,
    expected_output="Project plan with required documents and agent assignments"
)
```

### 2. Question Framework Migration

**LangGraph Pattern:**
```python
async def generate_questions(self, state: ConversationState) -> List[Question]:
    questions = []
    answered_ids = {q.question_id for q in state.answered_questions}
    
    product_questions = [
        {"id": "product_1", "content": "What problem?", "required": True},
        {"id": "product_2", "content": "Target users?", "required": True}
    ]
    
    for q in product_questions:
        if q["id"] not in answered_ids:
            questions.append(Question(**q))
    
    return questions
```

**CrewAI Tool Implementation:**
```python
class RequirementsGathererTool(BaseTool):
    name = "Requirements Gatherer"
    description = "Gathers requirements through structured questions"
    
    def _run(self, context: dict) -> dict:
        required_info = {
            "problem_statement": "What problem does this solve?",
            "target_users": "Who are the target users?",
            "success_metrics": "How will success be measured?",
            "constraints": "What are the constraints?",
            "timeline": "What is the timeline?"
        }
        
        # Check what's already answered
        missing = {k: v for k, v in required_info.items() 
                  if k not in context.get("answered", {})}
        
        if missing:
            # Use LLM to extract from conversation
            extracted = self._extract_from_context(context["messages"], missing)
            return {"status": "incomplete", "missing": missing, "extracted": extracted}
        
        return {"status": "complete", "data": context["answered"]}
```

### 3. Document Generation Migration

**LangGraph Pattern:**
```python
async def _generate_prd(self, state: AgentState) -> str:
    template_path = "templates/prd/structure.yaml"
    answers = self._extract_answers(state)
    
    # Complex template rendering with state
    prd_content = await self._render_template_with_llm(
        template_path, 
        answers,
        state["metadata"]
    )
    
    return prd_content
```

**CrewAI Tool Implementation:**
```python
class PRDGeneratorTool(BaseTool):
    name = "PRD Generator"
    description = "Generates comprehensive Product Requirements Documents"
    template_path = "templates/prd/structure.yaml"
    
    def _run(self, requirements: dict) -> str:
        # Load template
        template = self._load_yaml_template(self.template_path)
        
        # Generate sections with LLM enhancement
        sections = {}
        for section in template["sections"]:
            prompt = self._build_section_prompt(section, requirements)
            sections[section["id"]] = llm.invoke(prompt)
        
        # Compile final document
        return self._compile_document(template, sections)
    
    def _validate(self, document: str) -> bool:
        # Implement validation rules from template
        validator = DocumentValidator(self.template_path)
        return validator.validate(document)
```

### 4. WebSocket Integration Migration

**LangGraph Pattern:**
```python
async def handle_websocket(websocket: WebSocket, conversation_id: str):
    agent_executor = AgentExecutor(workflow)
    
    async for message in websocket:
        state = await load_state(conversation_id)
        state["messages"].append(message)
        
        # Stream tokens
        async for chunk in agent_executor.astream(state):
            await websocket.send_json({
                "type": "token",
                "content": chunk
            })
```

**CrewAI Implementation:**
```python
from crewai.callbacks import BaseCallbackHandler

class WebSocketStreamingCallback(BaseCallbackHandler):
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        
    async def on_agent_action(self, action: Any, **kwargs):
        await self.websocket.send_json({
            "type": "agent_action",
            "agent": kwargs.get("agent_name"),
            "action": str(action),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def on_task_complete(self, output: Any, **kwargs):
        await self.websocket.send_json({
            "type": "task_complete",
            "task": kwargs.get("task_name"),
            "output": str(output)[:500],  # Preview
            "timestamp": datetime.utcnow().isoformat()
        })

# Usage
async def handle_crewai_websocket(websocket: WebSocket, user_input: str):
    callback = WebSocketStreamingCallback(websocket)
    
    crew = Crew(
        agents=[...],
        tasks=[...],
        callbacks=[callback],
        verbose=True
    )
    
    result = await crew.kickoff_async(inputs={"request": user_input})
    
    await websocket.send_json({
        "type": "complete",
        "documents": result.raw
    })
```

### 5. Redis State → In-Memory State

**LangGraph Pattern:**
```python
class RedisStateManager:
    async def save_state(self, conversation_id: str, state: AgentState):
        await self.redis.set(
            f"conversation:{conversation_id}",
            json.dumps(state),
            ex=3600
        )
    
    async def load_state(self, conversation_id: str) -> AgentState:
        data = await self.redis.get(f"conversation:{conversation_id}")
        return json.loads(data) if data else self._default_state()
```

**CrewAI Pattern:**
```python
class ConversationManager:
    def __init__(self):
        self.conversations = {}  # In-memory for MVP
        
    def start_conversation(self, conversation_id: str) -> Conversation:
        conv = Conversation(
            id=conversation_id,
            messages=[],
            documents={},
            metadata={}
        )
        self.conversations[conversation_id] = conv
        return conv
    
    def get_crew_for_conversation(self, conv: Conversation) -> Crew:
        # Dynamic crew composition based on conversation
        project_type = conv.metadata.get("project_type", "standard")
        
        if project_type == "full":
            return self.full_documentation_crew()
        elif project_type == "feature":
            return self.feature_crew()
        else:
            return self.minimal_crew()
```

## Template and Tool Migration

### Converting YAML Templates to CrewAI Tools

**Step 1: Create Base Template Tool**
```python
from crewai_tools import BaseTool
import yaml
import jinja2

class TemplateDocumentTool(BaseTool):
    template_name: str
    template_path: str
    validation_rules: dict = {}
    
    def _run(self, context: dict) -> str:
        # Load YAML template
        with open(self.template_path) as f:
            template_data = yaml.safe_load(f)
        
        # Extract sections and questions
        sections = self._process_sections(template_data["sections"], context)
        
        # Generate document
        document = self._generate_document(sections, template_data)
        
        # Validate
        if not self._validate_document(document, template_data.get("validation_rules", {})):
            raise ValueError("Document validation failed")
        
        return document
```

**Step 2: Create Specific Tool Implementations**
```python
class PRDGeneratorTool(TemplateDocumentTool):
    name = "PRD Generator"
    description = "Generates Product Requirements Documents"
    template_name = "prd"
    template_path = "templates/prd/structure.yaml"
    
    def _enhance_with_llm(self, section: dict, context: dict) -> str:
        """Use LLM to enhance section content"""
        prompt = f"""
        Generate content for PRD section '{section['title']}':
        Context: {json.dumps(context)}
        Requirements: {section.get('description', '')}
        """
        return llm.invoke(prompt)

class ERDGeneratorTool(TemplateDocumentTool):
    name = "ERD Generator"
    description = "Generates Entity Relationship Diagrams"
    template_name = "erd"
    template_path = "templates/erd/structure.yaml"
    
    def _run(self, context: dict) -> str:
        # Generate ERD structure
        erd_data = super()._run(context)
        
        # Generate Mermaid diagram
        mermaid_diagram = self._generate_mermaid(erd_data)
        
        # Combine
        return f"{erd_data}\n\n## ERD Diagram\n```mermaid\n{mermaid_diagram}\n```"
```

## Migration Checklist

### Per-Agent Migration Steps

- [ ] **1. Extract Core Logic**
  - [ ] Identify agent's primary functions
  - [ ] Extract question frameworks
  - [ ] Document validation rules
  - [ ] Note state dependencies

- [ ] **2. Create CrewAI Agent**
  - [ ] Define role, goal, and backstory
  - [ ] Set appropriate LLM model
  - [ ] Configure delegation settings
  - [ ] Add memory if needed

- [ ] **3. Convert Templates to Tools**
  - [ ] Create tool class for each template
  - [ ] Migrate validation logic
  - [ ] Implement LLM enhancement
  - [ ] Add error handling

- [ ] **4. Define Tasks**
  - [ ] Create task for each major function
  - [ ] Set clear expected outputs
  - [ ] Define task dependencies
  - [ ] Configure async execution

- [ ] **5. Test Migration**
  - [ ] Unit test each tool
  - [ ] Test agent in isolation
  - [ ] Test full crew execution
  - [ ] Validate output quality

### System-Level Migration

- [ ] **1. WebSocket Integration**
  - [ ] Implement streaming callbacks
  - [ ] Add progress tracking
  - [ ] Handle errors gracefully
  - [ ] Test real-time updates

- [ ] **2. Database Integration**
  - [ ] Migrate from Redis to in-memory/DB hybrid
  - [ ] Update conversation storage
  - [ ] Maintain document versioning
  - [ ] Test persistence

- [ ] **3. API Compatibility**
  - [ ] Maintain existing endpoints
  - [ ] Add CrewAI-specific routes
  - [ ] Update response formats
  - [ ] Test backwards compatibility

- [ ] **4. Performance Testing**
  - [ ] Benchmark vs LangGraph
  - [ ] Monitor token usage
  - [ ] Test concurrent requests
  - [ ] Optimize bottlenecks

## Common Pitfalls and Solutions

### 1. State Management Complexity
**Problem**: LangGraph's complex state graph doesn't map directly to CrewAI  
**Solution**: Use task context and crew results instead of manual state passing

### 2. Question-Answer Flow
**Problem**: CrewAI doesn't have built-in question frameworks  
**Solution**: Implement as tools that return structured requirements

### 3. Phase Management
**Problem**: No explicit phases in CrewAI  
**Solution**: Use hierarchical process with orchestrator managing phases through task ordering

### 4. Document Dependencies
**Problem**: Some documents depend on others (e.g., SRS needs PRD)  
**Solution**: Use task context to pass outputs between agents

### 5. Validation Gates
**Problem**: No built-in validation between agents  
**Solution**: Add validation tools that can be called by the quality reviewer

## Testing Strategy

### 1. Unit Tests for Tools
```python
def test_prd_generator_tool():
    tool = PRDGeneratorTool()
    context = {
        "problem_statement": "Need internal tool for X",
        "target_users": "Engineering team",
        "requirements": ["Feature A", "Feature B"]
    }
    
    result = tool._run(context)
    assert "Problem Statement" in result
    assert "Target Users" in result
    assert len(result) > 1000  # Minimum content
```

### 2. Integration Tests for Agents
```python
async def test_product_manager_agent():
    pm = create_product_manager_agent()
    task = Task(
        description="Create PRD for internal tool",
        agent=pm,
        expected_output="Complete PRD document"
    )
    
    result = await task.execute()
    assert result.raw is not None
    validate_prd_structure(result.raw)
```

### 3. End-to-End Crew Tests
```python
async def test_full_documentation_crew():
    crew = create_full_documentation_crew()
    result = await crew.kickoff({
        "user_request": "Create documentation for employee portal"
    })
    
    assert "prd" in result.tasks_output
    assert "uxdd" in result.tasks_output
    assert "srs" in result.tasks_output
```

## Performance Optimization Tips

1. **Use Async Execution**: Enable `async_execution=True` for parallel tasks
2. **Implement Caching**: Cache template loading and common LLM calls
3. **Optimize Prompts**: Shorter, focused prompts reduce token usage
4. **Batch Operations**: Group similar operations when possible
5. **Memory Management**: Use CrewAI's memory only where needed

## Rollback Plan

If migration issues arise:

1. **Feature Flags**: Use flags to switch between LangGraph and CrewAI
2. **Parallel Operation**: Run both systems with traffic splitting
3. **Data Compatibility**: Ensure documents from both systems are compatible
4. **Quick Revert**: Keep LangGraph code ready for quick rollback

---

*Migration Guide Version: 1.0*  
*Last Updated: June 2025*  
*Next Step: Begin implementing core agent conversions*