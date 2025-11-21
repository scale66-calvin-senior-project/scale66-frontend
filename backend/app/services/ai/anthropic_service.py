"""
Anthropic Service - Anthropic API integration.

Provides:
- Text generation using Claude models
- Vision analysis using Claude Vision

Used by agents for LLM calls and text generation.
"""

import logging
import base64
import httpx
from typing import Optional, List
from anthropic import Anthropic, AsyncAnthropic
from app.core.config import settings


logger = logging.getLogger(__name__)

class AnthropicServiceError(Exception):
    """Base exception for Anthropic service errors."""
    pass

class AnthropicService:
    """
    Anthropic service for text generation and vision analysis.
    Default Model: claude-sonnet-4-5 (configured in settings)
    """

    _instance: Optional['AnthropicService'] = None
    _client: Optional[AsyncAnthropic] = None

    def __new__(cls):
        """Singleton instance creation."""
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance
    
    def __init__(self):
        """
        Initialization of the Anthropic service.
        """

        if self._client is None:
            try: 
                self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                raise AnthropicServiceError(f"Failed to initialize Anthropic client: {e}")
                
    
    async def generate_text(
        self, 
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate text using Anthropic's Claude Sonnet 4.5 model.
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_prompt: Optional system prompt to set the behavior of the model
            
        Returns:
            Generated text as a string
        """
        try:
            logger.info(f"Generating text with model: {settings.anthropic_model}")

            response = await self._client.messages.create(
                model=settings.anthropic_model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text.strip()
            logger.info(f"Generated text: {response_text}")

            return response_text
    

    async def analyze_image(
        self, 
        image_url: str,
        prompt: str,
        max_tokens: int = 4096,
    ) -> str:
        """
        Analyze image using Anthropic's Claude Vision model.
        
        Args:
            image_url: The URL of the image to analyze
            prompt: The prompt to send to the LLM
            max_tokens: The maximum number of tokens to generate

        Returns:
            Analysis result as a string
        """
        try:
            logger.info(f"Analyzing image: {image_url}")
            image_data = base64.standard_b64encode(httpx.get(image_url).content).decode("utf-8")

            response = await self._client.messages.create(
                model=settings.anthropic_model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        
        return response.content[0].text
        ```
        
        Use case: Finalizer agent analyzes images to decide text positioning.
        """
        # TODO: Implement vision analysis
        pass
    
    async def analyze_image_base64(
        self, 
        image_base64: str,
        prompt: str,
        detail: str = "auto"
    ) -> str:
        """
        Analyze image from base64 data using Claude Vision.
        
        Args:
            image_base64: Base64 encoded image
            prompt: Analysis prompt
            detail: Detail level
            
        Returns:
            Analysis result
        
        TODO: Implement base64 vision analysis:
        ```python
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        
        return response.content[0].text
        ```
        """
        # TODO: Implement base64 vision analysis
        pass
    
    async def generate_embeddings(
        self, 
        text: str,
        model: str = "voyage-large--instruct"
    ) -> List[float]:
        """
        Generate embeddings for text.
        
        Args:
            text: Input text
            model: Embedding model (using Voyage AI as recommended by Anthropic)
            
        Returns:
            Embedding vector
        
        TODO: Implement embeddings via Voyage AI:
        ```python
        import voyageai
        
        vo = voyageai.Client()
        result = vo.embed([text], model=model, input_type="document")
        
        return result.embeddings[0]
        ```
        
        Use case: Semantic search, similarity matching for brand kits.
        
        Note: Anthropic recommends Voyage AI for embeddings as they don't provide
        their own embedding models. Voyage AI is optimized for use with Claude.
        """
        # TODO: Implement embeddings
        pass


# Create singleton instance
anthropic_service = AnthropicService()