from typing import List, Optional

from app.agents.base_agent import BaseAgent
from app.models.pipeline import TemplateDeciderInput, TemplateDeciderOutput
from app.models.structured import ClaudeTemplateSelectionOutput
from app.services.template_service import template_service, TemplateMetadata


class TemplateDecider(BaseAgent[TemplateDeciderInput, TemplateDeciderOutput]):
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
        matching_templates = template_service.get_templates_for_format(input_data.format_type)
        
        prompt = self._build_prompt(
            input_data=input_data,
            templates=matching_templates
        )
        
        template_output = await self.anthropic.generate_structured_output(
            prompt=prompt,
            output_model=ClaudeTemplateSelectionOutput,
            max_tokens=500,
            temperature=0.3,
        )
        
        selected_template_id = template_output.template_id
        selected_template = template_service.get_template(selected_template_id)
        if not selected_template:
            selected_template = matching_templates[0]
            selected_template_id = selected_template.id
        
        selected_body_slide = selected_template.body_slides[0].slide if selected_template.body_slides else "1_body.png"
        
        cta_slide_filename = None
        if input_data.include_cta and selected_template.cta_slide:
            cta_slide_filename = selected_template.cta_slide
        
        return TemplateDeciderOutput(
            step_name="template_decider",
            success=True,
            template_id=selected_template_id,
            hook_slide=selected_template.hook_slide,
            body_slide=selected_body_slide,
            cta_slide=cta_slide_filename,
        )
    
    def _build_prompt(
        self,
        input_data: TemplateDeciderInput,
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

The carousel format has been decided: {input_data.format_type}

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
