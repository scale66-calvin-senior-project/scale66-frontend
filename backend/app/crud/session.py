"""
Session CRUD - Database operations for sessions table.

NOTE: Only needed if using CUSTOM session management instead of Supabase Auth.
If using Supabase Auth, session management is handled by Supabase.
"""

from typing import Optional
from datetime import datetime
from supabase import Client

from app.crud.base import BaseCRUD


class SessionCRUD(BaseCRUD):
    """
    CRUD operations for sessions table.
    
    NOTE: This is optional if using Supabase Auth (recommended).
    Supabase Auth handles sessions automatically.
    
    Use this only if implementing custom session management.
    
    TODO: Implement session operations if needed
    """
    
    def __init__(self):
        super().__init__(table_name="sessions")
    
    async def get_active_session(
        self, 
        supabase: Client, 
        user_id: str
    ) -> Optional[dict]:
        """
        Get active session for user.
        
        Args:
            supabase: Supabase client
            user_id: User ID
            
        Returns:
            Active session if found, None otherwise
        
        TODO: Implement get active session:
        ```python
        now = datetime.utcnow().isoformat()
        
        response = supabase.table(self.table_name) \
            .select('*') \
            .eq('user_id', user_id) \
            .gt('expires_at', now) \
            .order('created_at', desc=True) \
            .limit(1) \
            .execute()
        
        return response.data[0] if response.data else None
        ```
        """
        # TODO: Implement get active session
        pass
    
    async def invalidate_session(
        self, 
        supabase: Client,
        session_id: str
    ) -> bool:
        """
        Invalidate session (logout).
        
        Args:
            supabase: Supabase client
            session_id: Session ID
            
        Returns:
            True if invalidated, False otherwise
        
        TODO: Implement session invalidation:
        ```python
        response = supabase.table(self.table_name) \
            .delete() \
            .eq('id', session_id) \
            .execute()
        
        return len(response.data) > 0 if response.data else False
        ```
        """
        # TODO: Implement session invalidation
        pass


# Create singleton instance
session_crud = SessionCRUD()

