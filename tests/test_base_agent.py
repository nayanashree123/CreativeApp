"""
Test module for Base Agent framework.
Demonstrates base agent usage and validates core functionality.
"""

import asyncio
import json
from typing import Dict, Any

from src.agents.base_agent import BaseAgent
from src.core.models import DreamProfile, MarketAgentOutput, AgentOutput
from src.utils.llm_client import LLMClient
from src.prompts.prompt_loader import PromptLoader


class MockMarketAgent(BaseAgent):
    """
    Mock Market Agent for testing.
    Simulates market analysis without calling LLM.
    """
    
    async def execute(
        self,
        dream: DreamProfile,
        rag_context: str = None,
        additional_context: Dict[str, Any] = None
    ) -> AgentOutput:
        """
        Mock execution that returns simulated market analysis.
        """
        self.execution_count += 1
        
        # Simulate a market analysis response
        mock_response = {
            "agent_name": "Market Analyst",
            "confidence": 0.75,
            "reasoning": "Market analysis based on target: " + (dream.target_market or "General market"),
            "metadata": {"analysis_type": "mock"},
            "execution_time_ms": 100,
            "tokens_used": 500,
            "market_size_estimate": "$5B+ TAM with 20% annual growth",
            "target_demographics": "Professionals aged 25-40, tech-savvy, willing to pay for solutions",
            "competitive_landscape": "5-7 direct competitors, fragmented market",
            "opportunity_score": 0.72,
            "market_gaps": [
                "Lack of AI-powered personalization",
                "Poor mobile experience in existing solutions",
                "Underserved SMB segment"
            ],
            "entry_barriers": [
                "Network effects",
                "Customer switching costs",
                "Data moat"
            ]
        }
        
        try:
            output = MarketAgentOutput(**mock_response)
            self.success_count += 1
            return output
        except Exception as e:
            self.failure_count += 1
            raise


async def test_base_agent_framework():
    """
    Comprehensive test of base agent framework.
    """
    print("\n" + "="*60)
    print("TESTING BASE AGENT FRAMEWORK - PHASE 2")
    print("="*60)
    
    # Test 1: Prompt Loader
    print("\n[TEST 1] Prompt Loader")
    print("-" * 40)
    try:
        loader = PromptLoader()
        agents = loader.list_agents()
        print(f"✓ Loaded {len(agents)} agent prompts")
        print(f"  Agents: {', '.join(agents.keys())}")
        
        # Test specific prompt
        market_prompt = loader.get_prompt("market")
        print(f"✓ Market Agent Prompt loaded")
        print(f"  Name: {market_prompt['name']}")
        print(f"  System prompt length: {len(market_prompt['system_prompt'])} chars")
    except Exception as e:
        print(f"✗ Prompt Loader test failed: {e}")
        return False
    
    # Test 2: Base Agent Class Structure
    print("\n[TEST 2] Base Agent Class Structure")
    print("-" * 40)
    try:
        # Create a mock LLM client
        mock_llm = LLMClient(api_key="sk-test-key")
        
        # Create mock agent
        market_agent = MockMarketAgent(
            name="Market Analyst",
            llm_client=mock_llm,
            system_prompt="Test prompt",
            output_model=MarketAgentOutput
        )
        
        print(f"✓ Mock Market Agent created")
        print(f"  Name: {market_agent.name}")
        print(f"  Output model: {market_agent.output_model.__name__}")
        print(f"  Timeout: {market_agent.timeout_seconds}s")
    except Exception as e:
        print(f"✗ Agent creation failed: {e}")
        return False
    
    # Test 3: Agent Execution (Mock)
    print("\n[TEST 3] Agent Execution (Mock)")
    print("-" * 40)
    try:
        dream = DreamProfile(
            dream_text="I want to build an AI productivity platform",
            idea_name="ProductivityAI",
            target_market="Professionals and students",
            budget_range="$100K-500K",
            timeline="6 months"
        )
        
        print(f"✓ Test dream created: {dream.idea_name}")
        
        # Execute mock agent
        result = await market_agent.execute(dream)
        
        print(f"✓ Agent execution successful")
        print(f"  Result type: {type(result).__name__}")
        print(f"  Agent name: {result.agent_name}")
        print(f"  Confidence: {result.confidence}")
        print(f"  Market opportunity score: {result.opportunity_score}")
        print(f"  Execution time: {result.execution_time_ms:.0f}ms")
    except Exception as e:
        print(f"✗ Agent execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Input Formatting
    print("\n[TEST 4] Input Formatting & Context")
    print("-" * 40)
    try:
        rag_context = "Similar success: ProductivitySaaS achieved 50K users in 6 months\nKey factor: Freemium model"
        additional_context = {"market_segment": "B2B SaaS", "gpt_version": "GPT-4o"}
        
        formatted_input = market_agent._format_input(
            dream,
            rag_context,
            additional_context
        )
        
        print(f"✓ Input formatted successfully")
        print(f"  Formatted input length: {len(formatted_input)} chars")
        print(f"  Contains dream text: {'ProductivityAI' in formatted_input}")
        print(f"  Contains RAG context: {'ProductivitySaaS' in formatted_input}")
        print(f"  Contains additional context: {'B2B SaaS' in formatted_input}")
    except Exception as e:
        print(f"✗ Input formatting failed: {e}")
        return False
    
    # Test 5: Agent Metrics
    print("\n[TEST 5] Agent Metrics Tracking")
    print("-" * 40)
    try:
        metrics = market_agent.get_metrics()
        print(f"✓ Metrics retrieved")
        print(f"  Execution count: {metrics['execution_count']}")
        print(f"  Success count: {metrics['success_count']}")
        print(f"  Success rate: {metrics['success_rate']}")
        print(f"  Total tokens: {metrics['total_tokens_used']}")
        
        # Reset and verify
        market_agent.reset_metrics()
        metrics = market_agent.get_metrics()
        print(f"✓ Metrics reset")
        print(f"  Execution count after reset: {metrics['execution_count']}")
    except Exception as e:
        print(f"✗ Metrics test failed: {e}")
        return False
    
    # Test 6: Response Parsing
    print("\n[TEST 6] Response Parsing & Fallback")
    print("-" * 40)
    try:
        # Valid JSON
        valid_json = '{"key": "value", "number": 42}'
        parsed = market_agent._parse_response(valid_json)
        print(f"✓ Valid JSON parsed: {parsed}")
        
        # JSON embedded in text
        embedded_json = "Analysis: {\"key\": \"value\"} is the result"
        parsed = market_agent._parse_response(embedded_json)
        print(f"✓ Embedded JSON extracted: {parsed}")
        
        # Fallback case
        invalid = "This is just text without JSON"
        parsed = market_agent._parse_response(invalid)
        print(f"✓ Fallback applied: {parsed}")
    except Exception as e:
        print(f"✗ Response parsing failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✓")
    print("="*60)
    return True


async def main():
    """Run all tests."""
    success = await test_base_agent_framework()
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
