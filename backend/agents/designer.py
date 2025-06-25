"""
Designer Agent for CrewAI implementation.
Creates comprehensive UX/UI designs and documentation.
"""

from crewai import Agent
from typing import Dict, Any, List
from ..tools.uxdd_generator import UXDDGeneratorTool
from ..tools.design_system_tool import DesignSystemTool
from ..tools.wireframe_generator import WireframeGeneratorTool
from ..tools.prototype_validator import PrototypeValidatorTool
from ..tools.accessibility_checker import AccessibilityCheckerTool
from ..config import get_llm_model


class DesignerAgent:
    """Creates and configures the Designer agent for UX/UI design and documentation."""
    
    # Preserved design principles from original implementation
    DESIGN_PRINCIPLES = {
        "user_centered": "Focus on user needs and goals",
        "consistency": "Maintain visual and interaction consistency",
        "simplicity": "Keep interfaces clean and intuitive",
        "accessibility": "Ensure designs are inclusive and accessible",
        "feedback": "Provide clear feedback for user actions",
        "flexibility": "Support different user preferences and workflows",
        "error_prevention": "Design to prevent user errors",
        "recognition": "Make options visible rather than recall-based"
    }
    
    # Preserved design questions from original implementation
    DESIGN_QUESTIONS = [
        {
            "id": "design_1",
            "content": "What are the key user interface requirements?",
            "required": True
        },
        {
            "id": "design_2",
            "content": "What is the visual style and branding guidelines?",
            "required": True
        },
        {
            "id": "design_3",
            "content": "What are the main user flows and interactions?",
            "required": True
        },
        {
            "id": "design_4",
            "content": "What are the responsive design requirements?",
            "required": True
        },
        {
            "id": "design_5",
            "content": "What accessibility standards must be met?",
            "required": True
        },
        {
            "id": "design_6",
            "content": "What are the performance requirements for UI?",
            "required": False
        },
        {
            "id": "design_7",
            "content": "Are there existing design systems to follow?",
            "required": False
        },
        {
            "id": "design_8",
            "content": "What are the internationalization requirements?",
            "required": False
        }
    ]
    
    @staticmethod
    def create(model_override: str = None) -> Agent:
        """Create the Designer agent with full capabilities."""
        return Agent(
            role='Senior UX/UI Designer',
            goal='''Create intuitive, accessible, and visually appealing user interfaces 
            that enhance user experience and meet business objectives. Develop comprehensive 
            design documentation including UXDD, wireframes, and design systems.''',
            backstory='''You are an award-winning UX/UI Designer with 12+ years of experience 
            creating user-centered designs for web and mobile applications. You've worked 
            with Fortune 500 companies and innovative startups, always putting user needs 
            first while balancing business requirements. Your expertise spans user research, 
            information architecture, interaction design, visual design, and usability testing. 
            You're passionate about accessibility and inclusive design, ensuring your interfaces 
            work for everyone. You have deep knowledge of design systems, component libraries, 
            and modern design tools. Your design documentation is thorough and helps development 
            teams implement pixel-perfect interfaces. You stay current with design trends 
            while focusing on timeless usability principles.''',
            tools=[
                UXDDGeneratorTool(),
                DesignSystemTool(),
                WireframeGeneratorTool(),
                PrototypeValidatorTool(),
                AccessibilityCheckerTool()
            ],
            llm=get_llm_model('designer', override_model=model_override),
            verbose=True,
            max_iter=15,
            memory=False
        )
    
    @staticmethod
    def create_uxdd_task(project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for generating a UX Design Document."""
        return {
            "description": f"""Create a comprehensive UX Design Document (UXDD) 
            based on the following project context:
            
            {project_context}
            
            The UXDD should include:
            1. Executive Summary
            2. User Research Findings
            3. Information Architecture
            4. User Flows and Journey Maps
            5. Wireframes and Mockups
            6. Interaction Design Patterns
            7. Visual Design Guidelines
            8. Responsive Design Strategy
            9. Accessibility Considerations
            10. Usability Testing Plan
            11. Design System Components
            12. Implementation Guidelines
            
            Ensure the design is user-centered, accessible, and aligned with modern 
            UX best practices.""",
            "expected_output": """A complete UXDD document (2500-3500 words) with:
            - Detailed design rationale and decisions
            - Clear wireframes and user flows
            - Comprehensive design specifications
            - Accessibility compliance checklist
            - Implementation guidelines for developers"""
        }
    
    @staticmethod
    def create_design_system_task(project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for developing a design system."""
        return {
            "description": f"""Develop a comprehensive design system for the project:
            
            {project_context}
            
            The design system should include:
            1. Design Principles and Philosophy
            2. Color System (primary, secondary, semantic colors)
            3. Typography Scale and Guidelines
            4. Spacing and Grid System
            5. Component Library (buttons, forms, cards, etc.)
            6. Icon System and Guidelines
            7. Motion and Animation Principles
            8. Accessibility Standards
            9. Responsive Breakpoints
            10. Design Tokens
            11. Usage Guidelines and Best Practices
            
            Ensure consistency and scalability across all interfaces.""",
            "expected_output": """A complete design system including:
            - Figma/Sketch component library
            - Design tokens in JSON format
            - CSS/SCSS variables
            - Component documentation
            - Usage examples and guidelines"""
        }
    
    @staticmethod
    def create_wireframe_task(project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for generating wireframes."""
        return {
            "description": f"""Create comprehensive wireframes for all major screens 
            and user flows based on:
            
            {project_context}
            
            Deliverables should include:
            1. Low-fidelity wireframes for concept validation
            2. High-fidelity wireframes for development reference
            3. Responsive variations (mobile, tablet, desktop)
            4. Annotation and interaction notes
            5. User flow connections between screens
            6. Component specifications
            7. Content hierarchy and layout grids
            
            Focus on usability and clear information architecture.""",
            "expected_output": """Complete wireframe package including:
            - All major screens and states
            - Responsive variations
            - Detailed annotations
            - Interactive prototype links
            - Developer handoff specifications"""
        }
    
    @staticmethod
    def create_accessibility_audit_task(design_artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for accessibility audit."""
        return {
            "description": f"""Conduct a comprehensive accessibility audit of the 
            design artifacts:
            
            {design_artifacts}
            
            Evaluate against:
            1. WCAG 2.1 AA compliance
            2. Color contrast ratios
            3. Keyboard navigation support
            4. Screen reader compatibility
            5. Touch target sizes
            6. Focus indicators
            7. Alternative text requirements
            8. Semantic HTML structure
            9. ARIA labels and roles
            10. Cognitive load considerations
            
            Identify issues and provide remediation recommendations.""",
            "expected_output": """Detailed accessibility report including:
            - WCAG compliance checklist
            - Identified issues with severity levels
            - Specific remediation steps
            - Testing methodology
            - Recommendations for ongoing compliance"""
        }
    
    @staticmethod
    def create_user_flow_task(project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for mapping user flows."""
        return {
            "description": f"""Map comprehensive user flows for all major features 
            and scenarios:
            
            {project_context}
            
            Document:
            1. Primary user paths (happy paths)
            2. Alternative flows and edge cases
            3. Error states and recovery flows
            4. Entry and exit points
            5. Decision points and branching logic
            6. Integration points with external systems
            7. Data requirements at each step
            8. Success criteria and metrics
            
            Use standard flow chart notation and include detailed annotations.""",
            "expected_output": """Complete user flow documentation with:
            - Visual flow diagrams for all scenarios
            - Step-by-step descriptions
            - Decision logic documentation
            - Error handling flows
            - Success metrics for each flow"""
        }
    
    @staticmethod
    def validate_design_completeness(design_artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all design deliverables are complete."""
        required_artifacts = [
            "information_architecture",
            "user_flows",
            "wireframes",
            "visual_designs",
            "design_system",
            "accessibility_checklist",
            "responsive_specifications",
            "interaction_patterns"
        ]
        
        missing_artifacts = []
        completeness_score = 0
        
        for artifact in required_artifacts:
            if artifact in design_artifacts and design_artifacts[artifact]:
                completeness_score += 1
            else:
                missing_artifacts.append(artifact)
        
        quality_checks = {
            "has_responsive_designs": False,
            "has_accessibility_notes": False,
            "has_interaction_specs": False,
            "has_design_rationale": False
        }
        
        # Check quality indicators
        if design_artifacts.get("responsive_specifications"):
            quality_checks["has_responsive_designs"] = True
        if design_artifacts.get("accessibility_checklist"):
            quality_checks["has_accessibility_notes"] = True
        if design_artifacts.get("interaction_patterns"):
            quality_checks["has_interaction_specs"] = True
        if design_artifacts.get("design_rationale"):
            quality_checks["has_design_rationale"] = True
        
        return {
            "is_complete": len(missing_artifacts) == 0,
            "completeness_percentage": (completeness_score / len(required_artifacts)) * 100,
            "missing_artifacts": missing_artifacts,
            "quality_checks": quality_checks,
            "recommendations": DesignerAgent._generate_recommendations(missing_artifacts, quality_checks)
        }
    
    @staticmethod
    def _generate_recommendations(missing_artifacts: List[str], quality_checks: Dict[str, bool]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if missing_artifacts:
            recommendations.append(f"Complete missing artifacts: {', '.join(missing_artifacts)}")
        
        if not quality_checks["has_responsive_designs"]:
            recommendations.append("Add responsive design specifications for all breakpoints")
        
        if not quality_checks["has_accessibility_notes"]:
            recommendations.append("Include accessibility annotations and WCAG compliance notes")
        
        if not quality_checks["has_interaction_specs"]:
            recommendations.append("Document interaction patterns and micro-interactions")
        
        if not quality_checks["has_design_rationale"]:
            recommendations.append("Add design rationale explaining key decisions")
        
        return recommendations