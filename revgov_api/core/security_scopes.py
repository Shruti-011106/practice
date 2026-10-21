from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import User
from core.constants import ROLE_CEO, ROLE_SUPER_ADMIN, ROLE_HR_MANAGER
from modules.hr.models import Employee

async def get_employee_id_for_user(db: AsyncSession, user: User) -> int | None:
    result = await db.execute(select(Employee).where(Employee.email == user.email))
    employee = result.scalar_one_or_none()
    return employee.id if employee else None

async def get_employee_for_user(db: AsyncSession, user: User) -> Employee | None:
    result = await db.execute(select(Employee).where(Employee.email == user.email))
    return result.scalar_one_or_none()

def is_admin_or_ceo(user: User) -> bool:
    role_names = [role.name for role in user.roles]
    return ROLE_SUPER_ADMIN in role_names or ROLE_CEO in role_names

def is_admin_ceo_or_hr(user: User) -> bool:
    role_names = [role.name for role in user.roles]
    return ROLE_SUPER_ADMIN in role_names or ROLE_CEO in role_names or ROLE_HR_MANAGER in role_names
