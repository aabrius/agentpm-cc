"""
Engineer Agent for CrewAI implementation.
Creates technical specifications and architectural documentation.
"""

from crewai import Agent
from typing import Dict, Any, List
from ..tools.tech_spec_generator import TechSpecGeneratorTool
from ..tools.api_designer import APIDesignerTool
from ..tools.architecture_validator import ArchitectureValidatorTool
from ..tools.code_reviewer import CodeReviewerTool
from ..tools.performance_analyzer import PerformanceAnalyzerTool
from ..config import get_llm_model


class EngineerAgent:
    """Creates and configures the Engineer agent for technical architecture and implementation."""
    
    # Preserved engineering principles from original implementation
    ENGINEERING_PRINCIPLES = {
        "modularity": "Design modular, loosely coupled components",
        "scalability": "Build for horizontal and vertical scaling",
        "maintainability": "Write clean, documented, testable code",
        "performance": "Optimize for speed and resource efficiency",
        "security": "Implement security best practices throughout",
        "reliability": "Design for fault tolerance and recovery",
        "observability": "Include comprehensive logging and monitoring",
        "simplicity": "Choose simple solutions over complex ones"
    }
    
    # Preserved technical questions from original implementation
    TECHNICAL_QUESTIONS = [
        {
            "id": "tech_1",
            "content": "What are the primary technical requirements and constraints?",
            "required": True
        },
        {
            "id": "tech_2",
            "content": "What technology stack should be used?",
            "required": True
        },
        {
            "id": "tech_3",
            "content": "What are the performance and scalability targets?",
            "required": True
        },
        {
            "id": "tech_4",
            "content": "What are the integration points and APIs needed?",
            "required": True
        },
        {
            "id": "tech_5",
            "content": "What are the deployment and infrastructure requirements?",
            "required": True
        },
        {
            "id": "tech_6",
            "content": "What security measures must be implemented?",
            "required": False
        },
        {
            "id": "tech_7",
            "content": "What are the testing and quality assurance requirements?",
            "required": False
        },
        {
            "id": "tech_8",
            "content": "What are the monitoring and observability needs?",
            "required": False
        }
    ]
    
    @staticmethod
    def create(model_override: str = None) -> Agent:
        """Create the Engineer agent with full capabilities."""
        return Agent(
            role='Senior Software Engineer',
            goal='''Design and implement robust, scalable software solutions. Create 
            comprehensive technical specifications, API designs, and architectural 
            documentation that guide development teams to success.''',
            backstory='''You are a Senior Software Engineer with 10+ years of experience 
            building enterprise-grade applications. You've architected systems handling 
            millions of requests per day and led teams through complex technical challenges. 
            Your expertise spans multiple programming languages (Python, JavaScript, Go, Java), 
            cloud platforms (AWS, GCP, Azure), and architectural patterns (microservices, 
            event-driven, serverless). You're passionate about clean code, automated testing, 
            and DevOps practices. You excel at translating business requirements into 
            technical solutions, making pragmatic technology choices, and mentoring other 
            developers. Your technical specifications are known for their clarity and 
            completeness, helping teams avoid common pitfalls. You stay current with 
            technology trends while focusing on proven, production-ready solutions.''',
            tools=[
                TechSpecGeneratorTool(),
                APIDesignerTool(),
                ArchitectureValidatorTool(),
                CodeReviewerTool(),
                PerformanceAnalyzerTool()
            ],
            llm=get_llm_model('engineer', override_model=model_override),
            verbose=True,
            max_iter=15,
            memory=False
        )
    
    @staticmethod
    def create_tech_spec_task(project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for generating technical specifications."""
        return {
            "description": f"""Create comprehensive technical specifications based on:
            
            {project_context}
            
            The technical specification should include:
            1. Executive Summary
            2. System Architecture Overview
            3. Technology Stack Selection and Rationale
            4. Component Design and Interactions
            5. API Specifications (REST/GraphQL/gRPC)
            6. Data Flow and Processing
            7. Security Architecture
            8. Performance Requirements and Strategies
            9. Deployment Architecture
            10. Testing Strategy
            11. Monitoring and Observability
            12. Error Handling and Recovery
            13. Development Guidelines
            14. Dependencies and Third-party Services
            
            Ensure specifications are detailed enough for implementation.""",
            "expected_output": """Complete technical specification (3000-4000 words) with:
            - Architecture diagrams (component, sequence, deployment)
            - API documentation with examples
            - Performance benchmarks and SLAs
            - Security threat model
            - Implementation roadmap"""
        }
    
    @staticmethod
    def create_api_design_task(project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for API design and documentation."""
        return {
            "description": f"""Design comprehensive APIs for the project:
            
            {project_context}
            
            Create API specifications including:
            1. API Architecture (REST/GraphQL/gRPC decision)
            2. Resource Modeling and Endpoints
            3. Request/Response Schemas
            4. Authentication and Authorization
            5. Rate Limiting and Throttling
            6. Versioning Strategy
            7. Error Handling Standards
            8. Pagination and Filtering
            9. WebSocket/Real-time Events
            10. API Documentation (OpenAPI/GraphQL Schema)
            11. SDK Generation Strategy
            12. Testing and Mocking
            
            Follow API design best practices and ensure consistency.""",
            "expected_output": """Complete API design package with:
            - OpenAPI 3.0/GraphQL schema definitions
            - Postman/Insomnia collections
            - SDK examples in multiple languages
            - API testing strategies
            - Performance optimization guidelines"""
        }
    
    @staticmethod
    def create_architecture_review_task(proposed_architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for architecture review and validation."""
        return {
            "description": f"""Review and validate the proposed architecture:
            
            {proposed_architecture}
            
            Evaluate:
            1. Scalability and Performance
            2. Security and Compliance
            3. Reliability and Fault Tolerance
            4. Maintainability and Testability
            5. Cost Optimization
            6. Technology Choices
            7. Integration Complexity
            8. Operational Requirements
            9. Development Velocity Impact
            10. Technical Debt Risks
            
            Provide specific recommendations and alternative approaches.""",
            "expected_output": """Architecture review report including:
            - Risk assessment matrix
            - Performance projections
            - Cost analysis
            - Alternative architecture options
            - Implementation recommendations"""
        }
    
    @staticmethod
    def create_performance_optimization_task(system_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for performance optimization."""
        return {
            "description": f"""Analyze and optimize system performance based on metrics:
            
            {system_metrics}
            
            Focus on:
            1. Response Time Optimization
            2. Throughput Improvements
            3. Resource Utilization
            4. Database Query Optimization
            5. Caching Strategies
            6. CDN and Edge Computing
            7. Async Processing Patterns
            8. Connection Pooling
            9. Memory Management
            10. Concurrency Optimization
            
            Provide specific, measurable improvements.""",
            "expected_output": """Performance optimization plan with:
            - Bottleneck analysis
            - Optimization strategies with impact estimates
            - Implementation priority matrix
            - Before/after performance projections
            - Monitoring dashboard specifications"""
        }
    
    @staticmethod
    def create_deployment_strategy_task(project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for deployment strategy and CI/CD."""
        return {
            "description": f"""Design comprehensive deployment strategy for:
            
            {project_context}
            
            Include:
            1. CI/CD Pipeline Design
            2. Environment Strategy (Dev/Staging/Prod)
            3. Container/Serverless Architecture
            4. Blue-Green/Canary Deployment
            5. Rollback Procedures
            6. Infrastructure as Code (Terraform/CloudFormation)
            7. Secrets Management
            8. Monitoring and Alerting
            9. Disaster Recovery
            10. Auto-scaling Policies
            11. Cost Optimization
            12. Compliance and Auditing
            
            Ensure zero-downtime deployments and rapid rollback capability.""",
            "expected_output": """Complete deployment strategy with:
            - CI/CD pipeline configurations
            - IaC templates
            - Deployment runbooks
            - Monitoring dashboards
            - Disaster recovery procedures"""
        }
    
    @staticmethod
    def validate_technical_design(design: Dict[str, Any]) -> Dict[str, Any]:
        """Validate technical design for completeness and best practices."""
        validation_results = {
            "is_valid": True,
            "architecture_issues": [],
            "security_concerns": [],
            "scalability_risks": [],
            "maintainability_issues": [],
            "missing_components": []
        }
        
        # Check for essential components
        essential_components = [
            "authentication",
            "authorization",
            "logging",
            "monitoring",
            "error_handling",
            "data_validation",
            "api_documentation",
            "testing_strategy"
        ]
        
        for component in essential_components:
            if component not in str(design).lower():
                validation_results["missing_components"].append(component)
                validation_results["is_valid"] = False
        
        # Check for security considerations
        security_checks = [
            "encryption",
            "input_validation",
            "rate_limiting",
            "cors",
            "csrf_protection"
        ]
        
        for check in security_checks:
            if check not in str(design).lower():
                validation_results["security_concerns"].append(f"Missing {check} specification")
        
        # Check for scalability considerations
        if "load_balancing" not in str(design).lower():
            validation_results["scalability_risks"].append("No load balancing strategy defined")
        
        if "caching" not in str(design).lower():
            validation_results["scalability_risks"].append("No caching strategy defined")
        
        # Calculate technical score
        total_issues = sum([
            len(validation_results["architecture_issues"]),
            len(validation_results["security_concerns"]),
            len(validation_results["scalability_risks"]),
            len(validation_results["maintainability_issues"]),
            len(validation_results["missing_components"])
        ])
        
        validation_results["technical_score"] = max(0, 100 - (total_issues * 3))
        validation_results["recommendations"] = EngineerAgent._generate_technical_recommendations(validation_results)
        
        return validation_results
    
    @staticmethod
    def _generate_technical_recommendations(validation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if validation_results["architecture_issues"]:
            recommendations.append("Review architecture design for identified issues")
        
        if validation_results["security_concerns"]:
            recommendations.append("Implement comprehensive security measures: " + 
                                 ", ".join(validation_results["security_concerns"][:3]))
        
        if validation_results["scalability_risks"]:
            recommendations.append("Address scalability concerns before production deployment")
        
        if validation_results["maintainability_issues"]:
            recommendations.append("Improve code organization and documentation")
        
        if validation_results["missing_components"]:
            recommendations.append("Add missing essential components: " + 
                                 ", ".join(validation_results["missing_components"][:3]))
        
        if validation_results["technical_score"] < 70:
            recommendations.append("Consider architectural review before proceeding")
        
        return recommendations