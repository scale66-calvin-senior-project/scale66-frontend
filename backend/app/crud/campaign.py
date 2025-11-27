"""
Campaign CRUD - Database operations for campaigns table.

Column mapping: name -> campaign_name
"""

from typing import List, Optional
from supabase import Client

from app.crud.base import BaseCRUD


class CampaignCRUD(BaseCRUD):
    """CRUD operations for campaigns table."""
    
    COLUMN_MAP = {"name": "campaign_name"}
    
    def __init__(self):
        super().__init__(table_name="campaigns")
    
    async def get_by_user_id(self, supabase: Client, user_id: str) -> List[dict]:
        """Get all campaigns for user."""
        response = supabase.table(self.table_name) \
            .select('*').eq('user_id', user_id) \
            .order('created_at', desc=True).execute()
        return [self._from_db_columns(row) for row in response.data] if response.data else []
    
    async def get_by_id(
        self, supabase: Client, campaign_id: str, user_id: str
    ) -> Optional[dict]:
        """Get campaign by ID with ownership check."""
        response = supabase.table(self.table_name) \
            .select('*').eq('id', campaign_id).eq('user_id', user_id) \
            .maybe_single().execute()
        return self._from_db_columns(response.data)
    
    async def create_for_user(
        self, supabase: Client, user_id: str, campaign_data: dict
    ) -> Optional[dict]:
        """Create campaign for user."""
        db_data = self._to_db_columns(campaign_data)
        db_data["user_id"] = user_id
        response = supabase.table(self.table_name).insert(db_data).execute()
        return self._from_db_columns(response.data[0]) if response.data else None
    
    async def update(
        self, supabase: Client, campaign_id: str, user_id: str, campaign_data: dict
    ) -> Optional[dict]:
        """Update campaign with ownership check."""
        db_data = {k: v for k, v in self._to_db_columns(campaign_data).items() if v is not None}
        response = supabase.table(self.table_name) \
            .update(db_data).eq('id', campaign_id).eq('user_id', user_id).execute()
        return self._from_db_columns(response.data[0]) if response.data else None
    
    async def delete(self, supabase: Client, campaign_id: str, user_id: str) -> bool:
        """Delete campaign with ownership check."""
        response = supabase.table(self.table_name) \
            .delete().eq('id', campaign_id).eq('user_id', user_id).execute()
        return bool(response.data)


campaign_crud = CampaignCRUD()
