"""
Roadmap Generation Agent - Creates detailed execution roadmap with milestones.
"""

from src.agents.base_agent import BaseAgent
from src.core.models import RoadmapAgentOutput
from src.prompts.prompt_loader import PromptLoader
from src.utils.llm_client import LLMClient


class RoadmapAgent(BaseAgent):
    """
    Creates detailed execution roadmap with milestones and deliverables.
    
    Responsibilities:
    - Define Week 1 immediate actions
    - Define Month 1 goals and milestones
    - Define Month 3 key milestones
    - Define Month 6 vision and goals
    - Identify critical success factors
    - Suggest contingency plans
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize Roadmap Generation Agent.
        
        Args:
            llm_client: LLM client for API calls
        """
        loader = PromptLoader()
        system_prompt = loader.get_system_prompt("roadmap")
        super().__init__(
            name=loader.get_agent_name("roadmap"),
            llm_client=llm_client,
            system_prompt=system_prompt,
            output_model=RoadmapAgentOutput,
            timeout_seconds=60
        )
