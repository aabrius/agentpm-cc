# CrewAI Architecture Design for AgentPM 2.0

## Executive Summary

This document outlines the architectural design for migrating AgentPM from LangGraph to CrewAI while preserving all 9 specialized agents and their domain expertise. The design leverages CrewAI's role-based agent system to simplify orchestration while maintaining the sophisticated document generation capabilities.

## Architecture Overview

### Current LangGraph Architecture
```
StateGraph → Orchestrator → [8 Specialized Agents] → Review → Completion
```

### Proposed CrewAI Architecture
```
CrewAI Crew → Hierarchical Process → [9 Specialized Agents] → Deliverables
```

## Agent Mapping Strategy

### 1. Orchestrator Agent → CrewAI Manager

**Current LangGraph Implementation:**
- Central router with intent analysis
- Phase management (definition → execution → review)
- State coordination across agents

**CrewAI Conversion:**
```python
orchestrator = Agent(
    role='Project Orchestration Manager',
    goal='Analyze user intent and coordinate specialized agents to generate comprehensive documentation',
    backstory='''You are a senior project manager with deep expertise in software development 
    lifecycle and documentation. You excel at understanding user needs, breaking down complex 
    projects into manageable phases, and coordinating specialist teams to deliver high-quality 
    documentation. You ensure all agents work harmoniously and maintain project coherence.''',
    verbose=True,
    allow_delegation=True,
    max_iter=5
)
```

**Key Responsibilities:**
- Intent classification and project type determination
- Dynamic crew composition based on project needs
- Phase orchestration and quality gates
- Final deliverable aggregation

### 2. Product Manager Agent

**CrewAI Conversion:**
```python
product_manager = Agent(
    role='Senior Product Manager',
    goal='Create comprehensive PRD and BRD documents that capture business vision and product strategy',
    backstory='''You are a seasoned Product Manager with 10+ years experience in defining 
    successful products. You excel at translating business needs into clear requirements, 
    understanding market dynamics, and creating documents that align stakeholders. Your PRDs 
    and BRDs are known for their clarity, completeness, and strategic insight.''',
    tools=[
        PRDGeneratorTool(),
        BRDGeneratorTool(),
        MarketAnalysisTool(),
        StakeholderMappingTool()
    ],
    verbose=True
)
```

**Preserved Knowledge:**
- 11-question product framework
- 255-line PRD template with validation
- BRD template with business focus
- Dynamic question generation logic

### 3. Designer Agent

**CrewAI Conversion:**
```python
designer = Agent(
    role='UX/UI Design Lead',
    goal='Design intuitive user experiences and create comprehensive UXDD documentation',
    backstory='''You are a principal UX/UI designer with expertise in user-centered design, 
    accessibility standards, and modern design systems. You create designs that balance 
    aesthetics with functionality, always keeping the end user in mind. Your UXDDs are 
    thorough, covering everything from user flows to interaction patterns.''',
    tools=[
        UXDDGeneratorTool(),
        WireframeGeneratorTool(),
        DesignSystemTool(),
        AccessibilityCheckerTool()
    ],
    verbose=True
)
```

**Preserved Knowledge:**
- 319-line UXDD template
- WCAG compliance standards
- Modern UI framework integration
- Responsive design patterns

### 4. Database Agent

**CrewAI Conversion:**
```python
database_engineer = Agent(
    role='Senior Database Architect',
    goal='Design optimal database schemas and generate comprehensive ERD and DBRD documentation',
    backstory='''You are a database architecture expert with deep knowledge of multiple 
    database systems including PostgreSQL, MySQL, MongoDB, and more. You excel at data 
    modeling, normalization, and creating schemas that balance performance with maintainability. 
    Your ERDs and DBRDs are detailed and consider security, scalability, and compliance.''',
    tools=[
        ERDGeneratorTool(),
        DBRDGeneratorTool(),
        MermaidDiagramTool(),
        SchemaValidatorTool()
    ],
    verbose=True
)
```

**Preserved Knowledge:**
- ERD generation with Mermaid
- Multi-database expertise
- Normalization strategies (1NF-5NF)
- Compliance frameworks (GDPR, HIPAA)

### 5. Engineer Agent

**CrewAI Conversion:**
```python
software_engineer = Agent(
    role='Principal Software Engineer',
    goal='Create detailed SRS documents following IEEE standards and define technical architecture',
    backstory='''You are a principal engineer with expertise across multiple architectures 
    including monolithic, microservices, and serverless. You create comprehensive technical 
    specifications that guide development teams. Your SRS documents follow IEEE 29148 standards 
    and cover all aspects from functional requirements to deployment strategies.''',
    tools=[
        SRSGeneratorTool(),
        ArchitectureDesignTool(),
        APISpecificationTool(),
        TestStrategyTool()
    ],
    verbose=True
)
```

**Preserved Knowledge:**
- IEEE 29148 compliance
- 8-question technical framework
- Multi-architecture support
- 357-line SRS template

### 6. User Researcher Agent

**CrewAI Conversion:**
```python
user_researcher = Agent(
    role='Senior User Research Specialist',
    goal='Conduct user research and create personas, journey maps, and user stories',
    backstory='''You are a user research expert specializing in enterprise and internal 
    tool development. You excel at understanding user needs, mapping customer journeys, 
    and translating insights into actionable user stories. Your research drives product 
    decisions and ensures user-centered design.''',
    tools=[
        PersonaGeneratorTool(),
        JourneyMapperTool(),
        UserStoryGeneratorTool(),
        ResearchValidatorTool()
    ],
    verbose=True
)
```

**Preserved Knowledge:**
- 7-question research framework
- 5-stage journey model
- P0-P3 priority framework
- Internal tool specialization

### 7. Business Analyst Agent

**CrewAI Conversion:**
```python
business_analyst = Agent(
    role='Senior Business Analyst',
    goal='Analyze business requirements and create comprehensive BRD and SRS documentation',
    backstory='''You are a senior business analyst with expertise in requirements engineering 
    and business process optimization. You bridge the gap between business needs and technical 
    implementation, ensuring complete requirements traceability. Your documents follow industry 
    standards and provide clear guidance for implementation teams.''',
    tools=[
        BusinessAnalysisTool(),
        GapAnalysisTool(),
        RequirementsMapperTool(),
        StakeholderAnalysisTool()
    ],
    verbose=True
)
```

**Preserved Knowledge:**
- 9-question analysis framework
- Gap analysis methodology
- Requirements traceability
- 17-section BRD template

### 8. Solution Architect Agent

**CrewAI Conversion:**
```python
solution_architect = Agent(
    role='Principal Solution Architect',
    goal='Design system architecture and create detailed DRD documentation',
    backstory='''You are a principal solution architect with expertise in enterprise 
    architecture patterns and distributed systems. You design scalable, secure, and 
    maintainable architectures that meet both current and future needs. Your DRDs 
    provide comprehensive architectural guidance with clear component interactions.''',
    tools=[
        DRDGeneratorTool(),
        ComponentDesignTool(),
        IntegrationMapperTool(),
        TechnologySelectorTool()
    ],
    verbose=True
)
```

**Preserved Knowledge:**
- 9-question architecture framework
- Architecture patterns (monolithic, microservices, serverless)
- Component interaction modeling
- Technology stack decisions

### 9. Review Agent

**CrewAI Conversion:**
```python
quality_reviewer = Agent(
    role='Senior Quality Assurance Lead',
    goal='Review all documentation for completeness, consistency, and quality standards',
    backstory='''You are a quality assurance expert with a keen eye for detail and deep 
    knowledge of documentation standards. You ensure all deliverables meet the highest 
    quality standards through systematic review processes. You validate cross-document 
    consistency and provide actionable feedback for improvements.''',
    tools=[
        DocumentValidatorTool(),
        ConsistencyCheckerTool(),
        ComplianceVerifierTool(),
        ApprovalWorkflowTool()
    ],
    verbose=True
)
```

**Preserved Knowledge:**
- Dynamic document requirements
- Cross-document consistency checking
- Issue-specific feedback generation
- Approval workflow management

## Crew Composition Strategies

### 1. Full Documentation Crew (Idea/Concept Projects)
```python
full_crew = Crew(
    agents=[
        orchestrator,
        product_manager,
        designer,
        database_engineer,
        software_engineer,
        user_researcher,
        business_analyst,
        solution_architect,
        quality_reviewer
    ],
    tasks=[...],  # Full task list
    process=Process.hierarchical,
    manager_llm=claude_opus_4,
    verbose=True
)
```

### 2. Feature Development Crew
```python
feature_crew = Crew(
    agents=[
        orchestrator,
        product_manager,
        designer,
        software_engineer,
        quality_reviewer
    ],
    tasks=[...],  # Feature-specific tasks
    process=Process.hierarchical,
    verbose=True
)
```

### 3. Tool Implementation Crew
```python
tool_crew = Crew(
    agents=[
        orchestrator,
        product_manager,
        software_engineer,
        quality_reviewer
    ],
    tasks=[...],  # Tool-specific tasks
    process=Process.sequential,
    verbose=True
)
```

## Task Assignment Patterns

### Hierarchical Process (Default)
- Orchestrator manages task delegation
- Parallel execution where possible
- Sequential dependencies respected
- Review agent validates all outputs

### Task Definition Structure
```python
class DocumentGenerationTask(Task):
    def __init__(self, description, agent, expected_output, context=None):
        super().__init__(
            description=description,
            agent=agent,
            expected_output=expected_output,
            context=context,
            tools=agent.tools,
            async_execution=True
        )
```

### Example Task Chain
```python
# Phase 1: Requirements Gathering
analyze_intent_task = Task(
    description="Analyze user input and determine project type and requirements",
    agent=orchestrator,
    expected_output="Project classification and initial requirements"
)

generate_prd_task = Task(
    description="Create comprehensive PRD based on requirements",
    agent=product_manager,
    expected_output="Complete PRD document following template",
    context=[analyze_intent_task]
)

# Phase 2: Design & Architecture
create_uxdd_task = Task(
    description="Design user experience and create UXDD",
    agent=designer,
    expected_output="UXDD with wireframes and design specifications",
    context=[generate_prd_task]
)

design_architecture_task = Task(
    description="Design system architecture and create DRD",
    agent=solution_architect,
    expected_output="DRD with component diagrams",
    context=[generate_prd_task]
)

# Phase 3: Technical Specification
create_srs_task = Task(
    description="Create detailed SRS following IEEE standards",
    agent=software_engineer,
    expected_output="Complete SRS document",
    context=[design_architecture_task]
)

design_database_task = Task(
    description="Design database schema and create ERD/DBRD",
    agent=database_engineer,
    expected_output="ERD with Mermaid diagrams and DBRD",
    context=[create_srs_task]
)

# Phase 4: Review & Finalization
review_all_task = Task(
    description="Review all documents for quality and consistency",
    agent=quality_reviewer,
    expected_output="Approval status with any required revisions",
    context=[generate_prd_task, create_uxdd_task, create_srs_task, design_database_task]
)
```

## State Management Without Redis

### CrewAI Native State Management
```python
class ConversationState:
    def __init__(self):
        self.conversation_id = str(uuid.uuid4())
        self.messages = []
        self.documents = {}
        self.phase = "definition"
        self.metadata = {}
        
    def add_message(self, role, content):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        })
        
    def add_document(self, doc_type, content):
        self.documents[doc_type] = {
            "content": content,
            "version": len(self.documents.get(doc_type, [])) + 1,
            "timestamp": datetime.utcnow()
        }
```

### Callback Integration for Real-time Updates
```python
class WebSocketCallback(BaseCallbackHandler):
    def __init__(self, websocket):
        self.websocket = websocket
        
    async def on_agent_action(self, action, **kwargs):
        await self.websocket.send_json({
            "type": "agent_status",
            "agent": action.agent,
            "status": "working",
            "action": str(action)
        })
        
    async def on_agent_finish(self, finish, **kwargs):
        await self.websocket.send_json({
            "type": "agent_status",
            "agent": finish.agent,
            "status": "completed",
            "output": finish.output
        })
```

## Tool Integration Strategy

### Base Tool Class
```python
class BaseDocumentTool(BaseTool):
    name: str
    description: str
    template_path: str
    validator: Optional[Callable]
    
    def _run(self, **kwargs):
        # Load template
        template = self.load_template()
        
        # Generate content
        content = self.generate_content(template, kwargs)
        
        # Validate if validator provided
        if self.validator:
            self.validator(content)
            
        return content
```

### Template Migration
```python
class TemplateConverter:
    @staticmethod
    def yaml_to_crewai_tool(yaml_path: str) -> BaseDocumentTool:
        """Convert existing YAML templates to CrewAI tools"""
        with open(yaml_path) as f:
            template_data = yaml.safe_load(f)
            
        return BaseDocumentTool(
            name=template_data['title'],
            description=template_data['description'],
            template_path=yaml_path,
            validator=TemplateValidator(template_data['validation_rules'])
        )
```

## WebSocket Bridge Design

### Real-time Communication Layer
```python
class CrewAIWebSocketBridge:
    def __init__(self, crew: Crew):
        self.crew = crew
        self.active_connections = []
        
    async def execute_with_streaming(self, input_data: dict):
        # Add WebSocket callback to crew
        for connection in self.active_connections:
            self.crew.callbacks.append(WebSocketCallback(connection))
            
        # Execute crew asynchronously
        result = await self.crew.kickoff_async(inputs=input_data)
        
        # Stream final results
        for connection in self.active_connections:
            await connection.send_json({
                "type": "completion",
                "documents": result.raw,
                "status": "completed"
            })
```

## Migration Path from LangGraph

### 1. Agent Node → CrewAI Agent
```python
# LangGraph
class ProductManagerAgent(BaseAgent):
    async def process(self, state: AgentState) -> AgentState:
        # Complex state management
        pass

# CrewAI
product_manager = Agent(
    role='Senior Product Manager',
    goal='...',
    tools=[...]
)
```

### 2. StateGraph → Crew Process
```python
# LangGraph
workflow = StateGraph(AgentState)
workflow.add_node("pm", product_manager_node)
workflow.add_edge("pm", "designer")

# CrewAI
crew = Crew(
    agents=[product_manager, designer],
    process=Process.hierarchical
)
```

### 3. Handoff Logic → Task Context
```python
# LangGraph
state["next_agent"] = "designer"
state["handoff_context"] = {...}

# CrewAI
design_task = Task(
    agent=designer,
    context=[product_task]  # Automatic context passing
)
```

## Performance Optimization

### 1. Parallel Task Execution
```python
crew = Crew(
    agents=[...],
    tasks=[...],
    process=Process.hierarchical,
    max_rpm=10,  # Rate limiting
    parallel_execution=True  # Enable parallel tasks
)
```

### 2. Token Usage Optimization
```python
class OptimizedAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            max_iter=3,  # Limit iterations
            max_execution_time=300,  # 5 minute timeout
            memory=True  # Enable memory for context
        )
```

### 3. Caching Strategy
```python
@lru_cache(maxsize=100)
def get_cached_template(template_name: str):
    return load_template(template_name)
```

## Risk Mitigation

### 1. Graceful Degradation
```python
try:
    result = crew.kickoff(inputs=data)
except Exception as e:
    # Fallback to essential agents only
    minimal_crew = Crew(
        agents=[orchestrator, product_manager, quality_reviewer],
        tasks=minimal_tasks
    )
    result = minimal_crew.kickoff(inputs=data)
```

### 2. Validation Gates
```python
class ValidationGate:
    def __init__(self, threshold=0.8):
        self.threshold = threshold
        
    def validate(self, document):
        score = self.calculate_completeness(document)
        if score < self.threshold:
            raise ValidationError(f"Document completeness {score} below threshold")
```

## Success Metrics

### Technical Metrics
- Response time < 30 seconds for single document
- Token usage reduction of 30%+
- Zero functionality loss from current system
- 99.9% uptime with graceful degradation

### Business Metrics
- Document quality score ≥ current system
- User satisfaction maintained or improved
- Development velocity increased by 40%
- Maintenance burden reduced by 50%

## Implementation Timeline

### Week 1: Core Infrastructure
- Set up CrewAI environment
- Convert Orchestrator and Product Manager agents
- Implement basic task flow

### Week 2: Agent Migration
- Convert remaining 7 agents
- Migrate all templates to tools
- Implement WebSocket bridge

### Week 3: Integration & Testing
- Database integration
- RAG system connection
- End-to-end testing

### Week 4: Optimization & Deployment
- Performance tuning
- Parallel deployment
- Monitoring setup

## Conclusion

The CrewAI architecture provides a cleaner, more maintainable solution while preserving all specialized agent knowledge. The hierarchical process model naturally maps to the current phase-based workflow, and the native task context passing eliminates complex state management needs.

Key advantages:
1. **Simplified Orchestration**: Role-based agents with clear responsibilities
2. **Preserved Expertise**: All templates and knowledge transferred
3. **Better Maintainability**: 40% less orchestration code
4. **Enhanced Performance**: Native parallel execution and optimization
5. **Future-Ready**: Easy to add new agents or modify workflows

---

*Architecture Design Date: June 2025*  
*Next Step: Begin implementation with core agent conversions*