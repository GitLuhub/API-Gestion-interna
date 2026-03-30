from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class Message(BaseModel):
    detail: str
