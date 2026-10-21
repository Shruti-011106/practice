from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    DATABASE_URL = (
        f"postgresql+asyncpg://{os.getenv('POSTGRES_USER', 'egt_user')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'pg123')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'egt_db')}"
    )


engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    from sqlalchemy import select
    from auth.models import Role, User
    from core.security import get_password_hash
    from core.constants import (
        ROLE_SUPER_ADMIN,
        ROLE_CEO,
        ROLE_HR_MANAGER,
        ROLE_RECRUITER,
        ROLE_FINANCE_MANAGER,
        ROLE_PROJECT_MANAGER,
        ROLE_EMPLOYEE,
        ROLE_SALES_MANAGER,
        ROLE_PRESALES_MANAGER,
        ROLE_MARKETING_MANAGER,
        ROLE_LND_MANAGER,
        ROLE_CS_MANAGER,
    )

    DEFAULT_ROLE_PERMISSIONS = {
        ROLE_SUPER_ADMIN: {
            "QBR": "CRUD",
            "Escalation": "CRUD",
            "Revenue": "CRUD",
            "Project": "CRUD",
            "Finance/PO": "CRUD",
            "Finance/Invoice": "CRUD",
            "Finance/Budget": "CRUD",
            "HR/Employees": "CRUD",
            "HR/Recruitment": "CRUD",
            "L&D": "CRUD",
            "Sales/Proposals": "CRUD",
            "Sales/RFP": "CRUD",
            "Sales/POC": "CRUD",
            "Presales/BID": "CRUD",
            "Marketing": "CRUD",
            "Masters": "CRUD",
            "Settings": "CRUD",
            "Audit Log": "CRUD",
        },
        ROLE_CEO: {
            "QBR": "CRUD",
            "Escalation": "CRUD",
            "Revenue": "CRUD",
            "Project": "R",
            "Finance/PO": "CRUD",
            "Finance/Invoice": "CRUD",
            "Finance/Budget": "CRUD",
            "HR/Employees": "R",
            "HR/Recruitment": "R",
            "L&D": "R",
            "Sales/Proposals": "R",
            "Sales/RFP": "R",
            "Sales/POC": "R",
            "Presales/BID": "R",
            "Marketing": "R",
            "Masters": "R",
            "Settings": "CRUD",
            "Audit Log": "R",
        },
        ROLE_CS_MANAGER: {
            "QBR": "CU",
            "Escalation": "CU",
            "Revenue": "R",
            "Project": "R",
            "Finance/PO": "—",
            "Finance/Invoice": "—",
            "Finance/Budget": "—",
            "HR/Employees": "—",
            "HR/Recruitment": "—",
            "L&D": "—",
            "Sales/Proposals": "—",
            "Sales/RFP": "—",
            "Sales/POC": "—",
            "Presales/BID": "—",
            "Marketing": "—",
            "Masters": "—",
            "Settings": "—",
            "Audit Log": "—",
        },
        ROLE_PROJECT_MANAGER: {
            "QBR": "R",
            "Escalation": "R",
            "Revenue": "R",
            "Project": "CRUD",
            "Finance/PO": "CR",
            "Finance/Invoice": "R",
            "Finance/Budget": "R",
            "HR/Employees": "R",
            "HR/Recruitment": "R",
            "L&D": "R",
            "Sales/Proposals": "R",
            "Sales/RFP": "R",
            "Sales/POC": "R",
            "Presales/BID": "R",
            "Marketing": "R",
            "Masters": "R",
            "Settings": "R",
            "Audit Log": "R",
        },
        ROLE_FINANCE_MANAGER: {
            "QBR": "—",
            "Escalation": "—",
            "Revenue": "R",
            "Project": "R",
            "Finance/PO": "CRUD",
            "Finance/Invoice": "CRUD",
            "Finance/Budget": "CRUD",
            "HR/Employees": "—",
            "HR/Recruitment": "—",
            "L&D": "—",
            "Sales/Proposals": "—",
            "Sales/RFP": "—",
            "Sales/POC": "—",
            "Presales/BID": "—",
            "Marketing": "—",
            "Masters": "—",
            "Settings": "—",
            "Audit Log": "—",
        },
        ROLE_HR_MANAGER: {
            "QBR": "—",
            "Escalation": "—",
            "Revenue": "—",
            "Project": "—",
            "Finance/PO": "—",
            "Finance/Invoice": "—",
            "Finance/Budget": "R",
            "HR/Employees": "CRUD",
            "HR/Recruitment": "CRUD",
            "L&D": "CRUD",
            "Sales/Proposals": "—",
            "Sales/RFP": "—",
            "Sales/POC": "—",
            "Presales/BID": "—",
            "Marketing": "R",
            "Masters": "—",
            "Settings": "—",
            "Audit Log": "—",
        },
        ROLE_SALES_MANAGER: {
            "QBR": "R",
            "Escalation": "R",
            "Revenue": "R",
            "Project": "—",
            "Finance/PO": "—",
            "Finance/Invoice": "—",
            "Finance/Budget": "—",
            "HR/Employees": "—",
            "HR/Recruitment": "—",
            "L&D": "—",
            "Sales/Proposals": "CRUD",
            "Sales/RFP": "CRUD",
            "Sales/POC": "CRUD",
            "Presales/BID": "R",
            "Marketing": "R",
            "Masters": "—",
            "Settings": "—",
            "Audit Log": "—",
        },
        ROLE_PRESALES_MANAGER: {
            "QBR": "—",
            "Escalation": "—",
            "Revenue": "—",
            "Project": "—",
            "Finance/PO": "—",
            "Finance/Invoice": "—",
            "Finance/Budget": "—",
            "HR/Employees": "—",
            "HR/Recruitment": "—",
            "L&D": "R",
            "Sales/Proposals": "R",
            "Sales/RFP": "R",
            "Sales/POC": "CRUD",
            "Presales/BID": "CRUD",
            "Marketing": "—",
            "Masters": "—",
            "Settings": "—",
            "Audit Log": "—",
        },
        ROLE_MARKETING_MANAGER: {
            "QBR": "—",
            "Escalation": "—",
            "Revenue": "—",
            "Project": "—",
            "Finance/PO": "—",
            "Finance/Invoice": "—",
            "Finance/Budget": "—",
            "HR/Employees": "—",
            "HR/Recruitment": "R",
            "L&D": "R",
            "Sales/Proposals": "—",
            "Sales/RFP": "—",
            "Sales/POC": "—",
            "Presales/BID": "—",
            "Marketing": "CRUD",
            "Masters": "—",
            "Settings": "—",
            "Audit Log": "—",
        },
        ROLE_EMPLOYEE: {
            "QBR": "—",
            "Escalation": "—",
            "Revenue": "—",
            "Project": "—",
            "Finance/PO": "—",
            "Finance/Invoice": "—",
            "Finance/Budget": "—",
            "HR/Employees": "—",
            "HR/Recruitment": "—",
            "L&D": "R",
            "Sales/Proposals": "—",
            "Sales/RFP": "—",
            "Sales/POC": "—",
            "Presales/BID": "—",
            "Marketing": "—",
            "Masters": "—",
            "Settings": "—",
            "Audit Log": "—",
        },
        ROLE_RECRUITER: {
            "QBR": "—",
            "Escalation": "—",
            "Revenue": "—",
            "Project": "—",
            "Finance/PO": "—",
            "Finance/Invoice": "—",
            "Finance/Budget": "—",
            "HR/Employees": "—",
            "HR/Recruitment": "CRUD",
            "L&D": "—",
            "Sales/Proposals": "—",
            "Sales/RFP": "—",
            "Sales/POC": "—",
            "Presales/BID": "—",
            "Marketing": "—",
            "Masters": "—",
            "Settings": "—",
            "Audit Log": "—",
        },
        ROLE_LND_MANAGER: {
            "QBR": "—",
            "Escalation": "—",
            "Revenue": "—",
            "Project": "—",
            "Finance/PO": "—",
            "Finance/Invoice": "—",
            "Finance/Budget": "—",
            "HR/Employees": "—",
            "HR/Recruitment": "—",
            "L&D": "CRUD",
            "Sales/Proposals": "—",
            "Sales/RFP": "—",
            "Sales/POC": "—",
            "Presales/BID": "—",
            "Marketing": "—",
            "Masters": "—",
            "Settings": "—",
            "Audit Log": "—",
        },
    }

    async with AsyncSessionLocal() as session:
        # 1. Seed Roles
        result = await session.execute(select(Role))
        existing_roles = {role.name: role for role in result.scalars().all()}

        seeded_roles = {}
        for role_name, default_perms in DEFAULT_ROLE_PERMISSIONS.items():
            if role_name not in existing_roles:
                new_role = Role(name=role_name, permissions=default_perms)
                session.add(new_role)
                seeded_roles[role_name] = new_role
            else:
                role_obj = existing_roles[role_name]
                # Always sync permissions with the default list in code
                role_obj.permissions = default_perms
                seeded_roles[role_name] = role_obj

        await session.commit()

        # Refresh session to ensure all roles have IDs loaded
        for role in seeded_roles.values():
            await session.refresh(role)

        # 2. Seed Default Super Admin
        admin_email = "admin@egt.com"
        result = await session.execute(select(User).where(User.email == admin_email))
        admin_user = result.scalar_one_or_none()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash("Admin@123"),
                first_name="System",
                last_name="Admin",
                is_active=True,
                roles=[seeded_roles[ROLE_SUPER_ADMIN]],
            )
            session.add(admin_user)

        # 3. Seed Default CEO
        ceo_email = "ceo@egt.com"
        result = await session.execute(select(User).where(User.email == ceo_email))
        ceo_user = result.scalar_one_or_none()
        if not ceo_user:
            ceo_user = User(
                email=ceo_email,
                hashed_password=get_password_hash("Ceo@123"),
                first_name="System",
                last_name="CEO",
                is_active=True,
                roles=[seeded_roles[ROLE_CEO]],
            )
            session.add(ceo_user)

        await session.commit()
