"""
═══════════════════════════════════════════════════════════════════════════
                                PROMPTS.PY
       PROMPT PROCESSING LOGIC - ENHANCES USER PROMPTS FOR TEXT-TO-IMAGE
        AND IMAGE-TO-IMAGE GENERATION WITH CONTEXT AND GUIDELINES

FUNCTIONS:
    process_text_to_image_prompt() -> ENHANCES PROMPT FOR TEXT-TO-IMAGE GENERATION
    process_image_to_image_prompt() -> ENHANCES PROMPT FOR IMAGE EDITING
    process_prompt() -> ROUTES TO APPROPRIATE PROMPT PROCESSOR
    format_brand_context() -> FORMATS BRAND DATA INTO STRUCTURED CONTEXT
═══════════════════════════════════════════════════════════════════════════
"""

from typing import Dict, Optional, List


def format_brand_context(brand_data: Dict) -> str:
    """Formats brand.json data into a structured context string for the AI"""
    
    context_parts = []
    
    # Brand identity
    context_parts.append(f"BRAND: {brand_data.get('brand_name', 'Unknown')}")
    context_parts.append(f"INDUSTRY: {brand_data.get('industry', 'Unknown')}")
    
    # Brand voice
    if 'brand_voice' in brand_data:
        voice = brand_data['brand_voice']
        context_parts.append(f"\nBRAND VOICE:")
        context_parts.append(f"  Tone: {voice.get('tone', 'N/A')}")
        context_parts.append(f"  Style: {voice.get('style', 'N/A')}")
        if 'keywords' in voice:
            keywords = ', '.join(voice['keywords'])
            context_parts.append(f"  Keywords: {keywords}")
    
    # Values
    if 'values' in brand_data:
        values = ', '.join(brand_data['values'])
        context_parts.append(f"\nBRAND VALUES: {values}")
    
    # Target audience
    if 'target_audience' in brand_data:
        audience = brand_data['target_audience']
        context_parts.append(f"\nTARGET AUDIENCE:")
        context_parts.append(f"  Demographics: {audience.get('demographics', 'N/A')}")
        if 'pain_points' in audience:
            pain_points = '; '.join(audience['pain_points'])
            context_parts.append(f"  Pain Points: {pain_points}")
    
    # Messaging
    if 'messaging' in brand_data:
        messaging = brand_data['messaging']
        context_parts.append(f"\nBRAND MESSAGING:")
        context_parts.append(f"  Tagline: {messaging.get('tagline', 'N/A')}")
        if 'key_messages' in messaging:
            context_parts.append(f"  Key Messages:")
            for msg in messaging['key_messages'][:3]:  # Limit to 3 key messages
                context_parts.append(f"    - {msg}")
    
    # Visual style from existing Instagram posts
    if 'instagram' in brand_data and brand_data['instagram']:
        context_parts.append(f"\nEXISTING VISUAL STYLE (from {len(brand_data['instagram'])} posts):")
        for i, post in enumerate(brand_data['instagram'][:3], 1):  # Show up to 3 examples
            if 'visual_description' in post:
                context_parts.append(f"  Example {i}: {post['visual_description']}")
    
    # Logo description
    if 'logo' in brand_data and 'description' in brand_data['logo']:
        context_parts.append(f"\nLOGO: {brand_data['logo']['description']}")
    
    return '\n'.join(context_parts)


def process_text_to_image_prompt(user_prompt: str, brand_data: Optional[Dict] = None) -> str:
    if not brand_data:
        return user_prompt
    
    # Extract specific brand elements
    brand_name = brand_data.get('brand_name', '')
    logo_description = brand_data.get('logo', {}).get('description', '')
    pain_points = brand_data.get('target_audience', {}).get('pain_points', [])
    tagline = brand_data.get('messaging', {}).get('tagline', '')
    call_to_action = brand_data.get('messaging', {}).get('call_to_action', '')
    
    # Build the prompt with brand context
    prompt_parts = [user_prompt]
    
    if brand_name:
        prompt_parts.append(f"\nBrand: {brand_name}")
    
    if logo_description:
        prompt_parts.append(f"Logo style: {logo_description}")
    
    if tagline:
        prompt_parts.append(f"Brand tagline: {tagline}")
    
    if pain_points:
        pain_points_str = ', '.join(pain_points)
        prompt_parts.append(f"Target audience pain points: {pain_points_str}")
    
    if call_to_action:
        prompt_parts.append(f"Call to action: {call_to_action}")
    
    final_prompt = '\n'.join(prompt_parts)
    
    return final_prompt


def process_image_to_image_prompt(user_prompt: str, brand_data: Optional[Dict] = None) -> str:
    final_prompt = f""" 

reference the logo and the visual style of the brand. 
{user_prompt} """
    
    return final_prompt


def process_prompt(user_prompt: str, has_input_image: bool = False, brand_data: Optional[Dict] = None) -> str:
    """Routes to appropriate prompt processor based on generation type"""
    if has_input_image:
        return process_image_to_image_prompt(user_prompt, brand_data)
    else:
        return process_text_to_image_prompt(user_prompt, brand_data)
