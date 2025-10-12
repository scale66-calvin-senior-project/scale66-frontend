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
from core.image_generator import generate_images, load_brand_image, save_generated_image
from config import get_settings

router = APIRouter(prefix="/image", tags=["image"])

@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    try:
        settings = get_settings()
        
        input_image_base64 = None
        
        if request.brand_id and request.input_image_path:
            try:
                input_image_base64 = load_brand_image(
                    request.brand_id, 
                    request.input_image_path
                )
            except FileNotFoundError as e:
                raise HTTPException(
                    status_code=404,
                    detail=str(e)
                )
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=str(e)
                )
        
        elif request.input_image:
            input_image_base64 = request.input_image
        
        result = generate_images(
            prompt=request.prompt,
            aspect_ratio=request.aspect_ratio,
            api_key=settings.gemini_api_key,
            input_image=input_image_base64,
            brand_id=request.brand_id
        )
        
        saved_image_path = None
        if request.brand_id and result.get("images") and len(result["images"]) > 0:
            image_data = result["images"][0]["image_data"]
            has_input_image = bool(input_image_base64)
            
            saved_image_path = save_generated_image(
                brand_id=request.brand_id,
                image_base64=image_data,
                has_input_image=has_input_image,
                prompt=request.prompt
            )
            
            if saved_image_path:
                result["saved_image_path"] = saved_image_path
                print(f"✅ Saved generated image to: {saved_image_path}")
        
        return ImageGenerationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image generation failed: {str(e)}"
        )
