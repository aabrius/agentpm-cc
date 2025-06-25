"""
BRD Generator Tool for CrewAI implementation.
Generates comprehensive Business Requirements Documents.
"""

from typing import Dict, Any
from pydantic import Field
from .base_template_tool import BaseTemplateTool
from ..config import get_llm_model
import structlog

logger = structlog.get_logger()


class BRDGeneratorTool(BaseTemplateTool):
    """Tool for generating Business Requirements Documents."""
    
    name: str = Field(default="BRD Generator")
    description: str = Field(default="Generates comprehensive Business Requirements Documents following best practices")
    template_name: str = Field(default="brd")
    
    def _generate_with_llm(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate section content using LLM for dynamic sections."""
        llm = get_llm_model('business_analyst')
        
        # Build prompt based on section requirements
        prompt = self._build_section_prompt(section, context)
        
        try:
            response = llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Error generating BRD section with LLM", section=section.get("id"), error=str(e))
            return f"[Error generating content for {section.get('title', 'section')}]"
    
    def _build_section_prompt(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build LLM prompt for section generation."""
        section_title = section.get("title", "")
        section_desc = section.get("description", "")
        
        # Extract relevant context
        context_str = self._format_context_for_prompt(context)
        
        prompt = f"""Generate content for the '{section_title}' section of a Business Requirements Document.

Section Description: {section_desc}

Context and Requirements:
{context_str}

Please provide comprehensive, professional content that:
1. Focuses on business objectives and value
2. Clearly defines business processes and workflows
3. Identifies stakeholder needs and concerns
4. Provides measurable success criteria
5. Aligns with organizational goals
6. Is written for business stakeholders

Generate the section content:"""
        
        return prompt
    
    def _format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """Format context dictionary for LLM prompt."""
        formatted_parts = []
        
        # Map context keys to human-readable descriptions
        key_mappings = {
            "business_1": "Business Problem",
            "business_2": "Current Process",
            "business_3": "Desired Outcome",
            "business_4": "Stakeholders",
            "business_5": "Success Metrics",
            "business_6": "Constraints",
            "business_7": "Dependencies",
            "business_8": "Risks"
        }
        
        for key, value in context.items():
            if value and key in key_mappings:
                formatted_parts.append(f"- {key_mappings[key]}: {value}")
        
        return "\n".join(formatted_parts) if formatted_parts else "No specific context provided"
    
    def enhance_document(self, document: str, context: Dict[str, Any]) -> str:
        """Enhance the generated document with additional insights."""
        llm = get_llm_model('business_analyst')
        
        enhancement_prompt = f"""Review and enhance this Business Requirements Document:

{document}

Please:
1. Add any missing business context
2. Strengthen the business case and ROI
3. Ensure all stakeholder perspectives are represented
4. Verify process flows are complete
5. Add relevant industry best practices
6. Ensure alignment with strategic objectives

Return the enhanced document maintaining the same structure:"""
        
        try:
            response = llm.invoke(enhancement_prompt)
            enhanced = response.content if hasattr(response, 'content') else str(response)
            return enhanced
        except Exception as e:
            logger.error("Error enhancing BRD", error=str(e))
            return document  # Return original if enhancement fails
    
    def generate_executive_summary(self, document: str) -> str:
        """Generate an executive summary from the complete document."""
        llm = get_llm_model('business_analyst')
        
        summary_prompt = f"""Based on this Business Requirements Document, generate a concise executive summary:

{document}

The executive summary should:
1. Be 200-300 words
2. Highlight the key business problem and opportunity
3. Summarize the proposed solution and benefits
4. Include expected ROI and business impact
5. Mention key stakeholders and timeline

Executive Summary:"""
        
        try:
            response = llm.invoke(summary_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error("Error generating executive summary", error=str(e))
            return "Executive summary generation failed."
    
    def validate_brd_completeness(self, document: str) -> Dict[str, Any]:
        """Validate BRD completeness and quality."""
        validation_results = {
            "is_complete": True,
            "missing_sections": [],
            "quality_issues": [],
            "completeness_score": 100
        }
        
        # Check required sections
        required_sections = [
            "Executive Summary",
            "Business Objectives",
            "Current State Analysis",
            "Future State Vision",
            "Gap Analysis",
            "Stakeholder Analysis",
            "Success Metrics",
            "Implementation Roadmap"
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