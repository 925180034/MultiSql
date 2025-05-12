from typing import Dict, List, Any, Optional
import sqlite3
import json

class SchemaManager:
    """Database schema management tool"""
    
    def __init__(self, db_path: str = None, schema_cache_path: str = None):
        self.db_path = db_path
        self.schema_cache_path = schema_cache_path
        self.schema_cache = {}
        
        if schema_cache_path:
            self._load_schema_cache()
    
    def _load_schema_cache(self):
        """Load schema information from cache file"""
        try:
            with open(self.schema_cache_path, 'r') as f:
                self.schema_cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.schema_cache = {}
    
    def _save_schema_cache(self):
        """Save schema information to cache file"""
        if self.schema_cache_path:
            with open(self.schema_cache_path, 'w') as f:
                json.dump(self.schema_cache, f)
    
    def get_database_schema(self, db_id: str) -> Dict[str, Any]:
        """Get database schema information"""
        # First try to get from cache
        if db_id in self.schema_cache:
            return self.schema_cache[db_id]
        
        # Not in cache, extract from database
        schema = self._extract_schema_from_db(db_id)
        
        # Save to cache
        self.schema_cache[db_id] = schema
        self._save_schema_cache()
        
        return schema
    
    def _extract_schema_from_db(self, db_id: str) -> Dict[str, Any]:
        """Extract schema information from database"""
        # This is a simplified version, in production you'd connect to actual DB
        # For demo, we'll return a mock schema
        schema = {
            "db_id": db_id,
            "tables": [
                {
                    "name": "employees",
                    "columns": [
                        {"name": "id", "type": "INTEGER", "table": "employees"},
                        {"name": "name", "type": "TEXT", "table": "employees"},
                        {"name": "salary", "type": "INTEGER", "table": "employees"},
                        {"name": "department_id", "type": "INTEGER", "table": "employees"}
                    ],
                    "primary_keys": ["id"],
                    "foreign_keys": [
                        {"column": "department_id", "ref_table": "departments", "ref_column": "id"}
                    ]
                },
                {
                    "name": "departments",
                    "columns": [
                        {"name": "id", "type": "INTEGER", "table": "departments"},
                        {"name": "name", "type": "TEXT", "table": "departments"},
                        {"name": "location", "type": "TEXT", "table": "departments"}
                    ],
                    "primary_keys": ["id"],
                    "foreign_keys": []
                }
            ],
            "relationships": [
                {
                    "from_table": "employees",
                    "from_column": "department_id",
                    "to_table": "departments",
                    "to_column": "id"
                }
            ]
        }
        
        # In production, you would extract this from actual database:
        # db_path = f"{self.db_path}/{db_id}/{db_id}.sqlite"
        # Connect to database and extract schema
        
        return schema
    
    def get_optimal_join_path(self, db_schema: Dict[str, Any], tables: List[str]) -> List[Dict[str, Any]]:
        """Calculate optimal table join path"""
        if len(tables) <= 1:
            return []
        
        # Build table relationship graph
        graph = {}
        for relationship in db_schema["relationships"]:
            from_table = relationship["from_table"]
            to_table = relationship["to_table"]
            
            if from_table not in graph:
                graph[from_table] = []
            if to_table not in graph:
                graph[to_table] = []
                
            graph[from_table].append({
                "table": to_table,
                "relationship": relationship
            })
            graph[to_table].append({
                "table": from_table,
                "relationship": relationship
            })
        
        # Use minimum spanning tree algorithm to calculate optimal join path
        # Here simplified to just return relationships between tables in the list
        # In production, implement a proper MST algorithm
        mst = []
        for relationship in db_schema["relationships"]:
            if relationship["from_table"] in tables and relationship["to_table"] in tables:
                mst.append(relationship)
                
        return mst
