from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.crud_factory import make_router
from app.db import models as m, schemas as s
from core.constants import (
    ROLE_HR_MANAGER,
    ROLE_RECRUITER,
    ROLE_PROJECT_MANAGER,
    ROLE_EMPLOYEE,
    ROLE_LND_MANAGER,
)

employees = make_router(
    m.Employee,
    s.EmployeeCreate,
    s.EmployeeUpdate,
    s.EmployeeOut,
    "/employees",
    ["HR"],
    allowed_roles=[ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE],
)
learning = make_router(
    m.LearningTracker,
    s.LearningTrackerCreate,
    s.LearningTrackerUpdate,
    s.LearningTrackerOut,
    "/learning-trackers",
    ["HR"],
    allowed_roles=[
        ROLE_HR_MANAGER,
        ROLE_PROJECT_MANAGER,
        ROLE_EMPLOYEE,
        ROLE_LND_MANAGER,
    ],
)


async def set_linkedin_posting_id(obj: m.LinkedInTracker, db: AsyncSession):
    count = await db.scalar(select(func.count()).select_from(m.LinkedInTracker))
    obj.posting_id = f"JOB{(count + 1):03d}"


linkedin = make_router(
    m.LinkedInTracker,
    s.LinkedInTrackerCreate,
    s.LinkedInTrackerUpdate,
    s.LinkedInTrackerOut,
    "/linkedin-trackers",
    ["HR"],
    allowed_roles=[
        ROLE_HR_MANAGER,
        ROLE_RECRUITER,
        ROLE_PROJECT_MANAGER,
        ROLE_EMPLOYEE,
    ],
    before_create=set_linkedin_posting_id,
)


async def set_job_opening_defaults(obj: m.JobOpening, db: AsyncSession):
    count = await db.scalar(select(func.count()).select_from(m.JobOpening))
    obj.req_id = f"REQ{(count + 1):03d}"

    # Auto-calculate aging days if open_date is set
    if obj.open_date:
        obj.aging_days = (date.today() - obj.open_date).days
    else:
        obj.aging_days = 0


job_openings = make_router(
    m.JobOpening,
    s.JobOpeningCreate,
    s.JobOpeningUpdate,
    s.JobOpeningOut,
    "/job-openings",
    ["HR"],
    allowed_roles=[ROLE_HR_MANAGER, ROLE_RECRUITER],
    before_create=set_job_opening_defaults,
)

partner_tracker = make_router(
    m.PartnerTracker,
    s.PartnerTrackerCreate,
    s.PartnerTrackerUpdate,
    s.PartnerTrackerOut,
    "/partner-trackers",
    ["HR"],
    allowed_roles=[ROLE_HR_MANAGER, ROLE_RECRUITER],
)
vendor_hiring = make_router(
    m.VendorPartnerHiring,
    s.VendorPartnerHiringCreate,
    s.VendorPartnerHiringUpdate,
    s.VendorPartnerHiringOut,
    "/vendor-partner-hiring",
    ["HR"],
    allowed_roles=[ROLE_HR_MANAGER, ROLE_RECRUITER],
)
internship = make_router(
    m.InternshipStatus,
    s.InternshipStatusCreate,
    s.InternshipStatusUpdate,
    s.InternshipStatusOut,
    "/internship-statuses",
    ["HR"],
    allowed_roles=[ROLE_HR_MANAGER, ROLE_RECRUITER],
)
buddy = make_router(
    m.BuddyEngagement,
    s.BuddyEngagementCreate,
    s.BuddyEngagementUpdate,
    s.BuddyEngagementOut,
    "/buddy-engagements",
    ["HR"],
    allowed_roles=[ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER],
)
emp_performance = make_router(
    m.EmployeePerformance,
    s.EmployeePerformanceCreate,
    s.EmployeePerformanceUpdate,
    s.EmployeePerformanceOut,
    "/employee-performances",
    ["HR"],
    allowed_roles=[ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER],
)
