from typing import Dict, List, Optional
from datetime import datetime
from API_Database import delete_by_id
from API_Database.audit_log import get_audit_history

class Entry:
    """
    Base class for all database entities.
    
    Attributes:
        table_name: The name of the database table
        id: The primary key ID
        created_at: When the entry was created
        created_by: Who created the entry
        last_updated: When the entry was last updated
        last_updated_by: Who last updated the entry
    """

    def __init__(self, table_name: str, *args, **kwargs) -> None:
        """
        Initialize an Entry.
        
        Args:
            table_name: The name of the database table
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments including:
                id: The primary key ID
                created_at: When the entry was created
                created_by: Who created the entry
                last_updated: When the entry was last updated
                last_updated_by: Who last updated the entry
        """
        self.table_name = table_name
        self.id = kwargs.get('id', None)
        if self.id is not None:
            self.id = int(self.id)
            
        # Audit trail fields
        self.created_at = kwargs.get('created_at')
        self.created_by = kwargs.get('created_by')
        self.last_updated = kwargs.get('last_updated')
        self.last_updated_by = kwargs.get('last_updated_by')

    def get_id(self) -> int:
        """Returns the ID of the Entry."""
        return self.id

    def delete(self, current_user_id: Optional[int] = None) -> Dict:
        """
        Delete the Entry from the database.
        
        Args:
            current_user_id: The ID of the user performing the delete
            
        Returns:
            Dict: The result of the delete operation
        """
        return delete_by_id(self.get_id(), self.table_name)

    def get_audit_history(self, limit: int = 100, offset: int = 0) -> Dict:
        """
        Get the audit history for this entry.
        
        Args:
            limit: The maximum number of records to return
            offset: The number of records to skip
            
        Returns:
            Dict: The audit history
        """
        if not self.id:
            return {
                'status': 'error',
                'message': 'Entry ID is required'
            }
            
        return get_audit_history(
            table_name=self.table_name,
            record_id=self.id,
            limit=limit,
            offset=offset
        )

    @staticmethod
    def convert_int_attributes(obj: Dict, int_attributes: List):
        """
        Convert the necessary integer attributes from strings to integers
        
        Args:
            obj: The dictionary to convert
            int_attributes: The list of attributes to convert
            
        Returns:
            Dict: The converted dictionary
        """
        for attr in int_attributes:
            if attr in obj:
                if type(obj[attr]) == str:
                    obj[attr] = int(obj[attr].strip())
                elif type(obj[attr]) == List:
                    obj[attr] = [int(x) for x in obj[attr]]
        return obj
        
    @staticmethod
    def add_audit_fields(query: str, current_user_id: Optional[int] = None, is_insert: bool = False) -> str:
        """
        Add audit fields to a SQL query.
        
        Args:
            query: The SQL query
            current_user_id: The ID of the current user
            is_insert: Whether this is an INSERT query
            
        Returns:
            str: The modified query
        """
        if current_user_id is None:
            return query
            
        # For INSERT queries
        if is_insert:
            # Check if the query has a VALUES clause
            if 'VALUES' in query.upper():
                # Add created_by and last_updated_by to the columns
                columns_end = query.upper().find('VALUES')
                columns_part = query[:columns_end].strip()
                values_part = query[columns_end:].strip()
                
                # Check if the columns are explicitly listed
                if '(' in columns_part and ')' in columns_part:
                    # Add the audit fields to the columns
                    columns_end = columns_part.rfind(')')
                    columns_part = columns_part[:columns_end] + ', created_by, last_updated_by' + columns_part[columns_end:]
                    
                    # Add the values for the audit fields
                    values_start = values_part.find('(')
                    values_end = values_part.find(')')
                    values_part = values_part[:values_end] + f', {current_user_id}, {current_user_id}' + values_part[values_end:]
                    
                    return columns_part + ' ' + values_part
            
        # For UPDATE queries
        else:
            # Add last_updated_by to the SET clause
            set_index = query.upper().find('SET')
            where_index = query.upper().find('WHERE')
            
            if set_index != -1 and where_index != -1:
                set_clause = query[set_index + 3:where_index].strip()
                set_clause += f', last_updated = CURRENT_TIMESTAMP, last_updated_by = {current_user_id}'
                
                return query[:set_index + 3] + ' ' + set_clause + ' ' + query[where_index:]
        
        return query
