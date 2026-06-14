"""
Prompt loader and management utility.
Loads system prompts from YAML and provides them to agents.
"""

import logging
from pathlib import Path
from typing import Dict, Optional
import yaml

logger = logging.getLogger(__name__)


class PromptLoader:
    """
    Manages loading and accessing system prompts from YAML files.
    """
    
    _prompts_cache: Optional[Dict] = None
    _yaml_path: Optional[Path] = None
    
    @classmethod
    def set_yaml_path(cls, path: str) -> None:
        """Set the path to the system prompts YAML file."""
        cls._yaml_path = Path(path)
        cls._prompts_cache = None  # Clear cache
        logger.info(f"Prompt YAML path set to: {cls._yaml_path}")
    
    @classmethod
    def load_prompts(cls) -> Dict:
        """
        Load all prompts from YAML file.
        Results are cached for performance.
        
        Returns:
            Dictionary of all prompts
        """
        if cls._prompts_cache is not None:
            return cls._prompts_cache
        
        if cls._yaml_path is None:
            cls._yaml_path = Path("src/prompts/system_prompts.yaml")
        
        if not cls._yaml_path.exists():
            raise FileNotFoundError(f"Prompts YAML not found: {cls._yaml_path}")
        
        with open(cls._yaml_path, 'r') as f:
            cls._prompts_cache = yaml.safe_load(f)
        
        logger.info(f"Loaded {len(cls._prompts_cache)} agent prompts from {cls._yaml_path}")
        return cls._prompts_cache
    
    @classmethod
    def get_prompt(cls, agent_key: str) -> Dict:
        """
        Get prompt configuration for a specific agent.
        
        Args:
            agent_key: Key of the agent (e.g., 'market', 'risk')
            
        Returns:
            Dictionary with name, description, and system_prompt
            
        Raises:
            KeyError: If agent_key not found
        """
        prompts = cls.load_prompts()
        
        if agent_key not in prompts:
            available = list(prompts.keys())
            raise KeyError(
                f"Agent '{agent_key}' not found. "
                f"Available: {', '.join(available)}"
            )
        
        return prompts[agent_key]
    
    @classmethod
    def get_system_prompt(cls, agent_key: str) -> str:
        """
        Get just the system prompt text for an agent.
        
        Args:
            agent_key: Key of the agent
            
        Returns:
            System prompt string
        """
        prompt_config = cls.get_prompt(agent_key)
        return prompt_config['system_prompt']
    
    @classmethod
    def get_agent_name(cls, agent_key: str) -> str:
        """Get the display name for an agent."""
        prompt_config = cls.get_prompt(agent_key)
        return prompt_config.get('name', agent_key)
    
    @classmethod
    def get_agent_description(cls, agent_key: str) -> str:
        """Get the description for an agent."""
        prompt_config = cls.get_prompt(agent_key)
        return prompt_config.get('description', '')
    
    @classmethod
    def list_agents(cls) -> Dict[str, str]:
        """
        Get list of all available agents with their names.
        
        Returns:
            Dictionary mapping agent_key to agent_name
        """
        prompts = cls.load_prompts()
        return {
            key: config.get('name', key)
            for key, config in prompts.items()
        }
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear the prompts cache."""
        cls._prompts_cache = None
        logger.debug("Prompts cache cleared")


def get_prompt_loader() -> PromptLoader:
    """Get the prompt loader instance (singleton pattern)."""
    return PromptLoader()


if __name__ == "__main__":
    # Test prompt loading
    try:
        loader = PromptLoader()
        
        # Load all prompts
        agents = loader.list_agents()
        print(f"✓ Loaded {len(agents)} agents:")
        for key, name in agents.items():
            print(f"  - {key}: {name}")
        
        # Test individual agent access
        print("\n✓ Dream Understanding Agent:")
        prompt_config = loader.get_prompt("dream_understanding")
        print(f"  Name: {prompt_config['name']}")
        print(f"  Description: {prompt_config['description']}")
        print(f"  System Prompt: {prompt_config['system_prompt'][:100]}...")
        
    except Exception as e:
        print(f"✗ Error: {e}")
