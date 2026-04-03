import pytest
from app.services.audit import AuditService
from unittest.mock import AsyncMock, patch

@pytest.fixture
def audit_svc():
    return AuditService(session=AsyncMock())

@pytest.mark.asyncio
async def test_audit_log_action(audit_svc):
    with patch("app.services.audit.logger") as mock_logger:
        await audit_svc.log_action(
            action="CREATE",
            entity="User",
            entity_id="123",
            user_id="456",
            details={"k": "v"}
        )
        mock_logger.info.assert_called_once()
        log_call = mock_logger.info.call_args[0][0]
        assert "Audit - User CREATE by 456" in log_call
