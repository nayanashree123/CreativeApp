"""
End-to-end test for all analyzer agents with RAG context integration.
Tests that agents properly use retrieved knowledge base context.
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

from src.core.models import DreamProfile
from src.core.config import get_settings
from src.utils.llm_client import LLMClient
from src.rag import initialize_knowledge_base
from src.agents.dream_agent import DreamUnderstandingAgent
from src.agents.market_agent import MarketAgent
from src.agents.resource_agent import ResourceAgent
from src.agents.technology_agent import TechnologyAgent
from src.agents.innovation_agent import InnovationAgent


def create_test_dream() -> DreamProfile:
    """Create a sample dream for testing."""
    return DreamProfile(
        dream_text="I want to build an AI-powered customer support platform that uses NLP to handle 80% of common support tickets automatically.",
        idea_name="SupportAI",
        target_market="B2B SaaS companies with 100+ employees",
        budget_range="$150,000 - $300,000",
        timeline="6 months MVP",
        assumptions=[
            "Market demand for AI support solutions is high",
            "We can achieve 80% accuracy with fine-tuned models",
            "Customers will integrate via API"
        ],
        constraints=[
            "Limited initial team (2 founders)",
            "Must be profitable within 18 months"
        ]
    )


async def test_agent_with_rag(
    agent,
    dream: DreamProfile,
    test_name: str
) -> bool:
    """
    Test a single agent with RAG context.
    
    Args:
        agent: The agent to test
        dream: Test dream profile
        test_name: Name for logging
        
    Returns:
        True if test passed, False otherwise
    """
    try:
        print(f"\n[TEST] {test_name}")
        print("-" * 70)
        
        # Execute agent (should auto-retrieve RAG context if retriever is set)
        output = await agent.execute(dream)
        
        # Verify output
        if output is None:
            print(f"✗ Agent returned None")
            return False
        
        if not hasattr(output, 'agent_name'):
            print(f"✗ Output missing agent_name")
            return False
        
        print(f"✓ {output.agent_name} executed successfully")
        print(f"  Execution Time: {output.execution_time_ms:.0f}ms")
        print(f"  Tokens Used: {output.tokens_used}")
        
        # Show some output details based on agent type
        if hasattr(output, 'clarity_score'):
            print(f"  Clarity Score: {output.clarity_score}")
        elif hasattr(output, 'feasibility_score'):
            print(f"  Feasibility Score: {output.feasibility_score}")
        elif hasattr(output, 'capital_required'):
            print(f"  Capital Required: {output.capital_required}")
        elif hasattr(output, 'complexity_score'):
            print(f"  Complexity Score: {output.complexity_score}")
        elif hasattr(output, 'innovation_score'):
            print(f"  Innovation Score: {output.innovation_score}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        logger.exception(f"Agent execution failed: {e}")
        return False


async def main():
    """Run all agent tests with RAG context."""
    
    print("\n" + "=" * 70)
    print("🤖 AGENTS WITH RAG CONTEXT - END-TO-END TEST")
    print("=" * 70)
    
    # Initialize settings and LLM client
    settings = get_settings()
    llm_client = LLMClient(settings)
    
    # Initialize RAG retriever
    print("\n[SETUP] Initializing RAG retriever...")
    try:
        retriever = initialize_knowledge_base(
            knowledge_dir="knowledge",
            rebuild=False
        )
        print(f"✓ RAG initialized with {retriever.index.ntotal} documents")
    except Exception as e:
        print(f"✗ Failed to initialize RAG: {e}")
        logger.exception("RAG initialization failed")
        return False
    
    # Initialize agents WITH retriever
    print("\n[SETUP] Initializing agents with RAG retriever...")
    agents = [
        DreamUnderstandingAgent(llm_client),
        MarketAgent(llm_client),
        ResourceAgent(llm_client),
        TechnologyAgent(llm_client),
        InnovationAgent(llm_client)
    ]
    
    # Inject retriever into each agent
    for agent in agents:
        agent.retriever = retriever
        print(f"  ✓ {agent.name} - retriever injected")
    
    # Create test dream
    dream = create_test_dream()
    print(f"\n[SETUP] Using test dream: '{dream.idea_name}'")
    
    # Run tests for each agent
    print("\n[TESTS] Running agent tests with RAG context...")
    results = []
    
    test_cases = [
        (agents[0], "Dream Understanding Agent with RAG"),
        (agents[1], "Market Analyst Agent with RAG"),
        (agents[2], "Resource Analyst Agent with RAG"),
        (agents[3], "Technology Architecture Agent with RAG"),
        (agents[4], "Innovation & Differentiation Agent with RAG"),
    ]
    
    for agent, test_name in test_cases:
        result = await test_agent_with_rag(agent, dream, test_name)
        results.append((agent.name, result))
    
    # Summary
    print("\n" + "=" * 70)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("\nAgent Integration Status:")
        for agent_name, _ in results:
            print(f"  ✓ {agent_name} - Successfully uses RAG context")
        return True
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total} passed)")
        print("\nResults:")
        for agent_name, result in results:
            status = "✓" if result else "✗"
            print(f"  {status} {agent_name}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
