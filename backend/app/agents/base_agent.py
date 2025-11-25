"""
Base Agent - Abstract base class for all AI agents in the pipeline.

Provides:
- Service access (Anthropic, Gemini)
- Execution orchestration (validate → execute → track time)
- Error handling and logging
- Consistent output format (BasePipelineStep)
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

from app.services.ai import anthropic_service, gemini_service
from app.models.common import BasePipelineStep


# Type variable for input/output schemas
InputT = TypeVar('InputT')
OutputT = TypeVar('OutputT', bound=BasePipelineStep)


class AgentError(Exception):
    """Base exception for agent errors."""
    pass


class ValidationError(AgentError):
    """Raised when input validation fails."""
    pass


class ExecutionError(AgentError):
    """Raised when agent execution fails."""
    pass


class BaseAgent(ABC, Generic[InputT, OutputT]):
    """
    Abstract base class for all AI agents.
    
    Usage:
        class MyAgent(BaseAgent[MyInput, MyOutput]):
            async def _validate_input(self, input_data: MyInput) -> None:
                if not input_data.required_field:
                    raise ValidationError("Missing required field")
            
            async def _execute(self, input_data: MyInput) -> MyOutput:
                result = await self.anthropic.generate_text(...)
                return MyOutput(step_name="my_agent", success=True, result=result)
    """
    
    def __init__(self):
        """Initialize agent with services and logger."""
        self.anthropic = anthropic_service
        self.gemini = gemini_service
        self.logger = logging.getLogger(self.__class__.__name__)
        self.agent_name = self.__class__.__name__
    
    @abstractmethod
    async def _validate_input(self, input_data: InputT) -> None:
        """
        Validate input data before execution.
        
        Args:
            input_data: Typed input schema for this agent
            
        Raises:
            ValidationError: If input is invalid
        """
        pass
    
    @abstractmethod
    async def _execute(self, input_data: InputT) -> OutputT:
        """
        Execute agent-specific logic.
        
        Args:
            input_data: Validated input data
            
        Returns:
            Typed output schema (extends BasePipelineStep)
            
        Raises:
            ExecutionError: If execution fails
        """
        pass
    
    async def run(self, input_data: InputT) -> OutputT:
        """
        Public interface - orchestrates agent execution.
        
        Flow:
        1. Validate input
        2. Execute agent logic
        3. Track execution time
        4. Handle errors gracefully
        5. Return typed output
        
        Args:
            input_data: Input data for this agent
            
        Returns:
            Agent output with execution metadata
            
        Raises:
            AgentError: If validation or execution fails
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"{self.agent_name} - Starting execution")
            
            # Step 1: Validate input
            await self._validate_input(input_data)
            self.logger.debug(f"{self.agent_name} - Input validation passed")
            
            # Step 2: Execute agent logic
            output = await self._execute(input_data)
            
            # Step 3: Track execution time
            execution_time = int((time.time() - start_time) * 1000)
            output.execution_time = execution_time
            
            self.logger.info(
                f"{self.agent_name} - Execution completed successfully "
                f"({execution_time}ms)"
            )
            
            return output
            
        except ValidationError as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Input validation failed: {str(e)}"
            self.logger.error(f"{self.agent_name} - {error_msg}")
            
            # Return failed output for pipeline continuity
            return self._create_error_output(error_msg, execution_time_ms)
            
        except ExecutionError as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Execution failed: {str(e)}"
            self.logger.error(f"{self.agent_name} - {error_msg}", exc_info=True)
            
            return self._create_error_output(error_msg, execution_time_ms)
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(f"{self.agent_name} - {error_msg}", exc_info=True)
            
            return self._create_error_output(error_msg, execution_time_ms)
    
    def _create_error_output(self, error_message: str, execution_time_ms: int) -> OutputT:
        """
        Create error output when execution fails.
        
        Subclasses can override this to provide custom error outputs.
        
        Args:
            error_message: Error description
            execution_time_ms: Time taken before failure
            
        Returns:
            Error output with failed status
        """
        # This is a fallback - agents should override if needed
        # For MVP, we'll raise the error to halt the pipeline
        raise ExecutionError(error_message)