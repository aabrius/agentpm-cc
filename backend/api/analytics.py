"""
Analytics API endpoints for CrewAI implementation.
Provides comprehensive observability and metrics through REST API.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import structlog

from core.analytics import analytics_engine
from core.langfuse_config import langfuse_manager

logger = structlog.get_logger()

# Create analytics router
analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])


# Request/Response models
class DateRangeQuery(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class AnalyticsResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    timestamp: datetime


class HealthResponse(BaseModel):
    status: str
    health_score: float
    error_rate: float
    active_conversations: int
    system_status: str


class ConversationAnalyticsResponse(BaseModel):
    conversation_id: str
    metrics: Dict[str, Any]
    flow_analysis: Dict[str, Any]
    recommendations: List[str]


class AgentPerformanceResponse(BaseModel):
    agent_id: str
    performance_metrics: Dict[str, Any]
    efficiency_score: float
    recommendations: List[str]


class SystemOverviewResponse(BaseModel):
    system_metrics: Dict[str, Any]
    health_status: Dict[str, Any]
    performance_trends: Dict[str, Any]
    capacity_analysis: Dict[str, Any]


# Health and system status endpoints
@analytics_router.get("/health", response_model=HealthResponse)
async def get_system_health():
    """Get system health metrics and status."""
    try:
        health_data = await analytics_engine._calculate_system_health()
        
        return HealthResponse(
            status=health_data["status"],
            health_score=health_data["health_score"],
            error_rate=health_data["error_rate"],
            active_conversations=health_data["active_conversations"],
            system_status=health_data["status"]
        )
        
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get("/system/overview", response_model=SystemOverviewResponse)
async def get_system_overview():
    """Get comprehensive system overview."""
    try:
        overview_data = await analytics_engine.get_system_overview()
        
        return SystemOverviewResponse(
            system_metrics=overview_data,
            health_status=overview_data.get("health_status", {}),
            performance_trends=overview_data.get("performance_trends", {}),
            capacity_analysis=overview_data.get("capacity_analysis", {})
        )
        
    except Exception as e:
        logger.error(f"Failed to get system overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get("/system/tokens")
async def get_token_usage():
    """Get token usage statistics."""
    try:
        system_metrics = langfuse_manager.get_system_metrics()
        
        token_breakdown = {}
        cost_breakdown = {}
        
        for agent_id, agent_data in system_metrics["agent_metrics"].items():
            token_breakdown[agent_id] = agent_data["total_tokens"]
            cost_breakdown[agent_id] = agent_data["total_cost"]
        
        return AnalyticsResponse(
            status="success",
            data={
                "total_tokens": system_metrics["total_tokens"],
                "total_cost": system_metrics["total_cost"],
                "token_breakdown_by_agent": token_breakdown,
                "cost_breakdown_by_agent": cost_breakdown,
                "average_tokens_per_conversation": (
                    system_metrics["total_tokens"] / max(system_metrics["total_conversations"], 1)
                ),
                "average_cost_per_conversation": (
                    system_metrics["total_cost"] / max(system_metrics["total_conversations"], 1)
                )
            },
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to get token usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get("/system/costs")
async def get_cost_analysis():
    """Get detailed cost analysis."""
    try:
        cost_breakdown = analytics_engine._analyze_cost_breakdown()
        
        # Add cost trends and projections
        cost_data = {
            **cost_breakdown,
            "cost_per_conversation": {},
            "cost_efficiency": {},
            "cost_trends": {
                "daily_average": cost_breakdown["total_cost"] / max(1, 30),  # Rough estimate
                "projected_monthly": cost_breakdown["total_cost"] * (30 / max(1, 7)),  # Rough projection
                "optimization_potential": "15%"  # Would be calculated from actual data
            }
        }
        
        # Calculate cost per conversation for each agent
        for agent_id, agent_cost in cost_breakdown["by_agent"].items():
            agent_metrics = langfuse_manager.get_agent_metrics(agent_id)
            if agent_metrics and agent_metrics.total_executions > 0:
                cost_data["cost_per_conversation"][agent_id] = agent_cost / agent_metrics.total_executions
                cost_data["cost_efficiency"][agent_id] = agent_metrics.total_executions / max(agent_cost, 0.01)
        
        return AnalyticsResponse(
            status="success",
            data=cost_data,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to get cost analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Conversation analytics endpoints
@analytics_router.get("/conversations/{conversation_id}/metrics", response_model=ConversationAnalyticsResponse)
async def get_conversation_metrics(conversation_id: str):
    """Get detailed metrics for a specific conversation."""
    try:
        metrics = await analytics_engine.get_conversation_metrics(conversation_id)
        
        if "error" in metrics:
            raise HTTPException(status_code=404, detail=metrics["error"])
        
        # Get flow analysis
        flow_analysis = await analytics_engine.get_conversation_flow_analysis(conversation_id)
        
        # Generate recommendations
        recommendations = await _generate_conversation_recommendations(metrics)
        
        return ConversationAnalyticsResponse(
            conversation_id=conversation_id,
            metrics=metrics,
            flow_analysis=flow_analysis,
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get("/conversations/{conversation_id}/flow")
async def get_conversation_flow(conversation_id: str):
    """Get conversation flow analysis."""
    try:
        flow_analysis = await analytics_engine.get_conversation_flow_analysis(conversation_id)
        
        if "error" in flow_analysis:
            raise HTTPException(status_code=404, detail=flow_analysis["error"])
        
        return AnalyticsResponse(
            status="success",
            data=flow_analysis,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get("/conversations/{conversation_id}/export")
async def export_conversation_data(conversation_id: str):
    """Export complete conversation data for analysis."""
    try:
        export_data = langfuse_manager.export_conversation_data(conversation_id)
        
        if "error" in export_data:
            raise HTTPException(status_code=404, detail=export_data["error"])
        
        return AnalyticsResponse(
            status="success",
            data=export_data,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export conversation data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Agent performance endpoints
@analytics_router.get("/agents/{agent_id}/metrics", response_model=AgentPerformanceResponse)
async def get_agent_performance(agent_id: str):
    """Get detailed performance metrics for a specific agent."""
    try:
        performance_data = await analytics_engine.get_agent_performance(agent_id)
        
        if "error" in performance_data:
            raise HTTPException(status_code=404, detail=performance_data["error"])
        
        # Extract key metrics
        efficiency_score = performance_data.get("efficiency_score", 0)
        recommendations = performance_data.get("optimization_recommendations", [])
        
        return AgentPerformanceResponse(
            agent_id=agent_id,
            performance_metrics=performance_data,
            efficiency_score=efficiency_score,
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get("/agents")
async def get_all_agents_metrics():
    """Get performance metrics for all agents."""
    try:
        all_agents_data = {}
        
        for agent_id in langfuse_manager.agent_metrics.keys():
            agent_data = await analytics_engine.get_agent_performance(agent_id)
            all_agents_data[agent_id] = {
                "efficiency_score": agent_data.get("efficiency_score", 0),
                "success_rate": agent_data.get("success_rate", 0),
                "total_executions": agent_data.get("total_executions", 0),
                "cost_efficiency": agent_data.get("cost_efficiency", 0),
                "error_count": agent_data.get("error_count", 0)
            }
        
        # Add rankings
        ranked_agents = sorted(
            all_agents_data.items(),
            key=lambda x: x[1]["efficiency_score"],
            reverse=True
        )
        
        return AnalyticsResponse(
            status="success",
            data={
                "agent_metrics": all_agents_data,
                "agent_rankings": {
                    "by_efficiency": [agent[0] for agent in ranked_agents],
                    "by_success_rate": sorted(
                        all_agents_data.items(),
                        key=lambda x: x[1]["success_rate"],
                        reverse=True
                    )[:5]  # Top 5
                },
                "total_agents": len(all_agents_data)
            },
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to get all agents metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Document analytics endpoints
@analytics_router.get("/documents")
async def get_document_analytics():
    """Get document generation analytics."""
    try:
        document_data = await analytics_engine.get_document_analytics()
        
        return AnalyticsResponse(
            status="success",
            data=document_data,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to get document analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get("/documents/{document_type}")
async def get_document_type_analytics(document_type: str):
    """Get analytics for a specific document type."""
    try:
        all_document_data = await analytics_engine.get_document_analytics()
        document_stats = all_document_data["document_statistics"]
        
        if document_type not in document_stats:
            raise HTTPException(status_code=404, detail=f"Document type '{document_type}' not found")
        
        type_data = document_stats[document_type]
        
        # Add additional insights
        performance_insights = {
            "performance_rating": "excellent" if type_data["success_rate"] > 0.9 else 
                                 "good" if type_data["success_rate"] > 0.7 else
                                 "needs_improvement",
            "speed_rating": "fast" if type_data["average_generation_time"] < 30 else
                           "moderate" if type_data["average_generation_time"] < 60 else
                           "slow",
            "quality_rating": "high" if type_data["average_quality_score"] > 0.8 else
                             "medium" if type_data["average_quality_score"] > 0.6 else
                             "low"
        }
        
        return AnalyticsResponse(
            status="success",
            data={
                "document_type": document_type,
                "statistics": type_data,
                "performance_insights": performance_insights,
                "benchmarks": {
                    "target_success_rate": 0.95,
                    "target_generation_time": 45,
                    "target_quality_score": 0.85
                }
            },
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document type analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Reporting endpoints
@analytics_router.get("/reports/full")
async def get_full_analytics_report(
    start_date: Optional[datetime] = Query(None, description="Start date for report (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date for report (ISO format)"),
    report_type: str = Query("full", description="Type of report: full, system, agents, documents, conversations, performance")
):
    """Generate comprehensive analytics report."""
    try:
        report = await analytics_engine.export_analytics_report(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date
        )
        
        return AnalyticsResponse(
            status="success",
            data=report,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to generate analytics report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get("/reports/summary")
async def get_analytics_summary():
    """Get high-level analytics summary."""
    try:
        system_metrics = langfuse_manager.get_system_metrics()
        health_status = await analytics_engine._calculate_system_health()
        
        summary = {
            "overview": {
                "total_conversations": system_metrics["total_conversations"],
                "total_tokens": system_metrics["total_tokens"],
                "total_cost": system_metrics["total_cost"],
                "active_agents": len(system_metrics["agent_metrics"])
            },
            "health": {
                "status": health_status["status"],
                "health_score": health_status["health_score"],
                "error_rate": health_status["error_rate"]
            },
            "top_performers": {
                "most_active_agent": max(
                    system_metrics["agent_metrics"].items(),
                    key=lambda x: x[1]["total_executions"],
                    default=("none", {"total_executions": 0})
                )[0],
                "most_cost_effective": min(
                    [(k, v["total_cost"]/max(v["total_executions"], 1)) 
                     for k, v in system_metrics["agent_metrics"].items()],
                    key=lambda x: x[1],
                    default=("none", 0)
                )[0]
            },
            "trends": {
                "conversation_growth": "stable",  # Would calculate from historical data
                "cost_trend": "decreasing",
                "performance_trend": "improving"
            }
        }
        
        return AnalyticsResponse(
            status="success",
            data=summary,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to get analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Utility endpoints
@analytics_router.post("/flush")
async def flush_analytics_data():
    """Flush pending analytics data to external systems."""
    try:
        # Flush Langfuse data
        langfuse_manager.flush_data()
        
        return AnalyticsResponse(
            status="success",
            data={"message": "Analytics data flushed successfully"},
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to flush analytics data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get("/config")
async def get_analytics_config():
    """Get analytics configuration and status."""
    try:
        config = {
            "langfuse_enabled": langfuse_manager.enabled,
            "total_active_conversations": len(langfuse_manager.conversation_metrics),
            "total_tracked_agents": len(langfuse_manager.agent_metrics),
            "cache_size": len(analytics_engine.analytics_cache),
            "tracking_capabilities": {
                "conversation_tracking": True,
                "agent_performance": True,
                "document_generation": True,
                "cost_tracking": True,
                "flow_analysis": True,
                "real_time_metrics": True
            },
            "supported_models": list(langfuse_manager.model_costs.keys())
        }
        
        return AnalyticsResponse(
            status="success",
            data=config,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to get analytics config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
async def _generate_conversation_recommendations(metrics: Dict[str, Any]) -> List[str]:
    """Generate optimization recommendations for a conversation."""
    recommendations = []
    
    # Cost optimization
    if metrics.get("total_cost", 0) > 5.0:  # $5 threshold
        recommendations.append("Consider using more cost-effective models for routine operations")
    
    # Efficiency optimization
    if metrics.get("cost_per_message", 0) > 0.5:  # $0.50 per message
        recommendations.append("Review conversation flow to reduce message overhead")
    
    # Quality optimization
    quality_score = metrics.get("quality_score", 0)
    if quality_score < 0.7:
        recommendations.append("Review agent prompts and instructions to improve output quality")
    
    # Document success optimization
    doc_success_rate = metrics.get("document_success_rate", 0)
    if doc_success_rate < 0.8:
        recommendations.append("Investigate document generation failures and improve error handling")
    
    # Speed optimization
    if metrics.get("messages_per_minute", 0) < 2:
        recommendations.append("Optimize agent response times to improve conversation flow")
    
    if not recommendations:
        recommendations.append("Conversation performance is within optimal parameters")
    
    return recommendations