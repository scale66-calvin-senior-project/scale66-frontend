"""
Brand Kit Endpoints - CRUD operations for brand kit management.

Brand kits store user's brand information:
- Brand name, niche, style
- Colors, logos, images
- Customer pain points
- Product/service descriptions
- Social media links
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from supabase import Client

from app.api.deps import get_supabase_client, get_current_user
from app.crud.brand_kit import brand_kit_crud


router = APIRouter(prefix="/brand-kit", tags=["brand_kit"])


# Request/Response Models
class BrandKitCreate(BaseModel):
    brand_name: str
    brand_niche: str
    brand_colors: list[str]
    brand_style: str
    customer_pain_points: str
    product_service_desc: str
    social_media_links: Optional[dict] = None
    logo_url: Optional[str] = None
    brand_images: Optional[list[str]] = None
    past_posts: Optional[list[str]] = None


class BrandKitUpdate(BaseModel):
    brand_name: Optional[str] = None
    brand_niche: Optional[str] = None
    brand_colors: Optional[list[str]] = None
    brand_style: Optional[str] = None
    customer_pain_points: Optional[str] = None
    product_service_desc: Optional[str] = None
    social_media_links: Optional[dict] = None
    logo_url: Optional[str] = None
    brand_images: Optional[list[str]] = None
    past_posts: Optional[list[str]] = None


class BrandKitResponse(BaseModel):
    id: str
    user_id: str
    brand_name: str
    brand_niche: str
    brand_colors: list[str]
    brand_style: str
    customer_pain_points: str
    product_service_desc: str
    social_media_links: Optional[dict] = None
    logo_url: Optional[str] = None
    brand_images: Optional[list[str]] = None
    past_posts: Optional[list[str]] = None
    created_at: str
    updated_at: str


@router.post("/", response_model=BrandKitResponse, status_code=status.HTTP_201_CREATED)
async def create_brand_kit(
    brand_kit: BrandKitCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Create new brand kit for authenticated user.
    
    Args:
        brand_kit: Brand kit data
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        Created brand kit
    
    Raises:
        HTTPException: 400 if validation fails
    """
    user_id = current_user["id"]
    
    result = await brand_kit_crud.create_for_user(
        supabase, 
        user_id, 
        brand_kit.model_dump()
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create brand kit"
        )
    
    return BrandKitResponse(**result)


@router.get("/", response_model=BrandKitResponse)
async def get_brand_kit(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get brand kit for authenticated user.
    
    Args:
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        User's brand kit
    
    Raises:
        HTTPException: 404 if brand kit doesn't exist
    """
    user_id = current_user["id"]
    
    result = await brand_kit_crud.get_by_user_id(supabase, user_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand kit not found"
        )
    
    return BrandKitResponse(**result)


@router.put("/", response_model=BrandKitResponse)
async def update_brand_kit(
    brand_kit: BrandKitUpdate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Update brand kit for authenticated user.
    
    Args:
        brand_kit: Updated brand kit data
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        Updated brand kit
    
    Raises:
        HTTPException: 404 if brand kit doesn't exist
    """
    user_id = current_user["id"]
    
    update_data = brand_kit.model_dump(exclude_unset=True)
    
    result = await brand_kit_crud.update_for_user(supabase, user_id, update_data)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand kit not found"
        )
    
    return BrandKitResponse(**result)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand_kit(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Delete brand kit for authenticated user.
    
    Args:
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        None (204 No Content)
    
    Raises:
        HTTPException: 404 if brand kit doesn't exist
    """
    user_id = current_user["id"]
    
    deleted = await brand_kit_crud.delete_for_user(supabase, user_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand kit not found"
        )

