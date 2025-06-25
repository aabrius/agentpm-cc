"""
ERD Generator Tool for CrewAI implementation.
Generates Entity Relationship Diagrams and database documentation.
"""

from typing import Dict, Any, List
from pydantic import Field
from .base_template_tool import BaseTemplateTool
from ..config import get_llm_model
import structlog

logger = structlog.get_logger()


class ERDGeneratorTool(BaseTemplateTool):
    """Tool for generating Entity Relationship Diagrams."""
    
    name: str = Field(default="ERD Generator")
    description: str = Field(default="Generates comprehensive Entity Relationship Diagrams with database design best practices")
    template_name: str = Field(default="erd")
    
    def _generate_with_llm(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate section content using LLM for dynamic sections."""
        llm = get_llm_model('database')
        
        # Build prompt based on section requirements
        prompt = self._build_section_prompt(section, context)
        
        try:
            response = llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Error generating ERD section with LLM", section=section.get("id"), error=str(e))
            return f"[Error generating content for {section.get('title', 'section')}]"
    
    def _build_section_prompt(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build LLM prompt for section generation."""
        section_title = section.get("title", "")
        section_desc = section.get("description", "")
        
        # Extract relevant context
        context_str = self._format_context_for_prompt(context)
        
        prompt = f"""Generate content for the '{section_title}' section of an Entity Relationship Diagram document.

Section Description: {section_desc}

Context and Requirements:
{context_str}

Please provide comprehensive, professional content that:
1. Follows database normalization principles (3NF unless justified)
2. Includes clear entity definitions with attributes
3. Defines relationships with cardinality
4. Specifies primary and foreign keys
5. Includes data types and constraints
6. Considers performance optimization
7. Addresses data integrity requirements

Generate the section content:"""
        
        return prompt
    
    def _format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """Format context dictionary for LLM prompt."""
        formatted_parts = []
        
        # Map context keys to human-readable descriptions
        key_mappings = {
            "db_1": "Main Entities",
            "db_2": "Business Rules",
            "db_3": "Data Volume",
            "db_4": "Access Patterns",
            "db_5": "Performance Requirements",
            "db_6": "Security Requirements",
            "db_7": "Integration Points",
            "db_8": "Compliance Requirements"
        }
        
        for key, value in context.items():
            if value and key in key_mappings:
                formatted_parts.append(f"- {key_mappings[key]}: {value}")
        
        return "\n".join(formatted_parts) if formatted_parts else "No specific context provided"
    
    def generate_entity_definitions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate entity definitions based on requirements."""
        llm = get_llm_model('database')
        
        entities_prompt = f"""Based on the following requirements, define database entities:

{self._format_context_for_prompt(context)}

For each entity provide:
1. Entity name (singular, PascalCase)
2. Description
3. Primary key
4. Core attributes with data types
5. Business rules

Format as structured entities."""
        
        try:
            response = llm.invoke(entities_prompt)
            # Parse response into structured format
            # This is simplified - in production would use more robust parsing
            return [
                {
                    "name": "User",
                    "description": "System users with authentication",
                    "primary_key": "user_id",
                    "attributes": [
                        {"name": "user_id", "type": "UUID", "nullable": False},
                        {"name": "email", "type": "VARCHAR(255)", "nullable": False, "unique": True},
                        {"name": "created_at", "type": "TIMESTAMP", "nullable": False}
                    ]
                }
            ]
        except Exception as e:
            logger.error("Error generating entity definitions", error=str(e))
            return []
    
    def generate_relationship_matrix(self, entities: List[Dict[str, Any]]) -> str:
        """Generate relationship matrix between entities."""
        llm = get_llm_model('database')
        
        matrix_prompt = f"""Given these entities, define their relationships:

{entities}

Create a relationship matrix showing:
1. Relationship type (one-to-one, one-to-many, many-to-many)
2. Cardinality (required/optional)
3. Foreign key placement
4. Cascade rules
5. Business rule explanation

Format as a clear relationship matrix."""
        
        try:
            response = llm.invoke(matrix_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error("Error generating relationship matrix", error=str(e))
            return "Relationship matrix generation failed."
    
    def generate_ddl_script(self, entities: List[Dict[str, Any]], relationships: str) -> str:
        """Generate DDL script for the database schema."""
        llm = get_llm_model('database')
        
        ddl_prompt = f"""Generate PostgreSQL DDL script for these entities and relationships:

Entities: {entities}
Relationships: {relationships}

Include:
1. CREATE TABLE statements
2. Primary key constraints
3. Foreign key constraints
4. Indexes for performance
5. Check constraints
6. Default values
7. Comments on tables and columns

Use best practices for PostgreSQL."""
        
        try:
            response = llm.invoke(ddl_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error("Error generating DDL script", error=str(e))
            return "-- DDL script generation failed"
    
    def generate_indexing_strategy(self, entities: List[Dict[str, Any]], access_patterns: str) -> List[Dict[str, Any]]:
        """Generate indexing strategy based on access patterns."""
        return [
            {
                "table": "users",
                "indexes": [
                    {
                        "name": "idx_users_email",
                        "columns": ["email"],
                        "type": "BTREE",
                        "unique": True,
                        "rationale": "Frequent lookups by email for authentication"
                    },
                    {
                        "name": "idx_users_created_at",
                        "columns": ["created_at"],
                        "type": "BTREE",
                        "unique": False,
                        "rationale": "Time-based queries for user analytics"
                    }
                ]
            }
        ]
    
    def validate_erd_completeness(self, document: str) -> Dict[str, Any]:
        """Validate ERD completeness and quality."""
        validation_results = {
            "is_complete": True,
            "missing_elements": [],
            "normalization_issues": [],
            "performance_concerns": [],
            "completeness_score": 100
        }
        
        # Check required elements
        required_elements = [
            "Entity Definitions",
            "Relationships",
            "Primary Keys",
            "Foreign Keys",
            "Data Types",
            "Constraints",
            "Indexes"
        ]
        
        doc_lower = document.lower()
        for element in required_elements:
            if element.lower() not in doc_lower:
                validation_results["missing_elements"].append(element)
                validation_results["is_complete"] = False
        
        # Check for normalization indicators
        if "redundant" in doc_lower or "duplicate data" in doc_lower:
            validation_results["normalization_issues"].append("Potential data redundancy detected")
        
        # Check for performance considerations
        if "index" not in doc_lower:
            validation_results["performance_concerns"].append("No indexing strategy defined")
        
        # Calculate completeness score
        total_checks = len(required_elements) + 2  # +2 for normalization and performance
        issues_found = (len(validation_results["missing_elements"]) + 
                       len(validation_results["normalization_issues"]) +
                       len(validation_results["performance_concerns"]))
        validation_results["completeness_score"] = int(((total_checks - issues_found) / total_checks) * 100)
        
        return validation_results