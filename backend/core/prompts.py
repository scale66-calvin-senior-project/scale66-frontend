"""
═══════════════════════════════════════════════════════════════════════════
                                PROMPTS.PY
                    PROMPT PROCESSING FOR IMAGE GENERATION
═══════════════════════════════════════════════════════════════════════════
"""

from typing import Dict, Optional


def process_text_to_image_prompt(user_prompt: str, brand_data: Optional[Dict] = None) -> str:
    return user_prompt


def process_image_to_image_prompt(user_prompt: str, brand_data: Optional[Dict] = None) -> str:
    return user_prompt


def process_prompt(user_prompt: str, has_input_image: bool = False, brand_data: Optional[Dict] = None) -> str:
    if has_input_image:
        return process_image_to_image_prompt(user_prompt, brand_data)
    return process_text_to_image_prompt(user_prompt, brand_data)
