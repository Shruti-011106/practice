from core.service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from auth.models import User
from core.constants import ROLE_CEO, ROLE_SUPER_ADMIN
from modules.hr.models import Employee
from . import models, schemas

async def _get_employee_id_for_user(db: AsyncSession, user: User) -> int | None:
    result = await db.execute(select(Employee).where(Employee.user_id == user.id))
    employee = result.scalar_one_or_none()
    return employee.id if employee else None

def _is_admin_or_ceo(user: User) -> bool:
    role_names = [role.name for role in user.roles]
    return ROLE_SUPER_ADMIN in role_names or ROLE_CEO in role_names


class ProposalTrackerService(
    BaseService[
        models.ProposalTracker,
        schemas.ProposalTrackerCreate,
        schemas.ProposalTrackerUpdate,
    ]
):
    async def get_all_by_user(
        self, db: AsyncSession, user: User, skip: int = 0, limit: int = 100
    ) -> list[models.ProposalTracker]:
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.outerjoin(models.PresalesBID, self.model.presales_bid_id == models.PresalesBID.id)
                query = query.outerjoin(models.RFPTracker, models.PresalesBID.rfp_tracker_id == models.RFPTracker.id)
                query = query.where(
                    or_(
                        self.model.approver_id == emp_id,
                        models.RFPTracker.presales_owner_id == emp_id
                    )
                )
            else:
                return []
        
        query = query.offset(skip).limit(limit)
        if self.load_options:
            query = query.options(*self.load_options)
        result = await db.execute(query)
        return list(result.scalars().all())


    async def create(self, db: "AsyncSession", obj_in: schemas.ProposalTrackerCreate, **kwargs) -> models.ProposalTracker:
        if getattr(obj_in, "presales_bid_id", None):
            from sqlalchemy import select
            from fastapi import HTTPException
            
            # Check for duplicate
            existing = await db.execute(select(models.ProposalTracker).where(models.ProposalTracker.presales_bid_id == obj_in.presales_bid_id))
            if existing.scalars().first():
                raise HTTPException(status_code=400, detail="A Proposal has already been created for this Bid. Please check your existing records.")
                
            result = await db.execute(select(models.PresalesBID).where(models.PresalesBID.id == obj_in.presales_bid_id))
            bid = result.scalars().first()
            
            if not bid:
                raise HTTPException(status_code=404, detail="Presales BID not found")
            
            if not bid.status or bid.status.lower() != "approved":
                raise HTTPException(status_code=400, detail="Only 'Approved' Bids can be converted to a Proposal")
                
            # Lock the parent Bid
            bid.status = "Converted to Proposal"
            db.add(bid)
            
        db_obj = await super().create(db, obj_in, **kwargs)
        return await self.get(db, db_obj.id)

    async def update(self, db: "AsyncSession", db_obj: models.ProposalTracker, obj_in: schemas.ProposalTrackerUpdate, **kwargs) -> models.ProposalTracker:
        from fastapi import HTTPException
        
        old_status = db_obj.status
        new_status = getattr(obj_in, "status", None)
        
        if old_status and old_status.lower() == "converted to poc":
            if new_status and new_status.lower() != "converted to poc":
                raise HTTPException(status_code=400, detail="This Proposal has already moved to the POC phase. Its status cannot be reversed.")
        
        if new_status and new_status.strip().lower() == "accepted":
            new_internal_approval = getattr(obj_in, "internal_approval", None) or db_obj.internal_approval
            if not new_internal_approval or new_internal_approval.strip().lower() != "approved":
                raise HTTPException(status_code=400, detail="Proposal cannot be Accepted until Internal Approval is 'Approved'")
                
        return await super().update(db, db_obj, obj_in, **kwargs)

    async def reject_proposal(self, db: "AsyncSession", proposal: models.ProposalTracker) -> models.ProposalTracker:
        proposal.status = "Rejected"
        db.add(proposal)
        await db.commit()
        await db.refresh(proposal)
        return proposal


proposaltracker_service = ProposalTrackerService(models.ProposalTracker)


class RFPTrackerService(
    BaseService[models.RFPTracker, schemas.RFPTrackerCreate, schemas.RFPTrackerUpdate]
):
    async def get_all_by_user(
        self, db: AsyncSession, user: User, skip: int = 0, limit: int = 100
    ) -> list[models.RFPTracker]:
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(self.model.presales_owner_id == emp_id)
            else:
                return []
        
        query = query.offset(skip).limit(limit)
        if self.load_options:
            query = query.options(*self.load_options)
        result = await db.execute(query)
        return list(result.scalars().all())


    async def create(self, db: "AsyncSession", obj_in: schemas.RFPTrackerCreate, **kwargs) -> models.RFPTracker:
        if getattr(obj_in, "lead_id", None):
            from modules.sales.models import LeadTracker
            from sqlalchemy import select
            from fastapi import HTTPException
            
            # 1. Check if an RFP already exists for this lead
            existing_rfp_result = await db.execute(select(models.RFPTracker).where(models.RFPTracker.lead_id == obj_in.lead_id))
            if existing_rfp_result.scalars().first():
                raise HTTPException(status_code=400, detail="An RFP has already been generated for this Lead. Please check your existing records.")
            
            # 2. Proceed with checking the lead status
            result = await db.execute(select(LeadTracker).where(LeadTracker.id == obj_in.lead_id))
            lead = result.scalars().first()
            
            if not lead:
                raise HTTPException(status_code=404, detail="Lead not found")
            
            if not lead.lead_status or lead.lead_status.strip().lower() != "qualified":
                raise HTTPException(status_code=400, detail="Only Qualified leads can be converted to RFP")
                
            # Lead ko Converted mark kar dete hain
            lead.lead_status = "Converted to RFP"
            db.add(lead)
            
        db_obj = await super().create(db, obj_in, **kwargs)
        return await self.get(db, db_obj.id)

    async def update(self, db: "AsyncSession", db_obj: models.RFPTracker, obj_in: schemas.RFPTrackerUpdate, **kwargs) -> models.RFPTracker:
        old_status = db_obj.status
        new_status = getattr(obj_in, 'status', None)
        
        if old_status and old_status.lower() == "won":
            if new_status and new_status.lower() != "won":
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="This RFP has already been Won. Its status cannot be changed back.")
                
        return await super().update(db, db_obj, obj_in, **kwargs)

    async def reject_rfp(self, db: "AsyncSession", rfp: models.RFPTracker) -> models.RFPTracker:
        rfp.status = "Lost"
        db.add(rfp)
        await db.commit()
        await db.refresh(rfp)
        return rfp


rfptracker_service = RFPTrackerService(models.RFPTracker)


class POCTrackerService(
    BaseService[models.POCTracker, schemas.POCTrackerCreate, schemas.POCTrackerUpdate]
):
    async def get_all_by_user(
        self, db: AsyncSession, user: User, skip: int = 0, limit: int = 100
    ) -> list[models.POCTracker]:
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(self.model.owner_id == emp_id)
            else:
                return []
        
        query = query.offset(skip).limit(limit)
        if self.load_options:
            query = query.options(*self.load_options)
        result = await db.execute(query)
        return list(result.scalars().all())


    async def create(self, db: "AsyncSession", obj_in: schemas.POCTrackerCreate, **kwargs) -> models.POCTracker:
        if getattr(obj_in, "proposal_tracker_id", None):
            from sqlalchemy import select
            from fastapi import HTTPException
            
            # Check for duplicate POC
            existing = await db.execute(select(models.POCTracker).where(models.POCTracker.proposal_tracker_id == obj_in.proposal_tracker_id))
            if existing.scalars().first():
                raise HTTPException(status_code=400, detail="A POC has already been created for this Proposal. Please check your existing records.")
            
            result = await db.execute(select(models.ProposalTracker).where(models.ProposalTracker.id == obj_in.proposal_tracker_id))
            proposal = result.scalars().first()
            
            if not proposal:
                raise HTTPException(status_code=404, detail="Proposal Tracker not found")
            
            if not proposal.status or proposal.status.lower() != "accepted":
                raise HTTPException(status_code=400, detail="Only 'Accepted' Proposals can be converted to a POC")
                
            # Lock the parent Proposal
            proposal.status = "Converted to POC"
            db.add(proposal)
                
        db_obj = await super().create(db, obj_in, **kwargs)
        return await self.get(db, db_obj.id)

    async def update(self, db: "AsyncSession", db_obj: models.POCTracker, obj_in: schemas.POCTrackerUpdate, **kwargs) -> models.POCTracker:
        old_status = db_obj.status
        new_status = getattr(obj_in, 'status', None)
        
        if old_status and old_status.lower() == "converted to demo":
            if new_status and new_status.lower() != "converted to demo":
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="This POC has already advanced to the Demo phase. Its status cannot be reversed.")
                
        return await super().update(db, db_obj, obj_in, **kwargs)

    async def fail_poc(self, db: "AsyncSession", poc: models.POCTracker) -> models.POCTracker:
        poc.status = "Failed"
        db.add(poc)
        await db.commit()
        await db.refresh(poc)
        return poc


poctracker_service = POCTrackerService(models.POCTracker)


class PresalesBIDService(
    BaseService[
        models.PresalesBID, schemas.PresalesBIDCreate, schemas.PresalesBIDUpdate
    ]
):
    async def get_all_by_user(
        self, db: AsyncSession, user: User, skip: int = 0, limit: int = 100
    ) -> list[models.PresalesBID]:
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.outerjoin(models.RFPTracker, self.model.rfp_tracker_id == models.RFPTracker.id)
                query = query.where(
                    or_(
                        self.model.approver_id == emp_id,
                        models.RFPTracker.presales_owner_id == emp_id
                    )
                )
            else:
                return []
        
        query = query.offset(skip).limit(limit)
        if self.load_options:
            query = query.options(*self.load_options)
        result = await db.execute(query)
        return list(result.scalars().all())


    async def create(self, db: "AsyncSession", obj_in: schemas.PresalesBIDCreate, **kwargs) -> models.PresalesBID:
        if getattr(obj_in, "rfp_tracker_id", None):
            from sqlalchemy import select
            from fastapi import HTTPException
            
            # 1. Check if a Bid already exists for this RFP
            existing_bid_result = await db.execute(select(models.PresalesBID).where(models.PresalesBID.rfp_tracker_id == obj_in.rfp_tracker_id))
            if existing_bid_result.scalars().first():
                raise HTTPException(status_code=400, detail="A Bid has already been submitted for this RFP. Please check your existing records.")
                
            # 2. Proceed with checking the RFP status
            result = await db.execute(select(models.RFPTracker).where(models.RFPTracker.id == obj_in.rfp_tracker_id))
            rfp = result.scalars().first()
            
            if not rfp:
                raise HTTPException(status_code=404, detail="RFP Tracker not found")
            
            if not rfp.status or rfp.status.strip().lower() != "submitted":
                raise HTTPException(status_code=400, detail="Only 'Submitted' RFPs can be converted to a Bid")
                
            # Automatically set bid_submission_date to RFP's bid_closing_date
            if rfp.bid_closing_date:
                obj_in.bid_submission_date = rfp.bid_closing_date
                
            # 3. Mark RFP status as Won
            rfp.status = "Won"
            db.add(rfp)
                
        return await super().create(db, obj_in, **kwargs)

    async def update(self, db: "AsyncSession", db_obj: models.PresalesBID, obj_in: schemas.PresalesBIDUpdate, **kwargs) -> models.PresalesBID:
        old_status = db_obj.status
        new_status = getattr(obj_in, 'status', None)
        
        if old_status and old_status.lower() == "converted to proposal":
            if new_status and new_status.lower() != "converted to proposal":
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="This Bid has already been converted into a Proposal. Its status cannot be reversed.")
                
        return await super().update(db, db_obj, obj_in, **kwargs)

    async def reject_bid(self, db: "AsyncSession", bid: models.PresalesBID) -> models.PresalesBID:
        bid.status = "Rejected"
        db.add(bid)
        await db.commit()
        await db.refresh(bid)
        return bid


presalesbid_service = PresalesBIDService(models.PresalesBID)


class PresalesDemoService(
    BaseService[
        models.PresalesDemo, schemas.PresalesDemoCreate, schemas.PresalesDemoUpdate
    ]
):
    async def get_all_by_user(
        self, db: AsyncSession, user: User, skip: int = 0, limit: int = 100
    ) -> list[models.PresalesDemo]:
        query = select(self.model)
        if not _is_admin_or_ceo(user):
            emp_id = await _get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(self.model.demo_owner_id == emp_id)
            else:
                return []
        
        query = query.offset(skip).limit(limit)
        if self.load_options:
            query = query.options(*self.load_options)
        result = await db.execute(query)
        return list(result.scalars().all())


    async def create(self, db: "AsyncSession", obj_in: schemas.PresalesDemoCreate, **kwargs) -> models.PresalesDemo:
        if getattr(obj_in, "poc_tracker_id", None):
            from sqlalchemy import select
            from fastapi import HTTPException
            
            # Check for duplicate Demo
            existing = await db.execute(select(models.PresalesDemo).where(models.PresalesDemo.poc_tracker_id == obj_in.poc_tracker_id))
            if existing.scalars().first():
                raise HTTPException(status_code=400, detail="A Demo has already been created for this POC. Please check your existing records.")
            
            result = await db.execute(select(models.POCTracker).where(models.POCTracker.id == obj_in.poc_tracker_id))
            poc = result.scalars().first()
            
            if not poc:
                raise HTTPException(status_code=404, detail="POC Tracker not found")
            
            if not poc.status or poc.status.lower() != "completed":
                raise HTTPException(status_code=400, detail="Only 'Completed' POCs can be converted to a Demo")
                
            # Lock the parent POC
            poc.status = "Converted to Demo"
            db.add(poc)
                
        return await super().create(db, obj_in, **kwargs)

    async def update(self, db: "AsyncSession", db_obj: models.PresalesDemo, obj_in: schemas.PresalesDemoUpdate, **kwargs) -> models.PresalesDemo:
        old_status = db_obj.status
        new_status = getattr(obj_in, 'status', None)
        
        if old_status and old_status.lower() == "converted to pipeline":
            if new_status and new_status.lower() != "converted to pipeline":
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="This Demo has already been pushed to the Sales Pipeline. Its status cannot be reversed.")
                
        return await super().update(db, db_obj, obj_in, **kwargs)


presalesdemo_service = PresalesDemoService(models.PresalesDemo)


class PresalesGovernanceService(
    BaseService[
        models.PresalesGovernance,
        schemas.PresalesGovernanceCreate,
        schemas.PresalesGovernanceUpdate,
    ]
):
    pass


presalesgovernance_service = PresalesGovernanceService(models.PresalesGovernance)
