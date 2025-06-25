# Review Agent Knowledge Documentation

## Agent Overview

**Agent ID**: `review`  
**Agent Type**: `review`  
**Primary Role**: Quality assurance specialist responsible for reviewing all generated documentation for completeness, consistency, and compliance with standards to ensure deliverable quality

## Core Competencies

### Document Types Supported
- **Review Reports**: Comprehensive review assessments of all generated documentation
- **Validation Feedback**: Issue identification and revision requirements
- **Approval Documentation**: Final sign-off and completion certification

### Domain Expertise
- Document completeness validation and quality assessment
- Cross-document consistency checking
- Placeholder text and incomplete content detection
- Requirements traceability validation
- Standards compliance verification
- Issue identification and revision guidance
- Multi-phase document review orchestration
- Stakeholder approval workflow management

## LLM Configuration

### Model Settings
- **Model**: Uses system-configured LLM (via `get_llm()`)
- **Focus**: Quality assurance and document validation
- **Integration**: Works seamlessly with all other agents as final quality gate

### Core Review Philosophy
The Review Agent emphasizes comprehensive quality assurance through systematic validation methodologies. It ensures all generated documentation meets completeness standards, maintains cross-document consistency, and provides actionable feedback for any identified issues before final approval.

## Review Process Framework

### Review Trigger Conditions
- **Phase Requirement**: Only activates during "review" phase
- **Document Readiness**: Checks for presence of all required documents
- **Conversation Type Awareness**: Adapts requirements based on project type

### Document Requirements by Conversation Type
```python
def _get_required_documents(self, state: AgentState) -> List[str]:
    """Dynamic document requirements based on conversation type"""
    # "idea" type: Full documentation suite (PRD, BRD, UXDD, SRS, ERD, DBRD)
    # "feature" type: Feature-focused documents (PRD, UXDD, SRS)
    # "tool" type: Tool-specific documents (PRD, SRS)
    # default: Minimum viable documentation (PRD only)
```

#### Document Requirements Matrix:
1. **Idea/Concept Projects** (Most Comprehensive):
   - Product Requirements Document (PRD)
   - Business Requirements Document (BRD)
   - UX Design Document (UXDD)
   - Software Requirements Specification (SRS)
   - Entity Relationship Diagram (ERD)
   - Database Requirements Document (DBRD)

2. **Feature Development Projects**:
   - Product Requirements Document (PRD)
   - UX Design Document (UXDD)
   - Software Requirements Specification (SRS)

3. **Tool Implementation Projects**:
   - Product Requirements Document (PRD)
   - Software Requirements Specification (SRS)

4. **Default/Other Projects**:
   - Product Requirements Document (PRD)

## Review Capabilities

### Missing Document Detection
```python
def _generate_review_questions(self, missing_docs: List[str]) -> List[Question]:
    """Generate validation questions for missing documents"""
    # Identifies missing required documents
    # Creates targeted questions for each missing document
    # Provides options to generate or skip documents
    # Maintains full document name mapping for clarity
```

#### Document Name Mapping:
- **prd**: "Product Requirements Document"
- **brd**: "Business Requirements Document"
- **uxdd**: "UX Design Document"
- **srs**: "Software Requirements Specification"
- **erd**: "Entity Relationship Diagram"
- **dbrd**: "Database Requirements Document"

### Document Validation Process
```python
async def _review_documents(self, state: AgentState) -> Dict[str, Any]:
    """Comprehensive document review and validation"""
    # Basic validation: Content length and completeness
    # Placeholder detection: "to be defined", "todo" markers
    # Cross-document consistency checking
    # Issue compilation and status determination
```

#### Validation Criteria:
1. **Content Completeness**:
   - Minimum content length threshold (100 characters)
   - Section completion verification
   - Required field population checks

2. **Placeholder Detection**:
   - Identifies "to be defined" markers
   - Catches "TODO" and incomplete sections
   - Flags temporary or draft content

3. **Cross-Document Consistency**:
   - Terminology alignment across documents
   - Requirement traceability validation
   - Technical specification consistency
   - Business objective alignment

### Review Results Structure
```python
{
    "status": "approved" | "needs_revision",
    "issues": ["list of identified issues"],
    "reviewed_at": "ISO timestamp"
}
```

### Revision Question Generation
```python
def _generate_revision_questions(self, review_results: Dict[str, Any]) -> List[Question]:
    """Generate targeted questions for addressing review issues"""
    # Creates specific questions for each identified issue
    # Provides context for issue resolution
    # Maintains issue tracking for revision workflow
```

## Quality Assurance Framework

### Review Workflow States
1. **Document Collection Phase**:
   - Inventory of generated documents
   - Requirement matching against conversation type
   - Missing document identification

2. **Validation Phase**:
   - Individual document quality checks
   - Cross-document consistency validation
   - Compliance and standards verification

3. **Issue Resolution Phase**:
   - Issue-specific question generation
   - Revision guidance and suggestions
   - Iterative improvement workflow

4. **Approval Phase**:
   - Final validation confirmation
   - Status marking as "completed"
   - Timestamp documentation for audit trail

### Question Types and Context
- **Validation Questions**: Missing document generation decisions
  - Type: "validation"
  - Options: ["Yes", "No, skip this document"]
  - Context: Document type and review phase

- **Clarifying Questions**: Issue resolution guidance
  - Type: "clarifying"
  - Context: Specific issue details and remediation options
  - Required: True for all identified issues

### Review Intelligence Features
- **Dynamic Requirements**: Adapts document requirements based on project type
- **Progressive Validation**: Checks documents in order of importance
- **Contextual Feedback**: Provides specific, actionable revision guidance
- **Approval Workflow**: Manages completion status and timestamps

## Agent Collaboration Patterns

### Review Agent as Quality Gate
- **Final Checkpoint**: Last agent in the workflow ensuring quality
- **Cross-Agent Validation**: Verifies outputs from all specialized agents
- **Feedback Loop**: Triggers revision cycles when issues are found
- **Completion Authority**: Only agent that can mark conversation as "completed"

### Integration with Other Agents
- **Product Manager**: Validates PRD completeness and business alignment
- **Business Analyst**: Checks BRD/SRS consistency and requirements coverage
- **Designer**: Ensures UXDD quality and design specifications
- **Database**: Verifies ERD/DBRD technical accuracy
- **Engineer**: Validates SRS implementation readiness
- **User Researcher**: Confirms user-centered design coverage
- **Solution Architect**: Checks architectural consistency

## Migration Considerations for CrewAI

### Current Strengths to Preserve
1. **Dynamic Document Requirements**: Conversation type-based requirement adaptation
2. **Comprehensive Validation**: Multi-criteria quality assessment framework
3. **Issue-Specific Feedback**: Targeted revision guidance generation
4. **Workflow State Management**: Clear progression through review phases
5. **Cross-Document Consistency**: Holistic quality assurance approach
6. **Approval Authority**: Final quality gate with completion control

### Recommended CrewAI Mapping
```python
# Convert to CrewAI Review Agent
review_agent = Agent(
    role='Senior Quality Assurance Specialist',
    goal='Review all documentation for completeness, consistency, and quality assurance',
    backstory='''You are a Senior Quality Assurance Specialist with expertise in technical 
    documentation review, standards compliance, and quality validation. You ensure all project 
    deliverables meet the highest quality standards through systematic review processes, 
    cross-document consistency checking, and actionable feedback generation. Your role is 
    critical as the final quality gate before project completion.''',
    tools=[document_validator_tool, consistency_checker_tool, issue_analyzer_tool, 
           revision_guide_tool, approval_workflow_tool, compliance_verifier_tool],
    llm=Claude35Sonnet(),
    verbose=True
)
```

### Key Intelligence to Transfer
- Dynamic document requirement framework by conversation type
- Comprehensive validation criteria and quality thresholds
- Placeholder and incomplete content detection patterns
- Cross-document consistency validation methodology
- Issue-specific revision question generation
- Approval workflow and completion state management

### Tools to Create for CrewAI
1. **Document Validator Tool**: Individual document quality assessment
2. **Consistency Checker Tool**: Cross-document alignment verification
3. **Issue Analyzer Tool**: Problem identification and categorization
4. **Revision Guide Tool**: Targeted feedback and improvement suggestions
5. **Approval Workflow Tool**: Final validation and completion management
6. **Compliance Verifier Tool**: Standards and requirements compliance checking
7. **Missing Document Detector Tool**: Required document inventory management

## Current Implementation Files
- `/backend/agents/review.py` - Main Review agent implementation (162 lines)

## Quality Assurance Excellence Philosophy

### Systematic Review Approach
- **Comprehensive Coverage**: Every document reviewed against multiple criteria
- **Consistency Focus**: Cross-document alignment and terminology validation
- **Actionable Feedback**: Specific, targeted guidance for improvements
- **Iterative Improvement**: Support for revision cycles until quality standards met

### Standards Compliance
- **Documentation Standards**: Adherence to industry best practices
- **Completeness Validation**: Ensuring all required sections populated
- **Placeholder Elimination**: Zero tolerance for incomplete content
- **Traceability Verification**: Requirements alignment across documents

### Continuous Quality Improvement
- **Feedback Loop Integration**: Learning from common issues
- **Process Refinement**: Evolving validation criteria based on outcomes
- **Stakeholder Satisfaction**: Ensuring deliverables meet expectations
- **Audit Trail Maintenance**: Complete documentation of review process

---

*This documentation captures the Review Agent's comprehensive quality assurance methodologies, validation frameworks, and approval workflow capabilities for preservation during the CrewAI migration.*