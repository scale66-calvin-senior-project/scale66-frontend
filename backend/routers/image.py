"""
═══════════════════════════════════════════════════════════════════════════
                                IMAGE.PY
        IMAGE GENERATION API ROUTER - HANDLES TEXT-TO-IMAGE AND
         IMAGE-TO-IMAGE GENERATION USING GEMINI 2.5 FLASH IMAGE MODEL

ENDPOINTS:
    generate_image() -> GENERATES IMAGES USING TEXT OR IMAGE-TO-IMAGE PROMPTS
═══════════════════════════════════════════════════════════════════════════
"""

from fastapi import APIRouter, HTTPException  # type: ignore
from schemas.requests import ImageGenerationRequest
from schemas.responses import ImageGenerationResponse
from core.image_generator import generate_images
from config import get_settings

router = APIRouter(prefix="/image", tags=["image"])

@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    try:
        if not request.brand_id:
            raise HTTPException(status_code=400, detail="brand_id is required")
        
        settings = get_settings()
        
        result = generate_images(
            prompt=request.prompt,
            aspect_ratio=request.aspect_ratio,
            api_key=settings.gemini_api_key,
            input_image_path=request.input_image_path,
            brand_id=request.brand_id
        )
        
        print(f"✅ Saved generated image to: {result['saved_image_path']}")
        
        return ImageGenerationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
