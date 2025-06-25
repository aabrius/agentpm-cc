"""
Solution Architect Agent for CrewAI implementation.
Designs comprehensive system architectures and integration strategies.
"""

from crewai import Agent
from typing import Dict, Any, List
from ..tools.architecture_designer import ArchitectureDesignerTool
from ..tools.integration_planner import IntegrationPlannerTool
from ..tools.security_architect import SecurityArchitectTool
from ..tools.cloud_optimizer import CloudOptimizerTool
from ..tools.pattern_recommender import PatternRecommenderTool
from ..config import get_llm_model


class SolutionArchitectAgent:
    """Creates and configures the Solution Architect agent for system design."""
    
    # Preserved architecture principles from original implementation
    ARCHITECTURE_PRINCIPLES = {
        "separation_of_concerns": "Isolate different aspects of the system",
        "single_responsibility": "Each component has one clear purpose",
        "loose_coupling": "Minimize dependencies between components",
        "high_cohesion": "Related functionality stays together",
        "scalability": "Design for horizontal and vertical scaling",
        "resilience": "Build fault-tolerant systems",
        "security_by_design": "Security built in, not bolted on",
        "evolutionary": "Architecture can adapt to changing needs"
    }
    
    # Preserved architecture questions from original implementation
    ARCHITECTURE_QUESTIONS = [
        {
            "id": "arch_1",
            "content": "What are the system quality attributes (performance, security, scalability)?",
            "required": True
        },
        {
            "id": "arch_2",
            "content": "What are the integration requirements with existing systems?",
            "required": True
        },
        {
            "id": "arch_3",
            "content": "What are the data flow and storage requirements?",
            "required": True
        },
        {
            "id": "arch_4",
            "content": "What are the deployment and infrastructure constraints?",
            "required": True
        },
        {
            "id": "arch_5",
            "content": "What architectural patterns best fit the requirements?",
            "required": True
        },
        {
            "id": "arch_6",
            "content": "What are the disaster recovery and business continuity needs?",
            "required": False
        },
        {
            "id": "arch_7",
            "content": "What are the compliance and regulatory requirements?",
            "required": False
        },
        {
            "id": "arch_8",
            "content": "What is the expected system evolution and growth?",
            "required": False
        }
    ]
    
    @staticmethod
    def create(model_override: str = None) -> Agent:
        """Create the Solution Architect agent with full capabilities."""
        return Agent(
            role='Principal Solution Architect',
            goal='''Design robust, scalable system architectures that meet current needs 
            while enabling future growth. Create comprehensive architectural documentation 
            that guides implementation and ensures system quality attributes.''',
            backstory='''You are a Principal Solution Architect with 15+ years of experience 
            designing enterprise-scale systems. You've architected solutions for Fortune 500 
            companies, handling billions of transactions and petabytes of data. Your expertise 
            spans cloud platforms (AWS, Azure, GCP), architectural patterns (microservices, 
            event-driven, serverless), and various technology stacks. You excel at balancing 
            technical excellence with business pragmatism, creating architectures that are 
            both elegant and practical. You're known for your ability to see the big picture 
            while managing intricate technical details. Your architectural decisions have 
            saved companies millions in operational costs while improving system reliability. 
            You stay current with emerging technologies and architectural trends, but always 
            evaluate them against proven principles. You're skilled at communicating complex 
            architectural concepts to both technical and non-technical stakeholders, and your 
            documentation serves as the blueprint for successful implementations.''',
            tools=[
                ArchitectureDesignerTool(),
                IntegrationPlannerTool(),
                SecurityArchitectTool(),
                CloudOptimizerTool(),
                PatternRecommenderTool()
            ],
            llm=get_llm_model('solution_architect', override_model=model_override),
            verbose=True,
            max_iter=15,
            memory=False
        )
    
    @staticmethod
    def create_architecture_design_task(project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for system architecture design."""
        return {
            "description": f"""Design comprehensive system architecture for:
            
            {project_context}
            
            The architecture design should include:
            1. Architecture Overview and Vision
            2. System Context and Boundaries
            3. Component Architecture (4+1 Views)
            4. Data Architecture and Flow
            5. Integration Architecture
            6. Security Architecture
            7. Infrastructure Architecture
            8. Deployment Architecture
            9. Technology Stack Selection
            10. Architectural Patterns and Principles
            11. Quality Attribute Scenarios
            12. Architecture Decision Records (ADRs)
            13. Risk Assessment and Mitigation
            14. Evolution and Roadmap
            
            Use industry-standard notations (UML, C4, ArchiMate).""",
            "expected_output": """Complete architecture documentation with:
            - Multiple architecture views (logical, physical, deployment)
            - Detailed component diagrams
            - Integration patterns and APIs
            - Security threat model
            - ADRs for key decisions
            - Implementation guidelines"""
        }
    
    @staticmethod
    def create_integration_design_task(systems_to_integrate: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for integration architecture."""
        return {
            "description": f"""Design integration architecture for systems:
            
            {systems_to_integrate}
            
            Create comprehensive integration design including:
            1. Integration Patterns Selection
            2. API Design and Contracts
            3. Data Transformation and Mapping
            4. Message Formats and Protocols
            5. Event-Driven Architecture
            6. Service Orchestration vs Choreography
            7. Error Handling and Compensation
            8. Monitoring and Observability
            9. Security and Authentication
            10. Performance and Throttling
            11. Versioning Strategy
            12. Testing Strategy
            
            Focus on loose coupling and maintainability.""",
            "expected_output": """Integration architecture package with:
            - Integration pattern catalog
            - API specifications (OpenAPI/AsyncAPI)
            - Data mapping documentation
            - Sequence diagrams
            - Error handling playbook"""
        }
    
    @staticmethod
    def create_cloud_architecture_task(cloud_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for cloud architecture design."""
        return {
            "description": f"""Design cloud-native architecture based on:
            
            {cloud_requirements}
            
            Architecture should address:
            1. Multi-Cloud vs Single Cloud Strategy
            2. Compute Services Selection
            3. Storage and Database Services
            4. Networking and CDN
            5. Security and Compliance
            6. Auto-Scaling and Load Balancing
            7. Disaster Recovery and Backup
            8. Cost Optimization
            9. Monitoring and Logging
            10. CI/CD Pipeline
            11. Infrastructure as Code
            12. Container Orchestration
            
            Follow Well-Architected Framework principles.""",
            "expected_output": """Cloud architecture blueprint with:
            - Service selection rationale
            - Cost projections and optimization
            - IaC templates (Terraform/CloudFormation)
            - Security controls matrix
            - Operational runbooks"""
        }
    
    @staticmethod
    def create_security_architecture_task(security_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for security architecture design."""
        return {
            "description": f"""Design comprehensive security architecture for:
            
            {security_requirements}
            
            Security design should include:
            1. Threat Modeling (STRIDE/PASTA)
            2. Security Zones and Boundaries
            3. Authentication and Authorization
            4. Data Protection (At Rest/In Transit)
            5. Network Security
            6. Application Security
            7. Identity and Access Management
            8. Secrets Management
            9. Security Monitoring and SIEM
            10. Incident Response Plan
            11. Compliance Controls
            12. Security Testing Strategy
            
            Implement defense-in-depth approach.""",
            "expected_output": """Security architecture package with:
            - Threat model and risk assessment
            - Security controls implementation
            - Compliance mapping (SOC2, GDPR, etc.)
            - Security runbooks
            - Penetration testing scope"""
        }
    
    @staticmethod
    def create_pattern_recommendation_task(system_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for architectural pattern recommendations."""
        return {
            "description": f"""Recommend architectural patterns based on:
            
            {system_characteristics}
            
            Analyze and recommend:
            1. Application Architecture Patterns
            2. Data Management Patterns
            3. Integration Patterns
            4. Messaging Patterns
            5. Deployment Patterns
            6. Security Patterns
            7. Resilience Patterns
            8. Performance Patterns
            9. Multi-Tenancy Patterns
            10. Observability Patterns
            
            Provide pattern trade-offs and implementation guidance.""",
            "expected_output": """Pattern recommendation report with:
            - Pattern catalog with use cases
            - Trade-off analysis matrix
            - Implementation examples
            - Anti-patterns to avoid
            - Migration strategies"""
        }
    
    @staticmethod
    def validate_architecture_design(architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Validate architecture design against best practices."""
        validation_results = {
            "is_valid": True,
            "principle_violations": [],
            "missing_views": [],
            "quality_concerns": [],
            "risk_factors": [],
            "improvement_opportunities": []
        }
        
        # Check for required architectural views
        required_views = [
            "logical_view",
            "physical_view",
            "deployment_view",
            "process_view",
            "use_case_view"
        ]
        
        for view in required_views:
            if view not in architecture.get("views", {}):
                validation_results["missing_views"].append(view)
                validation_results["is_valid"] = False
        
        # Check architectural principles
        if architecture.get("coupling_score", 10) > 7:
            validation_results["principle_violations"].append("High coupling detected between components")
        
        if not architecture.get("scalability_strategy"):
            validation_results["quality_concerns"].append("No clear scalability strategy defined")
        
        if not architecture.get("fault_tolerance"):
            validation_results["quality_concerns"].append("Missing fault tolerance mechanisms")
        
        # Check for risks
        if not architecture.get("disaster_recovery"):
            validation_results["risk_factors"].append("No disaster recovery plan")
        
        if architecture.get("single_points_of_failure", 0) > 0:
            validation_results["risk_factors"].append("Single points of failure identified")
        
        # Check for optimization opportunities
        if not architecture.get("caching_strategy"):
            validation_results["improvement_opportunities"].append("Consider adding caching layer")
        
        if not architecture.get("cdn_usage"):
            validation_results["improvement_opportunities"].append("Consider CDN for static assets")
        
        # Calculate architecture score
        total_issues = sum([
            len(validation_results["principle_violations"]),
            len(validation_results["missing_views"]),
            len(validation_results["quality_concerns"]),
            len(validation_results["risk_factors"])
        ])
        
        validation_results["architecture_score"] = max(0, 100 - (total_issues * 5))
        validation_results["recommendations"] = SolutionArchitectAgent._generate_architecture_recommendations(validation_results)
        
        return validation_results
    
    @staticmethod
    def _generate_architecture_recommendations(validation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if validation_results["principle_violations"]:
            recommendations.append("Refactor architecture to follow SOLID principles")
        
        if validation_results["missing_views"]:
            recommendations.append(f"Complete missing architectural views: {', '.join(validation_results['missing_views'])}")
        
        if validation_results["quality_concerns"]:
            recommendations.append("Address quality attribute requirements")
        
        if validation_results["risk_factors"]:
            recommendations.append("Implement risk mitigation strategies for identified risks")
        
        if validation_results["improvement_opportunities"]:
            recommendations.append("Consider performance optimizations: " + 
                                 ", ".join(validation_results["improvement_opportunities"][:2]))
        
        if validation_results["architecture_score"] < 75:
            recommendations.append("Schedule architecture review board meeting")
        
        recommendations.append("Document all Architecture Decision Records (ADRs)")
        
        return recommendations