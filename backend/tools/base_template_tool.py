"""
Base template tool for CrewAI implementation.
Provides common functionality for all document generation tools.
"""

from crewai_tools import BaseTool
from pydantic import Field
from typing import Dict, Any, Optional
import yaml
import json
from pathlib import Path
from jinja2 import Template
import structlog

logger = structlog.get_logger()


class BaseTemplateTool(BaseTool):
    """Base class for all template-based document generation tools."""
    
    name: str = Field(default="Base Template Tool")
    description: str = Field(default="Base tool for template-based document generation")
    template_name: str = Field(default="base")
    template_path: Optional[str] = Field(default=None)
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.template_path:
            # Default to backend/templates/{template_name}/structure.yaml
            self.template_path = f"backend/templates/{self.template_name}/structure.yaml"
    
    def _run(self, context: Dict[str, Any]) -> str:
        """Generate document based on template and context."""
        try:
            # Load template
            template_data = self._load_template()
            
            # Process sections
            sections = self._process_sections(template_data.get("sections", []), context)
            
            # Generate document
            document = self._generate_document(sections, template_data, context)
            
            # Validate
            if not self._validate_document(document, template_data.get("validation_rules", {})):
                logger.warning(f"Document validation failed for {self.template_name}")
            
            return document
            
        except Exception as e:
            logger.error(f"Error generating {self.template_name} document", error=str(e))
            raise
    
    def _load_template(self) -> Dict[str, Any]:
        """Load YAML template from file."""
        template_file = Path(self.template_path)
        
        if not template_file.exists():
            # Try relative to project root
            template_file = Path(__file__).parent.parent.parent / self.template_path
        
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        
        with open(template_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _process_sections(self, sections: list, context: Dict[str, Any]) -> Dict[str, str]:
        """Process template sections with context."""
        processed_sections = {}
        
        for section in sections:
            section_id = section.get("id", "")
            section_title = section.get("title", "")
            section_content = self._generate_section_content(section, context)
            
            processed_sections[section_id] = {
                "title": section_title,
                "content": section_content,
                "order": section.get("order", 999),
                "required": section.get("required", False)
            }
        
        return processed_sections
    
    def _generate_section_content(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate content for a specific section."""
        # Extract questions for this section
        questions = section.get("questions", [])
        section_context = {}
        
        # Map questions to context values
        for question in questions:
            q_id = question.get("id", "")
            if q_id in context:
                section_context[q_id] = context[q_id]
        
        # Generate content using LLM if needed
        if self._should_use_llm(section, section_context):
            return self._generate_with_llm(section, section_context)
        else:
            return self._generate_with_template(section, section_context)
    
    def _should_use_llm(self, section: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Determine if LLM generation is needed for this section."""
        # Use LLM if section has dynamic content or insufficient context
        return section.get("dynamic", False) or len(context) < 2
    
    def _generate_with_llm(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate section content using LLM."""
        # This will be implemented by child classes
        raise NotImplementedError("Child classes must implement _generate_with_llm")
    
    def _generate_with_template(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate section content using Jinja2 template."""
        template_str = section.get("template", "")
        if not template_str:
            # Build default template from questions
            template_parts = []
            for question in section.get("questions", []):
                q_id = question.get("id", "")
                q_content = question.get("content", "")
                template_parts.append(f"**{q_content}**\n{{{{ {q_id} | default('To be defined') }}}}")
            template_str = "\n\n".join(template_parts)
        
        template = Template(template_str)
        return template.render(**context)
    
    def _generate_document(self, sections: Dict[str, Any], template_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Compile sections into final document."""
        # Sort sections by order
        sorted_sections = sorted(sections.items(), key=lambda x: x[1]["order"])
        
        # Build document
        document_parts = []
        
        # Add title
        title = template_data.get("title", "Document")
        document_parts.append(f"# {title}\n")
        
        # Add metadata
        if context.get("include_metadata", True):
            document_parts.append(self._generate_metadata(context))
        
        # Add sections
        for section_id, section_data in sorted_sections:
            if section_data["content"]:
                level = "##" if section_data.get("order", 0) < 10 else "###"
                document_parts.append(f"\n{level} {section_data['title']}\n")
                document_parts.append(section_data["content"])
        
        # Add footer
        document_parts.append(self._generate_footer())
        
        return "\n".join(document_parts)
    
    def _generate_metadata(self, context: Dict[str, Any]) -> str:
        """Generate document metadata section."""
        from datetime import datetime
        
        metadata = [
            "## Document Information\n",
            f"- **Generated**: {datetime.utcnow().isoformat()}",
            f"- **Type**: {self.template_name.upper()}",
            f"- **Version**: {context.get('version', '1.0')}",
        ]
        
        if context.get("author"):
            metadata.append(f"- **Author**: {context['author']}")
        
        if context.get("project_name"):
            metadata.append(f"- **Project**: {context['project_name']}")
        
        metadata.append("")  # Empty line
        return "\n".join(metadata)
    
    def _generate_footer(self) -> str:
        """Generate document footer."""
        return "\n---\n\n*Generated by AgentPM 2.0 - CrewAI Implementation*"
    
    def _validate_document(self, document: str, rules: Dict[str, Any]) -> bool:
        """Validate generated document against rules."""
        if not rules:
            rules = self.validation_rules
        
        # Basic validation
        if not document or len(document) < 100:
            return False
        
        # Check for required sections
        if rules.get("all_required_sections_present"):
            # This would check that all required sections have content
            pass
        
        # Check minimum completion
        min_completion = rules.get("minimum_questions_answered_per_section", 0.75)
        # This would calculate completion percentage
        
        # Check for placeholders
        placeholders = ["to be defined", "todo", "tbd", "[placeholder]"]
        for placeholder in placeholders:
            if placeholder.lower() in document.lower():
                logger.warning(f"Found placeholder text in {self.template_name}: {placeholder}")
        
        return True
    
    def get_required_fields(self) -> list:
        """Get list of required fields for this template."""
        template_data = self._load_template()
        required_fields = []
        
        for section in template_data.get("sections", []):
            for question in section.get("questions", []):
                if question.get("required", False):
                    required_fields.append({
                        "id": question["id"],
                        "content": question["content"],
                        "section": section.get("title", "")
                    })
        
        return required_fields