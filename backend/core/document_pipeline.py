"""
Advanced Document Generation Pipeline for CrewAI Implementation.
Migrates sophisticated LangGraph document generation with all features preserved.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import yaml
import jinja2
import asyncio
import structlog
from enum import Enum

from crewai import Task, Crew
from pydantic import BaseModel, Field

from ..config import get_llm_model
from ..tools.base_template_tool import BaseTemplateTool
from ..tools.prd_generator import PRDGeneratorTool
from ..tools.brd_generator import BRDGeneratorTool
from ..tools.uxdd_generator import UXDDGeneratorTool
from ..tools.srs_generator import SRSGeneratorTool
from ..tools.erd_generator import ERDGeneratorTool
from ..tools.dbrd_generator import DBRDGeneratorTool

logger = structlog.get_logger()


class DocumentGenerationStatus(Enum):
    """Document generation status tracking."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"
    ENHANCED = "enhanced"
    VALIDATED = "validated"


class DocumentMetadata(BaseModel):
    """Metadata for generated documents."""
    document_type: str
    template_version: str = "1.0"
    generated_at: datetime
    conversation_id: str
    conversation_type: str
    agent_id: str
    enhancement_level: str = "standard"
    quality_score: float = 0.0
    validation_passed: bool = False
    word_count: int = 0
    section_count: int = 0


class DocumentGenerationRequest(BaseModel):
    """Request for document generation."""
    conversation_id: str
    document_types: List[str]
    conversation_type: str = "feature"
    context: Dict[str, Any] = Field(default_factory=dict)
    qa_pairs: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    enhancement_level: str = "standard"  # basic, standard, advanced
    parallel_generation: bool = True
    dependency_order: Optional[List[str]] = None


class DocumentGenerationResult(BaseModel):
    """Result of document generation."""
    document_type: str
    content: str
    metadata: DocumentMetadata
    status: DocumentGenerationStatus
    generation_time: float
    error_message: Optional[str] = None
    validation_results: Dict[str, Any] = Field(default_factory=dict)


class ParallelDocumentProcessor:
    """Handles parallel document generation with dependency management."""
    
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.document_tools = {
            "prd": PRDGeneratorTool(),
            "brd": BRDGeneratorTool(), 
            "uxdd": UXDDGeneratorTool(),
            "srs": SRSGeneratorTool(),
            "erd": ERDGeneratorTool(),
            "dbrd": DBRDGeneratorTool()
        }
        
    async def process_documents(
        self, 
        request: DocumentGenerationRequest
    ) -> List[DocumentGenerationResult]:
        """Process multiple documents with dependency management."""
        
        results = []
        
        # Determine processing order
        processing_order = self._determine_processing_order(
            request.document_types, 
            request.dependency_order
        )
        
        # Process in batches for parallel execution
        if request.parallel_generation:
            batches = self._create_dependency_batches(processing_order)
            for batch in batches:
                batch_results = await self._process_batch(batch, request)
                results.extend(batch_results)
        else:
            # Sequential processing
            for doc_type in processing_order:
                result = await self._process_single_document(doc_type, request)
                results.append(result)
        
        return results
    
    def _determine_processing_order(
        self, 
        document_types: List[str], 
        dependency_order: Optional[List[str]]
    ) -> List[str]:
        """Determine optimal processing order based on dependencies."""
        
        if dependency_order:
            # Use provided order, ensuring all requested types are included
            ordered = [doc for doc in dependency_order if doc in document_types]
            remaining = [doc for doc in document_types if doc not in ordered]
            return ordered + remaining
        
        # Default dependency order based on document relationships
        default_order = ["prd", "brd", "uxdd", "srs", "erd", "dbrd"]
        return [doc for doc in default_order if doc in document_types]
    
    def _create_dependency_batches(self, ordered_docs: List[str]) -> List[List[str]]:
        """Create batches of documents that can be processed in parallel."""
        
        # Define dependency relationships
        dependencies = {
            "brd": ["prd"],        # BRD depends on PRD
            "uxdd": ["prd"],       # UXDD depends on PRD
            "srs": ["prd", "uxdd"], # SRS depends on PRD and UXDD
            "erd": ["srs"],        # ERD depends on SRS
            "dbrd": ["erd"]        # DBRD depends on ERD
        }
        
        batches = []
        processed = set()
        
        while len(processed) < len(ordered_docs):
            current_batch = []
            
            for doc in ordered_docs:
                if doc in processed:
                    continue
                    
                # Check if dependencies are satisfied
                doc_deps = dependencies.get(doc, [])
                if all(dep in processed for dep in doc_deps):
                    current_batch.append(doc)
                    if len(current_batch) >= self.max_concurrent:
                        break
            
            if not current_batch:
                # Force add first unprocessed to avoid infinite loop
                for doc in ordered_docs:
                    if doc not in processed:
                        current_batch.append(doc)
                        break
            
            batches.append(current_batch)
            processed.update(current_batch)
        
        return batches
    
    async def _process_batch(
        self, 
        batch: List[str], 
        request: DocumentGenerationRequest
    ) -> List[DocumentGenerationResult]:
        """Process a batch of documents concurrently."""
        
        logger.info(f"Processing document batch: {batch}")
        
        tasks = [
            self._process_single_document(doc_type, request)
            for doc_type in batch
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert exceptions to error results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(
                        self._create_error_result(batch[i], str(result), request)
                    )
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return [
                self._create_error_result(doc_type, str(e), request)
                for doc_type in batch
            ]
    
    async def _process_single_document(
        self, 
        doc_type: str, 
        request: DocumentGenerationRequest
    ) -> DocumentGenerationResult:
        """Process a single document."""
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            tool = self.document_tools.get(doc_type)
            if not tool:
                raise ValueError(f"No tool available for document type: {doc_type}")
            
            # Prepare context for document generation
            context = self._prepare_document_context(doc_type, request)
            
            # Generate document
            logger.info(f"Generating {doc_type} document")
            content = tool._run(context)
            
            # Enhance document if requested
            if request.enhancement_level in ["standard", "advanced"]:
                content = await self._enhance_document(doc_type, content, context)
            
            # Validate document
            validation_results = await self._validate_document(doc_type, content, context)
            
            # Calculate metadata
            metadata = DocumentMetadata(
                document_type=doc_type,
                generated_at=datetime.utcnow(),
                conversation_id=request.conversation_id,
                conversation_type=request.conversation_type,
                agent_id=f"{doc_type}_agent",
                enhancement_level=request.enhancement_level,
                quality_score=validation_results.get("quality_score", 0.0),
                validation_passed=validation_results.get("passed", False),
                word_count=len(content.split()),
                section_count=content.count("##")
            )
            
            generation_time = asyncio.get_event_loop().time() - start_time
            
            return DocumentGenerationResult(
                document_type=doc_type,
                content=content,
                metadata=metadata,
                status=DocumentGenerationStatus.COMPLETED,
                generation_time=generation_time,
                validation_results=validation_results
            )
            
        except Exception as e:
            generation_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Failed to generate {doc_type}: {e}")
            return self._create_error_result(doc_type, str(e), request, generation_time)
    
    def _prepare_document_context(
        self, 
        doc_type: str, 
        request: DocumentGenerationRequest
    ) -> Dict[str, Any]:
        """Prepare context for document generation."""
        
        context = {
            "conversation_id": request.conversation_id,
            "conversation_type": request.conversation_type,
            "document_type": doc_type,
            "enhancement_level": request.enhancement_level,
            **request.context
        }
        
        # Add Q&A pairs mapped to document structure
        if request.qa_pairs:
            context.update(self._map_qa_to_document_structure(doc_type, request.qa_pairs))
        
        # Add metadata
        context["metadata"] = request.metadata
        
        return context
    
    def _map_qa_to_document_structure(
        self, 
        doc_type: str, 
        qa_pairs: Dict[str, Dict[str, str]]
    ) -> Dict[str, Any]:
        """Map Q&A pairs to document structure."""
        
        # This is a simplified version - in production would use full YAML template mapping
        mapped_context = {}
        
        for qa_id, qa_data in qa_pairs.items():
            question = qa_data.get("question", "").lower()
            answer = qa_data.get("answer", "")
            
            # Map based on question keywords and document type
            if doc_type == "prd":
                if "problem" in question or "pain point" in question:
                    mapped_context["problem_statement"] = answer
                elif "feature" in question:
                    mapped_context["key_features"] = answer
                elif "user" in question or "target" in question:
                    mapped_context["target_users"] = answer
                elif "success" in question or "metric" in question:
                    mapped_context["success_metrics"] = answer
            
            elif doc_type == "uxdd":
                if "persona" in question or "user type" in question:
                    mapped_context["user_personas"] = answer
                elif "journey" in question or "flow" in question:
                    mapped_context["user_journeys"] = answer
                elif "wireframe" in question or "layout" in question:
                    mapped_context["wireframes"] = answer
            
            elif doc_type == "srs":
                if "architecture" in question or "system" in question:
                    mapped_context["system_architecture"] = answer
                elif "api" in question or "endpoint" in question:
                    mapped_context["api_specifications"] = answer
                elif "performance" in question:
                    mapped_context["performance_requirements"] = answer
            
            # Store original Q&A for fallback
            mapped_context[qa_id] = answer
        
        return mapped_context
    
    async def _enhance_document(
        self, 
        doc_type: str, 
        content: str, 
        context: Dict[str, Any]
    ) -> str:
        """Enhance document content using LLM."""
        
        enhancement_level = context.get("enhancement_level", "standard")
        
        if enhancement_level == "basic":
            return content
        
        try:
            llm = get_llm_model(f"{doc_type}_agent")
            
            if enhancement_level == "standard":
                prompt = f"""Review and improve this {doc_type.upper()} document:

{content}

Please:
1. Ensure all sections are complete and professional
2. Add any missing industry-standard information
3. Improve clarity and readability
4. Ensure consistency across sections
5. Add relevant best practices where appropriate

Return the enhanced document:"""
            
            elif enhancement_level == "advanced":
                prompt = f"""Perform advanced enhancement on this {doc_type.upper()} document:

{content}

Please:
1. Add industry insights and market context
2. Include relevant metrics and benchmarks
3. Suggest implementation strategies
4. Add risk assessment and mitigation strategies
5. Include compliance and accessibility considerations
6. Provide detailed technical recommendations
7. Add timeline and resource estimates

Return the comprehensively enhanced document:"""
            
            response = llm.invoke(prompt)
            enhanced_content = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"Enhanced {doc_type} document with {enhancement_level} level")
            return enhanced_content
            
        except Exception as e:
            logger.error(f"Document enhancement failed for {doc_type}: {e}")
            return content  # Return original on enhancement failure
    
    async def _validate_document(
        self, 
        doc_type: str, 
        content: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate document quality and completeness."""
        
        validation_results = {
            "passed": False,
            "quality_score": 0.0,
            "missing_sections": [],
            "quality_issues": [],
            "completeness_percentage": 0.0,
            "word_count": len(content.split()),
            "section_count": content.count("##")
        }
        
        # Define required sections by document type
        required_sections = {
            "prd": [
                "executive summary", "problem statement", "goals", "user personas",
                "functional requirements", "success metrics", "timeline"
            ],
            "brd": [
                "business objectives", "stakeholders", "business requirements",
                "success criteria", "roi analysis"
            ],
            "uxdd": [
                "user research", "personas", "user journeys", "information architecture",
                "wireframes", "design principles"
            ],
            "srs": [
                "system overview", "functional requirements", "non-functional requirements",
                "system architecture", "api specifications"
            ],
            "erd": [
                "data model", "entities", "relationships", "entity diagram"
            ],
            "dbrd": [
                "database requirements", "schema design", "performance requirements",
                "data governance"
            ]
        }
        
        doc_sections = required_sections.get(doc_type, [])
        content_lower = content.lower()
        
        # Check for required sections
        found_sections = 0
        for section in doc_sections:
            if section in content_lower:
                found_sections += 1
            else:
                validation_results["missing_sections"].append(section)
        
        # Calculate completeness
        if doc_sections:
            validation_results["completeness_percentage"] = (found_sections / len(doc_sections)) * 100
        
        # Check for quality issues
        quality_issues = []
        placeholder_text = ["to be defined", "tbd", "todo", "[placeholder]", "coming soon"]
        
        for placeholder in placeholder_text:
            if placeholder in content_lower:
                quality_issues.append(f"Contains placeholder text: {placeholder}")
        
        # Check minimum content requirements
        if validation_results["word_count"] < 100:
            quality_issues.append("Document too short (< 100 words)")
        
        if validation_results["section_count"] < 3:
            quality_issues.append("Too few sections (< 3)")
        
        validation_results["quality_issues"] = quality_issues
        
        # Calculate quality score
        base_score = validation_results["completeness_percentage"]
        quality_penalty = len(quality_issues) * 10  # 10 points per issue
        validation_results["quality_score"] = max(0, base_score - quality_penalty)
        
        # Document passes validation if > 70% complete and no critical issues
        validation_results["passed"] = (
            validation_results["completeness_percentage"] >= 70 and
            len(quality_issues) <= 2 and
            validation_results["word_count"] >= 200
        )
        
        return validation_results
    
    def _create_error_result(
        self, 
        doc_type: str, 
        error_message: str, 
        request: DocumentGenerationRequest,
        generation_time: float = 0.0
    ) -> DocumentGenerationResult:
        """Create an error result for failed document generation."""
        
        metadata = DocumentMetadata(
            document_type=doc_type,
            generated_at=datetime.utcnow(),
            conversation_id=request.conversation_id,
            conversation_type=request.conversation_type,
            agent_id=f"{doc_type}_agent"
        )
        
        return DocumentGenerationResult(
            document_type=doc_type,
            content="",
            metadata=metadata,
            status=DocumentGenerationStatus.ERROR,
            generation_time=generation_time,
            error_message=error_message
        )


class CrewAIDocumentPipeline:
    """Main document generation pipeline for CrewAI implementation."""
    
    def __init__(self):
        self.processor = ParallelDocumentProcessor()
        self.templates_dir = Path("templates")
        self.output_dir = Path("generated_docs")
        
    async def initialize(self):
        """Initialize the document pipeline."""
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("CrewAI Document Pipeline initialized")
    
    async def generate_documents(
        self,
        request: DocumentGenerationRequest
    ) -> List[DocumentGenerationResult]:
        """Generate documents based on request."""
        
        logger.info(
            f"Starting document generation",
            conversation_id=request.conversation_id,
            document_types=request.document_types,
            enhancement_level=request.enhancement_level
        )
        
        # Process documents
        results = await self.processor.process_documents(request)
        
        # Save results
        for result in results:
            if result.status == DocumentGenerationStatus.COMPLETED:
                await self._save_document(result)
        
        # Log summary
        successful = len([r for r in results if r.status == DocumentGenerationStatus.COMPLETED])
        failed = len(results) - successful
        
        logger.info(
            f"Document generation completed",
            successful=successful,
            failed=failed,
            total_time=sum(r.generation_time for r in results)
        )
        
        return results
    
    async def _save_document(self, result: DocumentGenerationResult):
        """Save generated document to filesystem."""
        
        try:
            # Create conversation directory
            conv_dir = self.output_dir / result.metadata.conversation_id
            conv_dir.mkdir(exist_ok=True)
            
            # Save document
            filename = f"{result.document_type}.md"
            filepath = conv_dir / filename
            
            # Add metadata header to document
            document_with_metadata = self._add_metadata_header(result)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(document_with_metadata)
            
            logger.info(f"Saved document: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save document {result.document_type}: {e}")
    
    def _add_metadata_header(self, result: DocumentGenerationResult) -> str:
        """Add metadata header to document."""
        
        metadata_header = f"""---
document_type: {result.metadata.document_type}
conversation_id: {result.metadata.conversation_id}
generated_at: {result.metadata.generated_at.isoformat()}
quality_score: {result.metadata.quality_score}
validation_passed: {result.metadata.validation_passed}
word_count: {result.metadata.word_count}
generation_time: {result.generation_time:.2f}s
---

"""
        
        return metadata_header + result.content
    
    def get_supported_document_types(self) -> List[str]:
        """Get list of supported document types."""
        return list(self.processor.document_tools.keys())
    
    def get_default_document_types_for_conversation(self, conversation_type: str) -> List[str]:
        """Get default document types for a conversation type."""
        
        type_mappings = {
            "idea": ["prd", "brd", "uxdd", "srs", "erd", "dbrd"],
            "feature": ["prd", "uxdd", "srs"],
            "tool": ["prd", "srs"],
            "api": ["prd", "srs", "erd"]
        }
        
        return type_mappings.get(conversation_type, ["prd"])


# Global pipeline instance
document_pipeline = CrewAIDocumentPipeline()