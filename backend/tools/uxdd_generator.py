"""
UXDD Generator Tool for CrewAI implementation.
Generates comprehensive UX Design Documents.
"""

from typing import Dict, Any, List
from pydantic import Field
from .base_template_tool import BaseTemplateTool
from ..config import get_llm_model
import structlog

logger = structlog.get_logger()


class UXDDGeneratorTool(BaseTemplateTool):
    """Tool for generating UX Design Documents."""
    
    name: str = Field(default="UXDD Generator")
    description: str = Field(default="Generates comprehensive UX Design Documents with user-centered design principles")
    template_name: str = Field(default="uxdd")
    
    def _generate_with_llm(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate section content using LLM for dynamic sections."""
        llm = get_llm_model('designer')
        
        # Build prompt based on section requirements
        prompt = self._build_section_prompt(section, context)
        
        try:
            response = llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Error generating UXDD section with LLM", section=section.get("id"), error=str(e))
            return f"[Error generating content for {section.get('title', 'section')}]"
    
    def _build_section_prompt(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build LLM prompt for section generation."""
        section_title = section.get("title", "")
        section_desc = section.get("description", "")
        
        # Extract relevant context
        context_str = self._format_context_for_prompt(context)
        
        prompt = f"""Generate content for the '{section_title}' section of a UX Design Document.

Section Description: {section_desc}

Context and Requirements:
{context_str}

Please provide comprehensive, professional content that:
1. Follows user-centered design principles
2. Includes specific design rationale and decisions
3. Considers accessibility and inclusive design
4. Provides clear visual hierarchy and information architecture
5. Addresses user goals and pain points
6. Includes interaction patterns and micro-interactions

Generate the section content:"""
        
        return prompt
    
    def _format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """Format context dictionary for LLM prompt."""
        formatted_parts = []
        
        # Map context keys to human-readable descriptions
        key_mappings = {
            "ux_1": "User Research Findings",
            "ux_2": "Target User Personas",
            "ux_3": "User Goals and Tasks",
            "ux_4": "Design Principles",
            "ux_5": "Visual Style Guide",
            "ux_6": "Interaction Patterns",
            "ux_7": "Accessibility Requirements",
            "ux_8": "Device and Platform Requirements"
        }
        
        for key, value in context.items():
            if value and key in key_mappings:
                formatted_parts.append(f"- {key_mappings[key]}: {value}")
        
        return "\n".join(formatted_parts) if formatted_parts else "No specific context provided"
    
    def generate_design_principles(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate design principles based on project context."""
        llm = get_llm_model('designer')
        
        principles_prompt = f"""Based on the following project context, generate 5-7 design principles:

{self._format_context_for_prompt(context)}

For each principle provide:
1. Principle name (2-4 words)
2. Description (1-2 sentences)
3. Example application

Format as a structured list."""
        
        try:
            response = llm.invoke(principles_prompt)
            # Parse response into structured format
            # This is simplified - in production would use more robust parsing
            return [
                {
                    "name": "User-First Design",
                    "description": "Every design decision prioritizes user needs and goals.",
                    "example": "Navigation structure based on user mental models, not organizational structure."
                }
            ]
        except Exception as e:
            logger.error("Error generating design principles", error=str(e))
            return []
    
    def generate_user_flows(self, context: Dict[str, Any]) -> str:
        """Generate user flow descriptions."""
        llm = get_llm_model('designer')
        
        flows_prompt = f"""Based on the project context, describe the main user flows:

{self._format_context_for_prompt(context)}

For each flow include:
1. Flow name and objective
2. Entry point
3. Step-by-step progression
4. Decision points
5. Success criteria
6. Error states and recovery

Focus on the 3-5 most critical flows."""
        
        try:
            response = llm.invoke(flows_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error("Error generating user flows", error=str(e))
            return "User flow generation failed."
    
    def generate_accessibility_checklist(self, document: str) -> List[Dict[str, Any]]:
        """Generate accessibility checklist based on the design."""
        checklist = [
            {
                "category": "Visual Design",
                "items": [
                    {"check": "Color contrast meets WCAG AA standards", "required": True},
                    {"check": "Text is readable at various zoom levels", "required": True},
                    {"check": "Focus indicators are clearly visible", "required": True}
                ]
            },
            {
                "category": "Interaction Design",
                "items": [
                    {"check": "All interactive elements are keyboard accessible", "required": True},
                    {"check": "Touch targets meet minimum size requirements", "required": True},
                    {"check": "Time-based interactions can be paused/extended", "required": False}
                ]
            },
            {
                "category": "Content Structure",
                "items": [
                    {"check": "Proper heading hierarchy is maintained", "required": True},
                    {"check": "Images have appropriate alt text", "required": True},
                    {"check": "Form labels are associated with inputs", "required": True}
                ]
            }
        ]
        
        return checklist
    
    def validate_uxdd_completeness(self, document: str) -> Dict[str, Any]:
        """Validate UXDD completeness and quality."""
        validation_results = {
            "is_complete": True,
            "missing_sections": [],
            "quality_issues": [],
            "accessibility_gaps": [],
            "completeness_score": 100
        }
        
        # Check required sections
        required_sections = [
            "Executive Summary",
            "User Research",
            "Information Architecture",
            "User Flows",
            "Wireframes",
            "Visual Design",
            "Interaction Design",
            "Accessibility"
        ]
        
        doc_lower = document.lower()
        for section in required_sections:
            if section.lower() not in doc_lower:
                validation_results["missing_sections"].append(section)
                validation_results["is_complete"] = False
        
        # Check for accessibility mentions
        accessibility_keywords = ["wcag", "screen reader", "keyboard", "contrast", "alt text"]
        accessibility_found = sum(1 for keyword in accessibility_keywords if keyword in doc_lower)
        
        if accessibility_found < 3:
            validation_results["accessibility_gaps"].append("Insufficient accessibility considerations")
        
        # Calculate completeness score
        total_checks = len(required_sections) + len(accessibility_keywords)
        issues_found = len(validation_results["missing_sections"]) + (5 - accessibility_found)
        validation_results["completeness_score"] = int(((total_checks - issues_found) / total_checks) * 100)
        
        return validation_results