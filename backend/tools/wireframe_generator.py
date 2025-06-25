"""
Wireframe Generator Tool for CrewAI implementation.
Generates wireframe descriptions and layout specifications.
"""

from typing import Dict, Any
from pydantic import Field
from .base_template_tool import BaseTemplateTool
from ..config import get_llm_model
import structlog

logger = structlog.get_logger()


class WireframeGeneratorTool(BaseTemplateTool):
    """Tool for generating wireframe descriptions and layout specifications."""
    
    name: str = Field(default="Wireframe Generator")
    description: str = Field(default="Generates detailed wireframe descriptions and UI layout specifications")
    template_name: str = Field(default="wireframes")
    
    def _generate_with_llm(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate section content using LLM for dynamic sections."""
        llm = get_llm_model('designer')
        
        # Build prompt based on section requirements
        prompt = self._build_section_prompt(section, context)
        
        try:
            response = llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Error generating wireframe section with LLM", section=section.get("id"), error=str(e))
            return f"[Error generating content for {section.get('title', 'section')}]"
    
    def _build_section_prompt(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build LLM prompt for section generation."""
        section_title = section.get("title", "")
        section_desc = section.get("description", "")
        
        # Extract relevant context
        context_str = self._format_context_for_prompt(context)
        
        prompt = f"""Generate content for the '{section_title}' section of wireframe specifications.

Section Description: {section_desc}

Context and Requirements:
{context_str}

Please provide detailed wireframe specifications that:
1. Describe layout structure and components
2. Define user interaction patterns
3. Specify content hierarchy and navigation
4. Include responsive design considerations
5. Address accessibility requirements
6. Use clear, implementable descriptions

Generate the section content:"""
        
        return prompt
    
    def _format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """Format context dictionary for LLM prompt."""
        formatted_parts = []
        
        # Map context keys to human-readable descriptions
        key_mappings = {
            "ux_1": "User Interface Requirements",
            "ux_2": "User Experience Goals",
            "ux_3": "Design Principles",
            "ux_4": "Content Structure",
            "ux_5": "Navigation Pattern",
            "ux_6": "Interaction Design",
            "ux_7": "Visual Hierarchy",
            "ux_8": "Responsive Behavior"
        }
        
        for key, value in context.items():
            if value and key in key_mappings:
                formatted_parts.append(f"- {key_mappings[key]}: {value}")
        
        return "\n".join(formatted_parts) if formatted_parts else "No specific context provided"
    
    def generate_component_specs(self, context: Dict[str, Any]) -> str:
        """Generate detailed component specifications."""
        llm = get_llm_model('designer')
        
        component_prompt = f"""Based on the following project context, generate detailed component specifications:

{self._format_context_for_prompt(context)}

For each major component, provide:
1. Component name and purpose
2. Layout structure (grid, flexbox, etc.)
3. Interactive elements and behaviors
4. Content requirements
5. State variations (hover, active, disabled)
6. Responsive breakpoints

Component Specifications:"""
        
        try:
            response = llm.invoke(component_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error("Error generating component specs", error=str(e))
            return "Component specification generation failed."
    
    def generate_user_flow_wireframes(self, context: Dict[str, Any]) -> str:
        """Generate wireframes for key user flows."""
        llm = get_llm_model('designer')
        
        flow_prompt = f"""Based on the following project context, create wireframe descriptions for key user flows:

{self._format_context_for_prompt(context)}

For each user flow, describe:
1. Entry point and initial state
2. Step-by-step screen progression
3. Decision points and branching
4. Error states and edge cases
5. Success/completion states
6. Navigation between screens

User Flow Wireframes:"""
        
        try:
            response = llm.invoke(flow_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error("Error generating user flow wireframes", error=str(e))
            return "User flow wireframe generation failed."