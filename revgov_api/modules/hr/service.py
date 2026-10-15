from core.service import BaseService
from . import models, schemas

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from fastapi import HTTPException, status
from auth.models import User

class EmployeeService(
    BaseService[models.Employee, schemas.EmployeeCreate, schemas.EmployeeUpdate]
):
    async def get(self, db: AsyncSession, id: int) -> models.Employee:
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(
                selectinload(self.model.department_details),
                selectinload(self.model.manager),
            )
            .filter(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100, manager_id: Optional[int] = None
    ) -> List[models.Employee]:
        from sqlalchemy.orm import selectinload
        from sqlalchemy import or_

        query = (
            select(self.model)
            .options(
                selectinload(self.model.department_details),
                selectinload(self.model.manager),
            )
        )
        if manager_id is not None:
            query = query.filter(
                or_(self.model.manager_id == manager_id, self.model.id == manager_id)
            )
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_unlinked_employees(self, db: AsyncSession) -> List[models.Employee]:
        from sqlalchemy.orm import selectinload
        query = (
            select(self.model)
            .options(
                selectinload(self.model.department_details),
                selectinload(self.model.manager),
            )
            .filter(self.model.user_id == None)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_my_employee_profile(self, db: AsyncSession, user_id: int) -> Optional[models.Employee]:
        from sqlalchemy.orm import selectinload
        query = (
            select(self.model)
            .options(
                selectinload(self.model.department_details),
                selectinload(self.model.manager),
            )
            .filter(self.model.user_id == user_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def create(
        self, db: AsyncSession, obj_in: schemas.EmployeeCreate, **extra_data
    ) -> models.Employee:
        # Check employee code uniqueness
        if obj_in.employee_code:
            query = select(self.model).filter(
                self.model.employee_code == obj_in.employee_code
            )
            result = await db.execute(query)
            if result.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Employee code '{obj_in.employee_code}' already exists. Duplicate entries are not allowed.",
                )

        # Check email uniqueness
        if obj_in.email:
            query = select(self.model).filter(self.model.email == obj_in.email)
            result = await db.execute(query)
            if result.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{obj_in.email}' already exists. Duplicate emails are not allowed.",
                )

        db_obj = await super().create(db, obj_in, **extra_data)
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(
                selectinload(self.model.department_details),
                selectinload(self.model.manager),
            )
            .filter(self.model.id == db_obj.id)
        )
        result = await db.execute(query)
        return result.scalar_one()

    async def update(
        self,
        db: AsyncSession,
        db_obj: models.Employee,
        obj_in: schemas.EmployeeUpdate,
        **extra_data,
    ) -> models.Employee:
        if isinstance(obj_in, dict):
            email = obj_in.get("email")
        else:
            email = getattr(obj_in, "email", None)

        if email and email != db_obj.email:
            query = select(self.model).filter(self.model.email == email)
            result = await db.execute(query)
            if result.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{email}' already exists. Duplicate emails are not allowed.",
                )

        db_obj = await super().update(db, db_obj, obj_in, **extra_data)
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(
                selectinload(self.model.department_details),
                selectinload(self.model.manager),
            )
            .filter(self.model.id == db_obj.id)
        )
        result = await db.execute(query)
        return result.scalar_one()


employee_service = EmployeeService(models.Employee)


class LearningTrackerService(
    BaseService[
        models.LearningTracker,
        schemas.LearningTrackerCreate,
        schemas.LearningTrackerUpdate,
    ]
):
    async def get_all_by_user(
        self, db: AsyncSession, user: User, skip: int = 0, limit: int = 100
    ) -> List[models.LearningTracker]:
        from core.security_scopes import is_admin_ceo_or_hr, get_employee_id_for_user
        
        query = select(self.model)
        if not is_admin_ceo_or_hr(user):
            emp_id = await get_employee_id_for_user(db, user)
            if emp_id:
                query = query.where(self.model.employee_id == emp_id)
            else:
                return []
        
        query = query.offset(skip).limit(limit)
        if self.load_options:
            query = query.options(*self.load_options)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create_by_user(
        self, db: AsyncSession, obj_in: schemas.LearningTrackerCreate, user: User, **kwargs
    ) -> models.LearningTracker:
        from core.security_scopes import is_admin_ceo_or_hr, get_employee_id_for_user
        
        if not is_admin_ceo_or_hr(user):
            emp_id = await get_employee_id_for_user(db, user)
            if emp_id:
                obj_in.employee_id = emp_id
                
        return await super().create(db, obj_in, **kwargs)

    async def update_by_user(
        self, db: AsyncSession, db_obj: models.LearningTracker, obj_in: schemas.LearningTrackerUpdate, user: User, **kwargs
    ) -> models.LearningTracker:
        from core.security_scopes import is_admin_ceo_or_hr, get_employee_id_for_user
        from fastapi import HTTPException
        
        if not is_admin_ceo_or_hr(user):
            emp_id = await get_employee_id_for_user(db, user)
            if emp_id:
                # 1. Verify ownership (they can't update someone else's tracker)
                if db_obj.employee_id != emp_id:
                    raise HTTPException(status_code=403, detail="You can only update your own Learning Tracker.")
                # 2. Prevent changing ownership
                obj_in.employee_id = emp_id
                
        return await super().update(db, db_obj, obj_in, **kwargs)


learningtracker_service = LearningTrackerService(models.LearningTracker)


class LinkedInTrackerService(
    BaseService[
        models.LinkedInTracker,
        schemas.LinkedInTrackerCreate,
        schemas.LinkedInTrackerUpdate,
    ]
):
    async def create(
        self, db: AsyncSession, obj_in: schemas.LinkedInTrackerCreate, **extra_data
    ) -> models.LinkedInTracker:
        posting_id = getattr(obj_in, "posting_id", None)
        if posting_id:
            query = select(self.model).filter(self.model.posting_id == posting_id)
            result = await db.execute(query)
            if result.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Posting ID '{posting_id}' already exists. Duplicate entries are not allowed.",
                )
        else:
            result = await db.execute(select(func.max(self.model.id)))
            max_id = result.scalar() or 0
            new_id = max_id + 1
            posting_id = f"LKD-POST-{100 + new_id}"

        obj_in_data = obj_in.model_dump()
        if obj_in_data.get("job_link"):
            obj_in_data["job_link"] = str(obj_in_data["job_link"])
        obj_in_data["posting_id"] = posting_id

        db_obj = self.model(**obj_in_data, **extra_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


linkedintracker_service = LinkedInTrackerService(models.LinkedInTracker)


class JobOpeningService(
    BaseService[models.JobOpening, schemas.JobOpeningCreate, schemas.JobOpeningUpdate]
):
    async def create(
        self, db: AsyncSession, obj_in: schemas.JobOpeningCreate, **extra_data
    ) -> models.JobOpening:
        result = await db.execute(select(func.max(self.model.id)))
        max_id = result.scalar() or 0
        new_id = max_id + 1

        from datetime import datetime

        current_year = datetime.now().year
        generated_req_id = f"REQ-{current_year}-{new_id:03d}"

        obj_in_data = obj_in.model_dump()
        obj_in_data["req_id"] = generated_req_id

        db_obj = self.model(**obj_in_data, **extra_data)
        db.add(db_obj)
        await db.commit()
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(
                selectinload(self.model.department_details),
                selectinload(self.model.hiring_manager),
            )
            .filter(self.model.id == db_obj.id)
        )
        result = await db.execute(query)
        db_obj_loaded = result.scalar_one()
        return db_obj_loaded


jobopening_service = JobOpeningService(models.JobOpening)


class InterviewGovernanceService(
    BaseService[
        models.InterviewGovernance,
        schemas.InterviewGovernanceCreate,
        schemas.InterviewGovernanceUpdate,
    ]
):
    async def create(
        self, db: AsyncSession, obj_in: schemas.InterviewGovernanceCreate, **extra_data
    ) -> models.InterviewGovernance:
        result = await db.execute(select(func.max(self.model.id)))
        max_id = result.scalar() or 0
        new_id = max_id + 1

        generated_interview_id = f"INT{new_id:02d}"

        obj_in_data = obj_in.model_dump()
        interviewer_ids = obj_in_data.pop("interviewer_ids", [])
        
        db_obj = self.model(
            **obj_in_data, interview_id=generated_interview_id, **extra_data
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Create feedback rows
        for i_id in interviewer_ids:
            fb = models.InterviewFeedback(
                interview_id=db_obj.id,
                interviewer_id=i_id,
                feedback_status=schemas.FeedbackStatusEnum.PENDING
            )
            db.add(fb)
            
        # Update candidate status
        if db_obj.candidate_id:
            candidate = await db.get(models.Candidate, db_obj.candidate_id)
            if candidate:
                candidate.status = f"Scheduled - {db_obj.round}"
                db.add(candidate)
                
        await db.commit()

        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(
                selectinload(self.model.job_opening),
                selectinload(self.model.candidate),
                selectinload(self.model.feedbacks).selectinload(models.InterviewFeedback.interviewer),
            )
            .filter(self.model.id == db_obj.id)
            .execution_options(populate_existing=True)
        )
        result = await db.execute(query)
        db_obj_loaded = result.scalar_one()
        return db_obj_loaded

    async def update(
        self,
        db: AsyncSession,
        db_obj: models.InterviewGovernance,
        obj_in: schemas.InterviewGovernanceUpdate,
    ) -> models.InterviewGovernance:
        obj_data = obj_in.model_dump(exclude_unset=True)
        interviewer_ids = obj_data.pop("interviewer_ids", None)
        
        # Update standard fields
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        
        # Handle interviewer_ids if provided
        if interviewer_ids is not None:
            result = await db.execute(
                select(models.InterviewFeedback)
                .where(models.InterviewFeedback.interview_id == db_obj.id)
            )
            existing_feedbacks = result.scalars().all()
            existing_interviewer_ids = {fb.interviewer_id for fb in existing_feedbacks}
            
            new_ids = set(interviewer_ids)
            to_add = new_ids - existing_interviewer_ids
            to_remove = existing_interviewer_ids - new_ids
            
            # Remove old feedbacks
            for fb in existing_feedbacks:
                if fb.interviewer_id in to_remove:
                    await db.delete(fb)
                    
            # Add new feedbacks
            for i_id in to_add:
                fb = models.InterviewFeedback(
                    interview_id=db_obj.id,
                    interviewer_id=i_id,
                    feedback_status=schemas.FeedbackStatusEnum.PENDING
                )
                db.add(fb)
                
            await db.commit()
            
        from sqlalchemy.orm import selectinload
        query = (
            select(self.model)
            .options(
                selectinload(self.model.job_opening),
                selectinload(self.model.candidate),
                selectinload(self.model.feedbacks).selectinload(models.InterviewFeedback.interviewer),
            )
            .filter(self.model.id == db_obj.id)
            .execution_options(populate_existing=True)
        )
        result = await db.execute(query)
        return result.scalar_one()

async def aggregate_interview_feedback(db: AsyncSession, interview_id: int):
    # Fetch interview with feedbacks
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(models.InterviewGovernance)
        .options(
            selectinload(models.InterviewGovernance.feedbacks),
            selectinload(models.InterviewGovernance.candidate)
        )
        .where(models.InterviewGovernance.id == interview_id)
    )
    interview = result.scalar_one_or_none()
    
    if not interview or not interview.feedbacks:
        return
        
    # Check if all feedbacks are submitted
    all_submitted = all(fb.feedback_status != schemas.FeedbackStatusEnum.PENDING for fb in interview.feedbacks)
    
    if all_submitted:
        interview.status = schemas.InterviewRoundStatusEnum.COMPLETED
        
        # Determine candidate status based on feedback
        has_reject = any(fb.feedback_status == schemas.FeedbackStatusEnum.NOT_SELECTED for fb in interview.feedbacks)
        has_on_hold = any(fb.feedback_status == schemas.FeedbackStatusEnum.ON_HOLD for fb in interview.feedbacks)
        all_selected = all(fb.feedback_status == schemas.FeedbackStatusEnum.SELECTED for fb in interview.feedbacks)
        
        if interview.candidate:
            round_name = interview.round or "Interview"
            if has_reject:
                interview.candidate.status = f"Rejected - {round_name}"
            elif has_on_hold:
                interview.candidate.status = f"On Hold - {round_name}"
            elif all_selected:
                interview.candidate.status = f"Selected - {round_name}"
            else:
                interview.candidate.status = f"Interview Completed - {round_name}"
            db.add(interview.candidate)
            
        db.add(interview)
        await db.commit()


interviewgovernance_service = InterviewGovernanceService(
    models.InterviewGovernance,
    load_options=[
        selectinload(models.InterviewGovernance.job_opening),
        selectinload(models.InterviewGovernance.candidate),
        selectinload(models.InterviewGovernance.feedbacks).selectinload(models.InterviewFeedback.interviewer),
    ]
)


class OfferTrackerService(
    BaseService[
        models.OfferTracker,
        schemas.OfferTrackerCreate,
        schemas.OfferTrackerUpdate,
    ]
):
    async def create(
        self, db: AsyncSession, obj_in: schemas.OfferTrackerCreate, **extra_data
    ) -> models.OfferTracker:
        result = await db.execute(select(func.max(self.model.id)))
        max_id = result.scalar() or 0
        new_id = max_id + 1

        generated_offer_id = f"OFF{new_id:02d}"

        obj_in_data = obj_in.model_dump()
        db_obj = self.model(
            **obj_in_data, offer_id=generated_offer_id, **extra_data
        )
        db.add(db_obj)
        await db.commit()
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(
                selectinload(self.model.candidate),
            )
            .filter(self.model.id == db_obj.id)
        )
        result = await db.execute(query)
        db_obj_loaded = result.scalar_one()
        return db_obj_loaded


offertracker_service = OfferTrackerService(models.OfferTracker)


class PartnerTrackerService(
    BaseService[
        models.PartnerTracker,
        schemas.PartnerTrackerCreate,
        schemas.PartnerTrackerUpdate,
    ]
):
    async def get(self, db: AsyncSession, id: int) -> models.PartnerTracker:
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(selectinload(self.model.account_manager))
            .filter(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[models.PartnerTracker]:
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(selectinload(self.model.account_manager))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(
        self, db: AsyncSession, obj_in: schemas.PartnerTrackerCreate, **extra_data
    ) -> models.PartnerTracker:
        result = await db.execute(select(func.max(self.model.id)))
        max_id = result.scalar() or 0
        new_id = max_id + 1

        generated_partner_id = f"PART{new_id:03d}"

        obj_in_data = obj_in.model_dump()
        obj_in_data["partner_id"] = generated_partner_id

        db_obj = self.model(**obj_in_data, **extra_data)
        db.add(db_obj)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database constraint violation. Please check if the account_manager_id exists.",
            )
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(selectinload(self.model.account_manager))
            .filter(self.model.id == db_obj.id)
        )
        result = await db.execute(query)
        db_obj_loaded = result.scalar_one()
        return db_obj_loaded


partnertracker_service = PartnerTrackerService(models.PartnerTracker)


class VendorPartnerHiringService(
    BaseService[
        models.VendorPartnerHiring,
        schemas.VendorPartnerHiringCreate,
        schemas.VendorPartnerHiringUpdate,
    ]
):
    async def get(self, db: AsyncSession, id: int) -> models.VendorPartnerHiring:
        query = select(self.model).filter(self.model.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[models.VendorPartnerHiring]:
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(
        self, db: AsyncSession, obj_in: schemas.VendorPartnerHiringCreate, **extra_data
    ) -> models.VendorPartnerHiring:
        db_obj = await super().create(db, obj_in, **extra_data)
        query = select(self.model).filter(self.model.id == db_obj.id)
        result = await db.execute(query)
        return result.scalar_one()


vendorpartnerhiring_service = VendorPartnerHiringService(models.VendorPartnerHiring)


class InternshipStatusService(
    BaseService[
        models.InternshipStatus,
        schemas.InternshipStatusCreate,
        schemas.InternshipStatusUpdate,
    ]
):
    async def get(self, db: AsyncSession, id: int) -> models.InternshipStatus:
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(selectinload(self.model.mentor))
            .filter(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[models.InternshipStatus]:
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(selectinload(self.model.mentor))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(
        self, db: AsyncSession, obj_in: schemas.InternshipStatusCreate, **extra_data
    ) -> models.InternshipStatus:
        db_obj = await super().create(db, obj_in, **extra_data)
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(selectinload(self.model.mentor))
            .filter(self.model.id == db_obj.id)
        )
        result = await db.execute(query)
        return result.scalar_one()


internshipstatus_service = InternshipStatusService(models.InternshipStatus)


class BuddyEngagementService(
    BaseService[
        models.BuddyEngagement,
        schemas.BuddyEngagementCreate,
        schemas.BuddyEngagementUpdate,
    ]
):
    async def get(self, db: AsyncSession, id: int) -> models.BuddyEngagement:
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(
                selectinload(self.model.new_joiner),
                selectinload(self.model.buddy_assigned),
            )
            .filter(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[models.BuddyEngagement]:
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(
                selectinload(self.model.new_joiner),
                selectinload(self.model.buddy_assigned),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(
        self, db: AsyncSession, obj_in: schemas.BuddyEngagementCreate, **extra_data
    ) -> models.BuddyEngagement:
        db_obj = await super().create(db, obj_in, **extra_data)
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(
                selectinload(self.model.new_joiner),
                selectinload(self.model.buddy_assigned),
            )
            .filter(self.model.id == db_obj.id)
        )
        result = await db.execute(query)
        return result.scalar_one()


buddyengagement_service = BuddyEngagementService(models.BuddyEngagement)


class EmployeePerformanceService(
    BaseService[
        models.EmployeePerformance,
        schemas.EmployeePerformanceCreate,
        schemas.EmployeePerformanceUpdate,
    ]
):
    async def get(self, db: AsyncSession, id: int) -> models.EmployeePerformance:
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(selectinload(self.model.employee))
            .filter(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[models.EmployeePerformance]:
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(selectinload(self.model.employee))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(
        self, db: AsyncSession, obj_in: schemas.EmployeePerformanceCreate, **extra_data
    ) -> models.EmployeePerformance:
        db_obj = await super().create(db, obj_in, **extra_data)
        from sqlalchemy.orm import selectinload

        query = (
            select(self.model)
            .options(selectinload(self.model.employee))
            .filter(self.model.id == db_obj.id)
        )
        result = await db.execute(query)
        return result.scalar_one()


employeeperformance_service = EmployeePerformanceService(models.EmployeePerformance)


class DepartmentMasterService(
    BaseService[
        models.DepartmentMaster,
        schemas.DepartmentMasterCreate,
        schemas.DepartmentMasterUpdate,
    ]
):
    async def create(
        self,
        db: AsyncSession,
        obj_in: schemas.DepartmentMasterCreate,
        user_email: str = None,
    ) -> models.DepartmentMaster:
        # Check uniqueness of department code
        existing = await db.execute(select(self.model).where(self.model.department_code == obj_in.department_code))
        if existing.scalars().first():
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Department Code already exists")

        obj_dict = obj_in.model_dump()
        if user_email is not None:
            obj_dict["created_by"] = user_email

        db_obj = self.model(**obj_dict)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


departmentmaster_service = DepartmentMasterService(models.DepartmentMaster)
