"""
Test suite for Phase 3: Analyzer Agents
Tests DreamUnderstandingAgent, MarketAgent, ResourceAgent, TechnologyAgent, InnovationAgent
"""

import sys
import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock

# Setup path
sys.path.insert(0, '/workspaces/AI_projects/CreativeApp')

from src.agents.dream_agent import DreamUnderstandingAgent
from src.agents.market_agent import MarketAgent
from src.agents.resource_agent import ResourceAgent
from src.agents.technology_agent import TechnologyAgent
from src.agents.innovation_agent import InnovationAgent
from src.core.models import (
    DreamProfile,
    DreamUnderstandingOutput,
    MarketAgentOutput,
    ResourceAgentOutput,
    TechnologyAgentOutput,
    InnovationAgentOutput
)
from src.prompts.prompt_loader import PromptLoader

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_dream_agent_initialization():
    """Test DreamUnderstandingAgent initializes correctly."""
    llm_client = MagicMock()
    agent = DreamUnderstandingAgent(llm_client)
    
    assert agent.name == "Dream Understanding Agent"
    assert agent.output_model == DreamUnderstandingOutput
    assert agent.llm_client == llm_client
    assert agent.system_prompt is not None
    print("✅ TEST 1: DreamUnderstandingAgent initialization working")


def test_market_agent_initialization():
    """Test MarketAgent initializes correctly."""
    llm_client = MagicMock()
    agent = MarketAgent(llm_client)
    
    assert agent.name == "Market Analyst Agent"
    assert agent.output_model == MarketAgentOutput
    assert agent.llm_client == llm_client
    assert agent.system_prompt is not None
    print("✅ TEST 2: MarketAgent initialization working")


def test_resource_agent_initialization():
    """Test ResourceAgent initializes correctly."""
    llm_client = MagicMock()
    agent = ResourceAgent(llm_client)
    
    assert agent.name == "Resource Analyst Agent"
    assert agent.output_model == ResourceAgentOutput
    assert agent.llm_client == llm_client
    assert agent.system_prompt is not None
    print("✅ TEST 3: ResourceAgent initialization working")


def test_technology_agent_initialization():
    """Test TechnologyAgent initializes correctly."""
    llm_client = MagicMock()
    agent = TechnologyAgent(llm_client)
    
    assert agent.name == "Technology Architecture Agent"
    assert agent.output_model == TechnologyAgentOutput
    assert agent.llm_client == llm_client
    assert agent.system_prompt is not None
    print("✅ TEST 4: TechnologyAgent initialization working")


def test_innovation_agent_initialization():
    """Test InnovationAgent initializes correctly."""
    llm_client = MagicMock()
    agent = InnovationAgent(llm_client)
    
    assert agent.name == "Innovation & Differentiation Agent"
    assert agent.output_model == InnovationAgentOutput
    assert agent.llm_client == llm_client
    assert agent.system_prompt is not None
    print("✅ TEST 5: InnovationAgent initialization working")


def test_all_agents_have_system_prompts():
    """Test that all agents loaded their system prompts correctly."""
    loader = PromptLoader()
    agents = loader.list_agents()
    
    # Check that we have the 5 analyzer agents in the system prompts
    analyzer_agents = ["dream_understanding", "market", "resource", "technology", "innovation"]
    for agent_key in analyzer_agents:
        prompt = loader.get_system_prompt(agent_key)
        assert prompt is not None
        assert len(prompt) > 100  # Prompts should be substantial
    
    print("✅ TEST 6: All analyzer agent system prompts loaded")


def test_input_formatting():
    """Test that agents can format input correctly."""
    llm_client = MagicMock()
    agent = DreamUnderstandingAgent(llm_client)
    
    dream = DreamProfile(
        dream_text="I want to build an AI platform for productivity",
        idea_name="ProductivityAI",
        target_market="Professionals",
        budget_range="$100K-$500K",
        timeline="6 months"
    )
    
    formatted_input = agent._format_input(dream)
    
    assert "ProductivityAI" in formatted_input
    assert "Professionals" in formatted_input
    assert "$100K-$500K" in formatted_input
    assert "6 months" in formatted_input
    print("✅ TEST 7: Input formatting working correctly")


def run_all_tests():
    """Run all tests."""
    try:
        print("\n" + "="*60)
        print("PHASE 3: ANALYZER AGENTS TEST SUITE")
        print("="*60 + "\n")
        
        test_dream_agent_initialization()
        test_market_agent_initialization()
        test_resource_agent_initialization()
        test_technology_agent_initialization()
        test_innovation_agent_initialization()
        test_all_agents_have_system_prompts()
        test_input_formatting()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED ✓ (7/7 tests)")
        print("="*60)
        print("\nPhase 3 Complete: 5 Analyzer Agents implemented and verified")
        print("Ready for Phase 4: RAG System Implementation")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
