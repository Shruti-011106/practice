from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.service import BaseService
from . import models, schemas


class ProjectGovernanceService(
    BaseService[
        models.ProjectGovernance,
        schemas.ProjectGovernanceCreate,
        schemas.ProjectGovernanceUpdate,
    ]
):
    pass


projectgovernance_service = ProjectGovernanceService(
    models.ProjectGovernance,
    load_options=[
        selectinload(models.ProjectGovernance.customer_details),
        selectinload(models.ProjectGovernance.pm),
        selectinload(models.ProjectGovernance.delivery_lead),
    ],
)


class DeliverableTrackerService(
    BaseService[
        models.DeliverableTracker,
        schemas.DeliverableTrackerCreate,
        schemas.DeliverableTrackerUpdate,
    ]
):
    async def _update_project_milestones(self, db: AsyncSession, project_id: int):

        query = select(models.DeliverableTracker).filter(
            models.DeliverableTracker.project_id == project_id
        )
        result = await db.execute(query)
        deliverables = result.scalars().all()

        total = len(deliverables)
        completed = sum(
            1
            for d in deliverables
            if d.status and d.status.lower() in ["completed", "done"]
        )

        milestone_status = (
            f"{completed}/{total} Completed" if total > 0 else "0/0 Completed"
        )

        upcoming = [
            d
            for d in deliverables
            if d.status
            and d.status.lower() not in ["completed", "done"]
            and d.planned_date
        ]
        upcoming.sort(key=lambda x: x.planned_date)
        next_milestone = upcoming[0].milestone_name if upcoming else None

        project_query = select(models.ProjectGovernance).filter(
            models.ProjectGovernance.id == project_id
        )
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()

        if project:
            project.milestone_status = milestone_status
            project.next_milestone = next_milestone
            await db.commit()

    async def create(
        self, db: AsyncSession, obj_in: schemas.DeliverableTrackerCreate, **kwargs
    ) -> models.DeliverableTracker:
        db_obj = await super().create(db, obj_in, **kwargs)
        if db_obj.project_id:
            await self._update_project_milestones(db, db_obj.project_id)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: models.DeliverableTracker,
        obj_in: schemas.DeliverableTrackerUpdate,
    ) -> models.DeliverableTracker:
        updated_obj = await super().update(db, db_obj, obj_in)
        if updated_obj.project_id:
            await self._update_project_milestones(db, updated_obj.project_id)
        return updated_obj

    async def delete(
        self, db: AsyncSession, id: int
    ) -> Optional[models.DeliverableTracker]:
        db_obj = await self.get(db, id)
        if db_obj:
            project_id = db_obj.project_id
            await super().delete(db, id)
            if project_id:
                await self._update_project_milestones(db, project_id)
        return db_obj


deliverabletracker_service = DeliverableTrackerService(
    models.DeliverableTracker,
    load_options=[
        selectinload(models.DeliverableTracker.project),
        selectinload(models.DeliverableTracker.owner),
    ],
)


class CustomerSatisfactionService(
    BaseService[
        models.CustomerSatisfaction,
        schemas.CustomerSatisfactionCreate,
        schemas.CustomerSatisfactionUpdate,
    ]
):
    pass


customersatisfaction_service = CustomerSatisfactionService(
    models.CustomerSatisfaction,
    load_options=[
        selectinload(models.CustomerSatisfaction.customer),
        selectinload(models.CustomerSatisfaction.project),
        selectinload(models.CustomerSatisfaction.owner),
    ],
)


class QATrackerService(
    BaseService[models.QATracker, schemas.QATrackerCreate, schemas.QATrackerUpdate]
):
    async def create(
        self, db: AsyncSession, obj_in: schemas.QATrackerCreate, **kwargs
    ) -> models.QATracker:
        if obj_in.test_cases_executed > 0:
            passed = obj_in.test_cases_executed - obj_in.defect_count
            obj_in.pass_pct = max(
                0, min(100, (passed / obj_in.test_cases_executed) * 100)
            )
        return await super().create(db, obj_in, **kwargs)

    async def update(
        self,
        db: AsyncSession,
        db_obj: models.QATracker,
        obj_in: schemas.QATrackerUpdate,
    ) -> models.QATracker:
        executed = (
            obj_in.test_cases_executed
            if obj_in.test_cases_executed is not None
            else db_obj.test_cases_executed
        )
        defects = (
            obj_in.defect_count
            if obj_in.defect_count is not None
            else db_obj.defect_count
        )
        if executed and executed > 0:
            passed = executed - defects
            obj_in.pass_pct = max(0, min(100, (passed / executed) * 100))
        return await super().update(db, db_obj, obj_in)


qatracker_service = QATrackerService(
    models.QATracker,
    load_options=[
        selectinload(models.QATracker.project),
        selectinload(models.QATracker.owner),
    ],
)


class ChangeRequestService(
    BaseService[
        models.ChangeRequest, schemas.ChangeRequestCreate, schemas.ChangeRequestUpdate
    ]
):
    pass


changerequest_service = ChangeRequestService(
    models.ChangeRequest,
    load_options=[
        selectinload(models.ChangeRequest.project),
    ],
)


class ResourceUtilizationService(
    BaseService[
        models.ResourceUtilization,
        schemas.ResourceUtilizationCreate,
        schemas.ResourceUtilizationUpdate,
    ]
):
    async def _update_project_utilization(self, db: AsyncSession, project_id: int):
        query = select(models.ResourceUtilization).filter(
            models.ResourceUtilization.project_id == project_id
        )
        result = await db.execute(query)
        resources = result.scalars().all()

        if resources:
            avg_utilization = sum(r.utilization_pct or 0 for r in resources) / len(
                resources
            )
        else:
            avg_utilization = 0.0

        project_query = select(models.ProjectGovernance).filter(
            models.ProjectGovernance.id == project_id
        )
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()

        if project:
            project.utilization_pct = avg_utilization
            await db.commit()

    async def _check_over_allocation(self, db: AsyncSession, employee_id: int, new_utilization: float, exclude_id: Optional[int] = None):
        from fastapi import HTTPException
        query = select(models.ResourceUtilization).filter(
            models.ResourceUtilization.employee_id == employee_id,
            models.ResourceUtilization.allocation_status.in_(["Active", "Assigned"])
        )
        if exclude_id:
            query = query.filter(models.ResourceUtilization.id != exclude_id)
            
        result = await db.execute(query)
        existing_assignments = result.scalars().all()
        
        current_total = sum(r.utilization_pct or 0 for r in existing_assignments)
        if current_total + new_utilization > 100:
            raise HTTPException(
                status_code=400, 
                detail=f"Resource Allocation Error: The selected employee is already {current_total}% utilized across active projects. Maximum available bandwidth is {100 - current_total}%."
            )

    async def create(
        self, db: AsyncSession, obj_in: schemas.ResourceUtilizationCreate, **kwargs
    ) -> models.ResourceUtilization:
        from datetime import date
        if obj_in.assigned_on is None:
            obj_in.assigned_on = date.today()
            
        if obj_in.allocation_status in ["Active", "Assigned"]:
            await self._check_over_allocation(db, obj_in.employee_id, obj_in.utilization_pct)

        db_obj = await super().create(db, obj_in, **kwargs)
        if db_obj.project_id:
            await self._update_project_utilization(db, db_obj.project_id)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: models.ResourceUtilization,
        obj_in: schemas.ResourceUtilizationUpdate,
    ) -> models.ResourceUtilization:
        from datetime import date
        
        new_status = obj_in.allocation_status if obj_in.allocation_status is not None else db_obj.allocation_status
        new_util = obj_in.utilization_pct if obj_in.utilization_pct is not None else db_obj.utilization_pct
        
        if new_status in ["Released", "Completed", "On Hold", "Shadow"]:
            obj_in.utilization_pct = 0.0
            obj_in.billable_pct = 0.0
            if new_status in ["Released", "Completed"]:
                # Default release date if not explicitly set
                # Note: For pydantic v1, accessing unset fields might be tricky, but assuming obj_in has release_date.
                if not getattr(obj_in, "release_date", None):
                    obj_in.release_date = date.today()
        elif new_status in ["Active", "Assigned"]:
            # We must use db_obj.employee_id because it's not changeable.
            await self._check_over_allocation(db, db_obj.employee_id, new_util, exclude_id=db_obj.id)
            
        old_project_id = db_obj.project_id
        updated_obj = await super().update(db, db_obj, obj_in)

        if updated_obj.project_id:
            await self._update_project_utilization(db, updated_obj.project_id)
        if old_project_id and old_project_id != updated_obj.project_id:
            await self._update_project_utilization(db, old_project_id)

        return updated_obj

    async def delete(
        self, db: AsyncSession, id: int
    ) -> Optional[models.ResourceUtilization]:
        db_obj = await self.get(db, id)
        if db_obj:
            project_id = db_obj.project_id
            await super().delete(db, id)
            if project_id:
                await self._update_project_utilization(db, project_id)
        return db_obj


resourceutilization_service = ResourceUtilizationService(
    models.ResourceUtilization,
    load_options=[
        selectinload(models.ResourceUtilization.employee),
        selectinload(models.ResourceUtilization.project),
    ],
)


class RAIDService(BaseService[models.RAID, schemas.RAIDCreate, schemas.RAIDUpdate]):
    async def _update_project_raid_counts(self, db: AsyncSession, project_id: int):
        query = select(models.RAID).filter(
            models.RAID.project_id == project_id, models.RAID.status != "closed"
        )
        result = await db.execute(query)
        raids = result.scalars().all()

        risks_count = sum(1 for r in raids if r.type.lower() == "risk")
        issues_count = sum(1 for r in raids if r.type.lower() == "issue")
        dependencies_count = sum(1 for r in raids if r.type.lower() == "dependency")

        project_query = select(models.ProjectGovernance).filter(
            models.ProjectGovernance.id == project_id
        )
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()

        if project:
            project.risks = risks_count
            project.escalations = issues_count
            project.dependencies = dependencies_count
            await db.commit()

    async def create(
        self, db: AsyncSession, obj_in: schemas.RAIDCreate, **kwargs
    ) -> models.RAID:
        db_obj = await super().create(db, obj_in, **kwargs)
        await self._update_project_raid_counts(db, db_obj.project_id)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: models.RAID, obj_in: schemas.RAIDUpdate
    ) -> models.RAID:
        updated_obj = await super().update(db, db_obj, obj_in)
        await self._update_project_raid_counts(db, updated_obj.project_id)
        return updated_obj

    async def delete(self, db: AsyncSession, id: int) -> Optional[models.RAID]:
        db_obj = await self.get(db, id)
        if db_obj:
            project_id = db_obj.project_id
            await super().delete(db, id)
            await self._update_project_raid_counts(db, project_id)
        return db_obj


raid_service = RAIDService(
    models.RAID,
    load_options=[
        selectinload(models.RAID.project),
        selectinload(models.RAID.owner),
    ],
)


class VendorSubcontractorGovernanceService(
    BaseService[
        models.VendorSubcontractorGovernance,
        schemas.VendorSubcontractorGovernanceCreate,
        schemas.VendorSubcontractorGovernanceUpdate,
    ]
):
    pass


vendorsubcontractorgovernance_service = VendorSubcontractorGovernanceService(
    models.VendorSubcontractorGovernance,
    load_options=[
        selectinload(models.VendorSubcontractorGovernance.project),
        selectinload(models.VendorSubcontractorGovernance.vendor),
    ],
)


class MilestoneBillingService(
    BaseService[
        models.MilestoneBilling,
        schemas.MilestoneBillingCreate,
        schemas.MilestoneBillingUpdate,
    ]
):
    pass


milestonebilling_service = MilestoneBillingService(
    models.MilestoneBilling,
    load_options=[
        selectinload(models.MilestoneBilling.project),
    ],
)


class ProjectClosureService(
    BaseService[
        models.ProjectClosure,
        schemas.ProjectClosureCreate,
        schemas.ProjectClosureUpdate,
    ]
):
    pass


projectclosure_service = ProjectClosureService(
    models.ProjectClosure,
    load_options=[
        selectinload(models.ProjectClosure.project),
    ],
)



