"""
Carousel Format Definitions and Text Generation Guides.

This module contains all format-related configuration for carousel generation:
- CarouselFormat enum defining available formats
- FORMAT_DESCRIPTIONS for format selection prompts
- FORMAT_TEXT_GUIDES for caption generation prompts
"""

from typing import Dict
from enum import Enum


class CarouselFormat(str, Enum):
    LISTICLE_TIPS = "listicle_tips"
    EDUCATIONAL_TUTORIAL = "educational_tutorial"
    DATA_INSIGHT_AUTHORITY = "data_insight_authority"


FORMAT_DESCRIPTIONS: Dict[str, str] = {
    CarouselFormat.LISTICLE_TIPS: """Numbered collection of discrete, standalone tips/insights, one per slide.
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

    CarouselFormat.EDUCATIONAL_TUTORIAL: """Step-by-step walkthrough to solving a problem in someone's life.
KEY CRITERIA (ALL must apply):
1. Content follows a sequential, progressive structure (each step builds on previous steps)
2. Focuses on solving a specific problem or achieving a specific outcome
3. Steps are logically ordered and interconnected (later steps depend on earlier ones)
4. Each slide represents a distinct step in the problem-solving process
5. Content guides the reader through a complete journey from problem to solution

NOT SUITABLE FOR:
- Standalone tips or insights that work independently
- Numbered lists of unrelated items
- Content where order doesn't matter
- General advice without a clear problem-solution structure
- Tips that don't build on each other sequentially""",

    CarouselFormat.DATA_INSIGHT_AUTHORITY: """Carousel built around research, statistics, trend data, or analytical findings with clear visualization.
KEY CRITERIA (ALL must apply):
1. Content is built around genuine research, statistics, trend data, or analytical findings (no fabrication)
2. Requires actual data or research to back all claims and insights
3. Structure follows: bold headline statistic → context/methodology → supporting data points visualized → implications/analysis → actionable conclusions → CTA
4. Establishes thought leadership and authority through substantiated insights
5. Data visualization is central to the content presentation

NOT SUITABLE FOR:
- Content without actual data, research, or statistics to support claims
- Fabricated or made-up statistics or research findings
- Opinion-based content without data backing
- Emotional content without data foundation
- General tips or advice not supported by research
- Content where data visualization isn't central to the message"""
}


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

