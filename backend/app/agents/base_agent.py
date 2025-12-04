import time
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from app.services.ai import anthropic_service, gemini_service
from app.models.common import BasePipelineStep


InputT = TypeVar('InputT')
OutputT = TypeVar('OutputT', bound=BasePipelineStep)


class AgentError(Exception):
    pass


class ValidationError(AgentError):
    pass


class ExecutionError(AgentError):
    pass


class BaseAgent(ABC, Generic[InputT, OutputT]):
    def __init__(self):
        self.anthropic = anthropic_service
        self.gemini = gemini_service
        self.agent_name = self.__class__.__name__
    
    @abstractmethod
    async def _validate_input(self, input_data: InputT) -> None:
        pass
    
    @abstractmethod
    async def _execute(self, input_data: InputT) -> OutputT:
        pass
    
    async def run(self, input_data: InputT) -> OutputT:
        start_time = time.time()
        
        try:
            await self._validate_input(input_data)
            
            output = await self._execute(input_data)
            
            execution_time = int((time.time() - start_time) * 1000)
            output.execution_time = execution_time
            
            return output
            
        except ValidationError as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Validation failed: {str(e)}"
            
            return self._create_error_output(error_msg, execution_time_ms)
            
        except ExecutionError as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Execution failed: {str(e)}"
            
            return self._create_error_output(error_msg, execution_time_ms)
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Unexpected error: {str(e)}"
            
            return self._create_error_output(error_msg, execution_time_ms)
    
    def _create_error_output(self, error_message: str, execution_time_ms: int) -> OutputT:
        raise ExecutionError(error_message)
