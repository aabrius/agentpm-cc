"""
Multi-Pass Document Generation Service
Implements iterative document refinement with quality review cycles
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import structlog
from ..agents.review import ReviewAgent
from ..prompts.enhanced_review_prompt import (
    ENHANCED_DOCUMENT_REVIEW_PROMPT,
    ENHANCED_CONSISTENCY_REVIEW_PROMPT,
    ENHANCED_ITERATIVE_IMPROVEMENT_PROMPT
)
from ..config import get_crew_config

logger = structlog.get_logger()


class DocumentQuality(Enum):
    """Quality levels for document generation"""
    DRAFT = "draft"          # Basic structure, minimal content
    STANDARD = "standard"    # Complete content, basic review
    PREMIUM = "premium"      # Multiple passes, enhanced review
    EXCELLENCE = "excellence" # 5-pass process, comprehensive validation


@dataclass
class ReviewResult:
    """Result from a single review pass"""
    pass_number: int
    quality_scores: Dict[str, float]
    overall_score: float
    issues: Dict[str, List[str]]  # severity -> issues
    recommendations: List[str]
    approval_status: str
    improvements_needed: bool


@dataclass
class IterationResult:
    """Result from a document improvement iteration"""
    iteration_number: int
    improvements_made: List[str]
    quality_improvement: float
    remaining_issues: List[str]
    ready_for_next_pass: bool


class MultiPassGenerator:
    """Service for multi-pass document generation and refinement"""
    
    def __init__(self, conversation_id: Optional[str] = None):
        self.conversation_id = conversation_id
        self.review_agent = ReviewAgent()
        self.max_iterations_per_pass = 3
        self.quality_threshold = 85.0
        self.excellence_threshold = 95.0
        
    async def generate_with_quality_level(
        self,
        initial_content: Dict[str, Any],
        document_type: str,
        quality_level: DocumentQuality = DocumentQuality.PREMIUM
    ) -> Dict[str, Any]:
        """Generate document with specified quality level"""
        
        logger.info(f"Starting multi-pass generation for {document_type} at {quality_level.value} level")
        
        # Configure passes based on quality level
        pass_config = self._get_pass_configuration(quality_level)
        
        # Initialize tracking
        generation_history = {
            "quality_level": quality_level.value,
            "document_type": document_type,
            "passes_completed": 0,
            "iterations_completed": 0,
            "quality_progression": [],
            "final_quality_score": 0,
            "review_results": [],
            "improvement_iterations": []
        }
        
        current_content = initial_content.copy()
        
        # Execute configured number of passes
        for pass_num in range(1, pass_config["passes"] + 1):
            logger.info(f"Executing review pass {pass_num}/{pass_config['passes']}")
            
            # Perform review pass
            review_result = await self._execute_review_pass(
                current_content, 
                document_type, 
                pass_num,
                pass_config["pass_focus"][pass_num - 1] if pass_num <= len(pass_config["pass_focus"]) else "comprehensive"
            )
            
            generation_history["review_results"].append(review_result)
            generation_history["quality_progression"].append(review_result.overall_score)
            
            # If improvements needed, iterate
            if review_result.improvements_needed and pass_num < pass_config["passes"]:
                iteration_results = await self._improve_content_iteratively(
                    current_content,
                    review_result,
                    document_type,
                    max_iterations=pass_config["max_iterations"]
                )
                
                generation_history["improvement_iterations"].extend(iteration_results)
                
                # Update content with improvements
                if iteration_results:
                    last_iteration = iteration_results[-1]
                    if last_iteration.ready_for_next_pass:
                        # Apply improvements to content (simplified)
                        current_content = self._apply_improvements(current_content, iteration_results)
            
            generation_history["passes_completed"] = pass_num
            
            # Check if excellence threshold reached early
            if review_result.overall_score >= self.excellence_threshold:
                logger.info(f"Excellence threshold reached at pass {pass_num}")
                break
        
        # Final quality assessment
        final_review = await self._execute_final_review(current_content, document_type)
        generation_history["final_quality_score"] = final_review.overall_score
        generation_history["review_results"].append(final_review)
        
        return {
            "content": current_content,
            "quality_metrics": generation_history,
            "approval_status": final_review.approval_status,
            "quality_score": final_review.overall_score,
            "recommendations": final_review.recommendations
        }
    
    async def generate_batch_with_consistency_review(
        self,
        documents: Dict[str, Dict[str, Any]],
        quality_level: DocumentQuality = DocumentQuality.PREMIUM
    ) -> Dict[str, Any]:
        """Generate multiple documents with cross-document consistency review"""
        
        logger.info(f"Starting batch generation with consistency review for {len(documents)} documents")
        
        # Generate individual documents first
        generated_docs = {}
        individual_quality_scores = {}
        
        for doc_name, doc_content in documents.items():
            doc_type = doc_content.get("type", "document")
            result = await self.generate_with_quality_level(
                doc_content,
                doc_type,
                quality_level
            )
            generated_docs[doc_name] = result["content"]
            individual_quality_scores[doc_name] = result["quality_score"]
        
        # Perform cross-document consistency review
        consistency_review = await self._execute_consistency_review(generated_docs)
        
        # If consistency issues found, perform harmonization
        if consistency_review["issues_found"]:
            harmonized_docs = await self._harmonize_documents(
                generated_docs,
                consistency_review["conflicts"]
            )
            generated_docs = harmonized_docs
        
        return {
            "documents": generated_docs,
            "individual_quality_scores": individual_quality_scores,
            "consistency_review": consistency_review,
            "batch_quality_score": sum(individual_quality_scores.values()) / len(individual_quality_scores),
            "harmonization_applied": consistency_review["issues_found"]
        }
    
    def _get_pass_configuration(self, quality_level: DocumentQuality) -> Dict[str, Any]:
        """Get pass configuration based on quality level"""
        
        configurations = {
            DocumentQuality.DRAFT: {
                "passes": 1,
                "max_iterations": 1,
                "pass_focus": ["basic_structure"]
            },
            DocumentQuality.STANDARD: {
                "passes": 2,
                "max_iterations": 2,
                "pass_focus": ["structure", "content"]
            },
            DocumentQuality.PREMIUM: {
                "passes": 3,
                "max_iterations": 2,
                "pass_focus": ["structure", "content", "clarity"]
            },
            DocumentQuality.EXCELLENCE: {
                "passes": 5,
                "max_iterations": 3,
                "pass_focus": ["structure", "content", "clarity", "strategic_value", "excellence_polish"]
            }
        }
        
        return configurations[quality_level]
    
    async def _execute_review_pass(
        self,
        content: Dict[str, Any],
        document_type: str,
        pass_number: int,
        focus_area: str
    ) -> ReviewResult:
        """Execute a single review pass with specific focus"""
        
        # Create review prompt with pass-specific focus
        review_prompt = ENHANCED_DOCUMENT_REVIEW_PROMPT.format(
            document_type=document_type,
            document_content=str(content)
        )
        
        # Simulate review execution (in real implementation, would use agent)
        # For now, return structured mock results
        mock_scores = {
            "completeness": 82.0 + (pass_number * 3),
            "accuracy": 85.0 + (pass_number * 2),
            "clarity": 80.0 + (pass_number * 4),
            "consistency": 88.0 + (pass_number * 2),
            "compliance": 90.0 + (pass_number * 1),
            "usability": 83.0 + (pass_number * 3),
            "innovation": 75.0 + (pass_number * 5),
            "scalability": 87.0 + (pass_number * 2)
        }
        
        overall_score = sum(mock_scores.values()) / len(mock_scores)
        
        # Determine issues based on scores
        issues = {
            "blocker": [],
            "critical": [],
            "major": [],
            "minor": [],
            "polish": []
        }
        
        recommendations = []
        
        for dimension, score in mock_scores.items():
            if score < 70:
                issues["critical"].append(f"{dimension} requires significant improvement")
                recommendations.append(f"Focus on enhancing {dimension}")
            elif score < 80:
                issues["major"].append(f"{dimension} needs improvement")
            elif score < 90:
                issues["minor"].append(f"{dimension} has room for enhancement")
            else:
                issues["polish"].append(f"{dimension} could be polished further")
        
        # Determine approval status
        if overall_score >= self.excellence_threshold:
            approval_status = "approved_excellent"
        elif overall_score >= self.quality_threshold:
            approval_status = "approved_conditional"
        else:
            approval_status = "requires_improvement"
        
        return ReviewResult(
            pass_number=pass_number,
            quality_scores=mock_scores,
            overall_score=overall_score,
            issues=issues,
            recommendations=recommendations,
            approval_status=approval_status,
            improvements_needed=overall_score < self.quality_threshold
        )
    
    async def _improve_content_iteratively(
        self,
        content: Dict[str, Any],
        review_result: ReviewResult,
        document_type: str,
        max_iterations: int
    ) -> List[IterationResult]:
        """Improve content through iterative refinement"""
        
        iterations = []
        current_quality = review_result.overall_score
        
        for iteration in range(1, max_iterations + 1):
            logger.info(f"Executing improvement iteration {iteration}/{max_iterations}")
            
            # Simulate improvement process
            improvements_made = []
            quality_improvement = 0
            
            # Address highest priority issues first
            if review_result.issues["critical"]:
                improvements_made.append("Addressed critical issues")
                quality_improvement += 10
            elif review_result.issues["major"]:
                improvements_made.append("Resolved major issues")
                quality_improvement += 7
            elif review_result.issues["minor"]:
                improvements_made.append("Enhanced minor issues")
                quality_improvement += 4
            else:
                improvements_made.append("Applied polish improvements")
                quality_improvement += 2
            
            new_quality = min(100, current_quality + quality_improvement)
            
            iteration_result = IterationResult(
                iteration_number=iteration,
                improvements_made=improvements_made,
                quality_improvement=quality_improvement,
                remaining_issues=[],
                ready_for_next_pass=new_quality >= self.quality_threshold
            )
            
            iterations.append(iteration_result)
            current_quality = new_quality
            
            # Stop if quality threshold reached
            if new_quality >= self.quality_threshold:
                break
        
        return iterations
    
    async def _execute_final_review(
        self,
        content: Dict[str, Any],
        document_type: str
    ) -> ReviewResult:
        """Execute final comprehensive review"""
        
        return await self._execute_review_pass(content, document_type, 99, "final_validation")
    
    async def _execute_consistency_review(
        self,
        documents: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute cross-document consistency review"""
        
        # Simulate consistency analysis
        conflicts_found = len(documents) > 1  # Mock: assume conflicts in multi-doc scenarios
        
        return {
            "issues_found": conflicts_found,
            "conflicts": [
                {
                    "type": "terminology",
                    "documents": list(documents.keys())[:2],
                    "description": "Inconsistent terminology usage",
                    "severity": "major"
                }
            ] if conflicts_found else [],
            "consistency_score": 85.0 if not conflicts_found else 75.0,
            "harmonization_required": conflicts_found
        }
    
    async def _harmonize_documents(
        self,
        documents: Dict[str, Dict[str, Any]],
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Harmonize documents to resolve conflicts"""
        
        # Simulate harmonization process
        harmonized = documents.copy()
        
        for doc_name in harmonized:
            # Mock: add harmonization metadata
            harmonized[doc_name]["harmonized"] = True
            harmonized[doc_name]["conflicts_resolved"] = len(conflicts)
        
        return harmonized
    
    def _apply_improvements(
        self,
        content: Dict[str, Any],
        iterations: List[IterationResult]
    ) -> Dict[str, Any]:
        """Apply improvements from iterations to content"""
        
        improved_content = content.copy()
        
        # Mock: add improvement metadata
        improved_content["improvements_applied"] = [
            improvement 
            for iteration in iterations 
            for improvement in iteration.improvements_made
        ]
        
        return improved_content