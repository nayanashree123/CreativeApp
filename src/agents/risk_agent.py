"""
Risk Assessment Agent - Identifies and evaluates risks across multiple dimensions.
"""

from src.agents.base_agent import BaseAgent
from src.core.models import RiskAgentOutput
from src.prompts.prompt_loader import PromptLoader
from src.utils.llm_client import LLMClient


class RiskAgent(BaseAgent):
    """
    Assesses risks across technical, market, execution, business, and regulatory dimensions.
    
    Responsibilities:
    - Identify risks in multiple categories
    - Assess probability and impact for each risk
    - Propose mitigation strategies
    - Calculate overall risk score
    - Identify go/no-go decision factors
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize Risk Assessment Agent.
        
        Args:
            llm_client: LLM client for API calls
        """
        loader = PromptLoader()
        system_prompt = loader.get_system_prompt("risk")
        super().__init__(
            name=loader.get_agent_name("risk"),
            llm_client=llm_client,
            system_prompt=system_prompt,
            output_model=RiskAgentOutput,
            timeout_seconds=60
        )
