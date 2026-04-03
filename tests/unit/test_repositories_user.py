import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from app.repositories.user import UserRepository
from app.models.user import User

@pytest.fixture
def db_session_mock():
    return AsyncMock()

@pytest.fixture
def user_repo(db_session_mock):
    return UserRepository(db_session_mock)

@pytest.mark.asyncio
async def test_get_by_email(user_repo, db_session_mock):
    mock_result = MagicMock()
    mock_user = User(id=uuid.uuid4(), email="test@repo.com")
    mock_result.scalars().first.return_value = mock_user
    db_session_mock.execute.return_value = mock_result
    
    result = await user_repo.get_by_email("test@repo.com")
    assert result is not None
    assert result.email == "test@repo.com"
    db_session_mock.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_by_email_with_roles(user_repo, db_session_mock):
    mock_result = MagicMock()
    mock_user = User(id=uuid.uuid4(), email="test@repo.com")
    mock_result.scalars().first.return_value = mock_user
    db_session_mock.execute.return_value = mock_result
    
    result = await user_repo.get_by_email_with_roles("test@repo.com")
    assert result is not None
    assert result.email == "test@repo.com"
    db_session_mock.execute.assert_called_once()
