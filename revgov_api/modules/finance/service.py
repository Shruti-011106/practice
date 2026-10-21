from core.service import BaseService
from . import models, schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from auth.models import User
from core.constants import ROLE_CEO, ROLE_SUPER_ADMIN
from modules.hr.models import Employee

async def _get_employee_id_for_user(db: AsyncSession, user: User) -> int | None:
    result = await db.execute(select(Employee).where(Employee.user_id == user.id))
    employee = result.scalar_one_or_none()
    return employee.id if employee else None

def _is_admin_or_ceo(user: User) -> bool:
    if not user.roles:
        return False
    role_names = [role.name for role in user.roles]
    return ROLE_SUPER_ADMIN in role_names or ROLE_CEO in role_names


class POTrackerService(BaseService[models.POTracker, schemas.POTrackerCreate, schemas.POTrackerUpdate]):
    async def create_by_user(self, db: AsyncSession, obj_in: schemas.POTrackerCreate, user: User):
        emp_id = await _get_employee_id_for_user(db, user)
        obj_in_data = obj_in.model_dump()
        obj_in_data["finance_owner_id"] = emp_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_all_with_kpis_by_user(self, db: AsyncSession, user: User):
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(self.model.finance_owner_id == emp_id)
            else:
                return {"kpis": {"total_pos": 0, "pending_approval": 0, "completed": 0, "total_amount": 0}, "data": []}
        
        result = await db.execute(query.order_by(self.model.id.desc()))
        records = result.scalars().all()
        
        kpis = {
            "total_pos": len(records),
            "pending_approval": sum([1 for r in records if r.approval_status and r.approval_status.lower() == "pending approval"]),
            "completed": sum([1 for r in records if r.payment_status and r.payment_status.lower() == "completed"]),
            "total_amount": sum([r.amount for r in records if r.amount])
        }
        return {"kpis": kpis, "data": records}

potracker_service = POTrackerService(models.POTracker)


class InvoiceTrackerService(BaseService[models.InvoiceTracker, schemas.InvoiceTrackerCreate, schemas.InvoiceTrackerUpdate]):
    async def create_by_user(self, db: AsyncSession, obj_in: schemas.InvoiceTrackerCreate, user: User):
        emp_id = await _get_employee_id_for_user(db, user)
        obj_in_data = obj_in.model_dump()
        obj_in_data["finance_owner_id"] = emp_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_all_with_kpis_by_user(self, db: AsyncSession, user: User):
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(self.model.finance_owner_id == emp_id)
            else:
                return {"kpis": {"total_invoices": 0, "pending_approval": 0, "completed": 0, "total_amount": 0}, "data": []}
        
        result = await db.execute(query.order_by(self.model.id.desc()))
        records = result.scalars().all()
        
        kpis = {
            "total_invoices": len(records),
            "pending_approval": sum([1 for r in records if r.payment_status and r.payment_status.lower() == "pending approval"]),
            "completed": sum([1 for r in records if r.payment_status and r.payment_status.lower() == "completed"]),
            "total_amount": sum([r.invoice_amount for r in records if r.invoice_amount])
        }
        return {"kpis": kpis, "data": records}

invoicetracker_service = InvoiceTrackerService(models.InvoiceTracker)


class BudgetTrackerService(BaseService[models.BudgetTracker, schemas.BudgetTrackerCreate, schemas.BudgetTrackerUpdate]):
    async def create_by_user(self, db: AsyncSession, obj_in: schemas.BudgetTrackerCreate, user: User):
        emp_id = await _get_employee_id_for_user(db, user)
        obj_in_data = obj_in.model_dump()
        obj_in_data["finance_owner_id"] = emp_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_all_with_kpis_by_user(self, db: AsyncSession, user: User):
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(self.model.finance_owner_id == emp_id)
            else:
                return {"kpis": {"total_projects": 0, "pending_approval": 0, "total_budget": 0, "total_remaining_budget": 0}, "data": []}
        
        result = await db.execute(query.order_by(self.model.id.desc()))
        records = result.scalars().all()
        
        kpis = {
            "total_projects": len(records),
            "pending_approval": sum([1 for r in records if r.approval_status and r.approval_status.lower() == "pending approval"]),
            "total_budget": sum([r.budget for r in records if r.budget]),
            "total_remaining_budget": sum([r.remaining for r in records if r.remaining])
        }
        return {"kpis": kpis, "data": records}

budgettracker_service = BudgetTrackerService(models.BudgetTracker)


class RequestOrderTrackerService(BaseService[models.RequestOrderTracker, schemas.RequestOrderTrackerCreate, schemas.RequestOrderTrackerUpdate]):
    async def create_by_user(self, db: AsyncSession, obj_in: schemas.RequestOrderTrackerCreate, user: User):
        emp_id = await _get_employee_id_for_user(db, user)
        obj_in_data = obj_in.model_dump()
        obj_in_data["finance_owner_id"] = emp_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_all_with_kpis_by_user(self, db: AsyncSession, user: User):
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(self.model.finance_owner_id == emp_id)
            else:
                return {"kpis": {"total_requests": 0, "pending_approval": 0, "approved_requests": 0, "total_cost": 0}, "data": []}
        
        result = await db.execute(query.order_by(self.model.id.desc()))
        records = result.scalars().all()
        
        kpis = {
            "total_requests": len(records),
            "pending_approval": sum([1 for r in records if r.approval_status and r.approval_status.lower() == "pending approval"]),
            "approved_requests": sum([1 for r in records if r.approval_status and r.approval_status.lower() == "approved"]),
            "total_cost": sum([r.cost for r in records if r.cost])
        }
        return {"kpis": kpis, "data": records}

requestordertracker_service = RequestOrderTrackerService(models.RequestOrderTracker)


class PaymentTrackerService(BaseService[models.PaymentTracker, schemas.PaymentTrackerCreate, schemas.PaymentTrackerUpdate]):
    async def create_by_user(self, db: AsyncSession, obj_in: schemas.PaymentTrackerCreate, user: User):
        emp_id = await _get_employee_id_for_user(db, user)
        obj_in_data = obj_in.model_dump()
        obj_in_data["finance_owner_id"] = emp_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_all_with_kpis_by_user(self, db: AsyncSession, user: User):
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(self.model.finance_owner_id == emp_id)
            else:
                return {"kpis": {"total_payments": 0, "completed_payments": 0, "pending_payments": 0, "total_amount": 0}, "data": []}
        
        result = await db.execute(query.order_by(self.model.id.desc()))
        records = result.scalars().all()
        
        kpis = {
            "total_payments": len(records),
            "completed_payments": sum([1 for r in records if r.status and r.status.lower() == "completed"]),
            "pending_payments": sum([1 for r in records if r.status and r.status.lower() == "pending"]),
            "total_amount": sum([r.amount for r in records if r.amount])
        }
        return {"kpis": kpis, "data": records}

paymenttracker_service = PaymentTrackerService(models.PaymentTracker)


class RevenueTrackerService(BaseService[models.RevenueTracker, schemas.RevenueTrackerCreate, schemas.RevenueTrackerUpdate]):
    async def create_by_user(self, db: AsyncSession, obj_in: schemas.RevenueTrackerCreate, user: User):
        emp_id = await _get_employee_id_for_user(db, user)
        obj_in_data = obj_in.model_dump()
        obj_in_data["sales_owner_id"] = emp_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_all_with_kpis_by_user(self, db: AsyncSession, user: User):
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(self.model.sales_owner_id == emp_id)
            else:
                return {"kpis": {"total_records": 0, "completed_records": 0, "total_target_revenue": 0, "total_achieved_revenue": 0}, "data": []}
        
        result = await db.execute(query.order_by(self.model.id.desc()))
        records = result.scalars().all()
        
        kpis = {
            "total_records": len(records),
            "completed_records": sum([1 for r in records if r.status and r.status.lower() == "completed"]),
            "total_target_revenue": sum([r.target_revenue for r in records if r.target_revenue]),
            "total_achieved_revenue": sum([r.achieved_revenue for r in records if r.achieved_revenue])
        }
        return {"kpis": kpis, "data": records}

revenuetracker_service = RevenueTrackerService(models.RevenueTracker)

