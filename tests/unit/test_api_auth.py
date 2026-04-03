import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.deps import get_user_repository
from unittest.mock import AsyncMock
from app.models.user import User

@pytest.fixture
def mock_user_repo():
    return AsyncMock()

@pytest.fixture
async def api_client(mock_user_repo):
    app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_auth_login_success(api_client, mock_user_repo):
    from app.core.security import get_password_hash
    mock_user = User(
        id=uuid.uuid4(),
        email="test@test.com",
        hashed_password=get_password_hash("password123"),
        roles=[]
    )
    mock_user_repo.get_by_email_with_roles.return_value = mock_user
    
    response = await api_client.post("/api/v1/auth/login", json={"email": "test@test.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.cookies

@pytest.mark.asyncio
async def test_auth_login_fail(api_client, mock_user_repo):
    mock_user_repo.get_by_email_with_roles.return_value = None
    response = await api_client.post("/api/v1/auth/login", json={"email": "wrong@test.com", "password": "wrong"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_auth_refresh_token_success(api_client, mock_user_repo):
    from app.core.security import create_refresh_token
    import uuid
    uid = uuid.uuid4()
    
    # Valid refresh token
    refresh_token = create_refresh_token({"sub": str(uid)})
    
    mock_user_repo.get_with_roles.return_value = User(id=uid, roles=[])
    
    # Send request with cookies
    response = await api_client.post("/api/v1/auth/refresh", cookies={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_auth_refresh_token_missing(api_client):
    response = await api_client.post("/api/v1/auth/refresh")
    assert response.status_code == 401
