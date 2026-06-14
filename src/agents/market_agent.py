"""
Market Analyst Agent - Analyzes market opportunity and competitive landscape.
"""

from src.agents.base_agent import BaseAgent
from src.core.models import MarketAgentOutput
from src.prompts.prompt_loader import PromptLoader
from src.utils.llm_client import LLMClient


class MarketAgent(BaseAgent):
    """
    Analyzes market opportunity, competition, and viability.
    
    Responsibilities:
    - Estimate total addressable market (TAM) size
    - Analyze competitive landscape
    - Identify market gaps and unmet needs
    - Assess entry barriers
    - Calculate opportunity score
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize Market Analyst Agent.
        
        Args:
            llm_client: LLM client for API calls
        """
        loader = PromptLoader()
        system_prompt = loader.get_system_prompt("market")
        super().__init__(
            name=loader.get_agent_name("market"),
            llm_client=llm_client,
            system_prompt=system_prompt,
            output_model=MarketAgentOutput,
            timeout_seconds=60
        )
