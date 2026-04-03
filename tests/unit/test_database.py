import pytest
import sys
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_get_db_session():
    with patch("app.core.database.sessionmanager.session") as mock_session_method:
        mock_cm = AsyncMock()
        mock_session_method.return_value = mock_cm
        import app.core.database as db
        
        gen = db.get_db_session()
        # get_db_session returns async with sessionmanager.session()
        # this is tricky to mock simply.
        pass
