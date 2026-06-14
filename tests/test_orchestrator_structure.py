"""
Quick validation test for orchestrator structure and imports.
Doesn't require LLM API key.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 80)
print("🔍 ORCHESTRATOR STRUCTURE VALIDATION")
print("=" * 80)

# Test 1: Import all agents
print("\n[TEST 1] Importing all agent classes...")
try:
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
    print("✓ All 10 agent classes imported successfully")
except Exception as e:
    print(f"✗ Failed to import agents: {e}")
    sys.exit(1)

# Test 2: Import orchestrator
print("\n[TEST 2] Importing orchestrator...")
try:
    from src.orchestration import DreamAnalysisOrchestrator, get_orchestrator
    print("✓ Orchestrator imported successfully")
except Exception as e:
    print(f"✗ Failed to import orchestrator: {e}")
    sys.exit(1)

# Test 3: Import models
print("\n[TEST 3] Importing all output models...")
try:
    from src.core.models import (
        DreamUnderstandingOutput,
        MarketAgentOutput,
        ResourceAgentOutput,
        RiskAgentOutput,
        TechnologyAgentOutput,
        InnovationAgentOutput,
        ExecutionAgentOutput,
        RealityAgentOutput,
        DecisionAgentOutput,
        RoadmapAgentOutput,
        DreamAnalysisResult
    )
    print("✓ All 11 output models imported successfully")
except Exception as e:
    print(f"✗ Failed to import models: {e}")
    sys.exit(1)

# Test 4: Check agent names from prompt loader
print("\n[TEST 4] Validating agent names from prompt loader...")
try:
    from src.prompts.prompt_loader import PromptLoader
    loader = PromptLoader()
    
    agent_names = [
        "dream_understanding",
        "market",
        "resource",
        "risk",
        "technology",
        "innovation",
        "execution",
        "reality",
        "decision",
        "roadmap"
    ]
    
    for agent_key in agent_names:
        name = loader.get_agent_name(agent_key)
        if not name:
            raise ValueError(f"Agent name not found for {agent_key}")
        print(f"  ✓ {agent_key:20} → {name}")
    
    print("✓ All agent names validated")
except Exception as e:
    print(f"✗ Failed validation: {e}")
    sys.exit(1)

# Test 5: Validate orchestrator structure
print("\n[TEST 5] Validating orchestrator structure...")
try:
    from src.utils.llm_client import LLMClient
    from src.core.config import get_settings
    
    # Check methods exist
    required_methods = [
        'analyze',
        'get_agent_metrics',
        '_initialize_agents'
    ]
    
    for method in required_methods:
        if not hasattr(DreamAnalysisOrchestrator, method):
            raise AttributeError(f"Method {method} not found in orchestrator")
        print(f"  ✓ Method: {method}")
    
    print("✓ Orchestrator structure validated")
except Exception as e:
    print(f"✗ Failed structure validation: {e}")
    sys.exit(1)

# Test 6: Validate DreamAnalysisResult structure
print("\n[TEST 6] Validating DreamAnalysisResult output structure...")
try:
    required_fields = [
        'dream_id',
        'original_dream',
        'dream_understanding',
        'market_analysis',
        'resource_analysis',
        'risk_assessment',
        'technology_assessment',
        'innovation_assessment',
        'execution_plan',
        'reality_synthesis',
        'final_decision',
        'roadmap',
        'total_execution_time_ms',
        'total_tokens_used'
    ]
    
    model_fields = DreamAnalysisResult.model_fields
    for field in required_fields:
        if field not in model_fields:
            raise KeyError(f"Field {field} not found in DreamAnalysisResult")
        print(f"  ✓ Field: {field}")
    
    print("✓ DreamAnalysisResult structure validated")
except Exception as e:
    print(f"✗ Failed field validation: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 80)
print("✅ ORCHESTRATOR STRUCTURE VALIDATION COMPLETE")
print("=" * 80)
print("\n📋 Summary:")
print("  ✓ All 10 agent classes available")
print("  ✓ Orchestrator class functional")
print("  ✓ All 11 output models defined")
print("  ✓ Agent prompts configured")
print("  ✓ Orchestrator methods implemented")
print("  ✓ Output structure validated")
print("\n🚀 Ready for orchestration pipeline!")
