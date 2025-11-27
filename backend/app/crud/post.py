"""
Post CRUD - Database operations for posts table.

Column mapping: caption -> final_caption
"""

from datetime import datetime
from typing import List, Optional
from supabase import Client

from app.crud.base import BaseCRUD


class PostCRUD(BaseCRUD):
    """CRUD operations for posts table."""
    
    COLUMN_MAP = {"caption": "final_caption"}
    
    def __init__(self):
        super().__init__(table_name="posts")
    
    def _from_db_columns(self, data: Optional[dict]) -> Optional[dict]:
        """Convert DB columns to model fields with JSONB defaults."""
        result = super()._from_db_columns(data)
        if result:
            if result.get("carousel_slides") is None:
                result["carousel_slides"] = []
            if result.get("carousel_metadata") is None:
                result["carousel_metadata"] = {}
        return result
    
    async def get_by_user_id(
        self, supabase: Client, user_id: str,
        campaign_id: Optional[str] = None, status: Optional[str] = None
    ) -> List[dict]:
        """Get posts for user with optional filters."""
        query = supabase.table(self.table_name).select('*').eq('user_id', user_id)
        if campaign_id:
            query = query.eq('campaign_id', campaign_id)
        if status:
            query = query.eq('status', status)
        response = query.order('created_at', desc=True).execute()
        return [self._from_db_columns(row) for row in response.data] if response.data else []
    
    async def get_by_id(
        self, supabase: Client, post_id: str, user_id: str
    ) -> Optional[dict]:
        """Get post by ID with ownership check."""
        response = supabase.table(self.table_name) \
            .select('*').eq('id', post_id).eq('user_id', user_id) \
            .maybe_single().execute()
        return self._from_db_columns(response.data)
    
    async def create_for_user(
        self, supabase: Client, user_id: str, post_data: dict
    ) -> Optional[dict]:
        """Create post for user."""
        db_data = self._to_db_columns(post_data)
        db_data["user_id"] = user_id
        db_data.setdefault("status", "draft")
        db_data.setdefault("platform", "instagram")
        response = supabase.table(self.table_name).insert(db_data).execute()
        return self._from_db_columns(response.data[0]) if response.data else None
    
    async def update(
        self, supabase: Client, post_id: str, user_id: str, post_data: dict
    ) -> Optional[dict]:
        """Update post with ownership check."""
        db_data = {k: v for k, v in self._to_db_columns(post_data).items() if v is not None}
        response = supabase.table(self.table_name) \
            .update(db_data).eq('id', post_id).eq('user_id', user_id).execute()
        return self._from_db_columns(response.data[0]) if response.data else None
    
    async def update_status(
        self, supabase: Client, post_id: str, user_id: str, status: str
    ) -> Optional[dict]:
        """Update post status with ownership check."""
        update_data = {"status": status}
        if status == "published":
            update_data["published_at"] = datetime.now().isoformat()
        response = supabase.table(self.table_name) \
            .update(update_data).eq('id', post_id).eq('user_id', user_id).execute()
        return self._from_db_columns(response.data[0]) if response.data else None
    
    async def delete(self, supabase: Client, post_id: str, user_id: str) -> bool:
        """Delete post with ownership check."""
        response = supabase.table(self.table_name) \
            .delete().eq('id', post_id).eq('user_id', user_id).execute()
        return bool(response.data)


post_crud = PostCRUD()
