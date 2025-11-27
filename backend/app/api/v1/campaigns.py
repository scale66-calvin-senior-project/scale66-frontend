"""
Campaign Endpoints - CRUD operations for campaign management.

Campaigns group related posts and provide context for content generation:
- Campaign name and description
- Target audience
- Goals and metrics
- Associated posts
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from supabase import Client

from app.api.deps import get_supabase_client, get_current_user
from app.crud.campaign import campaign_crud


router = APIRouter(prefix="/campaigns", tags=["campaigns"])


# Request/Response Models
class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_audience: Optional[str] = None
    goals: Optional[str] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_audience: Optional[str] = None
    goals: Optional[str] = None


class CampaignResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    target_audience: Optional[str] = None
    goals: Optional[str] = None
    created_at: str
    updated_at: str


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign: CampaignCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Create new campaign for authenticated user.
    
    Args:
        campaign: Campaign data
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        Created campaign
    """
    user_id = current_user["id"]
    
    result = await campaign_crud.create_for_user(
        supabase,
        user_id,
        campaign.model_dump()
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create campaign"
        )
    
    return CampaignResponse(**result)


@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    List all campaigns for authenticated user.
    
    Args:
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        List of campaigns
    """
    user_id = current_user["id"]
    
    campaigns = await campaign_crud.get_by_user_id(supabase, user_id)
    
    return [CampaignResponse(**campaign) for campaign in campaigns]


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get specific campaign by ID.
    
    Args:
        campaign_id: Campaign UUID
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        Campaign details
    
    Raises:
        HTTPException: 404 if campaign not found or doesn't belong to user
    """
    user_id = current_user["id"]
    
    result = await campaign_crud.get_by_id(supabase, campaign_id, user_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return CampaignResponse(**result)


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign: CampaignUpdate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Update campaign by ID.
    
    Args:
        campaign_id: Campaign UUID
        campaign: Updated campaign data
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        Updated campaign
    
    Raises:
        HTTPException: 404 if campaign not found
    """
    user_id = current_user["id"]
    
    update_data = campaign.model_dump(exclude_unset=True)
    
    result = await campaign_crud.update(supabase, campaign_id, user_id, update_data)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return CampaignResponse(**result)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Delete campaign by ID.
    
    Args:
        campaign_id: Campaign UUID
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        None (204 No Content)
    
    Raises:
        HTTPException: 404 if campaign not found
    
    Note:
        Associated posts will have their campaign_id set to NULL by database ON DELETE SET NULL constraint
    """
    user_id = current_user["id"]
    
    deleted = await campaign_crud.delete(supabase, campaign_id, user_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

