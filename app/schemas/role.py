from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
import uuid

class RoleBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, strip_whitespace=True)
    description: Optional[str] = Field(None, max_length=255, strip_whitespace=True)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50, strip_whitespace=True)
    description: Optional[str] = Field(None, max_length=255, strip_whitespace=True)

class RolePublic(RoleBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
