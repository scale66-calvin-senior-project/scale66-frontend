# AI Service Usage - Strict Separation

This document outlines the strict separation of AI services in the carousel generation system.

## Service Responsibilities

### OpenAI - ALL TEXT TASKS
- ✅ Format selection and strategy
- ✅ Content generation (hooks, slide text, CTAs)
- ✅ Image prompt creation and enhancement
- ✅ Performance analysis
- ✅ All text processing and reasoning

### Gemini - IMAGE GENERATION ONLY
- ✅ Image generation from text prompts
- ❌ NO text enhancement
- ❌ NO prompt modification
- ❌ NO content generation

## Agent Breakdown

### 1. FormatSelectorAgent
- **Service:** OpenAI only
- **Task:** Analyze business context and select optimal carousel format
- **Input:** Business parameters (niche, audience, pain point, CTA goal)
- **Output:** Format selection with reasoning

### 2. ContentGeneratorAgent
- **Service:** OpenAI only
- **Task:** Create content strategy and slide text
- **Input:** Business context + selected format
- **Output:** Strategy + slide content (text only)

### 3. ImagePromptEnhancerAgent
- **Service:** OpenAI only
- **Task:** Create and enhance image generation prompts
- **Input:** Slide content + business context
- **Output:** Enhanced text prompts for image generation

### 4. ImageGeneratorAgent
- **Service:** Gemini only
- **Task:** Generate images from text prompts
- **Input:** Enhanced text prompts (from OpenAI)
- **Output:** Generated image files

### 5. CarouselGeneratorAgent (Orchestrator)
- **Service:** OpenAI only (for final performance analysis)
- **Task:** Coordinate all agents and generate TikTok performance analysis
- **Input:** All agent outputs
- **Output:** Complete carousel result

## Workflow Flow

```
Business Input → OpenAI (Format Selection) → OpenAI (Content Generation) 
→ OpenAI (Image Prompt Enhancement) → Gemini (Image Generation) 
→ OpenAI (Performance Analysis) → Complete Carousel
```

## Key Changes Made

1. **Removed Gemini text capabilities:**
   - Deleted `enhance_image_prompt()` from GeminiService
   - Deleted `enhance_text()` from GeminiService

2. **Updated ImagePromptEnhancerAgent:**
   - Removed Gemini service dependency
   - Uses only OpenAI for all text processing
   - Removed `_enhance_with_gemini()` method

3. **Updated ImageGeneratorAgent:**
   - Removed Gemini prompt enhancement calls
   - Directly uses OpenAI-enhanced prompts for Gemini image generation

4. **Verified separation:**
   - No OpenAI image generation calls anywhere
   - No Gemini text processing calls anywhere
   - Clear service boundaries maintained

## Testing Verification

All syntax checks pass:
- ✅ app/agents/format_selector.py
- ✅ app/agents/content_generator.py
- ✅ app/agents/image_prompt_enhancer.py
- ✅ app/agents/image_generator.py
- ✅ app/agents/carousel_generator.py
- ✅ app/services/gemini_service.py

## Benefits

1. **Clear Responsibility Separation:** Each AI service does what it's best at
2. **No Service Confusion:** Impossible to accidentally use wrong service
3. **Optimal Results:** OpenAI for language tasks, Gemini for visual tasks
4. **Easy Maintenance:** Clear boundaries make debugging and updates simple
5. **Cost Optimization:** Use most appropriate service for each task