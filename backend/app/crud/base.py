"""
Base CRUD - Abstract base class for Supabase database operations.

Provides column mapping utilities for handling differences between
API model field names and database column names.
"""

from typing import Dict, Optional


class BaseCRUD:
    """Base CRUD class with column mapping support."""
    
    COLUMN_MAP: Dict[str, str] = {}
    
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    def _to_db_columns(self, data: dict) -> dict:
        """Convert API model field names to database column names."""
        return {self.COLUMN_MAP.get(k, k): v for k, v in data.items()}
    
    def _from_db_columns(self, data: Optional[dict]) -> Optional[dict]:
        """Convert database column names to API model field names."""
        if not data:
            return data
        reverse_map = {v: k for k, v in self.COLUMN_MAP.items()}
        return {reverse_map.get(k, k): v for k, v in data.items()}
