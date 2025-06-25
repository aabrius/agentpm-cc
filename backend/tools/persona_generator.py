"""
Persona Generator Tool for CrewAI implementation.
Generates detailed user personas and journey maps.
"""

from typing import Dict, Any
from pydantic import Field
from .base_template_tool import BaseTemplateTool
from ..config import get_llm_model
import structlog

logger = structlog.get_logger()


class PersonaGeneratorTool(BaseTemplateTool):
    """Tool for generating user personas and journey maps."""
    
    name: str = Field(default="Persona Generator")
    description: str = Field(default="Generates detailed user personas and customer journey maps")
    template_name: str = Field(default="personas")
    
    def _generate_with_llm(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate section content using LLM for dynamic sections."""
        llm = get_llm_model('user_researcher')
        
        # Build prompt based on section requirements
        prompt = self._build_section_prompt(section, context)
        
        try:
            response = llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Error generating persona section with LLM", section=section.get("id"), error=str(e))
            return f"[Error generating content for {section.get('title', 'section')}]"
    
    def _build_section_prompt(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build LLM prompt for section generation."""
        section_title = section.get("title", "")
        section_desc = section.get("description", "")
        
        # Extract relevant context
        context_str = self._format_context_for_prompt(context)
        
        prompt = f"""Generate content for the '{section_title}' section of user persona documentation.

Section Description: {section_desc}

Context and Requirements:
{context_str}

Please provide comprehensive persona information that:
1. Creates realistic, research-based user profiles
2. Includes demographic and psychographic details
3. Defines goals, motivations, and pain points
4. Describes user behaviors and preferences
5. Identifies technology usage patterns
6. Maps to specific product use cases

Generate the section content:"""
        
        return prompt
    
    def _format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """Format context dictionary for LLM prompt."""
        formatted_parts = []
        
        # Map context keys to human-readable descriptions
        key_mappings = {
            "user_1": "Target Audience",
            "user_2": "User Demographics",
            "user_3": "User Goals",
            "user_4": "Pain Points",
            "user_5": "Behaviors",
            "user_6": "Technology Usage",
            "user_7": "Preferences",
            "user_8": "Context of Use"
        }
        
        for key, value in context.items():
            if value and key in key_mappings:
                formatted_parts.append(f"- {key_mappings[key]}: {value}")
        
        return "\n".join(formatted_parts) if formatted_parts else "No specific context provided"
    
    def generate_primary_personas(self, context: Dict[str, Any]) -> str:
        """Generate primary user personas."""
        llm = get_llm_model('user_researcher')
        
        persona_prompt = f"""Based on the following project context, create 2-3 primary user personas:

{self._format_context_for_prompt(context)}

For each persona, provide:
1. Name, age, occupation, and background
2. Goals and motivations
3. Frustrations and pain points
4. Technology comfort level and preferences
5. Typical day and context of product use
6. Quote that captures their perspective
7. Photo/visual description

Primary Personas:"""
        
        try:
            response = llm.invoke(persona_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error("Error generating primary personas", error=str(e))
            return "Primary persona generation failed."
    
    def generate_journey_maps(self, context: Dict[str, Any]) -> str:
        """Generate customer journey maps for key personas."""
        llm = get_llm_model('user_researcher')
        
        journey_prompt = f"""Based on the following project context, create customer journey maps:

{self._format_context_for_prompt(context)}

For each journey map, include:
1. Awareness stage (how they discover the need)
2. Consideration stage (research and evaluation)
3. Decision stage (selection and purchase/signup)
4. Onboarding stage (first use experience)
5. Usage stage (regular interaction patterns)
6. Advocacy stage (sharing and recommending)

For each stage, define:
- User actions and behaviors
- Thoughts and emotions
- Pain points and frustrations
- Opportunities for improvement
- Touchpoints with the product/service

Customer Journey Maps:"""
        
        try:
            response = llm.invoke(journey_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error("Error generating journey maps", error=str(e))
            return "Journey map generation failed."
    
    def generate_empathy_maps(self, context: Dict[str, Any]) -> str:
        """Generate empathy maps for understanding user perspectives."""
        llm = get_llm_model('user_researcher')
        
        empathy_prompt = f"""Based on the following project context, create empathy maps for key user segments:

{self._format_context_for_prompt(context)}

For each empathy map, define what users:
1. THINK: Thoughts, beliefs, and preoccupations
2. FEEL: Emotions and feelings
3. SEE: Environment, friends, market offerings
4. SAY & DO: Attitude in public, behavior toward others
5. PAIN: Fears, frustrations, and obstacles
6. GAIN: Wants, needs, measures of success

Empathy Maps:"""
        
        try:
            response = llm.invoke(empathy_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error("Error generating empathy maps", error=str(e))
            return "Empathy map generation failed."