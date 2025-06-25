"""
Main execution file for AgentPM 2.0 CrewAI implementation.
Demonstrates how to use the multi-agent system with intelligent conversation flow.
"""

import asyncio
from typing import Dict, Any, Optional
import structlog
from crewai import Task
from crews.project_crew import ProjectCrew
from agents import OrchestratorAgent, ProductManagerAgent
from config import setup_logging
from websocket_manager import websocket_bridge
from conversation_flow import conversation_flow
from task_delegation import task_delegation_manager

# Setup logging
setup_logging()
logger = structlog.get_logger()


class AgentPMSystem:
    """Main system for running AgentPM with CrewAI and intelligent conversation flow."""
    
    def __init__(self):
        self.project_crew = ProjectCrew()
        self.conversation_flow = conversation_flow
        self.task_delegation = task_delegation_manager
        
    async def process_request(
        self,
        user_input: str,
        conversation_id: Optional[str] = None,
        project_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a user request through the intelligent conversation flow system."""
        
        logger.info(f"Processing request for conversation: {conversation_id}")
        
        # Register conversation for WebSocket updates
        if conversation_id:
            websocket_bridge.register_conversation(conversation_id)
            await websocket_bridge.send_crew_status(
                conversation_id, "starting", 0.0, {"message": "Initializing intelligent conversation flow"}
            )
        
        try:
            # Start conversation flow (replaces simple crew execution)
            result = await self.conversation_flow.start_conversation(
                conversation_id=conversation_id or f"conv_{asyncio.get_event_loop().time()}",
                user_input=user_input,
                conversation_type=project_type
            )
            
            # Index generated documents
            if conversation_id and result.get("results"):
                await websocket_bridge.send_crew_status(
                    conversation_id, "indexing", 0.9, {"message": "Indexing generated documents"}
                )
                await self._index_results(result["results"], conversation_id)
            
            if conversation_id:
                await websocket_bridge.send_crew_status(
                    conversation_id, "completed", 1.0, {"message": "Conversation flow completed successfully"}
                )
            
            return {
                "status": "success",
                "conversation_id": result.get("conversation_id", conversation_id),
                "results": result.get("results", {}),
                "phase": result.get("next_phase", "completed"),
                "flow_type": "intelligent_conversation"
            }
            
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            
            if conversation_id:
                await websocket_bridge.send_error(
                    conversation_id, "execution_error", str(e), {"step": "conversation_flow"}
                )
            
            return {
                "status": "error",
                "error": str(e),
                "conversation_id": conversation_id
            }
    
    async def continue_conversation(
        self,
        conversation_id: str,
        user_response: str
    ) -> Dict[str, Any]:
        """Continue an existing conversation with user response."""
        
        logger.info(f"Continuing conversation: {conversation_id}")
        
        try:
            # Register conversation for WebSocket updates
            websocket_bridge.register_conversation(conversation_id)
            await websocket_bridge.send_crew_status(
                conversation_id, "continuing", 0.1, {"message": "Processing user response"}
            )
            
            # Continue conversation flow
            result = await self.conversation_flow.continue_conversation(
                conversation_id=conversation_id,
                user_response=user_response
            )
            
            # Index any new documents
            if result.get("results"):
                await websocket_bridge.send_crew_status(
                    conversation_id, "indexing", 0.9, {"message": "Indexing new documents"}
                )
                await self._index_results(result["results"], conversation_id)
            
            await websocket_bridge.send_crew_status(
                conversation_id, "completed", 1.0, {"message": "Conversation continued successfully"}
            )
            
            return {
                "status": "success",
                "conversation_id": conversation_id,
                "results": result.get("results", {}),
                "phase": result.get("next_phase", "completed"),
                "flow_type": "conversation_continuation"
            }
            
        except Exception as e:
            logger.error(f"Error continuing conversation {conversation_id}: {e}", exc_info=True)
            
            await websocket_bridge.send_error(
                conversation_id, "continuation_error", str(e), {"step": "conversation_continuation"}
            )
            
            return {
                "status": "error",
                "error": str(e),
                "conversation_id": conversation_id
            }
    
    def get_conversation_status(self, conversation_id: str) -> Dict[str, Any]:
        """Get current status of a conversation."""
        return self.conversation_flow.get_conversation_status(conversation_id)
            
    def _create_tasks_for_project_type(
        self,
        project_type: str,
        user_input: str,
        conversation_id: Optional[str]
    ) -> list:
        """Create tasks based on project type."""
        tasks = []
        
        # Always start with orchestration
        orchestrator = self.project_crew.agents['orchestrator']
        tasks.append(Task(
            description=f"""Analyze and coordinate documentation for this request:
            {user_input}
            
            Conversation ID: {conversation_id or 'new'}
            Project Type: {project_type}
            
            Search for similar past projects and synthesize best practices.""",
            expected_output="Project analysis and coordination plan",
            agent=orchestrator
        ))
        
        # Add tasks based on project type
        if project_type in ['full_product', 'feature', 'api']:
            # Product requirements
            pm_agent = self.project_crew.agents['product_manager']
            tasks.append(Task(
                description=ProductManagerAgent.create_prd_task({"user_input": user_input})["description"],
                expected_output=ProductManagerAgent.create_prd_task({"user_input": user_input})["expected_output"],
                agent=pm_agent
            ))
            
        if project_type in ['full_product', 'feature']:
            # Design requirements
            designer = self.project_crew.agents['designer']
            tasks.append(Task(
                description=f"Create UX design documentation for: {user_input}",
                expected_output="Complete UXDD with wireframes and design principles",
                agent=designer
            ))
            
        if project_type in ['full_product', 'database']:
            # Database design
            db_agent = self.project_crew.agents['database']
            tasks.append(Task(
                description=f"Design database schema and create ERD for: {user_input}",
                expected_output="Complete ERD and DBRD documentation",
                agent=db_agent
            ))
            
        # Always end with review
        reviewer = self.project_crew.agents['review']
        tasks.append(Task(
            description="Review all generated documentation for quality and consistency",
            expected_output="Quality review report with recommendations",
            agent=reviewer
        ))
        
        return tasks
        
    def _extract_project_type(self, analysis_result: str) -> str:
        """Extract project type from analysis result."""
        # Simple extraction logic - in production would be more sophisticated
        result_lower = analysis_result.lower()
        
        if "full product" in result_lower or "complete application" in result_lower:
            return "full_product"
        elif "api" in result_lower or "backend" in result_lower:
            return "api"
        elif "database" in result_lower or "data model" in result_lower:
            return "database"
        elif "mvp" in result_lower or "prototype" in result_lower:
            return "mvp"
        else:
            return "feature"
            
    async def _run_task_async(self, task: Task, conversation_id: Optional[str] = None, agent_name: Optional[str] = None) -> str:
        """Run a single task asynchronously."""
        if conversation_id and agent_name:
            await websocket_bridge.send_agent_status(
                conversation_id, agent_name, "executing", {"task": task.description[:100]}
            )
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, task.execute)
        
        if conversation_id and agent_name:
            await websocket_bridge.send_agent_response(
                conversation_id, agent_name, result, is_partial=False
            )
            await websocket_bridge.send_agent_status(
                conversation_id, agent_name, "completed", {"result_length": len(result)}
            )
        
        return result
        
    async def _run_crew_async(self, crew, tasks: list, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Run crew asynchronously."""
        if conversation_id:
            await websocket_bridge.send_crew_status(
                conversation_id, "running", 0.5, {"tasks_count": len(tasks)}
            )
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, crew.kickoff, {"tasks": tasks})
        
        if conversation_id:
            await websocket_bridge.send_crew_status(
                conversation_id, "crew_completed", 0.8, {"result_keys": list(result.keys()) if isinstance(result, dict) else ["result"]}
            )
        
        return result
        
    async def _index_results(self, results: Dict[str, Any], conversation_id: str):
        """Index generated documents for future retrieval."""
        try:
            from tools.document_indexer import DocumentIndexerTool
            indexer = DocumentIndexerTool()
            
            # Index each generated document
            for doc_type, content in results.items():
                if isinstance(content, str) and len(content) > 100:
                    await indexer._arun({
                        "content": content,
                        "document_type": doc_type,
                        "title": f"{doc_type.upper()} for conversation {conversation_id}",
                        "conversation_id": conversation_id
                    })
                    
            logger.info(f"Indexed {len(results)} documents for conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Failed to index results: {e}")


async def main():
    """Example usage of the AgentPM system."""
    system = AgentPMSystem()
    
    # Example request
    user_request = """
    I want to build a task management application for software teams. 
    It should support project creation, task assignment, time tracking, 
    and integration with GitHub. The target users are development teams 
    of 5-50 people. We need both web and mobile apps.
    """
    
    # Process the request
    result = await system.process_request(
        user_input=user_request,
        conversation_id="demo-123",
        project_type=None  # Let system detect
    )
    
    print(f"Processing completed with status: {result['status']}")
    print(f"Detected project type: {result.get('project_type')}")
    

if __name__ == "__main__":
    asyncio.run(main())