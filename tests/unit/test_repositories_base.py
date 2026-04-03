import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from app.repositories.base import BaseRepository
from app.models.base import Base
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

class DummyModel(Base):
    __tablename__ = "dummy"
    id = Column(String, primary_key=True)
    name = Column(String)

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def base_repo(mock_session):
    return BaseRepository(DummyModel, mock_session)

@pytest.mark.asyncio
async def test_base_repo_get_all(base_repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [DummyModel(id=uuid.uuid4(), name="Test")]
    mock_session.execute.return_value = mock_result
    
    result = await base_repo.get_all()
    assert len(result) == 1
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_base_repo_count(base_repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = 10
    mock_session.execute.return_value = mock_result
    
    result = await base_repo.count()
    assert result == 10
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_base_repo_create(base_repo, mock_session):
    data = {"name": "Test"}
    result = await base_repo.create(data)
    assert result.name == "Test"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_base_repo_update(base_repo, mock_session):
    obj = DummyModel(id=uuid.uuid4(), name="Old")
    data = {"name": "New"}
    
    result = await base_repo.update(obj, data)
    assert result.name == "New"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_base_repo_delete(base_repo, mock_session):
    uid = uuid.uuid4()
    
    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result
    
    result = await base_repo.delete(uid)
    assert result is True
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()


