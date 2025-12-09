from typing import Optional

from app.agents.base_agent import BaseAgent
from app.models.pipeline import CaptionGeneratorInput, CaptionGeneratorOutput
from app.models.structured import ClaudeSlidesTextOutput
from app.constants import FORMAT_TEXT_GUIDES


class CaptionGenerator(BaseAgent[CaptionGeneratorInput, CaptionGeneratorOutput]):
    _instance: Optional['CaptionGenerator'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        super().__init__()
    
    async def _validate_input(self, input_data: CaptionGeneratorInput) -> None:
        pass
    
    async def _execute(self, input_data: CaptionGeneratorInput) -> CaptionGeneratorOutput:
        prompt = self._build_prompt(input_data)
        
        text_output = await self.anthropic.generate_structured_output(
            prompt=prompt,
            output_model=ClaudeSlidesTextOutput,
            max_tokens=4096,
            temperature=0.9,
        )
        
        expected_body_count = input_data.num_body_slides
        if len(text_output.body_texts) != expected_body_count:
            if len(text_output.body_texts) < expected_body_count:
                while len(text_output.body_texts) < expected_body_count:
                    text_output.body_texts.append("[Content continues...]")
            else:
                text_output.body_texts = text_output.body_texts[:expected_body_count]
        
        has_cta = input_data.cta_slide is not None
        if has_cta and not text_output.cta_text:
            text_output.cta_text = "Follow for more tips!"
        
        return CaptionGeneratorOutput(
            step_name="caption_generator",
            success=True,
            hook_text=text_output.hook_text,
            body_texts=text_output.body_texts,
            cta_text=text_output.cta_text if has_cta else None,
        )
    
    def _build_prompt(self, input_data: CaptionGeneratorInput) -> str:
        text_guide = FORMAT_TEXT_GUIDES.get(input_data.format_type, "")
        brand_kit = input_data.brand_kit
        pain_points = ", ".join(brand_kit.customer_pain_points) if brand_kit.customer_pain_points else "Not provided"
        
        # Determine slide structure
        has_cta = input_data.cta_slide is not None
        
        return f"""You are a social media caption writer. Generate carousel slide captions with the following structure:

REQUIRED OUTPUT STRUCTURE:
- hook_text: 1 attention-grabbing opening slide caption
- body_texts: {input_data.num_body_slides} main content slide captions (array)
{"- cta_text: 1 compelling call-to-action slide caption" if has_cta else ""}

{text_guide}

BRAND CONTEXT:
- Name: {brand_kit.brand_name}
- Niche: {brand_kit.brand_niche}
- Style: {brand_kit.brand_style}
- Product/Service: {brand_kit.product_service_desc}
- Customer Pain Points: {pain_points}

USER REQUEST: {input_data.user_prompt}

Generate the captions as structured above. {"The CTA should drive user action (follow, visit website, buy, engage, etc.)." if has_cta else ""}"""


caption_generator = CaptionGenerator()
