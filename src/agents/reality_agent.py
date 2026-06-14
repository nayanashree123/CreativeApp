"""
Reality Synthesis Agent - Synthesizes all analyzer outputs into comprehensive assessment.
"""

from src.agents.base_agent import BaseAgent
from src.core.models import RealityAgentOutput
from src.prompts.prompt_loader import PromptLoader
from src.utils.llm_client import LLMClient


class RealityAgent(BaseAgent):
    """
    Synthesizes insights from all analyzer agents into comprehensive assessment.
    
    Responsibilities:
    - Integrate insights from all 7 analyzer agents
    - Identify key enablers and blockers
    - Calculate overall feasibility score
    - Assess success probability
    - Provide synthesized assessment
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize Reality Synthesis Agent.
        
        Args:
            llm_client: LLM client for API calls
        """
        loader = PromptLoader()
        system_prompt = loader.get_system_prompt("reality")
        super().__init__(
            name=loader.get_agent_name("reality"),
            llm_client=llm_client,
            system_prompt=system_prompt,
            output_model=RealityAgentOutput,
            timeout_seconds=60
        )
