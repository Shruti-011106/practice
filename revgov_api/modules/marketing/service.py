from core.service import BaseService
from . import models, schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from datetime import date
from auth.models import User
from core.constants import ROLE_CEO, ROLE_SUPER_ADMIN
from modules.hr.models import Employee

async def _get_employee_id_for_user(db: AsyncSession, user: User) -> int | None:
    result = await db.execute(select(Employee).where(Employee.user_id == user.id))
    employee = result.scalar_one_or_none()
    return employee.id if employee else None

def _is_admin_or_ceo(user: User) -> bool:
    role_names = [role.name for role in user.roles]
    return ROLE_SUPER_ADMIN in role_names or ROLE_CEO in role_names



class EventWebinarService(
    BaseService[
        models.EventWebinar, schemas.EventWebinarCreate, schemas.EventWebinarUpdate
    ]
):
    async def get_all_with_kpis_by_user(self, db: AsyncSession, user: User):
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(
                    or_(
                        self.model.owner_id == emp_id,
                        self.model.created_by_id == emp_id
                    )
                )
            else:
                return {"kpis": {"total_events": 0, "total_participants": 0, "leads_generated": 0, "planned_events": 0}, "data": []}
        
        result = await db.execute(query.order_by(self.model.id.desc()))
        records = result.scalars().all()
        
        today = date.today()
        kpis = {
            "total_events": len(records),
            "total_participants": sum([r.participants for r in records if r.participants]),
            "leads_generated": sum([r.leads_generated for r in records if r.leads_generated]),
            "planned_events": sum([1 for r in records if r.date and r.date >= today])
        }
        return {"kpis": kpis, "data": records}

    async def create_by_user(self, db: AsyncSession, obj_in, user: User):
        obj_in_data = obj_in.model_dump()
        emp_id = await _get_employee_id_for_user(db, user)
        if emp_id:
            obj_in_data["created_by_id"] = emp_id
            
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


eventwebinar_service = EventWebinarService(models.EventWebinar)


class ContentBrandingService(
    BaseService[
        models.ContentBranding,
        schemas.ContentBrandingCreate,
        schemas.ContentBrandingUpdate,
    ]
):
    async def get_all_with_kpis_by_user(self, db: AsyncSession, user: User):
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(
                    or_(
                        self.model.owner_id == emp_id,
                        self.model.created_by_id == emp_id
                    )
                )
            else:
                return {"kpis": {"total_assets": 0, "approved_assets": 0, "pending_review": 0, "high_reusability": 0}, "data": []}
                
        result = await db.execute(query.order_by(self.model.id.desc()))
        records = result.scalars().all()
        
        kpis = {
            "total_assets": len(records),
            "approved_assets": sum([1 for r in records if r.approval_status and r.approval_status.lower() == "approved"]),
            "pending_review": sum([1 for r in records if r.approval_status and r.approval_status.lower() != "approved"]),
            "high_reusability": sum([1 for r in records if r.reusability])
        }
        return {"kpis": kpis, "data": records}

    async def create_by_user(self, db: AsyncSession, obj_in, user: User):
        obj_in_data = obj_in.model_dump()
        emp_id = await _get_employee_id_for_user(db, user)
        if emp_id:
            obj_in_data["created_by_id"] = emp_id
            
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


contentbranding_service = ContentBrandingService(models.ContentBranding)


class CampaignService(
    BaseService[models.Campaign, schemas.CampaignCreate, schemas.CampaignUpdate]
):
    async def get_all_with_kpis_by_user(self, db: AsyncSession, user: User):
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(
                    or_(
                        self.model.campaign_owner_id == emp_id,
                        self.model.created_by_id == emp_id
                    )
                )
            else:
                return {"kpis": {"total_campaigns": 0, "active_campaigns": 0, "high_roi": 0, "planned_campaigns": 0}, "data": []}
                
        result = await db.execute(query.order_by(self.model.id.desc()))
        records = result.scalars().all()
        
        today = date.today()
        kpis = {
            "total_campaigns": len(records),
            "active_campaigns": sum([1 for r in records if r.status and r.status.lower() in ["in progress", "active"]]),
            "high_roi": sum([1 for r in records if r.roi and r.roi >= 2.0]),
            "planned_campaigns": sum([1 for r in records if (r.status and r.status.lower() == "planned") or (r.start_date and r.start_date >= today)])
        }
        return {"kpis": kpis, "data": records}

    async def create_by_user(self, db: AsyncSession, obj_in, user: User):
        obj_in_data = obj_in.model_dump()
        emp_id = await _get_employee_id_for_user(db, user)
        if emp_id:
            obj_in_data["created_by_id"] = emp_id
            
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


campaign_service = CampaignService(models.Campaign)
