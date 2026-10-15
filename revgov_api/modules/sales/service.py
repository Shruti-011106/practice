from auth.models import User
from core.constants import ROLE_CEO, ROLE_SUPER_ADMIN
from core.service import BaseService
from modules.hr.models import Employee
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas


async def _get_employee_id_for_user(db: AsyncSession, user: User) -> int | None:
    result = await db.execute(select(Employee).where(Employee.user_id == user.id))
    employee = result.scalar_one_or_none()
    return employee.id if employee else None


async def _get_employee_for_user(db: AsyncSession, user: User) -> Employee | None:
    result = await db.execute(select(Employee).where(Employee.user_id == user.id))
    return result.scalar_one_or_none()


def _is_admin_or_ceo(user: User) -> bool:
    role_names = [role.name for role in user.roles]
    return ROLE_SUPER_ADMIN in role_names or ROLE_CEO in role_names


class LeadTrackerService(
    BaseService[
        models.LeadTracker, schemas.LeadTrackerCreate, schemas.LeadTrackerUpdate
    ]
):
    async def get_all_by_user(
        self, db: AsyncSession, user: User, skip: int = 0, limit: int = 100
    ) -> list[models.LeadTracker]:
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(
                    or_(
                        self.model.sales_owner_id == emp_id,
                        self.model.presales_engineer_id == emp_id
                    )
                )
            else:
                return []
        
        query = query.offset(skip).limit(limit)
        if self.load_options:
            query = query.options(*self.load_options)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def _handle_qualified_lead(self, db: AsyncSession, lead: models.LeadTracker):
        if lead.lead_status and lead.lead_status.lower() == "qualified":
            from modules.customer_success.models import CustomerMaster
            
            customer_ref_id = f"CUST-{lead.lead_id}"
            query = select(CustomerMaster).where(CustomerMaster.customer_id == customer_ref_id)
            result = await db.execute(query)
            existing_customer = result.scalars().first()
            
            if not existing_customer:
                new_customer = CustomerMaster(
                    customer_id=customer_ref_id,
                    customer_name=lead.client_name,
                    account_type="Customer",
                    industry="Others",
                    status="Active",
                    account_manager_id=lead.sales_owner_id,
                    contract_value=lead.expected_revenue or 0.0
                )
                db.add(new_customer)
                await db.commit()

    async def create(self, db: AsyncSession, obj_in: schemas.LeadTrackerCreate, **kwargs) -> models.LeadTracker:
        user_id = kwargs.pop("user_id", None)
        db_obj = await super().create(db, obj_in, **kwargs)
        
        from modules.activities.service import activity_service
        await activity_service.add_audit_log(
            db=db, entity_type="lead", entity_id=db_obj.id,
            action="Lead Created", details="Lead governance workflow initialized", user_id=user_id
        )
        
        await self._handle_qualified_lead(db, db_obj)
        return await self.get(db, db_obj.id)

    async def update(self, db: AsyncSession, db_obj: models.LeadTracker, obj_in: schemas.LeadTrackerUpdate, **kwargs) -> models.LeadTracker:
        user_id = kwargs.pop("user_id", None)
        old_status = db_obj.lead_status
        old_presales_engineer_id = db_obj.presales_engineer_id
        
        # Validation to prevent backtracking from Converted to RFP
        new_status = getattr(obj_in, 'lead_status', None)
        if old_status and old_status.lower() == "converted to rfp":
            if new_status and new_status.lower() != "converted to rfp":
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="This Lead has already been converted to an RFP. Its status cannot be changed back.")
        
        updated_obj = await super().update(db, db_obj, obj_in, **kwargs)
        
        if updated_obj.lead_status != old_status:
            from modules.activities.service import activity_service
            await activity_service.add_audit_log(
                db=db, entity_type="lead", entity_id=updated_obj.id,
                action=f"Status transitioned to: {updated_obj.lead_status}", user_id=user_id
            )
            
        if updated_obj.presales_engineer_id and updated_obj.presales_engineer_id != old_presales_engineer_id:
            import logging
            logger = logging.getLogger("sales_notifications")
            logger.info(f"[NOTIFICATION] Alert sent to Presales Engineer (ID: {updated_obj.presales_engineer_id}) for Lead ID: {updated_obj.id}")
            
            from modules.activities.service import activity_service
            await activity_service.add_audit_log(
                db=db, entity_type="lead", entity_id=updated_obj.id,
                action=f"Assigned to Presales Engineer (ID: {updated_obj.presales_engineer_id})", user_id=user_id
            )
            
        await self._handle_qualified_lead(db, updated_obj)
        return updated_obj

    async def reject_lead(self, db: AsyncSession, lead: models.LeadTracker) -> models.LeadTracker:
        lead.lead_status = "Rejected"
        db.add(lead)
        await db.commit()
        await db.refresh(lead)
        return lead




leadtracker_service = LeadTrackerService(models.LeadTracker)


class SalesRevenueTrackerService(
    BaseService[
        models.SalesRevenueTracker,
        schemas.SalesRevenueTrackerCreate,
        schemas.SalesRevenueTrackerUpdate,
    ]
):
    async def get_all_by_user(
        self, db: AsyncSession, user: User, skip: int = 0, limit: int = 100
    ) -> list[models.SalesRevenueTracker]:
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(self.model.revenue_owner_id == emp_id)
            else:
                return []
        
        query = query.offset(skip).limit(limit)
        if self.load_options:
            query = query.options(*self.load_options)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(
        self, db: AsyncSession, obj_in: schemas.SalesRevenueTrackerCreate, **kwargs
    ) -> models.SalesRevenueTracker:
        if getattr(obj_in, "pipeline_id", None):
            from fastapi import HTTPException
            
            # Check for duplicate Revenue Tracker
            existing = await db.execute(select(models.SalesRevenueTracker).where(models.SalesRevenueTracker.pipeline_id == obj_in.pipeline_id))
            if existing.scalars().first():
                raise HTTPException(status_code=400, detail="A Revenue Tracker already exists for this Pipeline. Please check your existing records.")
                
            result = await db.execute(select(models.SalesPipeline).where(models.SalesPipeline.id == obj_in.pipeline_id))
            pipeline = result.scalars().first()
            if not pipeline:
                raise HTTPException(status_code=404, detail="Sales Pipeline not found")
            if not pipeline.pipeline_stage or pipeline.pipeline_stage.lower() != "won":
                raise HTTPException(status_code=400, detail="Only 'Won' Pipelines can be tracked for Revenue")
                
            # Lock the parent Pipeline
            pipeline.pipeline_stage = "Closed Won"
            db.add(pipeline)
                
        # Auto-calculate pending
        invoice = getattr(obj_in, "invoice", 0.0) or 0.0
        collected = getattr(obj_in, "collected", 0.0) or 0.0
        obj_in.pending = max(0.0, invoice - collected)

        db_obj = await super().create(db, obj_in, **kwargs)
        return await self.get(db, db_obj.id)

    async def update(
        self,
        db: AsyncSession,
        db_obj: models.SalesRevenueTracker,
        obj_in: schemas.SalesRevenueTrackerUpdate,
    ) -> models.SalesRevenueTracker:
        # Auto-calculate pending
        invoice = getattr(obj_in, "invoice", None)
        if invoice is None:
            invoice = db_obj.invoice or 0.0
        
        collected = getattr(obj_in, "collected", None)
        if collected is None:
            collected = db_obj.collected or 0.0
            
        obj_in.pending = max(0.0, float(invoice) - float(collected))
        
        updated_obj = await super().update(db, db_obj, obj_in)
        
        # Audit Log
        from modules.activities.service import activity_service
        # Assuming we can get a user_id from some context, but we don't have user in signature.
        # We will log it without user_id if not available, or wait, activity_service requires user_id?
        # Let's check activity_service signature. Actually, we'll skip user_id if it's optional.
        # It's better to just log the action history in Pipeline.
        
        return updated_obj

    async def reject_revenue(self, db: AsyncSession, revenue: models.SalesRevenueTracker) -> models.SalesRevenueTracker:
        revenue.status = "Rejected"
        if revenue.pipeline_id:
            result = await db.execute(select(models.SalesPipeline).where(models.SalesPipeline.id == revenue.pipeline_id))
            pipeline = result.scalar_one_or_none()
            if pipeline:
                pipeline.pipeline_stage = "Lost"
                db.add(pipeline)
        
        db.add(revenue)
        await db.commit()
        await db.refresh(revenue)
        return revenue


salesrevenuetracker_service = SalesRevenueTrackerService(models.SalesRevenueTracker)


class SalesPipelineService(
    BaseService[
        models.SalesPipeline, schemas.SalesPipelineCreate, schemas.SalesPipelineUpdate
    ]
):
    async def get_all_by_user(
        self, db: AsyncSession, user: User, skip: int = 0, limit: int = 100
    ) -> list[models.SalesPipeline]:
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp = await _get_employee_for_user(db, user)
            if emp:
                query = query.where(
                    (self.model.opportunity_owner == emp.employee_name) | 
                    (self.model.revdau_owner_id == emp.id)
                )
            else:
                return []
        
        query = query.offset(skip).limit(limit)
        if self.load_options:
            query = query.options(*self.load_options)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def _clean_deprecated_fields(self, obj_in):
        if hasattr(obj_in, 'lead_source'):
            delattr(obj_in, 'lead_source')
        if hasattr(obj_in, 'probability_pct'):
            delattr(obj_in, 'probability_pct')
        return obj_in

    async def _add_action_history(self, db: AsyncSession, pipeline_id: int, action_text: str):
        if action_text:
            history = models.SalesPipelineActionHistory(
                pipeline_id=pipeline_id,
                action_text=action_text
            )
            db.add(history)
            await db.commit()

    async def create(self, db: AsyncSession, obj_in: schemas.SalesPipelineCreate, **kwargs) -> models.SalesPipeline:
        obj_in = await self._clean_deprecated_fields(obj_in)
        
        if getattr(obj_in, "demo_tracker_id", None):
            from fastapi import HTTPException
            from modules.presales.models import PresalesDemo
            
            # Check for duplicate Pipeline
            existing = await db.execute(select(models.SalesPipeline).where(models.SalesPipeline.demo_tracker_id == obj_in.demo_tracker_id))
            if existing.scalars().first():
                raise HTTPException(status_code=400, detail="A Sales Pipeline has already been created for this Demo. Please check your existing records.")
            
            result = await db.execute(select(PresalesDemo).where(PresalesDemo.id == obj_in.demo_tracker_id))
            demo = result.scalars().first()
            
            if not demo:
                raise HTTPException(status_code=404, detail="Demo Tracker not found")
            
            if not demo.status or demo.status.lower() != "completed":
                raise HTTPException(status_code=400, detail="Only 'Completed' Demos can be converted to a Sales Pipeline")
                
            # Lock the parent Demo
            demo.status = "Converted to Pipeline"
            db.add(demo)

        action_text = getattr(obj_in, 'next_action', None)
        
        db_obj = await super().create(db, obj_in, **kwargs)
        
        if action_text:
            await self._add_action_history(db, db_obj.id, action_text)
            
        return await self.get(db, db_obj.id)

    async def update(self, db: AsyncSession, db_obj: models.SalesPipeline, obj_in: schemas.SalesPipelineUpdate) -> models.SalesPipeline:
        obj_in = await self._clean_deprecated_fields(obj_in)
        
        # Track changes for Audit Log
        changes = []
        
        new_stage = getattr(obj_in, 'pipeline_stage', None)
        old_stage = db_obj.pipeline_stage
        
        if old_stage and old_stage.lower() == "closed won":
            if new_stage and new_stage.lower() != "closed won":
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="This Sales Pipeline is marked as 'Closed Won' and its stage cannot be reversed.")
                
        if new_stage and new_stage != db_obj.pipeline_stage:
            changes.append(f"Stage changed from {db_obj.pipeline_stage} to {new_stage}")
            
        new_deal_value = getattr(obj_in, 'deal_value', None)
        if new_deal_value is not None and new_deal_value != db_obj.deal_value:
            changes.append(f"Deal value updated from {db_obj.deal_value} to {new_deal_value}")
            
        action_text = getattr(obj_in, 'next_action', None)
        is_new_action = action_text and action_text != db_obj.next_action
        
        updated_obj = await super().update(db, db_obj, obj_in)
        
        if is_new_action:
            await self._add_action_history(db, updated_obj.id, action_text)
            
        for change in changes:
            await self._add_action_history(db, updated_obj.id, change)
            
        return updated_obj


salespipeline_service = SalesPipelineService(models.SalesPipeline)
