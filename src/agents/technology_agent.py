"""
Technology Architecture Agent - Recommends tech stack and assesses feasibility.
"""

from src.agents.base_agent import BaseAgent
from src.core.models import TechnologyAgentOutput
from src.prompts.prompt_loader import PromptLoader
from src.utils.llm_client import LLMClient


class TechnologyAgent(BaseAgent):
    """
    Recommends appropriate technology stack and assesses technical feasibility.
    
    Responsibilities:
    - Recommend technology stack
    - Describe architecture approach
    - Assess build complexity
    - Evaluate AI/ML requirements
    - Identify infrastructure needs
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize Technology Architecture Agent.
        
        Args:
            llm_client: LLM client for API calls
        """
        loader = PromptLoader()
        system_prompt = loader.get_system_prompt("technology")
        super().__init__(
            name=loader.get_agent_name("technology"),
            llm_client=llm_client,
            system_prompt=system_prompt,
            output_model=TechnologyAgentOutput,
            timeout_seconds=60
        )
