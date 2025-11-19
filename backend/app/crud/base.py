"""
Base CRUD - Base class for database operations using Supabase client.

Provides common CRUD operations that can be inherited by specific entity CRUD classes.
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic
from supabase import Client


ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD class with common database operations.
    
    Uses Supabase client for all database operations.
    No SQLAlchemy ORM needed - Supabase client handles PostgreSQL directly.
    
    TODO: Implement base CRUD operations:
    - create: Insert new record
    - get: Get record by ID
    - get_multi: Get multiple records with filters
    - update: Update record
    - delete: Delete record
    """
    
    def __init__(self, table_name: str):
        """
        Initialize CRUD with table name.
        
        Args:
            table_name: Name of Supabase table
        """
        self.table_name = table_name
    
    async def create(
        self, 
        supabase: Client, 
        obj_in: CreateSchemaType
    ) -> ModelType:
        """
        Create new record in database.
        
        Args:
            supabase: Supabase client
            obj_in: Pydantic model with data to create
            
        Returns:
            Created record
        
        TODO: Implement create:
        ```python
        data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
        
        response = supabase.table(self.table_name) \
            .insert(data) \
            .execute()
        
        if response.data:
            return response.data[0]
        raise Exception("Failed to create record")
        ```
        """
        # TODO: Implement create
        pass
    
    async def get(
        self, 
        supabase: Client, 
        id: str
    ) -> Optional[ModelType]:
        """
        Get record by ID.
        
        Args:
            supabase: Supabase client
            id: Record ID (UUID)
            
        Returns:
            Record if found, None otherwise
        
        TODO: Implement get:
        ```python
        response = supabase.table(self.table_name) \
            .select('*') \
            .eq('id', id) \
            .single() \
            .execute()
        
        return response.data if response.data else None
        ```
        """
        # TODO: Implement get
        pass
    
    async def get_multi(
        self, 
        supabase: Client,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filters.
        
        Args:
            supabase: Supabase client
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of filters (e.g., {"user_id": "123"})
            
        Returns:
            List of records
        
        TODO: Implement get_multi:
        ```python
        query = supabase.table(self.table_name).select('*')
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        # Apply pagination
        query = query.range(skip, skip + limit - 1)
        
        response = query.execute()
        return response.data if response.data else []
        ```
        """
        # TODO: Implement get_multi
        pass
    
    async def update(
        self, 
        supabase: Client,
        id: str,
        obj_in: UpdateSchemaType
    ) -> Optional[ModelType]:
        """
        Update record by ID.
        
        Args:
            supabase: Supabase client
            id: Record ID
            obj_in: Pydantic model with data to update
            
        Returns:
            Updated record if found, None otherwise
        
        TODO: Implement update:
        ```python
        # Convert to dict and remove None values
        data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in
        
        response = supabase.table(self.table_name) \
            .update(data) \
            .eq('id', id) \
            .execute()
        
        if response.data:
            return response.data[0]
        return None
        ```
        """
        # TODO: Implement update
        pass
    
    async def delete(
        self, 
        supabase: Client,
        id: str
    ) -> bool:
        """
        Delete record by ID.
        
        Args:
            supabase: Supabase client
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        
        TODO: Implement delete:
        ```python
        response = supabase.table(self.table_name) \
            .delete() \
            .eq('id', id) \
            .execute()
        
        return len(response.data) > 0 if response.data else False
        ```
        """
        # TODO: Implement delete
        pass

