"""
Copilot SDK client wrapper for GitHub Copilot API access.
Provides synchronous `generate()` method for seamless integration with LLMClient.
"""

import asyncio
import os
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# -------------------------------------------------------------------
# Project paths
# -------------------------------------------------------------------
CLIENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CLIENT_DIR.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_PATH)

# -------------------------------------------------------------------
# Copilot config
# -------------------------------------------------------------------
COPILOT_MODEL = os.getenv("COPILOT_MODEL", "gpt-5-mini")  # "auto", "gpt-5-mini", "claude-haiku-4.5"
COPILOT_TIMEOUT = int(os.getenv("COPILOT_TIMEOUT", "200"))
COPILOT_RETRIES = int(os.getenv("COPILOT_RETRIES", "3"))


def _load_token() -> str:
    """
    Always re-read token from project .env so refreshed token is used
    without restarting the process.
    """
    fallback_env_token = ""

    try:
        if ENV_PATH.exists():
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue

                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")

                    if key == "ALTERNATE_GITHUB_TOKEN" and value:
                        return value
                    if key == "GITHUB_TOKEN" and value:
                        fallback_env_token = value
    except Exception:
        pass

    return fallback_env_token or os.getenv("ALTERNATE_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN") or ""


def _build_prompt(prompt: str, system_prompt: Optional[str]) -> str:
    """Combine system prompt and user prompt into a single string for the SDK."""
    if system_prompt:
        return (
            f"[SYSTEM INSTRUCTIONS]\n{system_prompt}\n[END SYSTEM INSTRUCTIONS]\n\n"
            f"{prompt}"
        )
    return prompt


async def _run_inference(token: str, model: str, prompt: str, timeout: float) -> str:
    """Start a Copilot SDK session, send the prompt, and return the response."""
    try:
        from copilot import CopilotClient as _SdkCopilotClient
        from copilot import PermissionHandler
    except ImportError:
        raise RuntimeError(
            "'github-copilot-sdk' is not installed. Run: pip install github-copilot-sdk"
        )

    # Initialize Copilot client with GitHub token
    client = _SdkCopilotClient(github_token=token)

    session = await client.create_session(
        on_permission_request=PermissionHandler.approve_all,
        model=model or None,
    )
    try:
        event = await session.send_and_wait(prompt, timeout=timeout)

        if event is None:
            raise RuntimeError("Copilot returned no response.")

        # Extract content from SessionEvent.data.content
        content = None
        try:
            # SessionEvent has data attribute which is AssistantMessageData
            if hasattr(event, "data") and hasattr(event.data, "content"):
                content = event.data.content
        except (AttributeError, TypeError):
            pass
        
        # Fallback attempts
        if not content:
            content = getattr(event, "message", None)
        if not content:
            content = getattr(event, "content", None)
        if not content:
            # Last resort: convert to string and try to parse
            content = str(event)

        if not content or not str(content).strip():
            raise RuntimeError("Copilot returned empty response.")

        return str(content).strip()
    finally:
        await session.disconnect()


async def list_available_models(token: str) -> list[str]:
    """Fetch and return available model IDs."""
    try:
        from copilot import CopilotClient as _SdkCopilotClient
    except ImportError:
        raise RuntimeError(
            "'github-copilot-sdk' is not installed. Run: pip install github-copilot-sdk"
        )

    client = _SdkCopilotClient(github_token=token)

    await client.start()
    try:
        models = await client.list_models()
        return [m.id for m in models] if models else []
    finally:
        await client.stop()


class CopilotClient:
    """
    Wrapper around the GitHub Copilot SDK for seamless async integration.
    Exposes both async and sync methods for flexibility.
    """

    def __init__(
        self,
        model: str = COPILOT_MODEL,
        timeout: int = COPILOT_TIMEOUT,
        retries: int = COPILOT_RETRIES,
    ) -> None:
        self.model = model
        self.timeout = timeout
        self.retries = retries

    async def generate_async(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate a response using the Copilot SDK (async version).
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instructions
            temperature: Creativity level (0-1, typically 0-0.5 for tasks)
            max_tokens: Max response length (Copilot SDK may not fully honor this)
            
        Returns:
            Response text from Copilot
        """
        token = _load_token()
        if not token:
            raise RuntimeError(
                f"No GitHub token found. "
                f"Set ALTERNATE_GITHUB_TOKEN or GITHUB_TOKEN in {ENV_PATH}"
            )

        full_prompt = _build_prompt(prompt, system_prompt)
        last_err = None

        for attempt in range(1, self.retries + 1):
            try:
                return await _run_inference(token, self.model, full_prompt, float(self.timeout))
            except Exception as exc:
                last_err = exc
                if attempt < self.retries:
                    await asyncio.sleep(min(8.0, 1.5 * attempt))

        raise RuntimeError(
            f"Copilot call failed after {self.retries} retries: {last_err}"
        )

    def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate a response using the Copilot SDK (synchronous wrapper).
        Only use this when outside an async context. Prefer generate_async().
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instructions
            temperature: Creativity level (0-1, typically 0-0.5 for tasks)
            max_tokens: Max response length (Copilot SDK may not fully honor this)
            
        Returns:
            Response text from Copilot
        """
        token = _load_token()
        if not token:
            raise RuntimeError(
                f"No GitHub token found. "
                f"Set ALTERNATE_GITHUB_TOKEN or GITHUB_TOKEN in {ENV_PATH}"
            )

        full_prompt = _build_prompt(prompt, system_prompt)
        last_err = None

        for attempt in range(1, self.retries + 1):
            try:
                # Create a new event loop if needed (for thread safety)
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                return loop.run_until_complete(
                    _run_inference(token, self.model, full_prompt, float(self.timeout))
                )
            except Exception as exc:
                last_err = exc
                if attempt < self.retries:
                    time.sleep(min(8.0, 1.5 * attempt))

        raise RuntimeError(
            f"Copilot call failed after {self.retries} retries: {last_err}"
        )


def get_copilot_client() -> CopilotClient:
    """Get a Copilot client instance."""
    return CopilotClient()
