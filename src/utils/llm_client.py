"""
LLM Client wrapper for OpenAI API with async support and extended thinking.
Handles agent calls, error handling, and token tracking.
Supports both OpenAI and GitHub Copilot SDK.
"""

import asyncio
import json
import time
import logging
from typing import Optional, Dict, Any, Union
from openai import AsyncOpenAI, RateLimitError, APIConnectionError

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Async wrapper for LLM APIs (OpenAI or GitHub Copilot SDK).
    Handles agent calls with error recovery and token tracking.
    Automatically falls back to Copilot SDK if OpenAI API key is not available.
    """
    
    def __init__(
        self,
        settings: Optional[object] = None,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        copilot_client: Optional[object] = None,
        provider: Optional[str] = None,
    ):
        """
        Initialize LLM client with automatic provider selection.
        Defaults to Copilot SDK for demo purposes. Only uses OpenAI with a valid API key.
        
        Args:
            settings: Settings object with api_key, openai_model, etc. (preferred)
            api_key: OpenAI API key (used if settings not provided)
            model: Model to use (default: gpt-4o for OpenAI)
            temperature: Creativity level 0-1
            copilot_client: Pre-instantiated Copilot client (optional)
            provider: Force provider: "openai" or "copilot" (auto-detect if None)
        """
        # Extract settings if provided
        if settings is not None and not isinstance(settings, str):
            self.api_key = getattr(settings, 'openai_api_key', None) or api_key
            self.temperature = getattr(settings, 'openai_temperature', temperature)
            self.model = getattr(settings, 'openai_model', model)
            # Copilot settings
            self.copilot_temperature = getattr(settings, 'copilot_temperature', 0.2)
            self.copilot_model = getattr(settings, 'copilot_model', 'gpt-5-mini')
        else:
            self.api_key = api_key
            self.temperature = temperature
            self.model = model
            self.copilot_temperature = 0.2
            self.copilot_model = 'gpt-5-mini'
        
        # Validate API key - check if it's a real key or a placeholder
        has_valid_openai_key = self._is_valid_openai_key(self.api_key)
        
        # Determine provider (prioritize Copilot SDK for demo purposes)
        if provider:
            self.provider = provider
        elif has_valid_openai_key:
            # Only use OpenAI if we have a real, valid API key
            self.provider = "openai"
        elif copilot_client or self._has_copilot_token():
            # Default to Copilot SDK if no valid OpenAI key
            self.provider = "copilot"
        else:
            raise RuntimeError(
                "No LLM provider configured. "
                "Set OPENAI_API_KEY for OpenAI or GITHUB_TOKEN/ALTERNATE_GITHUB_TOKEN for Copilot SDK."
            )
        
        # Initialize client
        self.client = None
        if self.provider == "openai":
            if not has_valid_openai_key:
                raise RuntimeError(
                    "Invalid OpenAI API key provided. "
                    "Please set a real API key or use Copilot SDK."
                )
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info(f"✓ LLM Client initialized with OpenAI model: {self.model}")
        elif self.provider == "copilot":
            if copilot_client is None:
                # Lazy-load Copilot SDK client
                try:
                    from src.utils.copilot_helper import get_copilot_client
                    copilot_client = get_copilot_client()
                except ImportError as e:
                    raise RuntimeError(
                        f"Failed to import Copilot SDK: {e}. "
                        "Run: pip install github-copilot-sdk"
                    )
            self.client = copilot_client
            logger.info(f"✓ LLM Client initialized with Copilot SDK model: {self.copilot_model}")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        self.total_tokens_used = 0
        self.total_calls = 0
        self.failed_calls = 0
    
    @staticmethod
    def _is_valid_openai_key(api_key: Optional[str]) -> bool:
        """
        Check if the provided API key is a valid OpenAI key (not a placeholder).
        Valid keys start with 'sk-' but not placeholder patterns.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if key appears to be valid, False otherwise
        """
        if not api_key or not isinstance(api_key, str):
            return False
        
        api_key = api_key.strip()
        
        # Check for common placeholder patterns
        placeholders = [
            'sk-your',
            'sk-proj-your',
            'sk-placeholder',
            'your-api-key',
            'your-key-here',
            'sk-test',
            'test-key',
            'placeholder',
            'xxxx',
        ]
        
        api_key_lower = api_key.lower()
        if any(placeholder in api_key_lower for placeholder in placeholders):
            return False
        
        # Valid OpenAI keys start with sk- or sk-proj- and are reasonably long
        if api_key.startswith('sk-') and len(api_key) > 20:
            return True
        
        return False
    
    @staticmethod
    def _has_copilot_token() -> bool:
        """Check if Copilot SDK token is available."""
        try:
            from src.utils.copilot_helper import _load_token
            return bool(_load_token())
        except Exception:
            return False
    
    async def call_agent(
        self,
        agent_name: str,
        system_prompt: str,
        user_message: str,
        json_mode: bool = True,
        max_tokens: int = 2000,
        retries: int = 3
    ) -> Dict[str, Any]:
        """
        Call an agent via LLM with extended thinking support.
        
        Args:
            agent_name: Name of the agent (for logging)
            system_prompt: System prompt for the agent
            user_message: The actual task/question
            json_mode: Whether to expect JSON output
            max_tokens: Max tokens in response
            retries: Number of retry attempts for failures
            
        Returns:
            Dictionary with 'success', 'data', 'error', 'tokens_used', 'execution_time_ms'
        """
        start_time = time.time()
        attempt = 0
        last_error = None
        
        while attempt < retries:
            try:
                attempt += 1
                
                logger.debug(f"[{agent_name}] Attempt {attempt}/{retries}")
                
                # Build messages
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
                
                # Call API depending on provider/client capabilities
                if self.provider == "openai":
                    response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=self.temperature,
                        max_tokens=max_tokens,
                        response_format={"type": "json_object"} if json_mode else None,
                        timeout=60,  # 60 second timeout per call
                    )

                    # Extract response for OpenAI-style response
                    response_text = response.choices[0].message.content
                    tokens_used = getattr(response.usage, "total_tokens", 0)

                elif self.provider == "copilot":
                    # Support Copilot client with async generate_async() method
                    response_text = None
                    tokens_used = 0
                    
                    # Use Copilot-specific temperature (usually lower for better consistency)
                    copilot_temp = self.copilot_temperature
                    
                    # Check for async generate_async method (preferred)
                    if hasattr(self.client, "generate_async") and callable(getattr(self.client, "generate_async")):
                        response_text = await self.client.generate_async(
                            prompt=user_message,
                            system_prompt=system_prompt,
                            temperature=copilot_temp,
                            max_tokens=max_tokens,
                        )
                    # Fallback to sync generate method called in thread
                    elif hasattr(self.client, "generate") and callable(getattr(self.client, "generate")):
                        response_text = await asyncio.to_thread(
                            self.client.generate,
                            prompt=user_message,
                            system_prompt=system_prompt,
                            temperature=copilot_temp,
                            max_tokens=max_tokens,
                        )
                    else:
                        raise RuntimeError(
                            "Provided copilot_client does not implement generate_async() or generate()."
                        )
                else:
                    raise RuntimeError(f"Unsupported provider during call: {self.provider}")
                
                self.total_tokens_used += tokens_used
                self.total_calls += 1
                
                # Parse if JSON expected
                if json_mode:
                    try:
                        data = json.loads(response_text)
                    except json.JSONDecodeError as e:
                        logger.warning(f"[{agent_name}] Failed to parse JSON response: {e}")
                        # Try to extract JSON from response
                        try:
                            start_idx = response_text.find('{')
                            end_idx = response_text.rfind('}') + 1
                            if start_idx != -1 and end_idx > start_idx:
                                data = json.loads(response_text[start_idx:end_idx])
                            else:
                                raise ValueError("No JSON found in response")
                        except (json.JSONDecodeError, ValueError) as e2:
                            logger.error(f"[{agent_name}] Could not recover JSON: {e2}")
                            return {
                                "success": False,
                                "error": f"JSON parsing failed: {str(e2)}",
                                "tokens_used": tokens_used,
                                "execution_time_ms": (time.time() - start_time) * 1000,
                                "agent_name": agent_name
                            }
                else:
                    data = {"response": response_text}
                
                execution_time_ms = (time.time() - start_time) * 1000
                
                logger.info(
                    f"[{agent_name}] Success | Tokens: {tokens_used} | "
                    f"Time: {execution_time_ms:.0f}ms"
                )
                
                return {
                    "success": True,
                    "data": data,
                    "tokens_used": tokens_used,
                    "execution_time_ms": execution_time_ms,
                    "agent_name": agent_name,
                    "attempts": attempt
                }
                
            except RateLimitError as e:
                last_error = e
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(
                    f"[{agent_name}] Rate limited. Waiting {wait_time}s before retry..."
                )
                if attempt < retries:
                    await asyncio.sleep(wait_time)
                    
            except APIConnectionError as e:
                last_error = e
                logger.warning(
                    f"[{agent_name}] Connection error on attempt {attempt}: {e}"
                )
                if attempt < retries:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                last_error = e
                logger.error(
                    f"[{agent_name}] Unexpected error on attempt {attempt}: {e}",
                    exc_info=True
                )
                if attempt < retries and attempt < 2:  # Only retry twice for unexpected errors
                    await asyncio.sleep(1)
        
        # All retries exhausted
        self.failed_calls += 1
        execution_time_ms = (time.time() - start_time) * 1000
        
        logger.error(
            f"[{agent_name}] Failed after {retries} attempts. "
            f"Last error: {last_error}"
        )
        
        return {
            "success": False,
            "error": str(last_error),
            "execution_time_ms": execution_time_ms,
            "agent_name": agent_name,
            "attempts": attempt
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics."""
        success_rate = (
            (self.total_calls - self.failed_calls) / self.total_calls * 100
            if self.total_calls > 0 else 0
        )
        
        return {
            "total_calls": self.total_calls,
            "failed_calls": self.failed_calls,
            "success_rate": f"{success_rate:.1f}%",
            "total_tokens_used": self.total_tokens_used,
            "avg_tokens_per_call": (
                self.total_tokens_used / self.total_calls
                if self.total_calls > 0 else 0
            )
        }


# Global instance (can be replaced with dependency injection later)
_llm_client: Optional[LLMClient] = None


def initialize_llm_client(
    provider: str = "copilot",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    copilot_client: Optional[object] = None,
) -> LLMClient:
    """
    Initialize the global LLM client.
    
    Args:
        provider: "copilot" (default, free via GitHub Copilot SDK) or "openai"
        api_key: OpenAI API key (required if provider="openai")
        model: Model name (default: "gpt-5-mini" for copilot, "gpt-4o" for openai)
        copilot_client: Pre-initialized Copilot client (optional, will create if None)
        
    Returns:
        LLMClient instance
    """
    global _llm_client
    
    if provider == "copilot":
        if copilot_client is None:
            from src.utils.copilot_helper import get_copilot_client
            copilot_client = get_copilot_client()
        model = model or "gpt-5-mini"
        _llm_client = LLMClient(
            copilot_client=copilot_client,
            provider="copilot",
            model=model
        )
        logger.info(f"Initialized LLM client with Copilot provider (model: {model})")
    elif provider == "openai":
        if api_key is None:
            raise ValueError("api_key is required for OpenAI provider")
        model = model or "gpt-4o"
        _llm_client = LLMClient(api_key=api_key, model=model, provider="openai")
        logger.info(f"Initialized LLM client with OpenAI provider (model: {model})")
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    return _llm_client


def get_llm_client() -> LLMClient:
    """Get the global LLM client. Initializes with Copilot if not yet initialized."""
    global _llm_client
    if _llm_client is None:
        # Auto-initialize with Copilot (no API key needed)
        _llm_client = initialize_llm_client(provider="copilot")
    return _llm_client


if __name__ == "__main__":
    # Test client initialization
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        client = LLMClient(api_key=api_key)
        print("LLM Client initialized successfully")
        print(f"Model: {client.model}")
        print(f"Statistics: {client.get_statistics()}")
    else:
        print("ERROR: OPENAI_API_KEY not found in environment")
