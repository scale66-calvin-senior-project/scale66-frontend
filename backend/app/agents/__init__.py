"""
AI Agents - Pipeline for automated carousel content generation.

This package contains the complete AI pipeline matching the MVP diagram:
1. Orchestrator - Manages entire pipeline flow
2. CarouselFormatDecider - Decides carousel format (step 2)
3. StrategyGenerator - Creates strategic guidance for slides (step 3)
4. ImageGenerator - Generates carousel images (step 4)
5. TextGenerator - Generates on-screen text (step 5)
6. Finalizer - Combines text + images (step 6)
"""

from .base_agent import BaseAgent
from .orchestrator import Orchestrator
from .carousel_format_decider import CarouselFormatDecider
from .strategy_generator import StrategyGenerator
from .text_generator import TextGenerator
from .image_generator import ImageGenerator
from .finalizer import Finalizer

__all__ = [
    "BaseAgent",
    "Orchestrator",
    "CarouselFormatDecider",
    "StrategyGenerator",
    "TextGenerator",
    "ImageGenerator",
    "Finalizer",
]

