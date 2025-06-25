"""
Database Agent for CrewAI implementation.
Designs database schemas and creates comprehensive data documentation.
"""

from crewai import Agent
from typing import Dict, Any, List
from ..tools.erd_generator import ERDGeneratorTool
from ..tools.dbrd_generator import DBRDGeneratorTool
from ..tools.schema_optimizer import SchemaOptimizerTool
from ..tools.migration_planner import MigrationPlannerTool
from ..tools.data_dictionary_generator import DataDictionaryGeneratorTool
from ..config import get_llm_model


class DatabaseAgent:
    """Creates and configures the Database agent for data architecture and documentation."""
    
    # Preserved database design principles from original implementation
    DATABASE_PRINCIPLES = {
        "normalization": "Apply appropriate normalization (typically 3NF)",
        "integrity": "Enforce referential and data integrity",
        "performance": "Optimize for query performance",
        "scalability": "Design for future growth",
        "security": "Implement data security best practices",
        "consistency": "Ensure ACID compliance where needed",
        "flexibility": "Allow for schema evolution",
        "documentation": "Maintain comprehensive documentation"
    }
    
    # Preserved database questions from original implementation
    DATABASE_QUESTIONS = [
        {
            "id": "database_1",
            "content": "What are the main entities and their relationships?",
            "required": True
        },
        {
            "id": "database_2",
            "content": "What are the data volume and growth expectations?",
            "required": True
        },
        {
            "id": "database_3",
            "content": "What are the key queries and access patterns?",
            "required": True
        },
        {
            "id": "database_4",
            "content": "What are the data integrity and consistency requirements?",
            "required": True
        },
        {
            "id": "database_5",
            "content": "What are the performance and scalability requirements?",
            "required": True
        },
        {
            "id": "database_6",
            "content": "What compliance and security requirements apply?",
            "required": False
        },
        {
            "id": "database_7",
            "content": "Are there existing systems to integrate with?",
            "required": False
        },
        {
            "id": "database_8",
            "content": "What are the backup and recovery requirements?",
            "required": False
        }
    ]
    
    @staticmethod
    def create(model_override: str = None) -> Agent:
        """Create the Database agent with full capabilities."""
        return Agent(
            role='Senior Database Architect',
            goal='''Design optimal database schemas that ensure data integrity, 
            performance, and scalability. Create comprehensive documentation including 
            ERDs, DBRDs, and migration strategies.''',
            backstory='''You are a veteran Database Architect with 15+ years of experience 
            designing and optimizing database systems for enterprise applications. You've 
            worked with various database technologies including PostgreSQL, MySQL, MongoDB, 
            Redis, and cloud-native solutions. Your expertise covers relational modeling, 
            NoSQL design patterns, data warehousing, and real-time analytics systems. 
            You excel at balancing normalization with performance, implementing proper 
            indexing strategies, and ensuring data security. Your database designs have 
            supported applications with millions of users and petabytes of data. You're 
            known for creating clear ERDs and comprehensive documentation that helps teams 
            understand and maintain complex data models. You stay current with database 
            technologies and understand when to use SQL vs NoSQL solutions.''',
            tools=[
                ERDGeneratorTool(),
                DBRDGeneratorTool(),
                SchemaOptimizerTool(),
                MigrationPlannerTool(),
                DataDictionaryGeneratorTool()
            ],
            llm=get_llm_model('database', override_model=model_override),
            verbose=True,
            max_iter=15,
            memory=False
        )
    
    @staticmethod
    def create_erd_task(project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for generating an Entity Relationship Diagram."""
        return {
            "description": f"""Create a comprehensive Entity Relationship Diagram (ERD) 
            based on the following project context:
            
            {project_context}
            
            The ERD should include:
            1. All entities with attributes
            2. Primary and foreign keys
            3. Relationships with cardinality
            4. Constraints and business rules
            5. Indexes for performance
            6. Audit and timestamp fields
            7. Computed/derived fields
            8. Data types and sizes
            9. Default values and nullable flags
            10. Unique constraints
            
            Use standard ERD notation and ensure the design follows normalization 
            principles while optimizing for the specified access patterns.""",
            "expected_output": """Complete ERD documentation including:
            - Visual ERD diagram (Chen or Crow's Foot notation)
            - Detailed entity descriptions
            - Relationship explanations
            - Constraint definitions
            - Index strategy documentation"""
        }
    
    @staticmethod
    def create_dbrd_task(project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for generating a Database Requirements Document."""
        return {
            "description": f"""Create a comprehensive Database Requirements Document (DBRD) 
            based on the following project context:
            
            {project_context}
            
            The DBRD should include:
            1. Executive Summary
            2. Database Architecture Overview
            3. Data Model Design
            4. Performance Requirements and Strategies
            5. Security and Access Control
            6. Backup and Recovery Procedures
            7. Data Migration Strategy
            8. Scalability Plan
            9. Monitoring and Maintenance
            10. Compliance Requirements
            11. Integration Points
            12. Data Retention Policies
            
            Focus on both technical implementation and operational considerations.""",
            "expected_output": """A complete DBRD document (3000-4000 words) including:
            - Detailed technical specifications
            - Operational procedures
            - Performance benchmarks
            - Security protocols
            - Disaster recovery plans"""
        }
    
    @staticmethod
    def create_schema_optimization_task(initial_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for optimizing database schema."""
        return {
            "description": f"""Optimize the following database schema for performance 
            and scalability:
            
            {initial_schema}
            
            Analyze and optimize:
            1. Index strategy for common queries
            2. Denormalization opportunities
            3. Partitioning strategies
            4. Caching layer design
            5. Query optimization techniques
            6. Connection pooling configuration
            7. Read replica strategies
            8. Sharding considerations
            9. Archive strategy for old data
            10. Materialized views where appropriate
            
            Provide specific recommendations with performance impact estimates.""",
            "expected_output": """Optimization report including:
            - Recommended schema changes
            - Index creation scripts
            - Query optimization examples
            - Performance impact analysis
            - Implementation priority list"""
        }
    
    @staticmethod
    def create_migration_plan_task(current_schema: Dict[str, Any], target_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for database migration planning."""
        return {
            "description": f"""Create a detailed migration plan from current to target schema:
            
            Current Schema: {current_schema}
            Target Schema: {target_schema}
            
            The migration plan should include:
            1. Migration phases and sequence
            2. DDL scripts for schema changes
            3. Data transformation scripts
            4. Rollback procedures
            5. Zero-downtime migration strategy
            6. Data validation checkpoints
            7. Performance testing plan
            8. Risk assessment and mitigation
            9. Timeline and resource requirements
            10. Post-migration validation
            
            Ensure data integrity throughout the migration process.""",
            "expected_output": """Complete migration plan with:
            - Step-by-step migration guide
            - All necessary SQL scripts
            - Rollback scripts for each phase
            - Testing and validation procedures
            - Risk mitigation strategies"""
        }
    
    @staticmethod
    def create_data_dictionary_task(schema: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for generating a data dictionary."""
        return {
            "description": f"""Generate a comprehensive data dictionary for the schema:
            
            {schema}
            
            Document for each table/collection:
            1. Table purpose and business context
            2. Column descriptions and business rules
            3. Data types and constraints
            4. Relationships and dependencies
            5. Sample data and valid values
            6. Update frequency and sources
            7. Data quality rules
            8. Privacy and security classification
            9. Retention policies
            10. API/service dependencies
            
            Make it accessible for both technical and business users.""",
            "expected_output": """Complete data dictionary including:
            - Table-by-table documentation
            - Business glossary
            - Data lineage information
            - Usage examples
            - Maintenance procedures"""
        }
    
    @staticmethod
    def validate_schema_design(schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate database schema design for best practices."""
        validation_results = {
            "is_valid": True,
            "normalization_issues": [],
            "performance_concerns": [],
            "security_gaps": [],
            "naming_inconsistencies": [],
            "missing_elements": []
        }
        
        # Check for common issues
        if "tables" in schema:
            for table_name, table_def in schema["tables"].items():
                # Check naming conventions
                if not table_name.islower():
                    validation_results["naming_inconsistencies"].append(
                        f"Table '{table_name}' should use lowercase naming"
                    )
                
                # Check for primary key
                if "primary_key" not in table_def:
                    validation_results["missing_elements"].append(
                        f"Table '{table_name}' missing primary key"
                    )
                    validation_results["is_valid"] = False
                
                # Check for audit fields
                audit_fields = ["created_at", "updated_at"]
                for field in audit_fields:
                    if field not in table_def.get("columns", {}):
                        validation_results["missing_elements"].append(
                            f"Table '{table_name}' missing audit field '{field}'"
                        )
                
                # Check for proper indexes
                if "indexes" not in table_def and len(table_def.get("columns", {})) > 5:
                    validation_results["performance_concerns"].append(
                        f"Table '{table_name}' may need indexes for performance"
                    )
        
        # Calculate design score
        total_issues = sum([
            len(validation_results["normalization_issues"]),
            len(validation_results["performance_concerns"]),
            len(validation_results["security_gaps"]),
            len(validation_results["naming_inconsistencies"]),
            len(validation_results["missing_elements"])
        ])
        
        validation_results["design_score"] = max(0, 100 - (total_issues * 5))
        validation_results["recommendations"] = DatabaseAgent._generate_schema_recommendations(validation_results)
        
        return validation_results
    
    @staticmethod
    def _generate_schema_recommendations(validation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if validation_results["normalization_issues"]:
            recommendations.append("Review and resolve normalization issues to prevent data anomalies")
        
        if validation_results["performance_concerns"]:
            recommendations.append("Add appropriate indexes and consider query optimization")
        
        if validation_results["security_gaps"]:
            recommendations.append("Implement row-level security and encryption where needed")
        
        if validation_results["naming_inconsistencies"]:
            recommendations.append("Standardize naming conventions across all database objects")
        
        if validation_results["missing_elements"]:
            recommendations.append("Add missing required elements like primary keys and audit fields")
        
        if validation_results["design_score"] < 80:
            recommendations.append("Consider a design review with the team before implementation")
        
        return recommendations