import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from app.services.user import UserService
from app.models.user import User

@pytest.fixture
def user_repo_mock():
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

from datetime import datetime
from app.schemas.user import UserUpdate

@pytest.mark.asyncio
async def test_update_user(user_service, user_repo_mock, audit_service_mock):
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, email="1@x.com", first_name="A", last_name="A", is_active=True, is_superuser=False, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    user_repo_mock.get_by_id.return_value = mock_user
    user_repo_mock.get_by_email.return_value = None
    
    updated_user_mock = User(id=user_id, email="2@x.com", first_name="A", last_name="A", is_active=True, is_superuser=False, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    user_repo_mock.update.return_value = updated_user_mock
    
    update_schema = UserUpdate(email="2@x.com")
    result = await user_service.update_user(user_id, update_schema)
    
    assert result.email == "2@x.com"
    user_repo_mock.update.assert_called_once()
    audit_service_mock.log_action.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_users(user_service, user_repo_mock):
    mock_users = [
        User(id=uuid.uuid4(), email="1@x.com", first_name="A", last_name="A", is_active=True, is_superuser=False, created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
        User(id=uuid.uuid4(), email="2@x.com", first_name="B", last_name="B", is_active=True, is_superuser=False, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    ]
    user_repo_mock.get_all.return_value = mock_users
    user_repo_mock.count.return_value = 2
    
    result, total = await user_service.get_all_users()
    assert total == 2
    assert len(result) == 2
    user_repo_mock.get_all.assert_called_once()
    user_repo_mock.count.assert_called_once()
