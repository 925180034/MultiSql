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
        db_path = f"{self.db_path}/{db_id}/{db_id}.sqlite"
        schema = {
            "db_id": db_id,
            "tables": [],
            "relationships": []
        }
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                
                # Get table structure
                cursor.execute(f"PRAGMA table_info('{table_name}')")
                columns = cursor.fetchall()
                
                # Get sample data
                cursor.execute(f"SELECT * FROM '{table_name}' LIMIT 3")
                sample_rows = cursor.fetchall()
                sample_data = []
                for row in sample_rows:
                    sample_data.append(dict(zip([col[1] for col in columns], row)))
                
                # Get primary keys
                cursor.execute(f"PRAGMA table_info('{table_name}')")
                primary_keys = [col[1] for col in cursor.fetchall() if col[5] > 0]
                
                # Get foreign keys
                cursor.execute(f"PRAGMA foreign_key_list('{table_name}')")
                foreign_keys = []
                for fk in cursor.fetchall():
                    foreign_keys.append({
                        "column": fk[3],
                        "ref_table": fk[2],
                        "ref_column": fk[4]
                    })
                
                # Add table info
                schema["tables"].append({
                    "name": table_name,
                    "columns": [{"name": col[1], "type": col[2], "table": table_name} for col in columns],
                    "primary_keys": primary_keys,
                    "foreign_keys": foreign_keys,
                    "sample_rows": sample_data
                })
            
            # Build table relationships
            for table in schema["tables"]:
                for fk in table["foreign_keys"]:
                    relationship = {
                        "from_table": table["name"],
                        "from_column": fk["column"],
                        "to_table": fk["ref_table"],
                        "to_column": fk["ref_column"]
                    }
                    schema["relationships"].append(relationship)
            
            conn.close()
            
        except Exception as e:
            print(f"Error extracting schema for {db_id}: {str(e)}")
            
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
