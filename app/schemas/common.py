from pydantic import BaseModel
from typing import Optional, Any

class DBQueryRequest(BaseModel):
    query: str
    params: dict = {}

class GenericResponse(BaseModel):
    status: str
    data: Any = None
    message: Optional[str] = None
