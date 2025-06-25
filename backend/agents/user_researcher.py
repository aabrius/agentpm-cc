"""
User Researcher Agent for CrewAI implementation.
Creates user personas, journey maps, and research documentation.
"""

from crewai import Agent
from typing import Dict, Any, List
from ..tools.persona_generator import PersonaGeneratorTool
from ..tools.journey_mapper import JourneyMapperTool
from ..tools.research_synthesizer import ResearchSynthesizerTool
from ..tools.interview_analyzer import InterviewAnalyzerTool
from ..tools.survey_designer import SurveyDesignerTool
from ..config import get_llm_model


class UserResearcherAgent:
    """Creates and configures the User Researcher agent for user experience research."""
    
    # Preserved research methodologies from original implementation
    RESEARCH_METHODS = {
        "interviews": "In-depth user interviews for qualitative insights",
        "surveys": "Quantitative data collection at scale",
        "usability_testing": "Direct observation of user interactions",
        "card_sorting": "Information architecture validation",
        "journey_mapping": "Understanding end-to-end user experiences",
        "persona_development": "Creating representative user archetypes",
        "contextual_inquiry": "Observing users in their environment",
        "a_b_testing": "Comparing design variations with real users"
    }
    
    # Preserved user research questions from original implementation
    RESEARCH_QUESTIONS = [
        {
            "id": "research_1",
            "content": "Who are the primary and secondary users?",
            "required": True
        },
        {
            "id": "research_2",
            "content": "What are their main goals and pain points?",
            "required": True
        },
        {
            "id": "research_3",
            "content": "What is their current workflow or process?",
            "required": True
        },
        {
            "id": "research_4",
            "content": "What are their technical capabilities and limitations?",
            "required": True
        },
        {
            "id": "research_5",
            "content": "What motivates them to use this solution?",
            "required": True
        },
        {
            "id": "research_6",
            "content": "What are their expectations and success criteria?",
            "required": False
        },
        {
            "id": "research_7",
            "content": "What competing solutions do they currently use?",
            "required": False
        },
        {
            "id": "research_8",
            "content": "What cultural or contextual factors influence their behavior?",
            "required": False
        }
    ]
    
    @staticmethod
    def create(model_override: str = None) -> Agent:
        """Create the User Researcher agent with full capabilities."""
        return Agent(
            role='Senior User Experience Researcher',
            goal='''Understand users deeply through research, creating actionable insights 
            that drive product decisions. Develop comprehensive personas, journey maps, 
            and research findings that ensure user-centered design.''',
            backstory='''You are an expert User Experience Researcher with 12+ years of 
            experience uncovering user needs and behaviors. You've conducted research for 
            products ranging from consumer apps to enterprise software, always advocating 
            for the user's perspective. Your expertise includes qualitative and quantitative 
            research methods, from ethnographic studies to large-scale surveys. You excel 
            at synthesizing complex research data into clear, actionable insights that 
            product teams can use. Your personas are vivid and data-driven, your journey 
            maps reveal critical opportunities, and your research reports have shaped 
            successful products used by millions. You balance empathy with analytical rigor, 
            ensuring that user insights are both emotionally resonant and statistically 
            valid. You're skilled at facilitating workshops, conducting interviews, and 
            presenting findings to stakeholders at all levels.''',
            tools=[
                PersonaGeneratorTool(),
                JourneyMapperTool(),
                ResearchSynthesizerTool(),
                InterviewAnalyzerTool(),
                SurveyDesignerTool()
            ],
            llm=get_llm_model('user_researcher', override_model=model_override),
            verbose=True,
            max_iter=15,
            memory=False
        )
    
    @staticmethod
    def create_persona_development_task(project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for developing user personas."""
        return {
            "description": f"""Develop comprehensive user personas based on:
            
            {project_context}
            
            Each persona should include:
            1. Demographics and Background
            2. Goals and Motivations
            3. Pain Points and Frustrations
            4. Technical Proficiency
            5. Behavioral Patterns
            6. Preferred Channels and Devices
            7. Decision-Making Criteria
            8. Quote that Captures Their Perspective
            9. Day in the Life Scenario
            10. Relationship to Product/Service
            11. Success Metrics
            12. Potential Objections
            
            Create 3-5 primary personas and 2-3 secondary personas.""",
            "expected_output": """Complete persona documentation including:
            - Detailed persona profiles with visuals
            - Behavioral attributes and patterns
            - User needs and goals mapping
            - Persona comparison matrix
            - Usage scenarios for each persona"""
        }
    
    @staticmethod
    def create_journey_mapping_task(personas: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for journey mapping."""
        return {
            "description": f"""Create detailed user journey maps for personas:
            
            {personas}
            
            Each journey map should include:
            1. Journey Stages (Awareness → Consideration → Decision → Onboarding → Usage → Advocacy)
            2. User Actions at Each Stage
            3. Touchpoints and Channels
            4. Thoughts and Emotions
            5. Pain Points and Friction
            6. Opportunities for Improvement
            7. Moments of Truth
            8. Support Needs
            9. Success Metrics
            10. Cross-functional Dependencies
            
            Map both current state and ideal future state journeys.""",
            "expected_output": """Comprehensive journey maps including:
            - Visual journey diagrams
            - Emotion curves
            - Touchpoint inventory
            - Opportunity matrix
            - Implementation recommendations"""
        }
    
    @staticmethod
    def create_research_synthesis_task(research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for synthesizing research findings."""
        return {
            "description": f"""Synthesize user research findings from:
            
            {research_data}
            
            Create a comprehensive research report including:
            1. Executive Summary
            2. Research Methodology
            3. Key Findings and Insights
            4. User Needs Hierarchy
            5. Behavioral Patterns
            6. Attitudinal Insights
            7. Segmentation Analysis
            8. Competitive Benchmarking
            9. Design Implications
            10. Product Recommendations
            11. Further Research Needs
            12. Appendices with Raw Data
            
            Ensure findings are actionable and tied to business objectives.""",
            "expected_output": """Research synthesis report with:
            - Prioritized insights with evidence
            - Clear recommendations
            - Visual data representations
            - Stakeholder-specific summaries
            - Action item roadmap"""
        }
    
    @staticmethod
    def create_usability_study_task(prototype_or_product: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for planning and conducting usability studies."""
        return {
            "description": f"""Design a comprehensive usability study for:
            
            {prototype_or_product}
            
            Plan should include:
            1. Study Objectives and Research Questions
            2. Participant Recruitment Criteria
            3. Task Scenarios and Scripts
            4. Testing Protocol (Moderated/Unmoderated)
            5. Success Metrics and KPIs
            6. Data Collection Methods
            7. Analysis Framework
            8. Testing Environment Setup
            9. Accessibility Testing
            10. International/Cultural Considerations
            
            Design for both qualitative insights and quantitative metrics.""",
            "expected_output": """Complete usability study package:
            - Study protocol and scripts
            - Participant screener
            - Task scenarios
            - Data collection templates
            - Analysis framework"""
        }
    
    @staticmethod
    def create_survey_design_task(research_objectives: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for designing user surveys."""
        return {
            "description": f"""Design a comprehensive user survey based on objectives:
            
            {research_objectives}
            
            Survey should include:
            1. Screening Questions
            2. Demographic Collection
            3. Behavioral Questions
            4. Attitudinal Scales
            5. Feature Prioritization
            6. Satisfaction Metrics (NPS, CSAT, CES)
            7. Open-Ended Insights
            8. Competition Comparison
            9. Future Needs Assessment
            10. Segmentation Variables
            
            Ensure statistical validity and avoid bias.""",
            "expected_output": """Complete survey package with:
            - Question bank with logic flows
            - Response scales and options
            - Analysis plan
            - Sample size calculations
            - Distribution strategy"""
        }
    
    @staticmethod
    def validate_research_completeness(research_artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Validate research artifacts for completeness and quality."""
        validation_results = {
            "is_complete": True,
            "missing_elements": [],
            "quality_issues": [],
            "methodological_gaps": [],
            "bias_risks": []
        }
        
        # Required research elements
        required_elements = [
            "user_personas",
            "journey_maps",
            "user_needs",
            "pain_points",
            "research_methodology",
            "sample_size",
            "key_insights",
            "recommendations"
        ]
        
        for element in required_elements:
            if element not in research_artifacts or not research_artifacts[element]:
                validation_results["missing_elements"].append(element)
                validation_results["is_complete"] = False
        
        # Check for quality issues
        if research_artifacts.get("sample_size", 0) < 5:
            validation_results["quality_issues"].append("Sample size too small for reliable insights")
        
        if not research_artifacts.get("research_methodology"):
            validation_results["methodological_gaps"].append("No clear research methodology described")
        
        # Check for bias risks
        if not research_artifacts.get("diverse_participants"):
            validation_results["bias_risks"].append("Lack of participant diversity may introduce bias")
        
        if research_artifacts.get("leading_questions"):
            validation_results["bias_risks"].append("Survey contains leading questions")
        
        # Calculate research quality score
        total_issues = sum([
            len(validation_results["missing_elements"]),
            len(validation_results["quality_issues"]),
            len(validation_results["methodological_gaps"]),
            len(validation_results["bias_risks"])
        ])
        
        validation_results["quality_score"] = max(0, 100 - (total_issues * 5))
        validation_results["recommendations"] = UserResearcherAgent._generate_research_recommendations(validation_results)
        
        return validation_results
    
    @staticmethod
    def _generate_research_recommendations(validation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if validation_results["missing_elements"]:
            recommendations.append(f"Complete missing research elements: {', '.join(validation_results['missing_elements'][:3])}")
        
        if validation_results["quality_issues"]:
            recommendations.append("Address quality concerns to ensure research validity")
        
        if validation_results["methodological_gaps"]:
            recommendations.append("Document research methodology for transparency and reproducibility")
        
        if validation_results["bias_risks"]:
            recommendations.append("Mitigate bias risks through diverse sampling and neutral questioning")
        
        if validation_results["quality_score"] < 80:
            recommendations.append("Consider additional research to strengthen findings")
        
        recommendations.append("Validate findings with stakeholders before finalizing")
        
        return recommendations