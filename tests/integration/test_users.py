import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate
from app.models.user import User, Role, UserRole
from app.core.security import get_password_hash

@pytest.mark.asyncio
async def test_create_user_unauthorized(client: AsyncClient):
    """Test creating a user without authentication fails."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_users_unauthorized(client: AsyncClient):
    """Test getting users without authentication fails."""
    response = await client.get("/api/v1/users/")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_wrong_credentials(client: AsyncClient):
    """Test login with incorrect credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "message" in response.json()

@pytest.mark.asyncio
async def test_e2e_login_and_create_user(client: AsyncClient, db_session: AsyncSession):
    """
    Test End-to-End: 
    1. Login with an admin user.
    2. Obtain access token.
    3. Use token to create a new user.
    """
    # 1. Setup Database with an Admin User and Role
    admin_password = "admin_secure_password"
    admin_role = Role(id=uuid.uuid4(), name="Admin", description="Administrator")
    db_session.add(admin_role)
    
    admin_user = User(
        id=uuid.uuid4(),
        email="admin_e2e@example.com",
        hashed_password=get_password_hash(admin_password),
        first_name="Admin",
        last_name="E2E",
        is_active=True
    )
    db_session.add(admin_user)
    await db_session.flush() # flush to get IDs if needed
    
    # Assign the admin role to the user
    user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
    db_session.add(user_role)
    await db_session.commit()
    
    # 2. Login to get the token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin_e2e@example.com", "password": admin_password}
    )
    
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token_data = login_response.json()
    assert "access_token" in token_data
    access_token = token_data["access_token"]
    
    # 3. Use the token to create a new user
    new_user_payload = {
        "email": "new_e2e_user@example.com",
        "password": "new_user_secure_password",
        "first_name": "New",
        "last_name": "E2EUser"
    }
    
    create_response = await client.post(
        "/api/v1/users/",
        json=new_user_payload,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert create_response.status_code == 201, f"Create user failed: {create_response.text}"
    created_user = create_response.json()["data"]
    
    # 4. Verify the created user's data
    assert created_user["email"] == "new_e2e_user@example.com"
    assert created_user["first_name"] == "New"
    assert created_user["last_name"] == "E2EUser"
    assert "id" in created_user
    assert "password" not in created_user # Password should not be returned in public response
    assert created_user["is_active"] is True
