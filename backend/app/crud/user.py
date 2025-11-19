"""
User CRUD - Database operations for users table.
"""

from typing import Optional
from supabase import Client

from app.crud.base import BaseCRUD


class UserCRUD(BaseCRUD):
    """
    CRUD operations for users table.
    
    NOTE: If using Supabase Auth, user authentication is handled by Supabase.
    This CRUD is for the public.users table that extends auth.users.
    
    TODO: Implement user-specific operations
    """
    
    def __init__(self):
        super().__init__(table_name="users")
    
    async def get_by_email(
        self, 
        supabase: Client, 
        email: str
    ) -> Optional[dict]:
        """
        Get user by email.
        
        Args:
            supabase: Supabase client
            email: User email
            
        Returns:
            User record if found, None otherwise
        
        TODO: Implement get by email:
        ```python
        response = supabase.table(self.table_name) \
            .select('*') \
            .eq('email', email) \
            .single() \
            .execute()
        
        return response.data if response.data else None
        ```
        """
        # TODO: Implement get by email
        pass
    
    async def update_subscription(
        self, 
        supabase: Client,
        user_id: str,
        subscription_tier: str,
        stripe_customer_id: Optional[str] = None
    ) -> Optional[dict]:
        """
        Update user subscription information.
        
        Args:
            supabase: Supabase client
            user_id: User ID
            subscription_tier: Subscription tier ("free", "pro", "enterprise")
            stripe_customer_id: Stripe customer ID
            
        Returns:
            Updated user record
        
        TODO: Implement subscription update:
        ```python
        data = {"subscription_tier": subscription_tier}
        if stripe_customer_id:
            data["stripe_customer_id"] = stripe_customer_id
        
        response = supabase.table(self.table_name) \
            .update(data) \
            .eq('id', user_id) \
            .execute()
        
        return response.data[0] if response.data else None
        ```
        """
        # TODO: Implement subscription update
        pass
    
    async def mark_onboarding_complete(
        self, 
        supabase: Client,
        user_id: str
    ) -> Optional[dict]:
        """
        Mark user onboarding as completed.
        
        Args:
            supabase: Supabase client
            user_id: User ID
            
        Returns:
            Updated user record
        
        TODO: Implement onboarding completion:
        ```python
        response = supabase.table(self.table_name) \
            .update({"onboarding_completed": True}) \
            .eq('id', user_id) \
            .execute()
        
        return response.data[0] if response.data else None
        ```
        """
        # TODO: Implement onboarding completion
        pass


# Create singleton instance
user_crud = UserCRUD()

