from core.service import BaseService
from typing import Optional
from . import models, schemas

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from auth.models import User
from core.constants import ROLE_CEO, ROLE_SUPER_ADMIN, ROLE_HR_MANAGER
from modules.hr.models import Employee
from fastapi import HTTPException

async def _get_employee_id_for_user(db: AsyncSession, user: User) -> int | None:
    result = await db.execute(select(Employee).where(Employee.user_id == user.id))
    employee = result.scalar_one_or_none()
    return employee.id if employee else None

def _is_global_viewer(user: User) -> bool:
    if not user.roles:
        return False
    role_names = [role.name for role in user.roles]
    return ROLE_SUPER_ADMIN in role_names or ROLE_CEO in role_names or ROLE_HR_MANAGER in role_names

class ReusableAssetService(
    BaseService[
        models.ReusableAsset, schemas.ReusableAssetCreate, schemas.ReusableAssetUpdate
    ]
):
    async def create_by_user(self, db: AsyncSession, obj_in: schemas.ReusableAssetCreate, user: User):
        emp_id = await _get_employee_id_for_user(db, user)
        obj_in_data = obj_in.model_dump()
        obj_in_data["created_by_id"] = emp_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_all_by_user(self, db: AsyncSession, user: User):
        from sqlalchemy.orm import selectinload
        query = select(self.model).options(selectinload(self.model.owner))
        if not _is_global_viewer(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(
                    self.model.created_by_id == emp_id
                )
            else:
                return []
        
        result = await db.execute(query.order_by(self.model.id.desc()))
        return result.scalars().all()


reusableasset_service = ReusableAssetService(models.ReusableAsset)


# Knowledge Repository - Merged into Reusable Asset (Temporarily Disabled)
# class KnowledgeRepoService(BaseService[models.KnowledgeRepo, schemas.KnowledgeRepoCreate, schemas.KnowledgeRepoUpdate]):
#     pass
#
# knowledgerepo_service = KnowledgeRepoService(models.KnowledgeRepo)


class CapabilityBuildingService(
    BaseService[
        models.CapabilityBuilding,
        schemas.CapabilityBuildingCreate,
        schemas.CapabilityBuildingUpdate,
    ]
):
    async def create_by_user(self, db: AsyncSession, obj_in: schemas.CapabilityBuildingCreate, user: User):
        emp_id = await _get_employee_id_for_user(db, user)
        
        if obj_in.training_details is not None:
            obj_in.training_count = len(obj_in.training_details)
            
        obj_in_data = obj_in.model_dump()
        obj_in_data["created_by_id"] = emp_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_all_by_user(self, db: AsyncSession, user: User, view: Optional[str] = None):
        query = select(self.model)
        emp_id = await _get_employee_id_for_user(db, user)
        
        if view and view.lower() == "employee" and emp_id:
            query = query.where(self.model.employee_id == emp_id)
        elif view and view.lower() == "manager" and emp_id:
            query = query.where(
                or_(
                    self.model.practice_owner_id == emp_id,
                    self.model.created_by_id == emp_id,
                )
            )
        else:
            if not _is_global_viewer(user):
                if emp_id:
                    query = query.where(
                        or_(
                            self.model.employee_id == emp_id,
                            self.model.practice_owner_id == emp_id,
                            self.model.created_by_id == emp_id,
                        )
                    )
                else:
                    return []
        
        result = await db.execute(query.order_by(self.model.id.desc()))
        return result.scalars().all()

    async def update_by_user(self, db: AsyncSession, db_obj: models.CapabilityBuilding, obj_in: schemas.CapabilityBuildingUpdate, user: User):
        if not _is_global_viewer(user):
            emp_id = await _get_employee_id_for_user(db, user)
            
            # If they are just the employee, restrict what they can change
            if db_obj.employee_id == emp_id and db_obj.practice_owner_id != emp_id and db_obj.created_by_id != emp_id:
                if getattr(obj_in, "employee_id", None) is not None and obj_in.employee_id != db_obj.employee_id:
                    raise HTTPException(status_code=403, detail="You cannot modify the Employee field.")
                if getattr(obj_in, "technology", None) is not None and obj_in.technology != db_obj.technology:
                    raise HTTPException(status_code=403, detail="You cannot modify the Technology field.")
                if getattr(obj_in, "practice_owner_id", None) is not None and obj_in.practice_owner_id != db_obj.practice_owner_id:
                    raise HTTPException(status_code=403, detail="You cannot modify the Practice Owner field.")

        if obj_in.training_details is not None:
            obj_in.training_count = len(obj_in.training_details)

        return await super().update(db, db_obj, obj_in)


capabilitybuilding_service = CapabilityBuildingService(models.CapabilityBuilding)


class PartnershipAllianceService(
    BaseService[
        models.PartnershipAlliance,
        schemas.PartnershipAllianceCreate,
        schemas.PartnershipAllianceUpdate,
    ]
):
    pass


partnershipalliance_service = PartnershipAllianceService(models.PartnershipAlliance)


class TechCapabilityService(
    BaseService[
        models.TechCapability,
        schemas.TechCapabilityCreate,
        schemas.TechCapabilityUpdate,
    ]
):
    pass


techcapability_service = TechCapabilityService(models.TechCapability)


class InnovationAutomationService(
    BaseService[
        models.InnovationAutomation,
        schemas.InnovationAutomationCreate,
        schemas.InnovationAutomationUpdate,
    ]
):
    async def create_by_user(self, db: AsyncSession, obj_in: schemas.InnovationAutomationCreate, user: User):
        emp_id = await _get_employee_id_for_user(db, user)
        obj_in_data = obj_in.model_dump()
        obj_in_data["created_by_id"] = emp_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_all_by_user(self, db: AsyncSession, user: User):
        query = select(self.model)
        if not _is_global_viewer(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(
                    self.model.created_by_id == emp_id
                )
            else:
                return []
        
        result = await db.execute(query.order_by(self.model.id.desc()))
        return result.scalars().all()


innovationautomation_service = InnovationAutomationService(models.InnovationAutomation)


class TrainingTrackerService(
    BaseService[
        models.TrainingTracker,
        schemas.TrainingTrackerCreate,
        schemas.TrainingTrackerUpdate,
    ]
):
    pass


trainingtracker_service = TrainingTrackerService(models.TrainingTracker)
