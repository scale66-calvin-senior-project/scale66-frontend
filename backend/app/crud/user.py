"""
User CRUD - Database operations for users table.

Authentication is handled by Supabase Auth. This CRUD manages user profile data.
"""

from typing import Optional
from supabase import Client

from app.crud.base import BaseCRUD


class UserCRUD(BaseCRUD):
    """CRUD operations for users table."""
    
    def __init__(self):
        super().__init__(table_name="users")
    
    async def get_by_id(self, supabase: Client, user_id: str) -> Optional[dict]:
        """Get user by ID."""
        response = supabase.table(self.table_name) \
            .select('*').eq('id', user_id).maybe_single().execute()
        return response.data if response.data else None
    
    async def get_by_email(self, supabase: Client, email: str) -> Optional[dict]:
        """Get user by email."""
        try:
            response = supabase.table(self.table_name) \
                .select('*').eq('email', email).maybe_single().execute()
            return response.data if response and response.data else None
        except Exception:
            return None
    
    async def create(
        self, supabase: Client, user_id: str, email: str
    ) -> Optional[dict]:
        """Create user profile (usually via Supabase trigger on auth.users insert)."""
        response = supabase.table(self.table_name).insert({
            "id": user_id,
            "email": email,
            "subscription_tier": "free",
            "onboarding_completed": False,
        }).execute()
        return response.data[0] if response.data else None
    
    async def update(
        self, supabase: Client, user_id: str, user_data: dict
    ) -> Optional[dict]:
        """Update user profile."""
        data = {k: v for k, v in user_data.items() if v is not None}
        response = supabase.table(self.table_name).update(data).eq('id', user_id).execute()
        return response.data[0] if response.data else None
    
    async def update_subscription(
        self, supabase: Client, user_id: str,
        subscription_tier: str, stripe_customer_id: Optional[str] = None
    ) -> Optional[dict]:
        """Update user subscription."""
        data = {"subscription_tier": subscription_tier}
        if stripe_customer_id:
            data["stripe_customer_id"] = stripe_customer_id
        response = supabase.table(self.table_name).update(data).eq('id', user_id).execute()
        return response.data[0] if response.data else None
    
    async def mark_onboarding_complete(
        self, supabase: Client, user_id: str
    ) -> Optional[dict]:
        """Mark user onboarding as completed."""
        response = supabase.table(self.table_name) \
            .update({"onboarding_completed": True}).eq('id', user_id).execute()
        return response.data[0] if response.data else None


user_crud = UserCRUD()
