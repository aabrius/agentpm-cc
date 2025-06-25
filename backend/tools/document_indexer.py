"""
Document Indexer Tool for CrewAI implementation.
Indexes generated documents into the vector store for future retrieval.
"""

from typing import Dict, Any, List, Optional
from pydantic import Field
from crewai_tools import BaseTool
import asyncio
import uuid
from datetime import datetime
import structlog
from pinecone import Pinecone
import openai
import tiktoken
from ..config import settings

logger = structlog.get_logger()


class DocumentIndexerTool(BaseTool):
    """Tool for indexing documents into the knowledge base."""
    
    name: str = Field(default="Document Indexer")
    description: str = Field(default="Index generated documents into the knowledge base for future retrieval")
    
    def __init__(self):
        super().__init__()
        self.pinecone_client = None
        self.index = None
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
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
                logger.info(f"Connected to Pinecone index for indexing")
            else:
                logger.warning("Pinecone API key not configured")
                
            # Initialize OpenAI
            if settings.openai_api_key:
                openai.api_key = settings.openai_api_key
                
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize indexer tool: {e}")
            
    def _run(self, document: Dict[str, Any]) -> str:
        """Run synchronous indexing (wrapper for async)."""
        return asyncio.run(self._arun(document))
        
    async def _arun(self, document: Dict[str, Any]) -> str:
        """Index a document asynchronously."""
        self._initialize()
        
        if not self.index:
            return "Document indexing is not available (Pinecone not configured)"
            
        try:
            # Validate document structure
            required_fields = ["content", "document_type", "title"]
            for field in required_fields:
                if field not in document:
                    return f"Missing required field: {field}"
                    
            # Generate document ID if not provided
            doc_id = document.get("id", str(uuid.uuid4()))
            
            # Split document into chunks if too large
            chunks = self._chunk_document(document["content"])
            
            # Prepare vectors for indexing
            vectors = []
            for i, chunk in enumerate(chunks):
                # Generate embedding
                embedding = await self._generate_embedding(chunk)
                if not embedding:
                    continue
                    
                # Create vector with metadata
                chunk_id = f"{doc_id}_chunk_{i}" if len(chunks) > 1 else doc_id
                vectors.append({
                    'id': chunk_id,
                    'values': embedding,
                    'metadata': {
                        'content': chunk[:1000],  # Store first 1000 chars
                        'document_type': document["document_type"],
                        'conversation_id': document.get("conversation_id", ""),
                        'created_at': document.get("created_at", datetime.utcnow().isoformat()),
                        'title': document["title"],
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'tokens': len(self.tokenizer.encode(chunk)),
                        'project_name': document.get("project_name", ""),
                        'tags': document.get("tags", [])
                    }
                })
                
            if not vectors:
                return "Failed to generate embeddings for document"
                
            # Determine namespace
            namespace = f"conv_{document.get('conversation_id')}" if document.get('conversation_id') else "default"
            
            # Upsert to Pinecone
            self.index.upsert(vectors=vectors, namespace=namespace)
            
            logger.info(f"Indexed document {doc_id} with {len(vectors)} chunks")
            return f"Successfully indexed document '{document['title']}' with {len(vectors)} chunks"
            
        except Exception as e:
            logger.error(f"Document indexing failed: {e}")
            return f"Indexing failed: {str(e)}"
            
    def _chunk_document(self, content: str, max_tokens: int = 1000) -> List[str]:
        """Split document into chunks based on token count."""
        # Encode content
        tokens = self.tokenizer.encode(content)
        
        if len(tokens) <= max_tokens:
            return [content]
            
        # Split into chunks
        chunks = []
        current_chunk_tokens = []
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        current_paragraph_group = []
        
        for paragraph in paragraphs:
            para_tokens = self.tokenizer.encode(paragraph)
            
            # If adding this paragraph exceeds limit, save current chunk
            if current_chunk_tokens and len(current_chunk_tokens) + len(para_tokens) > max_tokens:
                # Decode and save current chunk
                chunk_text = '\n\n'.join(current_paragraph_group)
                chunks.append(chunk_text)
                current_chunk_tokens = []
                current_paragraph_group = []
                
            current_chunk_tokens.extend(para_tokens)
            current_paragraph_group.append(paragraph)
            
        # Add remaining content
        if current_paragraph_group:
            chunk_text = '\n\n'.join(current_paragraph_group)
            chunks.append(chunk_text)
            
        return chunks
        
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
            
    def index_prd(self, prd_content: str, title: str, conversation_id: str) -> str:
        """Index a Product Requirements Document."""
        return self._run({
            "content": prd_content,
            "document_type": "prd",
            "title": title,
            "conversation_id": conversation_id
        })
        
    def index_technical_spec(self, spec_content: str, title: str, conversation_id: str) -> str:
        """Index a Technical Specification."""
        return self._run({
            "content": spec_content,
            "document_type": "technical_spec",
            "title": title,
            "conversation_id": conversation_id
        })
        
    def index_design_doc(self, design_content: str, title: str, conversation_id: str) -> str:
        """Index a Design Document."""
        return self._run({
            "content": design_content,
            "document_type": "uxdd",
            "title": title,
            "conversation_id": conversation_id
        })
        
    def index_conversation_summary(self, summary: str, conversation_id: str, key_decisions: List[str]) -> str:
        """Index a conversation summary with key decisions."""
        content = f"{summary}\n\nKey Decisions:\n" + "\n".join(f"- {decision}" for decision in key_decisions)
        
        return self._run({
            "content": content,
            "document_type": "conversation_summary",
            "title": "Conversation Summary",
            "conversation_id": conversation_id,
            "tags": ["summary", "decisions"]
        })
        
    def batch_index_documents(self, documents: List[Dict[str, Any]]) -> str:
        """Index multiple documents in batch."""
        results = []
        for doc in documents:
            result = self._run(doc)
            results.append(f"- {doc.get('title', 'Untitled')}: {result}")
            
        return "Batch indexing results:\n" + "\n".join(results)