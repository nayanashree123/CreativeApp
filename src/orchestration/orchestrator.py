"""
Dream Analysis Orchestrator - Coordinates all agents for end-to-end analysis.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Optional

from src.core.models import DreamProfile, DreamAnalysisResult
from src.core.config import get_settings
from src.utils.llm_client import LLMClient
from src.rag import initialize_knowledge_base

# Import all agents
from src.agents.dream_agent import DreamUnderstandingAgent
from src.agents.market_agent import MarketAgent
from src.agents.resource_agent import ResourceAgent
from src.agents.risk_agent import RiskAgent
from src.agents.technology_agent import TechnologyAgent
from src.agents.innovation_agent import InnovationAgent
from src.agents.execution_agent import ExecutionAgent
from src.agents.reality_agent import RealityAgent
from src.agents.decision_agent import DecisionAgent
from src.agents.roadmap_agent import RoadmapAgent


logger = logging.getLogger(__name__)


class DreamAnalysisOrchestrator:
    """
    Orchestrates the complete dream-to-reality analysis pipeline.
    
    Runs all 10 agents in parallel, aggregates results, and produces
    a comprehensive analysis with decision and roadmap.
    """
    
    def __init__(self, use_rag: bool = True):
        """
        Initialize the orchestrator.
        
        Args:
            use_rag: Whether to use RAG retriever for agent context
        """
        self.settings = get_settings()
        self.llm_client = LLMClient(self.settings)
        
        # Initialize RAG if requested
        self.retriever = None
        if use_rag:
            try:
                self.retriever = initialize_knowledge_base(
                    knowledge_dir="knowledge",
                    rebuild=False
                )
                logger.info("✓ RAG retriever initialized for orchestrator")
            except Exception as e:
                logger.warning(f"Failed to initialize RAG: {e}. Continuing without RAG.")
        
        # Initialize all agents
        self._initialize_agents()
        
        logger.info("✓ DreamAnalysisOrchestrator initialized")
    
    def _initialize_agents(self) -> None:
        """Initialize all 10 agents."""
        self.agents = {
            "dream_understanding": DreamUnderstandingAgent(self.llm_client),
            "market_analysis": MarketAgent(self.llm_client),
            "resource_analysis": ResourceAgent(self.llm_client),
            "risk_assessment": RiskAgent(self.llm_client),
            "technology_assessment": TechnologyAgent(self.llm_client),
            "innovation_assessment": InnovationAgent(self.llm_client),
            "execution_plan": ExecutionAgent(self.llm_client),
            "reality_synthesis": RealityAgent(self.llm_client),
            "final_decision": DecisionAgent(self.llm_client),
            "roadmap": RoadmapAgent(self.llm_client),
        }
        
        # Inject retriever into all agents if available
        if self.retriever:
            for agent in self.agents.values():
                agent.retriever = self.retriever
            logger.debug("Injected RAG retriever into all agents")
    
    async def analyze(
        self,
        dream_text: str,
        idea_name: Optional[str] = None,
        target_market: Optional[str] = None,
        budget_range: Optional[str] = None,
        timeline: Optional[str] = None
    ) -> DreamAnalysisResult:
        """
        Analyze a dream through all agents and produce comprehensive result.
        
        Args:
            dream_text: Raw dream description from user
            idea_name: Optional structured idea name
            target_market: Optional target market description
            budget_range: Optional budget estimate
            timeline: Optional timeline
            
        Returns:
            DreamAnalysisResult with all agent outputs and final decision
        """
        analysis_id = str(uuid.uuid4())[:8]
        start_time = datetime.now()
        
        logger.info(f"[{analysis_id}] Starting dream analysis")
        logger.debug(f"[{analysis_id}] Dream: {dream_text[:100]}...")
        
        try:
            # Create dream profile
            dream = DreamProfile(
                dream_text=dream_text,
                idea_name=idea_name,
                target_market=target_market,
                budget_range=budget_range,
                timeline=timeline
            )
            
            # Run all agents in parallel for maximum efficiency
            logger.info(f"[{analysis_id}] Running all 10 agents in parallel...")
            
            results = await asyncio.gather(
                self.agents["dream_understanding"].execute(dream),
                self.agents["market_analysis"].execute(dream),
                self.agents["resource_analysis"].execute(dream),
                self.agents["risk_assessment"].execute(dream),
                self.agents["technology_assessment"].execute(dream),
                self.agents["innovation_assessment"].execute(dream),
                self.agents["execution_plan"].execute(dream),
                self.agents["reality_synthesis"].execute(dream),
                self.agents["final_decision"].execute(dream),
                self.agents["roadmap"].execute(dream),
                return_exceptions=True
            )
            
            # Check for exceptions
            for i, result in enumerate(results):
                agent_names = list(self.agents.keys())
                if isinstance(result, Exception):
                    logger.error(f"[{analysis_id}] Agent {agent_names[i]} failed: {result}")
                    raise result
            
            # Unpack results
            (
                dream_understanding,
                market_analysis,
                resource_analysis,
                risk_assessment,
                technology_assessment,
                innovation_assessment,
                execution_plan,
                reality_synthesis,
                final_decision,
                roadmap
            ) = results
            
            # Calculate total metrics
            total_execution_time_ms = sum(
                getattr(r, 'execution_time_ms', 0) for r in results
            )
            total_tokens_used = sum(
                getattr(r, 'tokens_used', 0) for r in results
            )
            
            completion_time = datetime.now()
            
            # Create final result
            analysis_result = DreamAnalysisResult(
                dream_id=analysis_id,
                original_dream=dream,
                dream_understanding=dream_understanding,
                market_analysis=market_analysis,
                resource_analysis=resource_analysis,
                risk_assessment=risk_assessment,
                technology_assessment=technology_assessment,
                innovation_assessment=innovation_assessment,
                execution_plan=execution_plan,
                reality_synthesis=reality_synthesis,
                final_decision=final_decision,
                roadmap=roadmap,
                analysis_started_at=start_time,
                analysis_completed_at=completion_time,
                total_execution_time_ms=total_execution_time_ms,
                total_tokens_used=total_tokens_used
            )
            
            logger.info(
                f"[{analysis_id}] ✓ Analysis complete | "
                f"Feasibility: {analysis_result.overall_feasibility:.0%} | "
                f"Decision: {final_decision.recommendation} | "
                f"Time: {total_execution_time_ms:.0f}ms | "
                f"Tokens: {total_tokens_used}"
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"[{analysis_id}] Analysis failed: {e}", exc_info=True)
            raise
    
    def get_agent_metrics(self) -> dict:
        """
        Get execution metrics for all agents.
        
        Returns:
            Dictionary with agent names and their metrics
        """
        metrics = {}
        for name, agent in self.agents.items():
            metrics[name] = {
                "executions": agent.execution_count,
                "successes": agent.success_count,
                "failures": agent.failure_count,
                "avg_execution_time_ms": (
                    agent.total_execution_time_ms / agent.execution_count
                    if agent.execution_count > 0 else 0
                ),
                "total_tokens": agent.total_tokens_used
            }
        return metrics


# Singleton instance for convenience
_orchestrator_instance: Optional[DreamAnalysisOrchestrator] = None


def get_orchestrator(use_rag: bool = True) -> DreamAnalysisOrchestrator:
    """
    Get or create the orchestrator singleton.
    
    Args:
        use_rag: Whether to use RAG retriever
        
    Returns:
        DreamAnalysisOrchestrator instance
    """
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = DreamAnalysisOrchestrator(use_rag=use_rag)
    return _orchestrator_instance


def reset_orchestrator() -> None:
    """Reset the orchestrator singleton."""
    global _orchestrator_instance
    _orchestrator_instance = None
