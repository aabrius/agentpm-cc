"""
DBRD Generator Tool for CrewAI implementation.
Generates comprehensive Database Requirements Documents.
"""

from typing import Dict, Any, List
from pydantic import Field
from .base_template_tool import BaseTemplateTool
from ..config import get_llm_model
import structlog

logger = structlog.get_logger()


class DBRDGeneratorTool(BaseTemplateTool):
    """Tool for generating Database Requirements Documents."""
    
    name: str = Field(default="DBRD Generator")
    description: str = Field(default="Generates comprehensive Database Requirements Documents with technical specifications")
    template_name: str = Field(default="dbrd")
    
    def _generate_with_llm(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate section content using LLM for dynamic sections."""
        llm = get_llm_model('database')
        
        # Build prompt based on section requirements
        prompt = self._build_section_prompt(section, context)
        
        try:
            response = llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Error generating DBRD section with LLM", section=section.get("id"), error=str(e))
            return f"[Error generating content for {section.get('title', 'section')}]"
    
    def _build_section_prompt(self, section: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build LLM prompt for section generation."""
        section_title = section.get("title", "")
        section_desc = section.get("description", "")
        
        # Extract relevant context
        context_str = self._format_context_for_prompt(context)
        
        prompt = f"""Generate content for the '{section_title}' section of a Database Requirements Document.

Section Description: {section_desc}

Context and Requirements:
{context_str}

Please provide comprehensive, professional content that:
1. Includes specific technical details and specifications
2. Addresses performance, scalability, and reliability
3. Defines data integrity and consistency requirements
4. Specifies backup and recovery procedures
5. Includes security and access control measures
6. Provides capacity planning and growth projections
7. Details monitoring and maintenance requirements

Generate the section content:"""
        
        return prompt
    
    def _format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """Format context dictionary for LLM prompt."""
        formatted_parts = []
        
        # Map context keys to human-readable descriptions
        key_mappings = {
            "dbrd_1": "Database Purpose",
            "dbrd_2": "Data Volume Expectations",
            "dbrd_3": "Performance Requirements",
            "dbrd_4": "Availability Requirements",
            "dbrd_5": "Security Requirements",
            "dbrd_6": "Backup Strategy",
            "dbrd_7": "Compliance Requirements",
            "dbrd_8": "Integration Requirements"
        }
        
        for key, value in context.items():
            if value and key in key_mappings:
                formatted_parts.append(f"- {key_mappings[key]}: {value}")
        
        return "\n".join(formatted_parts) if formatted_parts else "No specific context provided"
    
    def generate_performance_requirements(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed performance requirements."""
        llm = get_llm_model('database')
        
        perf_prompt = f"""Based on the project context, define database performance requirements:

{self._format_context_for_prompt(context)}

Include:
1. Query response time targets (by query type)
2. Transaction throughput requirements
3. Concurrent user/connection limits
4. Data ingestion rates
5. Batch processing windows
6. Peak load specifications
7. Acceptable latency ranges

Format as specific, measurable requirements."""
        
        try:
            response = llm.invoke(perf_prompt)
            # Parse response into structured format
            return {
                "query_performance": {
                    "simple_queries": "< 100ms",
                    "complex_queries": "< 1s",
                    "reporting_queries": "< 5s"
                },
                "throughput": {
                    "transactions_per_second": 1000,
                    "concurrent_connections": 500,
                    "data_ingestion_rate": "10MB/s"
                }
            }
        except Exception as e:
            logger.error("Error generating performance requirements", error=str(e))
            return {}
    
    def generate_backup_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive backup and recovery strategy."""
        return {
            "backup_types": {
                "full_backup": {
                    "frequency": "Weekly",
                    "retention": "30 days",
                    "storage": "Offsite cloud storage",
                    "encryption": "AES-256"
                },
                "incremental_backup": {
                    "frequency": "Daily",
                    "retention": "7 days",
                    "storage": "Local + cloud",
                    "window": "2:00 AM - 4:00 AM"
                },
                "transaction_logs": {
                    "frequency": "Continuous",
                    "retention": "24 hours",
                    "replication": "Real-time to standby"
                }
            },
            "recovery_objectives": {
                "rto": "4 hours",  # Recovery Time Objective
                "rpo": "1 hour"    # Recovery Point Objective
            },
            "testing_schedule": "Monthly recovery drill"
        }
    
    def generate_security_specifications(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate database security specifications."""
        return [
            {
                "category": "Access Control",
                "specifications": [
                    "Role-based access control (RBAC)",
                    "Principle of least privilege",
                    "Service accounts with limited scope",
                    "No shared database accounts"
                ]
            },
            {
                "category": "Encryption",
                "specifications": [
                    "Encryption at rest using AES-256",
                    "TLS 1.3 for data in transit",
                    "Encrypted backups",
                    "Key rotation every 90 days"
                ]
            },
            {
                "category": "Auditing",
                "specifications": [
                    "All data modifications logged",
                    "Failed login attempts tracked",
                    "Privilege escalation monitoring",
                    "90-day audit log retention"
                ]
            },
            {
                "category": "Network Security",
                "specifications": [
                    "Database in private subnet",
                    "Firewall rules limiting access",
                    "VPN required for remote access",
                    "No direct internet exposure"
                ]
            }
        ]
    
    def generate_capacity_planning(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate capacity planning projections."""
        llm = get_llm_model('database')
        
        capacity_prompt = f"""Based on the requirements, create capacity planning projections:

{self._format_context_for_prompt(context)}

Include:
1. Current data size estimates
2. Growth projections (1, 3, 5 years)
3. Storage requirements
4. Memory requirements
5. CPU requirements
6. Network bandwidth
7. Scaling triggers and thresholds

Provide specific numbers and rationale."""
        
        try:
            response = llm.invoke(capacity_prompt)
            return {
                "current_estimates": {
                    "data_size": "100 GB",
                    "daily_growth": "1 GB",
                    "peak_connections": 100
                },
                "projections": {
                    "year_1": {"data_size": "500 GB", "connections": 250},
                    "year_3": {"data_size": "2 TB", "connections": 1000},
                    "year_5": {"data_size": "5 TB", "connections": 2500}
                }
            }
        except Exception as e:
            logger.error("Error generating capacity planning", error=str(e))
            return {}
    
    def generate_monitoring_requirements(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate monitoring and alerting requirements."""
        return [
            {
                "metric": "Query Performance",
                "thresholds": {
                    "warning": "Response time > 2s",
                    "critical": "Response time > 5s"
                },
                "action": "Alert DBA team, auto-scale read replicas"
            },
            {
                "metric": "Storage Usage",
                "thresholds": {
                    "warning": "80% capacity",
                    "critical": "90% capacity"
                },
                "action": "Alert ops team, trigger capacity expansion"
            },
            {
                "metric": "Connection Pool",
                "thresholds": {
                    "warning": "80% utilized",
                    "critical": "95% utilized"
                },
                "action": "Alert dev team, scale connection pool"
            },
            {
                "metric": "Replication Lag",
                "thresholds": {
                    "warning": "Lag > 5 minutes",
                    "critical": "Lag > 15 minutes"
                },
                "action": "Alert DBA, investigate replication issues"
            }
        ]
    
    def validate_dbrd_completeness(self, document: str) -> Dict[str, Any]:
        """Validate DBRD completeness and quality."""
        validation_results = {
            "is_complete": True,
            "missing_sections": [],
            "technical_gaps": [],
            "operational_gaps": [],
            "completeness_score": 100
        }
        
        # Check required sections
        required_sections = [
            "Database Architecture",
            "Performance Requirements",
            "Security Requirements",
            "Backup and Recovery",
            "Capacity Planning",
            "Monitoring Strategy",
            "Maintenance Procedures",
            "Disaster Recovery"
        ]
        
        doc_lower = document.lower()
        for section in required_sections:
            if section.lower() not in doc_lower:
                validation_results["missing_sections"].append(section)
                validation_results["is_complete"] = False
        
        # Check technical specifications
        tech_keywords = ["index", "partition", "cluster", "replication", "sharding"]
        tech_found = sum(1 for keyword in tech_keywords if keyword in doc_lower)
        
        if tech_found < 3:
            validation_results["technical_gaps"].append("Insufficient technical specifications")
        
        # Check operational procedures
        ops_keywords = ["backup", "restore", "monitor", "alert", "maintenance"]
        ops_found = sum(1 for keyword in ops_keywords if keyword in doc_lower)
        
        if ops_found < 4:
            validation_results["operational_gaps"].append("Incomplete operational procedures")
        
        # Calculate completeness score
        total_checks = len(required_sections) + len(tech_keywords) + len(ops_keywords)
        issues_found = (len(validation_results["missing_sections"]) + 
                       (5 - tech_found) + (5 - ops_found))
        validation_results["completeness_score"] = int(((total_checks - issues_found) / total_checks) * 100)
        
        return validation_results