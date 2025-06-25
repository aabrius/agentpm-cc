"""
Knowledge Synthesizer Tool for CrewAI implementation.
Synthesizes information from multiple RAG search results into coherent insights.
"""

from typing import List, Dict, Any, Optional
from pydantic import Field
from crewai_tools import BaseTool
import structlog
from ..config import get_llm_model
from .rag_search import RAGSearchTool

logger = structlog.get_logger()


class KnowledgeSynthesizerTool(BaseTool):
    """Tool for synthesizing knowledge from multiple sources."""
    
    name: str = Field(default="Knowledge Synthesizer")
    description: str = Field(default="Synthesize information from multiple documents and sources into coherent insights")
    
    def __init__(self):
        super().__init__()
        self.rag_tool = RAGSearchTool()
        
    def _run(
        self,
        query: str,
        synthesis_type: str = "comprehensive",
        conversation_id: Optional[str] = None
    ) -> str:
        """Synthesize knowledge based on query."""
        try:
            # First, search for relevant information
            search_results = self.rag_tool._run(
                query=query,
                conversation_id=conversation_id,
                top_k=10
            )
            
            if "No relevant information found" in search_results:
                return "Unable to synthesize: No relevant information found in knowledge base."
                
            # Get LLM for synthesis
            llm = get_llm_model('orchestrator')
            
            # Build synthesis prompt based on type
            if synthesis_type == "comprehensive":
                prompt = self._build_comprehensive_prompt(query, search_results)
            elif synthesis_type == "comparison":
                prompt = self._build_comparison_prompt(query, search_results)
            elif synthesis_type == "evolution":
                prompt = self._build_evolution_prompt(query, search_results)
            elif synthesis_type == "best_practices":
                prompt = self._build_best_practices_prompt(query, search_results)
            else:
                prompt = self._build_comprehensive_prompt(query, search_results)
                
            # Generate synthesis
            response = llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            logger.error(f"Knowledge synthesis failed: {e}")
            return f"Synthesis failed: {str(e)}"
            
    def _build_comprehensive_prompt(self, query: str, search_results: str) -> str:
        """Build prompt for comprehensive synthesis."""
        return f"""Synthesize the following information to answer this query comprehensively:

Query: {query}

Retrieved Information:
{search_results}

Please provide a comprehensive synthesis that:
1. Identifies common themes and patterns
2. Highlights key insights and findings
3. Notes any contradictions or variations
4. Provides actionable recommendations
5. Summarizes the most important points

Synthesis:"""
    
    def _build_comparison_prompt(self, query: str, search_results: str) -> str:
        """Build prompt for comparison synthesis."""
        return f"""Compare and contrast the different approaches found in the following information:

Query: {query}

Retrieved Information:
{search_results}

Please provide a comparison that:
1. Identifies different approaches or solutions
2. Lists pros and cons of each approach
3. Highlights trade-offs and considerations
4. Recommends best approach for different scenarios
5. Provides decision criteria

Comparison Analysis:"""
    
    def _build_evolution_prompt(self, query: str, search_results: str) -> str:
        """Build prompt for evolution/timeline synthesis."""
        return f"""Analyze how the approach or solution has evolved over time based on:

Query: {query}

Retrieved Information:
{search_results}

Please provide an evolution analysis that:
1. Identifies chronological progression
2. Highlights major changes and improvements
3. Notes lessons learned
4. Shows current best practices
5. Suggests future directions

Evolution Analysis:"""
    
    def _build_best_practices_prompt(self, query: str, search_results: str) -> str:
        """Build prompt for best practices synthesis."""
        return f"""Extract and synthesize best practices from the following information:

Query: {query}

Retrieved Information:
{search_results}

Please provide best practices that include:
1. Proven patterns and approaches
2. Common pitfalls to avoid
3. Success factors and prerequisites
4. Implementation guidelines
5. Metrics for success

Best Practices:"""
    
    def synthesize_project_patterns(self, project_type: str) -> str:
        """Synthesize patterns from similar projects."""
        query = f"Patterns and approaches for {project_type} projects"
        return self._run(query, synthesis_type="best_practices")
        
    def synthesize_technical_approaches(self, problem: str) -> str:
        """Synthesize different technical approaches to a problem."""
        query = f"Technical solutions and architectures for {problem}"
        return self._run(query, synthesis_type="comparison")
        
    def synthesize_design_evolution(self, feature: str) -> str:
        """Synthesize how design approaches have evolved."""
        query = f"Design patterns and UX approaches for {feature}"
        return self._run(query, synthesis_type="evolution")
        
    def synthesize_requirements_patterns(self, domain: str) -> str:
        """Synthesize common requirements patterns for a domain."""
        query = f"Common requirements and features for {domain} applications"
        return self._run(query, synthesis_type="comprehensive")
        
    def synthesize_project_context(self, conversation_id: str) -> str:
        """Synthesize all context from a specific project."""
        query = "Project overview, key decisions, and current status"
        return self._run(
            query,
            synthesis_type="comprehensive",
            conversation_id=conversation_id
        )