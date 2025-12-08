from typing import Optional

from app.agents.base_agent import BaseAgent
from app.models.pipeline import FormatDeciderInput, FormatDeciderOutput
from app.models.structured import ClaudeFormatSelectionOutput
from app.constants import FORMAT_DESCRIPTIONS


class FormatDecider(BaseAgent[FormatDeciderInput, FormatDeciderOutput]):
    """
    Format Decider Agent - Selects carousel format and slide count.
    
    Input:
        user_prompt: str
        brand_kit: BrandKit
    
    Output:
        format_type: str
        num_body_slides: int
        include_cta: bool
    """
    _instance: Optional['FormatDecider'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        super().__init__()
    
    async def _validate_input(self, input_data: FormatDeciderInput) -> None:
        pass
    
    async def _execute(self, input_data: FormatDeciderInput) -> FormatDeciderOutput:
        prompt = self._build_prompt(input_data)
        
        format_output = await self.anthropic.generate_structured_output(
            prompt=prompt,
            output_model=ClaudeFormatSelectionOutput,
            max_tokens=500,
            temperature=0.3,
        )
        
        return FormatDeciderOutput(
            step_name="format_decider",
            success=True,
            format_type=format_output.format_type,
            num_body_slides=format_output.num_body_slides,
            include_cta=format_output.cta_slide,
        )
    
    def _build_prompt(self, input_data: FormatDeciderInput) -> str:
        format_list = "\n".join([
            f"### {fmt.value}\n{desc}"
            for fmt, desc in FORMAT_DESCRIPTIONS.items()
        ])
        
        brand_kit = input_data.brand_kit
        pain_points = ", ".join(brand_kit.customer_pain_points) if brand_kit.customer_pain_points else "Not provided"
        
        return f"""You are an expert social media marketing strategist selecting the optimal carousel FORMAT for a content request.

AVAILABLE FORMATS:
{format_list}

---

DECISION FRAMEWORK:

1. ANALYZE THE USER'S REQUEST
   - What type of content are they asking for?
   - Does it naturally break into discrete items, or is it a continuous narrative?
   - Is there an implied structure (list, story, comparison, etc.)?
   - How many distinct points/tips/items does this content naturally contain?

2. EVALUATE FORMAT FIT
   - Check EACH criterion in the format's "KEY CRITERIA" section
   - A format is a STRONG fit only if ALL criteria are met
   - Select the format that best matches the content structure

3. DETERMINE NUMBER OF BODY SLIDES
   - Body slides are the main content slides (not including hook or CTA)
   - Count the natural number of distinct points/tips/items in the user's request
   - Range: 1-8 body slides (most common: 3-7)
   - Examples: "5 tips" = 5 body slides, "7 ways" = 7 body slides, "best practices" = 4-6 body slides
   - If user specifies a number (e.g., "5 tips"), use that number
   - If not specified, choose based on topic complexity and content depth

4. DECIDE IF CTA SLIDE IS NEEDED
   - CTA (Call-To-Action) slides drive specific user actions: engagement, sales, follows, website visits, conversions
   - INCLUDE CTA (true) when:
     * Content is promotional or marketing-focused
     * Brand has clear product/service to promote
     * Goal is to drive action (sign up, buy, follow, visit website)
     * Customer pain points suggest need for solution/offer
   - SKIP CTA (false) when:
     * Purely educational or informational content
     * Storytelling or brand awareness focus
     * No clear action or conversion goal
     * Content is meant to provide value without asking for anything
   - Consider brand context and customer journey stage

---

CONTENT REQUEST:
"{input_data.user_prompt}"

BRAND CONTEXT:
- Brand Name: {brand_kit.brand_name}
- Brand Niche: {brand_kit.brand_niche}
- Brand Style: {brand_kit.brand_style}
- Customer Pain Points: {pain_points}
- Product/Service Description: {brand_kit.product_service_desc}

Select the optimal carousel format, determine the number of body slides needed, and decide if a CTA slide should be included. You MUST choose from the available format values listed above."""


format_decider = FormatDecider()

