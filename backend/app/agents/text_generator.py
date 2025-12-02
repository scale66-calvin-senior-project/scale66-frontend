"""
Text Generator Agent - Step 4 of AI Pipeline

Input: TextGeneratorInput (hook_slide_strategy, body_slides_strategy)
Output: TextGeneratorOutput (hook_slide_text, body_slides_text)
"""

from typing import Dict, List, Optional

from app.agents.base_agent import BaseAgent, ValidationError, ExecutionError
from app.models.pipeline import TextGeneratorInput, TextGeneratorOutput
from app.models.structured import ClaudeTextOutput
from app.agents.carousel_format_decider import CarouselFormat
from app.services.ai.anthropic_service import AnthropicServiceError


# Format-specific text structure and tone guides
FORMAT_TEXT_GUIDES: Dict[str, str] = {
    CarouselFormat.LISTICLE_TIPS: """Text framework for numbered tips/insights carousel.

HOOK SLIDE TEXT:
Structure: Direct statement that promises numbered value. No fluff, no buildup.
Tone: Confident, declarative, slightly provocative. Creates urgency or curiosity.
Length: Short and punchy (5-15 words). The number does the heavy lifting.

GOOD HOOK EXAMPLES:
- "These 5 tips are vital for growing on social media"
- "Never made a social media post before for your brand? Start here."
- "7 foods that are cheap, easy to prepare and great for losing weight"
- "The 5 hidden benefits of frequent social interactions"
- "Solopreneurs: stop making these 5 mistakes on social media"

BAD HOOK PATTERNS (AVOID):
- Generic openers: "Here's how to...", "Let me show you...", "Did you know..."
- Questions without tension: "Want to grow your business?"
- Clickbait without substance: "This ONE trick will change everything"
- Passive voice: "Social media growth can be achieved by..."

---

BODY SLIDE TEXT:
Structure: Lead with the insight, follow with context or action. Each tip is STANDALONE.
Tone: Direct and actionable. Conversational but authoritative. No hedge words.
Length: Match complexity. Simple insight = short (5-10 words). Complex strategy = long (20-35 words). When in doubt, go longer—a confusing short caption is worse than a clear long one.

GOOD BODY EXAMPLES:
- "Niche down." (simple insight, universally understood)
- "Consistency beats perfection." (simple insight, common wisdom)
- "Post when your audience is online, not when you feel like it." (tactical, needs contrast)
- "Done is better than perfect. Post that imperfect content and iterate." (tactical, reframes anxiety)
- "Build relationships, not just followers. Engage authentically with your niche community daily—comment thoughtfully, share others' content, and create conversation. These connections become your growth engine." (complex strategy, explains why and how)
- "The algorithm rewards engagement velocity. Reply to every comment within the first hour of posting—this signals relevance and boosts your reach to new audiences." (complex, explains mechanism)

BAD BODY PATTERNS (AVOID):
- Too short for complexity: "Ask questions that spark opinions" (confusing without context)
- Vague advice: "Be consistent" (no context or action)
- Starting with "You should..." or "You need to..."
- Filler phrases: "It's important to note that...", "One thing to keep in mind..."
- Incomplete thoughts that require reading other slides
- Questions instead of statements
- Number prefixes like "Number 1:", "Tip 2:" (the slide position already shows this)

---

IN-GROUP LANGUAGE:
Use words that signal who this content is FOR. Target audience should feel "this is for me."
- "Solopreneurs" not "business owners" (if targeting solopreneurs)
- "Founders" not "entrepreneurs" (if targeting startup founders)
- "Creators" not "people who make content" (if targeting content creators)
- Use niche-specific terms the audience uses to describe themselves

---

PARALLEL STRUCTURE (CRITICAL):
ALL body slides MUST use the same grammatical pattern. Decide the pattern and stick to it.

PICK ONE pattern for all body slides:
- Verb-first: "Post consistently...", "Engage daily...", "Batch your content..."
- Noun-first: "Consistency is...", "Engagement means...", "Content batching..."
- Short declarative: "Niche down.", "Stay consistent.", "Engage first."

DO NOT MIX patterns. If slide 1 starts with a verb, ALL slides start with verbs.
DO NOT use number prefixes ("Number 1:", "Tip 2:") - the slide position already indicates this.
""",
}


class TextGenerator(BaseAgent[TextGeneratorInput, TextGeneratorOutput]):
    """
    Converts strategy guidance into final slide text for carousels.
    
    Uses Claude Sonnet 4.5 with format-specific text guides to generate
    slide text that matches the structure and tone required by each format.
    No image analysis - runs before image generation.
    Singleton pattern ensures single instance across application.
    """
    
    _instance: Optional['TextGenerator'] = None
    
    def __new__(cls):
        """Singleton instance creation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize text generator agent."""
        super().__init__()
    
    async def _validate_input(self, input_data: TextGeneratorInput) -> None:
        """
        Validate input data before execution.
        
        Checks:
        - Brand kit is complete with required fields
        - Format type is valid
        - Complete strategy is not empty
        - Hook slide strategy is not empty
        - Body slides strategy array is valid and within limits
        - All strategy strings are valid
        
        Args:
            input_data: Text generator input schema
            
        Raises:
            ValidationError: If input is invalid
        """
        # Validate brand_kit
        if not input_data.brand_kit:
            raise ValidationError("brand_kit is required")
        
        # Check required brand kit fields
        required_fields = {
            "brand_name": input_data.brand_kit.brand_name,
            "brand_niche": input_data.brand_kit.brand_niche,
            "brand_style": input_data.brand_kit.brand_style,
            "product_service_desc": input_data.brand_kit.product_service_desc,
        }
        
        for field_name, field_value in required_fields.items():
            if not field_value or not str(field_value).strip():
                raise ValidationError(f"brand_kit.{field_name} is required")
        
        # Validate format_type
        if not input_data.format_type or not input_data.format_type.strip():
            raise ValidationError("format_type is required")
        
        # Validate complete_strategy
        if not input_data.complete_strategy or not input_data.complete_strategy.strip():
            raise ValidationError("complete_strategy cannot be empty")
        
        if len(input_data.complete_strategy.strip()) < 10:
            raise ValidationError("complete_strategy must be at least 10 characters")
        
        # Validate hook_slide_strategy
        if not input_data.hook_slide_strategy or not input_data.hook_slide_strategy.strip():
            raise ValidationError("hook_slide_strategy cannot be empty")
        
        if len(input_data.hook_slide_strategy.strip()) < 10:
            raise ValidationError("hook_slide_strategy must be at least 10 characters")
        
        # Validate body_slides_strategy
        if not input_data.body_slides_strategy:
            raise ValidationError("body_slides_strategy cannot be empty")
        
        if not isinstance(input_data.body_slides_strategy, list):
            raise ValidationError("body_slides_strategy must be a list")
        
        if len(input_data.body_slides_strategy) < 2:
            raise ValidationError("body_slides_strategy must contain at least 2 slides")
        
        if len(input_data.body_slides_strategy) > 9:
            raise ValidationError("body_slides_strategy cannot contain more than 9 slides")
        
        # Validate each body slide strategy
        for i, strategy in enumerate(input_data.body_slides_strategy):
            if not strategy or not isinstance(strategy, str) or not strategy.strip():
                raise ValidationError(f"body_slides_strategy[{i}] is empty or invalid")
            
            if len(strategy.strip()) < 5:
                raise ValidationError(
                    f"body_slides_strategy[{i}] must be at least 5 characters"
                )
        
        self.logger.debug("Input validation passed")
    
    async def _execute(self, input_data: TextGeneratorInput) -> TextGeneratorOutput:
        """
        Execute text generation for all slides.
        
        Args:
            input_data: Validated input data
            
        Returns:
            Generated text for the hook and body slides
            
        Raises:
            ExecutionError: If text generation fails
        """
        try:
            total_slides = 1 + len(input_data.body_slides_strategy)
            self.logger.debug(f"Generating text for {total_slides} slides")
            
            # Log the text guide being used
            text_guide = FORMAT_TEXT_GUIDES.get(input_data.format_type, "Default text approach")
            self.logger.info(f"Text Guide: {text_guide}")
            
            # Generate hook slide text
            self.logger.debug("Generating hook slide text")
            hook_text, hook_rationale = await self._generate_text(
                input_data=input_data,
                strategy=input_data.hook_slide_strategy,
                is_hook=True,
            )
            
            # Generate body slides text (pass previous texts for parallel structure)
            body_texts: List[str] = []
            body_rationales: List[str] = []
            
            for i, strategy in enumerate(input_data.body_slides_strategy):
                self.logger.debug(f"Generating body slide text {i+1}/{len(input_data.body_slides_strategy)}")
                body_text, body_rationale = await self._generate_text(
                    input_data=input_data,
                    strategy=strategy,
                    is_hook=False,
                    previous_body_texts=body_texts,  # Pass previous texts for parallel structure
                )
                body_texts.append(body_text)
                body_rationales.append(body_rationale)
            
            # Combine all rationales for logging
            all_rationales = [hook_rationale] + body_rationales
            
            self.logger.info(
                f"Text generation completed: "
                f"1 hook + {len(body_texts)} body texts"
            )
            
            return TextGeneratorOutput(
                step_name="text_generator",
                success=True,
                hook_slide_text=hook_text,
                body_slides_text=body_texts,
                captions_rationale=all_rationales,
            )
            
        except AnthropicServiceError as e:
            raise ExecutionError(f"Text generation service error: {str(e)}")
        except Exception as e:
            raise ExecutionError(f"Unexpected error during text generation: {str(e)}")
    
    async def _generate_text(
        self,
        input_data: TextGeneratorInput,
        strategy: str,
        is_hook: bool,
        previous_body_texts: Optional[List[str]] = None,
    ) -> tuple[str, str]:
        """
        Generate slide text from strategy guidance using format-specific text guide.
        
        Args:
            input_data: Full input data for context
            strategy: The strategy for this slide
            is_hook: Whether this is the hook slide
            previous_body_texts: Previously generated body texts (for parallel structure)
            
        Returns:
            Tuple of (text, rationale)
            
        Raises:
            ExecutionError: If generation fails
        """
        try:
            system_prompt = self._build_system_prompt(input_data.format_type, is_hook)
            user_prompt = self._build_user_prompt(
                complete_strategy=input_data.complete_strategy,
                slide_strategy=strategy,
                is_hook=is_hook,
                previous_body_texts=previous_body_texts,
            )
            
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            self.logger.debug(f"Generating text for {'hook' if is_hook else 'body'} slide")
            
            # Call Claude with structured output for guaranteed valid response
            text_output = await self.anthropic.generate_structured_output(
                prompt=full_prompt,
                output_model=ClaudeTextOutput,
                max_tokens=4096,
                temperature=0.9,
            )
            
            slide_text = text_output.caption.strip()
            
            self.logger.debug(
                f"Generated text ({len(slide_text)} chars): {slide_text}"
            )
            
            return slide_text, text_output.rationale.strip()
            
        except AnthropicServiceError as e:
            raise ExecutionError(f"Failed to generate text: {str(e)}")
        except Exception as e:
            raise ExecutionError(f"Unexpected error in text generation: {str(e)}")
    
    def _build_system_prompt(self, format_type: str, is_hook: bool) -> str:
        """
        Build system prompt for text generation.
        
        Args:
            format_type: The carousel format type
            is_hook: Whether this is the hook slide
            
        Returns:
            System prompt string
        """
        text_guide = FORMAT_TEXT_GUIDES.get(format_type)
        slide_type = "HOOK" if is_hook else "BODY"
        
        return f"""You are an expert carousel copy writer who creates FINAL SLIDE TEXT for social media carousels.

YOUR ROLE:
- Write final, ready-to-use text that goes directly on slides
- Use the STRATEGY to know WHAT to communicate
- Use the FORMAT TEXT GUIDE to know HOW to write it

CRITICAL RULES:

1. OUTPUT IS FINAL. Your text goes directly onto slides. No placeholders, no suggestions, no alternatives.

2. FORMAT TEXT GUIDE IS YOUR PRIMARY REFERENCE. It defines structure, tone, length, good examples, and bad patterns for this specific format. Follow it closely.

3. STRATEGY PROVIDES INTENT. The complete strategy and slide strategy tell you what message to convey. The FORMAT TEXT GUIDE tells you how to phrase it.

4. PARALLEL STRUCTURE FOR BODY SLIDES. If previous body slides are provided, match their grammatical pattern exactly.

---

FORMAT: {format_type}
SLIDE TYPE: {slide_type}

FORMAT TEXT GUIDE:
{text_guide}

---

OUTPUT:
- caption: The exact text for this slide
- rationale: Brief explanation of how this follows the format guide"""
    
    def _build_user_prompt(
        self,
        complete_strategy: str,
        slide_strategy: str,
        is_hook: bool,
        previous_body_texts: Optional[List[str]] = None,
    ) -> str:
        """
        Build user prompt for text generation.
        
        Args:
            complete_strategy: The complete carousel strategy for context
            slide_strategy: The strategy for this slide
            is_hook: Whether this is the hook slide
            previous_body_texts: Previously generated body texts (for parallel structure)
            
        Returns:
            User prompt string
        """
        # Build previous slides context for parallel structure
        previous_slides_section = ""
        if not is_hook and previous_body_texts:
            previous_texts_formatted = "\n".join(
                f"- Slide {i+2}: \"{text}\"" 
                for i, text in enumerate(previous_body_texts)
            )
            previous_slides_section = f"""
PREVIOUS BODY SLIDES:
{previous_texts_formatted}
"""
        
        return f"""COMPLETE STRATEGY:
"{complete_strategy}"

THIS SLIDE'S STRATEGY:
"{slide_strategy}"
{previous_slides_section}
Based on the complete strategy, this slide's strategy, and the FORMAT TEXT GUIDE, generate the slide text."""


text_generator = TextGenerator()