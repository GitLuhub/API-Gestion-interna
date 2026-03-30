import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog

logger = logging.getLogger(__name__)

class AuditService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_action(
        self,
        action: str,
        entity: str,
        entity_id: str,
        user_id: str | None = None,
        details: dict | None = None
    ) -> AuditLog:
        """
        Logs an action performed on an entity.
        :param action: The action performed (e.g., 'CREATE', 'UPDATE', 'DELETE')
        :param entity: The name of the entity model (e.g., 'User', 'Role')
        :param entity_id: The ID of the specific entity instance
        :param user_id: ID of the user performing the action
        :param details: Additional JSON data (e.g., changes made)
        """
        try:
            audit_log = AuditLog(
                user_id=str(user_id) if user_id else None,
                action=action,
                entity=entity,
                entity_id=str(entity_id),
                details=details
            )
            self.session.add(audit_log)
            # We don't commit here, we just add it to the current transaction.
            # It will get committed alongside the main business logic transaction.
            return audit_log
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            raise
