"""
Live integration test: Test Copilot client with dream agent
"""

import sys
import asyncio
import logging

sys.path.insert(0, '/workspaces/CreativeApp')

from src.agents.dream_agent import DreamUnderstandingAgent
from src.utils.llm_client import initialize_llm_client, get_llm_client
from src.core.models import DreamProfile

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_copilot_integration():
    """Test Copilot client with a real agent call."""
    
    print("\n" + "="*70)
    print("LIVE INTEGRATION TEST: Copilot Client + Dream Agent")
    print("="*70 + "\n")
    
    try:
        # Initialize Copilot client globally
        print("1️⃣ Initializing Copilot LLM client...")
        llm_client = initialize_llm_client(provider="copilot")
        print(f"   ✅ Copilot client initialized (model: {llm_client.model})\n")
        
        # Create agent
        print("2️⃣ Creating DreamUnderstandingAgent...")
        agent = DreamUnderstandingAgent(llm_client)
        print(f"   ✅ Agent created: {agent.name}\n")
        
        # Create test dream profile
        print("3️⃣ Creating test dream profile...")
        dream = DreamProfile(
            dream_text="I want to build an AI-powered productivity app that helps remote teams collaborate better with real-time AI suggestions",
            idea_name="TeamFlow AI",
            target_market="Remote teams at startups (5-50 people)",
            budget_range="$50K-$200K",
            timeline="6 months",
            assumptions=["Teams will pay $50-100/month", "AI can improve productivity by 20%"]
        )
        print(f"   ✅ Dream: {dream.idea_name}\n")
        
        # Execute agent
        print("4️⃣ Calling Dream Understanding Agent via Copilot...")
        print("   (This will make a real Copilot API call...)\n")
        
        result = await agent.execute(dream)
        
        # Display results
        print("5️⃣ Agent Response:")
        print("-" * 70)
        print(f"   Result type: {type(result).__name__}")
        print(f"   Result: {result}\n")
        
        # Check if we got a valid output (data should be present)
        if hasattr(result, 'data') and result.data:
            print("   ✅ COPILOT INTEGRATION WORKING!")
            success = True
        else:
            print("   ⚠️ Call succeeded but returned fallback/no data")
            success = False
        
        print("="*70)
        return success
        
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_copilot_integration())
    sys.exit(0 if success else 1)
