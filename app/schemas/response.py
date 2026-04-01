from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar("T")

class PaginationMeta(BaseModel):
    total: int
    skip: int
    limit: int

class StandardResponse(BaseModel, Generic[T]):
    data: T
    meta: Optional[PaginationMeta] = None
    message: Optional[str] = None
