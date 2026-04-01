from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid

class UserBase(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    first_name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    last_name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, max_length=255)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, strip_whitespace=True)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, strip_whitespace=True)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
