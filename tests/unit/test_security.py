import pytest
from app.core.security import get_password_hash, verify_password, create_access_token, verify_token
from app.core.config import settings

def test_password_hashing():
    password = "supersecretpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_token_creation_and_verification():
    data = {"sub": "user_id_123"}
    token = create_access_token(data=data)
    
    assert token is not None
    assert isinstance(token, str)
    
    payload = verify_token(token)
    assert payload.get("sub") == "user_id_123"
    assert "exp" in payload
    assert "iat" in payload

def test_verify_invalid_token():
    payload = verify_token("invalid.token.string")
    assert payload == {}
