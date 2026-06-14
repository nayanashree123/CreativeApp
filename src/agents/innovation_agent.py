"""
Innovation & Differentiation Agent - Evaluates novelty and competitive differentiation.
"""

from src.agents.base_agent import BaseAgent
from src.core.models import InnovationAgentOutput
from src.prompts.prompt_loader import PromptLoader
from src.utils.llm_client import LLMClient


class InnovationAgent(BaseAgent):
    """
    Evaluates innovation level and competitive differentiation.
    
    Responsibilities:
    - Score novelty/innovation level
    - Identify unique value propositions
    - Assess competitive advantages
    - Evaluate defensibility
    - Identify key innovation dimension
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize Innovation & Differentiation Agent.
        
        Args:
            llm_client: LLM client for API calls
        """
        loader = PromptLoader()
        system_prompt = loader.get_system_prompt("innovation")
        super().__init__(
            name=loader.get_agent_name("innovation"),
            llm_client=llm_client,
            system_prompt=system_prompt,
            output_model=InnovationAgentOutput,
            timeout_seconds=60
        )
