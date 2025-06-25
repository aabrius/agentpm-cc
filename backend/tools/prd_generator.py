"""
PRD Generator Tool for CrewAI implementation.
Generates comprehensive Product Requirements Documents.
"""

from typing import Dict, Any
from pydantic import Field
from .base_template_tool import BaseTemplateTool
from ..config import get_llm_model
import structlog

logger = structlog.get_logger()


class PRDGeneratorTool(BaseTemplateTool):
    """Tool for generating Product Requirements Documents."""
    
    name: str = Field(default="PRD Generator")
    description: str = Field(default="Generates comprehensive Product Requirements Documents following industry best practices")
    template_name: str = Field(default="prd")
    
    def _generate_with_llm(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate section content using LLM for dynamic sections."""
        llm = get_llm_model('product_manager')
        
        # Build prompt based on section requirements
        prompt = self._build_section_prompt(section, context)
        
        try:
            response = llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Error generating PRD section with LLM", section=section.get("id"), error=str(e))
            return f"[Error generating content for {section.get('title', 'section')}]"
    
    def _build_section_prompt(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build LLM prompt for section generation."""
        section_title = section.get("title", "")
        section_desc = section.get("description", "")
        
        # Extract relevant context
        context_str = self._format_context_for_prompt(context)
        
        prompt = f"""Generate content for the '{section_title}' section of a Product Requirements Document.

Section Description: {section_desc}

Context and Requirements:
{context_str}

Please provide comprehensive, professional content that:
1. Is specific and actionable
2. Avoids placeholder text
3. Includes relevant details based on the context
4. Follows PRD best practices
5. Is written for both technical and non-technical stakeholders

Generate the section content:"""
        
        return prompt
    
    def _format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """Format context dictionary for LLM prompt."""
        formatted_parts = []
        
        # Map context keys to human-readable descriptions
        key_mappings = {
            "product_1": "Problem Statement",
            "product_2": "Target Users",
            "product_3": "Key Features",
            "product_4": "Success Metrics",
            "product_5": "Business Model",
            "product_6": "User Journeys",
            "product_7": "Technical Constraints",
            "product_8": "Timeline",
            "product_9": "Budget",
            "product_10": "Stakeholders",
            "product_11": "Risks"
        }
        
        for key, value in context.items():
            if value and key in key_mappings:
                formatted_parts.append(f"- {key_mappings[key]}: {value}")
        
        return "\n".join(formatted_parts) if formatted_parts else "No specific context provided"
    
    def enhance_document(self, document: str, context: Dict[str, Any]) -> str:
        """Enhance the generated document with additional insights."""
        llm = get_llm_model('product_manager')
        
        enhancement_prompt = f"""Review and enhance this Product Requirements Document:

{document}

Please:
1. Add any missing critical information
2. Ensure consistency across sections
3. Strengthen the business case if needed
4. Verify all success metrics are measurable
5. Add relevant industry insights where applicable

Return the enhanced document maintaining the same structure:"""
        
        try:
            response = llm.invoke(enhancement_prompt)
            enhanced = response.content if hasattr(response, 'content') else str(response)
            return enhanced
        except Exception as e:
            logger.error("Error enhancing PRD", error=str(e))
            return document  # Return original if enhancement fails
    
    def generate_executive_summary(self, document: str) -> str:
        """Generate an executive summary from the complete document."""
        llm = get_llm_model('product_manager')
        
        summary_prompt = f"""Based on this Product Requirements Document, generate a concise executive summary:

{document}

The executive summary should:
1. Be 200-300 words
2. Highlight the key problem and solution
3. Summarize main features and benefits
4. Include high-level success metrics
5. Mention timeline and key stakeholders

Executive Summary:"""
        
        try:
            response = llm.invoke(summary_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error("Error generating executive summary", error=str(e))
            return "Executive summary generation failed."
    
    def validate_prd_completeness(self, document: str) -> Dict[str, Any]:
        """Validate PRD completeness and quality."""
        validation_results = {
            "is_complete": True,
            "missing_sections": [],
            "quality_issues": [],
            "completeness_score": 100
        }
        
        # Check required sections
        required_sections = [
            "Executive Summary",
            "Problem Statement",
            "Goals and Objectives",
            "User Personas",
            "Functional Requirements",
            "Non-Functional Requirements",
            "Success Metrics",
            "Timeline"
        ]
        
        doc_lower = document.lower()
        for section in required_sections:
            if section.lower() not in doc_lower:
                validation_results["missing_sections"].append(section)
                validation_results["is_complete"] = False
        
        # Check for quality issues
        quality_markers = {
            "to be defined": "Placeholder text found",
            "todo": "Incomplete sections",
            "[placeholder]": "Placeholder content",
            "tbd": "Information to be determined"
        }
        
        for marker, issue in quality_markers.items():
            if marker in doc_lower:
                validation_results["quality_issues"].append(issue)
        
        # Calculate completeness score
        total_checks = len(required_sections) + len(quality_markers)
        issues_found = len(validation_results["missing_sections"]) + len(validation_results["quality_issues"])
        validation_results["completeness_score"] = int(((total_checks - issues_found) / total_checks) * 100)
        
        return validation_results