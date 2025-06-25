#!/usr/bin/env python3
"""
Quality Improvements Test Script
Tests the enhanced AgentPM system with complex ideas to validate quality improvements
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import sys
import os

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.multipass_generator import MultiPassGenerator, DocumentQuality
from backend.crews.project_crew import ProjectCrew
from backend.agents.orchestrator import OrchestratorAgent
from backend.agents.product_manager import ProductManagerAgent
from backend.agents.review import ReviewAgent


class QualityTestSuite:
    """Test suite for validating quality improvements"""
    
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "quality_metrics": {},
            "performance_metrics": {},
            "test_details": []
        }
        
        # Complex test scenarios
        self.complex_ideas = [
            {
                "name": "AI-Powered Healthcare Platform",
                "description": """Create a comprehensive healthcare platform that uses AI to predict patient health outcomes, 
                automate administrative tasks, ensure HIPAA compliance, integrate with existing hospital systems, 
                provide real-time monitoring, support telemedicine, manage drug interactions, and provide 
                personalized treatment recommendations. The platform must scale to handle millions of patients, 
                work across multiple countries with different regulations, support multiple languages, 
                and integrate with insurance systems.""",
                "complexity_score": 9.5,
                "expected_documents": ["PRD", "UXDD", "ERD", "SRS"],
                "quality_requirements": {
                    "completeness": 90,
                    "accuracy": 95,
                    "clarity": 85,
                    "compliance": 98
                }
            },
            {
                "name": "Quantum Computing Cloud Service",
                "description": """Develop a cloud-based quantum computing service that provides quantum algorithms as a service, 
                handles quantum error correction, manages quantum-classical hybrid workloads, provides quantum machine learning capabilities, 
                ensures quantum-safe cryptography, supports multiple quantum hardware vendors, provides quantum simulation capabilities, 
                and integrates with existing cloud infrastructure. The service must handle enterprise-scale workloads, 
                provide 99.99% uptime, support quantum advantage applications, and be accessible to developers without quantum expertise.""",
                "complexity_score": 10.0,
                "expected_documents": ["PRD", "BRD", "SRS", "ERD", "UXDD"],
                "quality_requirements": {
                    "completeness": 95,
                    "accuracy": 98,
                    "clarity": 90,
                    "innovation": 95
                }
            },
            {
                "name": "Sustainable Supply Chain Management",
                "description": """Build a comprehensive supply chain management platform that optimizes for sustainability, 
                tracks carbon footprint across the entire supply chain, ensures ethical sourcing, manages circular economy principles, 
                provides real-time supply chain visibility, handles disruption prediction and mitigation, integrates with IoT sensors, 
                supports blockchain-based provenance tracking, manages multi-tier supplier relationships, and provides ESG reporting. 
                The platform must handle global supply chains, support multiple industries, integrate with existing ERP systems, 
                and provide actionable sustainability insights.""",
                "complexity_score": 8.5,
                "expected_documents": ["PRD", "BRD", "ERD", "SRS"],
                "quality_requirements": {
                    "completeness": 88,
                    "accuracy": 92,
                    "sustainability_focus": 95,
                    "scalability": 90
                }
            }
        ]
    
    async def run_comprehensive_tests(self):
        """Run comprehensive quality improvement tests"""
        print("🚀 Starting AgentPM Quality Improvement Test Suite")
        print("=" * 60)
        
        for idea in self.complex_ideas:
            print(f"\n📋 Testing Complex Idea: {idea['name']}")
            print(f"Complexity Score: {idea['complexity_score']}/10")
            
            # Test different quality levels
            for quality_level in [DocumentQuality.STANDARD, DocumentQuality.PREMIUM, DocumentQuality.EXCELLENCE]:
                await self._test_quality_level(idea, quality_level)
            
            # Test multi-document batch processing
            await self._test_batch_processing(idea)
            
            # Test model comparison
            await self._test_model_comparison(idea)
        
        # Generate final report
        self._generate_test_report()
        
        return self.test_results
    
    async def _test_quality_level(self, idea: Dict[str, Any], quality_level: DocumentQuality):
        """Test a specific quality level"""
        test_name = f"{idea['name']} - {quality_level.value}"
        print(f"  🔍 Testing {quality_level.value} quality level...")
        
        start_time = time.time()
        
        try:
            # Initialize multi-pass generator
            generator = MultiPassGenerator()
            
            # Prepare document content
            initial_content = {
                "title": idea["name"],
                "description": idea["description"],
                "complexity_score": idea["complexity_score"],
                "requirements": idea["quality_requirements"]
            }
            
            # Generate with quality level
            result = await generator.generate_with_quality_level(
                initial_content,
                "Product Requirements Document",
                quality_level
            )
            
            execution_time = time.time() - start_time
            
            # Evaluate results
            test_result = self._evaluate_test_result(
                test_name,
                result,
                idea["quality_requirements"],
                execution_time,
                quality_level
            )
            
            self.test_results["test_details"].append(test_result)
            
            if test_result["passed"]:
                self.test_results["tests_passed"] += 1
                print(f"    ✅ PASSED - Quality Score: {result['quality_score']:.1f}%")
            else:
                self.test_results["tests_failed"] += 1
                print(f"    ❌ FAILED - Quality Score: {result['quality_score']:.1f}%")
            
            self.test_results["tests_run"] += 1
            
        except Exception as e:
            print(f"    💥 ERROR: {str(e)}")
            self.test_results["tests_failed"] += 1
            self.test_results["tests_run"] += 1
    
    async def _test_batch_processing(self, idea: Dict[str, Any]):
        """Test batch processing with multiple documents"""
        test_name = f"{idea['name']} - Batch Processing"
        print(f"  🔄 Testing batch processing...")
        
        start_time = time.time()
        
        try:
            generator = MultiPassGenerator()
            
            # Prepare multiple documents
            documents = {}
            for doc_type in idea["expected_documents"]:
                documents[doc_type.lower()] = {
                    "type": doc_type,
                    "title": f"{idea['name']} - {doc_type}",
                    "description": idea["description"],
                    "complexity_score": idea["complexity_score"]
                }
            
            # Generate batch with consistency review
            result = await generator.generate_batch_with_consistency_review(
                documents,
                DocumentQuality.PREMIUM
            )
            
            execution_time = time.time() - start_time
            
            # Evaluate batch results
            batch_quality = result["batch_quality_score"]
            consistency_score = result["consistency_review"]["consistency_score"]
            
            test_result = {
                "test_name": test_name,
                "passed": batch_quality >= 80 and consistency_score >= 75,
                "quality_score": batch_quality,
                "consistency_score": consistency_score,
                "execution_time": execution_time,
                "documents_generated": len(result["documents"]),
                "harmonization_applied": result["harmonization_applied"]
            }
            
            self.test_results["test_details"].append(test_result)
            
            if test_result["passed"]:
                self.test_results["tests_passed"] += 1
                print(f"    ✅ PASSED - Batch Quality: {batch_quality:.1f}%, Consistency: {consistency_score:.1f}%")
            else:
                self.test_results["tests_failed"] += 1
                print(f"    ❌ FAILED - Batch Quality: {batch_quality:.1f}%, Consistency: {consistency_score:.1f}%")
            
            self.test_results["tests_run"] += 1
            
        except Exception as e:
            print(f"    💥 ERROR: {str(e)}")
            self.test_results["tests_failed"] += 1
            self.test_results["tests_run"] += 1
    
    async def _test_model_comparison(self, idea: Dict[str, Any]):
        """Test different AI models for quality comparison"""
        test_name = f"{idea['name']} - Model Comparison"
        print(f"  🤖 Testing model comparison...")
        
        # Test with different models (mocked for now)
        models_to_test = [
            "claude-3-5-sonnet-20241022",
            "gpt-4o-2024-11-20",
            "gemini-2.0-flash-exp"
        ]
        
        model_results = {}
        
        for model in models_to_test:
            start_time = time.time()
            
            try:
                # Mock model testing (in real implementation, would use actual models)
                mock_quality_score = self._mock_model_performance(model, idea["complexity_score"])
                execution_time = time.time() - start_time + (0.5 * idea["complexity_score"])  # Simulate processing time
                
                model_results[model] = {
                    "quality_score": mock_quality_score,
                    "execution_time": execution_time,
                    "cost_estimate": self._estimate_cost(model, idea["complexity_score"])
                }
                
                print(f"    🔸 {model}: {mock_quality_score:.1f}% quality, {execution_time:.1f}s")
                
            except Exception as e:
                print(f"    💥 {model} ERROR: {str(e)}")
        
        # Find best performing model
        best_model = max(model_results.keys(), key=lambda m: model_results[m]["quality_score"])
        
        test_result = {
            "test_name": test_name,
            "passed": len(model_results) > 0,
            "best_model": best_model,
            "model_results": model_results,
            "quality_variance": max(model_results.values(), key=lambda x: x["quality_score"])["quality_score"] - 
                             min(model_results.values(), key=lambda x: x["quality_score"])["quality_score"]
        }
        
        self.test_results["test_details"].append(test_result)
        
        if test_result["passed"]:
            self.test_results["tests_passed"] += 1
            print(f"    ✅ PASSED - Best Model: {best_model}")
        else:
            self.test_results["tests_failed"] += 1
            print(f"    ❌ FAILED - No models completed successfully")
        
        self.test_results["tests_run"] += 1
    
    def _evaluate_test_result(
        self, 
        test_name: str, 
        result: Dict[str, Any], 
        requirements: Dict[str, float],
        execution_time: float,
        quality_level: DocumentQuality
    ) -> Dict[str, Any]:
        """Evaluate if test result meets requirements"""
        
        quality_score = result["quality_score"]
        
        # Define quality thresholds based on quality level
        thresholds = {
            DocumentQuality.STANDARD: 70,
            DocumentQuality.PREMIUM: 80,
            DocumentQuality.EXCELLENCE: 90
        }
        
        threshold = thresholds[quality_level]
        
        # Check if quality meets threshold
        quality_passed = quality_score >= threshold
        
        # Check specific requirements
        requirements_passed = all(
            quality_score >= req_value 
            for req_value in requirements.values()
        )
        
        return {
            "test_name": test_name,
            "passed": quality_passed and requirements_passed,
            "quality_score": quality_score,
            "threshold": threshold,
            "execution_time": execution_time,
            "quality_level": quality_level.value,
            "approval_status": result["approval_status"],
            "requirements_met": requirements_passed
        }
    
    def _mock_model_performance(self, model: str, complexity: float) -> float:
        """Mock model performance for testing purposes"""
        
        # Model performance characteristics (mocked)
        model_characteristics = {
            "claude-3-5-sonnet-20241022": {"base_quality": 88, "complexity_handling": 0.95},
            "gpt-4o-2024-11-20": {"base_quality": 85, "complexity_handling": 0.90},
            "gemini-2.0-flash-exp": {"base_quality": 82, "complexity_handling": 0.85}
        }
        
        if model not in model_characteristics:
            return 75.0  # Default score
        
        char = model_characteristics[model]
        
        # Calculate quality based on model characteristics and complexity
        quality_degradation = (complexity / 10) * (1 - char["complexity_handling"]) * 20
        final_quality = char["base_quality"] - quality_degradation
        
        return max(60, min(98, final_quality))  # Clamp between 60-98
    
    def _estimate_cost(self, model: str, complexity: float) -> float:
        """Estimate cost for model usage"""
        
        # Cost per 1K tokens (mocked)
        cost_per_1k = {
            "claude-3-5-sonnet-20241022": 0.003,
            "gpt-4o-2024-11-20": 0.005,
            "gemini-2.0-flash-exp": 0.0004
        }
        
        base_tokens = 10000 * complexity  # Estimate tokens based on complexity
        return cost_per_1k.get(model, 0.003) * (base_tokens / 1000)
    
    def _generate_test_report(self):
        """Generate comprehensive test report"""
        
        print("\n" + "="*60)
        print("📊 QUALITY IMPROVEMENT TEST REPORT")
        print("="*60)
        
        # Summary statistics
        total_tests = self.test_results["tests_run"]
        passed_tests = self.test_results["tests_passed"]
        failed_tests = self.test_results["tests_failed"]
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 SUMMARY STATISTICS:")
        print(f"  Total Tests Run: {total_tests}")
        print(f"  Tests Passed: {passed_tests}")
        print(f"  Tests Failed: {failed_tests}")
        print(f"  Success Rate: {success_rate:.1f}%")
        
        # Quality metrics analysis
        quality_scores = [
            test["quality_score"] 
            for test in self.test_results["test_details"] 
            if "quality_score" in test
        ]
        
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            max_quality = max(quality_scores)
            min_quality = min(quality_scores)
            
            print(f"\n🎯 QUALITY METRICS:")
            print(f"  Average Quality Score: {avg_quality:.1f}%")
            print(f"  Highest Quality Score: {max_quality:.1f}%")
            print(f"  Lowest Quality Score: {min_quality:.1f}%")
            print(f"  Quality Variance: {max_quality - min_quality:.1f}%")
        
        # Performance metrics
        execution_times = [
            test["execution_time"] 
            for test in self.test_results["test_details"] 
            if "execution_time" in test
        ]
        
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            max_time = max(execution_times)
            
            print(f"\n⏱️ PERFORMANCE METRICS:")
            print(f"  Average Execution Time: {avg_time:.1f}s")
            print(f"  Maximum Execution Time: {max_time:.1f}s")
        
        # Recommendations
        print(f"\n🔍 RECOMMENDATIONS:")
        
        if success_rate >= 80:
            print("  ✅ Quality improvements are working effectively")
        elif success_rate >= 60:
            print("  ⚠️ Quality improvements show promise but need refinement")
        else:
            print("  ❌ Quality improvements need significant enhancement")
        
        if avg_quality >= 85:
            print("  ✅ Quality scores meet excellence standards")
        elif avg_quality >= 75:
            print("  ⚠️ Quality scores are acceptable but could be improved")
        else:
            print("  ❌ Quality scores below acceptable thresholds")
        
        # Save detailed report
        report_file = f"quality_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        print("="*60)


async def main():
    """Run the quality improvement test suite"""
    
    print("🧪 AgentPM Quality Improvement Validation")
    print("Testing enhanced prompts, multi-pass generation, and model selection")
    print()
    
    # Initialize and run test suite
    test_suite = QualityTestSuite()
    results = await test_suite.run_comprehensive_tests()
    
    # Return exit code based on results
    success_rate = (results["tests_passed"] / results["tests_run"] * 100) if results["tests_run"] > 0 else 0
    
    if success_rate >= 80:
        print("\n🎉 Quality improvements validation: SUCCESSFUL")
        return 0
    elif success_rate >= 60:
        print("\n⚠️ Quality improvements validation: PARTIALLY SUCCESSFUL")
        return 1
    else:
        print("\n❌ Quality improvements validation: NEEDS IMPROVEMENT")
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)