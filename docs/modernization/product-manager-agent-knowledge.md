# Product Manager Agent Knowledge Documentation

## Agent Overview

**Agent ID**: `pm_agent_01`  
**Agent Type**: `product_manager`  
**Primary Role**: Senior Product Manager with 15+ years experience specializing in business requirements and comprehensive product documentation

## Core Competencies

### Document Types Supported
- **PRD (Product Requirements Document)**: Primary expertise
- **FRD (Feature Requirements Document)**: Feature-specific requirements
- **Product Vision**: Strategic product direction and goals
- **Epic**: High-level user story collections

### Domain Expertise
- Business value analysis and stakeholder needs assessment
- Market analysis and competitive positioning
- User persona development and journey mapping
- Feature prioritization and MVP definition
- Success metrics and KPI definition
- Risk assessment and mitigation strategies

## LLM Configuration

### Model Settings
- **Model**: Claude 3 Opus (`claude-3-opus-20240229`)
- **Temperature**: 0.7 (higher creativity for business strategy)
- **Max Tokens**: 3000 (extended for comprehensive documents)
- **Langfuse Integration**: Full observability and token tracking

### System Prompt Intelligence
```
You are a Senior Product Manager with 15+ years of experience creating comprehensive product documentation including PRDs, FRDs, Product Vision documents, and Epics.

Your expertise includes:
- Business value analysis and stakeholder needs assessment
- Market analysis and competitive positioning
- User persona development and journey mapping
- Feature prioritization and MVP definition
- Success metrics and KPI definition
- Risk assessment and mitigation strategies

You ask thoughtful, probing questions that uncover:
- The core problem and its impact
- User needs and pain points
- Business objectives and constraints
- Market opportunities and competitive landscape
- Success criteria and measurement

When generating questions:
1. Start with high-level business context
2. Drill down into specific user needs
3. Ensure alignment between business goals and user value
4. Focus on measurable outcomes
5. Identify potential risks early
```

## Template-Based Intelligence

### PRD Template Structure (255 Lines)

#### Core Sections (10 sections):

1. **Executive Summary** (Required, Order: 1)
   - Questions: 4 essential questions covering problem, users, value proposition, goals
   - Key Questions:
     - "What is the core problem or opportunity you're addressing?"
     - "Who are the primary target users or customers?"
     - "What is the key value proposition or unique selling point?"
     - "What are the main goals you want to achieve with this product?"

2. **Problem Statement** (Required, Order: 2)
   - Questions: 4 detailed analysis questions including frequency options
   - Key Questions:
     - "What specific pain points or challenges are users experiencing?"
     - "How are users currently solving or working around this problem?"
     - "What are the negative consequences or costs of not solving this problem?"
     - "How frequently do users encounter this problem?" (with options: Daily/Weekly/Monthly/Occasionally/Rarely)

3. **Target Users** (Required, Order: 3)
   - Questions: 4 persona and market questions (some dynamic)
   - Key Questions:
     - "Can you describe your primary user persona in detail?"
     - "Are there secondary user personas? If yes, please describe them."
     - "What is the estimated market size for your target users?"
     - "What are the key characteristics that define your target users?" (dynamic)

4. **User Stories** (Required, Order: 4)
   - Dynamic section with template: "As a {persona}, I want to {action} so that {benefit}"
   - Questions focus on capabilities and expected outcomes

5. **Functional Requirements** (Required, Order: 5)
   - **Subsections**:
     - Core Features: MVP vs nice-to-have features
     - User Interface Requirements: Platform selection and design principles
     - Integrations: System connections and API requirements

6. **Non-Functional Requirements** (Required, Order: 6)
   - **Subsections**:
     - Performance Requirements: Response times and concurrent users
     - Security Requirements: Data handling and compliance
     - Scalability Requirements: Growth expectations

7. **Acceptance Criteria** (Required, Order: 7)
   - Dynamic auto-generation with Given-When-Then template
   - Measurable criteria for each requirement

8. **Success Metrics** (Required, Order: 8)
   - KPIs and success indicators
   - Target values and tracking methods

9. **Risks and Mitigation** (Optional, Order: 9)
   - Technical and business risk assessment
   - Mitigation strategies

10. **Timeline and Milestones** (Optional, Order: 10)
    - Project timeline and critical milestones

#### Validation Rules:
- All required sections must be present
- Minimum 80% questions answered per section
- Minimum 3 user stories required
- 90% acceptance criteria coverage

#### Document Relationships:
- **Derives from**: Vision Document, Business Requirements
- **Informs**: FRD, Technical Specification, Test Plan
- **References**: Market Analysis, Competitive Analysis

### BRD Template Structure (255 Lines)

#### Core Sections (10 sections):

1. **Executive Summary** (Required)
   - Business need, objectives, impact, timeline

2. **Business Objectives** (Required)
   - Measurable goals, success metrics, KPIs, ROI

3. **Stakeholder Analysis** (Required)
   - Primary stakeholders, needs, involvement, communication

4. **Current State Analysis** (Required)
   - Existing processes, pain points, systems, limitations

5. **Future State Vision** (Required)
   - Ideal state, improvements, process changes, new capabilities

6. **Gap Analysis** (Required)
   - Current vs future state gaps, resources needed, technical/process gaps

7. **Business Requirements** (Required)
   - **Subsections**:
     - Functional Business Requirements
     - Non-Functional Business Requirements

8. **Constraints and Assumptions** (Optional)
   - Budget, timeline, resource constraints, key assumptions

9. **Risk Analysis** (Optional)
   - Business risks, impact assessment, mitigation strategies

10. **Success Criteria** (Required)
    - Project success definition, acceptance criteria, benefit realization

#### Validation Rules:
- All required sections present
- Minimum 75% questions answered per section
- Business objectives must be quantifiable
- Success criteria must be measurable

#### Document Relationships:
- **Derives from**: Vision Document, Market Analysis
- **Informs**: PRD, FRD, Project Plan, Test Plan
- **References**: Stakeholder Register, Risk Register

## Advanced Capabilities

### Dynamic Question Generation
The agent uses LLM-powered dynamic question generation when template questions are insufficient:

```python
async def _generate_dynamic_questions(self, state, context) -> List[Question]:
    """Generate dynamic questions using LLM based on conversation context"""
    # Uses conversation history to generate contextual follow-up questions
    # Focuses on uncovered areas
    # Generates 3 targeted questions per call
```

### Document Generation Intelligence

#### PRD Generation Process:
1. **Answer Organization**: Groups answers by template sections
2. **LLM Synthesis**: Uses LLM to synthesize Q&A pairs into professional prose
3. **Template Following**: Maintains formal structure with section headers
4. **Metadata Integration**: Includes generation metadata and agent attribution

#### Multi-Document Support:
- **PRD**: Comprehensive product requirements
- **FRD**: Feature-specific requirements  
- **Product Vision**: Strategic direction
- **Epic**: High-level story collections

### Progress Tracking System

```python
def _calculate_progress(self, state, doc_type="prd") -> Dict[str, Any]:
    """Calculate completion percentage and current section"""
    return {
        "percentage": completion_percentage,
        "answered": questions_answered,
        "total": total_required_questions,
        "current_section": current_section_id
    }
```

### Section Management Intelligence

```python
def _get_current_section(self, state, doc_type="prd") -> Optional[Dict[str, Any]]:
    """Intelligently determine next section to work on"""
    # Analyzes answered questions against template requirements
    # Returns first section with unanswered required questions
    # Enables systematic progression through document structure
```

## Question Generation Strategy

### Template-Based Questions
- Structured questions from YAML templates
- Required vs optional question handling
- Section-by-section progression
- Multi-choice options for specific questions

### Dynamic Question Generation
- LLM-generated follow-up questions based on conversation context
- Contextual question content based on previous answers
- Adaptive questioning to fill knowledge gaps
- Integration with conversation history analysis

### Question Types Supported
- **Template**: Pre-defined structured questions
- **Dynamic**: LLM-generated contextual questions
- **Single Select**: Multiple choice questions
- **Text**: Open-ended text responses

## Business Intelligence Features

### Stakeholder Analysis
- Primary and secondary stakeholder identification
- Stakeholder needs and expectations mapping
- Communication requirements planning
- Involvement strategy definition

### Risk Assessment
- Technical and business risk identification
- Impact analysis and probability assessment
- Mitigation strategy development
- Risk monitoring recommendations

### Success Metrics Definition
- KPI identification and definition
- Target value setting
- Measurement method specification
- Success criteria establishment

### Market and Competitive Analysis
- Target market sizing and segmentation
- Competitive landscape assessment
- Value proposition articulation
- Market opportunity identification

## Integration Capabilities

### Agent Communication
- Redis pub/sub message handling
- Document update broadcasting
- Inter-agent collaboration support
- State synchronization across agents

### Observability Integration
- Langfuse LLM call tracking
- Token usage monitoring
- Cost calculation and optimization
- Activity logging and analytics

### Template System Integration
- YAML template loading and parsing
- Dynamic template fallbacks
- Template validation and verification
- Cross-document relationship tracking

## Migration Considerations for CrewAI

### Current Strengths to Preserve
1. **Deep Template Knowledge**: Comprehensive PRD/BRD template expertise
2. **Business Strategy Expertise**: Market analysis and stakeholder assessment capabilities
3. **Dynamic Question Generation**: Contextual LLM-powered questioning
4. **Progress Tracking**: Systematic document completion monitoring
5. **Multi-Document Support**: Support for PRD, FRD, Product Vision, Epic generation

### Recommended CrewAI Mapping
```python
# Convert to CrewAI Product Manager Agent
pm_agent = Agent(
    role='Senior Product Manager',
    goal='Generate comprehensive product documentation through strategic questioning',
    backstory='''You are a Senior Product Manager with 15+ years of experience creating 
    comprehensive product documentation including PRDs, FRDs, Product Vision documents, and Epics.
    Your expertise includes business value analysis, market analysis, user persona development, 
    feature prioritization, and success metrics definition.''',
    tools=[prd_template_tool, brd_template_tool, dynamic_question_tool, progress_tracker_tool],
    llm=Claude35Sonnet(temperature=0.7),  # Higher creativity for business strategy
    max_tokens=3000,  # Extended for comprehensive documents
    verbose=True
)
```

### Key Intelligence to Transfer
- PRD and BRD template structures (255 lines each)
- Question generation algorithms (template + dynamic)
- Document synthesis capabilities
- Progress tracking and section management
- Business analysis methodologies
- Risk assessment frameworks

### Tools to Create for CrewAI
1. **PRD Template Tool**: Structured PRD generation with validation
2. **BRD Template Tool**: Business requirements documentation
3. **Dynamic Questioning Tool**: LLM-powered contextual questions
4. **Progress Tracking Tool**: Document completion monitoring
5. **Stakeholder Analysis Tool**: Stakeholder mapping and analysis
6. **Risk Assessment Tool**: Risk identification and mitigation

## Current Implementation Files
- `/backend/agents/product_manager.py` - Main PM agent implementation (564 lines)
- `/backend/templates/prd/structure.yaml` - PRD template (255 lines)
- `/backend/templates/brd/structure.yaml` - BRD template (255 lines)
- `/backend/templates/frd/structure.yaml` - FRD template
- `/backend/templates/product_vision/structure.yaml` - Product Vision template

---

*This documentation captures the Product Manager agent's comprehensive business intelligence and template expertise for preservation during the CrewAI migration.*