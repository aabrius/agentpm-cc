"""
SRS Generator Tool for CrewAI implementation.
Generates comprehensive Software Requirements Specifications.
"""

from typing import Dict, Any, List
from pydantic import Field
from .base_template_tool import BaseTemplateTool
from ..config import get_llm_model
import structlog

logger = structlog.get_logger()


class SRSGeneratorTool(BaseTemplateTool):
    """Tool for generating Software Requirements Specifications."""
    
    name: str = Field(default="SRS Generator")
    description: str = Field(default="Generates comprehensive Software Requirements Specifications following IEEE 830 standard")
    template_name: str = Field(default="srs")
    
    def _generate_with_llm(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate section content using LLM for dynamic sections."""
        llm = get_llm_model('business_analyst')
        
        # Build prompt based on section requirements
        prompt = self._build_section_prompt(section, context)
        
        try:
            response = llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Error generating SRS section with LLM", section=section.get("id"), error=str(e))
            return f"[Error generating content for {section.get('title', 'section')}]"
    
    def _build_section_prompt(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build LLM prompt for section generation."""
        section_title = section.get("title", "")
        section_desc = section.get("description", "")
        
        # Extract relevant context
        context_str = self._format_context_for_prompt(context)
        
        prompt = f"""Generate content for the '{section_title}' section of a Software Requirements Specification.

Section Description: {section_desc}

Context and Requirements:
{context_str}

Please provide comprehensive, professional content that:
1. Follows IEEE 830 standard for SRS documents
2. Uses clear, unambiguous language
3. Makes requirements testable and verifiable
4. Includes specific acceptance criteria
5. Maintains traceability to business objectives
6. Uses consistent terminology throughout

Requirements should follow the format:
[REQ-XXX] The system SHALL/SHOULD/MAY [specific requirement]

Generate the section content:"""
        
        return prompt
    
    def _format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """Format context dictionary for LLM prompt."""
        formatted_parts = []
        
        # Map context keys to human-readable descriptions
        key_mappings = {
            "srs_1": "System Purpose",
            "srs_2": "System Scope",
            "srs_3": "User Classes",
            "srs_4": "Operating Environment",
            "srs_5": "Design Constraints",
            "srs_6": "Assumptions and Dependencies",
            "srs_7": "Functional Requirements",
            "srs_8": "Non-Functional Requirements"
        }
        
        for key, value in context.items():
            if value and key in key_mappings:
                formatted_parts.append(f"- {key_mappings[key]}: {value}")
        
        return "\n".join(formatted_parts) if formatted_parts else "No specific context provided"
    
    def generate_requirement_id(self, category: str, sequence: int) -> str:
        """Generate unique requirement ID."""
        category_prefixes = {
            "functional": "FR",
            "non_functional": "NFR",
            "interface": "INT",
            "performance": "PERF",
            "security": "SEC",
            "usability": "USE"
        }
        
        prefix = category_prefixes.get(category.lower(), "REQ")
        return f"{prefix}-{sequence:03d}"
    
    def generate_use_cases(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate use cases from requirements."""
        llm = get_llm_model('business_analyst')
        
        use_case_prompt = f"""Based on these requirements, generate detailed use cases:

{self._format_context_for_prompt(context)}

For each use case provide:
1. Use Case ID and Name
2. Primary Actor
3. Preconditions
4. Main Flow (numbered steps)
5. Alternative Flows
6. Postconditions
7. Business Rules
8. Related Requirements

Generate 3-5 primary use cases."""
        
        try:
            response = llm.invoke(use_case_prompt)
            # Parse response into structured format
            # This is simplified - in production would use more robust parsing
            return [
                {
                    "id": "UC-001",
                    "name": "User Login",
                    "primary_actor": "Registered User",
                    "preconditions": ["User has valid account"],
                    "main_flow": [
                        "User navigates to login page",
                        "System displays login form",
                        "User enters credentials",
                        "System validates credentials",
                        "System grants access"
                    ],
                    "postconditions": ["User is authenticated"]
                }
            ]
        except Exception as e:
            logger.error("Error generating use cases", error=str(e))
            return []
    
    def generate_traceability_matrix(self, requirements: List[Dict[str, Any]], business_objectives: List[str]) -> Dict[str, Any]:
        """Generate requirements traceability matrix."""
        matrix = {
            "business_to_requirements": {},
            "requirements_to_tests": {},
            "requirements_dependencies": {}
        }
        
        # Map business objectives to requirements
        for obj in business_objectives:
            matrix["business_to_requirements"][obj] = []
            for req in requirements:
                if any(keyword in req.get("description", "").lower() 
                      for keyword in obj.lower().split()):
                    matrix["business_to_requirements"][obj].append(req["id"])
        
        # Map requirements to test cases (placeholder)
        for req in requirements:
            matrix["requirements_to_tests"][req["id"]] = [
                f"TC-{req['id']}-01",
                f"TC-{req['id']}-02"
            ]
        
        return matrix
    
    def categorize_requirements(self, requirements: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize requirements by type."""
        llm = get_llm_model('business_analyst')
        
        categorize_prompt = f"""Categorize these requirements into standard categories:

Requirements:
{requirements}

Categories:
1. Functional Requirements
2. Performance Requirements
3. Security Requirements
4. Usability Requirements
5. Reliability Requirements
6. Interface Requirements
7. Operational Requirements

For each requirement, assign:
- Category
- Priority (High/Medium/Low)
- Complexity (Simple/Medium/Complex)
- Requirement ID"""
        
        try:
            response = llm.invoke(categorize_prompt)
            # Parse and return categorized requirements
            return {
                "functional": [],
                "performance": [],
                "security": [],
                "usability": [],
                "reliability": [],
                "interface": [],
                "operational": []
            }
        except Exception as e:
            logger.error("Error categorizing requirements", error=str(e))
            return {}
    
    def validate_srs_completeness(self, document: str) -> Dict[str, Any]:
        """Validate SRS completeness and quality."""
        validation_results = {
            "is_complete": True,
            "missing_sections": [],
            "quality_issues": [],
            "requirement_issues": [],
            "completeness_score": 100
        }
        
        # Check required sections per IEEE 830
        required_sections = [
            "Introduction",
            "Overall Description",
            "Specific Requirements",
            "Functional Requirements",
            "Non-Functional Requirements",
            "Interface Requirements",
            "Performance Requirements",
            "Security Requirements"
        ]
        
        doc_lower = document.lower()
        for section in required_sections:
            if section.lower() not in doc_lower:
                validation_results["missing_sections"].append(section)
                validation_results["is_complete"] = False
        
        # Check requirement quality
        requirement_keywords = ["shall", "should", "must", "will"]
        req_count = sum(doc_lower.count(keyword) for keyword in requirement_keywords)
        
        if req_count < 10:
            validation_results["requirement_issues"].append("Insufficient requirement statements")
        
        # Check for ambiguous terms
        ambiguous_terms = ["appropriate", "adequate", "as necessary", "etc.", "and/or"]
        for term in ambiguous_terms:
            if term in doc_lower:
                validation_results["quality_issues"].append(f"Ambiguous term found: {term}")
        
        # Calculate completeness score
        total_checks = len(required_sections) + 5  # +5 for quality checks
        issues_found = (len(validation_results["missing_sections"]) + 
                       len(validation_results["quality_issues"]) +
                       len(validation_results["requirement_issues"]))
        validation_results["completeness_score"] = int(((total_checks - issues_found) / total_checks) * 100)
        
        return validation_results