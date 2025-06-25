"""
Analytics Engine for CrewAI Implementation.
Provides comprehensive observability and performance metrics.
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import structlog

from .langfuse_config import langfuse_manager, ConversationMetrics, AgentMetrics

logger = structlog.get_logger()


@dataclass
class SystemMetrics:
    """System-wide performance metrics."""
    total_conversations: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    active_conversations: int = 0
    average_conversation_duration: float = 0.0
    model_usage: Dict[str, Dict[str, int]] = None
    peak_usage_times: List[str] = None
    error_rate: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.model_usage is None:
            self.model_usage = {}
        if self.peak_usage_times is None:
            self.peak_usage_times = []
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class DocumentMetrics:
    """Document generation performance metrics."""
    document_type: str
    total_generations: int = 0
    success_rate: float = 0.0
    average_generation_time: float = 0.0
    average_word_count: int = 0
    average_quality_score: float = 0.0
    last_generated: Optional[datetime] = None


@dataclass
class ConversationFlowMetrics:
    """Conversation flow analysis metrics."""
    conversation_id: str
    flow_type: str
    phase_transitions: List[Dict[str, Any]] = None
    agent_handoffs: List[Dict[str, Any]] = None
    total_phases: int = 0
    stuck_phases: List[str] = None
    optimization_opportunities: List[str] = None
    
    def __post_init__(self):
        if self.phase_transitions is None:
            self.phase_transitions = []
        if self.agent_handoffs is None:
            self.agent_handoffs = []
        if self.stuck_phases is None:
            self.stuck_phases = []
        if self.optimization_opportunities is None:
            self.optimization_opportunities = []


class AnalyticsEngine:
    """
    Comprehensive analytics engine for CrewAI implementation.
    Provides real-time metrics, performance analysis, and optimization insights.
    """
    
    def __init__(self):
        self.langfuse_manager = langfuse_manager
        self.metrics_history: List[SystemMetrics] = []
        self.document_metrics: Dict[str, DocumentMetrics] = {}
        self.conversation_flows: Dict[str, ConversationFlowMetrics] = {}
        self.analytics_cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_conversation_metrics(self, conversation_id: str) -> Dict[str, Any]:
        """Get comprehensive metrics for a specific conversation."""
        
        # Get base metrics from Langfuse manager
        conv_metrics = self.langfuse_manager.get_conversation_metrics(conversation_id)
        
        if not conv_metrics:
            return {"error": "Conversation not found"}
        
        # Enhance with additional analytics
        metrics_dict = asdict(conv_metrics)
        
        # Add derived metrics
        metrics_dict.update({
            "messages_per_minute": self._calculate_messages_per_minute(conv_metrics),
            "cost_per_message": self._calculate_cost_per_message(conv_metrics),
            "tokens_per_message": self._calculate_tokens_per_message(conv_metrics),
            "agent_efficiency": self._calculate_agent_efficiency(conversation_id),
            "phase_analysis": await self._analyze_conversation_phases(conversation_id),
            "document_success_rate": self._calculate_document_success_rate(conv_metrics),
            "quality_score": self._calculate_overall_quality_score(conv_metrics)
        })
        
        return metrics_dict
    
    async def get_agent_performance(self, agent_id: str) -> Dict[str, Any]:
        """Get detailed performance metrics for a specific agent."""
        
        agent_metrics = self.langfuse_manager.get_agent_metrics(agent_id)
        
        if not agent_metrics:
            return {"error": "Agent not found"}
        
        metrics_dict = asdict(agent_metrics)
        
        # Add performance analysis
        metrics_dict.update({
            "performance_trend": await self._analyze_agent_trend(agent_id),
            "efficiency_score": self._calculate_efficiency_score(agent_metrics),
            "cost_efficiency": self._calculate_cost_efficiency(agent_metrics),
            "specialization_areas": await self._identify_agent_specializations(agent_id),
            "optimization_recommendations": await self._generate_agent_recommendations(agent_id)
        })
        
        return metrics_dict
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get system-wide metrics and health status."""
        
        # Get base system metrics
        base_metrics = self.langfuse_manager.get_system_metrics()
        
        # Calculate enhanced metrics
        system_metrics = SystemMetrics(
            total_conversations=base_metrics["total_conversations"],
            total_tokens=base_metrics["total_tokens"],
            total_cost=base_metrics["total_cost"],
            active_conversations=len([
                c for c in self.langfuse_manager.conversation_metrics.values()
                if c.completed_at is None
            ])
        )
        
        # Add system health indicators
        health_status = await self._calculate_system_health()
        performance_trends = await self._analyze_system_trends()
        capacity_analysis = await self._analyze_system_capacity()
        
        return {
            **asdict(system_metrics),
            "health_status": health_status,
            "performance_trends": performance_trends,
            "capacity_analysis": capacity_analysis,
            "agent_distribution": self._analyze_agent_distribution(),
            "cost_breakdown": self._analyze_cost_breakdown(),
            "usage_patterns": await self._analyze_usage_patterns()
        }
    
    async def get_document_analytics(self) -> Dict[str, Any]:
        """Get document generation analytics across all types."""
        
        document_stats = {}
        
        # Analyze each document type
        for conv_metrics in self.langfuse_manager.conversation_metrics.values():
            for doc_info in conv_metrics.document_generations:
                doc_type = doc_info["document_type"]
                
                if doc_type not in document_stats:
                    document_stats[doc_type] = {
                        "total_generations": 0,
                        "successful_generations": 0,
                        "failed_generations": 0,
                        "total_generation_time": 0.0,
                        "total_word_count": 0,
                        "quality_scores": [],
                        "generation_times": []
                    }
                
                stats = document_stats[doc_type]
                stats["total_generations"] += 1
                
                if doc_info["success"]:
                    stats["successful_generations"] += 1
                else:
                    stats["failed_generations"] += 1
                
                if doc_info.get("generation_time"):
                    stats["total_generation_time"] += doc_info["generation_time"]
                    stats["generation_times"].append(doc_info["generation_time"])
                
                if doc_info.get("word_count"):
                    stats["total_word_count"] += doc_info["word_count"]
                
                if doc_info.get("quality_score"):
                    stats["quality_scores"].append(doc_info["quality_score"])
        
        # Calculate derived metrics
        for doc_type, stats in document_stats.items():
            total = stats["total_generations"]
            if total > 0:
                stats["success_rate"] = stats["successful_generations"] / total
                stats["average_generation_time"] = (
                    stats["total_generation_time"] / len(stats["generation_times"])
                    if stats["generation_times"] else 0
                )
                stats["average_word_count"] = (
                    stats["total_word_count"] / stats["successful_generations"]
                    if stats["successful_generations"] > 0 else 0
                )
                stats["average_quality_score"] = (
                    sum(stats["quality_scores"]) / len(stats["quality_scores"])
                    if stats["quality_scores"] else 0
                )
        
        return {
            "document_statistics": document_stats,
            "overall_success_rate": self._calculate_overall_document_success_rate(document_stats),
            "performance_rankings": self._rank_document_performance(document_stats),
            "optimization_opportunities": self._identify_document_optimizations(document_stats)
        }
    
    async def get_conversation_flow_analysis(self, conversation_id: str) -> Dict[str, Any]:
        """Analyze conversation flow patterns and efficiency."""
        
        conv_metrics = self.langfuse_manager.get_conversation_metrics(conversation_id)
        if not conv_metrics:
            return {"error": "Conversation not found"}
        
        # Analyze message flow
        message_flow = self._analyze_message_flow(conv_metrics.messages)
        
        # Analyze agent interactions
        agent_flow = self._analyze_agent_interactions(conv_metrics.agent_interactions)
        
        # Analyze document generation flow
        document_flow = self._analyze_document_generation_flow(conv_metrics.document_generations)
        
        # Calculate flow efficiency
        efficiency_metrics = self._calculate_flow_efficiency(conv_metrics)
        
        return {
            "conversation_id": conversation_id,
            "message_flow": message_flow,
            "agent_flow": agent_flow,
            "document_flow": document_flow,
            "efficiency_metrics": efficiency_metrics,
            "bottlenecks": self._identify_flow_bottlenecks(conv_metrics),
            "optimization_suggestions": self._suggest_flow_optimizations(conv_metrics)
        }
    
    async def export_analytics_report(
        self, 
        report_type: str = "full",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Export comprehensive analytics report."""
        
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Filter conversations by date range
        filtered_conversations = self._filter_conversations_by_date(start_date, end_date)
        
        report = {
            "report_metadata": {
                "report_type": report_type,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "generated_at": datetime.utcnow().isoformat(),
                "conversation_count": len(filtered_conversations)
            }
        }
        
        if report_type in ["full", "system"]:
            report["system_metrics"] = await self.get_system_overview()
        
        if report_type in ["full", "agents"]:
            report["agent_metrics"] = await self._generate_agent_report(filtered_conversations)
        
        if report_type in ["full", "documents"]:
            report["document_metrics"] = await self.get_document_analytics()
        
        if report_type in ["full", "conversations"]:
            report["conversation_metrics"] = await self._generate_conversation_report(filtered_conversations)
        
        if report_type in ["full", "performance"]:
            report["performance_analysis"] = await self._generate_performance_analysis(filtered_conversations)
        
        return report
    
    # Helper methods for metrics calculations
    
    def _calculate_messages_per_minute(self, conv_metrics: ConversationMetrics) -> float:
        """Calculate messages per minute for conversation."""
        if conv_metrics.duration_seconds > 0:
            return (conv_metrics.total_messages / conv_metrics.duration_seconds) * 60
        return 0.0
    
    def _calculate_cost_per_message(self, conv_metrics: ConversationMetrics) -> float:
        """Calculate cost per message."""
        if conv_metrics.total_messages > 0:
            return conv_metrics.total_cost / conv_metrics.total_messages
        return 0.0
    
    def _calculate_tokens_per_message(self, conv_metrics: ConversationMetrics) -> float:
        """Calculate tokens per message."""
        if conv_metrics.total_messages > 0:
            return conv_metrics.total_tokens / conv_metrics.total_messages
        return 0.0
    
    def _calculate_agent_efficiency(self, conversation_id: str) -> Dict[str, float]:
        """Calculate efficiency metrics for agents in conversation."""
        efficiency = {}
        
        for agent_id, metrics in self.langfuse_manager.agent_metrics.items():
            if metrics.total_executions > 0:
                # Simple efficiency metric: success rate * tokens/execution
                tokens_per_execution = metrics.token_usage["total"] / metrics.total_executions
                efficiency[agent_id] = metrics.success_rate * (1000 / max(tokens_per_execution, 1))
        
        return efficiency
    
    async def _analyze_conversation_phases(self, conversation_id: str) -> Dict[str, Any]:
        """Analyze conversation phase transitions."""
        # This would analyze message timestamps and agent changes
        # to identify phase transitions
        return {
            "discovery_duration": 0,
            "definition_duration": 0,
            "review_duration": 0,
            "phase_transitions": [],
            "stuck_phases": []
        }
    
    def _calculate_document_success_rate(self, conv_metrics: ConversationMetrics) -> float:
        """Calculate document generation success rate."""
        if not conv_metrics.document_generations:
            return 0.0
        
        successful = sum(1 for doc in conv_metrics.document_generations if doc["success"])
        return successful / len(conv_metrics.document_generations)
    
    def _calculate_overall_quality_score(self, conv_metrics: ConversationMetrics) -> float:
        """Calculate overall quality score for conversation."""
        quality_scores = [
            doc.get("quality_score", 0) 
            for doc in conv_metrics.document_generations 
            if doc.get("quality_score")
        ]
        
        if quality_scores:
            return sum(quality_scores) / len(quality_scores)
        return 0.0
    
    async def _analyze_agent_trend(self, agent_id: str) -> Dict[str, Any]:
        """Analyze performance trends for agent."""
        # This would analyze historical performance data
        return {
            "trend": "stable",
            "performance_change": 0.0,
            "trend_period": "7d"
        }
    
    def _calculate_efficiency_score(self, agent_metrics: AgentMetrics) -> float:
        """Calculate overall efficiency score for agent."""
        if agent_metrics.total_executions == 0:
            return 0.0
        
        # Weighted score: success rate (70%) + speed factor (30%)
        speed_factor = 1.0 / max(agent_metrics.average_duration, 0.1)
        return (agent_metrics.success_rate * 0.7) + (min(speed_factor, 1.0) * 0.3)
    
    def _calculate_cost_efficiency(self, agent_metrics: AgentMetrics) -> float:
        """Calculate cost efficiency for agent."""
        total_cost = sum(agent_metrics.cost_breakdown.values())
        if total_cost > 0 and agent_metrics.total_executions > 0:
            return agent_metrics.total_executions / total_cost
        return 0.0
    
    async def _identify_agent_specializations(self, agent_id: str) -> List[str]:
        """Identify agent specialization areas."""
        # This would analyze which types of tasks the agent performs best
        return ["document_generation", "technical_analysis"]
    
    async def _generate_agent_recommendations(self, agent_id: str) -> List[str]:
        """Generate optimization recommendations for agent."""
        recommendations = []
        
        agent_metrics = self.langfuse_manager.get_agent_metrics(agent_id)
        if not agent_metrics:
            return recommendations
        
        if agent_metrics.success_rate < 0.8:
            recommendations.append("Review agent prompts and instructions for clarity")
        
        if agent_metrics.error_count > 10:
            recommendations.append("Implement additional error handling and validation")
        
        total_cost = sum(agent_metrics.cost_breakdown.values())
        if total_cost > 50.0:  # $50 threshold
            recommendations.append("Consider using more cost-effective models for routine tasks")
        
        return recommendations
    
    async def _calculate_system_health(self) -> Dict[str, Any]:
        """Calculate overall system health metrics."""
        
        total_conversations = len(self.langfuse_manager.conversation_metrics)
        error_count = sum(
            m.error_count for m in self.langfuse_manager.agent_metrics.values()
        )
        
        total_operations = sum(
            m.total_executions + m.error_count 
            for m in self.langfuse_manager.agent_metrics.values()
        )
        
        error_rate = error_count / max(total_operations, 1)
        
        # Simple health score calculation
        health_score = max(0, min(100, (1 - error_rate) * 100))
        
        status = "healthy"
        if health_score < 70:
            status = "degraded"
        if health_score < 50:
            status = "unhealthy"
        
        return {
            "status": status,
            "health_score": health_score,
            "error_rate": error_rate,
            "total_conversations": total_conversations,
            "active_agents": len(self.langfuse_manager.agent_metrics)
        }
    
    async def _analyze_system_trends(self) -> Dict[str, Any]:
        """Analyze system performance trends."""
        # This would analyze historical data trends
        return {
            "conversation_volume_trend": "increasing",
            "cost_trend": "stable",
            "performance_trend": "improving",
            "error_trend": "decreasing"
        }
    
    async def _analyze_system_capacity(self) -> Dict[str, Any]:
        """Analyze system capacity and resource utilization."""
        active_conversations = len([
            c for c in self.langfuse_manager.conversation_metrics.values()
            if c.completed_at is None
        ])
        
        return {
            "active_conversations": active_conversations,
            "estimated_capacity": 100,  # This would be configurable
            "utilization_percentage": min(100, (active_conversations / 100) * 100),
            "resource_status": "optimal"
        }
    
    def _analyze_agent_distribution(self) -> Dict[str, Any]:
        """Analyze agent usage distribution."""
        agent_usage = {}
        
        for agent_id, metrics in self.langfuse_manager.agent_metrics.items():
            agent_usage[agent_id] = {
                "executions": metrics.total_executions,
                "success_rate": metrics.success_rate,
                "total_cost": sum(metrics.cost_breakdown.values())
            }
        
        return agent_usage
    
    def _analyze_cost_breakdown(self) -> Dict[str, Any]:
        """Analyze cost breakdown by model and agent."""
        cost_breakdown = {
            "by_model": {},
            "by_agent": {},
            "total_cost": 0.0
        }
        
        for agent_id, metrics in self.langfuse_manager.agent_metrics.items():
            agent_cost = sum(metrics.cost_breakdown.values())
            cost_breakdown["by_agent"][agent_id] = agent_cost
            cost_breakdown["total_cost"] += agent_cost
            
            for model, cost in metrics.cost_breakdown.items():
                cost_breakdown["by_model"][model] = cost_breakdown["by_model"].get(model, 0) + cost
        
        return cost_breakdown
    
    async def _analyze_usage_patterns(self) -> Dict[str, Any]:
        """Analyze usage patterns and peak times."""
        # This would analyze conversation creation times to identify patterns
        return {
            "peak_hours": [9, 10, 11, 14, 15, 16],
            "peak_days": ["Monday", "Tuesday", "Wednesday", "Thursday"],
            "usage_pattern": "business_hours"
        }
    
    def _filter_conversations_by_date(
        self, start_date: datetime, end_date: datetime
    ) -> List[ConversationMetrics]:
        """Filter conversations by date range."""
        filtered = []
        
        for conv_metrics in self.langfuse_manager.conversation_metrics.values():
            if start_date <= conv_metrics.created_at <= end_date:
                filtered.append(conv_metrics)
        
        return filtered
    
    # Additional helper methods for report generation
    async def _generate_agent_report(self, conversations: List[ConversationMetrics]) -> Dict[str, Any]:
        """Generate comprehensive agent performance report."""
        agent_report = {}
        
        for agent_id, metrics in self.langfuse_manager.agent_metrics.items():
            agent_report[agent_id] = await self.get_agent_performance(agent_id)
        
        return agent_report
    
    async def _generate_conversation_report(self, conversations: List[ConversationMetrics]) -> Dict[str, Any]:
        """Generate conversation analytics report."""
        total_conversations = len(conversations)
        total_tokens = sum(c.total_tokens for c in conversations)
        total_cost = sum(c.total_cost for c in conversations)
        
        avg_duration = sum(
            c.duration_seconds for c in conversations if c.duration_seconds > 0
        ) / max(len([c for c in conversations if c.duration_seconds > 0]), 1)
        
        return {
            "total_conversations": total_conversations,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "average_duration": avg_duration,
            "conversation_types": self._analyze_conversation_types(conversations),
            "success_rates": self._calculate_conversation_success_rates(conversations)
        }
    
    async def _generate_performance_analysis(self, conversations: List[ConversationMetrics]) -> Dict[str, Any]:
        """Generate performance analysis report."""
        return {
            "throughput_analysis": self._analyze_throughput(conversations),
            "efficiency_analysis": self._analyze_efficiency(conversations),
            "quality_analysis": self._analyze_quality(conversations),
            "bottleneck_analysis": self._analyze_bottlenecks(conversations)
        }
    
    def _analyze_conversation_types(self, conversations: List[ConversationMetrics]) -> Dict[str, int]:
        """Analyze distribution of conversation types."""
        type_counts = {}
        for conv in conversations:
            conv_type = conv.conversation_type
            type_counts[conv_type] = type_counts.get(conv_type, 0) + 1
        return type_counts
    
    def _calculate_conversation_success_rates(self, conversations: List[ConversationMetrics]) -> Dict[str, float]:
        """Calculate success rates by conversation type."""
        success_rates = {}
        type_counts = {}
        type_successes = {}
        
        for conv in conversations:
            conv_type = conv.conversation_type
            type_counts[conv_type] = type_counts.get(conv_type, 0) + 1
            
            # Consider conversation successful if it has generated documents
            if conv.document_generations:
                type_successes[conv_type] = type_successes.get(conv_type, 0) + 1
        
        for conv_type, total in type_counts.items():
            successes = type_successes.get(conv_type, 0)
            success_rates[conv_type] = successes / total if total > 0 else 0
        
        return success_rates
    
    def _analyze_throughput(self, conversations: List[ConversationMetrics]) -> Dict[str, Any]:
        """Analyze system throughput metrics."""
        if not conversations:
            return {"conversations_per_hour": 0, "tokens_per_hour": 0}
        
        # Calculate hourly averages
        total_hours = (max(c.created_at for c in conversations) - 
                      min(c.created_at for c in conversations)).total_seconds() / 3600
        
        if total_hours > 0:
            conversations_per_hour = len(conversations) / total_hours
            tokens_per_hour = sum(c.total_tokens for c in conversations) / total_hours
        else:
            conversations_per_hour = len(conversations)
            tokens_per_hour = sum(c.total_tokens for c in conversations)
        
        return {
            "conversations_per_hour": conversations_per_hour,
            "tokens_per_hour": tokens_per_hour,
            "peak_throughput": "Not calculated"  # Would need time-series data
        }
    
    def _analyze_efficiency(self, conversations: List[ConversationMetrics]) -> Dict[str, Any]:
        """Analyze system efficiency metrics."""
        total_conversations = len(conversations)
        if total_conversations == 0:
            return {"overall_efficiency": 0}
        
        # Calculate various efficiency metrics
        avg_tokens_per_conversation = sum(c.total_tokens for c in conversations) / total_conversations
        avg_cost_per_conversation = sum(c.total_cost for c in conversations) / total_conversations
        avg_duration = sum(c.duration_seconds for c in conversations if c.duration_seconds > 0) / total_conversations
        
        return {
            "overall_efficiency": min(100, max(0, 100 - (avg_cost_per_conversation * 10))),  # Simple metric
            "avg_tokens_per_conversation": avg_tokens_per_conversation,
            "avg_cost_per_conversation": avg_cost_per_conversation,
            "avg_duration_seconds": avg_duration
        }
    
    def _analyze_quality(self, conversations: List[ConversationMetrics]) -> Dict[str, Any]:
        """Analyze output quality metrics."""
        quality_scores = []
        
        for conv in conversations:
            for doc in conv.document_generations:
                if doc.get("quality_score"):
                    quality_scores.append(doc["quality_score"])
        
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
        else:
            avg_quality = 0
        
        return {
            "average_quality_score": avg_quality,
            "quality_distribution": self._calculate_quality_distribution(quality_scores),
            "quality_trend": "stable"  # Would need historical data
        }
    
    def _calculate_quality_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate distribution of quality scores."""
        if not scores:
            return {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        
        distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        
        for score in scores:
            if score >= 0.9:
                distribution["excellent"] += 1
            elif score >= 0.7:
                distribution["good"] += 1
            elif score >= 0.5:
                distribution["fair"] += 1
            else:
                distribution["poor"] += 1
        
        return distribution
    
    def _analyze_bottlenecks(self, conversations: List[ConversationMetrics]) -> Dict[str, Any]:
        """Identify system bottlenecks."""
        # Analyze agent performance to identify bottlenecks
        agent_performance = {}
        
        for agent_id, metrics in self.langfuse_manager.agent_metrics.items():
            agent_performance[agent_id] = {
                "avg_duration": metrics.average_duration,
                "error_rate": metrics.error_count / max(metrics.total_executions, 1),
                "success_rate": metrics.success_rate
            }
        
        # Identify potential bottlenecks
        bottlenecks = []
        for agent_id, perf in agent_performance.items():
            if perf["error_rate"] > 0.1:  # 10% error rate threshold
                bottlenecks.append(f"High error rate in {agent_id}")
            if perf["avg_duration"] > 30:  # 30 second threshold
                bottlenecks.append(f"Slow response time in {agent_id}")
        
        return {
            "identified_bottlenecks": bottlenecks,
            "agent_performance": agent_performance
        }


# Global analytics engine instance
analytics_engine = AnalyticsEngine()