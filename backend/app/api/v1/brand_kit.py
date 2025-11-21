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
    
    TODO: Implement brand kit creation:
    1. Get user_id from current_user
    2. Insert brand kit data into database
    3. Return created brand kit
    
    Raises:
        HTTPException: 400 if validation fails
    """
    # TODO: Implement create
    # user_id = current_user["id"]
    # response = supabase.table('brand_kits') \
    #     .insert({**brand_kit.dict(), 'user_id': user_id}) \
    #     .execute()
    # 
    # return BrandKitResponse(**response.data[0])
    pass


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
    
    TODO: Implement brand kit fetch:
    1. Get user_id from current_user
    2. Query brand_kits table filtered by user_id
    3. Return brand kit or 404 if not found
    
    Raises:
        HTTPException: 404 if brand kit doesn't exist
    """
    # TODO: Implement get
    # user_id = current_user["id"]
    # response = supabase.table('brand_kits') \
    #     .select('*') \
    #     .eq('user_id', user_id) \
    #     .single() \
    #     .execute()
    # 
    # if not response.data:
    #     raise HTTPException(status_code=404, detail="Brand kit not found")
    # 
    # return BrandKitResponse(**response.data)
    pass


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
    
    TODO: Implement brand kit update:
    1. Get user_id from current_user
    2. Update brand_kits table filtered by user_id
    3. Only update fields that are not None
    4. Return updated brand kit
    
    Raises:
        HTTPException: 404 if brand kit doesn't exist
    """
    # TODO: Implement update
    # user_id = current_user["id"]
    # 
    # # Only update non-None fields
    # update_data = {k: v for k, v in brand_kit.dict().items() if v is not None}
    # 
    # response = supabase.table('brand_kits') \
    #     .update(update_data) \
    #     .eq('user_id', user_id) \
    #     .execute()
    # 
    # if not response.data:
    #     raise HTTPException(status_code=404, detail="Brand kit not found")
    # 
    # return BrandKitResponse(**response.data[0])
    pass


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
    
    TODO: Implement brand kit deletion:
    1. Get user_id from current_user
    2. Delete brand_kits record filtered by user_id
    3. Return 204 on success
    
    Raises:
        HTTPException: 404 if brand kit doesn't exist
    """
    # TODO: Implement delete
    # user_id = current_user["id"]
    # 
    # response = supabase.table('brand_kits') \
    #     .delete() \
    #     .eq('user_id', user_id) \
    #     .execute()
    # 
    # if not response.data:
    #     raise HTTPException(status_code=404, detail="Brand kit not found")
    pass

