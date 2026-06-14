"""
Base Agent class for all specialized agents.
Provides common functionality: LLM calls, response parsing, logging, error handling.
"""

import json
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.core.models import AgentOutput, DreamProfile, ErrorResponse, FallbackAgentOutput
from src.utils.llm_client import LLMClient

# Type hint for retriever (avoid circular imports)
try:
    from src.rag.retriever import KnowledgeRetriever
except ImportError:
    KnowledgeRetriever = Optional[Any]


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents.
    Handles:
    - LLM communication
    - Response parsing and validation
    - Error handling and fallbacks
    - Execution logging and metrics
    """
    
    def __init__(
        self,
        name: str,
        llm_client: LLMClient,
        system_prompt: str,
        output_model: type = AgentOutput,
        timeout_seconds: int = 60,
        retriever: Optional[Any] = None
    ):
        """
        Initialize a specialized agent.
        
        Args:
            name: Name of the agent (e.g., "Market Analyst")
            llm_client: LLM client for API calls
            system_prompt: System prompt defining agent behavior
            output_model: Pydantic model for output validation
            timeout_seconds: Timeout for agent execution
            retriever: Optional KnowledgeRetriever for RAG context
        """
        self.name = name
        self.llm_client = llm_client
        self.system_prompt = system_prompt
        self.output_model = output_model
        self.timeout_seconds = timeout_seconds
        self.retriever = retriever
        
        # Metrics
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_execution_time_ms = 0
        self.total_tokens_used = 0
        
        logger.debug(f"Initialized agent: {self.name}" + 
                     (" (with RAG retriever)" if retriever else ""))
    
    def _format_input(
        self,
        dream: DreamProfile,
        rag_context: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format dream and context into a user message for the agent.
        
        Args:
            dream: The dream profile to analyze
            rag_context: Retrieved context from knowledge base
            additional_context: Any additional context for this agent
            
        Returns:
            Formatted user message string
        """
        message_parts = []
        
        # Core dream information
        message_parts.append("=== DREAM DETAILS ===")
        message_parts.append(f"Description: {dream.dream_text}")
        if dream.idea_name:
            message_parts.append(f"Idea Name: {dream.idea_name}")
        if dream.target_market:
            message_parts.append(f"Target Market: {dream.target_market}")
        if dream.budget_range:
            message_parts.append(f"Budget: {dream.budget_range}")
        if dream.timeline:
            message_parts.append(f"Timeline: {dream.timeline}")
        if dream.assumptions:
            message_parts.append(f"Assumptions:\n" + "\n".join(f"  - {a}" for a in dream.assumptions))
        if dream.constraints:
            message_parts.append(f"Constraints:\n" + "\n".join(f"  - {c}" for c in dream.constraints))
        
        # RAG Context
        if rag_context:
            message_parts.append("\n=== RELEVANT PATTERNS FROM KNOWLEDGE BASE ===")
            message_parts.append(rag_context)
        
        # Additional context (from other agents, etc.)
        if additional_context:
            message_parts.append("\n=== ADDITIONAL CONTEXT ===")
            for key, value in additional_context.items():
                if isinstance(value, (dict, list)):
                    message_parts.append(f"{key}:\n{json.dumps(value, indent=2)}")
                else:
                    message_parts.append(f"{key}: {value}")
        
        return "\n".join(message_parts)
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured format.
        Attempts JSON extraction with multiple fallback strategies.
        Handles both string and dict responses (LLMClient may pre-parse).
        
        Args:
            response_text: Raw response from LLM (string or dict)
            
        Returns:
            Parsed dictionary or error info
        """
        # If already a dict, LLMClient parsed it - return as-is
        if isinstance(response_text, dict):
            return response_text
        
        # Strip whitespace for string responses
        response_text = response_text.strip()
        
        # Try direct JSON parse first
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from response text (handles markdown code blocks)
        try:
            # Remove markdown code blocks if present
            cleaned = response_text
            if cleaned.startswith("```"):
                # Remove starting markdown block
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                else:
                    cleaned = cleaned[3:]
                # Remove ending markdown block
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            
            # Try parsing the cleaned version
            return json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Try to extract JSON from response text (handles embedded JSON)
        try:
            # Find JSON blocks - look for { and } pairs
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx + 1]
                parsed = json.loads(json_str)
                logger.info(f"[{self.name}] Extracted JSON from response (removed {start_idx} leading chars)")
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Try to extract arrays if they're the main content
        try:
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']')
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx + 1]
                parsed = json.loads(json_str)
                logger.info(f"[{self.name}] Extracted JSON array from response")
                return {"items": parsed}
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Last resort: structure the response as best we can
        logger.warning(f"[{self.name}] Could not parse JSON response, using text fallback")
        logger.debug(f"[{self.name}] Raw response that failed to parse:\n{response_text[:500]}...")
        return {
            "response": response_text,
            "parsing_failed": True,
            "error": "Could not parse as JSON"
        }
    
    def _build_reasoning_chain(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Extract reasoning steps from agent analysis.
        Used for explainability and debugging.
        
        Args:
            analysis: Agent output dictionary
            
        Returns:
            List of reasoning steps
        """
        reasoning = []
        
        # Extract reasoning field if present
        if "reasoning" in analysis:
            reasoning.append(analysis["reasoning"])
        
        # Extract other explanation fields
        explanation_fields = [
            "explanation", "analysis", "rationale",
            "key_findings", "assessment", "evaluation"
        ]
        for field in explanation_fields:
            if field in analysis:
                value = analysis[field]
                if isinstance(value, str):
                    reasoning.append(value)
                elif isinstance(value, list):
                    reasoning.extend(value)
        
        return reasoning if reasoning else ["Analysis complete"]
    
    def _log_execution(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        duration_ms: float,
        success: bool
    ) -> None:
        """
        Log agent execution details for debugging and monitoring.
        
        Args:
            inputs: Input parameters
            outputs: Agent outputs
            duration_ms: Execution time in milliseconds
            success: Whether execution was successful
        """
        status = "✓ SUCCESS" if success else "✗ FAILED"
        
        logger.info(
            f"[{self.name}] {status} | "
            f"Duration: {duration_ms:.0f}ms | "
            f"Tokens: {outputs.get('tokens_used', 0)}"
        )
        
        if not success:
            logger.warning(
                f"[{self.name}] Error: {outputs.get('error', 'Unknown error')}"
            )
    
    async def execute(
        self,
        dream: DreamProfile,
        rag_context: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> AgentOutput:
        """
        Execute the agent to analyze a dream.
        This is the main entry point for agent execution.
        
        Args:
            dream: Dream profile to analyze
            rag_context: Retrieved context from knowledge base (optional, auto-retrieves if retriever available)
            additional_context: Additional context for analysis
            
        Returns:
            AgentOutput instance with analysis results
        """
        self.execution_count += 1
        start_time_ms = datetime.now().timestamp() * 1000
        
        try:
            # Automatically retrieve RAG context if retriever available and context not provided
            if rag_context is None and self.retriever is not None:
                try:
                    rag_context = self.retriever.retrieve_for_agent(
                        agent_name=self.name,
                        dream_text=dream.dream_text,
                        top_k=3
                    )
                    logger.debug(f"[{self.name}] Auto-retrieved RAG context ({len(rag_context)} chars)")
                except Exception as e:
                    logger.warning(f"[{self.name}] Failed to retrieve RAG context: {e}")
                    # Continue without RAG context
            
            # Format input
            user_message = self._format_input(dream, rag_context, additional_context)
            
            logger.debug(f"[{self.name}] Executing with formatted input ({len(user_message)} chars)")
            
            # Call LLM with timeout
            llm_result = await asyncio.wait_for(
                self.llm_client.call_agent(
                    agent_name=self.name,
                    system_prompt=self.system_prompt,
                    user_message=user_message,
                    json_mode=True,
                    max_tokens=2000
                ),
                timeout=self.timeout_seconds
            )
            
            # Extract execution metrics
            duration_ms = datetime.now().timestamp() * 1000 - start_time_ms
            tokens_used = llm_result.get("tokens_used", 0)
            
            # Check if LLM call succeeded
            if not llm_result.get("success", False):
                error_msg = llm_result.get("error", "Unknown LLM error")
                logger.error(f"[{self.name}] LLM call failed: {error_msg}")
                
                self.failure_count += 1
                self._log_execution(
                    {"dream": dream.idea_name},
                    {"error": error_msg, "tokens_used": tokens_used},
                    duration_ms,
                    False
                )
                
                return self._create_fallback_output(
                    error_msg,
                    duration_ms,
                    tokens_used,
                    reason="LLM call failed"
                )
            
            # Parse response
            agent_data = self._parse_response(llm_result["data"])
            
            # Build complete output with metrics
            reasoning_chain = self._build_reasoning_chain(agent_data)
            output_dict = {
                **agent_data,
                "agent_name": self.name,
                "execution_time_ms": duration_ms,
                "tokens_used": tokens_used,
                "reasoning": " → ".join(reasoning_chain) if isinstance(reasoning_chain, list) else str(reasoning_chain)
            }
            
            # Validate output against model
            try:
                output = self.output_model(**output_dict)
                self.success_count += 1
                self.total_tokens_used += tokens_used
                self.total_execution_time_ms += duration_ms
                
                self._log_execution(
                    {"dream": dream.idea_name},
                    output_dict,
                    duration_ms,
                    True
                )
                
                return output
                
            except Exception as e:
                logger.error(
                    f"[{self.name}] Output validation failed: {e}\n"
                    f"Received data: {json.dumps(output_dict, indent=2)}"
                )
                
                self.failure_count += 1
                self._log_execution(
                    {"dream": dream.idea_name},
                    {"error": str(e), "tokens_used": tokens_used},
                    duration_ms,
                    False
                )
                
                return self._create_fallback_output(
                    str(e),
                    duration_ms,
                    tokens_used,
                    reason="Output validation failed"
                )
        
        except asyncio.TimeoutError:
            duration_ms = datetime.now().timestamp() * 1000 - start_time_ms
            error_msg = f"Agent execution timed out after {self.timeout_seconds}s"
            logger.error(f"[{self.name}] {error_msg}")
            
            self.failure_count += 1
            self._log_execution(
                {"dream": dream.idea_name},
                {"error": error_msg},
                duration_ms,
                False
            )
            
            return self._create_fallback_output(
                error_msg,
                duration_ms,
                0,
                reason="Timeout"
            )
        
        except Exception as e:
            duration_ms = datetime.now().timestamp() * 1000 - start_time_ms
            error_msg = f"Unexpected agent error: {str(e)}"
            logger.error(f"[{self.name}] {error_msg}", exc_info=True)
            
            self.failure_count += 1
            self._log_execution(
                {"dream": dream.idea_name},
                {"error": error_msg},
                duration_ms,
                False
            )
            
            return self._create_fallback_output(
                error_msg,
                duration_ms,
                0,
                reason="Unexpected error"
            )
    
    def _create_fallback_output(
        self,
        error_message: str,
        duration_ms: float,
        tokens_used: int,
        reason: str
    ) -> FallbackAgentOutput:
        """
        Create a fallback output when execution fails.
        
        Args:
            error_message: Error description
            duration_ms: Execution duration
            tokens_used: Tokens used before failure
            reason: Reason for fallback
            
        Returns:
            FallbackAgentOutput with error information
        """
        return FallbackAgentOutput(
            agent_name=self.name,
            confidence=0.0,
            reasoning=f"Agent failed: {reason}",
            metadata={
                "error_reason": reason,
                "original_error": error_message
            },
            execution_time_ms=duration_ms,
            tokens_used=tokens_used,
            error=ErrorResponse(
                error_code="AGENT_EXECUTION_FAILED",
                error_message=error_message,
                agent_name=self.name,
                details={"reason": reason}
            ),
            fallback_reason=reason
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics for this agent."""
        success_rate = (
            (self.success_count / self.execution_count * 100)
            if self.execution_count > 0 else 0
        )
        avg_time_ms = (
            (self.total_execution_time_ms / self.success_count)
            if self.success_count > 0 else 0
        )
        
        return {
            "agent_name": self.name,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": f"{success_rate:.1f}%",
            "avg_execution_time_ms": f"{avg_time_ms:.0f}",
            "total_tokens_used": self.total_tokens_used
        }
    
    def reset_metrics(self) -> None:
        """Reset execution metrics."""
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_execution_time_ms = 0
        self.total_tokens_used = 0
        logger.info(f"[{self.name}] Metrics reset")


if __name__ == "__main__":
    # Test base agent class structure
    print("✓ BaseAgent class defined successfully")
    print(f"  - Name: BaseAgent")
    print(f"  - Methods: {len([m for m in dir(BaseAgent) if not m.startswith('_')])}")
    print(f"  - Abstract methods: execute()")
