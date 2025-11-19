"""
Base Agent - Base class for all AI agents.

Provides common functionality:
- Error handling
- Logging
- Retry logic
- Rate limiting
- LLM call wrapper
"""

import logging
from typing import Optional, Any


logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all AI agents in the pipeline.
    
    Provides common functionality that all agents need:
    - Standardized error handling
    - Logging of agent steps
    - Retry logic for LLM calls
    - Rate limiting
    - Common LLM call interface
    
    TODO: Implement base functionality:
    1. Set up logging configuration
    2. Implement retry logic with exponential backoff
    3. Add rate limiting to prevent API quota issues
    4. Create unified LLM call interface
    5. Add error handling with meaningful error messages
    """
    
    def __init__(self):
        """
        Initialize base agent.
        
        TODO: Initialize common resources:
        - Logger instance
        - Retry configuration
        - Rate limiter
        - Error tracking
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        # TODO: Initialize rate limiter
        # TODO: Set retry configuration
        pass
    
    async def _call_llm(
        self, 
        prompt: str, 
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Call LLM with error handling and retry logic.
        
        Args:
            prompt: The prompt to send to the LLM
            model: Model name (e.g., "gpt-4", "gemini-2.5-flash")
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLM response text
            
        Raises:
            Exception: If all retries fail
        
        TODO: Implement LLM call wrapper:
        1. Detect model type (OpenAI vs Gemini)
        2. Call appropriate service (OpenAIService or GeminiService)
        3. Add retry logic (exponential backoff)
        4. Log request/response for debugging
        5. Handle rate limit errors
        6. Return response text
        
        Example:
        ```python
        from app.services.ai.openai_service import OpenAIService
        from app.services.ai.gemini_service import GeminiService
        
        if "gpt" in model:
            service = OpenAIService()
            response = await service.call(prompt, model, temperature, max_tokens)
        elif "gemini" in model:
            service = GeminiService()
            response = await service.call(prompt, model, temperature, max_tokens)
        
        return response
        ```
        """
        # TODO: Implement LLM call with retry logic
        self.logger.info(f"Calling LLM with model: {model}")
        # TODO: Add actual implementation
        pass
    
    async def _log_step(self, step_name: str, data: dict):
        """
        Log agent execution step for debugging and monitoring.
        
        Args:
            step_name: Name of the step being executed
            data: Data to log (input/output, metadata, etc.)
        
        TODO: Implement step logging:
        1. Log to console for development
        2. Save to database for production monitoring
        3. Include timestamp, agent name, step name
        4. Store input/output for debugging
        5. Consider structured logging (JSON format)
        
        Example:
        ```python
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.__class__.__name__,
            "step": step_name,
            "data": data
        }
        self.logger.info(f"Step: {step_name}", extra=log_entry)
        ```
        """
        # TODO: Implement structured logging
        self.logger.info(f"Executing step: {step_name}")
        pass
    
    async def _handle_error(self, error: Exception, context: dict) -> None:
        """
        Handle errors with context for debugging.
        
        Args:
            error: The exception that occurred
            context: Context information (agent, step, input data)
        
        TODO: Implement error handling:
        1. Log error with full context
        2. Save error to database for monitoring
        3. Send alerts for critical errors
        4. Provide user-friendly error messages
        """
        self.logger.error(
            f"Error in {context.get('agent')}.{context.get('step')}: {str(error)}",
            exc_info=True
        )
        # TODO: Add error tracking/monitoring
        pass
    
    async def _retry_with_backoff(
        self, 
        func, 
        max_retries: int = 3,
        initial_delay: float = 1.0
    ) -> Any:
        """
        Retry function with exponential backoff.
        
        Args:
            func: Async function to retry
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            
        Returns:
            Result from successful function call
            
        Raises:
            Exception: If all retries fail
        
        TODO: Implement exponential backoff:
        1. Try calling function
        2. If fails, wait with exponential backoff (1s, 2s, 4s, etc.)
        3. Retry up to max_retries times
        4. Log each retry attempt
        5. Raise last exception if all fail
        
        Example:
        ```python
        import asyncio
        
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                delay = initial_delay * (2 ** attempt)
                await asyncio.sleep(delay)
        ```
        """
        # TODO: Implement retry logic
        pass

