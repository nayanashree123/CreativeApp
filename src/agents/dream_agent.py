"""
Dream Understanding Agent - Parses and structures raw dream descriptions.
"""

from src.agents.base_agent import BaseAgent
from src.core.models import DreamUnderstandingOutput
from src.prompts.prompt_loader import PromptLoader
from src.utils.llm_client import LLMClient


class DreamUnderstandingAgent(BaseAgent):
    """
    Parses raw dream descriptions into structured, actionable insights.
    
    Responsibilities:
    - Parse the dream description into clear components
    - Identify core assumptions
    - Highlight constraints and limitations
    - Calculate clarity score
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize Dream Understanding Agent.
        
        Args:
            llm_client: LLM client for API calls
        """
        loader = PromptLoader()
        system_prompt = loader.get_system_prompt("dream_understanding")
        super().__init__(
            name=loader.get_agent_name("dream_understanding"),
            llm_client=llm_client,
            system_prompt=system_prompt,
            output_model=DreamUnderstandingOutput,
            timeout_seconds=60
        )
