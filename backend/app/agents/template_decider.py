from typing import Dict, List, Optional
from enum import Enum

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import TemplateDeciderInput, TemplateDeciderOutput
from app.models.structured import ClaudeFormatSelectionOutput, ClaudeTemplateSelectionOutput
from app.services.ai.anthropic_service import AnthropicServiceError
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
    _instance: Optional['TemplateDecider'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        super().__init__()
    
    async def _validate_input(self, input_data: TemplateDeciderInput) -> None:
        if not input_data.user_prompt or not input_data.user_prompt.strip():
            raise ValidationError("user_prompt cannot be empty")
        
        if len(input_data.user_prompt.strip()) < 10:
            raise ValidationError("user_prompt must be at least 10 characters")
        
        if not input_data.brand_kit:
            raise ValidationError("brand_kit is required")
        
        required_fields = {
            "brand_name": input_data.brand_kit.brand_name,
            "brand_niche": input_data.brand_kit.brand_niche,
            "brand_style": input_data.brand_kit.brand_style,
            "product_service_desc": input_data.brand_kit.product_service_desc,
        }
        
        for field_name, field_value in required_fields.items():
            if not field_value or not str(field_value).strip():
                raise ValidationError(f"brand_kit.{field_name} is required")
    
    async def _execute(self, input_data: TemplateDeciderInput) -> TemplateDeciderOutput:
        try:
            format_prompt = self._build_format_selection_prompt(input_data)
            
            format_output = await self.anthropic.generate_structured_output(
                prompt=format_prompt,
                output_model=ClaudeFormatSelectionOutput,
                max_tokens=500,
                temperature=0.3,
            )
            
            selected_format = format_output.format_type
            
            matching_templates = template_service.get_templates_for_format(selected_format)
            
            if not matching_templates:
                raise ExecutionError(
                    f"No templates found for format '{selected_format}'. "
                    f"Available formats: {[t.carousel_format for t in template_service.list_all_templates()]}"
                )
            
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
            
            num_slides = selected_template.num_slides
            
            combined_rationale = (
                f"Format: {format_output.format_rationale} "
                f"Template: {template_output.template_rationale}"
            )
            
            return TemplateDeciderOutput(
                step_name="template_decider",
                success=True,
                format_type=selected_format,
                num_slides=num_slides,
                template_id=selected_template_id,
                format_rationale=combined_rationale,
            )
            
        except AnthropicServiceError as e:
            raise ExecutionError(f"LLM service error: {str(e)}")
        except Exception as e:
            raise ExecutionError(f"Unexpected error during execution: {str(e)}")
    
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

2. EVALUATE FORMAT FIT
   - Check EACH criterion in the format's "KEY CRITERIA" section
   - A format is a STRONG fit only if ALL criteria are met
   - Select the format that best matches the content structure

---

CONTENT REQUEST:
"{input_data.user_prompt}"

BRAND CONTEXT:
- Brand Name: {brand_kit.brand_name}
- Brand Niche: {brand_kit.brand_niche}
- Brand Style: {brand_kit.brand_style}
- Customer Pain Points: {pain_points}
- Product/Service Description: {brand_kit.product_service_desc}

Select the optimal carousel format for this content request. You MUST choose from the available format values listed above."""
    
    def _build_template_selection_prompt(
        self,
        input_data: TemplateDeciderInput,
        format_type: str,
        templates: List[TemplateMetadata]
    ) -> str:
        template_options = "\n".join([
            f"- {t.id} ({t.num_slides} slides): {t.description}"
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

3. SLIDE COUNT
   - Each template has a fixed number of slides
   - Consider if the content naturally fits that slide count

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
