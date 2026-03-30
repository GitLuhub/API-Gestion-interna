from sqlalchemy import String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.models.base import Base, UUIDMixin, TimestampMixin

class UserRole(Base):
    __tablename__ = "user_roles"
    
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    
class Role(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "roles"
    
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    
    users: Mapped[list["User"]] = relationship(secondary="user_roles", back_populates="roles")

class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    
    # Soft delete support
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    roles: Mapped[list["Role"]] = relationship(secondary="user_roles", back_populates="users", lazy="joined")
