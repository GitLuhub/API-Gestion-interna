import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.role import RoleService
from app.schemas.role import RoleCreate
from app.models.user import Role

@pytest.fixture
def role_repo_mock():
    return AsyncMock()

@pytest.fixture
def user_repo_mock():
    return AsyncMock()

@pytest.fixture
def audit_service_mock():
    return AsyncMock()

@pytest.fixture
def role_service(role_repo_mock, user_repo_mock, audit_service_mock):
    return RoleService(
        role_repo=role_repo_mock,
        user_repo=user_repo_mock,
        audit_service=audit_service_mock
    )

@pytest.mark.asyncio
async def test_get_roles(role_service, role_repo_mock):
    mock_roles = [
        Role(id=uuid.uuid4(), name="Admin", created_at=datetime.utcnow(), updated_at=datetime.utcnow()), 
        Role(id=uuid.uuid4(), name="User", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    ]
    role_repo_mock.get_all.return_value = mock_roles
    
    result, total = await role_service.get_all_roles()
    assert len(result) == 2
    role_repo_mock.get_all.assert_called_once()

@pytest.mark.asyncio
@patch("app.services.role.delete_cache_pattern", new_callable=AsyncMock)
async def test_create_role(mock_delete_cache, role_service, role_repo_mock, audit_service_mock):
    role_repo_mock.get_by_name.return_value = None
    new_role = Role(id=uuid.uuid4(), name="Manager", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    role_repo_mock.create.return_value = new_role
    
    role_in = RoleCreate(name="Manager", description="Manage stuff")
    actor_id = uuid.uuid4()
    
    result = await role_service.create_role(role_in, actor_id=actor_id)
    assert result.name == "Manager"
    role_repo_mock.create.assert_called_once()
    audit_service_mock.log_action.assert_called_once()
