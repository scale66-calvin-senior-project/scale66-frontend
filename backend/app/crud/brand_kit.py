"""
Brand Kit CRUD - Database operations for brand_kits table.

Column mapping: product_service_desc -> product_service_description
"""

from typing import Optional
from supabase import Client

from app.crud.base import BaseCRUD


class BrandKitCRUD(BaseCRUD):
    """CRUD operations for brand_kits table."""
    
    COLUMN_MAP = {"product_service_desc": "product_service_description"}
    
    def __init__(self):
        super().__init__(table_name="brand_kits")
    
    def _from_db_columns(self, data: Optional[dict]) -> Optional[dict]:
        """Convert DB columns to model fields with pain_points normalization."""
        result = super()._from_db_columns(data)
        if result and "customer_pain_points" in result:
            pain_points = result["customer_pain_points"]
            if isinstance(pain_points, str):
                result["customer_pain_points"] = [pain_points] if pain_points else []
            elif pain_points is None:
                result["customer_pain_points"] = []
        return result
    
    async def get_by_id(self, supabase: Client, brand_kit_id: str) -> Optional[dict]:
        """Get brand kit by ID."""
        try:
            response = supabase.table(self.table_name) \
                .select('*').eq('id', brand_kit_id).maybe_single().execute()
            return self._from_db_columns(response.data)
        except Exception:
            return None
    
    async def get_by_user_id(self, supabase: Client, user_id: str) -> Optional[dict]:
        """Get brand kit for user."""
        try:
            response = supabase.table(self.table_name) \
                .select('*').eq('user_id', user_id).maybe_single().execute()
            return self._from_db_columns(response.data)
        except Exception:
            return None
    
    async def create_for_user(
        self, supabase: Client, user_id: str, brand_data: dict
    ) -> Optional[dict]:
        """Create brand kit for user."""
        db_data = self._to_db_columns(brand_data)
        db_data["user_id"] = user_id
        response = supabase.table(self.table_name).insert(db_data).execute()
        return self._from_db_columns(response.data[0]) if response.data else None
    
    async def update_for_user(
        self, supabase: Client, user_id: str, brand_data: dict
    ) -> Optional[dict]:
        """Update brand kit for user."""
        db_data = {k: v for k, v in self._to_db_columns(brand_data).items() if v is not None}
        response = supabase.table(self.table_name) \
            .update(db_data).eq('user_id', user_id).execute()
        return self._from_db_columns(response.data[0]) if response.data else None
    
    async def delete_for_user(self, supabase: Client, user_id: str) -> bool:
        """Delete brand kit for user."""
        response = supabase.table(self.table_name).delete().eq('user_id', user_id).execute()
        return bool(response.data)


brand_kit_crud = BrandKitCRUD()
