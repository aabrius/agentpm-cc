# User Researcher Agent Knowledge Documentation

## Agent Overview

**Agent ID**: `user_researcher`  
**Agent Type**: `user_researcher`  
**Primary Role**: User research specialist responsible for creating user personas, journey maps, and user stories to guide product development decisions

## Core Competencies

### Document Types Supported
- **Persona**: Detailed user profiles with demographics, goals, pain points, and behavioral patterns
- **User Journey**: Stage-by-stage mapping of user experience and touchpoints
- **User Story**: Prioritized feature requirements from user perspective with acceptance criteria

### Domain Expertise
- User research methodologies and question design
- Persona development and demographic analysis
- Journey mapping across 5-stage user lifecycle
- User story creation with priority frameworks
- Pain point identification and opportunity analysis
- Success metrics definition from user perspective
- Technical capability assessment and accessibility considerations

## LLM Configuration

### Model Settings
- **Model**: Uses system-configured LLM (via `get_llm()`)
- **Focus**: User-centered design and research-driven insights
- **Integration**: Works seamlessly with Designer and Product Manager agents

### Core Research Philosophy
The User Researcher Agent emphasizes evidence-based user understanding through structured research methodologies. It generates actionable insights that inform design and product decisions, focusing on internal workflow optimization and employee experience enhancement.

## Research Question Framework

### Core Research Questions (7 questions):

#### Required Questions (4 questions - 80% completion threshold):
1. **research_1**: "Who are the primary users of this product?"
   - **Purpose**: User identification and segmentation
   - **Required**: True
   - **Impact**: Foundation for all research activities

2. **research_2**: "What are the main user goals and motivations?"
   - **Purpose**: Understanding user drivers and objectives
   - **Required**: True
   - **Impact**: Guides feature prioritization and value proposition

3. **research_3**: "What are the key pain points users experience?"
   - **Purpose**: Problem identification and opportunity mapping
   - **Required**: True
   - **Impact**: Drives solution design and improvement areas

4. **research_4**: "Describe the typical user journey or workflow."
   - **Purpose**: Process understanding and touchpoint mapping
   - **Required**: True
   - **Impact**: Enables journey optimization and experience design

#### Optional Questions (3 questions - Enhancement and depth):
5. **research_5**: "What are the user demographics and characteristics?"
   - **Purpose**: Persona enrichment and targeting
   - **Required**: False
   - **Impact**: Improves personalization and accessibility

6. **research_6**: "What are the user's technical capabilities?"
   - **Purpose**: Technical proficiency assessment
   - **Required**: False
   - **Impact**: Informs UI complexity and feature design

7. **research_7**: "What are the success metrics from the user's perspective?"
   - **Purpose**: User-defined success criteria
   - **Required**: False
   - **Impact**: Guides metrics definition and validation

## Document Generation Capabilities

### User Persona Generation

#### Structure and Content:
```python
async def _generate_persona(self, state) -> str:
    """Generate comprehensive user persona document"""
    # Primary user identification
    # Demographics and characteristics
    # Goals and motivations mapping
    # Pain points and frustrations analysis
    # Technical proficiency assessment
    # Success metrics definition
    # Representative quotes and scenarios
```

#### Template Features:
- **Primary User Profile**: Based on research_1 input
- **Demographics Section**: Enhanced by research_5 (optional)
- **Goals & Motivations**: Derived from research_2
- **Pain Points & Frustrations**: Based on research_3
- **Technical Proficiency**: From research_6 assessment
- **Success Metrics**: User-defined success criteria from research_7
- **Quote Section**: Representative user perspective
- **Scenario Section**: Typical use case description
- **Metadata**: Generation timestamp and version tracking

### User Journey Mapping

#### 5-Stage Journey Model:
```python
async def _generate_user_journey(self, state) -> str:
    """Generate comprehensive user journey map"""
    # 1. Awareness - Need discovery and solution awareness
    # 2. Consideration - Research and evaluation phase
    # 3. Acquisition - Sign-up and onboarding process
    # 4. Service/Usage - Regular usage patterns and adoption
    # 5. Loyalty/Advocacy - Continued engagement and referrals
```

#### Journey Stage Details:
1. **Awareness Stage**:
   - User becomes aware of their need
   - Trigger points identification
   - Information sources analysis

2. **Consideration Stage**:
   - Research and evaluation activities
   - Comparison with alternatives
   - Decision criteria establishment

3. **Acquisition Stage**:
   - Sign-up or purchase process
   - Onboarding experience design
   - Initial setup and configuration

4. **Service/Usage Stage**:
   - Regular usage patterns
   - Feature adoption progression
   - Support interactions and needs

5. **Loyalty/Advocacy Stage**:
   - Continued engagement strategies
   - Referrals and recommendations
   - Expansion of usage scenarios

#### Integration Features:
- **User Profile**: Based on research_1 findings
- **Journey Overview**: Structured from research_4 workflow description
- **Pain Points Mapping**: Integrated research_3 analysis across stages
- **Opportunities Section**: Improvement recommendations per stage

### User Story Generation

#### Story Structure and Framework:
```python
async def _generate_user_story(self, state) -> str:
    """Generate prioritized user stories with acceptance criteria"""
    # Epic definition from core user journey
    # Story structure: "As a [user], I want to [action], so that [benefit]"
    # Priority matrix (P0-P3) implementation
    # Acceptance criteria specification
```

#### Story Categories:
1. **User Registration Story**:
   - Focus: Quick account creation
   - Benefit: Immediate product access
   - Acceptance Criteria: Simple form, email verification, optional profile

2. **Primary Goal Achievement Story**:
   - Focus: Core user objective fulfillment
   - Benefit: Efficient problem solving
   - Acceptance Criteria: Clear goal path, minimal steps, automatic progress saving

3. **Problem Resolution Story**:
   - Focus: Quick help and support access
   - Benefit: Continued productivity without frustration
   - Acceptance Criteria: Contextual help, accessible support, proactive issue resolution

#### Priority Matrix Framework:
- **P0 (Must have)**: Critical for MVP functionality
- **P1 (Important)**: Significant value but not blocking
- **P2 (Nice to have)**: Enhancement features
- **P3 (Future)**: Long-term considerations

## Advanced Research Methodologies

### Information Sufficiency Validation
```python
def _has_enough_info(self, state) -> bool:
    """Validate research completeness for document generation"""
    # Requires 80% completion of required questions
    # Ensures research_1, research_2, research_3, research_4 are answered
    # Enables quality control for generated documents
```

### Context-Aware Processing
- **Phase Management**: Only processes during "definition" phase
- **Question State Management**: Tracks answered vs. pending questions
- **Document Triggering**: Intelligent timing for document generation
- **State Preservation**: Maintains conversation context across interactions

## Template Integration System

### Internal Tool User Persona Template
- **Specialized for Internal Workflows**: Optimized for employee-facing tools
- **Role-Based Structure**: Job title, department, team organization
- **Business Context**: Key responsibilities and organizational goals
- **Workflow Integration**: Typical scenarios and daily usage patterns
- **Success Metrics**: Performance indicators and satisfaction measures
- **Portuguese Language Support**: Localized content for Brazilian teams

### User Journey Template Features
- **MermaidJS Integration**: Visual flowchart generation for journey stages
- **YAML Structure Support**: Structured data representation
- **Emotional Mapping**: User sentiment tracking across journey stages
- **Systems Integration**: Supporting tools and team involvement
- **Assumptions & Constraints**: Context documentation and limitations
- **Revision History**: Version control and approval tracking

### User Story Template Components
- **Business Value Emphasis**: Clear value proposition for each story
- **Acceptance Criteria**: Testable conditions for completion
- **Dependency Tracking**: Related stories and prerequisite identification
- **Stakeholder Management**: Reviewer and approval workflow
- **Technical Considerations**: Performance, security, compliance notes

## Quality Assurance Framework

### Research Validation Rules
- **Minimum Completion**: 80% of required questions must be answered
- **Context Validation**: Ensures research depth and relevance
- **Document Readiness**: Validates sufficient information for generation
- **Quality Gates**: Prevents incomplete or low-quality document generation

### Agent Collaboration Patterns
- **Designer Integration**: Shares user insights for UX/UI design decisions
- **Product Manager Coordination**: Provides user perspective for PRD development
- **Business Analyst Support**: Supplies user requirements for SRS documentation
- **Seamless Handoffs**: Maintains context across agent transitions

## Migration Considerations for CrewAI

### Current Strengths to Preserve
1. **Structured Research Framework**: 7-question methodology with clear required vs. optional categorization
2. **Multi-Document Generation**: Support for 3 complementary document types
3. **5-Stage Journey Model**: Comprehensive user lifecycle mapping
4. **Priority Framework**: P0-P3 user story prioritization system
5. **Internal Tool Focus**: Specialization for employee-facing applications
6. **Quality Validation**: 80% completion threshold and information sufficiency checks

### Recommended CrewAI Mapping
```python
# Convert to CrewAI User Research Specialist Agent
user_researcher_agent = Agent(
    role='Senior User Researcher',
    goal='Conduct user research and create actionable personas, journey maps, and user stories',
    backstory='''You are a Senior User Researcher with expertise in user-centered design, 
    persona development, and journey mapping. You specialize in internal tool optimization 
    and employee experience research, creating evidence-based insights that guide product 
    development decisions and improve organizational workflow efficiency.''',
    tools=[persona_generator_tool, journey_mapping_tool, user_story_tool, research_validator_tool],
    llm=Claude35Sonnet(),
    verbose=True
)
```

### Key Intelligence to Transfer
- 7-question research framework with validation logic
- 5-stage user journey mapping methodology
- P0-P3 priority framework for user stories
- Internal tool persona specialization
- Quality assurance and completion validation
- Multi-document generation coordination

### Tools to Create for CrewAI
1. **Research Question Tool**: Systematic user research question generation and validation
2. **Persona Generator Tool**: Comprehensive user persona creation with internal tool focus
3. **Journey Mapping Tool**: 5-stage user journey documentation with MermaidJS visualization
4. **User Story Tool**: Prioritized user story generation with acceptance criteria
5. **Research Validator Tool**: Quality assurance and information sufficiency checking
6. **Insight Synthesis Tool**: Cross-document insight integration and analysis

## Current Implementation Files
- `/backend/agents/user_researcher.py` - Main User Researcher agent implementation (330 lines)
- `/docs/templates/persona.md` - Internal tool user persona template (Portuguese)
- `/docs/templates/user-journey.md` - Comprehensive journey mapping template with MermaidJS
- `/docs/templates/user-story.md` - User story template with business value focus

## Research Excellence Philosophy

### Evidence-Based Design
- **User-Centered Approach**: All decisions grounded in user research
- **Data-Driven Insights**: Quantifiable user feedback and behavior analysis
- **Iterative Improvement**: Continuous research and validation cycles
- **Cross-Functional Collaboration**: Research integration across product teams

### Internal Tool Specialization
- **Employee Experience Focus**: Optimized for workforce productivity
- **Workflow Integration**: Research aligned with business processes
- **Organizational Context**: Understanding of corporate structures and needs
- **Efficiency Metrics**: Success measurement tied to operational improvements

### Quality and Validation
- **Research Rigor**: Systematic methodology and validation frameworks
- **Documentation Standards**: Comprehensive and actionable research outputs
- **Stakeholder Alignment**: Research findings aligned with business objectives
- **Continuous Learning**: Research insights inform future investigation priorities

---

*This documentation captures the User Researcher Agent's comprehensive research methodologies, persona development expertise, and journey mapping capabilities for preservation during the CrewAI migration.*