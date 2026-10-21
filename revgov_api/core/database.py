from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.engine import make_url
import asyncpg
import logging
import os
from dotenv import load_dotenv
from core.security import get_password_hash


logger = logging.getLogger(__name__)

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


async def ensure_database_exists(url_str: str | None = None) -> bool:
    """
    Checks if the target database exists; if not, connects to the default
    PostgreSQL maintenance database ('postgres' or 'template1') and creates it.
    """
    target_url = url_str or DATABASE_URL
    try:
        url = make_url(target_url)
        target_db = url.database
        if not target_db:
            return True

        user = url.username
        password = url.password
        host = url.host or "localhost"
        port = url.port or 5432

        # 1. Quick test to see if the database already exists and is reachable
        try:
            conn = await asyncpg.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=target_db,
            )
            await conn.close()
            return True
        except asyncpg.InvalidCatalogNameError:
            logger.info(f"Database '{target_db}' does not exist. Attempting to create it...")
        except Exception as e:
            logger.warning(f"Connection check to '{target_db}' encountered: {e}")
            return False

        # 2. Connect to maintenance database to create target_db
        maintenance_dbs = ["postgres", "template1"]
        for maint_db in maintenance_dbs:
            try:
                maint_conn = await asyncpg.connect(
                    user=user,
                    password=password,
                    host=host,
                    port=port,
                    database=maint_db,
                )
                try:
                    exists = await maint_conn.fetchval(
                        "SELECT 1 FROM pg_database WHERE datname = $1", target_db
                    )
                    if not exists:
                        escaped_db = target_db.replace('"', '""')
                        await maint_conn.execute(f'CREATE DATABASE "{escaped_db}"')
                        logger.info(f"Database '{target_db}' successfully created.")
                    return True
                finally:
                    await maint_conn.close()
            except Exception as ex:
                logger.warning(f"Could not connect to maintenance database '{maint_db}': {ex}")
                continue

        logger.error(
            f"Failed to automatically create database '{target_db}'. "
            "Please ensure the database server is running and user has CREATEDB privileges."
        )
        return False
    except Exception as e:
        logger.error(f"Unexpected error in ensure_database_exists: {e}")
        return False


async def init_db():
    await ensure_database_exists()
    from sqlalchemy import select, text
    import modules.administration.models  # noqa: F401

    #  13/10/26
    import modules.inventory.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS designation VARCHAR;"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS mobile_number VARCHAR(10);")) 
    
    
    from auth.models import Role, User
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
    from core.constants import get_default_permissions_for_role
    
    DEFAULT_ROLE_PERMISSIONS = {
        role: get_default_permissions_for_role(role)
        for role in [
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
        ]
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
                from sqlalchemy.orm.attributes import flag_modified

                role_obj.permissions = default_perms
                flag_modified(role_obj, "permissions")
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

        # 4. Seed Master Lookups
        from modules.masters.models import SystemLookup

        default_lookups = [
            {
                "type": "ASSET_CATEGORY",
                "code": "NOT_REUSED",
                "label": "Not Reused",
                "sort_order": 1,
            },
            {
                "type": "ASSET_CATEGORY",
                "code": "LOW_REUSE",
                "label": "Low Reuse",
                "sort_order": 2,
            },
            {
                "type": "ASSET_CATEGORY",
                "code": "MODERATE_REUSE",
                "label": "Moderate Reuse",
                "sort_order": 3,
            },
            {
                "type": "ASSET_CATEGORY",
                "code": "HIGH_REUSE",
                "label": "High Reuse",
                "sort_order": 4,
            },
            {
                "type": "ASSET_CATEGORY",
                "code": "ENTERPRISE_ASSET",
                "label": "Highly Reusable / Enterprise Asset",
                "sort_order": 5,
            },
            {
                "type": "MATURITY_LEVEL",
                "code": "STAGE_1",
                "label": "Stage 1",
                "sort_order": 1,
            },
            {
                "type": "MATURITY_LEVEL",
                "code": "STAGE_2",
                "label": "Stage 2",
                "sort_order": 2,
            },
            {
                "type": "MATURITY_LEVEL",
                "code": "STAGE_3",
                "label": "Stage 3",
                "sort_order": 3,
            },
        ]

        for lookup_data in default_lookups:
            result = await session.execute(
                select(SystemLookup).where(
                    SystemLookup.type == lookup_data["type"],
                    SystemLookup.code == lookup_data["code"],
                )
            )
            existing_lookup = result.scalar_one_or_none()
            if not existing_lookup:
                new_lookup = SystemLookup(**lookup_data)
                session.add(new_lookup)

        await session.commit()




# 13/10/26

