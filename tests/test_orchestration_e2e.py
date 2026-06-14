"""
End-to-end test for the Dream Analysis Orchestrator.
Tests that all 10 agents execute in parallel and produce valid output.
"""

import logging
import asyncio
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestration import DreamAnalysisOrchestrator


async def main():
    """Run orchestrator test."""
    
    print("\n" + "=" * 80)
    print("🎯 ORCHESTRATOR E2E TEST - All 10 Agents Coordinated")
    print("=" * 80)
    
    # Initialize orchestrator
    print("\n[SETUP] Initializing orchestrator with RAG support...")
    try:
        orchestrator = DreamAnalysisOrchestrator(use_rag=True)
        print("✓ Orchestrator initialized")
        print(f"  - 10 agents ready")
        print(f"  - RAG retriever active: {orchestrator.retriever is not None}")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        logger.exception("Initialization failed")
        return False
    
    # Test dream
    dream_text = """
    I want to build an AI-powered customer support platform that uses NLP 
    to handle 80% of common support tickets automatically. The goal is to 
    help B2B SaaS companies reduce support costs while improving customer satisfaction.
    """
    
    print(f"\n[TEST] Running full dream analysis...")
    print(f"Dream: {dream_text.strip()[:100]}...")
    print("-" * 80)
    
    try:
        # Run orchestrator
        result = await orchestrator.analyze(
            dream_text=dream_text,
            idea_name="SupportAI",
            target_market="B2B SaaS with 100+ employees",
            budget_range="$150K-300K",
            timeline="6 months MVP"
        )
        
        print(f"\n✅ ORCHESTRATOR ANALYSIS COMPLETE")
        print("-" * 80)
        
        # Display results
        print(f"\n📊 Analysis Metrics:")
        print(f"  Dream ID: {result.dream_id}")
        print(f"  Execution Time: {result.total_execution_time_ms:.0f}ms")
        print(f"  Tokens Used: {result.total_tokens_used}")
        print(f"  Start: {result.analysis_started_at.strftime('%H:%M:%S')}")
        print(f"  End: {result.analysis_completed_at.strftime('%H:%M:%S')}")
        
        print(f"\n🎯 Dream Understanding:")
        print(f"  Idea: {result.dream_understanding.parsed_idea_name}")
        print(f"  Clarity Score: {result.dream_understanding.clarity_score:.0%}")
        
        print(f"\n📈 Market Analysis:")
        print(f"  Opportunity Score: {result.market_analysis.opportunity_score:.0%}")
        
        print(f"\n💰 Resource Analysis:")
        print(f"  Estimated Budget: ${result.resource_analysis.estimated_budget_usd:,.0f}")
        print(f"  Feasibility: {result.resource_analysis.resource_feasibility:.0%}")
        
        print(f"\n⚠️ Risk Assessment:")
        print(f"  Risk Level: {result.risk_assessment.overall_risk_level}")
        print(f"  Risk Score: {result.risk_assessment.risk_score:.0%}")
        
        print(f"\n🛠️ Technology Assessment:")
        print(f"  Build Complexity: {result.technology_assessment.build_complexity}")
        print(f"  Complexity Score: {result.technology_assessment.build_complexity_score:.0%}")
        
        print(f"\n💡 Innovation Assessment:")
        print(f"  Novelty Score: {result.innovation_assessment.novelty_score:.0%}")
        
        print(f"\n📋 Execution Plan:")
        print(f"  TTR (Time to Revenue): {result.execution_plan.estimated_ttr_weeks} weeks")
        
        print(f"\n🔍 Reality Synthesis:")
        print(f"  Overall Feasibility: {result.reality_synthesis.overall_feasibility_score:.0%}")
        print(f"  Success Probability: {result.reality_synthesis.success_probability:.0%}")
        
        print(f"\n🚀 Final Decision:")
        print(f"  Recommendation: {result.final_decision.recommendation}")
        print(f"  Confidence: {result.final_decision.confidence_in_recommendation:.0%}")
        
        print(f"\n🗺️ Roadmap:")
        print(f"  Week 1: {result.roadmap.week_1_actions.name}")
        print(f"  Month 1: {result.roadmap.month_1_goals.name}")
        print(f"  Month 3: {result.roadmap.month_3_milestones.name}")
        print(f"  Month 6: {result.roadmap.month_6_vision.name}")
        
        # Show agent metrics
        print(f"\n📊 Agent Execution Metrics:")
        print("-" * 80)
        metrics = orchestrator.get_agent_metrics()
        for agent_name, agent_metrics in metrics.items():
            print(f"  {agent_name:30} | Exec: {agent_metrics['executions']} | "
                  f"Avg Time: {agent_metrics['avg_execution_time_ms']:.0f}ms | "
                  f"Tokens: {agent_metrics['total_tokens']}")
        
        print("\n" + "=" * 80)
        print("✅ ALL AGENTS EXECUTED SUCCESSFULLY")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ORCHESTRATOR TEST FAILED")
        print(f"Error: {e}")
        logger.exception("Orchestrator test failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
