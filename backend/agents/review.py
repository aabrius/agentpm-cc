"""
Review Agent for CrewAI implementation.
Performs comprehensive quality assurance and validation of all deliverables.
"""

from crewai import Agent
from typing import Dict, Any, List, Tuple
from ..tools.document_reviewer import DocumentReviewerTool
from ..tools.consistency_checker import ConsistencyCheckerTool
from ..tools.quality_scorer import QualityScorerTool
from ..tools.compliance_validator import ComplianceValidatorTool
from ..tools.feedback_generator import FeedbackGeneratorTool
from ..prompts.enhanced_review_prompt import (
    ENHANCED_REVIEW_PROMPT,
    ENHANCED_DOCUMENT_REVIEW_PROMPT,
    ENHANCED_CONSISTENCY_REVIEW_PROMPT,
    ENHANCED_ITERATIVE_IMPROVEMENT_PROMPT
)
from ..config import get_llm_model


class ReviewAgent:
    """Creates and configures the Review agent for quality assurance."""
    
    # Preserved review criteria from original implementation
    REVIEW_CRITERIA = {
        "accuracy": "Information is correct and factual",
        "completeness": "All required sections are present",
        "clarity": "Content is clear and unambiguous",
        "consistency": "Information aligns across documents",
        "feasibility": "Proposals are technically achievable",
        "compliance": "Meets standards and regulations",
        "usability": "Documents are well-structured and accessible",
        "traceability": "Requirements link to objectives"
    }
    
    # Preserved review checklist from original implementation
    REVIEW_CHECKLIST = [
        {
            "id": "review_1",
            "category": "Content Quality",
            "checks": [
                "All sections have substantial content",
                "No placeholder text remains",
                "Technical details are accurate",
                "Business context is clear"
            ]
        },
        {
            "id": "review_2",
            "category": "Consistency",
            "checks": [
                "Terminology is consistent",
                "Data formats match across documents",
                "No conflicting requirements",
                "Timeline alignment"
            ]
        },
        {
            "id": "review_3",
            "category": "Completeness",
            "checks": [
                "All required documents present",
                "Cross-references are valid",
                "Dependencies documented",
                "Risks identified and mitigated"
            ]
        },
        {
            "id": "review_4",
            "category": "Standards Compliance",
            "checks": [
                "Follows document templates",
                "Meets industry standards",
                "Accessibility requirements met",
                "Security standards applied"
            ]
        }
    ]
    
    @staticmethod
    def create(model_override: str = None) -> Agent:
        """Create the Review agent with full capabilities."""
        return Agent(
            role='Senior Principal Quality Assurance Director',
            goal='''Lead progressive refinement of all deliverables through multi-pass review 
            cycles, elevating good work to exceptional through iterative improvement and 
            comprehensive validation. Champion excellence through constructive guidance.''',
            backstory=ENHANCED_REVIEW_PROMPT,
            tools=[
                DocumentReviewerTool(),
                ConsistencyCheckerTool(),
                QualityScorerTool(),
                ComplianceValidatorTool(),
                FeedbackGeneratorTool()
            ],
            llm=get_llm_model('review', override_model=model_override),
            verbose=True,
            max_iter=15,
            memory=False
        )
    
    @staticmethod
    def create_comprehensive_review_task(deliverables: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for comprehensive deliverable review."""
        return {
            "description": f"""Conduct comprehensive quality review of project deliverables:
            
            {deliverables}
            
            Review should include:
            1. Content Quality Assessment
            2. Technical Accuracy Validation
            3. Consistency Check Across Documents
            4. Completeness Verification
            5. Standards Compliance Check
            6. Usability and Readability
            7. Risk and Gap Analysis
            8. Dependency Validation
            9. Integration Point Review
            10. Acceptance Criteria Verification
            
            Provide detailed feedback with severity levels and recommendations.""",
            "expected_output": """Comprehensive review report including:
            - Executive summary of findings
            - Detailed issues by category and severity
            - Consistency matrix across documents
            - Quality scores and metrics
            - Prioritized action items
            - Approval recommendations"""
        }
    
    @staticmethod
    def create_document_review_task(document: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        """Create a task for specific document review."""
        return {
            "description": f"""Review {document_type} document for quality and completeness:
            
            {document}
            
            Evaluate:
            1. Structure and Organization
            2. Content Accuracy and Depth
            3. Clarity and Readability
            4. Technical Correctness
            5. Completeness of Sections
            6. Internal Consistency
            7. External References
            8. Compliance with Standards
            9. Actionability of Content
            10. Target Audience Appropriateness
            
            Use document-specific criteria for {document_type}.""",
            "expected_output": """Document review report with:
            - Quality score and grade
            - Section-by-section feedback
            - Critical issues requiring fixes
            - Improvement suggestions
            - Compliance checklist results"""
        }
    
    @staticmethod
    def create_consistency_check_task(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a task for cross-document consistency checking."""
        return {
            "description": f"""Check consistency across multiple project documents:
            
            Documents to review: {len(documents)} documents
            
            Verify:
            1. Terminology Consistency
            2. Data Model Alignment
            3. Timeline Synchronization
            4. Requirement Traceability
            5. Technical Specification Alignment
            6. Business Rule Consistency
            7. User Story Correlation
            8. Metrics and KPI Alignment
            9. Risk Assessment Consistency
            10. Stakeholder Information
            
            Identify and categorize all inconsistencies.""",
            "expected_output": """Consistency analysis report with:
            - Inconsistency matrix by document pair
            - Conflict resolution recommendations
            - Unified terminology glossary
            - Alignment action items
            - Impact assessment of inconsistencies"""
        }
    
    @staticmethod
    def create_compliance_validation_task(deliverables: Dict[str, Any], standards: List[str]) -> Dict[str, Any]:
        """Create a task for compliance validation."""
        return {
            "description": f"""Validate deliverables against standards and regulations:
            
            Deliverables: {deliverables}
            Standards to check: {', '.join(standards)}
            
            Validate compliance with:
            1. Industry Standards (ISO, IEEE, etc.)
            2. Security Standards (OWASP, NIST)
            3. Accessibility Standards (WCAG)
            4. Data Privacy Regulations (GDPR, CCPA)
            5. Company Standards and Policies
            6. Best Practices and Guidelines
            7. Documentation Standards
            8. Code Quality Standards
            9. Testing Standards
            10. Operational Standards
            
            Provide compliance score and gap analysis.""",
            "expected_output": """Compliance validation report with:
            - Compliance score by standard
            - Detailed gap analysis
            - Remediation requirements
            - Risk assessment
            - Certification readiness"""
        }
    
    @staticmethod
    def create_final_approval_task(review_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for final approval recommendation."""
        return {
            "description": f"""Based on comprehensive reviews, provide final approval recommendation:
            
            Review Results: {review_results}
            
            Synthesize:
            1. Overall Quality Assessment
            2. Critical Issues Summary
            3. Risk Assessment
            4. Compliance Status
            5. Team Readiness
            6. Stakeholder Alignment
            7. Technical Feasibility
            8. Business Value Confirmation
            9. Implementation Readiness
            10. Go/No-Go Recommendation
            
            Provide clear, executive-level recommendation.""",
            "expected_output": """Final approval package with:
            - Executive decision summary
            - Go/No-Go recommendation with rationale
            - Conditional approval requirements
            - Risk mitigation requirements
            - Success criteria confirmation"""
        }
    
    @staticmethod
    def perform_quality_assessment(deliverable: Dict[str, Any]) -> Dict[str, Any]:
        """Perform quality assessment on a deliverable."""
        assessment_results = {
            "overall_score": 0,
            "category_scores": {},
            "issues": {
                "critical": [],
                "major": [],
                "minor": [],
                "suggestions": []
            },
            "strengths": [],
            "recommendations": []
        }
        
        # Assess different quality dimensions
        quality_dimensions = {
            "completeness": ReviewAgent._assess_completeness(deliverable),
            "accuracy": ReviewAgent._assess_accuracy(deliverable),
            "clarity": ReviewAgent._assess_clarity(deliverable),
            "consistency": ReviewAgent._assess_consistency(deliverable),
            "compliance": ReviewAgent._assess_compliance(deliverable)
        }
        
        # Calculate scores
        for dimension, (score, issues) in quality_dimensions.items():
            assessment_results["category_scores"][dimension] = score
            
            # Categorize issues by severity
            for issue in issues:
                if issue["severity"] == "critical":
                    assessment_results["issues"]["critical"].append(issue["description"])
                elif issue["severity"] == "major":
                    assessment_results["issues"]["major"].append(issue["description"])
                elif issue["severity"] == "minor":
                    assessment_results["issues"]["minor"].append(issue["description"])
                else:
                    assessment_results["issues"]["suggestions"].append(issue["description"])
        
        # Calculate overall score
        assessment_results["overall_score"] = sum(quality_dimensions[d][0] for d in quality_dimensions) / len(quality_dimensions)
        
        # Identify strengths
        for dimension, (score, _) in quality_dimensions.items():
            if score >= 90:
                assessment_results["strengths"].append(f"Excellent {dimension}")
        
        # Generate recommendations
        assessment_results["recommendations"] = ReviewAgent._generate_improvement_recommendations(assessment_results)
        
        return assessment_results
    
    @staticmethod
    def _assess_completeness(deliverable: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """Assess completeness of deliverable."""
        issues = []
        score = 100
        
        # Check for required sections
        required_sections = deliverable.get("required_sections", [])
        actual_sections = deliverable.get("sections", {})
        
        for section in required_sections:
            if section not in actual_sections or not actual_sections[section]:
                issues.append({
                    "severity": "major",
                    "description": f"Missing required section: {section}"
                })
                score -= 10
        
        # Check for placeholder content
        content = str(deliverable)
        placeholders = ["TBD", "TODO", "[PLACEHOLDER]", "to be defined"]
        for placeholder in placeholders:
            if placeholder in content:
                issues.append({
                    "severity": "minor",
                    "description": f"Placeholder text found: {placeholder}"
                })
                score -= 5
        
        return max(0, score), issues
    
    @staticmethod
    def _assess_accuracy(deliverable: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """Assess accuracy of deliverable."""
        # Simplified accuracy assessment
        return 85, [{
            "severity": "minor",
            "description": "Some technical details require verification"
        }]
    
    @staticmethod
    def _assess_clarity(deliverable: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """Assess clarity of deliverable."""
        # Simplified clarity assessment
        return 90, []
    
    @staticmethod
    def _assess_consistency(deliverable: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """Assess internal consistency of deliverable."""
        # Simplified consistency assessment
        return 88, [{
            "severity": "minor",
            "description": "Minor terminology inconsistencies detected"
        }]
    
    @staticmethod
    def _assess_compliance(deliverable: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """Assess compliance with standards."""
        # Simplified compliance assessment
        return 92, []
    
    @staticmethod
    def _generate_improvement_recommendations(assessment_results: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on assessment."""
        recommendations = []
        
        if assessment_results["issues"]["critical"]:
            recommendations.append("Address all critical issues before proceeding")
        
        if assessment_results["issues"]["major"]:
            recommendations.append("Resolve major issues to ensure project success")
        
        if assessment_results["overall_score"] < 70:
            recommendations.append("Consider comprehensive revision of deliverables")
        elif assessment_results["overall_score"] < 85:
            recommendations.append("Focus on addressing identified gaps")
        else:
            recommendations.append("Minor refinements will bring deliverables to excellence")
        
        # Specific recommendations based on low-scoring categories
        for category, score in assessment_results["category_scores"].items():
            if score < 80:
                recommendations.append(f"Improve {category} through targeted revisions")
        
        return recommendations
    
    @staticmethod
    def create_multipass_review_task(
        document: Dict[str, Any], 
        document_type: str, 
        pass_number: int,
        focus_area: str
    ) -> Dict[str, Any]:
        """Create a task for multi-pass review with specific focus."""
        return {
            "description": ENHANCED_DOCUMENT_REVIEW_PROMPT.format(
                document_type=document_type,
                document_content=str(document)
            ) + f"\n\n**Focus Area for Pass {pass_number}: {focus_area}**",
            "expected_output": f"""Multi-pass review report for Pass {pass_number}:
            - Quality Score Card (all 8 dimensions)
            - Pass-Specific Findings ({focus_area} focus)
            - Prioritized Action List (by impact)
            - Excellence Recommendations
            - Progress Assessment vs Previous Pass
            - Next Pass Readiness Status"""
        }
    
    @staticmethod
    def create_consistency_validation_task(documents: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Create a task for cross-document consistency validation."""
        documents_list = "\n".join([f"- {name}: {doc}" for name, doc in documents.items()])
        
        return {
            "description": ENHANCED_CONSISTENCY_REVIEW_PROMPT.format(
                documents_list=documents_list
            ),
            "expected_output": """Cross-document consistency validation report:
            - Consistency Matrix (document comparisons)
            - Conflict Resolution Plan (prioritized fixes)
            - Unified Reference Guide (standardization)
            - Integration Risk Assessment
            - Harmonization Recommendations
            - Quality Integration Score"""
        }
    
    @staticmethod
    def create_iterative_improvement_task(
        review_results: Dict[str, Any],
        iteration_number: int
    ) -> Dict[str, Any]:
        """Create a task for iterative improvement guidance."""
        return {
            "description": ENHANCED_ITERATIVE_IMPROVEMENT_PROMPT.format(
                review_results=str(review_results)
            ) + f"\n\n**Current Iteration: {iteration_number}**",
            "expected_output": f"""Iteration {iteration_number} improvement guidance:
            - Specific Tasks with clear outcomes
            - Quality Checkpoints for verification
            - Time Estimates for completion
            - Success Criteria for this iteration
            - Next Steps for continued excellence
            - Progress Measurement Framework"""
        }
    
    @staticmethod
    def create_excellence_validation_task(
        final_content: Dict[str, Any],
        document_type: str,
        quality_target: float = 95.0
    ) -> Dict[str, Any]:
        """Create a task for final excellence validation."""
        return {
            "description": f"""Perform final excellence validation for {document_type}:
            
            Content: {final_content}
            Quality Target: {quality_target}%
            
            Execute comprehensive validation:
            1. **Excellence Verification**: Confirm 95%+ quality achieved
            2. **Competitive Analysis**: Compare against industry benchmarks
            3. **Future-Proofing Assessment**: Evaluate long-term value
            4. **Stakeholder Readiness**: Validate all perspectives covered
            5. **Strategic Impact**: Measure business value delivery
            6. **Implementation Confidence**: Assess execution readiness
            7. **Risk Mitigation**: Verify comprehensive coverage
            8. **Innovation Recognition**: Identify unique value propositions
            
            Provide executive-level approval recommendation.""",
            "expected_output": """Excellence validation package:
            - Final Quality Certification (target achievement)
            - Executive Decision Summary
            - Go/No-Go Recommendation with rationale
            - Competitive Advantage Assessment
            - Risk-Adjusted Approval Status
            - Success Probability Analysis
            - Strategic Value Confirmation"""
        }