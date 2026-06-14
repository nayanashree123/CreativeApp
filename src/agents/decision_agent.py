"""
Decision Making Agent - Makes final recommendation on dream pursuit.
"""

from src.agents.base_agent import BaseAgent
from src.core.models import DecisionAgentOutput
from src.prompts.prompt_loader import PromptLoader
from src.utils.llm_client import LLMClient


class DecisionAgent(BaseAgent):
    """
    Makes final go/no-go decision on dream pursuit.
    
    Responsibilities:
    - Make final recommendation (PURSUE|PIVOT|DELAY|REJECT)
    - Provide confidence in recommendation
    - Identify key decision factors
    - Suggest alternative recommendations
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize Decision Making Agent.
        
        Args:
            llm_client: LLM client for API calls
        """
        loader = PromptLoader()
        system_prompt = loader.get_system_prompt("decision")
        super().__init__(
            name=loader.get_agent_name("decision"),
            llm_client=llm_client,
            system_prompt=system_prompt,
            output_model=DecisionAgentOutput,
            timeout_seconds=60
        )
