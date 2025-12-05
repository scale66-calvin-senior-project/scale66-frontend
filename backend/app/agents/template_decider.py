from typing import Dict, List, Optional
from enum import Enum

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import TemplateDeciderInput, TemplateDeciderOutput
from app.models.structured import ClaudeFormatSelectionOutput, ClaudeTemplateSelectionOutput
from app.services.template_service import template_service, TemplateMetadata


class CarouselFormat(str, Enum):
    LISTICLE_TIPS = "listicle_tips"


FORMAT_DESCRIPTIONS: Dict[str, str] = {
    CarouselFormat.LISTICLE_TIPS: """Numbered collection of discrete, standalone tips/insights, one per slide.

STRUCTURE: Numbered headline ("7 Ways to X") -> one item per slide -> bonus/CTA
CHARACTERISTICS: Scannable, save-worthy, satisfies completionist instinct

IDEAL FOR PROMPTS LIKE:
- "7 best habits before bed"
- "5 ways to grow social media quickly"
- "10 habits of successful people"
- "10 ways to grow brand awareness just starting out"

KEY CRITERIA (ALL must apply):
1. Content breaks into discrete, standalone items (each tip works independently)
2. Items are relatively unrelated to each other (no narrative thread required)
3. Natural numbered framing ("X ways to...", "X tips for...", "X mistakes...")
4. Each slide delivers complete value without needing other slides

NOT SUITABLE FOR:
- Sequential stories or journeys with a narrative arc
- Before/after transformations requiring context buildup
- Deep-dive explanations of a single concept
- Personal stories or case studies
- Content requiring progressive revelation""",
}


class TemplateDecider(BaseAgent[TemplateDeciderInput, TemplateDeciderOutput]):
    """
    Template Decider Agent - Selects carousel format and template.
    
    Input:
        user_prompt: str
        brand_kit: BrandKit
    
    Output:
        format_type: str
        num_body_slides: int
        template_id: str
        hook_slide: str
        body_slide: str
        cta_slide: Optional[str]
    """
    _instance: Optional['TemplateDecider'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        super().__init__()
    
    async def _validate_input(self, input_data: TemplateDeciderInput) -> None:
        pass
    
    async def _execute(self, input_data: TemplateDeciderInput) -> TemplateDeciderOutput:
        format_prompt = self._build_format_selection_prompt(input_data)
        
        format_output = await self.anthropic.generate_structured_output(
            prompt=format_prompt,
            output_model=ClaudeFormatSelectionOutput,
            max_tokens=500,
            temperature=0.3,
        )
        
        selected_format = format_output.format_type
        matching_templates = template_service.get_templates_for_format(selected_format)
        
        template_prompt = self._build_template_selection_prompt(
            input_data=input_data,
            format_type=selected_format,
            templates=matching_templates
        )
        
        template_output = await self.anthropic.generate_structured_output(
            prompt=template_prompt,
            output_model=ClaudeTemplateSelectionOutput,
            max_tokens=500,
            temperature=0.3,
        )
        
        selected_template_id = template_output.template_id
        selected_template = template_service.get_template(selected_template_id)
        if not selected_template:
            selected_template = matching_templates[0]
            selected_template_id = selected_template.id
        
        num_body_slides = format_output.num_body_slides
        selected_body_slide = selected_template.body_slides[0].slide if selected_template.body_slides else "1_body.png"
        
        cta_slide_filename = None
        if format_output.cta_slide and selected_template.cta_slide:
            cta_slide_filename = selected_template.cta_slide
        
        return TemplateDeciderOutput(
            step_name="template_decider",
            success=True,
            format_type=selected_format,
            num_body_slides=num_body_slides,
            template_id=selected_template_id,
            hook_slide=selected_template.hook_slide,
            body_slide=selected_body_slide,
            cta_slide=cta_slide_filename,
        )
    
    def _build_format_selection_prompt(self, input_data: TemplateDeciderInput) -> str:
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
    
    def _build_template_selection_prompt(
        self,
        input_data: TemplateDeciderInput,
        format_type: str,
        templates: List[TemplateMetadata]
    ) -> str:
        template_options = "\n".join([
            f"- {t.id}: {t.description}"
            for t in templates
        ])
        
        valid_ids = [t.id for t in templates]
        
        brand_kit = input_data.brand_kit
        
        return f"""You are an expert social media visual designer selecting the optimal TEMPLATE for a carousel.

The carousel format has been decided: {format_type}

Now select the best visual template based on the brand context and content topic.

---

AVAILABLE TEMPLATES:
{template_options}

---

SELECTION CRITERIA:

1. BRAND ALIGNMENT
   - Does the template's visual style match the brand's personality?
   - Consider: brand niche, brand style, target audience

2. CONTENT FIT
   - Does the template's aesthetic suit the content topic?
   - Some templates are better for professional content, others for casual/creative
   - Consider the tone and style of the content being created

---

CONTENT REQUEST:
"{input_data.user_prompt}"

BRAND CONTEXT:
- Brand Name: {brand_kit.brand_name}
- Brand Niche: {brand_kit.brand_niche}
- Brand Style: {brand_kit.brand_style}
- Product/Service Description: {brand_kit.product_service_desc}

Select the best template for this content. You MUST choose a template_id from: {valid_ids}"""


template_decider = TemplateDecider()
