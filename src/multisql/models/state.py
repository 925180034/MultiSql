from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class ColumnInfo(BaseModel):
    name: str
    type: str
    table: str
    description: Optional[str] = None

class TableInfo(BaseModel):
    name: str
    columns: List[ColumnInfo] = []
    primary_keys: List[str] = []
    foreign_keys: List[Dict[str, str]] = []
    sample_rows: Optional[List[Dict[str, Any]]] = None

class DatabaseSchema(BaseModel):
    db_id: str
    tables: List[TableInfo] = []
    relationships: List[Dict[str, Any]] = []

class NL2SQLState(BaseModel):
    """State model tracking the NL to SQL conversion process."""
    nl_query: str = ""
    db_schema: Optional[DatabaseSchema] = None
    parsed_intent: Optional[Dict[str, Any]] = None
    complexity_score: float = 0.0
    tables_involved: List[str] = []
    joins_needed: int = 0
    needs_schema_matching: bool = False
    schema_matching_result: Optional[Dict[str, Any]] = None
    generated_sql: str = ""
    execution_path: List[str] = []
    execution_time: Dict[str, float] = {}
