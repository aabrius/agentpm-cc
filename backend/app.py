"""
FastAPI application for AgentPM 2.0 CrewAI implementation.
Provides WebSocket and REST API endpoints.
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import uuid
import structlog

from main import AgentPMSystem
from core.document_pipeline import document_pipeline, DocumentGenerationRequest
from core.state_manager import state_manager
from websocket_manager import CrewAIWebSocketHandler
from config import setup_logging
from api.analytics import analytics_router

# Setup logging
setup_logging()
logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="AgentPM 2.0 - CrewAI Implementation",
    description="Multi-Agent Product Management System with CrewAI",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the AgentPM system
agent_system = AgentPMSystem()

# Include analytics router
app.include_router(analytics_router)


# Request/Response models
class ProcessRequestModel(BaseModel):
    user_input: str
    conversation_id: Optional[str] = None
    project_type: Optional[str] = None
    selected_model: Optional[str] = None


class ContinueConversationModel(BaseModel):
    user_response: str
    conversation_id: str


class CheckpointRequestModel(BaseModel):
    conversation_id: str


class RestoreRequestModel(BaseModel):
    conversation_id: str
    checkpoint_time: Optional[str] = None


class ProcessResponseModel(BaseModel):
    status: str
    project_type: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    conversation_id: Optional[str] = None
    error: Optional[str] = None
    phase: Optional[str] = None
    flow_type: Optional[str] = None


class DocumentGenerationRequestModel(BaseModel):
    conversation_id: str
    document_types: List[str]
    conversation_type: str = "feature"
    context: Optional[Dict[str, Any]] = None
    qa_pairs: Optional[Dict[str, Dict[str, str]]] = None
    enhancement_level: str = "standard"
    parallel_generation: bool = True


class DocumentGenerationResponseModel(BaseModel):
    status: str
    documents: List[Dict[str, Any]]
    conversation_id: str
    generation_time: float
    success_count: int
    error_count: int


# REST API Endpoints
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "AgentPM 2.0 - CrewAI Implementation",
        "status": "running",
        "version": "2.0.0"
    }


@app.post("/process", response_model=ProcessResponseModel)
async def process_request(request: ProcessRequestModel):
    """Process a user request through the multi-agent system."""
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        logger.info("Processing request via API", 
                   conversation_id=conversation_id,
                   project_type=request.project_type,
                   selected_model=request.selected_model)
        
        # Set model for conversation if provided
        if request.selected_model:
            from core.model_context import model_context
            model_context.set_model_for_conversation(conversation_id, request.selected_model)
        
        # Process the request
        result = await agent_system.process_request(
            user_input=request.user_input,
            conversation_id=conversation_id,
            project_type=request.project_type
        )
        
        return ProcessResponseModel(**result)
        
    except Exception as e:
        logger.error("API request processing failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-documents", response_model=DocumentGenerationResponseModel)
async def generate_documents(request: DocumentGenerationRequestModel):
    """Generate documents using the new document pipeline."""
    try:
        logger.info("Generating documents via API", 
                   conversation_id=request.conversation_id,
                   document_types=request.document_types)
        
        # Create document generation request
        generation_request = DocumentGenerationRequest(
            conversation_id=request.conversation_id,
            document_types=request.document_types,
            conversation_type=request.conversation_type,
            context=request.context or {},
            qa_pairs=request.qa_pairs or {},
            enhancement_level=request.enhancement_level,
            parallel_generation=request.parallel_generation
        )
        
        # Generate documents
        import time
        start_time = time.time()
        results = await document_pipeline.generate_documents(generation_request)
        total_time = time.time() - start_time
        
        # Process results
        documents = []
        success_count = 0
        error_count = 0
        
        for result in results:
            doc_info = {
                "document_type": result.document_type,
                "status": result.status.value,
                "generation_time": result.generation_time,
                "quality_score": result.metadata.quality_score,
                "word_count": result.metadata.word_count,
                "validation_passed": result.metadata.validation_passed
            }
            
            if result.error_message:
                doc_info["error"] = result.error_message
                error_count += 1
            else:
                success_count += 1
            
            documents.append(doc_info)
        
        return DocumentGenerationResponseModel(
            status="completed",
            documents=documents,
            conversation_id=request.conversation_id,
            generation_time=total_time,
            success_count=success_count,
            error_count=error_count
        )
        
    except Exception as e:
        logger.error("Document generation failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/document-types")
async def get_supported_document_types():
    """Get list of supported document types."""
    return {
        "supported_types": document_pipeline.get_supported_document_types(),
        "type_mappings": {
            "idea": document_pipeline.get_default_document_types_for_conversation("idea"),
            "feature": document_pipeline.get_default_document_types_for_conversation("feature"), 
            "tool": document_pipeline.get_default_document_types_for_conversation("tool"),
            "api": document_pipeline.get_default_document_types_for_conversation("api")
        }
    }


@app.get("/conversations/{conversation_id}")
async def get_conversation_status(conversation_id: str):
    """Get status of a specific conversation from state manager."""
    try:
        # Try to get from conversation flow first
        status = agent_system.get_conversation_status(conversation_id)
        
        if "error" not in status:
            return status
        
        # Try to get from persistent state
        await state_manager.initialize()
        persistent_state = await state_manager.get_conversation_state(conversation_id)
        
        if persistent_state:
            return {
                "conversation_id": conversation_id,
                "conversation_type": persistent_state.conversation_type,
                "status": persistent_state.status.value,
                "phase": persistent_state.phase.value,
                "agents_consulted": persistent_state.agents_consulted,
                "documents_generated": persistent_state.documents_generated,
                "message_count": len(persistent_state.messages),
                "created_at": persistent_state.created_at.isoformat(),
                "updated_at": persistent_state.updated_at.isoformat(),
                "source": "persistent_storage"
            }
        
        raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        
    except Exception as e:
        logger.error(f"Failed to get conversation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conversations/{conversation_id}/continue")
async def continue_conversation(conversation_id: str, request: ContinueConversationModel):
    """Continue an existing conversation."""
    try:
        result = await agent_system.continue_conversation(
            conversation_id=conversation_id,
            user_response=request.user_response
        )
        return result
        
    except Exception as e:
        logger.error(f"Failed to continue conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conversations/{conversation_id}/checkpoint")
async def create_checkpoint(conversation_id: str):
    """Create manual checkpoint for conversation."""
    try:
        await state_manager.initialize()
        checkpoint = await state_manager.create_checkpoint(conversation_id)
        return {
            "status": "success",
            "checkpoint": checkpoint,
            "message": f"Checkpoint created for conversation {conversation_id}"
        }
        
    except Exception as e:
        logger.error(f"Failed to create checkpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conversations/{conversation_id}/restore")
async def restore_conversation(conversation_id: str, request: RestoreRequestModel):
    """Restore conversation from checkpoint."""
    try:
        success = await agent_system.conversation_flow.restore_from_checkpoint(
            conversation_id=conversation_id,
            checkpoint_time=request.checkpoint_time
        )
        
        if success:
            return {
                "status": "success",
                "message": f"Conversation {conversation_id} restored successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Checkpoint not found or restoration failed")
            
    except Exception as e:
        logger.error(f"Failed to restore conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Detailed health check with system status."""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "services": {
            "crew_ai": "operational",
            "websocket": "operational", 
            "document_generation": "operational",
            "rag_system": "operational",
            "state_management": "operational",
            "conversation_flow": "operational"
        }
    }


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, conversation_id: Optional[str] = None):
    """WebSocket endpoint for real-time communication."""
    await CrewAIWebSocketHandler.websocket_endpoint(websocket, conversation_id)


@app.websocket("/ws/{conversation_id}")
async def websocket_with_conversation(websocket: WebSocket, conversation_id: str):
    """WebSocket endpoint with conversation ID in path."""
    await CrewAIWebSocketHandler.websocket_endpoint(websocket, conversation_id)


# Combined endpoint that processes request and streams via WebSocket
@app.post("/process-stream")
async def process_with_stream(request: ProcessRequestModel):
    """Process request and return conversation ID for WebSocket streaming."""
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        logger.info("Starting streaming request", 
                   conversation_id=conversation_id,
                   selected_model=request.selected_model)
        
        # Set model for conversation if provided
        if request.selected_model:
            from core.model_context import model_context
            model_context.set_model_for_conversation(conversation_id, request.selected_model)
        
        # Start processing in background task
        asyncio.create_task(
            agent_system.process_request(
                user_input=request.user_input,
                conversation_id=conversation_id,
                project_type=request.project_type
            )
        )
        
        return {
            "status": "started",
            "conversation_id": conversation_id,
            "websocket_url": f"/ws/{conversation_id}",
            "message": "Connect to WebSocket for real-time updates",
            "selected_model": request.selected_model
        }
        
    except Exception as e:
        logger.error("Stream request failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return {
        "error": "Not Found",
        "message": "The requested resource was not found",
        "status_code": 404
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    logger.error("Internal server error", error=str(exc), exc_info=True)
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "status_code": 500
    }


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting AgentPM 2.0 CrewAI service")
    
    # Initialize any required services here
    # e.g., database connections, external services, etc.
    
    logger.info("AgentPM 2.0 CrewAI service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down AgentPM 2.0 CrewAI service")
    
    # Cleanup any resources here
    # e.g., close database connections, cancel background tasks, etc.
    
    logger.info("AgentPM 2.0 CrewAI service shut down successfully")


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )