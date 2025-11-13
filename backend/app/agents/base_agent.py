"""
BaseAgent - Abstract base class providing common functionality for all pipeline agents.
Defines the standard interface and shared utilities (logging, configuration) that all
specialized agents inherit.

Main Functions:
    1. process() - Abstract method that all agents must implement
    2. log_info() - Logs informational messages with agent name prefix
    3. log_error() - Logs error messages with agent name prefix
    4. log_debug() - Logs debug messages with agent name prefix

Connections:
    - Inherited by: All agent classes (OrchestratorAgent, FormatSelectorAgent, 
                    ContentGeneratorAgent, CarouselGeneratorAgent, ImagePromptEnhancerAgent,
                    ImageGeneratorAgent)
    - Used for: Standardizing agent behavior and logging across the pipeline
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging


class BaseAgent(ABC):
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        pass
        
    def log_info(self, message: str):
        self.logger.info(f"[{self.name}] {message}")
        
    def log_error(self, message: str):
        self.logger.error(f"[{self.name}] {message}")
        
    def log_debug(self, message: str):
        self.logger.debug(f"[{self.name}] {message}")