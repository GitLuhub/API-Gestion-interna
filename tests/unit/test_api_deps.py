import pytest
from unittest.mock import AsyncMock
from app.api.deps import get_user_repository, get_role_repository, get_audit_service
from app.api.deps import get_user_service, get_role_service
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.services.audit import AuditService
from app.services.user import UserService
from app.services.role import RoleService

@pytest.mark.asyncio
async def test_deps_repos():
    db = AsyncMock()
    user_repo = await get_user_repository(db)
    assert isinstance(user_repo, UserRepository)
    
    role_repo = await get_role_repository(db)
    assert isinstance(role_repo, RoleRepository)
    
    audit_svc = await get_audit_service(db)
    assert isinstance(audit_svc, AuditService)

@pytest.mark.asyncio
async def test_deps_services():
    user_repo = AsyncMock()
    audit_svc = AsyncMock()
    user_svc = await get_user_service(user_repo, audit_svc)
    assert isinstance(user_svc, UserService)
    
    role_repo = AsyncMock()
    role_svc = await get_role_service(role_repo, user_repo, audit_svc)
    assert isinstance(role_svc, RoleService)
