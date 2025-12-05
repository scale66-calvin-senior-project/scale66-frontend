from typing import Dict, Optional

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import CaptionGeneratorInput, CaptionGeneratorOutput
from app.models.structured import ClaudeSlidesTextOutput
from app.agents.template_decider import CarouselFormat


FORMAT_TEXT_GUIDES: Dict[str, str] = {
    CarouselFormat.LISTICLE_TIPS: """
    Purpose: To convery information in a numbered list of tips/insights, one per slide.
    Caption Structure:
        Hook: A concise hook that attracts the ideal customer by targetting their pain points.
        Examples:
            1. "7 Ways to Start Social Media Marketing"
            2. "If you're a solopreneur, you need to know these 5 tips to get started"
            3. "Losing Weight has never been easier with these 5 tips"
            4. "Need more Leads? Try these 6 strategies"
            5. "8 Ways to Grow Your Social Media Audience"
        Body: A standalone tip, unrelated to other tips or external context that wouldn't be available to the target audience. One per slide.
        Examples:
            1. "Identify what you want to achieve with social media—whether it's brand awareness, lead generation, or sales. Then research and document your ideal customer profile, including demographics, interests, pain points, and where they spend time online."
            2. "Not all platforms are created equal. Select 2-3 platforms where your target audience is most active. Focus on quality over quantity—it's better to master one platform than to spread yourself thin across many."
            3. "Plan the types of content you'll post, posting frequency, and themes. A mix of educational, entertaining, and promotional content typically performs best. Consistency in posting schedule helps build audience engagement."
            4. "Use a clear profile picture, compelling bio with keywords, and link to your website. Make sure your brand voice and visual style are consistent across all platforms to build recognition."
            5. "Don't just broadcast—interact with your audience. Respond to comments, answer questions, and engage with content from accounts in your niche. Building relationships is key to growing organically."
            6. "Encourage customers to share their experiences with your product or service. Repost their content and give them credit. This builds trust, increases engagement, and provides authentic social proof."
    
    Sometimes, you may want to add a bonus/CTA to the end of the carousel. This should be done using the Brand Kit information.
    Things to avoid: 
        1. Do not include slide numbers in the caption text.
        2. Do not include any other text in the caption text other than the caption text itself.
        3. When creating caption text, always include more than usually expected. Aim for 15-30 words per caption. NEVER GO ABOVE 30 WORDS PER CAPTION.
        4. Each caption should be a standalone tip, unrelated to other tips or external context that wouldn't be available to the target audience.
    """,
}


class CaptionGenerator(BaseAgent[CaptionGeneratorInput, CaptionGeneratorOutput]):
    """
    Caption Generator Agent - Generates text captions for carousel slides.
    
    Input:
        format_type: str
        user_prompt: str
        brand_kit: BrandKit
        num_body_slides: int
        template_id: str
        hook_slide: str
        body_slide: str
        cta_slide: Optional[str]
    
    Output:
        hook_text: str
        body_texts: List[str]
        cta_text: Optional[str]
    """
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
