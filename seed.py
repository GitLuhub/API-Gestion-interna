import asyncio
import logging
from sqlalchemy import select
from app.core.database import sessionmanager
from app.core.security import get_password_hash
from app.models import Role, User, UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed():
    async with sessionmanager.session() as session:
        # Create base roles
        roles = ["Admin", "User", "Manager"]
        role_objs = {}
        for role_name in roles:
            stmt = select(Role).filter_by(name=role_name)
            result = await session.execute(stmt)
            role = result.scalar_one_or_none()
            if not role:
                logger.info(f"Creating role: {role_name}")
                role = Role(name=role_name, description=f"{role_name.capitalize()} role")
                session.add(role)
                await session.flush()
            else:
                logger.info(f"Role already exists: {role_name}")
            role_objs[role_name] = role

        # Create admin user
        admin_email = "admin@example.com"
        stmt = select(User).filter_by(email=admin_email)
        result = await session.execute(stmt)
        admin_user = result.scalar_one_or_none()
        
        if not admin_user:
            logger.info(f"Creating admin user: {admin_email}")
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash("admin123"),
                first_name="Admin",
                last_name="User",
                is_active=True,
                is_superuser=True
            )
            session.add(admin_user)
            await session.flush()
            
            # Assign admin role
            logger.info("Assigning admin role to admin user")
            user_role = UserRole(user_id=admin_user.id, role_id=role_objs["Admin"].id)
            session.add(user_role)
        else:
            logger.info(f"Admin user already exists: {admin_email}")

        await session.commit()
        logger.info("Database seeding completed.")

if __name__ == "__main__":
    asyncio.run(seed())
