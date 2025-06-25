"""
Business Analyst Agent for CrewAI implementation.
Creates comprehensive business analysis and requirements documentation.
"""

from crewai import Agent
from typing import Dict, Any, List
from ..tools.srs_generator import SRSGeneratorTool
from ..tools.process_mapper import ProcessMapperTool
from ..tools.requirements_analyzer import RequirementsAnalyzerTool
from ..tools.gap_analyzer import GapAnalyzerTool
from ..tools.roi_calculator import ROICalculatorTool
from ..config import get_llm_model


class BusinessAnalystAgent:
    """Creates and configures the Business Analyst agent for requirements analysis."""
    
    # Preserved BA principles from original implementation
    BA_PRINCIPLES = {
        "clarity": "Requirements must be clear and unambiguous",
        "completeness": "Capture all stakeholder needs",
        "consistency": "Ensure requirements don't conflict",
        "testability": "Requirements must be verifiable",
        "traceability": "Link requirements to business objectives",
        "feasibility": "Requirements must be technically achievable",
        "prioritization": "Rank requirements by business value",
        "measurability": "Define success criteria for each requirement"
    }
    
    # Preserved business analysis questions from original implementation
    BA_QUESTIONS = [
        {
            "id": "ba_1",
            "content": "What are the business objectives and success criteria?",
            "required": True
        },
        {
            "id": "ba_2",
            "content": "What are the current business processes?",
            "required": True
        },
        {
            "id": "ba_3",
            "content": "What are the functional requirements?",
            "required": True
        },
        {
            "id": "ba_4",
            "content": "What are the non-functional requirements?",
            "required": True
        },
        {
            "id": "ba_5",
            "content": "What are the constraints and dependencies?",
            "required": True
        },
        {
            "id": "ba_6",
            "content": "What is the expected ROI and business value?",
            "required": False
        },
        {
            "id": "ba_7",
            "content": "What are the regulatory and compliance requirements?",
            "required": False
        },
        {
            "id": "ba_8",
            "content": "What are the change management considerations?",
            "required": False
        }
    ]
    
    @staticmethod
    def create(model_override: str = None) -> Agent:
        """Create the Business Analyst agent with full capabilities."""
        return Agent(
            role='Senior Business Analyst',
            goal='''Bridge business needs with technical solutions through comprehensive 
            analysis and documentation. Create clear requirements specifications that 
            ensure successful project delivery and stakeholder satisfaction.''',
            backstory='''You are a Senior Business Analyst with 15+ years of experience 
            translating complex business needs into actionable requirements. You've worked 
            across industries including finance, healthcare, retail, and technology, 
            successfully delivering projects worth millions in business value. Your expertise 
            includes business process modeling (BPMN), requirements elicitation, stakeholder 
            management, and change management. You excel at uncovering hidden requirements, 
            identifying process improvements, and ensuring solutions align with strategic 
            objectives. Your SRS documents are known for their clarity and completeness, 
            serving as the single source of truth for development teams. You're skilled 
            in various BA methodologies including Agile, Waterfall, and hybrid approaches. 
            You have a keen eye for identifying risks and dependencies early, and you're 
            adept at facilitating workshops to achieve stakeholder consensus.''',
            tools=[
                SRSGeneratorTool(),
                ProcessMapperTool(),
                RequirementsAnalyzerTool(),
                GapAnalyzerTool(),
                ROICalculatorTool()
            ],
            llm=get_llm_model('business_analyst', override_model=model_override),
            verbose=True,
            max_iter=15,
            memory=False
        )
    
    @staticmethod
    def create_srs_task(project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for generating Software Requirements Specification."""
        return {
            "description": f"""Create a comprehensive Software Requirements Specification (SRS) 
            based on the following project context:
            
            {project_context}
            
            The SRS should include:
            1. Introduction and Purpose
            2. Overall Description
            3. Functional Requirements
            4. Non-Functional Requirements
            5. System Features and Use Cases
            6. External Interface Requirements
            7. Performance Requirements
            8. Security Requirements
            9. Quality Attributes
            10. Constraints and Assumptions
            11. Acceptance Criteria
            12. Traceability Matrix
            13. Appendices (Glossary, References)
            
            Follow IEEE 830 standard and ensure all requirements are SMART 
            (Specific, Measurable, Achievable, Relevant, Time-bound).""",
            "expected_output": """A complete SRS document (3000-4000 words) that:
            - Clearly defines all system requirements
            - Provides detailed use cases with scenarios
            - Includes acceptance criteria for each requirement
            - Maintains traceability to business objectives
            - Is ready for technical team implementation"""
        }
    
    @staticmethod
    def create_process_mapping_task(business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for business process mapping."""
        return {
            "description": f"""Map current and future business processes for:
            
            {business_context}
            
            Create comprehensive process documentation including:
            1. Process Overview and Objectives
            2. Process Boundaries and Scope
            3. Stakeholders and Roles (RACI Matrix)
            4. Current State Process Maps (As-Is)
            5. Pain Points and Inefficiencies
            6. Future State Process Maps (To-Be)
            7. Gap Analysis
            8. Process Metrics and KPIs
            9. Exception Handling
            10. Integration Points
            11. Automation Opportunities
            12. Implementation Roadmap
            
            Use BPMN 2.0 notation for all process diagrams.""",
            "expected_output": """Complete process documentation with:
            - BPMN diagrams for all processes
            - Detailed process narratives
            - Efficiency improvement metrics
            - Change impact analysis
            - Implementation timeline"""
        }
    
    @staticmethod
    def create_gap_analysis_task(current_state: Dict[str, Any], desired_state: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for gap analysis."""
        return {
            "description": f"""Conduct comprehensive gap analysis between:
            
            Current State: {current_state}
            Desired State: {desired_state}
            
            Analysis should include:
            1. Capability Gaps
            2. Process Gaps
            3. Technology Gaps
            4. Skills and Resource Gaps
            5. Data and Information Gaps
            6. Compliance and Policy Gaps
            7. Performance Gaps
            8. Cultural and Change Readiness Gaps
            9. Risk Assessment
            10. Prioritized Action Plan
            11. Resource Requirements
            12. Success Metrics
            
            Provide specific, actionable recommendations for closing each gap.""",
            "expected_output": """Detailed gap analysis report with:
            - Gap identification matrix
            - Impact and effort assessment
            - Prioritized remediation plan
            - Resource allocation recommendations
            - Risk mitigation strategies"""
        }
    
    @staticmethod
    def create_requirements_prioritization_task(requirements_list: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for requirements prioritization."""
        return {
            "description": f"""Prioritize requirements using MoSCoW and value/effort analysis:
            
            {requirements_list}
            
            Evaluate each requirement based on:
            1. Business Value and ROI
            2. Strategic Alignment
            3. Technical Complexity
            4. Resource Requirements
            5. Dependencies
            6. Risk Level
            7. Regulatory Compliance
            8. User Impact
            9. Time Sensitivity
            10. Cost-Benefit Analysis
            
            Create a prioritized backlog with clear rationale.""",
            "expected_output": """Prioritized requirements document with:
            - MoSCoW categorization (Must/Should/Could/Won't)
            - Value/Effort matrix
            - Dependency mapping
            - Release planning recommendations
            - Trade-off analysis"""
        }
    
    @staticmethod
    def create_roi_analysis_task(project_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for ROI and business case analysis."""
        return {
            "description": f"""Develop comprehensive ROI analysis and business case for:
            
            {project_details}
            
            Include:
            1. Executive Summary
            2. Cost Analysis (Initial and Ongoing)
            3. Benefit Identification and Quantification
            4. ROI Calculation and Payback Period
            5. Net Present Value (NPV)
            6. Risk-Adjusted Returns
            7. Sensitivity Analysis
            8. Non-Monetary Benefits
            9. Implementation Timeline Impact
            10. Competitive Advantage Assessment
            11. Alternative Solutions Comparison
            12. Recommendation and Justification
            
            Use industry-standard financial metrics.""",
            "expected_output": """Complete business case with:
            - Financial models and projections
            - Sensitivity analysis scenarios
            - Risk-adjusted calculations
            - Visual dashboards
            - Executive presentation deck"""
        }
    
    @staticmethod
    def validate_requirements_quality(requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Validate requirements for quality and completeness."""
        validation_results = {
            "is_valid": True,
            "clarity_issues": [],
            "completeness_gaps": [],
            "consistency_conflicts": [],
            "testability_problems": [],
            "traceability_missing": []
        }
        
        # Check each requirement
        for req_id, requirement in requirements.items():
            # Clarity check
            if len(requirement.get("description", "")) < 20:
                validation_results["clarity_issues"].append(f"{req_id}: Description too brief")
            
            # Completeness check
            required_fields = ["description", "acceptance_criteria", "priority", "source"]
            for field in required_fields:
                if field not in requirement:
                    validation_results["completeness_gaps"].append(f"{req_id}: Missing {field}")
                    validation_results["is_valid"] = False
            
            # Testability check
            if "acceptance_criteria" in requirement:
                criteria = requirement["acceptance_criteria"]
                if not any(word in criteria.lower() for word in ["must", "shall", "will", "should"]):
                    validation_results["testability_problems"].append(f"{req_id}: Vague acceptance criteria")
            
            # Traceability check
            if "business_objective" not in requirement:
                validation_results["traceability_missing"].append(f"{req_id}: No link to business objective")
        
        # Check for conflicts
        validation_results["consistency_conflicts"] = BusinessAnalystAgent._check_requirement_conflicts(requirements)
        
        # Calculate quality score
        total_issues = sum([
            len(validation_results["clarity_issues"]),
            len(validation_results["completeness_gaps"]),
            len(validation_results["consistency_conflicts"]),
            len(validation_results["testability_problems"]),
            len(validation_results["traceability_missing"])
        ])
        
        total_requirements = len(requirements)
        validation_results["quality_score"] = max(0, 100 - (total_issues * 2)) if total_requirements > 0 else 0
        validation_results["recommendations"] = BusinessAnalystAgent._generate_quality_recommendations(validation_results)
        
        return validation_results
    
    @staticmethod
    def _check_requirement_conflicts(requirements: Dict[str, Any]) -> List[str]:
        """Check for conflicting requirements."""
        conflicts = []
        req_list = list(requirements.items())
        
        for i, (req1_id, req1) in enumerate(req_list):
            for req2_id, req2 in req_list[i+1:]:
                # Simple conflict detection based on keywords
                if req1.get("resource") == req2.get("resource") and \
                   req1.get("action") != req2.get("action"):
                    conflicts.append(f"{req1_id} conflicts with {req2_id} on resource usage")
        
        return conflicts
    
    @staticmethod
    def _generate_quality_recommendations(validation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving requirements quality."""
        recommendations = []
        
        if validation_results["clarity_issues"]:
            recommendations.append("Improve requirement descriptions for clarity and detail")
        
        if validation_results["completeness_gaps"]:
            recommendations.append("Complete all required fields for each requirement")
        
        if validation_results["consistency_conflicts"]:
            recommendations.append("Resolve conflicting requirements before implementation")
        
        if validation_results["testability_problems"]:
            recommendations.append("Define clear, measurable acceptance criteria")
        
        if validation_results["traceability_missing"]:
            recommendations.append("Link all requirements to business objectives")
        
        if validation_results["quality_score"] < 80:
            recommendations.append("Conduct requirements review workshop with stakeholders")
        
        return recommendations