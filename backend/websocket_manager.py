"""
WebSocket Manager for CrewAI implementation.
Handles real-time communication with frontend during crew execution.
"""

import asyncio
import json
import uuid
from typing import Dict, Set, Optional, Any, Callable
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()


class WebSocketMessage(BaseModel):
    """WebSocket message structure."""
    type: str
    data: Dict[str, Any]
    conversation_id: Optional[str] = None
    timestamp: Optional[str] = None


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""
    
    def __init__(self):
        # Active WebSocket connections
        self.active_connections: Set[WebSocket] = set()
        # Map conversation_id to websockets
        self.conversation_connections: Dict[str, Set[WebSocket]] = {}
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, conversation_id: Optional[str] = None):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        # Store connection metadata
        self.connection_metadata[websocket] = {
            "conversation_id": conversation_id,
            "connected_at": asyncio.get_event_loop().time(),
            "connection_id": str(uuid.uuid4())
        }
        
        # Associate with conversation if provided
        if conversation_id:
            if conversation_id not in self.conversation_connections:
                self.conversation_connections[conversation_id] = set()
            self.conversation_connections[conversation_id].add(websocket)
        
        logger.info("WebSocket connected", 
                   conversation_id=conversation_id,
                   total_connections=len(self.active_connections))
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
            # Get metadata before removing
            metadata = self.connection_metadata.get(websocket, {})
            conversation_id = metadata.get("conversation_id")
            
            # Remove from conversation mapping
            if conversation_id and conversation_id in self.conversation_connections:
                self.conversation_connections[conversation_id].discard(websocket)
                if not self.conversation_connections[conversation_id]:
                    del self.conversation_connections[conversation_id]
            
            # Remove metadata
            self.connection_metadata.pop(websocket, None)
            
            logger.info("WebSocket disconnected",
                       conversation_id=conversation_id,
                       total_connections=len(self.active_connections))
    
    async def send_personal_message(self, message: WebSocketMessage, websocket: WebSocket):
        """Send message to specific WebSocket connection."""
        try:
            await websocket.send_text(message.model_dump_json())
        except Exception as e:
            logger.error("Failed to send personal message", error=str(e))
            self.disconnect(websocket)
    
    async def broadcast_to_conversation(self, message: WebSocketMessage, conversation_id: str):
        """Send message to all connections for a specific conversation."""
        if conversation_id not in self.conversation_connections:
            logger.warning("No connections for conversation", conversation_id=conversation_id)
            return
        
        connections = self.conversation_connections[conversation_id].copy()
        disconnect_list = []
        
        for connection in connections:
            try:
                await connection.send_text(message.model_dump_json())
            except Exception as e:
                logger.error("Failed to send message to connection", error=str(e))
                disconnect_list.append(connection)
        
        # Clean up failed connections
        for connection in disconnect_list:
            self.disconnect(connection)
    
    async def broadcast_to_all(self, message: WebSocketMessage):
        """Send message to all active connections."""
        connections = self.active_connections.copy()
        disconnect_list = []
        
        for connection in connections:
            try:
                await connection.send_text(message.model_dump_json())
            except Exception as e:
                logger.error("Failed to broadcast message", error=str(e))
                disconnect_list.append(connection)
        
        # Clean up failed connections
        for connection in disconnect_list:
            self.disconnect(connection)
    
    def get_connection_count(self, conversation_id: Optional[str] = None) -> int:
        """Get number of active connections."""
        if conversation_id:
            return len(self.conversation_connections.get(conversation_id, set()))
        return len(self.active_connections)


class CrewAIWebSocketBridge:
    """Bridge between CrewAI execution and WebSocket communication."""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.execution_callbacks: Dict[str, Callable] = {}
        
    def register_conversation(self, conversation_id: str, callback: Optional[Callable] = None):
        """Register a conversation for WebSocket updates."""
        if callback:
            self.execution_callbacks[conversation_id] = callback
        
        logger.info("Registered conversation for WebSocket updates", 
                   conversation_id=conversation_id)
    
    async def send_agent_status(self, conversation_id: str, agent_name: str, status: str, details: Optional[Dict] = None):
        """Send agent status update."""
        message = WebSocketMessage(
            type="agent_status",
            data={
                "agent": agent_name,
                "status": status,
                "details": details or {},
                "timestamp": asyncio.get_event_loop().time()
            },
            conversation_id=conversation_id
        )
        
        await self.connection_manager.broadcast_to_conversation(message, conversation_id)
        logger.debug("Sent agent status update", 
                    conversation_id=conversation_id, 
                    agent=agent_name, 
                    status=status)
    
    async def send_agent_response(self, conversation_id: str, agent_name: str, content: str, is_partial: bool = False):
        """Send agent response content."""
        message = WebSocketMessage(
            type="agent_response",
            data={
                "agent": agent_name,
                "content": content,
                "is_partial": is_partial,
                "timestamp": asyncio.get_event_loop().time()
            },
            conversation_id=conversation_id
        )
        
        await self.connection_manager.broadcast_to_conversation(message, conversation_id)
    
    async def send_crew_status(self, conversation_id: str, status: str, progress: Optional[float] = None, details: Optional[Dict] = None):
        """Send crew execution status."""
        message = WebSocketMessage(
            type="crew_status",
            data={
                "status": status,
                "progress": progress,
                "details": details or {},
                "timestamp": asyncio.get_event_loop().time()
            },
            conversation_id=conversation_id
        )
        
        await self.connection_manager.broadcast_to_conversation(message, conversation_id)
        logger.debug("Sent crew status update", 
                    conversation_id=conversation_id, 
                    status=status, 
                    progress=progress)
    
    async def send_document_update(self, conversation_id: str, document_type: str, document_id: str, status: str):
        """Send document generation update."""
        message = WebSocketMessage(
            type="document_update",
            data={
                "document_type": document_type,
                "document_id": document_id,
                "status": status,
                "timestamp": asyncio.get_event_loop().time()
            },
            conversation_id=conversation_id
        )
        
        await self.connection_manager.broadcast_to_conversation(message, conversation_id)
    
    async def send_error(self, conversation_id: str, error_type: str, message: str, details: Optional[Dict] = None):
        """Send error notification."""
        error_message = WebSocketMessage(
            type="error",
            data={
                "error_type": error_type,
                "message": message,
                "details": details or {},
                "timestamp": asyncio.get_event_loop().time()
            },
            conversation_id=conversation_id
        )
        
        await self.connection_manager.broadcast_to_conversation(error_message, conversation_id)
        logger.error("Sent error via WebSocket", 
                    conversation_id=conversation_id, 
                    error_type=error_type, 
                    message=message)
    
    async def send_task_progress(self, conversation_id: str, task_name: str, progress: float, details: Optional[Dict] = None):
        """Send individual task progress."""
        message = WebSocketMessage(
            type="task_progress",
            data={
                "task_name": task_name,
                "progress": progress,
                "details": details or {},
                "timestamp": asyncio.get_event_loop().time()
            },
            conversation_id=conversation_id
        )
        
        await self.connection_manager.broadcast_to_conversation(message, conversation_id)


# Global connection manager instance
connection_manager = ConnectionManager()
websocket_bridge = CrewAIWebSocketBridge(connection_manager)


class CrewAIWebSocketHandler:
    """Handles WebSocket endpoint for CrewAI system."""
    
    @staticmethod
    async def websocket_endpoint(websocket: WebSocket, conversation_id: Optional[str] = None):
        """Main WebSocket endpoint handler."""
        await connection_manager.connect(websocket, conversation_id)
        
        try:
            # Send initial connection confirmation
            welcome_message = WebSocketMessage(
                type="connection_established",
                data={
                    "conversation_id": conversation_id,
                    "timestamp": asyncio.get_event_loop().time(),
                    "message": "Connected to AgentPM CrewAI"
                },
                conversation_id=conversation_id
            )
            await connection_manager.send_personal_message(welcome_message, websocket)
            
            # Keep connection alive and handle incoming messages
            while True:
                try:
                    # Wait for messages from client (for potential bidirectional communication)
                    data = await websocket.receive_text()
                    
                    # Parse and handle client messages if needed
                    try:
                        client_message = json.loads(data)
                        await CrewAIWebSocketHandler._handle_client_message(
                            client_message, websocket, conversation_id
                        )
                    except json.JSONDecodeError:
                        logger.warning("Received invalid JSON from client", data=data)
                
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error("Error in WebSocket handler", error=str(e))
                    break
        
        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error("WebSocket connection error", error=str(e))
        finally:
            connection_manager.disconnect(websocket)
    
    @staticmethod
    async def _handle_client_message(message: Dict[str, Any], websocket: WebSocket, conversation_id: Optional[str]):
        """Handle messages received from client."""
        message_type = message.get("type")
        
        if message_type == "ping":
            # Respond to ping with pong
            pong_message = WebSocketMessage(
                type="pong",
                data={"timestamp": asyncio.get_event_loop().time()},
                conversation_id=conversation_id
            )
            await connection_manager.send_personal_message(pong_message, websocket)
        
        elif message_type == "request_status":
            # Client requesting current status
            status_message = WebSocketMessage(
                type="status_response",
                data={
                    "active_connections": connection_manager.get_connection_count(),
                    "conversation_connections": connection_manager.get_connection_count(conversation_id),
                    "timestamp": asyncio.get_event_loop().time()
                },
                conversation_id=conversation_id
            )
            await connection_manager.send_personal_message(status_message, websocket)
        
        elif message_type == "start_conversation":
            # Handle start conversation with model selection
            from conversation_flow import conversation_flow
            from core.model_context import model_context
            
            # Extract model selection
            selected_model = message.get("selected_model")
            conversation_type = message.get("conversation_type", "feature")
            user_input = message.get("message", "")
            
            # Set model for this conversation if provided
            if selected_model and conversation_id:
                model_context.set_model_for_conversation(conversation_id, selected_model)
                logger.info("Model set for conversation", 
                           conversation_id=conversation_id,
                           model=selected_model)
            
            # Start the conversation flow
            try:
                result = await conversation_flow.start_conversation(
                    conversation_id=conversation_id or str(uuid.uuid4()),
                    user_input=user_input,
                    conversation_type=conversation_type
                )
                
                # Send initial response
                response_message = WebSocketMessage(
                    type="conversation_started",
                    data={
                        "status": "started",
                        "conversation_id": conversation_id,
                        "model": selected_model,
                        "result": result
                    },
                    conversation_id=conversation_id
                )
                await connection_manager.send_personal_message(response_message, websocket)
                
            except Exception as e:
                logger.error("Failed to start conversation", error=str(e))
                error_message = WebSocketMessage(
                    type="error",
                    data={
                        "error_type": "conversation_start_failed",
                        "message": str(e)
                    },
                    conversation_id=conversation_id
                )
                await connection_manager.send_personal_message(error_message, websocket)
        
        else:
            logger.debug("Received unknown message type", message_type=message_type)


# Export for use in main application
__all__ = [
    "ConnectionManager",
    "CrewAIWebSocketBridge", 
    "CrewAIWebSocketHandler",
    "WebSocketMessage",
    "connection_manager",
    "websocket_bridge"
]