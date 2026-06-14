"""
Execution Planning Agent - Creates detailed execution plans and project roadmaps.
"""

from src.agents.base_agent import BaseAgent
from src.core.models import ExecutionAgentOutput
from src.prompts.prompt_loader import PromptLoader
from src.utils.llm_client import LLMClient


class ExecutionAgent(BaseAgent):
    """
    Creates detailed execution plans with project phases and milestones.
    
    Responsibilities:
    - Define minimal viable product (MVP) scope
    - Break down into project phases with timelines
    - Identify critical path items
    - Define success metrics
    - Estimate time to revenue
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize Execution Planning Agent.
        
        Args:
            llm_client: LLM client for API calls
        """
        loader = PromptLoader()
        system_prompt = loader.get_system_prompt("execution")
        super().__init__(
            name=loader.get_agent_name("execution"),
            llm_client=llm_client,
            system_prompt=system_prompt,
            output_model=ExecutionAgentOutput,
            timeout_seconds=60
        )
