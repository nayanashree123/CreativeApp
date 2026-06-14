"""
Data models for the Dream-to-Reality AI system.
Uses Pydantic v2 for type validation and auto-serialization.
"""

from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Enums
# ============================================================================

class DecisionType(str, Enum):
    """Possible decision outcomes."""
    PURSUE = "PURSUE"
    PIVOT = "PIVOT"
    DELAY = "DELAY"
    REJECT = "REJECT"


class RiskCategory(str, Enum):
    """Risk assessment categories."""
    TECHNICAL = "technical"
    MARKET = "market"
    EXECUTION = "execution"
    BUSINESS = "business"
    REGULATORY = "regulatory"


# ============================================================================
# Input Models
# ============================================================================

class DreamProfile(BaseModel):
    """
    User's dream/business idea input.
    Parsed from natural language description.
    """
    model_config = ConfigDict(validate_assignment=True)
    
    dream_text: str = Field(..., description="Raw dream description from user")
    idea_name: Optional[str] = Field(default=None, description="Name of the business idea")
    description: Optional[str] = Field(default=None, description="Structured description")
    target_market: Optional[str] = Field(default=None, description="Target audience/market")
    budget_range: Optional[str] = Field(default=None, description="Estimated budget (e.g., '$10K-50K')")
    timeline: Optional[str] = Field(default=None, description="Desired launch timeline")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions about the idea")
    constraints: List[str] = Field(default_factory=list, description="Known constraints")
    created_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# Agent Output Models
# ============================================================================

class Metric(BaseModel):
    """A single metric with name and value."""
    name: str
    value: float
    unit: Optional[str] = None
    description: Optional[str] = None


class PatternMatch(BaseModel):
    """A matched pattern from the knowledge base."""
    pattern_id: str
    name: str
    description: str
    relevance_score: float = Field(ge=0, le=1)
    key_takeaways: List[str]


class AgentOutput(BaseModel):
    """
    Base class for all agent outputs.
    Every agent extends this model.
    """
    model_config = ConfigDict(validate_assignment=True)
    
    agent_name: str
    confidence: float = Field(ge=0, le=1, description="0-1 confidence in this output")
    reasoning: str = Field(description="Explanation of reasoning")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    execution_time_ms: float = Field(default=0, description="Time to execute agent")
    tokens_used: int = Field(default=0, description="Tokens used in API call")


class DreamUnderstandingOutput(AgentOutput):
    """Parsed and structured dream understanding."""
    
    parsed_idea_name: str
    parsed_description: str
    parsed_target_market: str
    parsed_assumptions: List[str]
    parsed_constraints: List[str]
    clarity_score: float = Field(ge=0, le=1)


class MarketAgentOutput(AgentOutput):
    """Market analysis from analyst agent."""
    
    market_size_estimate: str
    target_demographics: str
    competitive_landscape: str
    opportunity_score: float = Field(ge=0, le=1)
    market_gaps: List[str]
    entry_barriers: List[str]
    similar_successes: List[Any] = Field(default_factory=list, description="Similar successful companies/products (strings or PatternMatch objects)")


class ResourceAgentOutput(AgentOutput):
    """Resource requirements analysis."""
    
    team_size_estimate: int
    estimated_budget_usd: int
    budget_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="Breakdown: dev, marketing, operations, contingency"
    )
    required_skills: List[str]
    resource_feasibility: float = Field(ge=0, le=1)
    funding_suggestions: List[str]


class RiskAgentOutput(AgentOutput):
    """Risk assessment and mitigation strategies."""
    
    overall_risk_level: str  # low, medium, high, critical
    risk_score: float = Field(ge=0, le=1, description="Higher = riskier")
    risks_identified: List[Dict[str, Any]] = Field(
        description="List of {category, description, probability, impact, mitigation}"
    )
    risk_mitigation_strategies: Dict[RiskCategory, List[str]] = Field(default_factory=dict)
    go_no_go_factors: List[str]


class TechnologyAgentOutput(AgentOutput):
    """Technology stack and feasibility assessment."""
    
    recommended_tech_stack: List[str]
    architecture_approach: str
    build_complexity: str  # low, medium, high
    build_complexity_score: float = Field(ge=0, le=1)
    ai_requirements: str
    infrastructure_needs: str
    similar_tech_implementations: List[Any] = Field(default_factory=list, description="Similar tech implementations (strings or PatternMatch objects)")


class InnovationAgentOutput(AgentOutput):
    """Innovation and differentiation analysis."""
    
    novelty_score: float = Field(ge=0, le=1, description="How novel/innovative")
    unique_value_propositions: List[str]
    competitive_advantages: List[str]
    defensibility_assessment: str
    innovation_dimension: str


class ExecutionAgentOutput(AgentOutput):
    """Execution plan and project phases."""
    
    mvp_definition: str
    project_phases: List[Dict[str, Any]] = Field(
        description="List of {phase, duration, deliverables, resources}"
    )
    critical_path_items: List[str]
    success_metrics: List[str]
    estimated_ttr_weeks: int  # time to revenue


class RealityAgentOutput(AgentOutput):
    """Synthesizes all analyzer outputs into reality assessment."""
    
    overall_feasibility_score: float = Field(ge=0, le=1)
    synthesized_assessment: str
    key_enablers: List[str]
    key_blockers: List[str]
    success_probability: float = Field(ge=0, le=1)


class DecisionAgentOutput(AgentOutput):
    """Final decision and recommendation."""
    
    recommendation: DecisionType
    confidence_in_recommendation: float = Field(ge=0, le=1)
    key_decision_factors: List[str]
    key_actions: List[str] = Field(default_factory=list, description="Immediate actions to take")
    alternative_recommendations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Other possible recommendations with reasoning"
    )


class Phase(BaseModel):
    """A project phase with milestones and deliverables."""
    name: str
    duration_weeks: int
    milestones: List[str]
    deliverables: List[str]
    resources_needed: Union[str, Dict[str, Any]] = Field(description="Resources needed (string or dict with breakdown)")
    dependencies: List[str] = Field(default_factory=list)


class RoadmapAgentOutput(AgentOutput):
    """Detailed roadmap for execution."""
    
    week_1_actions: Phase
    month_1_goals: Phase
    month_3_milestones: Phase
    month_6_vision: Phase
    critical_success_factors: List[str]
    contingency_plans: List[str]


# ============================================================================
# Alternative Dream Models
# ============================================================================

class AlternativeDream(BaseModel):
    """Alternative version of the dream with different focus."""
    variant_name: str  # e.g., "Safer version", "Faster version"
    description: str
    key_changes: List[str]
    estimated_feasibility: float = Field(ge=0, le=1)
    trade_offs: List[str]


# ============================================================================
# Error/Fallback Models (defined before DreamAnalysisResult)
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error_code: str
    error_message: str
    agent_name: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    details: Dict[str, Any] = Field(default_factory=dict)


class FallbackAgentOutput(AgentOutput):
    """Fallback output when agent fails."""
    error: ErrorResponse
    fallback_reason: str


# ============================================================================
# Final Results Model
# ============================================================================

class DreamAnalysisResult(BaseModel):
    """
    Complete analysis result for a dream.
    Contains all agent outputs and final decision.
    Accepts both successful agent outputs and fallback outputs (when API calls fail).
    """
    model_config = ConfigDict(validate_assignment=True)
    
    dream_id: str = Field(description="Unique ID for this analysis")
    original_dream: DreamProfile
    
    # All agent outputs - Union types allow both successful and fallback outputs
    dream_understanding: Union[DreamUnderstandingOutput, FallbackAgentOutput]
    market_analysis: Union[MarketAgentOutput, FallbackAgentOutput]
    resource_analysis: Union[ResourceAgentOutput, FallbackAgentOutput]
    risk_assessment: Union[RiskAgentOutput, FallbackAgentOutput]
    technology_assessment: Union[TechnologyAgentOutput, FallbackAgentOutput]
    innovation_assessment: Union[InnovationAgentOutput, FallbackAgentOutput]
    execution_plan: Union[ExecutionAgentOutput, FallbackAgentOutput]
    reality_synthesis: Union[RealityAgentOutput, FallbackAgentOutput]
    final_decision: Union[DecisionAgentOutput, FallbackAgentOutput]
    roadmap: Union[RoadmapAgentOutput, FallbackAgentOutput]
    
    # Alternative ideas
    alternative_dreams: List[AlternativeDream] = Field(default_factory=list)
    
    # Metadata
    analysis_started_at: datetime
    analysis_completed_at: Optional[datetime] = None
    total_execution_time_ms: float = Field(default=0)
    total_tokens_used: int = Field(default=0)
    
    # Convenience field: overall feasibility
    @property
    def overall_feasibility(self) -> float:
        """Calculate overall feasibility from synthesis."""
        # Handle both success and fallback cases
        if isinstance(self.reality_synthesis, RealityAgentOutput):
            return self.reality_synthesis.overall_feasibility_score
        else:
            # Fallback case - return 0 for failed analysis
            return 0.0


# ============================================================================
# RAG Context Models
# ============================================================================

class KnowledgeDocument(BaseModel):
    """A document in the knowledge base."""
    doc_id: str
    title: str
    category: str  # success, failure, model, pattern, etc.
    content: str
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class RAGContext(BaseModel):
    """Context retrieved from RAG for an agent."""
    agent_name: str
    relevant_documents: List[KnowledgeDocument]
    similarity_scores: List[float]
    formatted_context: str = Field(description="Formatted string to inject into prompt")


if __name__ == "__main__":
    # Test model instantiation
    dream = DreamProfile(
        dream_text="I want to create an AI-powered platform for personal productivity",
        idea_name="ProductivityAI",
        target_market="Professionals and students"
    )
    print(f"Dream created: {dream.idea_name}")
    print(f"JSON: {dream.model_dump_json(indent=2)}")
