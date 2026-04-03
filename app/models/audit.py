from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from app.models.base import Base, UUIDMixin, TimestampMixin

class AuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "audit_logs"
    
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., 'CREATE', 'UPDATE', 'DELETE'
    entity: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., 'User', 'Role'
    entity_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True) # Could store old/new values

    actor: Mapped["User"] = relationship(foreign_keys=[user_id])
