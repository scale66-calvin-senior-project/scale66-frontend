from typing import List, Optional

from app.agents.base_agent import BaseAgent
from app.models.pipeline import TemplateDeciderInput, TemplateDeciderOutput
from app.models.structured import ClaudeFormatSelectionOutput, ClaudeTemplateSelectionOutput
from app.services.template_service import template_service, TemplateMetadata
from app.constants import FORMAT_DESCRIPTIONS


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
        template_details = []
        for t in templates:
            body_desc = ""
            if t.body_slides:
                body_descriptions = "\n     ".join([
                    f"Body Slide {i+1}: {slide.description}"
                    for i, slide in enumerate(t.body_slides)
                ])
                body_desc = f"\n   - Body Slides:\n     {body_descriptions}"
            
            cta_desc = f"\n   - CTA Slide: {t.cta}" if t.cta else ""
            
            template_detail = f"""Template: {t.id}
   - Overview: {t.description}
   - Hook Slide: {t.hook}{body_desc}{cta_desc}"""
            template_details.append(template_detail)
        
        template_info = "\n\n".join(template_details)
        valid_ids = [t.id for t in templates]
        brand_kit = input_data.brand_kit
        
        return f"""You are an expert social media visual designer selecting the optimal TEMPLATE for a carousel.

The carousel format has been decided: {format_type}

Now select the best visual template based on the brand context and content topic by analyzing the detailed visual descriptions provided.

---

AVAILABLE TEMPLATES WITH DETAILED DESCRIPTIONS:

{template_info}

---

SELECTION CRITERIA:

1. VISUAL STYLE ALIGNMENT
   - Does the template's described visual style match the brand's personality?
   - Consider typography, color palette, layout, and design elements from descriptions
   - Match design style to brand: Modern, classic, playful, sophisticated, minimal, bold

2. BRAND ALIGNMENT
   - Does the template's visual language match the brand's personality and niche?
   - Brand Niche: {brand_kit.brand_niche}
   - Brand Style: {brand_kit.brand_style}
   - Consider: Would the target audience resonate with this aesthetic?

3. CONTENT FIT
   - Does the template's aesthetic suit the content topic?
   - Professional content benefits from: Clean, sophisticated, editorial designs
   - Creative/casual content benefits from: Playful, bold, illustrated designs
   - Luxury/premium content benefits from: High contrast, elegant, refined designs
   - Educational content benefits from: Clear hierarchy, readable, organized layouts
   - Nature/wellness content benefits from: Organic, fresh, calming aesthetics

4. CONSISTENCY ACROSS SLIDES
   - Do hook, body, and CTA descriptions show visual consistency?
   - Is the design system cohesive and professional?

---

CONTENT REQUEST:
"{input_data.user_prompt}"

BRAND CONTEXT:
- Brand Name: {brand_kit.brand_name}
- Brand Niche: {brand_kit.brand_niche}
- Brand Style: {brand_kit.brand_style}
- Product/Service Description: {brand_kit.product_service_desc}

---

TASK:
Based on the detailed visual descriptions provided, select the template that best matches the brand's visual identity and suits the content topic.

You MUST choose a template_id from: {valid_ids}"""


template_decider = TemplateDecider()
