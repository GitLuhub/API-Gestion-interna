import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from app.services.user import UserService
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User

@pytest.fixture
def user_repo_mock():
    return AsyncMock()

@pytest.fixture
def role_repo_mock():
    return AsyncMock()

@pytest.fixture
def audit_service_mock():
    return AsyncMock()

@pytest.fixture
def user_service(user_repo_mock, audit_service_mock):
    return UserService(
        user_repo=user_repo_mock,
        audit_service=audit_service_mock
    )

@pytest.mark.asyncio
async def test_get_user_found(user_service, user_repo_mock):
    user_id = uuid.uuid4()
    mock_user = User(
        id=user_id, email="test@example.com", first_name="A", last_name="B", 
        is_active=True, is_superuser=False, is_deleted=False, 
        created_at=datetime.utcnow(), updated_at=datetime.utcnow()
    )
    user_repo_mock.get_by_id.return_value = mock_user
    
    result = await user_service.get_user_by_id(user_id)
    assert result.id == user_id
    assert result.email == "test@example.com"
    user_repo_mock.get_by_id.assert_called_once_with(user_id)

from app.core.exceptions import NotFoundException

@pytest.mark.asyncio
async def test_get_user_not_found(user_service, user_repo_mock):
    user_repo_mock.get_by_id.return_value = None
    user_id = uuid.uuid4()
    
    with pytest.raises(NotFoundException):
        await user_service.get_user_by_id(user_id)

@pytest.mark.asyncio
async def test_create_user_success(user_service, user_repo_mock, audit_service_mock):
    user_repo_mock.get_by_email.return_value = None
    
    new_user_mock = User(
        id=uuid.uuid4(), 
        email="new@example.com", 
        first_name="Test", 
        last_name="User", 
        is_active=True,
        is_superuser=False,
        is_deleted=False,
        created_at=datetime.utcnow(), 
        updated_at=datetime.utcnow()
    )
    user_repo_mock.create.return_value = new_user_mock
    
    user_create = UserCreate(email="new@example.com", password="Password123!", first_name="Test", last_name="User")
    actor_id = uuid.uuid4()
    
    result = await user_service.create_user(user_create, actor_id=actor_id)
    
    assert result.email == "new@example.com"
    user_repo_mock.create.assert_called_once()
    audit_service_mock.log_action.assert_called_once()

@pytest.mark.asyncio
async def test_delete_user(user_service, user_repo_mock, audit_service_mock):
    user_id = uuid.uuid4()
    mock_user = User(
        id=user_id, email="test@example.com", first_name="A", last_name="B", 
        is_active=True, is_superuser=False, is_deleted=False, 
        created_at=datetime.utcnow(), updated_at=datetime.utcnow()
    )
    user_repo_mock.get_by_id.return_value = mock_user
    user_repo_mock.update.return_value = mock_user
    
    actor_id = uuid.uuid4()
    result = await user_service.delete_user(user_id, actor_id=actor_id)
    
    assert result is True
    user_repo_mock.update.assert_called_once()
    audit_service_mock.log_action.assert_called_once()
