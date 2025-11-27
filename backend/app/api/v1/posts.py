"""
Post Management Endpoints - CRUD operations for posts.

Posts represent generated carousel content:
- Carousel slides (images with text)
- Metadata (format, style, etc.)
- Posting status (draft, scheduled, published)
- Analytics (views, engagement)
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from supabase import Client

from app.api.deps import get_supabase_client, get_current_user
from app.crud.post import post_crud


router = APIRouter(prefix="/posts", tags=["posts"])


# Request/Response Models
class PostCreate(BaseModel):
    campaign_id: Optional[str] = None
    carousel_slides: list[str]  # URLs to images
    carousel_metadata: dict
    caption: Optional[str] = None
    platform: str  # "instagram", "tiktok", etc.
    status: str = "draft"  # "draft", "scheduled", "published"
    scheduled_for: Optional[datetime] = None


class PostUpdate(BaseModel):
    caption: Optional[str] = None
    status: Optional[str] = None
    scheduled_for: Optional[datetime] = None


class PostResponse(BaseModel):
    id: str
    user_id: str
    campaign_id: Optional[str] = None
    carousel_slides: list[str]
    carousel_metadata: dict
    caption: Optional[str] = None
    platform: str
    status: str
    scheduled_for: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: str
    updated_at: str


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Create new post (save generated carousel).
    
    Args:
        post: Post data
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        Created post
    
    Note:
        Carousel slides should already be uploaded to storage before calling this endpoint.
        This endpoint creates the database record for the post.
    """
    user_id = current_user["id"]
    
    result = await post_crud.create_for_user(
        supabase,
        user_id,
        post.model_dump()
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create post"
        )
    
    return PostResponse(**result)


@router.get("/", response_model=List[PostResponse])
async def list_posts(
    campaign_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    List all posts for authenticated user.
    
    Args:
        campaign_id: Optional filter by campaign
        status: Optional filter by status
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        List of posts
    """
    user_id = current_user["id"]
    
    posts = await post_crud.get_by_user_id(
        supabase,
        user_id,
        campaign_id=campaign_id,
        status=status
    )
    
    return [PostResponse(**post) for post in posts]


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get specific post by ID.
    
    Args:
        post_id: Post UUID
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        Post details
    
    Raises:
        HTTPException: 404 if post not found or doesn't belong to user
    """
    user_id = current_user["id"]
    
    result = await post_crud.get_by_id(supabase, post_id, user_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return PostResponse(**result)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    post: PostUpdate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Update post by ID.
    
    Args:
        post_id: Post UUID
        post: Updated post data
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        Updated post
    
    Raises:
        HTTPException: 404 if post not found
    """
    user_id = current_user["id"]
    
    update_data = post.model_dump(exclude_unset=True)
    
    result = await post_crud.update(supabase, post_id, user_id, update_data)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return PostResponse(**result)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Delete post by ID.
    
    Args:
        post_id: Post UUID
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        None (204 No Content)
    
    Note:
        Carousel slides in storage should be cleaned up separately via a background job.
        This endpoint only deletes the database record.
    """
    user_id = current_user["id"]
    
    deleted = await post_crud.delete(supabase, post_id, user_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )


@router.post("/{post_id}/publish")
async def publish_post(
    post_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Publish post to social media platform.
    
    Args:
        post_id: Post UUID
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        Publication status
    
    Note:
        This is a placeholder. Full implementation requires:
        1. Social media service integration
        2. Connected account verification
        3. Platform-specific API calls
        4. Error handling for API failures
    """
    user_id = current_user["id"]
    
    # Update post status to published
    result = await post_crud.update_status(supabase, post_id, user_id, "published")
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return {
        "message": "Post marked as published",
        "post_id": post_id,
        "status": "published"
    }

