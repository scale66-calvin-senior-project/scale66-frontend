"""
Session CRUD - Database operations for sessions table.

NOTE: Optional - Supabase Auth handles sessions automatically.
Only needed for custom session management.
"""

from datetime import datetime
from typing import Optional
from supabase import Client

from app.crud.base import BaseCRUD


class SessionCRUD(BaseCRUD):
    """CRUD operations for sessions table (optional with Supabase Auth)."""
    
    def __init__(self):
        super().__init__(table_name="sessions")
    
    async def get_active_session(
        self, supabase: Client, user_id: str
    ) -> Optional[dict]:
        """Get active session for user."""
        now = datetime.utcnow().isoformat()
        response = supabase.table(self.table_name) \
            .select('*').eq('user_id', user_id).gt('expires_at', now) \
            .order('created_at', desc=True).limit(1).execute()
        return response.data[0] if response.data else None
    
    async def invalidate_session(self, supabase: Client, session_id: str) -> bool:
        """Invalidate session (logout)."""
        response = supabase.table(self.table_name) \
            .delete().eq('id', session_id).execute()
        return bool(response.data)


session_crud = SessionCRUD()
