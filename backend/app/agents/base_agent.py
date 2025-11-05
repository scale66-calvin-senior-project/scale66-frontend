from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


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