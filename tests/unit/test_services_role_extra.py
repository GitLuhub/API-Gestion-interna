import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from app.services.role import RoleService
from app.models.user import User, Role
from app.core.exceptions import NotFoundException, BadRequestException

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
async def test_get_role_by_id(role_service, role_repo_mock):
    role_id = uuid.uuid4()
    mock_role = Role(id=role_id, name="Admin", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    role_repo_mock.get_by_id.return_value = mock_role
    
    result = await role_service.get_role_by_id(role_id)
    assert result.name == "Admin"

@pytest.mark.asyncio
async def test_get_role_by_id_not_found(role_service, role_repo_mock):
    role_repo_mock.get_by_id.return_value = None
    with pytest.raises(NotFoundException):
        await role_service.get_role_by_id(uuid.uuid4())

@pytest.mark.asyncio
async def test_assign_role_to_user(role_service, role_repo_mock, user_repo_mock, audit_service_mock):
    user_id = uuid.uuid4()
    role_id = uuid.uuid4()
    mock_user = User(id=user_id, email="test@test.com", is_deleted=False, roles=[])
    mock_role = Role(id=role_id, name="Admin")
    
    user_repo_mock.get_with_roles.return_value = mock_user
    role_repo_mock.get_by_id.return_value = mock_role
    role_repo_mock.db_session = AsyncMock()
    
    result = await role_service.assign_role_to_user(user_id, role_id)
    assert result is True

@pytest.mark.asyncio
async def test_revoke_role_from_user(role_service, role_repo_mock, user_repo_mock, audit_service_mock):
    user_id = uuid.uuid4()
    role_id = uuid.uuid4()
    mock_role = Role(id=role_id, name="Admin")
    mock_user = User(id=user_id, email="test@test.com", is_deleted=False, roles=[mock_role])
    
    user_repo_mock.get_with_roles.return_value = mock_user
    role_repo_mock.get_by_id.return_value = mock_role
    role_repo_mock.db_session = AsyncMock()
    
    result = await role_service.revoke_role_from_user(user_id, role_id)
    assert result is True

