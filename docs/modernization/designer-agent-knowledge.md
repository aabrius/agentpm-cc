# Designer Agent Knowledge Documentation

## Agent Overview

**Agent ID**: `designer`  
**Agent Type**: `designer`  
**Primary Role**: UX/UI design specialist responsible for creating comprehensive design documentation and user experience specifications

## Core Competencies

### Document Types Supported
- **UXDD (User Experience Design Document)**: Primary expertise - comprehensive UX design specifications
- **Wireframe Documentation**: Screen layout and structure documentation
- **Design Requirements**: Detailed design specifications and constraints
- **UXSM (UX Site Map)**: Information architecture and navigation structure

### Domain Expertise
- User experience design and research methodology
- Information architecture and navigation design
- Visual design systems and component libraries
- Accessibility standards and WCAG compliance
- Responsive design and multi-platform considerations
- Interaction design patterns and micro-interactions
- Design handoff and developer collaboration

## LLM Configuration

### Model Settings
- **Model**: Uses system-configured LLM (typically Claude 3 Opus)
- **Temperature**: Not explicitly set (uses default)
- **Max Tokens**: Not explicitly set (uses default)
- **Enhancement**: LLM-powered content generation for professional documentation

### Core Design Philosophy
The Designer Agent focuses on creating actionable, developer-ready design documentation that bridges user needs with technical implementation. It emphasizes accessibility-first design, modern design systems, and comprehensive specification coverage.

## Template-Based Intelligence

### UXDD Template Structure (319 Lines)

#### Core Sections (11 sections):

1. **Design Overview** (Required, Order: 1)
   - Questions: 4 essential questions covering design vision, principles, UI paradigm, emotional response
   - Key Questions:
     - "What is the overall design vision for this product?"
     - "What design principles will guide the UX?"
     - "What is the primary user interface paradigm? (web, mobile, desktop, etc.)"
     - Options: Web Application, Mobile App (iOS/Android), Desktop Application, Responsive Web, Progressive Web App, Multi-platform

2. **User Research** (Required, Order: 2)
   - Questions: 4 research-focused questions covering research findings, pain points, user goals, behavior patterns
   - Key Questions:
     - "What user research has been conducted?"
     - "What are the key user pain points discovered?"
     - "What are the user goals and motivations?"

3. **User Personas** (Required, Order: 3)
   - Questions: 4 persona development questions (including 1 dynamic)
   - Key Questions:
     - "Describe the primary user persona (demographics, goals, frustrations)"
     - "What are the secondary user personas?"
     - "How do personas influence design decisions?" (dynamic)

4. **User Journey Maps** (Required, Order: 4)
   - Questions: 4 journey mapping questions focusing on workflows and touchpoints
   - Key Questions:
     - "What are the primary user journeys?"
     - "What are the key touchpoints in each journey?" (dynamic)
     - "What are the pain points in the current journey?"

5. **Information Architecture** (Required, Order: 5)
   - Questions: 5 structure and navigation questions
   - Key Questions:
     - "How will information be organized and structured?"
     - "What is the navigation structure?"
     - "What are the main sections/areas of the application?"
     - "How will users find what they're looking for?"

6. **Interaction Design** (Required, Order: 6)
   - **Subsections**:
     - Interaction Patterns: Primary patterns, feature interactions, gestures/shortcuts
     - Micro-interactions: Enhancement interactions, feedback systems, loading states

7. **Visual Design** (Required, Order: 7)
   - **Subsections**:
     - Design System: Framework, color palette, typography, spacing/grid system
     - Component Library: Core UI components, consistency maintenance, component states

8. **Wireframes and Mockups** (Required, Order: 8)
   - Questions: 4 layout and responsive design questions
   - Key Questions:
     - "What are the key screens that need to be designed?"
     - "Describe the layout for the main dashboard/home screen"
     - "What are the responsive breakpoints?"
     - "How will the design adapt to different screen sizes?"

9. **Accessibility** (Required, Order: 9)
   - Questions: 5 comprehensive accessibility questions
   - Key Questions:
     - "What WCAG level will be targeted? (A, AA, AAA)"
     - Options: WCAG 2.1 Level A/AA/AAA, WCAG 3.0
     - "How will the design support screen readers?"
     - "What keyboard navigation will be supported?"
     - "How will color contrast requirements be met?"

10. **Usability Testing** (Optional, Order: 10)
    - Questions: 4 testing strategy questions covering testing plans, tasks, metrics, feedback

11. **Design Handoff** (Required, Order: 11)
    - Questions: 4 developer handoff questions
    - Key Questions:
      - "What design tools will be used for handoff?"
      - Options: Figma, Sketch, Adobe XD, Framer, Other
      - "What assets need to be provided to developers?"
      - "What are the design specifications (spacing, sizing, etc.)?"

#### Validation Rules:
- All required sections must be present
- Minimum 80% questions answered per section
- At least 1 persona required
- At least 1 user journey required
- Accessibility compliance verification
- Responsive design specification required

#### Document Relationships:
- **Derives from**: User Research, BRD, PRD
- **Informs**: Wireframe Documentation, Design Requirements, Frontend Development
- **References**: Brand Guidelines, Design System, Competitor Analysis

### Additional Templates

#### Wireframe Documentation Template
- Project overview and UI paradigm specification
- Page/screen inventory and structure
- User flow documentation
- Design constraints and accessibility considerations

#### Design Requirements Template
- UI paradigm and design principles
- Brand guidelines integration
- Component library specifications
- Accessibility requirements (WCAG compliance)

#### UX Site Map Template
- Hierarchical information structure
- Navigation flow documentation
- User access level definitions
- External system integration points

## Advanced Capabilities

### Dynamic Question Generation
The agent supports both template-based and dynamic question generation:

```python
async def generate_questions(self, state, context) -> List[Question]:
    """Generate design-specific questions from templates and dynamic context"""
    # Template-based questions from YAML structure
    # Dynamic questions based on conversation context
    # Filtering of already-answered questions
```

### Document Generation Intelligence

#### Template-Driven Content Creation:
1. **Structure Mapping**: Maps answered questions to template sections
2. **LLM Enhancement**: Uses LLM to synthesize Q&A pairs into professional prose
3. **Section Processing**: Handles subsections and complex template structures
4. **Professional Formatting**: Maintains consistent document formatting with headers, metadata

#### Multi-Document Support:
- **UXDD**: Comprehensive user experience documentation
- **Wireframe Doc**: Screen-specific layout documentation
- **Design Requirements**: Technical design specifications
- **UX Site Map**: Information architecture documentation

### Progress Tracking System

```python
def _has_enough_info(self, state) -> bool:
    """Check if sufficient information exists for document generation"""
    # Validates presence of required design questions
    # Ensures core design decisions are captured
    # Triggers document generation when ready
```

### Question Classification
- **Template Questions**: Pre-defined structured questions from YAML templates
- **Dynamic Questions**: LLM-generated contextual questions based on conversation
- **Required vs Optional**: Systematic handling of mandatory design decisions
- **Multi-Choice Options**: Standardized options for common design decisions

## Business Intelligence Features

### User Experience Research
- User research methodology validation
- Pain point identification and documentation
- User goal and motivation mapping
- Behavior pattern analysis

### Design System Management
- Component library standardization
- Design token specification
- Brand guideline integration
- Consistency enforcement across designs

### Accessibility Excellence
- WCAG 2.1/3.0 compliance verification
- Screen reader support planning
- Keyboard navigation specification
- Color contrast requirement management
- Alternative text strategy development

### Responsive Design Strategy
- Multi-platform design approach
- Breakpoint definition and management
- Adaptive design specification
- Progressive enhancement planning

## Integration Capabilities

### Agent Communication
- LangGraph state machine integration
- Multi-agent document coordination
- State synchronization across design phases
- Context preservation throughout conversation

### Template System Integration
- YAML template loading and parsing
- Dynamic section processing
- Subsection handling for complex structures
- Validation rule enforcement

### LLM Enhancement Integration
- Professional content synthesis from Q&A pairs
- Context-aware content generation
- Fallback mechanisms for offline operation
- Error handling and graceful degradation

## Migration Considerations for CrewAI

### Current Strengths to Preserve
1. **Comprehensive Template System**: 11-section UXDD template with 300+ lines of structured questions
2. **Accessibility-First Approach**: Built-in WCAG compliance and inclusive design patterns
3. **Multi-Document Support**: Supports 4 different design document types
4. **LLM-Enhanced Content**: Professional document synthesis capabilities
5. **Modern Design System Integration**: Support for contemporary UI frameworks and design tools
6. **Developer Handoff Excellence**: Structured specifications for design-to-development workflow

### Recommended CrewAI Mapping
```python
# Convert to CrewAI UX Designer Agent
designer_agent = Agent(
    role='Senior UX/UI Designer',
    goal='Create comprehensive design documentation through structured UX methodology',
    backstory='''You are a Senior UX/UI Designer with expertise in user experience research, 
    information architecture, accessibility standards, and modern design systems. You specialize 
    in creating developer-ready design documentation that bridges user needs with technical 
    implementation requirements.''',
    tools=[uxdd_template_tool, wireframe_tool, accessibility_audit_tool, design_system_tool],
    llm=Claude35Sonnet(),
    verbose=True
)
```

### Key Intelligence to Transfer
- UXDD template structure (319 lines) with 11 comprehensive sections
- Accessibility-first design methodology
- Multi-platform responsive design patterns
- Design system and component library management
- User research integration techniques
- Developer handoff specifications

### Tools to Create for CrewAI
1. **UXDD Template Tool**: Complete UX design document generation with validation
2. **Wireframe Documentation Tool**: Screen layout and structure specification
3. **Accessibility Audit Tool**: WCAG compliance verification and recommendations
4. **Design System Tool**: Component library and design token management
5. **Information Architecture Tool**: Site mapping and navigation structure design
6. **Design Handoff Tool**: Developer-ready specification generation

## Current Implementation Files
- `/backend/agents/designer.py` - Main Designer agent implementation (484 lines)
- `/backend/templates/uxdd/structure.yaml` - UXDD template (319 lines)
- Additional template files referenced but not directly accessed in this documentation

## Design Philosophy Integration

### Modern UX Methodology
- User-centered design approach
- Evidence-based design decisions
- Iterative design and validation
- Cross-functional collaboration

### Technical Excellence
- Design system consistency
- Component-based architecture
- Performance-conscious design
- Accessibility compliance verification

### Developer Collaboration
- Specification-driven handoff
- Asset organization and delivery
- Implementation guidance
- Quality assurance integration

---

*This documentation captures the Designer Agent's comprehensive UX/UI design expertise and template-driven methodology for preservation during the CrewAI migration.*