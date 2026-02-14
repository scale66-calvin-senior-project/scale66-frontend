from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
import logging

from app.api.dependencies import get_supabase, get_current_user
from app.api.schemas.user import UserUpdate, UserResponse
from app.crud.user import user_crud

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    supabase: Client = Depends(get_supabase),
    user_id: str = Depends(get_current_user)
):
    """
    Get the authenticated user's information.
    """
    user = await user_crud.get_by_id(supabase, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/users/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    supabase: Client = Depends(get_supabase),
    user_id: str = Depends(get_current_user)
):
    """
    Update the authenticated user's information.
    
    This can be used to:
    - Mark onboarding as complete
    - Update subscription tier (typically done via payment webhook)
    """
    # Update with only provided fields
    data = user_data.model_dump(exclude_unset=True)
    
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # For users table, we update by id directly (not user_id)
    # The base CRUD update method expects user_id for filtering, but for users table,
    # the id IS the user_id, so we pass None to skip the user_id filter
    try:
        # Direct update for users table (no user_id filter needed)
        response = supabase.table("users").update(data).eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        updated_user = response.data[0]
        logger.info(f"Updated user {user_id}: {data}")
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )
