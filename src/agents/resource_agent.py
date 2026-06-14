"""
Resource Analyst Agent - Estimates team, budget, and resource requirements.
"""

from src.agents.base_agent import BaseAgent
from src.core.models import ResourceAgentOutput
from src.prompts.prompt_loader import PromptLoader
from src.utils.llm_client import LLMClient


class ResourceAgent(BaseAgent):
    """
    Estimates team, budget, and resource requirements.
    
    Responsibilities:
    - Estimate team size needed (engineers, designers, product, etc.)
    - Break down budget into development, marketing, operations, contingency
    - Estimate total funding needed
    - Identify key skills required
    - Calculate resource feasibility score
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize Resource Analyst Agent.
        
        Args:
            llm_client: LLM client for API calls
        """
        loader = PromptLoader()
        system_prompt = loader.get_system_prompt("resource")
        super().__init__(
            name=loader.get_agent_name("resource"),
            llm_client=llm_client,
            system_prompt=system_prompt,
            output_model=ResourceAgentOutput,
            timeout_seconds=60
        )
