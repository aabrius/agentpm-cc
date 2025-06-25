"""
RAG Search Tool for CrewAI implementation.
Provides semantic search capabilities for agents to access historical knowledge.
"""

from typing import List, Dict, Any, Optional
from pydantic import Field
from crewai_tools import BaseTool
import asyncio
import os
import structlog
from pinecone import Pinecone
import openai
from ..config import settings

logger = structlog.get_logger()


class RAGSearchTool(BaseTool):
    """Tool for searching and retrieving information from the knowledge base."""
    
    name: str = Field(default="RAG Knowledge Search")
    description: str = Field(default="Search historical project knowledge, documents, and conversations for relevant information")
    
    def __init__(self):
        super().__init__()
        self.pinecone_client = None
        self.index = None
        self.openai_client = None
        self._initialized = False
        
    def _initialize(self):
        """Initialize connections to Pinecone and OpenAI."""
        if self._initialized:
            return
            
        try:
            # Initialize Pinecone
            if settings.pinecone_api_key:
                self.pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
                self.index = self.pinecone_client.Index(settings.pinecone_index_name)
                logger.info(f"Connected to Pinecone index: {settings.pinecone_index_name}")
            else:
                logger.warning("Pinecone API key not configured")
                
            # Initialize OpenAI
            if settings.openai_api_key:
                openai.api_key = settings.openai_api_key
                logger.info("OpenAI configured for embeddings")
            else:
                logger.warning("OpenAI API key not configured")
                
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG tool: {e}")
            
    def _run(self, query: str, **kwargs) -> str:
        """Run synchronous search (wrapper for async)."""
        return asyncio.run(self._arun(query, **kwargs))
        
    async def _arun(
        self, 
        query: str,
        conversation_id: Optional[str] = None,
        document_types: Optional[List[str]] = None,
        top_k: int = 5
    ) -> str:
        """Search for relevant information asynchronously."""
        self._initialize()
        
        if not self.index:
            return "RAG search is not available (Pinecone not configured)"
            
        try:
            # Generate embedding for query
            embedding = await self._generate_embedding(query)
            if not embedding:
                return "Could not generate embedding for search query"
                
            # Build filter
            filter_dict = {}
            if conversation_id:
                filter_dict['conversation_id'] = conversation_id
            if document_types:
                filter_dict['document_type'] = {"$in": document_types}
                
            # Determine namespace
            namespace = f"conv_{conversation_id}" if conversation_id else "default"
            
            # Search in Pinecone
            results = self.index.query(
                vector=embedding,
                top_k=top_k,
                namespace=namespace,
                filter=filter_dict if filter_dict else None,
                include_metadata=True
            )
            
            # Format results
            if not results.matches:
                return "No relevant information found in the knowledge base."
                
            formatted_results = []
            for i, match in enumerate(results.matches, 1):
                metadata = match.metadata
                formatted_results.append(
                    f"{i}. [{metadata.get('document_type', 'Unknown')}] "
                    f"{metadata.get('title', 'Untitled')} "
                    f"(Score: {match.score:.2f})\n"
                    f"   {metadata.get('content', '')[:200]}..."
                )
                
            return "Found relevant information:\n\n" + "\n\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"RAG search failed: {e}")
            return f"Search failed: {str(e)}"
            
    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding using OpenAI."""
        try:
            if not settings.openai_api_key:
                return None
                
            response = await openai.Embedding.acreate(
                input=text,
                model="text-embedding-ada-002"
            )
            
            return response['data'][0]['embedding']
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
            
    def search_similar_projects(self, project_description: str) -> str:
        """Search for similar past projects."""
        return self._run(
            f"Projects similar to: {project_description}",
            document_types=["prd", "brd"]
        )
        
    def search_technical_solutions(self, problem: str) -> str:
        """Search for technical solutions to specific problems."""
        return self._run(
            f"Technical solutions for: {problem}",
            document_types=["srs", "technical_spec", "architecture"]
        )
        
    def search_design_patterns(self, context: str) -> str:
        """Search for relevant design patterns and UX solutions."""
        return self._run(
            f"Design patterns and UX solutions for: {context}",
            document_types=["uxdd", "design_system"]
        )
        
    def search_database_schemas(self, entities: str) -> str:
        """Search for similar database schemas and data models."""
        return self._run(
            f"Database schemas for entities: {entities}",
            document_types=["erd", "dbrd", "data_model"]
        )
        
    def get_project_context(self, conversation_id: str) -> str:
        """Get all context from a specific conversation/project."""
        return self._run(
            "Project overview and key decisions",
            conversation_id=conversation_id,
            top_k=10
        )