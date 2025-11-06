from typing import Dict, Any, List
from .base_agent import BaseAgent
from .format_selector import FormatSelectorAgent
from .content_generator import ContentGeneratorAgent
from .image_prompt_enhancer import ImagePromptEnhancerAgent
from ..models.pipeline import StoryRequest, CarouselResult, CarouselSlide


class CarouselGeneratorAgent(BaseAgent):
    """Orchestrator agent that coordinates multiple specialized agents for carousel generation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        
        # Initialize specialized agents
        self.format_selector = FormatSelectorAgent(config)
        self.content_generator = ContentGeneratorAgent(config)
        self.image_prompt_enhancer = ImagePromptEnhancerAgent(config)
        
    async def process(self, story_request: StoryRequest) -> CarouselResult:
        """Generate a complete TikTok carousel using agentic workflow"""
        
        try:
            self.log_info(f"Starting agentic carousel generation for {story_request.niche}")
            
            # Step 1: Format Selection (OpenAI)
            self.log_info("Step 1: Selecting optimal carousel format...")
            carousel_format = await self.format_selector.process(story_request)
            self.log_info(f"Selected format: {carousel_format.format_name}")
            
            # Step 2: Content Generation (OpenAI)
            self.log_info("Step 2: Generating content strategy and slides...")
            content_data = await self.content_generator.process({
                "story_request": story_request,
                "carousel_format": carousel_format
            })
            
            strategy = content_data["strategy"]
            slides = content_data["slides"]
            self.log_info(f"Generated {len(slides)} slides with strategy")
            
            # Step 3: Image Prompt Enhancement (OpenAI only)
            self.log_info("Step 3: Enhancing image prompts...")
            enhanced_slides = await self.image_prompt_enhancer.process({
                "slides": slides,
                "story_request": story_request,
                "strategy": strategy
            })
            
            # Step 4: Generate performance analysis
            self.log_info("Step 4: Generating performance analysis...")
            why_this_works = await self._generate_performance_analysis(
                story_request, carousel_format, strategy, enhanced_slides
            )
            
            # Create final result
            carousel_result = CarouselResult(
                format_type=carousel_format.format_name,
                strategy=strategy,
                slides=enhanced_slides,
                why_this_works=why_this_works
            )
            
            self.log_info("Agentic carousel generation completed successfully")
            return carousel_result
            
        except Exception as e:
            raise Exception(f"Failed to generate carousel: {str(e)}")
    
    async def _generate_performance_analysis(self, story_request, carousel_format, strategy, slides) -> List[str]:
        """Generate analysis of why this carousel will perform well on TikTok"""
        
        from ..services.openai_service import OpenAIService
        openai_service = OpenAIService(self.config)
        
        analysis_prompt = f"""You are a TikTok algorithm expert. Analyze why this carousel will perform well on TikTok.

## CAROUSEL DETAILS:
**Format:** {carousel_format.format_name}
**Target Audience:** {story_request.target_audience}
**Niche:** {story_request.niche}
**Goal:** {story_request.cta_goal}

**Strategy:**
- Hook: {strategy.hook_strategy}
- Flow: {strategy.content_flow}
- Tactics: {', '.join(strategy.engagement_tactics)}
- CTA: {strategy.cta_approach}

**Slides:**
{self._format_slides_for_analysis(slides)}

## YOUR TASK:
Provide 5-7 specific reasons why this carousel will perform well on TikTok, considering:
- Hook effectiveness for stopping scroll
- Emotional arc and engagement retention
- Value proposition and save-worthiness
- Comment/share triggers
- Algorithm-friendly elements
- Target audience psychology

Format as a JSON list of strings:
["reason 1", "reason 2", "reason 3", ...]"""
        
        try:
            response = await openai_service.generate_text(
                prompt=analysis_prompt,
                max_tokens=800,
                temperature=0.4
            )
            
            # Parse JSON response
            import json
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback to manual parsing
                lines = response.strip().split('\n')
                return [line.strip('- "').strip('"') for line in lines if line.strip()]
                
        except Exception as e:
            self.log_error(f"Failed to generate performance analysis: {e}")
            return [
                "Strong hook targets specific audience pain point",
                "Content format optimized for engagement retention", 
                "Clear value proposition encourages saves",
                "Strategic CTA aligned with content goal",
                "Visual consistency supports brand recognition"
            ]
    
    def _format_slides_for_analysis(self, slides) -> str:
        """Format slides for performance analysis"""
        formatted = []
        for slide in slides:
            formatted.append(f"Slide {slide.slide_number}: {slide.slide_purpose} - '{slide.text_on_screen}'")
        return '\n'.join(formatted)